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
        h.assertTrue(advertised.contains("12=com.dynasty.cod3.Cod3VisualPacket:PLAY_TO_CLIENT:v1")
            &&advertised.contains("13=com.dynasty.network.EdictCastPacket:PLAY_TO_SERVER:v1")
            &&advertised.contains("14=com.dynasty.network.EdictVisualPacket:PLAY_TO_CLIENT:v1")
            &&advertised.contains("17=com.dynasty.infusion.InfusionRequest:PLAY_TO_SERVER:v1"),"Merged packet identities missing");
        for(String remote:new String[]{"8","9/{}",advertised.replace("13=","15="),
                advertised.replace("17=com.dynasty.infusion.InfusionRequest:PLAY_TO_SERVER:v1", ""),
                advertised.replace("PLAY_TO_SERVER","PLAY_TO_CLIENT"),advertised.replace(":v1",":v2")})
            h.assertTrue(!DynastyNetwork.acceptsProtocol(remote),"Incompatible peer accepted: "+remote);
        h.succeed();
    }
}
