"""As peças do perfil, no branding da Lecodaro.

Referência: "Lecodaro Branding" (fundo #07080a, cartões de vidro, as três luzes das marcas, wordmark
"Lecodaro" em Space Grotesk 500 com a esfera iridescente no lugar do ponto, ícones SO/CD/IO).
Toda animação parte do quadro inicial e termina no estado normal do elemento, para que leitores
sem CSS mostrem a peça pronta.
"""
import json
from datetime import date
from pathlib import Path

from vetor import altura_maiuscula, documento, largura, milhar, ruido, texto

AQUI = Path(__file__).parent
ICONES = json.loads((AQUI / "icones.json").read_text())["icones"]

FUNDO = "#07080a"
TITULO, TEXTO, TEXTO_2, ROTULO, DOMINIO = "#f7f7f9", "#b6bbc4", "#a4a9b3", "#6b7280", "#7f8590"

# Cores de cada marca, como no branding.
MARCAS = {
    "studio": {"letras": "SO", "x": 10.5, "borda": "#f9804f", "letra": "#ff9e74", "tinta": "251,138,92",
               "sombra": "234,75,40", "sufixo": "#ff9a6e", "luz": "244,113,58", "luz_op": .26, "fonte": "studio"},
    "cloud": {"letras": "CD", "x": 9.5, "borda": "#3bd873", "letra": "#66e497", "tinta": "69,214,126",
              "sombra": "21,163,74", "sufixo": "#5ee08f", "luz": "21,163,74", "luz_op": .26, "fonte": "cloud"},
    "info": {"letras": "IO", "x": 13.5, "borda": "#5a97ff", "letra": "#93bbff", "tinta": "95,160,255",
             "sombra": "37,99,235", "sufixo": "#8cb6ff", "luz": "37,99,235", "luz_op": .30, "fonte": "info"},
}


def _vidro(id_, l, a, raio):
    """Cartão de vidro escuro: fundo, reflexo diagonal, borda clara e o fio de luz no topo."""
    defs = (f'<linearGradient id="{id_}v" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".086"/>'
            f'<stop offset=".42" stop-color="#fff" stop-opacity=".02"/><stop offset="1" stop-color="#fff" stop-opacity=".043"/></linearGradient>'
            f'<linearGradient id="{id_}f" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<clipPath id="{id_}c"><rect width="{l}" height="{a}" rx="{raio}"/></clipPath>')
    fundo = f'<rect width="{l}" height="{a}" rx="{raio}" fill="{FUNDO}"/>'
    vidro = (f'<rect width="{l}" height="{a}" rx="{raio}" fill="url(#{id_}v)"/>'
             f'<rect x=".5" y=".5" width="{l - 1}" height="{a - 1}" rx="{raio - .5}" fill="none" stroke="#fff" stroke-opacity=".12"/>'
             f'<rect class="fio" x="{l * .12:.0f}" y="0" width="{l * .76:.0f}" height="1" fill="url(#{id_}f)"/>')
    return defs, fundo, vidro


def _luz(id_, cx, cy, r, rgb, opacidade, classe=""):
    defs = (f'<radialGradient id="{id_}"><stop offset="0" stop-color="rgb({rgb})" stop-opacity="{opacidade}"/>'
            f'<stop offset=".66" stop-color="rgb({rgb})" stop-opacity="0"/></radialGradient>')
    return defs, f'<circle class="{classe}" cx="{cx}" cy="{cy}" r="{r}" fill="url(#{id_})"/>'


