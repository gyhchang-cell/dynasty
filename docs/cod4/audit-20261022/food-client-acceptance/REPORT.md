# COD4-9 食品与既有符：最终客户端验收

结论：原始请求9行展开为15个真实Registry物品，8食品和7既有符全部完成真实生产Minecraft客户端的原生输入验收。run02为26/26（19食品使用+7符），run03为16/16食品前后视角补充；最终校验933/933通过。此结论针对下述使用动作、持续时长与Build收益待办，不代替六阶段自然生存路线、装备获取或开局2–3小时节奏验收。

可供主协调关闭的原文（本任务未修改任何TODO）：

> 实机验收药品/酒/香/军粮的使用动作、持续时长与对应 Build 收益；已完成的物品注册和普通配方不重复制作。

原文来自 [cod4-before.txt:122](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/cod4-before.txt:122)；用途分母来自 [request.txt:283](/Users/a15356015027/Desktop/dynasty/docs/cod4/request.txt:283) 的COD4-9表。32刻、EAT/DRINK、具体数值均是当前实现的实测行为，原表给的是用途目标，没有另加NBT保持、点香专属动画或符必须持续使用32刻等契约。

最终机器证据见 [final-acceptance.json](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/final-acceptance.json)，逐项简表见 [food-outcomes.json](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/food-outcomes.json)，全部检查见 [native-verification.json](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/native-verification.json)，人工看图结论和图片SHA见 [visual-review.json](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/visual-review.json)。已保留并引用主协调的 [19次独立原生时钟复核](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/coordinator-native-use-audit.json) 和 [run02独立看图复核](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/coordinator-run02-screenshot-review.json)，没有覆盖它们。

## 8食品逐项结果

所有8项在连接中的LocalPlayer和同UUID原生ServerPlayer上，短取消前后均为3→3，重新持续完成后为2。每次完整使用的服务端start→finish差均为32个真实世界刻，Finish事件useTicks=32；没有直接调用finishUsingItem。32刻在20TPS下名义1.6秒，不据此声称实际墙钟恒定或长期真人游玩时长。run02覆盖第一/第三人称、回春丹/壮行酒副手和御寒标签壮行酒；run03另覆盖8项正面+8项背面。

下表“本次原生”指真实连接客户端run02；期限初值/清除/扣物/当前答题窗口由其Finish事件核对。“持续/到期/实际Build”中的长时段与伤害/连击恢复实验复用已跑通的routes-05原生服务端8项，和本次客户端证据明确分开，细节见后文。

| 物品 | 原始用途 | 动作/耗时/数量 | 实际收益 | 持续/到期/实际Build证据 | 对应记录 |
|---|---|---|---|---|---|
| 回春丹 `regen_pill` | 战斗回血，站桩/重甲流 | EAT / 32刻；3→3→2 | 真实100上限、40当前生命→52；再生II100刻，客户端结算后53。 | 服务端原生再生确实继续回血，完成后102刻已消失；冷却198刻仍在、202刻已结束。 | [本次原生](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-02/first-regen_pill-result.json) · [全身画面](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-03/front-regen_pill-held-late.png)；既有 `food_regen_pill` |
| 聚气丹 `qi_pill` | 临时怒气/连击强化，连击流 | EAT / 32刻；3→3→2 | 怒气0→2；聚气截止=完成刻+200，阳气100刻；既有advanceCombo实际从1推进至3。 | 聚气202刻已失效；怒气因20刻周期刷新，202刻仍2、222刻归0，不冒称200刻立即清零。冷却200刻。 | [本次原生](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-02/first-qi_pill-result.json) · [全身画面](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-03/front-qi_pill-held-late.png)；既有 `food_qi_pill` |
| 避毒丹 `antidote_pill` | 清毒+短暂免疫，毒沼/毒蝎 | EAT / 32刻；3→3→2 | 原有毒状态清除，免疫截止=完成刻+600。 | 在+10刻重新施毒，+12刻已被原生刷新清除；到+602刻再施毒，+604刻仍有毒，证明600刻窗口结束。冷却200刻。 | [本次原生](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-02/first-antidote_pill-result.json) · [全身画面](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-03/front-antidote_pill-held-late.png)；既有 `food_antidote_pill` |
| 状元酒 `zhuangyuan_wine` | 科举答题时间增加，文官流 | DRINK / 32刻；3→3→2 | 实际DynastyKeju.answerDurationMillis从30000→36000ms，截止=完成刻+1200。 | 原生+1222刻答题窗口已回到30000ms，非仅写入期限。冷却200刻。未将此功能测量冒称完整科举真人答题流程。 | [本次原生](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-02/first-zhuangyuan_wine-result.json) · [全身画面](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-03/front-zhuangyuan_wine-held-late.png)；既有 `food_zhuangyuan_wine` |
| 壮行酒 `marching_wine` | 战斗攻击增加且有混乱代价，军功流 | DRINK / 32刻；3→3→2 | 阳气100刻+反胃80刻；对同一QA亡灵靶的真实主攻击伤害0.9399414→1.0585938。 | 原生+102刻两效果均消失，主攻击伤害回到0.9399414；增益与负面实际共存。冷却200刻。 | [本次原生](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-02/first-marching_wine-result.json) · [全身画面](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-03/front-marching_wine-held-late.png)；既有 `food_marching_wine` |
| 安魂香 `soul_incense` | 驱阴魂/清阴气，夜战 | EAT / 32刻；3→3→2 | 实际阴气与灼魂均清除，近距亡灵targetIsPlayer由true→false。 | 清除与失去仇恨为即时收益；无额外持续光环契约，不虚构持续秒数。冷却200刻。 | [本次原生](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-02/first-soul_incense-result.json) · [全身画面](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-03/front-soul_incense-held-late.png)；既有 `food_soul_incense` |
| 引路香 `guide_incense` | 短时标记最近遗迹，探索 | EAT / 32刻；3→3→2 | 正常生成世界中实际结构定位成功，cod4Guide含真实目标/维度；期限+1200；动作栏方向/约1634格/余60秒可见。 | 原生+1222刻标记字段已删除，冷却1198刻仍在、1202刻已结束。证明定位调用/标记，不声称已走到遗迹或自然获得香。 | [本次原生](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-02/first-guide_incense-result.json) · [全身画面](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-03/front-guide_incense-held-late.png)；既有 `food_guide_incense` |
| 军粮 `army_ration` | 持续饱食，远征/围猎 | EAT / 32刻；3→3→2 | 饥饿10→20，实际饱和效果200刻。 | 原生+202刻饱和效果已消失；冷却200刻。没有将静止QA用例冒称整场远征饥饿压力测试。 | [本次原生](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-02/first-army_ration-result.json) · [全身画面](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-03/front-army_ration-held-late.png)；既有 `food_army_ration` |

