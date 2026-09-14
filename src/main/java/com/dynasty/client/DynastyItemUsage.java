package com.dynasty.client;

/** 重点物品的用法文案表 / usage text for key items. */
public final class DynastyItemUsage {

    private DynastyItemUsage() {
    }

    public static String[] special(String path) {
        return switch (path) {
            case "exam_paper" -> new String[]{
                    "§6科举试卷§r：右键开始答题，界面中选择 1/2/3，答对得功名。",
                    "§6Exam Paper§r: right-click to sit the exam and answer 1/2/3 in the GUI."};
            case "tiger_tally" -> new String[]{
                    "§6虎符§r：右键打开调兵界面（阵型+人数）；潜行右键可威慑周围生物。",
                    "§6Tiger Tally§r: right-click to summon troops; sneak-use to intimidate."};
            case "jade_seal" -> new String[]{
                    "§6玉玺§r：右键查看王朝档案；潜行右键获得赐福。",
                    "§6Jade Seal§r: right-click for dynasty records; sneak-use for a blessing."};
            case "official_seal" -> new String[]{
                    "§6官印§r：官职象征，科举与任务的奖励/材料。",
                    "§6Official Seal§r: proof of office, used in exams and quests."};
            case "edict" -> new String[]{
                    "§6圣旨§r：右键为周围友军赐下「龙威」。",
                    "§6Imperial Edict§r: right-click to grant Dragon's Might to allies."};
            case "dynasty_guide" -> new String[]{
                    "§6王朝图鉴§r：右键打开 12 页内置指南（开局、维度、神兽、Boss…）。",
                    "§6Dynasty Codex§r: right-click for the 12-page built-in guide."};
            case "festival_lantern" -> new String[]{
                    "§6节令灯§r：右键开启当令节日；非节令期会提示日期。",
                    "§6Festival Lantern§r: right-click to start today's festival."};
            case "dynasty_potion" -> new String[]{
                    "王朝药水（饮用）：龙威 攻击 +300 / 铁壁 护甲 +20 且减伤 30% / 疾风 速度 / 民心 生命 +100 / 天命 幸运 +20。",
                    "Dynasty potion: Dragon's Might +300 damage, Iron Wall +20 armor & -30% damage taken, Loyalty +100 health, Mandate +20 luck."};
            case "dynasty_splash_potion" -> new String[]{
                    "喷溅药水：右击投掷，为范围内单位附加王朝增益。",
                    "Splash potion: right-click to throw and apply the buff in an area."};
            case "dynasty_lingering_potion" -> new String[]{
                    "滞留药水：投掷后留下药云，持续时间更长。",
                    "Lingering potion: leaves a cloud with a longer duration."};
            case "talisman_paper" -> new String[]{"材料：与朱砂、火药等合成各类符箓（符箓一次性但很强）。",
                    "Material: craft the talismans with cinnabar and gunpowder (single use but strong)."};
            case "fire_talisman" -> new String[]{"§c火符§r：右键前方爆炎，4.5 格内 600+攻击×3 火焰伤害并点燃 8 秒。",
                    "§cFire Talisman§r: blazing blast, 600 + 3x attack fire damage in 4.5 blocks, ignites 8s."};
            case "thunder_talisman" -> new String[]{"§b雷符§r：右键三道落雷，5 格内 800+攻击×4 伤害 + 缓慢 II + 虚弱 II。",
                    "§bThunder Talisman§r: triple lightning, 800 + 4x attack in 5 blocks with Slowness II and Weakness II."};
            case "wind_talisman" -> new String[]{"§f御风符§r：8 格内敌人 200+攻击×2 并全部击飞；自身疾风 III + 缓降 45 秒。",
                    "§fWind Talisman§r: knocks up everything within 8 blocks for 200 + 2x attack; Speed III and slow falling for you."};
            case "stealth_talisman" -> new String[]{"§7隐身符§r：隐身 60 秒 + 速度 II + 夜视，并清除 16 格内怪物仇恨。",
                    "§7Stealth Talisman§r: 60s invisibility, Speed II, night vision, and drops all aggro within 16 blocks."};
            case "vajra_talisman" -> new String[]{"§6金刚符§r：抗性 III + 力量 II 15 秒、抗火 60 秒（不回血，纯硬吃）。",
                    "§6Vajra Talisman§r: Resistance III + Strength II for 15s, fire resistance 60s."};
            case "soul_talisman" -> new String[]{"§5摄魂符§r：6 格内 500+攻击×3 伤害，并施加失明 + 虚弱 II 8 秒。",
                    "§5Soul Talisman§r: 500 + 3x attack in 6 blocks with Blindness and Weakness II."};
            case "return_talisman" -> new String[]{"§d归乡符§r：传送回世界出生点，并净化所有负面效果。",
                    "§dReturn Talisman§r: teleport to world spawn and cleanse all debuffs."};
            case "cinnabar" -> new String[]{"材料：制符、炼丹与制作官印。",
                    "Material: talismans, pills and seals."};
            case "jade" -> new String[]{"材料：玉甲、玉剑、玉玺与建筑。",
                    "Material: jade gear, seals and building."};
            case "bronze_ingot" -> new String[]{"材料：青铜兵器、将军铠与礼器。",
                    "Material: bronze weapons and general armor."};
            case "silver_ingot" -> new String[]{"材料：官银兵器与礼器。",
                    "Material: silver weapons and regalia."};
            case "dragon_crystal" -> new String[]{"材料：顶级龙晶兵器与护甲（后期伤害 170 → 2048，名器还带特攻）。",
                    "Material: top-tier dragon crystal gear (170 -> 2048 damage, plus extra flat damage)."};
            case "dragon_scale" -> new String[]{"材料：龙鳞甲（减伤 96%）与进阶弓。",
                    "Material: dragon scale armour (96% reduction) and late bows."};
            case "blueprint" -> new String[]{"§6兵器图纸§r：青铜期以后每把武器/护甲升级都要一张。",
                    "§6Blueprint§r: every weapon and armour upgrade past iron needs one."};
            case "refined_steel" -> new String[]{"材料：铁锭×3 + 朱砂 → 精钢×2，进阶弓与镐要用。",
                    "Material: 3 iron + cinnabar -> 2 refined steel, used by late bows and pickaxes."};
            case "rebel_head" -> new String[]{"§c叛将首级§r：击败叛将掉落，打造破军战斧的必要条件。",
                    "§cRebel Head§r: dropped by the Rebel General, required for the Po Jun Axe."};
            case "eunuch_token" -> new String[]{"§5内廷令牌§r：击败宦官首脑掉落，龙晶剑/天子剑需要。",
                    "§5Palace Token§r: dropped by the Eunuch Mastermind, needed for the top swords."};
            case "emperor_bone" -> new String[]{"§5帝骸骨§r：击败不死始皇/龙帝掉落，方天画戟与玄天套要用。",
                    "§5Emperor's Bone§r: dropped by the Undead/Dragon Emperor, used by the halberd and Xuantian set."};
            case "dragon_emperor_seal" -> new String[]{"§4龙帝玉玺§r：击败龙帝掉落，终盘装备的唯一凭据。",
                    "§4Dragon Emperor's Seal§r: dropped by the Dragon Emperor, the endgame token."};
            case "xuantian_jade" -> new String[]{"材料：帝骸骨 + 玉×2 + 龙晶，用于玄天真龙甲。",
                    "Material: Emperor Bone + 2 jade + dragon crystal, upgrades armour to the Xuantian set."};
            case "heart_mirror" -> new String[]{"§d护心镜§r：护甲 +8、额外 4% 减伤。",
                    "§dHeart Mirror§r: +8 armour and 4% extra damage reduction."};
            case "jade_crown" -> new String[]{"§d玉冠§r：生命上限 +220。",
                    "§dJade Crown§r: +220 max health."};
            case "jade_cicada" -> new String[]{"§d玉蝉§r：生命低于 30% 时自动获得抗性 II + 速度（保命，不回血）。",
                    "§dJade Cicada§r: below 30% health you gain Resistance II and Speed."};
            case "dragon_pearl" -> new String[]{"§d龙珠§r：攻击力 +25%、抗击退 +0.3。",
                    "§dDragon Pearl§r: +25% attack damage, +0.3 knockback resistance."};
            case "phoenix_ring" -> new String[]{"§d凤凰指环§r：常驻抗火；着火立刻灭火并加速。",
                    "§dPhoenix Ring§r: permanent fire resistance; extinguishes you and grants Speed."};
            case "storm_charm" -> new String[]{"§d雷纹护符§r：常驻抗性 I；雷雨天额外获得力量 II + 速度。",
                    "§dStorm Charm§r: permanent Resistance I; Strength II and Speed during storms."};
            case "moon_pendant" -> new String[]{"§d明月佩§r：夜间获得夜视、幸运 +2、攻击 +10%。",
                    "§dMoon Pendant§r: at night: night vision, +2 luck, +10% attack."};
            case "tiger_crest" -> new String[]{"§d虎符残片§r：每 40 秒威慑 8 格内敌人，使其放弃追击。",
                    "§dTiger Crest§r: every 40s intimidates mobs within 8 blocks."};
            case "jade_tortoise" -> new String[]{"§d玉龟符§r：水下呼吸 + 海豚恩惠 + 抗性 I（水战/渡海）。",
                    "§dJade Tortoise§r: water breathing, dolphin's grace and Resistance I."};
            case "war_drum_charm" -> new String[]{"§d战鼓坠§r：自身力量 I，并每 3 秒给 12 格内禁军/铁傀儡/宠物加力量。",
                    "§dWar Drum§r: Strength I for you and for guards/golems/pets within 12 blocks."};
            case "cinnabar_pouch" -> new String[]{"§d朱砂囊§r：每 2 秒净化中毒 / 凋零 / 失明 / 饥饿。",
                    "§dCinnabar Pouch§r: cleanses poison, wither, blindness and hunger every 2s."};
            case "dragon_whisker" -> new String[]{"§d龙须穗§r：攻速 +15%、击退 +0.5。",
                    "§dDragon Whisker§r: +15% attack speed, +0.5 knockback."};
            case "tiger_token" -> new String[]{"§d虎头令§r：移速 +8% 且常驻跳跃提升。",
                    "§dTiger Token§r: +8% movement speed with a permanent jump boost."};
            case "sun_feather" -> new String[]{"§d金乌翎§r：白天攻击 +15%、幸运 +1；夜里改为抗性 I。",
                    "§dSun Feather§r: by day +15% attack and +1 luck; by night Resistance I."};
            case "war_horse_bell" -> new String[]{"§d战马铃§r：骑乘时坐骑获得速度 II + 抗性 I。",
                    "§dWar Horse Bell§r: while mounted your mount gains Speed II and Resistance I."};
            case "iron_waist_token" -> new String[]{"§d玄铁腰牌§r：护甲 +6、抗击退 +0.2、生命 +150。",
                    "§dIron Waist Token§r: +6 armour, +0.2 knockback resistance, +150 health."};
            case "auspicious_bell" -> new String[]{"§d瑞兽铃§r：幸运 +3（钓鱼 / 掉落 / 附魔）。",
                    "§dAuspicious Bell§r: +3 luck (fishing, drops, enchanting)."};
            case "ritual_altar" -> new String[]{"§6法阵·祭坛§r：四周放 4 块玉石块成形后，用 Boss 信物右键召唤对应 Boss。",
                    "§6Ritual Altar§r: surround it with 4 jade blocks, then right-click with a boss token to summon that boss."};
            case "phoenix_feather" -> new String[]{"材料：轻身与飞行相关合成。",
                    "Material: featherwork and flight gear."};
            case "qilin_horn" -> new String[]{"材料：祥瑞之物，用于高级合成。",
                    "Material: auspicious horn for high-tier crafting."};
            case "fox_tail" -> new String[]{"材料：魅惑之物，用于符箓与丹药。",
                    "Material: bewitching tail for charms and pills."};
            case "healing_salve" -> new String[]{"丹药：右键立刻回复大量生命。",
                    "Pill: right-click to heal a large amount."};
            case "pill_focus" -> new String[]{"丹药：右键获得专注（挖掘更快、命中更准）。",
                    "Pill: right-click for Focus."};
            case "pill_longevity" -> new String[]{"丹药：右键获得长寿（大幅提升最大生命）。",
                    "Pill: right-click for Longevity (big max health)."};
            case "immortal_peach" -> new String[]{"仙桃：食用回复并提升生命上限；麒麟最爱。",
                    "Immortal Peach: heals and boosts max health; Qilin's favourite."};
            case "mooncake" -> new String[]{"食物：中秋佳品，食用获得夜视与饱腹。",
                    "Food: Mid-Autumn treat, grants night vision."};
            case "dumpling" -> new String[]{"食物：节庆饺子，回复并短暂增益。",
                    "Food: festive dumplings with a small buff."};
            case "hotpot" -> new String[]{"食物：火锅，食用获得抗性与高饱食度。",
                    "Food: hotpot, grants resistance and fills you up."};
            case "tea" -> new String[]{"饮品：清香提神，短暂提升移动速度。",
                    "Drink: refreshing tea, briefly raises speed."};
            case "wine" -> new String[]{"饮品：豪饮获得力量，但会有些眩晕。",
                    "Drink: strength with a little dizziness."};
            case "candied_hawthorn" -> new String[]{"食物：糖葫芦，酸甜开胃并回血。",
                    "Food: candied hawthorn, heals a little."};
            case "dragon_beard_candy" -> new String[]{"食物：龙须糖，细丝千缕，提升幸运。",
                    "Food: dragon beard candy, grants luck."};
            case "zongzi" -> new String[]{"食物：竹叶糯米粽，回复饱腹。",
                    "Food: sticky rice in bamboo leaves."};
            case "tangyuan" -> new String[]{"食物：甜糯汤圆，附带生命恢复。",
                    "Food: sweet rice balls with regeneration."};
            case "niangao" -> new String[]{"食物：年糕，食用获得抗性提升。",
                    "Food: rice cake, grants resistance."};
            case "osmanthus_cake" -> new String[]{"食物：桂花糕，食用获得幸运。",
                    "Food: osmanthus cake, grants luck."};
            case "cured_meat" -> new String[]{"食物：腊肉，饱食度高。",
                    "Food: cured meat, very filling."};
            case "roast_duck" -> new String[]{"食物：烤鸭，顶级饱食度。",
                    "Food: roast duck, the most filling dish."};
            case "longevity_noodles" -> new String[]{"食物：长寿面，食用大幅提升最大生命。",
                    "Food: longevity noodles, big max-health boost."};
            case "baijiu" -> new String[]{"饮品：白酒，力量提升但会眩晕。",
                    "Drink: baijiu, strength with nausea."};
            case "raw_silk" -> new String[]{"材料：由线合成，再织成丝绸。",
                    "Material: made from string, woven into silk."};
            case "silk" -> new String[]{"材料：手札、毛笔与锦衣的用料。",
                    "Material: ledgers, brushes and robes."};
            case "brocade" -> new String[]{"材料：高级装饰与礼服用料（交易佳品）。",
                    "Material: ornamental fabric for regalia and trade."};
            case "bamboo_slip" -> new String[]{"材料：书简，用于制作王朝手札。",
                    "Material: bamboo slips for the quest ledger."};
            case "ink_stick" -> new String[]{"材料：制符与书写。",
                    "Material: talismans and writing."};
            case "ink_brush" -> new String[]{"工具：书写与制符（有耐久）。",
                    "Tool: writing and talisman work (has durability)."};
            case "bronze_mirror" -> new String[]{"器物：铜镜，可作装饰与礼物。",
                    "Curio: bronze mirror for decor and gifts."};
            case "roof_tile" -> new String[]{"材料：琉璃瓦，用于宫殿屋顶。",
                    "Material: glazed roof tiles for palaces."};
            default -> null;
        };
    }
}
