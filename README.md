# Starsector Wiki

将 Starsector 游戏数据导出为 JSON，并提供 Web 前端展示。

## 项目结构

```
├── src/                # Vue 3 + Quasar 前端
├── public/
│   ├── data/           # 按 {version}/{locale} 组织的 JSON 数据
│   └── graphics/       # moveImg.py 拷贝的游戏贴图
├── tools/
│   ├── exporter/       # WikiExporter Java Mod（游戏内导出）
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
