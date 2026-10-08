package com.dynasty.network;

import com.dynasty.keju.KejuNet;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.network.NetworkEvent;

import java.util.function.Supplier;

/**
 * 服务端 → 客户端：打开科举界面。
 * Server -> client: open the Keju screen.
 */
public class OpenKejuPacket {

    private final int index;
    private final String question;
    private final String[] options;
    private final int answerMillis;

    public OpenKejuPacket(int index, String question, String a, String b, String c) {
        this(index, question, a, b, c, 30000);
    }

    public OpenKejuPacket(int index, String question, String a, String b, String c, int answerMillis) {
        if (answerMillis < 1000 || answerMillis > 120000) throw new IllegalArgumentException("Invalid exam duration");
        this.answerMillis = answerMillis;
        this.index = index;
        this.question = question;
        this.options = new String[]{a, b, c};
    }

    public static void encode(OpenKejuPacket pkt, FriendlyByteBuf buf) {
        buf.writeInt(pkt.index);
        buf.writeUtf(pkt.question);
        for (String option : pkt.options) {
            buf.writeUtf(option);
        }
        buf.writeVarInt(pkt.answerMillis);
    }

    /**
     * 线协议 v10：令牌、题干、三个选项和答题时限（毫秒）。
     * 读取时按 {@link KejuNet} 的长度上限拒绝超长字段（题库校验用同一套上限）。
     */
    public static OpenKejuPacket decode(FriendlyByteBuf buf) {
        int index = buf.readInt();
        String question = buf.readUtf(KejuNet.MAX_QUESTION_CHARS);
        String a = buf.readUtf(KejuNet.MAX_OPTION_CHARS);
        String b = buf.readUtf(KejuNet.MAX_OPTION_CHARS);
        String c = buf.readUtf(KejuNet.MAX_OPTION_CHARS);
        return new OpenKejuPacket(index, question, a, b, c, buf.readVarInt());
    }

    /** 本次令牌。/ the session token. */
    public int index() {
        return index;
    }
    public int answerMillis() { return answerMillis; }

    public String question() {
        return question;
    }

    /** 三个选项的副本。/ copy of the three options. */
    public String[] options() {
        return options.clone();
    }

    /** 只接收服务端 → 客户端的包；方向不符直接丢弃。 */
    public static void handle(OpenKejuPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        NetworkEvent.Context context = ctx.get();
        context.setPacketHandled(true);
        if (!KejuNet.acceptsOpen(context.getDirection())) {
            return;
        }
        context.enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                () -> () -> com.dynasty.client.ClientKeju.open(pkt.index, pkt.question, pkt.options, pkt.answerMillis)));
    }
}
