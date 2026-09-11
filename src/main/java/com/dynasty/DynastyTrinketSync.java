package com.dynasty;

import com.dynasty.network.DynastyNetwork;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;
import net.minecraftforge.network.PacketDistributor;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/** 服务端 → 客户端：同步已装备的饰品 id（供 HUD 等使用）。 */
public class DynastyTrinketSync {

    private final List<String> ids;

    public DynastyTrinketSync(List<String> ids) {
        this.ids = ids;
    }

    public static void send(ServerPlayer player) {
        DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(() -> player),
                new DynastyTrinketSync(DynastyTrinkets.equippedIds(player)));
    }

    public static void encode(DynastyTrinketSync packet, FriendlyByteBuf buf) {
        buf.writeVarInt(packet.ids.size());
        for (String id : packet.ids) {
            buf.writeUtf(id);
        }
    }

    public static DynastyTrinketSync decode(FriendlyByteBuf buf) {
        int size = buf.readVarInt();
        List<String> ids = new ArrayList<>();
        for (int i = 0; i < size; i++) {
            ids.add(buf.readUtf());
        }
        return new DynastyTrinketSync(ids);
    }

    public static void handle(DynastyTrinketSync packet, Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                () -> () -> com.dynasty.client.ClientTrinkets.set(packet.ids)));
        ctx.get().setPacketHandled(true);
    }
}
