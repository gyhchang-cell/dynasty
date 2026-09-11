package com.dynasty.client;

/** 重点物品的用法文案表 / usage text for key items. */
public final class DynastyItemUsage {

    private DynastyItemUsage() {
    }

    public static String[] special(String path) {
        return switch (path) {
            case "quest_ledger" -> new String[]{
                    "§6任务书§r：右键打开王朝任务界面；也可在背包左上角点「✦ 王朝任务」。",
                    "§6Quest Ledger§r: right-click for the quest screen (or the inventory button)."};
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
            case "talisman_paper" -> new String[]{"材料：与朱砂等合成各类符箓。",
                    "Material: craft talismans with cinnabar."};
            case "cinnabar" -> new String[]{"材料：制符、炼丹与制作官印。",
                    "Material: talismans, pills and seals."};
            case "jade" -> new String[]{"材料：玉甲、玉剑、玉玺与建筑。",
                    "Material: jade gear, seals and building."};
            case "bronze_ingot" -> new String[]{"材料：青铜兵器、将军铠与礼器。",
                    "Material: bronze weapons and general armor."};
            case "silver_ingot" -> new String[]{"材料：官银兵器与礼器。",
                    "Material: silver weapons and regalia."};
            case "dragon_crystal" -> new String[]{"材料：顶级龙晶兵器与护甲（攻击 1900-2048）。",
                    "Material: top-tier dragon crystal gear (1900-2048 damage)."};
            case "dragon_scale" -> new String[]{"材料：龙鳞甲（减伤 80%）与箭矢。",
                    "Material: dragon scale armor (80% reduction)."};
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
