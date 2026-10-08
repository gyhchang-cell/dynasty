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

    // Base wire schema 9; extensions also advertise IDs, payload revision and direction.
    // A cod3-only peer must never accept a cod6-only peer merely sharing a version.
    // Forge snapshots the supplier when the channel is constructed. Declare the complete
    // immutable table first; filling it during common setup makes the channel reject itself.
    private static final java.util.SortedMap<Integer,String> EXTENSIONS = java.util.Collections.unmodifiableSortedMap(
            new java.util.TreeMap<>(java.util.Map.of(
                    12, "com.dynasty.cod3.Cod3VisualPacket:PLAY_TO_CLIENT:v1",
                    13, "com.dynasty.network.EdictCastPacket:PLAY_TO_SERVER:v1",
                    14, "com.dynasty.network.EdictVisualPacket:PLAY_TO_CLIENT:v1")));
    private static final java.util.Set<Integer> REGISTERED_EXTENSIONS = new java.util.HashSet<>();
    public static String protocolVersion() { return "9/" + EXTENSIONS; }
    public static boolean acceptsProtocol(String remote) { return protocolVersion().equals(remote); }

    public static <T> void registerExtension(int packetId, Class<T> type,
            java.util.function.BiConsumer<T,net.minecraft.network.FriendlyByteBuf> encoder,
            java.util.function.Function<net.minecraft.network.FriendlyByteBuf,T> decoder,
            java.util.function.BiConsumer<T,java.util.function.Supplier<net.minecraftforge.network.NetworkEvent.Context>> handler,
            net.minecraftforge.network.NetworkDirection direction, int wireRevision) {
        if (packetId < 12 || REGISTERED_EXTENSIONS.contains(packetId))
            throw new IllegalArgumentException("Reserved or duplicate Dynasty packet ID: " + packetId);
        String schema = type.getName() + ":" + direction + ":v" + wireRevision;
        if (!schema.equals(EXTENSIONS.get(packetId)))
            throw new IllegalArgumentException("Dynasty packet is missing from the frozen wire schema: " + packetId);
        REGISTERED_EXTENSIONS.add(packetId);
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
