"""As cenas do LeninOS: cada função devolve um SVG pronto."""
import math
from datetime import date

from pixel import Camada, documento, faixas, gradiente, largura_texto, ruido

L = 416  # largura de todas as cenas: mesma escala de pixel em todas as imagens
BRANCO, PRETO = "#ffffff", "#000000"
BEGE, BEGE_ESCURO, CINZA_BORDA = "#ece9d8", "#d6d2c2", "#919b9c"
AZUL_TEXTO = "#0b3d91"

TITULO = ["#5aa6ff", "#3d8eff", "#2b7cf6", "#2270ef", "#1d68ea", "#1a62e6", "#185de2", "#1658de", "#1554da",
          "#1450d5", "#134cd0", "#1249cb", "#1146c6", "#1043c0", "#0f40bb", "#0e3db5", "#0d3aaf", "#0c37a9"]

SOL_MINI = ["..yyy..", ".yYYYy.", "yYYwYYy", "yYwwwYy", "yYYwYYy", ".yYYYy.", "..yyy.."]
PALETA_SOL = {"y": "#ff9f1c", "Y": "#ffd23f", "w": "#fff6c4"}


def milhar(n):
    return f"{n:,}".replace(",", ".")


def _texto_sombra(c, x, y, s, cor, sombra, escala=1):
    c.texto(x + escala, y + escala, s, sombra, escala)
    c.texto(x, y, s, cor, escala)


def _texto_contorno(c, x, y, s, cor, contorno, escala=1):
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1)):
        c.texto(x + dx, y + dy, s, contorno, escala)
    c.texto(x, y, s, cor, escala)


