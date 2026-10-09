package com.dynasty.network;

import net.minecraft.gametest.framework.*;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod3") @PrefixGameTestTemplate(false)
public final class Cod3ProtocolGameTests {
    @GameTest(template="bow_ritual_test")
    public static void wireSchemaRejectsMismatchedPeers(GameTestHelper h) {
        String local=DynastyNetwork.protocolVersion();
        h.assertTrue(local.contains("12=com.dynasty.cod3.Cod3VisualPacket:PLAY_TO_CLIENT:v1"),"Cod3 wire slot or direction missing");
        h.assertTrue(local.contains("17=com.dynasty.infusion.InfusionRequest:PLAY_TO_SERVER:v1"),"Infusion wire slot or direction missing");
        h.assertTrue(DynastyNetwork.acceptsProtocol(local),"Same schema rejected");
        h.assertTrue(!DynastyNetwork.acceptsProtocol("8"),"Ambiguous old protocol accepted");
        h.assertTrue(!DynastyNetwork.acceptsProtocol(local.replace("Cod3VisualPacket","EdictCastPacket")),"Different packet table accepted");
        h.assertTrue(!DynastyNetwork.acceptsProtocol(local.replace("PLAY_TO_CLIENT","PLAY_TO_SERVER")),"Wrong direction accepted");
        h.assertTrue(!DynastyNetwork.acceptsProtocol(local.replace(", 17=com.dynasty.infusion.InfusionRequest:PLAY_TO_SERVER:v1", "")),"Peer without infusion schema accepted");
        h.succeed();
    }
}
