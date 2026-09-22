package com.dynasty.network;

import com.dynasty.DynastyKeju;
import com.dynasty.keju.KejuNet;
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

    /** 本次令牌。/ the session token. */
    public int index() {
        return index;
    }

    /** 选项 1..3（越界由服务端会话裁定，不在这里静默修正）。*/
    public int choice() {
        return choice;
    }

    /**
     * 线协议不变：两个 int（令牌 + 选项）。只接收客户端 → 服务端的包；
     * 玩家身份取自上下文里的真实发送者，不接受包内自报身份。
     */
    public static void handle(AnswerKejuPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        NetworkEvent.Context context = ctx.get();
        context.setPacketHandled(true);
        if (!KejuNet.acceptsAnswer(context.getDirection())) {
            return;
        }
        ServerPlayer sender = context.getSender();
        if (sender == null) {
            return;
        }
        context.enqueueWork(() -> DynastyKeju.handleAnswer(sender, pkt.index, pkt.choice));
    }
}
