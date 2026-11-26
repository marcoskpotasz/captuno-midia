#!/usr/bin/env python3
"""Gera as artes (JPEG 1080x1350) de um post da Leva e Traz a partir de um JSON.

Uso: python3 render.py post.json saida.jpg
  - posts de 1 imagem geram saida.jpg
  - carrosséis geram saida-1.jpg, saida-2.jpg, ... (a lista de arquivos é impressa)

Campos comuns do JSON:
  tipo     servico | conteudo
  pilar    corporativo | turismo | gestao_escolar | institucional
  layout   classico | foto | foto_split | dica | carrossel
  chip     selo curto (ex.: "Fretamento corporativo", "Dica de viagem")
  title    título; use <em>...</em> para destacar 1-3 palavras
  subtitle 1 frase
  bullets  2 a 4 itens curtos (classico, foto_split, dica)
  cta      chamada final curta
  foto     caminho relativo a levaetraz/ (ex.: "fotos/micro-onibus-externo-logo.jpg"), para foto, foto_split e capa do carrossel
  caption, alt_text  legenda e texto alternativo do post

Carrossel (layout "carrossel"):
  slides   lista de 3 a 6 itens {"title": "...", "text": "..."}; a capa usa title/subtitle/foto
           do post (ou layout de dica, se não houver foto) e o último slide é o CTA.
"""
import html, io, json, pathlib, re, shutil, sys

KIT = pathlib.Path(__file__).resolve().parent
ROOT = KIT.parent  # levaetraz/

NAVY, BLUE, ORANGE, MUTED, PAPER = "#12324F", "#2A5B87", "#F1A205", "#5B6B7B", "#F4F6F9"

ROUTES = {
    "corporativo":    "M22 90 L250 90 L250 50 L520 50 L520 20 L900 20",
    "turismo":        "M22 90 C 200 90, 260 20, 460 40 S 720 90, 900 20",
    "gestao_escolar": "M22 90 L180 90 L180 55 L400 55 L400 85 L640 85 L640 20 L900 20",
    "institucional":  "M22 60 C 220 20, 380 100, 560 60 S 820 20, 900 40",
}

BASE_CSS = f"""
@font-face {{ font-family: "DM Sans"; src: url("{(KIT / 'fonts/DMSans.ttf').as_uri()}"); font-weight: 100 1000; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1080px; height: 1350px; }}
body {{ font-family: "DM Sans", sans-serif; color: {NAVY}; background: {PAPER}; position: relative; overflow: hidden; }}
.logo {{ height: 92px; }}
.label {{ display: flex; align-items: center; gap: 16px; font-weight: 700; font-size: 22px; letter-spacing: 4px; text-transform: uppercase; color: {BLUE}; }}
.label::before {{ content: ""; width: 48px; height: 4px; background: {ORANGE}; }}
h1 {{ font-weight: 800; line-height: 1.06; letter-spacing: -1.6px; }}
h1 em {{ font-style: normal; color: {BLUE}; }}
.dark h1 em {{ color: {ORANGE}; }}
.dark .label {{ color: #fff; }}
.since {{ font-size: 20px; font-weight: 600; letter-spacing: 4px; text-transform: uppercase; color: {MUTED}; }}
.dark .since {{ color: rgba(255,255,255,.75); }}
.footer {{ position: absolute; left: 80px; right: 80px; bottom: 64px; display: flex; align-items: flex-end; justify-content: space-between; gap: 40px; border-top: 2px solid {ORANGE}; padding-top: 26px; color: #fff; }}
.cta {{ font-size: 33px; font-weight: 800; line-height: 1.15; max-width: 540px; }}
.contact {{ text-align: right; font-size: 22px; line-height: 1.5; font-weight: 500; white-space: nowrap; opacity: .85; }}
.contact b {{ font-weight: 700; font-size: 25px; }}
.items {{ display: grid; }}
.item {{ display: grid; grid-template-columns: 62px 1fr; align-items: baseline; border-top: 1px solid #D5DCE4; padding: 20px 0; }}
.item:last-child {{ border-bottom: 1px solid #D5DCE4; }}
.item .n {{ font-size: 22px; font-weight: 700; color: {ORANGE}; letter-spacing: 1px; }}
.item .t {{ font-size: 29px; font-weight: 600; line-height: 1.25; }}
"""

