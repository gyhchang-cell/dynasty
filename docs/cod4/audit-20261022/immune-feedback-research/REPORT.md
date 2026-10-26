# Boss Immune / 受击文本：实现研究进度

状态：**研究进行中，未达到1000处，尚未完成本项研究。**

本报告只汇总已经实际读取全文方法及自有调用链的记录。下载项目数、Java文件数、候选方法数、同链包装、平台移植、相同渲染链的颜色/数字/动画变体均不自动计数。机器校验只检查引用哈希和语义键唯一，语义去重仍由逐条人工式源码审阅承担，不能靠键不同自证独立。

原需求依据：本项目 `docs/cod4/request.txt:348` 的 Boss Immune 行要求“免疫”灰字、弹开微光、嗡鸣、不受此次控制影响、不刷屏；`:351` 要求服务端决定类型和目标、客户端播放。`:270–271` 普通阴阳体质免疫没有灰字要求，保留现有 type9 回执边界。不要把“纹丝不动”扩展为冻结Boss正常AI、走路或所有原生动作。

授权边界：仅本研究docs/tools目录；未启动游戏、未运行上游源码、未改正式Java/资产/原清单或待办。本文静态观察不能证明画面可辨识、声音合适或两端实际同步。文字及语义接入由协调岗承担，不转交模型制作；声音优先已有原版合适资源，不强制新录音。

**有效语义去重：26/1000；缺口：974。** 固定版本已取得完整或选定源码的项目21个，项目数量不计研究数。正式最小设计与静态验收条件尚未交付，待足额后综合，不提前实施。

## 已获得的具体认识（研究观察，未定案设计）

- 血量差值数字只能看到变化；零伤、抵抗、拒控需有明确语义生产点。Mine and Slash 有明确 nullified 回执，Dummy 则展示“无限血但仍可有实际伤害事件数字”的不同情形。
- `hurt=false` 不能单独等同于Boss免控：共享伤害桶、边界/阶段、方向盾、自源排除各不同；Harbinger与Ignis还能在最终拒绝前生产动作或声音。减到0.1、减半等不应标作完全免疫。
- 动作栏本地化提示不是目标头顶浮字。Leviathan直接攻击者/投射物owner的差别会改变是否得到提示。
- 出生点快照、跟随目标、屏幕投影是不同锚定实现；包里有entityId不等于有维度/代际防护。缺失实体、换世界和实体ID复用仍须逐链核查。
- 粒子总容量、数字横向分槽、累加伤害和按目标节流/事件去重不是一件事。当前样本不能凭总上限宣称“不刷屏”。
- 深度必须看实际提交模式和GL状态。M&S RenderUtils强制GL_ALWAYS，HUD投影链也无世界深度；Damage Engine的注释不能覆盖实际SEE_THROUGH/NORMAL提交分支。
- GUI渲染时钟不能替代独立tick寿命。Simple Combat Indicators使用partialTick差值递增age，静态不足以保证低帧率真实到期时间。
- 已发现死代码/未接活路径，明确0计数；普通玩家体质不因Boss需求而新增灰字门槛。

## 有效记录索引

