# 30类×20只：原始数据独立复核

30/30类；6800个服务端采样tick；37391个采样帧。所有类采样tick均20只存活、NoAI=0。新增26类100预热/200采样；旧4类200/400，分别标注，不混淆配置。

粒子为存活粒子观测峰值；帧为间隔p95，tick为服务端墙时p95。客户端总实体包含玩家/靶子/投射物，不能当作怪物数量。

|类别|轮次 warm/sample|帧数|服务端存活/NoAI|客户端怪物范围|实际提交范围 / 20只帧比例|客户端总实体范围|粒子峰值|tick p95 ms|帧 p95 ms|截图|
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
|流民饥民 `famished_refugee`|run-04 100/200|1118|20/0|20|20 / 100.000%|22|0|3.75863|10.01879|[PNG](run-04/famished_refugee.png)|
|山贼喽啰 `bandit_thug`|run-04 100/200|1116|20/0|0–20|0–20 / 99.910%|1–22|0|1.71442|9.90779|[PNG](run-04/bandit_thug.png)|
|巡夜更夫 `night_watchman`|run-04 100/200|1100|20/0|20|20 / 100.000%|22|181|1.27475|9.98563|[PNG](run-04/night_watchman.png)|
|江湖骗子 `swindler`|run-04 100/200|1112|20/0|20|20 / 100.000%|22|0|2.70921|9.85221|[PNG](run-04/swindler.png)|
|采药客 `herb_picker`|run-04 100/200|1115|20/0|20|20 / 100.000%|22|0|3.08675|9.88292|[PNG](run-04/herb_picker.png)|
|赤狐 `red_fox`|run-04 100/200|1100|20/0|20|20 / 100.000%|22|0|1.55504|10.00971|[PNG](run-04/red_fox.png)|
|灰狼 `gray_wolf`|run-04 100/200|1098|20/0|20|20 / 100.000%|22|0|1.85963|10.13817|[PNG](run-04/gray_wolf.png)|
|野猪 `wild_boar`|run-04 100/200|1111|20/0|20|20 / 100.000%|22|0|2.81521|10.69896|[PNG](run-04/wild_boar.png)|
|巨蟒 `giant_python`|run-04 100/200|1076|20/0|20|20 / 100.000%|22|40|2.75325|13.48567|[PNG](run-04/giant_python.png)|
|花豹 `golden_leopard`|run-04 100/200|1025|20/0|0–20|0–20 / 99.902%|1–22|12|4.26300|17.85292|[PNG](run-04/golden_leopard.png)|
|树精 `tree_spirit`|run-02 200/400|2228|20/0|20|20 / 100.000%|22–34|30|1.71508|10.04658|[PNG](run-02/tree_spirit.png)|
|石精 `stone_sprite`|run-04 100/200|1038|20/0|20|20 / 100.000%|22|0|5.42533|17.82429|[PNG](run-04/stone_sprite.png)|
|灯笼鬼 `lantern_ghost`|run-04 100/200|1044|20/0|20|20 / 100.000%|22–42|13|3.85179|14.35021|[PNG](run-04/lantern_ghost.png)|
|剪纸童子 `paper_cut_child`|run-04 100/200|1075|20/0|20|20 / 100.000%|22|0|2.27663|13.72938|[PNG](run-04/paper_cut_child.png)|
|河童 `river_imp`|run-04 100/200|1100|20/0|20|20 / 100.000%|22–42|854|1.71208|10.17421|[PNG](run-04/river_imp.png)|
|水鬼 `drowning_ghost`|run-04 100/200|1104|20/0|20|20 / 100.000%|22|140|1.18254|9.97075|[PNG](run-04/drowning_ghost.png)|
|鲤鱼精 `carp_spirit`|run-04 100/200|1101|20/0|20|20 / 100.000%|22|156|1.33938|9.97563|[PNG](run-04/carp_spirit.png)|
|螺女 `snail_maiden`|run-04 100/200|1100|20/0|20|20 / 100.000%|22|138|2.25088|10.05038|[PNG](run-04/snail_maiden.png)|
|蟹将 `crab_soldier`|run-02 200/400|2248|20/0|20|20 / 100.000%|22|613|1.73700|10.10771|[PNG](run-02/crab_soldier.png)|
|蝙蝠妖 `bat_demon`|run-04 100/200|1040|20/0|20|20 / 100.000%|22|29|2.76150|17.19104|[PNG](run-04/bat_demon.png)|
|精卫鸟 `jingwei_bird`|run-04 100/200|1101|20/0|20|20 / 100.000%|22–41|140|2.78321|13.36800|[PNG](run-04/jingwei_bird.png)|
|灰隼 `gray_falcon`|run-04 100/200|1106|20/0|20|20 / 100.000%|22|545|3.53608|12.16046|[PNG](run-04/gray_falcon.png)|
|飞蝗群 `locust_swarm`|run-02 200/400|2266|20/0|20|20 / 100.000%|22|110|1.52713|9.81579|[PNG](run-02/locust_swarm.png)|
|尸蟞 `corpse_beetle`|run-04 100/200|1104|20/0|0–20|0–20 / 99.909%|1–22|152|4.12546|13.37879|[PNG](run-04/corpse_beetle.png)|
|毒蝎 `venom_scorpion`|run-04 100/200|1068|20/0|20|20 / 100.000%|22|13|2.58725|16.67933|[PNG](run-04/venom_scorpion.png)|
|石蚯龙 `stone_worm`|run-04 100/200|1114|20/0|20|20 / 100.000%|22|140|2.94513|11.32838|[PNG](run-04/stone_worm.png)|
|纸钱鬼 `paper_money_ghost`|run-04 100/200|1115|20/0|20|20 / 100.000%|22|20|2.53246|11.43779|[PNG](run-04/paper_money_ghost.png)|
|孤魂野鬼 `wandering_spirit`|run-02 200/400|2232|20/0|20|20 / 100.000%|22|27|1.31675|9.95300|[PNG](run-02/wandering_spirit.png)|
|机关木鹊 `wooden_magpie`|run-04 100/200|1119|20/0|0–20|0–20 / 99.911%|1–22|122|2.43058|10.32400|[PNG](run-04/wooden_magpie.png)|
|发条鼠 `clockwork_rat`|run-04 100/200|1117|20/0|20|20 / 100.000%|22|0|2.24821|10.33325|[PNG](run-04/clockwork_rat.png)|

