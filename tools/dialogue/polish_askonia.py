#!/usr/bin/env python3
"""Polish the auto-drafted Askonia quest packages (sd7s + sdse).

Fills: quest metadata, stages+bilingual briefings (paired from the
EN/CN jars' constant pools), curated characters, formulaic flag
glossary, ignore patterns. Run after draft_quest.py.
"""

import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
QUESTS = os.path.join(HERE, 'quests')


def load(name):
    with open(os.path.join(QUESTS, name), encoding='utf-8') as f:
        return json.load(f)


def save(name, data):
    with open(os.path.join(QUESTS, name), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def merge_characters(existing, curated):
    """保留草稿收集到的人物骨架，叠加人工策展的头衔。"""
    by_id = {c['id']: c for c in existing}
    for c in curated:
        if c['id'] in by_id:
            by_id[c['id']] = c
        else:
            by_id[c['id']] = c
    return list(by_id.values())


def icon_for(mission_id):
    path = os.path.expanduser('~/Games/starsector-0985a-en/data/campaign/person_missions.csv')
    with open(path, newline='', encoding='cp1252') as f:
        for r in csv.DictReader(f):
            if r['mission id'] == mission_id:
                return r['icon']
    return None


def bi(en, zh):
    return {'en': en, 'zh': zh}


CLONES = {
    'Perseus': '珀尔修斯', 'Hercules': '赫拉克勒斯', 'Jason': '杰森',
    'Achilles': '阿喀琉斯', 'Hector': '赫克托耳', 'Leonidas': '列奥尼达',
    'Pericles': '伯里克利',
}
CLONE_NICK = {
    'Perseus': "'Saturnian'", 'Hercules': "'Cyrino'", 'Jason': "'Korin'",
    'Achilles': "'Kalian'", 'Hector': "'Palatin'", 'Leonidas': "'Esculus'",
    'Pericles': "'Aventine'",
}


def formulaic_flags(prefix):
    """Generate glossary entries for the formulaic flag families."""
    gloss = {
        f'${prefix}_inProgress': bi('Mission in progress', '任务进行中'),
        f'${prefix}_missionCompleted': bi('Mission completed', '任务已完成'),
        f'${prefix}_missionComplete': bi('Mission completed', '任务已完成'),
        f'${prefix}_stage': bi('Mission stage variable', '任务阶段变量'),
    }
    for name, zh in CLONES.items():
        for stem, en_tpl, zh_tpl in (
            ('found', 'Location of {n} confirmed', '已确认 {nz} 的下落'),
        ):
            gloss[f'${prefix}_{stem}{name}'] = bi(en_tpl.format(n=name), zh_tpl.format(nz=zh))
    for who in ('Gargoyle', 'Arroyo', 'Inesis', 'Siyavong', 'OrcusRao', 'OwnAI'):
        name = {'OrcusRao': 'Orcus Rao', 'OwnAI': 'your own AI'}.get(who, who)
        gloss[f'${prefix}_decryptVia{who}'] = bi(
            f'Files decrypted via {name}', f'已通过 {name} 解密文件')
    return gloss


# ---------------------------------------------------------------- Seven Sons

sd7s = load('the_seven_sons.json')
sd7s['name'] = bi('The Seven Sons', '七子')
sd7s['factionId'] = 'sindrian_diktat'
sd7s['icon'] = icon_for('sd7s')
sd7s['summary'] = bi(
    "With Macario's files in hand, find a way to decrypt the ANDRADA "
    "dossier, then hunt down the seven clone-sons of Supreme Executor "
    "Philip Andrada - each a potential heir to the Sindrian Diktat.",
    '带着 Macario 的文件，设法解密 ANDRADA 档案，再找出最高元首 Philip Andrada '
    '的七名克隆子嗣——每一个都是辛达强权王座的潜在继承人。')

sd7s['stages'] = [
    {'id': 'CRACK_FILES', 'flag': '$sd7s_decryptedAndradaFiles',
     'briefing': bi('Find a way to decrypt the ANDRADA files.', '设法解密 ANDRADA 文件。')},
    {'id': 'TALK_GARGOYLE', 'flag': '$sd7s_decryptViaGargoyle',
     'briefing': bi('Take the files to Gargoyle and convince the hacker to decrypt them.',
                    '把文件带给 Gargoyle，说服这名黑客将其解密。')},
    {'id': 'TALK_ORCUS', 'flag': '$sd7s_decryptViaOrcusRao',
     'briefing': bi('Take the files to Orcus Rao.', '将文件交给 Orcus Rao。')},
    {'id': 'TALK_ARROYO', 'flag': '$sd7s_decryptViaArroyo',
     'briefing': bi("Take the files to Rayan Arroyo. He'll know how to turn this situation toward his advantage.",
                    '将文件交给 Rayan Arroyo。他自然知道如何把这场乱局变成自己的进项。')},
    {'id': 'TALK_INESIS', 'flag': '$sd7s_decryptViaInesis',
     'briefing': bi('Take the files to Faro Inesis to see if you can use Tri-Tachyon black-site resources to decrypt them.',
                    '将文件交给 Faro Inesis，看能否借助速子科技的黑色站点资源将其解密。')},
    {'id': 'TALK_SIYAVONG', 'flag': '$sd7s_decryptViaSiyavong',
     'briefing': bi('Take the files to Special Agent Finlay Siyavong of Fleet Intelligence to see if he can help.',
                    '将这些文件交给舰队情报部的特工 Finlay Siyavong，看看他是否愿意帮你解密。')},
    {'id': 'TALK_HORUS_YARIBAY', 'flag': '$sd7s_stage',
     'briefing': bi('Take the files to Horus Yaribay, on Kazeron.', '将文件交给 Kazeron 上的 Horus Yaribay。')},
    {'id': 'TALK_REYNARD_HANNAN', 'flag': '$sd7s_stage',
     'briefing': bi('Take the files to Reynard Hannan, on Kazeron.', '将文件交给 Kazeron 上的 Reynard Hannan。')},
    {'id': 'TALK_TO_AI', 'flag': '$sd7s_decryptViaOwnAI',
     'briefing': bi("You've decided to use your alpha-core AI administrator's abilities to decrypt the files.",
                    '你决定动用你的 Alpha 核心 AI 管理员的能力来解密这些文件。')},
    {'id': 'FIND_THEM', 'flag': '$sd7s_findAchilles',
     'briefing': bi('Find the seven clone-sons of Philip Andrada.', '找到 Philip Andrada 的七名克隆子嗣。')},
    {'id': 'COMPLETED', 'flag': '$sd7s_missionCompleted',
     'briefing': bi('Mission complete.', '任务完成。')},
]

sd7s['characters'] = merge_characters(sd7s['characters'], [    {'id': 'macario', 'name': bi('Dolos Macario', 'Dolos Macario'),
     'title': bi("Chief High Inspector, the 'Spider of Sindria'", "最高检察长，'辛德里亚之蛛'")},
    {'id': 'rao', 'name': bi('Orcus Rao', 'Orcus Rao'),
     'title': bi('Hegemony intelligence officer, Ragnar Complex (Valhalla)', '霸主情报官，Valhalla 星系 Ragnar Complex')},
    {'id': 'siyavong', 'name': bi('Finlay Siyavong', 'Finlay Siyavong'),
     'title': bi('Special Agent, Hegemony Fleet Intelligence', '霸主舰队情报部特工')},
    {'id': 'faro_inesis', 'name': bi('Faro Inesis', 'Faro Inesis'),
     'title': bi('Tri-Tachyon black-site administrator', '速子科技黑色站点主管')},
    {'id': 'arroyo', 'name': bi('Rayan Arroyo', 'Rayan Arroyo'),
     'title': bi('Free-lance fixer', '自由掮客')},
    {'id': 'horus_yaribay', 'name': bi('Horus Yaribay', 'Horus Yaribay'),
     'title': bi('Persean League official, Kazeron (Thule)', '英仙座联盟官员，Kazeron（Thule 星系）')},
    {'id': 'reynard_hannan', 'name': bi('Reynard Hannan', 'Reynard Hannan'),
     'title': bi('Persean League magnate, Kazeron (Thule)', '英仙座联盟巨贾，Kazeron（Thule 星系）')},
    {'id': 'daud', 'name': bi('Baikal Daud', 'Baikal Daud'),
     'title': bi('High Hegemon', '至高霸主')},
    {'id': 'glamor_rotanev', 'name': bi('Zunya Glamor-Rotanev', 'Zunya Glamor-Rotanev'),
     'title': bi('Tri-Tachyon Director, Eochu Bres', '速子科技主管，Eochu Bres')},
    {'id': 'gargoyle', 'name': bi('Gargoyle', 'Gargoyle'),
     'title': bi('Notorious hacker', '知名黑客')},
    {'id': 'baird', 'name': bi('Provost Baird', 'Provost Baird'),
     'title': bi('Galatia Academy Provost', 'Galatia 学院院长')},
    {'id': 'fortuna_kato', 'name': bi('Fortuna Kato', 'Fortuna Kato'),
     'title': bi('Persean aristocrat, Kato family matriarch', '英仙系贵族，Kato 家族主母')},
    {'id': 'maeus_moroz', 'name': bi('Maeus Moroz', 'Maeus Moroz'),
     'title': bi('Mercenary commander, adoptive father of Pericles', '佣兵队长，Pericles 的养父')},
    {'id': 'imoinu_kato', 'name': bi('Imoinu Kato', 'Imoinu Kato'),
     'title': bi('ARC rebel leader on Umbra', 'Umbra 的 ARC 反叛军首领')},
    {'id': 'achilles_andrada', 'name': bi("Achilles 'Kalian' Andrada", "Achilles 'Kalian' Andrada"),
     'title': bi('Clone-son of Philip Andrada', 'Philip Andrada 的克隆子嗣')},
])

sd7s['flags'] = formulaic_flags('sd7s')
sd7s['ignoreRulePatterns'] = [
    '^sdse', '^SDSE', '^PostSDSE', '^postSDSE',
    '^sdsw', '^SDSW', '^PostSDSW', '^postSDSW',
    '^sdr[A-Z]', '^SDR[A-Z]', '^PostSDR', '^postSDR',
    '^DEV', '^dev[A-Z]',
    'test', 'Test', 'TEST',
]
sd7s['ignoreRules'] = [
    'relLevelDiktatSDTU', 'relLevelDiktatSD7S', 'HyderGreetDefaultSD',
    'sdBarRaid0', 'ZGRacknowledgeDiktatB',
]
sd7s['ignoreRulePatterns'].extend(['^relLevel', '^flavorText', '^bar_desc'])
save('the_seven_sons.json', sd7s)

# ---------------------------------------------------------- Supreme Executor

sdse = load('the_supreme_executor.json')
sdse['name'] = bi('The Supreme Executor', '最高元首')
sdse['factionId'] = 'sindrian_diktat'
sdse['icon'] = icon_for('sdse')
sdse['summary'] = bi(
    "Hector and Achilles Andrada - and their backers - maneuver to "
    "declare themselves Supreme Executor of the Sindrian Diktat. Choose "
    "a side, or play them all.",
    'Hector 与 Achilles Andrada——以及他们背后的支持者——正为登上辛达强权的最高元首之位'
    '各显神通。选边站，或者，把每一方都玩弄于股掌之间。')

sdse['stages'] = [
    {'id': 'MACARIOS_PLOT', 'flag': '$sdse_missionCompleted__placeholder',
     'briefing': bi('Dolos Macario has made the first move. You must choose how to respond.',
                    'Dolos Macario 已经先出手了。你必须决定如何应对。')},
    {'id': 'TALK_TO_CONTACT', 'flag': '$sdse_talkToContact',
     'briefing': bi('Talk to your contact.', '与你的联系人谈谈。')},
    {'id': 'TALK_TO_ACHILLES', 'flag': '$sdse_talkToAchilles',
     'briefing': bi('Contact Achilles Andrada and tell him you will give him your support.',
                    '联系 Achilles Andrada，告知你将支持他。')},
    {'id': 'VISIT_RELAY', 'flag': '$sdse_visitRelay',
     'briefing': bi('Go to the comms relay in the Askonia system.', '前往 Askonia 星系的通讯中继站。')},
    {'id': 'WAIT_FOR_OPENING', 'flag': '$sdse_waitForOpening',
     'briefing': bi('Wait for one of the major players to make a move.', '等待某位主要角逐者先出手。')},
    {'id': 'HECTOR_REVEALED', 'flag': '$sdse_hectorDeclaredStageAdvance',
     'briefing': bi("Hector has declared himself Supreme Executor with the support of Macario and Caden.",
                    '在 Macario 与 Caden 的支持下，Hector 已自立为最高元首。')},
    {'id': 'HECTOR_REVEALED2', 'flag': '$sdse_hectorDeclaredStageAdvance2',
     'briefing': bi("Achilles is sure to make his own declaration soon...",
                    'Achilles 想必很快也会站出来宣布自己的主张...')},
    {'id': 'ACHILLES_REVEALED', 'flag': '$sdse_achillesDeclaredStageAdvance',
     'briefing': bi("Achilles 'Kalian' Andrada, backed by Fortuna Kato, declares himself Supreme Executor.",
                    "有 Fortuna Kato 撑腰的 Achilles 'Kalian' Andrada 宣布自己为最高元首。")},
    {'id': 'COMPLETED', 'flag': '$sdse_missionCompleted',
     'briefing': bi('Mission complete.', '任务完成。')},
]
# fix placeholder flag
sdse['stages'][0]['flag'] = '$sdse_inProgress'

sdse['characters'] = merge_characters(sdse['characters'], [
    {'id': 'macario', 'name': bi('Dolos Macario', 'Dolos Macario'),
     'title': bi("Chief High Inspector, the 'Spider of Sindria'", "最高检察长，'辛德里亚之蛛'")},
    {'id': 'rao', 'name': bi('Orcus Rao', 'Orcus Rao'),
     'title': bi('Hegemony intelligence officer', '霸主情报官')},
    {'id': 'siyavong', 'name': bi('Finlay Siyavong', 'Finlay Siyavong'),
     'title': bi('Special Agent, Hegemony Fleet Intelligence', '霸主舰队情报部特工')},
    {'id': 'faro_inesis', 'name': bi('Faro Inesis', 'Faro Inesis'),
     'title': bi('Tri-Tachyon black-site administrator', '速子科技黑色站点主管')},
    {'id': 'arroyo', 'name': bi('Rayan Arroyo', 'Rayan Arroyo'),
     'title': bi('Free-lance fixer', '自由掮客')},
    {'id': 'horus_yaribay', 'name': bi('Horus Yaribay', 'Horus Yaribay'),
     'title': bi('Persean League official, Kazeron', '英仙座联盟官员，Kazeron')},
    {'id': 'reynard_hannan', 'name': bi('Reynard Hannan', 'Reynard Hannan'),
     'title': bi('Persean League magnate, Kazeron', '英仙座联盟巨贾，Kazeron')},
    {'id': 'fortuna_kato', 'name': bi('Fortuna Kato', 'Fortuna Kato'),
     'title': bi('Persean aristocrat, backer of Achilles', '英仙系贵族，Achilles 的支持者')},
    {'id': 'imoinu_kato', 'name': bi('Imoinu Kato', 'Imoinu Kato'),
     'title': bi('ARC rebel leader on Umbra', 'Umbra 的 ARC 反叛军首领')},
    {'id': 'achilles_andrada', 'name': bi("Achilles 'Kalian' Andrada", "Achilles 'Kalian' Andrada"),
     'title': bi('Clone-son of Philip Andrada, contender for Supreme Executor', 'Philip Andrada 的克隆子嗣，最高元首之位的角逐者')},
])

sdse['flags'] = formulaic_flags('sdse')
sdse['flags'].update({
    '$sdse_proAchilles': bi('Backing Achilles', '支持 Achilles 阵营'),
    '$sdse_proHector': bi('Backing Hector', '支持 Hector 阵营'),
    '$sdse_antiMacario': bi('Working against Macario', '正在对付 Macario'),
    '$sdse_proKato': bi('Backed by the Kato family', '获得 Kato 家族支持'),
    '$sdse_backingFortuna': bi('Backed by Fortuna Kato', '获得 Fortuna Kato 支持'),
    '$sdse_talkFirstMacario': bi('Macario contacted first', '已先行联系 Macario'),
})
sdse['ignoreRulePatterns'] = [
    '^sdtu', '^SDTU', '^PostSDTU', '^postSDTU', '^postSDT',
    '^sd7s', '^SD7S', '^PostSD7S', '^postSD7S',
    '^sdsw', '^SDSW', '^PostSDSW', '^postSDSW',
    '^sdr[A-Z]', '^SDR[A-Z]',
    '^DEV', '^dev[A-Z]',
    '^relLevel', '^flavorText', '^bar_desc', 'test', 'Test', 'TEST',
]
sdse['ignoreRules'] = ['relLevelDiktatSDTU', 'relLevelDiktatSD7S', 'HyderGreetDefaultSD',
                       'sdBarRaid0', 'ZGRacknowledgeDiktatB']
save('the_supreme_executor.json', sdse)

print('polished: the_seven_sons.json, the_supreme_executor.json')
print('sd7s icon:', sd7s['icon'], '| sdse icon:', sdse['icon'])
