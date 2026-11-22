#!/usrbin/env python3
"""Build the full dialogue dictionary (every text-bearing rule, bilingual).

Output: public/data/{version}/dialogues/dictionary.json
A lazily-loaded, client-side-searchable index of ALL rules.csv text -
the "dialogue dictionary" complement to the curated quest trees.

Usage:
    python3 build_dictionary.py [--en DIR] [--cn DIR] [--version VER] [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_rules import GENERIC_TRIGGERS, load_bilingual  # noqa: E402

DATA_FILES = [
    'data/campaign/rules.csv',
    'data/campaign/rules/askoniaCrisis2.csv',
]

# 语义分类: 前缀 -> 分类 id（前端用 i18n 渲染标签）
CATEGORY_PREFIXES = [
    ('sdtu', 'usurpers'), ('SDTU', 'usurpers'),
    ('sd7s', 'seven_sons'), ('SD7S', 'seven_sons'),
    ('sdse', 'supreme_executor'), ('SDSE', 'supreme_executor'),
    ('sdsw', 'askonia_misc'), ('SDSW', 'askonia_misc'),
    ('sdr', 'askonia_misc'), ('SDR', 'askonia_misc'),
    ('sd', 'sindrian_misc'), ('SD', 'sindrian_misc'),
    ('ga', 'academy'), ('GA', 'academy'),
    ('lpp', 'luddic'), ('LPP', 'luddic'),
    ('bffi', 'bornanew'), ('BFFI', 'bornanew'),
    ('lke', 'luddic'), ('LKE', 'luddic'),
    ('zgr', 'ziggurat'), ('ZGR', 'ziggurat'),
    ('abyssal', 'abyss'),
    ('historian', 'historian'), ('Historian', 'historian'),
    ('tutorial', 'tutorial'), ('Tutorial', 'tutorial'),
]


def category_of(rule_id: str) -> str:
    for pref, cat in CATEGORY_PREFIXES:
        if rule_id.startswith(pref):
            return cat
    return 'other'


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--en', default=os.path.expanduser('~/Games/starsector-0985a-en'))
    ap.add_argument('--cn', default=os.path.expanduser('~/Games/starsector-0985a-cn'))
    ap.add_argument('--version', default='0.98.5a')
    ap.add_argument('--out', default='public/data')
    args = ap.parse_args()

    print('loading rules ...')
    rules, order, _ = load_bilingual(
        [os.path.join(args.en, f) for f in DATA_FILES],
        [os.path.join(args.cn, f) for f in DATA_FILES])

    entries = []
    for rid in order:
        br = rules[rid]
        r = br.en
        zh_text = (br.cn.text if br.cn else '') or r.text
        opts = []
        for i, o in enumerate(r.options):
            o_zh = o.label
            if br.cn and i < len(br.cn.options):
                o_zh = br.cn.options[i].label
            opts.append({'id': o.id, 'en': o.label, 'zh': o_zh})
        has_content = r.text or opts
        if not has_content:
            continue
        entries.append({
            'id': rid,
            'cat': category_of(rid),
            't': r.trigger,
            'c': r.conditions,
            'en': r.text,
            'zh': zh_text,
            'o': opts,
        })

    entries.sort(key=lambda e: e['id'].lower())
    out = {'version': args.version, 'count': len(entries), 'entries': entries}

    out_dir = os.path.join(args.out, args.version, 'dialogues')
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, 'dictionary.json')
    with open(dest, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    size = os.path.getsize(dest)
    print(f'wrote {dest}: {len(entries)} entries, {size/1e6:.1f} MB')

    # 分类统计
    from collections import Counter
    cats = Counter(e['cat'] for e in entries)
    for cat, n in cats.most_common():
        print(f'  {cat:20s} {n}')


if __name__ == '__main__':
    main()
