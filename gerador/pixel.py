"""Desenho em pixel-art que vira SVG.

Uma unidade do viewBox é um pixel da arte; o navegador amplia com `crispEdges`.
O estado sem animação de cada cena é o quadro final, para que leitores que
ignoram CSS (prévias, apps) mostrem a cena pronta.
"""
import json
import math
from html import escape
from pathlib import Path

_FONTE = {int(k): v for k, v in json.loads((Path(__file__).parent / "fonte8x8.json").read_text())["glifos"].items()}
LARGURA_LETRA = 8


def _caminho_de_pixels(pixels):
    """Junta pixels em faixas horizontais: um único `d` por cor."""
    linhas = {}
    for x, y in pixels:
        linhas.setdefault(y, []).append(x)
    partes = []
    for y in sorted(linhas):
        xs = sorted(set(linhas[y]))
        inicio = anterior = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == anterior + 1:
                anterior = x
                continue
            partes.append(f"M{inicio} {y}h{anterior - inicio + 1}v1h{inicio - anterior - 1}z")
            if x is not None:
                inicio = anterior = x
    return "".join(partes)


class Camada:
    """Grupo de pixels por cor, que vira um <g> com um <path> por cor."""

    def __init__(self, classe=None, estilo=None, transformar=None):
        self.cores = {}
        self.filhos = []
        self.classe, self.estilo, self.transformar = classe, estilo, transformar

    def px(self, x, y, cor):
        """A última cor pintada num pixel é a que vale (como numa tela)."""
        if not cor:
            return
        ponto = (int(x), int(y))
        for outra, pixels in self.cores.items():
            if outra != cor:
                pixels.discard(ponto)
        self.cores.setdefault(cor, set()).add(ponto)

    def apagar(self, x, y):
        for pixels in self.cores.values():
            pixels.discard((int(x), int(y)))

    def ret(self, x, y, l, a, cor):
        for yy in range(int(y), int(y + a)):
            for xx in range(int(x), int(x + l)):
                self.px(xx, yy, cor)

    def elipse(self, cx, cy, rx, ry, cor):
        for yy in range(int(cy - ry), int(cy + ry) + 1):
            for xx in range(int(cx - rx), int(cx + rx) + 1):
                if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1:
                    self.px(xx, yy, cor)

    def linha(self, x0, y0, x1, y1, cor):
        passos = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(int(passos) + 1):
            self.px(round(x0 + (x1 - x0) * i / passos), round(y0 + (y1 - y0) * i / passos), cor)

    def sprite(self, x, y, desenho, paleta):
        """`desenho`: lista de strings; cada caractere é uma chave da `paleta` (`.` é vazio)."""
        for dy, linha in enumerate(desenho):
            for dx, c in enumerate(linha):
                if c != "." and c != " ":
                    self.px(x + dx, y + dy, paleta[c])

    def texto(self, x, y, s, cor, escala=1):
        """Texto na fonte 8x8, desenhado como pixels (não depende de fonte instalada)."""
        for i, ch in enumerate(s):
            glifo = _FONTE.get(ord(ch))
            if glifo is None:
                raise ValueError(f"sem glifo para {ch!r}")
            for linha, bits in enumerate(glifo):
                for coluna in range(8):
                    if bits >> coluna & 1:
                        self.ret(x + (i * LARGURA_LETRA + coluna) * escala, y + linha * escala, escala, escala, cor)

    def adicionar(self, camada):
        self.filhos.append(camada)
        return camada

    def svg(self):
        atributos = ""
        if self.classe:
            atributos += f' class="{self.classe}"'
        if self.estilo:
            atributos += f' style="{self.estilo}"'
        if self.transformar:
            atributos += f' transform="{self.transformar}"'
        corpo = "".join(f'<path fill="{cor}" d="{_caminho_de_pixels(p)}"/>' for cor, p in self.cores.items())
        corpo += "".join(f.svg() if isinstance(f, Camada) else f for f in self.filhos)
        return f"<g{atributos}>{corpo}</g>"


def largura_texto(s, escala=1):
    return len(s) * LARGURA_LETRA * escala


def documento(largura, altura, titulo, css, raiz):
    titulo = escape(titulo)
    movimento_reduzido = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura} {altura}" '
        f'width="{largura * 2}" height="{altura * 2}" shape-rendering="crispEdges" role="img" '
        f'aria-label="{titulo}"><title>{titulo}</title>'
        f"<style>{css}{movimento_reduzido}</style>{raiz.svg()}</svg>"
    )


def faixas(camada, x, y, l, a, cores):
    """Degradê em faixas horizontais (uma por cor), do topo para baixo."""
    altura_faixa = a / len(cores)
    for i, cor in enumerate(cores):
        y0 = round(y + i * altura_faixa)
        camada.ret(x, y0, l, round(y + (i + 1) * altura_faixa) - y0, cor)


def misturar(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(a[i] + (b[i] - a[i]) * t):02x}" for i in range(3))


def gradiente(c1, c2, n):
    return [misturar(c1, c2, i / max(n - 1, 1)) for i in range(n)]


def ruido(x, y, semente=0):
    """Pseudoaleatório estável por posição (a arte não muda entre gerações)."""
    v = math.sin(x * 12.9898 + y * 78.233 + semente * 37.719) * 43758.5453
    return v - math.floor(v)
