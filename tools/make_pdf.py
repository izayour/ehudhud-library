import json, re, html, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path("/tmp/claude-0/-home-claude/1c3fcd83-f3c1-56d0-b892-b88e59067aa9/scratchpad")
BOOK_DIR = ROOT / "book"
FONTS = ROOT / "fonts"
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)

src = (BOOK_DIR / "zeez-dahab.html").read_text(encoding="utf-8")
# Pull the BOOK object literal out of the page script.
m = re.search(r"const BOOK = (\{.*?\n\});", src, re.S)
book_js = m.group(1)

BEETLE = """<svg viewBox="0 0 24 24" aria-hidden="true"><ellipse cx="12" cy="13.5" rx="6" ry="7.5" fill="currentColor"/><circle cx="12" cy="5" r="2.6" fill="currentColor"/><path d="M12 7v14" stroke="#FBF6EA" stroke-width="1.2"/><path d="M6.5 10 3 8M6 14H2.5M6.5 18 3.5 20.5M17.5 10 21 8M18 14h3.5M17.5 18l3 2.5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" fill="none"/></svg>"""

CSS = f"""
@font-face{{font-family:'Lalezar';src:url('file://{FONTS}/Lalezar.ttf')}}
@font-face{{font-family:'Baloo Bhaijaan 2';src:url('file://{FONTS}/Baloo.ttf');font-weight:400 800}}
@page{{size:280mm 175mm;margin:0}}
*{{box-sizing:border-box}}
html,body{{margin:0;padding:0;background:#FBF6EA}}
.sheet{{width:280mm;height:175mm;display:grid;grid-template-columns:46.6% 1fr;grid-template-rows:175mm;page-break-after:always;break-after:page;overflow:hidden;background:#FBF6EA}}
.sheet:last-child{{page-break-after:auto;break-after:auto}}
.pic{{position:relative;overflow:hidden;background:#EAF1F5}}
.pic img{{width:100%;height:100%;object-fit:cover;display:block}}
.pic::after{{content:"";position:absolute;inset:0 0 0 auto;width:10mm;background:linear-gradient(270deg,rgba(59,47,34,.18),transparent)}}
.txt{{direction:rtl;position:relative;min-height:0;overflow:hidden;display:flex;flex-direction:column;justify-content:center;padding:14mm 13mm 16mm;color:#3B2F22;font-family:'Baloo Bhaijaan 2',sans-serif}}
.cover{{display:flex;flex-direction:column;align-items:center;text-align:center;gap:7mm}}
.cover h1{{font-family:'Lalezar',sans-serif;font-weight:400;margin:0;font-size:52pt;line-height:1.05;color:#A9790F}}
.orn{{display:flex;align-items:center;gap:4mm;color:#A9790F}}
.orn span{{display:block;width:22mm;height:.6mm;background:currentColor;opacity:.5}}
.orn svg{{width:8mm}}
.author{{margin:0;font-size:17pt;color:#6E5C45;font-weight:500}}
.author b{{color:#3B2F22;font-weight:700}}
.story{{display:flex;flex-direction:column;gap:.55em;font-size:17pt}}
.story p{{margin:0;line-height:1.75;font-weight:500}}
.story p.dlg{{padding-inline-start:1.1em;text-indent:-1.1em}}
.folio{{position:absolute;bottom:6mm;left:0;right:0;text-align:center;font-size:10pt;color:#6E5C45}}
.end{{margin-top:.6em;text-align:center;font-family:'Lalezar',sans-serif;color:#A9790F;font-size:1.4em}}
"""

def esc(s):
    return html.escape(s, quote=True)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1243/chrome-linux64/chrome")
    page = browser.new_page()
    book = page.evaluate(f"() => ({book_js})")

    sheets = []
    n = len(book["pages"])
    for i, pg in enumerate(book["pages"]):
        img = f"file://{BOOK_DIR / pg['img']}" if pg.get("img") else ""
        pos = pg.get("pos", "50% 50%")
        if pg.get("type") == "cover":
            txt = (f'<div class="cover"><h1>{esc(book["title"])}</h1>'
                   f'<div class="orn"><span></span>{BEETLE}<span></span></div>'
                   f'<p class="author">تأليف <b>{esc(book["author"])}</b></p></div>')
        else:
            paras = "".join(
                f'<p{" class=\"dlg\"" if t.startswith("–") else ""}>{esc(t)}</p>' for t in pg["text"])
            folio = f'<p class="folio">{i:,}</p>'.replace(f">{i:,}<", ">" + str(i).translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")) + "<")
            txt = f'<div class="story">{paras}</div>{folio}'
        pic = f'<img src="{img}" alt="{esc(pg.get("alt",""))}" style="object-position:{pos}">' if img else ""
        sheets.append(f'<section class="sheet"><div class="pic">{pic}</div><div class="txt">{txt}</div></section>')

    doc = f'<!doctype html><html lang="ar"><head><meta charset="utf-8"><title>{esc(book["title"])}</title><style>{CSS}</style></head><body>{"".join(sheets)}</body></html>'
    tmp = OUT / "print.html"
    tmp.write_text(doc, encoding="utf-8")
    page.goto(f"file://{tmp}")
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(500)
    # Shrink text on long pages until it fits its page.
    report = page.evaluate("""() => [...document.querySelectorAll('.txt')].map(t => {
        const s = t.querySelector('.story'); if (!s) return null;
        const cs = getComputedStyle(t);
        const avail = t.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
        let fs = parseFloat(getComputedStyle(s).fontSize);
        while (s.offsetHeight > avail && fs > 8) { fs -= 0.25; s.style.fontSize = fs + 'px'; }
        return Math.round(fs * 0.75 * 10) / 10;
    })""")
    print("font sizes (pt):", report)
    page.pdf(path=str(OUT / "zeez-dahab.pdf"), width="280mm", height="175mm", print_background=True, prefer_css_page_size=True)
    browser.close()
print("done")
