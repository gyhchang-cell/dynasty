package com.dynasty;

/**
 * 悬停说明的**共享预算**（不引用任何客户端类，服务器也安全）。
 *
 * 为什么要单独一个类：饰品说明在 {@code DynastyTrinketTips}（共享物品类）里拼装，
 * 装备说明在 {@code client.DynastyTooltips} 里拼装，两边必须用同一个「默认几行」预算，
 * 但共享类**不能**去引用客户端类（专用服务器不该加载客户端代码）。
 *
 * Shared tooltip budget so the shared item classes and the client-side tooltip
 * code agree, without the server ever touching client classes.
 */
public final class DynastyTooltipBudget {

    private DynastyTooltipBudget() {
    }

    /** 默认（不按 Shift）最多显示几行我们自己的说明 / max custom lines shown without Shift */
    public static final int BRIEF_LIMIT = 3;
}
