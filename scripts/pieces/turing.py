"""Divisor: Máquina de Turing de incremento binário, simulada pelo script (nada escrito à mão).

q0 anda para a direita até o primeiro branco e volta (q1); q1 propaga o "vai um": 1→0 e segue à esquerda,
0 ou branco → 1 e para. Com a fita 1011 a máquina faz 8 transições e para com 1100 (11 + 1 = 12).
"""
from svgkit import Doc, discreto, fmt

L, A = 900, 120
BRANCO = "_"
ENTRADA = "1011"
DELTA = {  # (estado, lido) -> (escreve, move, próximo)
    ("q0", "0"): ("0", "R", "q0"),
    ("q0", "1"): ("1", "R", "q0"),
    ("q0", BRANCO): (BRANCO, "L", "q1"),
    ("q1", "1"): ("0", "L", "q1"),
    ("q1", "0"): ("1", "N", "halt"),
    ("q1", BRANCO): ("1", "N", "halt"),
}
CELULAS = 8
INICIO = 1  # a entrada ocupa as células 1..4; a 0 e as 5..7 são brancos


def simular():
    fita = [BRANCO] * CELULAS
    for i, s in enumerate(ENTRADA):
        fita[INICIO + i] = s
    cabeca, estado, passos = INICIO, "q0", []
    while estado != "halt":
        lido = fita[cabeca]
        escreve, move, prox = DELTA[(estado, lido)]
        nova = cabeca + {"L": -1, "R": 1, "N": 0}[move]
        passos.append(dict(estado=estado, cabeca=cabeca, lido=lido, escreve=escreve, move=move, prox=prox, nova=nova))
        fita[cabeca] = escreve
        cabeca, estado = nova, prox
        if not 0 <= cabeca < CELULAS:
            raise RuntimeError("a fita desenhada é curta demais")
    resultado = "".join(fita).strip(BRANCO)
    assert resultado == format(int(ENTRADA, 2) + 1, "b"), resultado
    return passos, fita


