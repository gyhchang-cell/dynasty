# COD4-1 真实双客户端生物交互验收

验收已完成；核心网络 30/30 通过，原需求全部适用机制矩阵 30 pass / 0 fail / 0 未覆盖。两名自动控制真实客户端、独立 UUID、原生 C2S，非 FakePlayer；不是两名真人，也不以真人参与作为门槛。

固定生产 Jar SHA256：`ce92592ecd1e1e6e5584cfb05646fb8e82e3275b4d81b235910a1e996ec2458b`。run-03/04/06 共 479 个阶段、164 张实际世界帧，六次客户端进程均 exit 0。原始断言失败 5 项：4 项 QA 判据/输入问题已用保留证据的补测澄清，1 项螺女铜钱探测不适用，均非产品失败。

## pass

- 30 类按 request 与 SecondaryMobs 完整核对；24 主动敌对自然选 host、host 旁观后转选 peer；6 中立不主动选敌。双方分别原生攻击的低血逃跑、受击反应及两端实体血量同步完成。更夫/精卫用全新实体分别验证双方独立挑衅；连续受击保留首个目标不当作隔离缺陷。
- 饥民首次喂食扣一、再次喂食不重复；采药客各自扣一铜钱得二茶叶，实体200tick冷却隔离；药草点真实等待1200tick后各得二茶叶、提前/重复无奖励。
- 骗子付款、带实体UUID假药、原客户识破及非客户拒绝通过。补测服务端事件trace记录双方潜行=true；stage3保留target但不攻击、受击逃跑通过。
- 赤狐可食物、纸钱鬼铜钱、发条鼠原生Q掉落各偷一件，标记原物死亡仅返还一次；骗子付币在识破前/后死亡也仅返还一次。
- 30 类基础死亡加4个主轮返还及1个识破后返还，共35次实际原生死亡、40个掉落实体；每尸单次事件，35次双方争抢拾取全部守恒。原始表正掉落种子为夹具，不声称重新统计掉率。

## 不适用探测（保留原始失败记录）

- **螺女铜钱交互没有入口/结果**：run-03/result-249.json，双方持铜钱真实 interact；服务端各三枚铜钱未变且无交易产物。源码只有中立、缩壳，不含交易定义。缩壳免伤与其余网络机制通过。原request:47没有螺女交易规格，通用交易只要求各自适用入口；本项不计产品缺陷或未完任务。先前“用户明确追加螺女交易”归因有误，现已纠正，不新增机制。

## 原文闭项

> [ ] 两名真实玩家验证仇恨、中立受击、喂食、交易、偷窃物返还和击杀掉落不重复；不要把 FakePlayer 测试等同于真实联机验收。

整条可判闭合：30类全部适用机制、双方隔离、掉落守恒以及真实客户端非FakePlayer证明通过。螺女铜钱探测不在需求分母。是否删TODO由主协调独立审计处理，本任务不改待办。真人主观观感和互联网延迟仅为覆盖边界。

## 完整矩阵

|#|registryId|中立/敌对|核心网络|特殊机制|结论|
|---|---|---|---|---|---|
|1|famished_refugee|中立|pass|pass|pass|
|2|bandit_thug|敌对|pass|不适用|pass|
|3|night_watchman|中立|pass|不适用|pass|
|4|swindler|中立|pass|pass|pass|
|5|herb_picker|中立|pass|pass|pass|
|6|red_fox|敌对|pass|pass|pass|
|7|gray_wolf|敌对|pass|不适用|pass|
|8|wild_boar|敌对|pass|不适用|pass|
|9|giant_python|敌对|pass|不适用|pass|
|10|golden_leopard|敌对|pass|不适用|pass|
|11|tree_spirit|敌对|pass|不适用|pass|
|12|stone_sprite|敌对|pass|不适用|pass|
|13|lantern_ghost|敌对|pass|不适用|pass|
|14|paper_cut_child|敌对|pass|不适用|pass|
|15|river_imp|敌对|pass|不适用|pass|
|16|drowning_ghost|敌对|pass|不适用|pass|
|17|carp_spirit|敌对|pass|不适用|pass|
|18|snail_maiden|中立|pass|pass|pass|
|19|crab_soldier|敌对|pass|不适用|pass|
|20|bat_demon|敌对|pass|不适用|pass|
|21|jingwei_bird|中立|pass|不适用|pass|
|22|gray_falcon|敌对|pass|不适用|pass|
|23|locust_swarm|敌对|pass|不适用|pass|
|24|corpse_beetle|敌对|pass|不适用|pass|
|25|venom_scorpion|敌对|pass|不适用|pass|
|26|stone_worm|敌对|pass|不适用|pass|
|27|paper_money_ghost|敌对|pass|pass|pass|
|28|wandering_spirit|敌对|pass|不适用|pass|
|29|wooden_magpie|敌对|pass|pass|pass|
|30|clockwork_rat|敌对|pass|pass|pass|

## 证据与边界

- applicability.json/md：原始分母、适用机制和来源哈希。report.json：逐类完整结果文件索引。
- run-03/04/06 的 connections、双端 manifest/input/render、服务端 result、原始 PNG、source-snapshot、退出码与 evidence-audit.json 均保留。
- qa-adjudications.json 与 native-shift-input-source.json：所有原始断言失败及补测定位；原失败文件不覆盖。
- 164张原始帧中，163张可证明本地第三人称玩家、另一玩家和当前生物同框；run-06/peer-view-0.png首帧本地玩家未入镜，只见另一玩家与生物，保留但排除三实体证明，详见visual-review.json。展示夹具 NoAI/摆位不冒充自然战斗。原始PNG是证据，contact拼图只供索引复核。
- 真人主观观感/音效、互联网延迟未覆盖；不作为本条新增门槛
- 四Jar私有实例，非完整整合包兼容或生存获取验收
- 初始实体/原料/装备/传送/高生命/击杀攻击属性/原始表正掉落种子均为明确服务端夹具
- 水生等在统一干平台上验证本条网络/受击/掉落；不声称全部独有战斗技能、游泳寻路或生成生态验收
- 展示为真实AFTER_LEVEL帧；NoAI/摆位展示不冒充自然战斗截图
- 普通crab_soldier夹具无cod4Summoner；用户已交主协调与Herschel的龙套租约蟹兵主动攻击缺陷不在本轮并行修改或验收范围
- 赤狐实际定义为偷一份可食物并储存，死亡返还一次；未把不存在的食物吃完消费阶段冒充通过

未改生产代码、资产、TODO、共享Jar或他人实例；本轮不修复产品，不并行改 SecondaryMob/SummonedGuard。
