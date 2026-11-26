"""Epiciclos de Fourier desenhando um λ (cálculo lambda, Church, 1936) e e^{iπ} + 1 = 0 em caligrafia.

1. O λ é construído pelo script: traços com espessura variável carimbados numa grade, contorno extraído
   (Moore-neighbor) e reamostrado por comprimento de arco (N pontos).
2. DFT direta: c_k = (1/N) Σ z_n e^{-2πikn/N}. Ficam os TERMOS coeficientes de maior módulo (k ≠ 0).
3. Cada termo vira um <g> aninhado que gira com <animateTransform type="rotate">; como os grupos são
   aninhados, cada um gira em relação ao pai: Δk = k_j − k_{j−1} voltas por período e fase arg(c_j) − arg(c_{j−1}).
4. O traço do λ é a própria série truncada; o stroke-dashoffset segue o comprimento de arco real em função do
   tempo (keyframes calculados), então a ponta e o traço andam juntos.
"""
import cmath
import math

from svgkit import AQUI, Doc, ELASTICO, contorno_glifos, fmt, quadros

L, A = 900, 360
TERMOS = 35
N = 512
PERIODO = 12.0  # s por volta completa (o λ inteiro)
CENTRO = complex(250, 182)
ALTURA_LAMBDA = 262


# ---------------------------------------------------------------------- o λ
def _bezier(p0, p1, p2, p3, n):
    for i in range(n + 1):
        u = i / n
        yield ((1 - u) ** 3 * p0 + 3 * (1 - u) ** 2 * u * p1 + 3 * (1 - u) * u * u * p2 + u ** 3 * p3)


def _tracos():
    """Linhas-mestras do λ (coordenadas numa caixa ~200×260, y para baixo) com a meia-espessura em cada ponto."""
    principal = list(_bezier(complex(20, 22), complex(42, 2), complex(70, 8), complex(86, 50), 60))
    principal += [complex(86, 50) + (complex(178, 238) - complex(86, 50)) * (i / 120) for i in range(1, 121)]
    principal += list(_bezier(complex(178, 238), complex(184, 252), complex(194, 254), complex(204, 244), 30))[1:]
    n = len(principal)
    pts = []
    for i, p in enumerate(principal):
        f = i / (n - 1)
        if f < 0.22:
            w = 6 + (13 - 6) * (f / 0.22)          # cauda fina que engrossa
        elif f < 0.9:
            w = 13
        else:
            w = 13 - 5 * ((f - 0.9) / 0.1)         # pé afinando
        pts.append((p, w))
    perna = [complex(118, 118) + (complex(20, 246) - complex(118, 118)) * (i / 140) for i in range(141)]
    pts += [(p, 11.5 - 2.5 * i / 140) for i, p in enumerate(perna)]
    return pts


def contorno_lambda() -> list[complex]:
    escala = 2  # grade com meio pixel
    largura, altura = 240 * escala, 290 * escala
    grade = [[False] * largura for _ in range(altura)]
    for p, w in _tracos():
        cx, cy, r = (p.real + 10) * escala, (p.imag + 10) * escala, w * escala
        for y in range(max(0, int(cy - r)), min(altura, int(cy + r) + 2)):
            dy = y - cy
            meia = r * r - dy * dy
            if meia < 0:
                continue
            dx = math.sqrt(meia)
            for x in range(max(0, int(cx - dx)), min(largura, int(cx + dx) + 2)):
                grade[y][x] = True
    # Moore-neighbor: percorre a borda no sentido horário a partir do pixel mais acima/à esquerda
    viz = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    inicio = next((x, y) for y in range(altura) for x in range(largura) if grade[y][x])
    atual, volta = inicio, 4  # chegou-se pelo oeste
    borda = [inicio]
    for _ in range(200000):
        for i in range(1, 9):
            d = (volta + i) % 8
            nx, ny = atual[0] + viz[d][0], atual[1] + viz[d][1]
            if 0 <= nx < largura and 0 <= ny < altura and grade[ny][nx]:
                px, py = atual[0] + viz[(volta + i - 1) % 8][0], atual[1] + viz[(volta + i - 1) % 8][1]
                volta = viz.index((px - nx, py - ny))
                atual = (nx, ny)
                break
        if atual == inicio:
            break
        borda.append(atual)
    else:
        raise RuntimeError("contorno do λ não fechou")
    pts = [complex(x, y) / escala for x, y in borda]
    # suaviza a escada de pixels (média móvel circular) e reamostra por comprimento de arco
    j = 4
    pts = [sum(pts[(i + k) % len(pts)] for k in range(-j, j + 1)) / (2 * j + 1) for i in range(len(pts))]
    return reamostrar(pts, N)


