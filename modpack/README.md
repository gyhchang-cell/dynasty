# Dynasty 王朝 · 整合包（Minecraft 1.20.1 / Forge 47.4.10）

## 建筑与地点汉化更新（2026-09-21）

皇家宫殿新区域生成64×64院落，增加藏书侧殿、锻造工坊、池桥与亭园；帝陵增加四侧室与回路，观星台改为双层与立体浑天仪。已有建筑不会自动覆盖，无需删除存档。探索者罗盘的六项王朝建筑已显示中文；科举试卷、徽墨、竹简更新图标。请重启当前实例，进入尚未生成的区域查看新建筑。

实际渲染、验证范围与前后对比：[建筑重制展示](../docs/art/architecture-remaster-v3/gallery.html)。

第二章开头新增罗盘教程：持有四块圆石后领取两个原版指南针，再合成自然罗盘与探索者罗盘。中心指南针、上下左右分别原木/圆石，四角留空。两种罗盘也在王朝创造栏中，中文名称包含“指南针”。新增模组或更换 JAR 后须重启游戏。

## 罗盘导航与 Boss 外形（2026-09-21）

两种罗盘均已收录。输入 `/dynasty_find` 打开王朝目的地菜单：主手拿探索者罗盘找建筑，拿自然罗盘找 Boss 栖息生物群系；先进入对应维度。
栖息区不保证出现 Boss，也不是远程实体追踪。龙帝与九霄天将新增实体悬浮装饰及护甲轮廓。
详见 [使用说明与验证范围](../docs/content/compass-boss-regalia-v1.md)。

## 建筑扩建（2026-09-21）

新生成国子监扩至 46×46，增加讲堂、附魔藏书区、工坊、炼药角、双池木桥及长廊。
宫殿正门和主殿补充台阶、屋檐、水景及可用陈设，保持中央通道畅通。
已生成建筑不自动替换；详见 [本轮建筑说明](../docs/content/architecture-remaster-v2.md)。
修复机关方块启动注册错误和星盘物品 ID 冲突；没有改机关玩法或新增自然机关房。

## 饰品与任务重制（2026-09-18）

169 件饰品按九类标准槽佩戴，已移除「王朝饰品」专属槽。分类槽各 1 格、戒指 2 格，万能槽初始 1 格。
完成「科举中第」「首次击败叛将」「踏入天朝」「斩帝」「沧海定波」五项里程碑，各永久 +1 万能槽，共 6 格。
安装 Curios 时饰品必须佩戴才生效。里程碑死亡保留、重复领取不叠加，旧档已完成任务自动补发。

饰品效果自第三十四轮起是「v2 格式」：一件饰品可以带两个不同条件的面
（例：破晓刃坠白天攻击 +22%、夜里移速 +10%），代价型设计用「生命上限 %」和**模组自有效果「内伤」**，
不再给自己套原版药水。格式与编码表见 [饰品与任务重制](../docs/饰品与任务重制.md)。

任务书现为 12 章 488 条：目标、路线、玩法提示和奖励分段显示；饰品任务标注部位；金色六边形突出加槽里程碑；修复放射节点相互遮挡。
完整规则与验收方法见 [饰品与任务重制](../docs/饰品与任务重制.md)。

## 📦 要上传整合包？直接用 `dist/` 里这三个文件

| 文件 | 上传到哪 | 说明 |
| --- | --- | --- |
| `dist/dynasty-modpack-1.4.0.zip` | **CurseForge** → 新建项目 → 类型选 **Modpack** | CF 格式：`manifest.json` 里用项目/文件 ID 引用 4 个核心模组（Curios/JEI/血条库），其余 24 个优化·便利·生存模组与本体一起打进 `overrides/mods/` |
| `dist/dynasty-1.4.0.mrpack` | **Modrinth** → 新建项目 → 类型选 **Modpack** | Modrinth 格式：`modrinth.index.json` + CDN 下载地址 + 哈希 |
| `dist/dynasty-1.4.0-manual.zip` | 网盘 / 群 / 服务端 | 免启动器手动包：`mods/` 里就是 29 个 jar |

步骤与注意事项见 **[`docs/upload.md`](../docs/upload.md)**（含审核可能要求"本体也发布成独立模组"时怎么办）。
**上传时选的是上面这几个文件（zip / mrpack），不是文件夹。**

---

