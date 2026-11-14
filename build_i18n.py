#!/usr/bin/env python3
"""Builds the translated pages of the site.

index.html (English) is the source of truth. For every language there is a dictionary
i18n/<lang>.json that maps the exact English text of each element to its translation.
Run `python3 build_i18n.py` after editing index.html, then commit the generated pages.
Use `python3 build_i18n.py --check` in CI or before committing: it fails if some text
was left untranslated or if a dictionary entry no longer matches the English page.
No dependencies beyond the Python standard library.
"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
LANGS = ['pt']

def text_segments(html):
    html = re.sub(r'<(script|style)\b.*?</\1>', '', html, flags=re.S)
    return [s.strip() for s in re.findall(r'>([^<>]+)<', html) if s.strip()]

def needs_translation(seg):
    return len(re.findall(r'[A-Za-zÀ-ÿ]{3,}', seg)) >= 2

def build(lang):
    cfg = json.loads((ROOT / 'i18n' / f'{lang}.json').read_text(encoding='utf-8'))
    src = (ROOT / 'index.html').read_text(encoding='utf-8')
    html, problems = src, []
    for k, v in cfg['units'].items():
        pat = '>' + k + '<'
        if pat not in html:
            problems.append(f'stale dictionary entry (no longer in index.html): {k[:70]!r}')
            continue
        html = html.replace(pat, '>' + v + '<')
    for k, v in cfg['attrs'].items():
        pat = '"' + k + '"'
        if pat not in html:
            problems.append(f'stale attribute entry: {k[:70]!r}')
            continue
        html = html.replace(pat, '"' + v + '"')
    for a, b in cfg['replace']:
        if a not in html:
            problems.append(f'stale replacement: {a[:70]!r}')
            continue
        html = html.replace(a, b)
    # the page lives one folder down: fix relative asset paths
    html = re.sub(r'(href|src)="(css|js|assets|resume)/', r'\1="../\2/', html)
    # text that is still identical to the English page and looks like prose
    ignore = {s for k in cfg['keep'] for s in text_segments('>' + k + '<')}
    ignore |= set(cfg.get('keep_text', []))
    en_seg = set(text_segments(src))
    untranslated = sorted({s for s in text_segments(html) if s in en_seg and s not in ignore and needs_translation(s)})
    out = ROOT / cfg['folder']
    out.mkdir(exist_ok=True)
    (out / 'index.html').write_text(html, encoding='utf-8')
    return problems, untranslated

if __name__ == '__main__':
    failed = False
    for lang in LANGS:
        problems, untranslated = build(lang)
        print(f'[{lang}] wrote {lang}/index.html')
        for p in problems: print('  WARNING', p); failed = True
        for s in untranslated: print('  UNTRANSLATED', repr(s[:90])); failed = True
        if not problems and not untranslated: print('  all text translated')
    if '--check' in sys.argv and failed: sys.exit(1)
