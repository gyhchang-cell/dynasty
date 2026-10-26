package net.mehvahdjukaar.dummmmmmy.network;

import net.mehvahdjukaar.dummmmmmy.Dummmmmmy;
import net.mehvahdjukaar.dummmmmmy.common.TargetDummyEntity;
import net.mehvahdjukaar.moonlight.api.platform.network.Message;
import net.minecraft.client.Minecraft;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.world.entity.Entity;

public record ClientBoundUpdateAnimationMessage(int entityID, float shake) implements Message {

    public static final CustomPacketPayload.TypeAndCodec<RegistryFriendlyByteBuf, ClientBoundUpdateAnimationMessage> TYPE =
            Message.makeType(Dummmmmmy.res("s2c_animation"), ClientBoundUpdateAnimationMessage::new);

    public ClientBoundUpdateAnimationMessage(RegistryFriendlyByteBuf buf) {
        this(buf.readInt(), buf.readFloat());
    }

    @Override
    public void write(RegistryFriendlyByteBuf buf) {
        buf.writeInt(this.entityID);
        buf.writeFloat(this.shake);
    }

    @Override
    public void handle(Context context) {
        Entity entity = Minecraft.getInstance().level.getEntity(this.entityID);
        if (entity instanceof TargetDummyEntity dummy) {
            dummy.updateAnimation(shake);
        }
    }

    @Override
    public Type<? extends CustomPacketPayload> type() {
        return TYPE.type();
    }
}

