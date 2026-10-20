"""Gera as imagens do perfil.

Uso: python3 gerador/gerar.py <pasta-de-saida> [--dados arquivo.json]
Sem --dados, coleta na API do GitHub com o token em GH_TOKEN.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import dados as coleta  # noqa: E402
import pecas  # noqa: E402


def main():
    saida = Path(sys.argv[1])
    saida.mkdir(parents=True, exist_ok=True)
    if "--dados" in sys.argv:
        dados = json.loads(Path(sys.argv[sys.argv.index("--dados") + 1]).read_text())
    else:
        dados = coleta.coletar(os.environ["GH_TOKEN"])
    perfil = json.loads((Path(__file__).parent.parent / "perfil.json").read_text())

    arquivos = {"banner.svg": pecas.banner(dados, perfil), "marcas.svg": pecas.cabecalho_marcas(perfil),
                "linguagens.svg": pecas.linguagens(dados, perfil),
                "botao-linkedin.svg": pecas.botao("linkedin"), "botao-lecodaro.svg": pecas.botao("lecodaro")}
    for i, marca in enumerate(perfil["marcas"]):
        arquivos[f"marca-{marca['id']}.svg"] = pecas.cartao_marca(marca, i)
    for nome, svg in arquivos.items():
        (saida / nome).write_text(svg)
    (saida / "dados.json").write_text(json.dumps(
        {k: v for k, v in dados.items() if k != "semanas"}, ensure_ascii=False, indent=1))
    print(f"{len(arquivos)} imagens em {saida}")


if __name__ == "__main__":
    main()
