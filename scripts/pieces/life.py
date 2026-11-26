"""Divisor: Jogo da Vida de Conway (B3/S23), dois planadores atravessando a faixa.

A faixa é um toro de 64×8 células. Um planador anda (1, 1) a cada 4 gerações, então volta à posição inicial
depois de mmc(64, 8) = 64 deslocamentos = 256 gerações: o ciclo fecha sem salto (conferido na simulação).
Cada célula tem um <animate> discreto de opacidade com os estados gerados pela simulação (viva, recém-morta
como rastro de fósforo, vazia).
"""
import math

from svgkit import Doc, discreto, fmt

L, A = 900, 110
COLS, LINS = 64, 8
CEL = 12.5
X0, Y0 = 100, 5
GERACAO = 0.125  # s
PLANADOR = [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]  # rumo sudeste
INICIAIS = [(3, 1), (35, 4)]


def passo(vivas: set[tuple[int, int]]) -> set[tuple[int, int]]:
    contagem: dict[tuple[int, int], int] = {}
    for x, y in vivas:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    p = ((x + dx) % COLS, (y + dy) % LINS)
                    contagem[p] = contagem.get(p, 0) + 1
    return {p for p, n in contagem.items() if n == 3 or (n == 2 and p in vivas)}


def simular() -> list[set[tuple[int, int]]]:
    vivas = {((ox + dx) % COLS, (oy + dy) % LINS) for ox, oy in INICIAIS for dx, dy in PLANADOR}
    geracoes = [vivas]
    periodo = 4 * math.lcm(COLS, LINS)
    for _ in range(periodo):
        geracoes.append(passo(geracoes[-1]))
    assert geracoes[-1] == geracoes[0], "o ciclo não fecha"
    assert all(len(g) == 5 * len(INICIAIS) for g in geracoes), "os planadores interagiram"
    return geracoes[:-1]


def construir(tema: str) -> str:
    doc = Doc(L, A, "Jogo da Vida de Conway",
              "Dois planadores do Jogo da Vida de Conway, regra B3/S23, de 1970, atravessam uma faixa "
              "quadriculada; as gerações foram calculadas pelo script.", tema)
    c = doc.c
    geracoes = simular()
    D = len(geracoes) * GERACAO

    grade = "".join(f"M{fmt(X0 + i * CEL)} {Y0}v{LINS * CEL}" for i in range(COLS + 1))
    grade += "".join(f"M{X0} {fmt(Y0 + j * CEL)}h{COLS * CEL}" for j in range(LINS + 1))
    partes = [doc.t("B3/S23", 24, 42, 15, "tinta"), doc.t("Conway", 24, 64, 14, "suave"),
              doc.t("1970", 24, 86, 14, "ambar", peso="m"),
              f'<path d="{grade}" stroke="{c["grade"]}" stroke-opacity="{float(c["grade_op"]) * 1.6:.3f}" stroke-width=".6"/>']

    cor = c["ambar"]
    tocadas = sorted(set().union(*geracoes), key=lambda p: (p[1], p[0]))
    celulas = []
    for x, y in tocadas:
        ev = []
        for g, vivas in enumerate(geracoes):
            anterior = geracoes[g - 1]  # g=0 olha a última geração (ciclo)
            v = "1" if (x, y) in vivas else (".22" if (x, y) in anterior else "0")
            ev.append((g * GERACAO, v))
        celulas.append(f'<rect x="{fmt(X0 + x * CEL + 1)}" y="{fmt(Y0 + y * CEL + 1)}" width="10.5" height="10.5" '
                       f'rx="1.5" fill="{cor}" opacity="{ev[0][1]}">{discreto("opacity", ev, D)}</rect>')
    partes.append(f'<g class="rm-hide">{"".join(celulas)}</g>')
    estatico = "".join(f'<rect x="{fmt(X0 + x * CEL + 1)}" y="{fmt(Y0 + y * CEL + 1)}" width="10.5" height="10.5" '
                       f'rx="1.5" fill="{cor}"/>' for x, y in sorted(geracoes[0]))
    partes.append(f'<g class="rm-show">{estatico}</g>')
    doc.corpo.append("".join(partes))
    return doc.render()