本整合包以 **我们自己的《Dynasty 王朝》模组**为绝对主体，另外借用几个成熟开源模组补足体验：

| 模组 | 版本 | 作用 | 许可 |
| --- | --- | --- | --- |
| **Dynasty 王朝**（本体） | 1.4.0 | 王朝、4 个自建维度、科举、军队、神兽、Boss、兵器甲胄与 119 件饰品；标准分类槽 + 任务成长万能槽 | 本项目 |
| **Curios API** | 5.14.1+1.20.1 | 119 件饰品使用九类标准槽与任务解锁的万能槽 | LGPL-3.0 |
| **Overflowing Bars** | 8.0.1 | **更美观的血条/护甲条/饥饿条**（生命溢出显示、分段配色） | 开源 |
| **Puzzles Lib** | 8.1.33 | Overflowing Bars 的前置库 | 开源 |
| **JEI** | 15.59.0.210 | 配方查询：所有王朝配方都能在 JEI 里查到，与我们的「图鉴」页互补 | MIT |
| **Embeddium** | 0.3.31 | **帧数优化**（Sodium 的 Forge 移植版，替换原版渲染管线） | LGPL-3.0 |
| **FerriteCore** | 6.0.1 | 降低内存占用（方块状态去重） | MIT |
| **ModernFix** | 5.27.83 | 启动提速 + 内存优化（动态资源 / 并行加载） | LGPL-3.0 |
| **Entity Culling** | 1.10.5 | 实体渲染剔除：看不见的实体不渲染，帧数明显提升 | MIT |
| **ImmediatelyFast** | 1.5.5 | 即时渲染优化（GUI/文字/实体批量提交） | LGPL-3.0 |
| **Clumps** | 12.0.0.4 | 经验球合并，大规模刷怪不卡 | MIT |
| **Memory Leak Fix** | 1.1.5 | 修复原版与 Forge 的内存泄漏 | LGPL-3.0 |
| **Jade** | 11.13.3 | 准星指向即显示方块/生物信息（替代 WAILA） | 开源 |
| **AppleSkin** | 2.5.1 | 显示饱食度/饱和度/食物回复量 | 开源 |
| **Mouse Tweaks** | 2.25.1 | 鼠标拖拽整理物品栏 | 开源 |
| **Crafting Tweaks** | 18.2.9 | 合成台一键整理 / 轮换配方 | 开源 |
| **Corpse** | 1.0.23 | **死亡不掉装备**：掉落物进尸体，跑回去全拿回 | LGPL-3.0 |
| **Waystones** | 14.1.21 | **传送石**：激活后可跨地图传送（+ Balm 前置） | 开源 |
| **Explorer's Compass** | 1.4.0 | 结构指南针：直接搜宫殿 / 帝陵 | 开源 |
| **Nature's Compass** | 1.12.0 | 群系指南针：搜天朝平原 / 地府等群系 | 开源 |
| **Xaero's Minimap / World Map** | 26.5.0 / 1.46.0 | 小地图 + 大地图（客户端） | 免费 | 
| **Comforts** | 6.4.0 | 睡袋 / 吊床，不用床也能过夜 | 开源 |
| **RightClickHarvest** | 4.6.1 | 右键收割成熟作物（+ Architectury、JamLib 前置） | LGPL-3.0 |
| **ToroHealth (Updated)** | 1.20.1 | **伤害数字显示**，打得准不准一眼看出 | 开源 |
| **TorchMaster** | 20.1.9 | 火把大师：范围阻止刷怪，营地更安全 | 开源 |
| **FTB Quests** | 2001.4.22 | 12 章 438 条任务、846 条前置，0 环；分段引导、节点避让、五项万能槽奖励；物品 / 击杀 / 维度 / 成就自动判定 | 开源 |
| **FTB Library** | 2001.2.13 | FTB 系列前置库 | 开源 |
| **FTB Teams** | 2001.3.2 | FTB 任务书的**强制前置**（本体代码会把它的「My Team」侧边栏按钮隐藏，界面更干净） | 开源 |
| **Item Filters** | 2001.1.0-build.59 | FTB 任务筛选器（**必须 build.55+**，Modrinth 只有 build.53 会导致启动失败） | 开源 |
| **Architectury API** | 9.2.14 | FTB / RightClickHarvest 的前置 | LGPL-3.0 |

