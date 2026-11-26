"""Linha do tempo: trilha de circuito impresso em duas faixas; um pulso percorre a trilha e, ao chegar em cada
nó, o ícone se desenha (stroke-dashoffset) e o ano aparece. O último nó ("agora") fica pulsando.

Datas conferidas: tear de Jacquard (patente de 1804), Notas de Ada Lovelace com a Nota G (1843),
Boole, "The Laws of Thought" (1854), Turing, "On Computable Numbers" (1936), ENIAC concluído e o
"First Draft of a Report on the EDVAC" de von Neumann (1945), transistor na Bell Labs (dez/1947) e a
mariposa no Harvard Mark II (9/set/1947, equipe de Grace Hopper), UNIX e Apollo 11 (1969), linguagem C (1972),
WWW pública e Linux (1991), Git (abr/2005).
"""
import math

from svgkit import Doc, ELASTICO, circulo, fmt, quadros, tempos_smil

L, A = 900, 364
Y1, Y2, YC = 96, 276, 192  # trilhas das duas faixas e o canal de retorno

MARCOS = [
    ("1804", "Jacquard", "tear de cartões", "jacquard"),
    ("1843", "Ada Lovelace", "Nota G", "nota"),
    ("1854", "George Boole", "álgebra booleana", "porta"),
    ("1936", "Alan Turing", "máquina universal", "fita"),
    ("1945", "ENIAC", "von Neumann", "valvula"),
    ("1947", "transistor", "Hopper · Mark II", "transistor"),
    ("1969", "UNIX · Apollo 11", "Margaret Hamilton", "lua"),
    ("1972", "linguagem C", "Dennis Ritchie", "chaves"),
    ("1991", "WWW · Linux", "Berners-Lee · Torvalds", "globo"),
    ("2005", "Git", "Linus Torvalds", "git"),
    ("agora", "você está aqui", "", "alvo"),
]
X1 = [66 + i * 148 for i in range(6)]
X2 = [100 + i * 175 for i in range(5)]

# Ícones de linha numa caixa 40×40 (traço 1,5). Um único path por ícone, desenhado de uma vez.
ICONES = {
    "jacquard": "M10 4H34V26H6V8Z"
                "M12 10.5a1.5 1.5 0 1 0 0.01 0M20 10.5a1.5 1.5 0 1 0 0.01 0M28 15.5a1.5 1.5 0 1 0 0.01 0"
                "M16 15.5a1.5 1.5 0 1 0 0.01 0M24 20.5a1.5 1.5 0 1 0 0.01 0M12 20.5a1.5 1.5 0 1 0 0.01 0"
                "M10 26V37M16 26V37M22 26V37M28 26V37M34 26V37",
    "nota": "M9 3H26L32 9V37H9ZM26 3V9H32M14 16H27M14 21H27M14 26H23M14 31H20",
    "porta": "M10 9H21A11 11 0 0 1 21 31H10ZM2 15H10M2 25H10M32 20H38",
    "fita": "M2 24H38V34H2ZM10 24V34M18 24V34M26 24V34M34 24V34M18 8H26V13L22 18L18 13Z",
    "valvula": "M13 33V15A7 7 0 0 1 27 15V33ZM16 33V38M20 33V38M24 33V38M16 20H24M16 24H24M17 29L20 26.5L23 29",
    "transistor": "M34 20A14 14 0 1 1 6 20A14 14 0 1 1 34 20M2 20H15M15 12V28M15 16L25 10V2M15 24L25 30V38"
                  "M20.5 29.2L25 30L23 25.8",
    "lua": "M25 5A15 15 0 1 0 35 27A12 12 0 1 1 25 5ZM31 8.5L32 6.5L33 8.5L35 9.5L33 10.5L32 12.5L31 10.5L29 9.5Z",
    "chaves": "M15 5C10 5 10 8 10 12V16C10 18.5 9 20 6 20C9 20 10 21.5 10 24V28C10 32 10 35 15 35"
              "M25 5C30 5 30 8 30 12V16C30 18.5 31 20 34 20C31 20 30 21.5 30 24V28C30 32 30 35 25 35",
    "globo": "M34 20A14 14 0 1 1 6 20A14 14 0 1 1 34 20M6 20H34M20 6C14 12 14 28 20 34C26 28 26 12 20 6"
             "M8.5 12.5H31.5M8.5 27.5H31.5",
    "git": "M15 8A3 3 0 1 1 9 8A3 3 0 1 1 15 8M15 32A3 3 0 1 1 9 32A3 3 0 1 1 15 32M31 16A3 3 0 1 1 25 16"
           "A3 3 0 1 1 31 16M12 11V29M28 19C28 25 18 23 13.5 29.5",
    "alvo": "M30 20A10 10 0 1 1 10 20A10 10 0 1 1 30 20M20 3V11M20 29V37M3 20H11M29 20H37",
}


