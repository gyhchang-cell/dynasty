# COD4-1 第二项：只读验收

**结论：部分验收，不应删除整条待办。** 产品基础怪指向COD1基础30，而非vanilla。19类有规格依据的形态/用途对应候选，在选定对应关系下均满足面数≤基怪；11类保留未定义。4类代表cohort完成原生负载采样，剩余26类未覆盖。

原文依据：`docs/cod4/request.txt` 开头查重基准及§1.0；实际COD1资料目录为 `docs/blueprint-cod1/`（不存在docs/cod1）。`cod1.txt` / `cod1_new.txt`规格与 `BlueprintEntities` 的30个TemplateMob注册一致；本次原生探测全部30类最终绑定，不混入精英/Boss。

原版比较和旧自有模型差值只保留作参考，不用于认定违反原文或自动认定产品缺陷。对应候选按形态/用途选择，尚非原作者声明的一对一映射。完整选择理由与strong/shape/role依据见 `cod1-comparison.json`。

山贼与更夫被LOWEST注册覆盖为SteveFighterRenderer；其他28类为ExpansionClient.Renderer。COD1同样按实际dispatcher最终绑定计算，包括Steve覆盖；GeoCube非空quads与原生ModelPart.Cube.polygons用相同口径。计数是quad而非triangle，主体以外的手持物品/额外层均未计入。没有按大小或贴图透明度猜面数。

|次级怪|实际cuboid/quad|COD1基础对应候选|基怪cuboid/quad|次级减基怪quad|判定|
|---|---:|---|---:|---:|---|
|流民饥民 `famished_refugee`|26/156|未定义|—|—|未定义|
|山贼喽啰 `bandit_thug`|21/126|zuwu_daoshou|26/156|-30|该对应下满足|
|巡夜更夫 `night_watchman`|15/90|zhenwang_zhangqiguan|90/540|-450|该对应下满足|
|江湖骗子 `swindler`|32/192|未定义|—|—|未定义|
|采药客 `herb_picker`|30/180|未定义|—|—|未定义|
|赤狐 `red_fox`|29/174|xunshan_mujiaquan|61/366|-192|该对应下满足|
|灰狼 `gray_wolf`|28/168|xunshan_mujiaquan|61/366|-198|该对应下满足|
|野猪 `wild_boar`|33/198|未定义|—|—|未定义|
|巨蟒 `giant_python`|15/90|bishui_xuanjiao_youzi|74/444|-354|该对应下满足|
|花豹 `golden_leopard`|28/168|未定义|—|—|未定义|
|树精 `tree_spirit`|40/240|kumu_shujing|74/444|-204|该对应下满足|
|石精 `stone_sprite`|17/102|jubi_shigandang|50/300|-198|该对应下满足|
|灯笼鬼 `lantern_ghost`|21/126|fuhun_baibu_tongzi|69/414|-288|该对应下满足|
|剪纸童子 `paper_cut_child`|28/168|zhiren_jianke|62/372|-204|该对应下满足|
|河童 `river_imp`|31/171|shashui_funigui|42/252|-81|该对应下满足|
|水鬼 `drowning_ghost`|23/138|shashui_funigui|42/252|-114|该对应下满足|
|鲤鱼精 `carp_spirit`|19/114|xueju_mangguyu|72/432|-318|该对应下满足|
|螺女 `snail_maiden`|20/120|未定义|—|—|未定义|
|蟹将 `crab_soldier`|31/186|bazu_digongzhu|70/420|-234|该对应下满足|
|蝙蝠妖 `bat_demon`|28/168|youdeng_guimianfu|59/354|-186|该对应下满足|
|精卫鸟 `jingwei_bird`|23/138|未定义|—|—|未定义|
|灰隼 `gray_falcon`|22/132|未定义|—|—|未定义|
|飞蝗群 `locust_swarm`|98/546|未定义|—|—|未定义|
|尸蟞 `corpse_beetle`|28/168|bazu_digongzhu|70/420|-252|该对应下满足|
|毒蝎 `venom_scorpion`|32/192|mingsha_shixie|70/420|-228|该对应下满足|
|石蚯龙 `stone_worm`|19/114|baimu_mowu|173/1038|-924|该对应下满足|
|纸钱鬼 `paper_money_ghost`|15/90|未定义|—|—|未定义|
|孤魂野鬼 `wandering_spirit`|15/90|yinbing_guizu|51/306|-216|该对应下满足|
|机关木鹊 `wooden_magpie`|27/162|未定义|—|—|未定义|
|发条鼠 `clockwork_rat`|29/174|xunshan_mujiaquan|61/366|-192|该对应下满足|

