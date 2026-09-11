package com.dynasty.network;

import com.dynasty.DynastyQuests;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/** 服务端 → 客户端：同步任务进度并打开任务界面。 */
public class QuestSyncPacket {

    private final int[] progress;
    private final boolean[] claimed;

    public QuestSyncPacket(int[] progress, boolean[] claimed) {
        this.progress = progress;
        this.claimed = claimed;
    }

    public static void encode(QuestSyncPacket pkt, FriendlyByteBuf buf) {
        buf.writeVarInt(DynastyQuests.count());
        for (int p : pkt.progress) {
            buf.writeVarInt(Math.max(0, p));
        }
        for (boolean c : pkt.claimed) {
            buf.writeBoolean(c);
        }
    }

    public static QuestSyncPacket decode(FriendlyByteBuf buf) {
        int n = buf.readVarInt();
        int[] progress = new int[n];
        boolean[] claimed = new boolean[n];
        for (int i = 0; i < n; i++) {
            progress[i] = buf.readVarInt();
        }
        for (int i = 0; i < n; i++) {
            claimed[i] = buf.readBoolean();
        }
        return new QuestSyncPacket(progress, claimed);
    }

    public static void handle(QuestSyncPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                () -> () -> com.dynasty.client.ClientQuests.receive(pkt.progress, pkt.claimed)));
        ctx.get().setPacketHandled(true);
    }
}