def construir(tema: str) -> str:
    doc = Doc(L, A, "Máquina de Turing: incremento binário",
              "Uma máquina de Turing soma 1 a 1011: a cabeça percorre a fita para a direita, volta propagando o "
              "vai um e para no estado halt com a fita 1100.", tema)
    c = doc.c
    passos, fita_final = simular()

    x0, y0, cw = 232, 52, 44
    def cx(i):
        return x0 + i * cw + cw / 2

    passo, t0 = 0.8, 0.8
    T = [t0 + k * passo for k in range(len(passos))]
    t_para = T[-1] + 0.35
    D = T[-1] + passo + 2.6          # ciclo completo
    some, volta = D - 0.9, D - 0.5   # some no fim do ciclo e reinicia

    # moldura da fita (com continuação tracejada: a fita é infinita)
    fixo = [doc.t("máquina de Turing", 24, 54, 15, "tinta"),
            doc.t("incremento binário", 24, 78, 14, "suave"),
            f'<path d="M{x0} {y0}h{CELULAS * cw}M{x0} {y0 + cw}h{CELULAS * cw}'
            + "".join(f"M{x0 + i * cw} {y0}v{cw}" for i in range(CELULAS + 1))
            + f'" stroke="{c["traco"]}" stroke-opacity=".45" stroke-width="1"/>'
            f'<path d="M{x0 - 26} {y0}h22M{x0 - 26} {y0 + cw}h22M{x0 + CELULAS * cw + 4} {y0}h22'
            f'M{x0 + CELULAS * cw + 4} {y0 + cw}h22" stroke="{c["traco"]}" stroke-opacity=".3" stroke-dasharray="3 4"/>',
            doc.t("estado", 640, 60, 14, "suave")]

    def quadro_estatico() -> str:
        """Quadro final (para prefers-reduced-motion): fita 1100, halt, última transição."""
        p = passos[-1]
        s = [doc.t(v, cx(i), y0 + 30, 20, "tinta", peso="m", ancora="middle") for i, v in enumerate(fita_final) if v != BRANCO]
        s.append(cabeca_svg(cx(p["nova"])))
        s.append(doc.t("halt", 708, 60, 18, "ambar", peso="m"))
        s.append(doc.t(rotulo(p), 640, 90, 16, "tinta"))
        return f'<g class="rm-show">{"".join(s)}</g>'

    def cabeca_svg(x: float, anima: str = "", luz: str = "") -> str:
        return (f'<g transform="translate({fmt(x)} 0)">{anima}'
                f'<rect x="-20" y="{y0 + 2}" width="40" height="{cw - 4}" rx="2" fill="{c["ambar"]}" fill-opacity=".12">{luz}</rect>'
                f'<path d="M-10 14H10V30L0 40L-10 30Z" stroke="{c["ambar"]}" stroke-width="1.4" stroke-linejoin="round"/>'
                f'<circle cy="22" r="2" fill="{c["ambar"]}"/></g>')

    def rotulo(p) -> str:
        return f'({p["estado"]}, {p["lido"]}) → ({p["prox"]}, {p["escreve"]}, {p["move"]})'

    # ---- símbolos: um <text> por (célula, símbolo), opacidade discreta ao longo do ciclo
    fita = [BRANCO] * CELULAS
    for i, s in enumerate(ENTRADA):
        fita[INICIO + i] = s
    historia = {i: [(0.0, fita[i])] for i in range(CELULAS)}
    for k, p in enumerate(passos):
        if p["escreve"] != p["lido"]:
            historia[p["cabeca"]].append((T[k] + 0.25, p["escreve"]))
    for i in range(CELULAS):
        historia[i].append((volta, fita[i]))

    anim = []
    for i in range(CELULAS):
        for simbolo in ("0", "1"):
            ev = [(t, "1" if s == simbolo else "0") for t, s in historia[i]]
            if all(v == "0" for _, v in ev):
                continue
            anim.append(doc.t(simbolo, cx(i), y0 + 30, 20, "tinta", peso="m", ancora="middle",
                              extra=f' opacity="{ev[0][1]}"').replace("</text>", discreto("opacity", ev, D) + "</text>"))

    # ---- cabeça: desliza entre células (spline) e volta ao início no reinício
    nos = [(0.0, cx(INICIO))]
    for k, p in enumerate(passos):
        if p["nova"] != p["cabeca"]:
            nos += [(T[k] + 0.4, cx(p["cabeca"])), (T[k] + 0.72, cx(p["nova"]))]
    nos += [(volta - 0.01, cx(passos[-1]["nova"])), (volta, cx(INICIO)), (D, cx(INICIO))]
    splines = []
    for (ta, xa), (tb, xb) in zip(nos, nos[1:]):
        splines.append("0.45 0 0.2 1" if xa != xb and tb - ta > 0.1 else "0 0 1 1")
    mov = (f'<animateTransform attributeName="transform" type="translate" calcMode="spline" dur="{fmt(D, 3)}s" '
           f'repeatCount="indefinite" values="{";".join(f"{fmt(x)} 0" for _, x in nos)}" '
           f'keyTimes="{";".join(fmt(t / D, 4) for t, _ in nos)}" keySplines="{";".join(splines)}"/>')
    luz_ev = [(0.0, ".12")]
    for k in range(len(passos)):
        luz_ev += [(T[k], ".32"), (T[k] + 0.35, ".12")]
    luz = discreto("fill-opacity", luz_ev, D)
    anim.append(cabeca_svg(cx(INICIO), mov, luz))

    # ---- estado e transição
    for estado in ("q0", "q1", "halt"):
        ev = [(0.0, "1" if estado == "q0" else "0")]
        for k, p in enumerate(passos):
            ev.append((T[k] + 0.25, "1" if p["prox"] == estado else "0"))
        ev.append((volta, "1" if estado == "q0" else "0"))
        anim.append(doc.t(estado, 708, 60, 18, "ambar", peso="m", extra=f' opacity="{ev[0][1]}"')
                    .replace("</text>", discreto("opacity", ev, D) + "</text>"))
    for k, p in enumerate(passos):
        fim = T[k + 1] + 0.15 if k + 1 < len(passos) else volta
        ev = [(0.0, "0"), (T[k] + 0.15, "1"), (fim, "0")]
        anim.append(doc.t(rotulo(p), 640, 90, 16, "tinta", extra=' opacity="0"')
                    .replace("</text>", discreto("opacity", ev, D) + "</text>"))

    # ---- resultado: sublinhado sob 1100 quando para
    x_a, x_b = x0 + INICIO * cw + 6, x0 + (INICIO + len(ENTRADA)) * cw - 6
    anim.append(f'<path d="M{x_a} {y0 + cw + 8}H{x_b}" stroke="{c["ambar"]}" stroke-width="1.5" opacity="0">'
                + discreto("opacity", [(0.0, "0"), (t_para, "1"), (volta, "0")], D) + "</path>")

    esmaece = (f'<animate attributeName="opacity" dur="{fmt(D, 3)}s" repeatCount="indefinite" values="1;1;0;0;1;1" '
               f'keyTimes="0;{fmt(some / D, 4)};{fmt((some + 0.35) / D, 4)};{fmt(volta / D, 4)};'
               f'{fmt((volta + 0.35) / D, 4)};1"/>')
    doc.corpo.append("".join(fixo) + f'<g class="rm-hide">{esmaece}{"".join(anim)}</g>' + quadro_estatico())
    return doc.render()
