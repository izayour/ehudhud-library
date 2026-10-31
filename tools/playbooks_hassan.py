"""Build Google Play Books files for الشاطر حسن: fixed-layout RTL EPUB 3, portrait PDF, cover JPEG."""
import re, json, html, pathlib, shutil, zipfile, uuid, datetime
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path("/tmp/claude-0/-home-claude/1c3fcd83-f3c1-56d0-b892-b88e59067aa9/scratchpad")
H = ROOT / "hassan"; FONTS = ROOT / "fonts"; ATT = pathlib.Path("/mnt/user-data/attachments/1c3fcd83-f3c1-56d0-b892-b88e59067aa9")
OUT = ROOT / "playbooks-hassan"; shutil.rmtree(OUT, ignore_errors=True); OUT.mkdir()
W, HGT = 1344, 1792
CHROME = "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"
TITLE = "الشاطر حسن"; AUTHOR = "إياد زيعور"; YEAR = datetime.date.today().year

# ---- story text from the interactive book ----
src = (H / "al-shater-hassan.html").read_text(encoding="utf-8")
body = re.search(r"pages: \[\n(.*?)\n  \]\n\};", src, re.S).group(1)
scenes = []
for line in body.split("\n"):
    line = line.strip().rstrip(",")
    if not line.startswith('{"'): continue
    p = json.loads(line)
    if p.get("title"): scenes.append({"title": p["title"], "text": list(p["text"]), "more": []})
    else: scenes[-1]["more"] += p["text"]          # scene 15 continuation page
assert len(scenes) == 16, len(scenes)

# ---- full-resolution pictures ----
raw = lambda k: H / "raw" / f"img-{k:03d}.png"
srcs = {0: raw(0), 1: raw(1), 2: raw(2), 3: raw(4), 4: ATT / "b40db93f-image.png", 5: raw(5), 6: raw(6), 7: raw(7),
        8: raw(9), 9: raw(12), 10: raw(10), 11: ATT / "40d3d934-image.png", 12: raw(11), 13: raw(13), 14: raw(14), 15: raw(15), 16: raw(16)}
work = OUT / "work"; work.mkdir()
for k, s in srcs.items():
    im = Image.open(s).convert("RGB")
    if im.size != (W, HGT): im = im.resize((W, HGT), Image.LANCZOS)
    im.save(work / f"pic{k:02d}.jpg", quality=90, optimize=True)

esc = lambda s: html.escape(s, quote=False)
CANDLE = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="56" height="56" aria-hidden="true"><path d="M16 3c3 4 4 6.5 4 8.5a4 4 0 0 1-8 0C12 9.5 13 7 16 3z" fill="#A4521A"/><rect x="12" y="15" width="8" height="12" rx="1.5" fill="#A4521A" opacity=".55"/><rect x="9" y="27" width="14" height="2.4" rx="1.2" fill="#A4521A"/></svg>'

def css(font_base):
    return f"""
@font-face{{font-family:'Lalezar';src:url(FONTDIR/Lalezar.ttf)}}
@font-face{{font-family:'Baloo Bhaijaan 2';src:url(FONTDIR/Baloo.ttf);font-weight:400 800}}
html,body{{margin:0;padding:0;width:{W}px;height:{HGT}px;overflow:hidden}}
body{{background:#FBF6EA;color:#33302A;font-family:'Baloo Bhaijaan 2',sans-serif}}
.page{{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;padding:150px 130px 170px}}
.story{{font-size:{font_base}px}}
.story h2{{font-family:'Lalezar',sans-serif;font-weight:400;font-size:1.75em;line-height:1.2;margin:0 0 .15em;color:#A4521A}}
.orn{{display:flex;align-items:center;gap:18px;margin:0 0 .7em}}
.orn span{{display:block;width:120px;height:3px;background:#A4521A;opacity:.4}}
.story p{{margin:0 0 .45em;line-height:1.72;font-weight:500}}
.story p.dlg{{padding-right:1.1em;text-indent:-1.1em}}
.folio{{position:absolute;bottom:70px;left:0;right:0;text-align:center;font-size:30px;color:#66604F}}
.pic{{position:absolute;inset:0;margin:0}} .pic img{{width:{W}px;height:{HGT}px;display:block}}
.center{{align-items:center;text-align:center}}
.end h2{{font-family:'Lalezar',sans-serif;font-weight:400;font-size:150px;margin:0;color:#A4521A}}
.end p{{font-size:46px;margin:.6em 0 0;color:#66604F}}
.copy{{font-size:34px;line-height:1.8;color:#4E4A3E}} .copy b{{color:#33302A}}
"""

AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
def text_inner(sc, n, key="text", head=True):
    paras = "".join(f'<p{" class=\"dlg\"" if t.startswith("–") else ""}>{esc(t)}</p>' for t in sc[key])
    h = f'<h2>{esc(sc["title"])}</h2><div class="orn"><span></span>{CANDLE}<span></span></div>' if head else ""
    return (f'<div class="page"><div class="story">{h}{paras}</div></div>'
            f'<p class="folio">{str(n).translate(AR)}</p>')

def doc(inner, font_base=54, fontdir="fonts", title=TITLE, lang="ar"):
    c = css(font_base).replace("FONTDIR", fontdir)
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE html>\n'
            f'<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{lang}" xml:lang="{lang}" dir="rtl">'
            f'<head><meta charset="UTF-8"/><meta name="viewport" content="width={W}, height={HGT}"/><title>{esc(title)}</title>'
            f'<style>{c}</style></head><body>{inner}</body></html>')

# ---- fit each text page; render cover ----
fit = {}
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={"width": W, "height": HGT})
    for i, sc in enumerate(scenes, 1):
        fs = 56
        while True:
            (work / "t.xhtml").write_text(doc(text_inner(sc, i), fs, fontdir=str(FONTS)), encoding="utf-8")
            pg.goto(f"file://{work}/t.xhtml"); pg.evaluate("document.fonts.ready")
            ok = pg.evaluate("(()=>{const s=document.querySelector('.story'),p=document.querySelector('.page'),cs=getComputedStyle(p);return s.scrollHeight <= p.clientHeight-parseFloat(cs.paddingTop)-parseFloat(cs.paddingBottom)})()")
            if ok or fs <= 30: break
            fs -= 1
        fit[i] = fs
        if sc["more"]:
            fs2 = 56
            while True:
                (work / "t.xhtml").write_text(doc(text_inner(sc, i, "more", False), fs2, fontdir=str(FONTS)), encoding="utf-8")
                pg.goto(f"file://{work}/t.xhtml"); pg.evaluate("document.fonts.ready")
                ok = pg.evaluate("(()=>{const s=document.querySelector('.story'),p=document.querySelector('.page'),cs=getComputedStyle(p);return s.scrollHeight <= p.clientHeight-parseFloat(cs.paddingTop)-parseFloat(cs.paddingBottom)})()")
                if ok or fs2 <= 30: break
                fs2 -= 1
            fit[(i, "more")] = fs2
    # cover: illustration with the title painted over it
    cover_html = f"""<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>
@font-face{{font-family:'Lalezar';src:url(file://{FONTS}/Lalezar.ttf)}}
@font-face{{font-family:'Baloo Bhaijaan 2';src:url(file://{FONTS}/Baloo.ttf);font-weight:400 800}}
html,body{{margin:0;width:{W}px;height:{HGT}px;overflow:hidden}}
.bg{{position:absolute;inset:0;background:url(file://{work}/pic00.jpg) center/cover}}
.top{{position:absolute;inset:0 0 auto;height:640px;background:linear-gradient(rgba(10,14,40,.82),rgba(10,14,40,.45) 60%,transparent)}}
.bot{{position:absolute;inset:auto 0 0;height:300px;background:linear-gradient(transparent,rgba(10,14,40,.8))}}
.t{{position:absolute;top:90px;left:0;right:0;text-align:center;direction:rtl}}
.k{{font-family:'Baloo Bhaijaan 2';font-weight:600;font-size:52px;color:#F3D9A4;margin:0}}
h1{{font-family:'Lalezar';font-weight:400;font-size:250px;line-height:1;margin:.05em 0 0;color:#FFE7B0;text-shadow:0 6px 0 #7A3A10,0 10px 30px rgba(0,0,0,.6)}}
.a{{position:absolute;bottom:80px;left:0;right:0;text-align:center;font-family:'Baloo Bhaijaan 2';font-size:58px;color:#FBF1DC;direction:rtl}}
.a b{{font-weight:700}}
</style></head><body><div class="bg"></div><div class="top"></div><div class="bot"></div>
<div class="t"><p class="k">حكاية شعبية</p><h1>{TITLE}</h1></div><p class="a">إعداد <b>{AUTHOR}</b></p></body></html>"""
    (work / "cover.html").write_text(cover_html, encoding="utf-8")
    pg.goto(f"file://{work}/cover.html"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
    pg.screenshot(path=str(OUT / "الشاطر حسن - الغلاف.jpg"), type="jpeg", quality=92)
    b.close()
print("font sizes:", fit)
shutil.copy(OUT / "الشاطر حسن - الغلاف.jpg", work / "cover.jpg")

# ---- page list (RTL spreads: text on the right, picture on the left) ----
pages = [("cover", '<figure class="pic"><img src="images/cover.jpg" alt="غلاف كتاب الشاطر حسن"/></figure>', "center")]
for i, sc in enumerate(scenes, 1):
    pages.append((f"t{i:02d}", text_inner(sc, i), "right", fit[i]))
    pages.append((f"p{i:02d}", f'<figure class="pic"><img src="images/pic{i:02d}.jpg" alt="{esc(sc["title"])}"/></figure>', "left"))
    if sc["more"]:
        pages.append((f"t{i:02d}b", text_inner(sc, i, "more", False), "right", fit[(i, "more")]))
        pages.append((f"p{i:02d}b", f'<figure class="pic"><img src="images/pic{i:02d}.jpg" alt="{esc(sc["title"])}"/></figure>', "left"))
pages.append(("end", '<div class="page center end"><h2>النهاية</h2><p>… وتتبعها مغامرة جديدة مع المارد</p></div>', "right"))
pages.append(("copy", f'<div class="page center copy"><p><b>{TITLE}</b><br/>حكاية شعبية<br/>إعداد: {AUTHOR}<br/><br/>© {YEAR} {AUTHOR}. جميع الحقوق محفوظة.</p></div>', "left"))

# ---- EPUB ----
ep = OUT / "epub"; (ep / "META-INF").mkdir(parents=True); oe = ep / "OEBPS"; (oe / "images").mkdir(parents=True); (oe / "fonts").mkdir()
(ep / "mimetype").write_text("application/epub+zip")
(ep / "META-INF/container.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
shutil.copy(work / "cover.jpg", oe / "images/cover.jpg")
for i in range(1, 17): shutil.copy(work / f"pic{i:02d}.jpg", oe / f"images/pic{i:02d}.jpg")
shutil.copy(FONTS / "Lalezar.ttf", oe / "fonts/Lalezar.ttf"); shutil.copy(FONTS / "Baloo.ttf", oe / "fonts/Baloo.ttf")
manifest, spine = [], []
for pgx in pages:
    pid, inner, side = pgx[0], pgx[1], pgx[2]
    fs = pgx[3] if len(pgx) > 3 else 54
    (oe / f"{pid}.xhtml").write_text(doc(inner, fs), encoding="utf-8")
    manifest.append(f'<item id="{pid}" href="{pid}.xhtml" media-type="application/xhtml+xml"{" properties=\"svg\"" if "<svg" in inner else ""}/>')
    spine.append(f'<itemref idref="{pid}" properties="page-spread-{side}"/>' if side != "center" else f'<itemref idref="{pid}" properties="rendition:page-spread-center"/>')
nav = doc('<nav epub:type="toc" id="toc"><h1>المحتويات</h1><ol>' + '<li><a href="cover.xhtml">الغلاف</a></li>' +
          "".join(f'<li><a href="t{i:02d}.xhtml">{esc(sc["title"])}</a></li>' for i, sc in enumerate(scenes, 1)) +
          '</ol></nav>', 40)
(oe / "nav.xhtml").write_text(nav, encoding="utf-8")
imgs = [f'<item id="img-cover" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>'] + \
       [f'<item id="img{i:02d}" href="images/pic{i:02d}.jpg" media-type="image/jpeg"/>' for i in range(1, 17)]
fonts = ['<item id="f1" href="fonts/Lalezar.ttf" media-type="font/ttf"/>', '<item id="f2" href="fonts/Baloo.ttf" media-type="font/ttf"/>']
uid = f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, 'al-shater-hassan-iyad-zayour')}"
now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
opf = f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="ar" dir="rtl">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="bookid">{uid}</dc:identifier><dc:title>{TITLE}</dc:title><dc:language>ar</dc:language>
<dc:creator id="c1">{AUTHOR}</dc:creator><meta refines="#c1" property="role" scheme="marc:relators">edt</meta>
<dc:publisher>{AUTHOR}</dc:publisher><dc:rights>© {YEAR} {AUTHOR}</dc:rights>
<dc:subject>حكايات شعبية</dc:subject><dc:subject>JUVENILE FICTION / Fairy Tales &amp; Folklore / Country &amp; Ethnic</dc:subject>
<meta property="dcterms:modified">{now}</meta>
<meta property="rendition:layout">pre-paginated</meta><meta property="rendition:orientation">portrait</meta><meta property="rendition:spread">landscape</meta>
</metadata>
<manifest><item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
{chr(10).join(manifest + imgs + fonts)}
</manifest>
<spine page-progression-direction="rtl">
{chr(10).join(spine)}
</spine></package>'''
(oe / "content.opf").write_text(opf, encoding="utf-8")
epub_path = OUT / "الشاطر حسن.epub"
with zipfile.ZipFile(epub_path, "w") as z:
    z.write(ep / "mimetype", "mimetype", compress_type=zipfile.ZIP_STORED)
    for f in sorted(ep.rglob("*")):
        if f.is_file() and f.name != "mimetype": z.write(f, f.relative_to(ep).as_posix(), compress_type=zipfile.ZIP_DEFLATED)

# ---- PDF (same pages, portrait) ----
sheets = []
for pgx in pages:
    pid, inner = pgx[0], pgx[1]
    fs = pgx[3] if len(pgx) > 3 else 54
    sheets.append(f'<section class="sheet"><div class="s" style="--fs:{fs}px">{inner.replace("images/", f"file://{oe}/images/")}</div></section>')
pdf_css = css(54).replace("FONTDIR", f"file://{FONTS}").replace(".story{font-size:54px}", ".story{font-size:var(--fs)}")
pdf_css = pdf_css.replace(f"html,body{{margin:0;padding:0;width:{W}px;height:{HGT}px;overflow:hidden}}", "html,body{margin:0;padding:0}")
pdf_html = f'<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>@page{{size:{W}px {HGT}px;margin:0}}{pdf_css}.sheet{{position:relative;width:{W}px;height:{HGT}px;overflow:hidden;break-after:page;background:#FBF6EA}}.sheet:last-child{{break-after:auto}}.s{{position:absolute;inset:0}}</style></head><body>{"".join(sheets)}</body></html>'
(work / "pdf.html").write_text(pdf_html, encoding="utf-8")
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=CHROME); pg = b.new_page()
    pg.goto(f"file://{work}/pdf.html"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(500)
    pg.pdf(path=str(OUT / "الشاطر حسن.pdf"), width=f"{W}px", height=f"{HGT}px", print_background=True, prefer_css_page_size=True)
    b.close()
print("pages:", len(pages)); print("done")
