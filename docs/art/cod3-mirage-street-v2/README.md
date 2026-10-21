# 蜃楼幻市·荒野长街：独立静态建筑资产

2026-10-20。状态：**BUILDING_READY / 静态资源及离线检查完成；游戏接入与实机验收未完成。**
本目录不代表整条奇观任务 DONE，不作为删清单依据。

## 实际交付

- 可编辑原创源：`tools/art/cod3/scenic_mirage_street.py`
- 生产资源：`src/main/resources/data/dynasty/structures/scenic_mirage_street.nbt`
- 客户端生产资源：`src/main/resources/assets/dynasty/scenic/mirage_street.json`，资源位置 `dynasty:scenic/mirage_street.json`，由同一生成器导出。
- 布局、锚点、门位和灯位：`geometry.json`
- 实际 NBT 回读、连通性、可达性、资源哈希：`checks.json`
- 原版 PNG 来源、哈希、实际 NBT 软件预览：`preview.json`
- 对接状态和文件指纹：`BUILDING_READY.json`

建筑以四间错落铺屋夹一条古街，入口为双层檐门楼。茶铺、绸铺、香铺和客栈的宽度、进深、屋高不同；客栈有楼板、腰梁和二层窗。浅砂岩墙、深瓦、木梁为主，朱色与赭色旗签为辅。门、窗、街道与屋内空腔都是真实几何空隙，不使用黑面片假装洞口。旗签是附着横梁的静态方块，没有旗帜方块实体。

## 100 张新增参考的口径

`references/selected-100.json` 每条包含作者发布页、图片 URL、本地图片、SHA-256 和逐图中文观察。`references/observations.txt` 是精简阅读版，`references/dedup.json` 记录九批共900条既有记录的指纹与去重结果。100张选择图片互不重复，与900条既有参考的图片哈希交集为零。

本轮候选340张，成功下载334张；实际查看274张，最终选取100张建筑/环境图片。**这是100张图片，不是100个整合包，也不等于100座不同建筑**；同一聚落不同角度是独立图片，拼图无论内含多少子图都只计一次。没有把未查看的141–200号候选算入观察。未入选候选仅是检索留档。

追加与并行 `cod3-stone-god-v2/references/reference-index.json` 当前100张记录核对，交集同样为零；九批900条加石神100条共1,000条作为本批排重基准。石神索引指纹与核对结果见 `references/dedup.json` 和 `checks.json`。

