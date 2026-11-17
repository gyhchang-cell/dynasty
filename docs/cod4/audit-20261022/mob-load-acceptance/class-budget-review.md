# 原11项COD1类预算补充

这是只读类比判定，不是新机制、正式预算变更或作者指定的一对一。原19对应不动；11项的精确同型基准仍不杜撰。先固化分组规则，再由原生计数算范围。计数此前已可见，因此不是盲审。

## 选择与计数原则

- 仅从实际注册的COD1基础30选择，按最终dispatcher原生模型计数，不纳入精英/Boss、vanilla或旧自身模型。
- 先按形态、肢体结构和移动/用途明确类组；骨架类比、粗类和用途参考分别标注，不能冒充精确物种对应。
- 对全部候选逐个比较。次级quad≤范围下限才是在全部候选下满足；超过上限则全部超出；落在中间只算部分满足。不拿上限当统一通过线。
- 计数包含实际烘焙的本体附件，外部手持层不算；quads不是triangles，不剔除低面数Steve候选、不拆分聚合虫群、不做体型比例换算。
- 没有同型结构时下限/上限为null，不借重型载具或高面数模型补齐。原19项不改，这11项只补证据和条件结论。

|类别|本体cuboid/quad|类组|基础cuboid范围|基础quad下限–上限|候选满足数|条件结论|
|---|---:|---|---:|---:|---:|---|
|流民饥民 `famished_refugee`|26/156|light_human_biped|18–26|108–156|1/6|仅部分候选下满足|
|江湖骗子 `swindler`|32/192|light_human_biped|18–26|108–156|0/6|全部候选下超出|
|采药客 `herb_picker`|30/180|light_human_biped|18–26|108–156|0/6|全部候选下超出|
|野猪 `wild_boar`|33/198|mobile_mammal_quadruped|61–69|366–414|2/2|全部候选下满足|
|花豹 `golden_leopard`|28/168|mobile_mammal_quadruped|61–69|366–414|2/2|全部候选下满足|
|精卫鸟 `jingwei_bird`|23/138|paired_wing_nonhumanoid|59–59|354–354|1/1|全部候选下满足|
|灰隼 `gray_falcon`|22/132|paired_wing_nonhumanoid|59–59|354–354|1/1|全部候选下满足|
|机关木鹊 `wooden_magpie`|27/162|paired_wing_nonhumanoid|59–59|354–354|1/1|全部候选下满足|
|纸钱鬼 `paper_money_ghost`|15/90|compact_wingless_airborne_ghost|41–69|246–414|3/3|全部候选下满足|
|螺女 `snail_maiden`|20/120|无|未定义|未定义|0/0|无可比基准|
|飞蝗群 `locust_swarm`|98/546|无|未定义|未定义|0/0|无可比基准|

## light_human_biped

正常尺度人类的头、躯干、双臂、双腿与轻装衣甲；排除巨盾、明确重装护卫、大旗、畸形尸体、纸扎、鬼魂、树石构装和攀爬猿形骨架。

|COD1基础ID|实际cuboid/quad|最终模型资源|
|---|---:|---|
|zuwu_daoshou|26/156|dynasty:models/entity/steve_fighters/zuwu_daoshou.json|
|juma_changqiangbing|25/150|dynasty:models/entity/steve_fighters/juma_changqiangbing.json|
|liannu_zhenzu|19/114|dynasty:models/entity/steve_fighters/liannu_zhenzu.json|
|fufa_jijiu|18/108|dynasty:models/entity/steve_fighters/fufa_jijiu.json|
|tiesuo_chihou|24/144|dynasty:models/entity/steve_fighters/tiesuo_chihou.json|
|kuijun_sishi|21/126|dynasty:models/entity/steve_fighters/kuijun_sishi.json|

次级Geo模型四肢分段多于COD1实际Steve模型，保留这项真实复杂度差异，不按骨骼归一化。冠、背篓、算盘与武器不同；COD1无中立交易/流民职业同型。

## mobile_mammal_quadruped

