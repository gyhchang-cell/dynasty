package com.dynasty;

import java.util.List;

/** 图鉴·兵器与工具 / codex: weapons and tools（完整进化链）。 */
final class DynastyCodexWeapons {

    private DynastyCodexWeapons() {
    }

    private static void add(List<DynastyCodex.Entry> l, String id, String zh, String en,
                            String zhUse, String enUse, String... ingredients) {
        l.add(new DynastyCodex.Entry(id, zh, en, zhUse, enUse, ingredients));
    }

    static void add(List<DynastyCodex.Entry> l) {
        // ---- 基础期 / basic tier ----
        add(l, "mu_mao", "合成：木棍×2 + 木板（攻击 5）", "Craft: 2 sticks + planks (5 damage)",
                "开局武器：便宜、伤害低，先打点动物与杂兵。回头可以一路进化上去。",
                "Starting weapon: cheap and weak; the first step of the whole chain.",
                "minecraft:stick", "minecraft:oak_planks");
        add(l, "shi_ge", "合成：木矛 + 圆石×2（攻击 9）", "Craft: spear + 2 cobblestone (9)",
                "石制兵器，比木矛结实一点。", "Stone tier, sturdier than the spear.",
                "dynasty:mu_mao", "minecraft:cobblestone");
        add(l, "tong_dao", "合成：石戈 + 铜锭×3（攻击 14）", "Craft: stone axe + 3 copper (14)",
                "用原版铜锭锻造，前期够用。", "Forge it from vanilla copper.",
                "dynasty:shi_ge", "minecraft:copper_ingot");
        add(l, "tie_jian", "合成：铜刀 + 铁锭×3（攻击 20）", "Craft: copper sabre + 3 iron (20)",
                "原版铁剑同级，抗得住前期的锦衣卫。", "Iron-tier blade for early elites.",
                "dynasty:tong_dao", "minecraft:iron_ingot");
        add(l, "lie_gong", "合成：木棍×3 + 线×3", "Craft: 3 sticks + 3 string",
                "远程入门弓：箭矢伤害 ×1.5 + 4。", "Entry bow: arrow damage x1.5 + 4.",
                "minecraft:stick", "minecraft:string");

        // ---- 王朝期 / dynasty tier（需要兵器图纸）----
        add(l, "blueprint", "合成：纸 + 墨条 + 竹简", "Craft: paper + ink stick + bamboo slip",
                "兵器图纸：从青铜剑开始，进阶武器都需要它（相当于「锻造配方」）。",
                "Weapon blueprint: every weapon past iron requires one.",
                "minecraft:paper", "dynasty:ink_stick", "dynasty:bamboo_slip");
        add(l, "sword_bronze", "合成：铁剑 + 青铜锭×3 + 图纸（攻击 34）",
                "Craft: iron sword + 3 bronze + blueprint (34)",
                "王朝第一把神兵，从这里开始数字会明显变大。",
                "The first dynasty blade - the numbers jump from here.",
                "dynasty:tie_jian", "dynasty:bronze_ingot", "dynasty:blueprint");
        add(l, "tang_dao", "合成：青铜剑 + 青铜锭×2 + 丝绸 + 图纸（攻击 46）",
                "Craft: bronze sword + 2 bronze + silk + blueprint (46)",
                "攻速最快（约 2.8 次/秒），命中后短暂加速，连击流首选。",
                "Fastest swing (~2.8/s) with a short speed boost on hit.",
                "dynasty:sword_bronze", "dynasty:bronze_ingot", "dynasty:silk");
        add(l, "huan_shou_dao", "合成：唐刀 + 青铜锭×2 + 铜钱 + 图纸（攻击 62）",
                "Craft: Tang Dao + 2 bronze + coin + blueprint (62)",
                "受击后获得力量 II —— 越被打越强。",
                "Taking a hit grants Strength II.",
                "dynasty:tang_dao", "dynasty:bronze_ingot", "dynasty:gold_coin");
        add(l, "chang_gong", "合成：猎弓 + 丝绸×2 + 精钢 + 图纸",
                "Craft: hunting bow + 2 silk + refined steel + blueprint",
                "远程进阶：箭矢伤害 ×2 + 20，耐久 1600。",
                "Mid bow: arrow damage x2 + 20, 1600 durability.",
                "dynasty:lie_gong", "dynasty:silk", "dynasty:refined_steel");
        add(l, "chang_qiang", "合成：环首刀 + 银锭×2 + 竹简 + 图纸（攻击 82）",
                "Craft: Huan Shou Dao + 2 silver + bamboo slip + blueprint (82)",
                "攻击距离 +3（可隔一格打到人），命中挑飞目标。",
                "+3 reach, and hits launch the target upward.",
                "dynasty:huan_shou_dao", "dynasty:silver_ingot", "dynasty:bamboo_slip");
        add(l, "yu_di", "合成：长枪 + 玉×2 + 丝绸 + 图纸（攻击 105）",
                "Craft: Chang Qiang + 2 jade + silk + blueprint (105)",
                "右键吹奏：8 格内敌人虚弱 + 缓慢，自身获得力量。",
                "Right-click: weakness + slowness in 8 blocks, strength for you.",
                "dynasty:chang_qiang", "dynasty:jade", "dynasty:silk");
        add(l, "sword_silver", "合成：玉笛 + 银锭×3 + 图纸（攻击 132）",
                "Craft: Jade Flute + 3 silver + blueprint (132)",
                "官银铸剑，中庸可靠。", "Reliable official-silver blade.",
                "dynasty:yu_di", "dynasty:silver_ingot", "dynasty:blueprint");
        add(l, "sword_jade", "合成：官银剑 + 玉×3 + 图纸（攻击 170）",
                "Craft: silver sword + 3 jade + blueprint (170)",
                "附魔值 32，最适合叠附魔。", "Enchantability 32 - best for stacking enchants.",
                "dynasty:sword_silver", "dynasty:jade", "dynasty:blueprint");
        add(l, "juque_sword", "合成：玉剑 + 玉×2 + 青铜锭 + 图纸（攻击 500）",
                "Craft: jade sword + 2 jade + bronze + blueprint (220)",
                "重击：命中击退并施加缓慢 II。", "Heavy hits knock back and inflict Slowness II.",
                "dynasty:sword_jade", "dynasty:jade", "dynasty:bronze_ingot");

        // ---- 名将期：需要 Boss 掉落物 / requires boss drops ----
        add(l, "pojun_axe", "合成：巨阙重剑 + 龙鳞×2 + 龙晶 + 叛将首级（攻击 650）",
                "Craft: Juque + 2 dragon scale + crystal + Rebel Head (300)",
                "★ 击败「叛将」获得首级才能锻造。破甲：无视目标一半士气减伤。",
                "★ Gated behind the Rebel General's head. Armour-piercing: halves enemy toughness.",
                "dynasty:juque_sword", "dynasty:dragon_scale", "dynasty:rebel_head");
        add(l, "dragon_bow", "合成：长弓 + 龙鳞×2 + 凤凰羽 + 龙晶（箭矢 ×3.5 + 150）",
                "Craft: longbow + 2 dragon scale + phoenix feather + crystal (arrow x3 + 90)",
                "★ 需要凤凰掉落「凤凰羽」。穿透 3、强击退，耐久 8000。",
                "★ Needs a phoenix feather. Pierce 3, heavy knockback, 8000 durability.",
                "dynasty:chang_gong", "dynasty:dragon_scale", "dynasty:phoenix_feather");

        // ---- 弓·速射支线（长弓 → 神臂弓 → 落雁弓 → 天狼弓）----
        add(l, "shenbi_bow", "合成：长弓 + 精钢×3 + 丝绸×2 + 图纸（箭矢 ×2.8 + 70）",
                "Craft: longbow + 3 refined steel + 2 silk + blueprint (x2.5 + 45)",
                "弓·速射支线第一步（另一条支线是龙吟弓的穿透流）。耐久 3000。",
                "First step of the rapid-fire bow branch. 3000 durability.",
                "dynasty:chang_gong", "dynasty:refined_steel", "dynasty:silk", "dynasty:blueprint");
        add(l, "luoyan_bow", "合成：神臂弓 + 精钢×4 + 银锭×2 + 图纸（箭矢 ×3.3 + 120）",
                "Craft: Shenbi Bow + 4 refined steel + 2 silver + blueprint (x2.9 + 75)",
                "速射支线中段：耐久 6000，中期弓手的主力。",
                "Mid-tier of the rapid-fire branch. 6000 durability.",
                "dynasty:shenbi_bow", "dynasty:refined_steel", "dynasty:silver_ingot",
                "dynasty:blueprint");
        add(l, "tianlang_bow", "合成：落雁弓 + 龙晶×2 + 精钢×6（箭矢 ×3.8 + 200、穿透 1）",
                "Craft: Luoyan Bow + 2 dragon crystal + 6 refined steel (x3.2 + 120, pierce 1)",
                "速射支线终点：带穿透 1，一箭能串两个敌人。耐久 7500。",
                "End of the rapid-fire branch: pierce 1. 7500 durability.",
                "dynasty:luoyan_bow", "dynasty:dragon_crystal", "dynasty:refined_steel");
        add(l, "sword_dragon_crystal", "合成：巨阙重剑 + 龙晶×2 + 龙鳞 + 内廷令牌（攻击 1400）",
                "Craft: Juque + 2 crystal + scale + Palace Token (420)",
                "★ 需要「宦官首脑」掉落的内廷令牌。顶级附魔剑（附魔值 40）。",
                "★ Needs the Eunuch Mastermind's token. Enchantability 40.",
                "dynasty:juque_sword", "dynasty:dragon_crystal", "dynasty:eunuch_token");

        // ---- 帝兵期：多件 Boss 掉落物 ----
        add(l, "halberd_fangtian", "合成：破军战斧 + 龙晶剑 + 龙鳞×2 + 帝骸骨 + 图纸（攻击 1900）",
                "Craft: Po Jun Axe + Dragon Crystal Sword + 2 scale + Emperor Bone (620)",
                "★★ 同时需要两把名兵与「不死始皇」的帝骸骨。横扫 3 格内敌人。",
                "★★ Requires two named weapons plus the Undead Emperor's bone. Sweeps nearby foes.",
                "dynasty:pojun_axe", "dynasty:sword_dragon_crystal", "dynasty:emperor_bone");
        add(l, "xuantian_axe", "合成：破军战斧 + 龙晶×2 + 龙帝玉玺（攻击 2500）",
                "Craft: Po Jun Axe + 2 crystal + Dragon Emperor's Seal (800)",
                "★★ 只有击败「龙帝」拿到玉玺才能做。破甲 + 震慑（缓慢 II）。",
                "★★ Only craftable with the Dragon Emperor's seal. Piercing + Slow II.",
                "dynasty:pojun_axe", "dynasty:dragon_crystal", "dynasty:dragon_emperor_seal");
        add(l, "tianzi_sword", "合成：方天画戟 + 玄天玉 + 龙帝玉玺 + 帝骸骨 + 内廷令牌 + 玉玺（攻击 3200）",
                "Craft: Halberd + Xuantian Jade + 3 boss tokens + Jade Seal (2048 + 500 extra)",
                "★★★ 终极神兵：三件 Boss 信物 + 科举最好拿到的「玉玺」。命中回气、对王朝敌人加伤 20%。",
                "★★★ The endgame blade: three boss tokens plus the Jade Seal from the exams. "
                        + "Heals on hit and deals +20% to dynasty enemies.",
                "dynasty:halberd_fangtian", "dynasty:dragon_emperor_seal", "dynasty:jade_seal");

        // ---- 工具 ----
        add(l, "pickaxe_jade", "合成：玉×2 + 木棍×2 + 图纸", "Craft: 2 jade + 2 sticks + blueprint",
                "工具：挖得快、攻击 170、耐久 45000。",
                "Tool: fast mining, 170 damage, 45000 durability.",
                "dynasty:jade", "minecraft:stick");
        add(l, "pickaxe_dragon_crystal", "合成：玉镐 + 龙晶×2 + 精钢 + 帝骸骨（攻击 420）",
                "Craft: jade pickaxe + 2 crystal + steel + Emperor Bone (420)",
                "顶阶工具：挖掘速度 28、耐久 120000。",
                "Endgame tool: speed 28, 120000 durability.",
                "dynasty:pickaxe_jade", "dynasty:dragon_crystal", "dynasty:emperor_bone");
            add(l, "longyuan_sword", "合成：龙渊剑 + 材料 ×2 + 图纸（攻击 1800，特攻 +200）",
                "Craft: sword_dragon_crystal + materials + blueprint (攻击 1800, +200 extra)",
                "毕业兵器之一：需要先做出「sword_dragon_crystal」。",
                "One of the endgame weapons; requires sword_dragon_crystal.",
                "dynasty:sword_dragon_crystal");
        add(l, "juling_axe", "合成：巨灵斧 + 材料 ×2 + 图纸（攻击 2200，特攻 +300）",
                "Craft: pojun_axe + materials + blueprint (攻击 2200, +300 extra)",
                "毕业兵器之一：需要先做出「pojun_axe」。",
                "One of the endgame weapons; requires pojun_axe.",
                "dynasty:pojun_axe");
        add(l, "qinglong_dao", "合成：青龙偃月刀 + 材料 ×2 + 图纸（攻击 2600，特攻 +350）",
                "Craft: huan_shou_dao + materials + blueprint (攻击 2600, +350 extra)",
                "毕业兵器之一：需要先做出「huan_shou_dao」。",
                "One of the endgame weapons; requires huan_shou_dao.",
                "dynasty:huan_shou_dao");
        add(l, "bawang_spear", "合成：霸王枪 + 材料 ×2 + 图纸（攻击 3000，特攻 +400）",
                "Craft: dragon_spear + materials + blueprint (攻击 3000, +400 extra)",
                "毕业兵器之一：需要先做出「dragon_spear」。",
                "One of the endgame weapons; requires dragon_spear.",
                "dynasty:dragon_spear");
        add(l, "houyi_bow", "合成：后羿弓 + 材料 ×2 + 图纸（箭矢 ×4.0 + 300，特攻 +250）",
                "Craft: sunbow + materials + blueprint (箭矢 ×4.0 + 300, +250 extra)",
                "毕业兵器之一：需要先做出「sunbow」。",
                "One of the endgame weapons; requires sunbow.",
                "dynasty:sunbow");
        add(l, "leiting_hammer", "合成：雷霆锤 + 材料 ×2 + 图纸（攻击 3300，特攻 +450）",
                "Craft: xuantian_axe + materials + blueprint (攻击 3300, +450 extra)",
                "毕业兵器之一：需要先做出「xuantian_axe」。",
                "One of the endgame weapons; requires xuantian_axe.",
                "dynasty:xuantian_axe");
        add(l, "taiyi_whisk", "合成：太乙拂尘 + 材料 ×2 + 图纸（攻击 3600，特攻 +500）",
                "Craft: yu_di + materials + blueprint (攻击 3600, +500 extra)",
                "毕业兵器之一：需要先做出「yu_di」。",
                "One of the endgame weapons; requires yu_di.",
                "dynasty:yu_di");
        add(l, "xuanwu_blade", "合成：玄武盾刀 + 材料 ×2 + 图纸（攻击 4000，特攻 +550）",
                "Craft: dragon_slayer + materials + blueprint (攻击 4000, +550 extra)",
                "毕业兵器之一：需要先做出「dragon_slayer」。",
                "One of the endgame weapons; requires dragon_slayer.",
                "dynasty:dragon_slayer");
        add(l, "zhuque_fan", "合成：朱雀羽扇 + 材料 ×2 + 图纸（攻击 4400，特攻 +600）",
                "Craft: supreme_sword + materials + blueprint (攻击 4400, +600 extra)",
                "毕业兵器之一：需要先做出「supreme_sword」。",
                "One of the endgame weapons; requires supreme_sword.",
                "dynasty:supreme_sword");
        add(l, "hunyuan_staff", "合成：混元珠杖 + 材料 ×2 + 图纸（攻击 5000，特攻 +800）",
                "Craft: tianzi_sword + materials + blueprint (攻击 5000, +800 extra)",
                "毕业兵器之一：需要先做出「tianzi_sword」。",
                "One of the endgame weapons; requires tianzi_sword.",
                "dynasty:tianzi_sword");

        // ---- 第三十二轮的 6 把帝兵 / the six imperial weapons of round 32 ----
        add(l, "qilin_war_axe", "合成：麒麟角 + 精钢×2 + 图纸（攻击 2000，特攻 +250）",
                "Craft: qilin horn + 2 refined steel + blueprint (2000 damage, +250 extra)",
                "麒麟战斧：攻高、击退稳，配麒麟线饰品很好用。",
                "Qilin War Axe: heavy hits with steady knockback; pairs well with the qilin trinket line.",
                "dynasty:qilin_horn", "dynasty:refined_steel", "dynasty:blueprint");
        add(l, "taiyi_sword", "合成：太乙玉 + 龙晶 + 图纸（攻击 2300，特攻 +300）",
                "Craft: taiyi jade + dragon crystal + blueprint (2300 damage, +300 extra)",
                "太乙法剑：需要先做出太乙玉（玄天玉 + 玉×2）。",
                "Taiyi Sword: needs Taiyi Jade (xuantian jade + 2 jade) first.",
                "dynasty:taiyi_jade", "dynasty:dragon_crystal", "dynasty:blueprint");
        add(l, "baihu_glaive", "合成：白虎牙 + 精钢×2 + 图纸（攻击 2600，特攻 +330）",
                "Craft: white tiger fang + 2 refined steel + blueprint (2600 damage, +330 extra)",
                "白虎戟：长柄，攻击距离 +3，适合骑马冲阵。",
                "White Tiger Glaive: a polearm with +3 reach, ideal for mounted charges.",
                "dynasty:baihu_fang", "dynasty:refined_steel", "dynasty:blueprint");
        add(l, "thunder_spear", "合成：雷部令 + 精钢×2 + 图纸（攻击 2900，特攻 +360）",
                "Craft: thunder token + 2 refined steel + blueprint (2900 damage, +360 extra)",
                "雷霆枪：雷部令来自符纸路线，冲锋时伤害很稳。",
                "Thunder Spear: the thunder token comes from the talisman line.",
                "dynasty:thunder_token", "dynasty:refined_steel", "dynasty:blueprint");
        add(l, "ziwei_saber", "合成：龙晶 + 玄天玉 + 图纸（攻击 3200，特攻 +400）",
                "Craft: dragon crystal + xuantian jade + blueprint (3200 damage, +400 extra)",
                "紫微刀：帝兵期的刀，攻速比战斧快。",
                "Ziwei Saber: a late-game sabre, faster than the war axes.",
                "dynasty:dragon_crystal", "dynasty:xuantian_jade", "dynasty:blueprint");
        add(l, "zhuque_bow", "合成：朱雀羽 + 凤凰羽 + 龙吟弓 + 图纸（箭矢 ×4.0 + 300）",
                "Craft: vermilion feather + phoenix feather + dragon bow + blueprint (×4.0 + 300)",
                "朱雀弓：需要朱雀羽（凤凰羽×2 + 朱砂×2），穿透 2。",
                "Vermilion Bow: needs a Vermilion Feather (2 phoenix feather + 2 cinnabar); pierces 2 targets.",
                "dynasty:zhuque_feather", "dynasty:phoenix_feather", "dynasty:dragon_bow");
    }
}
