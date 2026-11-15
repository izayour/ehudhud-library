#!/usr/bin/env python3
"""Turn a book's book.json into the description file the eHudHud site's package maker reads
(aiz06/ehudhud: STORY-PACKAGE.md, tools/package/make_package.py).

    python3 tools/book2spec.py books/<id> <spec.json> [--description "…"]
    python3 <ehudhud>/tools/package/make_package.py <spec.json> <ehudhud>/packages/<id>

- The cover page (type "cover") becomes the cover art: the site writes the title over it.
- Every paragraph becomes a block in reading order. A paragraph starting with "– " is a line of dialogue: a
  "speech" block (the reader puts the dash back); the books do not name the speaker, so it has no "who".
- Picture paths in the spec are absolute, so it can be written anywhere.
"""
import json, os, sys

CREDIT = {'original': 'تأليف', 'folk tale (retold)': 'إعداد', 'folk tale, retold': 'إعداد'}
ENDING = {'ar': 'تصبحون على خير', 'en': 'Good night!'}
WRITTEN = {'original': 'Written by', 'folk tale (retold)': 'Retold by', 'folk tale, retold': 'Retold by'}


def main():
    args = sys.argv[1:]
    desc = None
    if '--description' in args:
        i = args.index('--description'); desc = args[i + 1]; del args[i:i + 2]
    book_dir, spec_path = os.path.abspath(args[0]), args[1]
    b = json.load(open(os.path.join(book_dir, 'book.json'), encoding='utf-8'))
    lang = b['lang']
    pic = lambda name: os.path.join(book_dir, 'images', name)
    word = (CREDIT if lang == 'ar' else WRITTEN).get(b.get('origin'), 'تأليف' if lang == 'ar' else 'Written by')

    spec = {
        'id': b['id'], 'kind': 'picture-book', 'languages': [lang], 'original': lang,
        'title': {lang: b['title']}, 'author': {lang: b['author']},
        'credits': {lang: f"eHudHud. {word} {b['author']}"},
        'ending': {lang: ENDING.get(lang, '')},
        'pages': [],
    }
    if desc: spec['description'] = {lang: desc}
    for p in b['pages']:
        if p.get('type') == 'cover':
            spec['cover'] = {'art': pic(p['img'])}
            continue
        blocks = []
        for t in p.get('text', []):
            t = t.strip()
            if t.startswith('–') or t.startswith('-'):
                blocks.append({'type': 'speech', 'text': {lang: t.lstrip('–-').strip()}})
            else:
                blocks.append({'type': 'narration', 'text': {lang: t}})
        spec['pages'].append({'picture': pic(p['img']), 'blocks': blocks})
    if 'cover' not in spec: raise SystemExit('book.json has no cover page (type "cover")')
    json.dump(spec, open(spec_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f"{b['id']}: {len(spec['pages'])} pages, {sum(len(p['blocks']) for p in spec['pages'])} blocks -> {spec_path}")


if __name__ == '__main__':
    main()