非多节的陆生哺乳兽形躯干、头、尾和四肢支撑，能够连续地面移动；纳入以前肢承重的攀爬山魈，保留手掌解剖差异；排除以跳跃为主的蛙、背碑重壳龟、蛇和多足节肢。

|COD1基础ID|实际cuboid/quad|最终模型资源|
|---|---:|---|
|xunshan_mujiaquan|61/366|dynasty:geo/blueprint/xunshan_mujiaquan.geo.json|
|shanjing_shanxiao|69/414|dynasty:geo/blueprint/shanjing_shanxiao.geo.json|

没有精确猪/猫科COD1基怪。机械犬有齿轮附件，山魈有抓握前肢与攀爬差异；两者均纳入，不只选择较贵者。

拓宽敏感性：xunshan_mujiaquan=61/366、shanjing_shanxiao=69/414、chimu_zhuha=38/228、juli_bixi_kuilei=63/378。完整范围 {"cuboids_min": 38, "cuboids_max": 69, "quads_min": 228, "quads_max": 414, "quad_lower_ids": ["chimu_zhuha"], "quad_upper_ids": ["shanjing_shanxiao"]}。蛙/重龟不作为首选，仅说明放宽骨架分类的结果；没有挑赑屃单独抬高预算。

## paired_wing_nonhumanoid

单一紧凑非人形躯干、头、一对主动振翅翼与爪；排除额外双翼的巨臂人形、无翼飞颅、浮空鱼和聚合虫群。

|COD1基础ID|实际cuboid/quad|最终模型资源|
|---|---:|---|
|youdeng_guimianfu|59/354|dynasty:geo/blueprint/youdeng_guimianfu.geo.json|

COD1该组只有鬼面蝠。膜翼指骨不同于羽翼、鸟喙、尾羽及机械鸟关节；精确鸟类/机关鸟基准仍不存在。范围退化为单值不等于宣称物种一对一。

## compact_wingless_airborne_ghost

独立紧凑、无翼、可离地自由漂浮、具有接触/诅咒/干扰用途的阴魂；排除依水生存的水鬼、大型纸轿与轿夫载具、主动振翅蝙蝠。这不是共享解剖骨架类。

|COD1基础ID|实际cuboid/quad|最终模型资源|
|---|---:|---|
|muxue_feilu|41/246|dynasty:geo/blueprint/muxue_feilu.geo.json|
|yinbing_guizu|51/306|dynasty:geo/blueprint/yinbing_guizu.geo.json|
|fuhun_baibu_tongzi|69/414|dynasty:geo/blueprint/cod2_voxel/fuhun_baibu_tongzi.geo.json|

没有纸钱本体或吸钱同型。飞颅触须、阴兵铠甲、裹布童子轮廓不同；在用途参考范围内满足，不能关闭精确形态预算的未定义状态。

## 解释与剩余范围

轻装人形保留祭酒108、弩卒114等低预算：饥民156仅在刀手156下满足，骗子192和采药人180超出该组全部108–156候选，超过各候选的差额范围分别36–84、24–72 quad；这是类预算冲突，精确职业基准不存在，不能自动推导必须削模。其他外形不相近的重装人形204/222、旗官540没有拿来“过关”。

纸钱鬼仅是移动/用途参考，不是相同纸钱骨架；鸟类仅是双翼粗类，COD1没有真正鸟形/机械鸟形。所有“全部满足”仅针对文中穷举的合理候选集，不能外推未知模型。

螺女与飞蝗群仍无可比基准；不采用重龟/大蜈蚣/复合纸轿当替身，不拆飞蝗14个虫体进行除法来掩盖单实体总面数。

完整30基础怪的纳入组、排除理由、模型骨架/part父子链、原生渲染器/资源与源码锚点在JSON；可独立核对范围两端及所有候选，CSV便于筛选。

复现：`python3 tools/cod4/mob-load-acceptance/class_budget_review.py`。无需启动客户端；读已保存run-03原生烘焙结果与隔离快照。模型声明计数另行对照原生计数；按6面长方体/显式UV面计数，不按文件大小。