| 序号 | 语义键 | 项目 / 固定提交 | 首个来源（完整引用见下文） |
|---|---|---|---|
| 1 | `dnp-health-delta-worldtext` | Smootheez/dnp / `b5789d994856` | [1.21.9/src/main/java/io/github/smootheez/dnp/mixin/LivingEntityMixin.java:14](https://github.com/Smootheez/dnp/blob/b5789d994856dd246f4d2b64084fdeeb78ee804f/1.21.9/src/main/java/io/github/smootheez/dnp/mixin/LivingEntityMixin.java#L14-L22) |
| 2 | `torohealth-tracked-health-particle` | ToroCraft/ToroHealth / `2e0bed33201f` | [src/main/java/net/torocraft/torohealth/bars/BarState.java:27](https://github.com/ToroCraft/ToroHealth/blob/2e0bed33201fedac040f72015c8887865b62dfad/src/main/java/net/torocraft/torohealth/bars/BarState.java#L27-L83) |
| 3 | `provihealth-eye-anchored-health-text` | Provismet/ProviHealth / `a2bd9b63077d` | [src/main/java/com/provismet/provihealth/mixin/LivingEntityMixin.java:77](https://github.com/Provismet/ProviHealth/blob/a2bd9b63077d07af75fba359898597000219fbb6/src/main/java/com/provismet/provihealth/mixin/LivingEntityMixin.java#L77-L96) |
| 4 | `tes-explicit-component-and-health-particle-chain` | Tslat/TslatEntityStatus / `1bec5eaf4b18` | [Common/src/main/java/net/tslat/tslatentitystatus/api/TESParticleAPI.java:38](https://github.com/Tslat/TslatEntityStatus/blob/1bec5eaf4b18db2b4561c80cbe02921662298e8d/Common/src/main/java/net/tslat/tslatentitystatus/api/TESParticleAPI.java#L38-L101) |
| 5 | `retro-health-sync-active-text` | bigenergy/ReRetroDamageIndicators / `1633f7dc8a78` | [src/main/java/com/github/alexmodguy/retrodamageindicators/mixins/LivingEntityMixin.java:33](https://github.com/bigenergy/ReRetroDamageIndicators/blob/1633f7dc8a78d2b5053f0efb0a9205075970b02f/src/main/java/com/github/alexmodguy/retrodamageindicators/mixins/LivingEntityMixin.java#L33-L56) |
| 6 | `tf-lich-shield-and-clone-rejection` | TeamTwilight/twilightforest / `9911cf7c4223` | [src/main/java/twilightforest/entity/boss/Lich.java:356](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/Lich.java#L356-L407) |
| 7 | `tf-naga-home-source-rejection` | TeamTwilight/twilightforest / `9911cf7c4223` | [src/main/java/twilightforest/entity/boss/Naga.java:347](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/Naga.java#L347-L364) |
| 8 | `tf-alpha-yeti-ranged-phase-projectile-rejection` | TeamTwilight/twilightforest / `9911cf7c4223` | [src/main/java/twilightforest/entity/boss/AlphaYeti.java:167](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/AlphaYeti.java#L167-L179) |
| 9 | `tf-knight-phantom-directional-shield-rejection` | TeamTwilight/twilightforest / `9911cf7c4223` | [src/main/java/twilightforest/entity/boss/KnightPhantom.java:310](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/KnightPhantom.java#L310-L341) |
| 10 | `tf-mounted-goblin-shared-shield-rejection` | TeamTwilight/twilightforest / `9911cf7c4223` | [src/main/java/twilightforest/entity/monster/UpperGoblinKnight.java:89](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/monster/UpperGoblinKnight.java#L89-L121) |
| 11 | `cataclysm-range-damagebucket-authority` | lender544/new1.20.1 / `819937203e22` | [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java:73](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java#L73-L192) |
| 12 | `cataclysm-crab-burrow-window-rejection-sound` | lender544/new1.20.1 / `819937203e22` | [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/Amethyst_Crab_Entity.java:58](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/Amethyst_Crab_Entity.java#L58-L63) |
| 13 | `cataclysm-leviathan-environment-immunity-actionbar` | lender544/new1.20.1 / `819937203e22` | [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity.java:312](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity.java#L312-L350) |
| 14 | `dummy-authoritative-hit-number-particle` | MehVahdJukaar/DuMmmMmmy / `dc75223afd7e` | [common/src/main/java/net/mehvahdjukaar/dummmmmmy/common/TargetDummyEntity.java:403](https://github.com/MehVahdJukaar/DuMmmMmmy/blob/dc75223afd7ed1c5eb7b2662d08274874fd500f2/common/src/main/java/net/mehvahdjukaar/dummmmmmy/common/TargetDummyEntity.java#L403-L580) |
| 15 | `tf-hydra-root-and-part-authority` | TeamTwilight/twilightforest / `9911cf7c4223` | [src/main/java/twilightforest/entity/boss/Hydra.java:575](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/Hydra.java#L575-L645) |
| 16 | `tf-urghast-reflected-fireball-immunity-exception` | TeamTwilight/twilightforest / `9911cf7c4223` | [src/main/java/twilightforest/entity/boss/UrGhast.java:147](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/UrGhast.java#L147-L181) |
| 17 | `cataclysm-boss-effect-allowlist-refusal` | lender544/new1.20.1 / `819937203e22` | [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java:228](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java#L228-L230) |
| 18 | `damageengine-level-source-merge-and-targeted-worldtext` | Ovear-Mitama/Damage-Engine / `3bcb595a6817` | [common/src/main/java/damage/engine/util/DamageTrackerHelper.java:1](https://github.com/Ovear-Mitama/Damage-Engine/blob/3bcb595a681729c3a9ab18c4e3d052f2a9958a74/common/src/main/java/damage/engine/util/DamageTrackerHelper.java#L1-L231) |
| 19 | `immersivedamage-local-attribution-shader-fallback-chain` | txnimc/ImmersiveDamageIndicators / `c2d3a9f748a2` | [src/main/java/toni/immersivedamageindicators/mixins/LivingEntityMixin.java:1](https://github.com/txnimc/ImmersiveDamageIndicators/blob/c2d3a9f748a28835f6aa1af9cbdb2e396da05cc7/src/main/java/toni/immersivedamageindicators/mixins/LivingEntityMixin.java#L1-L65) |
| 20 | `mineandslash-native-nullified-receipt-particle` | RobertSkalko/Mine-And-Slash-Rework / `13dab4218dbc` | [src/main/java/com/robertx22/mine_and_slash/mmorpg/MMORPG.java:190](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/mmorpg/MMORPG.java#L190-L210) |
| 21 | `cataclysm-harbinger-rejection-after-emp-transition` | lender544/new1.20.1 / `819937203e22` | [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Harbinger_Entity.java:190](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Harbinger_Entity.java#L190-L200) |
| 22 | `cataclysm-ignis-counterstrike-refusal-receipt` | lender544/new1.20.1 / `819937203e22` | [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/Ignis_Entity.java:287](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/Ignis_Entity.java#L287-L393) |
| 23 | `simplecombat-server-hit-to-projected-hud-text` | sam-makes-stuff/simple_combat_indicators / `3992a22e66bc` | [src/main/java/net/sam/simple_combat_indicators/SimpleCombatIndicators.java:1](https://github.com/sam-makes-stuff/simple_combat_indicators/blob/3992a22e66bc6c1ba114b9054ba53449e7a33737/src/main/java/net/sam/simple_combat_indicators/SimpleCombatIndicators.java#L1-L53) |
| 24 | `botania-gaia-trueplayer-authority-and-phase-timer` | VazkiiMods/Botania / `0ddec883d6ec` | [Xplat/src/main/java/vazkii/botania/common/entity/GaiaGuardianEntity.java:435](https://github.com/VazkiiMods/Botania/blob/0ddec883d6ec4c7be78525267e29cbf1bd98c672/Xplat/src/main/java/vazkii/botania/common/entity/GaiaGuardianEntity.java#L435-L470) |
| 25 | `ironspells-authoritative-evasion-and-shroud-native-receipts` | iron431/irons-spells-n-spellbooks / `9a88991f5ec6` | [src/main/java/io/redspace/ironsspellbooks/player/ServerPlayerEvents.java:116](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/player/ServerPlayerEvents.java#L116-L117) |
| 26 | `battletext-native-events-caption-reroute-and-worldtime-lifecycle` | GenuineSounds/Battle-Text / `e7ba15b0e8dc` | [src/main/java/ninja/genuine/battle/BattleText.java:1](https://github.com/GenuineSounds/Battle-Text/blob/e7ba15b0e8dc5881a275920891af46687ef213a3/src/main/java/ninja/genuine/battle/BattleText.java#L1-L100) |

## 逐项观察与边界

### 1. dnp-health-delta-worldtext

**全文调用链：** 客户端onSyncedDataUpdated仅health键→WeakHashMap前后血量→renderParticleNumber→TextParticle进入particleEngine→TextParticleGroup.extractRenderState→extract字形；所有这些方法合并1条。

**实际观察：** 首次见实体只缓存；零差不产生文字；实体高度*.55限1..4作初始锚点，随机上升和朝相机横移；32格配置距离和实体黑名单；30tick衰减，NORMAL深度字体；粒子档位限255/127/63但while>在追加前，可能短暂多1；队列未见主动剔除已自然死亡引用的分支。

**与本任务的关系：** 免疫无血差，须在服务端拒控处发明确语义，不能从零伤推断Boss免疫；可借鉴相机朝向、按实体大小限幅与总量边界。

**覆盖边界：** 1.21.9客户端实现，非Forge1.20.1现成适配；粒子出生后按世界点运动而非持续跟随目标；本链未见单独维度epoch；不证明观感。

固定来源：

- [1.21.9/src/main/java/io/github/smootheez/dnp/mixin/LivingEntityMixin.java:14–22](https://github.com/Smootheez/dnp/blob/b5789d994856dd246f4d2b64084fdeeb78ee804f/1.21.9/src/main/java/io/github/smootheez/dnp/mixin/LivingEntityMixin.java#L14-L22)；SHA256 `edbb8999e26af4f9a3f9de315fd09a2a88a76eea5e6266fad1dc2ab469c487d0`。
- [1.21.9/src/main/java/io/github/smootheez/dnp/handler/HandleTextParticle.java:28–130](https://github.com/Smootheez/dnp/blob/b5789d994856dd246f4d2b64084fdeeb78ee804f/1.21.9/src/main/java/io/github/smootheez/dnp/handler/HandleTextParticle.java#L28-L130)；SHA256 `1b772b4cd7688538bff273024de25513421ee7e46a7e82f73075f08015b7d2ff`。
- [1.21.9/src/main/java/io/github/smootheez/dnp/particle/TextParticle.java:22–71](https://github.com/Smootheez/dnp/blob/b5789d994856dd246f4d2b64084fdeeb78ee804f/1.21.9/src/main/java/io/github/smootheez/dnp/particle/TextParticle.java#L22-L71)；SHA256 `2bc1b2e7578a984fcfc86830a1329f7eb1a21b3b4d0ac43cb1632546b420c775`。
- [1.21.9/src/main/java/io/github/smootheez/dnp/particle/TextParticleGroup.java:18–29](https://github.com/Smootheez/dnp/blob/b5789d994856dd246f4d2b64084fdeeb78ee804f/1.21.9/src/main/java/io/github/smootheez/dnp/particle/TextParticleGroup.java#L18-L29)；SHA256 `412eaeeaca6b8aea5a54e30a5c837e89202f7f2498f474ec4e52e69a8a416c0d`。

### 2. torohealth-tracked-health-particle

**全文调用链：** 已渲染LivingEntity经prepareRenderInWorld登记状态，玩家tick推进BarStates→BarState检测血差→BarParticle；世界render尾部遍历粒子，drawDamageNumber；同链总计1。

**实际观察：** 血量先min(max)，ceil差用于显示，累计伤害延迟20tick；粒子初始在半身朝相机移一个宽度，随机速度+重力，50tick后删除；按相机距离裁剪，启depth；状态缓存每200tick检查现世界实体ID/存活/chunk，未见世界键参与STATES。

**与本任务的关系：** 整数化后零值被drawDamageNumber跳过，更不能借其判断免疫；Boss短文字应有独立语义而沿用有界世界空间生命周期，缓存需防跨世界ID复用。

**覆盖边界：** 该版本为旧Fabric命名；无专用免疫字段；已读完整相关方法但未运行；全局无硬粒子数量上限不应照搬。

固定来源：

- [src/main/java/net/torocraft/torohealth/bars/BarState.java:27–83](https://github.com/ToroCraft/ToroHealth/blob/2e0bed33201fedac040f72015c8887865b62dfad/src/main/java/net/torocraft/torohealth/bars/BarState.java#L27-L83)；SHA256 `ca7e16fb9b7d422b16a3e712370d4bea97c23b51e4529a40806d7f8c48e04064`。
- [src/main/java/net/torocraft/torohealth/bars/BarStates.java:17–63](https://github.com/ToroCraft/ToroHealth/blob/2e0bed33201fedac040f72015c8887865b62dfad/src/main/java/net/torocraft/torohealth/bars/BarStates.java#L17-L63)；SHA256 `f993c17fb017a2b2d8a583ce3f6f5bf9b58b43f079bafdb6e7cfa0c6adc35886`。
- [src/main/java/net/torocraft/torohealth/bars/BarParticle.java:28–63](https://github.com/ToroCraft/ToroHealth/blob/2e0bed33201fedac040f72015c8887865b62dfad/src/main/java/net/torocraft/torohealth/bars/BarParticle.java#L28-L63)；SHA256 `9a0758a3ad91071b2056def6d5de17f274b1df4d954809714df0f9659bb82e71`。
- [src/main/java/net/torocraft/torohealth/bars/ParticleRenderer.java:16–59](https://github.com/ToroCraft/ToroHealth/blob/2e0bed33201fedac040f72015c8887865b62dfad/src/main/java/net/torocraft/torohealth/bars/ParticleRenderer.java#L16-L59)；SHA256 `98c0273d541df9e1b343a9ce2569bf5724c44ba6d339972fd2fa9cd1e87ef739`。
- [src/main/java/net/torocraft/torohealth/bars/HealthBarRenderer.java:40–65](https://github.com/ToroCraft/ToroHealth/blob/2e0bed33201fedac040f72015c8887865b62dfad/src/main/java/net/torocraft/torohealth/bars/HealthBarRenderer.java#L40-L65)；SHA256 `f6b13b529ce051cafb94ccc6fbce87ee556966585f6f58e56cd10049a8e15f5e`。
- [src/main/java/net/torocraft/torohealth/bars/HealthBarRenderer.java:157–168](https://github.com/ToroCraft/ToroHealth/blob/2e0bed33201fedac040f72015c8887865b62dfad/src/main/java/net/torocraft/torohealth/bars/HealthBarRenderer.java#L157-L168)；SHA256 `f6b13b529ce051cafb94ccc6fbce87ee556966585f6f58e56cd10049a8e15f5e`。
- [src/main/java/net/torocraft/torohealth/mixin/WorldRendererMixin.java:27–41](https://github.com/ToroCraft/ToroHealth/blob/2e0bed33201fedac040f72015c8887865b62dfad/src/main/java/net/torocraft/torohealth/mixin/WorldRendererMixin.java#L27-L41)；SHA256 `11c49cdd668f496bc3dc761598477d56831acac98edf4576ecc6c0f6b6b44f76`。
- [src/main/java/net/torocraft/torohealth/mixin/PlayerEntityMixin.java:22–31](https://github.com/ToroCraft/ToroHealth/blob/2e0bed33201fedac040f72015c8887865b62dfad/src/main/java/net/torocraft/torohealth/mixin/PlayerEntityMixin.java#L22-L31)；SHA256 `f9750317b1dfa43efeb229aabe455c804ceaf5823a0178615b6d75e6ff6306e1`。

### 3. provihealth-eye-anchored-health-text

**全文调用链：** LivingEntity tick尾更新HealthContainer前后值→非相机实体且距离内血差spawn HealthParticleEffect→HealthParticle初始化同时创建TextParticle→自定义particle group提取→submitText。特效/文字两层合并1条。

**实际观察：** 眼高初始锚；RISING/GRAVITY/STATIC三种运动是同链配置不另计；40tick，前半放大后半缩小，文字插值朝相机POLYGON_OFFSET全亮；数值codec限1..8字符整数，网络codec字符串8字符。用int前后值减法可把小血差显示0。

**与本任务的关系：** 可借鉴有限寿命和字形朝向，但免疫中文不应塞入只允许整数的序列化通道；Boss拒控文字需独立类型/翻译键，普通体质无需灰字。

**覆盖边界：** 不能以本实现证明汉字或Forge1.20.1兼容；本链是客户端血量观察，不表示服务端免疫回执；没有观察实机。

固定来源：

- [src/main/java/com/provismet/provihealth/mixin/LivingEntityMixin.java:77–96](https://github.com/Provismet/ProviHealth/blob/a2bd9b63077d07af75fba359898597000219fbb6/src/main/java/com/provismet/provihealth/mixin/LivingEntityMixin.java#L77-L96)；SHA256 `ad8ac2abd702eeced8aee95bcce7d7075455387e9333b24997129a190fb58996`。
- [src/main/java/com/provismet/provihealth/util/HealthContainer.java:11–29](https://github.com/Provismet/ProviHealth/blob/a2bd9b63077d07af75fba359898597000219fbb6/src/main/java/com/provismet/provihealth/util/HealthContainer.java#L11-L29)；SHA256 `acba2dca17535b047bb989c14edf36f7f1d4f3605cee97fe9724c359808fdd5a`。
- [src/main/java/com/provismet/provihealth/particle/HealthParticle.java:25–104](https://github.com/Provismet/ProviHealth/blob/a2bd9b63077d07af75fba359898597000219fbb6/src/main/java/com/provismet/provihealth/particle/HealthParticle.java#L25-L104)；SHA256 `1df334ac93423b294cbcd46a5c0e0ef279718f813417128d0a824f50a5e02b33`。
- [src/main/java/com/provismet/provihealth/particle/TextParticle.java:23–60](https://github.com/Provismet/ProviHealth/blob/a2bd9b63077d07af75fba359898597000219fbb6/src/main/java/com/provismet/provihealth/particle/TextParticle.java#L23-L60)；SHA256 `517f87a40c373cef0945a95f788e381740ca3591e020b87c0d5683747ab1770f`。
- [src/main/java/com/provismet/provihealth/particle/TextParticleRenderer.java:25–66](https://github.com/Provismet/ProviHealth/blob/a2bd9b63077d07af75fba359898597000219fbb6/src/main/java/com/provismet/provihealth/particle/TextParticleRenderer.java#L25-L66)；SHA256 `2a8047210845bb7007a7eed8b847d84d52a494b88eb6fdd77800429507531f0b`。
- [src/main/java/com/provismet/provihealth/mixin/ParticleManagerMixin.java:25–38](https://github.com/Provismet/ProviHealth/blob/a2bd9b63077d07af75fba359898597000219fbb6/src/main/java/com/provismet/provihealth/mixin/ParticleManagerMixin.java#L25-L38)；SHA256 `10d5af777cf76044ab97923e04e14709a94b524676e26d75c13dec4e35ff4290`。
- [src/main/java/com/provismet/provihealth/particle/HealthParticleEffect.java:14–43](https://github.com/Provismet/ProviHealth/blob/a2bd9b63077d07af75fba359898597000219fbb6/src/main/java/com/provismet/provihealth/particle/HealthParticleEffect.java#L14-L43)；SHA256 `0df3672a10980f27b17fe143871adfa2306b620e6407a6bf80621e668dbf882a`。

### 4. tes-explicit-component-and-health-particle-chain

**全文调用链：** 显式Component请求按实体tracking或世界点200格发包→entityId/Component/初始坐标→客户端state存在才收实体文字→统一manager→ComponentParticle朝相机居中；血差入口亦走同manager，claims优先消费差额，故整套合并1条，不拆API/packet/不同loader/数字包装。

**实际观察：** 可直接发Component而不需血差；实体版本packet附眼位+ID，缺state丢弃，不回退成未知实体；纯坐标版entityId=-1；GenericTESParticle按lifetime自减并只判断寿命，所读本体没有维度/实体死亡清除；claims处理返回未消费差额，避免同一血差原生/定制双画；自动血差0提前返回，瞬杀/满血恢复是翻译Component。 完整追到每帧LevelRenderer.submitFeatures→manager→TextRenderHelper.inWorldSubmit→自定义phase→WorldspaceTextFeatureRenderer.buildGroup→GlyphVisitor render；透明字体可能SEE_THROUGH，非默认一律深度遮挡。通用辅助类只支持同一条研究，不另外计数。

**与本任务的关系：** 直接语义Component链比血差推断适合零伤拒控；实体缺失应安全丢弃；本体寿命与world epoch须另检；不把同manager的多包装计多条。

**覆盖边界：** 已补读particle tick、世界submit挂钩、CustomSubmit phase、FeatureRenderer注册和字形visit完整方法。现代Minecraft抽取/提交架构不能直接搬到1.20.1；粒子本体只有寿命校验，未据此确认跨维度清理；不证明观感。

固定来源：

- [Common/src/main/java/net/tslat/tslatentitystatus/api/TESParticleAPI.java:38–101](https://github.com/Tslat/TslatEntityStatus/blob/1bec5eaf4b18db2b4561c80cbe02921662298e8d/Common/src/main/java/net/tslat/tslatentitystatus/api/TESParticleAPI.java#L38-L101)；SHA256 `5ef1fe646fc9f3b059a0d5af85445f01732f33e2d57be0e499a11be7cb78202c`。
- [NeoForge/src/main/java/net/tslat/tslatentitystatus/networking/TESNeoForgeNetworking.java:87–110](https://github.com/Tslat/TslatEntityStatus/blob/1bec5eaf4b18db2b4561c80cbe02921662298e8d/NeoForge/src/main/java/net/tslat/tslatentitystatus/networking/TESNeoForgeNetworking.java#L87-L110)；SHA256 `c2b7cbebb88aefac42fafb4015442546c312beafc7a13ea995aaccc252ba9381`。
- [Common/src/main/java/net/tslat/tslatentitystatus/core/networking/packet/NewComponentParticlePacket.java:22–56](https://github.com/Tslat/TslatEntityStatus/blob/1bec5eaf4b18db2b4561c80cbe02921662298e8d/Common/src/main/java/net/tslat/tslatentitystatus/core/networking/packet/NewComponentParticlePacket.java#L22-L56)；SHA256 `740994e330032802ec391b052c6d2ccf947740f0ada418b5dfe9a4ed407e1e61`。
- [Common/src/main/java/net/tslat/tslatentitystatus/api/client/util/TESClientParticleUtil.java:22–91](https://github.com/Tslat/TslatEntityStatus/blob/1bec5eaf4b18db2b4561c80cbe02921662298e8d/Common/src/main/java/net/tslat/tslatentitystatus/api/client/util/TESClientParticleUtil.java#L22-L91)；SHA256 `27a39c20dccfd87fab2a12e2214dcfc1acfb02dcf0d55b1b9b3f7afa4a4a4ce3`。
- [Common/src/main/java/net/tslat/tslatentitystatus/core/particle/TESParticleManager.java:40–139](https://github.com/Tslat/TslatEntityStatus/blob/1bec5eaf4b18db2b4561c80cbe02921662298e8d/Common/src/main/java/net/tslat/tslatentitystatus/core/particle/TESParticleManager.java#L40-L139)；SHA256 `1d371a1726c9a988c3bc91e19e8cdea2e0f0d6f637253756b9a51ae3f773e33f`。
- [Common/src/main/java/net/tslat/tslatentitystatus/core/particle/type/GenericTESParticle.java:21–49](https://github.com/Tslat/TslatEntityStatus/blob/1bec5eaf4b18db2b4561c80cbe02921662298e8d/Common/src/main/java/net/tslat/tslatentitystatus/core/particle/type/GenericTESParticle.java#L21-L49)；SHA256 `6d6a88f3303cd3c5ed5ab76e4d0f21aec75d50c2b431fac98b2a977247fa5976`。
- [Common/src/main/java/net/tslat/tslatentitystatus/core/particle/type/ComponentParticle.java:17–40](https://github.com/Tslat/TslatEntityStatus/blob/1bec5eaf4b18db2b4561c80cbe02921662298e8d/Common/src/main/java/net/tslat/tslatentitystatus/core/particle/type/ComponentParticle.java#L17-L40)；SHA256 `ea1b9082acc8c6a8e38192adcaf5dfaddc8d11b53ad3e649ade60a49e5d854d1`。
- [Common/src/main/java/net/tslat/tslatentitystatus/api/client/object/TESParticle.java:40–105](https://github.com/Tslat/TslatEntityStatus/blob/1bec5eaf4b18db2b4561c80cbe02921662298e8d/Common/src/main/java/net/tslat/tslatentitystatus/api/client/object/TESParticle.java#L40-L105)；SHA256 `0cbd572a6fdcf3ea22b5d777b777cf23e096726003d85bed7918b4d4fbe8ac4f`。
- [Common/src/main/java/net/tslat/tslatentitystatus/core/state/TESEntityState.java:94–148](https://github.com/Tslat/TslatEntityStatus/blob/1bec5eaf4b18db2b4561c80cbe02921662298e8d/Common/src/main/java/net/tslat/tslatentitystatus/core/state/TESEntityState.java#L94-L148)；SHA256 `2f287934ca4e6dae91880f64528101507dd3e6636c0ffd5c8019d54d80797960`。
- [Common/src/main/java/net/tslat/tslatentitystatus/mixin/client/ParticleEngineMixin.java:1–23](https://github.com/Tslat/TslatEntityStatus/blob/1bec5eaf4b18db2b4561c80cbe02921662298e8d/Common/src/main/java/net/tslat/tslatentitystatus/mixin/client/ParticleEngineMixin.java)；SHA256 `c444eb153328e841fc74ef00c47e537aa0617c9bd9184cf01a7cf352d7aa163a`。
- [Common/src/main/java/net/tslat/tslatentitystatus/mixin/client/LevelRendererMixin.java:1–78](https://github.com/Tslat/TslatEntityStatus/blob/1bec5eaf4b18db2b4561c80cbe02921662298e8d/Common/src/main/java/net/tslat/tslatentitystatus/mixin/client/LevelRendererMixin.java)；SHA256 `69b0721cd2745b2a854de14b1b9621fa12f9414f612ebb2d08c14d36c70bcbed`。
- [Common/src/main/java/net/tslat/tslatentitystatus/mixin/client/SubmitNodeCollectionMixin.java:1–54](https://github.com/Tslat/TslatEntityStatus/blob/1bec5eaf4b18db2b4561c80cbe02921662298e8d/Common/src/main/java/net/tslat/tslatentitystatus/mixin/client/SubmitNodeCollectionMixin.java)；SHA256 `e2c8454716f7371247ee00691eb1be56df115333a9dabc0bb4b73815a09c1003`。
- [Common/src/main/java/net/tslat/tslatentitystatus/mixin/client/FeatureRenderDispatcherMixin.java:1–29](https://github.com/Tslat/TslatEntityStatus/blob/1bec5eaf4b18db2b4561c80cbe02921662298e8d/Common/src/main/java/net/tslat/tslatentitystatus/mixin/client/FeatureRenderDispatcherMixin.java)；SHA256 `2b1ebc669dc073a61d282f0298ec3a47c72f77a9f3e6b3e6a3ed65d0a12fddfe`。
- [Common/src/main/java/net/tslat/tslatentitystatus/api/client/object/renderhelper/TextRenderHelper.java:1–422](https://github.com/Tslat/TslatEntityStatus/blob/1bec5eaf4b18db2b4561c80cbe02921662298e8d/Common/src/main/java/net/tslat/tslatentitystatus/api/client/object/renderhelper/TextRenderHelper.java)；SHA256 `c6683b133474b88d259bfe421f3c13150125ab333d7e35cd4bfe2de494a65da0`。
- [Common/src/main/java/net/tslat/tslatentitystatus/api/client/object/renderhelper/WorldspaceTextFeatureRenderer.java:1–84](https://github.com/Tslat/TslatEntityStatus/blob/1bec5eaf4b18db2b4561c80cbe02921662298e8d/Common/src/main/java/net/tslat/tslatentitystatus/api/client/object/renderhelper/WorldspaceTextFeatureRenderer.java)；SHA256 `2222e45d6c68383e74bfc3145d8d52845dce44c20f19806ac45b8740415d300d`。

### 5. retro-health-sync-active-text

**全文调用链：** health DATA同步首次初始化不显示→实体仍在level才spawnHurtParticles→独立activeDamageTexts→ClientTick重力和age→RenderLevel.AFTER_ENTITIES字体绘制；没有使用同仓DamageIndicatorParticle类，后者不可另计。

**实际观察：** 最大100文字直接丢新；出生实体眼高随机XZ，正血差绿负红；15..20tick，重力与缩放随age；有camera才tick，无camera清空；实际不描边分支SEE_THROUGH，描边字体八向；world render不检查HUD screen，不能承诺GUI遮挡。

**与本任务的关系：** 独立活动短文字列表可避免造服务端实体；需要明确世界切换清理和深度策略；零伤拒控不会触发health变化，不能直接套这个入口。

**覆盖边界：** 与astryxion同属Retro来源家族，多版本/移植先合并，不把其包装/旧Particle类/平台分别计。客户端实现不证明Boss语义或可读观感。

固定来源：

- [src/main/java/com/github/alexmodguy/retrodamageindicators/mixins/LivingEntityMixin.java:33–56](https://github.com/bigenergy/ReRetroDamageIndicators/blob/1633f7dc8a78d2b5053f0efb0a9205075970b02f/src/main/java/com/github/alexmodguy/retrodamageindicators/mixins/LivingEntityMixin.java#L33-L56)；SHA256 `146d0ca075419db4d81cc7350c1b090d6367d200757d9537c074ed7181fda412`。
- [src/main/java/com/github/alexmodguy/retrodamageindicators/RetroDamageIndicators.java:91–112](https://github.com/bigenergy/ReRetroDamageIndicators/blob/1633f7dc8a78d2b5053f0efb0a9205075970b02f/src/main/java/com/github/alexmodguy/retrodamageindicators/RetroDamageIndicators.java#L91-L112)；SHA256 `2ac2fc7fa114c40365358390cd7b5dade2f1aa8364c94a30f392d0ea052d429f`。
- [src/main/java/com/github/alexmodguy/retrodamageindicators/RetroDamageIndicators.java:306–423](https://github.com/bigenergy/ReRetroDamageIndicators/blob/1633f7dc8a78d2b5053f0efb0a9205075970b02f/src/main/java/com/github/alexmodguy/retrodamageindicators/RetroDamageIndicators.java#L306-L423)；SHA256 `2ac2fc7fa114c40365358390cd7b5dade2f1aa8364c94a30f392d0ea052d429f`。
- [src/main/java/com/github/alexmodguy/retrodamageindicators/RetroDamageIndicators.java:460–478](https://github.com/bigenergy/ReRetroDamageIndicators/blob/1633f7dc8a78d2b5053f0efb0a9205075970b02f/src/main/java/com/github/alexmodguy/retrodamageindicators/RetroDamageIndicators.java#L460-L478)；SHA256 `2ac2fc7fa114c40365358390cd7b5dade2f1aa8364c94a30f392d0ea052d429f`。

### 6. tf-lich-shield-and-clone-rejection

**全文调用链：** 原生hurtServer入口→瞬移不可见/影分身/同源巫妖/盾层判定→拒绝return false；破盾分支更新同步盾值并调用完整粒子构造→tracking玩家包→enqueueWork→当前玩家level.addParticle。完整hurtServer及其盾值getter、粒子辅助和包编解码/处理均已读；成功受伤后的传送行为不作为本条研究对象。

**实际观察：** 影分身有独立受击声；普通盾拒绝有格挡声和ENTITY_DAMAGE gameEvent；可破盾魔法damage>2削一层仍返回false，产生16颗面向攻击源的破盾粒子。没有任何文字组件；gameEvent出现并不表示血量损失。

**与本任务的关系：** 免疫语义应来自明确拒绝分支，不能以ENTITY_DAMAGE、格挡声或零血差推断。攻击成功破盾与完全无效应可区分；粒子与文字属于语义之后的表现。

**覆盖边界：** 未验证像素、网络运行或传送AI。粒子快照包无目标ID/维度epoch，当前level处理不等于长期目标绑定。Boss专用规则不能扩到普通阴阳体质。

固定来源：

- [src/main/java/twilightforest/entity/boss/Lich.java:356–407](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/Lich.java#L356-L407)；SHA256 `349b2b1a56ef7266ddd4cc18e5fa07869b5167ea99b9c46a5cae2a9c5d0305c9`。
- [src/main/java/twilightforest/entity/boss/Lich.java:824–857](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/Lich.java#L824-L857)；SHA256 `349b2b1a56ef7266ddd4cc18e5fa07869b5167ea99b9c46a5cae2a9c5d0305c9`。
- [src/main/java/twilightforest/components/entity/FortificationShieldAttachment.java:93–126](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/components/entity/FortificationShieldAttachment.java#L93-L126)；SHA256 `4022e623d36fef93954f95194b614634ef1477a00c19171e0cb8aa91dc8f4197`。
- [src/main/java/twilightforest/network/ParticlePacket.java:17–77](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/network/ParticlePacket.java#L17-L77)；SHA256 `13e431c33588b16f9d56ba71568cf351325903517a3a86d175d57e878feea1e7`。

### 7. tf-naga-home-source-rejection

**全文调用链：** 原生isInvulnerableTo→分别检查source实体和direct实体→isOtherEntityWithinHomeArea→三轴home bounds→home GlobalPos维度有效性；hurtServer仅在super成功后记伤害/眩晕累计。

**实际观察：** 爆炸直接拒绝；攻击者或投射物源任一越过home矩形边界也拒绝。无有效同维度home时边界辅助返回true。本链无专用S2C文字或声音。

**与本任务的关系：** Boss免疫原因可与攻击来源及区域有关；目标ID相同不能证明两次事件原因相同，维度/来源必须纳入语义分析。

**覆盖边界：** 只读模组覆写和home辅助，原版super以平台契约为界；不把无专用文本称作灰字实现。

固定来源：

- [src/main/java/twilightforest/entity/boss/Naga.java:347–364](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/Naga.java#L347-L364)；SHA256 `53caec5adb91a6463929f1f5e6444c4a41f50a4fb946f6f2df334e42009f6007`。
- [src/main/java/twilightforest/entity/boss/Naga.java:428–446](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/Naga.java#L428-L446)；SHA256 `53caec5adb91a6463929f1f5e6444c4a41f50a4fb946f6f2df334e42009f6007`。
- [src/main/java/twilightforest/entity/EnforcedHomePoint.java:46–60](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/EnforcedHomePoint.java#L46-L60)；SHA256 `bb20ce2b48aafb46e3cbd50e6e9270278fb356505e4a9b65a3fe84ad6e15d597`。

### 8. tf-alpha-yeti-ranged-phase-projectile-rejection

**全文调用链：** hurtServer完整覆写→canRampage本地布尔+isTired同步标志+IS_PROJECTILE标签→拒绝；否则super成功才置canRampage；setTired重置canRampage。

**实际观察：** 只在不能狂暴且未疲劳时免疫投射物；承受一次有效伤害会改变后续拒绝条件。拒绝路径没有自定义文本、粒子或声音。

**与本任务的关系：** 同一目标的免疫可随阶段变化，不能在客户端永久缓存“此Boss免疫”；拒绝回执应对应当次服务器决策。

**覆盖边界：** 未研究狂暴AI全时序或原版伤害内部；本条只计完整阶段拒绝链，不按三个状态分支拆数。

固定来源：

- [src/main/java/twilightforest/entity/boss/AlphaYeti.java:167–179](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/AlphaYeti.java#L167-L179)；SHA256 `79274f75491e46463b647e4fb29da2f35042c647f382f52fd2a6a2a00e662217`。
- [src/main/java/twilightforest/entity/boss/AlphaYeti.java:277–296](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/AlphaYeti.java#L277-L296)；SHA256 `79274f75491e46463b647e4fb29da2f35042c647f382f52fd2a6a2a00e662217`。

### 9. tf-knight-phantom-directional-shield-rejection

**全文调用链：** 原生hurtServer→完整isDamageSourceBlocked→pierce箭排除、BYPASSES_SHIELD、实际blocking item、sourceposition和水平点积→原版SHIELD_BLOCK声音→false；否则super。

**实际观察：** 正面且实际举盾才阻挡；穿刺箭、绕盾伤害、无源位置不走拒绝。使用已有原版格挡音，不需要新录音。

**与本任务的关系：** 格挡与Boss拒控是不同语义；不应把所有hurtServer false都标成Boss Immune。可借鉴原版声音资源与明确判定点。

**覆盖边界：** 代码注明该辅助为VanillaCopy；这里只计模组实际接入的整条Boss拒绝与声音链，不计原版复制方法为另一条，不证明画面。

固定来源：

- [src/main/java/twilightforest/entity/boss/KnightPhantom.java:310–341](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/KnightPhantom.java#L310-L341)；SHA256 `2c79a78ad7d78112b33059f7a1a99d7c039bae92904b308d532f143dc3ea832b`。

### 10. tf-mounted-goblin-shared-shield-rejection

**全文调用链：** 上层/下层hurtServer均以攻击角度进入同一个takeHitOnShield→disabled/斧头/伤害阈值→声音、盾值/禁用同步→拒绝；server AI恢复禁用，破盾广播STOP_ATTACKING→客户端breakItem。两个实体入口合为一条。

**实际观察：** 斧头首次命中禁用盾并被挡，后续禁用期直接不挡；disabled计数后置++达到100时恢复。累计3次高伤破盾，非正面可随机损盾。骑乘下层委托上层盾，不能把上下实体各计一次。

**与本任务的关系：** 共享盾/部件应归到同一语义目标，显示去重不能盲按命中部件刷屏；同步禁用状态与事件反馈不同。已有SHIELD_BREAK/BLOCK足以提供可选原版声音依据。

**覆盖边界：** 此为普通怪盾行为参考，不能据此新增普通体质灰字门槛；未做实际破盾画面或乘骑同步验收。

固定来源：

- [src/main/java/twilightforest/entity/monster/UpperGoblinKnight.java:89–121](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/monster/UpperGoblinKnight.java#L89-L121)；SHA256 `3c9d3b5a0aa2a74eceb32e2dfd054c6a7b7db65680573da82d8152fe594a58f4`。
- [src/main/java/twilightforest/entity/monster/UpperGoblinKnight.java:138–190](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/monster/UpperGoblinKnight.java#L138-L190)；SHA256 `3c9d3b5a0aa2a74eceb32e2dfd054c6a7b7db65680573da82d8152fe594a58f4`。
- [src/main/java/twilightforest/entity/monster/UpperGoblinKnight.java:237–248](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/monster/UpperGoblinKnight.java#L237-L248)；SHA256 `3c9d3b5a0aa2a74eceb32e2dfd054c6a7b7db65680573da82d8152fe594a58f4`。
- [src/main/java/twilightforest/entity/monster/UpperGoblinKnight.java:267–360](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/monster/UpperGoblinKnight.java#L267-L360)；SHA256 `3c9d3b5a0aa2a74eceb32e2dfd054c6a7b7db65680573da82d8152fe594a58f4`。
- [src/main/java/twilightforest/entity/monster/LowerGoblinKnight.java:155–188](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/monster/LowerGoblinKnight.java#L155-L188)；SHA256 `5aecd6e7b500c0c3f168993c295855b1dc426729d055f02aaf978bfac5efffa6`。

### 11. cataclysm-range-damagebucket-authority

**全文调用链：** 完整hurt入口及tick衰减链→原版isInvulnerableTo→bypass直接super→damageCap→calculateRange(source owner平方距离)→rangeCap到1.5倍线性减伤/更远拒绝→伤害桶→super结果false回滚桶；两个动画Boss基类同构链合并一条。

**实际观察：** range=-1无来源时不做范围拒绝；1.5倍处return false。伤害桶耗尽后并非免疫，而是amount=0.1继续super；受伤失败才回滚桶。tick按DpsCap/20衰减，AI关闭时不衰减。此链没有专用拒绝文本。

**与本任务的关系：** 伤害限流、部分减伤与拒控免疫必须分开，不能见hurtTime/cap就显示Immune。复用基类的多个Boss不重复计。

**覆盖边界：** 只读模组拥有的权威判定到原版super契约；不推断配置实际值或原版受伤内部，不证明任何灰字/运行观感。

固定来源：

- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java:73–192](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java#L73-L192)；SHA256 `0a2729372ae9a857d0eae7e01f50c8dc59d1eb9057a118f0ae94a3c38850c955`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/InternalAnimationMonster/IABossMonsters/IABoss_monster.java:129–249](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/InternalAnimationMonster/IABossMonsters/IABoss_monster.java#L129-L249)；SHA256 `8af844b7be3f4f151e9ca266e66fb9d17be749dad494d6fa1a0f96c52aa230b4`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/etc/Animation_Monsters.java:97–99](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/etc/Animation_Monsters.java#L97-L99)；SHA256 `0d0627a0cace404f105e5419cdf607f1a0a38ad048994a1a85bf7f5f5a57ffca`。

### 12. cataclysm-crab-burrow-window-rejection-sound

**全文调用链：** 完整hurt覆写读取当前动画和tick字段→CRAB_BURROW限定开区间→排除bypass→ANVIL_LAND原版音→false；未命中时进入已读共享Boss基类。

**实际观察：** 只在动画tick>9且<52期间挡普通伤害，边界9/52不挡；音量0.4音调2.0，拒绝路径没有粒子/文字。动画整个65tick并非全程无敌。

**与本任务的关系：** 视觉动画长度不可替代当次服务器拒绝区间；声音可以采用现有原版资源，文字语义需在实际false处接入。

**覆盖边界：** 动画更新/广播由lionfishapi外部契约承担，本条不把该库算研究或声称同步已验；不按每个动画帧拆条。

固定来源：

- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/Amethyst_Crab_Entity.java:58–63](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/Amethyst_Crab_Entity.java#L58-L63)；SHA256 `cf1474e98e0b8f29142c98bab49b5d954f9580bffcfe5f2264a0c5ae72e36592`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/Amethyst_Crab_Entity.java:149–162](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/Amethyst_Crab_Entity.java#L149-L162)；SHA256 `cf1474e98e0b8f29142c98bab49b5d954f9580bffcfe5f2264a0c5ae72e36592`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/LLibrary_Monster.java:57–81](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/LLibrary_Monster.java#L57-L81)；SHA256 `4c0b3e269a287687dee4fb0fa1cd89d7edf1bfbcb5621385448828676fb2633c`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java:73–137](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java#L73-L137)；SHA256 `0a2729372ae9a857d0eae7e01f50c8dc59d1eb9057a118f0ae94a3c38850c955`。

### 13. cataclysm-leviathan-environment-immunity-actionbar

**全文调用链：** 部件hurt→parent.attackEntityFromPart→parent.hurt；完整环境判断canInFluidType→FluidType.canSwim(self)；非可泳环境且配置开启、非bypass，directEntity为Player时displayClientMessage(translatable,true)，随后拒绝false。其余进共享hurt链，冲刺期成功受伤可触发STUN。

**实际观察：** 这是原生拒绝处的本地化文本回执，但载体是攻击者动作栏，不是目标头顶。检查的是directEntity，所以玩家射箭的direct为箭时不会命中Player提示分支。配置默认true。模组本方法无独立文本节流/事件去重。 已核对同提交en_us/zh_cn第84行分别为离水无敌英/中文提示，未声明GRAY样式。

**与本任务的关系：** 权威拒绝可显式发本地化语义，不需血量改变；攻击者/直接命中体要区分。部件必须映射本体，动作栏回执不能当作灰色目标锚定浮字范例。

**覆盖边界：** canSwim不等于简单isInWater，原版消息网络/GUI为平台契约；资源key与中英值已核对，不证明实机本地化。无游戏验收、无像素结论。

固定来源：

- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity.java:312–350](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity.java#L312-L350)；SHA256 `dc3af7a939ba1b13efed51404be77d61bd0efbf9433e87ae3e4984d1801ccad1`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity.java:367–389](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Entity.java#L367-L389)；SHA256 `dc3af7a939ba1b13efed51404be77d61bd0efbf9433e87ae3e4984d1801ccad1`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Part.java:59–66](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Leviathan/The_Leviathan_Part.java#L59-L66)；SHA256 `d20ca43b622d4c1adaf149403ed4c58dcb7c3f7185e2e7da804f18a49f8da409`。
- [src/main/java/com/github/L_Ender/cataclysm/config/CMCommonConfig.java:134–140](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/config/CMCommonConfig.java#L134-L140)；SHA256 `9186e4fd4adf95d7cf355da69a32bb0372db277ae3bd5ba6de7b3eb5bf0a8d6c`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java:73–137](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java#L73-L137)；SHA256 `0a2729372ae9a857d0eae7e01f50c8dc59d1eb9057a118f0ae94a3c38850c955`。
- [src/main/resources/assets/cataclysm/lang/en_us.json:84–84](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/resources/assets/cataclysm/lang/en_us.json#L84)；SHA256 `aaadbd486529e4c13bbe20fc349dc4870e286b3d3608c5ee8a7e4a84fab79c4f`。
- [src/main/resources/assets/cataclysm/lang/zh_cn.json:84–84](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/resources/assets/cataclysm/lang/zh_cn.json#L84)；SHA256 `37313b64c7282e09c32de4d5b2e170254a1d891e3c19fee1aa73e50f54c9b7a6`。

### 14. dummy-authoritative-hit-number-particle

**全文调用链：** 完整服务端hurt/setHealth/actualDamage→source/crit记录匹配→有战斗追踪玩家才发entityID+amount+damageType+crit；完整包读写/handle→客户端解析目标→particleFactory→35tick独立文字粒子→camera billboard+两次NORMAL font draw。重载/平台包装合并1条；Moonlight网络注册/发包为明确外部API边界。

**实际观察：** setHealth在无限血Dummy不实际降血也能发伤害数，说明同步血差不是唯一生产点。服务端玩家追踪300tick；同tickanimationPosition累加不等于伤害数字去重，每次仍可发包；客户端五个横向槽循环，目标当前位置+1出生后不跟随；35tick淡出，alpha最低4避免字体当不透明。NORMAL深度测试并非穿墙；暴击文字保留translatable Component。

**与本任务的关系：** 应在权威语义点发事件；伤害数与免疫文案需要独立类型。完整目标ID解析可以在目标不存在时不生成；出生点快照与持续锚定是不同选择，去重不能靠横向分槽假定已做。

**覆盖边界：** 包handle未显式检查Minecraft.level为空；无维度epoch/UUID/自定义冷却可见于本链；粒子生命周期由原版particle engine持有。不把Dummy模型/贴图当本任务研究，不做资产复制。平台网络和可选CriticalStrike getter为外部契约，未运行验证。

固定来源：

- [common/src/main/java/net/mehvahdjukaar/dummmmmmy/common/TargetDummyEntity.java:403–580](https://github.com/MehVahdJukaar/DuMmmMmmy/blob/dc75223afd7ed1c5eb7b2662d08274874fd500f2/common/src/main/java/net/mehvahdjukaar/dummmmmmy/common/TargetDummyEntity.java#L403-L580)；SHA256 `bd15e1e9953e432cca275510975638e47757617551dbea4c51341e251aa62aeb`。
- [common/src/main/java/net/mehvahdjukaar/dummmmmmy/common/TargetDummyEntity.java:612–700](https://github.com/MehVahdJukaar/DuMmmMmmy/blob/dc75223afd7ed1c5eb7b2662d08274874fd500f2/common/src/main/java/net/mehvahdjukaar/dummmmmmy/common/TargetDummyEntity.java#L612-L700)；SHA256 `bd15e1e9953e432cca275510975638e47757617551dbea4c51341e251aa62aeb`。
- [common/src/main/java/net/mehvahdjukaar/dummmmmmy/common/TargetDummyEntity.java:819–821](https://github.com/MehVahdJukaar/DuMmmMmmy/blob/dc75223afd7ed1c5eb7b2662d08274874fd500f2/common/src/main/java/net/mehvahdjukaar/dummmmmmy/common/TargetDummyEntity.java#L819-L821)；SHA256 `bd15e1e9953e432cca275510975638e47757617551dbea4c51341e251aa62aeb`。
- [common/src/main/java/net/mehvahdjukaar/dummmmmmy/common/TargetDummyEntity.java:861–926](https://github.com/MehVahdJukaar/DuMmmMmmy/blob/dc75223afd7ed1c5eb7b2662d08274874fd500f2/common/src/main/java/net/mehvahdjukaar/dummmmmmy/common/TargetDummyEntity.java#L861-L926)；SHA256 `bd15e1e9953e432cca275510975638e47757617551dbea4c51341e251aa62aeb`。
- [common/src/main/java/net/mehvahdjukaar/dummmmmmy/network/ClientBoundDamageNumberMessage.java:24–129](https://github.com/MehVahdJukaar/DuMmmMmmy/blob/dc75223afd7ed1c5eb7b2662d08274874fd500f2/common/src/main/java/net/mehvahdjukaar/dummmmmmy/network/ClientBoundDamageNumberMessage.java#L24-L129)；SHA256 `86e8badd84b394d412aca68cf14a5ee127423779a37e859cd669faeb4b5fe33c`。
- [common/src/main/java/net/mehvahdjukaar/dummmmmmy/network/ModMessages.java:8–15](https://github.com/MehVahdJukaar/DuMmmMmmy/blob/dc75223afd7ed1c5eb7b2662d08274874fd500f2/common/src/main/java/net/mehvahdjukaar/dummmmmmy/network/ModMessages.java#L8-L15)；SHA256 `4ca463c3c42d6cf9aca474113dc329940e7994af4ec2ea6dddc3bbbcc4459357`。
- [common/src/main/java/net/mehvahdjukaar/dummmmmmy/DummmmmmyClient.java:48–51](https://github.com/MehVahdJukaar/DuMmmMmmy/blob/dc75223afd7ed1c5eb7b2662d08274874fd500f2/common/src/main/java/net/mehvahdjukaar/dummmmmmy/DummmmmmyClient.java#L48-L51)；SHA256 `ab2576984a7f09d61e6f6ab4f6d2a8e39da88b441004ab046da1735b29272a43`。
- [common/src/main/java/net/mehvahdjukaar/dummmmmmy/client/DamageNumberParticle.java:31–222](https://github.com/MehVahdJukaar/DuMmmMmmy/blob/dc75223afd7ed1c5eb7b2662d08274874fd500f2/common/src/main/java/net/mehvahdjukaar/dummmmmmy/client/DamageNumberParticle.java#L31-L222)；SHA256 `f72ed94e4955eb8a8730c2e9a02b9ed2f08addd2af49165686a26515029161be`。
- [common/src/main/java/net/mehvahdjukaar/dummmmmmy/configs/ClientConfigs.java:76–124](https://github.com/MehVahdJukaar/DuMmmMmmy/blob/dc75223afd7ed1c5eb7b2662d08274874fd500f2/common/src/main/java/net/mehvahdjukaar/dummmmmmy/configs/ClientConfigs.java#L76-L124)；SHA256 `81a97869981c11cb4cd20e2286b22c90700fb80f0f873f3d5a9935d7aed4f650`。
- [common/src/main/java/net/mehvahdjukaar/dummmmmmy/configs/ClientConfigs.java:146–191](https://github.com/MehVahdJukaar/DuMmmMmmy/blob/dc75223afd7ed1c5eb7b2662d08274874fd500f2/common/src/main/java/net/mehvahdjukaar/dummmmmmy/configs/ClientConfigs.java#L146-L191)；SHA256 `81a97869981c11cb4cd20e2286b22c90700fb80f0f873f3d5a9935d7aed4f650`。
- [common/src/main/java/net/mehvahdjukaar/dummmmmmy/configs/CritMode.java:1–21](https://github.com/MehVahdJukaar/DuMmmMmmy/blob/dc75223afd7ed1c5eb7b2662d08274874fd500f2/common/src/main/java/net/mehvahdjukaar/dummmmmmy/configs/CritMode.java#L1-L21)；SHA256 `618ad368b7e5ec1494de450a99fd14a62ad57cbcb5b0cab01896704f58dcf612`。
- [common/src/main/java/net/mehvahdjukaar/dummmmmmy/common/CritRecord.java:1–35](https://github.com/MehVahdJukaar/DuMmmMmmy/blob/dc75223afd7ed1c5eb7b2662d08274874fd500f2/common/src/main/java/net/mehvahdjukaar/dummmmmmy/common/CritRecord.java#L1-L35)；SHA256 `337eaa3c00c8636791973a00f591d259173ab7adfb316a79b1114ba532de5cbc`。
- [common/src/main/java/net/mehvahdjukaar/dummmmmmy/compat/CritCompat.java:1–14](https://github.com/MehVahdJukaar/DuMmmMmmy/blob/dc75223afd7ed1c5eb7b2662d08274874fd500f2/common/src/main/java/net/mehvahdjukaar/dummmmmmy/compat/CritCompat.java#L1-L14)；SHA256 `e6294be5aaf9ac59a150a79275e9fe1c34bb416dc3b23d0d2a8fe28e64f48d5c`。

### 15. tf-hydra-root-and-part-authority

**全文调用链：** 完整HydraPart.hurtServer委托parent.attackEntityFromPart→服务端检查、同源本体/部件排除、死头/死颈排除、source owner平方距离→张嘴条件下super全伤/闭嘴时round(伤害/护甲倍率)；root.hurtServer只接受BYPASSES_INVULNERABILITY。已读完整所有决策方法和mouth/dead/addDamage辅助；其他地形破坏副作用不计。

**实际观察：** 本体根节点的false不代表所有部位免伤。普通距离阈值400是平方距离（20格），迫击炮多200平方单位，不是多200格。dying/dead部位拒绝；部件成功后才ENTITY_DAMAGE。闭嘴减伤可能四舍五入到0，但不能统一标Boss拒控。

**与本任务的关系：** 文字反馈的语义目标必须归本体，拒绝原因却要保留部位/阶段，避免本体和部件重复通知；不能拿根hurt覆写孤立判断整个Boss。

**覆盖边界：** 头状态动画时间表和原版super内部不在本条计数对象；尚无文字/自定义拒绝回执，不据静态推断画面。

固定来源：

- [src/main/java/twilightforest/entity/boss/Hydra.java:575–645](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/Hydra.java#L575-L645)；SHA256 `4e9627fdbb4cfc2781690fd0ae5e7bed312becf50fdfe8f0c298984b4411b1be`。
- [src/main/java/twilightforest/entity/boss/HydraPart.java:93–100](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/HydraPart.java#L93-L100)；SHA256 `9478a5c9294d3e826567aa9508fd01f6aff89d96bd29500a91bd63bf556687df`。
- [src/main/java/twilightforest/entity/boss/HydraHeadContainer.java:801–807](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/HydraHeadContainer.java#L801-L807)；SHA256 `f600a313b97139f7d16fac7f1cbd8dea1712de458b3018fd88c8339f0792148a`。
- [src/main/java/twilightforest/entity/boss/HydraHeadContainer.java:942–948](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/HydraHeadContainer.java#L942-L948)；SHA256 `f600a313b97139f7d16fac7f1cbd8dea1712de458b3018fd88c8339f0792148a`。
- [src/main/java/twilightforest/entity/boss/HydraHeadContainer.java:969–971](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/HydraHeadContainer.java#L969-L971)；SHA256 `f600a313b97139f7d16fac7f1cbd8dea1712de458b3018fd88c8339f0792148a`。

### 16. tf-urghast-reflected-fireball-immunity-exception

**全文调用链：** 完整isInvulnerableTo→isReflectedFireball以direct LargeFireball+source Player识别反弹→火焰/窒息/原版免伤条件；同文件hurtServer完整读用于核对tantrum=damage/10与真实healthLost记录的区别。

**实际观察：** 玩家反弹LargeFireball显式豁免免伤判定；同一种火球伤害的攻击者身份会改变结果。tantrum仅十分之一减伤，不是immune；完整拒绝判断本身无自定义文本/声音。

**与本任务的关系：** 服务端需保留直接来源和归属来源，展示原因不能只按伤害类型。减伤的低数值不能自动显示灰字。

**覆盖边界：** 本条研究主体为两个完整免伤判定方法；tantrum AI/getter/phase切换不计作完整生命周期研究。未运行网络或可视验收。

固定来源：

- [src/main/java/twilightforest/entity/boss/UrGhast.java:147–181](https://github.com/TeamTwilight/twilightforest/blob/9911cf7c4223ee7909e97659d0621a87683c8272/src/main/java/twilightforest/entity/boss/UrGhast.java#L147-L181)；SHA256 `5b9dc21d4df120773a65bca26321bc8d3100aa7cf852c2ba7b8412df5dc6d2cd`。

### 17. cataclysm-boss-effect-allowlist-refusal

**全文调用链：** 完整两个Boss基类canBeAffected→同一个EFFECTIVE_FOR_BOSSES_LOOKUP.contains→lazy registry tag对象→tag.contains；tag以mob_effect注册并提供实际默认资源。两个同构基类与全部白名单值合并1条，不按效果种类计数。

**实际观察：** 未列入白名单的效果在调用super前直接拒绝。默认白名单含slowness/mining_fatigue等有害效果，因此不能称“Boss全体免控/免负面”。Lazy缓存的是ITag对象，未发现此小类主动重新获取逻辑；是否随数据包更新取决于Forge标签对象契约，静态不推测reload故障。拒绝处没有文字、声音、额外网络回执。

**与本任务的关系：** Boss拒控文本应来自明确的canBeAffected/效果拒绝语义，不能从hasEffect=false推断（也可能未尝试施加）；Boss规则和普通玩家体质保持分域。

**覆盖边界：** 这里只读原生覆写和全部自有辅助到Forge接口契约；未验调用者addEffect结果、原生网络同步或画面；JSON条目和通用Lazy包装都不另计。

固定来源：

- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java:228–230](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java#L228-L230)；SHA256 `0a2729372ae9a857d0eae7e01f50c8dc59d1eb9057a118f0ae94a3c38850c955`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/InternalAnimationMonster/IABossMonsters/IABoss_monster.java:290–292](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/InternalAnimationMonster/IABossMonsters/IABoss_monster.java#L290-L292)；SHA256 `8af844b7be3f4f151e9ca266e66fb9d17be749dad494d6fa1a0f96c52aa230b4`。
- [src/main/java/com/github/L_Ender/cataclysm/init/ModTag.java:138–140](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/init/ModTag.java#L138-L140)；SHA256 `1a80d1bca9066029c6298d3837903c439e621dba7741204c6d3c82cef43791ee`。
- [src/main/java/com/github/L_Ender/cataclysm/init/ModTag.java:164–166](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/init/ModTag.java#L164-L166)；SHA256 `1a80d1bca9066029c6298d3837903c439e621dba7741204c6d3c82cef43791ee`。
- [src/main/java/com/github/L_Ender/cataclysm/util/LazyTagLookup.java:9–33](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/util/LazyTagLookup.java#L9-L33)；SHA256 `58afd43c4cab1ef4f40c1724ba3d5b860ab0a2537b60009c8dbeb5765096e65e`。
- [src/main/resources/data/cataclysm/tags/mob_effect/effective_for_bosses.json:1–36](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/resources/data/cataclysm/tags/mob_effect/effective_for_bosses.json#L1-L36)；SHA256 `baa03755247b2b7e66e05acac2acb989f83c6c832206224f9c647f1ae5b5f9d1`。

### 18. damageengine-level-source-merge-and-targeted-worldtext

**全文调用链：** 已读完整NeoForge生产事件注册：LivingIncomingDamage捕获快照→LivingDamage.Post实损→pending按tick/ServerLevel对象/target/directSource合并→ServerTick.Post flush→同level玩家S2C→完整客户端receiver过滤→IndicatorPos完整512格射线锚定→addIndicator客户端合并/容量→完整renderWorld及其所属辅助函数链→Anima drawWorldText3D辅助→完整WorldText3D drawComponent→原版font.drawInBatch。两层合并、所有重载、颜色/出场/追踪模式均合1条，不拆包装计数。

**实际观察：** health+absorption损失大于0或killed才产包，immune零变化不发。服务端去重有level对象边界，只合连续pending同键，换键会flush；客户端可选按目标ID/无ID距离0.35合并，heal/kill分离，出场开始后不再合并。容量0=不限；时钟为wall clock，500ms清理，持续命中推迟出场。entity模式每帧current level按ID解析目标并插值，失去目标停最后点；crosshair模式固定前6格。实际调用先seeThrough再normal，减少动画时只穿透；不能照注释声称被方块遮挡。

**与本任务的关系：** 必须单独产生拒控语义事件；可借鉴服务端维度内去重和客户端有界队列，但目标身份/维度生命周期不能只用数字ID。显示模式必须核对实际render调用参数。

**覆盖边界：** 研究固定源码的模组自有链；外部Anima辅助固定HEAD不保证与DE声明1.0.7二进制完全一致，不作为可直接粘贴/构建兼容证明。仅复核辅助绘制方法，动画基础库不逐个计数。NeoForge入口仅登录重置mod检测，未在所读路径找到清空所有飘字的登出/维度回调；跨维度遗留属于待验证风险，不直接定产品bug。无游戏/像素验收。

固定来源：

- [common/src/main/java/damage/engine/util/DamageTrackerHelper.java:1–231](https://github.com/Ovear-Mitama/Damage-Engine/blob/3bcb595a681729c3a9ab18c4e3d052f2a9958a74/common/src/main/java/damage/engine/util/DamageTrackerHelper.java#L1-L231)；SHA256 `fb8976394f6c901eeb8bd370f1e627791fc7042d44bfd984aad2679bf904420f`。
- [common/src/main/java/damage/engine/network/DamagePayload.java:1–43](https://github.com/Ovear-Mitama/Damage-Engine/blob/3bcb595a681729c3a9ab18c4e3d052f2a9958a74/common/src/main/java/damage/engine/network/DamagePayload.java#L1-L43)；SHA256 `f3ad77d51a8cbc17bfbb10352fb32f22ebaff2c37bc7ba105959a7bf387f95c4`。
- [common/src/client/java/damage/engine/hud/indicator/DamageIndicator.java:1–740](https://github.com/Ovear-Mitama/Damage-Engine/blob/3bcb595a681729c3a9ab18c4e3d052f2a9958a74/common/src/client/java/damage/engine/hud/indicator/DamageIndicator.java#L1-L740)；SHA256 `dd72c3dd4c5746b1ac034bcbdb92195c620763eea4cf2d6d0bbe73267c21f26f`。
- [common/src/client/java/damage/engine/client/IndicatorPos.java:1–58](https://github.com/Ovear-Mitama/Damage-Engine/blob/3bcb595a681729c3a9ab18c4e3d052f2a9958a74/common/src/client/java/damage/engine/client/IndicatorPos.java#L1-L58)；SHA256 `8c2408d9ae79993167bc38b232c598097680edc6d2724467361bdd50f80a21b4`。
- [common/src/client/java/damage/engine/mixin/client/ClientTickMixin.java:1–76](https://github.com/Ovear-Mitama/Damage-Engine/blob/3bcb595a681729c3a9ab18c4e3d052f2a9958a74/common/src/client/java/damage/engine/mixin/client/ClientTickMixin.java#L1-L76)；SHA256 `3cb75dbac8dd18499d13f4242096cbe761fbde920aa968525f8b3deed3807141`。
- [neoforge/src/main/java/damage/engine/DamageEngine.java:1–53](https://github.com/Ovear-Mitama/Damage-Engine/blob/3bcb595a681729c3a9ab18c4e3d052f2a9958a74/neoforge/src/main/java/damage/engine/DamageEngine.java#L1-L53)；SHA256 `4679cc8e93076561e42a1df811041bc59a2a7a9164e38398331723e7ce5178ee`。
- [neoforge/src/main/java/damage/engine/DamageEngineClient.java:1–94](https://github.com/Ovear-Mitama/Damage-Engine/blob/3bcb595a681729c3a9ab18c4e3d052f2a9958a74/neoforge/src/main/java/damage/engine/DamageEngineClient.java#L1-L94)；SHA256 `9084657551b3a4377257d3f8b987404922606ac15a05b3284d38a9f1acc9950d`。
- [neoforge/src/main/java/damage/engine/network/NetworkSetup.java:1–151](https://github.com/Ovear-Mitama/Damage-Engine/blob/3bcb595a681729c3a9ab18c4e3d052f2a9958a74/neoforge/src/main/java/damage/engine/network/NetworkSetup.java#L1-L151)；SHA256 `444b2473c70b0951297c76506444bae56844209f3d07ec82ccead6c634a6344d`。
- 辅助（0计数）：[Ovear-Mitama/Anima/common/src/client/java/anima/api/AnimaApi.java](https://github.com/Ovear-Mitama/Anima/blob/5089a46d28e5fe4addbe8868e5bfe5b3f7f8471f/common/src/client/java/anima/api/AnimaApi.java#L119-L165)；通用库只补字体提交/深度模式边界，不单独计数；版本适配仍待确认
- 辅助（0计数）：[Ovear-Mitama/Anima/common/src/client/java/anima/client/world/WorldText3D.java](https://github.com/Ovear-Mitama/Anima/blob/5089a46d28e5fe4addbe8868e5bfe5b3f7f8471f/common/src/client/java/anima/client/world/WorldText3D.java#L198-L293)；通用库只补字体提交/深度模式边界，不单独计数；版本适配仍待确认

### 19. immersivedamage-local-attribution-shader-fallback-chain

**全文调用链：** 完整tick HEAD血差缓存→TAIL要求getLastDamageSource.entity是LocalPlayer→一tick一个particle标志→factory→完整DamageParticle构造消息/回调/渲染/tick；shader检测动态选择vanilla字体回调或Caxton，ImmersiveMessage.render→manager.getRenderer→VanillaRenderer完整render→回调DamageParticle.renderMessage→两次NORMAL字体提交。平台注册、反射检测、原版/自定义字体回调、粒子生命周期均已读。

**实际观察：** 同源说明明确来自TargetDummy：继承的35tick寿命/相机姿态不再单独计数。本条区别是客户端本地攻击归属过滤、tick血差聚合及替换消息渲染/着色器回退，不是另一个Dummy版本。零血差无immune生产点；5秒消息时钟与35tick粒子寿命各自存在；粒子出生世界点固定不持续跟随。shader启用临时forceVanillaRenderer，结束复位，没有try/finally；不据此静态认定运行故障。

**与本任务的关系：** 可读性需核对真实字体渲染分支；普通受伤飘字的本地攻击归属过滤不能冒充Boss拒控回执。自定义字体与着色器冲突不必靠新增贴图解决。

**覆盖边界：** 同源视觉代码已合并去重；计数仅一个具有不同生产/归属/兼容语义的完整整合链。外部消息库为固定候选源码边界，未核对整包实际依赖Jar，没有编译/实机证明。LAST_ATTACK_SWING UUID缓存未在所读链找到清理，不断言泄漏。

固定来源：

- [src/main/java/toni/immersivedamageindicators/mixins/LivingEntityMixin.java:1–65](https://github.com/txnimc/ImmersiveDamageIndicators/blob/c2d3a9f748a28835f6aa1af9cbdb2e396da05cc7/src/main/java/toni/immersivedamageindicators/mixins/LivingEntityMixin.java#L1-L65)；SHA256 `06524a3a328206976334541e52fc46e20d03e97c92f55422ac6b2408935a5f84`。
- [src/main/java/toni/immersivedamageindicators/mixins/PlayerMixin.java:1–26](https://github.com/txnimc/ImmersiveDamageIndicators/blob/c2d3a9f748a28835f6aa1af9cbdb2e396da05cc7/src/main/java/toni/immersivedamageindicators/mixins/PlayerMixin.java#L1-L26)；SHA256 `597afb16e668e1e27e2d8bdbdbc8a8bd37c2541603899ca472275daeeb8ddddf`。
- [src/main/java/toni/immersivedamageindicators/particle/DamageParticle.java:1–301](https://github.com/txnimc/ImmersiveDamageIndicators/blob/c2d3a9f748a28835f6aa1af9cbdb2e396da05cc7/src/main/java/toni/immersivedamageindicators/particle/DamageParticle.java#L1-L301)；SHA256 `d557b9bd051137ae5a2d2339165c74026273fb1ba3dd6cb7cc08fa7f269ddb15`。
- [src/main/java/toni/immersivedamageindicators/foundation/ParticleRegistry.java:1–41](https://github.com/txnimc/ImmersiveDamageIndicators/blob/c2d3a9f748a28835f6aa1af9cbdb2e396da05cc7/src/main/java/toni/immersivedamageindicators/foundation/ParticleRegistry.java#L1-L41)；SHA256 `02a0b95ef0e160604ac8c1ef7b73a3cf8711cef2977c93980f2534b578528f32`。
- [src/main/java/toni/immersivedamageindicators/foundation/IrisCompat.java:1–45](https://github.com/txnimc/ImmersiveDamageIndicators/blob/c2d3a9f748a28835f6aa1af9cbdb2e396da05cc7/src/main/java/toni/immersivedamageindicators/foundation/IrisCompat.java#L1-L45)；SHA256 `a11593378f22ad7a7b962e182d3085faff1e087025665dd20b04b15fc1de19af`。
- [src/main/java/toni/immersivedamageindicators/foundation/CaxtonRenderer.java:1–51](https://github.com/txnimc/ImmersiveDamageIndicators/blob/c2d3a9f748a28835f6aa1af9cbdb2e396da05cc7/src/main/java/toni/immersivedamageindicators/foundation/CaxtonRenderer.java#L1-L51)；SHA256 `ee0bfd98f97eabf302c9bc7d60023d1d7bbddfccc96a41e46c6d7015e906e1ee`。
- [src/main/java/toni/immersivedamageindicators/api/CreateDamageIndicator.java:1–16](https://github.com/txnimc/ImmersiveDamageIndicators/blob/c2d3a9f748a28835f6aa1af9cbdb2e396da05cc7/src/main/java/toni/immersivedamageindicators/api/CreateDamageIndicator.java#L1-L16)；SHA256 `5a7109fb86ffe8d1f6fe252470c1244b25944c65424a0c04d63dc79f0804b785`。
- 辅助（0计数）：[txnimc/ImmersiveMessages/src/main/java/toni/immersivemessages/api/ImmersiveMessage.java](https://github.com/txnimc/ImmersiveMessages/blob/6d152088f58c911e0a7480b978ce75a05b232416/src/main/java/toni/immersivemessages/api/ImmersiveMessage.java#L274-L299)；辅助消息渲染库0信用；固定源码不是依赖Jar兼容保证
- 辅助（0计数）：[txnimc/ImmersiveMessages/src/main/java/toni/immersivemessages/ImmersiveMessagesManager.java](https://github.com/txnimc/ImmersiveMessages/blob/6d152088f58c911e0a7480b978ce75a05b232416/src/main/java/toni/immersivemessages/ImmersiveMessagesManager.java#L18-L104)；辅助消息渲染库0信用；固定源码不是依赖Jar兼容保证
- 辅助（0计数）：[txnimc/ImmersiveMessages/src/main/java/toni/immersivemessages/renderers/VanillaRenderer.java](https://github.com/txnimc/ImmersiveMessages/blob/6d152088f58c911e0a7480b978ce75a05b232416/src/main/java/toni/immersivemessages/renderers/VanillaRenderer.java#L20-L110)；辅助消息渲染库0信用；固定源码不是依赖Jar兼容保证

### 20. mineandslash-native-nullified-receipt-particle

**全文调用链：** MMORPG注册CommonEvents和S2C；CommonEvents→NewDamageMain注册DAMAGE_BEFORE_CALC消费者→OnPlayerDamageEntityEvent.accept（finally解除递归锁）→LivingHurtUtils.tryAttack/onAttack→无武器原生分支EntityData.unarmedAttack→EventBuilder.ofDamage/build→EffectEvent.Activate完整调度与calculateEffects→目标DodgeRating/SpellDodgeEffect.setHitAvoided→DamageEvent.activate取消原伤害并发显式DODGE/RESIST回执。InteractionNotifier只发攻击者ServerPlayer；注册的ExileInteractionResultPacket编解码实体ID和枚举→客户端配置门→当前level实体查找→nullified策略→原生ParticleEngine.add→CUSTOM DamageNullifiedParticle.render/tick→Default/Row→RenderUtils.font.drawInBatch。所有策略、元素数字、包装和语义枚举合并1条。

**实际观察：** 明确拒绝判定即使无HP变化也能发文字；取消/友伤/死亡等其他提前返回没有一概冒充闪避回执。当前DODGE/RESIST选择依据attackType.isAttack，不是直接序列化IS_BLOCKED/IS_DODGED，不能照搬成精确Boss免控理由。文字WHITE非灰色；每帧type.text.getString，locName经外部CLOC.blank（外部翻译契约未验证）。随机目标眼高出生后独立粒子，不持续跟随目标；Default寿命15–19tick/Row20tick，共享ParticleGroup容量1000，非语义节流或每目标去重；Default有SHIELD_BLOCK原版声音，Row分支没有相同播放。RenderUtils明确GL_ALWAYS深度而非受墙遮挡；相机距离向量限制6不是6格外剔除。数据仅entityId，无维度/UUID/代际字段，接收端无显式缺失实体保护；这些为静态风险边界，不报成已复现故障。

**与本任务的关系：** 拒控回执必须在权威语义分支生产，并保留原因边界；现有原版盾声音可作为参考，不要求录音。目标锚定、缺失目标防护、逐目标节流与世界生命周期需要分别审查，不能以全局粒子上限代替“不刷屏”。普通角色闪避参考不赋予普通阴阳体质灰字要求。

**覆盖边界：** 完整读本模组所列方法和调用链，事件/包底层Library of Exile及Minecraft粒子生命周期止于外部平台契约；未编译或启动游戏。旧DamageParticleRenderer.renderParticle无条件return、旧sendDamageParticle调用注释均不计有效显示。武器mechanic和其他所有技能调用未逐项认证，不据此声称覆盖全部来源。

固定来源：

- [src/main/java/com/robertx22/mine_and_slash/mmorpg/MMORPG.java:190–210](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/mmorpg/MMORPG.java#L190-L210)；SHA256 `c7ba27439828a35c9395b639fd3c514855cd20718fe35ad8e2e5509bc9c831bc`。
- [src/main/java/com/robertx22/mine_and_slash/mmorpg/event_registers/CommonEvents.java:48–280](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/mmorpg/event_registers/CommonEvents.java#L48-L280)；SHA256 `6850e2a7b472664de059164a39ca100c4ce7054f776e2d3cf91505c8bf1a9a25`。
- [src/main/java/com/robertx22/mine_and_slash/event_hooks/damage_hooks/reworked/NewDamageMain.java:9–76](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/event_hooks/damage_hooks/reworked/NewDamageMain.java#L9-L76)；SHA256 `935224c3ab8d6fd340740926667f8b6f2bd76e053f52abb933f4dc9d1141e01b`。
- [src/main/java/com/robertx22/mine_and_slash/event_hooks/damage_hooks/OnPlayerDamageEntityEvent.java:15–77](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/event_hooks/damage_hooks/OnPlayerDamageEntityEvent.java#L15-L77)；SHA256 `98674b4240e524734183919afff4b9adfb1a1ea24605e8843047f78a2cac64b6`。
- [src/main/java/com/robertx22/mine_and_slash/event_hooks/damage_hooks/LivingHurtUtils.java:42–104](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/event_hooks/damage_hooks/LivingHurtUtils.java#L42-L104)；SHA256 `dcd096ca6e71902ccf8f7a0256c90d012d14d26152a4d34d6b92f0140d84f801`。
- [src/main/java/com/robertx22/mine_and_slash/capability/entity/EntityData.java:445–486](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/capability/entity/EntityData.java#L445-L486)；SHA256 `4c5eb55e1c415bf0bc69712142e3162d9a24b4e2a59a3172bb3b275215eec6e7`。
- [src/main/java/com/robertx22/mine_and_slash/uncommon/effectdatas/EventBuilder.java:36–41](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/uncommon/effectdatas/EventBuilder.java#L36-L41)；SHA256 `51cdf40e98c694486553ba62c32c9e185cd502a5d62d3a15fd2d7459ef6e63b2`。
- [src/main/java/com/robertx22/mine_and_slash/uncommon/effectdatas/EffectEvent.java:156–251](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/uncommon/effectdatas/EffectEvent.java#L156-L251)；SHA256 `bd5552e4421ffd6e818da63a1bfa7718e9c250a8cc37190871c8db30d14f0ad5`。
- [src/main/java/com/robertx22/mine_and_slash/database/data/stats/types/defense/DodgeRating.java:74–114](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/database/data/stats/types/defense/DodgeRating.java#L74-L114)；SHA256 `caa4a0238b1c8d5d59c97872c02e9fa6489169e1fab60aa491211d5bbe680bf1`。
- [src/main/java/com/robertx22/mine_and_slash/database/data/stats/effects/defense/SpellDodgeEffect.java:1–60](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/database/data/stats/effects/defense/SpellDodgeEffect.java#L1-L60)；SHA256 `f70d7edafd8240237f79e093f5424d08d21c9b7c2d9410c9aeacf42137412cef`。
- [src/main/java/com/robertx22/mine_and_slash/uncommon/effectdatas/rework/EventData.java:88–93](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/uncommon/effectdatas/rework/EventData.java#L88-L93)；SHA256 `bee6cb24e4b34094a6df688b0959f210e08bb80b4bb47981d2b847a71e022de1`。
- [src/main/java/com/robertx22/mine_and_slash/uncommon/effectdatas/DamageEvent.java:584–765](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/uncommon/effectdatas/DamageEvent.java#L584-L765)；SHA256 `e48e4d4be4909a4c38be91325b2b73fe9b3f9924be9c74c8656a520ef9078f4c`。
- [src/main/java/com/robertx22/mine_and_slash/a_libraries/dmg_number_particle/particle/InteractionNotifier.java:1–16](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/a_libraries/dmg_number_particle/particle/InteractionNotifier.java#L1-L16)；SHA256 `fb7c8c8623db8854c5af79058a8036919dea614fe4db81d4219fc7e7a78f0b58`。
- [src/main/java/com/robertx22/mine_and_slash/mmorpg/registers/client/S2CPacketRegister.java:15–37](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/mmorpg/registers/client/S2CPacketRegister.java#L15-L37)；SHA256 `7cb9f420671afc08776eddc56423d6816f759aeffbe4a5098f3ed8993de2dcf5`。
- [src/main/java/com/robertx22/mine_and_slash/vanilla_mc/packets/interaction/ExileInteractionResultPacket.java:1–60](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/vanilla_mc/packets/interaction/ExileInteractionResultPacket.java#L1-L60)；SHA256 `e343907452eaee9ec560b4fd3b4f346ecd46752cc5bdc2e3ed16dc7c28468e6c`。
- [src/main/java/com/robertx22/mine_and_slash/vanilla_mc/packets/interaction/IParticleSpawnMaterial.java:29–63](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/vanilla_mc/packets/interaction/IParticleSpawnMaterial.java#L29-L63)；SHA256 `45c360e1ad10cd3e78bfb482f465d954655b9b2b45bd3eb6ace6cde7994dfa27`。
- [src/main/java/com/robertx22/mine_and_slash/a_libraries/dmg_number_particle/particle/InteractionResultHandler.java:1–121](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/a_libraries/dmg_number_particle/particle/InteractionResultHandler.java#L1-L121)；SHA256 `ad43b3a2b5a3065b670622da9f4d591d790ba5c803f2af0b143b21cb08a0ab61`。
- [src/main/java/com/robertx22/mine_and_slash/a_libraries/dmg_number_particle/particle/ExileInteractionResultParticle.java:1–64](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/a_libraries/dmg_number_particle/particle/ExileInteractionResultParticle.java#L1-L64)；SHA256 `d666e8981febeb63089f1a6d91f9d47215d0fe062c78b7b2a261ed4bf61e1692`。
- [src/main/java/com/robertx22/mine_and_slash/a_libraries/dmg_number_particle/particle/impl/DamageNullifiedParticle.java:1–43](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/a_libraries/dmg_number_particle/particle/impl/DamageNullifiedParticle.java#L1-L43)；SHA256 `c076d3e59c024ebda886b35b49323a6ebe9a28172524da438910b96c46733228`。
- [src/main/java/com/robertx22/mine_and_slash/a_libraries/dmg_number_particle/particle/style/Default.java:1–106](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/a_libraries/dmg_number_particle/particle/style/Default.java#L1-L106)；SHA256 `dde3e37f23cde9ffb63636ac478bbd7d682c5bf07420581183bb77f7f07ff095`。
- [src/main/java/com/robertx22/mine_and_slash/a_libraries/dmg_number_particle/particle/style/Row.java:1–118](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/a_libraries/dmg_number_particle/particle/style/Row.java#L1-L118)；SHA256 `dd6ac5dd619d3a9dafe32f839ca3e04169a0344357394da4d5d36f72942cdca5`。
- [src/main/java/com/robertx22/mine_and_slash/a_libraries/dmg_number_particle/particle/RenderUtils.java:1–36](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/a_libraries/dmg_number_particle/particle/RenderUtils.java#L1-L36)；SHA256 `d9947d0fcdde4982d11313bdca0f3142d6bfe649bf3d6f3bd0f8068c9ca196a1`。
- [src/main/java/com/robertx22/mine_and_slash/uncommon/interfaces/IAutoLocName.java:1–45](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/uncommon/interfaces/IAutoLocName.java#L1-L45)；SHA256 `fbefb1fb7c10c8ab40c8ddde5e426b6745b274a6ab7800691bda4b1e3ea61f10`。
- [src/main/java/com/robertx22/mine_and_slash/uncommon/localization/Words.java:375–411](https://github.com/RobertSkalko/Mine-And-Slash-Rework/blob/13dab4218dbcfc7a4f93b51ca6f1ec5274977507/src/main/java/com/robertx22/mine_and_slash/uncommon/localization/Words.java#L375-L411)；SHA256 `77f56a3a7172973ca268a5427c0b5127fa01f226893fb155274e629116ed4b62`。

### 21. cataclysm-harbinger-rejection-after-emp-transition

**全文调用链：** 完整hurt：同类来源拒绝→idleHeadUpdates/destroyBlocksTick副作用→EMP可先sendAnimationMessage(STUN)→半血powered箭矢拒绝→deactivateProgress普通来源拒绝→共享Boss hurt。完整aiStep追踪激活标志造成40tick进度及递减、STUN15tick声音和客户端烟粒子；getter/synced字段及动画字段辅助已读。

**实际观察：** 半血以health<=max/2定义，不是统一无敌态；EMP动作改变发生在后续箭矢/未激活拒绝前，所以hurt=false不能推出“没有动作/状态变化”。STUN音效由后续animationTick==15决定，客户端烟粒子是STUN态，不是专门免疫文本；本链无浮字和逐目标文本节流。

**与本任务的关系：** 专门研究“权威拒绝与已有副作用的顺序”：未来语义接入不能把任何false都翻译为Boss纹丝不动，也不能重复触发已有受控动作。普通玩家体质独立。

**覆盖边界：** 不把每个伤害来源/半血阈值拆条；此条独立于已计共享伤害桶，新增的是EMP先变动作后拒绝的本体决策。动画网络由lionfishapi契约承担，未研究库内部，不计库，不声称像素/同步已验。

固定来源：

- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Harbinger_Entity.java:190–200](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Harbinger_Entity.java#L190-L200)；SHA256 `67051377048ad66759c42ad74baa44e48d7d20305b68c4cc3f22dd448ded72b5`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Harbinger_Entity.java:214–246](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Harbinger_Entity.java#L214-L246)；SHA256 `67051377048ad66759c42ad74baa44e48d7d20305b68c4cc3f22dd448ded72b5`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Harbinger_Entity.java:275–437](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Harbinger_Entity.java#L275-L437)；SHA256 `67051377048ad66759c42ad74baa44e48d7d20305b68c4cc3f22dd448ded72b5`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Harbinger_Entity.java:810–817](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Harbinger_Entity.java#L810-L817)；SHA256 `67051377048ad66759c42ad74baa44e48d7d20305b68c4cc3f22dd448ded72b5`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Harbinger_Entity.java:836–838](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/The_Harbinger_Entity.java#L836-L838)；SHA256 `67051377048ad66759c42ad74baa44e48d7d20305b68c4cc3f22dd448ded72b5`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/LLibrary_Monster.java:57–81](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/LLibrary_Monster.java#L57-L81)；SHA256 `4c0b3e269a287687dee4fb0fa1cd89d7edf1bfbcb5621385448828676fb2633c`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java:73–137](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java#L73-L137)；SHA256 `0a2729372ae9a857d0eae7e01f50c8dc59d1eb9057a118f0ae94a3c38850c955`。

### 22. cataclysm-ignis-counterstrike-refusal-receipt

**全文调用链：** 完整Ignis.hurt/canBlockDamageSource及自有状态getter/Crackiness.byFraction：被攻击时可能进入COUNTER；已在反击有效窗口则广播STRIKE并播BLAZE_HURT后非bypass拒绝。反射深渊火球增加盾损；Boss阶段/自身火球/方向盾各有拒绝；半血阶段阈值另有减伤；最终super成功且裂度改变才播破甲音。

**实际观察：** COUNTER窗口>16<=46，破盾COUNTER>8<=38；动作与声音在bypass判断前发生，不能把声响当伤害已被拒绝证据。反射火球例外由directEntity类型与owner联合判断。方向盾源位置水平向量dot<0且!BYPASSES_SHIELD；反击分支不同于方向盾。阶段半伤不是免疫；外观裂度改变是成功受伤回执。无独立免疫浮字。

**与本任务的关系：** 专门研究带原生反击回执的拒绝：结果文字不得覆盖或重复已生产的反击/破甲语义；伤害owner、direct entity与绕盾标签要分别记录。与普通前盾模板重合部分不另计，只为整条counter/reflected-source权威链计1。

**覆盖边界：** 父类原版hurtCurrentlyUsedShield/blockUsingShield以及外部动画分发止于平台/库接口；不声称Boss动画资产或画面合格。此链可发生动作，作为设计反例而非照搬COD4“纹丝不动”。

固定来源：

- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/Ignis_Entity.java:287–393](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/Ignis_Entity.java#L287-L393)；SHA256 `ee40a6f5d470c40e60bc6f228bfe350741955fa0551c611c92db5266c7aedc54`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/Ignis_Entity.java:396–408](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/Ignis_Entity.java#L396-L408)；SHA256 `ee40a6f5d470c40e60bc6f228bfe350741955fa0551c611c92db5266c7aedc54`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/Ignis_Entity.java:435–510](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/Ignis_Entity.java#L435-L510)；SHA256 `ee40a6f5d470c40e60bc6f228bfe350741955fa0551c611c92db5266c7aedc54`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/Ignis_Entity.java:2602–2626](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/Ignis_Entity.java#L2602-L2626)；SHA256 `ee40a6f5d470c40e60bc6f228bfe350741955fa0551c611c92db5266c7aedc54`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/etc/Animation_Monsters.java:97–99](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/etc/Animation_Monsters.java#L97-L99)；SHA256 `0d0627a0cace404f105e5419cdf607f1a0a38ad048994a1a85bf7f5f5a57ffca`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/LLibrary_Monster.java:57–81](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/LLibrary_Monster.java#L57-L81)；SHA256 `4c0b3e269a287687dee4fb0fa1cd89d7edf1bfbcb5621385448828676fb2633c`。
- [src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java:73–137](https://github.com/lender544/new1.20.1/blob/819937203e22b4fa72fdeccc6c56ad415d65eeef/src/main/java/com/github/L_Ender/cataclysm/entity/AnimationMonster/BossMonsters/LLibrary_Boss_Monster.java#L73-L137)；SHA256 `0a2729372ae9a857d0eae7e01f50c8dc59d1eb9057a118f0ae94a3c38850c955`。

### 23. simplecombat-server-hit-to-projected-hud-text

**全文调用链：** 构造器注册Forge DamageHandler；LivingDamageEvent服务端且有source.entity→ModPackets按目标chunk追踪玩家发送attackerId/receiverId/damage→包enqueueWork→客户端仅当地玩家是攻击者时生成数字→同目标对象可替换旧记录并累加damage→DamageDealtIndicator出生点/动画→RenderGuiEvent.Post→worldToScreen相机投影→GuiGraphics.drawString。注册/codec/处理/构造/tick/完整投影绘制与config初始化方法均已读；包装和显示模式合并1条。

**实际观察：** 这是原生服务端伤害事件而非HP差推断，但没有独立拒控结果；无source.entity环境伤害直接不发。发送范围为目标chunk追踪列表，接收端再按攻击者ID筛选；不是广播给所有旁观者的文字。对象身份合并只在旧记录仍存活时有效，无事件序号去重/硬cap。出生位置是目标半高快照，投影只剔除w<=0，没有射线遮挡；GUI文字不具有世界深度遮挡。age在每次GUI渲染用partialTick差增加，跨多个tick只见分数环绕，低帧率实际时长不能据配置30tick保证；GUI不渲染时也不在独立tick回收。未见显式world/epoch清空或空player保护。isKill以收到时damage>=client target.health推断，不能当权威击杀结论。

**与本任务的关系：** 同一场景可对比世界绘字和屏幕投影绘字；拒控字不能复用damage事件当唯一来源。目标关联、网络接收范围、时间与可见性应各自有可审查证据，不把配置tick和实际tick回收混为一谈。

**覆盖边界：** 源码静态参考，不启动游戏、不证明低帧率故障或实际穿墙截图；伤害方向图标链只随全文阅读，未单独计数。与已有粒子链不同之处为服务器事件+攻击者筛选+目标对象合并+HUD投影/渲染时钟这一完整实现；不是绘字包装多计。

固定来源：

- [src/main/java/net/sam/simple_combat_indicators/SimpleCombatIndicators.java:1–53](https://github.com/sam-makes-stuff/simple_combat_indicators/blob/3992a22e66bc6c1ba114b9054ba53449e7a33737/src/main/java/net/sam/simple_combat_indicators/SimpleCombatIndicators.java#L1-L53)；SHA256 `9efa214159c708d4bf7bf232e088133188026ee2fceb104ab1722efa0cafdc6c`。
- [src/main/java/net/sam/simple_combat_indicators/networking/ModPackets.java:1–52](https://github.com/sam-makes-stuff/simple_combat_indicators/blob/3992a22e66bc6c1ba114b9054ba53449e7a33737/src/main/java/net/sam/simple_combat_indicators/networking/ModPackets.java#L1-L52)；SHA256 `d035571c304bea46f1f46a6fafe90944f0bfe0fc68a26b390e922c03b4e7eeee`。
- [src/main/java/net/sam/simple_combat_indicators/networking/packets/S2CAttackedPacket.java:1–42](https://github.com/sam-makes-stuff/simple_combat_indicators/blob/3992a22e66bc6c1ba114b9054ba53449e7a33737/src/main/java/net/sam/simple_combat_indicators/networking/packets/S2CAttackedPacket.java#L1-L42)；SHA256 `5e62101d43c0b42c683be7472482da8fefeb5c94e2d276f5b2b7916842b71e69`。
- [src/main/java/net/sam/simple_combat_indicators/networking/ClientPacketHandler.java:1–65](https://github.com/sam-makes-stuff/simple_combat_indicators/blob/3992a22e66bc6c1ba114b9054ba53449e7a33737/src/main/java/net/sam/simple_combat_indicators/networking/ClientPacketHandler.java#L1-L65)；SHA256 `316b3abe26959e87531b440962f0585e950604219378ada5ae3282595ffa99d7`。
- [src/main/java/net/sam/simple_combat_indicators/util/DamageHandler.java:1–19](https://github.com/sam-makes-stuff/simple_combat_indicators/blob/3992a22e66bc6c1ba114b9054ba53449e7a33737/src/main/java/net/sam/simple_combat_indicators/util/DamageHandler.java#L1-L19)；SHA256 `d971db15bd3386da7c5e7d68cecefe7e86e67445919bb13a885e1de33bf1e29f`。
- [src/main/java/net/sam/simple_combat_indicators/util/DamageDealtIndicator.java:1–190](https://github.com/sam-makes-stuff/simple_combat_indicators/blob/3992a22e66bc6c1ba114b9054ba53449e7a33737/src/main/java/net/sam/simple_combat_indicators/util/DamageDealtIndicator.java#L1-L190)；SHA256 `b47a180cf2cb5ff1b879195032daab4ffb9f0ccbfebd86a8b1d81271dc62e7bf`。
- [src/main/java/net/sam/simple_combat_indicators/render/DamageIndicatorRenderer.java:1–97](https://github.com/sam-makes-stuff/simple_combat_indicators/blob/3992a22e66bc6c1ba114b9054ba53449e7a33737/src/main/java/net/sam/simple_combat_indicators/render/DamageIndicatorRenderer.java#L1-L97)；SHA256 `bf18ce02bc119c101739d2f1dd792e9f1387ea2e8e609c7fe57b99264d1e6500`。
- [src/main/java/net/sam/simple_combat_indicators/render/CustomHudRenderer.java:1–176](https://github.com/sam-makes-stuff/simple_combat_indicators/blob/3992a22e66bc6c1ba114b9054ba53449e7a33737/src/main/java/net/sam/simple_combat_indicators/render/CustomHudRenderer.java#L1-L176)；SHA256 `7c7df338e978dcbe121b77455c4734a1dbfd0b28db3c71dc7c74a596891a63d6`。
- [src/main/java/net/sam/simple_combat_indicators/util/ConfigUtils.java:1–37](https://github.com/sam-makes-stuff/simple_combat_indicators/blob/3992a22e66bc6c1ba114b9054ba53449e7a33737/src/main/java/net/sam/simple_combat_indicators/util/ConfigUtils.java#L1-L37)；SHA256 `1a2b75f198ca44f9d286c33e2c9c6bd1d1e4531ced94080dab9d0dd9c4aa61bf`。
- [src/main/java/net/sam/simple_combat_indicators/config/ClientConfig.java:1–113](https://github.com/sam-makes-stuff/simple_combat_indicators/blob/3992a22e66bc6c1ba114b9054ba53449e7a33737/src/main/java/net/sam/simple_combat_indicators/config/ClientConfig.java#L1-L113)；SHA256 `f7b48d2c48210fc3b0cc07af8330ebbd0590ddde469f3e648512de0291cf3a24`。

### 24. botania-gaia-trueplayer-authority-and-phase-timer

**全文调用链：** 完整hurt/actuallyHurt/getDamageAfterArmorAbsorb→source.owner必须Player→PlayerHelper.isTruePlayer完整类/名称过滤→专有INVUL_TIME必须为0→cap32再super。完整spawn主方法设置160tick/health1、aiStep原生逐tick生产/递减无敌计时、save读回与同步getter/setter已读；玩家范围辅助读到实际查询。本条研究Boss攻击者资格与阶段计时权威，不按玩家数、阶段、helper或平台拆分。

**实际观察：** source.getEntity而非directEntity用于准入，玩家投射物可通过owner准入；非玩家/假玩家或计时非零直接false，不表示所有减伤都是免疫。isTruePlayer只是可配置fakePlayerClass及名称正则过滤，不是证明真人输入（自动化玩家仍不能称真人2人）。召唤与低血召怪期计时不同于原版invulnerableTime；accepted actuallyHurt设置原版至少20tick并安排移动/4tick后传送。hurt拒绝分支没有独立免疫浮字、音效或每目标文字节流。aiStep回血直接setHealth不同于heal覆写门控。

**与本任务的关系：** Boss语义需携带真正拒绝原因，不能把非玩家攻击、阶段无敌、32伤害上限和普通体质合成一类。研究玩家身份/来源归属与零血差拒绝的边界；不由此引入新真人验证或普通玩家灰字门槛。

**覆盖边界：** 完整读受伤决定方法、专用计时主要生产方法及所列助手；spawn/checkPylons/checkArena的建筑判定内部、完整战斗攻击/召怪/粒子渲染未逐链认证，不计这些辅助功能。原版super伤害与同步止于平台契约；未运行、未判断Boss画面。

固定来源：

- [Xplat/src/main/java/vazkii/botania/common/entity/GaiaGuardianEntity.java:435–470](https://github.com/VazkiiMods/Botania/blob/0ddec883d6ec4c7be78525267e29cbf1bd98c672/Xplat/src/main/java/vazkii/botania/common/entity/GaiaGuardianEntity.java#L435-L470)；SHA256 `33fdb491440b9478d0b92b7105afcce12ec329702092a21db728647a64e6a9fe`。
- [Xplat/src/main/java/vazkii/botania/common/entity/GaiaGuardianEntity.java:359–375](https://github.com/VazkiiMods/Botania/blob/0ddec883d6ec4c7be78525267e29cbf1bd98c672/Xplat/src/main/java/vazkii/botania/common/entity/GaiaGuardianEntity.java#L359-L375)；SHA256 `33fdb491440b9478d0b92b7105afcce12ec329702092a21db728647a64e6a9fe`。
- [Xplat/src/main/java/vazkii/botania/common/entity/GaiaGuardianEntity.java:392–413](https://github.com/VazkiiMods/Botania/blob/0ddec883d6ec4c7be78525267e29cbf1bd98c672/Xplat/src/main/java/vazkii/botania/common/entity/GaiaGuardianEntity.java#L392-L413)；SHA256 `33fdb491440b9478d0b92b7105afcce12ec329702092a21db728647a64e6a9fe`。
- [Xplat/src/main/java/vazkii/botania/common/entity/GaiaGuardianEntity.java:202–283](https://github.com/VazkiiMods/Botania/blob/0ddec883d6ec4c7be78525267e29cbf1bd98c672/Xplat/src/main/java/vazkii/botania/common/entity/GaiaGuardianEntity.java#L202-L283)；SHA256 `33fdb491440b9478d0b92b7105afcce12ec329702092a21db728647a64e6a9fe`。
- [Xplat/src/main/java/vazkii/botania/common/entity/GaiaGuardianEntity.java:568–588](https://github.com/VazkiiMods/Botania/blob/0ddec883d6ec4c7be78525267e29cbf1bd98c672/Xplat/src/main/java/vazkii/botania/common/entity/GaiaGuardianEntity.java#L568-L588)；SHA256 `33fdb491440b9478d0b92b7105afcce12ec329702092a21db728647a64e6a9fe`。
- [Xplat/src/main/java/vazkii/botania/common/entity/GaiaGuardianEntity.java:745–892](https://github.com/VazkiiMods/Botania/blob/0ddec883d6ec4c7be78525267e29cbf1bd98c672/Xplat/src/main/java/vazkii/botania/common/entity/GaiaGuardianEntity.java#L745-L892)；SHA256 `33fdb491440b9478d0b92b7105afcce12ec329702092a21db728647a64e6a9fe`。
- [Xplat/src/main/java/vazkii/botania/common/helper/PlayerHelper.java:40–58](https://github.com/VazkiiMods/Botania/blob/0ddec883d6ec4c7be78525267e29cbf1bd98c672/Xplat/src/main/java/vazkii/botania/common/helper/PlayerHelper.java#L40-L58)；SHA256 `76d8f3f2c7c7261cb13d604b6bccef8979c59a53bba8ab7fad6e69fb2beb11e7`。
- [Xplat/src/main/java/vazkii/botania/common/helper/VecHelper.java:23–25](https://github.com/VazkiiMods/Botania/blob/0ddec883d6ec4c7be78525267e29cbf1bd98c672/Xplat/src/main/java/vazkii/botania/common/helper/VecHelper.java#L23-L25)；SHA256 `13165848a2b84175738b1601265a35a9a35ee189e944b2b824aa66871ebb0180`。

### 25. ironspells-authoritative-evasion-and-shroud-native-receipts

**全文调用链：** EventBusSubscriber两原生入口LivingIncomingDamage和ProjectileImpact→EVASION优先、else-if ABYSSAL_SHROUD→完整doEffect server/bypass校验→取消事件；已读Evasion法术onCast、effect注册/onEffectAdded、次数扣除同步，Evasion/同事件Shroud策略合并1。回执经MagicManager.spawnParticles→ServerLevel.sendParticles原生网络，音效level.playSound；Evasion计数另经SyncedSpellData codec/doSync→已注册SyncPlayerData/SyncEntityData包→enqueueWork→ClientMagicData记录或当前实体应用（后者接口为外部实现边界）。

**实际观察：** Evasion在服务端排fall/BYPASSES_INVULNERABILITY/BYPASS_EVASION；先扣次数，<0移除效果但当前仍免伤。最多24次找位，传送事件可被取消，但doEffect不检查handleSpellTeleport返回值，最后仍portal云/ENDERMAN_TELEPORT/true；无可用落点也不等于此次拒伤失败。成功位移可能产生两处云与两次音。Shroud使用碰撞找空位/烟云及自有声音，没有同一次数消费；只调整局部sideStep.yRot返回值未赋回，不能凭调用名认定正确按朝向旋转。两个doEffect都有lookAt，违背本项目禁止强制转向的方向，不可照搬。此链没有免疫文字或自有事件序号去重，不能称灰字范例；已读玩家同步map按整数ID存储，本类未见清空，不能据此声称已复现跨维度bug。

**与本任务的关系：** 这是已有原生权威拒伤与粒子/声音回执的独立研究：拒伤、成功位移、文本与次数同步应分开判断；现有原版声音可参考，但不需要新录音。研究普通法术防护不对COD4普通阴阳体质新增灰字。两原生入口是否重复消耗须运行事件证据，静态不下故障结论。

**覆盖边界：** 完整读所列doEffect/调用者/计数codec/接收方法与位移助手；未审所有法术施法框架、mob具体setSyncedSpellData实现或原版粒子渲染内部，不把基础网络和图形算额外研究。无客户端启动、画面或音频通过结论。

固定来源：

- [src/main/java/io/redspace/ironsspellbooks/player/ServerPlayerEvents.java:116–117](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/player/ServerPlayerEvents.java#L116-L117)；SHA256 `f982d66f86f51158774d59a72f1d41a49803cdb714ddf45a1e0fd7a6e4bf7608`。
- [src/main/java/io/redspace/ironsspellbooks/player/ServerPlayerEvents.java:447–490](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/player/ServerPlayerEvents.java#L447-L490)；SHA256 `f982d66f86f51158774d59a72f1d41a49803cdb714ddf45a1e0fd7a6e4bf7608`。
- [src/main/java/io/redspace/ironsspellbooks/player/ServerPlayerEvents.java:546–564](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/player/ServerPlayerEvents.java#L546-L564)；SHA256 `f982d66f86f51158774d59a72f1d41a49803cdb714ddf45a1e0fd7a6e4bf7608`。
- [src/main/java/io/redspace/ironsspellbooks/effect/EvasionEffect.java:1–94](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/effect/EvasionEffect.java#L1-L94)；SHA256 `0053bad6372b1e44ac5121aae323b78c3c3f06c6c6ea4598307292321595a6e7`。
- [src/main/java/io/redspace/ironsspellbooks/effect/AbyssalShroudEffect.java:1–88](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/effect/AbyssalShroudEffect.java#L1-L88)；SHA256 `cae36b3bf046da498ea53fec6bfe17167b248bcf15f2edc4ec8be56a90416a72`。
- [src/main/java/io/redspace/ironsspellbooks/effect/MagicMobEffect.java:1–48](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/effect/MagicMobEffect.java#L1-L48)；SHA256 `30e07caead6afeb9770017ee62f64340df7729a6e512fc333de748f0bd63c374`。
- [src/main/java/io/redspace/ironsspellbooks/registries/MobEffectRegistry.java:23–28](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/registries/MobEffectRegistry.java#L23-L28)；SHA256 `2cc8632a7bb14cf11d2c4443ea3a25386e7d0d5d688940a11d46e80770c5b6f1`。
- [src/main/java/io/redspace/ironsspellbooks/spells/ender/EvasionSpell.java:1–66](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/spells/ender/EvasionSpell.java#L1-L66)；SHA256 `e4405ea374383753d8418505bc7da0a8f025712c2c42f5061d5e10594c13cdd5`。
- [src/main/java/io/redspace/ironsspellbooks/api/util/Utils.java:167–175](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/api/util/Utils.java#L167-L175)；SHA256 `733acc85898273b2721e2246d24acc5585dcb13a4c3246a5c8023fbd69c3d85d`。
- [src/main/java/io/redspace/ironsspellbooks/api/util/Utils.java:290–292](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/api/util/Utils.java#L290-L292)；SHA256 `733acc85898273b2721e2246d24acc5585dcb13a4c3246a5c8023fbd69c3d85d`。
- [src/main/java/io/redspace/ironsspellbooks/api/util/Utils.java:638–656](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/api/util/Utils.java#L638-L656)；SHA256 `733acc85898273b2721e2246d24acc5585dcb13a4c3246a5c8023fbd69c3d85d`。
- [src/main/java/io/redspace/ironsspellbooks/capabilities/magic/MagicManager.java:125–128](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/capabilities/magic/MagicManager.java#L125-L128)；SHA256 `81edce519130919e4b93e2a946dc7726beb52b7aaf866b53ce97155727c5aedd`。
- [src/main/java/io/redspace/ironsspellbooks/capabilities/magic/SyncedSpellData.java:51–78](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/capabilities/magic/SyncedSpellData.java#L51-L78)；SHA256 `0ec6564db910915b746ebbb3a1e59df291d456f7b672bd0c315c6f37614332e8`。
- [src/main/java/io/redspace/ironsspellbooks/capabilities/magic/SyncedSpellData.java:202–228](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/capabilities/magic/SyncedSpellData.java#L202-L228)；SHA256 `0ec6564db910915b746ebbb3a1e59df291d456f7b672bd0c315c6f37614332e8`。
- [src/main/java/io/redspace/ironsspellbooks/network/casting/SyncPlayerDataPacket.java:1–41](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/network/casting/SyncPlayerDataPacket.java#L1-L41)；SHA256 `d74a833ed13578fb804f12feef4117ef13fb28bcb18911c9960cec0a31213410`。
- [src/main/java/io/redspace/ironsspellbooks/network/casting/SyncEntityDataPacket.java:1–46](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/network/casting/SyncEntityDataPacket.java#L1-L46)；SHA256 `401b5f8dcac711dc2e8cb7d8b236e4077385a1fcb94ededbf9462efb1ce33f80`。
- [src/main/java/io/redspace/ironsspellbooks/setup/PayloadHandler.java:51–64](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/setup/PayloadHandler.java#L51-L64)；SHA256 `c8439e0d281f9a8e7a7eab9fa8a8085a852d1795beade0bf7b70836e50a2b8cd`。
- [src/main/java/io/redspace/ironsspellbooks/player/ClientMagicData.java:176–213](https://github.com/iron431/irons-spells-n-spellbooks/blob/9a88991f5ec6e4f076278a9c11dcaf1281980f20/src/main/java/io/redspace/ironsspellbooks/player/ClientMagicData.java#L176-L213)；SHA256 `d0a2bcde48ceb7becd6d540c897784634a09eea581a4a140ce663c215bb98f72`。

### 26. battletext-native-events-caption-reroute-and-worldtime-lifecycle

**全文调用链：** 固定提交四Java全文已读：FML init注册System到FML/Forge总线→LivingHurt/LivingHeal正数事件→本玩家且ClosedCaption已加载则IMC DirectMessage重定向并return；否则synchronized textList生成Text→RenderWorldLastEvent调用System.tick按world.totalWorldTime每个观测时间值只更新一次→到期回收、距离排序、immutable快照→Renderer相机朝向+font五次绘制。伤害/治疗/颜色/字幕路由全合并1条，ClosedCaption库内部0计数。

**实际观察：** 文字从事件amount生成而非客户端血差；LivingHurt所处阶段不能当最终护甲后实损。正数门排除零伤，链没有明确免疫原因。单玩家字幕重定向避免本分支同时显示浮字，其他实体仍世界字。Text保存出生世界坐标无实体持续关联；Renderer在Y额外+2并24格剔除，深度测试关闭，按距离远先画，alpha最低5；40次onUpdate生命周期但只在world render观察worldTime变化时递减一次，跨过多个tick不补步，没有自有维度epoch/换世界清空/总量上限/逐目标节流。整数截断使0<amount<1会显示0；配置sideVariance字段未参与已读move，不能凭配置注释称已有侧移开关效果。wither灰色0x505050仅伤害类型配色，不是Boss灰色“免疫”字。

**与本任务的关系：** 战斗文字可以因自我视角/字幕集成选择单一路由，但路由兼容不能冒充网络权威免控。实际GL状态、低帧率生命周期、总量和小数显示要看执行方法，不能由特性说明推断。

**覆盖边界：** 源码年代为cpw FML API；虽有注册及完整实现，未编译/启动确认本项目兼容或专服加载安全。事件方法未自检side，亦未见自有S2C结果包，不能当作已验多人服务端权威链。ClosedCaption是否消费该IMC止于外部契约，主浮字分支不依赖它。

固定来源：

- [src/main/java/ninja/genuine/battle/BattleText.java:1–100](https://github.com/GenuineSounds/Battle-Text/blob/e7ba15b0e8dc5881a275920891af46687ef213a3/src/main/java/ninja/genuine/battle/BattleText.java#L1-L100)；SHA256 `5df54a204cddf07c8b9172208670e9229d8a53c4cee4fa11285eeac6ab3b6f3a`。
- [src/main/java/ninja/genuine/battle/system/System.java:1–140](https://github.com/GenuineSounds/Battle-Text/blob/e7ba15b0e8dc5881a275920891af46687ef213a3/src/main/java/ninja/genuine/battle/system/System.java#L1-L140)；SHA256 `e17a7c46bb036eae8f09a134e80a0f30303efa897f18d42ccb0631c6105c6e27`。
- [src/main/java/ninja/genuine/battle/text/Text.java:1–183](https://github.com/GenuineSounds/Battle-Text/blob/e7ba15b0e8dc5881a275920891af46687ef213a3/src/main/java/ninja/genuine/battle/text/Text.java#L1-L183)；SHA256 `f378d1b4ad40f2cbafb74cc27a1f75800cf2fa5173f04918c3b8c25fe0df3e33`。
- [src/main/java/ninja/genuine/battle/render/Renderer.java:1–61](https://github.com/GenuineSounds/Battle-Text/blob/e7ba15b0e8dc5881a275920891af46687ef213a3/src/main/java/ninja/genuine/battle/render/Renderer.java#L1-L61)；SHA256 `81cc5eeef7094a54864d81794953add0e64754c027e777c770170297542c97b6`。

## 继续研究入口

`reviewed.json` 为有效台账；`candidate-index.json` 为词法筛选线索，全部0计数，不能将其总量当已研读；`candidates.json` 记录实际读过但未满足完整/相关/独立门槛的候选与排除原因。`semantic-dedup.json` 记录合并依据。`sources.json` 保存固定版本及逐文件SHA；源码全文位于对应tools/sources目录。

后续优先补明确的Boss拒控/拒伤回执、已有世界文字组件的世界切换/实体销毁处理、逐目标或逐事件节流实现。Goety monolith 已读拒绝→原生entity event→shieldTime→渲染，但empowered赋值入口尚未核实，仍0计数；不把它直接报成可运行范例。不会用纯图形/基础网络库或同链包装补足1000。
