package com.dynasty.network;

import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty_network")
@PrefixGameTestTemplate(false)
public final class NetworkCompatibilityGameTests {
    @GameTest(template="bow_ritual_test")
    public static void frozenSchemaRejectsIndependentWireChanges(GameTestHelper h) throws Exception {
        String local = DynastyNetwork.protocolVersion();
        String schema = DynastyNetwork.protocolSchema();
        h.assertTrue(schema.contains("17=com.dynasty.infusion.InfusionRequest:PLAY_TO_SERVER:v1"),
                "Infusion registration must be advertised before channel construction");
        h.assertTrue(DynastyNetwork.acceptsProtocol(local), "The local frozen schema accepts itself");
        var snapshot=net.minecraftforge.network.NetworkRegistry.class.getDeclaredMethod("buildChannelVersions");
        snapshot.setAccessible(true);
        var channels=(java.util.Map<?,?>)snapshot.invoke(null);
        h.assertTrue(local.equals(channels.get(new net.minecraft.resources.ResourceLocation("dynasty:dynasty"))),
                "Forge must cache the complete compact version before login");
        h.assertTrue(!DynastyNetwork.acceptsProtocol(schema),"Unbounded legacy schema version rejected");
        rejects(h, local, schema.replace("/keju=" + OpenKejuPacket.WIRE_REVISION,
                "/keju=" + (OpenKejuPacket.WIRE_REVISION + 1)), "exam payload");
        rejects(h, local, schema.replace("/army=" + com.dynasty.army.ArmyMenu.LAYOUT_REVISION,
                "/army=" + (com.dynasty.army.ArmyMenu.LAYOUT_REVISION + 1)), "army menu layout");
        rejects(h, local, schema.replace("17=", "18="), "extension ID");
        rejects(h, local, schema.replace("InfusionRequest:PLAY_TO_SERVER:v1",
                "InfusionRequest:PLAY_TO_CLIENT:v1"), "extension direction");
        rejects(h, local, schema.replace("InfusionRequest:PLAY_TO_SERVER:v1",
                "InfusionRequest:PLAY_TO_SERVER:v2"), "extension payload revision");
        rejects(h, local, "10/{}", "legacy base version 10");
        rejects(h, local, "9/{}", "legacy base version 9");
        var buffer=new net.minecraft.network.FriendlyByteBuf(io.netty.buffer.Unpooled.buffer());
        try {
            buffer.writeUtf(local,256);
            h.assertTrue(buffer.readUtf(256).equals(local),"Version fits Forge login channel limit");
            h.assertTrue(local.equals(DynastyNetwork.fingerprintSchema(schema)),"Fingerprint includes the full schema");
        } finally {buffer.release();}
        h.succeed();
    }

    private static void rejects(GameTestHelper h, String local, String peer, String change) {
        String tag=DynastyNetwork.fingerprintSchema(peer);
        h.assertTrue(!local.equals(tag), "Test must actually change " + change);
        h.assertTrue(!DynastyNetwork.acceptsProtocol(tag), "Incompatible peer accepted: " + change);
    }
}
