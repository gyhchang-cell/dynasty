# Dynasty 王朝 · 整合包（Minecraft 1.20.1 / Forge 47.4.10）

## 📦 要上传整合包？直接用 `dist/` 里这三个文件

| 文件 | 上传到哪 | 说明 |
| --- | --- | --- |
| `dist/dynasty-modpack-1.4.0.zip` | **CurseForge** → 新建项目 → 类型选 **Modpack** | CF 格式：`manifest.json` 里用项目/文件 ID 引用 4 个开源模组，我们本体在 `overrides/mods/` |
| `dist/dynasty-1.4.0.mrpack` | **Modrinth** → 新建项目 → 类型选 **Modpack** | Modrinth 格式：`modrinth.index.json` + CDN 下载地址 + 哈希 |
| `dist/dynasty-1.4.0-manual.zip` | 网盘 / 群 / 服务端 | 免启动器手动包：`mods/` 里就是 5 个 jar |

步骤与注意事项见 **[`docs/upload.md`](../docs/upload.md)**（含审核可能要求"本体也发布成独立模组"时怎么办）。
**上传时选的是上面这几个文件（zip / mrpack），不是文件夹。**

---

本整合包以 **我们自己的《Dynasty 王朝》模组**为绝对主体，另外借用几个成熟开源模组补足体验：

| 模组 | 版本 | 作用 | 许可 |
| --- | --- | --- | --- |
| **Dynasty 王朝**（本体） | 1.4.0 | 全部玩法：王朝、维度、科举、军队、神兽、Boss、任务/图鉴、兵器进化链、饰品 | 本项目 |
| **Curios API** | 5.14.1+1.20.1 | **饰品槽位**：我们的 10 件饰品直接放进 Curios 的 charm / necklace / ring / belt / head / curio 槽 | LGPL-3.0 |
| **Overflowing Bars** | 8.0.1 | **更美观的血条/护甲条/饥饿条**（生命溢出显示、分段配色） | 开源 |
| **Puzzles Lib** | 8.1.33 | Overflowing Bars 的前置库 | 开源 |
| **JEI** | 15.59.0.210 | 配方查询：所有王朝配方都能在 JEI 里查到，与我们的「图鉴」页互补 | MIT |

> 饰品本体、数值、效果全部是我们自己的（`Dynasty` 内实现），Curios 只提供槽位与穿戴系统。
> 我们的本体对 Curios 是**软依赖**：没有 Curios 时自动退回自带的「百宝妆匣」6 槽位，不会崩。

---

## 一、怎么装（普通玩家）

### 方式 A：直接放 mods 文件夹（最稳，推荐 PCL2 / HMCL）
1. 用启动器安装 **Minecraft 1.20.1 + Forge 47.4.10** 的隔离实例。
2. 把 `modpack/mods/` 里的 **全部 5 个 jar** 复制到该实例的 `mods/` 目录。
3. 启动游戏。首次进世界会收到 **王朝说明书** 与 **百宝妆匣**，跟着任务走即可。
4. 键位：按 `E` 打开背包 → 左侧 Curios 的饰品槽（或点 Curios 标签）→ 把玉佩/玉璧等拖进去，效果立即生效。

### 方式 B：用启动器导入
* **Prism / MultiMC / ATLauncher（Modrinth 格式）**：把 `modpack/` 整个目录（含 `modrinth.index.json`）作为 Modrinth 整合包导入。
* **CurseForge 启动器**：看 `modpack/curseforge-manifest.json`（列出文件名、下载地址与 sha1）。若导入不识别，请用方式 A。
* **缺模组时**：运行 `modpack/download_mods.sh`（Mac/Linux）一键补齐。

### 方式 C：服务器
服务端与客户端都放这 5 个 jar（Curios 两端都要；JEI / Overflowing Bars / Puzzles Lib 主要给客户端）。

---

## 二、能不能用 IDEA 跑？（重要）

**能，但要分清"开发环境"和"整合包本体"：**

| 场景 | 做法 | 结果 |
| --- | --- | --- |
| 开发/调试本体 | 在本文件夹用 IDEA 打开 → Gradle → `runClient` / `runServer` | ✅ 可用。Curios 是 `compileOnly` 编译依赖，本体在没有第三方模组时**优雅降级**（饰品走自带妆匣），日志会打印 `Curios not present - trinkets use the built-in pouch` |
| 想连第三方模组一起在 IDEA 里跑 | 不建议 | ❌ Curios / Puzzles Lib / Overflowing Bars 都是 **Mixin 模组**，它们的 Mixin 目标名是 SRG 名称，在 official 映射的开发环境里无法应用（Forge 开发环境已知限制，实测 `Mixin apply failed ... f_19803_`）。这与本模组无关 |
| 真正玩整合包 | 用启动器（方式 A/B） | ✅ 生产环境映射正常，5 个模组同时生效：Curios 饰品槽 + 美化血条 + JEI + 王朝本体 |

