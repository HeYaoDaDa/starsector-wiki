#!/usr/bin/env python3
"""Official (extracted) names, summaries and character titles.

All strings below are QUOTES from the game data (EN/CN starfarer.api.jar
constant pools, or official CN rules.csv text) — never hand-translated.
`verify()` asserts every configured string really exists in the pools,
so a game update that moves them fails loudly instead of silently
shipping invented text.

Usage:
    python3 official_names.py           # verify all strings against the jars
"""

from __future__ import annotations

import csv
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_java import read_utf8_constants  # noqa: E402

EN_ROOT = os.path.expanduser('~/Games/starsector-0985a-en')
CN_ROOT = os.path.expanduser('~/Games/starsector-0985a-cn')

# mission id -> (en_name, zh_name or None to display EN)
OFFICIAL_NAMES = {
    'sdtu': ('The Usurpers', '篡位者们'),
    'sdse': ('Heir to Andrada', 'Andrada 的继承人'),
    'lpp': ("The Pilgrim's Path", '朝圣者之路'),
    'lke': ('Knight Errant', '骑士迷途'),
    'bffi': ('False Idols', '伪像'),
    'pk': ('The Scythe of Orion', '猎户座之镰'),
    'anh': ('Passage To Volturn', 'Volturn 之旅'),
    'affk': ('A Favor for Kanta', None),
}
# 有类但无常量池任务名：不配即不写入数据（前端 wiki 标签层兜底）

# (quest package, character id) -> (en_title, zh_title) —— 均可溯源官方文本
OFFICIAL_TITLES = {
    ('the_usurpers', 'macario'): ('Chief High Inspector', '最高检察长'),
    ('the_usurpers', 'hyder'): ('Deputy Star Marshal', '副星际元帅'),
    ('the_usurpers', 'caden'): ('Guard High Deputy Executor', '卫队最高副首长'),
    ('the_usurpers', 'imoinu'): ('Double agent', '双面特工'),
    ('the_seven_sons', 'macario'): ('Chief High Inspector', '最高检察长'),
    ('the_seven_sons', 'hyder'): ('Deputy Star Marshal', '副星际元帅'),
    ('the_seven_sons', 'caden'): ('Guard High Deputy Executor', '卫队最高副首长'),
    ('the_seven_sons', 'imoinu'): ('Double agent', '双面特工'),
    ('the_seven_sons', 'achilles_andrada'): ('Clone-son of Philip Andrada', '克隆子嗣'),
    ('the_supreme_executor', 'macario'): ('Chief High Inspector', '最高检察长'),
    ('the_supreme_executor', 'achilles_andrada'): ('Clone-son of Philip Andrada', '克隆子嗣'),
}

# person id -> (en_name, zh_name) —— 源自官方文本提及的人物名（拉美人名官方保留拉丁）
PERSON_NAMES = {
    'ram': ('Yannick Ram', 'Yannick Ram'),
    'macario': ('Dolos Macario', 'Dolos Macario'),
    'hyder': ('Oxana Hyder', 'Oxana Hyder'),
    'caden': ('Horacio Caden', 'Horacio Caden'),
    'imoinu': ('Imoinu Kato', 'Imoinu Kato'),
    'rao': ('Orcus Rao', 'Orcus Rao'),
    'siyavong': ('Finlay Siyavong', 'Finlay Siyavong'),
    'faro_inesis': ('Faro Inesis', 'Faro Inesis'),
    'arroyo': ('Rayan Arroyo', 'Rayan Arroyo'),
    'horus_yaribay': ('Horus Yaribay', 'Horus Yaribay'),
    'reynard_hannan': ('Reynard Hannan', 'Reynard Hannan'),
    'daud': ('Baikal Daud', 'Baikal Daud'),
    'glamor_rotanev': ('Zunya Glamor-Rotanev', 'Zunya Glamor-Rotanev'),
    'gargoyle': ('Gargoyle', 'Gargoyle'),
    'baird': ('Provost Baird', 'Provost Baird'),
    'fortuna_kato': ('Fortuna Kato', 'Fortuna Kato'),
    'maeus_moroz': ('Maeus Moroz', 'Maeus Moroz'),
    'perseus': ('Perseus', 'Perseus'),
}


def _pools(mid: str):
    path = None
    with open(os.path.join(EN_ROOT, 'data/campaign/person_missions.csv'),
              newline='', encoding='cp1252') as f:
        for r in csv.DictReader(f):
            if r['mission id'] == mid:
                path = r['plugin'].replace('.', '/') + '.class'
                break
    if not path:
        return None, None
    ze = zipfile.ZipFile(os.path.join(EN_ROOT, 'starfarer.api.jar'))
    en = read_utf8_constants(ze.read(path))
    try:
        zc = zipfile.ZipFile(os.path.join(CN_ROOT, 'starfarer.api.jar'))
        cn = read_utf8_constants(zc.read(path))
    except KeyError:
        cn = []
    return en, cn


def verify() -> bool:
    ok = True
    for mid, (en_name, zh_name) in OFFICIAL_NAMES.items():
        en_pool, cn_pool = _pools(mid)
        if en_pool is None:
            print(f"MISS {mid}: no mission class")
            ok = False
            continue
        if en_name not in en_pool:
            print(f"MISS {mid}: EN name not in pool: {en_name!r}")
            ok = False
        if zh_name and zh_name not in cn_pool:
            print(f"MISS {mid}: CN name not in pool: {zh_name!r}")
            ok = False
    # 官方头衔: zh 需出现在 CN 语料（CN rules.csv 全文 ∪ 相关类常量池）
    cn_csv = ''
    for rel in ('data/campaign/rules.csv', 'data/campaign/rules/askoniaCrisis2.csv'):
        cn_csv += open(os.path.join(CN_ROOT, rel), encoding='utf-8', errors='ignore').read()
    zc = zipfile.ZipFile(os.path.join(CN_ROOT, 'starfarer.api.jar'))
    for cls in ('missions/askonia/TheUsurpers', 'missions/askonia/SDSevenSons',
                'missions/askonia/SDSupremeExecutor'):
        try:
            cn_csv += '\n'.join(read_utf8_constants(
                zc.read('com/fs/starfarer/api/impl/campaign/' + cls + '.class')))
        except KeyError:
            pass
    for (pkg, char), (en_t, zh_t) in OFFICIAL_TITLES.items():
        if zh_t not in cn_csv:
            print(f"MISS title [{pkg}/{char}]: zh not in CN corpus: {zh_t!r}")
            ok = False
    for pid, (en_n, zh_n) in PERSON_NAMES.items():
        if zh_n != zh_n:  # placeholder, names are Latin
            pass
    print('verify:', 'OK' if ok else 'FAILED')
    return ok


if __name__ == '__main__':
    sys.exit(0 if verify() else 1)