不以较大Boss、重做前自身模型、任意vanilla或无关大型核心怪冒充对应基准。11项保留原因逐条见JSON。未自行削模；当前没有从这19个对应中发现面数超标，因此不派发无依据的减资产修复。

## 原生客户端负载记录

|场景|帧间隔p50/p95 ms|渲染墙时p95 ms|服务端tick均值/p95 ms|20只实际提交帧比例|活跃路径均值|已移动只数均值|粒子均值/峰值|
|---|---:|---:|---:|---:|---:|---:|---:|
|baseline-dry|8.91/10.09|0.49|0.87/1.25|0.0%|0.00|0.00|0.0/0|
|tree_spirit|8.91/10.05|0.98|1.27/1.72|100.0%|19.33|19.98|6.5/30|
|locust_swarm|8.68/9.82|1.51|1.00/1.53|100.0%|9.70|19.99|5.4/110|
|wandering_spirit|8.83/9.95|0.82|0.99/1.32|100.0%|20.00|20.00|3.6/27|
|baseline-water|8.88/9.98|0.59|0.86/1.42|0.0%|0.00|0.00|78.1/96|
|crab_soldier|8.68/10.11|1.49|1.22/1.74|100.0%|11.38|20.00|340.6/613|
|baseline-after|8.96/9.96|0.58|0.71/0.98|0.0%|0.00|0.00|17.0/30|

镜头位于(0,76,25)，俯角29°；地面Y64、43×37石台，FOV选项1.0（110°）。这是约25格距离的同屏测试，不是近距离大面积填充率压力测试。每场景200tick预热、400tick采样；无实体基线保持同配置/镜头/地形，水生场景使用水池基线。基线指无SecondaryMob，战斗场景另有1只测试靶和自然发出的投射物。怪物AI全开，靶子单独关闭AI并每tick补血、每80tick换目标点；怪物未瞬移。没有注入人工粒子。

帧间隔包含帧率限制与系统调度；渲染墙时不是GPU计时器。服务端时间为原生ServerTick START至END，原始逐帧、逐tick与攻击事件CSV保留。该机器同时运行其他Java任务，CPU负载记录保留，不能把本轮增量视为排除干扰后的单模组净成本。

游魂在共用目标处有明显模型重叠，事件证明20次独立实体提交，但截图无法分辨20个轮廓。蝗虫群的原生接触技只针对玩家，本靶为Cow，因此其原生攻击事件为0，不能把这一组算作玩家接触技能或最坏粒子负载验收。水池空场本身也有粒子（峰值96），末尾空场仍有余留粒子（峰值30），未把它们记成0。

只覆盖最重飞行模型、树精地面寻路、游魂直接移动及蟹兵水生移动。其余26类、自然复杂地形、混合群、多人与整包性能未验收。是否全20只持续同屏需结合上表事件比例与PNG，低于20的帧不掩盖。

未负载测试的26类：famished_refugee、bandit_thug、night_watchman、swindler、herb_picker、red_fox、gray_wolf、wild_boar、giant_python、golden_leopard、stone_sprite、lantern_ghost、paper_cut_child、river_imp、drowning_ghost、carp_spirit、snail_maiden、bat_demon、jingwei_bird、gray_falcon、corpse_beetle、venom_scorpion、stone_worm、paper_money_ghost、wooden_magpie、clockwork_rat。

## 重现与证据

- `tools/cod4/mob-load-acceptance/prepare.py` 创建独立源码/资源/Gradle缓存快照；不碰主frozen。
- `run.py run-02` 使用全新私有profile；复测须换新run参数，保留旧世界。
- QA在额外sourceSet，未向正式src写入，也未创建或替换正式Jar。
- `geometry-counts.csv` / `geometry-audit.json` / `run-02/native-geometry.json` 是次级30类计数；vanilla比较仅供参考。
- `cod1-comparison.json` / `cod1-comparison.csv` / `run-03/native-cod1-geometry.json` 是COD1基础30原生计数与19对应、11未定义证据。
- 重现顺序：prepare.py → run.py(全新run) → audit.py → cod1_compare.py → summarize.py；现有分析脚本明确引用run-02负载与run-03基怪探测，复测时应显式调整对应路径。
- `run-02/frames.csv` / `ticks.csv` / `attacks.csv` / 原生PNG与客户端日志是负载证据。
- `run-01/FAIL.txt` 保留首次发现Steve渲染覆盖的探测失败；不算负载测试通过。
- 本任务未修改正式渲染器、模型、贴图或TODO。
