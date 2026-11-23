#!/usr/bin/env python3
"""Shared library for parsing Starsector rules.csv dialogue files.

Handles:
- CSV parsing with multi-line quoted fields (cp1252 / utf-8 auto-detect)
- Bilingual merge (EN + CN) by rule id
- Options cell parsing: "[num:]optionTriggerId:label" entries
- Script command parsing (FireAll/FireBest targets, flag assignments, ...)
- Condition splitting and flag extraction
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

GENERIC_TRIGGERS = {
    # triggers shared by the whole game, not quest-specific hubs
    'PopulateOptions', 'DialogOptionSelected', 'PickGreeting', 'OpenCommLink',
    'OpenInteractionDialog', 'BeginFleetEncounter', 'MarketPostDock',
    'MarketPostOpen', 'MarketOpened', 'RetireOptions', 'NewGameOptionSelected',
}

_FIRE_RE = re.compile(r'^(FireAll|FireBest)\s+(.+)$')
_OPTION_COND_RE = re.compile(r'^\$option\s*==\s*(\S+)$')
_OPTION_SET_RE = re.compile(r'^\$option\s*=\s*(\S+?)(?:\s+\d+)?$')
_FLAG_RE = re.compile(r'(!?)\$([A-Za-z_][A-Za-z0-9_.]*)')
_SCORE_RE = re.compile(r'\bscore\s*:\s*-?\d+\b')
_NUM_PREFIX_RE = re.compile(r'^(\d+)\s*:\s*')


@dataclass
class Option:
    """One dialog option entry from an options cell."""
    num: Optional[str] = None       # hotkey number, if given
    id: str = ''                    # option trigger id (becomes $option)
    label: str = ''                 # display text


@dataclass
class Rule:
    """One row of rules.csv (comment / blank rows dropped)."""
    id: str = ''
    trigger: str = ''
    conditions: List[str] = field(default_factory=list)
    score: Optional[int] = None
    script_lines: List[str] = field(default_factory=list)
    text: str = ''
    options: List[Option] = field(default_factory=list)
    notes: str = ''

    # --- derived helpers -------------------------------------------------
    def fire_targets(self) -> List[str]:
        """FireAll/FireBest trigger targets, in order."""
        out = []
        for line in self.script_lines:
            m = _FIRE_RE.match(line.strip())
            if m:
                target = m.group(2).split()[0]
                if target not in ('DialogOptionSelected',):
                    out.append(target)
        return out

    def option_set(self) -> Optional[str]:
        """If this rule auto-selects an option ($option = X), return X."""
        for line in self.script_lines:
            m = _OPTION_SET_RE.match(line.strip())
            if m:
                return m.group(1)
        return None

    def option_handled(self) -> Optional[str]:
        """If this rule responds to $option == X, return X."""
        for c in self.conditions:
            m = _OPTION_COND_RE.match(c.strip())
            if m:
                return m.group(1)
        return None

    def flags(self) -> List[Dict[str, object]]:
        """Flags referenced in conditions: [{flag, negated, raw}]"""
        out = []
        seen = set()
        for c in self.conditions:
            for m in _FLAG_RE.finditer(c):
                negated = m.group(1) == '!'
                flag = '$' + m.group(2)
                key = (flag, negated)
                if key not in seen:
                    seen.add(key)
                    out.append({'flag': flag, 'negated': negated, 'raw': c.strip()})
        return out

    def effects(self) -> List[str]:
        """Human-readable subset of script effects (assignments, credits, rep, end)."""
        out = []
        for line in self.script_lines:
            s = line.strip()
            if not s:
                continue
            if s.startswith(('FireAll', 'FireBest', 'Call ', 'Show', 'Set', 'AddText',
                             'AddPara', 'Highlight', 'SetTextHighlights', 'playSound',
                             'SetTooltip', 'SetOptionColor', 'SetEnabled', 'SetShortcut',
                             'BeginConversation', 'EndConversation', 'RemoveOption')):
                continue
            out.append(s)
        return out

    def ends_conversation(self) -> bool:
        return any(l.strip().startswith('EndConversation') for l in self.script_lines)


# --- CSV loading -----------------------------------------------------------

def load_rules_csv(path: str) -> List[Rule]:
    """Parse a rules.csv file. Tries utf-8 then cp1252."""
    last_err: Exception = NotImplementedError()
    for enc in ('utf-8', 'cp1252'):
        try:
            with open(path, newline='', encoding=enc) as f:
                return _parse_rows(f)
        except UnicodeDecodeError as e:
            last_err = e
    raise last_err


def _parse_rows(f) -> List[Rule]:
    rules: List[Rule] = []
    for row in csv.DictReader(f):
        rid = (row.get('id') or '').strip()
        if not rid or rid.startswith('#'):
            continue
        cond_cell = (row.get('conditions') or '')
        script_cell = (row.get('script') or '')
        text_cell = (row.get('text') or '')
        opt_cell = (row.get('options') or '')
        notes = (row.get('notes') or '').strip()

        conditions, score = _split_conditions(cond_cell)
        rules.append(Rule(
            id=rid,
            trigger=(row.get('trigger') or '').strip(),
            conditions=conditions,
            score=score,
            script_lines=[l.strip() for l in script_cell.split('\n') if l.strip()],
            text=_clean_text(text_cell),
            options=parse_options_cell(opt_cell),
            notes=notes,
        ))
    return rules


def _split_conditions(cell: str):
    """Split condition cell on ';' and newlines; strip score annotations."""
    parts = [p.strip() for p in re.split(r'[;\n]+', cell) if p.strip()]
    score = None
    cleaned = []
    for p in parts:
        if p.startswith('#'):
            # disabled / commented condition, e.g. "#!$global.sd7s_inProgress"
            continue
        if p.startswith('Call '):
            # script invocation used as a condition hook, not a real condition
            continue
        m = re.search(r'\bscore\s*:\s*(-?\d+)\s*$', p)
        if m:
            score = int(m.group(1))
            p = p[:m.start()].strip()
        if p:
            cleaned.append(p)
    return cleaned, score


def _clean_text(text: str) -> str:
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # strip trailing whitespace per line, collapse >2 blank lines
    lines = [l.rstrip() for l in text.split('\n')]
    out = []
    blank = 0
    for l in lines:
        if l == '':
            blank += 1
            if blank > 1:
                continue
        else:
            blank = 0
        out.append(l)
    return '\n'.join(out).strip()


def parse_options_cell(cell: str) -> List[Option]:
    """Parse options cell: newline-separated '[num:]triggerId:label' entries.

    Labels may be quoted; continuation lines are folded back into the label.
    """
    if not cell.strip():
        return []
    out: List[Option] = []
    for raw in cell.replace('\r\n', '\n').split('\n'):
        line = raw.strip()
        if not line:
            continue
        num = None
        m = _NUM_PREFIX_RE.match(line)
        if m:
            num = m.group(1)
            line = line[m.end():]
        if line.startswith('#'):
            # 注释/禁用行（如 "#cutCommLink:..."）——不折叠进上一条
            continue
        # split trigger id from label at first ':'
        if ':' not in line:
            # continuation of previous label
            if out:
                out[-1].label += '\n' + line
            continue
        oid, label = line.split(':', 1)
        oid = oid.strip()
        label = label.strip()
        if label.startswith('"'):
            # quoted label, possibly with a trailing annotation outside the
            # quotes, e.g.  opt:"Say the thing." (lie)
            end = label.rfind('"')
            if end > 0:
                rest = label[end + 1:].strip()
                label = label[1:end] + ((' ' + rest) if rest else '')
        if not oid:
            continue
        # a label that itself contains ':' but no valid id part → continuation
        if not re.match(r'^[A-Za-z0-9_$.]+$', oid):
            if out:
                out[-1].label += '\n' + line
            continue
        out.append(Option(num=num, id=oid, label=label))
    return out


# --- bilingual merge --------------------------------------------------------

@dataclass
class BiRule:
    """EN + CN pair of the same rule id."""
    en: Rule
    cn: Optional[Rule] = None

    @property
    def id(self) -> str:
        return self.en.id


def load_bilingual(en_paths: List[str], cn_paths: List[str]):
    """Load rules from several EN files and matching CN files, merge by id.

    Returns (rules: Dict[str, BiRule], order: List[str], report: dict)
    """
    en_rules: Dict[str, Rule] = {}
    order: List[str] = []
    for p in en_paths:
        for r in load_rules_csv(p):
            if r.id in en_rules:
                continue  # first file wins
            en_rules[r.id] = r
            order.append(r.id)

    cn_rules: Dict[str, Rule] = {}
    for p in cn_paths:
        for r in load_rules_csv(p):
            cn_rules.setdefault(r.id, r)

    rules: Dict[str, BiRule] = {}
    report = {
        'en_only': [],
        'cn_only': sorted(set(cn_rules) - set(en_rules)),
        'condition_mismatch': [],
        'option_id_mismatch': [],
    }
    for rid in order:
        en = en_rules[rid]
        cn = cn_rules.get(rid)
        if cn is None:
            report['en_only'].append(rid)
        else:
            if _norm_conds(en.conditions) != _norm_conds(cn.conditions):
                report['condition_mismatch'].append(rid)
            en_ids = [o.id for o in en.options]
            cn_ids = [o.id for o in cn.options]
            if en_ids != cn_ids:
                report['option_id_mismatch'].append(rid)
        rules[rid] = BiRule(en=en, cn=cn)
    return rules, order, report


def _norm_conds(conds: List[str]) -> List[str]:
    return sorted(' '.join(c.split()) for c in conds)


# --- indexes ---------------------------------------------------------------

class RuleIndex:
    """Indexes over a bilingual rule set for graph traversal."""

    def __init__(self, rules: Dict[str, BiRule]):
        self.rules = rules
        self.by_trigger: Dict[str, List[BiRule]] = {}
        self.by_option: Dict[str, List[BiRule]] = {}
        self.option_setters: Dict[str, List[BiRule]] = {}
        for br in rules.values():
            t = br.en.trigger
            if t:
                self.by_trigger.setdefault(t, []).append(br)
            opt = br.en.option_handled()
            if opt:
                self.by_option.setdefault(opt, []).append(br)
            setter = br.en.option_set()
            if setter:
                self.option_setters.setdefault(setter, []).append(br)

    def hub_rules(self, trigger: str) -> List[BiRule]:
        """Rules that hang off a custom trigger hub (in file order)."""
        return self.by_trigger.get(trigger, [])

    def option_responses(self, option_id: str) -> List[BiRule]:
        return self.by_option.get(option_id, [])
