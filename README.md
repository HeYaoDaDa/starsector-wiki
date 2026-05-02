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

## 工作流

```
1. 安装 WikiExporter Mod → Starsector
2. 启动游戏 → 模拟战 → 按 F8 → 退出
       ↓
   starsector.log 包含导出的 JSON
       ↓
3. python3 tools/splitlog/SplitLog.py <game_root>
       ↓
   public/data/data.json
       ↓
4. python3 tools/splitlog/moveImg.py <game_root>
       ↓
   public/graphics/*
       ↓
5. yarn && quasar dev
```

### 1. 安装 Mod

将 `tools/exporter/` 目录打包或直接放到 Starsector 的 `mods/` 目录下。
汉化游戏只需要 `data` 和 `graphics` 两个文件夹即可。

### 2. 触发导出

启动游戏（dev 模式），进入**模拟战**，然后按 **F8** 触发数据导出。完成后退出游戏。

游戏日志 `<game_root>/starsector.log` 中将包含所有导出数据。

### 3. 提取数据

```bash
python3 tools/splitlog/SplitLog.py /opt/starsector
```

从游戏日志中提取 JSON，生成 `public/data/data.json`。

### 4. 拷贝贴图

```bash
python3 tools/splitlog/moveImg.py /opt/starsector
```

将游戏贴图资源（舰船、武器、势力图标等）复制到 `public/graphics/`。

### 5. 启动前端

```bash
yarn
quasar dev
```

访问本地开发服务器查看 Wiki。

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3, Quasar, TypeScript, Pinia |
| 导出 | Java (Starsector Mod API), org.json |
| 后处理 | Python 3 |

## 导出的数据类型

舰船、武器、船体插件、舰船系统、商品、工业设施、行星类型、市场状态、子市场、特殊物品、势力、星系、行星/空间站、人物。
