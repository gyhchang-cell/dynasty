package com.dynasty.network;

import net.minecraft.gametest.framework.*;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod6") @PrefixGameTestTemplate(false)
public final class EdictProtocolGameTests {
    @GameTest(template="bow_ritual_test")
    public static void wireSchemaRejectsMismatchedPeers(GameTestHelper h) {
        String local=DynastyNetwork.protocolVersion();
        String schema=DynastyNetwork.protocolSchema();
        h.assertTrue(schema.contains("13=com.dynasty.network.EdictCastPacket:PLAY_TO_SERVER:v1")&&schema.contains("14=com.dynasty.network.EdictVisualPacket:PLAY_TO_CLIENT:v2"),"Edict slots or directions missing");
        h.assertTrue(!DynastyNetwork.acceptsProtocol(DynastyNetwork.fingerprintSchema(schema.replace("EdictVisualPacket:PLAY_TO_CLIENT:v2","EdictVisualPacket:PLAY_TO_CLIENT:v1"))),"Older visual packet must not be decoded with the holder-aware schema");
        h.assertTrue(DynastyNetwork.acceptsProtocol(local)&&!DynastyNetwork.acceptsProtocol("8"),"Schema handshake broken");
        String olderArmy=schema.replace("/army="+com.dynasty.army.ArmyMenu.LAYOUT_REVISION,
                "/army="+(com.dynasty.army.ArmyMenu.LAYOUT_REVISION-1));
        h.assertTrue(!olderArmy.equals(schema)&&!DynastyNetwork.acceptsProtocol(DynastyNetwork.fingerprintSchema(olderArmy)),"Older army menu accepted");
        h.assertTrue(!DynastyNetwork.acceptsProtocol(DynastyNetwork.fingerprintSchema(schema.replace("13=","12="))),"Shifted IDs accepted");
        var packet=new EdictVisualPacket(java.util.UUID.randomUUID(),2,123L,new net.minecraft.world.phys.Vec3(1,2,3),new net.minecraft.world.phys.Vec3(4,5,6),"dynasty:jiuxiao",41,java.util.UUID.randomUUID());
        var buffer=new net.minecraft.network.FriendlyByteBuf(io.netty.buffer.Unpooled.buffer());
        try {EdictVisualPacket.encode(packet,buffer);h.assertTrue(packet.equals(EdictVisualPacket.decode(buffer))&&buffer.readableBytes()==0,"Edict visual wire roundtrip");}
        finally {buffer.release();}
        h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void articulatedWhiskLagAndPacketBoundsAreFinite(GameTestHelper h){
        h.assertTrue(com.dynasty.DynastyWeapons.TAIYI_WHISK.get() instanceof com.dynasty.TaiyiWhiskItem,"Real registered weapon uses the articulated path");
        h.assertTrue(com.dynasty.WhiskPose.SEGMENTS==5,"Five parented silk segments");
        for(int windup:com.dynasty.EdictSpells.WINDUP){
            h.assertTrue(com.dynasty.WhiskPose.bend(2,windup,0)!=com.dynasty.WhiskPose.bend(2,windup,4),"Distal silk lags the root");
            for(int i=0;i<5;i++)for(double age:new double[]{0,windup*.5,windup,windup+6,windup+17}){
                float bend=com.dynasty.WhiskPose.bend(age,windup,i);h.assertTrue(Float.isFinite(bend)&&Math.abs(bend)<.6,"All actual spell timelines keep bounded bends");
            }
            h.assertTrue(com.dynasty.WhiskPose.bend(windup+17,windup,4)==0,"Completed cast returns to a stable resting pose");
        }
        var bad=new EdictVisualPacket(java.util.UUID.randomUUID(),6,0,net.minecraft.world.phys.Vec3.ZERO,net.minecraft.world.phys.Vec3.ZERO);
        h.assertTrue(!bad.valid(),"Out-of-range spell cannot index the pose timeline");
        var far=new EdictVisualPacket(java.util.UUID.randomUUID(),2,0,net.minecraft.world.phys.Vec3.ZERO,new net.minecraft.world.phys.Vec3(100,0,0));
        h.assertTrue(!far.valid(),"Visual packet cannot create an unbounded cast segment");h.succeed();
    }
}
