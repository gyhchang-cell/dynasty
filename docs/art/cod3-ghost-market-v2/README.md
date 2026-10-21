# 幽谷鬼市·鬼火长街：静态建筑交付

本目录交付 #22 的原创静态环境建筑，供主线加载。当前为 `BUILDING_READY`；整个奇观仍为 `PARTIAL`，尚未在游戏内验收，不删除任务清单。

实际产物：

- 生成源：`tools/art/cod3/scenic_ghost_market.py`。
- 标准结构 NBT：`src/main/resources/data/dynasty/structures/scenic_ghost_market.nbt`。
- 版本 1 客户端数据：`src/main/resources/assets/dynasty/scenic/ghost_market.json`，拟新增加载位置 `dynasty:scenic/ghost_market.json`。
- 开口、铺位、柱脚、十二处灯位中心及事件约定：`geometry.json`。
- 独立检查与交付指纹：`checks.json`、`BUILDING_READY.json`。

## 造型与尺度

建筑本地范围 28×16×44 格，实际最高顶点 Y9；主体为一条沿 +Z 延伸的 44 米窄街。两侧低岩肩有宽窄和高低变化，六间铺棚错位设置，入口和尾部均为单层低牌架。采用纸铺、药草棚、铜器棚、茶供铺、契书铺、旧器棚的柜台与货架分工，不新增 NPC、商店逻辑或 AI。

与 #14 沙漠街市的宽铺面、四座房屋、两层门楼不同，本批独立编写几何，采用纵长占地、曲折中线、六座单层半开放棚屋及两侧岩肩。没有导入、旋转、缩放或改材质复用 #14 的建筑。通用 NBT 编码、版本 1 数据格式和软件渲染工具继续复用。

主体只含原版不透明整块，14 种方块、16 个真实 palette 状态。原木轴向随立柱、X 横梁、Z 纵梁变化，荧光块使用 `axis=y`。门洞和内部空间是实际未占用体素，柜台避开入口；全部 2,981 个方块面连通，外露面 5,564 个，包含底面、门洞和内腔面。几何检查可从街口走到街尾及六铺内部，共 789 个可达地面格；这是离线几何净空检查，不代表已完成游戏寻路或碰撞验收。

十二个实体灯块由柱梁支撑，中心坐标逐一记录在 `geometry.json/lights`。它们提供稳定的美术位置，运行时鬼火、远景 LOD、雾、透明度和声音仍由主线负责。关闭特效仍能辨认棚面、柜台、门洞和街线。

## 坐标与接入

入口朝 -Z，街线沿 +Z。所有 NBT 与客户端方块保持相同未平移本地坐标；客户端数据完整保留 palette 与 Properties。

```text
centerPivot = [14, 0, 22]
anchor      = [14, 0, 0]  # 街口标志点，不是运行时原点
groundBlockY = 0
walkingFeetY = 1
world = groundCenter + rotation(local - [14, 0, 22])
```

支点相对的实际顶点包围盒为 `[-14,0,-22]` 至 `[14,9,22]`；原尺度保守渲染半径可用 29。旋转时也要变换包围盒。主线需在真实阴司场地选择合适地面，验证岩肩与地形、屋脚接地和入口视线，不进行结构世界放置。

主事件约定为 `dynasty:underworld`、夜间 13000～23999、雾环境、1800 tick（90 秒）、中距、远处鬼火、隐约叫卖、特效预算不超过 200。阴司无自然天空光，不能假定自然雨可触发：具体雨／区域雾判定由主线按维度实际能力接入。制作期间没有播放声音。

## 参考与检查

已从作者图库下载候选并实际查看 149 张建筑图，选定 100 张，来自 20 个项目，与前 1,500 条记录零 SHA256 重叠，包含并行兵俑模型 100 张及兵俑贴图 100 张。另核对前 1,500 个可用解码 RGBA 指纹：其中 1,450 项从原文件核验并解码，50 项采用既有清单的解码指纹；新图内部及与上述记录均无完全相同的 RGBA。解码比较包括尺寸，不排除缩放、裁剪或同建筑不同视角。每张获选图均保留来源链接、缓存图、对应观察拼版和中文构造笔记，见 `references/selected-100.json`、`observations.txt` 与 `decoded-rgba-audit.json`。单位为图片：整张拼版计一张，同一建筑的不同角度可能是不同图片，不宣称有 100 座不同建筑。未查看的现代街景、武器、界面等候选缓存已清理。

重点参考来源包括作者发布的 [Ancient Structures: Chinese](https://modrinth.com/mod/ancient-structures-chinese/gallery)、[qrafty's Japanese Villages](https://modrinth.com/datapack/qraftys-japanese-villages/gallery) 与 [Villages and Pillages](https://modrinth.com/mod/villages-and-pillages/gallery)。提取的是低檐、柱梁、真实开口、错位门面与地形围合原则，未复制任何模型、结构文件或贴图。

48 项离线检查通过，覆盖确定性导出、标准 NBT、完整客户端 palette、方位与外露面、面连通、主街净空、铺内可达、柱脚与灯位、参考去重及既有资产指纹。完整原生验收仍待主线处理，不能以软件预览代替。

## 软件预览与复现

预览直接读取当前 NBT、客户端外露面和本地 Minecraft 1.20.1 原版 PNG，以最近邻采样呈现。提供正、背、左、右、45°、灰模、暗光、黑影、18 米街口、街内视角与俯视；1.8 米人物和一米材质参照仅存在于预览，落在实际街口地面。街内透视采用 1.62 米视高和 70° 垂直视场。没有雾、粒子、鬼火、泛光、音效或相机震动。软件是双面光栅器，原生 UV、绕序、背面裁剪和透明深度仍需游戏内验证。

```sh
python3 tools/art/cod3/scenic_ghost_market.py
python3 tools/art/cod3/scenic_ghost_market.py --check
/Users/a15356015027/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 tools/art/cod3/scenic_ghost_market.py --review
```

前两条只需 Python 标准库；预览另需 NumPy、Pillow 和已缓存的原版材质 JAR。命令仅写本批资源与文档，不运行 Java、Gradle、客户端或服务端，不写存档。没有修改共享 Java、世界生成、任务、指南针或清单，没有调整声音、亮度、关闭现有客户端，也没有提交或推送。