def safe(text):
    t = html.escape(text or "")
    for tag in ("em", "br"):
        t = (t.replace(f"&lt;{tag}&gt;", f"<{tag}>").replace(f"&lt;/{tag}&gt;", f"</{tag}>")
              .replace(f"&lt;{tag}/&gt;", f"<{tag}/>"))
    return t

def title_size(title, sizes=(78, 70, 62, 54)):
    n = len(re.sub(r"</?em>", "", title))
    return sizes[0] if n <= 34 else sizes[1] if n <= 48 else sizes[2] if n <= 64 else sizes[3]

def route_svg(pilar, w=920, h=110):
    grid = "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="110" stroke="#fff" stroke-opacity=".07"/>' for x in range(0, 921, 46))
    grid += "".join(f'<line x1="0" y1="{y}" x2="920" y2="{y}" stroke="#fff" stroke-opacity=".07"/>' for y in range(5, 110, 35))
    d = ROUTES.get(pilar, ROUTES["corporativo"])
    pts = re.findall(r"(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)", d)
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    return (f'<svg viewBox="0 0 920 110" width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">{grid}'
            f'<path d="{d}" fill="none" stroke="{BLUE}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="2" stroke-dasharray="10 12"/>'
            f'<circle cx="{x0}" cy="{y0}" r="12" fill="{NAVY}" stroke="#fff" stroke-width="4"/>'
            f'<circle cx="{x1}" cy="{y1}" r="16" fill="{ORANGE}"/><circle cx="{x1}" cy="{y1}" r="6" fill="{NAVY}"/></svg>')

def items_html(bullets):
    return "".join(f'<div class="item"><span class="n">{i+1:02d}</span><span class="t">{safe(b)}</span></div>'
                   for i, b in enumerate((bullets or [])[:4]))

def footer(cta):
    return (f'<div class="footer"><div class="cta">{safe(cta)}</div>'
            f'<div class="contact"><b>levaetraztransporte.com.br</b><br>@levaetraz.transporte</div></div>')

def logo(white=False):
    return f'<img class="logo" src="{(KIT / ("logo-branco.png" if white else "logo.png")).as_uri()}">'

def photo_info(rel):
    p = (ROOT / rel).resolve()
    if not p.exists():
        raise SystemExit(f"foto não encontrada: {rel}")
    pos = "center center"
    cat = ROOT / "fotos" / "fotos.json"
    if cat.exists():
        for f in json.loads(cat.read_text(encoding="utf-8")):
            if f["arquivo"] == p.name:
                pos = f.get("posicao", pos)
    return p.as_uri(), pos

def page(body, extra_css="", cls=""):
    return (f'<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><style>{BASE_CSS}{extra_css}</style></head>'
            f'<body class="{cls}">{body}</body></html>')

TOP_CSS = ".top { position: absolute; left: 80px; right: 80px; top: 64px; display: flex; align-items: center; justify-content: space-between; }"

# ---------- layouts ----------

def classico(p):
    css = TOP_CSS + f"""
    .content {{ position: absolute; left: 80px; right: 80px; top: 236px; }}
    h1 {{ font-size: {title_size(p['title'])}px; margin-top: 30px; max-width: 920px; }}
    .sub {{ font-size: 31px; line-height: 1.38; margin-top: 28px; color: {MUTED}; max-width: 880px; }}
    .items {{ margin-top: 44px; width: 860px; }}
    .panel {{ position: absolute; left: 0; right: 0; bottom: 0; height: 380px; background: {NAVY}; clip-path: polygon(0 60px, 100% 0, 100% 100%, 0 100%); }}
    .lines {{ position: absolute; left: 80px; bottom: 196px; }}
    """
    body = (f'<div class="top">{logo()}<div class="since">Desde 1997 · São Paulo</div></div>'
            f'<div class="content"><div class="label">{safe(p["chip"])}</div><h1>{safe(p["title"])}</h1>'
            f'<p class="sub">{safe(p.get("subtitle"))}</p><div class="items">{items_html(p.get("bullets"))}</div></div>'
            f'<div class="panel"></div><div class="lines">{route_svg(p["pilar"])}</div>{footer(p["cta"])}')
    return page(body, css)

