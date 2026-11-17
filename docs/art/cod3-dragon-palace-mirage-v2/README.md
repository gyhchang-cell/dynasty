# 水中倒城·龙宫幻影：独立建筑资产

奇观 #17 的原创正立水府资产已导出，独立建筑部分达到 BUILDING_READY。整项奇观仍为 PARTIAL：运行时加载、实际水面倒影、客户端原生画面、任务与中文指南针的接入由主任务继续验证。本目录的软件预览不能作为这些环节通过的证据，未据此删除完整奇观清单项。

## 实际文件与形态

- 可编辑源：`tools/art/cod3/scenic_dragon_palace_mirage.py`
- 标准结构 NBT：`src/main/resources/data/dynasty/structures/scenic_dragon_palace_mirage.nbt`
- 客户端 version 1 数据：`src/main/resources/assets/dynasty/scenic/dragon_palace_mirage.json`
- 几何与坐标：`geometry.json`；离线检查：`checks.json`；预览来源：`preview.json`
- 交付指纹与接入待办：`BUILDING_READY.json`

建筑采用中央重檐主殿、三级台基、入口双阙和两条低水廊。中轴桥接至主殿，两侧水庭留空；柱、梁、檐、屋脊和台阶组成连续支撑。主殿有三间正面开口、侧窗和内部空腔。它是独立轴线式宫殿设计，未以先前四铺街市换色或重排代替水府。原版海晶石屋面、白石台柱、深木檐梁形成水府材质层次，不增加人物、怪物或自制贴图。

声明边界为 **48×24×40**；实际占用从 `[4,0,0]` 至 `[43,22,37]`（方块坐标包含两端，最高方块顶面 Y23）。共有 **4,976** 个方块、**7,726** 个外露面，采用单一 LOD。外露面包含室内空腔面，未按展示相机删面。八种材料均为原版不透明静态完整方块，保留 `quartz_pillar` 的 `axis=y`。无实体、方块实体、容器、门、流体或逻辑方块；NBT 未注册为自动生成结构，也未放置进世界。几何路径检查代表桥与台阶的结构合理性，不表示视觉幻影具有世界碰撞。

## 水线与接入坐标

| 字段 | 值与含义 |
| --- | --- |
| 局部水面 | `Y=0`，也是最低基础方块的底面 |
| `centerPivot` | `[24,0,20]`，运行时定位到真实水面中心 |
| `anchor` | `[24,0,0]`，入口水线标记，非行走脚点 |
| `front` | `-Z`，沿 `+Z` 进入主殿 |
| `groundBlockY` | `0`，基础最低层；不等于桥面高度 |
| 桥廊脚点 | `Y=2` |
| 主殿地面脚点 | `Y=4` |

NBT 与 JSON 都保留同一套未平移局部坐标。运行时使用：

```text
world = waterCenter + rotation(local - [24,0,20])
```

不要在读取前再次减去旋转中心。入口水线标记变换前相对中心为 `[0,0,-20]`。资产保持正立，未预先翻转、生成镜像副本或反转法线。主任务须在实际水面执行倒影变换，并分别核对镜像后的绕序、法线、裁剪和深度。

客户端 JSON 与街市交付采用相同 version 1 schema：`size / anchor / centerPivot / front / groundBlockY / palette / blocks / exposedFaces`。`blocks` 为 `[x,y,z,paletteIndex]`，`exposedFaces` 为 `[x,y,z,paletteIndex,direction]`；`palette` 保留完整 `Name` 与 `Properties`。方向采用原版坐标：north=-Z、south=+Z、west=-X、east=+X、down=-Y、up=+Y。

宿主事件约定为 `dynasty:dragon_palace`、中距离、1,200 tick（60 秒）、单 LOD、150 特效预算和水域环境音。**150 是运行时特效预算，不是建筑面数。** 本次不新增发声行为，也没有播放音效。

## 本批 100 张参考

实际查看 234 张候选图，从 16 个作者项目图库选出 100 张；235 个候选中第 29 张下载失败，未计入。`references/selected-100.json` 逐张记录作者图库页、图片地址、本地缓存、SHA-256 与中文观察；`observations.txt` 提供便读记录。与前十一批共 1,100 条参考记录比对，本批 100 个图片哈希互异、历史重合为 0；历史索引指纹保存在 `prior-manifests.json` 和 `dedup.json`，离线检查重新核对了缓存及历史索引。

计数单位为完整图片，不代表 100 个独立项目或 100 栋不同建筑。同一建筑的不同视角可能分别入选，一张拼图只计一张。联系表是实际看图记录，不以下载成功替代观察。

主要借鉴与落地：

