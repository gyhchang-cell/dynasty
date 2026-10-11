package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.*;
import com.dynasty.blueprint.combat.AttackState;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.*;
import java.util.*;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class JinwuGameTests {
    private static final net.minecraft.server.level.TicketType<UUID> TICKET=net.minecraft.server.level.TicketType.create("dynasty_jinwu_qa",UUID::compareTo);
    private record Ticket(net.minecraft.world.level.ChunkPos chunk,UUID id){}
    private static final Map<ServerLevel,List<Ticket>> TICKETS=new HashMap<>();
    private static final Map<ServerLevel,List<Jinwu>> FIXTURES=new HashMap<>();
    @AfterBatch(batch="jinwu") public static void release(ServerLevel level){
        var fixtures=FIXTURES.remove(level);if(fixtures!=null)for(var m:fixtures)if(!m.isRemoved())m.discard();
        var tickets=TICKETS.remove(level);if(tickets!=null)for(var t:tickets)level.getChunkSource().removeRegionTicket(TICKET,t.chunk(),2,t.id(),true);
    }
    @AfterBatch(batch="jinwu_guard") public static void releaseGuard(ServerLevel level){release(level);}
    private static Jinwu mob(GameTestHelper h){
        var chunks=new HashSet<net.minecraft.world.level.ChunkPos>();
        for(int x:new int[]{0,15})for(int z:new int[]{0,15})chunks.add(new net.minecraft.world.level.ChunkPos(h.absolutePos(new BlockPos(x,2,z))));
        for(var c:chunks){var t=new Ticket(c,UUID.randomUUID());h.getLevel().getChunkSource().addRegionTicket(TICKET,c,2,t.id(),true);TICKETS.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(t);}
        for(int x=0;x<16;x++)for(int z=0;z<16;z++){h.setBlock(x,1,z,Blocks.STONE);for(int y=2;y<9;y++)h.setBlock(x,y,z,Blocks.AIR);}
        var m=h.spawn(EliteContent.JINWU.get(),new BlockPos(7,2,5));m.setNoAi(true);m.setNoGravity(true);m.bindEncounter("jinwu@"+m.getUUID()+":jinwu");FIXTURES.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(m);return m;
    }
    private static Cow cow(GameTestHelper h,int x,int z){
        var c=h.spawn(EntityType.COW,new BlockPos(x,2,z));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);c.setHealth(1000);c.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);return c;
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=35,batch="jinwu")
    public static void sweepUsesOneSecondTellAndAnActualShortRearDangerZone(GameTestHelper h){
        var m=mob(h);var front=cow(h,7,8);var near=cow(h,7,4);var far=cow(h,7,2);var escaped=cow(h,13,8);
        h.assertTrue(m.startSkill(341,front),"Registered server sweep starts");
        h.runAfterDelay(18,()->h.assertTrue(front.getHealth()==1000&&near.getHealth()==1000&&far.getHealth()==1000,"No premature damage during the one-second tell"));
        h.runAfterDelay(23,()->{h.assertTrue(front.getHealth()<1000&&near.getHealth()<1000,"Forward sweep and close rear hit use actual damage");h.assertTrue(far.getHealth()==1000&&escaped.getHealth()==1000,"Rear beyond 1.5 and forward beyond four blocks remain safe");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=45,batch="jinwu")
    public static void chargeTravelsEightBlocksAndHitsEachStripVictimOnlyOnce(GameTestHelper h){
        var m=mob(h);var front=cow(h,7,12);var side=cow(h,10,9);var start=m.position();h.assertTrue(m.startSkill(342,front),"Actual straight charge starts");
        h.runAfterDelay(14,()->h.assertTrue(m.position().distanceToSqr(start)<.01&&front.getHealth()==1000,"All three stomps precede physical movement"));
        h.runAfterDelay(34,()->{h.assertTrue(m.position().distanceTo(start)>=7.5&&m.position().distanceTo(start)<=8.1,"Physical travel remains within the eight-block budget: "+m.position().distanceTo(start));h.assertTrue(Math.abs(front.getHealth()-989)<.01&&side.getHealth()==1000,"One actual eleven-point hit per UUID and a safe side step: "+front.getHealth());h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=45,batch="jinwu")
    public static void collisionStopsTheChargeBeforeDamageBehindTheWall(GameTestHelper h){
        var m=mob(h);var front=cow(h,7,12);h.assertTrue(m.startSkill(342,front),"Charge locks before the wall is raised");
        for(int x=3;x<=11;x++)for(int y=2;y<=5;y++)h.setBlock(x,y,9,Blocks.STONE);
        h.runAfterDelay(31,()->{h.assertTrue(m.phase()==AttackState.STUN&&m.getZ()<h.absolutePos(new BlockPos(7,2,9)).getZ(),"Native collision ends movement in forty-tick recovery");h.assertTrue(front.getHealth()==1000,"No segment or damage crosses the wall");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="jinwu")
    public static void orderBuffsOnlyOrdinarySoldiersFromTheSameSiteAndExpires(GameTestHelper h){
        var m=mob(h);var target=cow(h,7,10);var ally=h.spawn(BlueprintEntities.ZUWU_DAOSHOU.get(),new BlockPos(5,2,6));var outside=h.spawn(BlueprintEntities.JUMA_CHANGQIANGBING.get(),new BlockPos(9,2,6));
        ally.setNoAi(true);ally.setNoGravity(true);outside.setNoAi(true);outside.setNoGravity(true);ally.bindEncounter(m.encounterSite()+":squad");outside.bindEncounter(m.encounterSite()+"-other:squad");
        h.assertTrue(m.startSkill(343,target),"Actual rally starts");
        h.runAfterDelay(22,()->h.assertTrue(!ally.hasEffect(MobEffects.DAMAGE_BOOST),"Full 1.2-second order tell"));
        h.runAfterDelay(27,()->{h.assertTrue(ally.hasEffect(MobEffects.DAMAGE_BOOST)&&ally.hasEffect(MobEffects.MOVEMENT_SPEED),"Real finite server effects reach the same-site ordinary soldier");h.assertTrue(!outside.hasEffect(MobEffects.DAMAGE_BOOST),"A neighbouring site's soldier cannot join");});
        h.runAfterDelay(90,()->{h.assertTrue(!ally.hasEffect(MobEffects.DAMAGE_BOOST)&&!ally.hasEffect(MobEffects.MOVEMENT_SPEED),"Both rally effects expire normally");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=35,batch="jinwu")
    public static void acceptedArmourReducedDamageInterruptsOrderWithoutDeferredBuffs(GameTestHelper h){
        var m=mob(h);var target=cow(h,7,10);var ally=h.spawn(BlueprintEntities.ZUWU_DAOSHOU.get(),new BlockPos(5,2,6));ally.setNoAi(true);ally.setNoGravity(true);ally.bindEncounter(m.encounterSite()+":squad");
        h.assertTrue(m.startSkill(343,target),"Order starts");m.hurt(m.damageSources().mobAttack(target),2);h.assertTrue(m.phase()==AttackState.WINDUP,"A small accepted hit does not fake a stagger");m.invulnerableTime=0;m.hurt(m.damageSources().mobAttack(target),30);
        h.assertTrue(m.phase()==AttackState.STUN,"At least eight accepted health loss interrupts the tell");
        h.runAfterDelay(29,()->{h.assertTrue(!ally.hasEffect(MobEffects.DAMAGE_BOOST),"Cancelled order never issues a delayed rally");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=45,batch="jinwu")
    public static void consumedSweepAndAbsoluteCooldownSurviveEntityReload(GameTestHelper h){
        var m=mob(h);var target=cow(h,7,8);h.assertTrue(m.startSkill(341,target),"Sweep starts");
        h.runAfterDelay(23,()->{float hp=target.getHealth();var t=new CompoundTag();m.save(t);var id=m.getUUID();var epoch=m.skillStart();m.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);var loaded=EliteContent.JINWU.get().create(h.getLevel());loaded.load(t);h.getLevel().addFreshEntity(loaded);FIXTURES.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(loaded);
            h.assertTrue(loaded.getUUID().equals(id)&&loaded.skillStart()==epoch&&!loaded.attack().ready(341,h.getLevel().getGameTime()),"Native identity, original action clock and cooldown persist");
            h.runAfterDelay(6,()->{h.assertTrue(target.getHealth()==hp,"Consumed sweep cannot replay after native NBT load");h.succeed();});
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="jinwu_guard")
    public static void fixedGuardSlotSurvivesUnloadAndDeathPermanentlyClearsIt(GameTestHelper h){
        var m=mob(h);m.discard();var level=h.getLevel();var feet=h.absolutePos(new BlockPos(7,2,5));level.getChunkAt(feet);
        var ticket=new Ticket(new net.minecraft.world.level.ChunkPos(feet),UUID.randomUUID());level.getChunkSource().addRegionTicket(TICKET,ticket.chunk(),2,ticket.id(),true);TICKETS.computeIfAbsent(level,k->new ArrayList<>()).add(ticket);
        for(int x=-2;x<=2;x++)for(int z=-2;z<=2;z++){level.setBlockAndUpdate(feet.offset(x,-1,z),Blocks.STONE.defaultBlockState());for(int y=0;y<4;y++)level.setBlockAndUpdate(feet.offset(x,y,z),Blocks.AIR.defaultBlockState());}
        String key="jinwu-guard@"+feet.asLong()+":jinwu";UUID[] id={null};
        h.startSequence().thenWaitUntil(()->h.assertTrue(level.isPositionEntityTicking(feet),"Wait for the isolated native entity section"))
            .thenExecute(()->{
                var rule=level.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING);boolean old=rule.get();rule.set(true,level.getServer());
                try{h.assertTrue(EliteEncounters.spawnJinwu(level,key,feet,feet.offset(0,0,8)),"One registered guard occupies the real floor");var marker=BlueprintSpawnState.get(level).markers.get(key);id[0]=marker.members.iterator().next();h.assertTrue(!EliteEncounters.spawnJinwu(level,key,feet,feet.offset(0,0,8)),"A second entrant cannot duplicate it");}
                finally{rule.set(old,level.getServer());}
            }).thenIdle(2).thenExecute(()->{
                var rule=level.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING);boolean old=rule.get();rule.set(true,level.getServer());
                try{var marker=BlueprintSpawnState.get(level).markers.get(key);var actor=level.getEntity(id[0]);h.assertTrue(actor instanceof Jinwu,"Native entity manager resolves the saved guard UUID");var tag=new CompoundTag();actor.save(tag);actor.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);h.assertTrue(!EliteEncounters.spawnJinwu(level,key,feet,feet.offset(0,0,8)),"Unload retains its saved slot");var loaded=EliteContent.JINWU.get().create(level);loaded.load(tag);level.addFreshEntity(loaded);loaded.hurt(loaded.damageSources().genericKill(),10000);
                    h.assertTrue(marker.cleared&&marker.members.isEmpty()&&BlueprintSpawnState.load(BlueprintSpawnState.get(level).save(new CompoundTag())).markers.get(key).cleared,"Confirmed death saves the permanent clear");h.assertTrue(!EliteEncounters.spawnJinwu(level,key,feet,feet.offset(0,0,8)),"Cleared structure cannot respawn another guard");
                }finally{rule.set(old,level.getServer());}
            }).thenSucceed();
    }
}
