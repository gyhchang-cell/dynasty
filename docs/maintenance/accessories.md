# 王朝饰品目录（accessories）

> 只读扫描生成：槽位来自 `tools/art/gen_curios.py` 的 `classifications()`（同时是游戏里
> `data/curios/tags/items/<槽>.json` 的写入来源）；效果来自 `DynastyTrinkets.EXTRA_TABLE`
> 与 `DynastyTrinketTips`（表驱动 130 件 + 手写 39 件）。**未评价强弱、未改任何槽位分配。**

## 槽位说明

* **分类槽**（每件饰品只有一个，见“槽位”列）：头部 / 项链 / 戒指（2 格）/ 手镯 / 手部 / 身体 / 背部 / 腰带 / 护符。
* **万能槽**（`curio`，初始 1 格，五个任务里程碑各 +1，最多 6 格）：校验器 `dynasty:accessory`
  （`DynastyCuriosBridge.java:34-36`）= `#dynasty:accessories` 里的 169 件 → **下表每件都能进万能槽**。
* 依据文件：`data/curios/tags/items/<槽>.json`、`data/dynasty/curios/slots/<槽>.json`、
  `data/dynasty/tags/items/accessories.json`、`data/dynasty/curios/entities/player.json`。

## 全部饰品（169 件）

