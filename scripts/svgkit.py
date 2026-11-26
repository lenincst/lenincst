"""Esqueleto comum dos SVGs: fonte embutida (subset), tema, acessibilidade e utilidades de animação.

Regras que valem para todas as peças (o GitHub exibe os SVGs via <img>):
- nada externo: a fonte vai em base64 dentro do próprio SVG, só com os glifos usados;
- animação só em CSS (@keyframes) e SMIL, nunca JavaScript;
- o estilo "de repouso" de cada elemento é o quadro final: com prefers-reduced-motion as animações CSS
  são desligadas e o que é SMIL fica em grupos `.rm-hide`, trocados por um quadro estático `.rm-show`.
"""
from __future__ import annotations

import base64
import io
import json
import logging
from html import escape
from pathlib import Path

from fontTools import subset
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

logging.getLogger("fontTools.subset").setLevel(logging.ERROR)  # avisos sobre tabelas descartadas (meta)

AQUI = Path(__file__).resolve().parent
PALETA = json.loads((AQUI / "palette.json").read_text(encoding="utf-8"))
ICONES = json.loads((AQUI / "icons.json").read_text(encoding="utf-8"))["icones"]

# Fontes (IBM Plex, SIL OFL 1.1 — ver scripts/fonts/OFL.txt). "Plex" é Reserved Font Name: o subset
# embutido é uma versão modificada, então é renomeado (família "LCR Mono") e mantém copyright e licença.
FONTES = {
    "r": AQUI / "fonts" / "IBMPlexMono-Regular.ttf",
    "m": AQUI / "fonts" / "IBMPlexMono-Medium.ttf",
}
PESO = {"r": 400, "m": 500}
FAMILIA = "LCR Mono"
RESERVA = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
AVANCO = 0.6  # IBM Plex Mono: todo glifo avança 600/1000 em (conferido em _subset)

TEMAS = ("dark", "light")


def fmt(v: float, casas: int = 2) -> str:
    """Número curto para SVG: sem zeros à direita nem "-0"."""
    s = f"{v:.{casas}f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def largura(s: str, tamanho: float) -> float:
    return len(s) * AVANCO * tamanho


def _subset(caminho: Path, chars: set[str]) -> bytes:
    fonte = TTFont(caminho, recalcTimestamp=False)  # build reprodutível: mesma entrada, mesmos bytes
    cmap = fonte.getBestCmap()
    for ch in chars:
        if ord(ch) not in cmap:
            raise ValueError(f"glifo ausente em {caminho.name}: {ch!r} (U+{ord(ch):04X})")
        if fonte["hmtx"][cmap[ord(ch)]][0] != 600:
            raise ValueError(f"glifo {ch!r} não é monoespaçado em {caminho.name}")
    opcoes = subset.Options()
    opcoes.flavor = "woff2"
    opcoes.layout_features = []
    opcoes.hinting = False
    opcoes.desubroutinize = True
    opcoes.name_IDs = [0, 13, 14]  # copyright e licença; o nome é regravado abaixo
    opcoes.notdef_outline = False
    sub = subset.Subsetter(opcoes)
    sub.populate(unicodes={ord(c) for c in chars | {" "}})
    sub.subset(fonte)
    nomes = fonte["name"]
    for nid, valor in ((1, FAMILIA), (2, "Regular"), (4, FAMILIA), (6, FAMILIA.replace(" ", ""))):
        nomes.setName(valor, nid, 3, 1, 0x409)
    buf = io.BytesIO()
    fonte.save(buf)
    return buf.getvalue()


def contorno_glifos(caminho: Path, texto: str, tamanho: float, x: float, y: float) -> list[tuple[str, str, float]]:
    """Contornos (path d) de cada glifo, com a linha de base em y. Devolve [(char, d, avanço)]."""
    fonte = TTFont(caminho)
    cmap, glifos, hmtx = fonte.getBestCmap(), fonte.getGlyphSet(), fonte["hmtx"]
    k = tamanho / fonte["head"].unitsPerEm
    saida, cursor = [], x
    for ch in texto:
        nome = cmap[ord(ch)]
        caneta = SVGPathPen(glifos, ntos=lambda v: fmt(v, 1))
        glifos[nome].draw(TransformPen(caneta, (k, 0, 0, -k, cursor, y)))
        avanco = hmtx[nome][0] * k
        saida.append((ch, caneta.getCommands(), avanco))
        cursor += avanco
    return saida


