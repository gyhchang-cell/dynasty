package com.dynasty.network;

import net.minecraft.gametest.framework.*;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_infusion") @PrefixGameTestTemplate(false)
public final class InfusionProtocolGameTests {
    @GameTest(template="bow_ritual_test")
    public static void infusionSchemaPreservesOtherExtensionsAndRejectsMismatchedPeers(GameTestHelper h) {
        String local=DynastyNetwork.protocolVersion();
        String schema=DynastyNetwork.protocolSchema();
        String infusion="17=com.dynasty.infusion.InfusionRequest:PLAY_TO_SERVER:v1";
        h.assertTrue(schema.contains(infusion),"Infusion wire slot/direction/revision missing");
        h.assertTrue(schema.contains("12=com.dynasty.cod3.Cod3VisualPacket:PLAY_TO_CLIENT:v1"),"Cod3 packet overwritten");
        h.assertTrue(schema.contains("13=com.dynasty.network.EdictCastPacket:PLAY_TO_SERVER:v1"),"Edict request overwritten");
        h.assertTrue(schema.contains("14=com.dynasty.network.EdictVisualPacket:PLAY_TO_CLIENT:v2"),"Edict feedback overwritten");
        h.assertTrue(DynastyNetwork.acceptsProtocol(local),"Same schema rejected");
        h.assertTrue(!DynastyNetwork.acceptsProtocol("8"),"Legacy schema accepted");
        h.assertTrue(!DynastyNetwork.acceptsProtocol(DynastyNetwork.fingerprintSchema(schema.replace(infusion,""))),"Peer missing infusion accepted");
        h.assertTrue(!DynastyNetwork.acceptsProtocol(DynastyNetwork.fingerprintSchema(schema.replace(infusion,infusion.replace("17=","12=")))),"Colliding infusion ID accepted");
        h.assertTrue(!DynastyNetwork.acceptsProtocol(DynastyNetwork.fingerprintSchema(schema.replace(infusion,infusion.replace("PLAY_TO_SERVER","PLAY_TO_CLIENT")))),"Wrong infusion direction accepted");
        h.assertTrue(!DynastyNetwork.acceptsProtocol(DynastyNetwork.fingerprintSchema(schema.replace(infusion,infusion.replace(":v1",":v2")))),"Different payload revision accepted");
        h.succeed();
    }
}
