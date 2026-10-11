# Cod2 原创 Cuboid 改造 / 2026-10-10 至 11 夜间

用户已授权本地实际改造、逐项验证和夜间继续。只修改美术资源、必要的贴图路径和独立 QA 工具；没有改动战斗、任务、AI、技能注册、命中逻辑、实体碰撞尺寸，也没有推送 GitHub。

## 第一批

| 实体 | 旧模型问题 | 新体块、骨骼和动作 |
| --- | --- | --- |
| 巨臂石敢当 `jubi_shigandang` | 连续细长躯干没有头脸/胸腰身份，共用士兵色岛，巨拳像箱子 | 38 模型单位高；14×9×10 胸、8×5×8 腰、12×7×10 碑式骨盆、独足和不对称巨拳。`root → body → waist → chest → neck → head`，巨拳分肩/上臂/肘/拳；保留断链和碑文。第 16 tick 上勾，第 30 tick 落拳。 |
| 巨力赑屃傀儡 `juli_bixi_kuilei` | 一大块水平箱壳、细杆悬空腿，壳和头不易分辨 | 34 单位高，28×8×28 阶梯龟甲、独立腹甲、负碑、短龙颈、四组肩腿/活塞/脚、两段尾。甲体与负碑连接但独立动作，脚掌反向补偿以承重；咬击 18 tick、重踏 32 tick。 |
| 铜臂飞天夜叉 `tongbi_feitian_yecha` | 水平杆挂布式翼，五段巨臂拖到脚下，长躯干无分段 | 胸/腰/骨盆和铜面具，40 单位含角高；三段粗阶梯折翼、屈膝兽足、五段铜臂和三指手掌。`torso → waist → chest` 专用翼臂树。保留 `giant_palm`/`hook_*` 挂点；16 tick 横扫，20 tick 抓取后闭指。 |

各模型交付实际 `geo/blueprint/<id>.geo.json`、`animations/blueprint/<id>.animation.json`、`textures/entity/blueprint/<id>.png`。PNG 恰好 16×16，白底至少 1 像素边距，含白底四种纯色，非白色区域由 2×2 格组成；UV 只采内部有效色岛。肖像在纯白底上正面展示各生物。放大贴图采用最近邻。

`blockbench/` 保留三个 `.bbmodel` 编辑源与独立动画源，内嵌贴图；无第三方模型或贴图。Blockbench 坐标转换、上下表面 UV 方向与甲片 inflate 保留。编辑项目后可在 Animation 模式导入旁边的同名 `.animation.json`。

制作工具为 `tools/art/cod2-voxel/`：Cuboid 生成、离线落点关键帧、多角度软件深度缓冲预览、资源检查、独立 Forge 客户端 QA。使用 bundled Python（Pillow + NumPy）生成及检查，Java 17 离线构建。

## 技术参考

阅读了用户指定的三个官方项目，重点核对实际代码和当前版本兼容性：

