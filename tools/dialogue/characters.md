# 剧情人物整理（Story Characters）—— 0.98.5a

> ⚠️ **本文包含全部主线剧情的剧透。**

整理 vanilla 0.98.5a 中所有**在剧情里实际登场**的人物（66 条人物档案），
按剧情线 / 势力分组；另附"仅在文本中提及"的重要人物与对话树里的非人物"说话人"。

## 数据来源

| 字段 | 来源 |
|------|------|
| 姓名 / 性别 / 势力 / 头衔 / 驻地 / 重要度 / 头像 ID | `starfarer.api.jar` 中 `ids/People.java` 与 `missions/askonia/SDSevenSons.java` 的字节码（`javap -c` 解析，见附录 B） |
| 头衔中英对照 | 官方 `data/world/factions/default_ranks.json`（EN/CN 双份） |
| 势力中文名 | 前端导出数据 `public/data/0.98.5a/zh/data.json`（FACTION.displayName） |
| 登场剧情 | 任务包 `tools/dialogue/quests/*.json` 场景说话人 + 任务类字节码中 `People.*` 字段引用 |

人名政策：**官方中文不翻译人名**（全游戏唯一例外：Asharu 的隐士 "Old Man" 官方译作
"古老先生"，源自 CN 版 `People.class`）。因此下表人名一律保留英文原名。
"剧情角色"一列为 **wiki 手写注解**（同 `src/questEditorial.ts` 的编辑层政策），
其余字段均为提取数据。

## 登场剧情对照

| 简称 | 任务包 | 官方名（EN / CN） |
|------|--------|-------------------|
| 学院主线 | `the_academy_arc` | The Galatia Academy Arc / Galatia 学院主线（wiki 标签） |
| 篡位者们 | `the_usurpers` | The Usurpers / 篡位者们 |
| 继承人 | `the_supreme_executor` | Heir to Andrada / Andrada 的继承人 |
| 七子 | `the_seven_sons` | The Seven Sons / 七子（wiki 标签） |
| 朝圣者之路 | `luddic_pilgrims_path` | The Pilgrim's Path / 朝圣者之路 |
| 骑士迷途 | `luddic_knight_errant` | Knight Errant / 骑士迷途 |
| 伪像 | `bornanew_files` | False Idols / 伪像 |
| 猎户座之镰 | `recover_a_planetkiller` | The Scythe of Orion / 猎户座之镰 |
| 暮光之剑 | `sword_of_eventide` | Sword of Eventide / 暮光之剑（wiki 标签） |
| Volturn 之旅 | `a_new_hope` | Passage To Volturn / Volturn 之旅 |
| Kanta 的委托 | `misc_stories`（affk） | A Favor for Kanta |
| 杂项 | `misc_stories` | 教程、历史学家碎碎念等 |

> 注：`the_academy_arc` 对话树目前只策展了中后期阶段（Fikenhild 实验线 → Ziggurat → 群星之门），
> 但人物档案已按 jar 全量收录，不受策展进度影响。

---

## 1. Galatia 学院主线

学院（`ga_market`，Galatia 星系空间站）阵营本身为"非势力团体"，剧情上独立于各大势力。

| 人物 | 身份 | 势力 · 驻地 | 登场 | 剧情角色 |
|------|------|-------------|------|----------|
| **Anahita Baird**（`baird`） | 院长（Provost） | 独立 · Galatia 学院空间站 | 学院主线、七子（提及） | 学院首脑，主线全程的发布人：从收留玩家、委派杂务，到力推"群星之门"重启计划；结局时追问 Scylla 的下落。 |
| **Alviss Sebestyen**（`sebestyen`） | 副院士（Associate Academician） | 独立 · 学院空间站 | 学院主线 | 玩家在学院的固定接洽人；教程后续大多数任务（数据核心、废墟勘探、运送 VIP 等）的委托人。 |
| **Cornelius Elek**（`elek`） | 院士（Academician） | 独立 · 学院空间站 | 学院主线 | "Fikenhild 实验"线的委托与回报人；Ziggurat 计划期间被请回学院参与核心工作。 |
| **Arnaud Iscare**（`ga_recruiter`） | 院士 | 独立 · 学院空间站 | 继承人 | 学院招募事务负责人（头像 ID 为 ga_recruiter）。 |
| **Tobe Simisola**（`simisola`） | 院士 | 独立 · 学院空间站 | 学院主线（后期） | 后期加入的院士；定位到可为星门持续供电的日冕汲取站（coronal tap）残骸。 |
| **Scylla Coureuse**（`coureuse`） | 科学家 | 独立 · Laicaille 栖息地 | 学院主线 | 失踪的前任研究员，曾与 Baird、Zal 一同研发星门开启方法；"寻找 Coureuse"即以其为目标。 |
| **Adonya Coureuse**（`adonya`） | 已退休人员（Pensioner） | 独立 · Fikenhild | 学院主线 | Scylla 的母亲；从她口中可打探女儿下落与当年项目内情。 |
| **Elissa Zal**（`zal`） | 身份不明（Unknown） | 独立 · Fikenhild | 学院主线 | 曾协助 Coureuse / Baird 开发星门开启方法的关键人物，隐居 Fikenhild；终章与 Coureuse 一同被召回学院。 |
| **Bione Lata**（`bione`） | 公民 | 独立 · Fikenhild | 学院主线 | Fikenhild 居民，实验调查线的情报源之一。 |
| **Cavin Pharoh**（`cavin`） | 激进主义分子（Activist） | 独立 · Fikenhild | 学院主线 | 同上，Fikenhild 在地活动家。 |
| **Darshan Lamech**（`lamech`） | 科学家 | 独立 · Tse 特许经营站 | （休眠） | Port Tse 的"Dr. Lamech"。0.98.5 中其对话规则整段被注释停用；原与"黑客硬件"线相关（现由 Arroyo 提供硬件）。 |
| **Gargoyle**（`gargoyle`） | 骇客（Hacker） | 独立 · Tse 特许经营站 | 学院主线、七子 | Port Tse 的神秘"骇客"，情报与黑料贩子；Ziggurat 线（Kelise 的行踪）与七子解密（ANDRADA 档案）的关键渠道。 |
| **Callisto Ibrahim**（`ibrahim`） | 企业家 | 独立 · Agreus | 学院主线 | 以"吹牛不眨眼"闻名的船长，"Hamatsu"号船主；曾承运 Ziggurat 工程师 Kelise，从而被卷入主线。 |
| **Loke**（`clone_loke`） | 克隆体（Clone） | 海盗注册 · Nova Maxios | 学院主线（终章） | 前军阀 Onesimos Loke 的克隆体（Cydonia 所造），Kanta 的"宠物"；"At the Gates"阶段需从左径手中夺回，与 Kallichore 事件直接相关。 |