class Doc:
    """Um SVG em construção. `tema` escolhe as cores; `t()` registra os glifos para o subset."""

    def __init__(self, largura_: float, altura: float, titulo: str, descricao: str, tema: str):
        self.w, self.h = largura_, altura
        self.titulo, self.descricao = titulo, descricao
        self.tema = tema
        self.c = PALETA[tema]
        self.css: list[str] = []
        self.defs: list[str] = []
        self.corpo: list[str] = []
        self._chars = {k: set() for k in FONTES}

    # ------------------------------------------------------------------ texto
    def t(self, s: str, x: float, y: float, tam: float, cor: str, peso: str = "r", ancora: str = "start",
          cls: str = "", estilo: str = "", extra: str = "") -> str:
        """<text> em Plex Mono. `cor` é uma chave da paleta ou uma cor literal."""
        self._chars[peso].update(s)
        cor = self.c.get(cor, cor)
        a = f' text-anchor="{ancora}"' if ancora != "start" else ""
        c = f' class="{cls}"' if cls else ""
        st = f' style="{estilo}"' if estilo else ""
        return (f'<text x="{fmt(x)}" y="{fmt(y)}" font-size="{fmt(tam)}" font-weight="{PESO[peso]}" '
                f'fill="{cor}"{a}{c}{st}{extra}>{escape(s)}</text>')

    def usa(self, s: str, peso: str = "r") -> None:
        """Registra glifos usados fora de t() (ex.: texto montado à mão)."""
        self._chars[peso].update(s)

    # ------------------------------------------------------------------ saída
    def render(self) -> str:
        faces = []
        for peso, chars in self._chars.items():
            if not chars:
                continue
            dados = base64.b64encode(_subset(FONTES[peso], chars)).decode()
            faces.append(f'@font-face{{font-family:"{FAMILIA}";font-weight:{PESO[peso]};'
                         f'src:url(data:font/woff2;base64,{dados}) format("woff2")}}')
        base = (f'text{{font-family:"{FAMILIA}",{RESERVA};font-variant-ligatures:none}}'
                ".rm-show{display:none}"
                "@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}"
                ".rm-hide{display:none!important}.rm-show{display:inline!important}}")
        estilo = "".join(faces) + base + "".join(self.css)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {fmt(self.w)} {fmt(self.h)}" '
                f'width="{fmt(self.w)}" height="{fmt(self.h)}" role="img" aria-labelledby="t d" fill="none">'
                f'<title id="t">{escape(self.titulo)}</title><desc id="d">{escape(self.descricao)}</desc>'
                f'<style>{estilo}</style><defs>{"".join(self.defs)}</defs>{"".join(self.corpo)}</svg>\n')


# ---------------------------------------------------------------------- animação
def bezier(p1x: float, p1y: float, p2x: float, p2y: float):
    """Curva cubic-bezier do CSS: devolve (x(u), y(u)) para u em [0, 1]."""
    def eixo(a, b, u):
        return 3 * a * u * (1 - u) ** 2 + 3 * b * u * u * (1 - u) + u ** 3
    return (lambda u: eixo(p1x, p2x, u)), (lambda u: eixo(p1y, p2y, u))


def tempo_para_progresso(curva: tuple[float, float, float, float], alvo: float) -> float:
    """Fração do tempo em que a easing `curva` atinge `alvo` de progresso (inversa por bisseção)."""
    bx, by = bezier(*curva)
    lo, hi = 0.0, 1.0
    for _ in range(60):
        meio = (lo + hi) / 2
        if by(meio) < alvo:
            lo = meio
        else:
            hi = meio
    return bx((lo + hi) / 2)


def quadros(nome: str, pontos: list[tuple[float, str]], total: float) -> str:
    """@keyframes a partir de (tempo em s, declarações). Tempos viram porcentagens de `total`."""
    partes = []
    for t, decl in pontos:
        p = max(0.0, min(100.0, 100 * t / total))
        partes.append(f"{fmt(p, 3)}%{{{decl}}}")
    return f"@keyframes {nome}{{{''.join(partes)}}}"


def tempos_smil(tempos: list[float], total: float) -> str:
    return ";".join(fmt(t / total, 4) for t in tempos)


def discreto(atributo: str, eventos: list[tuple[float, str]], total: float, extra: str = "") -> str:
    """<animate> discreto e cíclico a partir de (tempo, valor); repete valores só quando mudam."""
    eventos = sorted(eventos)
    if eventos[0][0] > 0:
        raise ValueError("o primeiro evento precisa estar em t=0")
    tempos, valores = [], []
    for t, v in eventos:
        if valores and v == valores[-1]:
            continue
        if tempos and t <= tempos[-1]:
            tempos[-1], valores[-1] = t, v  # mesmo instante: vale o último
            continue
        tempos.append(t)
        valores.append(v)
    return (f'<animate attributeName="{atributo}" calcMode="discrete" dur="{fmt(total, 3)}s" repeatCount="indefinite" '
            f'values="{";".join(valores)}" keyTimes="{tempos_smil(tempos, total)}"{extra}/>')


def retangulo(x: float, y: float, w: float, h: float, r: float) -> str:
    """Retângulo arredondado como <path> (para desenhar com stroke-dashoffset e pathLength)."""
    return (f"M{fmt(x + r)} {fmt(y)}H{fmt(x + w - r)}A{fmt(r)} {fmt(r)} 0 0 1 {fmt(x + w)} {fmt(y + r)}"
            f"V{fmt(y + h - r)}A{fmt(r)} {fmt(r)} 0 0 1 {fmt(x + w - r)} {fmt(y + h)}H{fmt(x + r)}"
            f"A{fmt(r)} {fmt(r)} 0 0 1 {fmt(x)} {fmt(y + h - r)}V{fmt(y + r)}A{fmt(r)} {fmt(r)} 0 0 1 {fmt(x + r)} {fmt(y)}Z")


def circulo(cx: float, cy: float, r: float) -> str:
    """Círculo como <path> (dois arcos), começando à direita."""
    return (f"M{fmt(cx + r)} {fmt(cy)}A{fmt(r)} {fmt(r)} 0 1 1 {fmt(cx - r)} {fmt(cy)}"
            f"A{fmt(r)} {fmt(r)} 0 1 1 {fmt(cx + r)} {fmt(cy)}")


ELASTICO = "cubic-bezier(.2,.75,.25,1)"   # entradas: rápido no começo, assenta devagar
SUAVE = "cubic-bezier(.45,0,.2,1)"        # deslocamentos coreografados
