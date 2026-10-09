package com.dynasty.expansion;

import com.dynasty.cod3.SecretTracker;
import com.mojang.authlib.GameProfile;
import java.util.UUID;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class WellSecretGameTests {
    private static ServerPlayer player(GameTestHelper h){return player(h,new GameProfile(UUID.randomUUID(),"well-native"));}
    private static ServerPlayer player(GameTestHelper h,GameProfile profile){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),profile);
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(3,2,3))));return p;
    }
    private static BlockPos well(GameTestHelper h){var at=h.absolutePos(new BlockPos(3,2,3));h.getLevel().setBlockAndUpdate(at,SmallInteractions.ENTRIES.get("ancient_well").get().defaultBlockState());return at;}
    private static void use(GameTestHelper h,ServerPlayer p,BlockPos at){h.getLevel().getBlockState(at).use(h.getLevel(),p,InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(at),Direction.UP,at,false));}
    private static void ready(ServerPlayer p){var root=EquipmentBehaviors.saved(p);root.putLong("site_ancient_well_start",p.level().getGameTime()-3600);root.putLong("site_ancient_well_next",p.level().getGameTime());}
    @GameTest(template="bow_ritual_test",batch="cod4_well_native",setupTicks=20)
    public static void emptyBucketProximityAndOriginalDeadlineCannotBeBypassed(GameTestHelper h){
        var p=player(h);var at=well(h);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.BUCKET));use(h,p,at);
        h.assertTrue(!EquipmentBehaviors.saved(p).contains("site_ancient_well_start"),"Empty bucket starts no paid delivery sequence");
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.WATER_BUCKET));use(h,p,at);var root=EquipmentBehaviors.saved(p);long now=h.getLevel().getGameTime();
        h.assertTrue(root.getLong("site_ancient_well_start")==now&&root.getLong("site_ancient_well_next")==now+515,"Original three-minute duration is divided into seven actual delivery intervals");
        use(h,p,at);h.assertTrue(p.getMainHandItem().is(Items.WATER_BUCKET)&&root.getInt("site_ancient_well_count")==0,"Starting/spamming before the first deadline consumes no water and adds no counter");
        ready(p);p.setPos(p.getX()+30,p.getY(),p.getZ());var far=SecretTracker.deliverWellWater(p,at);h.assertTrue(!far.accepted()&&!far.claimed()&&p.getMainHandItem().is(Items.WATER_BUCKET),"Adapter rejects a remote player before consuming or claiming");
        p.setPos(Vec3.atBottomCenterOf(at));h.getLevel().setBlockAndUpdate(at,Blocks.STONE.defaultBlockState());h.assertTrue(!SecretTracker.deliverWellWater(p,at).accepted(),"Removed/non-Site context cannot act as a fake secret anchor");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_well_deliveries",setupTicks=20,timeoutTicks=120)
    public static void sevenActualWaterBucketsCompleteOriginalTaskAndNativeSecretOnce(GameTestHelper h){
        var p=player(h);var at=well(h);for(int i=0;i<8;i++)p.getInventory().setItem(i,new ItemStack(Items.WATER_BUCKET));
        p.addEffect(new MobEffectInstance(ExpansionEffects.YIN.get(),1000));p.addEffect(new MobEffectInstance(ExpansionEffects.SOUL.get(),1000));use(h,p,at);ready(p);
        for(int i=0;i<7;i++){final int step=i;h.runAtTickTime(1+i*10,()->{
            p.getInventory().selected=step;EquipmentBehaviors.saved(p).putLong("site_ancient_well_next",h.getLevel().getGameTime());use(h,p,at);
            h.assertTrue(p.getMainHandItem().is(Items.BUCKET)&&p.getInventory().countItem(Items.BUCKET)==step+1,"Each accepted step consumes exactly its selected actual water bucket and retains empty buckets");
            h.assertTrue(p.getPersistentData().getCompound("cod3_progress_8").getInt("Count")==step+1,"Original native secret counter owns real deliveries");
            if(step<6)h.assertTrue(!EquipmentBehaviors.saved(p).getBoolean("site_ancient_well_done")&&p.getInventory().countItem(ExpansionContent.item("jade"))==0,"Partial deliveries cannot manufacture completion/reward");
            else{
                h.assertTrue(EquipmentBehaviors.saved(p).getBoolean("site_ancient_well_done")&&SecretTracker.wellClaimed(p)&&p.getInventory().countItem(ExpansionContent.item("jade"))==1,"Seven deliveries finish the original Site and exactly one native secret reward");
                h.assertTrue(!p.hasEffect(ExpansionEffects.YIN.get())&&!p.hasEffect(ExpansionEffects.SOUL.get()),"Original completed-site cleanse remains");
                var adv=p.server.getAdvancements().getAdvancement(new net.minecraft.resources.ResourceLocation("dynasty","cod4_ancient_well"));h.assertTrue(p.getAdvancements().getOrStartProgress(adv).isDone(),"Actual existing optional FTB advancement hook is awarded");
                p.getInventory().selected=7;use(h,p,at);h.assertTrue(p.getMainHandItem().is(Items.WATER_BUCKET)&&p.getInventory().countItem(ExpansionContent.item("jade"))==1,"Reusing a completed well never consumes the eighth bucket or repeats its reward");
                var q=player(h,p.getGameProfile());SecretTracker.clone(new PlayerEvent.Clone(q,p,true));q.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.WATER_BUCKET));use(h,q,at);
                h.assertTrue(SecretTracker.wellClaimed(q)&&q.getMainHandItem().is(Items.WATER_BUCKET)&&q.getInventory().countItem(ExpansionContent.item("jade"))==0,"Actual clone preserves the native persistent claim without rewarding again");h.succeed();
            }
        });}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_well_native",setupTicks=20)
    public static void seventhDeliveryStillRequiresThreeMinutesAndProofCannotBeForgedByOldCounter(GameTestHelper h){
        var p=player(h);var at=well(h);var root=EquipmentBehaviors.saved(p);long now=h.getLevel().getGameTime();
        root.putInt("site_ancient_well_count",7);root.putLong("site_ancient_well_start",now-100);root.putLong("site_ancient_well_next",now);
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.WATER_BUCKET));h.assertTrue(!SecretTracker.get(h.getLevel()).claim(p,8,at),"Old generic seven-count field alone cannot claim a native reward");
        var nativeProgress=new CompoundTag();nativeProgress.putLong("Anchor",at.asLong());nativeProgress.putInt("Count",6);nativeProgress.putLong("Last",now-10);p.getPersistentData().put("cod3_progress_8",nativeProgress);
        use(h,p,at);h.assertTrue(p.getMainHandItem().is(Items.WATER_BUCKET)&&nativeProgress.getInt("Count")==6&&!SecretTracker.wellClaimed(p),"Seventh water is not consumed before original total duration even if the interval field is overdue");
        ready(p);use(h,p,at);h.assertTrue(p.getMainHandItem().is(Items.BUCKET)&&SecretTracker.wellClaimed(p)&&p.getInventory().countItem(ExpansionContent.item("jade"))==1,"Original persisted native partial progress completes after the real deadline, without resetting six deliveries");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_well_legacy",setupTicks=20,timeoutTicks=120)
    public static void legacyCompletedSiteKeepsItsRewardHistoryWhileMissingNativeSecretIsEarned(GameTestHelper h){
        var p=player(h);var other=player(h);var at=well(h);var root=EquipmentBehaviors.saved(p);root.putBoolean("site_ancient_well_done",true);root.putInt("site_ancient_well_count",7);ready(p);
        p.addEffect(new MobEffectInstance(ExpansionEffects.YIN.get(),1000));p.getInventory().setItem(9,new ItemStack(ExpansionContent.item("copper_coin"),2));
        for(int i=0;i<7;i++){p.getInventory().setItem(i,new ItemStack(Items.WATER_BUCKET));final int step=i;h.runAtTickTime(1+i*10,()->{
            p.getInventory().selected=step;root.putLong("site_ancient_well_next",h.getLevel().getGameTime());use(h,p,at);
            h.assertTrue(root.getBoolean("site_ancient_well_done")&&root.getInt("site_ancient_well_count")==7,"Legacy completion and counters are never rolled back during actual missing-secret steps");
            if(step==6){
                h.assertTrue(SecretTracker.wellClaimed(p)&&p.getInventory().countItem(ExpansionContent.item("jade"))==1&&p.getInventory().countItem(ExpansionContent.item("copper_coin"))==2&&p.hasEffect(ExpansionEffects.YIN.get()),"Only newly earned original native reward is added; old site items and cleanse are not replayed");
                h.assertTrue(!SecretTracker.wellClaimed(other)&&!EquipmentBehaviors.saved(other).getBoolean("site_ancient_well_done"),"Detached second test character has independent original player-scope claims; real network multiplayer remains pending");h.succeed();
            }
        });}
    }
}
