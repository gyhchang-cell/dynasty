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
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;
import java.util.*;

/** Native acceptance source only: user's Java pause remains in force. */
@GameTestHolder("dynasty_army") @PrefixGameTestTemplate(false)
public final class BronzeSuanniGameTests {
    private static final TicketType<UUID> TYPE=TicketType.create("dynasty_suanni_qa",UUID::compareTo);
    private record Ticket(ChunkPos chunk,UUID id){}
    private static final Map<ServerLevel,List<Ticket>> TICKETS=new HashMap<>();
    private static final Map<ServerLevel,List<Entity>> FIXTURES=new HashMap<>();
    private static final Map<ServerLevel,Boolean> GRIEF=new HashMap<>();
    private static final Map<ServerLevel,List<String>> MARKERS=new HashMap<>();
    private static <T extends Entity>T own(GameTestHelper h,T e){FIXTURES.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(e);return e;}
    @AfterBatch(batch="bronze_suanni") public static void release(ServerLevel world){
        var rule=GRIEF.remove(world);if(rule!=null)world.getGameRules().getRule(GameRules.RULE_MOBGRIEFING).set(rule,world.getServer());
        var es=FIXTURES.remove(world);if(es!=null)for(var e:es)if(!e.isRemoved())e.discard();
        var ts=TICKETS.remove(world);if(ts!=null)for(var t:ts)world.getChunkSource().removeRegionTicket(TYPE,t.chunk(),2,t.id(),true);
        var keys=MARKERS.remove(world);if(keys!=null){var state=BlueprintSpawnState.get(world);for(var key:keys)state.markers.remove(key);state.setDirty();}
    }
    @AfterBatch(batch="bronze_suanni_grief") public static void releaseGrief(ServerLevel world){release(world);}
    private static BronzeSuanni caster(GameTestHelper h){
        var chunks=new HashSet<ChunkPos>();for(int x:new int[]{-16,0,16,32})for(int z:new int[]{-16,0,16,32})chunks.add(new ChunkPos(h.absolutePos(new BlockPos(x,2,z))));
        for(var chunk:chunks){var t=new Ticket(chunk,UUID.randomUUID());h.getLevel().getChunkSource().addRegionTicket(TYPE,chunk,2,t.id(),true);TICKETS.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(t);}
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=0;y<9;y++)h.setBlock(x,y,z,y<=1?Blocks.STONE:Blocks.AIR);
        var m=own(h,h.spawn(EliteContent.BRONZE_SUANNI.get(),new BlockPos(7,2,3)));m.setNoAi(true);m.setPersistenceRequired();return m;
    }
    private static Cow target(GameTestHelper h,int x,int z){var c=own(h,h.spawn(EntityType.COW,new BlockPos(x,2,z)));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);c.setHealth(1000);c.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);return c;}
    private static void grief(GameTestHelper h,boolean value){var rule=h.getLevel().getGameRules().getRule(GameRules.RULE_MOBGRIEFING);GRIEF.putIfAbsent(h.getLevel(),rule.get());rule.set(value,h.getLevel().getServer());}
    @GameTest(template="bow_ritual_test",timeoutTicks=138,batch="bronze_suanni")
    public static void completeTwentyFourTickTellOneOutletSweepAndRecovery(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,8);var start=m.position();grief(h,false);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(451,victim),"Actual fire sweep starts"));
        h.runAfterDelay(27,()->h.assertTrue(m.phase()==AttackState.WINDUP&&m.effects().isEmpty()&&victim.getHealth()==1000,"All24tell ticks are harmless"));
        h.runAfterDelay(30,()->h.assertTrue(m.effects().size()==1&&m.effects().get(0).flame()&&m.effects().get(0).length()>7.9,"One real eight metre flame mesh, no duplicate damage entity"));
        h.runAfterDelay(64,()->h.assertTrue(victim.getHealth()<1000&&victim.isOnFire()&&m.position().distanceToSqr(start)<.01,"Planted sweep reaches frontal body and ignites it"));
        h.runAfterDelay(90,()->h.assertTrue(m.phase()==AttackState.RECOVERY&&m.effects().isEmpty()&&!m.attack().ready(451,h.getLevel().getGameTime()),"60active ticks expire the jet;44tick counter window preserves cooldown"));
        h.runAfterDelay(134,()->{h.assertTrue(m.phase()==AttackState.IDLE&&!m.noPhysics&&m.fireImmune(),"Native collision and fire immunity remain");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=95,batch="bronze_suanni")
    public static void wallAddedAfterLockTrimsActualJetAndProtectsVictim(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,10);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(451,victim),"Fire locks before obstacle"));
        h.runAfterDelay(8,()->{for(int x=0;x<16;x++)for(int y=2;y<7;y++)h.setBlock(x,y,7,Blocks.STONE);});
        h.runAfterDelay(58,()->h.assertTrue(m.flameLength(54)<2.5&&m.effects().size()==1&&m.effects().get(0).length()<2.5,"Actual tube terminates at new wall"));
        h.runAfterDelay(90,()->{h.assertTrue(victim.getHealth()==1000&&!victim.isOnFire()&&m.effects().isEmpty(),"No damage crosses wall; effect expires");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="bronze_suanni")
    public static void tenTickTellFiveProgressiveCracksAndFiniteLifetime(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,8);grief(h,false);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(452,victim),"Stomp starts"));
        h.runAfterDelay(13,()->h.assertTrue(m.effects().isEmpty(),"No fissure precedes10tick impact"));
        h.runAfterDelay(16,()->h.assertTrue(m.effects().size()==1,"First .5m cell alone appears"));
        h.runAfterDelay(32,()->{var cracks=m.effects();h.assertTrue(cracks.size()==5&&cracks.stream().noneMatch(SuanniEffect::flame),"Exactly five progressive cracks; not a simultaneous five metre damage ray");h.assertTrue(cracks.stream().allMatch(e->e.position().subtract(m.stompOrigin()).horizontalDistance()<=4.51),"Five metre line ends at4.5m cell plus its width");h.assertTrue(h.getBlockState(new BlockPos(8,1,4)).is(Blocks.STONE),"Griefing-disabled floor intact");});
        h.runAfterDelay(94,()->{h.assertTrue(m.effects().isEmpty(),"All ground flames expire within60ticks of birth");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60,batch="bronze_suanni")
    public static void lateWallStopsFissurePropagation(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,8);grief(h,false);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(452,victim),"Fissure locks direction"));
        h.runAfterDelay(8,()->{for(int x=0;x<16;x++)for(int y=2;y<6;y++)h.setBlock(x,y,6,Blocks.STONE);});
        h.runAfterDelay(34,()->{h.assertTrue(m.effects().size()==2&&m.effects().stream().allMatch(e->e.getZ()<h.absolutePos(new BlockPos(7,2,6)).getZ()),"Only first two cells survive, propagation stops at wall");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=35,batch="bronze_suanni_grief")
    public static void oneLayerWhitelistProtectsChestOreAndGriefRule(GameTestHelper h){
        var m=caster(h);var stone=h.absolutePos(new BlockPos(3,1,10));var chest=h.absolutePos(new BlockPos(4,1,10));var ore=h.absolutePos(new BlockPos(5,1,10));h.setBlock(4,1,10,Blocks.CHEST);h.setBlock(5,1,10,Blocks.DIAMOND_ORE);
        h.runAfterDelay(4,()->{grief(h,false);m.breakAllowedFloor(h.getLevel(),stone);h.assertTrue(!h.getLevel().isEmptyBlock(stone),"Native grief rule vetoes terrain mutation");grief(h,true);m.breakAllowedFloor(h.getLevel(),stone);m.breakAllowedFloor(h.getLevel(),chest);m.breakAllowedFloor(h.getLevel(),ore);
            h.assertTrue(h.getLevel().isEmptyBlock(stone)&&h.getLevel().getBlockState(stone.below()).is(Blocks.STONE),"Exactly selected layer breaks, no column excavation");h.assertTrue(h.getLevel().getBlockState(chest).is(Blocks.CHEST)&&h.getLevel().getBlockState(ore).is(Blocks.DIAMOND_ORE),"Containers and ore are excluded");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40,batch="bronze_suanni")
    public static void fourteenTickRoarBreaksRealShieldRespectsResistanceAndWalls(GameTestHelper h){
        var m=caster(h);var resistant=target(h,7,6);var exposed=target(h,9,5);exposed.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(0);var behind=target(h,4,3);
        var p=own(h,new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"suanni-qa")));p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.setGameMode(GameType.SURVIVAL);p.moveTo(h.absolutePos(new BlockPos(7,2,6)),180,0);p.setNoGravity(true);p.setItemInHand(InteractionHand.OFF_HAND,new ItemStack(Items.SHIELD));h.getLevel().addNewPlayer(p);h.onEachTick(p::doTick);
        h.runAfterDelay(4,()->{p.startUsingItem(InteractionHand.OFF_HAND);h.assertTrue(m.startSkill(453,resistant),"Roar locks");for(int z=0;z<8;z++)for(int y=2;y<6;y++)h.setBlock(5,y,z,Blocks.STONE);});
        h.runAfterDelay(17,()->h.assertTrue(p.isBlocking()&&exposed.getHealth()==1000,"All14tell ticks preserve blocking and health"));
        h.runAfterDelay(20,()->{h.assertTrue(!p.isBlocking()&&p.getCooldowns().isOnCooldown(Items.SHIELD),"Actual shield disabled60ticks");h.assertTrue(resistant.getDeltaMovement().horizontalDistance()<.001&&exposed.getDeltaMovement().horizontalDistance()>.05&&behind.getDeltaMovement().horizontalDistance()<.001,"Native resistance protects resistant body; wall blocks; exposed body is knocked back");h.assertTrue(exposed.getHealth()==1000,"Roar is displacement, not extra unlisted damage");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=80,batch="bronze_suanni")
    public static void heavyWindupInterruptCooldownAndSavedClockGapNeverReplay(GameTestHelper h){
        var m=caster(h);var victim=target(h,7,8);
        h.runAfterDelay(4,()->h.assertTrue(m.startSkill(451,victim),"Windup begins"));
        h.runAfterDelay(8,()->{m.hurt(m.damageSources().magic(),24);h.assertTrue(m.phase()==AttackState.STUN&&m.effects().isEmpty()&&!m.attack().ready(451,h.getLevel().getGameTime()),"Accepted heavy hit interrupts with retained cooldown");});
        h.runAfterDelay(44,()->{var n=own(h,h.spawn(EliteContent.BRONZE_SUANNI.get(),new BlockPos(7,2,3)));n.setNoAi(true);m.discard();h.assertTrue(n.startSkill(452,victim),"Fresh saved attack starts");var tag=n.saveWithoutId(new CompoundTag());tag.putLong("LastCombatTick",h.getLevel().getGameTime()-20);n.load(tag);});
        h.runAfterDelay(72,()->{h.assertTrue(victim.getHealth()==1000&&h.getLevel().getEntitiesOfClass(SuanniEffect.class,m.getBoundingBox().inflate(16)).isEmpty(),"Time gap cancels rather than replaying missed cracks");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=115,batch="bronze_suanni")
    public static void singleSavedUuidConfirmedDeathPermanentlyClearsTombSlot(GameTestHelper h){
        var fixture=caster(h);fixture.discard();var feet=h.absolutePos(new BlockPos(7,2,7));var entrant=h.absolutePos(new BlockPos(7,2,0));String key="qa/suanni/"+UUID.randomUUID();MARKERS.computeIfAbsent(h.getLevel(),k->new ArrayList<>()).add(key);
        h.runAfterDelay(4,()->{h.assertTrue(EliteEncounters.spawnBronzeSuanni(h.getLevel(),key,feet,entrant),"Real encounter helper spawns in clear solid vault");var marker=BlueprintSpawnState.get(h.getLevel()).markers.get(key);var actor=(BronzeSuanni)h.getLevel().getEntity(marker.members.iterator().next());own(h,actor);actor.setNoAi(true);actor.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);h.assertTrue(!marker.members.isEmpty()&&!marker.cleared&&!EliteEncounters.spawnBronzeSuanni(h.getLevel(),key,feet,entrant),"Unload retains UUID, does not clear tomb");BlueprintSpawnState.get(h.getLevel()).markers.remove(key);h.assertTrue(EliteEncounters.spawnBronzeSuanni(h.getLevel(),key,feet,entrant),"Fresh test slot spawns");var next=(BronzeSuanni)h.getLevel().getEntity(BlueprintSpawnState.get(h.getLevel()).markers.get(key).members.iterator().next());own(h,next);next.setNoAi(true);next.hurt(next.damageSources().genericKill(),10000);});
        h.runAfterDelay(8,()->{var marker=BlueprintSpawnState.get(h.getLevel()).markers.get(key);h.assertTrue(marker.cleared&&marker.members.isEmpty()&&!EliteEncounters.spawnBronzeSuanni(h.getLevel(),key,feet,entrant),"Confirmed death persists one-shot clear without respawn");});
        h.runAfterDelay(98,()->{h.assertTrue(h.getLevel().getEntitiesOfClass(BronzeSuanni.class,new AABB(feet).inflate(16),e->e.encounterSite().equals(key)).isEmpty(),"90tick broken furnace corpse removes once");h.succeed();});
    }
}
