# Roadmap

## 1. Tidy the build
- [ ] One build script, `tools/build.py <id>`, that reads `books/<id>/book.json` and produces `index.html`, the landscape PDF, the offline HTML, and (optionally) Play Books EPUB + PDF + cover.
- [ ] Move each book's colours and ornament (beetle, bird, orange, candle, sprout) into a `theme` block in `book.json`.
- [ ] Remove absolute paths from the old scripts, then delete them.

## 2. Bring the books to ehudhud.com
- [ ] Find out how ehudhud.com packages its picture books (`stories/<id>/story.json`, `.pack` files, `card.json`, tile image) and add an exporter for that format.
- [ ] Add زيز دهب, الطائر الأخضر, الشاطر حسن and The Conqueror of the Desert.
- [ ] Replace the 19-page أرض الشموس الصغيرة with the 46-page version (Samir's journey, corrected merchant pictures).
- [ ] Give each new book a shelf tile with a readable text title (the fox story and أرض الشموس الصغيرة cards currently have none), an age, a lesson tag and a "تحدّث مع طفلك" line.

## 3. Turn on sales
- [ ] Decide the model: e.g. Kalila wa Dimna stories and one picture book free; new picture books priced (≈ $2.99 CAD) or a whole-library bundle.
- [ ] Fill `price` in `catalog.json` and the site catalogue; test a Stripe purchase end to end.

## 4. Site fixes from the review (31 Oct 2026)
- [ ] Add a contact email and a short "for schools" note.
- [ ] الديك الهادر is missing its lesson tag.
- [ ] The Two Guardians book is English-only, so Arabic visitors never see it (shelf says ١٠ حكايات).
- [ ] On phones the top menu runs off the edge ("كيف ت…").
- [ ] Add alt text to tile images.

## 5. Picture fixes still open
- أرض الشموس الصغيرة: merchant consistency on pages 2, 3, 5, 6, 8, 9, 10, 46 (edit prompt with the character sheet); page 15 (Samir inside the elders' room); page 45 (blossoms only, no fruit).
- الطائر الأخضر: stepmother and bird vary between pages (optional).

## 6. Publishing
- [ ] Google Play Books: الشاطر حسن files are ready in `dist/al-shater-hassan/playbooks/`.
- [ ] Later: package ehudhud.com as an Android app (already an installable web app) once sales start.

## 7. New books
- [ ] الشاطر حسن — book 2 (the marid at the river).
- [ ] The Two Guardians of the Great Tree — bring into this repo.
