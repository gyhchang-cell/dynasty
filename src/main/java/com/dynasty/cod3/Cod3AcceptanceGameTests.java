package com.dynasty.cod3;

import com.dynasty.DynastyBlocks;
import com.dynasty.entity.DynastyEntities;
import com.dynasty.workshop.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.gametest.*;
import java.util.UUID;

@GameTestHolder("dynasty_cod3")
@PrefixGameTestTemplate(false)
public final class Cod3AcceptanceGameTests {
    private static FakePlayer player(GameTestHelper h,BlockPos pos){
        var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"cod3-accept"));
        p.setPos(Vec3.atCenterOf(h.absolutePos(pos)));return p;
    }
    @GameTest(template="bow_ritual_test")
    public static void allEightMenusShiftClickAndShareReceipts(GameTestHelper h){
        int index=0;
        for(var recipe:WorkshopRecipes.ALL){
            var pos=new BlockPos(1+index%4,2,1+index/4);index++;
            var block=(BlockItem)new WorkshopRecipes.Cost("dynasty:"+recipe.station(),1).stack().getItem();
            h.setBlock(pos,block.getBlock());var station=(WorkshopBlockEntity)h.getBlockEntity(pos);
            var a=player(h,pos);var b=player(h,pos);
            var menuA=new WorkshopMenu(1,a.getInventory(),station,station.data);
            var menuB=new WorkshopMenu(2,b.getInventory(),station,station.data);
            for(var cost:recipe.costs()){
                a.getInventory().setItem(0,cost.stack());
                h.assertTrue(!menuA.quickMoveStack(a,31).isEmpty(),"Shift-click input rejected: "+recipe.station());
                h.assertTrue(menuA.deposited()==menuB.deposited(),"Two menus diverged");
            }
            h.assertTrue(station.ready(),"Shift-click recipe did not complete");
            menuA.removed(a);
            var saved=station.saveWithoutMetadata();station.load(saved);
            h.assertTrue(station.ready()&&menuB.deposited()==recipe.total(),"Closing/reload lost progress");
            h.assertTrue(!menuB.quickMoveStack(b,3).isEmpty(),"Shift-click output rejected");
            h.assertTrue(!station.ready()&&station.getItem(3).isEmpty(),"Output receipt not reset");
            h.assertTrue(menuB.quickMoveStack(b,3).isEmpty(),"Second menu took duplicate output");
            int output=0;for(var stack:b.getInventory().items)if(ItemStack.isSameItemSameTags(stack,recipe.result()))output+=stack.getCount();
            h.assertTrue(output==recipe.count(),"Wrong shift-click output amount");
        }h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void partiallyFullInventoryRetainsOutputAcrossReload(GameTestHelper h){
        var pos=new BlockPos(2,2,2);h.setBlock(pos,DynastyBlocks.HERBAL_BASIN.get());
        var station=(WorkshopBlockEntity)h.getBlockEntity(pos);var p=player(h,pos);
        for(var cost:station.recipe().costs()){var stack=cost.stack();while(!stack.isEmpty())station.accept(stack);}
        for(int i=0;i<36;i++)p.getInventory().setItem(i,new ItemStack(Items.DIRT,64));
        var result=station.recipe().result();var almost=result.copy();almost.setCount(almost.getMaxStackSize()-1);p.getInventory().setItem(0,almost);
        var menu=new WorkshopMenu(1,p.getInventory(),station,station.data);
        menu.quickMoveStack(p,3);
        h.assertTrue(station.ready()&&station.getItem(3).getCount()==result.getCount()-1,"Partial output was reset");
        station.load(station.saveWithoutMetadata());
        h.assertTrue(station.getItem(3).getCount()==result.getCount()-1,"Reload recreated extracted output");
        h.assertTrue(menu.quickMoveStack(p,3).isEmpty(),"Full inventory extracted more output");
        p.getInventory().setItem(1,ItemStack.EMPTY);menu.quickMoveStack(p,3);
        h.assertTrue(!station.ready()&&station.getItem(3).isEmpty(),"Final output receipt not reset");h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void deathReloadSettlesImmediatelyAndDoesNotPayAgain(GameTestHelper h){
        var level=h.getLevel();var storage=level.getDataStorage();var original=BossDeathState.get(level);
        try{
            storage.set("dynasty_cod3_deaths",new BossDeathState());
            for(var floor:BlockPos.betweenClosed(new BlockPos(1,1,1),new BlockPos(5,1,5)))h.setBlock(floor,net.minecraft.world.level.block.Blocks.STONE);
            var boss=DynastyEntities.REBEL_GENERAL.get().create(level);boss.moveTo(h.absolutePos(new BlockPos(3,2,3)),0,0);level.addFreshEntity(boss);
            boss.setHealth(0);boss.die(boss.damageSources().genericKill());
            var saved=BossDeathState.get(level).save(new CompoundTag());
            var record=saved.getList("Entries",Tag.TAG_COMPOUND).getCompound(0);
            var loot=new ListTag();loot.add(new ItemStack(Items.DIAMOND,3).save(new CompoundTag()));record.put("Loot",loot);record.putInt("XP",0);
            storage.set("dynasty_cod3_deaths",BossDeathState.load(saved));BossDeathState.settle(level);
            h.assertTrue(boss.isRemoved(),"Restart did not safely settle DYING");
            var complete=BossDeathState.get(level).save(new CompoundTag()).getList("Entries",10).getCompound(0);
            h.assertTrue(complete.getBoolean("LootPlaced")&&complete.getBoolean("XPAwarded")&&complete.getBoolean("RewardGranted")&&complete.getBoolean("Cleaned"),"Incomplete reward phases");
            long remains=java.util.stream.StreamSupport.stream(BlockPos.betweenClosed(boss.blockPosition().offset(-2,0,-2),boss.blockPosition().offset(2,3,2)).spliterator(),false).filter(p->level.getBlockEntity(p) instanceof LootableRemains.Remains).count();
            storage.set("dynasty_cod3_deaths",BossDeathState.load(BossDeathState.get(level).save(new CompoundTag())));BossDeathState.settle(level);
            long again=java.util.stream.StreamSupport.stream(BlockPos.betweenClosed(boss.blockPosition().offset(-2,0,-2),boss.blockPosition().offset(2,3,2)).spliterator(),false).filter(p->level.getBlockEntity(p) instanceof LootableRemains.Remains).count();
            h.assertTrue(remains==1&&again==remains,"Reload duplicated loot container");
            var stale=DynastyEntities.REBEL_GENERAL.get().create(level);stale.setUUID(boss.getUUID());
            var join=new net.minecraftforge.event.entity.EntityJoinLevelEvent(stale,level);BossDeathState.join(join);
            h.assertTrue(join.isCanceled(),"Saved corpse bypassed tombstone without marker");
        }finally{storage.set("dynasty_cod3_deaths",original);}h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void restartHonorsPartialLootReceiptAndMalformedRecords(GameTestHelper h){
        var level=h.getLevel();var storage=level.getDataStorage();var original=BossDeathState.get(level);
        try{
            var entry=new CompoundTag();entry.putUUID("Boss",UUID.randomUUID());entry.putString("Type","dynasty:rebel_general");entry.putLong("Position",h.absolutePos(new BlockPos(2,2,2)).asLong());entry.putLong("Start",Long.MAX_VALUE);entry.putBoolean("LootPlaced",true);entry.putInt("XP",0);
            var loot=new ListTag();loot.add(new ItemStack(Items.DIAMOND,5).save(new CompoundTag()));entry.put("Loot",loot);
            var entries=new ListTag();entries.add(new CompoundTag());entries.add(entry);var saved=new CompoundTag();saved.put("Entries",entries);
            storage.set("dynasty_cod3_deaths",BossDeathState.load(saved));BossDeathState.settle(level);
            var result=BossDeathState.get(level).save(new CompoundTag()).getList("Entries",10);
            h.assertTrue(result.size()==1&&result.getCompound(0).getBoolean("Cleaned"),"Malformed journal blocked valid reward");
            h.assertTrue(level.getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,new net.minecraft.world.phys.AABB(h.absolutePos(new BlockPos(0,1,0)),h.absolutePos(new BlockPos(7,5,7))),e->e.getItem().is(Items.DIAMOND)).isEmpty(),"Partial receipt paid loot twice");
        }finally{storage.set("dynasty_cod3_deaths",original);}h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void shapeContractCoversFortyTemplatesRotationAndTiming(GameTestHelper h){
        for(int n=1;n<=40;n++){
            var d=Cod3Catalog.vfx(n);var instance=new VfxInstance(d,new Vec3(10,4,-3),new Vec3(1,0,0),42,0,40,1.5,10,12);
            var v=instance.volume(10);Vec3 inside=switch(v.shape()){
                case LINE->v.point(0,0,v.length()/2);
                case CHAIN->v.centerline(0,.5);
                case SPHERE->v.origin();
                case ANNULUS->v.origin().add((v.innerRadius()+v.radius())/2,.1,0);
                case CONE->v.point(0,.1,v.radius()/2);
                default->v.origin().add(0,.1,0);
            };
            h.assertTrue(instance.contains(inside,10)==d.damaging(),"Missing volume: "+n);
            h.assertTrue(!instance.contains(inside,9)&&!instance.contains(inside,22),"Damage escaped active window: "+n);
            h.assertTrue(!instance.contains(v.origin().add(100,100,100),10),"Volume escaped bounds: "+n);
            h.assertTrue(d.budget(128,true)<d.budget(16,false),"LOW/far budget not reduced: "+n);
        }
        var line=Cod3Catalog.vfx(3);
        h.assertTrue(line.contains(new Vec3(0,8,0),Vec3.ZERO,new Vec3(0,1,0)),"Vertical line ignores pitch");
        h.assertTrue(!line.contains(new Vec3(.16,8,0),Vec3.ZERO,new Vec3(0,1,0)),"Line uses full width as half width");
        h.assertTrue(!Cod3Catalog.vfx(5).contains(new Vec3(2.4,1,2.4),Vec3.ZERO,new Vec3(0,0,1)),"Fire cylinder has square corners");
        h.assertTrue(!Cod3Catalog.vfx(18).damaging(),"Tiger afterimage became a damaging projectile");
        h.assertTrue(!Cod3Catalog.vfx(19).contains(new Vec3(7,.1,1),Vec3.ZERO,new Vec3(0,0,1)),"Phoenix fan exceeds ninety degrees");
        h.assertTrue(!Cod3Catalog.vfx(12).contains(new Vec3(0,.1,0),Vec3.ZERO,new Vec3(0,0,1)),"Gold ring unexpectedly includes its hollow center");
        var packet=new Cod3VisualPacket("minecraft:overworld",12,-1,3,7,30,1,Vec3.ZERO,new Vec3(0,0,1),"combat_10_8",0);
        h.assertTrue(VfxInstance.combat(packet).windupTicks()==10&&VfxInstance.combat(packet).activeTicks()==8,"Combat timing not preserved on wire");h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void templateTimelinesSoundsAndInstanceLimitsAreValid(GameTestHelper h){
        for(int id=1;id<=40;id++){
            var d=Cod3Catalog.vfx(id);var t=VfxTimeline.timing(d,d.duration());
            h.assertTrue(t.spawnEnd()>=0&&t.spawnEnd()<t.expandEnd()&&t.expandEnd()<t.sustainEnd()&&t.sustainEnd()<d.duration(),"Invalid timeline: "+id);
            h.assertTrue(t.phase(t.expandEnd(),d.duration())==VfxInstance.Phase.SUSTAIN&&t.phase(t.sustainEnd(),d.duration())==VfxInstance.Phase.COLLAPSE&&t.phase(d.duration(),d.duration())==VfxInstance.Phase.END,"Phase boundary off by one: "+id);
            h.assertTrue(t.expansion(t.spawnEnd())==0&&t.expansion(t.expandEnd())==1&&t.alpha(d.duration(),d.duration())==0,"Visual did not finish: "+id);
            var doubled=VfxTimeline.timing(d,d.duration()*2);
            h.assertTrue(doubled.expandEnd()==t.expandEnd()*2&&doubled.limit()==t.limit(),"Scaled lifetime changed instance budget");
            h.assertTrue(net.minecraftforge.registries.ForgeRegistries.SOUND_EVENTS.containsKey(VfxTimeline.sound(id).getLocation()),"Missing 1.20.1 sound: "+id);
            var instance=new VfxInstance(d,Vec3.ZERO,new Vec3(0,0,1),1,0,d.duration(),1);
            for(int age=0;age<=d.duration();age++)h.assertTrue(instance.phase(age)==t.phase(age,d.duration())&&Math.abs(instance.expansion(age)-t.expansion(age))<1e-6,"Default server/client timeline drift: "+id);
        }
        h.assertTrue(VfxTimeline.limit(17)==1&&VfxTimeline.limit(33)==1&&VfxTimeline.limit(30)==2,"Large effects bypass caps");
        var d=Cod3Catalog.vfx(13);var v=VfxVolume.of(d,Vec3.ZERO,new Vec3(0,0,1),1,1,12);
        for(int branch=0;branch<v.branches();branch++)for(int step=0;step<=32;step++)h.assertTrue(v.contains(v.centerline(branch,step/32.))&&v.bounds().contains(v.centerline(branch,step/32.)),"Spline visual escaped hit or query volume");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void actualCombatVolumeExcludesSquareCornersAndNeverHitsTwice(GameTestHelper h){
        var at=h.absolutePos(new BlockPos(3,2,3));var origin=Vec3.atBottomCenterOf(at);
        var owner=net.minecraft.world.entity.EntityType.COW.create(h.getLevel());owner.setNoAi(true);owner.setPos(origin);h.getLevel().addFreshEntity(owner);
        var inside=net.minecraft.world.entity.EntityType.COW.create(h.getLevel());inside.setNoAi(true);inside.setPos(origin.add(1,0,0));h.getLevel().addFreshEntity(inside);
        var corner=net.minecraft.world.entity.EntityType.COW.create(h.getLevel());corner.setNoAi(true);corner.setPos(origin.add(1.8,0,1.8));h.getLevel().addFreshEntity(corner);
        h.assertTrue(Cod3CombatVfx.castDisk(owner,origin,new Vec3(0,0,1),.25,5,10,2,e->true,e->{}),"Actual server cast rejected");
        h.runAtTickTime(4,()->h.assertTrue(inside.getHealth()==inside.getMaxHealth(),"Damage before telegraph ended"));
        h.runAtTickTime(18,()->{
            h.assertTrue(inside.getHealth()==inside.getMaxHealth()-2,"Cast hit more or less than once");
            h.assertTrue(corner.getHealth()==corner.getMaxHealth(),"Circle hit its AABB corners");
            owner.discard();inside.discard();corner.discard();h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test")
    public static void scenicSnapshotsPersistAnchorSeedAndOriginalStart(GameTestHelper h){
        var level=h.getLevel();var scene=new ScenicEvents();var anchor=Vec3.atCenterOf(h.absolutePos(new BlockPos(3,2,3)));
        h.assertTrue(scene.start(level,1,anchor)&&scene.start(level,4,anchor.add(0,0,1))&&scene.start(level,5,anchor.add(0,0,2)),"Three required scenic templates did not start");
        h.assertTrue(!scene.start(level,1,anchor)&&!scene.start(level,0,anchor)&&!scene.start(level,1,new Vec3(Double.NaN,0,0)),"Invalid/duplicate scene accepted");
        var before=scene.packets(level,anchor);var saved=scene.save(new CompoundTag());var restored=ScenicEvents.load(saved);
        h.assertTrue(before.equals(restored.packets(level,anchor)),"Reconnect changed scene seed/time/anchor");
        h.assertTrue(restored.packets(level,anchor.add(300,0,0)).isEmpty(),"Leaving region retained scene");
        h.runAtTickTime(20,()->{
            var after=restored.packets(level,anchor);
            h.assertTrue(after.size()==3&&after.get(0).start()==before.get(0).start()&&after.get(0).tick()>=20,"Late observer restarted scene");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test")
    public static void smithAndCaptainUseActualPaymentsAndPersonalReceipts(GameTestHelper h){
        var pos=new BlockPos(2,2,2);var p=player(h,pos);var q=player(h,pos);
        var smith=NpcContent.NPCS.get("lao_chen").get().create(h.getLevel());smith.setNoAi(true);smith.setPos(p.position());h.getLevel().addFreshEntity(smith);
        var coin=net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(net.minecraft.resources.ResourceLocation.parse("dynasty:copper_coin"));
        var sword=new ItemStack(Items.IRON_SWORD);sword.setDamageValue(100);p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,sword);
        h.assertTrue(!NpcServices.repair(p,smith)&&sword.getDamageValue()==100,"Unpaid repair succeeded");
        p.getInventory().setItem(1,new ItemStack(coin,4));NpcDialogue.open(p,smith);var session=NpcDialogue.session(p.getUUID());
        h.assertTrue(NpcDialogue.choose(p,session.token(),"repair")&&sword.getDamageValue()<100&&p.getInventory().countItem(coin)==0,"Smith did not charge actual repair payment");
        h.assertTrue(!NpcDialogue.choose(p,session.token(),"repair"),"Old repair button replayed");
        var captain=NpcContent.NPCS.get("han_chong").get().create(h.getLevel());captain.setNoAi(true);captain.setPos(p.position());h.getLevel().addFreshEntity(captain);
        var roster=net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(net.minecraft.resources.ResourceLocation.parse("dynasty:bamboo_slip"));
        p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(roster,2));q.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(roster));
        h.assertTrue(NpcServices.commemorate(p,captain)&&p.getMainHandItem().getCount()==1,"Captain did not consume one roster");
        var receipt=p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).copy();
        h.assertTrue(!NpcServices.commemorate(p,captain)&&p.getMainHandItem().getCount()==1&&NpcServices.commemorate(q,captain),"Memorial receipt shared or replayed");
        p.getPersistentData().put(Player.PERSISTED_NBT_TAG,receipt);h.assertTrue(!NpcServices.commemorate(p,captain),"Reload lost memorial receipt");
        smith.discard();captain.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test")
    public static void itemWeatherAndRegionSecretsRequireRealConditions(GameTestHelper h){
        var level=h.getLevel();var storage=level.getDataStorage();var original=SecretTracker.get(level);long day=level.getDayTime();boolean rain=level.isRaining(),thunder=level.isThundering();float rainLevel=level.getRainLevel(1),thunderLevel=level.getThunderLevel(1);
        try{
            storage.set("dynasty_cod3_secrets",new SecretTracker());var pos=new BlockPos(2,2,2);var at=h.absolutePos(pos);var p=player(h,pos);
            level.setBlockAndUpdate(at,StoryAnchor.BLOCK.get().defaultBlockState().setValue(StoryAnchor.KIND,14));SecretTracker.attach(level,at,15);
            SecretTracker.trigger(p,at,SecretDefinition.Trigger.USE_ITEM_AT_POS);
            h.assertTrue(p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).isEmpty(),"Wrong offering claimed secret");
            var bronze=net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(net.minecraft.resources.ResourceLocation.parse("dynasty:bronze_ingot"));p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(bronze,2));
            SecretTracker.trigger(p,at,SecretDefinition.Trigger.USE_ITEM_AT_POS);h.assertTrue(p.getMainHandItem().getCount()==1,"Real item offering not paid");
            SecretTracker.trigger(p,at,SecretDefinition.Trigger.USE_ITEM_AT_POS);h.assertTrue(p.getMainHandItem().getCount()==1,"Repeated secret consumed another item");
            level.setBlockAndUpdate(at,StoryAnchor.BLOCK.get().defaultBlockState().setValue(StoryAnchor.KIND,13));SecretTracker.attach(level,at,14);p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,ItemStack.EMPTY);
            level.setDayTime(12000);level.setWeatherParameters(0,0,false,false);SecretTracker.trigger(p,at,SecretDefinition.Trigger.WEATHER_WINDOW);
            String weatherKey=level.dimension().location()+":secret_14";h.assertTrue(!p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).contains(weatherKey),"Clear weather passed storm condition");
            level.setWeatherParameters(0,200,true,true);level.setRainLevel(1);level.setThunderLevel(1);SecretTracker.trigger(p,at,SecretDefinition.Trigger.WEATHER_WINDOW);h.assertTrue(p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).contains(weatherKey),"Real weather/time trigger failed");
            level.setBlockAndUpdate(at,StoryAnchor.BLOCK.get().defaultBlockState().setValue(StoryAnchor.KIND,17));SecretTracker.attach(level,at,18);
            p.setPos(Vec3.atCenterOf(at));SecretTracker.trigger(p,p.blockPosition(),SecretDefinition.Trigger.ENTER_REGION);
            String regionKey=level.dimension().location()+":secret_18";h.assertTrue(!p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).contains(regionKey),"Region height requirement ignored");
            p.setPos(Vec3.atCenterOf(at.above(2)));SecretTracker.trigger(p,p.blockPosition(),SecretDefinition.Trigger.ENTER_REGION);h.assertTrue(p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).contains(regionKey),"Actual high region entry failed");
        }finally{storage.set("dynasty_cod3_secrets",original);level.setDayTime(day);level.setWeatherParameters(0,0,rain,thunder);level.setRainLevel(rainLevel);level.setThunderLevel(thunderLevel);}h.succeed();
    }

    @GameTest(template="bow_ritual_test")
    public static void threeFunctionalNpcTemplatesSpawnAndTradeWithRealStock(GameTestHelper h){
        int index=0;
        for(String role:java.util.List.of("lao_chen","han_chong","baibao_jin")){
            var pos=new BlockPos(1+index*2,2,2);index++;h.setBlock(pos,StoryAnchor.npcState(role));
            var anchor=(StoryAnchor.Anchor)h.getBlockEntity(pos);anchor.onLoad();var absolute=h.absolutePos(pos);
            var uuid=UUID.nameUUIDFromBytes((h.getLevel().dimension().location()+":"+absolute+":"+role).getBytes(java.nio.charset.StandardCharsets.UTF_8));
            var npc=(DynastyNpcEntity)h.getLevel().getEntity(uuid);h.assertTrue(npc!=null&&npc.home().equals(absolute.above()),"Template did not spawn with persistent home: "+role);npc.setNoAi(true);
            var p=new net.minecraft.server.level.ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"cod3-stock"));
            p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.setPos(npc.position());
            NpcDialogue.open(p,npc);var session=NpcDialogue.session(p.getUUID());
            h.assertTrue(NpcDialogue.choose(p,session.token(),"trade")&&p.containerMenu instanceof net.minecraft.world.inventory.MerchantMenu,"Dialogue did not open real trade: "+role);
            var menu=(net.minecraft.world.inventory.MerchantMenu)p.containerMenu;var offer=npc.getOffers().get(0);menu.setSelectionHint(0);menu.getSlot(0).set(offer.getCostA().copy());
            if(!offer.getCostB().isEmpty())menu.getSlot(1).set(offer.getCostB().copy());
            h.assertTrue(!menu.quickMoveStack(p,2).isEmpty()&&offer.getUses()==1,"Native trade did not consume one stock: "+role);
            var saved=npc.saveWithoutId(new CompoundTag());var restored=NpcContent.NPCS.get(role).get().create(h.getLevel());restored.load(saved);
            h.assertTrue(restored.getOffers().get(0).getUses()==1,"Reload reset NPC stock: "+role);
            anchor.load(anchor.saveWithoutMetadata());anchor.onLoad();h.assertTrue(h.getLevel().getEntity(uuid)==npc,"Home reload duplicated NPC: "+role);
            p.closeContainer();npc.discard();
        }h.succeed();
    }

    @GameTest(template="bow_ritual_test")
    public static void wanderingMerchantRespawnPersistsAndNeverDuplicates(GameTestHelper h){
        var pos=new BlockPos(2,2,2);h.setBlock(pos,StoryAnchor.npcState("baibao_jin"));var anchor=(StoryAnchor.Anchor)h.getBlockEntity(pos);anchor.onLoad();
        var at=h.absolutePos(pos);var uuid=UUID.nameUUIDFromBytes((h.getLevel().dimension().location()+":"+at+":baibao_jin").getBytes(java.nio.charset.StandardCharsets.UTF_8));
        var npc=(DynastyNpcEntity)h.getLevel().getEntity(uuid);h.assertTrue(npc!=null,"Merchant not generated");
        var death=new net.minecraftforge.event.entity.living.LivingDeathEvent(npc,npc.damageSources().genericKill());NpcContent.Lifecycle.death(death);
        var saved=anchor.saveWithoutMetadata();h.assertTrue(saved.getLong("RespawnAt")>h.getLevel().getGameTime(),"Merchant death did not persist cooldown");
        npc.discard();anchor.load(saved);anchor.onLoad();h.assertTrue(h.getLevel().getEntity(uuid)==null,"Merchant respawned before cooldown");
        saved.putLong("RespawnAt",h.getLevel().getGameTime());anchor.load(saved);anchor.onLoad();
        var replacement=h.getLevel().getEntity(uuid);h.assertTrue(replacement instanceof DynastyNpcEntity&&replacement!=npc,"Merchant did not recover after saved cooldown");
        anchor.onLoad();h.assertTrue(h.getLevel().getEntity(uuid)==replacement&&anchor.saveWithoutMetadata().getLong("RespawnAt")==-1,"Repeated home load duplicated merchant");
        replacement.discard();h.succeed();
    }

    @GameTest(template="bow_ritual_test")
    public static void bloodWaveRetreatUsesSameMovingVolume(GameTestHelper h){
        var d=Cod3Catalog.vfx(37);var origin=new Vec3(2,2,2);var direction=new Vec3(1,0,0);
        for(int lifetime:new int[]{28,56}){
            var t=VfxTimeline.timing(d,lifetime);double max=t.sustainEnd()*.2;
            var crest=VfxVolume.of(d,origin,direction,1,1,t.sustainEnd(),lifetime);
            var retreat=VfxVolume.of(d,origin,direction,1,1,(t.sustainEnd()+lifetime)/2,lifetime);
            var end=VfxVolume.of(d,origin,direction,1,1,lifetime,lifetime);
            h.assertTrue(Math.abs(crest.origin().x-origin.x-max)<1e-6,"Wave advance speed changed");
            h.assertTrue(Math.abs(retreat.origin().x-origin.x-max/2)<1e-6,"Wave did not retreat during collapse");
            h.assertTrue(end.origin().distanceTo(origin)<1e-6,"Wave did not return to anchor");
        }h.succeed();
    }
}
