package com.dynasty.client;

import com.dynasty.network.BowEffectPacket;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import java.util.Map;
import java.util.HashMap;
import java.util.List;
import java.util.ArrayList;

public final class ClientBowEffects {
    public record Effect(BowEffectPacket packet, long born) {}
    public static final Map<Integer, Effect> ARROWS = new HashMap<>();
    public static final List<Effect> IMPACTS = new ArrayList<>();
    private static ClientLevel world;
    public static void clean() {
        ClientLevel current = Minecraft.getInstance().level;
        if (world != current) { ARROWS.clear(); IMPACTS.clear(); world = current; }
        if (world == null) return;
        long now = world.getGameTime();
        ARROWS.values().removeIf(e -> now - e.born > 30);
        IMPACTS.removeIf(e -> now - e.born > 60);
    }
    public static void receive(BowEffectPacket packet) {
        clean();
        if (world == null || packet.tier()<0 || packet.tier()>4 || packet.theme()<0 || packet.theme()>4
                || !Double.isFinite(packet.x()+packet.y()+packet.z())) return;
        Effect effect = new Effect(packet, world.getGameTime());
        if (packet.kind() == 0) { ARROWS.put(packet.entityId(), effect); if(ARROWS.size()>96) ARROWS.remove(ARROWS.keySet().iterator().next()); }
        else if (packet.kind() == 1) {
            IMPACTS.add(effect);
            if (IMPACTS.size() > 48) IMPACTS.remove(0);
        }
        else if (packet.kind() == 2) ARROWS.remove(packet.entityId());
    }
    private ClientBowEffects() {}
}