> **任务书怎么开**：右键「任务书」物品，或按「Open Quests」键（默认可能未绑定，去
> `选项 → 控制 → FTB Quests` 里确认/设置）。**12 章 438 条**，
> 左侧栏按 **3 组**分好类（可折叠，和「愚者 / 登神者」一个样子），
> 各章按兵器流派、甲胄部位、材料与玩法拆成多条支线，节点按重要性区分大小与形状，
> 多条线可以同时推进；章与章之间相连（章首 ← 上一章末尾）：
>
> | 分组 | 章节 | 条数 | 主题 |
> | --- | --- | --- | --- |
> | 王朝主线 | 一、初入王朝 | 29 | 兵器、冶炼、文书、货币 |
> | 王朝主线 | 二、农桑百工 | 33 | 图鉴、庖厨、营造、符箓、丹药 |
> | 王朝主线 | 三、朝堂科举 | 29 | 科举中第解锁万能槽 |
> | 王朝主线 | 四、军旅与平叛 | 39 | 初胜叛将解锁万能槽 |
> | 王朝主线 | 五、神兽与帝王 | 29 | 神兽与帝王挑战 |
> | 万里山河 | 六、天朝·龙庭 | 24 | 踏入天朝解锁万能槽 |
> | 万里山河 | 七、地府幽冥 | 31 | 幽冥探险与装备 |
> | 万里山河 | 八、九霄天界 | 20 | 天将与天界宝物 |
> | 万里山河 | 九、东海龙宫 | 19 | 沧海定波解锁万能槽 |
> | 神兵宝甲 | 十、兵器谱 | 49 | 兵器流派、斩帝里程碑解锁万能槽 |
> | 神兵宝甲 | 十一、甲胄谱 | 68 | 部位与轻重甲升级链 |
> | 神兵宝甲 | 十二、饰品图鉴 | 68 | 饰品功能、佩戴部位与搭配 |
>
> 每章还有一句**副标题**（标题下面那行小字）；任务节点按重要性换形状：
> 章首是**齿轮**、章末是**六边形**、支线起点是**菱形**、其余是**圆点**。
>
> **四个维度**：天朝·龙庭（天朝传送门）/ 地府（地府传送门）/ 九霄天界（九霄传送门）/ 东海龙宫（龙宫传送门）。
>
> **Boss 六个**：龙帝、叛将、宦官首脑、亡故始皇、九霄天将、东海龙王 —— 大招都会提前 1 秒预警。
>
> **任务只有 FTB 任务书这一处**（模组自带的「✦ 王朝任务」界面已删除）。
>
> **官阶（20 阶）**：布衣 → 童生 → 秀才 → … → 大学士 → 丞相 → 摄政王 → **天子**。
> 功名门槛每阶递增 25 点；每升一阶 **+2 生命 / +0.25 攻击 / +0.25 护甲**，
> 官阶提供属性；万能饰品槽通过五个关键任务永久解锁，初始 1 格 → 完成后 6 格。
> **功名主要靠打怪（Boss +220~300）、与 NPC 交互、第一次获得新物品**，任务只给一点点。
>
> **开局只送《王朝说明书》**：左边是可折叠的**分组目录**（开始·上车 / 王朝·仕途 /
> 兵甲·装备 / 世界·探索 / 收尾），右边是正文，共 **34 页**玩法说明
> （开局路线、功名来源、饰品槽位、Boss 打法与预警、资源分布、卡点排查）。


>
> **任务规则（1.4.0 改版）**：
> 1. **严格前置** —— 每条任务依赖上一条，前一条没完成，后面的会锁着（跨章节同理）。
> 2. **不用自己点完成** —— 物品（带在身上即算）、击杀计数、进过维度、成就（真做过才发）四种自动判定，
>    原来那些 `checkmark`（玩家自己点勾）已经全部去掉。
> 3. **物品不用上交** —— `config/ftbquests/quests/data.snbt` 里 `default_consume_items: false`，
>    只判定「有没有做出来」，物品不会被收走（**奖励会自动领取**，`default_autoclaim_rewards`）。
> 4. **奖励是物品 + 经验 + 功名** —— 铜钱/金锭/龙鳞/龙晶……终盘给**下界之星**与天子剑材料。
> **任务界面只有 FTB 任务书这一处**（模组自带的「✦ 王朝任务」界面已经删掉）。
>
> **Boss 想反复打就用「法阵·祭坛」**：玉石块×4 + 龙晶合成；四周 3×3 环里放 4 块玉石块成形，
> 拿着 Boss 掉落的信物（龙帝玉玺 / 叛将首级 / 内廷令牌 / 帝骸骨）右键即可再召唤一次。