> 一句话：**IDEA 用来开发本体；整合包用启动器玩。**（IDEA 里 Gradle 面板点 ↻ 重新导入后即可运行 `runClient`。）

---

## 三、目录说明

```
modpack/
├── mods/                     5 个 jar（dynasty 本体 + Curios + JEI + OverflowingBars + PuzzlesLib）
├── config/                   配置（首次启动后各模组写入自己的配置）
├── modrinth.index.json       Modrinth 格式清单（含下载地址与 sha1/sha512）
├── curseforge-manifest.json  CurseForge 风格清单
├── download_mods.sh          一键重新下载第三方模组
└── README.md                 本文件
```

## 四、第三方模组来源（均为公开发布的开源/免费模组）

* Curios API — https://modrinth.com/mod/curios （作者 C4，LGPL-3.0）
* Overflowing Bars — https://modrinth.com/mod/overflowing-bars
* Puzzles Lib — https://modrinth.com/mod/puzzles-lib
* JEI — https://modrinth.com/mod/jei （作者 mezz，MIT）

若某位作者希望调整引用方式，告知我会立刻替换或移除对应条目。


> 饰品本体、数值、效果全部是我们自己的（`Dynasty` 内实现），Curios 只提供槽位与穿戴系统。

---

## 一、怎么装（普通玩家）

### 方式 A：直接放 mods 文件夹（最稳，推荐 PCL2 / HMCL）
1. 用启动器安装 **Minecraft 1.20.1 + Forge 47.4.10** 的全新版本/隔离实例。
2. 把 `modpack/mods/` 里的 **全部 4 个 jar** 复制到该实例的 `.minecraft/mods/` 目录。
3. 启动游戏即可。首次进入世界会收到 **王朝说明书** 与 **百宝妆匣**，跟着任务走。

### 方式 B：用启动器导入整合包
* **Prism / MultiMC / ATLauncher（支持 Modrinth 格式）**：把整个 `modpack/` 目录（含 `modrinth.index.json`）作为一个 Modrinth 整合包导入。
* **CurseForge 启动器**：见 `modpack/curseforge-manifest.json`（我用它列了文件名、下载地址与 sha1；CF 启动器要求项目 ID，若导入不识别，请用方式 A）。
* **缺少模组时**：运行 `modpack/download_mods.sh`（Mac/Linux）或按 README 表格里的下载地址手动下载。

### 方式 C：服务器
把 4 个 jar 放进服务端 `mods/`，客户端同样放 4 个（Curios 与本体必需，JEI / Overflowing Bars 客户端装即可）。

---

## 二、能不能用 IDEA 跑？

**能**，但 IDEA 跑的是"开发环境"，不是整合包本体：

| 目的 | 怎么做 | 说明 |
| --- | --- | --- |
| 开发/调试本体 | 在工程根目录（本文件夹）用 IDEA 打开，点 Gradle → `runClient` | 第三方模组通过 `build.gradle` 里的 `libs/repo` 本地 Maven + `fg.deobf` 自动加载，**不需要**手动放 mods |
| 连带整合包一起调试 | 同上，`libs/repo` 里已含 Curios / JEI / OverflowingBars 的反混淆版本 | 三者在 `dependencies` 里，`runClient` 时会一起进游戏 |
| 真正玩整合包 | 用启动器（方式 A/B） | 开发环境有映射差异，个别第三方模组可能报错，不建议拿来长期游玩 |

IDEA 里第一次打开如果报错，执行一次 **Gradle 重载**（右侧 Gradle 面板 ↻），再运行 `runClient`。

---

## 三、目录说明

```
modpack/
├── mods/                     4 个 jar（本体 + Curios + JEI + OverflowingBars）
├── config/                   整合包配置（首次启动后各模组会写入自己的配置）
├── modrinth.index.json       Modrinth 格式整合包清单（含下载地址与哈希）
├── curseforge-manifest.json  CurseForge 风格清单
├── download_mods.sh          一键重新下载第三方模组
└── README.md                 本文件
```

## 四、第三方模组来源（均为公开发布的开源/免费模组）

* Curios API — https://modrinth.com/mod/curios （作者 C4，LGPL-3.0）
* Overflowing Bars — https://modrinth.com/mod/overflowing-bars
* JEI — https://modrinth.com/mod/jei （作者 mezz，MIT）

若你是模组作者并希望调整引用方式，请告知，我会立刻替换或移除对应条目。
