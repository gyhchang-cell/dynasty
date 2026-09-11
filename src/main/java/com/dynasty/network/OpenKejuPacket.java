package com.dynasty.network;

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

    public OpenKejuPacket(int index, String question, String a, String b, String c) {
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
    }

    public static OpenKejuPacket decode(FriendlyByteBuf buf) {
        int index = buf.readInt();
        String question = buf.readUtf();
        String a = buf.readUtf();
        String b = buf.readUtf();
        String c = buf.readUtf();
        return new OpenKejuPacket(index, question, a, b, c);
    }

    public static void handle(OpenKejuPacket pkt, Supplier<NetworkEvent.Context> ctx) {
        ctx.get().enqueueWork(() -> DistExecutor.unsafeRunWhenOn(Dist.CLIENT,
                () -> () -> com.dynasty.client.ClientKeju.open(pkt.index, pkt.question, pkt.options)));
        ctx.get().setPacketHandled(true);
    }
}
