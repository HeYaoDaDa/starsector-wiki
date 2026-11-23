// ============================================================
// wiki 编辑层 —— 手写文本允许区（前端 UI 文本，非游戏数据）
//
// 政策：任务包/对话数据里的游戏文本一律来自提取；
// 聚合包名、无官方名标签、flag 条件注解等手写内容只住这里。
// 由 tools/dialogue/gen_editorial.py 生成/维护。
/* eslint-disable quotes */
// ============================================================

export interface Bilingual {
  en: string;
  zh: string;
}

/** 聚合包与无官方名任务的 wiki 标签 */
export const QUEST_META: Record<string, { name: Bilingual; summary?: Bilingual }> = {
  'the_academy_arc': {
    name: { en: "The Galatia Academy Arc", zh: "Galatia 学院主线" },
    summary: { en: "The Galatia Academy storyline: tutorial aftermath, finding Coureuse, Project Ziggurat, and At the Gates.", zh: "Galatia 学院主线：教程后续、寻找 Coureuse、Ziggurat 计划，直至群星之门。" },
  },
  'contact_missions': {
    name: { en: "Contact Missions", zh: "接触任务合集" },
    summary: { en: "The smaller jobs offered by contacts.", zh: "接触人提供的中小任务合集。" },
  },
  'misc_stories': {
    name: { en: "Miscellany", zh: "杂项剧情" },
    summary: { en: "Tutorial guidance, the Historian's tales, and other odds and ends.", zh: "新手引导、历史学家的讲述，以及其他零散剧情。" },
  },
  'the_seven_sons': {
    name: { en: "The Seven Sons", zh: "七子" },
  },
  'sword_of_eventide': {
    name: { en: "Sword of Eventide", zh: "暮光之剑" },
  },
};