### 参考「愚者」整合包筛出来的辅助模组（均不含玩法内容）

| 分类 | 模组 |
| --- | --- |
| 性能 | Noisium（世界生成）、Radium（服务端逻辑）、Saturn（内存）、Async Locator（结构搜索异步）、All The Leaks（内存泄漏）、Spark（分析器） |
| 界面 | Better Advancements、Controlling + Searchables、Legendary Tooltips + Iceberg + Prism、Great Scrollable Tooltips、Item Borders |
| 信息 | Just Enough Resources、Enchantment Descriptions + Bookshelf、**Just Enough Characters（拼音搜索）**、Travelers Titles + Yungs API、Tips |
| 操作 | Trash Slot、Construction Wand、Shoulder Surfing Reloaded（**Inventory Profiles Next 已移除**：它的按钮挡住背包左上角的任务入口） |
| 生存 | Sophisticated Backpacks + Core、Polymorph（配方冲突）、AttributeFix、Yeetus Experimentus、CustomSkinLoader |

> 「愚者」里的 Create / 暮色森林 / Alex's Mobs / 各种魔法与枪械等**内容模组一律没有加**，
> 拆掉任何一个辅助模组都不会影响本体运行。

> 连锁采掘（挖矿/砍树连带）已经**做进本体**：按住潜行破坏矿石或原木即可连锁，
> 所以整合包不再需要 Vein Mining（避免双重触发），详见说明书第 16 页。

> 以上优化与便利模组**都不改玩法**（不新增内容、不改数值、不加合成），只是让游戏更流畅更好用；
> 若你不想要其中某一个，直接删掉对应的 jar 即可，本体与整合包都不会崩。

> 饰品本体、数值、效果全部是我们自己的（`Dynasty` 内实现），Curios 只提供槽位与穿戴系统。
> 饰品**只放 Curios 槽位**：九类标准槽 + 任务成长万能槽，没有「王朝饰品」专属槽。安装 Curios 时背包和副手不提供饰品效果。
> **27 件饰品除了合成，还能从建筑宝箱里开出来**：宫殿遗迹 / 宝塔 / 长城城楼用 `palace_ruin`，
> 帝陵与神庙主殿用 `imperial_mausoleum`，另有神庙 `temple`、天罡法阵 `ritual_circle`、
> 兵营 `barracks`、烽火台 `watchtower` 四张专属战利品表（饰品池 50% 概率触发、按权重抽取）。

---

## 一、怎么装（普通玩家）

### 方式 A：直接放 mods 文件夹（最稳，推荐 PCL2 / HMCL）
1. 用启动器安装 **Minecraft 1.20.1 + Forge 47.4.10** 的隔离实例。
2. 把 `modpack/mods/` 里的 **全部 29 个 jar** 复制到该实例的 `mods/` 目录。
3. 启动游戏。首次进世界会收到 **王朝说明书**；右键「任务书」或按 Open Quests 键看 FTB 任务，饰品放进 Curios 槽位即可。
4. 键位：按 `E` 打开背包 → 左侧 Curios 的饰品槽（或点 Curios 标签）→ 把玉佩/玉璧等拖进去，效果立即生效。

### 方式 B：用启动器导入
* **Prism / MultiMC / ATLauncher（Modrinth 格式）**：把 `modpack/` 整个目录（含 `modrinth.index.json`）作为 Modrinth 整合包导入。
* **CurseForge 启动器**：看 `modpack/curseforge-manifest.json`（列出文件名、下载地址与 sha1）。若导入不识别，请用方式 A。
* **缺模组时**：运行 `modpack/download_mods.sh`（Mac/Linux）一键补齐。

### 方式 C：服务器
服务端与客户端都放这 29 个 jar（Curios 两端都要；JEI / Overflowing Bars / Puzzles Lib 主要给客户端）。

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
├── mods/                     29 个 jar（dynasty 本体 + 28 个第三方：饰品槽/配方/血条/优化/生存便利）
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
3. 启动游戏即可。首次进入世界会收到 **王朝说明书**，任务与饰品见上面的说明。

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