> 学院线还牵动多名"外援"：**Damos Hannan**、**Finlay Siyavong**（英仙座，见 §6），
> **Jorien Kanta**、**Livewell Cotton**（海盗/左径，见 §4、§3），以及速子科技的
> **Arroyo / Glamor-Rotanev**（见 §7）。

## 2. Askonia 危机 · 辛达强权三部曲

`篡位者们` → `Andrada 的继承人` → `七子`（按剧情时序衔接），三段剧情共享同一舞台（Askonia 星系）与人物池。
核心谜团：最高执政官 Andrada 晚年密令"克隆子嗣计划"，而**有人正在逐个猎杀这些子嗣**。

| 人物 | 身份 | 势力 · 驻地 | 登场 | 剧情角色 |
|------|------|-------------|------|----------|
| **Philip Andrada**（`andrada`） | 最高指挥官（辛达强权元首） | 辛达强权 · Sindria | 三部曲背景核心 | 最高执政官本人；"克隆子嗣计划"的始作俑者，其续命图谋是整个危机的引信。 |
| **Dolos Macario**（`macario`） | 最高检察长 / 情报局长 | 辛达强权 · Sindria | 篡位者们、七子 | 情报系统首脑，"篡位者们"主线的委托人；内斗的主要操盘者之一，玩家对其的信任度（`$trust`）决定剧情走向。 |
| **Oxana Hyder**（`hyder`） | 副星际元帅 / 舰队指挥官 | 辛达强权 · Sindria | 篡位者们、继承人、七子 | 舰队实力派，与 Macario 对立的另一极；个人舰队 `PersonalFleetOxanaHyder` 常驻辛德里亚轨道。 |
| **Horacio Caden**（`caden`） | 卫队最高副首长 / 特种部队总管 | 辛达强权 · Sindria | 篡位者们、继承人、七子 | 亲卫武装的最高长官；被激怒或被说服会显著改变局势。 |
| **Yannick Ram**（`ram`） | 特别探员（陆军上尉） | 辛达强权 · Volturn（任务中） | 篡位者们 | 在 Volturn 潜伏接触玩家的密探，"篡位者们"的引子。 |
| **Laverna Tell**（`tell`） | 军事总督（陆军上将） | 辛达强权 · Cruor | 继承人 | 内政安全部实权人物，"绝对派"的最早鼓吹者；宣布扩建 Cruor 监狱体系。 |
| **Spender Balashi**（`sec_officer`） | 军官（海军上尉） | 辛达强权 · Sindria | （元首随员） | Andrada 的安保副官，戏份寥寥的背景人物。 |
| **Achilles 'Kalian' Andrada**（`achilles`） | 军官 · 克隆子嗣 | 英仙座注册 · Yesod（Zagan 系） | 七子、继承人 | 克隆子嗣；获 Kazeron 女宗主 Fortuna Kato 撑腰，图谋接掌辛达强权（游戏内姓名牌为 Achilles Kalian）。 |
| **Hector 'Palatin' Andrada**（`hector`） | 身份不明 · 克隆子嗣 | 独立 · Sindria | 七子 | 克隆子嗣；原藏身 Donn 系小行星 58966 Elysium，后在 Macario 协助下转移至辛德里亚。 |
| **Hercules 'Cyrino' Andrada**（`hercules`） | 助理院士 · 克隆子嗣 | 独立 · Galatia 学院空间站 | 七子 | 潜伏在学院的克隆子嗣；可能当着玩家的面被"无名刺客"暗杀——猎杀子嗣线索的关键一幕。 |
| **Erdene Benoit**（`benoit`） | 助理院士 | 独立 · 学院空间站 | 七子（伴随 Hercules） | 随 Hercules 潜伏学院期间出现的人物。 |
| **Marcellus Lott**（`lott`） | 安保主管 | 独立 · 学院空间站 | 七子（同上） | 同上；学院安保主管。 |
| **Maeus Moroz**（`maeus_moroz`） | 雇佣军官 | 独立 · Orthrus（Samarra 系） | 七子 | 受雇看护子嗣"Pericles"的佣兵头目；玩家循线赶到时 Pericles 已被暗杀，Moroz 悲愤之下迁怒于人（可发展为敌对舰队）。 |
| **Wyatt Cydonia**（`cydonia`） | 博士 | 海盗 · Kanta 之巢 | 七子、继承人 | 克隆技术的操刀者：既造了七子的克隆体，也造了 Loke；曾尝试把老 Andrada 的意识转移到 Perseus（失败）；事发后投奔 Kanta，两线中均可被玩家约谈对质。 |
| **Crasis**（`crasis`） | Alpha 核心（人工智能） | 独立 · 17054 Irkalla（Duzahk 系） | 七子 | 与 Aureolin 一对；在 Irkalla 以假通讯身份"NETI"应答访客，实为脑死亡子嗣 Leonidas 的看护者。 |
| **Aureolin**（`aureolin`） | Gamma 核心（人工智能） | 独立 · 17054 Irkalla | 七子 | 同上；与 Crasis 一唱一和，主张"生存优先"。 |
| 无名 **Qaras 特工**（`sd7s_qaras_agent`） | — | Qaras（Yma 系） | 七子 | 七子线在 Qaras 的拦截目标（需击败其舰队）。 |