def esfera(id_, cx, cy, r):
    """A esfera iridescente da Lecodaro (o "ponto" do wordmark). As cores giram devagar."""
    camadas = [  # (centro x, centro y, raio, cor, opacidade) a partir do degradê do branding
        (.72, .26, .434, "251,138,92", .6), (.26, .72, .454, "69,214,126", .65), (.76, .70, .475, "95,160,255", .75)]
    defs = [f'<radialGradient id="{id_}b" cx=".5" cy=".42" r=".567"><stop offset="0" stop-color="#363b45"/>'
            f'<stop offset="1" stop-color="#0a0b0e"/></radialGradient>',
            f'<radialGradient id="{id_}w" cx=".5" cy="1.12" r=".564"><stop offset="0" stop-color="#fff" stop-opacity=".32"/>'
            f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>',
            f'<radialGradient id="{id_}s" cx=".33" cy=".26" r=".3"><stop offset="0" stop-color="#fff" stop-opacity=".98"/>'
            f'<stop offset=".433" stop-color="#fff" stop-opacity=".4"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>']
    cores = []
    for i, (gx, gy, gr, rgb, op) in enumerate(camadas):
        defs.append(f'<radialGradient id="{id_}{i}" cx="{gx}" cy="{gy}" r="{gr}"><stop offset="0" stop-color="rgb({rgb})" stop-opacity="{op}"/>'
                    f'<stop offset="1" stop-color="rgb({rgb})" stop-opacity="0"/></radialGradient>')
        cores.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="url(#{id_}{i})"/>')
    corpo = (f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="url(#{id_}b)"/>'
             f'<g class="gira" style="transform-origin:{cx:.2f}px {cy:.2f}px">{"".join(cores)}</g>'
             f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="url(#{id_}w)"/>'
             f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="url(#{id_}s)"/>'
             f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r - r * .06:.2f}" fill="none" stroke="#fff" stroke-opacity=".28" stroke-width="{r * .12:.2f}"/>')
    return "".join(defs), corpo


def icone(id_, marca, x, y, lado):
    """Ícone do sistema da Lecodaro: quadrado escuro, borda na cor da marca e as duas letras."""
    m = MARCAS[marca]
    k = lado / 96
    defs = (f'<linearGradient id="{id_}g" x1=".27" y1="0" x2=".73" y2="1"><stop offset="0" stop-color="#1b1d22"/>'
            f'<stop offset="1" stop-color="#0b0c0f"/></linearGradient>'
            f'<radialGradient id="{id_}t" cx=".2" cy="0" r="1.3" gradientTransform="translate(.2 0) scale(1 .77) translate(-.2 0)">'
            f'<stop offset="0" stop-color="rgb({m["tinta"]})" stop-opacity=".24"/><stop offset=".6" stop-color="rgb({m["tinta"]})" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="{id_}h"><stop offset="0" stop-color="rgb({m["sombra"]})" stop-opacity=".55"/>'
            f'<stop offset="1" stop-color="rgb({m["sombra"]})" stop-opacity="0"/></radialGradient>')
    raio = 23 * k
    corpo = (f'<ellipse cx="{x + lado / 2}" cy="{y + lado * .92:.1f}" rx="{lado * .55:.1f}" ry="{lado * .3:.1f}" fill="url(#{id_}h)"/>'
             f'<rect x="{x}" y="{y}" width="{lado}" height="{lado}" rx="{raio:.1f}" fill="url(#{id_}g)"/>'
             f'<rect x="{x}" y="{y}" width="{lado}" height="{lado}" rx="{raio:.1f}" fill="url(#{id_}t)"/>'
             f'<rect x="{x + k:.2f}" y="{y + k:.2f}" width="{lado - 2 * k:.2f}" height="{lado - 2 * k:.2f}" rx="{raio - k:.1f}" '
             f'fill="none" stroke="{m["borda"]}" stroke-width="{2 * k:.2f}"/>'
             + texto(m["letras"], "wordmark", 22 * lado / 48, x + m["x"] * lado / 48, y + 31.5 * lado / 48, cor=m["letra"]))
    return defs, corpo


def _quebrar(s, fonte, tamanho, maximo):
    linhas, atual = [], ""
    for palavra in s.split():
        tentativa = f"{atual} {palavra}".strip()
        if atual and largura(tentativa, fonte, tamanho) > maximo:
            linhas.append(atual)
            atual = palavra
        else:
            atual = tentativa
    return linhas + [atual]


