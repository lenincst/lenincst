"""Hero: engrenagens de Babbage → cartão perfurado com "LENIN" em ASCII → CRT digitando o nome.

Coreografia (s): 0–1.8 engrenagens se desenham e giram · 2.0 cartão entra · 3.0–4.3 furos ·
4.75 cena some · 4.9–5.9 CRT liga · 6.1–7.6 nome digitado · 7.8 subtítulo · 8.0+ repouso
(cursor piscando, contador de ano 1837 → 1936 → 1969 → 2026, engrenagens já fora de cena).
"""
import math

from svgkit import Doc, ELASTICO, SUAVE, circulo, fmt, quadros, retangulo

L, A = 900, 320
NOME = "Lenin Costa da Rosa"
SUBTITULO = "Engenheiro de Software · Florianópolis, BR"
PALAVRA = "LENIN"
ANOS = ("1837", "1936", "1969", "2026")

# ----------------------------------------------------------------- engrenagens
MODULO = 4.0  # módulo m: raio primitivo = m·z/2, então dentes do mesmo módulo engrenam


class Engrenagem:
    def __init__(self, z: int, cx: float, cy: float, fase: float):
        self.z, self.cx, self.cy, self.fase = z, cx, cy, fase
        self.r = MODULO * z / 2

    @property
    def passo(self) -> float:
        return 2 * math.pi / self.z

    def contorno(self) -> str:
        """Perfil trapezoidal: adendo m, dedendo 1,25m, folga no flanco (espessura < meio passo)."""
        ra, rf, p = self.r + MODULO, self.r - 1.25 * MODULO, self.passo

        def pt(rr, a):
            return f"{fmt(rr * math.cos(a))} {fmt(rr * math.sin(a))}"

        d = [f"M{pt(rf, self.fase - 0.28 * p)}"]
        for k in range(self.z):
            c = self.fase + k * p
            d.append(f"L{pt(ra, c - 0.16 * p)}A{fmt(ra)} {fmt(ra)} 0 0 1 {pt(ra, c + 0.16 * p)}"
                     f"L{pt(rf, c + 0.28 * p)}A{fmt(rf)} {fmt(rf)} 0 0 1 {pt(rf, c + p - 0.28 * p)}")
        return "".join(d) + "Z"


def engrenar(motora: Engrenagem, z: int, angulo: float) -> Engrenagem:
    """Posiciona uma engrenagem acoplada a `motora` na direção `angulo` com a fase que intercala os dentes.

    No ponto de contato, a posição de um dente da motora ao longo da tangente (u = -δ·r) precisa cair no
    meio de um vão da movida: fase = ângulo + π + (δ·r_motora − passo_circular/2) / r_movida.
    """
    r = MODULO * z / 2
    d = motora.r + r
    cx, cy = motora.cx + d * math.cos(angulo), motora.cy + d * math.sin(angulo)
    delta = (angulo - motora.fase) % motora.passo
    fase = angulo + math.pi + (delta * motora.r - math.pi * MODULO / 2) / r
    return Engrenagem(z, cx, cy, fase)


def desenho_engrenagem(doc: Doc, g: Engrenagem, classe_giro: str, atraso: float) -> str:
    c = doc.c
    rf = g.r - 1.25 * MODULO
    aro, cubo, furo = rf - 6, max(9.0, g.r * 0.26), max(4.0, g.r * 0.1)
    raios = 6 if g.z >= 24 else 4
    detalhe = [circulo(0, 0, aro), circulo(0, 0, cubo), circulo(0, 0, furo)]
    for k in range(raios):
        a = g.fase + k * 2 * math.pi / raios
        for lado in (-1, 1):
            off = lado * 2.2
            x0, y0 = cubo * math.cos(a), cubo * math.sin(a)
            x1, y1 = aro * math.cos(a), aro * math.sin(a)
            nx, ny = -math.sin(a) * off, math.cos(a) * off
            detalhe.append(f"M{fmt(x0 + nx)} {fmt(y0 + ny)}L{fmt(x1 + nx)} {fmt(y1 + ny)}")
    # chaveta no furo do eixo: detalhe de desenho técnico que também denuncia a rotação
    detalhe.append(f"M{fmt(furo * 0.45)} {fmt(-furo)}V{fmt(-furo - 3)}H{fmt(-furo * 0.45)}V{fmt(-furo)}")
    return (f'<g transform="translate({fmt(g.cx)} {fmt(g.cy)})"><g class="{classe_giro}">'
            f'<path class="traco" style="animation-delay:{atraso:.2f}s" pathLength="1" d="{g.contorno()}" '
            f'stroke="{c["traco"]}" stroke-width="1.3" stroke-linejoin="round"/>'
            f'<path class="det" style="animation-delay:{atraso + 0.5:.2f}s" d="{"".join(detalhe)}" '
            f'stroke="{c["traco"]}" stroke-opacity=".55" stroke-width="1"/>'
            f'</g><path class="det" style="animation-delay:{atraso + 0.6:.2f}s" d="{circulo(0, 0, g.r)}" '
            f'stroke="{c["ciano"]}" stroke-opacity=".7" stroke-width=".8" stroke-dasharray="9 3 2 3"/></g>')


