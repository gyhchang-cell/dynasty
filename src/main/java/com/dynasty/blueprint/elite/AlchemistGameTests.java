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

/** Prepared for the next authorized Java run; never a substitute for client/network acceptance. */
@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class AlchemistGameTests {
    private static final net.minecraft.server.level.TicketType<UUID> TICKET=net.minecraft.server.level.TicketType.create("dynasty_alchemy_qa",UUID::compareTo);
    private record Ticket(net.minecraft.world.level.ChunkPos chunk,UUID id){}
    private static final Map<ServerLevel,List<Ticket>> TICKETS=new HashMap<>();
    private static final Map<ServerLevel,List<Entity>> FIXTURES=new HashMap<>();
    private static <T extends Entity>T own(GameTestHelper h,T e){FIXTURES.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(e);return e;}
    @AfterBatch(batch="alchemist") public static void release(ServerLevel level){
        var fixtures=FIXTURES.remove(level);if(fixtures!=null)for(var e:fixtures){if(e instanceof Alchemist caster)caster.clearOwned();if(!e.isRemoved())e.discard();}
        var tickets=TICKETS.remove(level);if(tickets!=null)for(var t:tickets)level.getChunkSource().removeRegionTicket(TICKET,t.chunk(),2,t.id(),true);
    }
    private static Alchemist caster(GameTestHelper h){
        var chunks=new HashSet<net.minecraft.world.level.ChunkPos>();for(int x:new int[]{0,15})for(int z:new int[]{0,15})chunks.add(new net.minecraft.world.level.ChunkPos(h.absolutePos(new BlockPos(x,2,z))));
        for(var c:chunks){var t=new Ticket(c,UUID.randomUUID());h.getLevel().getChunkSource().addRegionTicket(TICKET,c,2,t.id(),true);TICKETS.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(t);}
        for(int x=0;x<16;x++)for(int z=0;z<16;z++){h.setBlock(x,1,z,Blocks.STONE);for(int y=2;y<10;y++)h.setBlock(x,y,z,Blocks.AIR);}
        var m=own(h,h.spawn(EliteContent.ALCHEMIST.get(),new BlockPos(7,2,5)));m.setNoAi(true);m.setPersistenceRequired();return m;
    }
    private static Cow target(GameTestHelper h,int z){var c=own(h,h.spawn(EntityType.COW,new BlockPos(7,2,z)));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);c.setHealth(1000);return c;}
    @GameTest(template="bow_ritual_test",timeoutTicks=90,batch="alchemist")
    public static void helixHonorsSixteenTickTellAndActualBlockCollision(GameTestHelper h){
        var m=caster(h);var victim=target(h,13);for(int x=2;x<14;x++)for(int y=2;y<8;y++)h.setBlock(x,y,9,Blocks.STONE);
        // The tell begins in clear sight; a new real wall must intercept the flight, not cancel its cast.
        for(int x=2;x<14;x++)for(int y=2;y<8;y++)h.setBlock(x,y,9,Blocks.AIR);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(381,victim),"Registered native caster begins the double-helix tell"));
        h.runAfterDelay(18,()->{h.assertTrue(h.getLevel().getEntitiesOfClass(AlchemistOrb.class,m.getBoundingBox().inflate(20),o->o.ownedBy(m)).isEmpty(),"Full sixteen-tick tell has no harmful projectile");for(int x=2;x<14;x++)for(int y=2;y<8;y++)h.setBlock(x,y,9,Blocks.STONE);});
        h.runAfterDelay(23,()->h.assertTrue(h.getLevel().getEntitiesOfClass(AlchemistOrb.class,m.getBoundingBox().inflate(20),o->o.ownedBy(m)).size()==2,"Exactly two opposite-phase native entities were released"));
        h.runAfterDelay(65,()->{h.assertTrue(victim.getHealth()==1000,"Physical wall blocks both flight and the two-block burst behind it");h.assertTrue(h.getLevel().getEntitiesOfClass(AlchemistOrb.class,m.getBoundingBox().inflate(20),o->o.ownedBy(m)).isEmpty(),"Wall contacts terminate their finite flight");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=210,batch="alchemist")
    public static void seaLastsEightSecondsWithoutChangingFloorBlocks(GameTestHelper h){
        var m=caster(h);var victim=target(h,8);h.runAfterDelay(4,()->h.assertTrue(m.startSkill(382,victim),"Native fire sea starts"));
        h.runAfterDelay(26,()->h.assertTrue(victim.getHealth()==1000&&h.getLevel().getEntitiesOfClass(AlchemistZone.class,m.getBoundingBox().inflate(12),z->z.ownedBy(m)).isEmpty(),"Complete 1.2-second ground tell remains harmless"));
        h.runAfterDelay(55,()->{var pools=h.getLevel().getEntitiesOfClass(AlchemistZone.class,m.getBoundingBox().inflate(12),z->z.ownedBy(m));h.assertTrue(pools.size()==1&&pools.get(0).getRadius()==5&&victim.getHealth()<1000,"One real five-block zone deals native hostile damage");});
        h.runAfterDelay(190,()->{h.assertTrue(h.getLevel().getEntitiesOfClass(AlchemistZone.class,m.getBoundingBox().inflate(12),z->z.ownedBy(m)).isEmpty(),"Original zone expires after 160 ticks rather than refreshing");for(int x=2;x<13;x++)for(int z=0;z<11;z++)h.assertTrue(h.getBlockState(new BlockPos(x,1,z)).is(Blocks.STONE),"Fire sea never edits the authored floor");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=170,batch="alchemist")
    public static void goldPillsActuallyFlyAndMakeTwoFiniteMercuryZones(GameTestHelper h){
        var m=caster(h);var victim=target(h,11);h.runAfterDelay(4,()->h.assertTrue(m.startSkill(383,victim),"Native three-pill cast begins"));
        h.runAfterDelay(29,()->{var orbs=h.getLevel().getEntitiesOfClass(AlchemistOrb.class,m.getBoundingBox().inflate(20),o->o.ownedBy(m));h.assertTrue(m.shellActive()&&orbs.size()==2&&orbs.stream().allMatch(AlchemistOrb::pill),"One swallowed pill enables the shell and the other two exist as flying entities");h.assertTrue(h.getLevel().getEntitiesOfClass(AlchemistZone.class,m.getBoundingBox().inflate(20),z->z.ownedBy(m)).isEmpty(),"Mercury is not placed instantly at the target");});
        h.runAfterDelay(65,()->{var pools=h.getLevel().getEntitiesOfClass(AlchemistZone.class,m.getBoundingBox().inflate(20),z->z.ownedBy(m));h.assertTrue(pools.size()==2&&pools.stream().allMatch(z->z.getRadius()==2.5F),"Both physical landings create bounded distinct mercury zones");});
        h.runAfterDelay(76,()->{var pools=h.getLevel().getEntitiesOfClass(AlchemistZone.class,m.getBoundingBox().inflate(20),z->z.ownedBy(m));h.assertTrue(victim.hasEffect(net.minecraft.world.effect.MobEffects.POISON),"After its first native pulse the cloud applies poison to a hostile target");m.hurt(m.damageSources().genericKill(),10000);h.assertTrue(pools.stream().allMatch(Entity::isRemoved),"Owner death removes damaging zones immediately");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=250,batch="alchemist")
    public static void shellAndPerAttackerReflectionCooldownSurviveTheSameSave(GameTestHelper h){
        var m=caster(h);var victim=target(h,11);var live=new AtomicReference<>(m);var expires=new AtomicReference<Long>();
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(383,victim),"Shell cast begins"));
        h.runAfterDelay(30,()->{m.clearOwned();m.invulnerableTime=0;float before=victim.getHealth();m.hurt(m.damageSources().mobAttack(victim),4);h.assertTrue(victim.getHealth()<before,"Accepted damage reflects through native thorns");var tag=new CompoundTag();m.save(tag);expires.set(m.shellUntil());m.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);var restored=own(h,EliteContent.ALCHEMIST.get().create(h.getLevel()));restored.load(tag);restored.setNoAi(true);h.getLevel().addFreshEntity(restored);live.set(restored);h.assertTrue(restored.getUUID().equals(m.getUUID())&&restored.shellUntil()==expires.get(),"Same UUID preserves original absolute ten-second shell deadline");});
        h.runAfterDelay(41,()->{var restored=live.get();restored.invulnerableTime=0;victim.invulnerableTime=0;float before=victim.getHealth();restored.hurt(restored.damageSources().mobAttack(victim),4);h.assertTrue(victim.getHealth()==before,"Reload cannot bypass the saved per-attacker twenty-tick reflection cooldown");});
        h.runAfterDelay(56,()->{var restored=live.get();restored.invulnerableTime=0;float before=victim.getHealth();restored.hurt(restored.damageSources().mobAttack(victim),4);h.assertTrue(victim.getHealth()<before,"Original cooldown naturally permits a later accepted contact");});
        h.runAfterDelay(229,()->{h.assertTrue(!live.get().shellActive()&&h.getLevel().getGameTime()>=expires.get(),"Ten-second shell expires on the original clock");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=80,batch="alchemist")
    public static void acceptedHeavyContactInterruptsTheTellWithoutRestoringCooldown(GameTestHelper h){
        var m=caster(h);var victim=target(h,11);h.runAfterDelay(4,()->h.assertTrue(m.startSkill(381,victim),"Interruptible tell begins"));
        h.runAfterDelay(8,()->{float before=m.getHealth();h.assertTrue(m.hurt(m.damageSources().mobAttack(victim),20)&&before-m.getHealth()>=8,"Native armor pipeline accepts a heavy contact");h.assertTrue(m.phase()==AttackState.STUN&&m.skillId()==0&&!m.attack().ready(381,h.getLevel().getGameTime()),"Twenty-tick stun retains consumed skill cooldown");});
        h.runAfterDelay(40,()->{h.assertTrue(h.getLevel().getEntitiesOfClass(AlchemistOrb.class,m.getBoundingBox().inflate(20),o->o.ownedBy(m)).isEmpty(),"Cancelled release cannot create late projectiles");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=110,batch="alchemist")
    public static void nativeStructureSlotRetainsUnloadedOwnerAndConfirmedDeathCooldown(GameTestHelper h){
        var template=caster(h);var feet=template.blockPosition();template.discard();String key="alchemy-native@"+feet.asLong()+":alchemist";var world=h.getLevel();
        h.startSequence().thenWaitUntil(()->h.assertTrue(world.isPositionEntityTicking(feet),"Loaded structure floor is natively entity-ticking")).thenExecute(()->{
            var rule=world.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING);boolean old=rule.get();rule.set(true,world.getServer());try{
                h.assertTrue(EliteEncounters.spawnAlchemist(world,key,feet,feet.offset(0,0,8)),"Real loaded native structure spawner accepts the clear authored floor");var marker=BlueprintSpawnState.get(world).markers.get(key);var actor=(Alchemist)own(h,world.getEntity(marker.members.iterator().next()));h.assertTrue(!actor.isNoAi()&&marker.members.size()==1,"Ordinary actor owns exactly one SavedData slot");var tag=new CompoundTag();actor.save(tag);actor.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);h.assertTrue(!EliteEncounters.spawnAlchemist(world,key,feet,feet.offset(0,0,8)),"Unloaded UUID retains its slot");var restored=own(h,EliteContent.ALCHEMIST.get().create(world));restored.load(tag);world.addFreshEntity(restored);restored.hurt(restored.damageSources().genericKill(),10000);h.assertTrue(marker.members.isEmpty()&&marker.nextSpawn==world.getGameTime()+12000,"Confirmed death clears the owner and starts the original 12000-tick cooldown");h.assertTrue(!EliteEncounters.spawnAlchemist(world,key,feet,feet.offset(0,0,8)),"Another entrant cannot skip death cooldown");
            }finally{rule.set(old,world.getServer());}
        }).thenSucceed();
    }
}
