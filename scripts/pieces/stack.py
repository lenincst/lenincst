"""Stack: "Linguagens que mais uso" como saída de compilador (barra com easing + porcentagem contando em SMIL
discreto, sincronizada com a mesma curva da barra) e "Também na carreira" como um grafo de dependências.

Porcentagens: as do README v1 (linguagens.svg do branch `output`, gerado em 25/11/2026 a partir dos bytes por
linguagem dos repositórios do próprio Lenin): PHP 60, Python 17, Laravel (Blade) 9, JavaScript 6,
TypeScript 4, Bash (Shell) 4.
"""
from svgkit import Doc, ICONES, ELASTICO, fmt, quadros, tempo_para_progresso, tempos_smil

L, A = 900, 320

LINGUAGENS = [  # (rótulo no "compilador", nome exibido, ícone Simple Icons, porcentagem)
    ("php", "PHP", "php", 60),
    ("python", "Python", "python", 17),
    ("laravel", "Laravel", "laravel", 9),
    ("javascript", "JavaScript", "javascript", 6),
    ("typescript", "TypeScript", "typescript", 4),
    ("bash", "Bash", "gnubash", 4),
]
# Também na carreira: nós do grafo (x, y do centro) e arestas "depende de"
NOS = {
    "React": ("react", 580, 168),
    "Spring": ("springboot", 672, 168),
    "Java": ("openjdk", 776, 88),
    "MySQL": ("mysql", 776, 168),
    "MongoDB": ("mongodb", 776, 248),
    "AWS": (None, 862, 168),
}
ARESTAS = [("React", "Spring"), ("Spring", "Java"), ("Spring", "MySQL"), ("Spring", "MongoDB"),
           ("Java", "AWS"), ("MySQL", "AWS"), ("MongoDB", "AWS")]
CAMADAS = [["React"], ["Spring"], ["Java", "MySQL", "MongoDB"], ["AWS"]]
COR_AWS = "#FF9900"

CURVA_BARRA = (0.22, 0.8, 0.24, 1.0)
DUR_BARRA = 1.1


def icone(nome: str, x: float, y: float, tam: float) -> str:
    ic = ICONES[nome]
    return (f'<path transform="translate({fmt(x)} {fmt(y)}) scale({fmt(tam / 24, 4)})" '
            f'fill="{ic["cor"]}" d="{ic["d"]}"/>')


def odometro(doc: Doc, valor: int, x_fim: float, y: float, inicio: float, idx: int) -> str:
    """Porcentagem que conta de 0 até `valor` com a mesma easing da barra (dígitos em fita, SMIL discreto)."""
    tam, passo = 16, 22
    cw = 0.6 * tam
    x_pct = x_fim - cw
    x_uni, x_dez = x_pct - cw, x_pct - 2 * cw
    # instante (fração da duração) em que a barra passa por v/valor: inversa da cubic-bezier
    instantes = {v: tempo_para_progresso(CURVA_BARRA, v / valor) for v in range(1, valor + 1)}

    def fita(digitos: list[str], x: float, muda) -> str:
        textos = "".join(doc.t(d, x, y + k * passo, tam, "tinta") for k, d in enumerate(digitos) if d)
        tempos, valores = [0.0], ["0 0"]
        for v in range(1, valor + 1):
            pos = muda(v)
            if pos != muda(v - 1):
                tempos.append(instantes[v])
                valores.append(f"0 {-pos * passo}")
        if len(tempos) == 1:
            return f"<g>{textos}</g>"
        return (f'<g>{textos}<animateTransform attributeName="transform" type="translate" calcMode="discrete" '
                f'values="{";".join(valores)}" keyTimes="{";".join(fmt(t, 4) for t in tempos)}" '
                f'begin="{inicio:.3f}s" dur="{DUR_BARRA}s" fill="freeze"/></g>')

    doc.defs.append(f'<clipPath id="od{idx}"><rect x="{fmt(x_dez - 1)}" y="{y - 15}" width="{fmt(2 * cw + 2)}" '
                    f'height="20"/></clipPath>')
    animado = (f'<g class="rm-hide" clip-path="url(#od{idx})">'
               f'{fita([""] + [str(d) for d in range(1, 10)], x_dez, lambda v: v // 10)}'
               f'{fita([str(d) for d in range(10)], x_uni, lambda v: v % 10)}</g>')
    estatico = f'<g class="rm-show">{doc.t(str(valor), x_uni + cw, y, tam, "tinta", ancora="end")}</g>'
    return animado + estatico + doc.t("%", x_pct, y, tam, "suave")