CSS_BASE = """
@keyframes girar{to{transform:rotate(360deg)}}
@keyframes respirar{50%{opacity:.55}}
@keyframes fio{0%,100%{opacity:.35}50%{opacity:1}}
@keyframes entrar{from{opacity:0;transform:translateY(18px)}}
@keyframes flutuar{50%{transform:translateY(-5px)}}
@keyframes surgir{from{opacity:0}}
.gira{animation:girar 14s linear infinite}
.fio{animation:fio 5s ease-in-out infinite}
"""


# --------------------------------------------------------------------------- banner

def banner(dados, perfil):
    L = 1200
    nome = "Lecodaro"
    tracking = -0.035
    # o wordmark ocupa a largura: "Lecodaro" + margem + esfera (7 e 16 de 92, como no branding)
    em_total = largura(nome, "wordmark", 1, tracking) + (7 + 16) / 92
    tamanho = 1000 / em_total
    cap = altura_maiuscula("wordmark", tamanho)
    largura_nome = largura(nome, "wordmark", tamanho, tracking)
    x_nome = (L - tamanho * em_total) / 2
    base = 78 + cap
    r_esfera = tamanho * 8 / 92
    cx_esfera = x_nome + largura_nome + tamanho * 7 / 92 + r_esfera
    cy_esfera = base - r_esfera
    base_sub = base + 74
    topo_pontos = base_sub + 66
    passo = 1060 / 52
    base_legenda = topo_pontos + 6 * 19 + 46
    A = round(base_legenda + 36)

    defs_vidro, fundo, vidro = _vidro("b", L, A, 40)
    defs = [defs_vidro]
    luzes = []
    for id_, cx, cy, r, rgb, op, classe in (("la", 40, A + 40, 330, "251,138,92", .30, "derivaA"),
                                            ("lb", L / 2, A + 120, 360, "69,214,126", .20, "derivaB"),
                                            ("lc", L - 40, -40, 340, "95,160,255", .30, "derivaC")):
        d, c = _luz(id_, cx, cy, r, rgb, op, classe)
        defs.append(d)
        luzes.append(c)
    d_esfera, c_esfera = esfera("e", cx_esfera, cy_esfera, r_esfera)
    defs.append(d_esfera)

    css = CSS_BASE + """
@keyframes subir{from{opacity:0;transform:translateY(40px)}}
@keyframes derivaA{50%{transform:translate(110px,-40px)}}
@keyframes derivaB{50%{transform:translate(-120px,-30px)}}
@keyframes derivaC{50%{transform:translate(-90px,50px)}}
@keyframes pulsar{50%{opacity:.3}}
@keyframes anel{from{transform:scale(1);opacity:.9}to{transform:scale(3.4);opacity:0}}
.derivaA{animation:derivaA 18s ease-in-out infinite}
.derivaB{animation:derivaB 22s ease-in-out infinite}
.derivaC{animation:derivaC 20s ease-in-out infinite}
.letra{animation:subir 1s cubic-bezier(.2,.7,.2,1) both;animation-delay:calc(var(--i) * 70ms + 120ms)}
.esf{animation:entrar 1s cubic-bezier(.2,.7,.2,1) .8s both}
.sub{animation:surgir 1.2s ease-out 1s both}
.col{animation:surgir .5s ease-out both}
.ponto{animation:pulsar 5s ease-in-out infinite}
.anel{transform-box:fill-box;transform-origin:center;animation:anel 2.2s ease-out infinite}
.leg{animation:surgir 1s ease-out 1.6s both}"""

    partes = ['<g clip-path="url(#bc)">', fundo, *luzes, vidro]
    partes.append(texto(nome, "wordmark", tamanho, x_nome, base, cor=TITULO, tracking=tracking, classe="letra", por_letra=True))
    partes.append(f'<g class="esf">{c_esfera}</g>')
    partes.append(f'<g class="sub">{texto(perfil["subtitulo"], "display", 34, L / 2, base_sub, cor=TEXTO_2, ancora="meio", tracking=-0.01)}</g>')

    # cada ponto é um dia do último ano; o brilho é o nível de contribuição daquele dia
    niveis = {"NONE": .07, "FIRST_QUARTILE": .28, "SECOND_QUARTILE": .5, "THIRD_QUARTILE": .75, "FOURTH_QUARTILE": .95}
    x0 = (L - 1060) / 2
    semanas = dados["semanas"]
    for w, semana in enumerate(semanas):
        col = [f'<g class="col" style="animation-delay:{0.9 + w * 0.018:.3f}s">']
        for dia in semana:
            d = date.fromisoformat(dia["data"]).isoweekday() % 7
            cx, cy = x0 + w * passo, topo_pontos + d * 19
            classe = ""
            if dia["nivel"] != "NONE":
                classe = f' class="ponto" style="animation-delay:{-ruido(w * 7 + d) * 5:.2f}s"'
            col.append(f'<circle{classe} cx="{cx:.1f}" cy="{cy}" r="4.4" fill="#fff" fill-opacity="{niveis.get(dia["nivel"], .07)}"/>')
        col.append("</g>")
        partes.append("".join(col))
    ultimo = semanas[-1][-1]
    d = date.fromisoformat(ultimo["data"]).isoweekday() % 7
    partes.append(f'<circle class="anel" cx="{x0 + (len(semanas) - 1) * passo:.1f}" cy="{topo_pontos + d * 19}" r="4.4" '
                  f'fill="none" stroke="#fff" stroke-opacity=".8" stroke-width="1.4"/>')
    esquerda = f"{milhar(dados['contribuicoes_ano'])} contribuições no último ano"
    direita = f"{milhar(dados['commits'])} commits"
    partes.append(f'<g class="leg">{texto(esquerda.upper(), "mono_medio", 14, x0, base_legenda, cor=ROTULO, tracking=0.16)}'
                  f'{texto(direita.upper(), "mono_medio", 14, L - x0, base_legenda, cor=ROTULO, ancora="fim", tracking=0.16)}</g>')
    partes.append("</g>")
    return documento(L, A, f"Lecodaro: {perfil['subtitulo']}. Cada ponto é um dia de contribuição no GitHub no último ano.",
                     css, "".join(partes), "".join(defs))