- [Blockbench Bedrock codec](https://github.com/JannisX11/blockbench/blob/master/js/formats/bedrock/bedrock.js)：Cuboid、bone pivot、X 坐标镜像、X/Y 旋转符号、每面 UV 和上下 UV 方向。用于保留可编辑项目与实际导出资源的坐标一致性。
- [GeckoLib 4 Geo Models](https://github.com/bernie-g/geckolib/wiki/Geo-Models-(Geckolib4))：模型、动画、贴图路径分别由 GeoModel 返回。项目继续使用现有 Forge 1.20.1 / GeckoLib 4.8.4，没有套用 GeckoLib 5 的路径或 API。
- [Blockbench Plugins GeckoLib codec](https://github.com/JannisX11/blockbench-plugins/blob/master/plugins/geckolib/src/ts/codec.ts) 与 [format constants](https://github.com/JannisX11/blockbench-plugins/blob/master/plugins/geckolib/src/ts/constants.ts)：`geckolib_model`、骨骼树、每面 UV 和独立动画文件。没有安装或执行来源不明的第三方插件。

## 验收证据与范围

`*-before.png` 保存原始资源五视图；`*-review.png` 检查正面、45°、90°、背面、纯黑剪影；`*-comparison.png` 是前后对比；`*-actions.png` 检查动作。这些明确是软件预览，不是游戏截图。

`native/solo1/` 是首轮真实 Forge 客户端截图、服务端动作 epoch、实际播放 Gecko clip、独立运行快照和资源重载记录，36 组姿势及重载后再次渲染已通过。该轮之后继续修正了动作插值的穿地问题，因此最终资源仍必须重新运行检查与客户端，不能把首轮证据当最终版本验收。

最终版本已通过：`validation.json` 的所有像素/UV/骨骼/旧挂点/动画时长/四分之一 tick 落点及编辑源坐标检查；Java 17 离线 `build`；`native/solo3/` 的 36 组真实客户端姿势与资源重载后再次渲染。运行快照中三套 geo/animation/texture 的 SHA-256 与当前资源逐一一致。`solo2` 曾因移动夹具自然减速提前回到待机失败；只修正 QA 持续移动和真实速度同步，未修改生产 AI。真实客户端夹具属于美术加载、姿势、接入验收，不代表地下城路线、完整战斗难度或长期性能已通过。

Cod2 的第 11 类动画需求还包括视听、镜头、地形、内爆等完整效果，本批三个美术资源不代表该整段完成；生态、地牢和事件段落也不能因一个模型通过而删除。本批不删除这些未完整验收的提示词。

## 第二批

幽灯鬼面蝠、穴居盲骨鱼（保留资源 ID `xueju_mangguyu`）、煞水浮溺鬼已完成实际重做。独立专用骨架、21 个原 clip、三张 16×16 四色 PNG 与可编辑 bbmodel 已交付，见 [第二批记录](FLOATERS.md)。`validation-floaters.json`、离线构建、生产 JAR 资源哈希及 `native/floaters3/` 的 37 个真实客户端姿势和资源重载均通过。蝠提灯握持、鱼张颚与发光背棘、水鬼三节水鞭与水下融化已检查；没有改变生产玩法逻辑。

## 第三批

青铜双头蛇傀、巡山木甲犬、八足地工蛛、鸣沙石蝎已完成实际重做，见 [第三批记录](MECHANICALS.md)。四套专用骨架共 137 个 bone、266 个 Cuboid、33 个原 clip；四张原生 16×16 四色 PNG、可编辑 bbmodel 和独立动画源齐全。蛇的两个头使用不同甲冠与机关口；犬体按原实体大小缩放；蛛有八条完整髋膝足链；蝎保留生产 IK 的身份骨骼并重做七节弯尾和双钳。

最终资源通过 `validation-mechanicals.json`、Java 17 离线构建、JAR 与客户端快照哈希核对、旧生成器保护，以及 `native/mechanicals5/` 的 49 张真实姿势截图和资源重载。`native/mechanical-details3/` 另有 37 张截图，确认后头刺击/喷毒、真实砂地掘沙与出土、第 20 tick 尾刺、蛛由真实天花板支撑松脱并落地。落地截图等到客户端也到达地面再采样，服务端实际记录靶血 1000→990.2。前一轮版本及显示器休眠失败记录保留，不能充当最终资源证据。

## 第四批

百目魔蜈、碧水玄蛟幼子、赤目朱蛤、符法祭酒已完成实际重做，见 [第四批记录](BEASTS-PRIEST.md)。四套资源合计 310 bones、364 Cuboid、30 个原 clips，原生 16×16 四色 PNG、可编辑 bbmodel 和独立动画源齐全。蜈蚣使用逐节膝足和厚甲，玄蛟有龙首与高颈/低腹/尾，朱蛤有粗后腿、厚颚与程序限距舌，祭酒保留胸腰盆/袖符惯性包装并把握杖移至袖外。

最终静态、离线构建、生产 JAR/快照 SHA 与旧生成器隔离保护均通过。`native/beasts-priest2/` 有 50 张真实 Forge 姿势截图和资源重载，含实际深水缠绕、真实跳跃飞行和友军施符；`native/beast-details3/` 另有 25 张真实截图，检查完整倒挂四方向/瞪视和真实足额减血触发朱蛤毒囊。此前池边第一人称遮挡、33 启动拒绝及吊顶镜头遮挡的证据保留并明确无效/失败标记。十四套全部 42 个资源哈希一致，前十套没有改动。

## 第五批

拒马长枪兵、溃军死士、枯木树精、连弩阵卒已完成实际重做，见 [第五批记录](ARMIES-TREE.md)。四套共183 bones/301 Cuboid/30原 clips，16×16四色贴图、bbmodel/独立动画齐全。离线支撑臂稳定双手握持，树精采用偏心粗树干/六向根盘/不对称四叉冠枝。

静态/离线构建/JAR及三个真实不可变快照SHA、旧生成器54资源保护通过。armies-tree1 与 army-details2 各50张真实截图/52条记录，含生产冲刺靶架枪、真实连续40近敌tick后引爆（靶血1000→986）、受伤唤醒树精和camouflage四方向、第三次刀刺/弩发及真实翻滚。隐形牛靶的爆炸火焰遮挡尸体，单独 powder-death3 清理这一个检查夹具的火后补验两张真实死亡姿势及重载；真实引爆截图保留。其余轮次/部分遮挡标记保留，不能把遮挡尸体图片当清楚的视觉证据。

全夜当前完成普通怪队列30/30个模型。所有完成项有实际资源、五方向/黑剪影与动作、构建和真实 Forge 证据；完整 Cod2 玩法/生态/地牢及第11类效果仍未全验收，本轮没有新增提示词删除。

## 后续队列

第六批橹盾甲士、墓穴飞颅、披甲叛将护卫、铁索斥候已检查原件五视图并保存SHA基线，已写制作前计划并改造实际资源，见 [第六批计划及记录](SHIELD-SKULL-GUARD-SCOUT.md)。已通过静态/握持矩阵、离线构建、旧生成器66资源保护及三个真实客户端快照。主轮 shield-skull1 51张/52条记录，细节 shield-details3 50张/51条，清晰受伤补轮 shield-hurt2 3张/4条。包括真实飞颅俯冲/血池、三次正面真伤反击、真实钩索命中和第6tick膝击。源码、JAR、三个快照66资源SHA一致；前十八套保持不变。第七批至第九批的最终验收见后文。童子/纸人的旧dirty资源原字节保留，新的独立资源已接入。

本聊天夜间自动续作持续到北京时间 2026-10-11 09:00。每批必须实际修改资源、构建和游戏验证，使用静音隔离存档。未通过的条目保留，不把计划或预览冒充完成。

## 第七批

尸变力士、阴兵鬼卒、阴阳纸轿游魂、阵亡掌旗官已完成，见 CORPSE-GHOST-PALANQUIN-FLAG.md。69/28/43/79 bones、83/51/86/90 Cuboid、27原clips；四套原生16×16四色、bbmodel/独立动画。五视图/黑剪影与动作实际检查，修正力士外指脱离掌块、鬼卒戈刺角度；握戈一致和每四分之一tick双手旗杆支持误差最高0.002079模型单位，静态/构建/旧生成器78资源保护通过。spirits-procession1有51真实截图/52条记录，含真实伤害尸瘴1、真实近战触发鬼卒侧移及6tick透明恢复、纸轿实际夹持hook、实际友军军魂效果及资源重载。当前、JAR、不可变客户端快照78资源SHA一致，前22套不变；未改生产逻辑，不新增cod2提示词删除。下一批是山魈、刀手，原件已查看；童子/纸人仍他人dirty，保留。

## 第八批

山精山魈和卒伍刀手已完成实际改造，见 APE-DAO.md。56/43骨、69/73粗Cuboid，16张原clip、两套16×16四色、bbmodel/独立动画。专用伏地兽骨架/粗眉面颊与长爪、厚甲斗笠闭面刀兵；geo本身保留held_rock，闲置clip隐藏，五视图展示实际闲置。静态/握刀矩阵、四真实爪底接触点对应生产1.95/1.72高度偏移、十二墙IK包装层不设动画、旧生成器84资源保护、离线build通过。ape-dao1 26张/27条，含真实14tick起跳和18tick飞行、实际高地站稳后18tick产生投石弹；ape-wall1 13张/14条，包含真实墙面碰撞及4个无遮挡挂墙角度、攀爬及第24tick扑击，实际south/contact0.46875。全部图片已查看。当前、生产JAR、两个真实不可变运行快照84资源SHA一致，前26套不变。

## 第九批与普通怪队列核对

缚魂白布童子、纸人剑客已实际改造并验收，见 [第九批记录](CHILD-PAPER.md)。82/38骨、69/62 Cuboid、14原clip，实际16×16四色PNG与bbmodel/独立动画。使用cod2_voxel子目录保留他人的旧geo UV修正、旧动画与共享atlas五文件SHA；美术加载器绑定新路径。双手灯把/纸剑所有四分之一tick相对矩阵一致，四惯性包装骨不动画。白布童子40tick实际ServerPlayer诅咒、SoulBind和食物20→18；纸人真实致命近战32→1、目标后5格teleport、6tick客户端落点/12tick复原与7tick真实死亡。child-paper2为25图/26记录，paper-shed3补4图/5记录，均包含实际重载。child-paper1为保留的时序诊断失败，不充验收。最终90当前/JAR/不可变快照SHA、95新旧文件旧生成器保护、30套150运行及可编辑文件核对通过。

30/30是本队列普通怪美术数量，不代表Cod2全部任务完成，也不覆盖其他人正在制作的精英/Boss/secondary。继续检查已存在的精英造型和并行资源归属，既有Cod2删除记录保持，含玩法/生态/地下城的原文继续保留。

## 第十批：现有精英与召唤物

陷阵断头将、千机百炼偃师、机关小蛛已实际重做并验收，见 [第十批记录](ELITES.md)。46/70/19骨、85/89/46粗Cuboid、16原clip，三套16×16四色、bbmodel/独立动画。双膝跪倒、厚胸腰盆和双兽肩、六臂/机关厚箱、八阶梯足已实际看五方向、黑剪影与动作；巨刃/提头握持每四分之一tick相对矩阵一致。旧精英资源和所有生产技能/AI/renderer代码15文件SHA不变，另建cod2_voxel资源和独立美术加载器。

elites5真实Forge40图/41记录，含两精英真受击/死亡、各三招真服务端接触、小蛛owner/launch和自然引信及实际资源重载；全部40画面已查看。源文件/生产JAR/不可变游戏快照99资源SHA一致，前30普通怪不变。33套共165运行/可编辑文件，旧生成器隔离112文件保护通过。elites1误用旧QA已ABORTED，elites2未启动，elites3夹具目标误置FAIL，elites4通过功能但双腿交叉等视觉PARTIAL，均不作为最终资源验收。

本聊天当前完成33套美术（30普通怪+2现有精英+1召唤物）。鬼车-v2、cod6 Boss和禁卫由其他并行美术批次负责，保留；尚无实现的Cod2命名精英/Boss不能用旧实体改名替代。没有把整个cod2.txt标成完成，没有新增删除。

## 最终本地交付与补充实机核验

完整逐模型路径和SHA见 [DELIVERY_20261011.json](DELIVERY_20261011.json)：33套共99实际geo/动画/PNG，加入bbmodel与独立动画源为165文件。`build/cod2-voxel-build/libs/dynasty-1.4.0.jar` 为实际成功构建产物；`build-final-supplement.log` 结束为BUILD SUCCESSFUL。`jar-validation-final.json` 核对99当前资源、该JAR、elites5/elites6/load18-3真实不可变快照，前30套不变，QA未进生产JAR。

`elites6` 追加40图/41记录，真正Gecko baked胸骨hurt为7.28°/1.44°，两个真实death膝均−125°，抛头隐藏/巨刃握槽同变换/背箱85°/真实小蛛引信缩放均核对，40画面已实际查看。详见 [精英记录](ELITES.md) 和 `elite-baked-validation.json`。

`load18-3` 的空场、18静止、18物理行走、实际重载后18四场景原始图全部已查看；每个载入测量帧实际提交18不同Geo实体，行走每帧18个walk clip。18只均调用原Entity.move碰撞引擎，累计位移约22.98格，起终点距离约3.78格；帧中位约9.09–9.13ms。详见 [混合负载记录](MIXED-LOAD.md) 和 `mixed-load-validation.json`。这是关闭AI的本机几何成本观测，保留正常遮挡，不代表自然AI/多人战斗/TPS全部验收。

`prompt-preservation-final.json` 证明原备份减去既有7处删除与当前cod2.txt逐字节相同。本夜美术没有新增删除；完整地牢、生态、事件、缺失命名Boss/精英及第11类效果仍留原文。制作规范已保存在 `src/main/resources/assets/dynasty/AGENTS.md` 供后续沿用。夜间截止后已结束续作并删除dynasty-cod2自动化，无活动自有构建或客户端。关闭时33套全部165文件和生产JAR仍与已接受SHA一致，提示词原字节保持；详见NIGHT_CLOSE_20261011.json。