> 三部曲的"外援"：英仙座的 **Fortuna Kato / Horus Yaribay / Reynard Hannan**（§6）、
> 海盗的 **Ko Jove**（§4）、速子的 **Faro Inesis / Gallu Blanc / Arroyo / Glamor-Rotanev**（§7）、
> 霸主的 **Orcus Rao / Baikal Daud**（§5），以及 **Gargoyle**（§1）。

## 3. 卢德教会 · 卢德骑士团 · 卢德左径

三条卢德线：`朝圣者之路`（巡礼圣地）、`骑士迷途`（教会内幕与左径冲突）、`伪像`（Olinadu 假圣物事件）。

| 人物 | 身份 | 势力 · 驻地 | 登场 | 剧情角色 |
|------|------|-------------|------|----------|
| **Sophronia Jaspis**（`jaspis`） | 大祭司（教母） | 卢德教会 · Gilead | 朝圣者之路、伪像、骑士迷途 | 卢德教会最高层；朝圣路线的权威背书者，也是教会政治的深水区。 |
| **Jethro Bornanew**（`bornanew`） | 见习修士（修士） | 卢德教会 · Gilead | 伪像、骑士迷途 | "伪像"事件的关键证人：被 Ulmus Pond 当众胁迫的一幕是该线的引爆点。 |
| **Gideon Oak**（`oak`） | 行星教卫（神父） | 卢德骑士团 · Hesperus | 朝圣者之路、伪像 | 卢德骑士团核心人物，"行星教卫"（Excubitor Orbis）头衔持有者。 |
| **Ned Boot**（`initiate`） | 初信者（修士） | 卢德骑士团 · Hesperus | （背景） | Hesperus 的初信者，微末小角色。 |
| **Moyra Standfast**（`standfast`） | 神龛祭司（教母） | 卢德教会 · Volturn | 朝圣者之路、继承人 | Volturn 圣坛的主持者，朝圣者之路的一站。 |
| **Cedra Keepfaith**（`cedra_keepfaith`） | 助理祭司（修女） | 卢德教会 · Tartessus | （背景） | Tartessus 的教会基层。 |
| **Dejan Larix**（`larix`） | 骑士队长（修士） | 卢德骑士团 · Tartessus | （背景） | Tartessus 的骑士队长。 |
| **Nile Virens**（`virens`） | 恐怖分子（修士） | 卢德左径 · Mazalot | 骑士迷途 | Mazalot 左径头目，"骑士迷途"中与教会/骑士团正面冲突的一极。 |
| **Livewell Cotton**（`cotton`） | 恐怖分子（修士） | 卢德左径 · Epiphany | 学院主线（终章）、骑士迷途（提及） | 左径"新星"；其小组绑走了 Loke 克隆体，"At the Gates"必须从他手里把人捞出来。 |
| **Wrestling Sedge**（`sedge`） | 恐怖分子（修士） | 卢德左径 · Chalcedon | （背景/遭遇） | Chalcedon 左径头目。 |
| **Ulmus Pond**（`ulmus_pond`） | 探员（伪装） | 独立注册 · Olinadu | 伪像 | 潜伏 Olinadu 的左径中人；在公开场合胁迫 Bornanew 的打手，眼神"像鱼一样凸出"。 |

## 4. 海盗与 Kanta 家族

