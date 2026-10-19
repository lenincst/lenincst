"""As peças do perfil: banner, cartões das marcas e faixa de linguagens.

Visual: fundo quase preto, tipografia grande, brilho âmbar. Toda animação parte do quadro inicial
e termina no estado normal do elemento, para que leitores sem CSS mostrem a peça pronta.
"""
import json
import re
from datetime import date
from pathlib import Path

from vetor import altura_maiuscula, documento, largura, milhar, ruido, texto

AQUI = Path(__file__).parent
ICONES = json.loads((AQUI / "icones.json").read_text())["icones"]

FUNDO, BORDA = "#09090b", "#27272a"
TEXTO, TEXTO_2, TEXTO_3 = "#fafafa", "#a1a1aa", "#71717a"
AMBAR = "#ffb547"
NIVEIS = {"NONE": "#1c1c21", "FIRST_QUARTILE": "#5b3613", "SECOND_QUARTILE": "#9a5418",
          "THIRD_QUARTILE": "#e0791f", "FOURTH_QUARTILE": AMBAR}


def _cartao(l, a, raio=28):
    return (f'<rect width="{l}" height="{a}" rx="{raio}" fill="{FUNDO}"/>'
            f'<rect x=".5" y=".5" width="{l - 1}" height="{a - 1}" rx="{raio - .5}" fill="none" stroke="{BORDA}"/>')


# --------------------------------------------------------------------------- banner