# --------------------------------------------------------------------------- marcas

def cabecalho_marcas():
    L, A = 1200, 72
    defs_vidro, fundo, vidro = _vidro("h", L, A, 22)
    frase = [("Todo dado precisa de ", TEXTO_2), ("ordem", "#5ee08f"), (", toda ideia precisa de ", TEXTO_2),
             ("forma", "#ff9a6e"), (", toda descoberta precisa de ", TEXTO_2), ("voz", "#8cb6ff")]
    total = sum(largura(t, "display", 17) for t, _ in frase)
    x = L - 36 - total
    partes = ['<g clip-path="url(#hc)">', fundo, vidro,
              texto("CONHEÇA AS MARCAS DA LECODARO", "mono_medio", 14, 36, 41, cor=ROTULO, tracking=0.22)]
    for t, cor in frase:
        partes.append(texto(t, "display", 17, x, 42, cor=cor))
        x += largura(t, "display", 17)
    partes.append("</g>")
    return documento(L, A, "Conheça as marcas da Lecodaro. Todo dado precisa de ordem, toda ideia precisa de forma, "
                     "toda descoberta precisa de voz.", CSS_BASE, "".join(partes), defs_vidro)


def cartao_marca(marca, indice):
    L, A = 400, 298
    m = MARCAS[marca["id"]]
    atraso = indice * 0.25
    defs_vidro, fundo, vidro = _vidro("m", L, A, 30)
    d_luz, c_luz = _luz("ml", 30, 20, 230, m["luz"], m["luz_op"], "brilho")
    d_ico, c_ico = icone("i", marca["id"], 34, 34, 84)
    css = CSS_BASE + f"""
.brilho{{animation:respirar 6s ease-in-out {-atraso * 4:.1f}s infinite}}
.ico{{animation:entrar .8s cubic-bezier(.2,.7,.2,1) {atraso:.2f}s both}}
.flutua{{animation:flutuar 4.5s ease-in-out {atraso:.2f}s infinite}}
.txt{{animation:entrar .8s cubic-bezier(.2,.7,.2,1) {atraso + 0.15:.2f}s both}}"""
    nome_l = largura("Lecodaro", "wordmark", 40, -0.03)
    partes = ['<g clip-path="url(#mc)">', fundo, c_luz, vidro,
              f'<g class="ico"><g class="flutua">{c_ico}</g></g>', '<g class="txt">',
              texto("Lecodaro", "wordmark", 40, 34, 176, cor="#f4f4f6", tracking=-0.03),
              texto(marca["sufixo"], m["fonte"], 19, 34 + nome_l + 12, 176, cor=m["sufixo"], tracking=-0.015),
              texto(marca["dominio"], "mono", 15, 34, 206, cor=DOMINIO)]
    for i, linha in enumerate(_quebrar(marca["descricao"], "texto", 17, L - 68)):
        partes.append(texto(linha, "texto", 17, 34, 244 + i * 25, cor=TEXTO))
    partes.append("</g></g>")
    return documento(L, A, f"Lecodaro {marca['sufixo']} ({marca['dominio']}): {marca['descricao']}",
                     css, "".join(partes), defs_vidro + d_luz + d_ico)


