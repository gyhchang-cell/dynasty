# 雾中军阵·长城残影：独立静态建筑资产

奇观 #18 的原创建筑部分达到 **BUILDING_READY**：折线断墙、低宽主烽燧、两端不同残墩、马道、石阶与三面连接完整的静态残旗均已导出。完整奇观仍待主线接入及原生验证，本次未删除共享清单项。

本条为纯环境奇观。真实条目要求主世界古战场、晨雾、60 秒、中距离、远处旗影、微弱号角和 200 特效预算。当前源码把“晨雾”映射为主世界 `ruined_battlefield` 附近、dayTime 0..2500 与 RAIN；未新增天气系统。它与 #4 的近景兵俑制作分开，不添加人物、士兵、AI、战斗、奖励、任务或指南针逻辑。全局任务/指南针待办继续由原负责方处理，不列为本条纯环境奇观的完成条件。

## 实际资源

- 源：`tools/art/cod3/scenic_great_wall_echo.py`
- 标准压缩 NBT：`src/main/resources/data/dynasty/structures/scenic_great_wall_echo.nbt`
- 客户端 version 1：`src/main/resources/assets/dynasty/scenic/great_wall_echo.json`
- 真实条目及制作边界：`requirements.json`
- 坐标、旗挂点及建筑信息：`geometry.json`
- 44 项离线检查：`checks.json`
- 预览来源和原版纹理指纹：`preview.json`
- 最终文件指纹与主线接入事项：`BUILDING_READY.json`

**64×24×32** 声明边界，实际占用 `[0,0,0]` 至 `[63,22,27]`（方块位置包含两端，最高顶面 Y23）。共 **6,086** 个占用方块、**5,320** 个外露面，完整建筑低于 10,000 面。统计包含室内空腔面，不按展示相机删面。JSON 为 178,231 字节。

使用九种原版不透明静态完整方块：圆石、石砖、裂石砖、苔石砖、磨制安山岩、云杉原木、云杉木板、红羊毛、黑羊毛。原木三个 axis 状态完整保留，共十一条 palette 状态。无实体、方块实体、旗帜方块、容器、流体、门或发声/燃烧逻辑。所谓烽燧的干木料为静态原木，没有点火。本批没有生成自制贴图，也没有复制作者资源。

## 原创布局与返修

墙身沿 X 延伸，Z 方向逐段折转；墙顶由两端逐步抬向主烽燧。基础随墙线加宽收分，没有附带一整块展示地台。中央烽燧是横宽石台上的中空上室及平顶垛口，避免西式尖顶城堡的高细塔。西残墩保留较高后角、破损前墙；东残墩更低，保留另一侧残墙，二者并非同一塔换色镜像。

断损集中在墙端、少量女墙和残墩上缘。基础、墙身、压顶、柱角、横梁、旗杆和旗面全部在同一面连接体内。完整主体、主次体块与真实空腔均能在灰模和黑影中辨认，未借浓雾、粒子或发光掩盖建筑。

复查修正了两个具体问题：先清除伸入烽燧上室的原墙垛；再把挡住前后门洞视线的内部梯移到侧墙，重开对应顶板洞。现在正背门洞中线真实贯通，梯仍能通至屋顶。返修前证据保存在 `before-chamber-refinement/`。检查覆盖完整角墩、空腔、门洞贯通和入口至各平台的几何路径。

## 地面锚点与加载约定

| 字段 | 值 |
| --- | --- |
| 局部地面 / 基础最低底面 | Y0 |
| `centerPivot` | `[32,0,16]` |
| `anchor` | `[34,0,1]`，正面落脚台的地面标记 |
| `front` | `-Z` |
| 入口人物脚点 | `[34,1,1]` |
| 主烽燧上室脚点 | `[34,8,12]` |
| 主烽燧屋顶脚点 | `[38,15,20]` |
| 西残墩 / 东残墩脚点 | `[12,6,10]` / `[53,7,20]` |

NBT 与客户端 JSON 均未平移、缩小或预旋转。运行时按一次中心平移处理：

```text
world = groundCenter + rotation(local - [32,0,16])
```

