#!/usr/bin/env python3
"""Auto-draft a quest package from the rules corpus.

Two-phase discovery:
1. Collect quest-relevant context keys (persons / markets / entity flags)
   from every rule that references the quest needle.
2. Sweep the corpus for scene-entry candidates:
   - stage-gated entries ($<gameId>_stage == X, any trigger)
   - hook-flag entries (e.g. $sdtu_missionCompleted for the sequel start)
   - bar events ($menuState == bar) referencing the quest
   - market-dock flavor / entity dialogs referencing the quest
   - ALL conversations of quest-relevant persons (greetings + topic
     pools), even when the entry rule itself doesn't reference the quest
   - custom-trigger hubs that nothing in the CSV ever fires
     (Java-fired entry points) -> trigger-rooted scenes

Usage:
    python3 draft_quest.py --game-id sd7s --stage-var '$sd7s_stage' \
        [--hook-flag '$global.sdtu_missionCompleted'] \
        --quest-id the_seven_sons --out quests/the_seven_sons.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import OrderedDict
from typing import Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_rules import BiRule, RuleIndex, GENERIC_TRIGGERS, load_bilingual  # noqa: E402

DATA_FILES = [
    'data/campaign/rules.csv',
    'data/campaign/rules/askoniaCrisis2.csv',
]
PERSON_COND = re.compile(r'^\$id == (\S+)$')
MARKET_COND = re.compile(r'^\$market\.id == (\S+)$')
ENTITY_COND = re.compile(r'^\$entity\.(\S+)$')
STAGE_COND = re.compile(r'^(\$\w+_stage) == ([A-Z_]+)$')
GENERIC = GENERIC_TRIGGERS | {'MarketPostDock', 'MarketPostOpen', 'MarketOpened'}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--en', default=os.path.expanduser('~/Games/starsector-0985a-en'))
    ap.add_argument('--cn', default=os.path.expanduser('~/Games/starsector-0985a-cn'))
    ap.add_argument('--game-id', required=True)
    ap.add_argument('--stage-var', required=True)
    ap.add_argument('--hook-flag', default=None)
    ap.add_argument('--quest-id', default=None)
    ap.add_argument('--name-en', default='')
    ap.add_argument('--name-zh', default='')
    ap.add_argument('--out', default=None)
    args = ap.parse_args()

    rules, order, _ = load_bilingual(
        [os.path.join(args.en, f) for f in DATA_FILES],
        [os.path.join(args.cn, f) for f in DATA_FILES])
    idx = RuleIndex(rules)
    needle = args.game_id
    stage_var = args.stage_var

    # ---- phase 1: quest-relevant context keys ---------------------------
    quest_persons = set()
    quest_markets = set()
    quest_entities = set()
    fired_triggers = set()
    for br in rules.values():
        fired_triggers.update(br.en.fire_targets())
        r = br.en
        blob = ' '.join([r.id, r.trigger, ' '.join(r.conditions),
                         '\n'.join(r.script_lines),
                         ' '.join(o.id for o in r.options)]).lower()
        if needle not in blob:
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

    # ---- phase 2: sweep entry candidates ---------------------------------
    scenes: 'OrderedDict[str, dict]' = OrderedDict()
    orphan_hubs: 'OrderedDict[str, None]' = OrderedDict()

    def scene_key(stage, ctx):
        base = (stage.lower() if stage else 'misc') + '_' + ctx
        if base in scenes:
            n = 2
            while f'{base}_{n}' in scenes:
                n += 1
            base = f'{base}_{n}'
        return base

    def add_candidate(br: Optional[BiRule], stage, ctx, speaker, root_spec=None):
        if br is not None:
            if not br.en.text and not br.en.options:
                return
            root = root_spec or ('r:' + br.en.id)
        else:
            root = root_spec
        ctx = ctx or 'other'
        for key, sc in scenes.items():
            if sc['stage'] == stage and sc['_ctx'] == ctx:
                if root not in sc['roots']:
                    sc['roots'].append(root)
                if speaker and not sc.get('speaker'):
                    sc['speaker'] = speaker
                return
        key = scene_key(stage, ctx)
        scenes[key] = {
            'id': key,
            'stage': stage,
            'speaker': speaker,
            'title': {'en': '', 'zh': ''},
            'location': None,
            'roots': [root],
            '_ctx': ctx,
        }

    def rule_ctx(r) -> str:
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
        has_needle = needle in blob

        stage = None
        for c in r.conditions:
            m = STAGE_COND.match(c.strip())
            if m and m.group(1) == stage_var:
                stage = m.group(2)
        hooked = False
        if stage is None and args.hook_flag:
            for c in r.conditions:
                if args.hook_flag in c and '!' != c.strip()[0]:
                    hooked = True

        ctx, spk = rule_ctx(r)

        if stage is not None or hooked:
            if not (r.text or r.options):
                continue
            add_candidate(br, stage, ctx, spk)
            continue

        if not has_needle:
            continue

        if '$menuState == bar' in r.conditions:
            add_candidate(br, None, 'bar', None)
            continue
        if r.trigger in ('MarketPostDock', 'MarketPostOpen'):
            add_candidate(br, None, ctx if ctx != 'other' else 'dock', None)
            continue
        if r.trigger in ('OpenInteractionDialog', 'BeginFleetEncounter'):
            if ctx != 'other':
                add_candidate(br, None, ctx, None)
            continue
        # quest-person conversations: greetings + topic pools
        if r.trigger in ('PickGreeting', 'OpenCommLink', 'PopulateOptions') and spk in quest_persons:
            add_candidate(br, None, 'conv_' + spk, spk)
            continue
        # custom hubs nothing fires (Java-fired / dead)
        if (r.trigger not in GENERIC
                and r.trigger not in fired_triggers
                and (r.text or r.options)):
            orphan_hubs.setdefault(r.trigger, None)
            continue

    for trig in orphan_hubs:
        add_candidate(None, None, 'orphan_' + trig[:24].lower(), None,
                      root_spec=f't:{trig}')

    # ---- formulaic titles ------------------------------------------------
    for sc in scenes.values():
        ctx = sc['_ctx']
        if ctx.startswith('conv_'):
            who = ctx[5:]
            sc['title'] = {'en': f'Conversations: {who}', 'zh': f'对话：{who}'}
            sc['location'] = {'en': f'Comm / bar conversations with {who}',
                              'zh': f'与 {who} 的通讯 / 交谈'}
        elif ctx.startswith('talk_'):
            who = ctx[5:]
            sc['title'] = {'en': f'Talk: {who}', 'zh': f'与 {who} 交谈'}
            sc['location'] = {'en': f'Comm conversation with {who}',
                              'zh': f'与 {who} 的通讯'}
        elif ctx.startswith('greet_talk_'):
            who = ctx[len('greet_talk_'):]
            sc['title'] = {'en': f'Greetings: {who}', 'zh': f'问候：{who}'}
        elif ctx.startswith('mkt_'):
            where = ctx[4:]
            sc['title'] = {'en': f'Market: {where}', 'zh': f'市场：{where}'}
            sc['location'] = {'en': f'Docked at {where}', 'zh': f'靠港 {where}'}
        elif ctx.startswith('ent_'):
            sc['title'] = {'en': 'Fleet encounter', 'zh': '舰队遭遇'}
        elif ctx == 'bar':
            sc['title'] = {'en': 'Bar event', 'zh': '酒吧事件'}
            sc['location'] = {'en': 'Bar conversation', 'zh': '酒吧交谈'}
        elif ctx == 'dock':
            sc['title'] = {'en': 'Docked flavor text', 'zh': '靠港见闻'}
        elif ctx.startswith('orphan_'):
            sc['title'] = {'en': f'Event: {ctx[7:]}', 'zh': f'事件：{ctx[7:]}'}
        else:
            sc['title'] = {'en': sc['id'], 'zh': sc['id']}
        if sc['stage'] is None and ctx.startswith('talk_'):
            sc['title']['en'] = 'Quest start: ' + sc['title']['en']
            sc['title']['zh'] = '任务开始：' + sc['title']['zh']

    # ---- draft package ----------------------------------------------------
    characters = [
        {'id': p, 'name': {'en': p, 'zh': p}, 'title': {'en': '', 'zh': ''}}
        for p in sorted(quest_persons)
    ]
    out = {
        'id': args.quest_id or args.game_id,
        'gameId': args.game_id,
        'name': {'en': args.name_en, 'zh': args.name_zh},
        'summary': {'en': '', 'zh': ''},
        'factionId': None,
        'stages': [],
        'characters': characters,
        'flags': {},
        'scenes': [
            {k: v for k, v in sc.items() if not k.startswith('_')}
            for sc in scenes.values()
        ],
        'excludeRules': [],
        'ignoreRules': [],
        'ignoreRulePatterns': ['^DEV', '^dev[A-Z]', 'test', 'Test', 'TEST',
                                '^relLevel', '^flavorText'],
    }
    dest = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'quests', out['id'] + '.json')
    with open(dest, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f'draft: {dest}')
    print(f'scenes: {len(scenes)}, characters: {len(characters)}')
    by_stage: Dict[str, List[str]] = {}
    for sc in scenes.values():
        by_stage.setdefault(sc['stage'] or '(misc)', []).append(sc['id'])
    for st in sorted(by_stage):
        ids = by_stage[st]
        print(f'  {st}: {len(ids)}')


if __name__ == '__main__':
    main()