| # | 中文名 | 注册 ID | 槽位 | 效果简述（依据代码表） | 效果依据文件 |
| --- | --- | --- | --- | --- | --- |
| 1 | 深渊珠 | `dynasty:abyss_pearl` | 项链（+万能槽） | [夜晚] 攻击 +35% · 击退 +0.4；命中：会心 +50% 额外伤害，概率 30% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 2 | 丹炉坠 | `dynasty:alchemy_furnace_charm` | 护符（+万能槽） | [常驻] 生命 +260；效果：再生 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 3 | 炼丹坠 | `dynasty:alchemy_pendant` | 项链（+万能槽） | [常驻] 生命 +200；效果：再生 II | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 4 | 破甲符牌 | `dynasty:armor_piercer_token` | 护符（+万能槽） | [常驻] 攻击 +16% · 击退 +0.3 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 5 | 箭囊 | `dynasty:arrow_quiver` | 背部（+万能槽） | [常驻] 攻击 +8% · 移速 +4% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 6 | 瑞兽铃 | `dynasty:auspicious_bell` | 护符（+万能槽） | 攻速 +10%；每 20 秒 驱散虚弱与缓慢 | `DynastyTrinketTips.java` LEGACY 表 |
| 7 | 八卦镜 | `dynasty:bagua_mirror` | 护符（+万能槽） | [常驻] 护甲 +14；效果：抗性 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 8 | 竹笛 | `dynasty:bamboo_flute` | 护符（+万能槽） | 每 5 秒 让 8 格内敌人缓慢 | `DynastyTrinketTips.java` LEGACY 表 |
| 9 | 熊掌 | `dynasty:bear_paw` | 手部（+万能槽） | [常驻] 生命 +300 · 攻击 +8% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 10 | 腰带扣 | `dynasty:belt_buckle` | 腰带（+万能槽） | [常驻] 护甲 +6 · 生命 +120 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 11 | 血铁腰带 | `dynasty:blood_iron_sash` | 腰带（+万能槽） | [常驻] 生命上限 -15% · 护甲 +18 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 12 | 血誓印 | `dynasty:blood_oath_seal` | 护符（+万能槽） | [常驻] 生命上限 -30% · 攻击 +35%；命中：吸血 +15%（按造成的伤害回血） | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 13 | 寒骨佩 | `dynasty:bone_chill_pendant` | 项链（+万能槽） | [水下] 攻击 +25%；效果：内伤 II；命中：雷罚 附加 +45 点伤害，概率 35% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 14 | 白骨算筹 | `dynasty:bone_reaper_tally` | 护符（+万能槽） | [常驻] 生命上限 -20% · 攻击 +25%；[常驻] 击退 +0.5；命中：斩杀 +20% 血线以下的目标（Boss / 神兽免斩） | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 15 | 弓弦护腕 | `dynasty:bow_string` | 手镯（+万能槽） | [常驻] 攻速 +12% · 攻击 +5% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 16 | 铜镜 | `dynasty:bronze_mirror` | 护符（+万能槽） | 每 30 秒 自动净化一个负面效果 | `DynastyTrinketTips.java` LEGACY 表 |
| 17 | 笔架坠 | `dynasty:brush_rack` | 护符（+万能槽） | [常驻] 攻速 +14% · 攻击 +6% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 18 | 亡者烛 | `dynasty:candle_of_the_dead` | 护符（+万能槽） | [夜晚] 攻击 +30%；[白天] 生命 -150 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 19 | 铁骑带 | `dynasty:cavalry_sash` | 腰带（+万能槽） | [骑乘] 攻击 +15% · 移速 +10% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 20 | 朱砂囊 | `dynasty:cinnabar_pouch` | 腰带（+万能槽） | 每 2 秒 驱散中毒 / 凋零 / 失明 / 饥饿 | `DynastyTrinketTips.java` LEGACY 表 |
| 21 | 云锦囊 | `dynasty:cloud_brocade` | 身体（+万能槽） | 生命 +160 · 护甲 +8 | `DynastyTrinketTips.java` LEGACY 表 |
| 22 | 云纹佩 | `dynasty:cloud_pattern` | 护符（+万能槽） | [常驻] 移速 +12% · 抗击退 +0.3 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 23 | 海螺号 | `dynasty:conch_horn` | 护符（+万能槽） | [常驻] 生命 +240 · 移速 +8% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 24 | 鹤羽 | `dynasty:crane_feather` | 背部（+万能槽） | [常驻] 移速 +10%；效果：缓降 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 25 | 血契坠 | `dynasty:crimson_pact_charm` | 项链（+万能槽） | [常驻] 生命上限 -40% · 攻击 +50%；命中：吸血 +20%（按造成的伤害回血），概率 60% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 26 | 破晓刃坠 | `dynasty:dawn_blade_charm` | 护符（+万能槽） | [白天] 攻击 +22%；[夜晚] 移速 +10%；命中：突袭 +35% 额外伤害（只在目标满血时生效） | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 27 | 晨钟坠 | `dynasty:dawn_drum` | 手部（+万能槽） | [白天] 攻速 +12% · 移速 +8% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 28 | 榻前符 | `dynasty:deathbed_talisman` | 护符（+万能槽） | [残血] 攻击 +30% · 移速 +30%；命中：斩杀 +25% 血线以下的目标（Boss / 神兽免斩），概率 60% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 29 | 鹿角 | `dynasty:deer_antler` | 头部（+万能槽） | [常驻] 生命 +260；效果：再生 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 30 | 地煞符 | `dynasty:disha_talisman` | 护符（+万能槽） | [常驻] 护甲 +18 · 击退 +0.4 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 31 | 潜蛟印 | `dynasty:diver_signet` | 护符（+万能槽） | [水下] 护甲 +20 · 攻击 +25% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 32 | 龙血珠 | `dynasty:dragon_blood_pearl` | 护符（+万能槽） | [常驻] 生命 +360 · 攻击 +14% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 33 | 龙骨戒 | `dynasty:dragon_bone_ring` | 戒指（+万能槽） | 护甲 +10 · 抗击退 +0.3 · 攻击 +8% | `DynastyTrinketTips.java` LEGACY 表 |
| 34 | 龙王逆鳞 | `dynasty:dragon_king_scale` | 身体（+万能槽） | 攻击 +20% · 抗击退 +0.5 · 护甲 +6 | `DynastyTrinketTips.java` LEGACY 表 |
| 35 | 龙珠 | `dynasty:dragon_pearl` | 护符（+万能槽） | 攻击 +25% · 抗击退 +0.3 | `DynastyTrinketTips.java` LEGACY 表 |
| 36 | 龙袍玉带 | `dynasty:dragon_robe_sash` | 腰带（+万能槽） | [常驻] 护甲 +14 · 生命 +200 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 37 | 龙鳞护符 | `dynasty:dragon_scale_charm` | 项链（+万能槽） | 护甲 +12 · 抗击退 +0.4 | `DynastyTrinketTips.java` LEGACY 表 |
| 38 | 龙鳞带 | `dynasty:dragon_scale_sash` | 腰带（+万能槽） | [常驻] 护甲 +16 · 抗击退 +0.5 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 39 | 龙须穗 | `dynasty:dragon_whisker` | 腰带（+万能槽） | 攻速 +15% · 击退 +0.5 | `DynastyTrinketTips.java` LEGACY 表 |
| 40 | 鼓槌 | `dynasty:drum_beater` | 手部（+万能槽） | [常驻] 攻速 +15% · 攻击 +5% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 41 | 夜袭徽 | `dynasty:dusk_raider_badge` | 护符（+万能槽） | [夜晚] 攻击 +20% · 移速 +12% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 42 | 暮色帷幕 | `dynasty:dusk_veil_charm` | 护符（+万能槽） | [夜晚] 攻击 +26%；[白天] 生命上限 -20%；命中：会心 +45% 额外伤害，概率 25% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 43 | 蚀月珠 | `dynasty:eclipse_bead` | 项链（+万能槽） | [夜晚] 攻击 +30%；[白天] 护甲 -6；命中：会心 +55% 额外伤害，概率 20% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 44 | 龙威敕令 | `dynasty:edict_of_dragon` | 护符（+万能槽） | [常驻] 攻击 +10%；效果：龙威 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 45 | 威慑敕令 | `dynasty:edict_of_dread` | 护符（+万能槽） | [常驻] 攻击 +10%；效果：威慑 I；命中：斩杀 +10% 血线以下的目标（Boss / 神兽免斩） | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 46 | 铁壁敕令 | `dynasty:edict_of_iron` | 护符（+万能槽） | [常驻] 护甲 +8；效果：铁壁 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 47 | 忠诚敕令 | `dynasty:edict_of_loyalty` | 护符（+万能槽） | [常驻] 生命 +180；效果：忠诚 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 48 | 天命敕令 | `dynasty:edict_of_mandate` | 护符（+万能槽） | [常驻] 幸运 +2；效果：天命 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 49 | 疾风敕令 | `dynasty:edict_of_swift` | 护符（+万能槽） | [常驻] 移速 +6%；效果：疾风 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 50 | 血肉骰 | `dynasty:flesh_gamble_dice` | 护符（+万能槽） | [常驻] 攻击 +20%；[残血] 攻击 +40% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 51 | 折扇 | `dynasty:folding_fan` | 手部（+万能槽） | [常驻] 移速 +6% · 攻速 +8% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 52 | 狐灵佩 | `dynasty:fox_spirit_pendant` | 项链（+万能槽） | [常驻] 移速 +12% · 幸运 +2 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 53 | 狐尾坠 | `dynasty:fox_tail_charm` | 腰带（+万能槽） | 跳跃提升 II · 移速 +5% | `DynastyTrinketTips.java` LEGACY 表 |
| 54 | 渡鬼符 | `dynasty:ghost_ferry_tally` | 护符（+万能槽） | [常驻] 攻速 +30%；[常驻] 生命上限 -25%；效果：内伤 I；命中：斩杀 +15% 血线以下的目标（Boss / 神兽免斩），概率 60% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 55 | 金莲冠 | `dynasty:gilded_lotus_crown` | 头部（+万能槽） | [常驻] 攻击 +10% · 移速 +5% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 56 | 棋盘坠 | `dynasty:go_board` | 护符（+万能槽） | [常驻] 攻速 +10% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 57 | 金印 | `dynasty:gold_seal_charm` | 护符（+万能槽） | 功名 +25%；每 30 秒 +2 忠诚度 | `DynastyTrinketTips.java` LEGACY 表 |
| 58 | 金丹 | `dynasty:golden_pill` | 护符（+万能槽） | [常驻] 生命 +400；效果：再生 III | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 59 | 古琴弦 | `dynasty:guqin_string` | 手镯（+万能槽） | [常驻] 攻速 +8% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 60 | 琴穗 | `dynasty:guqin_tassel` | 护符（+万能槽） | [常驻] 攻速 +8% · 生命 +120 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 61 | 鹰眼 | `dynasty:hawk_eye` | 头部（+万能槽） | [常驻] 攻击 +10% · 攻击距离 +2 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 62 | 护心镜 | `dynasty:heart_mirror` | 身体（+万能槽） | 护甲 +8 · 额外减伤 4% | `DynastyTrinketTips.java` LEGACY 表 |
| 63 | 马镫 | `dynasty:horse_stirrup` | 腰带（+万能槽） | [骑乘] 移速 +10% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 64 | 仙鹤羽 | `dynasty:immortal_crane_feather` | 背部（+万能槽） | [常驻] 移速 +12%；效果：缓降 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 65 | 东珠耳坠 | `dynasty:imperial_pearl_earring` | 项链（+万能槽） | [常驻] 生命 +200 · 幸运 +1 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 66 | 御玺佩 | `dynasty:imperial_seal_charm` | 护符（+万能槽） | 功名 +40%；生命 +100 · 护甲 +4 | `DynastyTrinketTips.java` LEGACY 表 |
| 67 | 香囊 | `dynasty:incense_sachet` | 腰带（+万能槽） | [常驻] 生命 +160；效果：再生 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 68 | 砚台坠 | `dynasty:ink_slab_charm` | 护符（+万能槽） | [常驻] 幸运 +2 · 生命 +160 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 69 | 砚台 | `dynasty:inkstone` | 护符（+万能槽） | 攻速 +12% · 攻击 +6% | `DynastyTrinketTips.java` LEGACY 表 |
| 70 | 内伤符 | `dynasty:internal_injury_talisman` | 护符（+万能槽） | [常驻] 攻击 +45%；效果：内伤 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 71 | 盔缨 | `dynasty:iron_helmet_plume` | 头部（+万能槽） | [常驻] 护甲 +12 · 移速 +6% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 72 | 铁护肩 | `dynasty:iron_pauldron` | 身体（+万能槽） | [常驻] 护甲 +14 · 攻击 +5% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 73 | 军粮坠 | `dynasty:iron_ration_charm` | 护符（+万能槽） | [常驻] 生命 +350 · 攻速 -8% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 74 | 玄铁腰牌 | `dynasty:iron_waist_token` | 腰带（+万能槽） | 生命 +150 · 护甲 +6 · 抗击退 +0.2 | `DynastyTrinketTips.java` LEGACY 表 |
| 75 | 象牙 | `dynasty:ivory_tusk` | 护符（+万能槽） | [常驻] 攻击距离 +2 · 攻击 +6% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 76 | 玉带钩 | `dynasty:jade_belt_hook` | 腰带（+万能槽） | [常驻] 护甲 +8 · 抗击退 +0.3 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 77 | 玉璧 | `dynasty:jade_bi_disc` | 项链（+万能槽） | 生命 +150 | `DynastyTrinketTips.java` LEGACY 表 |
| 78 | 玉辟邪 | `dynasty:jade_bixie` | 护符（+万能槽） | [常驻] 击退 +0.4 · 攻击 +8% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 79 | 玉笔筒 | `dynasty:jade_brush_holder` | 护符（+万能槽） | [常驻] 攻速 +12% · 攻击 +6% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 80 | 玉蝉 | `dynasty:jade_cicada` | 护符（+万能槽） | 残血（<30%）时 抗性 II + 迅捷 | `DynastyTrinketTips.java` LEGACY 表 |
| 81 | 玉琮 | `dynasty:jade_cong` | 护符（+万能槽） | [常驻] 护甲 +12 · 抗击退 +0.4 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 82 | 玉冠 | `dynasty:jade_crown` | 头部（+万能槽） | 生命 +220 | `DynastyTrinketTips.java` LEGACY 表 |
| 83 | 玉飞天 | `dynasty:jade_flying_apsara` | 护符（+万能槽） | [常驻] 移速 +8%；效果：缓降 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 84 | 玉麒麟 | `dynasty:jade_kylin` | 护符（+万能槽） | [常驻] 生命 +220 · 攻击 +10% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 85 | 玉髓佩 | `dynasty:jade_marrow_charm` | 项链（+万能槽） | [常驻] 生命 +180 · 护甲 +5 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 86 | 玉佩 | `dynasty:jade_pendant` | 项链（+万能槽） | 减伤 8% | `DynastyTrinketTips.java` LEGACY 表 |
| 87 | 玉扳指 | `dynasty:jade_ring` | 戒指（+万能槽） | [常驻] 攻速 +10% · 攻击距离 +1 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 88 | 玉如意 | `dynasty:jade_ruyi` | 手部（+万能槽） | [常驻] 幸运 +2；效果：幸运 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 89 | 玉殓佩 | `dynasty:jade_shroud_charm` | 护符（+万能槽） | [常驻] 生命 +400 · 移速 -10%；效果：内伤 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 90 | 玉蚕 | `dynasty:jade_silkworm` | 护符（+万能槽） | [残血] 生命 +120；效果：再生 II | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 91 | 玉龟符 | `dynasty:jade_tortoise` | 护符（+万能槽） | 水下呼吸 · 海豚的恩惠 · 抗性 | `DynastyTrinketTips.java` LEGACY 表 |
| 92 | 玉璋 | `dynasty:jade_zhang` | 护符（+万能槽） | [常驻] 攻击 +12% · 攻速 +8% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 93 | 因果牒 | `dynasty:karma_ledger_charm` | 护符（+万能槽） | [常驻] 攻击 +30%；[残血] 护甲 +30 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 94 | 护膝 | `dynasty:knee_guard` | 身体（+万能槽） | [常驻] 移速 +5% · 抗击退 +0.2 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 95 | 豹尾 | `dynasty:leopard_tail` | 腰带（+万能槽） | [常驻] 移速 +12% · 攻速 +6% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 96 | 汲生戒 | `dynasty:lifedrain_ring` | 戒指（+万能槽） | [常驻] 攻击 +30% · 攻速 +10%；效果：内伤 II；命中：吸血 +12%（按造成的伤害回血） | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 97 | 补子官徽 | `dynasty:mandarin_rank_badge` | 身体（+万能槽） | [常驻] 幸运 +2 · 生命 +180 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 98 | 功牌 | `dynasty:merit_badge` | 身体（+万能槽） | 生命 +200 · 抗击退 +0.3 | `DynastyTrinketTips.java` LEGACY 表 |
| 99 | 铜镜袋 | `dynasty:mirror_pouch` | 腰带（+万能槽） | [常驻] 护甲 +10；效果：抗性 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 100 | 明月佩 | `dynasty:moon_pendant` | 项链（+万能槽） | 夜晚 夜视 · 攻击 +10% · 攻速 +10% | `DynastyTrinketTips.java` LEGACY 表 |
| 101 | 月华镜 | `dynasty:moonlit_mirror` | 身体（+万能槽） | [夜晚] 攻速 +14%；[白天] 幸运 +2 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 102 | 幽冥缚戒 | `dynasty:nether_binding_ring` | 戒指（+万能槽） | [夜晚] 攻击 +40%；[白天] 生命上限 -20%；命中：雷罚 附加 +60 点伤害，概率 30% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 103 | 夜鹭羽 | `dynasty:night_heron_feather` | 背部（+万能槽） | [夜晚] 攻击 +18% · 击退 +0.3；命中：突袭 +30% 额外伤害（只在目标满血时生效） | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 104 | 正阳佩 | `dynasty:noon_pendant` | 项链（+万能槽） | [白天] 生命 +240；[夜晚] 生命 -160 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 105 | 桃木剑 | `dynasty:peach_sword` | 护符（+万能槽） | [常驻] 攻击 +16% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 106 | 珠网坠 | `dynasty:pearl_net_charm` | 护符（+万能槽） | [常驻] 生命 +200 · 幸运 +2 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 107 | 凤羽翎 | `dynasty:phoenix_feather_charm` | 头部（+万能槽） | 移速 +10% · 常驻缓降 | `DynastyTrinketTips.java` LEGACY 表 |
| 108 | 凤钗 | `dynasty:phoenix_hairpin` | 头部（+万能槽） | [常驻] 生命 +240 · 幸运 +1 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 109 | 凤凰指环 | `dynasty:phoenix_ring` | 戒指（+万能槽） | 常驻抗火 · 移速 +3%；着火时 立刻灭火并加速 | `DynastyTrinketTips.java` LEGACY 表 |
| 110 | 凤翼坠 | `dynasty:phoenix_wing_charm` | 背部（+万能槽） | [常驻] 移速 +10%；效果：缓降 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 111 | 枪缨 | `dynasty:pike_tassel` | 腰带（+万能槽） | [常驻] 攻击 +10% · 攻击距离 +1 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 112 | 诗文卷轴 | `dynasty:poem_scroll` | 护符（+万能槽） | [常驻] 幸运 +2；效果：幸运 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 113 | 紫气珠 | `dynasty:purple_qi_pearl` | 护符（+万能槽） | [常驻] 生命 +320 · 攻击 +14% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 114 | 麒麟蹄 | `dynasty:qilin_hoof_charm` | 护符（+万能槽） | [常驻] 生命 +260 · 攻速 +8% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 115 | 麒麟角坠 | `dynasty:qilin_horn_charm` | 项链（+万能槽） | 攻击 +10% · 护甲 +4 · 常驻再生 | `DynastyTrinketTips.java` LEGACY 表 |
| 116 | 疾抽手套 | `dynasty:quickdraw_glove` | 手部（+万能槽） | [常驻] 攻速 +18% · 击退 +0.6；命中：连击 +5% 每层 额外伤害（最多 6 层、3 秒内有效） | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 117 | 祈雨结 | `dynasty:rain_prayer_knot` | 护符（+万能槽） | [雷雨] 攻速 +20% · 攻击 +30% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 118 | 望距罗盘 | `dynasty:ranging_compass_charm` | 护符（+万能槽） | [常驻] 攻击距离 +2 · 攻击 +8% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 119 | 犀角 | `dynasty:rhino_horn` | 护符（+万能槽） | [常驻] 攻击 +14% · 护甲 +6 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 120 | 刀穗 | `dynasty:saber_tassel` | 腰带（+万能槽） | [常驻] 攻击 +7% · 攻速 +5% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 121 | 祭刃坠 | `dynasty:sacrificial_blade_charm` | 护符（+万能槽） | [常驻] 攻击 +38%；效果：内伤 I；命中：斩杀 +18% 血线以下的目标（Boss / 神兽免斩），概率 80% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 122 | 甲片 | `dynasty:scale_plate` | 身体（+万能槽） | [常驻] 护甲 +9 · 抗击退 +0.2 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 123 | 血莲 | `dynasty:scarlet_lotus` | 护符（+万能槽） | [残血] 护甲 +14 · 攻速 +15% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 124 | 墨玉印坠 | `dynasty:scholar_ink_badge` | 身体（+万能槽） | [常驻] 生命 +180 · 幸运 +1 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 125 | 书箱坠 | `dynasty:scroll_case_charm` | 背部（+万能槽） | [常驻] 攻速 +10% · 幸运 +1 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 126 | 海螺 | `dynasty:sea_conch` | 护符（+万能槽） | 水下呼吸；水下 攻击 +30% · 护甲 +10 | `DynastyTrinketTips.java` LEGACY 表 |
| 127 | 避水珠 | `dynasty:sea_pearl` | 护符（+万能槽） | 水下呼吸 · 海豚的恩惠；水下 攻击 +20% · 护甲 +6 | `DynastyTrinketTips.java` LEGACY 表 |
| 128 | 印章坠 | `dynasty:seal_charm` | 护符（+万能槽） | [常驻] 生命 +100 · 幸运 +1 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 129 | 双天印 | `dynasty:seal_of_two_heavens` | 护符（+万能槽） | [常驻] 攻击 +12%；[白天] 移速 +6%；效果：龙威 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 130 | 破阵锤坠 | `dynasty:siege_hammer_charm` | 护符（+万能槽） | [满血] 攻击 +25%；命中：斩杀 +12% 血线以下的目标（Boss / 神兽免斩），概率 80% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 131 | 锦囊 | `dynasty:silk_pouch` | 腰带（+万能槽） | 常驻夜视 · 水下呼吸 | `DynastyTrinketTips.java` LEGACY 表 |
| 132 | 天羽 | `dynasty:sky_feather` | 背部（+万能槽） | 跳跃提升 II · 移速 +8% | `DynastyTrinketTips.java` LEGACY 表 |
| 133 | 蛇胆 | `dynasty:snake_gall` | 护符（+万能槽） | [水下] 攻击 +10% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 134 | 命烛坠 | `dynasty:soul_candle_charm` | 项链（+万能槽） | [常驻] 生命上限 -25%；[夜晚] 攻击 +28%；命中：吸血 +10%（按造成的伤害回血），概率 50% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 135 | 司南 | `dynasty:south_pointing_compass` | 护符（+万能槽） | 常驻抗性提升 | `DynastyTrinketTips.java` LEGACY 表 |
| 136 | 星盘 | `dynasty:star_compass` | 护符（+万能槽） | 攻击 +12% · 移速 +6% | `DynastyTrinketTips.java` LEGACY 表 |
| 137 | 星图佩 | `dynasty:star_diagram_charm` | 护符（+万能槽） | [常驻] 幸运 +3 · 生命 +140 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 138 | 星斗盘 | `dynasty:star_dial` | 护符（+万能槽） | [常驻] 攻击 +12% · 攻速 +10% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 139 | 无星夜戒 | `dynasty:starless_night_ring` | 戒指（+万能槽） | [夜晚] 生命 +220；[夜晚] 攻击 +16%；命中：吸血 +8%（按造成的伤害回血） | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 140 | 镇海锚坠 | `dynasty:storm_anchor_charm` | 护符（+万能槽） | [常驻] 护甲 +20 · 击退 +0.5 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 141 | 雷纹护符 | `dynasty:storm_charm` | 护符（+万能槽） | 常驻抗性；雷雨天 额外力量 II + 迅捷 | `DynastyTrinketTips.java` LEGACY 表 |
| 142 | 追阳戒 | `dynasty:sun_chaser_ring` | 戒指（+万能槽） | [白天] 移速 +12% · 攻击 +10% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 143 | 金乌翎 | `dynasty:sun_feather` | 头部（+万能槽） | 白天 攻击 +15% · 击退 +0.3；夜晚 抗性 | `DynastyTrinketTips.java` LEGACY 表 |
| 144 | 剑穗 | `dynasty:sword_tassel` | 腰带（+万能槽） | [常驻] 攻击 +6% · 攻击距离 +1 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 145 | 符纸包 | `dynasty:talisman_pouch` | 腰带（+万能槽） | [常驻] 幸运 +3；效果：幸运 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 146 | 茶盏 | `dynasty:tea_cup` | 护符（+万能槽） | [常驻] 生命 +200；效果：再生 II | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 147 | 承天佩 | `dynasty:throne_inheritance_charm` | 项链（+万能槽） | [常驻] 生命 +260；效果：天命 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 148 | 雷印符 | `dynasty:thunder_seal_charm` | 护符（+万能槽） | [常驻] 攻击 +14% · 攻速 +10% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 149 | 天罡符 | `dynasty:tiangang_talisman` | 护符（+万能槽） | [常驻] 攻击 +18% · 抗击退 +0.4 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 150 | 潮信坠 | `dynasty:tide_compass_charm` | 护符（+万能槽） | [常驻] 攻击距离 +2 · 移速 +6% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 151 | 虎爪 | `dynasty:tiger_claw` | 手部（+万能槽） | [常驻] 攻击 +12% · 击退 +0.4 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 152 | 虎符残片 | `dynasty:tiger_crest` | 护符（+万能槽） | 每 40 秒 威压 8 格内敌人，让他们放弃锁定你 | `DynastyTrinketTips.java` LEGACY 表 |
| 153 | 虎头令 | `dynasty:tiger_token` | 护符（+万能槽） | 移速 +8% · 跳跃提升 | `DynastyTrinketTips.java` LEGACY 表 |
| 154 | 长明烛 | `dynasty:tomb_candle` | 护符（+万能槽） | 常驻夜视；每 2 秒 清除凋零 | `DynastyTrinketTips.java` LEGACY 表 |
| 155 | 守陵印 | `dynasty:tomb_warden_seal` | 护符（+万能槽） | [常驻] 护甲 +25；效果：内伤 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 156 | 龟血符 | `dynasty:turtle_blood_charm` | 护符（+万能槽） | [残血] 生命 +300 · 护甲 +16；效果：抗性 I | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 157 | 龟甲 | `dynasty:turtle_shell` | 背部（+万能槽） | [常驻] 护甲 +16 · 抗击退 +0.5 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 158 | 蝉蜕影 | `dynasty:twilight_cicada` | 护符（+万能槽） | [白天] 抗击退 +0.4；[夜晚] 攻击距离 +1 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 159 | 不倾之壁 | `dynasty:unbroken_wall_charm` | 护符（+万能槽） | [常驻] 抗击退 +0.5；效果：铁壁 II | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 160 | 鬼门钥 | `dynasty:underworld_gate_key` | 护符（+万能槽） | [雷雨] 攻击 +45%；命中：雷罚 附加 +90 点伤害，概率 25% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 161 | 战旗坠 | `dynasty:war_banner_charm` | 背部（+万能槽） | [常驻] 攻击 +12% · 攻速 +6% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 162 | 战神印 | `dynasty:war_deity_signet` | 护符（+万能槽） | [常驻] 攻击 +15%；效果：龙威 II；命中：会心 +40% 额外伤害，概率 30% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 163 | 战鼓坠 | `dynasty:war_drum_charm` | 护符（+万能槽） | 常驻力量 I；每秒 给 12 格内友军力量 | `DynastyTrinketTips.java` LEGACY 表 |
| 164 | 战马铃 | `dynasty:war_horse_bell` | 腰带（+万能槽） | 骑乘时 坐骑迅捷 II + 抗性；步行时 护甲 +5 | `DynastyTrinketTips.java` LEGACY 表 |
| 165 | 战鼓墩 | `dynasty:warlord_drum_charm` | 手部（+万能槽） | [满血] 攻速 +12%；[残血] 攻击 +40%；命中：连击 +6% 每层 额外伤害（最多 6 层、3 秒内有效） | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 166 | 酒葫芦 | `dynasty:wine_gourd` | 腰带（+万能槽） | [常驻] 生命 +240 · 击退 +0.3 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 167 | 绷带佩 | `dynasty:wound_binder_charm` | 护符（+万能槽） | [残血] 护甲 +25 · 攻速 +18% | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 168 | 护腕 | `dynasty:wrist_guard` | 手镯（+万能槽） | [常驻] 护甲 +10 · 抗击退 +0.3 | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |
| 169 | 禅珠串 | `dynasty:zen_bead_string` | 手镯（+万能槽） | [残血] 生命 +220；效果：再生 II | `DynastyTrinkets.java` EXTRA_TABLE + `DynastyTrinketTips.java` 解码 |

## 待确认

* 缺中文名：无
* 效果无法从代码表推导（既不在 EXTRA_TABLE 也不在 LEGACY）：无
* 手写饰品（LEGACY）只有展示文案、没有结构化数值；数值以 `DynastyTrinkets` 的 `apply()` / `tick()`
  switch 为准，本表按 LEGACY 文案转写。
* 连携档位（2/3/4 件的具体加成）见 `DynastyTrinkets.LINK_TABLE` 与 `DynastyTrinketLink.java`，
  本表只标出所属连携组。
