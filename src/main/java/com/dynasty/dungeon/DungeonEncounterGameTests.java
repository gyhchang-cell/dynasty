package com.dynasty.dungeon;

import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.material.PushReaction;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;

/** Vanilla zombie is an adapter fixture, never a substitute or acceptance test for Zhaoming. */
@GameTestHolder("dynasty_cod2")
@PrefixGameTestTemplate(false)
public final class DungeonEncounterGameTests {
    private static final ResourceLocation ZOMBIE=new ResourceLocation("minecraft:zombie");
    private static final ResourceLocation TEST_DUNGEON=new ResourceLocation("dynasty_cod2:encounter_fixture");
    private static final ResourceLocation WORLD_LOOT=new ResourceLocation("dynasty:dungeons/chensha_expedition_notes");
    private static final ResourceLocation PLAYER_LOOT=new ResourceLocation("dynasty:dungeons/chensha_artisan_supplies");
    private static ServerPlayer player(GameTestHelper h,String name){
        var level=h.getLevel();var p=new ServerPlayer(level.getServer(),level,new GameProfile(UUID.randomUUID(),name));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(level.getServer(),
            new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setGameMode(GameType.SURVIVAL);return p;
    }
    private static DungeonEncounters.Binding binding(DungeonEncounters.EncounterStarter starter){
        return new DungeonEncounters.Binding(ZOMBIE,starter,WORLD_LOOT,PLAYER_LOOT,Set.of());
    }
    private static DungeonEncounters.Context context(GameTestHelper h,UUID instance,List<UUID> players){
        var pos=Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(3,2,3)));
        return new DungeonEncounters.Context(instance,TEST_DUNGEON,null,pos,new AABB(pos.add(-2,-1,-2),pos.add(2,4,2)),players);
    }
    private static DungeonEncounterState defeated(DungeonStateStore store,UUID instance,List<UUID> players){
        var state=store.encounter(instance,TEST_DUNGEON.toString(),true);state.reserve(ZOMBIE);state.activate(UUID.randomUUID());
        players.forEach(state::join);state.defeat(state.boss(),ZOMBIE,state.attempt());return state;
    }
    private static int count(ServerPlayer player,net.minecraft.world.item.Item item){
        return player.getInventory().items.stream().filter(s->s.is(item)).mapToInt(ItemStack::getCount).sum();
    }
    @GameTest(template="bow_ritual_test",batch="cod2_encounter")
    public static void missingDependenciesNeverReserveOrSpawnABoss(GameTestHelper h){
        var store=new DungeonStateStore();var state=store.encounter(UUID.randomUUID(),TEST_DUNGEON.toString(),true);
        var calls=new AtomicInteger();var starter=(DungeonEncounters.EncounterStarter)(level,c)->{calls.incrementAndGet();return null;};
        var context=context(h,UUID.randomUUID(),List.of());
        h.assertTrue(DungeonEncounters.start(h.getLevel(),store,state,context,null)==DungeonEncounters.Result.MISSING_DEPENDENCY,"No fallback starter when cod1 has not registered");
        var missing=new DungeonEncounters.Binding(ZOMBIE,starter,WORLD_LOOT,PLAYER_LOOT,Set.of(new ResourceLocation("dynasty_cod2:absent_reward")));
        h.assertTrue(DungeonEncounters.start(h.getLevel(),store,state,context,missing)==DungeonEncounters.Result.MISSING_DEPENDENCY,"Unavailable exact reward item blocks encounter");
        var badTable=new DungeonEncounters.Binding(ZOMBIE,starter,new ResourceLocation("dynasty_cod2:absent_loot"),null,Set.of());
        h.assertTrue(DungeonEncounters.start(h.getLevel(),store,state,context,badTable)==DungeonEncounters.Result.MISSING_DEPENDENCY,"Absent loot table cannot become empty loot");
        h.assertTrue(state.phase()==DungeonEncounterState.Phase.READY&&state.attempt()==null&&calls.get()==0,"All missing dependency paths leave the reservation untouched");
        h.assertTrue(DungeonEncounters.missingChenshaDependencies(h.getLevel()).contains("dynasty:zhaoming_di"),"Current production dependency is reported, not renamed to an existing boss");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod2_encounter")
    public static void realDeathValidatesUuidTypeAndAttemptAndCannotReplay(GameTestHelper h){
        var level=h.getLevel();var instance=UUID.randomUUID();var player=player(h,"encounter-a");
        var store=DungeonStateStore.get(level);var state=store.encounter(instance,TEST_DUNGEON.toString(),true);var calls=new AtomicInteger();
        var binding=binding((sl,c)->{calls.incrementAndGet();var mob=EntityType.ZOMBIE.create(sl);mob.setNoAi(true);mob.moveTo(c.spawn().x,c.spawn().y,c.spawn().z);c.bindActor(mob);sl.addFreshEntity(mob);return mob;});
        h.assertTrue(DungeonEncounters.start(level,store,state,context(h,instance,List.of(player.getUUID())),binding)==DungeonEncounters.Result.STARTED,"Actual existing actor is started by supplied adapter");
        var boss=(net.minecraft.world.entity.Mob)level.getEntity(state.boss());
        h.assertTrue(boss!=null&&state.participant(player.getUUID()),"Actor UUID and initial entrant persisted");
        h.assertTrue(!DungeonEncounters.recordDeath(level,boss),"Live actor cannot unlock a coffin");
        h.assertTrue(!state.defeat(UUID.randomUUID(),ZOMBIE,state.attempt())&&!state.defeat(state.boss(),new ResourceLocation("minecraft:cow"),state.attempt())
            &&!state.defeat(state.boss(),ZOMBIE,UUID.randomUUID()),"Wrong actor, type, or encounter token rejected");
        DungeonEncounters.start(level,store,state,context(h,instance,List.of()),binding);
        h.assertTrue(calls.get()==1,"Second core/entrant call cannot spawn another actor");
        boss.setHealth(0);var cancelled=new net.minecraftforge.event.entity.living.LivingDeathEvent(boss,level.damageSources().genericKill());cancelled.setCanceled(true);
        DungeonEncounters.onDeath(cancelled);h.assertTrue(state.phase()==DungeonEncounterState.Phase.ACTIVE,"Cancelled death cannot unlock rewards");boss.setHealth(20);
        boss.hurt(level.damageSources().genericKill(),10000);
        h.assertTrue(state.phase()==DungeonEncounterState.Phase.DEFEATED&&!DungeonEncounters.recordDeath(level,boss),"Actual Forge death callback records exactly one defeat");
        var reloaded=DungeonStateStore.load(store.save(new CompoundTag()));
        h.assertTrue(reloaded.encounter(instance,TEST_DUNGEON.toString(),false).phase()==DungeonEncounterState.Phase.DEFEATED,"Defeat survives SavedData round trip");
        store.room(instance,"imperial_vault").reset();
        h.assertTrue(state.phase()==DungeonEncounterState.Phase.DEFEATED,"Debug room reset cannot erase boss death");
        var drops=new java.util.ArrayList<net.minecraft.world.entity.item.ItemEntity>();
        drops.add(new net.minecraft.world.entity.item.ItemEntity(level,boss.getX(),boss.getY(),boss.getZ(),new ItemStack(Items.WRITTEN_BOOK)));
        drops.add(new net.minecraft.world.entity.item.ItemEntity(level,boss.getX(),boss.getY(),boss.getZ(),new ItemStack(Items.ROTTEN_FLESH)));
        var uniqueBinding=new DungeonEncounters.Binding(ZOMBIE,binding.starter(),WORLD_LOOT,null,Set.of(new ResourceLocation("minecraft:written_book")));
        h.assertTrue(DungeonEncounters.suppressDuplicateDrops(state,boss,drops,uniqueBinding)&&drops.size()==1&&drops.get(0).getItem().is(Items.ROTTEN_FLESH),"Coffin-owned rewards cannot also drop from the bound actor; ordinary loot remains");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod2_encounter")
    public static void unloadedBossAndFailedStarterKeepTheirReservations(GameTestHelper h){
        var level=h.getLevel();var instance=UUID.randomUUID();var store=new DungeonStateStore();var state=store.encounter(instance,TEST_DUNGEON.toString(),true);
        var actor=new java.util.concurrent.atomic.AtomicReference<net.minecraft.world.entity.Mob>();var calls=new AtomicInteger();
        var binding=binding((sl,c)->{calls.incrementAndGet();var mob=EntityType.ZOMBIE.create(sl);mob.setNoAi(true);mob.moveTo(c.spawn().x,c.spawn().y,c.spawn().z);c.bindActor(mob);sl.addFreshEntity(mob);actor.set(mob);return mob;});
        DungeonEncounters.start(level,store,state,context(h,instance,List.of()),binding);var uuid=actor.get().getUUID();
        actor.get().remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
        var restored=DungeonStateStore.load(store.save(new CompoundTag()));var reloaded=restored.encounter(instance,TEST_DUNGEON.toString(),false);
        DungeonEncounters.start(level,restored,reloaded,context(h,instance,List.of()),binding);
        h.assertTrue(calls.get()==1&&reloaded.phase()==DungeonEncounterState.Phase.ACTIVE&&uuid.equals(reloaded.boss()),"Unloaded actor retains UUID and cannot be replaced after reload");
        var failed=new DungeonEncounterState();var wrong=binding((sl,c)->null);
        h.assertTrue(DungeonEncounters.start(level,store,failed,context(h,UUID.randomUUID(),List.of()),wrong)==DungeonEncounters.Result.START_RESERVED,"A starter that failed to bind reserves its attempt");
        var failedReload=DungeonEncounterState.load(failed.save());
        h.assertTrue(!failedReload.reserve(ZOMBIE)&&failedReload.phase()==DungeonEncounterState.Phase.STARTING,"Failed/partially spawned starts are not automatically retried");
        var partial=new DungeonEncounterState();var partialInstance=UUID.randomUUID();var partialContext=context(h,partialInstance,List.of());
        var partialBinding=binding((sl,c)->{var mob=EntityType.ZOMBIE.create(sl);mob.setNoAi(true);mob.moveTo(c.spawn().x,c.spawn().y,c.spawn().z);c.bindActor(mob);sl.addFreshEntity(mob);actor.set(mob);return null;});
        DungeonEncounters.start(level,store,partial,partialContext,partialBinding);
        h.assertTrue(DungeonEncounters.recover(level,partial,partialInstance,TEST_DUNGEON,partialContext.arena())&&actor.get().getUUID().equals(partial.boss()),"A partial start can adopt its uniquely matching already-loaded actor without another spawn");
        actor.get().discard();
        h.assertTrue(DungeonEncounterState.load(new CompoundTag()).phase()==DungeonEncounterState.Phase.STARTING,"Malformed record fails closed instead of regenerating a boss");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod2_encounter")
    public static void twoPlayersAndTwoInstancesShareUniqueReceiptsAndFullInventoryEscrow(GameTestHelper h){
        var level=h.getLevel();var first=player(h,"reward-a");var second=player(h,"reward-b");var outsider=player(h,"reward-c");
        var store=new DungeonStateStore();var instance=UUID.randomUUID();var state=defeated(store,instance,List.of(first.getUUID(),second.getUUID()));var binding=binding((sl,c)->null);
        for(int slot=0;slot<first.getInventory().items.size();slot++)first.getInventory().items.set(slot,new ItemStack(Items.STONE,64));
        h.assertTrue(DungeonEncounters.claim(level,store,state,TEST_DUNGEON,first,binding)==DungeonEncounters.Result.INVENTORY_FULL,"Full inventory stores actual generated loot in escrow");
        var saved=store.save(new CompoundTag());store=DungeonStateStore.load(saved);state=store.encounter(instance,TEST_DUNGEON.toString(),false);
        h.assertTrue(!store.reward(DungeonEncounters.worldKey(TEST_DUNGEON)).empty(),"Unclaimed world bundle persists without item entities");
        first.getInventory().clearContent();
        h.assertTrue(DungeonEncounters.claim(level,store,state,TEST_DUNGEON,first,binding)==DungeonEncounters.Result.CLAIMED,"Same owner resumes persisted delivery");
        int blueprint=count(first,net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(new ResourceLocation("dynasty:blueprint")));
        h.assertTrue(count(first,Items.WRITTEN_BOOK)==1&&blueprint==1,"World fixture loot and personal fixture loot both delivered exactly once");
        h.assertTrue(DungeonEncounters.claim(level,store,state,TEST_DUNGEON,first,binding)==DungeonEncounters.Result.ALREADY_CLAIMED,"Repeated open never rerolls");
        h.assertTrue(DungeonEncounters.claim(level,store,state,TEST_DUNGEON,second,binding)==DungeonEncounters.Result.CLAIMED
            &&count(second,Items.WRITTEN_BOOK)==0&&count(second,net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(new ResourceLocation("dynasty:blueprint")))==1,"Second participant receives only their personal bundle");
        h.assertTrue(DungeonEncounters.claim(level,store,state,TEST_DUNGEON,outsider,binding)==DungeonEncounters.Result.INELIGIBLE,"Nonparticipant cannot steal a reward");
        var another=defeated(store,UUID.randomUUID(),List.of(first.getUUID(),second.getUUID()));
        h.assertTrue(DungeonEncounters.claim(level,store,another,TEST_DUNGEON,first,binding)==DungeonEncounters.Result.ALREADY_CLAIMED
            &&count(first,Items.WRITTEN_BOOK)==1&&count(first,net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(new ResourceLocation("dynasty:blueprint")))==blueprint,"A second structure instance cannot duplicate world or player rewards");
        var tombstone=store.reward(DungeonEncounters.worldKey(TEST_DUNGEON));
        h.assertTrue(tombstone.empty()&&!tombstone.deliver(second),"Consumed key persists and ownership cannot transfer");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod2_encounter")
    public static void coffinBindingIsProtectedAndRoomCompletionCannotUnlockIt(GameTestHelper h){
        var level=h.getLevel();var pos=h.absolutePos(new BlockPos(3,2,3));var origin=pos.subtract(ChenshaPiece.coffinOffset());var instance=UUID.randomUUID();
        level.setBlockAndUpdate(pos,DungeonContent.COFFIN.get().defaultBlockState());var be=(DungeonMechanismBlockEntity)level.getBlockEntity(pos);
        be.configure(instance,"imperial_vault","imperial_coffin",origin.offset(ChenshaPiece.core("imperial_vault")),-1,List.of());
        be.configureEncounter(origin.east());h.assertTrue(!be.saveWithoutMetadata().contains("EncounterOrigin"),"Shifted coffin marker cannot control an arena");
        be.configureEncounter(origin);var saved=be.saveWithoutMetadata();
        var copy=new DungeonMechanismBlockEntity(pos,be.getBlockState());copy.load(saved);
        h.assertTrue(copy.saveWithoutMetadata().getLong("EncounterOrigin")==origin.asLong(),"Authored coffin binding round trips");
        saved.putLong("Controller",origin.offset(ChenshaPiece.core("imperial_vault")).east().asLong());copy.load(saved);
        h.assertTrue(!copy.saveWithoutMetadata().contains("EncounterOrigin"),"Copied NBT with a different core fails closed");
        var room=DungeonStateStore.get(level).room(instance,"imperial_vault");room.complete();be.syncVisual(room);
        h.assertTrue(!level.getBlockState(pos).getValue(DungeonMechanismBlock.OPEN),"Mechanism complete command does not simulate boss defeat");
        h.assertTrue(be.getBlockState().getDestroySpeed(level,pos)<0&&be.getBlockState().getPistonPushReaction()==PushReaction.BLOCK
            &&be.getBlockState().getBlock().getExplosionResistance()>1000000,"Coffin cannot be mined, moved or blasted to bypass a receipt");
        var old=new CompoundTag();old.putInt("Version",1);old.put("Rooms",new CompoundTag());
        h.assertTrue(DungeonStateStore.load(old).encounter(instance,TEST_DUNGEON.toString(),false)==null,"Old world data creates no completed encounter or receipt");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod2_encounter")
    public static void participantsAreBoundedAndCreativeOrOutsidePlayersCannotJoin(GameTestHelper h){
        var player=player(h,"arena-modes");var origin=h.absolutePos(new BlockPos(-31,-10,-15));
        player.setPos(origin.getX()+31.5,origin.getY()+10,origin.getZ()+15.5);
        h.assertTrue(DungeonEncounters.entrant(player,origin),"Living survival player within the actual dome is eligible");
        player.setGameMode(GameType.CREATIVE);h.assertTrue(!DungeonEncounters.entrant(player,origin),"Creative excluded");
        player.setGameMode(GameType.SPECTATOR);h.assertTrue(!DungeonEncounters.entrant(player,origin),"Spectator excluded");
        player.setGameMode(GameType.SURVIVAL);player.setPos(origin.getX()+9,origin.getY()+10,origin.getZ()+3);
        h.assertTrue(!DungeonEncounters.entrant(player,origin),"Bounding box corner outside the ellipse does not count as the arena");
        var state=new DungeonEncounterState();state.reserve(ZOMBIE);state.activate(UUID.randomUUID());
        for(int i=0;i<100;i++)state.join(UUID.randomUUID());
        h.assertTrue(state.save().getList("Participants",8).size()==64,"Participant state has a finite cap");h.succeed();
    }
}
