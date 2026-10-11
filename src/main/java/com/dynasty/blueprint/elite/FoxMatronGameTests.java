package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.*;
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

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class FoxMatronGameTests {
    private static final net.minecraft.server.level.TicketType<UUID> TICKET=net.minecraft.server.level.TicketType.create("dynasty_fox_qa",UUID::compareTo);
    private record Ticket(net.minecraft.world.level.ChunkPos chunk,UUID id){}
    private static final Map<ServerLevel,List<Ticket>> TICKETS=new HashMap<>();
    private static final Map<ServerLevel,List<FoxMatron>> FIXTURES=new HashMap<>();
    @AfterBatch(batch="fox_matron") public static void cleanup(ServerLevel level){
        var actors=FIXTURES.remove(level);if(actors!=null)for(var m:actors){for(var clone:level.getEntitiesOfClass(FoxMatron.class,m.getBoundingBox().inflate(32),f->f.ownedBy(m)))clone.discard();if(!m.isRemoved())m.discard();}
        var ts=TICKETS.remove(level);if(ts!=null)for(var t:ts)level.getChunkSource().removeRegionTicket(TICKET,t.chunk(),2,t.id(),true);
    }
    @AfterBatch(batch="fox_guard") public static void cleanupGuard(ServerLevel level){cleanup(level);}
    @AfterBatch(batch="fox_hover") public static void cleanupHover(ServerLevel level){cleanup(level);}
    private static FoxMatron fox(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++){h.setBlock(x,1,z,Blocks.STONE);for(int y=2;y<8;y++)h.setBlock(x,y,z,Blocks.AIR);}
        for(int x:new int[]{0,15})for(int z:new int[]{0,15}){var t=new Ticket(new net.minecraft.world.level.ChunkPos(h.absolutePos(new BlockPos(x,2,z))),UUID.randomUUID());h.getLevel().getChunkSource().addRegionTicket(TICKET,t.chunk(),2,t.id(),true);TICKETS.computeIfAbsent(h.getLevel(),l->new ArrayList<>()).add(t);}
        var m=h.spawn(EliteContent.FOX.get(),new BlockPos(7,2,5));m.setNoAi(true);m.bindEncounter("fox-test@"+m.getUUID()+":fox_matron");FIXTURES.computeIfAbsent(h.getLevel(),l->new ArrayList<>()).add(m);return m;
    }
    private static Cow cow(GameTestHelper h,int x,int z){var c=h.spawn(EntityType.COW,new BlockPos(x,2,z));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);c.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);c.setHealth(1000);return c;}
    @GameTest(template="bow_ritual_test",timeoutTicks=120,batch="fox_hover")
    public static void ordinaryIdleFlyingControllerPreservesTheHalfBlockHover(GameTestHelper h){
        var m=fox(h);m.setPersistenceRequired();m.setPos(m.position().add(0,.5,0));double initial=m.getY();
        h.startSequence().thenWaitUntil(()->h.assertTrue(m.tickCount>=2&&h.getLevel().isPositionEntityTicking(m.blockPosition()),"Normal controller test starts only in a native ticking section"))
        .thenExecute(()->m.setNoAi(false)).thenIdle(24).thenExecute(()->{h.assertTrue(m.isAlive()&&!m.isNoAi()&&m.isNoGravity()&&Math.abs(m.getY()-initial)<.05,"The ordinary flying controller cannot turn gravity back on while idle: y="+m.getY()+" initial="+initial+" noGravity="+m.isNoGravity());}).thenSucceed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=130,batch="fox_matron")
    public static void slowBeamHasAFullTellOneHitAndAFiniteNativeHaze(GameTestHelper h){
        var m=fox(h);var victim=cow(h,7,11);h.assertTrue(m.startSkill(351,victim),"Native mirror starts");
        h.runAfterDelay(19,()->h.assertTrue(victim.getHealth()==1000,"No damage before full one-second tell"));
        h.runAfterDelay(43,()->h.assertTrue(victim.getHealth()<1000&&victim.hasEffect(EliteContent.FOX_HAZE.get()),"Slow physical ray segment reaches the real target and applies native haze"));
        h.runAfterDelay(65,()->h.assertTrue(Math.abs(victim.getHealth()-994.4)<.01,"Each projectile can hit only once"));
        h.runAfterDelay(125,()->{h.assertTrue(!victim.hasEffect(EliteContent.FOX_HAZE.get()),"Four-second native effect cannot stick permanently");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60,batch="fox_matron")
    public static void aNewWallStopsTheAlreadyLockedSlowBeam(GameTestHelper h){
        var m=fox(h);var victim=cow(h,7,11);h.assertTrue(m.startSkill(351,victim),"Beam locks before wall exists");for(int x=6;x<=8;x++)for(int y=2;y<=5;y++)h.setBlock(x,y,8,Blocks.STONE);
        h.runAfterDelay(55,()->{h.assertTrue(victim.getHealth()==1000&&!victim.hasEffect(EliteContent.FOX_HAZE.get()),"Actual block collider stops the travelling segment");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=75,batch="fox_matron")
    public static void fiveFireCellsRemainLockedAndSideSteppingIsSafe(GameTestHelper h){
        var m=fox(h);var victim=cow(h,7,8);var side=cow(h,11,8);h.assertTrue(m.startSkill(352,victim),"Five-cell native fire starts");var origin=m.firePoint(0);
        h.runAfterDelay(19,()->h.assertTrue(victim.getHealth()==1000,"First marked cell waits twenty ticks"));
        h.runAfterDelay(23,()->{h.assertTrue(victim.getHealth()<1000,"First actual column impacts its marked cell");victim.setPos(victim.position().add(4,0,0));});
        h.runAfterDelay(72,()->{h.assertTrue(m.firePoint(0).distanceToSqr(origin)<.0001,"Marks never retarget after the tell");h.assertTrue(side.getHealth()==1000,"Lateral escape remains outside every real fire hitbox");h.assertTrue(Arrays.equals(Arrays.stream(m.attack().save().getIntArray("Fired")).sorted().toArray(),new int[]{20,32,44,56,68}),"Exactly five consumed server impact frames");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=35,batch="fox_matron")
    public static void aHeavyAcceptedHitCreatesOnlyTwoHarmlessOneHealthDecoys(GameTestHelper h){
        var m=fox(h);var victim=cow(h,7,10);m.hurt(m.damageSources().mobAttack(victim),30);h.assertTrue(m.skillId()==353,"Accepted heavy damage triggers the actual split tell");
        h.runAfterDelay(10,()->{
            var clones=h.getLevel().getEntitiesOfClass(FoxMatron.class,m.getBoundingBox().inflate(16),f->f.ownedBy(m));h.assertTrue(clones.size()==2&&clones.stream().allMatch(f->f.isDecoy()&&f.getMaxHealth()==1),"Only two real owner-bound one-health decoys");
            h.assertTrue(clones.stream().noneMatch(f->f.startSkill(351,victim)),"Fake casters cannot deal real attacks");var clone=clones.get(0);clone.hurt(clone.damageSources().genericKill(),10000);
            h.assertTrue(m.isAlive(),"Breaking a fake leaves the real caster alive");m.hurt(m.damageSources().genericKill(),10000);
            h.assertTrue(clones.stream().allMatch(Entity::isRemoved),"Actual owner death immediately cleans up both fake actors");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40,batch="fox_matron")
    public static void consumedFireEpochAndCooldownSurviveNativeNbtReload(GameTestHelper h){
        var m=fox(h);var victim=cow(h,7,10);h.assertTrue(m.startSkill(352,victim),"Native fire starts");
        h.runAfterDelay(25,()->{var tag=new CompoundTag();m.save(tag);float hp=victim.getHealth();long epoch=m.skillStart();var id=m.getUUID();m.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);var loaded=EliteContent.FOX.get().create(h.getLevel());loaded.load(tag);h.getLevel().addFreshEntity(loaded);FIXTURES.get(h.getLevel()).add(loaded);
            h.assertTrue(loaded.getUUID().equals(id)&&loaded.skillStart()==epoch&&!loaded.attack().ready(352,h.getLevel().getGameTime()),"Original entity/action/cooldown persist");h.runAfterDelay(4,()->{h.assertTrue(victim.getHealth()==hp,"Consumed first column cannot replay after load");h.succeed();});
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="fox_guard")
    public static void realNightGuardLedgerRejectsDuplicatesAndRetainsAnUnloadedUuid(GameTestHelper h){
        var m=fox(h);m.discard();var level=h.getLevel();var feet=h.absolutePos(new BlockPos(7,2,5));String key="fox-guard@"+feet.asLong()+":fox_matron";
        long[] originalDay={0};boolean[] originalRule={false};
        h.startSequence().thenWaitUntil(()->h.assertTrue(level.isPositionEntityTicking(feet),"Wait for actual native ticking section"))
        .thenExecute(()->{originalDay[0]=level.getDayTime();originalRule[0]=level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING);level.setDayTime(18000);level.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING).set(true,level.getServer());})
        .thenIdle(2).thenExecute(()->{
            try{h.assertTrue(!level.isDay(),"Native skylight cache has actually entered night");h.assertTrue(EliteEncounters.spawnFox(level,key,feet,feet.offset(0,0,8)),"Real night floor accepts one registered fox");var marker=BlueprintSpawnState.get(level).markers.get(key);var id=marker.members.iterator().next();h.assertTrue(!EliteEncounters.spawnFox(level,key,feet,feet.offset(0,0,8)),"Second entrant cannot duplicate the matron");
                var actor=level.getEntity(id);h.assertTrue(actor instanceof FoxMatron,"Actual entity manager resolves guard UUID");FIXTURES.get(level).add((FoxMatron)actor);actor.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);h.assertTrue(marker.members.contains(id)&&!EliteEncounters.spawnFox(level,key,feet,feet.offset(0,0,8)),"Chunk unload keeps its encounter slot");h.succeed();
            }finally{level.setDayTime(originalDay[0]);level.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING).set(originalRule[0],level.getServer());}
        });
    }
}
