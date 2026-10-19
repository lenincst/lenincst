"""Coleta os números do perfil na API do GitHub.

Só saem daqui agregados: nenhum nome de repositório privado vai para as imagens.
O token precisa enxergar os repositórios privados (escopo `repo`).
"""
import json
import os
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

API = "https://api.github.com"
USUARIO = "lenincst"
FUSO = ZoneInfo("America/Sao_Paulo")

# Endereços com que o Lenin já fez commit: ficam fora do repositório (que é público),
# num arquivo da VPS apontado por PERFIL_EMAILS, um por linha. Linha que começa com
# "*" vale como sufixo (ex.: "*.c.maquina.internal").
def _emails():
    caminho = os.environ.get("PERFIL_EMAILS")
    if not caminho:
        return set(), ()
    linhas = [l.strip().lower() for l in open(caminho) if l.strip()]
    return {l for l in linhas if not l.startswith("*")}, tuple(l[1:] for l in linhas if l.startswith("*"))


def _pedir(caminho, token, corpo=None):
    url = caminho if caminho.startswith("http") else API + caminho
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(url, data=dados, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "perfil-lenincst",
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        proximo = None
        for parte in resp.headers.get("Link", "").split(","):
            if 'rel="next"' in parte:
                proximo = parte[parte.index("<") + 1:parte.index(">")]
        return json.load(resp), proximo


def _paginas(caminho, token):
    while caminho:
        pagina, caminho = _pedir(caminho, token)
        yield from pagina


def _eh_do_lenin(commit, emails, sufixos):
    if (commit.get("author") or {}).get("login") == USUARIO:
        return True
    email = commit["commit"]["author"]["email"].lower()
    return email in emails or (bool(sufixos) and email.endswith(sufixos))


def coletar(token):
    repos = [r for r in _paginas(f"/user/repos?affiliation=owner&per_page=100", token)
             if r["owner"]["login"] == USUARIO and not r["fork"]]

    emails, sufixos = _emails()
    linguagens = Counter()
    horas = Counter()
    dias_semana = Counter()
    commits = 0
    primeiro = None
    for r in repos:
        lings, _ = _pedir(f"/repos/{USUARIO}/{r['name']}/languages", token)
        linguagens.update(lings)
        if r["size"] == 0:
            continue
        for c in _paginas(f"/repos/{USUARIO}/{r['name']}/commits?per_page=100", token):
            if not _eh_do_lenin(c, emails, sufixos):
                continue
            commits += 1
            quando = datetime.fromisoformat(c["commit"]["author"]["date"].replace("Z", "+00:00")).astimezone(FUSO)
            horas[quando.hour] += 1
            dias_semana[quando.weekday()] += 1
            primeiro = quando if primeiro is None or quando < primeiro else primeiro

    consulta = """{ user(login: "%s") { createdAt contributionsCollection {
        contributionCalendar { totalContributions weeks { contributionDays {
          date contributionCount contributionLevel } } } } } }""" % USUARIO
    grafo, _ = _pedir("/graphql", token, {"query": consulta})
    usuario = grafo["data"]["user"]
    calendario = usuario["contributionsCollection"]["contributionCalendar"]
    semanas = [[{"data": d["date"], "total": d["contributionCount"], "nivel": d["contributionLevel"]}
                for d in s["contributionDays"]] for s in calendario["weeks"]]

    return {
        "gerado_em": datetime.now(FUSO).isoformat(timespec="minutes"),
        "conta_desde": usuario["createdAt"][:10],
        "repos_total": len(repos),
        "repos_privados": sum(1 for r in repos if r["private"]),
        "commits": commits,
        "primeiro_commit": primeiro.date().isoformat() if primeiro else None,
        "contribuicoes_ano": calendario["totalContributions"],
        "semanas": semanas,
        "sequencias": _sequencias(semanas),
        "linguagens": dict(linguagens.most_common()),
        "horas": [horas[h] for h in range(24)],
        "dias_semana": [dias_semana[d] for d in range(7)],
    }


def _sequencias(semanas):
    """Maior sequência de dias seguidos com contribuição e a sequência atual."""
    dias = [d for s in semanas for d in s]
    maior = atual = corrida = 0
    for d in dias:
        corrida = corrida + 1 if d["total"] else 0
        maior = max(maior, corrida)
    # A atual tolera o dia de hoje ainda vazio.
    for i, d in enumerate(reversed(dias)):
        if d["total"]:
            atual += 1
        elif i > 0:
            break
    return {"maior": maior, "atual": atual}


if __name__ == "__main__":
    import sys
    json.dump(coletar(os.environ["GH_TOKEN"]), sys.stdout, ensure_ascii=False, indent=1)
