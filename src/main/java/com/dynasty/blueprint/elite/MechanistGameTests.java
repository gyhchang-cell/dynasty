package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.BlueprintSpawnState;
import com.dynasty.blueprint.combat.AttackState;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class MechanistGameTests {
    private static final net.minecraft.server.level.TicketType<java.util.UUID> SHIELD_TICKET=net.minecraft.server.level.TicketType.create("dynasty_wheel_shield_qa",java.util.UUID::compareTo);
    private static final java.util.Map<net.minecraft.server.level.ServerLevel,java.util.List<Runnable>> SHIELD_CLEANUP=new java.util.HashMap<>();
    @AfterBatch(batch="mechanist_shield") public static void releaseShieldFixture(net.minecraft.server.level.ServerLevel level){
        var cleanup=SHIELD_CLEANUP.remove(level);if(cleanup!=null)for(var action:cleanup)action.run();
    }
    private static Mechanist mob(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++){
            h.setBlock(x,1,z,Blocks.STONE);for(int y=2;y<=9;y++)h.setBlock(x,y,z,Blocks.AIR);
            if(x==0||x==15||z==0||z==15)for(int y=2;y<=7;y++)h.setBlock(x,y,z,Blocks.STONE);
        }
        var m=h.spawn(EliteContent.MECHANIST.get(),new BlockPos(7,2,5));m.setNoAi(true);m.setNoGravity(true);return m;
    }
    private static Cow cow(GameTestHelper h,int x,int z){var c=h.spawn(EntityType.COW,new BlockPos(x,2,z));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);c.setHealth(1000);c.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);return c;}
    @GameTest(template="bow_ritual_test",timeoutTicks=80,batch="mechanist")
    public static void netHasFourteenTickTellPillarEscapeAndFiniteNinetyPercentSlow(GameTestHelper h){
        var m=mob(h);var front=cow(h,7,8);var side=cow(h,11,5);var behindPillar=cow(h,5,8);
        h.setBlock(6,2,7,Blocks.STONE);h.setBlock(6,3,7,Blocks.STONE);h.setBlock(6,4,7,Blocks.STONE);
        double speed=front.getAttributeValue(Attributes.MOVEMENT_SPEED);h.assertTrue(m.startSkill(321,front),"Real server net starts");
        h.runAfterDelay(12,()->h.assertTrue(!front.hasEffect(EliteContent.THREAD_NET.get()),"No effect before the 0.7-second tell"));
        h.runAfterDelay(17,()->{
            h.assertTrue(front.hasEffect(EliteContent.THREAD_NET.get())&&Math.abs(front.getAttributeValue(Attributes.MOVEMENT_SPEED)-speed*.1)<.00001,"Exactly ninety-percent slow");
            h.assertTrue(!side.hasEffect(EliteContent.THREAD_NET.get())&&!behindPillar.hasEffect(EliteContent.THREAD_NET.get()),"Side step and real solid pillar escape the sector");
            h.assertTrue(!MechanistNet.allowsDisplacement(front),"Displacement eligibility is rejected by the actual effect");
        });
        h.runAfterDelay(70,()->{h.assertTrue(!front.hasEffect(EliteContent.THREAD_NET.get())&&MechanistNet.allowsDisplacement(front)&&Math.abs(front.getAttributeValue(Attributes.MOVEMENT_SPEED)-speed)<.00001,"Effect and attribute fully restore");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=75,batch="mechanist")
    public static void wheelsHaveTwoLockedArcsCentralGapAndBoundedLifetime(GameTestHelper h){
        var m=mob(h);var middle=cow(h,7,12);h.assertTrue(m.startSkill(322,middle),"Actual wheel cast starts");
        h.runAfterDelay(8,()->h.assertTrue(h.getLevel().getEntitiesOfClass(MechanistWheel.class,m.getBoundingBox().inflate(16)).isEmpty(),"Full half-second box tell"));
        h.runAfterDelay(13,()->{
            var wheels=h.getLevel().getEntitiesOfClass(MechanistWheel.class,m.getBoundingBox().inflate(16),w->w.ownedBy(m));
            h.assertTrue(wheels.size()==2,"Exactly two logical wheels");
            h.assertTrue(wheels.get(0).getX()!=wheels.get(1).getX(),"Opposite physical arcs leave a central gap");
        });
        h.runAfterDelay(55,()->{h.assertTrue(middle.getHealth()==1000,"Standing in the two arcs' centre avoids damage");h.assertTrue(h.getLevel().getEntitiesOfClass(MechanistWheel.class,m.getBoundingBox().inflate(16)).isEmpty(),"Absolute forty-tick wheel lifetime");h.succeed();});
    }
    public static final class WheelBlockProbe {
        final java.util.UUID player;float original=-1,blocked=-1,damage;
        WheelBlockProbe(net.minecraft.server.level.ServerPlayer player){this.player=player.getUUID();}
        @net.minecraftforge.eventbus.api.SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.LOWEST)
        public void block(net.minecraftforge.event.entity.living.ShieldBlockEvent event){
            if(event.getEntity().getUUID().equals(player)&&event.getDamageSource().getDirectEntity() instanceof MechanistWheel){original=event.getOriginalBlockedDamage();blocked=event.getBlockedDamage();}
        }
        @net.minecraftforge.eventbus.api.SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.LOWEST)
        public void damage(net.minecraftforge.event.entity.living.LivingDamageEvent event){
            if(event.getEntity().getUUID().equals(player)&&event.getSource().getDirectEntity() instanceof MechanistWheel)damage+=event.getAmount();
        }
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=800,batch="mechanist_shield")
    public static void raisedShieldDeflectsARealCopperWheel(GameTestHelper h){
        var level=h.getLevel();var cleanup=SHIELD_CLEANUP.computeIfAbsent(level,k->new java.util.ArrayList<>());
        // A survival player must not be reachable by hostile actors from earlier test batches.
        var origin=new BlockPos(22000,130,22000);
        for(int x:new int[]{0,15})for(int z:new int[]{0,15}){
            var chunk=new net.minecraft.world.level.ChunkPos(origin.offset(x,0,z));level.getChunk(chunk.x,chunk.z);var id=java.util.UUID.randomUUID();
            level.getChunkSource().addRegionTicket(SHIELD_TICKET,chunk,2,id,true);cleanup.add(()->level.getChunkSource().removeRegionTicket(SHIELD_TICKET,chunk,2,id,true));
        }
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=-1;y<8;y++)level.setBlockAndUpdate(origin.offset(x,y,z),(y==-1?Blocks.STONE:Blocks.AIR).defaultBlockState());
        var m=EliteContent.MECHANIST.get().create(level);m.setNoAi(true);m.setNoGravity(true);m.setPersistenceRequired();m.moveTo(origin.getX()+7.5,origin.getY(),origin.getZ()+5.5);level.addFreshEntity(m);
        var target=EntityType.COW.create(level);target.setNoAi(true);target.setNoGravity(true);target.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);target.setHealth(1000);target.moveTo(origin.getX()+7.5,origin.getY(),origin.getZ()+12.5);level.addFreshEntity(target);
        cleanup.add(()->{for(var wheel:level.getEntitiesOfClass(MechanistWheel.class,m.getBoundingBox().inflate(24),w->w.ownedBy(m)))wheel.discard();m.discard();target.discard();});
        var player=new net.minecraft.server.level.ServerPlayer(h.getLevel().getServer(),h.getLevel(),new com.mojang.authlib.GameProfile(java.util.UUID.randomUUID(),"mechanist-shield"));
        player.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),player);
        player.setGameMode(net.minecraft.world.level.GameType.SURVIVAL);player.moveTo(m.position().add(2.45,0,6));player.setYRot(180);h.getLevel().addNewPlayer(player);
        h.onEachTick(()->{if(!player.isRemoved())player.doTick();});
        player.setItemInHand(net.minecraft.world.InteractionHand.OFF_HAND,new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.SHIELD));player.startUsingItem(net.minecraft.world.InteractionHand.OFF_HAND);
        var probe=new WheelBlockProbe(player);net.minecraftforge.common.MinecraftForge.EVENT_BUS.register(probe);
        cleanup.add(()->{net.minecraftforge.common.MinecraftForge.EVENT_BUS.unregister(probe);player.discard();});
        h.startSequence().thenWaitUntil(()->h.assertTrue(level.isPositionEntityTicking(m.blockPosition())&&m.tickCount>=2,"Private native entity section is actually ticking"))
        .thenExecute(()->com.dynasty.Dynasty.LOGGER.info("WHEEL_SHIELD_NATIVE_READY worldTick={} actorTicks={} playerHealth={}",level.getGameTime(),m.tickCount,player.getHealth()))
        .thenIdle(68).thenExecute(()->{h.assertTrue(player.isAlive()&&player.isBlocking(),"Actual survival shield raise completes after native spawn immunity expires");h.assertTrue(m.startSkill(322,target),"Actual wheel release targets the locked forward point");})
        .thenIdle(30).thenExecute(()->{
            h.assertTrue(probe.original>0&&probe.blocked==probe.original&&probe.damage==0&&player.getOffhandItem().getDamageValue()>0,
                "Actual wheel damage is fully blocked through vanilla shield durability: original="+probe.original+" blocked="+probe.blocked+" directWheelDamage="+probe.damage+" hp="+player.getHealth()+" shieldDamage="+player.getOffhandItem().getDamageValue());
        }).thenSucceed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30,batch="mechanist")
    public static void solidWallAndUnloadedTimeGapCancelPhysicalWheel(GameTestHelper h){
        var m=mob(h);var target=cow(h,7,12);var wheel=EliteContent.WHEEL.get().create(h.getLevel());wheel.launch(m,new Vec3(0,0,1),1);h.getLevel().addFreshEntity(wheel);
        var original=new CompoundTag();wheel.save(original);
        for(int x=3;x<=11;x++)for(int y=2;y<=4;y++)h.setBlock(x,y,8,Blocks.STONE);
        h.runAfterDelay(10,()->{
            h.assertTrue(wheel.isRemoved()&&target.getHealth()==1000,"Real block collision cancels the arc before anything behind the wall is damaged");
            for(int x=3;x<=11;x++)for(int y=2;y<=4;y++)h.setBlock(x,y,8,Blocks.AIR);
            var saved=original.copy();saved.putLong("LastTick",h.getLevel().getGameTime()-8);saved.putLong("Born",h.getLevel().getGameTime()-10);
            var restored=EliteContent.WHEEL.get().create(h.getLevel());restored.load(saved);h.getLevel().addFreshEntity(restored);
            h.runAfterDelay(3,()->{h.assertTrue(restored.isRemoved()&&target.getHealth()==1000,"An unloaded time gap cannot sweep a delayed damaging segment");h.succeed();});
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=75,batch="mechanist")
    public static void projectileCheckpointKeepsConsumedHitsAndExpiredWheelsCannotReappear(GameTestHelper h){
        var m=mob(h);var target=cow(h,9,12);h.assertTrue(m.startSkill(322,target),"Wheel starts");
        h.runAfterDelay(28,()->{
            var wheels=h.getLevel().getEntitiesOfClass(MechanistWheel.class,m.getBoundingBox().inflate(16),w->w.ownedBy(m));h.assertTrue(!wheels.isEmpty(),"A real outgoing wheel exists");
            var w=wheels.get(0);var tag=new CompoundTag();w.save(tag);var id=w.getUUID();w.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            var restored=EliteContent.WHEEL.get().create(h.getLevel());restored.load(tag);h.getLevel().addFreshEntity(restored);
            h.assertTrue(restored.getUUID().equals(id)&&restored.born()==tag.getLong("Born"),"Native owner, identity and absolute arc time survive");
            h.runAtTickTime(65,()->{
                var expired=EliteContent.WHEEL.get().create(h.getLevel());expired.load(tag);h.getLevel().addFreshEntity(expired);
                h.runAtTickTime(68,()->{h.assertTrue(expired.isRemoved(),"Restoring old NBT cannot replay a wheel trajectory");h.succeed();});
            });
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=45,batch="mechanist")
    public static void shootingAnAirborneSpiderCountersItsCasterWithoutTerrainDamage(GameTestHelper h){
        var m=mob(h);var shooter=cow(h,7,10);var wall=new BlockPos(8,2,5);h.setBlock(wall,Blocks.STONE);
        var s=h.spawn(EliteContent.SPIDER.get(),new BlockPos(7,3,5));s.launch(m,shooter.getUUID(),0);s.setNoAi(true);s.setNoGravity(true);s.setPos(m.position().add(0,.6,0));
        float before=m.getHealth();s.hurt(s.damageSources().mobProjectile(shooter,shooter),20);
        h.assertTrue(s.isRemoved()&&m.getHealth()<before,"Early airborne kill bursts once and can damage its own caster");
        h.assertTrue(h.getLevel().getBlockState(h.absolutePos(wall)).is(Blocks.STONE),"Blast never edits terrain");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=170,batch="mechanist")
    public static void summonsAreCappedAndOwnerDeathOrAbsoluteExpiryCleansThem(GameTestHelper h){
        var m=mob(h);var target=cow(h,7,12);h.assertTrue(m.startSkill(323,target),"Real spider cast starts");
        h.runAfterDelay(23,()->{
            var summons=h.getLevel().getEntitiesOfClass(ClockworkSpider.class,m.getBoundingBox().inflate(24),s->s.ownedBy(m));h.assertTrue(summons.size()==4,"One cast creates four logical eight-legged summons");
            for(var s:summons){s.setNoGravity(true);s.setPos(m.position().add(0,5,0));}
        });
        h.runAfterDelay(145,()->{
            h.assertTrue(h.getLevel().getEntitiesOfClass(ClockworkSpider.class,m.getBoundingBox().inflate(24),s->s.ownedBy(m)).isEmpty(),"Absolute six-second lifetime cannot be extended by target or flight");
            var s=h.spawn(EliteContent.SPIDER.get(),new BlockPos(7,3,5));s.launch(m,target.getUUID(),0);m.hurt(m.damageSources().genericKill(),10000);
            h.assertTrue(s.isRemoved(),"Caster death cleans the actual surviving summon");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=65,batch="mechanist")
    public static void rearBackpackHitInterruptsTellAndConsumedCastDoesNotReplayOnLoad(GameTestHelper h){
        var m=mob(h);var front=cow(h,7,10);var back=cow(h,7,3);h.assertTrue(m.startSkill(323,front),"Box windup starts");
        m.hurt(m.damageSources().mobAttack(back),20);h.assertTrue(m.phase()==AttackState.STUN,"Accepted rear damage breaks the windup");
        h.runAfterDelay(25,()->h.assertTrue(h.getLevel().getEntitiesOfClass(ClockworkSpider.class,m.getBoundingBox().inflate(16)).isEmpty(),"Interrupted cast has no deferred summons"));
        h.runAfterDelay(35,()->{
            h.assertTrue(m.startSkill(322,front),"Independent wheel skill remains available after recovery");
            h.runAtTickTime(50,()->{
                var t=new CompoundTag();m.save(t);int count=h.getLevel().getEntitiesOfClass(MechanistWheel.class,m.getBoundingBox().inflate(16)).size();m.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
                var loaded=EliteContent.MECHANIST.get().create(h.getLevel());loaded.load(t);h.getLevel().addFreshEntity(loaded);
                h.runAtTickTime(55,()->{h.assertTrue(h.getLevel().getEntitiesOfClass(MechanistWheel.class,loaded.getBoundingBox().inflate(16)).size()<=count,"Consumed wheel release is not replayed by entity NBT load");h.succeed();});
            });
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=25,batch="mechanist")
    public static void permanentDeathReleasesStructureSlotButUnloadAndSecondEntrantDoNot(GameTestHelper h){
        var m=mob(h);m.discard();var level=h.getLevel();var feet=new BlockPos(22000,130,22000);level.getChunkAt(feet);
        for(int x=-2;x<=2;x++)for(int z=-2;z<=2;z++){level.setBlockAndUpdate(feet.offset(x,-1,z),Blocks.STONE.defaultBlockState());for(int y=0;y<4;y++)level.setBlockAndUpdate(feet.offset(x,y,z),Blocks.AIR.defaultBlockState());}
        var entrant=feet.offset(0,0,7);
        var rule=level.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING);boolean old=rule.get();rule.set(true,level.getServer());String key="mechanist-test@"+feet.asLong();
        try{
            h.assertTrue(EliteEncounters.spawnMechanist(level,key,feet,entrant),"Real registered structure encounter creates one elite");var marker=BlueprintSpawnState.get(level).markers.get(key);var id=marker.members.iterator().next();
            h.assertTrue(!EliteEncounters.spawnMechanist(level,key,feet,entrant),"Second entrant cannot duplicate the slot");var e=level.getEntity(id);var t=new CompoundTag();e.save(t);e.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            h.assertTrue(!EliteEncounters.spawnMechanist(level,key,feet,entrant)&&BlueprintSpawnState.load(BlueprintSpawnState.get(level).save(new CompoundTag())).markers.get(key).members.contains(id),"SavedData retains unloaded member");
            var loaded=EliteContent.MECHANIST.get().create(level);loaded.load(t);level.addFreshEntity(loaded);loaded.hurt(loaded.damageSources().genericKill(),10000);
            h.assertTrue(marker.members.isEmpty()&&marker.nextSpawn>=level.getGameTime()+11999,"Confirmed death alone starts a long cooldown");h.succeed();
        }finally{rule.set(old,level.getServer());}
    }
}