def banner(dados, perfil):
    L = 1200
    nome = "LECODARO"
    tamanho = 100 * 1080 / largura(nome, "titulo", 100, -0.01)
    cap = altura_maiuscula("titulo", tamanho)
    base_titulo = 70 + cap
    base_sub = base_titulo + 72
    topo_pontos = base_sub + 62
    passo = 1060 / 52
    fundo_pontos = topo_pontos + 6 * 19
    base_legenda = fundo_pontos + 46
    A = round(base_legenda + 34)

    defs = f"""
<linearGradient id="tit" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#b4b4bd"/></linearGradient>
<linearGradient id="faixa" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="varredura" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{AMBAR}" stop-opacity="0"/><stop offset=".5" stop-color="{AMBAR}" stop-opacity=".16"/><stop offset="1" stop-color="{AMBAR}" stop-opacity="0"/></linearGradient>
<radialGradient id="luzA"><stop offset="0" stop-color="#ff7a1a" stop-opacity=".30"/><stop offset="1" stop-color="#ff7a1a" stop-opacity="0"/></radialGradient>
<radialGradient id="luzB"><stop offset="0" stop-color="#3b5bff" stop-opacity=".22"/><stop offset="1" stop-color="#3b5bff" stop-opacity="0"/></radialGradient>
<radialGradient id="halo"><stop offset="0" stop-color="{AMBAR}" stop-opacity=".45"/><stop offset="1" stop-color="{AMBAR}" stop-opacity="0"/></radialGradient>
<radialGradient id="foco"><stop offset=".3" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>
<mask id="sumir"><rect width="{L}" height="{A}" fill="url(#foco)"/></mask>
<pattern id="grade" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#fff" stroke-opacity=".06"/></pattern>
<clipPath id="moldura"><rect width="{L}" height="{A}" rx="28"/></clipPath>
<clipPath id="forma">{texto(nome, "titulo", tamanho, L / 2, base_titulo, ancora="meio", tracking=-0.01, por_letra=True)}</clipPath>"""

    css = f"""
@keyframes subir{{from{{opacity:0;transform:translateY(46px)}}}}
@keyframes surgir{{from{{opacity:0}}}}
@keyframes derivaA{{50%{{transform:translate(90px,40px)}}}}
@keyframes derivaB{{50%{{transform:translate(-110px,-30px)}}}}
@keyframes brilho{{0%{{transform:translateX(0)}}30%,100%{{transform:translateX({L + 500}px)}}}}
@keyframes piscar{{50%{{opacity:0}}}}
@keyframes pulsar{{50%{{opacity:.35}}}}
@keyframes anel{{from{{transform:scale(1);opacity:.9}}to{{transform:scale(3.4);opacity:0}}}}
@keyframes varrer{{from{{transform:translateX(0)}}to{{transform:translateX({L + 360}px)}}}}
.letra{{animation:subir 1s cubic-bezier(.2,.7,.2,1) both;animation-delay:calc(var(--i) * 75ms + 150ms)}}
.sub{{animation:surgir 1s ease-out 1s both}}
.cursor{{animation:piscar 1.1s steps(1) infinite}}
.luzA{{animation:derivaA 18s ease-in-out infinite}}
.luzB{{animation:derivaB 22s ease-in-out infinite}}
.brilho{{animation:brilho 7s ease-in-out 1.9s infinite}}
.col{{animation:surgir .5s ease-out both}}
.ponto{{animation:pulsar 5s ease-in-out infinite}}
.anel{{transform-box:fill-box;transform-origin:center;animation:anel 2.2s ease-out infinite}}
.varre{{animation:varrer 6s linear 2.5s infinite}}
.leg{{animation:surgir 1s ease-out 1.6s both}}"""

    partes = [f'<g clip-path="url(#moldura)">', _cartao(L, A),
              f'<circle class="luzA" cx="260" cy="120" r="460" fill="url(#luzA)"/>',
              f'<circle class="luzB" cx="980" cy="{A - 80}" r="420" fill="url(#luzB)"/>',
              f'<rect width="{L}" height="{A}" fill="url(#grade)" mask="url(#sumir)"/>']

    partes.append(texto(nome, "titulo", tamanho, L / 2, base_titulo, cor="url(#tit)", ancora="meio",
                        tracking=-0.01, classe="letra", por_letra=True))
    partes.append(f'<g clip-path="url(#forma)"><rect class="brilho" x="-420" y="{base_titulo - cap - 10}" '
                  f'width="300" height="{cap + 20}" fill="url(#faixa)" transform="skewX(-18)"/></g>')

    sub = perfil["subtitulo"]
    tam_sub = 30
    partes.append(f'<g class="sub">{texto(sub, "mono_medio", tam_sub, L / 2, base_sub, cor=TEXTO_2, ancora="meio", tracking=0.02)}'
                  f'<rect class="cursor" x="{L / 2 + largura(sub, "mono_medio", tam_sub, 0.02) / 2 + 10:.1f}" '
                  f'y="{base_sub - 24}" width="14" height="28" fill="{AMBAR}"/></g>')

    # cada ponto é um dia do último ano; a cor é o nível de contribuição daquele dia
    x0 = (L - 1060) / 2
    semanas = dados["semanas"]
    pontos = []
    for w, semana in enumerate(semanas):
        col = [f'<g class="col" style="animation-delay:{0.9 + w * 0.018:.3f}s">']
        for dia in semana:
            d = date.fromisoformat(dia["data"]).isoweekday() % 7
            cx, cy = x0 + w * passo, topo_pontos + d * 19
            cor = NIVEIS.get(dia["nivel"], NIVEIS["NONE"])
            if dia["nivel"] in ("THIRD_QUARTILE", "FOURTH_QUARTILE"):
                col.append(f'<circle cx="{cx:.1f}" cy="{cy}" r="13" fill="url(#halo)"/>')
            if dia["nivel"] != "NONE":
                atraso = -ruido(w * 7 + d) * 5
                col.append(f'<circle class="ponto" style="animation-delay:{atraso:.2f}s" cx="{cx:.1f}" cy="{cy}" r="4.6" fill="{cor}"/>')
            else:
                col.append(f'<circle cx="{cx:.1f}" cy="{cy}" r="4.6" fill="{cor}"/>')
        col.append("</g>")
        pontos.append("".join(col))
    partes += pontos
    ultimo = semanas[-1][-1]
    d = date.fromisoformat(ultimo["data"]).isoweekday() % 7
    partes.append(f'<circle class="anel" cx="{x0 + (len(semanas) - 1) * passo:.1f}" cy="{topo_pontos + d * 19}" r="4.6" '
                  f'fill="none" stroke="{AMBAR}" stroke-width="1.6"/>')
    partes.append(f'<rect class="varre" x="-240" y="{topo_pontos - 14}" width="120" height="{6 * 19 + 28}" fill="url(#varredura)"/>')

    esquerda = f"{milhar(dados['contribuicoes_ano'])} contribuições no último ano · cada ponto é um dia"
    direita = f"{milhar(dados['commits'])} commits"
    partes.append(f'<g class="leg">{texto(esquerda, "mono", 17, x0, base_legenda, cor=TEXTO_3)}'
                  f'{texto(direita, "mono", 17, L - x0, base_legenda, cor=TEXTO_3, ancora="fim")}</g>')
    partes.append("</g>")
    return documento(L, A, f"LECODARO: {sub}. Cada ponto é um dia de contribuição no GitHub no último ano.",
                     css, "".join(partes), defs)


