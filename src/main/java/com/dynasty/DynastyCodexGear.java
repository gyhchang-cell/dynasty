package com.dynasty;

import java.util.List;

/** 图鉴·护甲 / 材料信物 / 新饰品 / codex: armour, relics and the new trinkets. */
final class DynastyCodexGear {

    private DynastyCodexGear() {
    }

    private static void add(List<DynastyCodex.Entry> l, String id, String zh, String en,
                            String zhUse, String enUse, String... ingredients) {
        l.add(new DynastyCodex.Entry(id, zh, en, zhUse, enUse, ingredients));
    }

    static void add(List<DynastyCodex.Entry> l) {
        // 护甲进化链 / armour evolution
        add(l, "cloth_chestplate", "合成：丝绸（布巾/布甲/布裤/布靴同款图案）",
                "Craft from silk (same pattern for the whole set)",
                "布衣套：防御很低但便宜，整套减伤约 12%、生命 +120。开局先穿它。",
                "Cloth set: cheap, ~12% set reduction and +120 health. The starting armour.",
                "dynasty:silk");
        add(l, "general_chestplate", "进化：布甲 + 青铜锭×3 + 图纸（各部位同理）",
                "Upgrade: cloth piece + 3 bronze + blueprint (same for every piece)",
                "将军铠：整套护甲 27、减伤 64%、生命 +600。",
                "General set: 27 armour, 64% set reduction, +600 health.",
                "dynasty:cloth_chestplate", "dynasty:bronze_ingot");
        add(l, "jade_chestplate", "进化：将军铠 + 玉×3 + 图纸",
                "Upgrade: general piece + 3 jade + blueprint",
                "玉甲：整套护甲 44、减伤 80%、生命 +880、附魔值最高。",
                "Jade set: 44 armour, 80% reduction, +880 health, best enchantability.",
                "dynasty:general_chestplate", "dynasty:jade");
        add(l, "dragon_scale_chestplate", "进化：玉甲 + 龙鳞×2 + 龙晶 + 图纸",
                "Upgrade: jade piece + 2 dragon scale + crystal + blueprint",
                "龙鳞甲：整套护甲 60、减伤 96%、生命 +1200。",
                "Dragon scale set: 60 armour, 96% reduction, +1200 health.",
                "dynasty:jade_chestplate", "dynasty:dragon_scale");
        add(l, "xuantian_chestplate", "进化：龙鳞甲 + 玄天玉 + 龙晶 + 帝骸骨 + 龙帝玉玺",
                "Upgrade: dragon scale piece + Xuantian Jade + crystal + Emperor Bone + Dragon Emperor's Seal",
                "★★ 玄天真龙甲：整套护甲 76、减伤 92%、生命 +1520。终盘套装，必须击败龙帝。",
                "★★ Xuantian set: 76 armour, 92% reduction, +1520 health. Requires the Dragon Emperor.",
                "dynasty:dragon_scale_chestplate", "dynasty:xuantian_jade",
                "dynasty:dragon_emperor_seal");

        // 材料与信物 / relics
        add(l, "refined_steel", "合成：铁锭×3 + 朱砂 → 精钢×2",
                "Craft: 3 iron ingots + cinnabar -> 2 refined steel",
                "中后期通用材料：图纸配方与进阶弓、镐都要用。",
                "Mid/late crafting material used by bows, pickaxes and blueprints.",
                "minecraft:iron_ingot", "dynasty:cinnabar");
        add(l, "rebel_head", "掉落：击败「叛将」（地府/宫殿深处）",
                "Drop: the Rebel General", "打造破军战斧的必要条件。",
                "Required for the Po Jun Axe.", "dynasty:pojun_axe");
        add(l, "eunuch_token", "掉落：击败「宦官首脑」", "Drop: the Eunuch Mastermind",
                "打造龙晶剑、天子剑的必要条件。", "Required for the Dragon Crystal and Heaven swords.",
                "dynasty:sword_dragon_crystal");
        add(l, "emperor_bone", "掉落：击败「不死始皇」/「龙帝」",
                "Drop: the Undead Emperor / Dragon Emperor",
                "打造方天画戟、玄天玉、龙晶镐的必要条件。",
                "Required for the halberd, Xuantian jade and the crystal pickaxe.",
                "dynasty:halberd_fangtian");
        add(l, "dragon_emperor_seal", "掉落：击败「龙帝」（天朝·龙庭）",
                "Drop: the Dragon Emperor (celestial realm)",
                "★★ 终盘唯一凭据：玄天钺、玄天真龙甲、天子剑都点名要它。",
                "★★ The endgame token: the Xuantian axe, armour and the Sword of Heaven all need it.",
                "dynasty:xuantian_axe");
        add(l, "xuantian_jade", "合成：帝骸骨 + 玉×2 + 龙晶",
                "Craft: Emperor Bone + 2 jade + dragon crystal",
                "玄天套装的强化玉料。", "The material that upgrades armour into the Xuantian set.",
                "dynasty:emperor_bone", "dynasty:jade", "dynasty:dragon_crystal");

        // 10 套甲 / 10 件兵器点名要的高阶材料 / materials for the ten sets and weapons
        add(l, "xuanwu_shell", "合成：龙鳞×2 + 精钢×2 + 图纸",
                "Craft: 2 dragon scale + 2 refined steel + blueprint",
                "玄武甲的甲片：极致防御路线（四件套减伤 88%）。",
                "The plate of the Xuanwu set: the pure-defence route.",
                "dynasty:dragon_scale", "dynasty:refined_steel", "dynasty:blueprint");
        add(l, "qinglong_scale", "合成：龙鳞×2 + 龙晶 + 图纸",
                "Craft: 2 dragon scale + dragon crystal + blueprint",
                "青龙鳞甲、青龙偃月刀的鳞料；青龙线攻击 +10%。",
                "Scale for the Qinglong set and the Qinglong glaive: +10% attack.",
                "dynasty:dragon_scale", "dynasty:dragon_crystal", "dynasty:blueprint");
        add(l, "baihu_fang", "合成：龙晶×2 + 精钢×2 + 图纸",
                "Craft: 2 dragon crystal + 2 refined steel + blueprint",
                "白虎铠、霸王枪的锋料；白虎线攻高击退高。",
                "Fang for the White Tiger set and the Hegemon spear: high attack and knockback.",
                "dynasty:dragon_crystal", "dynasty:refined_steel", "dynasty:blueprint");
        add(l, "zhuque_feather", "合成：凤凰羽×2 + 朱砂×2 + 图纸",
                "Craft: 2 phoenix feather + 2 cinnabar + blueprint",
                "朱雀羽衣、朱雀羽扇的羽料；朱雀线抗火、火伤减半。",
                "Feather for the Vermilion set and fan: fire resistance and halved fire damage.",
                "dynasty:phoenix_feather", "dynasty:cinnabar", "dynasty:blueprint");
        add(l, "taiyi_jade", "合成：玄天玉 + 玉×2 + 图纸",
                "Craft: xuantian jade + 2 jade + blueprint",
                "太乙甲、太乙拂尘的玉料；太乙线全属性小幅提升。",
                "Jade for the Taiyi set and whisk: a small boost to every attribute.",
                "dynasty:xuantian_jade", "dynasty:jade", "dynasty:blueprint");
        add(l, "thunder_token", "合成：符纸×2 + 朱砂×2 + 图纸",
                "Craft: 2 talisman paper + 2 cinnabar + blueprint",
                "雷部令：雷霆锤的引雷令牌，也是雷部使者相关的信物。",
                "Thunder Token: the lightning token for the Thunder Hammer.",
                "dynasty:talisman_paper", "dynasty:cinnabar", "dynasty:blueprint");
        add(l, "hunyuan_pearl", "合成：龙晶×2 + 龙帝玉玺 + 帝骸骨",
                "Craft: 2 dragon crystal + Dragon Emperor Seal + Emperor Bone",
                "★★ 毕业材料：混元甲与混元珠杖的唯一材料，必须先打龙帝与始皇。",
                "★★ The graduation material: needed by the Hunyuan set and staff. Slay the Dragon Emperor and the First Emperor first.",
                "dynasty:dragon_crystal", "dynasty:dragon_emperor_seal", "dynasty:emperor_bone");

        // 新饰品 / new trinkets
        add(l, "heart_mirror", "合成：青铜锭×2 + 银锭 + 丝绸",
                "Craft: 2 bronze + silver ingot + silk",
                "饰品：护甲 +8、额外 4% 减伤；可放饰品槽或 Curios「饰品」槽。",
                "Trinket: +8 armour and 4% extra damage reduction.",
                "dynasty:bronze_ingot", "dynasty:silver_ingot");
        add(l, "jade_crown", "合成：玉×2 + 金锭 + 丝绸",
                "Craft: 2 jade + gold coin + silk",
                "饰品：生命上限 +220，配合护甲套装效果更好。",
                "Trinket: +220 max health.",
                "dynasty:jade", "dynasty:gold_coin");
        // ---- 新增饰品 / new trinkets ----
        add(l, "jade_cicada", "合成：玉×2 + 丝绸 + 朱砂",
                "Craft: 2 jade + silk + cinnabar",
                "饰品：生命低于 30% 时自动获得抗性 II + 速度（保命，不回血）。",
                "Trinket: under 30% health you gain Resistance II and Speed (no healing).",
                "dynasty:jade", "dynasty:cinnabar");
        add(l, "dragon_pearl", "合成：龙晶×2 + 龙鳞 + 玉",
                "Craft: 2 dragon crystal + scale + jade",
                "饰品：攻击力 +25%、抗击退 +0.3 —— 输出流核心。",
                "Trinket: +25% attack damage and +0.3 knockback resistance.",
                "dynasty:dragon_crystal", "dynasty:dragon_scale");
        add(l, "phoenix_ring", "合成：凤凰羽 + 金锭×2 + 玉",
                "Craft: phoenix feather + 2 gold ingots + jade",
                "饰品：常驻抗火；着火时立刻灭火并加速（地府/岩浆海必备）。",
                "Trinket: permanent fire resistance and instantly extinguishes you with a speed boost.",
                "dynasty:phoenix_feather", "minecraft:gold_ingot");
        add(l, "storm_charm", "合成：朱砂 + 金锭 + 徽墨 + 丝绸",
                "Craft: cinnabar + gold ingot + ink stick + silk",
                "饰品：常驻抗性 I；雷雨天气额外获得力量 II + 速度。",
                "Trinket: permanent Resistance I; in rain/thunder you also gain Strength II and Speed.",
                "dynasty:cinnabar", "minecraft:gold_ingot");
        add(l, "moon_pendant", "合成：玉 + 荧石粉 + 金锭 + 丝绸",
                "Craft: jade + glowstone dust + gold ingot + silk",
                "饰品：夜间获得夜视、幸运 +2、攻击 +10%（夜战/探陵神器）。",
                "Trinket: at night you gain night vision, +2 luck and +10% attack.",
                "dynasty:jade", "minecraft:glowstone_dust");
        add(l, "tiger_crest", "合成：青铜锭×2 + 铜钱×2",
                "Craft: 2 bronze ingots + 2 copper coins",
                "饰品：每 40 秒威慑 8 格内敌人，令其放弃追击你。",
                "Trinket: every 40s intimidates hostile mobs within 8 blocks so they stop chasing you.",
                "dynasty:bronze_ingot", "dynasty:copper_coin");
        // 法阵·祭坛 / ritual altar
        add(l, "ritual_altar", "合成：玉石块×4 + 龙晶（也可在法阵/神庙建筑里找到）",
                "Craft: 4 jade blocks + dragon crystal (also spawns in ritual circles and temples)",
                "用 Boss 信物对着它右键即可召唤对应 Boss；四周 3×3 环里放 4 块玉石块才算成形。",
                "Right-click with a boss token to summon that boss; needs 4 jade blocks around it.",
                "dynasty:jade_block", "dynasty:dragon_crystal");
        // ---- 第三批饰品（可在建筑宝箱开出）/ third batch ----
        add(l, "jade_tortoise", "合成：玉×2 + 青铜锭 + 海洋之心（或宝箱开出）",
                "Craft: 2 jade + bronze + heart of the sea (or find in chests)",
                "饰品：水下呼吸 + 海豚恩惠 + 抗性 I —— 水战/渡海用。",
                "Trinket: water breathing, dolphin's grace and Resistance I.",
                "dynasty:jade", "minecraft:heart_of_the_sea");
        add(l, "war_drum_charm", "合成：青铜锭×2 + 丝绸 + 朱砂（或宝箱开出）",
                "Craft: 2 bronze + silk + cinnabar (or find in chests)",
                "饰品：自身常驻力量 I，并每 3 秒给 12 格内禁军/铁傀儡/宠物加力量。",
                "Trinket: Strength I for you, and every 3s for guards/golems/pets within 12 blocks.",
                "dynasty:bronze_ingot", "dynasty:silk");
        add(l, "cinnabar_pouch", "合成：朱砂×2 + 丝绸 + 符纸（或宝箱开出）",
                "Craft: 2 cinnabar + silk + talisman paper (or find in chests)",
                "饰品：每 2 秒净化中毒 / 凋零 / 失明 / 饥饿 —— 剧毒克星。",
                "Trinket: cleanses poison, wither, blindness and hunger every 2 seconds.",
                "dynasty:cinnabar", "dynasty:talisman_paper");
        add(l, "dragon_whisker", "合成：龙鳞 + 龙晶 + 丝绸 + 精钢（或宝箱开出）",
                "Craft: dragon scale + crystal + silk + steel (or find in chests)",
                "饰品：攻速 +15%、击退 +0.5 —— 连击流专属。",
                "Trinket: +15% attack speed and +0.5 attack knockback.",
                "dynasty:dragon_scale", "dynasty:dragon_crystal");
        add(l, "tiger_token", "合成：青铜锭 + 银锭 + 铜钱 + 丝绸（或宝箱开出）",
                "Craft: bronze + silver + coin + silk (or find in chests)",
                "饰品：移动速度 +8% 且常驻跳跃提升 —— 跑图神器。",
                "Trinket: +8% movement speed and permanent jump boost.",
                "dynasty:bronze_ingot", "dynasty:silver_ingot");
        add(l, "sun_feather", "合成：凤凰羽 + 荧石粉 + 金锭 + 织锦（或宝箱开出）",
                "Craft: phoenix feather + glowstone + gold + brocade (or find in chests)",
                "饰品：白天攻击 +15%、幸运 +1；夜里改给抗性 I（与明月佩互补）。",
                "Trinket: by day +15% attack and +1 luck; by night Resistance I.",
                "dynasty:phoenix_feather", "minecraft:glowstone_dust");
        add(l, "war_horse_bell", "合成：青铜锭×2 + 金锭 + 丝绸（或宝箱开出）",
                "Craft: 2 bronze + gold + silk (or find in chests)",
                "饰品：骑乘时坐骑获得速度 II + 抗性 I —— 骑兵流。",
                "Trinket: while mounted your mount gains Speed II and Resistance I.",
                "dynasty:bronze_ingot", "minecraft:gold_ingot");
        add(l, "iron_waist_token", "合成：铁锭×2 + 青铜锭 + 丝绸（或宝箱开出）",
                "Craft: 2 iron + bronze + silk (or find in chests)",
                "饰品：护甲 +6、抗击退 +0.2、生命 +150 —— 均衡加强。",
                "Trinket: +6 armour, +0.2 knockback resistance and +150 health.",
                "minecraft:iron_ingot", "dynasty:bronze_ingot");
        add(l, "auspicious_bell", "合成：金锭×2 + 青铜锭 + 丝绸（或宝箱开出）",
                "Craft: 2 gold coins + bronze + silk (or find in chests)",
                "饰品：幸运 +3 —— 钓鱼、掉落、附魔都更顺。",
                "Trinket: +3 luck (fishing, drops, enchanting).",
                "dynasty:gold_coin", "dynasty:bronze_ingot");
    }
}
