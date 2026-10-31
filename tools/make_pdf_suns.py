import re, html, pathlib, base64
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path("/tmp/claude-0/-home-claude/1c3fcd83-f3c1-56d0-b892-b88e59067aa9/scratchpad")
BOOK_DIR = ROOT / "suns"
FONTS = ROOT / "fonts"
OUT = ROOT / "out-suns"
OUT.mkdir(exist_ok=True)
NAME = "أرض الشموس الصغيرة"

src = (BOOK_DIR / "ard-al-shumus.html").read_text(encoding="utf-8")
book_js = re.search(r"const BOOK = (\{.*?\n\});", src, re.S).group(1)

BIRD = """<svg viewBox="0 0 32 32"><circle cx="16" cy="18" r="10" fill="currentColor"/><path d="M16 8c0-3 2-5 5-5-1 3-3 4-5 5z" fill="#4F7A2E"/><circle cx="12.5" cy="15" r="1.6" fill="#FBF6EA" opacity=".55"/></svg>"""

CSS = f"""
@font-face{{font-family:'Lalezar';src:url('file://{FONTS}/Lalezar.ttf')}}
@font-face{{font-family:'Baloo Bhaijaan 2';src:url('file://{FONTS}/Baloo.ttf');font-weight:400 800}}
@page{{size:280mm 175mm;margin:0}}
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0;background:#FBF6EA}}
.sheet{{width:280mm;height:175mm;display:grid;grid-template-columns:46.6% 1fr;grid-template-rows:175mm;break-after:page;overflow:hidden;background:#FBF6EA}}
.sheet:last-child{{break-after:auto}}
.pic{{position:relative;overflow:hidden;background:#F3E4CC}}
.pic img{{width:100%;height:100%;object-fit:cover;display:block}}
.pic::after{{content:"";position:absolute;inset:0 0 0 auto;width:10mm;background:linear-gradient(270deg,rgba(51,48,42,.18),transparent)}}
.txt{{direction:rtl;position:relative;min-height:0;overflow:hidden;display:flex;flex-direction:column;justify-content:center;padding:9mm 10mm 13mm;color:#33302A;font-family:'Baloo Bhaijaan 2',sans-serif}}
.cover{{display:flex;flex-direction:column;align-items:center;text-align:center;gap:6mm}}
.kicker{{margin:0;font-size:14pt;color:#66604F}}
.cover h1{{font-family:'Lalezar',sans-serif;font-weight:400;margin:0;font-size:50pt;line-height:1.05;color:#C2580F}}
.orn{{display:flex;align-items:center;gap:4mm;color:#C2580F}}
.orn span{{display:block;width:22mm;height:.6mm;background:currentColor;opacity:.45}}
.orn svg{{width:10mm}}
.author{{margin:0;font-size:17pt;color:#66604F;font-weight:500}}
.author b{{color:#33302A;font-weight:700}}
.story{{display:flex;flex-direction:column;gap:.4em;font-size:17pt}}
.story p{{margin:0;line-height:1.6;font-weight:500}}
.verse{{padding:.5em 1em;border-right:3px solid #C2580F;background:rgba(46,114,71,.07);border-radius:10px 4px 4px 10px}}
.verse p{{font-weight:600;color:#C2580F;line-height:1.7}}
.sec{{font-family:'Lalezar',sans-serif;font-weight:400;font-size:1.6em;line-height:1.2;margin:0 0 .2em;color:#C2580F}}
.story p.lesson{{font-weight:700;color:#C2580F}}
.folio{{position:absolute;bottom:6mm;left:0;right:0;text-align:center;font-size:10pt;color:#66604F}}
"""
esc = lambda s: html.escape(s, quote=True)
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1243/chrome-linux64/chrome")
    page = browser.new_page()
    book = page.evaluate(f"() => ({book_js})")
    sheets = []
    for i, pg in enumerate(book["pages"]):
        if pg.get("type") == "cover":
            txt = (f'<div class="cover"><h1>{esc(book["title"])}</h1>'
                   f'<div class="orn"><span></span>{BIRD}<span></span></div>'
                   f'<p class="author">{esc(book["credit"])} <b>{esc(book["author"])}</b></p></div>')
        else:
            parts = []
            if pg.get("title"):
                parts.append(f'<h2 class="sec">{esc(pg["title"])}</h2>')
            for t in pg["text"]:
                if isinstance(t, dict) and t.get("lesson"):
                    parts.append(f'<p class="lesson">{esc(t["lesson"])}</p>')
                elif isinstance(t, dict):
                    parts.append('<div class="verse">' + "".join(f"<p>{esc(l)}</p>" for l in t["verse"]) + "</div>")
                else:
                    parts.append(f"<p>{esc(t)}</p>")
            txt = f'<div class="story">{"".join(parts)}</div><p class="folio">{str(i).translate(AR)}</p>'
        img = f'<img src="file://{BOOK_DIR / pg["img"]}" style="object-position:{pg.get("pos","50% 50%")}">' if pg.get("img") else ""
        sheets.append(f'<section class="sheet"><div class="pic">{img}</div><div class="txt">{txt}</div></section>')
    doc = f'<!doctype html><html lang="ar"><head><meta charset="utf-8"><title>{esc(book["title"])}</title><style>{CSS}</style></head><body>{"".join(sheets)}</body></html>'
    tmp = OUT / "print.html"; tmp.write_text(doc, encoding="utf-8")
    page.goto(f"file://{tmp}"); page.evaluate("document.fonts.ready"); page.wait_for_timeout(500)
    sizes = page.evaluate("""() => [...document.querySelectorAll('.txt')].map(t => {
        const s = t.querySelector('.story'); if (!s) return null;
        const cs = getComputedStyle(t);
        const avail = t.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
        let fs = parseFloat(getComputedStyle(s).fontSize);
        while (s.offsetHeight > avail && fs > 8) { fs -= 0.25; s.style.fontSize = fs + 'px'; }
        return Math.round(fs * 0.75 * 10) / 10; })""")
    print("pt:", sizes)
    page.pdf(path=str(OUT / f"{NAME}.pdf"), width="280mm", height="175mm", print_background=True, prefer_css_page_size=True)
    browser.close()

# Offline single-file copy of the interactive book, pictures embedded.
s = src
s = re.sub(r'(img"?: )"([a-z0-9]+\.jpg)"', lambda m: (m.group(1) + '"data:image/jpeg;base64,' + base64.b64encode((BOOK_DIR / m.group(2)).read_bytes()).decode() + '"') if (BOOK_DIR / m.group(2)).exists() else m.group(0), s)
s = '<!doctype html><html lang="ar"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' + s.replace("</style>", "</style></head><body>", 1) + "</body></html>"
(OUT / f"{NAME}.html").write_text(s, encoding="utf-8")
print("done")