# --------------------------------------------------------------------------- cartões das marcas

def _icone_marca(id_, x, y, lado, recorte=None):
    svg = (AQUI / "marcas" / f"{id_}.svg").read_text()
    viewbox = recorte or re.search(r'viewBox="([^"]+)"', svg).group(1)
    interno = re.sub(r"^<svg[^>]*>|</svg>\s*$", "", svg.strip())
    interno = re.sub(r"<title>.*?</title>", "", interno)
    return f'<svg x="{x}" y="{y}" width="{lado}" height="{lado}" viewBox="{viewbox}">{interno}</svg>'


def cartao_marca(marca, indice):
    L, A = 400, 236
    no_ar = marca["situacao"] == "no ar"
    cor_status = "#22c55e" if no_ar else AMBAR
    atraso = indice * 0.25
    defs = (f'<radialGradient id="g{marca["id"]}"><stop offset="0" stop-color="{marca["cor"]}" stop-opacity=".35"/>'
            f'<stop offset="1" stop-color="{marca["cor"]}" stop-opacity="0"/></radialGradient>'
            f'<clipPath id="m"><rect width="{L}" height="{A}" rx="24"/></clipPath>')
    css = f"""
@keyframes respirar{{50%{{opacity:.45}}}}
@keyframes flutuar{{50%{{transform:translateY(-5px)}}}}
@keyframes anel{{from{{transform:scale(1);opacity:.8}}to{{transform:scale(3);opacity:0}}}}
@keyframes entrar{{from{{opacity:0;transform:translateY(16px)}}}}
.brilho{{animation:respirar 6s ease-in-out {-atraso * 4:.1f}s infinite}}
.icone{{animation:entrar .8s cubic-bezier(.2,.7,.2,1) {atraso:.2f}s both}}
.flutua{{animation:flutuar 4.5s ease-in-out {atraso:.2f}s infinite}}
.anel{{transform-box:fill-box;transform-origin:center;animation:anel 2s ease-out infinite}}
.txt{{animation:entrar .8s cubic-bezier(.2,.7,.2,1) {atraso + 0.15:.2f}s both}}"""
    status = marca["situacao"]
    largura_status = largura(status, "mono", 15) + 48
    partes = [f'<g clip-path="url(#m)">', _cartao(L, A, 24),
              f'<circle class="brilho" cx="70" cy="60" r="210" fill="url(#g{marca["id"]})"/>',
              f'<g class="icone"><g class="flutua">{_icone_marca(marca["id"], 30, 28, 68, marca.get("recorte"))}</g></g>',
              f'<rect x="{L - 28 - largura_status:.1f}" y="34" width="{largura_status:.1f}" height="30" rx="15" fill="#18181b" stroke="{BORDA}"/>',
              f'<circle cx="{L - 28 - largura_status + 18:.1f}" cy="49" r="4.5" fill="{cor_status}"/>',
              f'<circle class="anel" cx="{L - 28 - largura_status + 18:.1f}" cy="49" r="4.5" fill="none" stroke="{cor_status}" stroke-width="1.5"/>',
              texto(status, "mono", 15, L - 28 - largura_status + 34, 54, cor=TEXTO_2),
              f'<g class="txt">',
              texto(marca["nome"], "rotulo", 31, 32, 146, cor=TEXTO),
              texto(marca["descricao"], "rotulo", 20, 32, 178, cor=TEXTO_2),
              texto(marca["dominio"], "mono", 17, 32, 210, cor=TEXTO_3),
              "</g></g>"]
    return documento(L, A, f"{marca['nome']}: {marca['descricao']} ({marca['dominio']})", css, "".join(partes), defs)


