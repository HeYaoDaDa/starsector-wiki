# Starsector Wiki

将 Starsector 游戏数据导出为 JSON，并提供 Web 前端展示。

## 项目结构

```
├── src/                # Vue 3 + Quasar 前端
├── public/
│   ├── data/           # 按 {version}/{locale} 组织的 JSON 数据
│   │   └── {version}/dialogues/   # 任务对话树（双语合并，与 locale 无关）
│   └── graphics/       # moveImg.py 拷贝的游戏贴图
├── tools/
│   ├── exporter/       # WikiExporter Java Mod（游戏内导出）
│   ├── dialogue/       # 任务对话解析管线（Python，离线读 rules.csv）
│   └── splitlog/       # Python 后处理脚本
└── package.json        # 前端依赖与脚本
```

## 工作流 / Workflow

### 首次导出

1. 将 `tools/exporter/` 目录复制到 Starsector 游戏 `mods/` 目录下，并在游戏启动器中勾选 WikiExporter

2. 启动 Starsector → 载入存档 → 进入模拟（Simulation）

3. 按 F8 导出数据（数据会输出到游戏日志 `starsector.log`）

4. 运行数据提取脚本，从日志中提取 JSON 文件：
   ```bash
   python3 tools/splitlog/SplitLog.py <游戏根目录路径>
   ```
   输出为扁平文件 `public/data/{name}.json`

5. 将提取的 JSON 文件手动整理为前端所需的目录结构：
   ```
   public/data/{version}/{locale}/data.json
   ```

6. 更新 `public/data/manifest.json`，添加对应的版本和语言条目

7. 复制贴图资源：
   ```bash
   python3 tools/splitlog/moveImg.py <游戏根目录路径>
   ```

8. 启动 Wiki 前端：
   ```bash
   pnpm install
   pnpm quasar dev
   ```

## 任务与对话 / Quests & Dialogue

对话数据不走游戏内导出——直接离线解析游戏目录里的 `rules.csv`（中英双语言按规则 ID 对齐），
产出按"任务 → 阶段 → 场景 → 对话树"组织的 JSON，前端提供交互式对话浏览（中英对照、
条件标注、分支跳转）。

```bash
# 读取 ~/Games/starsector-0985a-{en,cn}，生成 public/data/{version}/dialogues/
python3 tools/dialogue/build_quests.py
```

详见 [tools/dialogue/README.md](tools/dialogue/README.md)。工具链：

- `draft_quest.py` —— 按 `$xxx_stage ==` 条件自动聚类场景草稿（大任务线用）
- `extract_java.py` —— 双 jar（EN/CN）常量池提取，任务简报官方双语
- `build_dictionary.py` —— 全库对话词典（14,255 条，懒加载 + 前端全文搜索）

当前收录：

- 篡夺者（The Usurpers）—— 覆盖率已迭代至只剩已知噪声
- 七子（The Seven Sons）+ 最高元首（The Supreme Executor）—— 自动起草 + 官方简报，
  覆盖率仍在按 `report_*.md` 持续迭代
- 对话词典（`#/dialogue_dict`）—— rules.csv 全部带文本规则，中英检索

## 构建时 Canvas 预计算 / Build-time Canvas Precomputation

为消除运行时加载贴图并计算 Canvas 尺寸的性能开销，构建时会自动预计算所有武器和舰船的
`CanvasResult`（边界框尺寸），结果写入 `canvas-cache.json`。

### 流程

```bash
# 手动预计算（prebuild 会自动执行，一般无需手动运行）
node tools/precompute-canvas.mjs

# 构建（自动触发 prebuild）
npm run build
# 或
pnpm quasar build
```

### 原理

`tools/precompute-canvas.mjs` 会：

1. 读取 `public/data/manifest.json`，发现所有版本和 locale
2. 对每个版本，读取 `data.json` 中的武器/舰船数据
3. 用 `image-size` 库读取对应 PNG 贴图的宽高（仅文件头，微秒级）
4. 运行与前端相同的 `computeCanvasSprites` 数学计算
5. 将结果写入所有 locale 的 `canvas-cache.json`

前端 `AppData.initData()` 在加载 `data.json` 后紧接着加载 `canvas-cache.json`，
直接填入 `shipCanvasMap` / `weaponCanvasMap`。`ShipSpriteDiv` 和 `WeaponSpriteDiv`
从这些 Map 同步读取缓存，**无需加载贴图、无需数学计算、无需等待 async**。

### 缓存文件

```
public/data/{version}/{locale}/canvas-cache.json
```

- 约 70 KB 纯 JSON（gzip 后约 30 KB）
- 与 locale 无关，所有 locale 共享相同数据
- 由 `prebuild` 脚本自动生成，应提交到 Git

### 注意

如果 `canvas-cache.json` 不存在，前端将加载失败（显示 "Load Error!"），
不会回退到运行时计算。务必在构建前执行预计算。

## 多语言 / Multi-Language

### 数据结构

导出数据按 `版本/语言` 组织在 `public/data/` 目录下（需手动维护）：

```
public/data/
├── manifest.json          # 版本列表（手动维护）
└── {version}/
    └── {locale}/
        └── data.json      # 该版本 + 语言的游戏数据
```

示例：
```
public/data/
├── manifest.json
└── 0.97a/
    ├── en/
    │   └── data.json      # 0.97a 英文数据
    └── zh/
        └── data.json      # 0.97a 中文数据
```

### 导出流程

1. 每种语言：切换游戏语言 → 重启 → 进入模拟 → 按 F8
2. 运行 `SplitLog.py` 从日志中提取扁平 JSON 文件
3. 将 JSON 文件手动整理为 `{version}/{locale}/data.json` 格式
4. 更新 `manifest.json`

### manifest.json

`public/data/manifest.json` 需**手动维护**，前端通过此文件发现可用的版本和语言：

```json
{
  "versions": [
    { "version": "0.98a", "locales": ["en", "zh"] }
  ]
}
```

## 多版本 / Multi-Version

### 版本自动检测

- Java 导出器自动从 `Global.getSettings().getVersionString()` 获取版本号
- 版本号中的特殊字符会被替换为 `_` 以防止路径问题
- 不同版本的导出数据存放在独立的目录中，互不覆盖

### 前端版本选择器

- 连接数据后，前端工具栏会显示版本选择下拉菜单
- 切换版本会自动加载对应版本的游戏数据
- 版本选择器仅在 manifest.json 中存在多个版本时显示

### 说明

当前 `SplitLog.py` 仅支持从日志中提取扁平 JSON 文件（`export_<名称>_export_<内容>`），
**不支持**自动组织 `{version}/{locale}/data.json` 目录结构。

如需更新数据：
1. 运行 Java 导出器 + SplitLog.py 提取 JSON
2. 手动将文件放入对应的版本/语言目录下
3. 更新 `manifest.json`

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3, Quasar, TypeScript, Pinia |
| 导出 | Java (Starsector Mod API), org.json |
| 后处理 | Python 3 |

## 导出的数据类型

舰船、武器、船体插件、舰船系统、商品、工业设施、行星类型、市场状态、子市场、特殊物品、势力、星系、行星/空间站、人物。

任务对话（篡夺者等，见"任务与对话"一节）。