入口 anchor 相对中心为 `[2,0,-15]`。Y0 是基础底面，入口台顶为 Y1，不能把二者混为同一个脚点。若保持一格一米，中心平移后的保守渲染 AABB 为 min `[-32,0,-16]`、max `[32,23,12]`（顶点边界），可用半径 **43** 的球保守包围；当前事件定义中的半径 29 不能直接作为本资产的完整裁剪界。实际世界地形落点、遮挡、朝向与裁剪由主线接入时验证。

version 1 schema 与前两批一致：`size / anchor / centerPivot / front / groundBlockY / palette / blocks / exposedFaces`。体素行为 `[x,y,z,paletteIndex]`，外露面行为 `[x,y,z,paletteIndex,direction]`。palette 保留完整原版 `Name` 与 `Properties`，不丢原木 axis。north=-Z、south=+Z、west=-X、east=+X、down=-Y、up=+Y。不得在读取时再次预减 pivot。

## 静态旗、远处旗影与动画边界

三面残旗均为完整方块组成的静态轮廓。旗面贴住完整竖杆，顶端横杆连接旗面和竖杆；旗杆底端直接落在实际平台，不是单独悬浮零件。

| 旗 | 竖杆底 / 顶（方块位置） | 旗面展开方向 |
| --- | --- | --- |
| 西残墩旗 | `[10,6,6]` / `[10,16,6]` | +X |
| 主烽燧旗 | `[34,15,18]` / `[34,22,18]` | +X |
| 东残墩旗 | `[54,7,20]` / `[54,16,20]` | +Z |

`geometry.json.flags` 逐一给出 `pole_bottom / pole_top / crossbar / static_cloth / attachment_line`，全部是同一套 NBT 局部坐标。远处旗影需要主线实现 LOD 选择/淡入淡出与原生观察验证；可由这些坐标选出竖杆、横杆、旗面体素，在相同世界锚点显示。若删除其余体素重建远景网格，应重新求选中体素的相邻面，不能假定全建筑外露面表仍是完整的远景面表。

本批**不包含飘旗动画**，也没有必须生成的可见实体。若主线另加飘旗，需保留现有竖杆和真实挂接线，先移除/隐藏对应 `static_cloth` 体素再绘制动画旗，避免双层重叠。侧旗法向不同，不能把三面旗都按同一朝向绘制。动画、远景 LOD、雾、号角、200 特效预算和 1,200 tick 生命周期均由主线处理；200 不是建筑面数。

## 本批参考：100 张，21 个作者图库

实际查看 279 张候选图，从 21 个项目图库选出 100 张。总计 283 个候选，13/18/25/58 号下载失败，未查看、未计入；历史重复图已排除。`references/selected-100.json` 逐图记录来源页、图片地址、缓存文件、SHA-256、实际看图记录与中文观察；`observations.txt` 是相同的 100 条观察。下载缓存不自动等于实际参考。

本批 100 个图片哈希互异，对前十二批共 **1,200** 条参考记录重合为 **0**，包含 #17 龙宫参考。十二份历史索引与指纹见 `references/prior-manifests.json`、`dedup.json`；检查重新验证了历史索引和选中缓存。计数单位为完整图片，并非 100 栋独立建筑或 100 个项目；同一建筑的不同视角可能分别入选，拼图只计一次。

主要结构观察及使用边界：

