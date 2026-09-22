package com.dynasty.bounty;

import java.util.ArrayList;
import java.util.List;

/**
 * 服务端 → 客户端的界面数据（只含字符串/数字，客户端不参与任何判定）。
 * Server -> client view data. The client only renders it.
 */
public final class BountyView {

    /** 条目状态（客户端只用来显示不同按钮） */
    public enum State { AVAILABLE, ACCEPTED, READY, CLAIMED, LOCKED }

    public static final class Entry {
        public final String instanceId;
        public final String titleKey;
        public final String descKey;
        public final BountyModel.Type type;
        public final String targetKey;
        public final int amount;
        public final int progress;
        public final State state;
        public final int emeralds;
        public final int experience;
        public final List<BountyModel.Stack> supplies;

        public Entry(String instanceId, String titleKey, String descKey, BountyModel.Type type,
                     String targetKey, int amount, int progress, State state,
                     int emeralds, int experience, List<BountyModel.Stack> supplies) {
            this.instanceId = instanceId;
            this.titleKey = titleKey;
            this.descKey = descKey;
            this.type = type;
            this.targetKey = targetKey;
            this.amount = amount;
            this.progress = progress;
            this.state = state;
            this.emeralds = emeralds;
            this.experience = experience;
            this.supplies = List.copyOf(supplies);
        }

        public List<BountyModel.Stack> rewardItems() {
            List<BountyModel.Stack> out = new ArrayList<>();
            if (emeralds > 0) {
                out.add(new BountyModel.Stack("minecraft:emerald", emeralds));
            }
            out.addAll(supplies);
            return out;
        }
    }

    public final long day;
    public final int activeCount;
    public final int maxActive;
    public final String statusKey;
    public final List<Entry> entries;

    public BountyView(long day, int activeCount, int maxActive, String statusKey, List<Entry> entries) {
        this.day = day;
        this.activeCount = activeCount;
        this.maxActive = maxActive;
        this.statusKey = statusKey;
        this.entries = List.copyOf(entries);
    }
}