| 人物 | 身份 | 势力 · 驻地 | 登场 | 剧情角色 |
|------|------|-------------|------|----------|
| **Jorien Kanta**（`kanta`） | 军阀（最高指挥官） | 海盗 · Kanta 之巢 | Kanta 的委托、学院主线（终章） | 海盗世界的"老祖宗"；为取回爱宠 Loke 克隆体不惜与玩家交易，甚至插手学院终章。 |
| **Bellamy Kanta**（`bellamy_kanta`） | 管理员 | 英仙座注册 · Salamanca | （家族网络） | Kanta 家族后裔，在英仙座境内任殖民官，是家族影响力的触角。 |
| **K-O Jove**（`ko_jove`） | 黑帮头目（Underworld Boss） | 海盗 · Qaras（Yma 系） | 七子、继承人 | Qaras 地下世界头目，Kanta 家族关联人物；七子线里掌握子嗣线索的地头蛇。 |
| **Imoinu Kato**（`imoinu_kato`，篡位者们包内 ID `imoinu`） | 军需官（自由斗士） | 海盗 · Umbra | 篡位者们、继承人 | 叛离 Kato 氏族的"双面特工"（官方头衔即 Double agent）：明面是海盗补给官，实际是 Kato 家出走的"不肖继承人"。 |

## 5. 霸主（Hegemony）与 Eventide

`暮光之剑` 的舞台在 Hegemony 辖下的 Eventide（Raesvelg 围城战英雄 Rao 家族的封地）；
`猎户座之镰` 则是霸主高层的黑幕戏。

| 人物 | 身份 | 势力 · 驻地 | 登场 | 剧情角色 |
|------|------|-------------|------|----------|
| **Baikal Daud**（`daud`） | 最高指挥官（霸主元首） | 霸主 · Chicomoztoc | 七子（对话出场）、历史背景 | 霸主最高执行官；七子线里对 Askonia 局势做出最终裁量。 |
| **Alejandro Rivas**（`rivas`） | 安保主管 | 霸主 · Chicomoztoc | （背景） | 首都安全主管，背景人物。 |
| **Orcus Rao**（`rao`） | 海军上将 / 军事总督 | 霸主 · Ragnar 综合设施 | 猎户座之镰、篡位者们（提及）、七子、继承人 | Raesvelg 围城战的英雄，Ragnar 舰队指挥官；猎户座之镰中回收"行星杀手"的幕后拍板人，暗中资助 Nortia 的"宪章派"叛乱。 |
| **Neriene Rao**（`neriene_rao`） | 军官（海军中校） | 霸主 · Eventide | 暮光之剑 | Rao 家族成员；Eventide 舞会上与玩家共舞、试探来意的关键对话者。 |
| **Augusta Rao**（`augusta_rao`） | 贵族 | 霸主 · Eventide | 暮光之剑 | 自立门户的 Rao 家族贵妇，"她自己的家族"与 Orcus 一脉早已失和。 |
| **Caspian Sang**（`caspian`） | 军官（海军上尉） | 霸主 · Eventide | 暮光之剑 | Eventide 舞会上那声"喔，$playerName！"的傲慢军官，冲突的直接引信。 |
| **Magnus Cardona**（`magnus`） | 军官（海军中校） | 霸主 · Eventide | 暮光之剑 | Eventide 军官集团成员。 |
| **Alo Skiron**（`skiron`） | 管理员（海军中校） | 霸主 · 猎户座之镰目标行星（动态） | 猎户座之镰 | 被派驻"苔原行星"的行政官——驻地随任务目标随机生成。 |

## 6. 英仙座联盟（Persean League）

Kazeron 诸宗族（Gens Kato / Yaribay / Hannan）是联盟政治的主场，也是七子线的重要变量。

| 人物 | 身份 | 势力 · 驻地 | 登场 | 剧情角色 |
|------|------|-------------|------|----------|
| **Fortuna Kato**（`fortuna_kato`） | 贵族（女宗主） | 英仙座 · Kazeron | 七子、继承人 | Kato 宗主；公开为克隆子嗣 Achilles 撑腰，意图借其遥控辛达强权。 |
| **Horus Yaribay**（`horus_yaribay`） | 贵族（宗主） | 英仙座 · Kazeron | 七子、继承人、伪像 | Yaribay 宗主；继承人线中联盟方的重要说客（请玩家援助 Nortia 宪章派等）。 |
| **Reynard Hannan**（`reynard_hannan`） | 宗主 | 英仙座 · Kazeron | 七子、继承人 | Hannan 宗主；联盟对 Askonia 局势表态的关键人物。 |
| **Damos Hannan**（`damos_hannan`） | 基地指挥官（陆军上校） | 英仙座 · Laicaille 栖息地 | 学院主线（FC 线背景） | Laicaille 基地指挥官；寻找 Coureuse 时绕不开的军方关卡。 |
| **Menes Yaribay**（`menes_yaribay`） | 管理员（贵族） | 英仙座 · Olinadu | 伪像 | Olinadu 新任民选执政官（demarchon）；上任周年炫富式的"收藏"展出引爆了假圣物事件，是"伪像"的袭击目标。 |
| **Dardan Kato**（`dardan_kato`） | 管理员 | 英仙座 · Mazalot | （背景） | Mazalot 殖民官，Kato 宗族成员。 |
| **Finlay Siyavong**（`siyavong`） | 特别探员（探员） | 英仙座 · Fikenhild | 学院主线、七子、继承人 | 驻 Fikenhild 的联盟特工；实验调查线与七子线均有戏份的多面人物。 |

