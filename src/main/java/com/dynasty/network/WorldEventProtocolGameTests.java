package com.dynasty.network;

import net.minecraft.gametest.framework.*;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod2") @PrefixGameTestTemplate(false)
public final class WorldEventProtocolGameTests {
    @GameTest(template="bow_ritual_test")
    public static void wireSchemaRejectsMismatchedPeers(GameTestHelper h) {
        String local=DynastyNetwork.protocolVersion();
        String schema=DynastyNetwork.protocolSchema();
        h.assertTrue(schema.contains("15=com.dynasty.worldevent.WorldEventStatePacket:PLAY_TO_CLIENT:v1"),"World event wire slot or direction missing");
        h.assertTrue(DynastyNetwork.acceptsProtocol(local),"Same schema rejected");
        h.assertTrue(!DynastyNetwork.acceptsProtocol("8"),"Ambiguous old protocol accepted");
        h.assertTrue(!DynastyNetwork.acceptsProtocol(DynastyNetwork.fingerprintSchema(schema.replace("WorldEventStatePacket","EdictCastPacket"))),"Different packet table accepted");
        h.assertTrue(!DynastyNetwork.acceptsProtocol(DynastyNetwork.fingerprintSchema(schema.replace("PLAY_TO_CLIENT","PLAY_TO_SERVER"))),"Wrong direction accepted");
        h.succeed();
    }
}
