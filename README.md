# eHudHud Library

Source files for the illustrated children's books published on [ehudhud.com](https://ehudhud.com) — text, pictures, image prompts, and the scripts that turn each book into an interactive web book, a printable PDF, and Google Play Books files.

## Books

| Folder | Title | Language | Origin | Pages | Pictures | On ehudhud.com |
|---|---|---|---|---|---|---|
| `books/zeez-dahab` | زيز دهب | Arabic | original | 9 | 10 | no |
| `books/al-tair-al-akhdar` | الطائر الأخضر | Arabic | folk tale, retold | 19 | 20 | no |
| `books/ard-al-shumus` | أرض الشموس الصغيرة | Arabic | original | 46 | 43 | old 19-page version |
| `books/al-shater-hassan` | الشاطر حسن | Arabic | folk tale, retold | 17 | 17 | no |
| `books/conqueror-of-the-desert` | The Conqueror of the Desert | English | original | 42 | 25 | no |

All written or retold by Iyad Zayour. `catalog.json` holds the same list in machine-readable form, with a `price` field for each book (empty = not yet priced).

## What is in each book folder

```
books/<id>/
  book.json        the book itself: title, author, credit line, language, direction, and every page
                   (text paragraphs, the picture it uses). This is the source of truth.
  index.html       the interactive page-turning book; open it in a browser or host the folder as-is
  images/          the illustrations, trimmed and compressed for the web
  *.txt            the prompts used to draw the pictures, with a character sheet
```

Open any `books/<id>/index.html` directly in a browser to read the book.

## Layout conventions

- Landscape spreads: picture on the left, text on the right.
- Arabic books read right to left (Next = left arrow / swipe right); English reads left to right.
- Long pages shrink their text to fit; very long scenes are split across two pages that share one picture.
- Dialogue lines start with "– " and get a hanging indent.

## Outputs (`dist/`, not committed)

`dist/` is ignored by git because the files are large and can be rebuilt. Attach them to a GitHub Release when you publish a version.

| Book | Files |
|---|---|
| each book | `<title>.pdf` (landscape, print-ready, fonts embedded) and `<title>.html` (single-file offline copy, pictures embedded) |
| الشاطر حسن | `playbooks/` — fixed-layout RTL EPUB 3 (passes EpubCheck), portrait PDF and cover JPEG for Google Play Books |

## Tools

`tools/` holds the build scripts used so far (Python 3 + Playwright + Pillow):

- `make_pdf_*.py` — landscape PDF and offline single-file HTML for each book
- `playbooks_hassan.py` — Play Books EPUB/PDF/cover for الشاطر حسن

They were written book by book and still contain absolute paths from the build machine; the first task on the roadmap is to replace them with one script that reads `book.json`.

`fonts/` holds the open-licence Google Fonts the books use (Lalezar, Baloo Bhaijaan 2, Baloo 2, Andika), so PDFs and EPUBs embed them.

## Roadmap

See [ROADMAP.md](ROADMAP.md).