/** flag 条件注解（按任务包组织） */
export const FLAG_GLOSSARY: Record<string, Record<string, Bilingual>> = {
'the_usurpers': {
    "$global.sdtu_ramDidProposal": { en: "Ram made his proposal", zh: "Ram 已提出提议" },
    "$global.sdtu_inProgress": { en: "Mission in progress", zh: "任务进行中" },
    "$global.sdtu_missionCompleted": { en: "Mission completed", zh: "任务已完成" },
    "$global.sdtu_meetRamOnVolturn": { en: "Met Ram on Volturn", zh: "已在 Volturn 见过 Ram" },
    "$global.sdtu_interceptFleet": { en: "Intercept stage unlocked (patrol fleet spawned)", zh: "拦截阶段已开始（巡逻舰队已生成）" },
    "$global.sdtu_meetHyder": { en: "Hyder meeting unlocked", zh: "Hyder 会谈已解锁" },
    "$global.sdtu_didHyderMeeting": { en: "Done talking with Hyder", zh: "已完成与 Hyder 的会谈" },
    "$global.sdtu_foughtDiktatPatrol": { en: "Fought the Diktat patrol", zh: "已与巡逻舰队交战" },
    "$global.sdtu_promisedToHelpPatrolLeader": { en: "Promised to help the patrol leader", zh: "已承诺帮助巡逻队长" },
    "$global.sdtu_gotPatrolCrewToMutiny": { en: "Got the patrol crew to mutiny", zh: "已使巡逻队船员哗变" },
    "$global.sdtu_didPatrolTraitorTransfer": { en: "Patrol officer handed over for real", zh: "巡逻队军官已被实际移交" },
    "$global.sdtu_extractAgent": { en: "Extract-agent stage unlocked", zh: "解救特工阶段已解锁" },
    "$global.sdtu_meetCaden": { en: "Caden meeting unlocked", zh: "Caden 会谈已解锁" },
    "$global.sdtu_didCadenMeeting": { en: "Done talking with Caden", zh: "已完成与 Caden 的会谈" },
    "$global.sdtu_enragedCaden": { en: "Caden enraged at you", zh: "Caden 已被激怒" },
    "$global.sdtu_toldCadenPlayerBacksHim": { en: "Told Caden you back him", zh: "已告知 Caden 你支持他" },
    "$global.sdtu_deliverNews": { en: "Deliver-news stage unlocked", zh: "传讯阶段已解锁" },
    "$global.sdtu_emergencyIntercept": { en: "Emergency intercept happened", zh: "应急拦截已发生" },
    "$global.sdtu_completed": { en: "Mission completed", zh: "任务已完成" },
    "$global.didSDBarRaid": { en: "Experienced the 'Sindrian Diktat bar raid' event", zh: "已触发'辛达强权酒吧袭击'事件" },
    "$global.SDTU_barRaidDelay": { en: "Bar-raid event cooldown active", zh: "酒吧袭击事件冷却中" },
    "$entity.sdtu_interceptFleet": { en: "The 'traitor' patrol fleet (transponder matches Macario's file)", zh: "'叛国'巡逻舰队（应答器信号与 Macario 的文件相符）" },
    "$sdtu_merc": { en: "The mercenary fleet hired by Macario", zh: "Macario 雇佣的佣兵舰队" },
    "$sdtuAgentDebris": { en: "The debris field where the agent died", zh: "特工遇害处的残骸场" },
    "$sdtu_antisFleet": { en: "ARC raider fleet", zh: "ARC 掠夺者舰队" },
    "$sdtu_antisRevengeFleet": { en: "ARC revenge fleet", zh: "ARC 复仇舰队" },
    "$global.sdtu_umbraAgentCoop": { en: "The Umbra agent agreed to cooperate", zh: "Umbra 特工已同意合作" },
    "$global.sdtu_resolvedARCagent": { en: "ARC agent matter resolved", zh: "ARC 特工事件已了结" },
    "$global.sdtu_raidedUmbra": { en: "Raided Umbra for the agent", zh: "已为特工袭击过 Umbra" },
    "$global.sdtu_hintedRaoInvolvement": { en: "Heard Rao's name in connection with this", zh: "听闻此事与 Rao 有关" },
    "$liedAboutSDTUagent": { en: "Lied about the SDTU agent", zh: "曾就辛达强权特工一事撒谎" },
    "$madeArrestClaim": { en: "Made the arrest claim", zh: "已宣称执行逮捕" },
    "$sentWarrant": { en: "Sent the (forged) warrant", zh: "已出示（伪造的）逮捕令" },
    "$trust": { en: "Macario's trust in you", zh: "Macario 对你的信任度" },
    "$askedWhatPlan": { en: "Asked: what plan?", zh: "已问过：什么计划？" },
    "$askedForMe": { en: "Asked: what's in it for me?", zh: "已问过：我能得到什么？" },
    "$askedWhyWant": { en: "Asked: why trust me?", zh: "已问过：为什么信任我？" },
    "$askedGazeOut": { en: "Asked about 'turning gaze outward'", zh: "已问过'向外看'的含义" },
    "$askedAndradaKnow": { en: "Asked if Andrada knows", zh: "已问过 Andrada 是否知情" },
    "$askedYouTraitor": { en: "Called Macario the traitor", zh: "已反指 Macario 才是叛国者" },
    "$askedAmbition": { en: "Asked about Macario's ambition", zh: "已试探 Macario 的野心" },
    "$saidAnswerServe": { en: "Said you live to serve the Diktat", zh: "已表态愿为辛达强权效力" },
    "$saidAnswerEarly": { en: "Gave an early answer to Macario", zh: "已提前给出了回答" },
  },
  'the_seven_sons': {
    "$sd7s_inProgress": { en: "Mission in progress", zh: "任务进行中" },
    "$sd7s_missionCompleted": { en: "Mission completed", zh: "任务已完成" },
    "$sd7s_missionComplete": { en: "Mission completed", zh: "任务已完成" },
    "$sd7s_stage": { en: "Mission stage variable", zh: "任务阶段变量" },
    "$sd7s_foundPerseus": { en: "Location of Perseus confirmed", zh: "已确认 珀尔修斯 的下落" },
    "$sd7s_foundHercules": { en: "Location of Hercules confirmed", zh: "已确认 赫拉克勒斯 的下落" },
    "$sd7s_foundJason": { en: "Location of Jason confirmed", zh: "已确认 杰森 的下落" },
    "$sd7s_foundAchilles": { en: "Location of Achilles confirmed", zh: "已确认 阿喀琉斯 的下落" },
    "$sd7s_foundHector": { en: "Location of Hector confirmed", zh: "已确认 赫克托耳 的下落" },
    "$sd7s_foundLeonidas": { en: "Location of Leonidas confirmed", zh: "已确认 列奥尼达 的下落" },
    "$sd7s_foundPericles": { en: "Location of Pericles confirmed", zh: "已确认 伯里克利 的下落" },
    "$sd7s_decryptViaGargoyle": { en: "Files decrypted via Gargoyle", zh: "已通过 Gargoyle 解密文件" },
    "$sd7s_decryptViaArroyo": { en: "Files decrypted via Arroyo", zh: "已通过 Arroyo 解密文件" },
    "$sd7s_decryptViaInesis": { en: "Files decrypted via Inesis", zh: "已通过 Inesis 解密文件" },
    "$sd7s_decryptViaSiyavong": { en: "Files decrypted via Siyavong", zh: "已通过 Siyavong 解密文件" },
    "$sd7s_decryptViaOrcusRao": { en: "Files decrypted via Orcus Rao", zh: "已通过 Orcus Rao 解密文件" },
    "$sd7s_decryptViaOwnAI": { en: "Files decrypted via your own AI", zh: "已通过 your own AI 解密文件" },
  },
  'the_supreme_executor': {
    "$sdse_inProgress": { en: "Mission in progress", zh: "任务进行中" },
    "$sdse_missionCompleted": { en: "Mission completed", zh: "任务已完成" },
    "$sdse_missionComplete": { en: "Mission completed", zh: "任务已完成" },
    "$sdse_stage": { en: "Mission stage variable", zh: "任务阶段变量" },
    "$sdse_foundPerseus": { en: "Location of Perseus confirmed", zh: "已确认 珀尔修斯 的下落" },
    "$sdse_foundHercules": { en: "Location of Hercules confirmed", zh: "已确认 赫拉克勒斯 的下落" },
    "$sdse_foundJason": { en: "Location of Jason confirmed", zh: "已确认 杰森 的下落" },
    "$sdse_foundAchilles": { en: "Location of Achilles confirmed", zh: "已确认 阿喀琉斯 的下落" },
    "$sdse_foundHector": { en: "Location of Hector confirmed", zh: "已确认 赫克托耳 的下落" },
    "$sdse_foundLeonidas": { en: "Location of Leonidas confirmed", zh: "已确认 列奥尼达 的下落" },
    "$sdse_foundPericles": { en: "Location of Pericles confirmed", zh: "已确认 伯里克利 的下落" },
    "$sdse_decryptViaGargoyle": { en: "Files decrypted via Gargoyle", zh: "已通过 Gargoyle 解密文件" },
    "$sdse_decryptViaArroyo": { en: "Files decrypted via Arroyo", zh: "已通过 Arroyo 解密文件" },
    "$sdse_decryptViaInesis": { en: "Files decrypted via Inesis", zh: "已通过 Inesis 解密文件" },
    "$sdse_decryptViaSiyavong": { en: "Files decrypted via Siyavong", zh: "已通过 Siyavong 解密文件" },
    "$sdse_decryptViaOrcusRao": { en: "Files decrypted via Orcus Rao", zh: "已通过 Orcus Rao 解密文件" },
    "$sdse_decryptViaOwnAI": { en: "Files decrypted via your own AI", zh: "已通过 your own AI 解密文件" },
    "$sdse_proAchilles": { en: "Backing Achilles", zh: "支持 Achilles 阵营" },
    "$sdse_proHector": { en: "Backing Hector", zh: "支持 Hector 阵营" },
    "$sdse_antiMacario": { en: "Working against Macario", zh: "正在对付 Macario" },
    "$sdse_proKato": { en: "Backed by the Kato family", zh: "获得 Kato 家族支持" },
    "$sdse_backingFortuna": { en: "Backed by Fortuna Kato", zh: "获得 Fortuna Kato 支持" },
    "$sdse_talkFirstMacario": { en: "Macario contacted first", zh: "已先行联系 Macario" },
  },
};

export function questMeta(id: string) {
  return QUEST_META[id];
}

export function flagGlossary(questId: string, flag: string): Bilingual | undefined {
  return FLAG_GLOSSARY[questId]?.[flag];
}
