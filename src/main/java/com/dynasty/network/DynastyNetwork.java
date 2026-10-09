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

    // Freeze the full extension schema before Forge snapshots the channel supplier.
    // Independent base revisions prevent unrelated menu/payload changes sharing a version.
    private static final java.util.SortedMap<Integer,String> EXTENSIONS = java.util.Collections.unmodifiableSortedMap(
            new java.util.TreeMap<>(java.util.Map.of(
                    12, "com.dynasty.cod3.Cod3VisualPacket:PLAY_TO_CLIENT:v1",
                    13, "com.dynasty.network.EdictCastPacket:PLAY_TO_SERVER:v1",
                    14, "com.dynasty.network.EdictVisualPacket:PLAY_TO_CLIENT:v2",
                    15, "com.dynasty.worldevent.WorldEventStatePacket:PLAY_TO_CLIENT:v1",
                    16, "com.dynasty.expansion.CombatFeedback:PLAY_TO_CLIENT:v2",
                    17, "com.dynasty.infusion.InfusionRequest:PLAY_TO_SERVER:v1")));
    private static final java.util.Set<Integer> REGISTERED_EXTENSIONS = new java.util.HashSet<>();
    private static final String PROTOCOL_VERSION = fingerprintSchema(protocolSchema());
    public static String protocolSchema() {
        return "11/keju=" + OpenKejuPacket.WIRE_REVISION + "/army="
                + com.dynasty.army.ArmyMenu.LAYOUT_REVISION + "/" + EXTENSIONS;
    }
    // Forge's login ModList encodes each channel version with writeUtf(..., 256).
    // Fingerprint the complete frozen schema; never drop an extension to fit the limit.
    static String fingerprintSchema(String schema) {
        try {
            return "12/" + java.util.HexFormat.of().formatHex(java.security.MessageDigest.getInstance("SHA-256")
                .digest(schema.getBytes(java.nio.charset.StandardCharsets.UTF_8)));
        } catch (java.security.NoSuchAlgorithmException impossible) {
            throw new AssertionError("Java must provide SHA-256", impossible);
        }
    }
    public static String protocolVersion() { return PROTOCOL_VERSION; }
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
        // IDs 12-16 belong to cod3/edict/world-event/combat-feedback extensions.
        registerExtension(17, com.dynasty.infusion.InfusionRequest.class,
                com.dynasty.infusion.InfusionRequest::encode, com.dynasty.infusion.InfusionRequest::decode,
                com.dynasty.infusion.InfusionRequest::handle,
                net.minecraftforge.network.NetworkDirection.PLAY_TO_SERVER, 1);
    }
}
