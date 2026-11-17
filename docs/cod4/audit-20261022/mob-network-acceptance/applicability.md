# COD4-1 实际双客户端适用矩阵

分母30：6中立、24敌对。虾兵为召唤额外实体，不计入30。夹具提供初始实体、装备/原料、平台与位置，不修改产品行为。

|序号|生物|registryId|自然仇恨|受击|特殊输入|死亡/拾取|
|---|---|---|---|---|---|---|
|1|流民饥民|famished_refugee|不主动选敌|受击逃跑且不反击|食物首次扣一并友好；第二客户再次喂食不重复扣款|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|2|山贼喽啰|bandit_thug|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|3|巡夜更夫|night_watchman|不主动选敌|中立受击逃跑并允许反击|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|4|江湖骗子|swindler|不主动选敌|受击逃跑且不反击|受伤开场→付铜钱→带实体UUID假药；非客户不能识破，原客户潜行持原假药识破；死亡还币一次|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|5|采药客|herb_picker|不主动选敌|受击逃跑且不反击|铜钱换2茶叶；全体共享200tick冷却，双客户隔离核对|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|6|赤狐|red_fox|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|自然攻击偷走一份可食物；死亡返还一次（当前实现为存储，非消费吃完）|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|7|灰狼|gray_wolf|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|8|野猪|wild_boar|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|9|巨蟒|giant_python|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|10|花豹|golden_leopard|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|11|树精|tree_spirit|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|12|石精|stone_sprite|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|13|灯笼鬼|lantern_ghost|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|14|剪纸童子|paper_cut_child|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|15|河童|river_imp|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|16|水鬼|drowning_ghost|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|17|鲤鱼精|carp_spirit|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|18|螺女|snail_maiden|不主动选敌|受击逃跑且不反击|中立采集/受击40tick缩壳；铜钱交易原需求不适用，真实交互无结果仅记录探测|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|19|蟹将|crab_soldier|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|20|蝙蝠妖|bat_demon|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|21|精卫鸟|jingwei_bird|不主动选敌|中立受击逃跑并允许反击|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|22|灰隼|gray_falcon|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|23|飞蝗群|locust_swarm|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|24|尸蟞|corpse_beetle|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|25|毒蝎|venom_scorpion|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|26|石蚯龙|stone_worm|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|27|纸钱鬼|paper_money_ghost|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|自然攻击偷铜钱一枚；死亡返还一次|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|28|孤魂野鬼|wandering_spirit|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|不适用特殊物品交互|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|29|机关木鹊|wooden_magpie|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|钢索维修20生命，满血不扣款|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|
|30|发条鼠|clockwork_rat|自然选中较近host，host旁观后转选peer|原生受击/仇恨；低血逃跑通用逻辑|原生客户端Q丢掉物→自然拾取偷一件；死亡返还一次|双客户端attack同一实体→单次原生LivingDropsEvent→共同争抢拾取，物品守恒|