原生冷却对8食品均验证了即时再次使用被阻止；除引路香1200刻外均200刻，均有到期前2刻仍在/到期后2刻消失的既有运行断言。安魂香是即时清除/转移仇恨，冷却时长不等同作用持续时长。避毒保护通过原生tick清理再次施加的毒，不夸大成任何时点都不可能出现毒图标。

现有 `cod4WarmWine` 标签壮行酒是附加用例，不新增第16个Registry：本次32刻/扣1、保留阳气与反胃、清除寒脉、温暖期限+1200均实测；没有另称本次跑完温暖效果整段到期。副手回春丹/壮行酒同样短取消0、完整扣1，左手使用画面已实际查看。

## 7既有瞬发符

原表的“火符/雷符/御风/隐身/金刚/摄魂/归乡”展开为7项，没有漏出分母。它们原生UseAnim=NONE、duration=0，没有食品start/stop/finish事件。各项真实单次点击数量16→15，随后按住重复施放4次到11，放开后不再消耗；对应5个原生服务端RightClickItem事件。不会要求瞬发符32刻或取消退还。

| Registry | 本次实际收益与画面 | 原生结果 |
|---|---|---|
| `fire_talisman` | 靶怪5000→4397、燃烧；火焰/烟和命中提示。 | [结果](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-02/first-fire_talisman-result.json) |
| `thunder_talisman` | 靶怪5000→4196、缓慢II/虚弱II；白粒子/伤害804/三雷命中提示。 | [结果](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-02/first-thunder_talisman-result.json) |
| `wind_talisman` | 靶怪5000→4798，玩家速度III/跳跃II/缓降；白色风粒子。 | [结果](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-02/first-wind_talisman-result.json) |
| `stealth_talisman` | 实际隐身/夜视/速度、清除靶怪对玩家仇恨；烟雾与图标。 | [结果](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-02/first-stealth_talisman-result.json) |
| `vajra_talisman` | 实际抗性III/力量II/抗火；对应图标和聊天提示。 | [结果](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-02/first-vajra_talisman-result.json) |
| `soul_talisman` | 单次后靶怪5000→4497、失明/虚弱；后续灵魂粒子可见。五次扣符不等于五次有效伤害。 | [结果](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-02/first-soul_talisman-result.json) |
| `return_talisman` | 真实位置变为[0.5,77,0.5]、清毒；森林出生点/传送粒子/回城提示。 | [结果](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance/run-02/first-return_talisman-result.json) |

符的持续效果只核对本次实际施加和即时反馈，没有声称重新跑完全部符效果到期。原表该行的任务来源/JEI用途不是本次客户端动作补充的新增制作；本报告只为上引食品动作/时长/Build验收待办提供收口证据。

## 实际输入、画面和相机

