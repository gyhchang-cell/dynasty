package com.dynasty.network;

import net.minecraft.gametest.framework.*;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod6") @PrefixGameTestTemplate(false)
public final class EdictProtocolGameTests {
    @GameTest(template="bow_ritual_test")
    public static void wireSchemaRejectsMismatchedPeers(GameTestHelper h) {
        String local=DynastyNetwork.protocolVersion();
        String schema=DynastyNetwork.protocolSchema();
        h.assertTrue(schema.contains("13=com.dynasty.network.EdictCastPacket:PLAY_TO_SERVER:v1")&&schema.contains("14=com.dynasty.network.EdictVisualPacket:PLAY_TO_CLIENT:v1"),"Edict slots or directions missing");
        h.assertTrue(DynastyNetwork.acceptsProtocol(local)&&!DynastyNetwork.acceptsProtocol("8"),"Schema handshake broken");
        String olderArmy=schema.replace("/army="+com.dynasty.army.ArmyMenu.LAYOUT_REVISION,
                "/army="+(com.dynasty.army.ArmyMenu.LAYOUT_REVISION-1));
        h.assertTrue(!olderArmy.equals(schema)&&!DynastyNetwork.acceptsProtocol(DynastyNetwork.fingerprintSchema(olderArmy)),"Older army menu accepted");
        h.assertTrue(!DynastyNetwork.acceptsProtocol(DynastyNetwork.fingerprintSchema(schema.replace("13=","12="))),"Shifted IDs accepted");
        var packet=new EdictVisualPacket(java.util.UUID.randomUUID(),2,123L,new net.minecraft.world.phys.Vec3(1,2,3),new net.minecraft.world.phys.Vec3(4,5,6));
        var buffer=new net.minecraft.network.FriendlyByteBuf(io.netty.buffer.Unpooled.buffer());
        try {EdictVisualPacket.encode(packet,buffer);h.assertTrue(packet.equals(EdictVisualPacket.decode(buffer))&&buffer.readableBytes()==0,"Edict visual wire roundtrip");}
        finally {buffer.release();}
        h.succeed();
    }
}
