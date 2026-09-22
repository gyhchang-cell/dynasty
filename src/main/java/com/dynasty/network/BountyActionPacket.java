package com.dynasty.network;

import com.dynasty.bounty.BountyService;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/**
 * 客户端 → 服务端：委托操作**意图**（不携带数量/奖励，服务端全部重新判定）。
 * Client -> server: an intent only. Counts, progress and rewards are recomputed server-side.
 */
public class BountyActionPacket {

    private final String action;
    private final String instanceId;

    public BountyActionPacket(String action, String instanceId) {
        this.action = action == null ? "" : action;
        this.instanceId = instanceId == null ? "" : instanceId;
    }

    public static void encode(BountyActionPacket pkt, FriendlyByteBuf buf) {
        buf.writeUtf(pkt.action, 16);
        buf.writeUtf(pkt.instanceId, 96);
    }

    public static BountyActionPacket decode(FriendlyByteBuf buf) {
        return new BountyActionPacket(buf.readUtf(16), buf.readUtf(96));
    }

    public static void handle(BountyActionPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        NetworkEvent.Context context = ctx.get();
        context.enqueueWork(() -> {
            ServerPlayer player = context.getSender();
            if (player != null) {
                BountyService.handleAction(player, pkt.action, pkt.instanceId);
            }
        });
        context.setPacketHandled(true);
    }
}
