package com.dynasty;

import com.dynasty.entity.DynastyEntities;
import com.dynasty.entity.ImperialSoldier;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;

import java.util.ArrayList;
import java.util.List;

/**
 * 军队阵型系统：方阵、锋矢、雁行、横阵、圆阵。
 * Army formation system: square, wedge, crane wing, line and circle formations.
 */
@SuppressWarnings("null")
public final class DynastyArmy {

    private DynastyArmy() {
    }

    public static final String[] FORMATIONS = {"square", "wedge", "crane", "line", "circle"};

    /** 生成阵型并返回士兵数量 / spawns the formation and returns the soldier count. */
    public static int formUp(ServerPlayer player, String formation, int count) {
        ServerLevel level = player.serverLevel();
        List<int[]> offsets = offsetsFor(formation, count);
        int spawned = 0;
        for (int[] o : offsets) {
            ImperialSoldier soldier = DynastyEntities.IMPERIAL_SOLDIER.get().create(level);
            if (soldier == null) {
                continue;
            }
            BlockPos pos = rotate(player, o[0], o[1]);
            soldier.moveTo(pos.getX() + 0.5D, player.getY(), pos.getZ() + 0.5D, player.getYRot(), 0.0F);
            soldier.setOwner(player);
            soldier.setCustomName(Component.literal("§e禁军"));
            level.addFreshEntity(soldier);
            spawned++;
        }
        double loyalty = 1.0D + DynastyStats.getLoyalty(player) / 200.0D;
        player.sendSystemMessage(Component.literal("§6[军阵] §f" + formationName(formation)
                + "§7 已列阵（" + spawned + " 名禁军，忠诚加成 ×" + String.format("%.2f", loyalty) + "）"));
        DynastyQuestManager.notifyEvent(player, "army");
        return spawned;
    }

    private static String formationName(String formation) {
        return switch (formation) {
            case "wedge" -> "锋矢阵";
            case "crane" -> "雁行阵";
            case "line" -> "横阵";
            case "circle" -> "圆阵";
            default -> "方阵";
        };
    }

    /** 以玩家朝向为基准旋转偏移 / rotate offsets by the player's facing. */
    private static BlockPos rotate(ServerPlayer player, int dx, int dz) {
        double yaw = Math.toRadians(player.getYRot());
        double sin = Math.sin(yaw);
        double cos = Math.cos(yaw);
        int x = (int) Math.round(dx * cos + dz * sin);
        int z = (int) Math.round(-dx * sin + dz * cos);
        return new BlockPos(player.getBlockX() + x, player.getBlockY(), player.getBlockZ() + z);
    }

    /** 计算阵型偏移（前=+z）/ computes formation offsets (front = +z). */
    private static List<int[]> offsetsFor(String formation, int count) {
        List<int[]> out = new ArrayList<>();
        count = Math.max(1, Math.min(64, count));
        switch (formation) {
            case "wedge" -> {
                for (int i = 0; i < count; i++) {
                    int row = i / 2 + 1;
                    int side = (i % 2 == 0) ? 1 : -1;
                    out.add(new int[]{side * row, -row});
                }
            }
            case "crane" -> {
                for (int i = 0; i < count; i++) {
                    int row = i / 2 + 1;
                    int side = (i % 2 == 0) ? 1 : -1;
                    out.add(new int[]{side * row * 2, -row * 2});
                }
            }
            case "line" -> {
                int half = count / 2;
                for (int i = 0; i < count; i++) {
                    out.add(new int[]{i - half, 2});
                }
            }
            case "circle" -> {
                double step = 2 * Math.PI / count;
                int radius = Math.max(3, count / 2);
                for (int i = 0; i < count; i++) {
                    out.add(new int[]{(int) Math.round(Math.cos(step * i) * radius),
                            (int) Math.round(Math.sin(step * i) * radius)});
                }
            }
            default -> {
                int width = (int) Math.ceil(Math.sqrt(count));
                for (int i = 0; i < count; i++) {
                    out.add(new int[]{i % width - width / 2, i / width - width / 2 + 2});
                }
            }
        }
        return out;
    }
}
