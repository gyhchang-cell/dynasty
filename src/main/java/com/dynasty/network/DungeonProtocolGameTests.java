package com.dynasty.network;

import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import net.minecraftforge.network.NetworkRegistry;

/** Read the actual Forge handshake snapshot, not just Dynasty's version helper. */
@GameTestHolder("dynasty_cod2")
@PrefixGameTestTemplate(false)
public final class DungeonProtocolGameTests {
    @GameTest(template="bow_ritual_test")
    public static void frozenForgeChannelAcceptsItsOwnCompleteWireTable(GameTestHelper h) throws Exception {
        var method=NetworkRegistry.class.getDeclaredMethod("buildChannelVersions");
        method.setAccessible(true);
        var channels=(java.util.Map<?,?>)method.invoke(null);
        var advertised=(String)channels.get(new ResourceLocation("dynasty:dynasty"));
        h.assertTrue(advertised!=null&&advertised.equals(DynastyNetwork.protocolVersion()),"Forge cached an incomplete wire table");
        h.assertTrue(DynastyNetwork.acceptsProtocol(advertised),"Own advertised channel version rejected");
        String schema=DynastyNetwork.protocolSchema();
        h.assertTrue(schema.contains("12=com.dynasty.cod3.Cod3VisualPacket:PLAY_TO_CLIENT:v1")
            &&schema.contains("13=com.dynasty.network.EdictCastPacket:PLAY_TO_SERVER:v1")
            &&schema.contains("14=com.dynasty.network.EdictVisualPacket:PLAY_TO_CLIENT:v2")
            &&schema.contains("17=com.dynasty.infusion.InfusionRequest:PLAY_TO_SERVER:v1"),"Merged packet identities missing");
        for(String remote:new String[]{"8","9/{}",schema.replace("13=","15="),
                schema.replace(", 17=com.dynasty.infusion.InfusionRequest:PLAY_TO_SERVER:v1", ""),
                schema.replace("PLAY_TO_SERVER","PLAY_TO_CLIENT"),schema.replace(":v1",":v2")})
            h.assertTrue(!DynastyNetwork.acceptsProtocol(DynastyNetwork.fingerprintSchema(remote)),"Incompatible peer accepted: "+remote);
        h.succeed();
    }
}
