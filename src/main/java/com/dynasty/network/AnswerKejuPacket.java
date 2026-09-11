package com.dynasty.network;

import com.dynasty.DynastyKeju;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/**
 * 客户端 → 服务端：提交科举答案。
 * Client -> server: submit the exam answer.
 */
public class AnswerKejuPacket {

    private final int index;
    private final int choice;

    public AnswerKejuPacket(int index, int choice) {
        this.index = index;
        this.choice = choice;
    }

    public static void encode(AnswerKejuPacket pkt, FriendlyByteBuf buf) {
        buf.writeInt(pkt.index);
        buf.writeInt(pkt.choice);
    }

    public static AnswerKejuPacket decode(FriendlyByteBuf buf) {
        return new AnswerKejuPacket(buf.readInt(), buf.readInt());
    }

    public static void handle(AnswerKejuPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() -> {
            ServerPlayer player = ctx.get().getSender();
            if (player != null) {
                DynastyKeju.handleAnswer(player, pkt.index, pkt.choice);
            }
        });
        ctx.get().setPacketHandled(true);
    }
}
