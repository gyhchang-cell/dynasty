package com.dynasty.network;

import com.dynasty.bounty.BountyModel;
import com.dynasty.bounty.BountyView;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/**
 * 服务端 → 客户端：悬赏告示板界面数据（客户端只负责显示）。
 * Server -> client: bounty board view. The client only renders it.
 */
public class BountyBoardPacket {

    private final BountyView view;

    public BountyBoardPacket(BountyView view) {
        this.view = view;
    }

    public static void encode(BountyBoardPacket pkt, FriendlyByteBuf buf) {
        BountyView view = pkt.view;
        buf.writeLong(view.day);
        buf.writeVarInt(view.activeCount);
        buf.writeVarInt(view.maxActive);
        buf.writeUtf(view.statusKey == null ? "" : view.statusKey);
        buf.writeVarInt(view.entries.size());
        for (BountyView.Entry entry : view.entries) {
            buf.writeUtf(entry.instanceId);
            buf.writeUtf(entry.titleKey);
            buf.writeUtf(entry.descKey);
            buf.writeVarInt(entry.type.ordinal());
            buf.writeUtf(entry.targetKey);
            buf.writeVarInt(entry.amount);
            buf.writeVarInt(entry.progress);
            buf.writeVarInt(entry.state.ordinal());
            buf.writeVarInt(entry.emeralds);
            buf.writeVarInt(entry.experience);
            buf.writeVarInt(entry.supplies.size());
            for (BountyModel.Stack stack : entry.supplies) {
                buf.writeUtf(stack.item);
                buf.writeVarInt(stack.count);
            }
        }
    }

    public static BountyBoardPacket decode(FriendlyByteBuf buf) {
        long day = buf.readLong();
        int active = buf.readVarInt();
        int maxActive = buf.readVarInt();
        String status = buf.readUtf();
        int count = buf.readVarInt();
        List<BountyView.Entry> entries = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            String instanceId = buf.readUtf();
            String titleKey = buf.readUtf();
            String descKey = buf.readUtf();
            BountyModel.Type type = BountyModel.Type.values()[buf.readVarInt()];
            String targetKey = buf.readUtf();
            int amount = buf.readVarInt();
            int progress = buf.readVarInt();
            BountyView.State state = BountyView.State.values()[buf.readVarInt()];
            int emeralds = buf.readVarInt();
            int experience = buf.readVarInt();
            int supplies = buf.readVarInt();
            List<BountyModel.Stack> stacks = new ArrayList<>();
            for (int s = 0; s < supplies; s++) {
                stacks.add(new BountyModel.Stack(buf.readUtf(), buf.readVarInt()));
            }
            entries.add(new BountyView.Entry(instanceId, titleKey, descKey, type, targetKey, amount,
                    progress, state, emeralds, experience, stacks));
        }
        return new BountyBoardPacket(new BountyView(day, active, maxActive,
                status.isEmpty() ? null : status, entries));
    }

    public static void handle(BountyBoardPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                () -> () -> com.dynasty.client.ClientBounty.accept(pkt.view)));
        ctx.get().setPacketHandled(true);
    }
}
