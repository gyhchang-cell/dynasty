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
import net.minecraftforge.gametest.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicReference;

/** Prepared source only while the user pauses Java; real collision and persistence regressions. */
@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class TideYashaGameTests {
    private static final net.minecraft.server.level.TicketType<UUID> TICKET=net.minecraft.server.level.TicketType.create("dynasty_tide_qa",UUID::compareTo);
    private record Ticket(net.minecraft.world.level.ChunkPos chunk,UUID id){}
    private static final Map<ServerLevel,List<Ticket>> TICKETS=new HashMap<>();
    private static final Map<ServerLevel,List<Entity>> FIXTURES=new HashMap<>();
    private static <T extends Entity>T own(GameTestHelper h,T e){FIXTURES.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(e);return e;}
    @AfterBatch(batch="tide_yasha") public static void release(ServerLevel world){
        var fixtures=FIXTURES.remove(world);if(fixtures!=null)for(var e:fixtures){if(e instanceof TideYasha caster)caster.clearOwned();if(!e.isRemoved())e.discard();}
        var tickets=TICKETS.remove(world);if(tickets!=null)for(var t:tickets)world.getChunkSource().removeRegionTicket(TICKET,t.chunk(),2,t.id(),true);
    }
    private static TideYasha caster(GameTestHelper h){
        var chunks=new HashSet<net.minecraft.world.level.ChunkPos>();for(int x:new int[]{0,15})for(int z:new int[]{0,15})chunks.add(new net.minecraft.world.level.ChunkPos(h.absolutePos(new BlockPos(x,2,z))));
        for(var chunk:chunks){var t=new Ticket(chunk,UUID.randomUUID());h.getLevel().getChunkSource().addRegionTicket(TICKET,chunk,2,t.id(),true);TICKETS.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(t);}
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<10;y++)h.setBlock(x,y,z,y==1?Blocks.STONE:Blocks.AIR);
        var m=own(h,h.spawn(EliteContent.TIDE_YASHA.get(),new BlockPos(7,2,3)));m.setNoAi(true);m.setPersistenceRequired();return m;
    }
    private static Cow target(GameTestHelper h,int x,int z){var c=own(h,h.spawn(EntityType.COW,new BlockPos(x,2,z)));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);c.setHealth(1000);return c;}
    @GameTest(template="bow_ritual_test",timeoutTicks=90,batch="tide_yasha")
    public static void eighteenTickWaveRetainsCentreGapAndStopsAtARealWall(GameTestHelper h){
        var m=caster(h);var centre=target(h,7,13);var left=target(h,4,13);var right=target(h,10,13);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(391,centre),"Native wave begins in clear sight"));
        h.runAfterDelay(20,()->h.assertTrue(h.getLevel().getEntitiesOfClass(TideVortex.class,m.getBoundingBox().inflate(20),v->v.ownedBy(m)).isEmpty(),"No damaging columns before the full eighteen-tick tell"));
        h.runAfterDelay(26,()->{h.assertTrue(h.getLevel().getEntitiesOfClass(TideVortex.class,m.getBoundingBox().inflate(20),v->v.ownedBy(m)).size()==2,"Exactly two diverging registered native columns");for(int x=0;x<16;x++)for(int y=2;y<6;y++)h.setBlock(x,y,9,Blocks.STONE);});
        h.runAfterDelay(70,()->{h.assertTrue(centre.getHealth()==1000&&left.getHealth()==1000&&right.getHealth()==1000,"Full-height physical wall protects all targets, including centre gap");h.assertTrue(h.getLevel().getEntitiesOfClass(TideVortex.class,m.getBoundingBox().inflate(20),v->v.ownedBy(m)).isEmpty(),"Blocked columns terminate");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=95,batch="tide_yasha")
    public static void divergingColumnsLiftSideTargetsOnceAndLeaveTheCentreClear(GameTestHelper h){
        var m=caster(h);var centre=target(h,7,13);var left=target(h,4,13);var right=target(h,10,13);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(391,centre),"Wave begins"));
        h.runAfterDelay(65,()->{h.assertTrue(centre.getHealth()==1000,"The centre route remains outside both damaging columns");h.assertTrue(left.getHealth()<1000&&left.getHealth()>=992&&right.getHealth()<1000&&right.getHealth()>=992,"Each column damages its side target at most once through native damage");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=95,batch="tide_yasha")
    public static void diveLocksTheWarningThenRejectsAWalledEmergence(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,9);var locked=new AtomicReference<net.minecraft.world.phys.Vec3>();var start=m.position();
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(392,victim),"Native dive begins at a reachable floor"));
        h.runAfterDelay(16,()->victim.teleportTo(victim.getX()+2,victim.getY(),victim.getZ()));
        h.runAfterDelay(26,()->{locked.set(m.poolPoint());victim.teleportTo(victim.getX()+2,victim.getY(),victim.getZ());for(int x=0;x<16;x++)for(int y=2;y<7;y++)h.setBlock(x,y,6,Blocks.STONE);});
        h.runAfterDelay(32,()->h.assertTrue(m.poolPoint().equals(locked.get())&&victim.getHealth()==1000,"Last ten ticks lock the exact visible warning and remain harmless"));
        h.runAfterDelay(39,()->{h.assertTrue(m.position().distanceToSqr(start)<.01&&victim.getHealth()==1000,"A new physical wall cancels emergence instead of teleporting through it");h.assertTrue(!m.attack().ready(392,h.getLevel().getGameTime()),"Cancellation retains consumed dive cooldown");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=110,batch="tide_yasha")
    public static void threeNativeDashesTravelSixBlocksAndWallContactInterrupts(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,7);var start=m.position();
        // Remove the bait after locking the direction so its body cannot clip the test route.
        h.runAfterDelay(4,()->{m.setNoAi(false);h.assertTrue(m.startSkill(393,victim),"Three-dash tell begins");victim.discard();});
        h.runAfterDelay(41,()->h.assertTrue(m.getY()>start.y+.1,"Third dash uses native gravity and a real jump, rather than a visual-only rise"));
        h.runAfterDelay(55,()->{h.assertTrue(Math.abs(m.position().subtract(start).horizontalDistance()-6)<.08,"Three actual clipped move calls cover two blocks per ten-tick segment");m.attack().cancel();m.teleportTo(start.x,start.y,start.z);m.attack().load(new CompoundTag(),TideYasha::skill,h.getLevel().getGameTime());var next=target(h,7,7);h.assertTrue(m.startSkill(393,next),"Independent wall-contact case starts");next.discard();for(int x=0;x<16;x++)for(int y=2;y<6;y++)h.setBlock(x,y,6,Blocks.STONE);});
        h.runAfterDelay(80,()->{h.assertTrue(m.getZ()<h.absolutePos(new BlockPos(7,2,6)).getZ()-1,"Normal collider stops the first dash before the wall");h.assertTrue(m.phase()==AttackState.STUN&&m.skillId()==0,"Physical contact creates the advertised counter window");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=90,batch="tide_yasha")
    public static void heavyInterruptAndSameUuidSavePreserveCooldownWithoutLateRelease(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,11);var live=new AtomicReference<>(m);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(391,victim),"Interruptible tell starts"));
        h.runAfterDelay(8,()->{float before=m.getHealth();h.assertTrue(m.hurt(m.damageSources().mobAttack(victim),20)&&before-m.getHealth()>=8,"Actual armored damage exceeds the interrupt threshold");h.assertTrue(m.phase()==AttackState.STUN&&!m.attack().ready(391,h.getLevel().getGameTime()),"Heavy contact consumes the original cooldown");var tag=new CompoundTag();m.save(tag);m.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);var restored=own(h,EliteContent.TIDE_YASHA.get().create(h.getLevel()));restored.load(tag);restored.setNoAi(true);h.getLevel().addFreshEntity(restored);live.set(restored);});
        h.runAfterDelay(40,()->{h.assertTrue(live.get().getUUID().equals(m.getUUID())&&!live.get().attack().ready(391,h.getLevel().getGameTime()),"Original UUID and absolute cooldown survive native NBT");h.assertTrue(h.getLevel().getEntitiesOfClass(TideVortex.class,live.get().getBoundingBox().inflate(20),v->v.ownedBy(live.get())).isEmpty(),"Cancelled release never replays after restore");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=110,batch="tide_yasha")
    public static void submergedSlotRejectsDryEntryRetainsUnloadAndStartsDeathCooldown(GameTestHelper h){
        var fixture=caster(h);var feet=fixture.blockPosition();fixture.discard();String key="tide-native@"+feet.asLong()+":tide_yasha";var world=h.getLevel();
        h.startSequence().thenWaitUntil(()->h.assertTrue(world.isPositionEntityTicking(feet),"Ruin fixture is entity-ticking")).thenExecute(()->{
            var rule=world.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING);boolean old=rule.get();rule.set(true,world.getServer());try{
                h.assertTrue(!EliteEncounters.spawnTideYasha(world,key,feet,feet.offset(0,0,8)),"Dry floor cannot act as a submerged ruin entry");
                for(int x=4;x<=10;x++)for(int z=0;z<=6;z++)for(int y=2;y<=4;y++)h.setBlock(x,y,z,Blocks.WATER);
                h.assertTrue(EliteEncounters.spawnTideYasha(world,key,feet,feet.offset(0,0,8)),"Clear loaded water floor spawns one ordinary actor");var marker=BlueprintSpawnState.get(world).markers.get(key);var actor=(TideYasha)own(h,world.getEntity(marker.members.iterator().next()));var tag=new CompoundTag();actor.save(tag);actor.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
                h.assertTrue(!EliteEncounters.spawnTideYasha(world,key,feet,feet.offset(0,0,8)),"Unloaded UUID reserves its existing encounter slot");var restored=own(h,EliteContent.TIDE_YASHA.get().create(world));restored.load(tag);world.addFreshEntity(restored);restored.hurt(restored.damageSources().genericKill(),10000);
                h.assertTrue(marker.members.isEmpty()&&marker.nextSpawn==world.getGameTime()+12000,"Confirmed death starts the existing saved cooldown");h.assertTrue(!EliteEncounters.spawnTideYasha(world,key,feet,feet.offset(0,0,8)),"Another entrant cannot skip that cooldown");
            }finally{rule.set(old,world.getServer());}
        }).thenSucceed();
    }
}