def trilha() -> tuple[str, list[float], list[tuple[float, float]], float]:
    """Polilinha da trilha (com chanfros de 45°, como em PCB) e a distância de cada nó desde o início."""
    pts = [(20, Y1), (874, Y1), (890, Y1 + 16), (890, YC - 16), (874, YC), (38, YC), (22, YC + 16),
           (22, Y2 - 16), (38, Y2), (X2[-1], Y2)]
    d = "M" + "L".join(f"{x} {y}" for x, y in pts)
    acum = [0.0]
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        acum.append(acum[-1] + math.hypot(xb - xa, yb - ya))

    def distancia(x, y):
        for i, ((xa, ya), (xb, yb)) in enumerate(zip(pts, pts[1:])):
            if ya == yb == y and min(xa, xb) <= x <= max(xa, xb):
                return acum[i] + abs(x - xa)
        raise ValueError((x, y))

    nos = [(x, Y1) for x in X1] + [(x, Y2) for x in X2]
    return d, [distancia(x, y) for x, y in nos], nos, acum[-1]


def construir(tema: str) -> str:
    doc = Doc(L, A, "Linha do tempo da computação",
              "Trilha de circuito impresso com marcos: 1804 tear de Jacquard; 1843 Ada Lovelace, Nota G; "
              "1854 George Boole, álgebra booleana; 1936 Alan Turing, máquina universal; 1945 ENIAC e a "
              "arquitetura de von Neumann; 1947 transistor e a mariposa do Mark II, de Grace Hopper; 1969 UNIX "
              "e Apollo 11, Margaret Hamilton; 1972 linguagem C, Dennis Ritchie; 1991 WWW e Linux; 2005 Git; "
              "e agora, você está aqui.", tema)
    c, css = doc.c, doc.css
    d, dist, nos, total = trilha()

    # tempos de chegada: 0,5 s por trecho, 0,25 s parado em cada nó, retorno pelo canal mais longo
    inicio, parada, trecho, retorno = 0.5, 0.25, 0.5, 1.1
    chegadas = [inicio + 0.35]
    for i in range(1, len(nos)):
        chegadas.append(chegadas[-1] + parada + (retorno if i == len(X1) else trecho))
    fim = chegadas[-1]

    # pontos (tempo, fração do caminho): parado no início, vai ao nó, espera, segue
    pontos = [(0.0, 0.0), (inicio, 0.0)]
    for i, (t, s) in enumerate(zip(chegadas, dist)):
        pontos.append((t, s / total))
        if i < len(nos) - 1:
            pontos.append((t + parada, s / total))
    curva = ".45,0,.2,1"
    css.append(quadros("acende", [(t, f"stroke-dashoffset:{fmt(1 - f, 4)}") for t, f in pontos], fim)
               + f".acesa{{stroke-dasharray:1;animation:acende {fim:.2f}s cubic-bezier({curva}) both}}")

    # máscara: a trilha é interrompida dentro de cada pad (sem depender da cor do fundo)
    furos = "".join(f'<circle cx="{x}" cy="{y}" r="7.5" fill="#000"/>' for x, y in nos)
    doc.defs.append(f'<mask id="pads" maskUnits="userSpaceOnUse" x="0" y="0" width="{L}" height="{A}">'
                    f'<rect width="{L}" height="{A}" fill="#fff"/>{furos}<circle cx="20" cy="{Y1}" r="4" fill="#000"/></mask>')
    doc.corpo.append(f'<g mask="url(#pads)"><path d="{d}" stroke="{c["traco"]}" stroke-opacity="{doc.op(.26)}" stroke-width="1.5"/>'
                     f'<path class="acesa" pathLength="1" d="{d}" stroke="{c["ambar"]}" stroke-width="1.5"/></g>'
                     f'<path d="{circulo(20, Y1, 4)}" stroke="{c["traco"]}" stroke-opacity="{doc.op(.5)}" stroke-width="1.2"/>')

    css.append("@keyframes desenha{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
               ".ic{stroke-dasharray:1;animation:desenha .9s cubic-bezier(.5,0,.25,1) both}"
               "@keyframes rot{from{opacity:0;transform:translateY(6px)}}"
               f".rot{{animation:rot .55s {ELASTICO} both}}"
               "@keyframes liga{from{opacity:0;transform:scale(0)}}"
               ".nucleo{transform-box:fill-box;transform-origin:center;animation:liga .3s cubic-bezier(.3,1.5,.5,1) both}")
    partes = []
    for i, ((x, y), t, (ano, titulo, sub, icone)) in enumerate(zip(nos, chegadas, MARCOS)):
        ultimo = i == len(nos) - 1
        partes.append(f'<path d="{circulo(x, y, 5.5)}" stroke="{c["traco"]}" stroke-opacity="{doc.op(.6)}" stroke-width="1.2"/>')
        # o último núcleo tem duas animações (liga + bate) com atrasos próprios na classe .agora
        estilo = "" if ultimo else f' style="animation-delay:{t:.2f}s"'
        partes.append(f'<circle class="{"agora" if ultimo else "nucleo"}"{estilo} '
                      f'cx="{x}" cy="{y}" r="3" fill="{c["ambar"]}"/>')
        partes.append(f'<path class="ic" pathLength="1" style="animation-delay:{t:.2f}s" '
                      f'transform="translate({x - 20} {y - 66})" d="{ICONES[icone]}" '
                      f'stroke="{c["ambar"] if ultimo else c["tinta"]}" stroke-width="1.5" '
                      f'stroke-linecap="round" stroke-linejoin="round"/>')
        rot = [doc.t(ano, x, y + 32, 17, "ambar", peso="m", ancora="middle"),
               doc.t(titulo, x, y + 54, 15, "tinta", ancora="middle")]
        if sub:
            rot.append(doc.t(sub, x, y + 74, 14, "suave", ancora="middle"))
        partes.append(f'<g class="rot" style="animation-delay:{t + 0.1:.2f}s">{"".join(rot)}</g>')
    xa, ya = nos[-1]
    css.append("@keyframes onda{0%{opacity:.9;transform:scale(1)}70%,100%{opacity:0;transform:scale(3.2)}}"
               f".onda{{transform-box:fill-box;transform-origin:center;opacity:0;"
               f"animation:onda 2.4s cubic-bezier(.2,.6,.3,1) {fim + 0.2:.2f}s infinite}}"
               "@keyframes bate{0%,55%{opacity:1}75%,90%{opacity:.25}100%{opacity:1}}"
               f".agora{{transform-box:fill-box;transform-origin:center;animation:liga .3s cubic-bezier(.3,1.5,.5,1) {fim:.2f}s both,bate 2.4s ease-in-out {fim + 0.2:.2f}s infinite}}")
    partes.append(f'<circle class="onda" cx="{xa}" cy="{ya}" r="5.5" stroke="{c["ambar"]}" stroke-width="1"/>')
    doc.corpo.append("".join(partes))

    # pulso (SMIL animateMotion): mesmos tempos e mesma easing da trilha acesa
    tempos = [t for t, _ in pontos]
    chaves = ";".join(fmt(f, 4) for _, f in pontos)
    splines = ";".join(["0.45 0 0.2 1"] * (len(pontos) - 1))
    doc.corpo.append(
        f'<g class="rm-hide"><g opacity="1"><circle r="9" fill="{c["ambar"]}" fill-opacity=".16"/>'
        f'<circle r="3.2" fill="{c["ambar"]}"/>'
        f'<animateMotion dur="{fim:.2f}s" fill="freeze" calcMode="spline" path="{d}" keyPoints="{chaves}" '
        f'keyTimes="{tempos_smil(tempos, fim)}" keySplines="{splines}"/>'
        f'<animate attributeName="opacity" dur="{fim + 0.3:.2f}s" fill="freeze" values="1;1;0" '
        f'keyTimes="0;{fmt(fim / (fim + 0.3), 4)};1"/></g></g>')
    return doc.render()