def reamostrar(pts: list[complex], n: int) -> list[complex]:
    fechado = pts + [pts[0]]
    acum = [0.0]
    for a, b in zip(fechado, fechado[1:]):
        acum.append(acum[-1] + abs(b - a))
    total, saida, seg = acum[-1], [], 0
    for i in range(n):
        alvo = total * i / n
        while acum[seg + 1] < alvo:
            seg += 1
        f = (alvo - acum[seg]) / ((acum[seg + 1] - acum[seg]) or 1)
        saida.append(fechado[seg] + (fechado[seg + 1] - fechado[seg]) * f)
    return saida


def dft(z: list[complex]) -> list[tuple[int, complex]]:
    n = len(z)
    coef = []
    for k in range(-n // 2, n // 2):
        s = sum(z[m] * cmath.exp(-2j * math.pi * k * m / n) for m in range(n)) / n
        coef.append((k, s))
    return coef


def serie(termos: list[tuple[int, complex]], t: float) -> complex:
    return sum(c * cmath.exp(2j * math.pi * k * t) for k, c in termos)


# ---------------------------------------------------------------------- SVG
def construir(tema: str) -> str:
    doc = Doc(L, A, "Epiciclos de Fourier desenhando a letra lambda",
              f"{TERMOS} epiciclos, calculados por transformada discreta de Fourier, desenham um lambda, "
              "homenagem ao cálculo lambda de Alonzo Church, de 1936. Ao lado, a identidade de Euler, "
              "e elevado a i pi mais 1 igual a 0, escrita como caligrafia.", tema)
    c, css = doc.c, doc.css

    z = contorno_lambda()
    # escala e centraliza (o termo k=0 é o centroide; vira a translação base)
    ys = [p.imag for p in z]
    k_esc = ALTURA_LAMBDA / (max(ys) - min(ys))
    media = sum(z) / len(z)
    z = [(p - media) * k_esc for p in z]
    coef = dft(z)
    termos = sorted((t for t in coef if t[0] != 0), key=lambda t: -abs(t[1]))[:TERMOS]
    c0 = dict(coef)[0]  # ~0 depois de centralizar

    # curva reconstruída e comprimento de arco em função do tempo
    M = 720
    curva = [CENTRO + c0 + serie(termos, i / M) for i in range(M + 1)]
    acum = [0.0]
    for a, b in zip(curva, curva[1:]):
        acum.append(acum[-1] + abs(b - a))
    total = acum[-1]
    d_curva = "M" + "L".join(f"{fmt(p.real, 1)} {fmt(p.imag, 1)}" for p in curva[:-1]) + "Z"
    paradas = [(PERIODO * i / 72, f"stroke-dashoffset:{fmt(1 - acum[i * M // 72] / total, 4)}") for i in range(73)]
    css.append(quadros("traca", paradas, PERIODO)
               + f".lambda{{stroke-dasharray:1;animation:traca {PERIODO}s linear .6s both}}")

    # epiciclos aninhados
    css.append("@keyframes recua{to{opacity:.42}}"
               f".epi{{animation:recua 1.6s ease-in-out {PERIODO + 0.6:.1f}s both}}")
    abre, fecha = [], []
    ang_pai, k_pai = 0.0, 0
    for k, cf in termos:
        r = abs(cf)
        ang = math.degrees(cmath.phase(cf))
        rel, dk = ang - ang_pai, k - k_pai
        circulo = (f'<circle r="{fmt(r, 2)}" stroke="{c["traco"]}" stroke-opacity=".2" stroke-width=".8"/>'
                   if r >= 1.2 else "")
        abre.append(f'<g><animateTransform attributeName="transform" type="rotate" from="{fmt(rel, 3)}" '
                    f'to="{fmt(rel + 360 * dk, 3)}" dur="{PERIODO}s" begin=".6s" repeatCount="indefinite"/>'
                    f'{circulo}<path d="M0 0H{fmt(r, 2)}" stroke="{c["traco"]}" stroke-opacity=".5" stroke-width=".9"/>'
                    f'<g transform="translate({fmt(r, 2)} 0)">')
        fecha.append("</g></g>")
        ang_pai, k_pai = ang, k
    ponta = f'<circle r="3" fill="{c["ambar"]}"/><circle r="7" fill="{c["ambar"]}" fill-opacity=".18"/>'
    # antes de começar (begin=.6s) cada grupo precisa já estar na fase inicial: transform estático igual ao "from"
    epiciclos = "".join(abre) + ponta + "".join(fecha)
    epiciclos = _fase_inicial(epiciclos, termos)
    doc.corpo.append(
        f'<path class="lambda" pathLength="1" d="{d_curva}" stroke="{c["ambar"]}" stroke-width="1.8" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
        f'<g class="rm-hide"><g class="epi" transform="translate({fmt((CENTRO + c0).real)} {fmt((CENTRO + c0).imag)})">'
        f'{epiciclos}</g></g>')

    # ---------------- identidade de Euler em caligrafia (contornos do IBM Plex Serif Italic)
    serif = AQUI / "fonts" / "IBMPlexSerif-Italic.ttf"
    x, base, tam, sup = 586, 150, 60, 34
    glifos = []
    for ch, d, av in contorno_glifos(serif, "e", tam, x, base):
        glifos.append(d)
        x += av
    x += 2
    for ch, d, av in contorno_glifos(serif, "iπ", sup, x, base - 30):
        glifos.append(d)
        x += av
    x += 10
    for ch, d, av in contorno_glifos(serif, " + 1 = 0", tam, x, base):
        if d:
            glifos.append(d)
        x += av
    assert x < L - 8, f"identidade não cabe: {x}"
    css.append("@keyframes caneta{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
               "@keyframes tinta{from{fill-opacity:0}}"
               ".gl{stroke-dasharray:1;animation:caneta .9s cubic-bezier(.55,0,.35,1) both,"
               "tinta .6s ease-out both}")
    t = 1.2
    for d in glifos:
        doc.corpo.append(f'<path class="gl" pathLength="1" style="animation-delay:{t:.2f}s,{t + 0.7:.2f}s" d="{d}" '
                         f'fill="{c["tinta"]}" stroke="{c["tinta"]}" stroke-width=".9" stroke-linejoin="round"/>')
        t += 0.42
    css.append(f"@keyframes leg{{from{{opacity:0;transform:translateY(6px)}}}}.leg{{animation:leg .7s {ELASTICO} both}}")
    doc.corpo.append(f'<g class="leg" style="animation-delay:{t:.2f}s">'
                     + doc.t("cálculo lambda — Church, 1936", 588, 218, 15, "tinta")
                     + doc.t(f"série de Fourier · {TERMOS} epiciclos", 588, 244, 14, "suave") + "</g>")
    return doc.render()


def _fase_inicial(svg: str, termos) -> str:
    """Põe em cada <g> animado um transform="rotate(fase)" igual ao `from`, para o quadro antes do begin."""
    partes = svg.split('<g><animateTransform attributeName="transform" type="rotate" from="')
    saida = [partes[0]]
    for p in partes[1:]:
        fase = p.split('"', 1)[0]
        saida.append(f'<g transform="rotate({fase})"><animateTransform attributeName="transform" type="rotate" from="{p}')
    return "".join(saida)