def _botao_xp(c, x, y, l, a, rotulo, foco=False, desativado=False):
    faixas(c, x, y, l, a, gradiente("#ffffff", "#e3e0d0", a))
    for i in range(l):
        c.px(x + i, y, "#003c74")
        c.px(x + i, y + a - 1, "#003c74")
    for j in range(a):
        c.px(x, y + j, "#003c74")
        c.px(x + l - 1, y + j, "#003c74")
    if foco:
        for i in range(1, l - 1):
            c.px(x + i, y + 1, "#cee7ff")
            c.px(x + i, y + a - 2, "#6982ee")
    for px, py in ((x, y), (x + l - 1, y), (x, y + a - 1), (x + l - 1, y + a - 1)):
        c.apagar(px, py)
    cor = "#a0a0a0" if desativado else PRETO
    c.texto(x + (l - largura_texto(rotulo)) // 2, y + (a - 8) // 2 + 1, rotulo, cor)


def janela(c, a, titulo, icone=None):
    """Moldura de janela azul (estilo anos 2000) ocupando a cena inteira."""
    for i, cor in enumerate(TITULO):
        c.ret(0, i, L, 1, cor)
    c.ret(0, 18, L, a - 18, "#0b47d6")
    c.ret(3, 18, L - 6, a - 21, BEGE)
    for x, y in ((0, 0), (1, 0), (2, 0), (0, 1), (0, 2), (L - 1, 0), (L - 2, 0), (L - 3, 0), (L - 1, 1), (L - 1, 2)):
        c.apagar(x, y)
    for x in range(3, L - 3):
        c.px(x, 0, "#7fbaff")
    xt = 6
    if icone:
        c.sprite(5, 5, icone[0], icone[1])
        xt = 16
    _texto_sombra(c, xt, 5, titulo, BRANCO, "#0a2a7a")
    # botões: minimizar, maximizar, fechar
    for i, (cor1, cor2) in enumerate((("#5d9bff", "#2563e0"), ("#5d9bff", "#2563e0"), ("#ee8a63", "#c8401a"))):
        bx = L - 54 + i * 17
        faixas(c, bx, 2, 15, 14, gradiente(cor1, cor2, 14))
        for k in range(15):
            c.px(bx + k, 2, BRANCO)
            c.px(bx + k, 15, BRANCO)
        for k in range(14):
            c.px(bx, 2 + k, BRANCO)
            c.px(bx + 14, 2 + k, BRANCO)
        for px, py in ((bx, 2), (bx + 14, 2), (bx, 15), (bx + 14, 15)):
            c.apagar(px, py)
    c.ret(L - 50, 11, 6, 2, BRANCO)                      # _
    c.ret(L - 34, 5, 8, 7, BRANCO)                       # []
    c.ret(L - 33, 7, 6, 4, "#2a6cea")
    for k in range(7):                                   # X
        c.px(L - 16 + k, 5 + k, BRANCO)
        c.px(L - 15 + k, 5 + k, BRANCO)
        c.px(L - 10 - k, 5 + k, BRANCO)
        c.px(L - 9 - k, 5 + k, BRANCO)


def _abas(c, y, nomes, ativa):
    x = 8
    for i, nome in enumerate(nomes):
        l = largura_texto(nome) + 12
        if i == ativa:
            c.ret(x, y, l, 15, "#fcfcfe")
            c.ret(x, y, l, 2, "#ffc83c")
            c.ret(x - 1, y + 2, 1, 13, CINZA_BORDA)
            c.ret(x + l, y + 2, 1, 13, CINZA_BORDA)
        else:
            c.ret(x, y + 2, l, 13, "#f4f3ee")
            c.ret(x, y + 2, l, 1, CINZA_BORDA)
            c.ret(x - 1, y + 3, 1, 12, CINZA_BORDA)
            c.ret(x + l, y + 3, 1, 12, CINZA_BORDA)
        c.texto(x + 6, y + 4, nome, PRETO)
        x += l + 2


def _painel(c, x, y, l, a, cor="#fcfcfe"):
    c.ret(x, y, l, a, CINZA_BORDA)
    c.ret(x + 1, y + 1, l - 2, a - 2, cor)


# --------------------------------------------------------------------------- abertura

def _colina_frente(x):
    return 158 - 26 * math.exp(-((x - 280) / 150) ** 2)


def _colina_fundo(x):
    return 140 - 16 * math.exp(-((x - 90) / 90) ** 2)


FLORES = {
    "FIRST_QUARTILE": ([".....", "..w..", ".wyw.", "..w..", "..g.."], {"w": "#ffffff", "y": "#ffd400", "g": "#2f7d1f"}),
    "SECOND_QUARTILE": ([".....", "..Y..", ".YoY.", "..Y..", "..g.."], {"Y": "#ffd400", "o": "#ff8c00", "g": "#2f7d1f"}),
    "THIRD_QUARTILE": (["..P..", ".PoP.", "..P..", ".gg..", "..g.."], {"P": "#ff7eb6", "o": "#fff2a8", "g": "#2f7d1f"}),
    "FOURTH_QUARTILE": ([".R.R.", "RRoRR", ".RRR.", "..g..", ".gg.."], {"R": "#ff3d57", "o": "#ffe14d", "g": "#2f7d1f"}),
}


def _nuvem(c, x, y, s):
    for cx, cy, rx, ry in ((0, 4, 9, 5), (9, 1, 9, 7), (19, 4, 9, 5), (8, 6, 13, 4)):
        c.elipse(x + cx * s, y + cy * s, rx * s, ry * s, BRANCO)
    for xx in range(int(x - 8 * s), int(x + 28 * s)):
        c.px(xx, int(y + 9 * s), "#dbe9ff")


def abertura(dados, perfil):
    a = 234
    css = [
        "@keyframes amanhecer{from{opacity:1}to{opacity:0}}",
        "@keyframes nascer{0%{transform:translateY(112px)}55%{transform:translateY(24px)}80%{transform:translateY(6px)}100%{transform:none}}",
        "@keyframes aparecer{from{opacity:0}to{opacity:1}}",
        "@keyframes piscar{50%{opacity:0}}",
        "@keyframes vento{from{transform:translateX(-160px)}to{transform:translateX(520px)}}",
        "@keyframes voar{from{transform:translateX(-60px)}to{transform:translateX(480px)}}",
        ".aurora{opacity:0;animation:amanhecer 4s steps(8) .4s both}",
        ".sol{animation:nascer 4.4s steps(14) .2s both}",
        ".raio1{animation:piscar 1s steps(1) infinite}",
        ".raio2{animation:piscar 1s steps(1) -.5s infinite}",
        ".sub{animation:aparecer .6s steps(3) 4.5s both}",
        ".flor{animation:aparecer .3s steps(2) both}",
        ".n1{animation:vento 90s steps(680) -30s infinite}",
        ".n2{animation:vento 120s steps(680) -85s infinite}",
        ".n3{animation:vento 70s steps(680) -12s infinite}",
        ".ave{animation:voar 26s steps(540) 6s infinite}",
        ".asaA{animation:piscar .5s steps(1) infinite}",
        ".asaB{animation:piscar .5s steps(1) -.25s infinite}",
        ".placa{animation:aparecer .4s steps(2) 6.4s both}",
    ]
    raiz = Camada()

    ceu = raiz.adicionar(Camada())
    faixas(ceu, 0, 0, L, 160, gradiente("#1a5fd6", "#a6d8ff", 16))

    aurora = raiz.adicionar(Camada("aurora"))
    faixas(aurora, 0, 0, L, 160, gradiente("#1b1140", "#4a2470", 6) + gradiente("#7a2f78", "#ff9a52", 10))
    for i in range(40):
        aurora.px(int(ruido(i, 1) * L), int(ruido(i, 2) * 70), "#fff7d6")

    # o sol: "LECODARO LTDA" nascendo atrás da colina
    sol = raiz.adicionar(Camada("sol"))
    cx, cy = 208, 58
    halo = Camada()
    for y in range(cy - 56, cy + 57):
        for x in range(cx - 64, cx + 65):
            r = math.hypot(x - cx, y - cy)
            if 38 < r <= 46 and (x + y) % 2 == 0:
                halo.px(x, y, "#ffe9a6")
            elif 46 < r <= 54 and x % 2 == 0 and y % 2 == 0:
                halo.px(x, y, "#fff3c9")
    sol.adicionar(halo)
    disco = Camada()
    for i, cor in enumerate(gradiente("#fff6c4", "#ffb000", 9) + gradiente("#ffa400", "#ff7a00", 9)):
        for y in range(cy - 36 + i * 4, cy - 36 + (i + 1) * 4):
            meia = math.sqrt(max(0, 36 ** 2 - (y - cy + 0.5) ** 2))
            disco.ret(round(cx - meia), y, round(2 * meia), 1, cor)
    sol.adicionar(disco)
    for k, classe in ((0, "raio1"), (1, "raio2")):
        raios = sol.adicionar(Camada(classe))
        for i in range(8):
            ang = (i * 2 + k) * math.pi / 8
            raios.linha(round(cx + 58 * math.cos(ang)), round(cy + 58 * math.sin(ang) * 0.9),
                        round(cx + 68 * math.cos(ang)), round(cy + 68 * math.sin(ang) * 0.9), "#ffe066")
    titulo = perfil["empresa"]
    _texto_contorno(sol.adicionar(Camada()), cx - largura_texto(titulo, 2) // 2, cy - 8, titulo, BRANCO, "#a33b00", 2)

    for classe, x, y, s in (("n1", 40, 12, 1), ("n2", 250, 8, 1.3), ("n3", 330, 80, 0.8)):
        _nuvem(raiz.adicionar(Camada(classe)), x, y, s)

    ave = raiz.adicionar(Camada("ave"))
    for i, (bx, by) in enumerate(((10, 34), (22, 28), (30, 38))):
        ave.adicionar(Camada("asaA")).sprite(bx, by, ["#...#", ".#.#.", "..#.."], {"#": "#24324a"})
        ave.adicionar(Camada("asaB")).sprite(bx, by, [".....", "##.##", "..#.."], {"#": "#24324a"})

    sub = raiz.adicionar(Camada("sub"))
    frase = f"{perfil['cargo']} · {perfil['funcao']}"
    _texto_sombra(sub, (L - largura_texto(frase)) // 2, 108, frase, BRANCO, "#0b2a6b")

    campo = raiz.adicionar(Camada())
    sombra_noite = Camada("aurora")
    for x in range(L):
        topo_fundo, topo_frente = round(_colina_fundo(x)), round(_colina_frente(x))
        for y in range(topo_fundo, topo_frente):
            campo.px(x, y, "#2f7330" if ruido(x, y, 3) < 0.12 else gradiente("#4a9e3d", "#367f33", 4)[min(3, (y - topo_fundo) // 5)])
        for y in range(topo_frente, 218):
            prof = min(5, (y - topo_frente) // 9)
            cor = gradiente("#86df5a", "#3c932b", 6)[prof]
            campo.px(x, y, "#3f9a2b" if ruido(x, y, 5) < 0.08 else cor)
        campo.px(x, topo_frente, "#b2f27a")
        for y in range(min(topo_fundo, topo_frente), 218):
            sombra_noite.px(x, y, "#1b0d33")
    sombra_noite.estilo = "fill-opacity:.55"

    # flores: uma por dia com contribuição, semana a semana, da esquerda para a direita
    x0 = 68
    for w, semana in enumerate(dados["semanas"]):
        flor = Camada("flor", f"animation-delay:{4.8 + w * 0.035:.3f}s")
        xc = x0 + w * 6
        topo = round(_colina_frente(xc + 2)) + 5
        for dia in semana:
            d = date.fromisoformat(dia["data"]).isoweekday() % 7
            desenho = FLORES.get(dia["nivel"])
            if desenho:
                flor.sprite(xc, topo + d * 6, *desenho)
        raiz.adicionar(flor)
    raiz.adicionar(sombra_noite)

    placa = raiz.adicionar(Camada("placa"))
    placa.ret(16, 140, 3, 26, "#5b3410")
    placa.ret(52, 140, 3, 26, "#5b3410")
    placa.ret(4, 124, 64, 24, "#6b3f17")
    placa.ret(5, 125, 62, 22, "#b06d30")
    for x in range(5, 67, 7):
        placa.px(x, 130, "#9a5c25")
        placa.px(x + 3, 141, "#9a5c25")
    n = milhar(dados["contribuicoes_ano"])
    placa.texto(4 + (64 - largura_texto(n)) // 2, 127, n, "#3b2208")
    placa.texto(4 + (64 - largura_texto("no ano")) // 2, 137, "no ano", "#3b2208")

    marca = raiz.adicionar(Camada())
    _texto_sombra(marca, L - largura_texto("LeninOS") - 6, 206, "LeninOS", BRANCO, "#1e5a14")

    # barra de tarefas
    barra = raiz.adicionar(Camada())
    barra.ret(0, 218, L, 1, "#3c80f6")
    faixas(barra, 0, 219, L, 15, gradiente("#2c6ff0", "#1d4fc4", 15))
    faixas(barra, 0, 218, 80, 16, gradiente("#5cbf55", "#2a7f2a", 16))
    for x, y in ((79, 218), (78, 218), (79, 219), (79, 233), (78, 233), (79, 232)):
        barra.apagar(x, y)
    barra.sprite(6, 222, SOL_MINI, PALETA_SOL)
    _texto_sombra(barra, 18, 222, "iniciar", BRANCO, "#1b4d16")
    for x, l, rotulo, ativo in ((86, 124, perfil["empresa"], True), (214, 78, "dev.exe", False)):
        barra.ret(x, 220, l, 12, "#1a45ad" if ativo else "#3c81f3")
        barra.ret(x, 220, l, 1, "#163d9c" if ativo else "#6fa3ff")
        if ativo:
            barra.sprite(x + 3, 222, SOL_MINI, PALETA_SOL)
        else:
            barra.ret(x + 3, 222, 9, 8, PRETO)
            barra.texto(x + 3, 222, ">", "#c0c0c0")
        barra.texto(x + 14, 222, rotulo[:13], BRANCO)
    faixas(barra, 344, 218, L - 344, 16, gradiente("#18a0f0", "#0b78d4", 16))
    barra.ret(344, 218, 1, 16, "#0a5aa8")
    barra.sprite(350, 222, ["..#....", ".##.#..", "###..#.", "###..#.", ".##.#..", "..#...."], {"#": BRANCO})
    hoje = date.fromisoformat(dados["gerado_em"][:10]).strftime("%d/%m")
    barra.texto(L - largura_texto(hoje) - 6, 222, hoje, BRANCO)

    titulo_svg = f"{perfil['empresa']} nascendo como o sol sobre um campo de flores; cada flor é um dia com contribuição no GitHub"
    return documento(L, a, titulo_svg, "".join(css), raiz)


# --------------------------------------------------------------------------- propriedades do sistema

def _monitor(c, x, y):
    c.ret(x, y, 64, 50, "#7d7a6e")
    c.ret(x + 1, y + 1, 62, 48, "#e8e4d4")
    c.ret(x + 5, y + 5, 54, 38, "#2a2a2a")
    faixas(c, x + 7, y + 7, 50, 34, gradiente("#3a86e8", "#bfe3ff", 8))
    c.elipse(x + 32, y + 30, 8, 8, "#ffc23a")
    c.elipse(x + 32, y + 30, 5, 5, "#fff2a6")
    for xx in range(x + 7, x + 57):
        topo = round(y + 34 - 4 * math.exp(-((xx - x - 40) / 14) ** 2))
        c.ret(xx, topo, 1, y + 41 - topo, "#4fb83a")
    c.ret(x + 24, y + 50, 16, 4, "#7d7a6e")
    c.ret(x + 14, y + 54, 36, 4, "#5f5d55")


def sistema(dados, perfil):
    linhas = [
        ("Sistema:", None),
        ("LeninOS Professional", PRETO),
        (f"Edição Fundador · desde {dados['conta_desde'][:4]}", PRETO),
        ("", None),
        ("Registrado para:", None),
        (perfil["nome"], PRETO),
        (f"{perfil['cargo']} · {perfil['empresa']}", PRETO),
        (perfil["funcao"], PRETO),
        (f"Foco: {perfil['especialidade']}", PRETO),
        ("", None),
        ("Computador:", None),
        (f"{perfil['cidade']} · {perfil['pais']}", PRETO),
        (f"{milhar(dados['commits'])} commits · {perfil['anos_programando']} anos", PRETO),
        (f"Pico de energia: {_pico(dados)}h", PRETO),
        (f"Recorde: {dados['sequencias']['maior']} dias seguidos", PRETO),
    ]
    a = 50 + len(linhas) * 11 + 40
    c = Camada()
    janela(c, a, "Propriedades do sistema", (SOL_MINI, PALETA_SOL))
    _abas(c, 24, ["Geral", "Marcas", "Código", "Café"], 0)
    _painel(c, 6, 39, L - 12, a - 72)
    _monitor(c, 18, 56)
    y = 48
    for texto, cor in linhas:
        if texto:
            if cor is None:
                c.texto(100, y, texto, AZUL_TEXTO)
            else:
                c.texto(116, y, texto, cor)
        y += 11
    by = a - 26
    _botao_xp(c, L - 214, by, 64, 17, "OK", foco=True)
    _botao_xp(c, L - 144, by, 72, 17, "Cancelar")
    _botao_xp(c, L - 66, by, 58, 17, "Aplicar", desativado=True)
    return documento(L, a, f"Propriedades do sistema: {perfil['nome']}, {perfil['cargo']} da {perfil['empresa']}, {perfil['funcao']}", "", c)


def _pico(dados):
    return max(range(24), key=lambda h: dados["horas"][h])


# --------------------------------------------------------------------------- prompt de comando

def terminal(dados, perfil):
    cinza, branco, verde, amarelo = "#c0c0c0", "#ffffff", "#3cff5a", "#ffd23c"
    prompt = "C:\\LECODARO>"
    roteiro = [
        ("cmd", "whoami"),
        ("out", [(perfil["nome"], branco)]),
        ("out", [(f"{perfil['cargo']} da {perfil['empresa']}", amarelo)]),
        ("out", [(f"{perfil['funcao']} · {perfil['anos_programando']} anos", cinza)]),
        ("vazio", None),
        ("cmd", "dir marcas"),
    ]
    for m in perfil["marcas"]:
        cor = verde if m["situacao"] == "ONLINE" else amarelo
        roteiro.append(("out", [(f"{m['dominio']:<16}{m['curta']:<22}", cinza), (m["situacao"], cor)]))
    roteiro += [("vazio", None), ("cmd", "type especialidade.txt"),
                ("out", [(f"Tecnologia para {perfil['especialidade']}:", branco)])]
    roteiro += [("out", [(linha, cinza)]) for linha in perfil["faz"]]
    roteiro += [
        ("vazio", None),
        ("cmd", "git shortlog -sn --author=lenin"),
        ("out", [(f"{dados['commits']:>6}  ", amarelo), (perfil["nome"], branco)]),
        ("out", [(f"{dados['repos_total']} repositórios · {dados['repos_privados']} privados (código da empresa)", cinza)]),
        ("vazio", None),
        ("cmd", "echo %HORA_FAVORITA%"),
        ("out", [(f"{_pico(dados)}h · o melhor código sai à noite", cinza)]),
        ("vazio", None),
        ("fim", None),
    ]
    altura_linha = 10
    a = 18 + 8 + len(roteiro) * altura_linha + 6
    raiz = Camada()
    moldura = raiz.adicionar(Camada())
    janela(moldura, a, "Prompt de comando - lenin@lecodaro",
           ([".######.", "#PPPPPP#", "#P>PPPP#", "#PP>PPP#", "#P>P__P#", "#PPPPPP#", ".######."],
            {"#": "#c0c0c0", "P": PRETO, ">": BRANCO, "_": BRANCO}))
    moldura.ret(3, 18, L - 6, a - 21, PRETO)

    corpo = raiz.adicionar(Camada(estilo="clip-path:url(#corpo)"))
    raiz.filhos.insert(0, f'<defs><clipPath id="corpo"><rect x="3" y="18" width="{L - 6}" height="{a - 21}"/></clipPath></defs>')
    css = ["@keyframes piscar{50%{opacity:0}}", ".cursor{animation:piscar 1s steps(1) infinite}"]
    t = 0.6
    y = 26
    x0 = 7
    capas = []

    def capa(x, largura, inicio, duracao, passos):
        """Retângulo preto que esconde o texto e anda para a direita (efeito de digitação).
        Mora fora da tela: só cobre o texto antes e durante a animação (fill backwards)."""
        nome = f"c{len(capas)}"
        fora = L + 10
        css.append(f"@keyframes {nome}{{from{{transform:translateX({x - fora}px)}}to{{transform:translateX({x + largura - fora}px)}}}}"
                   f".{nome}{{animation:{nome} {duracao:.2f}s steps({passos}) {inicio:.2f}s backwards}}")
        capas.append(f'<rect class="{nome}" x="{fora}" y="{y - 1}" width="{largura + 2}" height="{altura_linha}" fill="#000"/>')

    for tipo, conteudo in roteiro:
        if tipo in ("cmd", "fim"):
            corpo.texto(x0, y, prompt, cinza)
            capa(x0, largura_texto(prompt), t, 0.05, 1)
            t += 0.25
            if tipo == "cmd":
                xc = x0 + largura_texto(prompt + " ")
                corpo.texto(xc, y, conteudo, branco)
                duracao = len(conteudo) * 0.055
                capa(xc, largura_texto(conteudo), t, duracao, len(conteudo))
                t += duracao + 0.35
            else:
                cursor = Camada("cursor")
                cursor.ret(x0 + largura_texto(prompt + " "), y + 6, 8, 2, cinza)
                corpo.adicionar(cursor)
        elif tipo == "out":
            x = x0 + 16
            for texto, cor in conteudo:
                corpo.texto(x, y, texto, cor)
                x += largura_texto(texto)
            capa(x0, x - x0, t, 0.05, 1)
            t += 0.12
        else:
            t += 0.1
        y += altura_linha
    corpo.filhos.extend(capas)
    return documento(L, a, f"Prompt de comando: {perfil['nome']}, {perfil['cargo']} da {perfil['empresa']}, e as marcas da empresa",
                     "".join(css), raiz)


# --------------------------------------------------------------------------- gerenciador de tarefas

FONTE_3X5 = {
    "A": ["###", "#.#", "###", "#.#", "#.#"], "B": ["##.", "#.#", "##.", "#.#", "##."],
    "C": ["###", "#..", "#..", "#..", "###"], "E": ["###", "#..", "##.", "#..", "###"],
    "G": ["###", "#..", "#.#", "#.#", "###"], "H": ["#.#", "#.#", "###", "#.#", "#.#"],
    "J": ["..#", "..#", "..#", "#.#", "###"], "L": ["#..", "#..", "#..", "#..", "###"],
    "M": ["#.#", "###", "###", "#.#", "#.#"], "P": ["###", "#.#", "###", "#..", "#.."],
    "R": ["##.", "#.#", "##.", "#.#", "#.#"], "S": ["###", "#..", "###", "..#", "###"],
    "T": ["###", ".#.", ".#.", ".#.", ".#."], "V": ["#.#", "#.#", "#.#", "#.#", ".#."],
    "W": ["#.#", "#.#", "###", "###", "#.#"], "Y": ["#.#", "#.#", ".#.", ".#.", ".#."],
    "D": ["##.", "#.#", "#.#", "#.#", "##."], "I": ["###", ".#.", ".#.", ".#.", "###"],
    "Z": ["###", "..#", ".#.", "#..", "###"], "X": ["#.#", "#.#", ".#.", "#.#", "#.#"],
    "4": ["#.#", "#.#", "###", "..#", "..#"], "N": ["##.", "#.#", "#.#", "#.#", "#.#"],
    "O": ["###", "#.#", "#.#", "#.#", "###"], "U": ["#.#", "#.#", "#.#", "#.#", "###"],
    "K": ["#.#", "#.#", "##.", "#.#", "#.#"], "F": ["###", "#..", "##.", "#..", "#.."],
}


def _icone_linguagem(c, x, y, sigla, cor):
    """Ícone 12x12: quadrado arredondado na cor da linguagem, com a sigla."""
    c.ret(x, y, 12, 12, cor)
    for px, py in ((x, y), (x + 11, y), (x, y + 11), (x + 11, y + 11)):
        c.apagar(px, py)
    r, g, b = (int(cor[i:i + 2], 16) for i in (1, 3, 5))
    letra = PRETO if 0.299 * r + 0.587 * g + 0.114 * b > 150 else BRANCO
    for i, ch in enumerate(sigla):
        c.sprite(x + 2 + i * 5, y + 4, FONTE_3X5[ch], {"#": letra})


def tarefas(dados, perfil):
    codigo = {k: v for k, v in dados["linguagens"].items() if k in perfil["linguagens_codigo"] and k not in ("HTML", "CSS")}
    total = sum(codigo.values()) or 1
    linhas = [(nome, perfil["linguagens_codigo"][nome], bytes_ / total) for nome, bytes_ in codigo.items()]
    linhas.sort(key=lambda l: -l[2])
    carreira = perfil["stack_carreira"]

    altura_linha = 14
    y_lista = 64
    y_grafico = y_lista + 14 + (len(linhas) + len(carreira)) * altura_linha + 18
    a = y_grafico + 84 + 34
    raiz = Camada()
    c = raiz.adicionar(Camada())
    janela(c, a, "Gerenciador de tarefas do LeninOS",
           (["#######", "#.....#", "#.#...#", "#.##.##", "#.#####", "#######"], {"#": "#3cff5a", ".": PRETO}))
    c.texto(8, 21, "Arquivo Opções Exibir Ajuda", PRETO)
    _abas(c, 33, ["Aplicativos", "Processos", "Desempenho"], 1)
    _painel(c, 6, 48, L - 12, y_grafico - 66, BRANCO)
    c.ret(7, 49, L - 14, 13, BEGE)
    c.ret(7, 62, L - 14, 1, CINZA_BORDA)
    for x, rotulo in ((10, "Nome da imagem"), (160, "Usuário"), (250, "CPU")):
        c.texto(x, 52, rotulo, PRETO)
        c.ret(x - 3, 50, 1, 11, CINZA_BORDA)

    css = ["@keyframes encher{from{transform:scaleX(0)}to{transform:none}}",
           "@keyframes varrer{from{transform:translateX(-396px)}to{transform:none}}",
           ".varre{animation:varrer 2.4s steps(66) .6s both}"]
    y = y_lista + 2
    for i, (nome, info, parte) in enumerate(linhas):
        if i == 0:
            c.ret(7, y - 2, L - 14, altura_linha, "#316ac5")
        cor_texto = BRANCO if i == 0 else PRETO
        _icone_linguagem(c, 10, y, info["sigla"], info["cor"])
        c.texto(26, y + 2, f"{nome.lower()}.exe", cor_texto)
        c.texto(160, y + 2, "lecodaro", cor_texto)
        barra = raiz.adicionar(Camada(estilo=f"transform-origin:250px 0;animation:encher .8s steps(10) {0.3 + i * 0.15:.2f}s both"))
        c.ret(250, y + 2, 104, 8, PRETO)
        segmentos = max(1, round(parte * 26))
        for s in range(segmentos):
            barra.ret(251 + s * 4, y + 3, 3, 6, "#22e04a")
        pct = f"{parte * 100:.0f}%"
        c.texto(L - 14 - largura_texto(pct), y + 2, pct, cor_texto)
        y += altura_linha
    for item in carreira:
        _icone_linguagem(c, 10, y, item["sigla"], item["cor"])
        nome = item["nome"].lower().replace(" ", "")
        c.texto(26, y + 2, f"{nome}.exe", PRETO)
        c.texto(160, y + 2, "carreira", "#6a6a6a")
        c.texto(250, y + 2, f"{perfil['anos_programando']} anos", "#6a6a6a")
        y += altura_linha

    # desempenho: contribuições por semana, desenhadas como o gráfico verde de CPU
    c.texto(8, y_grafico - 12, "Histórico de uso: contribuições por semana", PRETO)
    gx, gy, gl, ga = 8, y_grafico, L - 16, 80
    c.ret(gx, gy, gl, ga, PRETO)
    grade = Camada()
    for xx in range(gx, gx + gl, 12):
        grade.ret(xx, gy, 1, ga, "#004d26")
    for yy in range(gy, gy + ga, 12):
        grade.ret(gx, yy, gl, 1, "#004d26")
    totais = [sum(d["total"] for d in s) for s in dados["semanas"]]
    maximo = max(totais) or 1
    passo = (gl - 4) / max(len(totais) - 1, 1)
    linha = Camada()
    pontos = [(round(gx + 2 + i * passo), round(gy + ga - 3 - v / maximo * (ga - 8))) for i, v in enumerate(totais)]
    for (x1, y1), (x2, y2) in zip(pontos, pontos[1:]):
        for xx in range(x1, x2 + 1):
            yy = round(y1 + (y2 - y1) * (xx - x1) / max(x2 - x1, 1))
            linha.ret(xx, yy + 1, 1, gy + ga - 2 - yy, "#0b5d1e")
    for (x1, y1), (x2, y2) in zip(pontos, pontos[1:]):
        linha.linha(x1, y1, x2, y2, "#3cff5a")
    grafico = raiz.adicionar(Camada(estilo="clip-path:url(#grafico)"))
    grafico.adicionar(grade)
    grafico.adicionar(linha)
    grafico.adicionar(f'<rect class="varre" x="{gx + gl}" y="{gy}" width="{gl}" height="{ga}" fill="#000"/>')
    raiz.filhos.insert(0, f'<defs><clipPath id="grafico"><rect x="{gx}" y="{gy}" width="{gl}" height="{ga}"/></clipPath></defs>')
    inicio = date.fromisoformat(dados["semanas"][0][0]["data"])
    rot_inicio = f"{inicio.month:02d}/{inicio.year}"
    c.texto(gx, gy + ga + 3, rot_inicio, "#555555")
    c.texto(gx + gl - largura_texto("hoje"), gy + ga + 3, "hoje", "#555555")

    sy = a - 17
    c.ret(3, sy - 1, L - 6, 1, CINZA_BORDA)
    status = [f"Processos: {len(linhas) + len(carreira)}", "CPU: 100%", f"{milhar(dados['contribuicoes_ano'])} no ano"]
    x = 8
    for s in status:
        c.texto(x, sy + 3, s, PRETO)
        x += largura_texto(s) + 10
        c.ret(x - 6, sy, 1, 13, CINZA_BORDA)
    return documento(L, a, "Gerenciador de tarefas: linguagens que o Lenin mais programa e o histórico de contribuições",
                     "".join(css), raiz)


# --------------------------------------------------------------------------- atalhos das marcas

SETA_ATALHO = ["########", "#wwwwww#", "#wbbbbw#", "#wwwbbw#", "#wwbwbw#", "#wbwwbw#", "#wwwwww#", "########"]


def _desenho_marca(c, id_, x, y):
    if id_ == "holding":
        c.elipse(x + 25, y + 6, 5, 5, "#ffc23a")
        c.ret(x + 6, y + 6, 16, 26, "#3d4f73")
        c.ret(x + 7, y + 7, 14, 25, "#5a6f99")
        c.ret(x + 20, y + 14, 10, 18, "#4a5d85")
        for wy in range(y + 9, y + 30, 4):
            for wx in (x + 9, x + 13, x + 17):
                c.ret(wx, wy, 2, 2, "#ffe066" if ruido(wx, wy) < 0.6 else "#2a3550")
            c.ret(x + 23, wy + 2, 2, 2, "#ffe066" if ruido(wy, 1) < 0.5 else "#2a3550")
        c.ret(x + 12, y + 3, 4, 3, "#3d4f73")
    elif id_ == "cloud":
        for cx, cy, rx, ry in ((10, 16, 7, 6), (17, 11, 8, 8), (24, 16, 7, 6), (17, 18, 12, 5)):
            c.elipse(x + cx, y + cy, rx, ry, "#2b6bd6")
        for cx, cy, rx, ry in ((10, 16, 6, 5), (17, 11, 7, 7), (24, 16, 6, 5), (17, 18, 11, 4)):
            c.elipse(x + cx, y + cy, rx, ry, BRANCO)
        c.sprite(x + 13, y + 9, ["..#..", ".###.", "#####", ".###.", ".###.", ".###."], {"#": "#ff8a00"})
    elif id_ == "studio":
        c.ret(x + 3, y + 4, 26, 20, "#d8d2bc")
        c.ret(x + 5, y + 6, 22, 15, "#102018")
        c.texto(x + 6, y + 9, "<", "#3cff5a")
        c.texto(x + 15, y + 9, ">", "#3cff5a")
        c.linha(x + 15, y + 9, x + 12, y + 17, "#3cff5a")
        c.ret(x + 12, y + 24, 8, 3, "#b7b09a")
        c.ret(x + 7, y + 27, 18, 3, "#9a937e")
    elif id_ == "club":
        c.ret(x + 10, y + 2, 4, 12, "#d63b3b")
        c.ret(x + 18, y + 2, 4, 12, "#2b6bd6")
        c.elipse(x + 16, y + 20, 10, 10, "#c98a10")
        c.elipse(x + 16, y + 20, 8, 8, "#ffcf3a")
        c.sprite(x + 11, y + 15, ["..#..", "..#..", "#####", ".###.", ".#.#.", "#...#"], {"#": "#fff4b8"})
    elif id_ == "info":
        c.ret(x + 4, y + 4, 24, 26, "#9a9a9a")
        c.ret(x + 5, y + 5, 22, 24, "#fafafa")
        c.ret(x + 7, y + 7, 18, 4, "#222222")
        c.ret(x + 7, y + 13, 8, 7, "#d63b3b")
        for ly in range(y + 13, y + 27, 3):
            c.ret(x + 17, ly, 8, 1, "#777777")
        for ly in range(y + 22, y + 27, 3):
            c.ret(x + 7, ly, 8, 1, "#777777")


def atalho(marca):
    l, a = 72, 58
    c = Camada()
    c.ret(0, 0, l, a, "#3a6ea5")
    for px, py in ((0, 0), (l - 1, 0), (0, a - 1), (l - 1, a - 1)):
        c.apagar(px, py)
    _desenho_marca(c, marca["id"], 20, 2)
    c.sprite(20, 26, SETA_ATALHO, {"#": "#5a5a5a", "w": BRANCO, "b": "#2b6bd6"})
    for i, rotulo in enumerate(marca["rotulo"]):
        _texto_sombra(c, (l - largura_texto(rotulo)) // 2, 37 + i * 10, rotulo, BRANCO, PRETO)
    return documento(l, a, f"Atalho para {marca['nome']} ({marca['dominio']})", "", c)


def botao(rotulo, icone):
    l = largura_texto(rotulo) + 34
    a = 20
    c = Camada()
    _botao_xp(c, 0, 0, l, a, "")
    c.sprite(6, 4, *icone)
    c.texto(24, 6, rotulo, PRETO)
    return documento(l, a, rotulo, "", c)


ICONE_LINKEDIN = (["############", "#ww#########", "#ww#########", "############", "#ww#ww#www##",
                   "#ww#wwwwwww#", "#ww#www##ww#", "#ww#ww###ww#", "#ww#ww###ww#", "#ww#ww###ww#", "############"],
                  {"#": "#0a66c2", "w": BRANCO})
ICONE_SITE = (SOL_MINI + ["......."], PALETA_SOL)


def fim():
    a = 44
    c = Camada()
    c.ret(0, 0, L, a, PRETO)
    frase = "Agora é seguro fechar esta aba."
    c.texto((L - largura_texto(frase)) // 2, 12, frase, "#ff9a1f")
    c.texto((L - largura_texto("LeninOS")) // 2, 26, "LeninOS", "#5a5a5a")
    return documento(L, a, frase, "", c)


# --------------------------------------------------------------------------- meu computador

DISCO = ["..............", ".############.", "#bbbbbbbbbbbb#", "#############", "#wwwwwwwwwwgg#", "#wwwwwwwwwwww#", ".############."]


def _caixa_lateral(c, x, y, l, titulo, itens):
    faixas(c, x, y, l, 14, gradiente("#ffffff", "#c6d3f7", 14))
    c.texto(x + 6, y + 3, titulo, "#215dc6")
    c.ret(x, y + 14, l, 6 + len(itens) * 10, "#d6dff7")
    for i, item in enumerate(itens):
        c.texto(x + 6, y + 18 + i * 10, item, "#0b2a6b")
    return y + 14 + 6 + len(itens) * 10


def computador(dados, perfil):
    ferramentas = perfil["ferramentas"]
    linhas_ferramentas = (len(ferramentas) + 1) // 2
    y_ferr = 50 + 14 + len(perfil["operacoes"]) * 34 + 10
    a = y_ferr + 16 + linhas_ferramentas * 14 + 26
    raiz = Camada()
    c = raiz.adicionar(Camada())
    janela(c, a, "Meu computador", (["#######", "#bbbbb#", "#bbbbb#", "#######", "..###..", ".#####."],
                                    {"#": "#d8d2bc", "b": "#3a86e8"}))
    c.texto(8, 22, "Endereço", "#555555")
    c.ret(82, 20, L - 90, 12, BRANCO)
    c.ret(82, 20, L - 90, 1, "#7f9db9")
    c.texto(86, 22, "C:\\LENIN\\carreira", PRETO)

    # painel lateral azul
    faixas(c, 3, 36, 124, a - 57, gradiente("#7ba2e7", "#6375d6", 12))
    y = _caixa_lateral(c, 10, 42, 110, "Especialidade", ["Marketing", "Growth", "MarTech", "CRO e dados"])
    _caixa_lateral(c, 10, y + 8, 110, "Detalhes", [perfil["empresa"][:13], "Fundador", f"{perfil['anos_programando']} anos", "programando"])

    x0 = 134
    c.ret(x0 - 2, 36, L - x0 - 1, a - 57, BRANCO)
    c.texto(x0 + 2, 42, "Operações em que atuei", "#215dc6")
    c.ret(x0 + 2, 52, L - x0 - 12, 1, "#7ba2e7")
    css = ["@keyframes encher{from{transform:scaleX(0)}to{transform:none}}"]
    maior = max(o["valor"] for o in perfil["operacoes"])
    y = 58
    for i, op in enumerate(perfil["operacoes"]):
        c.sprite(x0 + 2, y + 2, DISCO, {"#": "#8a8a8a", "b": "#5a5a5a", "w": "#d8d8d8", "g": "#3cdc3c"})
        c.texto(x0 + 20, y, op["nome"], PRETO)
        largura_barra = L - x0 - 34
        c.ret(x0 + 20, y + 11, largura_barra, 8, "#7f9db9")
        c.ret(x0 + 21, y + 12, largura_barra - 2, 6, BRANCO)
        barra = raiz.adicionar(Camada(estilo=f"transform-origin:{x0 + 21}px 0;animation:encher 1s steps(12) {0.4 + i * 0.4:.1f}s both"))
        faixas(barra, x0 + 21, y + 12, round((largura_barra - 2) * op["valor"] / maior), 6, ["#4f8ff7", "#2a6fd6", "#1f5bbf"])
        c.texto(x0 + 20, y + 22, op["rotulo"], "#555555")
        y += 34

    c.texto(x0 + 2, y_ferr, "Painel de controle", "#215dc6")
    c.ret(x0 + 2, y_ferr + 10, L - x0 - 12, 1, "#7ba2e7")
    for i, f in enumerate(ferramentas):
        fx = x0 + 2 + (i % 2) * 138
        fy = y_ferr + 16 + (i // 2) * 14
        _icone_linguagem(c, fx, fy, f["sigla"], f["cor"])
        c.texto(fx + 16, fy + 2, f["nome"], PRETO)

    sy = a - 17
    c.ret(3, sy - 1, L - 6, 1, CINZA_BORDA)
    c.texto(8, sy + 3, f"{len(perfil['operacoes'])} unidades · {len(ferramentas)} ferramentas", PRETO)
    return documento(L, a, "Meu computador: operações em que o Lenin atuou e ferramentas de Marketing, Growth e dados que domina",
                     "".join(css), raiz)