# --------------------------------------------------------------------------- linguagens

def linguagens(dados, perfil):
    L, A = 1200, 252
    total = sum(dados["linguagens"].get(i["linguagem"], 0) for i in perfil["codigo"]) or 1
    medidas = sorted(((i, dados["linguagens"].get(i["linguagem"], 0) / total) for i in perfil["codigo"]), key=lambda m: -m[1])
    itens = medidas + [(i, None) for i in perfil["carreira"]]
    margem, divisao = 56, 36
    largura_item = (L - 2 * margem - divisao) / len(itens)
    defs_vidro, fundo, vidro = _vidro("g", L, A, 30)
    defs = defs_vidro + ('<linearGradient id="trio" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fb8a5c"/>'
                         '<stop offset=".5" stop-color="#45d67e"/><stop offset="1" stop-color="#5fa0ff"/></linearGradient>')
    css = CSS_BASE + """
@keyframes encher{from{transform:scaleX(0)}}
.item{animation:entrar .8s cubic-bezier(.2,.7,.2,1) both}
.flutua{animation:flutuar 5s ease-in-out infinite}
.barra{transform-box:fill-box;transform-origin:left;animation:encher 1.2s cubic-bezier(.2,.7,.2,1) both}
.cab{animation:surgir 1s ease-out both}"""
    x_div = margem + len(medidas) * largura_item + divisao / 2
    partes = ['<g clip-path="url(#gc)">', fundo, vidro,
              f'<g class="cab">{texto("NO CÓDIGO DA LECODARO", "mono_medio", 13, margem + 12, 60, cor=ROTULO, tracking=0.22)}'
              f'{texto("TAMBÉM NA CARREIRA", "mono_medio", 13, x_div + divisao / 2 + 12, 60, cor=ROTULO, tracking=0.22)}</g>',
              f'<rect x="{x_div:.1f}" y="44" width="1" height="{A - 88}" fill="#fff" fill-opacity=".1"/>']
    for n, (item, parte) in enumerate(itens):
        x = margem + n * largura_item + (divisao if parte is None else 0)
        cx = x + largura_item / 2
        atraso = 0.2 + n * 0.07
        bloco = [f'<g class="item" style="animation-delay:{atraso:.2f}s"><g class="flutua" style="animation-delay:{-n * 0.45:.2f}s">']
        if item.get("icone"):
            ic = ICONES[item["icone"]]
            bloco.append(f'<path fill="{ic["cor"]}" transform="translate({cx - 20:.1f} 92) scale({40 / 24:.4f})" d="{ic["d"]}"/>')
        else:
            bloco.append(texto(item["nome"], "wordmark", 30, cx, 124, cor=item["cor"], ancora="meio"))
        bloco.append("</g>")
        bloco.append(texto(item["nome"], "texto_medio", 15, cx, 168, cor="#9aa0aa", ancora="meio"))
        if parte is not None:
            bloco.append(f'<rect x="{cx - 30:.1f}" y="184" width="60" height="4" rx="2" fill="#fff" fill-opacity=".08"/>')
            bloco.append(f'<rect class="barra" style="animation-delay:{atraso + 0.4:.2f}s" x="{cx - 30:.1f}" y="184" '
                         f'width="{max(3, 60 * parte):.1f}" height="4" rx="2" fill="url(#trio)"/>')
            bloco.append(texto(f"{parte * 100:.0f}%", "mono", 13, cx, 210, cor=DOMINIO, ancora="meio"))
        bloco.append("</g>")
        partes.append("".join(bloco))
    partes.append("</g>")
    return documento(L, A, "Linguagens que o Lenin mais programa no código da Lecodaro e as que usa na carreira",
                     css, "".join(partes), defs)


