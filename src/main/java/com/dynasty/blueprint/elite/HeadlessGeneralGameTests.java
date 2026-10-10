package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.BlueprintSpawnState;
import com.dynasty.blueprint.SkullBloodPool;
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
public final class HeadlessGeneralGameTests {
    private static final java.util.Map<net.minecraft.server.level.ServerLevel,Runnable> WORLD_CLEANUP=new java.util.HashMap<>();
    @AfterBatch(batch="headless_world") public static void cleanWorldFixture(net.minecraft.server.level.ServerLevel level){
        var cleanup=WORLD_CLEANUP.remove(level);if(cleanup!=null)cleanup.run();
    }
    private static HeadlessGeneral mob(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++){
            h.setBlock(x,1,z,Blocks.STONE);for(int y=2;y<=9;y++)h.setBlock(x,y,z,Blocks.AIR);
            if(x==0||x==15||z==0||z==15)for(int y=2;y<=7;y++)h.setBlock(x,y,z,Blocks.STONE);
        }
        var m=h.spawn(EliteContent.HEADLESS.get(),new BlockPos(7,2,7));m.setNoAi(true);m.setNoGravity(true);return m;
    }
    private static Cow cow(GameTestHelper h,int x,int z){var c=h.spawn(EntityType.COW,new BlockPos(x,2,z));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);c.setHealth(1000);return c;}
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="headless_elite")
    public static void roarHasFullTellAndConeSideEscape(GameTestHelper h){
        var m=mob(h);var front=cow(h,7,13);var side=cow(h,12,7);
        h.assertTrue(m.startSkill(301,front),"Real server roar starts");
        h.runAfterDelay(22,()->h.assertTrue(front.getHealth()==1000&&side.getHealth()==1000,"No damage before 1.2-second tell"));
        h.runAfterDelay(27,()->h.assertTrue(front.getHealth()<1000&&side.getHealth()==1000&&front.hasEffect(net.minecraft.world.effect.MobEffects.WEAKNESS),"Cone contact hits front but permits lateral evasion"));
        h.runAfterDelay(92,()->{h.assertTrue(!front.hasEffect(net.minecraft.world.effect.MobEffects.WEAKNESS)&&m.skillId()==0,"Finite weakness and action cleanup");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=85,batch="headless_elite")
    public static void spinHasThreeContactsAndThirtyTickRecovery(GameTestHelper h){
        var m=mob(h);var target=cow(h,7,9);float[] hp={1000,1000,1000};
        h.onEachTick(()->{if(target.isAlive()){target.setPos(m.position().add(0,0,1));target.setDeltaMovement(Vec3.ZERO);}});
        h.assertTrue(m.startSkill(302,target),"Spin starts");
        h.runAfterDelay(14,()->h.assertTrue(target.getHealth()==1000,"Full 0.8-second twist warning"));
        h.runAfterDelay(28,()->{hp[0]=target.getHealth();h.assertTrue(hp[0]<1000,"First circle contact");});
        h.runAfterDelay(38,()->{hp[1]=target.getHealth();h.assertTrue(hp[1]<hp[0],"Second circle contact");});
        h.runAfterDelay(48,()->{hp[2]=target.getHealth();h.assertTrue(hp[2]<hp[1],"Third circle contact");});
        h.runAfterDelay(55,()->h.assertTrue(m.phase()==AttackState.RECOVERY&&target.getHealth()==hp[2],"Recovery leaves a real punish window with no damage"));
        h.runAfterDelay(80,()->{h.assertTrue(target.getHealth()==hp[2]&&m.skillId()==0&&!m.startSkill(302,target),"Exactly three contacts; cooldown remains");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60,batch="headless_elite")
    public static void thrownHeadLocksLandingAndReloadDoesNotReplay(GameTestHelper h){
        var m=mob(h);var target=cow(h,7,12);var landing=target.position();
        h.assertTrue(m.startSkill(303,target),"Head throw starts");
        h.runAfterDelay(10,()->target.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(12,2,12)))));
        h.runAfterDelay(23,()->{
            h.assertTrue(target.getHealth()==1000,"Sidestep escapes locked landing");
            var pools=h.getLevel().getEntitiesOfClass(SkullBloodPool.class,m.getBoundingBox().inflate(12));
            h.assertTrue(pools.size()==1&&pools.get(0).position().distanceToSqr(landing)<.01,"One pool uses the warned point");
            var saved=new CompoundTag();m.save(saved);var id=m.getUUID();m.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            var restored=EliteContent.HEADLESS.get().create(h.getLevel());restored.load(saved);h.getLevel().addFreshEntity(restored);
            h.runAtTickTime(50,()->{h.assertTrue(restored.getUUID().equals(id)&&h.getLevel().getEntitiesOfClass(SkullBloodPool.class,restored.getBoundingBox().inflate(12)).size()==1,"Consumed impact remains consumed after real entity NBT reload");h.succeed();});
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=50,batch="headless_elite")
    public static void rearCounterBreaksThrowButNotSpin(GameTestHelper h){
        var m=mob(h);var target=cow(h,7,10);var rear=cow(h,7,5);
        h.assertTrue(m.startSkill(303,target),"Throw tell begins");m.hurt(m.damageSources().mobAttack(rear),4);
        h.assertTrue(m.attack().current()==null&&m.phase()==AttackState.STUN,"Actual accepted back hit interrupts throw");
        h.runAfterDelay(32,()->{
            h.assertTrue(h.getLevel().getEntitiesOfClass(SkullBloodPool.class,m.getBoundingBox().inflate(12)).isEmpty(),"Cancelled throw never leaks delayed damage");
            h.assertTrue(m.startSkill(302,target),"Independent spin remains usable");m.invulnerableTime=0;m.hurt(m.damageSources().mobAttack(rear),4);
            h.assertTrue(m.attack().current()==HeadlessGeneral.SPIN,"Spin retains authored unstoppable windup");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=35,batch="headless_elite")
    public static void structureMembershipSurvivesUnloadAndBlocksSecondEntrant(GameTestHelper h){
        var level=h.getLevel();var feet=new BlockPos(10000,130,10000);var entrant=feet.offset(-6,0,-6);
        level.getChunkAt(feet);
        for(int x=-2;x<=2;x++)for(int z=-2;z<=2;z++){
            level.setBlockAndUpdate(feet.offset(x,-1,z),Blocks.STONE.defaultBlockState());
            for(int y=0;y<=5;y++)level.setBlockAndUpdate(feet.offset(x,y,z),Blocks.AIR.defaultBlockState());
        }
        var rule=level.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING);boolean previous=rule.get();rule.set(true,level.getServer());
        String key="headless-gametest@"+feet.asLong();
        try{
            h.assertTrue(EliteEncounters.spawn(level,key,feet,entrant),"One native authored encounter spawns");
            var marker=BlueprintSpawnState.get(level).markers.get(key);var id=marker.members.iterator().next();
            h.assertTrue(!EliteEncounters.spawn(level,key,feet,entrant.offset(1,0,0)),"Second entrant cannot duplicate member");
            var actor=level.getEntity(id);h.assertTrue(actor instanceof HeadlessGeneral,"Actual registered elite identity");var actorState=new CompoundTag();actor.save(actorState);actor.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            h.assertTrue(!EliteEncounters.spawn(level,key,feet,entrant)&&marker.members.contains(id),"Null UUID lookup is not death");
            var snapshot=BlueprintSpawnState.load(BlueprintSpawnState.get(level).save(new CompoundTag()));
            h.assertTrue(snapshot.markers.get(key).members.contains(id),"Native SavedData retains membership");
            var restored=EliteContent.HEADLESS.get().create(level);restored.load(actorState);level.addFreshEntity(restored);restored.discard();
            h.runAfterDelay(3,()->{h.assertTrue(marker.members.isEmpty()&&marker.nextSpawn>level.getGameTime(),"Confirmed permanent removal releases the same marker, unlike chunk unload");h.succeed();});
        }finally{rule.set(previous,level.getServer());}
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=240,batch="headless_world")
    public static void productionBattlefieldTickSpawnsRealEliteAndStartsDeathCooldown(GameTestHelper h){
        var level=h.getLevel();var registry=level.registryAccess();var structure=registry.registryOrThrow(net.minecraft.core.registries.Registries.STRUCTURE)
            .get(new net.minecraft.resources.ResourceLocation("dynasty","ruined_battlefield"));
        var settings=net.minecraft.world.level.levelgen.flat.FlatLevelGeneratorSettings.getDefault(registry.lookupOrThrow(net.minecraft.core.registries.Registries.BIOME),
            registry.lookupOrThrow(net.minecraft.core.registries.Registries.STRUCTURE_SET),registry.lookupOrThrow(net.minecraft.core.registries.Registries.PLACED_FEATURE));
        settings.getLayersInfo().clear();settings.getLayersInfo().add(new net.minecraft.world.level.levelgen.flat.FlatLayerInfo(127,Blocks.STONE));
        settings.getLayersInfo().add(new net.minecraft.world.level.levelgen.flat.FlatLayerInfo(1,Blocks.GRASS_BLOCK));settings.updateLayers();
        var generator=new net.minecraft.world.level.levelgen.FlatLevelSource(settings);var origin=new net.minecraft.world.level.ChunkPos(640,640);
        // Remote fixture chunks need a native ticket: a FakePlayer has no client view-distance tickets.
        level.getChunkSource().addRegionTicket(net.minecraft.server.level.TicketType.FORCED,origin,3,origin);
        var start=structure.generate(registry,generator,generator.getBiomeSource(),level.getChunkSource().randomState(),level.getStructureManager(),level.getSeed(),origin,0,level,b->true);
        h.assertTrue(start.isValid(),"Production battlefield generates from a real levelled terrain context");
        level.getChunk(origin.x,origin.z).setStartForStructure(structure,start);var bounds=start.getBoundingBox();
        var tickingChunks=new java.util.ArrayList<net.minecraft.world.level.ChunkPos>();
        for(int x=bounds.minX()>>4;x<=bounds.maxX()>>4;x++)for(int z=bounds.minZ()>>4;z<=bounds.maxZ()>>4;z++){
            var chunk=level.getChunk(x,z);chunk.addReferenceForStructure(structure,origin.toLong());
            var position=chunk.getPos();tickingChunks.add(position);
            level.getChunkSource().addRegionTicket(net.minecraft.server.level.TicketType.FORCED,position,2,position);
            var clip=new net.minecraft.world.level.levelgen.structure.BoundingBox(x*16,bounds.minY(),z*16,x*16+15,bounds.maxY(),z*16+15);
            for(var piece:start.getPieces())piece.postProcess(level,level.structureManager(),generator,net.minecraft.util.RandomSource.create(3),clip,chunk.getPos(),BlockPos.ZERO);
        }
        var player=new net.minecraftforge.common.util.FakePlayer(level,new com.mojang.authlib.GameProfile(java.util.UUID.randomUUID(),"headless-entry"));
        var floor=start.getPieces().get(0).getBoundingBox();
        player.setGameMode(net.minecraft.world.level.GameType.CREATIVE);player.setPos(floor.minX()+10.5,floor.minY()+4,floor.minZ()+12.5);level.addNewPlayer(player);
        h.assertTrue(level.getBlockState(player.blockPosition().below()).isFaceSturdy(level,player.blockPosition().below(),net.minecraft.core.Direction.UP),"Entrant stands on the generated battlefield, not the structure's expanded terrain-adaptation bounds");
        var killHook=level.getServer().getAdvancements().getAdvancement(new net.minecraft.resources.ResourceLocation("dynasty","blueprint/kill_xianzhen_duantoujiang"));
        h.assertTrue(killHook!=null,"Registered kill advancement loads from runtime resources");
        var rule=level.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING);boolean previous=rule.get();rule.set(true,level.getServer());
        String key=level.dimension().location()+"/dynasty:ruined_battlefield@"+origin.toLong()+":headless_general";
        WORLD_CLEANUP.put(level,()->{
            rule.set(previous,level.getServer());level.players().remove(player);player.discard();
            level.getChunkSource().removeRegionTicket(net.minecraft.server.level.TicketType.FORCED,origin,3,origin);
            for(var chunk:tickingChunks)level.getChunkSource().removeRegionTicket(net.minecraft.server.level.TicketType.FORCED,chunk,2,chunk);
        });
        h.startSequence().thenWaitUntil(()->{
            var marker=BlueprintSpawnState.get(level).markers.get(key);
            var entity=marker==null||marker.members.isEmpty()?null:level.getEntity(marker.members.iterator().next());
            h.assertTrue(entity instanceof HeadlessGeneral,"Wait for a real accessible structure-spawned actor; marker="+
                (marker==null?"absent":marker.produced+"/"+marker.members+" next="+marker.nextSpawn)+" gameTime="+level.getGameTime()+
                " entrant="+player.position()+" ticking="+level.isPositionEntityTicking(player.blockPosition()));
        }).thenExecute(()->{
            var marker=BlueprintSpawnState.get(level).markers.get(key);
            h.assertTrue(marker.members.size()==1,"Native structure tick enforces one elite");
            var elite=(HeadlessGeneral)level.getEntity(marker.members.iterator().next());
            h.assertTrue(!elite.isNoAi()&&!elite.isNoGravity()&&elite.encounterSite().equals(key),"Production actor has ordinary AI, gravity and persisted site");
            elite.hurt(elite.damageSources().playerAttack(player),10000);
            h.assertTrue(elite.isDeadOrDying()&&marker.members.isEmpty()&&marker.nextSpawn>level.getGameTime(),"Confirmed death releases UUID and starts actual cooldown");
            // Forge refuses advancement awards to FakePlayer; HeadlessClientQa uses a real connected player.
            h.assertTrue(!EliteEncounters.spawn(level,key,elite.blockPosition(),player.blockPosition()),"Immediate re-entry cannot refill");
        }).thenSucceed();
    }
}
