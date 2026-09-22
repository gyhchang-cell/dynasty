package com.dynasty.bounty;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * 悬赏委托的**纯数据模型**（不引用任何 Minecraft 类，便于用 javac 直接跑单元测试）。
 *
 * Pure data model for the bounty board: no Minecraft imports, so the state machine and
 * rules can be unit-tested with plain javac/java (see tools/bounty/BountyRulesTest.java).
 */
public final class BountyModel {

    private BountyModel() {
    }

    /** 委托类型 / offer type */
    public enum Type {
        /** 收购：交物品 */
        ACQUIRE,
        /** 讨伐：接取后击杀指定生物 */
        HUNT,
        /** 考察：接取后亲自进入指定维度 */
        EXPLORE;

        public static Type byName(String name) {
            for (Type type : values()) {
                if (type.name().equalsIgnoreCase(name)) {
                    return type;
                }
            }
            return null;
        }
    }

    /** 目标种类 / what the target id refers to */
    public enum TargetKind {
        ITEM, ENTITY, DIMENSION;

        public static TargetKind byName(String name) {
            for (TargetKind kind : values()) {
                if (kind.name().equalsIgnoreCase(name)) {
                    return kind;
                }
            }
            return null;
        }
    }

    /** 奖励里的一叠物品 / one item stack inside a reward */
    public static final class Stack {
        public final String item;
        public final int count;

        public Stack(String item, int count) {
            this.item = item;
            this.count = count;
        }

        @Override
        public String toString() {
            return item + " x" + count;
        }
    }

    /** 奖励：绿宝石 + 少量经验 + 普通补给 / rewards: emeralds, small xp, ordinary supplies */
    public static final class Reward {
        public final int emeralds;
        public final int experience;
        public final List<Stack> supplies;

        public Reward(int emeralds, int experience, List<Stack> supplies) {
            this.emeralds = emeralds;
            this.experience = experience;
            this.supplies = Collections.unmodifiableList(new ArrayList<>(supplies));
        }

        public List<Stack> allItems() {
            List<Stack> out = new ArrayList<>();
            if (emeralds > 0) {
                out.add(new Stack("minecraft:emerald", emeralds));
            }
            out.addAll(supplies);
            return out;
        }

        @Override
        public String toString() {
            return "emeralds=" + emeralds + " xp=" + experience + " supplies=" + supplies;
        }
    }

    /** 一条委托定义（来自数据包 JSON）/ one offer definition loaded from a datapack */
    public static final class Offer {
        public final String id;
        public final Type type;
        public final String titleKey;
        public final String descKey;
        public final TargetKind targetKind;
        public final String target;
        public final int amount;
        public final int weight;
        public final String prerequisite;
        public final Reward reward;

        public Offer(String id, Type type, String titleKey, String descKey, TargetKind targetKind,
                     String target, int amount, int weight, String prerequisite, Reward reward) {
            this.id = id;
            this.type = type;
            this.titleKey = titleKey;
            this.descKey = descKey;
            this.targetKind = targetKind;
            this.target = target;
            this.amount = amount;
            this.weight = weight;
            this.prerequisite = prerequisite;
            this.reward = reward == null ? new Reward(0, 0, List.of()) : reward;
        }

        @Override
        public String toString() {
            return id + "[" + type + " " + target + " x" + amount + " w" + weight + "]";
        }
    }

    /**
     * 一个**发布实例**：某一天发布的第 slot 条委托，带接取时的目标与奖励快照。
     * 实例 ID 只由「日 + 委托 ID + 槽位」决定 → 同一天重启/重载后完全一致，
     * 因此「每个发布实例每名玩家最多领奖一次」可以靠实例 ID 记住。
     */
    public static final class Instance {
        public final long day;
        public final int slot;
        public final Offer offer;
        /** 快照（数据包重载不会改变已接取委托的目标/奖励）*/
        public final Type type;
        public final TargetKind targetKind;
        public final String target;
        public final int amount;
        public final Reward reward;

        public Instance(long day, int slot, Offer offer, Reward reward) {
            this.day = day;
            this.slot = slot;
            this.offer = offer;
            this.type = offer.type;
            this.targetKind = offer.targetKind;
            this.target = offer.target;
            this.amount = offer.amount;
            this.reward = reward;
        }

        public String instanceId() {
            return day + ":" + slot + ":" + offer.id;
        }

        public String titleKey() {
            return offer.titleKey;
        }

        public String descKey() {
            return offer.descKey;
        }

        @Override
        public String toString() {
            return instanceId() + " target=" + target + " x" + amount;
        }
    }
}