最贴近目标的图包括 [Better Villages 沙漠集市与草原层檐聚落](https://modrinth.com/mod/better-village/gallery)、[Discoveria 的层檐建筑](https://modrinth.com/datapack/discoveria/gallery)、Moog's Voyager Structures 门架拼图；详见291、296、300、258、321、322号记录。其他风格仅用于柱梁支撑、门洞深度、街道留白、体量主次的比较，未复制模型、地图、贴图、独特建筑或转成西式城镇。

## 客户端读取约定

| 字段 | 数值/约定 |
|---|---|
| 资源ID | `dynasty:scenic_mirage_street` |
| 奇观编号 | 14 |
| NBT 声明尺寸 | 44 × 24 × 32，顺序为 x/y/z |
| 原点 | 最小局部方块角，标准结构NBT坐标 |
| 街口锚点 | `[22, 1, 0]` |
| 客户端渲染原点/旋转中心 | `centerPivot = [22, 1, 16]` |
| 正面 | `-Z`，由街口向内部沿 `+Z` |
| 局部地面方块 | y=0，其上表面/行走平面 y=1 |
| 中心原点变换后的地面 | 地面方块底部Y=-1，行走面Y=0 |
| 中街净空 | x=18…25、z=0…31，在y=1…3保持空，共8格宽 |
| 生产体素 | 3,648个非空气方块，单一LOD |
| 暴露面 | 7,370个单位面，包含底面；非帧率或性能实测 |
| 方块实体/实体 | 0 / 0 |
| 自定义贴图 | 0；仅原版不透明完整方块 |
| 灯位 | 6个静态蛙明灯方块体素；本资产不实现动态光照 |

主对话已确定世界变换为 `world = eventCenter + rotation(local - [22,1,16])`。JSON 的 `blocks` 与 `exposedFaces` **保留与NBT逐项相同的局部坐标，未预先减中心点**。渲染器只减一次 `centerPivot`。`anchor=[22,1,0]` 仅标记街口，变换后入口为 `[0,0,-16]`，不能当成当前渲染原点。

客户端只需读取 `assets/dynasty/scenic/mirage_street.json`，不再依赖客户端资源管理器访问 `data/`。NBT保留为同源结构校验产物，不用于世界放置。

JSON `version=1`，包含 `size/anchor/centerPivot/front/groundBlockY/palette/blocks/exposedFaces`。`palette` 完整保留NBT的 `Name` 与已有 `Properties`；`blocks` 为 `[x,y,z,paletteIndex]`；`exposedFaces` 为 `[x,y,z,paletteIndex,face]`。方向严格按原版：down=Y-、up=Y+、north=Z-、south=Z+、west=X-、east=X+。没有采用软件预览辅助器中相反的east/west标签。

仅剔除与相邻不透明完整方块共享的面；本批所有调色板材质都属于此类，即使相邻材质不同也剔除其内部面。底面、窗洞、内部空腔和外表面全部保留，不按摄影机方向猜测裁剪。UV不烘焙进JSON，主对话运行时读取原版atlas。JSON为稳定排序的紧凑UTF-8数据，179,562字节；实际方块、调色板和逐面数据已用回读NBT独立重建核对，重复导出字节一致。

**NBT 仅作为客户端视觉体素数据容器，绝不能调用结构放置API向玩家存档放街道。** 没有 `structure`、`structure_set` 或 `template_pool` 注册，也没有空气清除记录、容器、可交互门、告示牌、流体或实体。不要把透明度渐隐实现成改写方块。运行时宜预先缓存外露面，避免每帧遍历全部结构或创建数千个独立方块渲染调用；实际效果和耗时由主任务接入后验证。

主任务保留既有事件条件：主世界荒漠、深夜、晴天、90秒、中距离、单LOD、隐约集市声、效果预算80。80是事件效果预算，不能把它误解为建筑只能80个面。本交付只描述这些约定，不实现事件计时、声效、透明渐隐、同步、任务或指南针，也没有操作设备音量。

## 检查与返修

回读实际生产NBT，检查边界、无重复坐标、无实体/方块实体、原版完整方块白名单、3,648个方块与地面六邻接连通、中央街道净空以及四铺门洞到房内的地面可达性。源码重导出和回读结构一致，重复生成字节一致，并修正了不同Python版本 gzip 头部差异。追加客户端逐项一致性、方向/原点和石神去重检查后，共32项通过；NBT几何和哈希未变，原有真实NBT预览仍对应当前模型。

初版离线预览发现屋檐偏厚、孤立角块像城垛。第二版将檐边改为单层，阶梯连接处单独补厚；转角改为连续短挑檐，檐下增加木构承托，窗下补木质窗台。初版留在 `before-roof-refinement/`。修订后体素从3,938降到3,648，所有构件仍与地面连通，街道净宽和四铺可达性保持。

已实际查看修订后的正面、背面、左侧、右侧、45度、无纹理灰模、纯黑剪影、暗光和街内门面。街内图可以看到门、柜台、旗签与柱廊的真实厚度。门楼和各铺屋面在侧向会相互遮挡，这是四铺布局的正常空间关系；入口与街轴在正面剪影仍贯通。

全部PNG均是**软件预览，不是游戏截图**。正交图含原比例1.8米参照人与1米方块；参照人脚位为y=1，仅用于预览，不写入NBT。`street-24m.png` 使用1.62米视高和70度垂直FOV；`street-inside.png` 相机在局部z=8、同一视高。`gray.png` 使用统一中性材质，不是将材质转成灰度冒充灰模；`dim.png` 是减光检查，不模拟真实游戏夜间光照或幻景透明管线。

## 复现

无需 Java：

```sh
python3 tools/art/cod3/scenic_mirage_street.py
python3 tools/art/cod3/scenic_mirage_street.py --check
/Users/a15356015027/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 tools/art/cod3/scenic_mirage_street.py --review
```

预览依赖本地numpy、Pillow和已有只读软件栅格器，并从Minecraft 1.20.1本地资源ZIP读取原版PNG；不启动ZIP中的代码。本轮没有运行Java/Gradle，没有声音或亮度操作，没有打开、关闭、改写用户存档，没有提交或推送，没有修改共享Java和任务清单。

待主任务完成：客户端JSON加载及幽影网格渲染、中文任务/指南针对接核对、90秒淡入淡出与预算验证、昼夜及遮挡/透明排序/重载检查、单机和多人实机验证。未完成前，清单保留。

## 2026-10-20 主清单整合验收完成

以上建筑交付时待接入说明为历史状态。编号14已接入真实原版方块BakedQuad/图集和缓存外露网格，保持90秒、单LOD、至多一座可见街市。实际加载荒漠完整44x32占地检查，坡差≤2m，晴朗深夜16000…22000显示，近处24…40m淡出，160m远处消失。不放置NBT、不改地形、不生成实体、不覆盖全局雾效。使用客户端实际收到的MOTION_BLOCKING高度图；原地面与幽影铺地之间仅加1/64m渲染间距，修复共面闪烁。原版村民环境声充当低声集市提示，最大0.04/64m内衰减，保持master=0未听音。无新粒子，低于80上限。

13项专用服检查、最终构建、18个静音原生场景36张图通过；人工复看正侧背/近景/低特效/重载/晚到与显隐。实际JSON与NBT3648方块/7370外露面逐项一致。受控平坦荒漠为测试场地，不声称自然出现频率；未做单独多人客户端、中文任务或指南针对接。两份清单只删除14号唯一行，累计10项1000张不重复参考。最终包：build/cod3-mirage-street-20261020/dynasty-1.4.0-cod3-scenic-20261020.jar；SHA256 85da74d104820b1d490d27a2b085549a4c148509d0b6a1e018e1f7673a6d3778。详见docs/cod3/verification-20261020-mirage-street.json和native/。
