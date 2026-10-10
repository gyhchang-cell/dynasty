package com.dynasty.network;

import com.dynasty.DynastyItems;
import com.dynasty.army.ArmyRoster;
import com.dynasty.infusion.InfusionRequest;
import com.mojang.authlib.GameProfile;
import io.netty.buffer.Unpooled;
import io.netty.handler.codec.DecoderException;
import java.lang.reflect.*;
import java.util.*;
import java.util.function.Supplier;
import net.minecraft.gametest.framework.*;
import net.minecraft.network.*;
import net.minecraft.network.protocol.PacketFlow;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.gametest.*;
import net.minecraftforge.network.*;

/** Exercise Forge's registered discriminator/decoder/handler, not an alternate packet policy. */
@GameTestHolder("dynasty_network") @PrefixGameTestTemplate(false)
public final class NetworkIntentNativeGameTests {
    private static Object codec()throws Exception{
        var f=DynastyNetwork.CHANNEL.getClass().getDeclaredField("indexedCodec");f.setAccessible(true);return f.get(DynastyNetwork.CHANNEL);
    }
    private static NetworkEvent.Context context(Connection connection,NetworkDirection direction)throws Exception{
        var c=NetworkEvent.Context.class.getDeclaredConstructor(Connection.class,NetworkDirection.class,int.class);c.setAccessible(true);return c.newInstance(connection,direction,Integer.MIN_VALUE);
    }
    private static void consume(FriendlyByteBuf payload,NetworkEvent.Context context)throws Exception{
        var codec=codec();var method=codec.getClass().getDeclaredMethod("consume",FriendlyByteBuf.class,int.class,Supplier.class);method.setAccessible(true);
        try{method.invoke(codec,payload,Integer.MIN_VALUE,(Supplier<NetworkEvent.Context>)()->context);}
        catch(InvocationTargetException failure){if(failure.getCause() instanceof Exception cause)throw cause;throw failure;}
    }
    private static FriendlyByteBuf intent(int id){
        var b=new FriendlyByteBuf(Unpooled.buffer());b.writeByte(id);
        switch(id){
            case 4->AnswerKejuPacket.encode(new AnswerKejuPacket(31,2),b);
            case 5,7->StatsRequestPacket.encode(new StatsRequestPacket(),b);
            case 6->ArmyFormPacket.encode(new ArmyFormPacket(0,1),b);
            case 10->BountyActionPacket.encode(new BountyActionPacket("accept","unknown-instance"),b);
            case 13->EdictCastPacket.encode(new EdictCastPacket(),b);
            case 17->InfusionRequest.encode(new InfusionRequest(1,0,0,1),b);
            default->throw new IllegalArgumentException("Not a client intent");
        }return b;
    }
    @GameTest(template="bow_ritual_test",batch="network_direction_native",timeoutTicks=60)
    public static void actualForgeCodecRejectsOppositeAndLoginDirectionsForEveryOriginalOrdinalBeforeReadingBody(GameTestHelper h)throws Exception{
        String[] types={"DragonDescentPacket","WeaponImpactPacket","BowEffectPacket","OpenKejuPacket","AnswerKejuPacket","StatsRequestPacket","ArmyFormPacket","StatsRequestPacket","StatsSyncPacket","BountyBoardPacket","BountyActionPacket","BlueprintVisualEvent","Cod3VisualPacket","EdictCastPacket","EdictVisualPacket","WorldEventStatePacket","CombatFeedback","InfusionRequest"};
        var client=new HashSet<Integer>(List.of(0,1,2,3,8,9,11,12,14,15,16));
        var codec=codec();var find=codec.getClass().getDeclaredMethod("findIndex",short.class);find.setAccessible(true);
        for(int id=0;id<types.length;id++){
            var handler=find.invoke(codec,(short)id);h.assertTrue(handler!=null,"Original native ordinal exists: "+id);
            var field=handler.getClass().getDeclaredField("messageType");field.setAccessible(true);h.assertTrue(((Class<?>)field.get(handler)).getSimpleName().equals(types[id]),"Original packet identity unchanged at "+id);
            var allowed=client.contains(id)?NetworkDirection.PLAY_TO_CLIENT:NetworkDirection.PLAY_TO_SERVER;
            var direction=handler.getClass().getDeclaredField("networkDirection");direction.setAccessible(true);h.assertTrue(direction.get(handler).equals(Optional.of(allowed)),"Actual Forge registration restricts original message direction: "+id);
            for(var forbidden:new NetworkDirection[]{allowed==NetworkDirection.PLAY_TO_CLIENT?NetworkDirection.PLAY_TO_SERVER:NetworkDirection.PLAY_TO_CLIENT,NetworkDirection.LOGIN_TO_CLIENT,NetworkDirection.LOGIN_TO_SERVER}){
                var connection=new Connection(PacketFlow.SERVERBOUND);var b=new FriendlyByteBuf(Unpooled.buffer());b.writeByte(id);b.writeByte(255);
                try{
                    boolean rejected=false;try{consume(b,context(connection,forbidden));}catch(IllegalStateException expected){rejected=expected.getMessage().contains("Invalid packet received");}
                    h.assertTrue(rejected&&b.readerIndex()==1,"Forge rejects reverse/login packet before decoder or gameplay handler: ordinal="+id+" direction="+forbidden);
                }finally{b.release();}
            }
        }h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="network_fixed_intent_native",timeoutTicks=60)
    public static void actualRegisteredClientIntentsKeepLegalWireBodiesButRejectForeignIdentityPriceDimensionAndOversizedListExtensions(GameTestHelper h)throws Exception{
        for(int id:new int[]{4,5,6,7,10,13,17}){
            var legal=intent(id);try{
                var c=context(new Connection(PacketFlow.SERVERBOUND),NetworkDirection.PLAY_TO_SERVER);consume(legal,c);
                h.assertTrue(!legal.isReadable()&&c.getPacketHandled(),"Original fixed request is accepted by actual Forge decoder/handler: "+id);
            }finally{legal.release();}
            for(int extra=0;extra<5;extra++){
                var b=intent(id);switch(extra){
                    case 0->b.writeUUID(UUID.randomUUID());
                    case 1->b.writeInt(-1);
                    case 2->b.writeUtf("foreign:unavailable_dimension");
                    case 3->{b.writeVarInt(Integer.MAX_VALUE);b.writeZero(131072);}
                    case 4->b.writeByte(0);
                }
                try{
                    var c=context(new Connection(PacketFlow.SERVERBOUND),NetworkDirection.PLAY_TO_SERVER);boolean rejected=false;
                    try{consume(b,c);}catch(DecoderException expected){rejected=expected.getMessage().contains("Unexpected fields");}
                    h.assertTrue(rejected&&!c.getPacketHandled(),"Foreign identity/price/dimension/list/unknown field rejected before actual gameplay handler: ordinal="+id+" extension="+extra);
                }finally{b.release();}
            }
        }
        var oversized=new FriendlyByteBuf(Unpooled.buffer());oversized.writeByte(10);oversized.writeUtf("x".repeat(17));oversized.writeUtf("unknown-instance");
        try{boolean rejected=false;try{consume(oversized,context(new Connection(PacketFlow.SERVERBOUND),NetworkDirection.PLAY_TO_SERVER));}catch(DecoderException expected){rejected=true;}h.assertTrue(rejected,"Native bounded UTF decoder rejects an oversized action before request execution");}finally{oversized.release();}
        h.succeed();
    }
    private record NativePlayer(ServerPlayer player,Connection connection){}
    private static NativePlayer player(GameTestHelper h)throws Exception{
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"packet-native"));
        var connection=new Connection(PacketFlow.SERVERBOUND);p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),connection,p);connection.setListener(p.connection);return new NativePlayer(p,connection);
    }
    @GameTest(template="bow_ritual_test",batch="network_army_sender_native",timeoutTicks=60)
    public static void actualForgeArmyRequestUsesOnlyNativeSenderPaidRosterAndRejectsBoundsOrForeignTallyMetadata(GameTestHelper h)throws Exception{
        var ownerFixture=player(h);var strangerFixture=player(h);var owner=ownerFixture.player();var stranger=strangerFixture.player();
        try{
            for(int x=2;x<=14;x++)for(int z=1;z<=14;z++)for(int y=30;y<=35;y++)h.getLevel().setBlock(h.absolutePos(new net.minecraft.core.BlockPos(x,y,z)),(y==30?net.minecraft.world.level.block.Blocks.STONE:net.minecraft.world.level.block.Blocks.AIR).defaultBlockState(),18);
            owner.setPos(net.minecraft.world.phys.Vec3.atBottomCenterOf(h.absolutePos(new net.minecraft.core.BlockPos(8,31,3))));
            owner.getInventory().setItem(10,new ItemStack(DynastyItems.SILVER_COIN.get(),64));h.assertTrue(ArmyRoster.recruit(owner,0),"Original production transaction creates one paid identity");
            var record=ArmyRoster.soldiers(owner).getCompound(0);record.putInt("Slot",0);var id=record.getUUID("Id");
            var tally=new ItemStack(DynastyItems.TIGER_TALLY.get());tally.getOrCreateTag().putUUID("Owner",owner.getUUID());tally.getOrCreateTag().putUUID("soldierId",id);tally.getOrCreateTag().putString("dimension","foreign:unavailable_dimension");
            stranger.setItemInHand(InteractionHand.MAIN_HAND,tally);owner.setItemInHand(InteractionHand.MAIN_HAND,tally.copy());
            ArmyRoster.data(stranger);var paidBefore=ArmyRoster.data(owner).copy();var strangerBefore=ArmyRoster.data(stranger).copy();var inventoryBefore=owner.getInventory().save(new net.minecraft.nbt.ListTag());
            for(int[] request:new int[][]{{0,1},{0,9},{-1,1},{5,1},{Integer.MAX_VALUE,1},{0,-1},{0,0},{0,10},{0,Integer.MAX_VALUE}}){
                var b=new FriendlyByteBuf(Unpooled.buffer());b.writeByte(6);ArmyFormPacket.encode(new ArmyFormPacket(request[0],request[1]),b);
                try{consume(b,context(strangerFixture.connection(),NetworkDirection.PLAY_TO_SERVER));}finally{b.release();}
                h.assertTrue(ArmyRoster.data(owner).equals(paidBefore)&&ArmyRoster.data(stranger).equals(strangerBefore)&&owner.getInventory().save(new net.minecraft.nbt.ListTag()).equals(inventoryBefore),"Native sender cannot access another player's paid asset through copied tally metadata or invalid formation/count");
            }
            owner.setItemInHand(InteractionHand.MAIN_HAND,ItemStack.EMPTY);var b=intent(6);try{consume(b,context(ownerFixture.connection(),NetworkDirection.PLAY_TO_SERVER));}finally{b.release();}
            h.assertTrue(ArmyRoster.data(owner).equals(paidBefore),"Owner lacking original tally authority cannot deploy through native custom packet");
            owner.setItemInHand(InteractionHand.MAIN_HAND,tally.copy());
            for(int[] bad:new int[][]{{-1,1},{5,1},{Integer.MAX_VALUE,1},{0,-1},{0,0},{0,10},{0,Integer.MAX_VALUE}}){
                var invalid=new FriendlyByteBuf(Unpooled.buffer());invalid.writeByte(6);ArmyFormPacket.encode(new ArmyFormPacket(bad[0],bad[1]),invalid);
                try{consume(invalid,context(ownerFixture.connection(),NetworkDirection.PLAY_TO_SERVER));}finally{invalid.release();}
                h.assertTrue(ArmyRoster.data(owner).equals(paidBefore),"Bounds rejection occurs with an actual paid owner and physically valid native deployment site");
            }
            var valid=intent(6);try{consume(valid,context(ownerFixture.connection(),NetworkDirection.PLAY_TO_SERVER));}finally{valid.release();}
            h.assertTrue(record.getString("State").equals("DEPLOYED")&&record.hasUUID("Entity")&&record.getLong("Generation")==1&&ArmyRoster.data(stranger).equals(strangerBefore),"Same actual Forge decoder/handler legally deploys exactly the owner's original paid soldier when authority and bounds are valid");
            h.succeed();
        }finally{for(var p:List.of(owner,stranger)){ArmyRoster.recall(p);net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent(p));com.dynasty.DynastyTrinkets.forget(p);p.discard();}}
    }
    private NetworkIntentNativeGameTests(){}
}
