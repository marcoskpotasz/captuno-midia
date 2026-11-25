#!/usr/bin/env python3
"""Gera a arte (JPEG 1080x1350) de um post da Leva e Traz a partir de um JSON.

Uso: python3 render.py post.json saida.jpg

Campos do JSON:
  pilar        corporativo | turismo | gestao_escolar
  chip         texto curto do selo (ex.: "Fretamento corporativo")
  title        título; use <em>...</em> para destacar palavras na cor de destaque
  subtitle     1-2 frases
  bullets      lista com 2 a 4 itens curtos
  cta          chamada final (curta)
  (o campo "illustration" é ignorado: o visual usa o logo e um grafismo de rota)
"""
import html, json, pathlib, re, sys, shutil, io

KIT = pathlib.Path(__file__).resolve().parent

# Paleta oficial (extraída do logo): azul #2A5B87, laranja #F1A205, marinho #12324F.
# O pilar muda só o traçado do grafismo de rota no bloco inferior.
ROUTES = {
    "corporativo":    "M22 90 L250 90 L250 50 L520 50 L520 20 L900 20",
    "turismo":        "M22 90 C 200 90, 260 20, 460 40 S 720 90, 900 20",
    "gestao_escolar": "M22 90 L180 90 L180 55 L400 55 L400 85 L640 85 L640 20 L900 20",
}

def graphic(pilar):
    grid = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="110" stroke="#ffffff" stroke-opacity=".07"/>' for x in range(0, 921, 46))
    grid += "".join(f'<line x1="0" y1="{y}" x2="920" y2="{y}" stroke="#ffffff" stroke-opacity=".07"/>' for y in range(5, 110, 35))
    d = ROUTES.get(pilar, ROUTES["corporativo"])
    pts = re.findall(r"(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)", d)
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    return (grid
        + f'<path d="{d}" fill="none" stroke="#2A5B87" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>'
        + f'<path d="{d}" fill="none" stroke="#ffffff" stroke-opacity=".55" stroke-width="2" stroke-dasharray="10 12"/>'
        + f'<circle cx="{x0}" cy="{y0}" r="12" fill="#12324F" stroke="#ffffff" stroke-width="4"/>'
        + f'<circle cx="{x1}" cy="{y1}" r="16" fill="#F1A205"/><circle cx="{x1}" cy="{y1}" r="6" fill="#12324F"/>')

def safe(text):
    # escapa tudo e reabilita apenas <em> e <br>
    t = html.escape(text)
    for tag in ("em", "br"):
        t = t.replace(f"&lt;{tag}&gt;", f"<{tag}>").replace(f"&lt;/{tag}&gt;", f"</{tag}>").replace(f"&lt;{tag}/&gt;", f"<{tag}/>")
    return t

def build_html(post):
    plain_title = post["title"].replace("<em>", "").replace("</em>", "")
    n = len(plain_title)
    title_size = "78px" if n <= 34 else "70px" if n <= 48 else "62px" if n <= 64 else "54px"
    items = post.get("bullets", [])[:4]
    bullets = "".join(f'<div class="item"><span class="n">{i+1:02d}</span><span class="t">{safe(b)}</span></div>' for i, b in enumerate(items))
    tpl = (KIT / "template.html").read_text(encoding="utf-8")
    rep = {
        "title_size": title_size, "graphic": graphic(post["pilar"]),
        "chip": safe(post["chip"]), "title": safe(post["title"]), "subtitle": safe(post["subtitle"]),
        "bullets": bullets, "cta": safe(post["cta"]),
    }
    for k, v in rep.items():
        tpl = tpl.replace("{{" + k + "}}", v)
    return tpl

def find_browser():
    for p in ("google-chrome", "chromium", "chromium-browser"):
        if shutil.which(p):
            return shutil.which(p)
    return None  # usa o Chromium do Playwright

def main(src, out):
    post = json.loads(pathlib.Path(src).read_text(encoding="utf-8"))
    page_html = build_html(post)
    tmp = KIT / "_render.html"
    tmp.write_text(page_html, encoding="utf-8")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        exe = find_browser()
        browser = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350})
        page.goto(tmp.as_uri())
        page.wait_for_timeout(400)
        png = page.screenshot(type="png")
        browser.close()
    tmp.unlink()
    from PIL import Image
    Image.open(io.BytesIO(png)).convert("RGB").save(out, "JPEG", quality=92, optimize=True)
    print("ok", out)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
