package com.dynasty;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 饰品**连携**（第三十四轮新增）：同一主题的饰品一起戴才有额外加成。
 *
 * 饰品表第 15 格写「连携组」（0 = 不参与），每个组有 2 / 3 / 4 件三档，
 * **只取达到的最高档，不叠层** —— 例：昼夜双生 2 件给移速 +5%，3 件给攻击 +8% 与移速 +5%，
 * 4 件给攻击 +12% 与移速 +8%。参数同样来自生成器打印的 `LINK_TABLE`，改表就改行为。
 *
 * 结算方式与饰品本身一致：**每秒「先清后加」**（用 `link_<组号>` 这个 id 占一段 UUID），
 * 所以摘下任意一件，档位会立刻回退，不会留下幽灵加成。生效档位变化时给玩家一句提示。
 *
 * Accessory synergy: wear 2/3/4 pieces of the same theme for extra bonuses. Highest reached
 * tier wins (no stacking); effects are cleared and re-applied every second, exactly like
 * normal accessories, so unequipping one piece rolls the tier back immediately.
 */
public final class DynastyTrinketLink {

    private static final Map<String, Integer> GROUP_OF = new HashMap<>();
    private static final Map<Integer, String> GROUP_NAMES = new HashMap<>();

    /** 一条连携加成：组、需要的件数、类型（0 属性 / 1 模组效果）、编码、数值、条件 */
    private record Link(int group, int need, int kind, int code, double value, int condition) {}

    private static final List<Link> LINKS = new ArrayList<>();

    /** 上一次提示过的「生效档位」文本，用来避免每秒刷屏 */
    private static final Map<UUID, String> SHOWN = new HashMap<>();

    private DynastyTrinketLink() {
    }

    /**
     * 建表时调用一次：把每件饰品的连携组、以及连携加成表抽出来。
     * 之后每秒只算「每组戴了几件」，不再遍历饰品表。
     */
    public static void index(Object[][] trinkets, Object[][] links, Map<Integer, String> names) {
        GROUP_OF.clear();
        GROUP_NAMES.clear();
        LINKS.clear();
        GROUP_NAMES.putAll(names);
        for (Object[] row : trinkets) {
            if (row.length > 14 && (Integer) row[14] > 0) {
                GROUP_OF.put((String) row[0], (Integer) row[14]);
            }
        }
        for (Object[] row : links) {
            LINKS.add(new Link((Integer) row[0], (Integer) row[1], (Integer) row[2],
                    (Integer) row[3], (Double) row[4], (Integer) row[5]));
        }
    }

    public static void forget(Player player) {
        SHOWN.remove(player.getUUID());
    }

    /** 每秒结算：先清掉自己上一轮的修饰符，再按件数给最高档。 */
    public static void apply(Player player, java.util.Set<String> active) {
        for (int group : GROUP_NAMES.keySet()) {
            DynastyTrinkets.clearAttrs(player, "link_" + group);
        }
        if (LINKS.isEmpty() || active.isEmpty()) {
            return;
        }
        Map<Integer, Integer> counts = new HashMap<>();
        for (String id : active) {
            Integer group = GROUP_OF.get(id);
            if (group != null) {
                counts.merge(group, 1, Integer::sum);
            }
        }
        StringBuilder reached = new StringBuilder();
        for (int group : GROUP_NAMES.keySet()) {
            int count = counts.getOrDefault(group, 0);
            if (count < 2) {
                continue;
            }
            int best = 0;
            for (Link link : LINKS) {
                if (link.group() == group && link.need() <= count) {
                    best = Math.max(best, link.need());
                }
            }
            if (best == 0) {
                continue;
            }
            for (Link link : LINKS) {
                if (link.group() != group || link.need() != best
                        || !DynastyTrinkets.conditionMet(player, link.condition())) {
                    continue;
                }
                if (link.kind() == 0) {
                    DynastyTrinkets.applySpecAttr(player, "link_" + group, 0, link.code(), link.value());
                } else {
                    DynastyTrinkets.applySpecEffect(player, link.code(), (int) link.value());
                }
            }
            if (reached.length() > 0) {
                reached.append("、");
            }
            reached.append(GROUP_NAMES.get(group)).append(" ").append(best).append(" 件");
        }
        notifyChange(player, reached.toString());
    }

    /** 生效档位变化时提示一次（摘下 / 换上都会提示，便于玩家验证机制）。 */
    private static void notifyChange(Player player, String text) {
        UUID uuid = player.getUUID();
        if (text.equals(SHOWN.getOrDefault(uuid, ""))) {
            return;
        }
        SHOWN.put(uuid, text);
        if (!text.isEmpty() && player instanceof ServerPlayer server) {
            server.displayClientMessage(Component.literal("§6[连携] §r" + text + " —— 生效中"), true);
        }
    }
}
