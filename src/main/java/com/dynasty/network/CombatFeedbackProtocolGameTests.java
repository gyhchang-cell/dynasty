package com.dynasty.network;

import net.minecraft.gametest.framework.*;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class CombatFeedbackProtocolGameTests {
    @GameTest(template="bow_ritual_test")
    public static void wireSchemaRejectsMismatchedPeers(GameTestHelper h) {
        String local=DynastyNetwork.protocolVersion();
        String schema=DynastyNetwork.protocolSchema();
        h.assertTrue(schema.contains("16=com.dynasty.expansion.CombatFeedback:PLAY_TO_CLIENT:v2"),"Combat feedback wire slot or direction missing");
        h.assertTrue(DynastyNetwork.acceptsProtocol(local),"Same schema rejected");
        h.assertTrue(!DynastyNetwork.acceptsProtocol("8"),"Ambiguous old protocol accepted");
        h.assertTrue(!DynastyNetwork.acceptsProtocol(DynastyNetwork.fingerprintSchema(schema.replace("CombatFeedback","EdictCastPacket"))),"Different packet table accepted");
        h.assertTrue(!DynastyNetwork.acceptsProtocol(DynastyNetwork.fingerprintSchema(schema.replace("PLAY_TO_CLIENT","PLAY_TO_SERVER"))),"Wrong direction accepted");
        h.succeed();
    }
}