## 对应轮次基线（无SecondaryMob）

|轮次/基线|帧数|粒子峰值|tick p95 ms|帧 p95 ms|客户端总实体|
|---|---:|---:|---:|---:|---:|
|run-02/baseline-dry|2224|0|1.24779|10.09367|1|
|run-02/baseline-water|2229|96|1.42471|9.97679|1|
|run-02/baseline-after|2211|30|0.98117|9.96054|1|
|run-04/baseline-dry|1107|0|1.69988|10.11508|1|
|run-04/baseline-water|1105|148|1.69858|11.85538|1|
|run-04/baseline-after|1097|0|0.80675|9.91846|1|

## 接触补测及异常帧

蝗虫run-06另测：200tick、1112帧，全部提交20只；采样期成功对玩家伤害1次；粒子峰值0；tick p95=3.88192ms，帧p95=10.07000ms。该低顶接触夹具与普通干场基线不同，不作净增量比较。

- bandit_thug：[{"phase": "bandit_thug", "age": "300", "interval_ms": "9.60921", "render_ms": "0.36546", "rendered_cohort": "0", "client_cohort": "0", "particles": "0", "client_entities": "1"}]
- golden_leopard：[{"phase": "golden_leopard", "age": "300", "interval_ms": "14.71663", "render_ms": "0.43117", "rendered_cohort": "0", "client_cohort": "0", "particles": "0", "client_entities": "1"}]
- corpse_beetle：[{"phase": "corpse_beetle", "age": "300", "interval_ms": "18.73300", "render_ms": "0.50992", "rendered_cohort": "0", "client_cohort": "0", "particles": "9", "client_entities": "1"}]
- wooden_magpie：[{"phase": "wooden_magpie", "age": "300", "interval_ms": "9.43325", "render_ms": "0.42779", "rendered_cohort": "0", "client_cohort": "0", "particles": "0", "client_entities": "1"}]

## 并行机器环境

|轮次|1分钟load最少/最多|Java进程数最少/最多|
|---|---:|---:|
|run-02|14.14/19.02|12/19|
|run-04|13.84/98.10|8/19|
|run-06|12.94/16.95|9/14|

Java进程包含客户端、Gradle等，不能把它当成客户端数量。CPU/load日志已列入输入SHA-256。

## 范围与重现

p95算法：排序后取零基索引floor((n−1)×0.95)；未删异常值、未删末端0提交帧。JSON保留精确值、计数直方图、所有低于20帧和原始文件SHA-256；CSV可独立导入。源码只读重算命令：`python3 tools/cod4/mob-load-acceptance/verify_load30.py`。不依赖旧汇总脚本；旧JSON若存在，只用于复算结果一致性交叉验证；缺失时仍可仅从原始CSV复算。

- Run02 four classes200 warm/400 sample, open arena; run04 remaining26 classes100/200, glass enclosure. Dry/water baselines are same run and enclosure configuration. Do not pool them as identical workloads.
- Alive/no_ai are server cohort counts, client_cohort is SecondaryMob count, client_total_entities is all client entities including player/dummy/projectiles. Total server entity count was not separately recorded; do not invent it. SecondaryProjectile count is separately available.
- Actual renderer submissions are distinct entity IDs collected from GeoEntity.Pre or Steve RenderLiving.Post. This is not GPU-visible pixel count or20 distinguishable silhouettes. Four run04 phase-end frames have rendered/client cohort0, retained.
- Particles are total observed live client particles, including environment, water and residual effects. Not a count of emitted particles or attributable exclusively to this mob. Water baseline nonzero is retained.
- AI enabled on all20 cohort mobs. QA Cow alone NoAI and waypoint teleport/refill; four passive/escape types additionally receive controlled1-damage provocation. Native path counts/position changes do not prove every mob has successful pathfinding or all skills trigger.
- Frame interval includes120fps cap and host scheduling. ServerTick START/END and render wall time include QA observation overhead and are not GPU timestamps. Parallel Java/other machine work is documented in per-run host-load JSONL; small differences are not causal evidence.
- Run06 contact supplement uses low roof and extra ArmorStand observer plus in-arena survival player. Its dry baseline does not match that fixture; contact timings are descriptive, not isolated net cost. Successful contact and20 submissions do not establish worst-case particle coverage.
- Original crab continuous full-submersion boundary, all skills, mixed cohorts, natural terrain, multiplayer, long sessions and full modpack remain outside acceptance.19 prior COD1 pairings unchanged; class-range extension is separately documented.
