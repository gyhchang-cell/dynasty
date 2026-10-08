package com.dynasty.worldevent;

import com.dynasty.blueprint.BlueprintEntities;
import com.dynasty.blueprint.TemplateMob;
import com.dynasty.blueprint.combat.Faction;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import java.util.*;

/** Real lifecycle and combat fixtures. Fixture loot explicitly does not certify the source event rewards. */
@GameTestHolder("dynasty_cod2")
@PrefixGameTestTemplate(false)
public final class WorldEventGameTests {
    private static WorldEventDefinition definition(String id){return WorldEventDefinitions.ALL.get(new ResourceLocation("dynasty:"+id));}
    private static FakePlayer player(GameTestHelper h,BlockPos pos){
        var p=new FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"cod2-event-test"));
        p.setPos(net.minecraft.world.phys.Vec3.atBottomCenterOf(pos));h.getLevel().addNewPlayer(p);return p;
    }
    private static void remove(GameTestHelper h,FakePlayer p,WorldEventInstance instance){
        DynastyWorldEventManager.finish(h.getLevel(),WorldEventStore.get(h.getLevel()),instance,false);
        WorldEventStore.get(h.getLevel()).instances.remove(instance.uuid);h.getLevel().removePlayerImmediately(p,Entity.RemovalReason.DISCARDED);
    }
    private static WorldEventInstance fixture(GameTestHelper h,String id,BlockPos center,FakePlayer p){
        var i=new WorldEventInstance(definition(id),center,h.getLevel().getGameTime()-80,44L,new ResourceLocation("dynasty:dungeons/chensha_artisan_supplies"));
        i.participate(p.getUUID());WorldEventStore.get(h.getLevel()).instances.put(i.uuid,i);return i;
    }
    @GameTest(template="bow_ritual_test",batch="cod2_event_catalog")
    public static void allThirtyRuntimeIdsAreBoundedAndMissingContentCannotStart(GameTestHelper h){
        h.assertTrue(WorldEventDefinitions.ALL.size()==30&&WorldEventDefinitions.ALL.values().stream().filter(d->d.controller()==WorldEventDefinition.Controller.UNIMPLEMENTED).count()==27,"Exactly thirty IDs are known; twenty-seven absent controllers remain explicitly blocked");
        var d=definition("tianlei_dihuo");var result=DynastyWorldEventManager.start(h.getLevel(),d,h.absolutePos(new BlockPos(5,2,5)),null,true);
        h.assertTrue(!result.started()&&result.missing().contains("controller:dynasty:tianlei_dihuo"),"Unimplemented controller cannot silently become a generic event");
        for(String id:List.of("yinbing_jiedao","juejing_biaoche","xuanniao_zhige"))h.assertTrue(DynastyWorldEventManager.missing(h.getLevel(),definition(id)).isEmpty(),"Real template dependencies and source reward tables are installed: "+id);
        h.assertTrue(!WorldEventStore.get(h.getLevel()).instances.containsKey(result.instance()),"Blocked start allocates no actors/instance");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod2_event_catalog")
    public static void instanceDiskRoundTripPreservesReservationsParticipantsBranchAndEscrow(GameTestHelper h){
        var d=definition("juejing_biaoche");var i=new WorldEventInstance(d,h.absolutePos(new BlockPos(4,2,4)),100,998L,d.rewardTable());
        i.phase=WorldEventInstance.Phase.ACTIVE;i.spawned=3;i.provoked=true;
        for(int n=0;n<80;n++)i.participate(UUID.randomUUID());var actor=UUID.randomUUID();i.actors.put(actor,new WorldEventInstance.Actor(actor,new ResourceLocation("dynasty:zuwu_daoshou"),"REBELS",false));
        var owner=i.participants.iterator().next();i.pendingRewards.put(owner,new ArrayList<>(List.of(new ItemStack(Items.DIAMOND,3))));i.rewardGranted=true;
        var restored=WorldEventInstance.load(i.save());
        h.assertTrue(restored!=null&&restored.uuid.equals(i.uuid)&&restored.seed==998L&&restored.participants.size()==64&&restored.spawned==3&&restored.provoked,"Disk retains absolute state and participant cap");
        h.assertTrue(!restored.actors.get(actor).dead()&&restored.pendingRewards.get(owner).get(0).getCount()==3,"Unloaded actor is reserved, pending reward remains exact");
        var store=new WorldEventStore();store.instances.put(i.uuid,i);store.cooldowns.put("group/test",1000L);store.worldStates.add("dynasty:fog");var loaded=WorldEventStore.load(store.save(new CompoundTag()));
        h.assertTrue(loaded.instances.size()==1&&loaded.cooldowns.get("group/test")==1000L&&loaded.worldStates.contains("dynasty:fog"),"SavedData reload preserves cooldown/weather world states");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod2_event_battle",timeoutTicks=90)
    public static void realBattleUsesTwoSpawnBudgetAndRewardsOnlyAfterRecordedEnemyDeaths(GameTestHelper h){
        var level=h.getLevel();var center=h.absolutePos(new BlockPos(8,2,8));
        for(int x=-17;x<=17;x++)for(int z=-17;z<=17;z++){
            var floor=center.offset(x,-1,z);if(!level.hasChunkAt(floor))continue;
            level.setBlockAndUpdate(floor,Blocks.STONE.defaultBlockState());for(int y=1;y<=4;y++)level.setBlockAndUpdate(floor.above(y),Blocks.AIR.defaultBlockState());
        }
        var p=player(h,center);var i=fixture(h,"juejing_biaoche",center,p);var store=WorldEventStore.get(level);
        try{
            DynastyWorldEventManager.tickInstance(level,store,i,2);h.assertTrue(i.spawned<=2&&i.actors.size()<=2,"One batch cannot create more than two actors");
            for(int n=0;n<30&&i.spawned<13;n++)DynastyWorldEventManager.tickInstance(level,store,i,2);
            h.assertTrue(i.spawned==13&&i.phase==WorldEventInstance.Phase.ACTIVE,"Authored three guards and ten rebels actually enter world, produced="+i.spawned);
            for(var a:i.actors.values()){
                var entity=level.getEntity(a.uuid());h.assertTrue(entity instanceof TemplateMob,"Every reserved UUID points to a real cod1 combatant");var mob=(TemplateMob)entity;mob.setNoAi(true);
                h.assertTrue(mob.faction()==(a.team().equals("ARMY")?Faction.DYNASTY_ARMY:Faction.REBELS),"Controller installs exact opposing factions");
                if(a.team().equals("REBELS")){mob.setHealth(1);mob.hurt(mob.damageSources().playerAttack(p),1000);}
            }
            h.assertTrue(i.actors.values().stream().filter(a->a.team().equals("REBELS")).allMatch(WorldEventInstance.Actor::dead),"Real uncanceled Forge deaths update encounter ledger");
            DynastyWorldEventManager.tickInstance(level,store,i,2);
            h.assertTrue(i.phase==WorldEventInstance.Phase.SUCCESS&&i.rewardGranted,"Living guards plus all defeated rebels are success");
            int before=p.getInventory().countItem(com.dynasty.DynastyRelics.BLUEPRINT.get());
            DynastyWorldEventManager.finish(level,store,i,true);DynastyWorldEventManager.deliverPending(level,i);
            h.assertTrue(before==1&&p.getInventory().countItem(com.dynasty.DynastyRelics.BLUEPRINT.get())==1,"Test fixture reward generates once across repeated completion");h.succeed();
        }finally{remove(h,p,i);}
    }
    @GameTest(template="bow_ritual_test",batch="cod2_event_escrow")
    public static void fullInventoryKeepsRewardEscrowAndRestoresOnlyOwnedTerrain(GameTestHelper h){
        var level=h.getLevel();var center=h.absolutePos(new BlockPos(5,2,5));var p=player(h,center);var i=fixture(h,"juejing_biaoche",center,p);
        try{
            for(int n=0;n<p.getInventory().items.size();n++)p.getInventory().items.set(n,new ItemStack(Items.COBBLESTONE,64));
            var a=center.offset(2,0,0);var b=center.offset(3,0,0);level.setBlockAndUpdate(a,Blocks.RED_WOOL.defaultBlockState());level.setBlockAndUpdate(b,Blocks.GOLD_BLOCK.defaultBlockState());
            i.blocks.put(a,new WorldEventInstance.TemporaryBlock(Blocks.STONE.defaultBlockState(),Blocks.RED_WOOL.defaultBlockState()));i.blocks.put(b,new WorldEventInstance.TemporaryBlock(Blocks.STONE.defaultBlockState(),Blocks.RED_WOOL.defaultBlockState()));
            DynastyWorldEventManager.finish(level,WorldEventStore.get(level),i,true);
            h.assertTrue(i.pendingRewards.containsKey(p.getUUID())&&p.getInventory().countItem(com.dynasty.DynastyRelics.BLUEPRINT.get())==0,"Full inventory leaves exact fixture items in persistent escrow");
            h.assertTrue(level.getBlockState(a).is(Blocks.STONE)&&level.getBlockState(b).is(Blocks.GOLD_BLOCK),"Cleanup restores own block but preserves a later player edit");
            var restored=WorldEventInstance.load(i.save());p.getInventory().clearContent();DynastyWorldEventManager.deliverPending(level,restored);DynastyWorldEventManager.deliverPending(level,restored);
            h.assertTrue(p.getInventory().countItem(com.dynasty.DynastyRelics.BLUEPRINT.get())==1&&restored.pendingRewards.isEmpty(),"Restored reward delivers its remaining bundle exactly once");h.succeed();
        }finally{remove(h,p,i);}
    }
    @GameTest(template="bow_ritual_test",batch="cod2_event_procession")
    public static void processionStaysPeacefulUntilRealAttackAndExpiredUnloadedActorCannotReturn(GameTestHelper h){
        var level=h.getLevel();var center=h.absolutePos(new BlockPos(5,2,5));var p=player(h,center);var i=fixture(h,"yinbing_jiedao",center,p);i.phase=WorldEventInstance.Phase.ACTIVE;
        var mob=BlueprintEntities.YINBING_GUIZU.get().create(level);mob.setNoAi(true);mob.setPos(net.minecraft.world.phys.Vec3.atBottomCenterOf(center.offset(3,0,0)));mob.getPersistentData().putUUID(DynastyWorldEventManager.ACTOR_TAG,i.uuid);
        i.actors.put(mob.getUUID(),new WorldEventInstance.Actor(mob.getUUID(),net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getKey(mob.getType()),"SPIRITS",false));level.addFreshEntity(mob);
        try{
            mob.setTarget(p);h.assertTrue(mob.getTarget()==null&&DynastyWorldEventManager.marching(mob),"Peaceful procession rejects normal player targeting");
            h.assertTrue(mob.hurt(mob.damageSources().playerAttack(p),1)&&i.provoked,"Actual accepted player damage provokes procession");
            mob.setTarget(p);h.assertTrue(mob.getTarget()==p,"Provoked actual ghost can retaliate using existing AI");
            var tag=new CompoundTag();mob.save(tag);mob.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            h.assertTrue(!i.actors.get(mob.getUUID()).dead(),"Chunk unload is not a victory/death and cannot refill the squad");
            DynastyWorldEventManager.finish(level,WorldEventStore.get(level),i,false);
            var copy=BlueprintEntities.YINBING_GUIZU.get().create(level);copy.load(tag);
            h.assertTrue(!level.addFreshEntity(copy)&&copy.isRemoved(),"Expired instance rejects actor on later chunk reload");h.succeed();
        }finally{remove(h,p,i);mob.discard();}
    }
    private WorldEventGameTests(){}
    @GameTest(template="bow_ritual_test",batch="cod2_event_celestial")
    public static void actualCelestialTemplateRepairsWeaponsOnceAndGrantsThirtyMinuteBuffs(GameTestHelper h){
        var level=h.getLevel();var center=h.absolutePos(new BlockPos(5,2,5));var p=player(h,center);var i=fixture(h,"xuanniao_zhige",center,p);
        try{
            var sword=new ItemStack(Items.IRON_SWORD);sword.setDamageValue(200);p.getInventory().items.set(0,sword);
            DynastyWorldEventManager.tickInstance(level,WorldEventStore.get(level),i,2);int damage=sword.getDamageValue();
            DynastyWorldEventManager.tickInstance(level,WorldEventStore.get(level),i,2);
            h.assertTrue(damage==125&&sword.getDamageValue()==125,"Real 30% maximum-durability restoration occurs once for this event");
            h.assertTrue(p.hasEffect(net.minecraft.world.effect.MobEffects.LUCK)&&p.getEffect(net.minecraft.world.effect.MobEffects.LUCK).getDuration()==36000
                &&p.hasEffect(net.minecraft.world.effect.MobEffects.DAMAGE_BOOST),"Celestial template grants actual half-hour luck/attack effects");h.succeed();
        }finally{remove(h,p,i);}
    }
    @GameTest(template="bow_ritual_test",batch="cod2_event_permit")
    public static void sourceDocumentProvidesTemporaryArmyPassageAndAttackingRevokesIt(GameTestHelper h){
        var level=h.getLevel();var center=h.absolutePos(new BlockPos(5,2,5));var p=player(h,center);var mob=BlueprintEntities.ZUWU_DAOSHOU.get().create(level);mob.setNoAi(true);mob.setPos(net.minecraft.world.phys.Vec3.atBottomCenterOf(center.offset(2,0,0)));level.addFreshEntity(mob);
        try{
            p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(WorldEventItems.OFFICIAL_DOCUMENT.get(),2));
            WorldEventItems.OFFICIAL_DOCUMENT.get().use(level,p,net.minecraft.world.InteractionHand.MAIN_HAND);mob.setTarget(p);
            h.assertTrue(mob.getTarget()==null&&p.getMainHandItem().getCount()==1,"Real document is consumed and stops proactive army targeting");
            mob.hurt(mob.damageSources().playerAttack(p),1);mob.setTarget(p);
            h.assertTrue(!p.getPersistentData().contains(WorldEventItems.PERMIT)&&mob.getTarget()==p,"Accepted attack revokes pass and permits retaliation");h.succeed();
        }finally{mob.discard();level.removePlayerImmediately(p,Entity.RemovalReason.DISCARDED);}
    }
    @GameTest(template="bow_ritual_test",batch="cod2_event_peace",timeoutTicks=200)
    public static void celestialPeaceCancelsAnActualPendingAttackAndCombatReturnsAfterItEnds(GameTestHelper h){
        var level=h.getLevel();var center=new BlockPos(8192,100,8192);
        var forced=new HashSet<net.minecraft.world.level.ChunkPos>();var actors=new ArrayList<Entity>();
        var player=new FakePlayer[1];var event=new WorldEventInstance[1];
        // A 48-block area event cannot share the neighboring 16-block GameTest arena.
        for(int x=-1;x<=1;x++)for(int z=-1;z<=1;z++){
            var chunk=new net.minecraft.world.level.ChunkPos(center.offset(x*16,0,z*16));
            if(!level.getForcedChunks().contains(chunk.toLong())){level.setChunkForced(chunk.x,chunk.z,true);forced.add(chunk);}
        }
        Runnable cleanup=()->{
            actors.forEach(Entity::discard);if(player[0]!=null&&event[0]!=null)remove(h,player[0],event[0]);
            for(var chunk:forced)level.setChunkForced(chunk.x,chunk.z,false);
        };
        float[] health=new float[1];
        h.startSequence().thenIdle(20).thenWaitUntil(()->{
            for(var chunk:forced){var loaded=level.getChunkSource().getChunkNow(chunk.x,chunk.z);
                h.assertTrue(loaded!=null&&loaded.getFullStatus().isOrAfter(net.minecraft.server.level.FullChunkStatus.ENTITY_TICKING),"Remote event fixture waits for loaded entity sections");}
        }).thenExecute(()->{
            try{
                for(int x=-4;x<=4;x++)for(int z=-4;z<=4;z++){
                    level.setBlockAndUpdate(center.offset(x,-1,z),Blocks.STONE.defaultBlockState());
                    for(int y=0;y<=3;y++)level.setBlockAndUpdate(center.offset(x,y,z),Blocks.AIR.defaultBlockState());
                }
                player[0]=player(h,center);var attacker=BlueprintEntities.YINBING_GUIZU.get().create(level);var target=BlueprintEntities.TIESUO_CHIHOU.get().create(level);
                for(var mob:List.of(attacker,target)){mob.setNoAi(true);mob.setNoGravity(true);actors.add(mob);}
                attacker.setPos(net.minecraft.world.phys.Vec3.atBottomCenterOf(center));target.setPos(net.minecraft.world.phys.Vec3.atBottomCenterOf(center.east(2)));
                level.addFreshEntity(attacker);level.addFreshEntity(target);health[0]=target.getHealth();
                h.assertTrue(attacker.startSkill(com.dynasty.blueprint.ArmySkills.GHOST_THRUST,target),"Real contact is pending before blessing");
                event[0]=fixture(h,"xuanniao_zhige",center,player[0]);event[0].phase=WorldEventInstance.Phase.ACTIVE;
            }catch(RuntimeException|Error e){cleanup.run();throw e;}
        }).thenIdle(25).thenExecute(()->{
            var attacker=(TemplateMob)actors.get(0);var target=(TemplateMob)actors.get(1);
            h.assertTrue(target.getHealth()==health[0]&&attacker.attack().current()==null&&DynastyWorldEventManager.pacified(attacker),"Blessing cancels the real server damage frame, not just the target cursor; health="+target.getHealth()+" initial="+health[0]+" skill="+attacker.skillId()+" pacified="+DynastyWorldEventManager.pacified(attacker)+" ticks="+attacker.tickCount);
            event[0].phase=WorldEventInstance.Phase.FAILED;
        }).thenIdle(55).thenExecute(()->{
            var attacker=(TemplateMob)actors.get(0);var target=(TemplateMob)actors.get(1);
            h.assertTrue(!DynastyWorldEventManager.pacified(attacker),"Ended blessing clears its combat prohibition");
            // Preserve the existing authored cooldown (full attack length + recovery cooldown).
            attacker.setPos(net.minecraft.world.phys.Vec3.atBottomCenterOf(center));target.setPos(net.minecraft.world.phys.Vec3.atBottomCenterOf(center.east(2)));
            h.assertTrue(attacker.startSkill(com.dynasty.blueprint.ArmySkills.GHOST_THRUST,target),"Ended blessing restores an in-range action after its original cooldown");
        }).thenIdle(22).thenExecute(()->{
            try{h.assertTrue(((TemplateMob)actors.get(1)).getHealth()<health[0],"Restored real contact deals damage");}finally{cleanup.run();}
        }).thenSucceed();
    }
    @GameTest(template="bow_ritual_test",batch="cod2_event_catalog")
    public static void reservedActorTypeCannotBeReplacedByAnotherCreature(GameTestHelper h){
        var center=h.absolutePos(new BlockPos(6,2,6));var p=player(h,center);var i=fixture(h,"yinbing_jiedao",center,p);
        var imposter=BlueprintEntities.ZUWU_DAOSHOU.get().create(h.getLevel());imposter.setNoAi(true);imposter.setPos(net.minecraft.world.phys.Vec3.atBottomCenterOf(center));
        i.actors.put(imposter.getUUID(),new WorldEventInstance.Actor(imposter.getUUID(),new ResourceLocation("dynasty:yinbing_guizu"),"SPIRITS",false));
        imposter.getPersistentData().putUUID(DynastyWorldEventManager.ACTOR_TAG,i.uuid);
        try{h.assertTrue(!h.getLevel().addFreshEntity(imposter)&&!i.actors.get(imposter.getUUID()).dead(),"Mismatched type is rejected without converting unload into death");h.succeed();}finally{imposter.discard();remove(h,p,i);}
    }
}
