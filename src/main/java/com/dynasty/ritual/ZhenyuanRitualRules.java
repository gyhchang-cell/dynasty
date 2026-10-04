package com.dynasty.ritual;

/** Pure, deterministic rules, shared by the server and regression tests. */
public final class ZhenyuanRitualRules {
    public static final int ALL = 31;
    public static final int CHARGE_TICKS = 100;
    public static final String[] OFFERINGS = {
            "qinglong_scale", "baihu_fang", "zhuque_feather", "xuanwu_shell", "hunyuan_pearl"
    };
    public static final String[] NAMES = {"东·青龙鳞", "西·白虎牙", "南·朱雀羽", "北·玄武壳", "中央·混元珠"};
    private ZhenyuanRitualRules() {}

    public enum OfferResult { ACCEPTED, INVALID_SLOT, WRONG_ITEM, ALREADY_OFFERED, FOUR_SIGILS_REQUIRED }

    public static OfferResult offer(int mask, int slot, String item) {
        if (slot < 0 || slot >= OFFERINGS.length) return OfferResult.INVALID_SLOT;
        if ((mask & (1 << slot)) != 0) return OfferResult.ALREADY_OFFERED;
        if (slot == 4 && (mask & 15) != 15) return OfferResult.FOUR_SIGILS_REQUIRED;
        if (!("dynasty:" + OFFERINGS[slot]).equals(item)) return OfferResult.WRONG_ITEM;
        return OfferResult.ACCEPTED;
    }
    public static int visualStage(String phase) {
        return switch (phase) {
            case "charging" -> 1;
            case "active", "paused" -> 2;
            case "victory", "returned" -> 3;
            default -> 0;
        };
    }
}