## 7. 速子科技（Tri-Tachyon）

| 人物 | 身份 | 势力 · 驻地 | 登场 | 剧情角色 |
|------|------|-------------|------|----------|
| **Artemisia Sun**（`sun`） | 最高指挥官（CEO） | 速子科技 · Eochu Bres | （对话/背景提及） | 速子科技最高执行官；暂无登场戏份，在对白与历史学家碎碎念中被反复提及。 |
| **Zunya Glamor-Rotanev**（`glamor_rotanev`） | 情报局长 / 高级主管 | 速子科技 · Eochu Bres | 学院主线、七子 | 速子情报系统首脑；Ziggurat 黑幕的直接对话者之一。 |
| **Rayan Arroyo**（`arroyo`） | 企业家 / 高级主管 | 速子科技 · Eochu Bres | 学院主线、七子、继承人、猎户座之镰 | 速子高级主管，玩家可用的贸易接触人；提供黑客硬件、七子解密渠道、Kelise 的档案调阅等多线服务。 |
| **Faro Inesis**（`faro_inesis`） | 特别探员（经理） | 速子科技 · Tibicena | 七子、继承人 | 速子派驻外围的特工；继承人/七子线中速子方利益的操盘手，对 Nortia 宪章派的底细一清二楚。 |
| **Gallu Blanc**（`gallu_blanc`） | 管理员 / 高级主管 | 独立注册 · Nomios | 七子 | Nomios 行政官，速子背景深厚；替公司掩盖 Perseus 意识转移实验的善后先生，被问急了会"让 HR 找你聊聊"（游戏 tag：拒收 AI 核心）。 |

## 8. 独立人物与零散剧情

| 人物 | 身份 | 势力 · 驻地 | 登场 | 剧情角色 |
|------|------|-------------|------|----------|
| **"古老先生" / Old Man**（`robedman`） | 隐士 | 独立 · Asharu | Volturn 之旅 | Asharu 的怪隐士，全游戏唯一有官方中文名的人物；"Volturn 之旅"的委托人。通讯录中隐藏。 |
| **历史学家**（无名） | — | 各酒吧（随机） | 杂项 | 随机姓名与性别的酒吧 NPC，讲古型角色：以十几段碎碎念交代大崩塌、14 战斗群、霸主立国等背景设定，并出售蓝图/特殊物品线索。 |

> `接触任务合集`（contact_missions，24 个中小任务）由上述剧情人物与随机生成的接触人提供，
> 无独立命名角色，不在本表范围。

## 9. 仅在剧情文本中提及（无人物档案）

| 人物 | 出处 | 说明 |
|------|------|------|
| **Kelise Astraia** | 学院主线（Ziggurat 线） | Culann 星铸厂的前武器工程师，被"黑项目"（Ziggurat/Alpha Site）高薪挖走；乘 Ibrahim 的"Hamatsu"号失踪，是 Ziggurat 线的引子。 |
| **Perseus 'Saturnian' Andrada** | 七子 | 克隆子嗣；Cydonia 曾尝试把老 Andrada 的意识转移进他体内——失败。其病历构成 Nomios 一段支线的核心。 |
| **Leonidas 'Esculus' Andrada** | 七子 | 克隆子嗣；如今脑死亡、靠维生系统躺在 17054 Irkalla，由 Crasis / Aureolin 看护。 |
| **Jason 'Korin'** | 七子 | 克隆子嗣之一；档案显示其在 Culann 的速子"慈善学校"长大，出逃后买了黑船票去了 **Qaras（Yma 系）**，与 Kanta 帮派势力搅在一起——正是 Ko Jove 的地盘。 |
| **Onesimos Loke** | 学院主线 / 历史背景 | 大崩塌前的"前军阀"，Kanta 的克隆体"宠物"即以他为本体。 |
| **Admiral Kali Molina** | 历史学家碎碎念 | 霸主开国元勋，在 Eventide 发表"霸主宣言"。 |
| **Warlord Leonis** | 历史学家碎碎念 | 14 战斗群到来之前统治英仙座的"残暴军阀"，被霸主先祖推翻。 |

## 10. 对话树里的非人物"说话人"

任务对话包里以实体身份"说话"的非人物对象（可在前端对话树里作为场景/说话方出现）：

