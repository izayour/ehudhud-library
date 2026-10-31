import re, html, json, pathlib, base64
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path("/tmp/claude-0/-home-claude/1c3fcd83-f3c1-56d0-b892-b88e59067aa9/scratchpad")
D = ROOT / "desert"; FONTS = ROOT / "fonts"; OUT = ROOT / "out-desert"; OUT.mkdir(exist_ok=True)
NAME = "The Conqueror of the Desert"
src = (D / "conqueror-of-the-desert.html").read_text(encoding="utf-8")
pages = json.loads(re.search(r"pages: (\[.*?\n  \])", src, re.S).group(1))
chimg = {int(k): v for k, v in re.findall(r'(\d+): "(c\d+\.jpg)"', re.search(r"const CHAPTER_IMG = \{(.*?)\};", src).group(1))}

SPROUT = '<svg viewBox="0 0 32 32"><path d="M16 30V15" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><path d="M16 17c-1-6-6-9-12-8 0 6 5 10 12 8z" fill="currentColor"/><path d="M16 14c1-6 6-10 13-9 0 7-6 11-13 9z" fill="currentColor" opacity=".8"/><path d="M8 30h16" stroke="currentColor" stroke-width="2" stroke-linecap="round" opacity=".5"/></svg>'
CSS = f"""
@font-face{{font-family:'Baloo 2';src:url('file://{FONTS}/Baloo2.ttf');font-weight:400 800}}
@font-face{{font-family:'Andika';src:url('file://{FONTS}/Andika.ttf')}}
@page{{size:280mm 175mm;margin:0}}
*{{box-sizing:border-box}} html,body{{margin:0;background:#FCF8EF}}
.sheet{{width:280mm;height:175mm;display:grid;grid-template-columns:46.6% 1fr;grid-template-rows:175mm;break-after:page;overflow:hidden}}
.sheet:last-child{{break-after:auto}}
.pic{{position:relative;overflow:hidden;background:#EFE5D2}} .pic img{{width:100%;height:100%;object-fit:cover;display:block}}
.pic::after{{content:"";position:absolute;inset:0 0 0 auto;width:10mm;background:linear-gradient(270deg,rgba(47,42,34,.18),transparent)}}
.txt{{position:relative;min-height:0;overflow:hidden;display:flex;flex-direction:column;justify-content:center;padding:14mm 14mm 16mm;color:#2F2A22;font-family:'Andika',sans-serif}}
.cover{{display:flex;flex-direction:column;align-items:center;text-align:center;gap:5mm}}
.kicker{{margin:0;font-size:11pt;color:#6B6150;text-transform:uppercase;letter-spacing:.14em}}
h1{{font-family:'Baloo 2';font-weight:800;margin:0;line-height:.98;font-size:46pt;color:#4F7A2E}}
h1 span{{display:block;font-size:.42em;font-weight:600;color:#C9861F;margin-bottom:.15em}}
.orn{{display:flex;align-items:center;gap:4mm;color:#4F7A2E}} .orn span{{width:22mm;height:.6mm;background:currentColor;opacity:.45}} .orn svg{{width:9mm}}
.author{{margin:0;font-size:15pt;color:#6B6150}} .author b{{color:#2F2A22}}
.story{{display:flex;flex-direction:column;gap:.32em;font-size:15pt}}
.chap{{display:flex;align-items:baseline;gap:.5em;margin-bottom:.45em}}
.chap .n{{font-family:'Baloo 2';font-weight:800;color:#C9861F}} .chap h2{{font-family:'Baloo 2';font-weight:700;font-size:1.45em;line-height:1.1;margin:0;color:#4F7A2E}}
.story p{{margin:0;line-height:1.5}}
.folio{{position:absolute;bottom:6mm;left:0;right:0;text-align:center;font-size:9pt;color:#6B6150}}
"""
e = lambda s: html.escape(s)
sheets = [f'<section class="sheet"><div class="pic"><img src="file://{D}/cover.jpg"></div><div class="txt"><div class="cover"><p class="kicker">A Picture-Book Story</p><h1><span>The Conqueror</span>of the Desert</h1><div class="orn"><span></span>{SPROUT}<span></span></div><p class="author">Written by <b>Iyad Zayour</b></p></div></div></section>']
for n, p in enumerate(pages, 1):
    head = f'<div class="chap"><span class="n">{p["ch"]}</span><h2>{e(p["title"])}</h2></div>' if p.get("title") else ""
    body = "".join(f"<p>{e(t)}</p>" for t in p["text"])
    sheets.append(f'<section class="sheet"><div class="pic"><img src="file://{D}/{chimg[p["ch"]]}"></div><div class="txt"><div class="story">{head}{body}</div><p class="folio">{n}</p></div></section>')
doc = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{NAME}</title><style>{CSS}</style></head><body>{"".join(sheets)}</body></html>'
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium-1243/chrome-linux64/chrome")
    pg = b.new_page(); tmp = OUT / "print.html"; tmp.write_text(doc, encoding="utf-8")
    pg.goto(f"file://{tmp}"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(500)
    print("pt:", pg.evaluate("""() => [...document.querySelectorAll('.txt')].map(t => { const s=t.querySelector('.story'); if(!s) return null;
        const cs=getComputedStyle(t), avail=t.clientHeight-parseFloat(cs.paddingTop)-parseFloat(cs.paddingBottom);
        let fs=parseFloat(getComputedStyle(s).fontSize); while(s.offsetHeight>avail&&fs>8){fs-=.25;s.style.fontSize=fs+'px'} return Math.round(fs*7.5)/10 })"""))
    pg.pdf(path=str(OUT / f"{NAME}.pdf"), width="280mm", height="175mm", print_background=True, prefer_css_page_size=True)
    b.close()
s = re.sub(r'"((?:cover|c\d+)\.jpg)"', lambda m: '"data:image/jpeg;base64,' + base64.b64encode((D / m.group(1)).read_bytes()).decode() + '"', src)
s = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' + s.replace("</style>", "</style></head><body>", 1) + "</body></html>"
(OUT / f"{NAME}.html").write_text(s, encoding="utf-8")
print("done")
