#!/usr/bin/env python3
"""Build multi-mission quest packages ("series") in one corpus pass.

For each mission in a series:
- auto-detect its stage variable ($<needle>_stage ==) in the corpus
- sweep scene-entry candidates (two-phase discovery, same as draft_quest)
- extract stage enums + bilingual briefings from the EN/CN jars
- assign scene.stage = mission id so the frontend groups scenes per mission

Usage:
    python3 build_series.py            # builds all series below
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
import zipfile
from collections import OrderedDict
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_rules import BiRule, RuleIndex, GENERIC_TRIGGERS, load_bilingual  # noqa: E402
from extract_java import read_utf8_constants  # noqa: E402
from official_names import OFFICIAL_NAMES, PERSON_NAMES  # noqa: E402

DATA_FILES = [
    'data/campaign/rules.csv',
    'data/campaign/rules/askoniaCrisis2.csv',
]
EN_ROOT = os.path.expanduser('~/Games/starsector-0985a-en')
CN_ROOT = os.path.expanduser('~/Games/starsector-0985a-cn')
HERE = os.path.dirname(os.path.abspath(__file__))
QUESTS = os.path.join(HERE, 'quests')

PERSON_COND = re.compile(r'^\$id == (\S+)$')
MARKET_COND = re.compile(r'^\$market\.id == (\S+)$')
ENTITY_COND = re.compile(r'^\$entity\.(\S+)$')
STAGE_COND = re.compile(r'^(\$\w+_stage) == ([A-Z_]+)$')
PROSE_RE = re.compile(r'[a-z]{3} [a-z]+')
GENERIC = GENERIC_TRIGGERS | {'MarketPostDock', 'MarketPostOpen', 'MarketOpened'}

# --------------------------------------------------------------------------
# 系列定义

ACADEMY_MISSIONS = ['gaIntro', 'gaIntro2', 'gaData', 'gaDA', 'gaCO', 'gaProbe',
                    'gaVIP', 'gaOp', 'gaBA', 'gaRR', 'gaTJ', 'gaTTS', 'gaTTB',
                    'gaFC', 'gaPZ', 'gaRH', 'gaKA', 'gaATG', 'gaDHO']
CONTACT_NEEDLES = ['seco', 'dcom', 'extr', 'smug', 'tabo', 'ssat', 'mcb', 'ucb',
                   'hijack', 'jabr', 'ddro', 'sitm', 'rdsm', 'rsom', 'cpm', 'cpc',
                   'psb', 'sShip', 'dhi', 'dsp', 'cheapCom', 'proCom', 'hmdf',
                   'locrlf']

SERIES = [
    # 名称/简介政策：
    # - 单任务包：名字来自 official_names.py（jar 常量池提取，构建时校验）
    # - 聚合包：数据里不写名字/简介，由前端 wiki 编辑层（questEditorial.ts）提供
    {
        'id': 'the_academy_arc',
        'missions': ACADEMY_MISSIONS,
        'extra_needles': {'gaPZ': ['zgr']},
    },
    {'id': 'luddic_pilgrims_path', 'missions': ['lpp']},
    {'id': 'luddic_knight_errant', 'missions': ['lke']},
    {'id': 'bornanew_files', 'missions': ['bffi']},
    {'id': 'recover_a_planetkiller', 'missions': ['pk']},
    {'id': 'sword_of_eventide', 'missions': ['soe']},
    {'id': 'a_new_hope', 'missions': ['anh']},
    {'id': 'contact_missions', 'missions': CONTACT_NEEDLES},
    {'id': 'misc_stories', 'missions': ['tutorial', 'historian', 'affk']},
]


def class_for(mission: str) -> Optional[str]:
    """Java class name for a mission id (from person_missions.csv)."""
    path = os.path.join(EN_ROOT, 'data/campaign/person_missions.csv')
    with open(path, newline='', encoding='cp1252') as f:
        for r in csv.DictReader(f):
            if r['mission id'] == mission:
                return r['plugin']
    return None


def icon_for(mission: str) -> Optional[str]:
    path = os.path.join(EN_ROOT, 'data/campaign/person_missions.csv')
    with open(path, newline='', encoding='cp1252') as f:
        for r in csv.DictReader(f):
            if r['mission id'] == mission:
                return r['icon']
    return None


def java_stages(mission: str):
    """(stage enum ids, paired bilingual prose) from EN/CN jars."""
    cls = class_for(mission)
    if not cls:
        return [], ([], [])
    path = cls.replace('.', '/') + '.class'
    out_stages: List[str] = []
    en_prose: List[str] = []
    cn_prose: List[str] = []
    try:
        ze = zipfile.ZipFile(os.path.join(EN_ROOT, 'starfarer.api.jar'))
        ss = read_utf8_constants(ze.read(path))
        for s in ss:
            if re.fullmatch(r'[A-Z][A-Z0-9_]*', s) and s != 'Stage':
                out_stages.append(s)
            elif (len(s) >= 20 and ' ' in s and not s.startswith(('$', 'com/', 'java/', 'L', '('))
                  and '/' not in s and PROSE_RE.search(s) and s.rstrip().endswith('.')):
                en_prose.append(s[1:] if re.match(r'^[A-Za-z]:', s) else s)
    except (KeyError, zipfile.BadZipFile):
        pass
    try:
        zc = zipfile.ZipFile(os.path.join(CN_ROOT, 'starfarer.api.jar'))
        ss = read_utf8_constants(zc.read(path))
        cn_prose = [s for s in ss if re.search(r'[\u4e00-\u9fff]', s) and len(s) > 8]
    except (KeyError, zipfile.BadZipFile):
        pass
    # dedupe stages preserving order
    seen = set()
    stages = [s for s in out_stages if not (s in seen or seen.add(s))]
    return stages, (en_prose, cn_prose)


def needle_re(n: str):
    """needle 匹配：前后无小写字母（避免 extr 误匹配 extreme）。"""
    return re.compile(r'(?<![A-Za-z0-9_])' + re.escape(n) + r'(?![a-z])')


def sweep(rules, idx: RuleIndex, needles: List[str], stage_var: Optional[str]):
    """Two-phase sweep (mirror of draft_quest). Returns (scenes, persons)."""
    needle_set = set(needles)
    needle_res = [needle_re(n) for n in needle_set]
    blob_hit = lambda blob: any(rx.search(blob) for rx in needle_res)
    quest_persons, quest_markets, quest_entities = set(), set(), set()
    fired = set()
    for br in rules.values():
        fired.update(br.en.fire_targets())
        r = br.en
        blob = ' '.join([r.id, r.trigger, ' '.join(r.conditions),
                         '\n'.join(r.script_lines),
                         ' '.join(o.id for o in r.options)]).lower()
        if not blob_hit(blob):
            continue
        for c in r.conditions:
            c = c.strip()
            m = PERSON_COND.match(c)
            if m:
                quest_persons.add(m.group(1))
                continue
            m = MARKET_COND.match(c)
            if m:
                quest_markets.add(m.group(1))
                continue
            m = ENTITY_COND.match(c)
            if m:
                quest_entities.add(m.group(1))

    scenes: 'OrderedDict[str, dict]' = OrderedDict()
    orphans: 'OrderedDict[str, None]' = OrderedDict()

    def scene_key(stage, ctx):
        base = (stage.lower() if stage else 'misc') + '_' + ctx
        if base in scenes:
            n = 2
            while f'{base}_{n}' in scenes:
                n += 1
            base = f'{base}_{n}'
        return base

    def add(br, stage, ctx, speaker, root=None):
        if br is not None:
            if not br.en.text and not br.en.options:
                return
            root = root or ('r:' + br.en.id)
        ctx = ctx or 'other'
        for sc in scenes.values():
            if sc['stage'] == stage and sc['_ctx'] == ctx:
                if root not in sc['roots']:
                    sc['roots'].append(root)
                if speaker and not sc.get('speaker'):
                    sc['speaker'] = speaker
                return
        key = scene_key(stage, ctx)
        scenes[key] = {'id': key, 'stage': stage, 'speaker': speaker,
                       'roots': [root], '_ctx': ctx}

    def rule_ctx(r):
        for c in r.conditions:
            c = c.strip()
            m = PERSON_COND.match(c)
            if m:
                return 'talk_' + m.group(1), m.group(1)
            m = MARKET_COND.match(c)
            if m:
                return 'mkt_' + m.group(1), None
            m = ENTITY_COND.match(c)
            if m:
                return 'ent_' + m.group(1), None
        return 'other', None

    for br in rules.values():
        r = br.en
        blob = ' '.join([r.id, r.trigger, ' '.join(r.conditions),
                         ' '.join(o.id for o in r.options)]).lower()
        has_needle = blob_hit(blob)

        stage = None
        if stage_var:
            for c in r.conditions:
                m = STAGE_COND.match(c.strip())
                if m and m.group(1) == stage_var:
                    stage = m.group(2)

        ctx, spk = rule_ctx(r)
        if stage is not None:
            if r.text or r.options:
                add(br, stage, ctx, spk)
            continue
        if not has_needle:
            continue
        if '$menuState == bar' in r.conditions:
            add(br, None, 'bar', None)
            continue
        if r.trigger in ('MarketPostDock', 'MarketPostOpen'):
            add(br, None, ctx if ctx != 'other' else 'dock', None)
            continue
        if r.trigger in ('OpenInteractionDialog', 'BeginFleetEncounter'):
            if ctx != 'other':
                add(br, None, ctx, None)
            continue
        if r.trigger in ('PickGreeting', 'OpenCommLink', 'PopulateOptions') and spk in quest_persons:
            add(br, None, 'conv_' + spk, spk)
            continue
        if (r.trigger not in GENERIC and r.trigger not in fired
                and (r.text or r.options)):
            orphans.setdefault(r.trigger, None)
            continue

    for trig in orphans:
        add(None, None, 'orphan_' + trig[:24].lower(), None, root=f't:{trig}')

    # formulaic titles —— 不再写入数据；场景标题由前端按 kind/ref 渲染
    for sc in scenes.values():
        pass
    return scenes, sorted(quest_persons)


def main() -> None:
    print('loading corpus ...')
    rules, order, _ = load_bilingual(
        [os.path.join(EN_ROOT, f) for f in DATA_FILES],
        [os.path.join(CN_ROOT, f) for f in DATA_FILES])
    idx = RuleIndex(rules)

    for spec in SERIES:
        missions = spec['missions']
        all_scenes: List[dict] = []
        all_persons: List[str] = []
        stages_out: List[dict] = []

        for mission in missions:
            needles = [mission] + spec.get('extra_needles', {}).get(mission, [])
            # 自动探测阶段变量: $<mission>_stage ==
            stage_var = f'${mission}_stage'
            has_stage = any(
                stage_var in c for br in rules.values() for c in br.en.conditions)
            scenes, persons = sweep(rules, idx, needles, stage_var if has_stage else None)
            for sc in scenes.values():
                # 归属到任务: scene.stage = mission id（前端按任务分组）
                sc_out = {k: v for k, v in sc.items() if not k.startswith('_')}
                sc_out['speakerOverrides'] = {}
                if sc_out['stage'] is None:
                    sc_out['stage'] = mission
                sc_out['id'] = f"{mission}_{sc['id']}"
                all_scenes.append(sc_out)
            all_persons.extend(p for p in persons if p not in all_persons)

            # 阶段 = 任务本身（系列包）或 Java Stage 枚举
            enum_stages, (en_prose, cn_prose) = java_stages(mission)
            if len(missions) > 1:
                briefing_en = en_prose[0] if en_prose else ''
                briefing_zh = cn_prose[0] if cn_prose else ''
                stages_out.append({
                    'id': mission,
                    'flag': f'${mission}_ref',
                    'briefing': {'en': briefing_en, 'zh': briefing_zh or briefing_en},
                })
            else:
                for i, st in enumerate(enum_stages[:12]):
                    en = en_prose[i] if i < len(en_prose) else ''
                    zh = cn_prose[i] if i < len(cn_prose) else ''
                    stages_out.append({
                        'id': st,
                        'flag': f'${mission}_{st}',
                        'briefing': {'en': en, 'zh': zh or en},
                    })
                if not stages_out:
                    stages_out.append({
                        'id': mission,
                        'flag': f'${mission}_ref',
                        'briefing': {'en': en_prose[0] if en_prose else '',
                                     'zh': (cn_prose[0] if cn_prose else '') or (en_prose[0] if en_prose else '')},
                    })

        characters = []
        for p in all_persons:
            known = PERSON_NAMES.get(p)
            entry = {
                'id': p,
                'name': {'en': known[0], 'zh': known[1] or known[0]} if known
                        else {'en': p, 'zh': p},
            }
            characters.append(entry)

        # 名称政策：单任务包取官方提取名（official_names 校验过），
        # 聚合包不写 name/summary（前端 wiki 编辑层提供）
        pkg_name = None
        pkg_summary = None
        if len(missions) == 1 and missions[0] in OFFICIAL_NAMES:
            en_name, zh_name = OFFICIAL_NAMES[missions[0]]
            pkg_name = {'en': en_name, 'zh': zh_name or en_name}

        out = {
            'id': spec['id'],
            'gameId': missions + spec.get('extra_needles', {}).get('gaPZ', []),
            'factionId': None,
            'icon': icon_for(missions[0]),
            'stages': stages_out,
            'characters': characters,
            'scenes': all_scenes,
            'excludeRules': [],
            'ignoreRules': [],
            'ignoreRulePatterns': ['^DEV', '^dev[A-Z]', 'test', 'Test', 'TEST',
                                    '^relLevel', '^flavorText', '^bar_desc',
                                    '^sd7s', '^SD7S', '^sdse', '^SDSE', '^sdtu', '^SDTU',
                                    '^sdsw', '^SDSW', '^sdr', '^SDR'],
        }
        if pkg_name:
            out['name'] = pkg_name
        dest = os.path.join(QUESTS, spec['id'] + '.json')
        with open(dest, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        print(f"{spec['id']}: {len(all_scenes)} scenes, {len(stages_out)} stages "
              f"-> {dest}")


if __name__ == '__main__':
    main()