| 实体 | 类型 | 登场 | 说明 |
|------|------|------|------|
| Galatia 学院空间站（`station_galatia_academy`） | 空间站 | 学院主线、七子 | 学院本体，多数任务的起点与终点。 |
| Beholder 站（`beholder_station`） | 空间站 | 朝圣者之路 | Kumani Aru 轨道上的圣坛站，朝圣路线之一。 |
| Killa 圣坛（`killa`） | 遗迹地点 | 朝圣者之路 | 传说中"可能有，也可能已不存在"的圣坛。 |
| Sindria 中继站（`sindria_relay`） | 通讯中继 | 继承人 | 继承人线中被用作剧情节点的 Askonia 中继站。 |
| Nortia（`nortia`） | 卫星（市场） | 继承人 | Askonia 卫星；"宪章派"（ACA）叛乱的大本营，霸主暗中介入。 |
| 58966 Elysium（`58966elysium`） | 小行星基地 | 七子 | Donn 系内临时生成的"asteroid_base"，Hector 的初始藏身处。 |
| 17054 Irkalla（`17054irkalla`） | 小行星基地 | 七子 | Duzahk 系内临时生成；Leonidas 的"棺材"，Crasis / Aureolin 驻地；玩家到访后被"近乎泄愤地"炸毁。 |
| Orthrus / Yesod | 市场（Samarra / Zagan 系） | 七子 | 分别是 Moroz（Pericles 线索）与 Achilles 的驻地，酒吧事件的发生地。 |
| "Hamatsu" | 船只 | 学院主线 | Ibrahim 名下的旧 Venture 级船，Kelise 的"失联航班"。 |

---

## 附录 A —— 人物档案总表（66 条，按人物 ID 排序）

全部为 jar 提取数据（创建来源：`People.java` 的 createMiscCharacters / createAcademyPersonnel /
createFactionLeaders / add\* 系列，或 `SDSevenSons.addLargeSons()`）。
`职务` = post（通讯录显示用），`军衔` = rank，`重要度` = PersonImportance。

