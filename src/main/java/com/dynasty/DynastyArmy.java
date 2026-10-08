package com.dynasty;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;


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
        int idx=java.util.Arrays.asList(FORMATIONS).indexOf(formation);
        int spawned=com.dynasty.army.ArmyRoster.deploy(player,idx,count);
        player.displayClientMessage(Component.literal(spawned>0?"已部署 "+spawned+" 名军籍禁卫":"无法出阵：检查虎符、兵册、场上部队和槽位障碍"),true);
        return spawned;
    }

}
