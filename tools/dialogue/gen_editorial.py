#!/usr/bin/env python3
"""Generate src/questEditorial.ts — the ONLY place where hand-written
quest-related text may live (frontend editorial layer).

Reads flag glossaries from the quest packages (before they are stripped
from the data layer) and combines them with aggregation labels.

Game data policy: quests/*.json & dialogues/*.json contain extracted
text only; everything hand-written lives here, in the frontend.
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
QUESTS = os.path.join(HERE, 'quests')
DEST = os.path.join(HERE, '..', '..', 'src', 'questEditorial.ts')

# 聚合包 / 无官方名任务的 wiki 标签（前端编辑层，非游戏数据）
AGGREGATIONS = {
    'the_academy_arc': {
        'name': {'en': 'The Galatia Academy Arc', 'zh': 'Galatia 学院主线'},
        'summary': {
            'en': 'The Galatia Academy storyline: tutorial aftermath, finding '
                  'Coureuse, Project Ziggurat, and At the Gates.',
            'zh': 'Galatia 学院主线：教程后续、寻找 Coureuse、Ziggurat 计划，直至群星之门。',
        },
    },
    'contact_missions': {
        'name': {'en': 'Contact Missions', 'zh': '接触任务合集'},
        'summary': {
            'en': 'The smaller jobs offered by contacts.',
            'zh': '接触人提供的中小任务合集。',
        },
    },
    'misc_stories': {
        'name': {'en': 'Miscellany', 'zh': '杂项剧情'},
        'summary': {
            'en': 'Tutorial guidance, the Historian\'s tales, and other odds and ends.',
            'zh': '新手引导、历史学家的讲述，以及其他零散剧情。',
        },
    },
    # 类常量池中无任务名，使用 wiki 标签
    'the_seven_sons': {
        'name': {'en': 'The Seven Sons', 'zh': '七子'},
        'summary': None,
    },
    'sword_of_eventide': {
        'name': {'en': 'Sword of Eventide', 'zh': '暮光之剑'},
        'summary': None,
    },
}


def ts_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def main() -> None:
    # FLAG_GLOSSARY 幂等保护：任务包已按零手写政策移除 flags 字段，
    # 若现有 questEditorial.ts 已含 FLAG_GLOSSARY 块则原样保留
    existing_glossary = None
    if os.path.exists(DEST):
        with open(DEST, encoding='utf-8') as f:
            old = f.read()
        m = re.search(
            r'export const FLAG_GLOSSARY[^=]*= \{\n(.*?)\n\};',
            old, re.DOTALL)
        if m and m.group(1).strip():
            # 包里已无 flags：保留现有非空块
            existing_glossary = m.group(0)

    glossary_blocks = []
    if existing_glossary:
        glossary_blocks.append(existing_glossary[
            existing_glossary.index('{') + 1:existing_glossary.rindex('}')].strip())
    for fn in sorted(os.listdir(QUESTS)):
        if not fn.endswith('.json'):
            continue
        with open(os.path.join(QUESTS, fn), encoding='utf-8') as f:
            pkg = json.load(f)
        flags = pkg.get('flags', {})
        if not flags:
            continue
        lines = [f"  '{pkg['id']}': {{"]
        for flag, gloss in flags.items():
            lines.append(
                f"    {ts_str(flag)}: {{ en: {ts_str(gloss['en'])}, "
                f"zh: {ts_str(gloss['zh'])} }},"
            )
        lines.append('  },')
        glossary_blocks.append('\n'.join(lines))

    meta_lines = []
    for qid, m in AGGREGATIONS.items():
        name = m['name']
        summary = m.get('summary')
        meta_lines.append(
            f"  '{qid}': {{\n"
            f"    name: {{ en: {ts_str(name['en'])}, zh: {ts_str(name['zh'])} }},\n"
            + (f"    summary: {{ en: {ts_str(summary['en'])}, zh: {ts_str(summary['zh'])} }},\n"
               if summary else '')
            + "  },"
        )

    out = f"""// ============================================================
// wiki 编辑层 —— 手写文本允许区（前端 UI 文本，非游戏数据）
//
// 政策：任务包/对话数据里的游戏文本一律来自提取；
// 聚合包名、无官方名标签、flag 条件注解等手写内容只住这里。
// 由 tools/dialogue/gen_editorial.py 生成/维护。
/* eslint-disable quotes */
// ============================================================

export interface Bilingual {{
  en: string;
  zh: string;
}}

/** 聚合包与无官方名任务的 wiki 标签 */
export const QUEST_META: Record<string, {{ name: Bilingual; summary?: Bilingual }}> = {{
{chr(10).join(meta_lines)}
}};

/** flag 条件注解（按任务包组织） */
export const FLAG_GLOSSARY: Record<string, Record<string, Bilingual>> = {{
{chr(10).join(glossary_blocks)}
}};

export function questMeta(id: string) {{
  return QUEST_META[id];
}}

export function flagGlossary(questId: string, flag: string): Bilingual | undefined {{
  return FLAG_GLOSSARY[questId]?.[flag];
}}
"""
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as f:
        f.write(out)
    print(f'wrote {os.path.relpath(DEST)}: {len(AGGREGATIONS)} meta entries, '
          f'{len(glossary_blocks)} glossaries')


if __name__ == '__main__':
    main()