| ID | 姓名 | 性别 | 势力 | 驻地 | 职务 | 军衔 | 重要度 | 头像 ID |
|----|------|------|------|------|------|------|--------|---------|
| `achilles` | Achilles Kalian | MALE | persean | yesod | POST_OFFICER | SPACE_LIEUTENANT | MEDIUM | achilles_andrada |
| `adonya` | Adonya Coureuse | FEMALE | independent | fikenhild | POST_PENSIONER | CITIZEN | VERY_LOW | =id（adonya） |
| `andrada` | Philip Andrada | MALE | sindrian_diktat | sindria | POST_FACTION_LEADER | FACTION_LEADER | VERY_HIGH | andrada |
| `arroyo` | Rayan Arroyo | MALE | tritachyon | eochu_bres | POST_ENTREPRENEUR | SENIOR_EXECUTIVE | HIGH | =id（arroyo） |
| `augusta_rao` | Augusta Rao | FEMALE | hegemony | eventide | POST_ARISTOCRAT | CITIZEN | HIGH | augusta_rao |
| `aureolin` | Aureolin | ANY | independent | 17054irkalla(注册于 orthrus) | Gamma 核心 | 人工智能（AI_CORE） | MEDIUM | =id（aureolin） |
| `baird` | Anahita Baird | FEMALE | independent | ga_market | POST_PROVOST | CITIZEN | VERY_HIGH | baird |
| `bellamy_kanta` | Bellamy Kanta | MALE | persean | salamanca | POST_ADMINISTRATOR | CITIZEN | MEDIUM | bellamy_kanta |
| `benoit` | Erdene Benoit | FEMALE | independent | ga_market | POST_ASSISTANT_ACADEMICIAN | CITIZEN | VERY_LOW | benoit |
| `bione` | Bione Lata | FEMALE | independent | fikenhild | POST_CITIZEN | CITIZEN | VERY_LOW | =id（bione） |
| `bornanew` | Jethro Bornanew | MALE | luddic_church | gilead | POST_NOVICE | BROTHER | LOW | jethro_bornanew |
| `caden` | Horacio Caden | MALE | sindrian_diktat | sindria | POST_GUARD_LEADER | GUARD_HIGH_DEPUTY_EXECUTOR | HIGH | horacio_caden |
| `caspian` | Caspian Sang | MALE | hegemony | eventide | POST_OFFICER | SPACE_LIEUTENANT | LOW | caspian |
| `cavin` | Cavin Pharoh | MALE | independent | fikenhild | POST_ACTIVIST | CITIZEN | VERY_LOW | =id（cavin） |
| `cedra_keepfaith` | Cedra Keepfaith | FEMALE | luddic_church | tartessus | POST_SUBCURATE | SISTER | LOW | cedra_keepfaith |
| `clone_loke` | Loke | MALE | pirates | new_maxios | POST_AGENT | CLONE | MEDIUM | =id（clone_loke） |
| `cotton` | Livewell Cotton | MALE | luddic_path | epiphany | POST_TERRORIST | BROTHER | HIGH | =id（cotton） |
| `coureuse` | Scylla Coureuse | FEMALE | independent | laicaille_habitat | POST_SCIENTIST | CITIZEN | LOW | =id（coureuse） |
| `crasis` | Crasis | ANY | independent | 17054irkalla(注册于 orthrus) | Alpha 核心 | 人工智能（AI_CORE） | MEDIUM | =id（crasis） |
| `cydonia` | Wyatt Cydonia | MALE | pirates | kantas_den | POST_DOCTOR | CITIZEN | MEDIUM | doctor |
| `damos_hannan` | Damos Hannan | MALE | persean | laicaille_habitat | POST_BASE_COMMANDER | GROUND_COLONEL | HIGH | damos_hannan |
| `dardan_kato` | Dardan Kato | MALE | persean | mazalot | POST_ADMINISTRATOR | CITIZEN | MEDIUM | dardan_kato |
| `daud` | Baikal Daud | MALE | hegemony | chicomoztoc | POST_FACTION_LEADER | FACTION_LEADER | VERY_HIGH | baikal |
| `elek` | Cornelius Elek | MALE | independent | ga_market | POST_ACADEMICIAN | CITIZEN | LOW | elek |
| `faro_inesis` | Faro Inesis | MALE | tritachyon | tibicena | POST_SPECIAL_AGENT | EXECUTIVE | HIGH | faro_inesis |
| `fortuna_kato` | Fortuna Kato | FEMALE | persean | kazeron | POST_ARISTOCRAT | HOUSE_LEADER_FEMALE | HIGH | =id（fortuna_kato） |
| `ga_recruiter` | Arnaud Iscare | MALE | independent | ga_market | POST_ACADEMICIAN | CITIZEN | LOW | ga_recruiter |
| `gallu_blanc` | Gallu Blanc | MALE | independent | nomios | POST_ADMINISTRATOR | SENIOR_EXECUTIVE | HIGH | gallu_blanc |
| `gargoyle` | Gargoyle | ANY | independent | port_tse | POST_HACKER | CITIZEN | MEDIUM | =id（gargoyle） |
| `glamor_rotanev` | Zunya Glamor-Rotanev | FEMALE | tritachyon | eochu_bres | POST_INTELLIGENCE_DIRECTOR | SENIOR_EXECUTIVE | VERY_HIGH | =id（glamor_rotanev） |
| `hector` | Hector Palatin | MALE | independent | sindria | POST_UNKNOWN | CITIZEN | MEDIUM | hector_andrada |
| `hercules` | Hercules Cyrino | MALE | independent | ga_market | POST_ASSISTANT_ACADEMICIAN | CITIZEN | LOW | hercules_andrada |
| `horus_yaribay` | Horus Yaribay | MALE | persean | kazeron | POST_ARISTOCRAT | HOUSE_LEADER_MALE | HIGH | =id（horus_yaribay） |
| `hyder` | Oxana Hyder | FEMALE | sindrian_diktat | sindria | POST_FLEET_COMMANDER | DEPUTY_STAR_MARSHAL | HIGH | oxana_hyder |
| `ibrahim` | Callisto Ibrahim | FEMALE | independent | agreus | POST_ENTREPRENEUR | CITIZEN | HIGH | =id（ibrahim） |
| `imoinu_kato` | Imoinu Kato | FEMALE | pirates | umbra | POST_SUPPLY_OFFICER | FREEDOM_FIGHTER | MEDIUM | imoinu_kato |
| `initiate` | Ned Boot | MALE | knights_of_ludd | hesperus | POST_INITIATE | BROTHER | VERY_LOW | initiate |
| `jaspis` | Sophronia Jaspis | FEMALE | luddic_church | gilead | POST_ARCHCURATE | MOTHER | HIGH | jaspis |
| `kanta` | Jorien Kanta | FEMALE | pirates | kantas_den | POST_WARLORD | FACTION_LEADER | VERY_HIGH | kanta |
| `ko_jove` | K-O Jove | MALE | pirates | qaras | POST_UNDERWORLD_BOSS | CRIMINAL | HIGH | ko_jove |
| `lamech` | Darshan Lamech | MALE | independent | port_tse | POST_SCIENTIST | CITIZEN | MEDIUM | =id（lamech） |
| `larix` | Dejan Larix | MALE | knights_of_ludd | tartessus | KNIGHT_CAPTAIN | BROTHER | LOW | larix |
| `lott` | Marcellus Lott | MALE | independent | ga_market | POST_SECURITY_CHIEF | CITIZEN | MEDIUM | lott |
| `macario` | Dolos Macario | MALE | sindrian_diktat | sindria | POST_INTELLIGENCE_DIRECTOR | CHIEF_HIGH_INSPECTOR | HIGH | dolos_macario |
| `maeus_moroz` | Maeus Moroz | MALE | independent | orthrus | POST_MERCENARY | CITIZEN | MEDIUM | maeus_moroz |
| `magnus` | Magnus Cardona | MALE | hegemony | eventide | POST_OFFICER | SPACE_COMMANDER | LOW | magnus_cardona |
| `menes_yaribay` | Menes Yaribay | MALE | persean | olinadu | POST_ADMINISTRATOR | ARISTOCRAT | MEDIUM | =id（menes_yaribay） |
| `neriene_rao` | Neriene Rao | FEMALE | hegemony | eventide | POST_OFFICER | SPACE_COMMANDER | MEDIUM | neriene_rao |
| `oak` | Gideon Oak | MALE | knights_of_ludd | hesperus | POST_EXCUBITOR_ORBIS | FATHER | HIGH | gideon_oak |
| `ram` | Yannick Ram | MALE | sindrian_diktat | sindria | POST_SPECIAL_AGENT | GROUND_CAPTAIN | LOW | yannick_ram |
| `rao` | Orcus Rao | MALE | hegemony | ragnar_complex | POST_MILITARY_ADMINISTRATOR | SPACE_ADMIRAL | VERY_HIGH | orcus_rao |
| `reynard_hannan` | Reynard Hannan | MALE | persean | kazeron | FACTION_LEADER | HOUSE_LEADER_MALE | VERY_HIGH | reynard_hannan |
| `rivas` | Alejandro Rivas | MALE | hegemony | chicomoztoc | POST_SECURITY_CHIEF | CITIZEN | LOW | rivas |
| `robedman` | Old Man（古老先生） | MALE | independent | asharu | POST_HERMIT | CITIZEN | MEDIUM | robed_man |
| `sebestyen` | Alviss Sebestyen | MALE | independent | ga_market | POST_ASSOCIATE_ACADEMICIAN | CITIZEN | MEDIUM | sebestyen |
| `sec_officer` | Spender Balashi | MALE | sindrian_diktat | sindria | POST_OFFICER | SPACE_LIEUTENANT | VERY_LOW | balashi |
| `sedge` | Wrestling Sedge | MALE | luddic_path | chalcedon | POST_TERRORIST | BROTHER | MEDIUM | sedge |
| `simisola` | Tobe Simisola | MALE | independent | ga_market | POST_ACADEMICIAN | CITIZEN | LOW | simisola |
| `siyavong` | Finlay Siyavong | MALE | persean | fikenhild | POST_SPECIAL_AGENT | AGENT | HIGH | =id（siyavong） |
| `skiron` | Alo Skiron | FEMALE | hegemony | (dynamic) | POST_ADMINISTRATOR | SPACE_COMMANDER | MEDIUM | skiron |
| `standfast` | Moyra Standfast | FEMALE | luddic_church | volturn | POST_SHRINE_PRIEST | MOTHER | MEDIUM | standfast |
| `sun` | Artemisia Sun | FEMALE | tritachyon | eochu_bres | POST_FACTION_LEADER | FACTION_LEADER | VERY_HIGH | sun |
| `tell` | Laverna Tell | FEMALE | sindrian_diktat | cruor | POST_MILITARY_ADMINISTRATOR | GROUND_GENERAL | MEDIUM | laverna_tell |
| `ulmus_pond` | Ulmus Pond | MALE | independent | olinadu | POST_AGENT | CITIZEN | LOW | ulmus_pond |
| `virens` | Nile Virens | MALE | luddic_path | mazalot | POST_TERRORIST | BROTHER | MEDIUM | nile_virens |
| `zal` | Elissa Zal | FEMALE | independent | fikenhild | POST_UNKNOWN | CITIZEN | MEDIUM | =id（zal） |

