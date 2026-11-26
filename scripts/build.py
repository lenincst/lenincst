"""Gera assets/*.dark.svg e assets/*.light.svg do README a partir de scripts/palette.json.

Uso:  python scripts/build.py            (requer: pip install -r scripts/requirements.txt)

Tudo o que é calculado (engrenamento, ASCII do cartão, máquina de Turing, Jogo da Vida, DFT do λ) sai daqui,
com asserções que param o build se algo não fechar. Depois de gerar, cada SVG é validado como XML e
conferido contra o orçamento de tamanho (150 KB por arquivo, 1 MB no total).
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from pieces import boot, footer, fourier, life, stack, timeline, turing  # noqa: E402
from svgkit import TEMAS  # noqa: E402

SAIDA = AQUI.parent / "assets"
PECAS = {
    "boot": boot.construir,
    "timeline": timeline.construir,
    "stack": stack.construir,
    "turing": turing.construir,
    "fourier": fourier.construir,
    "life": life.construir,
    "footer-lecodaro": footer.lecodaro,
    "footer-linkedin": footer.linkedin,
    "footer-hello": footer.hello,
}
LIMITE_ARQUIVO = 150 * 1024
LIMITE_TOTAL = 1024 * 1024


def main() -> int:
    SAIDA.mkdir(exist_ok=True)
    so = set(sys.argv[1:])
    total, problemas = 0, []
    for nome, construir in PECAS.items():
        if so and nome not in so:
            continue
        for tema in TEMAS:
            svg = construir(tema)
            ET.fromstring(svg)  # XML bem-formado (levanta ParseError se não for)
            caminho = SAIDA / f"{nome}.{tema}.svg"
            caminho.write_text(svg, encoding="utf-8", newline="\n")
            tamanho = len(svg.encode())
            total += tamanho
            marca = "" if tamanho <= LIMITE_ARQUIVO else "  <-- acima de 150 KB"
            if marca:
                problemas.append(caminho.name)
            print(f"{caminho.name:32s} {tamanho / 1024:7.1f} KB{marca}")
    print(f"{'total':32s} {total / 1024:7.1f} KB")
    if total > LIMITE_TOTAL and not so:
        problemas.append("total acima de 1 MB")
    if problemas:
        print("fora do orçamento:", ", ".join(problemas))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
