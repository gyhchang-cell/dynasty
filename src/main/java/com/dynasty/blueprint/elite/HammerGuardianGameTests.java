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

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class HammerGuardianGameTests {
    private static final net.minecraft.server.level.TicketType<UUID> TICKET=net.minecraft.server.level.TicketType.create("dynasty_hammer_qa",UUID::compareTo);
    private record Ticket(net.minecraft.world.level.ChunkPos chunk,UUID id){}
    private static final Map<ServerLevel,List<Ticket>> TICKETS=new HashMap<>();
    private static final Map<ServerLevel,List<Entity>> FIXTURES=new HashMap<>();
    @AfterBatch(batch="hammer") public static void release(ServerLevel level){
        var fixtures=FIXTURES.remove(level);if(fixtures!=null)for(var m:fixtures){if(m instanceof HammerGuardian caster)level.getEntitiesOfClass(HammerChain.class,caster.getBoundingBox().inflate(32),e->e.ownedBy(caster)).forEach(Entity::discard);if(!m.isRemoved())m.discard();}
        var tickets=TICKETS.remove(level);if(tickets!=null)for(var t:tickets)level.getChunkSource().removeRegionTicket(TICKET,t.chunk(),2,t.id(),true);
    }
    @AfterBatch(batch="hammer_guard") public static void releaseGuard(ServerLevel level){release(level);}
    private static <T extends Entity>T own(GameTestHelper h,T entity){FIXTURES.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(entity);return entity;}
    private static HammerGuardian mob(GameTestHelper h){
        var chunks=new HashSet<net.minecraft.world.level.ChunkPos>();for(int x:new int[]{0,15})for(int z:new int[]{0,15})chunks.add(new net.minecraft.world.level.ChunkPos(h.absolutePos(new BlockPos(x,2,z))));
        for(var c:chunks){var t=new Ticket(c,UUID.randomUUID());h.getLevel().getChunkSource().addRegionTicket(TICKET,c,2,t.id(),true);TICKETS.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(t);}
        for(int x=0;x<16;x++)for(int z=0;z<16;z++){h.setBlock(x,1,z,Blocks.STONE);for(int y=2;y<9;y++)h.setBlock(x,y,z,Blocks.AIR);}
        var m=own(h,h.spawn(EliteContent.HAMMER.get(),new BlockPos(7,2,5)));m.setNoAi(true);m.setNoGravity(true);m.setPersistenceRequired();m.bindEncounter("hammer@"+m.getUUID()+":hammer_guardian");return m;
    }
    private static Cow cow(GameTestHelper h,int x,int y,int z){var c=own(h,h.spawn(EntityType.COW,new BlockPos(x,y,z)));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);c.setHealth(1000);c.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);return c;}
    @GameTest(template="bow_ritual_test",timeoutTicks=650,batch="hammer")
    public static void groundWaveHasARealTellExpandingRingsAndJumpCounter(GameTestHelper h){
        var m=mob(h);var near=cow(h,7,2,7);var middle=cow(h,7,2,9);var outer=cow(h,7,2,11);var airborne=cow(h,8,3,7);
        var level=h.getLevel();var origin=new BlockPos(26000,130,26000);var offset=net.minecraft.world.phys.Vec3.atLowerCornerOf(origin.subtract(h.absolutePos(new BlockPos(0,2,0))));
        for(int x:new int[]{0,15})for(int z:new int[]{0,15}){var c=new net.minecraft.world.level.ChunkPos(origin.offset(x,0,z));level.getChunk(c.x,c.z);var t=new Ticket(c,UUID.randomUUID());level.getChunkSource().addRegionTicket(TICKET,c,2,t.id(),true);TICKETS.computeIfAbsent(level,k->new ArrayList<>()).add(t);}
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=-1;y<8;y++)level.setBlockAndUpdate(origin.offset(x,y,z),(y==-1?Blocks.STONE:Blocks.AIR).defaultBlockState());
        for(var actor:List.of(m,near,middle,outer,airborne)){actor.moveTo(actor.position().add(offset));actor.setDeltaMovement(net.minecraft.world.phys.Vec3.ZERO);}
        h.startSequence().thenWaitUntil(()->h.assertTrue(level.isPositionEntityTicking(m.blockPosition())&&m.tickCount>=2,"Private ring court has native entity ticking"))
            .thenExecute(()->h.assertTrue(m.startSkill(361,near),"Double slam starts from registered server actor"))
            .thenIdle(25).thenExecute(()->h.assertTrue(near.getHealth()==1000&&middle.getHealth()==1000&&outer.getHealth()==1000,"Full 28-tick tell remains harmless"))
            .thenIdle(6).thenExecute(()->h.assertTrue(near.getHealth()<1000&&middle.getHealth()==1000&&outer.getHealth()==1000,"Only the first circle reached contact"))
            .thenIdle(16).thenExecute(()->h.assertTrue(middle.getHealth()<1000&&outer.getHealth()==1000,"Second ring reaches four blocks independently"))
            .thenIdle(16).thenExecute(()->{h.assertTrue(outer.getHealth()<1000&&airborne.getHealth()==1000,"Six-block ring is real, while raised feet evade all waves: outer="+outer.getHealth()+" airborne="+airborne.getHealth()+" actor="+m.position());h.assertTrue(m.shockDamage().is(net.minecraft.tags.DamageTypeTags.BYPASSES_SHIELD),"Registered physical wave explicitly bypasses a raised shield");}).thenSucceed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=110,batch="hammer")
    public static void slowWheelCollidesWithStoneAndGivesThreeSecondsOfRealStun(GameTestHelper h){
        var m=mob(h);var target=cow(h,7,2,11);h.assertTrue(m.startSkill(362,target),"Wheel starts before a wall is installed");
        for(int x=4;x<=10;x++)for(int y=2;y<=5;y++)h.setBlock(x,y,7,Blocks.STONE);
        h.runAfterDelay(16,()->{h.assertTrue(m.phase()==AttackState.WINDUP,"Nine-tenths-second tell");m.knockback(3,1,0);h.assertTrue(m.getDeltaMovement().horizontalDistanceSqr()<.001,"Windup has genuine knockback resistance");});
        h.runAfterDelay(35,()->{h.assertTrue(m.phase()==AttackState.STUN&&m.skillId()==0,"Native movement collision enters a real stun and cancels further impacts");h.assertTrue(target.getHealth()==1000,"Wall blocks all remaining swings");});
        h.runAfterDelay(70,()->h.assertTrue(m.phase()==AttackState.STUN,"Collision recovery lasts for the actual three-second window"));
        h.runAfterDelay(95,()->{h.assertTrue(m.phase()==AttackState.IDLE&&!m.attack().ready(362,h.getLevel().getGameTime()),"Stun expires without resetting the spent wheel cooldown");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="hammer")
    public static void onePhysicalHammerReturnsAndCannotSurviveOwnerDeath(GameTestHelper h){
        var m=mob(h);var target=cow(h,7,2,14);h.assertTrue(m.startSkill(363,target),"Long throw starts");
        h.runAfterDelay(33,()->h.assertTrue(h.getLevel().getEntitiesOfClass(HammerChain.class,m.getBoundingBox().inflate(20),e->e.ownedBy(m)).isEmpty()&&target.getHealth()==1000,"No projectile or damage during the long tell"));
        h.runAfterDelay(40,()->{var list=h.getLevel().getEntitiesOfClass(HammerChain.class,m.getBoundingBox().inflate(20),e->e.ownedBy(m));h.assertTrue(list.size()==1&&list.get(0).ownerId().equals(m.getUUID()),"Exactly one physical owner-bound hammer");});
        h.runAfterDelay(83,()->h.assertTrue(target.getHealth()<1000,"Actual outgoing/returning sweep intersects the target"));
        h.runAfterDelay(88,()->{h.assertTrue(h.getLevel().getEntitiesOfClass(HammerChain.class,m.getBoundingBox().inflate(20),e->e.ownedBy(m)).isEmpty(),"Absolute 48-tick lifetime terminates the chain");var probe=EliteContent.HAMMER_CHAIN.get().create(h.getLevel());probe.launch(m,new net.minecraft.world.phys.Vec3(0,0,1));h.getLevel().addFreshEntity(probe);own(h,probe);m.hurt(m.damageSources().genericKill(),10000);h.assertTrue(probe.isRemoved(),"Owner death cleans the remaining physical projectile immediately");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=55,batch="hammer")
    public static void consumedThrowAndAbsoluteCooldownSurviveNativeActorReload(GameTestHelper h){
        var m=mob(h);var target=cow(h,7,2,14);h.assertTrue(m.startSkill(363,target),"Throw starts");
        h.runAfterDelay(40,()->{var tag=new CompoundTag();m.save(tag);var old=m.attack().save();m.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);var loaded=own(h,EliteContent.HAMMER.get().create(h.getLevel()));loaded.load(tag);h.getLevel().addFreshEntity(loaded);
            h.assertTrue(loaded.getUUID().equals(m.getUUID())&&loaded.skillStart()==old.getLong("Started")&&Arrays.equals(loaded.attack().save().getIntArray("Fired"),old.getIntArray("Fired")),"UUID, original clock and consumed release survive native NBT");h.assertTrue(!loaded.attack().ready(363,h.getLevel().getGameTime()),"Absolute spent cooldown survives load");
            h.runAfterDelay(7,()->{h.assertTrue(h.getLevel().getEntitiesOfClass(HammerChain.class,loaded.getBoundingBox().inflate(20),e->e.ownedBy(loaded)).size()<=1,"Loading a consumed throw cannot duplicate its physical hammer");h.succeed();});
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40,batch="hammer")
    public static void acceptedHeavyWindupDamageInterruptsTheThrowBeforeRelease(GameTestHelper h){
        var m=mob(h);var target=cow(h,7,2,14);h.assertTrue(m.startSkill(363,target),"Throw starts");m.invulnerableTime=0;m.hurt(m.damageSources().mobAttack(target),45);
        h.assertTrue(m.isAlive()&&m.phase()==AttackState.STUN,"Accepted health loss interrupts the actual windup");
        h.runAfterDelay(38,()->{h.assertTrue(h.getLevel().getEntitiesOfClass(HammerChain.class,m.getBoundingBox().inflate(20),e->e.ownedBy(m)).isEmpty()&&target.getHealth()==1000,"Interrupted throw cannot release after its original contact frame");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=160,batch="hammer_guard")
    public static void nativeGuardSlotPersistsWhileUnloadedAndClearsOnceOnDeath(GameTestHelper h){
        var m=mob(h);m.discard();var world=h.getLevel();var feet=h.absolutePos(new BlockPos(7,2,5));String key="hammer-guard@"+feet.asLong()+":hammer_guardian";
        h.startSequence().thenWaitUntil(()->h.assertTrue(world.isPositionEntityTicking(feet),"Wait for the native entity section"))
            .thenExecute(()->{var rule=world.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING);boolean old=rule.get();rule.set(true,world.getServer());try{
                h.assertTrue(EliteEncounters.spawnHammer(world,key,feet,feet.offset(0,0,8)),"The registered guard occupies a real collision-free floor");var marker=BlueprintSpawnState.get(world).markers.get(key);var actor=world.getEntity(marker.members.iterator().next());h.assertTrue(actor instanceof HammerGuardian,"Saved UUID resolves to the actual native entity");own(h,actor);h.assertTrue(!EliteEncounters.spawnHammer(world,key,feet,feet.offset(0,0,8)),"Another entrant cannot duplicate it");
                var tag=new CompoundTag();actor.save(tag);actor.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);h.assertTrue(!EliteEncounters.spawnHammer(world,key,feet,feet.offset(0,0,8)),"Chunk unload retains the occupied slot");var loaded=own(h,EliteContent.HAMMER.get().create(world));loaded.load(tag);world.addFreshEntity(loaded);loaded.hurt(loaded.damageSources().genericKill(),10000);
                h.assertTrue(marker.cleared&&marker.members.isEmpty()&&BlueprintSpawnState.load(BlueprintSpawnState.get(world).save(new CompoundTag())).markers.get(key).cleared,"Confirmed death writes the permanent clear exactly once");h.assertTrue(!EliteEncounters.spawnHammer(world,key,feet,feet.offset(0,0,8)),"Cleared tomb cannot recreate this guard");
            }finally{rule.set(old,world.getServer());}}).thenSucceed();
    }
}