测试使用独立生产客户端，全包86个mod JAR、96个加载mod；原生LocalPlayer和集成服务端PlayerList内同UUID的ServerPlayer真实连接，SURVIVAL。输入由原生keyUse按下/保持/放开，进入MultiPlayerGameMode与原生网络路径；释放调用releaseUsingItem。QA记录Forge原生start/stop/finish/RightClickItem和client/server逐刻状态；驱动脚本的文件轮询等待不计入任何生存时长。

run03的128个采集状态全部记录并核对cameraEntity、renderCameraEntity、playerEntity、cameraType、玩家与相机位置。三者UUID均为 `31cf8578-bdae-3097-9f0a-19f2d16f6f96`、类型minecraft:player。玩家在 `[27.5,95.0,29.5]`，正面为THIRD_PERSON_FRONT、背面为THIRD_PERSON_BACK；每张状态的具体渲染相机位置见final-acceptance的camera_samples。靶怪侧移后玩家全身和举臂姿势可见，未将靶僵尸当玩家。

人工逐项看了8食品run03正面全身图、7符run02反馈图，并补看2张背面、2张副手、御寒变体及结算图；22张主证据+6张补充图的路径/SHA和具体可见内容均在visual-review.json。原始PNG未编辑，2560×1600。酒举杯/药丸进食/军粮碎屑均可见；香按现有EAT显示，没有擅自以动画风格替代原规格。

run01第三人称被QA南瓜靶怪挡住，作为早期夹具失败保留，最终验收排除所有run01视觉证据。run02只改私有靶怪位置补清晰全身；run03只增QA相机身份采集。还发现部分原生PNG读取停帧，例如run03的front-marching_wine-completed和settled像素相同，仍显示举物。该两帧不证明结束姿势、物品数量或精确时序；全部截图只用于实际看见的姿势/效果，32刻与扣物由独立原生事件证明。像素和同时采集状态不保证逐帧同步，未将原因未经证实的停帧归为生产缺陷。声音关闭，没有音频验收声明。

## 服务端持续时间复用与版本约束

复用 [routes-05/native-results.json](/Users/a15356015027/Desktop/dynasty/tools/cod4/journey-acceptance/evidence/routes/routes-05/native-results.json) 中8个 `food_<registry>` 成功记录，断言源码为 [JourneySupplyGameTests.java](/Users/a15356015027/Desktop/dynasty/tools/cod4/journey-acceptance/evidence/routes/routes-05/JourneySupplyGameTests.java)。这些是旧有独立原生ServerPlayer服务端实验，每世界刻推进原生player tick，实际完成配方扣料→原FTB目标→取消→32刻完整使用→到期；其初始材料/条件同样由QA提供。它们不是连接客户端，也不拿detached玩家冒充本次画面；只复用获准的持续时间和Build证据。

新客户端使用已由协调验证的生产修复JAR `0e1fbac34942714cd90a18ec1b404303b5d4d5bf96ce7c96277e16e561fe5c27`。与原验证生产JAR `ce92592ecd1e1e6e5584cfb05646fb8e82e3275b4d81b235910a1e996ec2458b` 的zip逐项差异仅3个WorkshopJei类；涉及食品、符、效果、装备行为、科举、连击的6个Java文件SHA在当前树、生产冻结源码和routes-05快照中全部一致，详见final-acceptance.implementation_binding。不是依据名称相似推测旧测试可复用。

## 范围、退出和交付

QA提供3食品/16符、原料（旧服务端实验）、100上限/40当前生命、饥饿10、毒/阴气/灼魂/寒脉和无AI亡灵靶；正常结构生成世界中使用浮空/无重力夹具，关闭自然刷怪、自然回血等。自然获取数量为0，不声称六阶段自然生存闭环或2–3小时实际开局节奏已过，也不将“没有真人”加为验收门槛。结构定位成功是真实调用，但不是完整探索路线。

run01 PID10053、run02 PID13525、run03 PID15192均由自身finish指令正常退出，exit-code均0，最后keyUse已释放。只读复用安装的生产启动器元数据/库/资源，客户端所有存档、配置、JAR覆盖、日志均在本任务私有profile。复核时modpack所有原始文件SHA与run02/run03启动快照一致；未覆盖其他代理实例、未修改正式Java/资产/用户整合包/任务主表/TODO。

改变的路径限于 [tools/cod4/food-client-acceptance/](/Users/a15356015027/Desktop/dynasty/tools/cod4/food-client-acceptance) 与 [docs/cod4/audit-20261022/food-client-acceptance/](/Users/a15356015027/Desktop/dynasty/docs/cod4/audit-20261022/food-client-acceptance)。脚本/QA helper、原始PNG/事件、分母、逐项收益、最终校验和本报告均在该范围。QA夹具/证据缺陷已明确修正或排除；本项没有新确认的生产代码缺陷，也没有生产修复。
