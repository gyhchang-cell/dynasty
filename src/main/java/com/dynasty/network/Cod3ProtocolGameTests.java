package com.dynasty.network;

import net.minecraft.gametest.framework.*;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod3") @PrefixGameTestTemplate(false)
public final class Cod3ProtocolGameTests {
    @GameTest(template="bow_ritual_test")
    public static void wireSchemaRejectsMismatchedPeers(GameTestHelper h) {
        String local=DynastyNetwork.protocolVersion();
        String schema=DynastyNetwork.protocolSchema();
        h.assertTrue(schema.contains("12=com.dynasty.cod3.Cod3VisualPacket:PLAY_TO_CLIENT:v1"),"Cod3 wire slot or direction missing");
        h.assertTrue(DynastyNetwork.acceptsProtocol(local),"Same schema rejected");
        h.assertTrue(!DynastyNetwork.acceptsProtocol("8"),"Ambiguous old protocol accepted");
        h.assertTrue(!DynastyNetwork.acceptsProtocol(DynastyNetwork.fingerprintSchema(schema.replace("Cod3VisualPacket","EdictCastPacket"))),"Different packet table accepted");
        h.assertTrue(!DynastyNetwork.acceptsProtocol(DynastyNetwork.fingerprintSchema(schema.replace("PLAY_TO_CLIENT","PLAY_TO_SERVER"))),"Wrong direction accepted");
        h.succeed();
    }
}
