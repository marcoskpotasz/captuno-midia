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
  illustration van | onibus | aeroporto | escolar  (opcional; padrão por pilar)
"""
import html, json, pathlib, sys, shutil, io

KIT = pathlib.Path(__file__).resolve().parent

THEMES = {
    "corporativo":    {"bg": "#0E2A47", "accent": "#F5B21B", "glow": "rgba(245,178,27,.14)", "ill": "onibus"},
    "turismo":        {"bg": "#0B4A5A", "accent": "#FFC64D", "glow": "rgba(255,198,77,.16)", "ill": "van"},
    "gestao_escolar": {"bg": "#173A2E", "accent": "#8BE28B", "glow": "rgba(139,226,139,.14)", "ill": "escolar"},
}

def wheel(cx, cy, r=34):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#0b1726"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r*0.45:.0f}" fill="#cfd6df"/>')

def vehicle(kind, accent):
    if kind == "onibus":
        body = (
            '<rect x="20" y="40" width="520" height="190" rx="28" fill="#ffffff"/>'
            f'<rect x="20" y="168" width="520" height="22" fill="{accent}"/>'
            + "".join(f'<rect x="{60+i*92}" y="66" width="76" height="72" rx="10" fill="#9fd3ef"/>' for i in range(4))
            + '<rect x="440" y="66" width="76" height="72" rx="10" fill="#9fd3ef"/><rect x="500" y="150" width="0" height="0"/>'
            '<rect x="24" y="200" width="20" height="14" rx="4" fill="#ffd27a"/>'
            + wheel(120, 236) + wheel(440, 236)
        )
        return f'<svg viewBox="0 0 560 280" xmlns="http://www.w3.org/2000/svg">{body}</svg>'
    if kind in ("van", "aeroporto", "escolar"):
        stripe = accent
        extra = ""
        if kind == "aeroporto":
            extra = ('<g transform="translate(330,-10) rotate(-12)">'
                     '<path d="M0 40 L150 30 L190 38 L150 48 L0 46 Z" fill="#ffffff" opacity=".9"/>'
                     '<path d="M80 36 L50 0 L72 0 L120 34 Z" fill="#ffffff" opacity=".9"/>'
                     '<path d="M84 46 L58 80 L80 80 L122 46 Z" fill="#ffffff" opacity=".9"/></g>')
        if kind == "escolar":
            extra = ('<g transform="translate(410,0)">'
                     '<rect x="0" y="0" width="120" height="90" rx="14" fill="#ffffff"/>'
                     f'<rect x="14" y="16" width="60" height="10" rx="5" fill="{accent}"/>'
                     '<rect x="14" y="36" width="92" height="8" rx="4" fill="#c8d3dd"/>'
                     '<rect x="14" y="52" width="72" height="8" rx="4" fill="#c8d3dd"/>'
                     f'<circle cx="98" cy="70" r="12" fill="{accent}"/></g>')
        body = (
            extra +
            '<path d="M30 230 L30 120 Q30 92 58 90 L360 84 Q392 84 414 106 L486 170 Q520 176 526 200 L526 230 Z" fill="#ffffff"/>'
            '<path d="M372 104 L440 166 L372 166 Z" fill="#9fd3ef"/>'
            + "".join(f'<rect x="{62+i*82}" y="110" width="66" height="54" rx="9" fill="#9fd3ef"/>' for i in range(4))
            + f'<rect x="30" y="182" width="496" height="18" fill="{stripe}"/>'
            '<rect x="506" y="206" width="20" height="12" rx="4" fill="#ffd27a"/>'
            + wheel(130, 232) + wheel(420, 232)
        )
        return f'<svg viewBox="0 0 560 280" xmlns="http://www.w3.org/2000/svg">{body}</svg>'
    raise ValueError(f"ilustração desconhecida: {kind}")

CHECK = '<svg width="22" height="22" viewBox="0 0 24 24"><path d="M5 12.5l4.2 4.2L19 7" stroke="#10233b" stroke-width="3.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def safe(text):
    # escapa tudo e reabilita apenas <em> e <br>
    t = html.escape(text)
    for tag in ("em", "br"):
        t = t.replace(f"&lt;{tag}&gt;", f"<{tag}>").replace(f"&lt;/{tag}&gt;", f"</{tag}>").replace(f"&lt;{tag}/&gt;", f"<{tag}/>")
    return t

def build_html(post):
    th = THEMES[post["pilar"]]
    plain_title = post["title"].replace("<em>", "").replace("</em>", "")
    n = len(plain_title)
    title_size = "84px" if n <= 34 else "74px" if n <= 48 else "64px" if n <= 64 else "56px"
    bullets = "".join(f'<li><span class="ck">{CHECK}</span><span>{safe(b)}</span></li>' for b in post.get("bullets", [])[:4])
    tpl = (KIT / "template.html").read_text(encoding="utf-8")
    rep = {
        "bg": th["bg"], "accent": th["accent"], "glow": th["glow"], "title_size": title_size,
        "illustration": vehicle(post.get("illustration") or th["ill"], th["accent"]),
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
