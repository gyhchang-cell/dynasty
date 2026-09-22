package com.dynasty.bounty;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Random;

/**
 * 委托规则（纯逻辑）：日界、每日发布的**决定论抽取**、定义校验、背包空间与击杀归属判定。
 *
 * 决定论要求：同一世界同一天、任何玩家、任何重启，都得到同一组 6 条 → 用「按 id 排序 + 以日数为种子」
 * 的加权抽取，不依赖 HashMap 迭代顺序，也不依赖运行时随机。
 */
public final class BountyRules {

    private BountyRules() {
    }

    /** 每游戏日发布的委托条数 / offers published per in-game day */
    public static final int DAILY_PUBLISH = 6;
    /** 主世界一天的 tick 数 / ticks per day */
    public static final long TICKS_PER_DAY = 24000L;

    public static long dayOf(long gameTime) {
        return Math.floorDiv(gameTime, TICKS_PER_DAY);
    }

    /**
     * 决定论加权抽取（不放回）。同样的 (pool, count, day) 永远得到同样的顺序与集合。
     */
    public static List<BountyModel.Offer> pickDaily(List<BountyModel.Offer> pool, int count, long day) {
        List<BountyModel.Offer> candidates = new ArrayList<>(pool);
        candidates.sort(Comparator.comparing(offer -> offer.id));
        Random random = new Random(day * 0x9E3779B97F4A7C15L + 0x5DEECE66DL);
        List<BountyModel.Offer> picked = new ArrayList<>();
        while (picked.size() < count && !candidates.isEmpty()) {
            int total = 0;
            for (BountyModel.Offer offer : candidates) {
                total += Math.max(1, offer.weight);
            }
            int roll = random.nextInt(total);
            int index = 0;
            while (index < candidates.size() - 1 && roll >= Math.max(1, candidates.get(index).weight)) {
                roll -= Math.max(1, candidates.get(index).weight);
                index++;
            }
            picked.add(candidates.remove(index));
        }
        return picked;
    }

    /**
     * 校验一条定义；返回错误说明（null = 合法）。加载时用，坏定义只跳过自己不炸服。
     */
    public static String validate(BountyModel.Offer offer) {
        if (offer.id == null || offer.id.isBlank()) {
            return "缺少 id";
        }
        if (offer.type == null) {
            return "type 必须是 acquire / hunt / explore 之一";
        }
        if (offer.titleKey == null || !offer.titleKey.startsWith("dynasty.bounty.")) {
            return "titleKey 必须以 dynasty.bounty. 开头（翻译键）";
        }
        if (offer.descKey == null || !offer.descKey.startsWith("dynasty.bounty.")) {
            return "descKey 必须以 dynasty.bounty. 开头（翻译键）";
        }
        if (offer.targetKind == null || offer.target == null || offer.target.isBlank()) {
            return "缺少 target（物品 / 实体 / 维度 ID）";
        }
        if (offer.type == BountyModel.Type.EXPLORE && offer.targetKind != BountyModel.TargetKind.DIMENSION) {
            return "考察委托的 targetKind 必须是 dimension";
        }
        if (offer.type == BountyModel.Type.HUNT && offer.targetKind != BountyModel.TargetKind.ENTITY) {
            return "讨伐委托的 targetKind 必须是 entity";
        }
        if (offer.type == BountyModel.Type.ACQUIRE && offer.targetKind != BountyModel.TargetKind.ITEM) {
            return "收购委托的 targetKind 必须是 item";
        }
        if (offer.amount <= 0 || offer.amount > 512) {
            return "amount 必须在 1..512（当前 " + offer.amount + "）";
        }
        if (offer.weight <= 0 || offer.weight > 100) {
            return "weight 必须在 1..100（当前 " + offer.weight + "）";
        }
        if (offer.reward == null) {
            return "缺少 reward";
        }
        if (offer.reward.emeralds < 0 || offer.reward.emeralds > 16) {
            return "绿宝石奖励必须 0..16（当前 " + offer.reward.emeralds + "）";
        }
        if (offer.reward.experience < 0 || offer.reward.experience > 30) {
            return "经验奖励必须 0..30（当前 " + offer.reward.experience + "）";
        }
        if (offer.reward.emeralds == 0 && offer.reward.supplies.isEmpty() && offer.reward.experience == 0) {
            return "奖励不能为空";
        }
        for (BountyModel.Stack stack : offer.reward.supplies) {
            if (stack.item == null || !stack.item.contains(":")) {
                return "补给物品 ID 非法：" + stack.item;
            }
            if (stack.count <= 0 || stack.count > 32) {
                return "补给数量必须 1..32（当前 " + stack.count + "）";
            }
            if (isForbiddenReward(stack.item)) {
                return "禁止把 " + stack.item + " 作为委托奖励（Boss 信物 / 毕业装备 / 永久属性）";
            }
        }
        return null;
    }

    /** 不允许出现在奖励里的东西：Boss 信物、终盘装备、饰品槽 / forbidden reward items */
    public static boolean isForbiddenReward(String itemId) {
        if (itemId == null) {
            return false;
        }
        if (itemId.endsWith("_token") || itemId.contains("seal") || itemId.equals("dynasty:rebel_head")
                || itemId.equals("dynasty:emperor_bone") || itemId.equals("dynasty:xuantian_jade")) {
            return true;
        }
        return itemId.contains("supreme_sword") || itemId.contains("tianzi_sword")
                || itemId.contains("halberd_fangtian") || itemId.contains("dragon_slayer")
                || itemId.contains("unlock_curio") || itemId.contains("accessory_slot");
    }

    /** 背包能否容纳奖励（每种物品需要一个空位，或已有同类堆叠）。 */
    public static boolean rewardFits(int emptySlots, int distinctStacks) {
        return emptySlots >= distinctStacks;
    }
}
