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

    // Base wire schema 10 adds the server-owned exam duration to OpenKejuPacket.
    // A cod3-only peer must never accept a cod6-only peer merely sharing a version.
    private static final java.util.SortedMap<Integer,String> EXTENSIONS = new java.util.TreeMap<>();
    public static String protocolVersion() { return "10/" + EXTENSIONS; }
    public static boolean acceptsProtocol(String remote) { return protocolVersion().equals(remote); }

    public static <T> void registerExtension(int packetId, Class<T> type,
            java.util.function.BiConsumer<T,net.minecraft.network.FriendlyByteBuf> encoder,
            java.util.function.Function<net.minecraft.network.FriendlyByteBuf,T> decoder,
            java.util.function.BiConsumer<T,java.util.function.Supplier<net.minecraftforge.network.NetworkEvent.Context>> handler,
            net.minecraftforge.network.NetworkDirection direction, int wireRevision) {
        if (packetId < 12 || EXTENSIONS.containsKey(packetId))
            throw new IllegalArgumentException("Reserved or duplicate Dynasty packet ID: " + packetId);
        EXTENSIONS.put(packetId, type.getName() + ":" + direction + ":v" + wireRevision);
        CHANNEL.registerMessage(packetId, type, encoder, decoder, handler, java.util.Optional.of(direction));
    }

    @SuppressWarnings("removal")
    public static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(
            new ResourceLocation(Dynasty.MODID, "dynasty"),
            DynastyNetwork::protocolVersion,
            DynastyNetwork::acceptsProtocol,
            DynastyNetwork::acceptsProtocol);

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
    }
}