# ----------------------------------------------------------------- cartão
def bits(ch: str) -> list[int]:
    v = ord(ch)
    assert v < 128, "ASCII de 7 bits"
    return [(v >> (7 - j)) & 1 for j in range(8)]  # j=0 é o bit de peso 128


def construir(tema: str) -> str:
    doc = Doc(L, A, "Lenin Costa da Rosa — Engenheiro de Software, Florianópolis",
              "Engrenagens da máquina diferencial de Babbage giram; um cartão perfurado codifica LENIN em "
              "ASCII binário; a cena vira um terminal de CRT que digita Lenin Costa da Rosa, Engenheiro de "
              "Software, Florianópolis, BR, com um contador de anos 1837, 1936, 1969 e 2026.", tema)
    c = doc.c
    css = doc.css

    # ---------- ato 1: grade + engrenagens
    ga = Engrenagem(32, 140, 172, -math.radians(20))
    gb = engrenar(ga, 14, -math.radians(20))
    gc = engrenar(gb, 24, math.radians(40))
    periodo_a = 18.0  # s por volta da maior; as outras seguem a razão de dentes
    giros = {"ga": (ga, periodo_a, "cw"), "gb": (gb, periodo_a * gb.z / ga.z, "ccw"),
             "gc": (gc, periodo_a * gc.z / ga.z, "cw")}
    css.append("@keyframes cw{to{transform:rotate(360deg)}}@keyframes ccw{to{transform:rotate(-360deg)}}")
    for nome, (_, per, sentido) in giros.items():
        css.append(f".{nome}{{animation:{sentido} {per:.3f}s linear infinite}}")
    css.append("@keyframes desenha{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
               ".traco{stroke-dasharray:1;animation:desenha 1.3s cubic-bezier(.6,0,.3,1) both}"
               "@keyframes surge{from{opacity:0}}"
               ".det{animation:surge .8s ease-out both}")
    doc.defs.append(f'<pattern id="grade" width="20" height="20" patternUnits="userSpaceOnUse">'
                    f'<path d="M20 0H0V20" stroke="{c["grade"]}" stroke-opacity="{c["grade_op"]}" '
                    f'stroke-width=".6"/></pattern>')

    ato1 = [f'<rect class="det" width="{L}" height="{A}" fill="url(#grade)"/>']
    # linhas de centro (traço-ponto), fixas: não giram com as engrenagens
    centro = []
    for g in (ga, gb, gc):
        e = g.r + MODULO + 8
        centro.append(f"M{fmt(g.cx - e)} {fmt(g.cy)}H{fmt(g.cx + e)}M{fmt(g.cx)} {fmt(g.cy - e)}V{fmt(g.cy + e)}")
    ato1.append(f'<path class="det" style="animation-delay:1.1s" d="{"".join(centro)}" stroke="{c["ciano"]}" '
                f'stroke-opacity=".55" stroke-width=".7" stroke-dasharray="10 3 2 3"/>')
    for i, (nome, (g, _, _)) in enumerate(giros.items()):
        ato1.append(desenho_engrenagem(doc, g, nome, 0.15 + i * 0.25))
    rotulos = [(ga, ga.cx, ga.cy + ga.r + 30), (gb, gb.cx + 4, gb.cy - gb.r - 16), (gc, gc.cx, gc.cy + gc.r + 26)]
    for g, x, y in rotulos:
        ato1.append(doc.t(f"z={g.z}", x, y, 14, "suave", ancora="middle", cls="det", estilo="animation-delay:1.3s"))
    ato1.append(doc.t("fig. 1 — Babbage, máquina diferencial, 1822", 40, 306, 15, "suave", cls="det",
                      estilo="animation-delay:1.5s"))

    # ---------- ato 1b: cartão perfurado
    cx0, cy0, cw, ch = 452, 34, 400, 248
    corte = 20
    cartao = [f'<path d="M{cx0 + corte} {cy0}H{cx0 + cw}V{cy0 + ch}H{cx0}V{cy0 + corte}Z" fill="{c["cartao"]}" '
              f'stroke="{c["traco"]}" stroke-opacity=".8" stroke-width="1.2"/>']
    col_x = [566 + i * 64 for i in range(len(PALAVRA))]
    lin_y = [80 + j * 22 for j in range(8)]
    for j, peso in enumerate(2 ** (7 - j) for j in range(8)):
        cartao.append(doc.t(str(peso), 524, lin_y[j] + 5, 14, "suave", ancora="end"))
    furos, guias = [], []
    t_furo, passo_furo = 3.0, 0.075
    fim_coluna = []
    for i, letra in enumerate(PALAVRA):
        b = bits(letra)
        for j in range(8):
            x, y = col_x[i] - 7, lin_y[j] - 8
            guias.append(f"M{x} {y}h14v16h-14Z")
            if b[j]:
                furos.append(f'<rect class="furo" style="animation-delay:{t_furo:.3f}s" x="{x}" y="{y}" '
                             f'width="14" height="16" rx="1.5" fill="{c["furo"]}"/>')
                t_furo += passo_furo
        fim_coluna.append(t_furo)
        cartao.append(doc.t(f"{ord(letra):02X}", col_x[i], 62, 14, "suave", ancora="middle"))
        cartao.append(doc.t(letra, col_x[i], 270, 18, "tinta", peso="m", ancora="middle", cls="letra",
                            estilo=f"animation-delay:{t_furo:.3f}s"))
    cartao.insert(1, f'<path d="{"".join(guias)}" stroke="{c["traco"]}" stroke-opacity=".22" stroke-width=".8"/>')
    cartao.extend(furos)
    css.append("@keyframes entra{from{transform:translateX(520px)}}"
               f".cartao{{animation:entra .95s {ELASTICO} 2s both}}"
               "@keyframes fura{from{opacity:0;transform:scale(1.9)}}"
               ".furo{transform-box:fill-box;transform-origin:center;animation:fura .22s cubic-bezier(.3,1.4,.5,1) both}"
               "@keyframes letra{from{opacity:0;transform:translateY(5px)}}"
               ".letra{animation:letra .35s ease-out both}")
    ato1.append(f'<g class="cartao">{"".join(cartao)}</g>')
    ato1.append(doc.t("fig. 2 — LENIN em ASCII, 1 coluna/letra", 452, 306, 15, "suave", cls="det",
                      estilo="animation-delay:2.6s"))

    fim_ato1 = 4.75
    css.append(quadros("sai", [(0, "opacity:1;transform:none;visibility:visible"),
                               (fim_ato1, "opacity:1;transform:none;visibility:visible"),
                               (fim_ato1 + 0.6, "opacity:0;transform:scale(.985);visibility:hidden")], fim_ato1 + 0.6)
               + f".ato1{{opacity:0;visibility:hidden;transform-origin:450px 160px;"
                 f"animation:sai {fim_ato1 + 0.6:.2f}s {SUAVE} both}}")
    doc.corpo.append(f'<g class="ato1">{"".join(ato1)}</g>')

    # ---------- ato 2: CRT
    bx, by, bw, bh = 22, 10, 856, 300
    sx, sy, sw, sh = 42, 28, 816, 260
    doc.defs.append(f'<pattern id="varre" width="6" height="3" patternUnits="userSpaceOnUse">'
                    f'<rect width="6" height="1" fill="{c["linha_varredura"]}" fill-opacity="{c["varredura_op"]}"/></pattern>'
                    f'<radialGradient id="fosforo" cx=".42" cy=".5" r=".7">'
                    f'<stop offset="0" stop-color="{c["ambar"]}" stop-opacity="{c["brilho_op"]}"/>'
                    f'<stop offset="1" stop-color="{c["ambar"]}" stop-opacity="0"/></radialGradient>'
                    f'<linearGradient id="faixa" x1="0" y1="0" x2="0" y2="1">'
                    f'<stop offset="0" stop-color="{c["ambar"]}" stop-opacity="0"/>'
                    f'<stop offset=".5" stop-color="{c["ambar"]}" stop-opacity=".045"/>'
                    f'<stop offset="1" stop-color="{c["ambar"]}" stop-opacity="0"/></linearGradient>'
                    f'<clipPath id="tela"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="26"/></clipPath>')
    t_crt = 4.9
    css.append(f".moldura{{stroke-dasharray:1;animation:desenha 1s {SUAVE} {t_crt}s both}}"
               f"@keyframes liga{{from{{opacity:0;transform:scaleY(.02)}}40%{{opacity:1;transform:scaleY(.04)}}}}"
               f".tela{{transform-origin:450px 158px;animation:liga .7s {SUAVE} {t_crt + 0.35:.2f}s both}}"
               "@keyframes varre{from{transform:translateY(-90px)}to{transform:translateY(300px)}}"
               ".faixa{animation:varre 7s linear 6s infinite backwards}"
               f".led{{animation:surge .3s ease-out {t_crt + 1.0:.2f}s both}}")
    crt = [f'<path class="moldura" pathLength="1" d="{retangulo(bx, by, bw, bh, 20)}" stroke="{c["traco"]}" '
           f'stroke-opacity=".7" stroke-width="1.2"/>',
           f'<g class="tela"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="26" fill="{c["tela"]}" '
           f'stroke="{c["traco"]}" stroke-opacity=".35" stroke-width="1"/>'
           f'<g clip-path="url(#tela)"><rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="url(#fosforo)"/>'
           f'<rect class="faixa" x="{sx}" y="{sy}" width="{sw}" height="70" fill="url(#faixa)"/>'
           f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="url(#varre)"/></g></g>',
           f'<circle class="led" cx="{bx + bw - 28}" cy="{by + bh - 9}" r="2.4" fill="{c["ambar"]}"/>']

    # nome digitado: um <text> por caractere, com ritmo humano (pausa maior depois de espaço)
    tam, x0, base = 46, 92, 168
    cw_ = 0.6 * tam
    cor_nome = "ambar" if tema == "dark" else "tinta"
    t = 6.1
    tempos = []
    for i, ch in enumerate(NOME):
        tempos.append(t)
        if ch != " ":
            crt.append(doc.t(ch, x0 + i * cw_, base, tam, cor_nome, peso="m", cls="k",
                             estilo=f"animation-delay:{t:.3f}s"))
        jitter = (math.sin(i * 12.9898) * 43758.5453) % 1  # pseudoaleatório estável
        t += 0.055 + 0.05 * jitter + (0.09 if ch == " " else 0)
    fim_nome = t
    css.append("@keyframes k{from{opacity:0}to{opacity:1}}.k{animation:k .06s linear both}")

    # cursor: anda uma célula por tecla (steps), depois pisca no fim do nome
    pontos = [(0, "transform:translateX(0)")]
    for i, ti in enumerate(tempos):
        pontos.append((ti + 0.001, f"transform:translateX({fmt((i + 1) * cw_)}px)"))
    pontos.append((fim_nome, f"transform:translateX({fmt(len(NOME) * cw_)}px)"))
    css.append(quadros("anda", pontos, fim_nome) +
               f".cursor{{transform:translateX({fmt(len(NOME) * cw_)}px);animation:anda {fim_nome:.3f}s steps(1,end) both}}"
               f".cursor-luz{{animation:surge .2s linear {t_crt + 1.0:.2f}s both}}"
               "@keyframes pisca{0%,49.9%{opacity:1}50%,100%{opacity:0}}"
               f".cursor-pisca{{animation:pisca 1.06s linear {fim_nome + 0.1:.2f}s infinite}}")
    crt.append(f'<g class="cursor-luz"><g class="cursor"><rect class="cursor-pisca" x="{x0 + 2}" y="{base - 36}" '
               f'width="{fmt(cw_ - 4)}" height="44" fill="{c["ambar"]}" fill-opacity=".85"/></g></g>')

    t_sub = fim_nome + 0.25
    crt.append(doc.t(SUBTITULO, x0, 216, 20, "tinta" if tema == "dark" else "suave", cls="sub",
                     estilo=f"animation-delay:{t_sub:.2f}s", extra=' fill-opacity=".82"' if tema == "dark" else ""))
    css.append("@keyframes sub{from{opacity:0;transform:translateY(8px)}}"
               f".sub{{animation:sub .7s {ELASTICO} both}}")

    # contador de anos (canto superior direito da tela)
    t_ano, por_ano = t_sub + 0.3, 4.5
    ciclo = por_ano * len(ANOS)
    css.append(f".ano{{animation:surge .6s ease-out {t_ano:.2f}s both}}"
               "@keyframes ciclo{0%{opacity:0}2%,23%{opacity:1}25%,100%{opacity:0}}")
    ano = [doc.t("ano", 782, 62, 14, "suave", ancora="end")]
    for k, a in enumerate(ANOS):
        repouso = "" if a == ANOS[-1] else "opacity:0;"
        ano.append(doc.t(a, 830, 62, 16, "ciano", peso="m", ancora="end",
                         estilo=f"{repouso}animation:ciclo {ciclo:.1f}s linear {t_ano + k * por_ano:.2f}s infinite backwards"))
    crt.append(f'<g class="ano">{"".join(ano)}</g>')
    doc.corpo.append("".join(crt))
    return doc.render()