def construir(tema: str) -> str:
    doc = Doc(L, A, "Linguagens que mais uso e também na carreira",
              "Linguagens que mais uso: PHP 60%, Python 17%, Laravel 9%, JavaScript 6%, TypeScript 4% e Bash 4%, "
              "exibidas como saída de compilador. Também na carreira: Java, Spring, React, MySQL, MongoDB e AWS, "
              "como um grafo de dependências.", tema)
    c, css = doc.c, doc.css
    css.append("@keyframes linha{from{opacity:0;transform:translateX(-8px)}}"
               f".linha{{animation:linha .35s {ELASTICO} both}}"
               "@keyframes enche{from{transform:scaleX(0)}}"
               f".barra{{transform-box:fill-box;transform-origin:left;"
               f"animation:enche {DUR_BARRA}s cubic-bezier({','.join(map(str, CURVA_BARRA))}) both}}"
               "@keyframes surge{from{opacity:0}}.ok{animation:surge .25s ease-out both}"
               ".cab{animation:surge .6s ease-out both}")

    # ---------------- coluna 1: compilador
    partes = [doc.t("Linguagens que mais uso", 24, 32, 17, "tinta", peso="m", cls="cab"),
              f'<path class="cab" d="M24 46H512" stroke="{c["traco"]}" stroke-opacity=".18"/>',
              doc.t("Também na carreira", 556, 32, 17, "tinta", peso="m", cls="cab",
                    estilo="animation-delay:.2s"),
              f'<path class="cab" style="animation-delay:.2s" d="M556 46H884" stroke="{c["traco"]}" stroke-opacity=".18"/>']
    for i, (rot, _, ic, pct) in enumerate(LINGUAGENS):
        y = 84 + i * 40
        t0 = 0.4 + i * 0.45
        t_barra = t0 + 0.25
        nome_x = 58 + len("compiling ") * 9.6
        fim_nome = nome_x + len(rot) * 9.6
        linha = [icone(ic, 24, y - 17, 22),
                 doc.t("compiling", 58, y, 16, "suave"),
                 doc.t(rot, nome_x, y, 16, "tinta"),
                 f'<path d="M{fmt(fim_nome + 8)} {y - 4}H298" stroke="{c["fraco"]}" stroke-width="1.6" '
                 f'stroke-linecap="round" stroke-dasharray="0 6.4"/>']
        partes.append(f'<g class="linha" style="animation-delay:{t0:.2f}s">{"".join(linha)}</g>')
        partes.append(f'<rect x="306" y="{y - 9}" width="120" height="6" rx="3" fill="{c["traco"]}" fill-opacity=".1"/>'
                      f'<rect class="barra" style="animation-delay:{t_barra:.2f}s" x="306" y="{y - 9}" '
                      f'width="{fmt(120 * pct / 100)}" height="6" rx="3" fill="{c["ambar"]}"/>')
        partes.append(odometro(doc, pct, 478, y, t_barra, i))
        partes.append(doc.t("ok", 492, y, 16, "ciano", peso="m", cls="ok",
                            estilo=f"animation-delay:{t_barra + DUR_BARRA:.2f}s"))
    fim_compilador = 0.4 + 5 * 0.45 + 0.25 + DUR_BARRA

    # ---------------- coluna 2: grafo de dependências
    t_cam = [fim_compilador * 0.25 + k * 0.75 for k in range(len(CAMADAS))]
    t_no = {n: t_cam[k] for k, cam in enumerate(CAMADAS) for n in cam}
    css.append("@keyframes no{from{opacity:0;transform:scale(.6)}}"
               ".no{transform-box:fill-box;transform-origin:center;animation:no .45s cubic-bezier(.3,1.35,.5,1) both}"
               "@keyframes desenha{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
               ".aresta{stroke-dasharray:1;animation:desenha .55s cubic-bezier(.5,0,.3,1) both}")
    caminhos = []
    for k, (a, b) in enumerate(ARESTAS):
        _, xa, ya = NOS[a]
        _, xb, yb = NOS[b]
        x0, x1 = xa + 21, xb - 23
        meio = (x0 + x1) / 2
        d = f"M{x0} {ya}C{fmt(meio)} {ya} {fmt(meio)} {yb} {x1} {yb}"
        caminhos.append(d)
        atraso = t_no[a] + 0.3
        partes.append(f'<path id="ar{k}" class="aresta" pathLength="1" style="animation-delay:{atraso:.2f}s" d="{d}" '
                      f'stroke="{c["traco"]}" stroke-opacity=".45" stroke-width="1.2"/>'
                      f'<path class="ok" style="animation-delay:{atraso + 0.5:.2f}s" d="M{x1 - 5} {yb - 3.5}L{x1} {yb}'
                      f'L{x1 - 5} {yb + 3.5}" stroke="{c["traco"]}" stroke-opacity=".6" stroke-width="1.2" '
                      f'stroke-linecap="round" stroke-linejoin="round"/>')
    for nome, (ic, x, y) in NOS.items():
        miolo = (icone(ic, x - 11, y - 11, 22) if ic else
                 doc.t("AWS", x, y + 5.5, 15, COR_AWS, peso="m", ancora="middle"))
        partes.append(f'<g class="no" style="animation-delay:{t_no[nome]:.2f}s">'
                      f'<rect x="{x - 20}" y="{y - 20}" width="40" height="40" rx="9" stroke="{c["traco"]}" '
                      f'stroke-opacity=".38" stroke-width="1.1"/>{miolo}'
                      f'{doc.t(nome, x, y + 40, 14, "suave", ancora="middle")}</g>')

    # repouso: um sinal discreto percorre as dependências, uma aresta por vez
    fim = t_cam[-1] + 0.6
    ciclo = 1.4 * len(ARESTAS) + 2.0
    sinais = []
    for k in range(len(ARESTAS)):
        ini = k * 1.4
        sinais.append(f'<circle r="2.2" fill="{c["ambar"]}" opacity="0">'
                      f'<animateMotion dur="{ciclo}s" begin="{fim:.2f}s" repeatCount="indefinite" '
                      f'keyPoints="0;0;1;1" keyTimes="0;{fmt(ini / ciclo, 4)};{fmt((ini + 1.2) / ciclo, 4)};1" '
                      f'calcMode="linear"><mpath xlink:href="#ar{k}"/></animateMotion>'
                      f'<animate attributeName="opacity" dur="{ciclo}s" begin="{fim:.2f}s" repeatCount="indefinite" '
                      f'values="0;0;.9;.9;0;0" keyTimes="{tempos_smil([0, ini, ini + 0.15, ini + 1.05, ini + 1.2, ciclo], ciclo)}"/>'
                      f'</circle>')
    partes.append(f'<g class="rm-hide">{"".join(sinais)}</g>')
    doc.corpo.append("".join(partes))
    return doc.render()
