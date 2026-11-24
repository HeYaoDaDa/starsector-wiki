# 任务对话导出管线（tools/dialogue）

把 Starsector 的 `rules.csv` 对话规则图整理为 wiki 前端可浏览的**任务对话树**。

## 背景

Starsector 的对话不是线性剧本，而是一张**规则图**：

- `data/campaign/rules.csv`（约 1.1 万条规则）+ `data/campaign/rules/askoniaCrisis2.csv`
- 每条规则：`id, trigger, conditions, script, text, options, notes`
- 对话按 trigger 挂成"选项池"（hub），玩家点选项 → `DialogOptionSelected` 规则给出文本与效果 → `FireAll/FireBest` 跳到下一个 hub
- 任务阶段藏在条件里的 `$global.*` / `$sdtu_stage` 标志中
- 任务阶段结构在 Java 类里（`starfarer.api.jar`，未混淆，直接读常量池即可，无需反编译）

中英文两份安装的规则**按规则 ID 完全对齐**，可逐条双语对照。

## 组成

```
tools/dialogue/
├── lib_rules.py            # rules.csv 解析 / 双语合并 / 索引
├── extract_java.py         # 从 starfarer.api.jar 提取任务阶段与简报
├── build_quests.py         # 主构建器（CLI）
├── quests/
│   └── the_usurpers.json   # 任务包（人工策展层）
└── report_<quest>.md       # 构建报告（自动生成，见下）
```

## 流程

```bash
# 全部任务包（默认读 ~/Games/starsector-0985a-{en,cn}）
python3 tools/dialogue/build_quests.py

# 指定游戏目录 / 版本 / 单个任务
python3 tools/dialogue/build_quests.py \
    --en ~/Games/starsector-0985a-en \
    --cn ~/Games/starsector-0985a-cn \
    --version 0.98.5a \
    --quests the_usurpers
```

输出：

- `public/data/{version}/dialogues/{quest}.json` — 前端消费的对话树（双语合并，与 locale 无关）
- `public/data/{version}/dialogues/index.json` — 任务索引
- `tools/dialogue/report_{quest}.md` — 策展报告

### 提取 Java 任务数据（一次性参考）

```bash
python3 tools/dialogue/extract_java.py ~/Games/starsector-0985a-en askonia.TheUsurpers
```

输出 Stage 枚举、阶段简报原文、相关 flag，用于编写任务包的 `stages` 部分。

## 任务包格式（quests/*.json）

```jsonc
{
  "id": "the_usurpers",            // 前端路由与文件名
  "gameId": "sdtu",                // 规则匹配用的游戏内部 id
  "name": { "en": "...", "zh": "..." },
  "summary": { "en": "...", "zh": "..." },
  "factionId": "sindrian_diktat",
  "stages": [ { "id": "MEET_RAM", "flag": "$sdtu_meetRamOnVolturn", "briefing": {...} } ],
  "characters": [ { "id": "macario", "name": {...}, "title": {...} } ],
  "flags": { "$global.sdtu_meetHyder": { "en": "...", "zh": "已与 Hyder 会谈" } },  // 条件术语表
  "scenes": [
    {
      "id": "ram_safehouse",
      "stage": "MEET_RAM",          // 归属任务阶段（null = 阶段外）
      "speaker": "ram",             // 场景默认说话人
      "speakerOverrides": { "SDTUMacarioIntroHub": "macario" },
      "title": {...}, "location": {...},
      "roots": ["r:sdtuVolturnMeetRamOption", "r:sdtuRamSafehouse11", "t:SDTUUmbraRaidFinishedA"]
    }
  ],
  "excludeRules": [...],            // 开发者规则（不进对话树）
  "ignoreRules": [...],             // 已知 Java 触发/废弃规则（报告降噪）
  "ignoreRulePatterns": ["^sd7s", "^SDSE", ...]
}
```

### 场景根（roots）写法

| 写法 | 含义 |
|------|------|
| `r:<ruleId>` | 从一条规则合成入口步骤（PopulateOptions/PickGreeting/OpenCommLink 等） |
| `m:<ruleId>:<条件needle>` | 同上，并把所有"条件里含 needle"的通用触发器规则（如 PopulateOptions 提供的实体选项池）合并进来 |
| `t:<trigger>` | 从一个自定义 trigger hub 进入（通常是 Java 代码触发的事件，如 `t:sdtuPatrolDefeated`） |

### 构建器如何展开对话

- **T: 步骤**：一个 trigger hub 屏——收集该 trigger 的所有规则（含条件变体）的文本与选项；`FireBest` 指向的**纯文本**触发器递归内联为同一屏的更多文本，指向**带选项**的触发器则成为 `next`（继续按钮）
- **O: 步骤**：选项响应——`$option == X` 的规则文本；无 Fire 目标时自动挂回来源选项池（问答式对话）
- **S: 步骤**：场景入口合成步骤，带 `entryConditions`（前端显示为"触发方式"）
- 通用触发器（PopulateOptions 等）永远不会作为屏幕展开（防止把全游戏菜单拖进来）
- Java 直接触发的选项（无任何规则提供）按 `ignoreRules` 归档

## 构建报告（report_*.md）

- **Uncovered rules**：引用了任务但没被任何场景走到——新策展线索
- **Dangling options**：没有任何响应规则的游戏原生死选项
- **External triggers**：被 Fire 但规则表里不存在的 trigger（Java 侧或原版笔误）
- **Flags without glossary**：出现在条件里但术语表没收录的 flag——补进任务包 `flags` 即可提升可读性

## 剧情人物总表（characters.md）

[characters.md](characters.md) 整理 vanilla 全部剧情人物（66 条档案，按剧情线分组）。
档案数据提取自 `ids/People.java` 与 `SDSevenSons.addLargeSons()` 的字节码（方法见其附录 B），
头衔中英对照取自官方 `default_ranks.json`；"剧情角色"注解为 wiki 编辑层手写内容。

## 新增一个任务

1. `python3 extract_java.py <en_game_root> askonia.<MissionClass>` 拿到阶段与简报（英文），人工补中文简报
2. 在游戏 `rules.csv` 里找到该任务的入口规则（酒馆事件 / 通讯问候 / 舰队遭遇），写 `quests/<id>.json`
3. 跑构建器，看报告补 roots / flags / ignoreRules，直到 uncovered 只剩已知噪声
4. 前端自动出现在任务列表（读取 `dialogues/index.json`）
