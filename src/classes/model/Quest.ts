/**
 * 任务对话数据模型
 *
 * 由 tools/dialogue/build_quests.py 生成:
 *   public/data/{version}/dialogues/index.json   任务索引
 *   public/data/{version}/dialogues/{quest}.json 单个任务对话树
 */

export interface Bilingual {
  en: string;
  zh: string;
}

export interface QuestStage {
  id: string;
  flag: string;
  briefing: Bilingual;
}

export interface QuestCharacter {
  id: string;
  name: Bilingual;
  title: Bilingual;
}

export interface QuestFlagGlossary {
  /** flag -> {en, zh} 说明 */
  [flag: string]: Bilingual;
}

/** 一段对话文本（来自一条规则） */
export interface DialogueText {
  rule: string;
  en: string;
  zh: string;
  conditions: string[];
  effects: string[];
  small?: boolean;
}

/** 一个玩家选项 */
export interface DialogueOption {
  id: string;
  num: string | null;
  en: string;
  zh: string;
  conditions: string[];
  /** 响应步骤 id (O:xxx)，无响应则为 null */
  target: string | null;
  optionRule: string;
}

/** 一个对话"屏"：一次触发/选择所显示的全部内容 */
export interface DialogueStep {
  id: string;
  /** S: 入口 / T: 触发器屏 / O: 选项响应 */
  kind: 'S' | 'T' | 'O';
  texts: DialogueText[];
  options: DialogueOption[];
  /** 自动继续的目标步骤 */
  next: string[];
  end: boolean;
  external: boolean;
  menuReturn: boolean;
  stageHints: string[];
  ruleIds: string[];
  /** 场景入口步骤的触发条件（如何遇到该场景） */
  entryConditions?: string[];
}

export interface QuestScene {
  id: string;
  title: Bilingual;
  location: Bilingual | null;
  /** 所属任务阶段 id，null 表示阶段外（如任务开始前） */
  stage: string | null;
  speaker: string | null;
  speakerOverrides: Record<string, string>;
  /** 入口步骤 id 列表 */
  entries: string[];
  steps: Record<string, DialogueStep>;
}

export interface Quest {
  id: string;
  name: Bilingual;
  summary: Bilingual;
  factionId: string | null;
  icon: string | null;
  stages: QuestStage[];
  characters: QuestCharacter[];
  flags: QuestFlagGlossary;
  scenes: QuestScene[];
}

export interface QuestIndexEntry {
  id: string;
  name: Bilingual;
  summary: Bilingual;
  factionId: string | null;
  icon: string | null;
  stageCount: number;
  sceneCount: number;
}

export interface QuestIndex {
  version: string;
  quests: QuestIndexEntry[];
}
