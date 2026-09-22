package com.dynasty.bounty;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * 单人委托状态机（纯逻辑，可单元测试）。
 *
 * 负责：每日发布的水位与快照、最多 3 个已接委托、讨伐/考察进度、提交与领奖的**原子判定**、
 * 已领记录（防重复领奖）、以及存档用的行格式序列化。
 *
 * 关键设计（对应防刷条款）：
 *   * **只增不减的日水位**：{@code lastDay} 只升不降 → 时间倒退时不会重新发布旧日期的实例；
 *   * **发布实例 ID 决定论**：同一天同一槽位 → 同一个 instanceId，重启/重载后一致；
 *   * **已领集合按天保存**（保留最近 {@link #KEEP_DAYS} 天）：旧日期不再重发，清理不会恢复领奖机会；
 *   * **提交是「先算后扣」**：数量不足返回 INSUFFICIENT 且消耗量为 0，调用方不扣任何物品；
 *   * **领奖需要背包空间**：空间不足时保持可领取状态，不把奖励丢地上。
 */
public final class BountyStateMachine {

    public static final int MAX_ACTIVE = 3;
    /** 保留最近多少天的已领记录 / how many days of claim history to keep */
    public static final int KEEP_DAYS = 16;
    /** 存档行格式版本 / persistence format tag */
    public static final String FORMAT = "bounty-v1";

    public enum Accept { OK, FULL, ALREADY_ACCEPTED, ALREADY_CLAIMED, NOT_PUBLISHED }

    public enum Submit { OK, NOT_ACCEPTED, WRONG_TYPE, INSUFFICIENT, ALREADY_DONE, ALREADY_CLAIMED }

    public enum Claim { OK, NOT_ACCEPTED, NOT_DONE, NO_SPACE, ALREADY_CLAIMED }

    /** 一个已接委托（含快照与进度）/ an accepted offer with snapshot + progress */
    public static final class Accepted {
        public final BountyModel.Instance instance;
        public int progress;
        public boolean done;
        /** 收购委托：是否已经交过（交过即 done，同一实例不能重复交）*/
        public boolean submitted;

        Accepted(BountyModel.Instance instance) {
            this.instance = instance;
        }

        public int amount() {
            return instance.amount;
        }
    }

    private long lastDay = Long.MIN_VALUE;
    private long publicationDay = Long.MIN_VALUE;
    /** 一次性待消耗量：只由「刚刚成功的这一次 submit」设置，读取后清零 */
    private int pendingConsume;
    private final List<BountyModel.Instance> published = new ArrayList<>();
    private final Map<String, Accepted> accepted = new LinkedHashMap<>();
    private final Map<Long, Set<String>> claimed = new LinkedHashMap<>();

    // ------------------------------------------------------------------ 发布

    /** 时间倒退保护：有效日 = max(真实日, 已见最高日)。 */
    public long effectiveDay(long currentDay) {
        return Math.max(currentDay, lastDay);
    }

    public boolean needsPublication(long effectiveDay) {
        return effectiveDay > publicationDay;
    }

    /** 发布今天的委托列表（只允许向前推进；倒退时保持不变）。 */
    public void publish(long effectiveDay, List<BountyModel.Instance> instances) {
        if (effectiveDay <= publicationDay) {
            return;
        }
        publicationDay = effectiveDay;
        lastDay = Math.max(lastDay, effectiveDay);
        published.clear();
        published.addAll(instances);
    }

    public long publicationDay() {
        return publicationDay;
    }

    public long lastDay() {
        return lastDay;
    }

    public List<BountyModel.Instance> published() {
        return List.copyOf(published);
    }

    public BountyModel.Instance publishedById(String instanceId) {
        for (BountyModel.Instance instance : published) {
            if (instance.instanceId().equals(instanceId)) {
                return instance;
            }
        }
        return null;
    }

    public Map<String, Accepted> accepted() {
        return accepted;
    }

    public Accepted acceptedById(String instanceId) {
        return accepted.get(instanceId);
    }

    // ------------------------------------------------------------------ 接取 / 放弃

    public Accept accept(BountyModel.Instance instance) {
        if (publishedById(instance.instanceId()) == null) {
            return Accept.NOT_PUBLISHED;
        }
        if (accepted.containsKey(instance.instanceId())) {
            return Accept.ALREADY_ACCEPTED;
        }
        if (isClaimed(instance.instanceId())) {
            return Accept.ALREADY_CLAIMED;
        }
        if (accepted.size() >= MAX_ACTIVE) {
            return Accept.FULL;
        }
        accepted.put(instance.instanceId(), new Accepted(instance));
        return Accept.OK;
    }

    /** 放弃：只移除这条记录（进度丢弃），不发奖励，已领记录不动。 */
    public boolean abandon(String instanceId) {
        Accepted removed = accepted.remove(instanceId);
        return removed != null;
    }

    // ------------------------------------------------------------------ 讨伐 / 考察

    /** 接取后击杀才计数；实体 ID 必须与快照一致。返回被推进的委托条数。 */
    public int addHuntProgress(String entityId, int amount) {
        int touched = 0;
        for (Accepted record : accepted.values()) {
            if (record.instance.type != BountyModel.Type.HUNT || record.done
                    || !record.instance.target.equals(entityId)) {
                continue;
            }
            record.progress = Math.min(record.amount(), record.progress + amount);
            if (record.progress >= record.amount()) {
                record.done = true;
            }
            touched++;
        }
        return touched;
    }

    /** 进入指定维度后完成考察委托；维度 ID 必须与快照一致。 */
    public int markExplore(String dimensionId) {
        int touched = 0;
        for (Accepted record : accepted.values()) {
            if (record.instance.type != BountyModel.Type.EXPLORE || record.done
                    || !record.instance.target.equals(dimensionId)) {
                continue;
            }
            record.progress = record.amount();
            record.done = true;
            touched++;
        }
        return touched;
    }

    // ------------------------------------------------------------------ 收购提交

    /**
     * 收购提交：**先判定再消耗**。可用数量不足 → {@code INSUFFICIENT}，消耗量保持 0，
     * 调用方据此不扣任何物品（不会出现「扣一半再失败」）。
     */
    public Submit submit(String instanceId, int available) {
        Accepted record = accepted.get(instanceId);
        if (record == null) {
            return isClaimed(instanceId) ? Submit.ALREADY_CLAIMED : Submit.NOT_ACCEPTED;
        }
        if (record.instance.type != BountyModel.Type.ACQUIRE) {
            return Submit.WRONG_TYPE;
        }
        if (isClaimed(instanceId)) {
            return Submit.ALREADY_CLAIMED;
        }
        if (record.submitted && record.done) {
            return Submit.ALREADY_DONE;
        }
        if (available < record.amount()) {
            return Submit.INSUFFICIENT;
        }
        record.submitted = true;
        record.progress = record.amount();
        record.done = true;
        pendingConsume = record.amount();
        return Submit.OK;
    }

    /**
     * 本次**刚刚成功的提交**应消耗的数量；读取后清零（重复提交/失败时恒为 0，
     * 所以「重复点击提交」永远不会再扣材料）。
     */
    public int consumedOnSubmit(String instanceId) {
        int amount = pendingConsume;
        pendingConsume = 0;
        return amount;
    }

    // ------------------------------------------------------------------ 领奖

    /** 完成 + 未领过 + 背包有空间才成立；空间不足 → {@code NO_SPACE}，委托保持可领取。 */
    public Claim claim(String instanceId, boolean hasSpace) {
        Accepted record = accepted.get(instanceId);
        if (record == null) {
            return isClaimed(instanceId) ? Claim.ALREADY_CLAIMED : Claim.NOT_ACCEPTED;
        }
        if (isClaimed(instanceId)) {
            return Claim.ALREADY_CLAIMED;
        }
        if (!record.done) {
            return Claim.NOT_DONE;
        }
        if (!hasSpace) {
            return Claim.NO_SPACE;
        }
        claimDay(record.instance.day).add(instanceId);
        accepted.remove(instanceId);
        prune();
        return Claim.OK;
    }

    public boolean isClaimed(String instanceId) {
        for (Set<String> ids : claimed.values()) {
            if (ids.contains(instanceId)) {
                return true;
            }
        }
        return false;
    }

    public Set<String> claimedOnDay(long day) {
        return claimed.getOrDefault(day, Set.of());
    }

    private Set<String> claimDay(long day) {
        return claimed.computeIfAbsent(day, key -> new LinkedHashSet<>());
    }

    /** 只保留最近 {@link #KEEP_DAYS} 天。旧日期在日水位之后不会重发，所以清理是安全的。 */
    private void prune() {
        List<Long> days = new ArrayList<>(claimed.keySet());
        days.sort(Long::compareTo);
        while (days.size() > KEEP_DAYS) {
            claimed.remove(days.remove(0));
        }
    }

    // ------------------------------------------------------------------ 存档（行格式，纯文本，可单元测试）

    public List<String> toLines() {
        List<String> lines = new ArrayList<>();
        lines.add(FORMAT + "|" + lastDay + "|" + publicationDay);
        for (BountyModel.Instance instance : published) {
            lines.add("PUB|" + instance.day + "|" + instance.slot + "|" + instance.offer.id + "|"
                    + instance.type + "|" + instance.targetKind + "|" + instance.target + "|"
                    + instance.amount + "|" + encodeReward(instance.reward));
        }
        for (Accepted record : accepted.values()) {
            lines.add("ACC|" + record.instance.instanceId() + "|" + record.instance.day + "|"
                    + record.instance.slot + "|" + record.instance.offer.id + "|"
                    + record.instance.type + "|" + record.instance.targetKind + "|"
                    + record.instance.target + "|" + record.instance.amount + "|"
                    + encodeReward(record.instance.reward) + "|" + record.progress + "|"
                    + record.done + "|" + record.submitted);
        }
        for (Map.Entry<Long, Set<String>> entry : claimed.entrySet()) {
            for (String id : entry.getValue()) {
                lines.add("CLM|" + entry.getKey() + "|" + id);
            }
        }
        return lines;
    }

    private static String encodeReward(BountyModel.Reward reward) {
        StringBuilder builder = new StringBuilder();
        builder.append(reward.emeralds).append(":").append(reward.experience);
        for (BountyModel.Stack stack : reward.supplies) {
            builder.append(":").append(stack.item).append("=").append(stack.count);
        }
        return builder.toString();
    }

    private static BountyModel.Reward decodeReward(String text) {
        String[] parts = text.split(":");
        int emeralds = parts.length > 0 ? parseInt(parts[0], 0) : 0;
        int xp = parts.length > 1 ? parseInt(parts[1], 0) : 0;
        List<BountyModel.Stack> supplies = new ArrayList<>();
        for (int i = 2; i < parts.length; i++) {
            String[] pair = parts[i].split("=");
            if (pair.length == 2) {
                supplies.add(new BountyModel.Stack(pair[0], parseInt(pair[1], 1)));
            }
        }
        return new BountyModel.Reward(emeralds, xp, supplies);
    }

    private static int parseInt(String text, int fallback) {
        try {
            return Integer.parseInt(text.trim());
        } catch (NumberFormatException ignored) {
            return fallback;
        }
    }

    /** 从存档行恢复（坏行跳过，不影响服务器启动）。 */
    public static BountyStateMachine fromLines(List<String> lines) {
        BountyStateMachine state = new BountyStateMachine();
        for (String line : lines) {
            String[] parts = line.split("\\|");
            try {
                if (parts[0].startsWith("bounty-v") && parts.length >= 3) {
                    state.lastDay = Long.parseLong(parts[1]);
                    state.publicationDay = Long.parseLong(parts[2]);
                } else if (parts[0].equals("PUB") && parts.length >= 9) {
                    state.published.add(new BountyModel.Instance(Long.parseLong(parts[1]),
                            Integer.parseInt(parts[2]), offerOf(parts[3], parts[4], parts[5], parts[6],
                            Integer.parseInt(parts[7])), decodeReward(parts[8])));
                } else if (parts[0].equals("ACC") && parts.length >= 13) {
                    BountyModel.Instance instance = new BountyModel.Instance(Long.parseLong(parts[2]),
                            Integer.parseInt(parts[3]), offerOf(parts[4], parts[5], parts[6], parts[7],
                            Integer.parseInt(parts[8])), decodeReward(parts[9]));
                    Accepted record = new Accepted(instance);
                    record.progress = Integer.parseInt(parts[10]);
                    record.done = Boolean.parseBoolean(parts[11]);
                    record.submitted = Boolean.parseBoolean(parts[12]);
                    state.accepted.put(parts[1], record);
                } else if (parts[0].equals("CLM") && parts.length >= 3) {
                    state.claimDay(Long.parseLong(parts[1])).add(parts[2]);
                }
            } catch (RuntimeException ignored) {
                // 坏行跳过：一条坏记录不会让服务器起不来
            }
        }
        return state;
    }

    private static BountyModel.Offer offerOf(String id, String type, String targetKind,
                                             String target, int amount) {
        return new BountyModel.Offer(id, BountyModel.Type.valueOf(type), "", "",
                BountyModel.TargetKind.valueOf(targetKind), target, amount, 0, null,
                new BountyModel.Reward(0, 0, List.of()));
    }
}