- [Ancient Structures: Chinese 作者图库](https://modrinth.com/datapack/ancient-structures-chinese-dp/gallery)：中式堡寨的塔墙衔接、上墙阶梯与旗杆落点，用于确定军防关系；不复制木寨布局、旗纹或建筑文件。
- [More Chinese Structures 作者图库](https://modrinth.com/datapack/more-chinese-structures/gallery)：低墙、高低体块与石台承托；本景观保留长墙主体，不改成村落或殿宇。
- [Dungeons and Taverns Pillager Outpost Overhaul 作者图库](https://modrinth.com/mod/dungeons-and-taverns-pillager-outpost-overhaul/gallery)：要塞围墙、前哨高低差和上墙路径；不使用其木塔模板。
- [Philip's Ruins 作者图库](https://modrinth.com/mod/philips-ruins/gallery)：缺顶、大断面、墙角厚度与残墙负空间，落实为两端不同残墩和集中断损。
- [Combat Structures 作者图库](https://modrinth.com/mod/combat-structures/gallery)：城墙基础与地势连续，不让墙或台脚悬空；舍弃西式尖塔与原布局。
- [Create: Let The Adventure Begin 作者图库](https://modrinth.com/mod/create-let-the-adventure-begin/gallery)：方塔、残堡、观察平台和入口的连接，只借结构关系，不引入 Create 方块或机械依赖。

其它来源与逐图取舍见索引。下界、末地、罗马或日式参考仅用于石体、门洞、墙脚和支承关系；实际输出保持中式边塞军防身份，不移植其文化装饰、尖顶、熔岩或悬空造型。没有取得或声称研究爱发电付费建筑资产。

## 软件复查与重现

最终十一张图均已实际查看：正、背、左、右、斜前五向，`gray.png`、`silhouette.png`、`dim.png`、`approach-40m.png`、`beacon-close.png`、`plan.png`。贴图图直接读取当前导出 NBT 和本机原版 1.20.1 的 16×16 PNG，逐面最近邻采样；原木端面按实际 axis 选择。原版纹理未复制到项目资源。灰模采用统一中性材质，不是彩色贴图去色；黑影包含全部 NBT 几何。

比例人物高 1.8 米，脚点 Y1，1 米石/木参照也落在真实入口平台；参照不进入 NBT。40 米入口透视图在平台上 1.62 米视高，垂直 FOV 70°。平面图背景表示没有导出体素，不是附加地板。软件照明、双面面片与无雾环境不能证明原生法线、裁剪、Atlas UV 朝向、透明混合、实际地形和多人效果；没有运行 Java 或原生游戏验证。

仓库根目录执行纯 Python 导出与核对：

```sh
python3 tools/art/cod3/scenic_great_wall_echo.py
python3 tools/art/cod3/scenic_great_wall_echo.py --check
```

本机已有 NumPy/Pillow、原版纹理缓存和只读软件帮助器，可重现预览，无需安装或启动 Java：

```sh
/Users/a15356015027/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 tools/art/cod3/scenic_great_wall_echo.py --review
```

44 项离线检查通过：格式/尺寸、静态原版方块、无实体载荷、确定性导出、源与产物一致、完整 palette 与未移位体素、全部外露面方向、面数、全体连通、角墩、空腔、门洞、三旗连通与原木 axis、非矩形基础、各平台几何路径、无 worldgen 注册、十二批索引稳定、100 张去重/缓存指纹，以及冻结 #17 与已验收 #14 的文件稳定性。运行时接入、晨雾/号角、远景 LOD、生命周期清理、原生客户端和多人验证仍由主线完成。

本次未改共享 Java 或清单、未放进世界、未注册 worldgen、未触用户存档、未动音量亮度、未提交或推送。冻结资产基线见 `protected-baseline.json`。

## 2026-10-20 主线整合验收完成

#18正式接入已加载古战场结构邻域与真实干燥地面，不放置NBT、不生成服务器实体。60秒/scale1，晨0…2500tick与现有RAIN晨雾替代映射；近景6086块5320面，远处原位3残旗92块290面，88…112m交叉淡化，最小粒子设置仅保留旗影。近24…40m与远176…224m渐隐，alpha上限0.52；范围按实际64×28×23m，不套旧29m形体半径。低声号角上限0.035/128m衰减；master=0未试听。新增粒子0低于200预算。

19项专用服务器检查和构建通过，20场景40张静音原生帧及人工复查看图通过：五向、近远/旗影/过渡、普通视高、天气时间、重载、晚到/重复包、两包只绘一座、贴近/坏地面/到期/离区清理。测试为一次性平坦主世界及真实注册的古战场StructureStart夹具，非自然触发频率或独立多人客户端证据，不覆盖用户存档。前12项资源与渲染类保持一致。

本项100张参考来自21项目，与前1200张零重复；累计13项1300张。两份清单仅删18号唯一行。最终包：build/cod3-great-wall-20261020/dynasty-1.4.0-cod3-scenic-20261020.jar；SHA256 2972c8cd5df4fc95d14d06162ff27a26bc219f5a8521d89a41276f3f06ac45d1。完整证据见docs/cod3/verification-20261020-great-wall-echo.json和native/。
