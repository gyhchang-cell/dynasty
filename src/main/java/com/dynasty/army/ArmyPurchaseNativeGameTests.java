package com.dynasty.army;
import com.dynasty.*;
import com.mojang.authlib.GameProfile;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.network.protocol.game.ServerboundContainerButtonClickPacket;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.storage.*;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;
/** Native menu packets and actual player-data files simulate pre/post-confirm restart, without a client GUI claim. */
@GameTestHolder("dynasty_army") @PrefixGameTestTemplate(false)
public final class ArmyPurchaseNativeGameTests {
    private static ServerPlayer player(GameTestHelper h,GameProfile profile,BlockPos desk){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),profile);p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.setPos(Vec3.atBottomCenterOf(desk.north(2)));return p;
    }
    private static ArmyMenu open(GameTestHelper h,ServerPlayer p,BlockPos desk){
        p.gameMode.useItemOn(p,h.getLevel(),p.getMainHandItem(),InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(desk),Direction.UP,desk,false));
        h.assertTrue(p.containerMenu instanceof ArmyMenu,"Actual native block-use opens original server recruitment menu");return (ArmyMenu)p.containerMenu;
    }
    private static void packet(ServerPlayer p,ArmyMenu menu,int code){p.connection.handleContainerButtonClick(new ServerboundContainerButtonClickPacket(menu.containerId,code));}
    private static void close(ServerPlayer p){p.closeContainer();net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent(p));DynastyTrinkets.forget(p);p.discard();}
    @GameTest(template="bow_ritual_test",batch="army_purchase_native_disk",setupTicks=20,timeoutTicks=160)
    public static void actualDeskUseAndNativeButtonPacketsKeepThreeRolesAtomicAcrossPreAndPostConfirmPlayerDataRestart(GameTestHelper h)throws Exception{
        var desk=h.absolutePos(new BlockPos(6,2,6));h.getLevel().setBlockAndUpdate(desk,ArmyContent.DESK.get().defaultBlockState());
        var base=LevelStorageSource.createDefault(h.getLevel().getServer().getWorldPath(LevelResource.ROOT).resolve("native-purchase-qa"));
        for(int role=0;role<3;role++){
            var profile=new GameProfile(UUID.randomUUID(),"purchase-native");var p=player(h,profile,desk);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyItems.TIGER_TALLY.get()));p.setItemInHand(InteractionHand.OFF_HAND,new ItemStack(DynastyItems.TIGER_TALLY.get()));
            var coins=new ItemStack(DynastyItems.SILVER_COIN.get(),64);coins.getOrCreateTag().putString("NativeForeignCoinTag","unchanged");p.getInventory().setItem(10,coins);
            String before="before-"+role,after="after-"+role;UUID paid;int code;
            try{
                try(var access=base.createAccess(before)){access.createPlayerStorage().save(p);}
                var menu=open(h,p,desk);code=(menu.view.get(2)<<8)|role;packet(p,menu,code);
                h.assertTrue(ArmyRoster.coins(p)==64-ArmyRoster.PRICE[role]&&ArmyRoster.soldiers(p).size()==1,"Actual native menu packet pays exact original silver price and creates one original role");
                var record=ArmyRoster.soldiers(p).getCompound(0);paid=record.getUUID("Id");h.assertTrue(record.getInt("Role")==role&&record.getString("State").equals("RESERVE")&&record.getFloat("Health")==ArmyRoster.HEALTH[role]&&record.getInt("Slot")==-1,"Actual paid soldier identity/role/health/reserve remains original");
                packet(p,menu,code);h.assertTrue(ArmyRoster.coins(p)==64-ArmyRoster.PRICE[role]&&ArmyRoster.soldiers(p).size()==1,"Repeated actual native button packet cannot charge or create again");
                try(var access=base.createAccess(after)){access.createPlayerStorage().save(p);}
                p.closeContainer();
                var pre=player(h,profile,desk);try(var access=base.createAccess(before)){
                    h.assertTrue(access.createPlayerStorage().load(pre)!=null&&ArmyRoster.coins(pre)==64&&ArmyRoster.soldiers(pre).isEmpty(),"Actual before-confirm player-data file reload restores no payment and no soldier, not half a transaction");
                    var preMenu=open(h,pre,desk);packet(pre,preMenu,(preMenu.view.get(2)<<8)|role);h.assertTrue(ArmyRoster.coins(pre)==64-ArmyRoster.PRICE[role]&&ArmyRoster.soldiers(pre).size()==1,"Before-confirm restart allows exactly one fresh legal transaction");
                }finally{close(pre);}
                var post=player(h,profile,desk);try(var access=base.createAccess(after)){
                    h.assertTrue(access.createPlayerStorage().load(post)!=null&&ArmyRoster.coins(post)==64-ArmyRoster.PRICE[role]&&ArmyRoster.soldiers(post).size()==1&&ArmyRoster.find(post,paid)!=null&&post.getInventory().getItem(10).getOrCreateTag().getString("NativeForeignCoinTag").equals("unchanged"),"Actual after-confirm native player-data file preserves payment, unique paid identity and foreign inventory NBT together");
                    var postMenu=open(h,post,desk);h.assertTrue(postMenu.view.get(2)!=(code>>>8),"Persisted original menu revision advances across actual file reload and menu recreation");packet(post,postMenu,code);
                    h.assertTrue(ArmyRoster.coins(post)==64-ArmyRoster.PRICE[role]&&ArmyRoster.soldiers(post).size()==1&&ArmyRoster.find(post,paid)!=null,"Actual pre-restart native button code replayed against new current container is stale, no second payment/asset");
                }finally{close(post);}
            }finally{close(p);}
        }h.succeed();
    }
}
