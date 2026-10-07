package com.dynasty.network;

import com.dynasty.Dynasty;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.simple.SimpleChannel;

/**
 * Dynasty 网络通道（科举 GUI 用）。
 * Dynasty network channel (used by the Keju GUI).
 */
public class DynastyNetwork {

    private static final String PROTOCOL = "8";

    @SuppressWarnings("removal")
    public static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(
            new ResourceLocation(Dynasty.MODID, "dynasty"),
            () -> PROTOCOL,
            PROTOCOL::equals,
            PROTOCOL::equals);

    private static int id = 0;

    public static void register() {
        CHANNEL.registerMessage(id++, DragonDescentPacket.class,
                DragonDescentPacket::encode, DragonDescentPacket::decode, DragonDescentPacket::handle,
                java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_CLIENT));
        CHANNEL.registerMessage(id++, WeaponImpactPacket.class,
                WeaponImpactPacket::encode, WeaponImpactPacket::decode, WeaponImpactPacket::handle,
                java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_CLIENT));
        CHANNEL.registerMessage(id++, BowEffectPacket.class,
                BowEffectPacket::encode, BowEffectPacket::decode, BowEffectPacket::handle,
                java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_CLIENT));
        CHANNEL.registerMessage(id++, OpenKejuPacket.class,
                OpenKejuPacket::encode, OpenKejuPacket::decode, OpenKejuPacket::handle);
        CHANNEL.registerMessage(id++, AnswerKejuPacket.class,
                AnswerKejuPacket::encode, AnswerKejuPacket::decode, AnswerKejuPacket::handle);
        CHANNEL.registerMessage(id++, StatsRequestPacket.class,
                StatsRequestPacket::encode, StatsRequestPacket::decode, StatsRequestPacket::handle);
        CHANNEL.registerMessage(id++, ArmyFormPacket.class,
                ArmyFormPacket::encode, ArmyFormPacket::decode, ArmyFormPacket::handle);
        CHANNEL.registerMessage(id++, StatsRequestPacket.class,
                StatsRequestPacket::encode, StatsRequestPacket::decode, StatsRequestPacket::handle);
        CHANNEL.registerMessage(id++, StatsSyncPacket.class,
                StatsSyncPacket::encode, StatsSyncPacket::decode, StatsSyncPacket::handle);
        CHANNEL.registerMessage(id++, BountyBoardPacket.class,
                BountyBoardPacket::encode, BountyBoardPacket::decode, BountyBoardPacket::handle,
                java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_CLIENT));
        CHANNEL.registerMessage(id++, BountyActionPacket.class,
                BountyActionPacket::encode, BountyActionPacket::decode, BountyActionPacket::handle,
                java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_SERVER));
        // Append only: preserve existing packet ordinals. Both peers must use the new protocol.
        CHANNEL.registerMessage(id++, com.dynasty.blueprint.BlueprintVisualEvent.class,
                com.dynasty.blueprint.BlueprintVisualEvent::encode,
                com.dynasty.blueprint.BlueprintVisualEvent::decode,
                com.dynasty.blueprint.BlueprintVisualEvent::handle,
                java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_CLIENT));
        CHANNEL.registerMessage(id++, com.dynasty.cod3.Cod3VisualPacket.class,
                com.dynasty.cod3.Cod3VisualPacket::encode, com.dynasty.cod3.Cod3VisualPacket::decode,
                com.dynasty.cod3.Cod3VisualPacket::handle,
                java.util.Optional.of(net.minecraftforge.network.NetworkDirection.PLAY_TO_CLIENT));
    }
}
