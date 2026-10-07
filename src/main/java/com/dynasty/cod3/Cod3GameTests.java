package com.dynasty.cod3;

import com.dynasty.*;
import com.dynasty.entity.DynastyEntities;
import com.dynasty.workshop.*;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.entity.Mob;
import net.minecraftforge.common.capabilities.ForgeCapabilities;
import net.minecraftforge.gametest.*;
import java.util.*;

@GameTestHolder("dynasty_cod3")
@PrefixGameTestTemplate(false)
public final class Cod3GameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void stationAutomationAndPartialOutput(GameTestHelper h){
        h.setBlock(new BlockPos(2,2,2),DynastyBlocks.HERBAL_BASIN.get());var be=(WorkshopBlockEntity)h.getBlockEntity(new BlockPos(2,2,2));
        var in=be.getCapability(ForgeCapabilities.ITEM_HANDLER,Direction.UP).orElseThrow(()->new AssertionError("No input capability"));
        var out=be.getCapability(ForgeCapabilities.ITEM_HANDLER,Direction.DOWN).orElseThrow(()->new AssertionError("No output capability"));
        h.assertTrue(in.extractItem(0,1,false).isEmpty(),"Hopper pulled input");
        h.assertTrue(!in.insertItem(0,new ItemStack(Items.DIRT),false).isEmpty(),"Invalid item accepted");
        for(var cost:be.recipe().costs())h.assertTrue(in.insertItem(0,cost.stack(),false).isEmpty(),"Valid hopper input rejected");
        h.assertTrue(be.ready(),"Hopper failed to finish same recipe");
        h.assertTrue(out.extractItem(0,1,true).getCount()==1&&be.getItem(3).getCount()==2,"Simulation changed output");
        h.assertTrue(out.extractItem(0,1,false).getCount()==1&&be.ready(),"Partial output reset progress too soon");
        var saved=be.saveWithoutMetadata();be.load(saved);h.assertTrue(be.getItem(3).getCount()==1,"Reload duplicated partial output");
        h.assertTrue(out.extractItem(0,64,false).getCount()==1&&!be.ready(),"Last output did not reset");
        h.assertTrue(out.extractItem(0,64,false).isEmpty(),"Duplicate hopper extraction");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void legacyStationMigrationAndMixedInput(GameTestHelper h){
        int i=0;
        for(var recipe:WorkshopRecipes.ALL){
            var p=new BlockPos(1+i%4,2,1+i/4);i++;var item=new WorkshopRecipes.Cost("dynasty:"+recipe.station(),1).stack();h.setBlock(p,((BlockItem)item.getItem()).getBlock());var be=(WorkshopBlockEntity)h.getBlockEntity(p);
            var old=new CompoundTag();old.putString("Recipe",recipe.output());old.putInt("Deposited",recipe.total());be.load(old);
            h.assertTrue(be.ready()&&be.getItem(3).getCount()==recipe.count(),"Legacy complete output not migrated");h.assertTrue(!be.collect().isEmpty()&&be.collect().isEmpty(),"Legacy output duplicated");
            var first=recipe.costs().get(0).stack();h.assertTrue(be.accept(first),"Hand deposit failed");
            for(var cost:recipe.costs()){var stack=cost.stack();if(cost==recipe.costs().get(0))stack.shrink(1);be.setItem(0,stack);}
            h.assertTrue(be.ready(),"Hand/GUI inputs use different counters");
            var copy=new WorkshopBlockEntity(be.getBlockPos(),be.getBlockState());copy.handleUpdateTag(be.getUpdateTag());h.assertTrue(copy.deposited()==be.deposited(),"Client progress differs");
        }h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=400)
    public static void sixIntrosFinishWithoutFreezingPlayers(GameTestHelper h){
        var types=List.of(DynastyEntities.DRAGON_EMPEROR.get(),DynastyEntities.REBEL_GENERAL.get(),DynastyEntities.EUNUCH_MASTERMIND.get(),DynastyEntities.UNDEAD_FIRST_EMPEROR.get(),DynastyEntities.NINE_HEAVEN_GENERAL.get(),DynastyEntities.DRAGON_KING.get());
        var bosses=new ArrayList<Mob>();int i=0;
        for(var type:types){Mob boss=type.create(h.getLevel());boss.moveTo(h.absolutePos(new BlockPos(1+i%3,2,1+i/3)),0,0);i++;h.getLevel().addFreshEntity(boss);h.assertTrue(BossSequenceRunner.start(boss),"Missing altar intro binding");h.assertTrue(!BossSequenceRunner.start(boss),"Started twice");bosses.add(boss);}
        h.runAtTickTime(340,()->{for(var b:bosses){h.assertTrue(!BossSequenceRunner.active(b)&&!b.isNoAi()&&!b.isInvulnerable(),"Boss stuck in intro: "+b.getType());b.discard();}h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void introRestoresAndWatchdogUnlocks(GameTestHelper h){
        var type=DynastyEntities.DRAGON_KING.get();var boss=type.create(h.getLevel());BossSequenceRunner.start(boss);
        boss.getPersistentData().getCompound(BossSequenceRunner.KEY).putInt("Tick",100);var saved=boss.saveWithoutId(new CompoundTag());
        var copy=type.create(h.getLevel());copy.load(saved);BossSequenceRunner.tick(copy);
        h.assertTrue(copy.getPersistentData().getCompound(BossSequenceRunner.KEY).getInt("Tick")==101&&copy.isInvulnerable(),"Lost intro checkpoint");
        copy.getPersistentData().getCompound(BossSequenceRunner.KEY).putInt("Watchdog",400);BossSequenceRunner.tick(copy);
        h.assertTrue(!copy.isInvulnerable()&&!copy.isNoAi(),"Watchdog left boss locked");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void canceledDeathAndWorldFlagsRemainSafe(GameTestHelper h){
        var boss=DynastyEntities.REBEL_GENERAL.get().create(h.getLevel());
        var death=new net.minecraftforge.event.entity.living.LivingDeathEvent(boss,boss.damageSources().genericKill());
        BossDeathState.death(death);h.assertTrue(BossDeathState.managed(boss),"Missing death marker");death.setCanceled(true);BossDeathState.canceledDeath(death);
        h.assertTrue(!BossDeathState.managed(boss)&&!boss.isNoAi()&&!boss.isInvulnerable(),"Canceled death left a frozen boss");
        var world=Cod3WorldState.get(h.getLevel());world.unlock(h.getLevel(),"world_02");h.assertTrue(world.unlocked("world_02")&&!world.unlock(h.getLevel(),"world_02"),"World state broadcast repeated");
        var npc=NpcContent.NPCS.get("lao_chen").get().create(h.getLevel());h.assertTrue(npc.worldChanged(),"NPC ignored restored world state");
        var p=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"cod3-menu"));
        h.setBlock(new BlockPos(2,2,2),DynastyBlocks.MARROW_VAT.get());var be=(WorkshopBlockEntity)h.getBlockEntity(new BlockPos(2,2,2));p.setPos(be.getBlockPos().getX(),be.getBlockPos().getY(),be.getBlockPos().getZ());
        var a=new WorkshopMenu(1,p.getInventory(),be,be.data);var b=new WorkshopMenu(2,p.getInventory(),be,be.data);
        var input=be.recipe().costs().get(0).stack();be.accept(input);h.assertTrue(a.deposited()==b.deposited()&&a.deposited()==1,"Menus do not share the counter");
        p.setPos(p.getX()+20,p.getY(),p.getZ());h.assertTrue(!a.stillValid(p),"Distant menu stayed valid");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=300)
    public static void deathDefersLootThenCleansOnce(GameTestHelper h){
        var boss=DynastyEntities.REBEL_GENERAL.get().create(h.getLevel());boss.moveTo(h.absolutePos(new BlockPos(3,2,3)),0,0);h.getLevel().addFreshEntity(boss);boss.setHealth(0);boss.die(boss.damageSources().genericKill());
        h.assertTrue(BossDeathState.managed(boss),"Death not journaled");
        h.runAtTickTime(30,()->h.assertTrue(!boss.isRemoved(),"Vanilla 20 tick removal won"));
        h.runAtTickTime(270,()->{
            h.assertTrue(boss.isRemoved(),"Corpse never cleaned");var records=BossDeathState.get(h.getLevel()).save(new CompoundTag()).getList("Entries",10);boolean complete=false;
            for(var t:records){var n=(CompoundTag)t;if(n.getUUID("Boss").equals(boss.getUUID()))complete=n.getBoolean("RewardGranted")&&n.getBoolean("Cleaned");}
            h.assertTrue(complete,"Reward journal incomplete");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void catalogResourcesAndShapeContract(GameTestHelper h){
        for(int i=1;i<=40;i++){var d=Cod3Catalog.vfx(i);h.assertTrue(d.near()>d.far()&&d.duration()>0,"Invalid VFX budget");}
        var line=Cod3Catalog.vfx(3);h.assertTrue(line.contains(new net.minecraft.world.phys.Vec3(0,0,8),net.minecraft.world.phys.Vec3.ZERO,new net.minecraft.world.phys.Vec3(0,0,1)),"Line misses axis");h.assertTrue(!line.contains(new net.minecraft.world.phys.Vec3(5,0,8),net.minecraft.world.phys.Vec3.ZERO,new net.minecraft.world.phys.Vec3(0,0,1)),"Line includes outside visual width");
        for(var type:NpcContent.NPCS.values()){var npc=type.get().create(h.getLevel());h.assertTrue(npc!=null&&npc.getMaxHealth()>0,"NPC missing attributes");h.assertTrue(!npc.getOffers().isEmpty(),"NPC trade missing");}
        h.assertTrue(Cod3Catalog.entries("secrets").size()==30&&Cod3Catalog.entries("scenic").size()==25,"Catalogue lost requested entries");
        var packet=new Cod3VisualPacket("minecraft:overworld",4,123,321,12,20,1,net.minecraft.world.phys.Vec3.ZERO,new net.minecraft.world.phys.Vec3(0,0,1),"",0,0xABCDEF);
        var buffer=new net.minecraft.network.FriendlyByteBuf(io.netty.buffer.Unpooled.buffer());
        try{Cod3VisualPacket.encode(packet,buffer);h.assertTrue(Cod3VisualPacket.decode(buffer).equals(packet)&&packet.valid(),"VFX packet lost fields/tint");}finally{buffer.release();}
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void playerAndWorldSecretsNeverDoubleClaim(GameTestHelper h){
        var l=h.getLevel();var previous=SecretTracker.get(l);l.getDataStorage().set("dynasty_cod3_secrets",new SecretTracker());
        var p=new net.minecraftforge.common.util.FakePlayer(l,new com.mojang.authlib.GameProfile(UUID.randomUUID(),"cod3-a"));var q=new net.minecraftforge.common.util.FakePlayer(l,new com.mojang.authlib.GameProfile(UUID.randomUUID(),"cod3-b"));
        BlockPos at=h.absolutePos(new BlockPos(2,2,2));l.setBlockAndUpdate(at,StoryAnchor.BLOCK.get().defaultBlockState().setValue(StoryAnchor.KIND,2));p.setPos(at.getX(),at.getY(),at.getZ());q.setPos(at.getX(),at.getY(),at.getZ());SecretTracker.attach(l,at,3);
        var tracker=SecretTracker.get(l);h.assertTrue(tracker.claim(p,3,at)&&!tracker.claim(q,3,at),"World secret awarded twice");
        // A world claim must never attach SavedData's CompoundTag to either player's NBT.
        l.setBlockAndUpdate(at,StoryAnchor.BLOCK.get().defaultBlockState().setValue(StoryAnchor.KIND,1));SecretTracker.attach(l,at,2);
        h.assertTrue(tracker.claim(p,2,at)&&!tracker.claim(p,2,at)&&tracker.claim(q,2,at),"World claim aliased player ownership");l.getDataStorage().set("dynasty_cod3_secrets",previous);h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void wellUsesWaterAndDoesNotConsumeAfterClaim(GameTestHelper h){
        var l=h.getLevel();BlockPos at=h.absolutePos(new BlockPos(5,2,5));l.setBlockAndUpdate(at,StoryAnchor.BLOCK.get().defaultBlockState().setValue(StoryAnchor.KIND,7));SecretTracker.attach(l,at,8);
        var p=new net.minecraftforge.common.util.FakePlayer(l,new com.mojang.authlib.GameProfile(UUID.randomUUID(),"cod3-well"));p.setPos(at.getX(),at.getY(),at.getZ());
        p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(Items.BUCKET));SecretTracker.trigger(p,at,SecretDefinition.Trigger.COMBINATION);
        h.assertTrue(p.getPersistentData().getCompound("cod3_progress_8").getInt("Count")==0,"Empty bucket advanced the well");
        for(int i=0;i<7;i++){final int step=i;h.runAtTickTime(1+i*10,()->{
            p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(Items.WATER_BUCKET));SecretTracker.trigger(p,at,SecretDefinition.Trigger.COMBINATION);
            h.assertTrue(p.getMainHandItem().is(Items.BUCKET),"Water offering was not consumed");
            if(step==6){p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(Items.WATER_BUCKET));SecretTracker.trigger(p,at,SecretDefinition.Trigger.COMBINATION);h.assertTrue(p.getMainHandItem().is(Items.WATER_BUCKET),"Already claimed well consumed another offering");h.succeed();}
        });}
    }
}
