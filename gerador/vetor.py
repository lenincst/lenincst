"""Texto como desenho vetorial e o esqueleto dos SVGs.

As letras vêm de `fontes.json` (contornos e kerning extraídos de Space Grotesk e JetBrains Mono)
e viram `<path>`: o texto sai igual em qualquer navegador, sem carregar fonte nenhuma.
"""
import json
from html import escape
from pathlib import Path

_DADOS = json.loads((Path(__file__).parent / "fontes.json").read_text())
FONTES = _DADOS["fontes"]


def _posicoes(s, fonte, tracking):
    """Avanço de cada letra em unidades da fonte, com kerning e espaçamento extra (em em)."""
    f = FONTES[fonte]
    extra = tracking * f["upm"]
    x, saida, anterior = 0, [], None
    for ch in s:
        if anterior is not None:
            x += f["kern"].get(anterior + ch, 0) + extra
        glifo = f["glifos"].get(ch) or f["glifos"]["?"]
        saida.append((ch, x, glifo))
        x += glifo["a"]
        anterior = ch
    return saida, x


def largura(s, fonte, tamanho, tracking=0.0):
    return _posicoes(s, fonte, tracking)[1] * tamanho / FONTES[fonte]["upm"]


def altura_maiuscula(fonte, tamanho):
    return FONTES[fonte]["maiuscula"] * tamanho / FONTES[fonte]["upm"]


def texto(s, fonte, tamanho, x, y, cor="#fff", ancora="inicio", tracking=0.0, classe=None, por_letra=False, extra=""):
    """`y` é a linha de base. Com `por_letra`, cada letra é um <path> (para animar uma a uma)."""
    posicoes, total = _posicoes(s, fonte, tracking)
    k = tamanho / FONTES[fonte]["upm"]
    if ancora == "meio":
        x -= total * k / 2
    elif ancora == "fim":
        x -= total * k
    if por_letra:
        partes = []
        for i, (ch, px, g) in enumerate(posicoes):
            if g["d"]:
                caminho = (f'<path fill="{cor}" transform="translate({x + px * k:.2f} {y:.2f}) scale({k:.5f})" '
                           f'd="{g["d"]}"/>')
                if classe:
                    # o <g> recebe a animação (transform via CSS); o <path> guarda a posição
                    caminho = f'<g class="{classe}" style="--i:{i}">{caminho}</g>'
                partes.append(caminho)  # sem classe: <path> solto, que pode ir dentro de <clipPath>
        return "".join(partes)
    corpo = "".join(f'<path transform="translate({px} 0)" d="{g["d"]}"/>' for ch, px, g in posicoes if g["d"])
    atrib = f' class="{classe}"' if classe else ""
    return f'<g{atrib} fill="{cor}" transform="translate({x:.2f} {y:.2f}) scale({k:.5f})"{extra}>{corpo}</g>'


def documento(largura_, altura, titulo, css, corpo, defs=""):
    movimento_reduzido = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura_} {altura}" width="{largura_}" '
            f'height="{altura}" role="img" aria-label="{escape(titulo)}"><title>{escape(titulo)}</title>'
            f'<defs>{defs}</defs><style>{css}{movimento_reduzido}</style>{corpo}</svg>')


def ruido(i, semente=0):
    """Pseudoaleatório estável (a arte não muda de um dia para o outro sem motivo)."""
    import math
    v = math.sin(i * 12.9898 + semente * 78.233) * 43758.5453
    return v - math.floor(v)


def milhar(n):
    return f"{n:,}".replace(",", ".")
