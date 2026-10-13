package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.BlueprintSpawnState;
import com.dynasty.blueprint.combat.AttackState;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.*;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.item.*;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

/** Native acceptance SOURCE prepared during the user's Java pause; NOT RUN. */
@GameTestHolder("dynasty_army") @PrefixGameTestTemplate(false)
public final class GoldenEagleGameTests {
    private static final TicketType<UUID> TYPE=TicketType.create("dynasty_eagle_qa",UUID::compareTo);
    private record Ticket(net.minecraft.world.level.ChunkPos chunk,UUID id){}
    private static final Map<ServerLevel,List<Ticket>> TICKETS=new HashMap<>();
    private static final Map<ServerLevel,List<Entity>> FIXTURES=new HashMap<>();
    private static <T extends Entity>T own(GameTestHelper h,T e){FIXTURES.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(e);return e;}
    @AfterBatch(batch="golden_eagle") public static void release(ServerLevel world){
        var es=FIXTURES.remove(world);if(es!=null)for(var e:es)if(!e.isRemoved())e.discard();
        var ts=TICKETS.remove(world);if(ts!=null)for(var t:ts)world.getChunkSource().removeRegionTicket(TYPE,t.chunk(),2,t.id(),true);
    }
    private static GoldenEagle caster(GameTestHelper h){
        var chunks=new HashSet<net.minecraft.world.level.ChunkPos>();for(int x:new int[]{0,15})for(int z:new int[]{0,15})chunks.add(new net.minecraft.world.level.ChunkPos(h.absolutePos(new BlockPos(x,2,z))));
        for(var chunk:chunks){var t=new Ticket(chunk,UUID.randomUUID());h.getLevel().getChunkSource().addRegionTicket(TYPE,chunk,2,t.id(),true);TICKETS.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(t);}
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=0;y<30;y++)h.setBlock(x,y,z,y<=1?Blocks.STONE:Blocks.AIR);
        var m=own(h,h.spawn(EliteContent.GOLDEN_EAGLE.get(),new BlockPos(7,6,4)));m.setNoAi(true);m.setPersistenceRequired();return m;
    }
    private static Cow target(GameTestHelper h,int x,int z){var c=own(h,h.spawn(EntityType.COW,new BlockPos(x,2,z)));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);c.setHealth(1000);c.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);return c;}
    private static List<EagleArrow> arrows(GameTestHelper h,GoldenEagle m){return h.getLevel().getEntitiesOfClass(EagleArrow.class,m.getBoundingBox().inflate(48),e->e.ownedBy(m));}
    @GameTest(template="bow_ritual_test",timeoutTicks=125,batch="golden_eagle")
    public static void thirtyTickTellOneActualLightArrowThenTwentyFourRainArrows(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,11);var count=new AtomicInteger();
        h.onEachTick(()->count.accumulateAndGet((int)arrows(h,m).stream().filter(e->e.kind()==EagleArrow.FALLING).count(),Math::max));
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(441,victim),"Rain starts"));
        h.runAfterDelay(33,()->h.assertTrue(arrows(h,m).isEmpty()&&victim.getHealth()==1000&&m.phase()==AttackState.WINDUP,"Full30tick harmless tell"));
        h.runAfterDelay(36,()->{var es=arrows(h,m);h.assertTrue(es.size()==1&&es.get(0).kind()==EagleArrow.MARKER&&es.get(0).getDeltaMovement().y>0,"One real upward light arrow leaves bow");for(var e:es)own(h,e);});
        h.runAfterDelay(75,()->h.assertTrue(count.get()==24,"Real light-arrow arrival splits into exactly24 finite falling arrows"));
        h.runAfterDelay(119,()->{h.assertTrue(arrows(h,m).isEmpty(),"Rain arrows expire; no persistent pile");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=110,batch="golden_eagle")
    public static void realRoofStopsLightArrowAndRain(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,11);var count=new AtomicInteger();h.onEachTick(()->count.accumulateAndGet(arrows(h,m).size(),Math::max));
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(441,victim),"Rain starts before roof"));
        h.runAfterDelay(28,()->{for(int x=4;x<=10;x++)for(int z=3;z<=13;z++)h.setBlock(x,8,z,Blocks.STONE);});
        h.runAfterDelay(85,()->{h.assertTrue(victim.getHealth()==1000&&count.get()<=1&&arrows(h,m).isEmpty(),"A native roof stops upward ray and no arrows teleport above it");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=85,batch="golden_eagle")
    public static void twelveTickWingTellThirtySixPhysicalFeathersThenExpiry(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,11);var count=new AtomicInteger();h.onEachTick(()->count.accumulateAndGet(arrows(h,m).size(),Math::max));
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(442,victim),"Fan starts"));
        h.runAfterDelay(15,()->h.assertTrue(arrows(h,m).isEmpty()&&m.phase()==AttackState.WINDUP,"Twelve tick fold precedes every feather"));
        h.runAfterDelay(22,()->{h.assertTrue(count.get()==36,"Exactly36 physical feathers, not36 damage callbacks");for(var e:arrows(h,m))own(h,e);});
        h.runAfterDelay(80,()->{h.assertTrue(arrows(h,m).isEmpty(),"Every hard feather expires by60ticks");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=80,batch="golden_eagle")
    public static void diveUsesRealCollisionAndCannotPassThroughLateWall(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,11);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(443,victim),"Dive starts"));
        h.runAfterDelay(16,()->{for(int x=5;x<=9;x++)for(int y=2;y<=10;y++)h.setBlock(x,y,8,Blocks.STONE);});
        h.runAfterDelay(37,()->{h.assertTrue(m.getZ()<h.absolutePos(new BlockPos(7,2,8)).getZ()&&m.phase()==AttackState.STUN&&victim.getHealth()==1000&&!m.isNoGravity(),"Late solid wall stops movement, cancels strike and returns gravity");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=150,batch="golden_eagle")
    public static void lateHeavyCounterGroundsForOneHundredTicksAndKeepsCooldown(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,11);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(443,victim),"Dive starts"));
        h.runAfterDelay(33,()->{h.assertTrue(m.hurt(m.damageSources().generic(),20),"Heavy hit at29tick accepted");h.assertTrue(m.phase()==AttackState.STUN&&!m.isNoGravity()&&!m.attack().ready(443,h.getLevel().getGameTime()),"Late counter grounds caster and retains spent cooldown");});
        h.runAfterDelay(130,()->h.assertTrue(m.phase()==AttackState.STUN&&m.onGround(),"Full five-second grounded counter window"));
        h.runAfterDelay(135,()->{h.assertTrue(m.phase()==AttackState.IDLE&&!m.attack().ready(443,h.getLevel().getGameTime()),"Stun ends while cooldown is still authoritative");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=35,batch="golden_eagle")
    public static void actualUpwardPlayerShieldBlocksFallingArrowAndSpendsDurability(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,11);var p=own(h,new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"eagle-qa")));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.setGameMode(GameType.SURVIVAL);p.moveTo(h.absolutePos(new BlockPos(11,2,11)),0,-80);p.setNoGravity(true);p.setItemInHand(InteractionHand.OFF_HAND,new ItemStack(Items.SHIELD));h.getLevel().addNewPlayer(p);h.onEachTick(p::doTick);
        h.runAfterDelay(4,()->{h.assertTrue(m.startSkill(441,victim),"Rain epoch starts");p.startUsingItem(InteractionHand.OFF_HAND);});
        h.runAfterDelay(12,()->{h.assertTrue(EagleArrow.overheadShield(p,p.getEyePosition().add(0,3,0)),"Actual held shield and upward native look qualify");h.assertTrue(m.launchArrow(EagleArrow.FALLING,p.position().add(0,4,0),new Vec3(0,-.8,0),Vec3.ZERO),"Real falling native arrow created");});
        h.runAfterDelay(22,()->{h.assertTrue(p.getHealth()==p.getMaxHealth()&&p.getItemInHand(InteractionHand.OFF_HAND).getDamageValue()==1,"Real arrow contact blocks damage and spends exactly one shield durability");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40,batch="golden_eagle")
    public static void loadedClockGapAndCorruptLandingCancelWithoutReplay(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,11);
        h.runAfterDelay(4,()->{h.assertTrue(m.startSkill(441,victim),"Rain starts");h.assertTrue(m.launchArrow(EagleArrow.MARKER,m.position().add(0,3,0),new Vec3(0,.2,0),m.position().add(0,6,0)),"Tracked marker exists");var tag=new CompoundTag();m.addAdditionalSaveData(tag);tag.putLong("LastCombatTick",h.getLevel().getGameTime()-20);m.readAdditionalSaveData(tag);});
        h.runAfterDelay(8,()->{h.assertTrue(m.skillId()==0&&arrows(h,m).isEmpty()&&!m.attack().ready(441,h.getLevel().getGameTime()),"Unloaded time gap cancels, retains cooldown and removes marker without burst");h.assertTrue(m.startSkill(443,victim),"Different skill can start after safe cancellation");var tag=new CompoundTag();m.addAdditionalSaveData(tag);tag.putFloat("LandingX",Float.NaN);m.readAdditionalSaveData(tag);h.assertTrue(m.skillId()==0,"Nonfinite saved landing rejected");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=115,batch="golden_eagle")
    public static void realStructureSlotDeathCooldownGravityAndNinetyTickRemoval(GameTestHelper h){
        var fixture=caster(h);fixture.discard();var ground=h.absolutePos(new BlockPos(7,2,4));var entrant=h.absolutePos(new BlockPos(7,2,14));String key="golden-eagle-qa/"+UUID.randomUUID();
        h.runAfterDelay(4,()->{h.assertTrue(EliteEncounters.spawnGoldenEagle(h.getLevel(),key,ground,entrant),"Actual encounter endpoint spawns over loaded clear ground");h.assertTrue(!EliteEncounters.spawnGoldenEagle(h.getLevel(),key,ground,entrant),"One structure UUID slot blocks duplicate");var mob=h.getLevel().getEntitiesOfClass(GoldenEagle.class,new AABB(ground).inflate(16),e->e.encounterSite().equals(key)).get(0);own(h,mob);mob.setNoAi(true);mob.hurt(mob.damageSources().genericKill(),10000);h.assertTrue(!mob.isNoGravity(),"Death restores actual fall gravity");});
        h.runAfterDelay(15,()->{var marker=BlueprintSpawnState.get(h.getLevel()).markers.get(key);h.assertTrue(marker!=null&&marker.members.isEmpty()&&marker.nextSpawn>=h.getLevel().getGameTime()+11980&&!EliteEncounters.spawnGoldenEagle(h.getLevel(),key,ground,entrant),"Confirmed death releases UUID, persists12000tick cooldown");});
        h.runAfterDelay(96,()->{h.assertTrue(h.getLevel().getEntitiesOfClass(GoldenEagle.class,new AABB(ground).inflate(16),e->e.encounterSite().equals(key)).isEmpty(),"Ninety tick death removes corpse once");BlueprintSpawnState.get(h.getLevel()).markers.remove(key);BlueprintSpawnState.get(h.getLevel()).setDirty();h.succeed();});
    }
}