# --------------------------------------------------------------------------- botões

SETA = "M0 12 L12 0 M3 0 H12 V9"


def botao(tipo):
    L, A = 580, 132
    defs_vidro, fundo, vidro = _vidro("k", L, A, 28)
    defs = [defs_vidro]
    lado, ix, iy = 76, 28, 28
    if tipo == "linkedin":
        d_luz, c_luz = _luz("kl", 40, 20, 220, "10,102,194", .35, "brilho")
        ico = (f'<rect x="{ix}" y="{iy}" width="{lado}" height="{lado}" rx="{lado * 23 / 96:.1f}" fill="#0a66c2"/>'
               + texto("in", "wordmark", 44, ix + lado / 2, iy + 54, cor="#fff", ancora="meio", tracking=-0.02))
        titulo = texto("LinkedIn", "wordmark", 34, 128, 70, cor="#f4f4f6", tracking=-0.02)
        sub, rotulo = "linkedin.com/in/lenincst", "LinkedIn de Lenin Costa da Rosa"
    else:
        d_luz, c_luz = _luz("kl", 40, 20, 220, "95,160,255", .22, "brilho")
        defs.append('<linearGradient id="kg" x1=".27" y1="0" x2=".73" y2="1"><stop offset="0" stop-color="#1b1d22"/>'
                    '<stop offset="1" stop-color="#0b0c0f"/></linearGradient>')
        d_esf, c_esf = esfera("ke", ix + lado / 2, iy + lado / 2, lado * 19 / 96)
        defs.append(d_esf)
        ico = (f'<rect x="{ix}" y="{iy}" width="{lado}" height="{lado}" rx="{lado * 23 / 96:.1f}" fill="url(#kg)"/>'
               f'<rect x="{ix + .8}" y="{iy + .8}" width="{lado - 1.6}" height="{lado - 1.6}" rx="{lado * 23 / 96 - .8:.1f}" '
               f'fill="none" stroke="#fff" stroke-opacity=".34" stroke-width="1.6"/>' + c_esf)
        l_nome = largura("Lecodaro", "wordmark", 34, -0.035)
        d_pt, c_pt = esfera("kp", 128 + l_nome + 6, 70 - 3.2, 3.2)
        defs.append(d_pt)
        titulo = texto("Lecodaro", "wordmark", 34, 128, 70, cor="#f4f4f6", tracking=-0.035) + c_pt
        sub, rotulo = "lecodaro.com", "Site da Lecodaro"
    defs.append(d_luz)
    css = CSS_BASE + ".brilho{animation:respirar 6s ease-in-out infinite}"
    partes = ['<g clip-path="url(#kc)">', fundo, c_luz, vidro, ico, titulo,
              texto(sub, "mono", 16, 128, 100, cor=DOMINIO),
              f'<path d="{SETA}" transform="translate({L - 52} {A / 2 - 6})" fill="none" stroke="{ROTULO}" '
              f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>', "</g>"]
    return documento(L, A, rotulo, css, "".join(partes), "".join(defs))
