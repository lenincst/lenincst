"""Rodapé discreto: dois links pequenos (sublinhado que se desenha + cursor) e o fecho em terminal.

O fecho é o hello world de Kernighan & Ritchie, "The C Programming Language" (1978).
"""
from svgkit import Doc, fmt

TAM = 15
CW = 0.6 * TAM

CSS_LINK = ("@keyframes risca{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
            ".risco{stroke-dasharray:1;animation:risca .9s cubic-bezier(.6,0,.3,1) .5s both}"
            "@keyframes pisca{0%,49.9%{opacity:1}50%,100%{opacity:0}}"
            ".cur{animation:pisca 1.06s linear 1.4s infinite}")


def _link(tema: str, antes: str, alvo: str, titulo: str, descricao: str) -> str:
    texto = f"{antes}{alvo} ↗"
    w = len(texto) * CW + 18
    doc = Doc(w, 34, titulo, descricao, tema)
    c = doc.c
    x = 2
    doc.css.append(CSS_LINK)
    partes = []
    if antes:
        partes.append(doc.t(antes, x, 21, TAM, "suave"))
    xa = x + len(antes) * CW
    partes.append(doc.t(alvo, xa, 21, TAM, "tinta"))
    partes.append(doc.t("↗", xa + (len(alvo) + 1) * CW, 21, TAM, "suave"))
    partes.append(f'<path class="risco" pathLength="1" d="M{fmt(xa)} 27.5H{fmt(xa + len(alvo) * CW)}" '
                  f'stroke="{c["ambar"]}" stroke-width="1.2" stroke-linecap="round"/>')
    partes.append(f'<rect class="cur" x="{fmt(x + len(texto) * CW + 5)}" y="9" width="1.6" height="16" fill="{c["ambar"]}"/>')
    doc.corpo.append("".join(partes))
    return doc.render()


def lecodaro(tema: str) -> str:
    return _link(tema, "fundador da ", "lecodaro.com", "fundador da lecodaro.com",
                 "Link discreto: fundador da lecodaro.com, com sublinhado animado.")


def linkedin(tema: str) -> str:
    return _link(tema, "", "in/lenincst", "LinkedIn: in/lenincst",
                 "Link discreto para o LinkedIn in/lenincst, com sublinhado animado.")


def hello(tema: str) -> str:
    comando = 'printf("hello, world\\n");'
    doc = Doc(400, 92, "hello, world",
              'Terminal digitando printf("hello, world\\n"); com a nota // K&R, 1978, a saída hello, world '
              "e, por fim, exit 0.", tema)
    c, css = doc.c, doc.css
    partes = [doc.t("$", 4, 24, TAM, "ambar"), doc.t("$", 4, 80, TAM, "ambar", cls="l3")]

    def digita(s: str, x0: float, y: float, t: float, cor: str) -> float:
        for i, ch in enumerate(s):
            if ch != " ":
                partes.append(doc.t(ch, x0 + i * CW, y, TAM, cor, cls="k", estilo=f"animation-delay:{t:.3f}s"))
            t += 0.045 + 0.03 * ((i * 7919) % 11) / 10
        return t

    t = digita(comando, 4 + 2 * CW, 24, 0.6, "tinta")
    t_com = t + 0.2
    partes.append(doc.t("// K&R, 1978", 4 + (2 + len(comando) + 2) * CW, 24, TAM, "fraco", cls="fade",
                        estilo=f"animation-delay:{t_com:.2f}s"))
    t_saida = t_com + 0.45
    partes.append(doc.t("hello, world", 4, 52, TAM, "tinta", cls="fade", estilo=f"animation-delay:{t_saida:.2f}s"))
    t_l3 = t_saida + 0.5
    t_fim = digita("exit 0", 4 + 2 * CW, 80, t_l3 + 0.35, "suave")
    partes.append(f'<g class="fade" style="animation-delay:{t_l3:.2f}s"><rect class="bloco" '
                  f'x="{fmt(4 + 2 * CW)}" y="67" width="{fmt(CW - 1)}" height="17" fill="{c["ambar"]}" fill-opacity=".8"/></g>')
    css.append("@keyframes k{from{opacity:0}to{opacity:1}}.k{animation:k .06s linear both}"
               "@keyframes fade{from{opacity:0}}.fade,.l3{animation:fade .35s ease-out both}"
               f".l3{{animation-delay:{t_l3:.2f}s}}"
               "@keyframes pisca{0%,49.9%{opacity:1}50%,100%{opacity:0}}")
    # o cursor anda com a digitação de "exit 0" e depois pisca
    passos = len("exit 0")
    css.append(f"@keyframes anda{{0%{{transform:translateX(0)}}100%{{transform:translateX({fmt(passos * CW)}px)}}}}"
               f".bloco{{transform:translateX({fmt(passos * CW)}px);"
               f"animation:anda {t_fim - t_l3 - 0.35:.2f}s steps({passos},end) {t_l3 + 0.35:.2f}s both,"
               f"pisca 1.06s linear {t_fim + 0.2:.2f}s infinite}}")
    doc.corpo.append("".join(partes))
    return doc.render()
