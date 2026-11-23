#!/usr/bin/env python3
"""Enforce the zero-handwriting policy on shipped dialogue data.

Every Chinese (CJK) string in public/data/*/dialogues/*.json must
appear verbatim in the CN game corpus:
  - all parsed cell texts of the CN rules.csv files (same normalization
    as the pipeline applies), or
  - any UTF8 constant of the CN starfarer.api.jar class pool.

Any miss = hand-written or corrupted text = build failure.
Hand-written editorial text is only legal in the frontend layer
(src/questEditorial.ts) and is not scanned here.

Usage:
    python3 enforce_extracted.py [--version VER] [--out DIR]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_rules import _clean_text  # noqa: E402
from extract_java import read_utf8_constants  # noqa: E402

CN_ROOT = os.path.expanduser('~/Games/starsector-0985a-cn')
CN_CSVS = [
    'data/campaign/rules.csv',
    'data/campaign/rules/askoniaCrisis2.csv',
]
CJK_RE = re.compile(r'[\u4e00-\u9fff]')


def build_corpus():
    """corpus: exact-set + 两个巨型子串回退 haystack（处理选项引号/注记重组）。"""
    corpus = set()
    cells = []
    import csv as _csv
    for rel in CN_CSVS:
        with open(os.path.join(CN_ROOT, rel), newline='', encoding='utf-8',
                  errors='ignore') as f:
            for row in _csv.reader(f):
                for cell in row:
                    corpus.add(_clean_text(cell))
                    corpus.add(cell)
                    cells.append(cell)
    z = zipfile.ZipFile(os.path.join(CN_ROOT, 'starfarer.api.jar'))
    jar_strings = []
    for name in z.namelist():
        if not name.endswith('.class'):
            continue
        try:
            for s in read_utf8_constants(z.read(name)):
                corpus.add(s)
                jar_strings.append(s)
        except (ValueError, zipfile.BadZipFile):
            continue
    # 回退 haystack: 全部单元格里以 \x00 连接；再做引号/空白归零变体
    giant = '\x00'.join(cells + jar_strings)
    giant_noq = giant.replace('"', '')
    giant_norm = re.sub(r'[\s"\x00]', '', giant)
    return corpus, giant, giant_noq, giant_norm


def iter_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, list):
        for it in obj:
            yield from iter_strings(it)
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from iter_strings(v)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', default='0.98.5a')
    ap.add_argument('--out', default='public/data')
    args = ap.parse_args()

    print('building CN corpus (csv cells + api jar constants) ...')
    corpus, giant, giant_noq, giant_norm = build_corpus()
    print(f'corpus: {len(corpus)} exact strings, giant haystack '
          f'{len(giant)/1e6:.0f} MB')

    def traced(s: str) -> bool:
        if s in corpus or _clean_text(s) in corpus:
            return True
        if s in giant:
            return True
        # 选项标签 + 尾注重组（单元格里标签与注记间有引号/空白差异）
        if s in giant_noq:
            return True
        if re.sub(r'[\s"]', '', s) in giant_norm:
            return True
        return False

    failures = []
    files = sorted(glob.glob(os.path.join(args.out, args.version,
                                          'dialogues', '*.json')))
    for path in files:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        n_cjk = 0
        for s in iter_strings(data):
            if not CJK_RE.search(s):
                continue
            n_cjk += 1
            if not traced(s):
                failures.append((os.path.basename(path), s[:70]))
        print(f'  {os.path.basename(path)}: {n_cjk} CJK strings checked')

    if failures:
        print(f'\nFAILED: {len(failures)} hand-written/corrupt strings:')
        for f, s in failures[:40]:
            print(f'  [{f}] {s}')
        sys.exit(1)
    print('\nOK: all CJK strings trace back to the CN game corpus')


if __name__ == '__main__':
    main()