def foto(p):
    src, pos = photo_info(p["foto"])
    css = TOP_CSS + f"""
    body {{ background: {NAVY}; }}
    .bg {{ position: absolute; inset: 0; background: url('{src}') {pos} / cover no-repeat; }}
    .shade {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(18,50,79,.75) 0%, rgba(18,50,79,.15) 20%, rgba(18,50,79,.2) 38%, rgba(18,50,79,.9) 62%, {NAVY} 80%); }}
    .content {{ position: absolute; left: 80px; right: 80px; bottom: 250px; color: #fff; }}
    h1 {{ font-size: {title_size(p['title'], (80, 72, 64, 56))}px; margin-top: 26px; max-width: 920px; }}
    .sub {{ font-size: 30px; line-height: 1.38; margin-top: 24px; color: rgba(255,255,255,.85); max-width: 860px; }}
    """
    body = (f'<div class="bg"></div><div class="shade"></div>'
            f'<div class="top">{logo(True)}<div class="since">Desde 1997 · São Paulo</div></div>'
            f'<div class="content"><div class="label">{safe(p["chip"])}</div><h1>{safe(p["title"])}</h1>'
            f'<p class="sub">{safe(p.get("subtitle"))}</p></div>{footer(p["cta"])}')
    return page(body, css, "dark")

def foto_split(p):
    src, pos = photo_info(p["foto"])
    css = f"""
    .ph {{ position: absolute; left: 0; right: 0; top: 0; height: 560px; background: url('{src}') {pos} / cover no-repeat; clip-path: polygon(0 0, 100% 0, 100% 86%, 0 100%); }}
    .badge {{ position: absolute; left: 60px; top: 52px; background: #fff; padding: 18px 26px; border-radius: 6px; box-shadow: 0 8px 30px rgba(0,0,0,.18); }}
    .badge .logo {{ height: 70px; display: block; }}
    .content {{ position: absolute; left: 80px; right: 80px; top: 600px; }}
    h1 {{ font-size: {title_size(p['title'], (66, 60, 54, 48))}px; margin-top: 22px; max-width: 920px; }}
    .sub {{ font-size: 28px; line-height: 1.38; margin-top: 18px; color: {MUTED}; max-width: 900px; }}
    .items {{ margin-top: 26px; width: 920px; }}
    .item {{ padding: 15px 0; }} .item .t {{ font-size: 27px; }}
    .bar {{ position: absolute; left: 0; right: 0; bottom: 0; height: 190px; background: {NAVY}; }}
    .footer {{ bottom: 44px; border-top: none; padding-top: 0; }}
    """
    bullets = (p.get("bullets") or [])[:3]
    body = (f'<div class="ph"></div><div class="badge">{logo()}</div>'
            f'<div class="content"><div class="label">{safe(p["chip"])}</div><h1>{safe(p["title"])}</h1>'
            f'<p class="sub">{safe(p.get("subtitle"))}</p><div class="items">{items_html(bullets)}</div></div>'
            f'<div class="bar"></div>{footer(p["cta"])}')
    return page(body, css)

def dica(p):
    css = TOP_CSS + f"""
    body {{ background: {NAVY}; color: #fff; }}
    .content {{ position: absolute; left: 80px; right: 80px; top: 250px; bottom: 250px; display: flex; flex-direction: column; }}
    h1 {{ font-size: {title_size(p['title'], (80, 72, 64, 56))}px; margin-top: 30px; max-width: 920px; }}
    .sub {{ font-size: 31px; line-height: 1.38; margin-top: 24px; color: rgba(255,255,255,.78); max-width: 880px; }}
    .cards {{ margin-top: auto; display: grid; gap: 18px; }}
    .card {{ display: grid; grid-template-columns: 80px 1fr; gap: 10px; align-items: center; background: rgba(255,255,255,.07); border-left: 6px solid {ORANGE}; padding: 26px 30px; border-radius: 4px; }}
    .card .n {{ font-size: 46px; font-weight: 800; color: {ORANGE}; }}
    .card .t {{ font-size: 31px; font-weight: 600; line-height: 1.28; }}
    """
    cards = "".join(f'<div class="card"><span class="n">{i+1}</span><span class="t">{safe(b)}</span></div>'
                    for i, b in enumerate((p.get("bullets") or [])[:4]))
    body = (f'<div class="top">{logo(True)}<div class="since">Desde 1997 · São Paulo</div></div>'
            f'<div class="content"><div class="label">{safe(p["chip"])}</div><h1>{safe(p["title"])}</h1>'
            f'<p class="sub">{safe(p.get("subtitle"))}</p><div class="cards">{cards}</div></div>{footer(p["cta"])}')
    return page(body, css, "dark")

