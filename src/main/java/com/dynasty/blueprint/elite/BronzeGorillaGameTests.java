package com.dynasty.blueprint.elite;
import com.dynasty.blueprint.BlueprintSpawnState;
import com.dynasty.blueprint.combat.AttackState;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;
import java.util.*;

/** Prepared native acceptance sources; user has paused Java, none of these has run. */
@GameTestHolder("dynasty_army") @PrefixGameTestTemplate(false)
public final class BronzeGorillaGameTests {
    private static final net.minecraft.server.level.TicketType<UUID> TYPE=net.minecraft.server.level.TicketType.create("dynasty_ape_qa",UUID::compareTo);
    private record Ticket(net.minecraft.world.level.ChunkPos chunk,UUID id){}
    private static final Map<ServerLevel,List<Ticket>> TICKETS=new HashMap<>();
    private static final Map<ServerLevel,List<Entity>> FIXTURES=new HashMap<>();
    private static final Map<ServerLevel,Boolean> GRIEF_RULES=new HashMap<>();
    private static final Map<ServerLevel,List<String>> MARKERS=new HashMap<>();
    private static <T extends Entity>T own(GameTestHelper h,T e){FIXTURES.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(e);return e;}
    @AfterBatch(batch="bronze_gorilla") public static void release(ServerLevel world){
        var old=GRIEF_RULES.remove(world);if(old!=null)world.getGameRules().getRule(GameRules.RULE_MOBGRIEFING).set(old,world.getServer());
        var es=FIXTURES.remove(world);if(es!=null)for(var e:es)if(!e.isRemoved())e.discard();
        var ts=TICKETS.remove(world);if(ts!=null)for(var t:ts)world.getChunkSource().removeRegionTicket(TYPE,t.chunk(),2,t.id(),true);
        var keys=MARKERS.remove(world);if(keys!=null){var state=BlueprintSpawnState.get(world);for(var key:keys)state.markers.remove(key);state.setDirty();}
    }
    @AfterBatch(batch="bronze_gorilla_grief") public static void releaseGrief(ServerLevel world){release(world);}
    private static BronzeGorilla caster(GameTestHelper h){
        var chunks=new HashSet<net.minecraft.world.level.ChunkPos>();for(int x:new int[]{0,15})for(int z:new int[]{0,15})chunks.add(new net.minecraft.world.level.ChunkPos(h.absolutePos(new BlockPos(x,2,z))));
        for(var chunk:chunks){var t=new Ticket(chunk,UUID.randomUUID());h.getLevel().getChunkSource().addRegionTicket(TYPE,chunk,2,t.id(),true);TICKETS.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(t);}
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=0;y<10;y++)h.setBlock(x,y,z,y<=1?Blocks.STONE:Blocks.AIR);
        var m=own(h,h.spawn(EliteContent.BRONZE_GORILLA.get(),new BlockPos(7,2,3)));m.setNoAi(true);m.setPersistenceRequired();return m;
    }
    private static Cow target(GameTestHelper h,int x,int z){var c=own(h,h.spawn(EntityType.COW,new BlockPos(x,2,z)));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);c.setHealth(1000);c.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);return c;}
    private static void grief(GameTestHelper h,boolean value){var rule=h.getLevel().getGameRules().getRule(GameRules.RULE_MOBGRIEFING);GRIEF_RULES.putIfAbsent(h.getLevel(),rule.get());rule.set(value,h.getLevel().getServer());}
    private static List<GorillaStone> stones(GameTestHelper h,BronzeGorilla m){return h.getLevel().getEntitiesOfClass(GorillaStone.class,m.getBoundingBox().inflate(34),e->e.ownedBy(m));}
    @GameTest(template="bow_ritual_test",timeoutTicks=145,batch="bronze_gorilla")
    public static void fullTellEightMetreAdvanceNarrowBandAndCounterWindow(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,7);var flank=target(h,11,7);var start=m.position();grief(h,false);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(421,victim),"Smash starts on actual native clock"));
        h.runAfterDelay(27,()->h.assertTrue(m.phase()==AttackState.WINDUP&&victim.getHealth()==1000&&m.position().distanceToSqr(start)<.01,"All24tell ticks are harmless and planted"));
        h.runAfterDelay(93,()->h.assertTrue(m.phase()==AttackState.RECOVERY&&Math.abs(m.position().subtract(start).horizontalDistance()-8)<.08&&victim.getHealth()<1000&&flank.getHealth()==1000,"Real64step advance is8m; only narrow frontal band hurts"));
        h.runAfterDelay(133,()->h.assertTrue(m.phase()==AttackState.RECOVERY&&!m.attack().ready(421,h.getLevel().getGameTime()),"42tick counter window retains cooldown"));
        h.runAfterDelay(138,()->{h.assertTrue(m.phase()==AttackState.IDLE&&h.getBlockState(new BlockPos(7,1,7)).is(Blocks.STONE),"Recovery ends; griefing-disabled floor survives");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=85,batch="bronze_gorilla")
    public static void lateWallCancelsLockedAdvanceAndPreservesCooldown(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,7);grief(h,false);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(421,victim),"Smash locks facing"));
        h.runAfterDelay(10,()->{for(int x=4;x<=10;x++)for(int y=2;y<8;y++)h.setBlock(x,y,8,Blocks.STONE);victim.moveTo(h.absolutePos(new BlockPos(12,2,7)),0,0);});
        h.runAfterDelay(60,()->{h.assertTrue(m.phase()==AttackState.STUN&&m.getZ()<h.absolutePos(new BlockPos(7,2,8)).getZ()-1&&!m.attack().ready(421,h.getLevel().getGameTime()),"Clipped body cannot turn or push through new wall; cancellation keeps cooldown");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=85,batch="bronze_gorilla")
    public static void twentyFourStepLeapUsesActualLockedFloorAndGravity(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,13);var start=m.position();
        h.runAfterDelay(4,()->{m.setNoAi(false);h.assertTrue(m.startSkill(423,victim),"Ten-metre loaded landing is legal");victim.discard();});
        h.runAfterDelay(15,()->h.assertTrue(m.position().distanceToSqr(start)<.01,"All12tell ticks precede flight"));
        h.runAfterDelay(28,()->h.assertTrue(m.getY()>start.y+2.8&&m.getZ()>start.z+4&&!m.noPhysics&&!m.isNoGravity(),"Midpoint is physical3m arc, never phasing or no-gravity"));
        h.runAfterDelay(42,()->{h.assertTrue(m.phase()==AttackState.RECOVERY&&m.position().distanceToSqr(m.landing())<.03,"35tick impact reaches real floor, including final6tick warning interval");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=95,batch="bronze_gorilla")
    public static void eighteenTickTellThenOneRealBallisticBoulder(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,13);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(422,victim),"Throw starts"));
        h.runAfterDelay(21,()->h.assertTrue(stones(h,m).isEmpty()&&victim.getHealth()==1000,"All18tell ticks have no damaging projectile"));
        h.runAfterDelay(24,()->{var rocks=stones(h,m).stream().filter(e->!e.fragment()).toList();h.assertTrue(rocks.size()==1&&rocks.get(0).getDeltaMovement().horizontalDistance()>.4,"Exactly one1.5m native stone actually travels");for(var e:rocks)own(h,e);});
        h.runAfterDelay(55,()->{h.assertTrue(victim.getHealth()<1000&&stones(h,m).stream().filter(GorillaStone::fragment).count()<=3,"Physical throw contacts native victim; split cap3");m.hurt(m.damageSources().magic(),10000);});
        h.runAfterDelay(58,()->{h.assertTrue(stones(h,m).isEmpty(),"Owner death clears stones");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=65,batch="bronze_gorilla")
    public static void floorImpactCreatesExactlyThreeNonRecursiveFiniteFragments(GameTestHelper h){
        var m=caster(h);var rock=own(h,EliteContent.GORILLA_BOULDER.get().create(h.getLevel()));
        h.runAfterDelay(4,()->{var at=net.minecraft.world.phys.Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(7,2,9))).add(0,.05,0);rock.launch(m,at,new Vec3(0,-.2,.2));h.getLevel().addFreshEntity(rock);});
        h.runAfterDelay(8,()->{var shards=stones(h,m);h.assertTrue(rock.isRemoved()&&shards.size()==3&&shards.stream().allMatch(GorillaStone::fragment),"A real floor collision splits exactly3, not a particle approximation");for(var e:shards)own(h,e);});
        h.runAfterDelay(45,()->{h.assertTrue(stones(h,m).isEmpty(),"Fragments hit or expire within30ticks without recursive growth");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=75,batch="bronze_gorilla")
    public static void heavyInterruptAndTimeGapNeverReplayGroundOrThrownDamage(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,7);var tag=new CompoundTag();
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(421,victim),"Interruptible windup begins"));
        h.runAfterDelay(8,()->{m.hurt(m.damageSources().magic(),20);h.assertTrue(m.phase()==AttackState.STUN&&!m.attack().ready(421,h.getLevel().getGameTime()),"Accepted heavy hit interrupts, cooldown retained");m.saveWithoutId(tag);});
        h.runAfterDelay(45,()->{var restored=own(h,EliteContent.BRONZE_GORILLA.get().create(h.getLevel()));restored.load(tag);restored.setNoAi(true);restored.setPersistenceRequired();h.getLevel().addFreshEntity(restored);m.discard();});
        h.runAfterDelay(50,()->{h.assertTrue(victim.getHealth()==1000&&stones(h,m).isEmpty(),"Restored expired windup cannot dump delayed damage");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=75,batch="bronze_gorilla")
    public static void existingCampSlotKeepsUnloadedUuidAndConfirmedDeathCooldown(GameTestHelper h){
        var fixture=caster(h);fixture.discard();var feet=h.absolutePos(new BlockPos(7,2,7));var entrant=h.absolutePos(new BlockPos(7,2,0));String key="qa/bronze_gorilla/"+UUID.randomUUID();
        MARKERS.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(key);
        h.runAfterDelay(4,()->{h.assertTrue(EliteEncounters.spawnBronzeGorilla(h.getLevel(),key,feet,entrant),"Actual authored-site spawn helper succeeds");var marker=BlueprintSpawnState.get(h.getLevel()).markers.get(key);var actor=(BronzeGorilla)h.getLevel().getEntity(marker.members.iterator().next());own(h,actor);actor.setNoAi(true);actor.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);h.assertTrue(!marker.members.isEmpty()&&!EliteEncounters.spawnBronzeGorilla(h.getLevel(),key,feet,entrant),"Unload retains UUID; no duplicate materializes");
            BlueprintSpawnState.get(h.getLevel()).memberDied(actor.getUUID(),h.getLevel().getGameTime());h.assertTrue(marker.members.isEmpty()&&marker.nextSpawn==h.getLevel().getGameTime()+12000&&!EliteEncounters.spawnBronzeGorilla(h.getLevel(),key,feet,entrant),"Confirmed death preserves12000tick cooldown");BlueprintSpawnState.get(h.getLevel()).markers.remove(key);BlueprintSpawnState.get(h.getLevel()).setDirty();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=85,batch="bronze_gorilla")
    public static void newMidflightWallCancelsAndNormalGravityResumes(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,13);
        h.runAfterDelay(4,()->{m.setNoAi(false);h.assertTrue(m.startSkill(423,victim),"Legal flight starts before obstruction appears");victim.discard();});
        h.runAfterDelay(18,()->{for(int x=4;x<=10;x++)for(int y=2;y<9;y++)h.setBlock(x,y,9,Blocks.STONE);});
        h.runAfterDelay(42,()->h.assertTrue(m.phase()==AttackState.STUN&&!m.isNoGravity()&&!m.noPhysics&&!m.attack().ready(423,h.getLevel().getGameTime()),"Real collision cancels flight and keeps gravity/cooldown"));
        h.runAfterDelay(74,()->{h.assertTrue(m.onGround()&&m.getY()<h.absolutePos(new BlockPos(7,3,3)).getY(),"Native gravity returns interrupted actor to floor");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=70,batch="bronze_gorilla")
    public static void unloadedActiveCheckpointCannotReplayAnyOfEightImpacts(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,7);var tag=new CompoundTag();var restored=new java.util.concurrent.atomic.AtomicReference<BronzeGorilla>();
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(421,victim),"Active action begins"));
        h.runAfterDelay(11,()->{m.saveWithoutId(tag);m.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);});
        h.runAfterDelay(18,()->{var actor=own(h,EliteContent.BRONZE_GORILLA.get().create(h.getLevel()));actor.load(tag);actor.setNoAi(true);h.getLevel().addFreshEntity(actor);restored.set(actor);});
        h.runAfterDelay(60,()->{h.assertTrue(victim.getHealth()==1000&&restored.get().attack().current()==null&&!restored.get().attack().ready(421,h.getLevel().getGameTime()),"Time gap cancels checkpoint while keeping spent cooldown, no late damage");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=110,batch="bronze_gorilla_grief")
    public static void smashBreaksOnlyOneShallowAllowedCellPerSwing(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,7);grief(h,true);h.setBlock(8,1,5,Blocks.CHEST);h.setBlock(6,1,6,Blocks.IRON_ORE);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(421,victim),"Eight bounded floor punches begin"));
        h.runAfterDelay(96,()->{h.assertTrue(h.getBlockState(new BlockPos(6,1,4)).isAir()&&h.getBlockState(new BlockPos(6,0,4)).is(Blocks.STONE),"First allowed contact excavates exactly one layer");h.assertTrue(h.getBlockState(new BlockPos(8,1,5)).is(Blocks.CHEST)&&h.getBlockState(new BlockPos(6,1,6)).is(Blocks.IRON_ORE),"Containers and ores survive later contacts");h.succeed();});
    }
}