- [Dungeons and Taverns Ocean Monument Overhaul 作者图库](https://modrinth.com/mod/dungeons-and-taverns-ocean-monument-overhaul/gallery)：水下宽台基、低廊与高主体的层级，落实为三级台基和主殿/水廊的高度差。
- [Repurposed Structures Better Ocean Monuments Compat 作者图库](https://modrinth.com/mod/repurposed-structures-better-ocean-monuments-compat/gallery)：柱间开口和海晶材料分层，落实为真实廊道空隙及深浅青屋面。
- [ATI Structures 作者图库](https://modrinth.com/mod/ati-structures-fabricforge/gallery)：水域建筑与平台的接触、主体与侧翼关系；不移植圆顶、异域立面或原图布局。
- [Shrines 作者图库](https://modrinth.com/mod/shrines/gallery)与 [Japanese Temple 作者图库](https://modrinth.com/mod/japanese-temple/gallery)：观察阶梯屋盖、檐下承托和柱距；实际组织为本项目的中式轴线殿阙，不复制对方文化标识或专属造型。
- [Moog's Temples Reimagined 作者图库](https://modrinth.com/mod/mtr-moogs-temples-reimagined/gallery)与 [Philip's Ruins 作者图库](https://modrinth.com/mod/philips-ruins/gallery)：水下轮廓、入口与遗迹体块读图，保留清楚的中央桥与开放水庭。

其余来源、逐图取舍和未采用的元素均见索引。本轮没有取得爱发电付费资产，不声称研究了不可访问的内容；未复制作者建筑文件、纹理或模型。

## 软件图与返修

`front.png / back.png / left.png / right.png / three-quarter.png` 为五向图，另有 `gray.png / silhouette.png / dim.png / approach-28m.png / plan.png`。十张最终图均经过实际查看。灰模使用统一中性材质，黑影直接来自真实 NBT 几何，不依赖粒子、水雾、倒影或发光遮挡主体。

贴图图从当前导出 NBT 和本机原版 1.20.1 PNG 逐面采样，以最近邻显示。原版纹理哈希及文件来源记录在 `preview.json`；海晶灯动态 PNG 仅取第 0 帧用于静态软件预览。未把原版纹理复制进交付资源。预览人物高 1.8 米，脚点在真实桥面 Y2，旁置 1 米方块；这些参照不进入 NBT。入口透视图在入口前 28 米，视高为桥面上 1.62 米，垂直 FOV 为 70°。平面图浅蓝表示未导出体素的空处，不是输出水块。

复查已修正廊灯与檐之间的连接件，并收窄原本切断两根柱身的侧窗，补回六个柱段。`before-column-refinement/` 保存修柱前的检查与图片，最终文件以本目录及交付指纹为准。柱身连续检查已加入生成器。

这些是离线软件图，光照与暗光均为软件照明。未运行 Java/Gradle 或原生客户端，不能证明实际水下雾、透明混合、反射法线、深度、特效生命周期和多人观察效果。接入后的原生验证仍需主任务完成。

## 重现

在仓库根目录，纯 Python 导出及核对不启动 Java：

```sh
python3 tools/art/cod3/scenic_dragon_palace_mirage.py
python3 tools/art/cod3/scenic_dragon_palace_mirage.py --check
```

软件预览需 NumPy、Pillow、现有只读 `tools/art/boss-forms/texture_review.py` 和本机原版纹理缓存。本机可直接使用已有依赖，无需安装：

```sh
/Users/a15356015027/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 tools/art/cod3/scenic_dragon_palace_mirage.py --review
```

36 项离线检查通过，包括确定性压缩 NBT、源/产物一致、JSON 完整调色板与体素一致、所有外露面方向一致、面数、全体连通、每根柱身完整、水庭留空、主殿空腔、入口/主殿/双阙/双廊路径，以及参考去重和历史索引稳定。未修改旧街市、共享 Java、任务清单、用户存档、设备音量或亮度，未提交或推送。

## 2026-10-20 主清单整合验收完成

以上建筑交付时待接入说明为历史状态。#17现已接入真实龙宫维度与真实水面高度，保留原立资产在运行时绕水面仅作一次Y镜像，直接变换坐标矩阵/逆转置法线矩阵，使用NO_CULL处理反绕序，LEQUAL处理真实地形遮挡。渲染放在真实半透明水体前，不另画假水面、不调全局雾或亮度。与#14共用实际BakedQuad/原版图集version1网格加载器，仍保留各自独立条件、排序、缓存和声音归属。

实际48x40完整水面和4976个倒置体素分别验证，反射体素覆盖的两层世界水块须真实源水、无固体碰撞。60秒、scale1、单LOD、最多一座可见城，alpha<=0.58，近24…40m淡出、远144…176m淡出，附加粒子0低于150预算；本地水声最大0.05/96m内衰减，master=0未听音。无天气或时段门槛，无NBT世界放置、服务器实体、地形光照、奖励、任务/战斗/AI改动。

最终两次独立17项专用服检查和构建成功，20场景40张静音原生截图通过；主线复看五向/远近/水下/灰黑软件图，实际水下相机和原生水雾正确，重载/晚到/两包只绘一城、离区/到期/切维度正确清理。共享加载器接入后街市仍绘7370面。测试是一次性真实龙宫维度里的封闭深水池，截图中的池壁属于测试地形，非模组资产；不声称自然出现频率或独立多人客户端已验。龙宫固定夜景较暗，未改变用户亮度。

两份清单只删17号唯一行，累计12项1200张不重复参考；独立任务/指南针待办保留。本项100张来自16项目。最终包：build/cod3-dragon-palace-20261020/dynasty-1.4.0-cod3-scenic-20261020.jar；SHA256 bdc337210cce3e8eb8eee1ed8663cfbae9fc87135542f38d4e9080c9b95ed226。详见docs/cod3/verification-20261020-dragon-palace-mirage.json、qa-corrections.md和native/。
