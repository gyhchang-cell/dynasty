package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.*;
import com.dynasty.blueprint.combat.AttackState;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.*;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicReference;

/** Source prepared during the user's Java pause; actual native damage, sweep, use and save assertions. */
@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class InkAssassinGameTests {
    private static final TicketType<UUID> TICKET=TicketType.create("dynasty_ink_qa",UUID::compareTo);
    private record Ticket(net.minecraft.world.level.ChunkPos chunk,UUID id){}
    private static final Map<ServerLevel,List<Ticket>> TICKETS=new HashMap<>();
    private static final Map<ServerLevel,List<Entity>> FIXTURES=new HashMap<>();
    private static <T extends Entity>T own(GameTestHelper h,T e){FIXTURES.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(e);return e;}
    @AfterBatch(batch="ink_assassin") public static void release(ServerLevel world){
        var fixtures=FIXTURES.remove(world);if(fixtures!=null)for(var e:fixtures){if(e instanceof InkAssassin caster)caster.clearOwned();if(!e.isRemoved())e.discard();}
        var tickets=TICKETS.remove(world);if(tickets!=null)for(var t:tickets)world.getChunkSource().removeRegionTicket(TICKET,t.chunk(),2,t.id(),true);
    }
    private static InkAssassin caster(GameTestHelper h){
        var chunks=new HashSet<net.minecraft.world.level.ChunkPos>();for(int x:new int[]{0,15})for(int z:new int[]{0,15})chunks.add(new net.minecraft.world.level.ChunkPos(h.absolutePos(new BlockPos(x,2,z))));
        for(var chunk:chunks){var t=new Ticket(chunk,UUID.randomUUID());h.getLevel().getChunkSource().addRegionTicket(TICKET,chunk,2,t.id(),true);TICKETS.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(t);}
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=0;y<10;y++)h.setBlock(x,y,z,y<=1?Blocks.STONE:Blocks.AIR);
        var m=own(h,h.spawn(EliteContent.INK_ASSASSIN.get(),new BlockPos(7,2,3)));m.setNoAi(true);m.setPersistenceRequired();return m;
    }
    private static Cow target(GameTestHelper h,int x,int z){var c=own(h,h.spawn(EntityType.COW,new BlockPos(x,2,z)));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);c.setHealth(1000);c.setYRot(0);return c;}
    @GameTest(template="bow_ritual_test",timeoutTicks=110,batch="ink_assassin")
    public static void finiteConcealmentKeepsColliderAndBackContactReallyTriplesDamage(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,8);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(411,victim),"Clear stealth cast begins"));
        h.runAfterDelay(30,()->h.assertTrue(m.concealed()&&m.isInvisible()&&!m.noPhysics&&!m.isNoGravity()&&m.getBbWidth()==1.4F&&victim.getHealth()==1000,"Hidden actor retains ordinary registered collider and does not deal early damage"));
        h.runAfterDelay(85,()->{h.assertTrue(!m.concealed()&&!m.isInvisible()&&victim.getHealth()==982,"One actual unarmored contact from the rear deals exactly three times base six damage");h.assertTrue(Math.abs(m.getZ()-(victim.getZ()-1))<.02,"Exactly one legal one-block rear emergence");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=110,batch="ink_assassin")
    public static void turningAfterTheLockedTrailPreventsTheBackCritical(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,8);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(411,victim),"Stealth begins"));
        h.runAfterDelay(77,()->victim.setYRot(180));
        h.runAfterDelay(85,()->{h.assertTrue(victim.getHealth()==994&&!m.isInvisible(),"Turning toward the locked rear point leaves only ordinary six damage, rather than a guaranteed critical");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=110,batch="ink_assassin")
    public static void aLateWallCancelsRearEmergenceWithoutRefundingCooldown(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,8);var start=m.position();
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(411,victim),"Clear route begins"));
        h.runAfterDelay(77,()->{for(int x=0;x<16;x++)for(int y=2;y<7;y++)h.setBlock(x,y,6,Blocks.STONE);});
        h.runAfterDelay(86,()->{h.assertTrue(m.position().distanceToSqr(start)<.01&&victim.getHealth()==1000&&!m.isInvisible()&&m.phase()==AttackState.STUN,"New solid wall blocks the native blink and releases concealment into a counter window");h.assertTrue(!m.attack().ready(411,h.getLevel().getGameTime()),"Obstacle cancellation preserves consumed cooldown");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="ink_assassin")
    public static void fourRealDiagonalPassesDealFourContactsAndAnchorsExpire(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,8);
        h.runAfterDelay(4,()->{h.assertTrue(m.startSkill(412,victim),"Native four-anchor field begins");h.assertTrue(h.getLevel().getEntitiesOfClass(InkSpike.class,m.getBoundingBox().inflate(32),s->s.ownedBy(m)).size()==4,"Exactly four living breakable anchors");});
        h.runAfterDelay(13,()->h.assertTrue(victim.getHealth()==1000&&m.phase()==AttackState.WINDUP,"Half-second field tell is harmless"));
        h.runAfterDelay(61,()->{h.assertTrue(victim.getHealth()==976,"Four separated native center contacts each deal six actual damage");h.assertTrue(m.phase()==AttackState.RECOVERY&&h.getLevel().getEntitiesOfClass(InkSpike.class,m.getBoundingBox().inflate(32),s->s.ownedBy(m)).isEmpty(),"All anchors expire when traversal ends");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60,batch="ink_assassin")
    public static void nativePlayerSweepAgainstNearbyBaitActuallyBreaksAnAnchor(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,8);var bait=target(h,5,7);
        var p=own(h,new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"ink-sweep")));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.setGameMode(GameType.SURVIVAL);p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(Items.IRON_SWORD));h.getLevel().addNewPlayer(p);h.onEachTick(()->{if(!p.isRemoved())p.doTick();});
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(412,victim),"Breakable field begins"));
        h.runAfterDelay(8,()->{p.moveTo(bait.getX(),bait.getY(),bait.getZ()+1,180,0);p.setOnGround(true);p.resetAttackStrengthTicker();for(int i=0;i<22;i++)p.doTick();p.attack(bait);h.assertTrue(bait.getHealth()<1000&&m.phase()==AttackState.STUN&&m.skillId()==0,"Native sword sweep on a nearby ordinary living target reaches the anchor and cancels the field");h.assertTrue(!m.attack().ready(412,h.getLevel().getGameTime())&&h.getLevel().getEntitiesOfClass(InkSpike.class,m.getBoundingBox().inflate(32),s->s.ownedBy(m)).isEmpty(),"Counter removes remaining anchors and retains original cooldown");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=165,batch="ink_assassin")
    public static void threeDelayedCloudsAreHarmlessForOneSecondAndUsableBambooDispersesThem(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,8);
        var p=own(h,new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"ink-breath")));
        var at=h.absolutePos(new BlockPos(7,2,0));p.moveTo(at.getX()+.5,at.getY(),at.getZ()+.5,0,10);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(413,victim),"Backward roll and ink throw begin"));
        h.runAfterDelay(15,()->{var clouds=h.getLevel().getEntitiesOfClass(InkCloud.class,m.getBoundingBox().inflate(32),c->c.ownedBy(m));h.assertTrue(clouds.size()==3&&clouds.stream().allMatch(InkCloud::isWaiting),"Exactly three harmless pellets, not immediate damaging clouds");victim.teleportTo(victim.getX(),victim.getY(),h.absolutePos(new BlockPos(7,2,6)).getZ());});
        h.runAfterDelay(30,()->h.assertTrue(!victim.hasEffect(MobEffects.BLINDNESS),"Full twenty-tick pellet fuse has not yet elapsed"));
        h.runAfterDelay(36,()->{h.assertTrue(victim.hasEffect(MobEffects.BLINDNESS)&&victim.getEffect(MobEffects.BLINDNESS).getDuration()<=100,"Native cloud grants only five seconds of vanilla blindness");var stack=new ItemStack(BlueprintSalvage.HOLLOW_INK_BAMBOO.get(),2);h.assertTrue(stack.getUseDuration()==20,"Actual bamboo item requires a full second of use");stack.getItem().finishUsingItem(stack,h.getLevel(),p);h.assertTrue(stack.getCount()==1&&p.getCooldowns().isOnCooldown(stack.getItem()),"Actual use consumes one salvage and starts a finite cooldown");h.assertTrue(h.getLevel().getEntitiesOfClass(InkCloud.class,m.getBoundingBox().inflate(32),c->c.ownedBy(m)).isEmpty(),"Visible six-block breath cone removes all three clouds");});
        h.runAfterDelay(145,()->{h.assertTrue(!victim.hasEffect(MobEffects.BLINDNESS),"Dispersed clouds never refresh a permanent blindness");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=105,batch="ink_assassin")
    public static void unloadedUuidRetainsSlotAndMissedStealthNeverReplays(GameTestHelper h){
        var fixture=caster(h);var feet=fixture.blockPosition();fixture.discard();var victim=target(h,7,11);var world=h.getLevel();var live=new AtomicReference<InkAssassin>();String key="ink-native@"+feet.asLong()+":ink_assassin";
        h.startSequence().thenWaitUntil(()->h.assertTrue(world.isPositionEntityTicking(feet),"Inner-vault fixture is ticking")).thenExecute(()->{
            var rule=world.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING);boolean old=rule.get();rule.set(true,world.getServer());try{h.assertTrue(EliteEncounters.spawnInkAssassin(world,key,feet,feet.offset(0,0,8)),"One real structure actor spawns");var marker=BlueprintSpawnState.get(world).markers.get(key);var actor=(InkAssassin)own(h,world.getEntity(marker.members.iterator().next()));actor.setNoAi(true);live.set(actor);h.assertTrue(actor.startSkill(411,victim),"Native stealth clock starts before saving");}finally{rule.set(old,world.getServer());}
        }).thenIdle(8).thenExecute(()->{var actor=live.get();var tag=new CompoundTag();actor.save(tag);actor.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);h.assertTrue(BlueprintSpawnState.get(world).markers.get(key).members.contains(actor.getUUID()),"Unload retains exact saved member UUID");h.runAfterDelay(5,()->{var restored=own(h,EliteContent.INK_ASSASSIN.get().create(world));restored.load(tag);world.addFreshEntity(restored);live.set(restored);});}).thenIdle(12).thenExecute(()->{
            var actor=live.get();h.assertTrue(actor.skillId()==0&&!actor.isInvisible()&&!actor.attack().ready(411,world.getGameTime())&&victim.getHealth()==1000,"Missed native interval cancels stealth, restores visibility and keeps cooldown without delayed critical");actor.hurt(actor.damageSources().genericKill(),10000);var marker=BlueprintSpawnState.get(world).markers.get(key);h.assertTrue(marker.members.isEmpty()&&marker.nextSpawn==world.getGameTime()+12000,"Confirmed death begins saved encounter cooldown");
        }).thenSucceed();
    }
}
