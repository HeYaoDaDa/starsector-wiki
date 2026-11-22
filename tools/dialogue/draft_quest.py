#!/usr/bin/env python3
"""Auto-draft a quest package from the rules corpus.

Discovery strategy:
- Scene entry candidates = generic-trigger rules (PopulateOptions /
  PickGreeting / OpenCommLink / OpenInteractionDialog) gated by the
  quest's stage variable ($<gameId>_stage == X) or by a hook flag
  (e.g. $sdtu_missionCompleted for the post-Usurpers start).
- Candidates are clustered by conversation context: $id == <person>,
  $market.id == <market>, $entity.<flag>, or 'other'.
- Each cluster becomes one scene (multi-entry), attached to the stage
  (or null for hooks).

The draft is then hand-polished: titles, speakers, characters, flags
glossary, ignoreRules.

Usage:
    python3 draft_quest.py --game-id sd7s --stage-var '$sd7s_stage' \
        [--hook-flag '$global.sdtu_missionCompleted'] \
        [--out quests/the_seven_sons.json]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import OrderedDict
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_rules import RuleIndex, GENERIC_TRIGGERS, load_bilingual  # noqa: E402

DATA_FILES = [
    'data/campaign/rules.csv',
    'data/campaign/rules/askoniaCrisis2.csv',
]
ENTRY_TRIGGERS = ('PopulateOptions', 'PickGreeting', 'OpenCommLink',
                  'OpenInteractionDialog')
PERSON_COND = re.compile(r'^\$id == (\S+)$')
MARKET_COND = re.compile(r'^\$market\.id == (\S+)$')
ENTITY_COND = re.compile(r'^\$entity\.(\S+)$')
STAGE_COND = re.compile(r'^(\$\w+_stage) == ([A-Z_]+)$')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--en', default=os.path.expanduser('~/Games/starsector-0985a-en'))
    ap.add_argument('--cn', default=os.path.expanduser('~/Games/starsector-0985a-cn'))
    ap.add_argument('--game-id', required=True)
    ap.add_argument('--stage-var', required=True)
    ap.add_argument('--hook-flag', default=None)
    ap.add_argument('--greetings', action='store_true',
                    help='also include $id-gated PickGreeting/OpenCommLink rules '
                         'referencing the quest (contact comm greetings)')
    ap.add_argument('--quest-id', default=None)
    ap.add_argument('--name-en', default='')
    ap.add_argument('--name-zh', default='')
    ap.add_argument('--out', default=None)
    args = ap.parse_args()

    rules, order, _ = load_bilingual(
        [os.path.join(args.en, f) for f in DATA_FILES],
        [os.path.join(args.cn, f) for f in DATA_FILES])
    idx = RuleIndex(rules)

    stage_var = args.stage_var
    needle = args.game_id

    # candidate entry rules ------------------------------------------------
    scenes: 'OrderedDict[str, dict]' = OrderedDict()
    persons: 'OrderedDict[str, None]' = OrderedDict()

    def scene_key(stage: str, ctx: str) -> str:
        base = (stage.lower() if stage else 'start') + '_' + ctx
        if base in scenes:
            n = 2
            while f'{base}_{n}' in scenes:
                n += 1
            base = f'{base}_{n}'
        return base

    def add_candidate(br, stage, ctx, ctx_speaker=None):
        rid = br.en.id
        if not br.en.text and not br.en.options:
            return
        ctx = ctx or 'other'
        # merge into an existing scene of same stage+ctx when possible
        for key, sc in scenes.items():
            if sc['stage'] == stage and sc['_ctx'] == ctx:
                if rid not in sc['roots']:
                    sc['roots'].append(f'r:{rid}')
                if ctx_speaker and not sc.get('speaker'):
                    sc['speaker'] = ctx_speaker
                return
        key = scene_key(stage, ctx)
        scenes[key] = {
            'id': key,
            'stage': stage,
            'speaker': ctx_speaker,
            'title': {'en': '', 'zh': ''},
            'location': None,
            'roots': [f'r:{rid}'],
            '_ctx': ctx,
        }

    for br in rules.values():
        r = br.en
        if r.trigger not in ENTRY_TRIGGERS:
            continue
        blob = ' '.join([r.id, r.trigger, ' '.join(r.conditions),
                         ' '.join(o.id for o in r.options)]).lower()
        if needle not in blob:
            continue
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
        greeting = False
        if stage is None and args.greetings:
            person = None
            for c in r.conditions:
                m = PERSON_COND.match(c.strip())
                if m:
                    person = m.group(1)
                    break
            if person and r.trigger in ('PickGreeting', 'OpenCommLink'):
                greeting = True
        if stage is None and not hooked and not greeting:
            continue

        ctx = None
        speaker = None
        for c in r.conditions:
            c = c.strip()
            m = PERSON_COND.match(c)
            if m:
                ctx = ('greet_' if greeting and not hooked else '') + 'talk_' + m.group(1)
                if not greeting or hooked:
                    speaker = m.group(1)
                    persons.setdefault(m.group(1), None)
                else:
                    persons.setdefault(m.group(1), None)
                break
            m = MARKET_COND.match(c)
            if m:
                ctx = 'mkt_' + m.group(1)
                break
            m = ENTITY_COND.match(c)
            if m:
                ctx = 'ent_' + m.group(1)
                break
        add_candidate(br, stage, ctx, speaker)

    # draft package --------------------------------------------------------
    characters = [
        {'id': p, 'name': {'en': p, 'zh': p}, 'title': {'en': '', 'zh': ''}}
        for p in persons
    ]

    # formulaic titles from context
    for sc in scenes.values():
        ctx = sc['_ctx']
        if ctx and ctx.startswith('greet_talk_'):
            who = ctx[len('greet_talk_'):]
            sc['title'] = {'en': f'Greetings: {who}', 'zh': f'问候：{who}'}
            sc['location'] = {'en': f'Comm conversation with {who}',
                             'zh': f'与 {who} 的通讯'}
        elif ctx and ctx.startswith('talk_'):
            who = ctx[5:]
            sc['title'] = {'en': f'Talk: {who}', 'zh': f'与 {who} 交谈'}
            sc['location'] = {'en': f'Comm conversation with {who}',
                             'zh': f'与 {who} 的通讯'}
        elif ctx and ctx.startswith('mkt_'):
            where = ctx[4:]
            sc['title'] = {'en': f'Market: {where}', 'zh': f'市场：{where}'}
            sc['location'] = {'en': f'Docked at {where}',
                              'zh': f'靠港 {where}'}
        elif ctx and ctx.startswith('ent_'):
            sc['title'] = {'en': 'Fleet encounter', 'zh': '舰队遭遇'}
        elif ctx == 'other':
            sc['title'] = {'en': sc['id'], 'zh': sc['id']}
        if sc['stage'] is None:
            sc['title']['en'] = 'Quest start: ' + sc['title']['en']
            sc['title']['zh'] = '任务开始：' + sc['title']['zh']
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
        'ignoreRulePatterns': ['^DEV', '^dev[A-Z]'],
    }
    dest = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'quests', out['id'] + '.json')
    with open(dest, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    # summary for the curator ----------------------------------------------
    print(f"draft: {dest}")
    print(f"scenes: {len(scenes)}, characters: {len(characters)}")
    by_stage: Dict[str, List[str]] = {}
    for sc in scenes.values():
        by_stage.setdefault(sc['stage'] or '(hook)', []).append(sc['id'])
    for st, ids in by_stage.items():
        print(f"  {st}: {len(ids)}")
        for i in ids:
            print(f"     - {i}  roots={len(scenes[i]['roots'])}")


if __name__ == '__main__':
    main()