def slide(p, i, total, s):
    css = TOP_CSS + f"""
    .logo {{ height: 70px; }}
    .count {{ font-size: 24px; font-weight: 700; color: {MUTED}; letter-spacing: 2px; }}
    .big {{ position: absolute; left: 72px; top: 240px; font-size: 230px; font-weight: 800; color: {ORANGE}; line-height: 1; letter-spacing: -6px; }}
    .content {{ position: absolute; left: 80px; right: 80px; top: 540px; }}
    h1 {{ font-size: {title_size(s['title'], (78, 70, 62, 56))}px; max-width: 920px; }}
    .rule {{ width: 90px; height: 5px; background: {ORANGE}; margin-top: 34px; }}
    .txt {{ font-size: 40px; line-height: 1.42; margin-top: 34px; color: {MUTED}; max-width: 900px; }}
    .panel {{ position: absolute; left: 0; right: 0; bottom: 0; height: 150px; background: {NAVY}; }}
    .lines {{ position: absolute; left: 80px; bottom: 40px; }}
    .next {{ position: absolute; right: 80px; bottom: 58px; color: #fff; font-size: 24px; font-weight: 700; letter-spacing: 1px; }}
    """
    body = (f'<div class="top">{logo()}<div class="count">{i:02d} / {total:02d}</div></div>'
            f'<div class="big">{i-1:02d}</div>'
            f'<div class="content"><h1>{safe(s["title"])}</h1><div class="rule"></div><p class="txt">{safe(s.get("text"))}</p></div>'
            f'<div class="panel"></div><div class="lines">{route_svg(p["pilar"], 560, 67)}</div><div class="next">Arraste →</div>')
    return page(body, css)

def slide_cta(p, total):
    css = TOP_CSS + f"""
    body {{ background: {NAVY}; color: #fff; }}
    .count {{ font-size: 24px; font-weight: 700; color: rgba(255,255,255,.6); letter-spacing: 2px; }}
    .content {{ position: absolute; left: 80px; right: 80px; top: 330px; }}
    h1 {{ font-size: {title_size(p['cta'], (80, 74, 66, 58))}px; margin-top: 28px; }}
    .sub {{ font-size: 31px; line-height: 1.4; margin-top: 28px; color: rgba(255,255,255,.8); max-width: 860px; }}
    .lines {{ position: absolute; left: 80px; bottom: 250px; }}
    """
    body = (f'<div class="top">{logo(True)}<div class="count">{total:02d} / {total:02d}</div></div>'
            f'<div class="content"><div class="label">Leva e Traz Transporte</div><h1>{safe(p["cta"])}</h1>'
            f'<p class="sub">Peça um orçamento sem compromisso pelo link da bio ou no site.</p></div>'
            f'<div class="lines">{route_svg(p["pilar"])}</div>{footer("Desde 1997 em São Paulo")}')
    return page(body, css, "dark")

def carrossel(p):
    slides = p["slides"][:6]
    total = len(slides) + 2
    cover = dict(p, cta="Arraste para ver →")
    pages = [foto(cover) if p.get("foto") else dica(dict(cover, bullets=[]))]
    pages += [slide(p, i + 2, total, s) for i, s in enumerate(slides)]
    pages.append(slide_cta(p, total))
    return pages

LAYOUTS = {"classico": classico, "foto": foto, "foto_split": foto_split, "dica": dica}

# ---------- render ----------

def find_browser():
    for b in ("google-chrome", "chromium", "chromium-browser"):
        if shutil.which(b):
            return shutil.which(b)
    return None

def shoot(pages, outs):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    tmp = KIT / "_render.html"
    with sync_playwright() as pw:
        exe = find_browser()
        browser = pw.chromium.launch(executable_path=exe) if exe else pw.chromium.launch()
        pg = browser.new_page(viewport={"width": 1080, "height": 1350})
        for h, out in zip(pages, outs):
            tmp.write_text(h, encoding="utf-8")
            pg.goto(tmp.as_uri()); pg.wait_for_timeout(500)
            Image.open(io.BytesIO(pg.screenshot(type="png"))).convert("RGB").save(out, "JPEG", quality=90, optimize=True)
            print("ok", out)
        browser.close()
    tmp.unlink(missing_ok=True)

def main(src, out):
    p = json.loads(pathlib.Path(src).read_text(encoding="utf-8"))
    layout = p.get("layout", "classico")
    if layout == "carrossel":
        pages = carrossel(p)
        stem = out[:-4] if out.lower().endswith(".jpg") else out
        outs = [f"{stem}-{i+1}.jpg" for i in range(len(pages))]
    else:
        pages = [LAYOUTS[layout](p)]
        outs = [out]
    shoot(pages, outs)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