> `=id（…）` 表示头像按"人物 ID 即头像 ID"规则从 `settings.json` 的 `characters` 分类解析
> （如 `baird` → `graphics/portraits/characters/provost_baird.png`）。

## 附录 B —— 数据来源与复现方法

人物档案并非来自任何文本文件，而是从**字节码**里解出来的（vanilla 的剧情人物全部在 Java 里
`createPerson()` 逐个创建）：

```bash
# 1) 反汇编人物创建类（游戏自带 JDK）
~/Games/starsector-0985a-en/jre_linux/bin/javap -p -c \
  -classpath ~/Games/starsector-0985a-en/starfarer.api.jar \
  com.fs.starfarer.api.impl.campaign.ids.People          # createFactionLeaders / createMiscCharacters / add*
# SDSevenSons.addLargeSons() 创建克隆子嗣、Moroz、Crasis/Aureolin
~/Games/starsector-0985a-en/jre_linux/bin/javap -p -c \
  -classpath ~/Games/starsector-0985a-en/starfarer.api.jar \
  com.fs.starfarer.api.impl.campaign.missions.askonia.SDSevenSons
```

2) 按 `createPerson → setId/setFaction/setRankId/setPostId/setImportance/setFirst/setLast/setPortraitSprite`
的固定调用序列解析上述输出（状态机逐条吃 `ldc`/`getstatic` + `invokeinterface`），
得到 66 条结构化档案。

3) 中英头衔来自官方 `data/world/factions/default_ranks.json`（两份语言包各一份，含 `#` 注释与
不严格 JSON，需宽松解析）；CN 版 `People.class` 与 EN 逐字节比对，仅 "Old/Man" → "古老/先生"
一处本地化。

4) 出场关联：任务包 `tools/dialogue/quests/*.json` 的场景说话人 ∪ 任务类常量池中的
`People.XXX` 字段引用（后者用 `javap -c` 全量 grep `ids/People\.`）。

5) 交叉验证：`public/data/0.98.5a/{en,zh}/data.json` 的 PERSON 导出（314 条，含全部重要人物，
可核对驻地与头像路径）。个别档案（Hyder/Caden 的辛德里亚驻地、Cydonia 的 Kanta 之巢等）
依此校正——字节码中复用同一 market 局部变量，简单解析会得到空值。

游戏更新后重跑 1–5 即可再生成附录 A；正文表格的"剧情角色"注解为手写，需随版本人工核对。

