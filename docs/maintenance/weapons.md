# 王朝武器目录（weapons）

> 只读扫描：注册行与构造参数取自 `DynastyWeapons.java` / `DynastyGear.java`（下表“代码依据”给出文件:行），
> 材质加成取自 `DynastyTiers`，特攻取自 `DynastyBalance.WEAPON_BONUS`，获取途径由配方 / 掉落 / 授予代码交叉核对。
> **不推荐毕业排名、不评价强弱。**

## 基础伤害 ≠ 实际战斗伤害（务必区分）

* 表里的**面板攻击力**是按 `1（玩家基础）+ 材质攻击加成（DynastyTiers.getAttackDamageBonus）+ 武器构造参数 dmg`
  换算出的**物品属性面板值**，与代码注释里的“总攻击力”一致（例：`mu_mao` 1+0+4=5、`tianzi_sword` 1+140+3059=3200）。
  它是**换算值**，我没有在游戏里逐把核对 tooltip。
* **实际战斗伤害还要叠加别的**：`DynastyBalance.WEAPON_BONUS` 的名器特攻（命中时追加固定伤害，
  因为原版 `ATTACK_DAMAGE` 属性上限是 2048）、`DynastyCombatEvents` 的战斗事件倍率、目标护甲/抗性/附魔等。
  例：`sword_dragon_crystal` 面板 1400，另有特攻 +150，最终伤害并不等于 1550。
* **弓**：`HuntingBowItem` / `DragonBowItem` 在 `DynastyWeapons.java:152` / `:222` 做
  `arrow.setBaseDamage(箭矢基础 × multiplier + bonus)`；表里列的是**原始参数**，不是最终箭伤。
  弓的最终伤害还受拉弓时长、附魔与 `DynastyBowRitual`（法阵）影响，本表不换算。

## 全部武器（52 件）