# --------------------------------------------------------------------------- linguagens

def linguagens(dados, perfil):
    L, A = 1200, 250
    medidas = []
    total = sum(dados["linguagens"].get(i["linguagem"], 0) for i in perfil["codigo"]) or 1
    for item in perfil["codigo"]:
        medidas.append((item, dados["linguagens"].get(item["linguagem"], 0) / total))
    medidas.sort(key=lambda m: -m[1])
    itens = [(i, p) for i, p in medidas] + [(i, None) for i in perfil["carreira"]]

    margem, divisao = 56, 36
    largura_item = (L - 2 * margem - divisao) / len(itens)
    css = """
@keyframes entrar{from{opacity:0;transform:translateY(18px)}}
@keyframes flutuar{50%{transform:translateY(-4px)}}
@keyframes encher{from{transform:scaleX(0)}}
@keyframes surgir{from{opacity:0}}
.item{animation:entrar .8s cubic-bezier(.2,.7,.2,1) both}
.flutua{animation:flutuar 5s ease-in-out infinite}
.barra{transform-box:fill-box;transform-origin:left;animation:encher 1.2s cubic-bezier(.2,.7,.2,1) both}
.cab{animation:surgir 1s ease-out both}"""
    partes = [_cartao(L, A)]
    x_div = margem + len(medidas) * largura_item + divisao / 2
    partes.append(f'<g class="cab">{texto("NO CÓDIGO DA LECODARO", "mono_medio", 15, margem + 12, 62, cor=TEXTO_3, tracking=0.12)}'
                  f'{texto("TAMBÉM NA CARREIRA", "mono_medio", 15, x_div + divisao / 2 + 12, 62, cor=TEXTO_3, tracking=0.12)}</g>')
    partes.append(f'<rect x="{x_div:.1f}" y="44" width="1" height="{A - 88}" fill="{BORDA}"/>')
    for n, (item, parte) in enumerate(itens):
        x = margem + n * largura_item + (divisao if parte is None else 0)
        cx = x + largura_item / 2
        atraso = 0.2 + n * 0.07
        bloco = [f'<g class="item" style="animation-delay:{atraso:.2f}s"><g class="flutua" style="animation-delay:{-n * 0.45:.2f}s">']
        if item.get("icone"):
            icone = ICONES[item["icone"]]
            bloco.append(f'<path fill="{icone["cor"]}" transform="translate({cx - 21:.1f} 96) scale({42 / 24:.4f})" d="{icone["d"]}"/>')
        else:
            bloco.append(texto(item["nome"], "titulo", 30, cx, 128, cor=item["cor"], ancora="meio"))
        bloco.append("</g>")
        bloco.append(texto(item["nome"], "rotulo", 15, cx, 172, cor=TEXTO, ancora="meio"))
        if parte is not None:
            bloco.append(f'<rect x="{cx - 30:.1f}" y="188" width="60" height="4" rx="2" fill="#27272a"/>')
            bloco.append(f'<rect class="barra" style="animation-delay:{atraso + 0.4:.2f}s" x="{cx - 30:.1f}" y="188" '
                         f'width="{max(3, 60 * parte):.1f}" height="4" rx="2" fill="{AMBAR}"/>')
            bloco.append(texto(f"{parte * 100:.0f}%", "mono", 14, cx, 214, cor=TEXTO_3, ancora="meio"))
        bloco.append("</g>")
        partes.append("".join(bloco))
    return documento(L, A, "Linguagens que o Lenin mais programa no código da Lecodaro e as que usa na carreira",
                     css, "".join(partes))
