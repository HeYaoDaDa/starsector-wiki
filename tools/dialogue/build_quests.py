#!/usr/bin/env python3
"""Build quest dialogue JSONs for the wiki frontend.

Pipeline:
1. Parse EN + CN rules.csv (+ rules/askoniaCrisis2.csv) and merge by rule id
2. For each quest package (tools/dialogue/quests/*.json), traverse the rule
   graph from the curated scene roots
3. Emit public/data/{version}/dialogues/{quest}.json + index.json
4. Emit a curation report (coverage, dangling links, unglossed flags)

Scene roots in a quest package:
  "r:<ruleId>"                      synthetic entry step built from that rule
  "m:<ruleId>:<condNeedle>"         same, plus merge in all generic-trigger
                                    rules whose conditions contain <condNeedle>
                                    (e.g. PopulateOptions providers for a
                                    fleet-entity dialog)
  "t:<triggerName>"                 entry at a custom trigger hub

Usage:
    python3 build_quests.py [--en DIR] [--cn DIR] [--version VER] [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional, Set

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_rules import (  # noqa: E402
    BiRule, Rule, RuleIndex, GENERIC_TRIGGERS, load_bilingual,
)

DATA_FILES = [
    'data/campaign/rules.csv',
    'data/campaign/rules/askoniaCrisis2.csv',
]
DEPTH_LIMIT = 8

_STAGE_COND_RE = re.compile(r'^\$sdtu_stage\s*==\s*(\S+)$')
_ADDTEXT_RE = re.compile(r'^(AddText|AddTextSmall)\s+"(.*)"\s*$')


# ---------------------------------------------------------------------------
# quest graph builder

class QuestBuilder:
    def __init__(self, index: RuleIndex, order: List[str], quest: dict):
        self.idx = index
        self.order = order
        self.quest = quest
        self.exclude: Set[str] = set(quest.get('excludeRules', []))
        # steps per scene: scene_id -> {step_id: step}
        self.scene_steps: Dict[str, Dict[str, dict]] = {}
        # rules consumed (for coverage report)
        self.consumed: Set[str] = set()
        self.report = {
            'dangling_options': [],      # options with no response rules
            'external_triggers': [],     # fired triggers with no rules at all
            'uncovered_rules': [],       # quest-referencing rules not reached
            'unglossed_flags': [],       # flags seen but missing from glossary
            'skipped_dev_rules': 0,
            'provider_hits': 0,
        }

    # -- helpers -----------------------------------------------------------

    def _is_dev(self, r: Rule) -> bool:
        if r.id in self.exclude:
            return True
        if r.id.lower().startswith(('dev', 'sddev')):
            return True
        if any('$global.isDevMode' in c for c in r.conditions):
            return True
        return False

    def _script_text_blocks(self, br: BiRule) -> List[dict]:
        """AddText / AddTextSmall paragraphs embedded in the script column."""
        blocks = []

        def extract(script_lines: List[str]):
            out = []
            for line in script_lines:
                m = _ADDTEXT_RE.match(line.strip())
                if m:
                    text = m.group(2).replace('\\"', '"')
                    out.append((m.group(1), text))
            return out

        en_adds = extract(br.en.script_lines)
        cn_adds = extract(br.cn.script_lines) if br.cn else []
        for i, (cmd, en_text) in enumerate(en_adds):
            zh_text = cn_adds[i][1] if i < len(cn_adds) and cn_adds[i][1] != en_text else ''
            blocks.append({
                'rule': br.id,
                'en': en_text,
                'zh': zh_text or en_text,
                'conditions': list(br.en.conditions),
                'effects': [],
                'small': cmd == 'AddTextSmall',
            })
        return blocks

    def _bilingual_option(self, br: BiRule, i: int) -> Optional[dict]:
        try:
            o_en = br.en.options[i]
        except IndexError:
            return None
        o_zh = o_en
        if br.cn and i < len(br.cn.options):
            o_zh = br.cn.options[i]
        return {
            'id': o_en.id,
            'num': o_en.num,
            'en': o_en.label,
            'zh': o_zh.label,
        }

    def _text_block(self, br: BiRule, extra_conditions: List[str] = None) -> dict:
        conds = list(br.en.conditions)
        if extra_conditions:
            conds = extra_conditions + conds
        effects = [e for e in br.en.effects()
                   if not e.startswith('$option')
                   and not e.startswith(('AddText', 'AddPara'))]
        return {
            'rule': br.id,
            'en': br.en.text,
            'zh': (br.cn.text if br.cn else '') or br.en.text,
            'conditions': conds,
            'effects': effects,
        }

    def _has_options(self, trigger: str) -> bool:
        return any(r.en.options for r in self.idx.hub_rules(trigger)
                   if not self._is_dev(r.en))

    def _provider_rules(self, needle: str) -> List[BiRule]:
        """Generic-trigger rules (PopulateOptions etc.) whose conditions
        reference the needle — the option pool for an entity dialog."""
        out = []
        for br in self.idx.rules.values():
            r = br.en
            if r.trigger not in GENERIC_TRIGGERS:
                continue
            if self._is_dev(r):
                continue
            if any(needle in c for c in r.conditions):
                out.append(br)
        return out

    def _collect_flags(self, rules: List[BiRule]):
        seen = []
        for br in rules:
            for f in br.en.flags():
                key = (f['flag'], f['negated'])
                if key not in seen:
                    seen.append(key)
        glossary = self.quest.get('flags', {})
        for flag, _negated in seen:
            if flag not in glossary and flag not in self.report['unglossed_flags']:
                self.report['unglossed_flags'].append(flag)

    # -- step expansion ----------------------------------------------------

    def _init_step(self, scene_id: str, step_id: str) -> dict:
        steps = self.scene_steps[scene_id]
        step = {
            'id': step_id,
            'kind': step_id.split(':', 1)[0],
            'texts': [],
            'options': [],
            'next': [],
            'end': False,
            'external': False,
            'menuReturn': False,
            'stageHints': [],
            'ruleIds': [],
        }
        steps[step_id] = step  # register early to break cycles
        return step

    def _add_rule_to_step(self, scene_id: str, step: dict, br: BiRule,
                          prefix_conds: List[str]):
        """Append one rule's texts/effects/options to a step being built."""
        r = br.en
        self.consumed.add(br.id)
        step['ruleIds'].append(br.id)
        if r.text:
            step['texts'].append(self._text_block(br, prefix_conds))
        for block in self._script_text_blocks(br):
            if prefix_conds:
                block['conditions'] = prefix_conds + block['conditions']
            step['texts'].append(block)
        if r.ends_conversation():
            step['end'] = True
        for i in range(len(r.options)):
            opt = self._bilingual_option(br, i)
            if opt is None:
                continue
            opt['conditions'] = list(prefix_conds) + list(r.conditions)
            opt['target'] = None  # resolved after step registration
            opt['optionRule'] = br.id
            step['options'].append(opt)
        m = _STAGE_COND_RE.match(' '.join(r.conditions))
        if m and m.group(1) not in step['stageHints']:
            step['stageHints'].append(m.group(1))
        return r

    def expand(self, scene_id: str, step_id: str, initiator: Optional[List[BiRule]],
               parent_step: Optional[str] = None,
               provider_needle: Optional[str] = None) -> dict:
        """Expand one dialog 'screen'.

        initiator: rules that run when this step triggers (None for T: steps,
        where the trigger's own rules are the initiator).
        """
        steps = self.scene_steps[scene_id]
        if step_id in steps:
            return steps[step_id]

        step = self._init_step(scene_id, step_id)
        involved: List[BiRule] = []
        visited: Set[str] = set()
        optioned_targets: List[str] = []
        auto_options: List[str] = []

        def inline(trigger: str, depth: int, prefix_conds: List[str]):
            if depth > DEPTH_LIMIT or trigger in visited:
                return
            visited.add(trigger)
            for br in self.idx.hub_rules(trigger):
                r = br.en
                if self._is_dev(r):
                    self.report['skipped_dev_rules'] += 1
                    continue
                involved.append(br)
                self._add_rule_to_step(scene_id, step, br, prefix_conds)
                for ft in r.fire_targets():
                    self._route_fire_target(ft, step, optioned_targets,
                                             visited, lambda t, pc: inline(t, depth + 1, pc),
                                             prefix_conds)
                setter = r.option_set()
                if setter and setter not in auto_options:
                    auto_options.append(setter)

        # -- initiating rules ------------------------------------------------
        if step_id.startswith('T:'):
            inline(step_id[2:], 0, [])
        else:
            # O:<optionId> response or S:<ruleId> synthetic entry
            rules = initiator if initiator is not None else []
            for br in rules:
                r = br.en
                if self._is_dev(r):
                    self.report['skipped_dev_rules'] += 1
                    continue
                involved.append(br)
                self._add_rule_to_step(scene_id, step, br, [])
                for ft in r.fire_targets():
                    self._route_fire_target(
                        ft, step, optioned_targets, visited,
                        lambda t, pc=[]: inline(t, 1, pc), [])
                setter = r.option_set()
                if setter and setter not in auto_options:
                    auto_options.append(setter)

        # -- provider rules (m: roots): merge the entity option pool -------
        if provider_needle:
            for br in self._provider_rules(provider_needle):
                r = br.en
                if self._is_dev(r):
                    continue
                involved.append(br)
                self.consumed.add(br.id)
                self.report['provider_hits'] += 1
                if r.text:
                    step['texts'].append(self._text_block(br))
                for i in range(len(r.options)):
                    opt = self._bilingual_option(br, i)
                    if opt is None:
                        continue
                    opt['conditions'] = list(r.conditions)
                    opt['target'] = None
                    opt['optionRule'] = br.id
                    step['options'].append(opt)

        # -- next links -------------------------------------------------------
        next_ids: List[str] = []
        for t in optioned_targets:
            nid = 'T:' + t
            if nid not in next_ids:
                next_ids.append(nid)
        for o in auto_options:
            oid = 'O:' + o
            if oid not in next_ids:
                next_ids.append(oid)
        step['next'] = next_ids

        # hub-loop: a response with no fire target returns to its parent pool
        if not next_ids and not step['end'] and not step['options'] \
                and parent_step is not None and parent_step != step_id:
            step['next'] = [parent_step]

        # -- resolve option targets -> response steps --------------------------
        for opt in step['options']:
            oid = 'O:' + opt['id']
            responses = self.idx.option_responses(opt['id'])
            if not self._valid_responses(responses):
                self.report['dangling_options'].append(
                    {'scene': scene_id, 'step': step_id, 'option': opt['id']})
                opt['target'] = None
            else:
                opt['target'] = oid
                if oid not in steps:
                    self.expand(scene_id, oid, responses, parent_step=step_id)

        # -- expand next screens ----------------------------------------------
        for nid in next_ids:
            if nid.startswith('T:'):
                t = nid[2:]
                if self.idx.hub_rules(t):
                    self.expand(scene_id, nid, None, parent_step=step_id)
            elif nid.startswith('O:'):
                responses = self.idx.option_responses(nid[2:])
                if self._valid_responses(responses):
                    self.expand(scene_id, nid, responses, parent_step=step_id)

        self._collect_flags(involved)
        return step

    def _route_fire_target(self, ft: str, step: dict,
                           optioned_targets: List[str], visited: Set[str],
                           inline_fn, prefix_conds: List[str]):
        """Classify a fired trigger: menu return / external / optioned hub /
        pure-text chain to inline."""
        if ft == 'DialogOptionSelected':
            return
        if ft in GENERIC_TRIGGERS:
            # e.g. FireBest PopulateOptions = "return to menu"
            step['menuReturn'] = True
            return
        if not self.idx.hub_rules(ft):
            if ft not in self.report['external_triggers']:
                self.report['external_triggers'].append(ft)
            return
        if self._has_options(ft):
            if ft not in optioned_targets:
                optioned_targets.append(ft)
        else:
            # pure text chain: inline with merged conditions
            # (inline() manages its own visited-set entry)
            if ft not in visited:
                inline_fn(ft, prefix_conds)

    def _valid_responses(self, responses: List[BiRule]) -> bool:
        return any(not self._is_dev(br.en) for br in responses)

    # -- scene building ------------------------------------------------------

    def build_scene(self, scene: dict, root_scene_map: Dict[str, str]) -> dict:
        scene_id = scene['id']
        self.scene_steps[scene_id] = {}
        entries = []
        for root in scene['roots']:
            kind, _, rest = root.partition(':')
            if kind == 'r':
                br = self.idx.rules.get(rest)
                if br is None:
                    raise KeyError(f"root rule not found: {rest}")
                step_id = 'S:' + rest
                entries.append(step_id)
                self.expand(scene_id, step_id, [br])
                self._mark_entry_conditions(scene_id, step_id, [br])
            elif kind == 'm':
                rule_id, _, needle = rest.partition(':')
                br = self.idx.rules.get(rule_id)
                if br is None:
                    raise KeyError(f"root rule not found: {rule_id}")
                step_id = 'S:' + rule_id
                entries.append(step_id)
                self.expand(scene_id, step_id, [br], provider_needle=needle)
                self._mark_entry_conditions(scene_id, step_id, [br])
            elif kind == 't':
                step_id = 'T:' + rest
                entries.append(step_id)
                self.expand(scene_id, step_id, None)
                self._mark_entry_conditions(
                    scene_id, step_id, self.idx.hub_rules(rest))
            else:
                raise ValueError(f"bad root spec: {root}")
        return {
            'id': scene_id,
            'title': scene['title'],
            'location': scene.get('location'),
            'stage': scene.get('stage'),
            'speaker': scene.get('speaker'),
            'speakerOverrides': scene.get('speakerOverrides', {}),
            'entries': entries,
            'steps': self.scene_steps[scene_id],
        }

    def _mark_entry_conditions(self, scene_id: str, step_id: str,
                               rules: List[BiRule]):
        """Record how a scene entry triggers (shown as 触发方式 in the UI)."""
        steps = self.scene_steps[scene_id]
        step = steps.get(step_id)
        if step is None:
            return
        conds: List[str] = []
        for br in rules:
            if self._is_dev(br.en):
                continue
            for c in br.en.conditions:
                if c not in conds and '$option' not in c:
                    conds.append(c)
        step['entryConditions'] = conds

    def build(self) -> dict:
        # map of root step ids -> owning scene, for cross-scene links
        root_scene_map: Dict[str, str] = {}
        for scene in self.quest['scenes']:
            for root in scene['roots']:
                kind, _, rest = root.partition(':')
                if kind == 'm':
                    rest = rest.partition(':')[0]
                sid = ('S:' + rest) if kind in ('r', 'm') else ('T:' + rest)
                root_scene_map.setdefault(sid, scene['id'])

        scenes_out = [self.build_scene(s, root_scene_map) for s in self.quest['scenes']]

        # coverage: quest-referencing rules not consumed by any scene
        needle = self.quest['gameId']
        ignored = set(self.quest.get('ignoreRules', []))
        patterns = [re.compile(p) for p in self.quest.get('ignoreRulePatterns', [])]
        for rid in self.order:
            br = self.idx.rules[rid]
            r = br.en
            if rid in ignored or any(p.match(rid) for p in patterns):
                continue
            blob = ' '.join([r.id, r.trigger, ' '.join(r.conditions),
                             '\n'.join(r.script_lines),
                             ' '.join(o.id + o.label for o in r.options)]).lower()
            if needle in blob and rid not in self.consumed and not self._is_dev(r):
                self.report['uncovered_rules'].append(rid)

        return {
            'id': self.quest['id'],
            'name': self.quest['name'],
            'summary': self.quest['summary'],
            'factionId': self.quest.get('factionId'),
            'icon': self.quest.get('icon'),
            'stages': self.quest['stages'],
            'characters': self.quest['characters'],
            'flags': self.quest.get('flags', {}),
            'scenes': scenes_out,
        }


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--en', default=os.path.expanduser('~/Games/starsector-0985a-en'))
    ap.add_argument('--cn', default=os.path.expanduser('~/Games/starsector-0985a-cn'))
    ap.add_argument('--version', default='0.98.5a')
    ap.add_argument('--out', default='public/data')
    ap.add_argument('--quests', nargs='*', default=None,
                    help='quest ids to build (default: all packages)')
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    quests_dir = os.path.join(here, 'quests')
    packages = sorted(f for f in os.listdir(quests_dir) if f.endswith('.json'))
    if args.quests:
        packages = [f"{q}.json" for q in args.quests]

    print(f"loading rules from {args.en} / {args.cn} ...")
    rules, order, merge_report = load_bilingual(
        [os.path.join(args.en, f) for f in DATA_FILES],
        [os.path.join(args.cn, f) for f in DATA_FILES])
    print(f"  merged {len(rules)} bilingual rules; "
          f"en_only={len(merge_report['en_only'])} "
          f"cn_only={len(merge_report['cn_only'])} "
          f"cond_mismatch={len(merge_report['condition_mismatch'])} "
          f"opt_mismatch={len(merge_report['option_id_mismatch'])}")
    index = RuleIndex(rules)

    out_dir = os.path.join(args.out, args.version, 'dialogues')
    os.makedirs(out_dir, exist_ok=True)

    index_out = {'version': args.version, 'quests': []}
    for pkg_file in packages:
        with open(os.path.join(quests_dir, pkg_file), encoding='utf-8') as f:
            quest = json.load(f)
        print(f"building quest: {quest['id']} ...")
        builder = QuestBuilder(index, order, quest)
        out = builder.build()
        n_steps = sum(len(s['steps']) for s in out['scenes'])
        n_texts = sum(len(st['texts']) for s in out['scenes'] for st in s['steps'].values())
        print(f"  scenes={len(out['scenes'])} steps={n_steps} texts={n_texts}")
        rep = builder.report
        print(f"  report: uncovered={len(rep['uncovered_rules'])} "
              f"dangling={len(rep['dangling_options'])} "
              f"external={len(rep['external_triggers'])} "
              f"unglossed_flags={len(rep['unglossed_flags'])} "
              f"dev_skipped={rep['skipped_dev_rules']} "
              f"providers={rep['provider_hits']}")

        # write quest json
        with open(os.path.join(out_dir, quest['id'] + '.json'), 'w',
                  encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, separators=(',', ':'))

        # write report
        rep_path = os.path.join(here, f"report_{quest['id']}.md")
        with open(rep_path, 'w', encoding='utf-8') as f:
            f.write(f"# Curation report: {quest['id']}\n\n")
            f.write(f"- scenes: {len(out['scenes'])}\n")
            f.write(f"- steps: {n_steps}\n")
            f.write(f"- text blocks: {n_texts}\n")
            f.write(f"- dev rules skipped: {rep['skipped_dev_rules']}\n")
            f.write(f"- provider rules merged: {rep['provider_hits']}\n\n")
            f.write("## Uncovered rules (reference the quest but not reached)\n\n")
            for rid in rep['uncovered_rules']:
                f.write(f"- `{rid}` (trigger: {rules[rid].en.trigger})\n")
            f.write("\n## Dangling options (no response rules)\n\n")
            for d in rep['dangling_options']:
                f.write(f"- `{d['option']}` in `{d['step']}` ({d['scene']})\n")
            f.write("\n## External triggers (fired but no rules found / Java-side)\n\n")
            for t in rep['external_triggers']:
                f.write(f"- `{t}`\n")
            f.write("\n## Flags without glossary entries\n\n")
            for fl in rep['unglossed_flags']:
                f.write(f"- `{fl}`\n")

        index_out['quests'].append({
            'id': out['id'],
            'name': out['name'],
            'summary': out['summary'],
            'factionId': out.get('factionId'),
            'icon': out.get('icon'),
            'stageCount': len(out['stages']),
            'sceneCount': len(out['scenes']),
        })
        print(f"  wrote {os.path.join(out_dir, quest['id'] + '.json')} + {rep_path}")

    with open(os.path.join(out_dir, 'index.json'), 'w', encoding='utf-8') as f:
        json.dump(index_out, f, ensure_ascii=False, indent=2)
    print(f"wrote {os.path.join(out_dir, 'index.json')}")


if __name__ == '__main__':
    main()