| # | 中文名 | 注册 ID | 类型 | 基础参数 | 面板攻击力（换算值） | 名器特攻 | 获取途径 | 代码依据 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 青铜剑 | `dynasty:sword_bronze` | 剑（SwordItem） | BRONZE（材质加成 +22）· dmg 11 · speed -2.4 | 34 | — | 合成 `recipes/sword_bronze.json` | `DynastyGear.java:39` |
| 2 | 官银剑 | `dynasty:sword_silver` | 剑（SwordItem） | OFFICIAL_SILVER（材质加成 +40）· dmg 91 · speed -2.2 | 132 | — | 合成 `recipes/sword_silver.json` | `DynastyGear.java:40` |
| 3 | 玉剑 | `dynasty:sword_jade` | 剑（SwordItem） | JADE（材质加成 +70）· dmg 99 · speed -2 | 170 | — | 合成 `recipes/sword_jade.json` | `DynastyGear.java:41` |
| 4 | 龙晶剑 | `dynasty:sword_dragon_crystal` | 剑（SwordItem） | DRAGON_CRYSTAL（材质加成 +140）· dmg 1259 · speed -1.8 | 1400 | +150 | 合成 `recipes/sword_dragon_crystal.json` | `DynastyGear.java:42` |
| 5 | 方天画戟 | `dynasty:halberd_fangtian` | Sword | DRAGON_CRYSTAL（材质加成 +140）· dmg 1759 · speed -2.6 | 1900 | +250 | 合成 `recipes/halberd_fangtian.json` | `DynastyGear.java:46` |
| 6 | 分水三叉戟 | `dynasty:sea_trident` | Sword | DRAGON_CRYSTAL（材质加成 +140）· dmg 1959 · speed -2.2 | 2100 | +300 | 合成 `recipes/sea_trident.json` | `DynastyGear.java:50` |
| 7 | 玉镐 | `dynasty:pickaxe_jade` | 镐（工具，非武器） | JADE（材质加成 +70）· dmg 99 · speed -2.8 | 170 | — | 合成 `recipes/pickaxe_jade.json` | `DynastyGear.java:53` |
| 8 | 龙晶镐 | `dynasty:pickaxe_dragon_crystal` | 镐（工具，非武器） | DRAGON_CRYSTAL（材质加成 +140）· dmg 279 · speed -2.8 | 420 | — | 合成 `recipes/pickaxe_dragon_crystal.json` | `DynastyGear.java:55` |
| 9 | 木矛 | `dynasty:mu_mao` | 剑（SwordItem） | PRIMITIVE（材质加成 +0）· dmg 4 · speed -2 | 5 | — | 合成 `recipes/mu_mao.json` | `DynastyWeapons.java:238` |
| 10 | 石戈 | `dynasty:shi_ge` | 剑（SwordItem） | STONE（材质加成 +1）· dmg 7 · speed -2.2 | 9 | — | 合成 `recipes/shi_ge.json` | `DynastyWeapons.java:242` |
| 11 | 铜刀 | `dynasty:tong_dao` | 剑（SwordItem） | COPPER（材质加成 +3）· dmg 10 · speed -2 | 14 | — | 合成 `recipes/tong_dao.json` | `DynastyWeapons.java:246` |
| 12 | 铁剑 | `dynasty:tie_jian` | 剑（SwordItem） | IRON（材质加成 +5）· dmg 14 · speed -2.4 | 20 | — | 合成 `recipes/tie_jian.json` | `DynastyWeapons.java:250` |
| 13 | 猎弓 | `dynasty:lie_gong` | 弓（BowItem 子类） | 倍率 ×1.5 + 4 | — | — | 合成 `recipes/lie_gong.json` | `DynastyWeapons.java:253` |
| 14 | 唐刀 | `dynasty:tang_dao` | 剑（SwordItem） | BRONZE（材质加成 +22）· dmg 23 · speed -1 | 46 | — | 合成 `recipes/tang_dao.json` | `DynastyWeapons.java:260` |
| 15 | 环首刀 | `dynasty:huan_shou_dao` | 剑（SwordItem） | BRONZE（材质加成 +22）· dmg 39 · speed -2.2 | 62 | — | 合成 `recipes/huan_shou_dao.json` | `DynastyWeapons.java:264` |
| 16 | 长弓 | `dynasty:chang_gong` | 弓（BowItem 子类） | 倍率 ×2.0 + 20 | — | — | 合成 `recipes/chang_gong.json` | `DynastyWeapons.java:267` |
| 17 | 长枪 | `dynasty:chang_qiang` | Polearm | OFFICIAL_SILVER（材质加成 +40）· dmg 41 · speed -2.6 | 82 | — | 合成 `recipes/chang_qiang.json` | `DynastyWeapons.java:271` |
| 18 | 玉笛 | `dynasty:yu_di` | Flute | JADE（材质加成 +70）· dmg 34 · speed -1.8 | 105 | — | 合成 `recipes/yu_di.json` | `DynastyWeapons.java:275` |
| 19 | 巨阙重剑 | `dynasty:juque_sword` | 剑（SwordItem） | JADE（材质加成 +70）· dmg 429 · speed -3 | 500 | — | 合成 `recipes/juque_sword.json` | `DynastyWeapons.java:280` |
| 20 | 破军战斧 | `dynasty:pojun_axe` | Axe | DRAGON_CRYSTAL（材质加成 +140）· dmg 509 · speed -2.9 | 650 | +120 | 合成 `recipes/pojun_axe.json` | `DynastyWeapons.java:285` |
| 21 | 龙吟弓 | `dynasty:dragon_bow` | 弓（BowItem 子类，可带击退/穿透） | 倍率 ×3.5 + 150，击退 2、穿透 3 | — | — | 合成 `recipes/dragon_bow.json` | `DynastyWeapons.java:289` |
| 22 | 玄天钺 | `dynasty:xuantian_axe` | Axe | DRAGON_CRYSTAL（材质加成 +140）· dmg 2359 · speed -3 | 2500 | +300 | 合成 `recipes/xuantian_axe.json` | `DynastyWeapons.java:295` |
| 23 | 天子剑 | `dynasty:tianzi_sword` | 剑（SwordItem） | DRAGON_CRYSTAL（材质加成 +140）· dmg 3059 · speed -2.2 | 3200 | +500 | 合成 `recipes/tianzi_sword.json` | `DynastyWeapons.java:300` |
| 24 | 斩马刀 | `dynasty:zhanma_dao` | 剑（SwordItem） | OFFICIAL_SILVER（材质加成 +40）· dmg 189 · speed -2.4 | 230 | — | 合成 `recipes/zhanma_dao.json` | `DynastyWeapons.java:306` |
| 25 | 鱼肠剑 | `dynasty:yuchang_dagger` | 剑（SwordItem） | BRONZE（材质加成 +22）· dmg 177 · speed -1.2 | 200 | — | 击杀 `dynasty:assassin` 掉落（DynastyBossDrops） | `DynastyWeapons.java:310` |
| 26 | 青釭剑 | `dynasty:qinggang_sword` | 剑（SwordItem） | JADE（材质加成 +70）· dmg 529 · speed -2 | 600 | +70 | 击杀 `dynasty:eunuch_mastermind` 掉落（DynastyBossDrops） | `DynastyWeapons.java:314` |
| 27 | 御赐金锏 | `dynasty:gilded_mace` | 剑（SwordItem） | JADE（材质加成 +70）· dmg 729 · speed -2.6 | 800 | +100 | 条件授予（DynastyWeaponGifts，每人一次） | `DynastyWeapons.java:318` |
| 28 | 倚天剑 | `dynasty:yitian_sword` | 剑（SwordItem） | JADE（材质加成 +70）· dmg 729 · speed -2 | 800 | +90 | 击杀 `dynasty:rebel_general` 掉落（DynastyBossDrops） | `DynastyWeapons.java:322` |
| 29 | 龙胆亮银枪 | `dynasty:dragon_spear` | Polearm | DRAGON_CRYSTAL（材质加成 +140）· dmg 959 · speed -2.4 | 1100 | +120 | 击杀 `dynasty:undead_first_emperor` 掉落（DynastyBossDrops） | `DynastyWeapons.java:325` |
| 30 | 射日弓 | `dynasty:sunbow` | 弓（BowItem 子类） | 倍率 ×4.5 + 280 | — | +200 | 条件授予（DynastyWeaponGifts，每人一次） | `DynastyWeapons.java:329` |
| 31 | 七星宝刀 | `dynasty:seven_star_saber` | 剑（SwordItem） | DRAGON_CRYSTAL（材质加成 +140）· dmg 1459 · speed -2.2 | 1600 | +220 | 条件授予（DynastyWeaponGifts，每人一次） | `DynastyWeapons.java:334` |
| 32 | 屠龙刀 | `dynasty:dragon_slayer` | 剑（SwordItem） | DRAGON_CRYSTAL（材质加成 +140）· dmg 2159 · speed -2.4 | 2300 | +350 | 合成 `recipes/dragon_slayer.json` | `DynastyWeapons.java:338` |
| 33 | 尚方宝剑 | `dynasty:supreme_sword` | 剑（SwordItem） | DRAGON_CRYSTAL（材质加成 +140）· dmg 2659 · speed -2 | 2800 | +400 | 条件授予（DynastyWeaponGifts，每人一次） | `DynastyWeapons.java:342` |
| 34 | 神臂弓 | `dynasty:shenbi_bow` | 弓（BowItem 子类） | 倍率 ×2.8 + 70 | — | — | 合成 `recipes/shenbi_bow.json` | `DynastyWeapons.java:349` |
| 35 | 落雁弓 | `dynasty:luoyan_bow` | 弓（BowItem 子类） | 倍率 ×3.3 + 120 | — | — | 合成 `recipes/luoyan_bow.json` | `DynastyWeapons.java:353` |
| 36 | 天狼弓 | `dynasty:tianlang_bow` | 弓（BowItem 子类，可带击退/穿透） | 倍率 ×3.8 + 200，击退 1、穿透 1 | — | +150 | 合成 `recipes/tianlang_bow.json` | `DynastyWeapons.java:357` |
| 37 | 龙渊剑 | `dynasty:longyuan_sword` | LongyuanSword | DRAGON_CRYSTAL（材质加成 +140）· dmg 1659 · speed -2 | 1800 | +200 | 合成 `recipes/longyuan_sword.json` | `DynastyWeapons.java:361` |
| 38 | 巨灵斧 | `dynasty:juling_axe` | Axe | DRAGON_CRYSTAL（材质加成 +140）· dmg 2059 · speed -3 | 2200 | +300 | 合成 `recipes/juling_axe.json` | `DynastyWeapons.java:364` |
| 39 | 青龙偃月刀 | `dynasty:qinglong_dao` | 剑（SwordItem） | DRAGON_CRYSTAL（材质加成 +140）· dmg 2459 · speed -2.4 | 2600 | +350 | 合成 `recipes/qinglong_dao.json` | `DynastyWeapons.java:368` |
| 40 | 霸王枪 | `dynasty:bawang_spear` | Polearm | DRAGON_CRYSTAL（材质加成 +140）· dmg 2859 · speed -2.4 | 3000 | +400 | 合成 `recipes/bawang_spear.json` | `DynastyWeapons.java:370` |
| 41 | 后羿弓 | `dynasty:houyi_bow` | 弓（BowItem 子类，毕业弓） | 倍率 ×4.0 + 300 | — | +250 | 合成 `recipes/houyi_bow.json` | `DynastyWeapons.java:373` |
| 42 | 雷霆锤 | `dynasty:leiting_hammer` | Axe | DRAGON_CRYSTAL（材质加成 +140）· dmg 3159 · speed -3.1 | 3300 | +450 | 合成 `recipes/leiting_hammer.json` | `DynastyWeapons.java:376` |
| 43 | 太乙拂尘 | `dynasty:taiyi_whisk` | Polearm | DRAGON_CRYSTAL（材质加成 +140）· dmg 3459 · speed -2.2 | 3600 | +500 | 合成 `recipes/taiyi_whisk.json` | `DynastyWeapons.java:379` |
| 44 | 玄武盾刀 | `dynasty:xuanwu_blade` | 剑（SwordItem） | DRAGON_CRYSTAL（材质加成 +140）· dmg 3859 · speed -2.6 | 4000 | +550 | 合成 `recipes/xuanwu_blade.json` | `DynastyWeapons.java:383` |
| 45 | 朱雀羽扇 | `dynasty:zhuque_fan` | 剑（SwordItem） | DRAGON_CRYSTAL（材质加成 +140）· dmg 4259 · speed -2 | 4400 | +600 | 合成 `recipes/zhuque_fan.json` | `DynastyWeapons.java:386` |
| 46 | 混元珠杖 | `dynasty:hunyuan_staff` | Polearm | DRAGON_CRYSTAL（材质加成 +140）· dmg 4859 · speed -2.4 | 5000 | +800 | 合成 `recipes/hunyuan_staff.json` | `DynastyWeapons.java:388` |
| 47 | 麒麟战斧 | `dynasty:qilin_war_axe` | Axe | DRAGON_CRYSTAL（材质加成 +140）· dmg 1859 · speed -2.9 | 2000 | +250 | 合成 `recipes/qilin_war_axe.json` | `DynastyWeapons.java:394` |
| 48 | 太乙法剑 | `dynasty:taiyi_sword` | 剑（SwordItem） | DRAGON_CRYSTAL（材质加成 +140）· dmg 2159 · speed -2.2 | 2300 | +300 | 合成 `recipes/taiyi_sword.json` | `DynastyWeapons.java:398` |
| 49 | 白虎戟 | `dynasty:baihu_glaive` | Polearm | DRAGON_CRYSTAL（材质加成 +140）· dmg 2459 · speed -2.8 | 2600 | +330 | 合成 `recipes/baihu_glaive.json` | `DynastyWeapons.java:400` |
| 50 | 雷霆枪 | `dynasty:thunder_spear` | Polearm | DRAGON_CRYSTAL（材质加成 +140）· dmg 2759 · speed -2.6 | 2900 | +360 | 合成 `recipes/thunder_spear.json` | `DynastyWeapons.java:403` |
| 51 | 紫微刀 | `dynasty:ziwei_saber` | 剑（SwordItem） | DRAGON_CRYSTAL（材质加成 +140）· dmg 3059 · speed -2.4 | 3200 | +400 | 合成 `recipes/ziwei_saber.json` | `DynastyWeapons.java:407` |
| 52 | 朱雀弓 | `dynasty:zhuque_bow` | 弓（BowItem 子类，可带击退/穿透） | 倍率 ×4.0 + 300，击退 2、穿透 4 | — | +300 | 合成 `recipes/zhuque_bow.json` | `DynastyWeapons.java:409` |

## 待确认

* 获取途径未核实：无
* 面板攻击力是**按公式换算**的（未在游戏内逐把查看 tooltip）；若与实机显示不一致，以实机为准。
* 弓的 `multiplier/bonus` 只是箭伤公式的两个参数；最终箭伤未展开（见上文说明）。
* 长柄（PolearmItem）额外给 `+3 触及 / +2 方块触及`（`DynastyWeapons.java:66-77`），不体现在攻击力里。
* 玉笛（FluteItem）右键是范围虚弱+缓慢（`DynastyWeapons.java:89-116`），与攻击力无关。
* 镐是工具（`PickaxeItem`），只为完整性列出，不作为武器评价。
