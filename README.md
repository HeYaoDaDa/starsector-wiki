# Starsector Wiki

将 Starsector 游戏数据导出为 JSON，并提供 Web 前端展示。

## 项目结构

```
├── src/                # Vue 3 + Quasar 前端
├── public/
│   ├── data/           # SplitLog.py 输出的 JSON 数据
│   └── graphics/       # moveImg.py 拷贝的游戏贴图
├── tools/
│   ├── exporter/       # WikiExporter Java Mod（游戏内导出）
│   └── splitlog/       # Python 后处理脚本
└── package.json        # 前端依赖与脚本
```

## 工作流 / Workflow

0. 将 `mods/StarsectorWikiExporter` 文件夹复制到 Starsector 游戏 `mods/` 目录下，并在游戏启动器中勾选该 Mod

1. 启动 Starsector → 载入存档 → 进入模拟（Simulation）

2. **[多语言 / Multi-Language]** 每种语言需要单独导出：
   - 将游戏语言切换为目标语言
   - 重启游戏
   - 载入存档 → 进入模拟
   - 按 F8 导出数据
   - 重复以上步骤，为每种需要的语言（如 en, zh）各导出一次

3. 运行数据提取脚本（支持多版本 + 多语言）：
   ```bash
   python3 tools/splitlog/SplitLog.py <游戏根目录路径>
   ```

4. 复制贴图资源：
   ```bash
   python3 tools/splitlog/moveImg.py <游戏根目录路径>
   ```

5. 启动 Wiki 前端：
   ```bash
   pnpm install
   pnpm quasar dev
   ```

## 多语言 / Multi-Language

### 数据结构

导出数据按 `版本/语言` 组织在 `public/data/` 目录下：

```
public/data/
├── manifest.json          # 版本列表 (自动生成)
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

1. 修改 `tools/exporter/src/exporter/WikiExporterModPlugin.java` 中的 `locale` 常量
   - `String locale = "en";` → 导出英文
   - `String locale = "zh";` → 导出中文
2. 每种语言：切换游戏语言 → 重启 → 进入模拟 → 按 F8
3. 运行 `SplitLog.py` 一次即可处理所有导出

### manifest.json

`SplitLog.py` 自动生成 `public/data/manifest.json`，前端通过此文件发现可用的版本和语言：

```json
{
  "versions": [
    { "version": "0.97a", "locales": ["en", "zh"] }
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

### SplitLog.py 选择式清除

- 运行 `SplitLog.py` 时，仅清除当前正在导出的 `版本/语言` 目录
- 其他版本的语言目录保持不变
- 日志中的旧格式行（`export_data_export_`）会被警告并跳过

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3, Quasar, TypeScript, Pinia |
| 导出 | Java (Starsector Mod API), org.json |
| 后处理 | Python 3 |

## 导出的数据类型

舰船、武器、船体插件、舰船系统、商品、工业设施、行星类型、市场状态、子市场、特殊物品、势力、星系、行星/空间站、人物。
