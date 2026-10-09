package com.dynasty.network;

import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty_network")
@PrefixGameTestTemplate(false)
public final class NetworkCompatibilityGameTests {
    @GameTest(template="bow_ritual_test")
    public static void frozenSchemaRejectsIndependentWireChanges(GameTestHelper h) {
        String local = DynastyNetwork.protocolVersion();
        h.assertTrue(local.contains("17=com.dynasty.infusion.InfusionRequest:PLAY_TO_SERVER:v1"),
                "Infusion registration must be advertised before channel construction");
        h.assertTrue(DynastyNetwork.acceptsProtocol(local), "The local frozen schema accepts itself");
        rejects(h, local, local.replace("/keju=" + OpenKejuPacket.WIRE_REVISION,
                "/keju=" + (OpenKejuPacket.WIRE_REVISION + 1)), "exam payload");
        rejects(h, local, local.replace("/army=" + com.dynasty.army.ArmyMenu.LAYOUT_REVISION,
                "/army=" + (com.dynasty.army.ArmyMenu.LAYOUT_REVISION + 1)), "army menu layout");
        rejects(h, local, local.replace("17=", "18="), "extension ID");
        rejects(h, local, local.replace("InfusionRequest:PLAY_TO_SERVER:v1",
                "InfusionRequest:PLAY_TO_CLIENT:v1"), "extension direction");
        rejects(h, local, local.replace("InfusionRequest:PLAY_TO_SERVER:v1",
                "InfusionRequest:PLAY_TO_SERVER:v2"), "extension payload revision");
        rejects(h, local, "10/{}", "legacy base version 10");
        rejects(h, local, "9/{}", "legacy base version 9");
        h.succeed();
    }

    private static void rejects(GameTestHelper h, String local, String peer, String change) {
        h.assertTrue(!local.equals(peer), "Test must actually change " + change);
        h.assertTrue(!DynastyNetwork.acceptsProtocol(peer), "Incompatible peer accepted: " + change);
    }
}
