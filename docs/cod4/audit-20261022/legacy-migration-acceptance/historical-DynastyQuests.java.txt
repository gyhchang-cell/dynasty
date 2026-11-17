package com.dynasty;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

import java.util.ArrayList;
import java.util.List;

/**
 * 王朝任务数据：章节 → 任务（目标 / 奖励 / 前置）。
 * Dynasty quest data: chapters -> quests (objective / rewards / prerequisites).
 * 目标类型：ITEM 收集、KILL 击杀、EVENT 自定义事件（科举 / 列阵 / 拜访等）。
 */
public final class DynastyQuests {

    private DynastyQuests() {
    }

    public enum Type { ITEM, KILL, EVENT }

    public static final class Quest {
        public final int index;
        public final String chapter;
        public final String title;
        public final String desc;
        public final Type type;
        public final String target;
        public final int need;
        public final int[] requires;
        private ItemStack[] rewards;

        Quest(int index, String chapter, String title, String desc, Type type, String target,
              int need, int[] requires) {
            this.index = index;
            this.chapter = chapter;
            this.title = title;
            this.desc = desc;
            this.type = type;
            this.target = target;
            this.need = need;
            this.requires = requires;
        }

        public ItemStack[] rewards() {
            if (rewards == null) {
                rewards = DynastyQuestRewards.build(index);
            }
            ItemStack[] copy = new ItemStack[rewards.length];
            for (int i = 0; i < rewards.length; i++) {
                copy[i] = rewards[i].copy();
            }
            return copy;
        }

        public Item icon() {
            if (type == Type.ITEM) {
                Item item = net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(new ResourceLocation(target));
                return item == null ? Items.PAPER : item;
            }
            if (type == Type.KILL) {
                return Items.IRON_SWORD;
            }
            ItemStack[] r = rewards();
            return r.length > 0 ? r[0].getItem() : Items.NETHER_STAR;
        }
    }

    public static final String[] CHAPTERS = {
            "一、初入王朝", "二、朝堂之路", "三、军旅生涯", "四、天朝·龙庭", "五、地府幽冥", "六、神兽与帝王"
    };

    private static List<Quest> quests;

    public static List<Quest> all() {
        if (quests == null) {
            quests = build();
        }
        return quests;
    }

    public static Quest get(int index) {
        List<Quest> list = all();
        return index >= 0 && index < list.size() ? list.get(index) : null;
    }

    public static int count() {
        return all().size();
    }

    private static List<Quest> build() {
        List<Quest> q = new ArrayList<>();
        q.add(new Quest(0, CHAPTERS[0], "玉石在手", "挖掘玉矿，收集 4 块玉。", Type.ITEM, "dynasty:jade", 4, new int[]{}));
        q.add(new Quest(1, CHAPTERS[0], "第一桶金", "收集 8 枚铜钱。", Type.ITEM, "dynasty:copper_coin", 8, new int[]{0}));
        q.add(new Quest(2, CHAPTERS[0], "熔铸青铜", "收集 4 块青铜锭。", Type.ITEM, "dynasty:bronze_ingot", 4, new int[]{0}));
        q.add(new Quest(3, CHAPTERS[0], "铸剑为凭", "打造一把青铜剑。", Type.ITEM, "dynasty:sword_bronze", 1, new int[]{2}));
        q.add(new Quest(4, CHAPTERS[0], "造纸制符", "制作 2 张符纸。", Type.ITEM, "dynasty:talisman_paper", 2, new int[]{0}));

        q.add(new Quest(5, CHAPTERS[1], "科举中第", "用科举试卷答题并答对。", Type.EVENT, "keju", 1, new int[]{4}));
        q.add(new Quest(6, CHAPTERS[1], "官阶初授", "功名累积晋升为秀才。", Type.EVENT, "rank1", 1, new int[]{5}));
        q.add(new Quest(7, CHAPTERS[1], "拜见大臣", "找到大臣并与之交谈。", Type.EVENT, "minister", 1, new int[]{5}));
        q.add(new Quest(8, CHAPTERS[1], "玉玺在手", "制作或获得一枚玉玺。", Type.ITEM, "dynasty:jade_seal", 1, new int[]{6}));

        q.add(new Quest(9, CHAPTERS[2], "虎符调兵", "用虎符列阵，召集至少 8 名禁军。", Type.EVENT, "army", 1, new int[]{7}));
        q.add(new Quest(10, CHAPTERS[2], "龙鳞披甲", "获得一件龙鳞胸甲。", Type.ITEM, "dynasty:dragon_scale_chestplate", 1, new int[]{9}));
        q.add(new Quest(11, CHAPTERS[2], "讨伐叛军", "斩杀 10 名叛军。", Type.KILL, "dynasty:rebel_soldier", 10, new int[]{9}));
        q.add(new Quest(12, CHAPTERS[2], "安抚民心", "把叛乱值降到 20 以下。", Type.EVENT, "calm", 1, new int[]{11}));

        q.add(new Quest(13, CHAPTERS[3], "踏入天朝", "穿过玉门，进入天朝·龙庭。", Type.EVENT, "dim_celestial", 1, new int[]{8}));
        q.add(new Quest(14, CHAPTERS[3], "龙晶之美", "在天朝采集 4 颗龙晶。", Type.ITEM, "dynasty:dragon_crystal", 4, new int[]{13}));
        q.add(new Quest(15, CHAPTERS[3], "龙晶神兵", "打造一把龙晶剑。", Type.ITEM, "dynasty:sword_dragon_crystal", 1, new int[]{14}));
        q.add(new Quest(16, CHAPTERS[3], "营造宫室", "收集 16 块宫殿砖。", Type.ITEM, "dynasty:palace_bricks", 16, new int[]{13}));

        q.add(new Quest(17, CHAPTERS[4], "下探地府", "穿过冥门，进入地府。", Type.EVENT, "dim_underworld", 1, new int[]{15}));
        q.add(new Quest(18, CHAPTERS[4], "幽冥斩妖", "斩杀 4 只九尾狐。", Type.KILL, "dynasty:nine_tailed_fox", 4, new int[]{17}));
        q.add(new Quest(19, CHAPTERS[4], "帝陵取宝", "寻得 4 枚龙钱。", Type.ITEM, "dynasty:dragon_coin", 4, new int[]{17}));

        q.add(new Quest(20, CHAPTERS[5], "祥瑞麒麟", "以仙桃结交麒麟。", Type.EVENT, "qilin", 1, new int[]{16}));
        q.add(new Quest(21, CHAPTERS[5], "凤羽在手", "获得一根凤凰羽。", Type.ITEM, "dynasty:phoenix_feather", 1, new int[]{18}));
        q.add(new Quest(22, CHAPTERS[5], "龙帝陨落", "在天朝击败龙帝。", Type.KILL, "dynasty:dragon_emperor", 1, new int[]{20}));
        q.add(new Quest(23, CHAPTERS[5], "天下共主", "晋升至大学士。", Type.EVENT, "rank9", 1, new int[]{22}));
        return q;
    }
}
