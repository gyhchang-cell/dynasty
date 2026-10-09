package com.dynasty.blueprint;

import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class ToadGameTests {
    private static TemplateMob toad(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=10;y++)h.setBlock(x,y,z,y==1||y==10?Blocks.STONE:Blocks.AIR);
        var mob=h.spawn(BlueprintEntities.CHIMU_ZHUHA.get(),new BlockPos(7,2,5));mob.setNoAi(true);mob.setOnGround(true);return mob;
    }
    private static net.minecraft.world.entity.animal.Cow enemy(GameTestHelper h,int x,int z){
        var cow=h.spawn(EntityType.COW,new BlockPos(x,2,z));cow.setNoAi(true);cow.setNoGravity(true);
        cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);cow.setHealth(200);return cow;
    }
    private static net.minecraft.server.level.ServerPlayer player(GameTestHelper h,int x,int z){
        var p=new net.minecraft.server.level.ServerPlayer(h.getLevel().getServer(),h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"toad-test"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        // Damage assertions must not race full-food vanilla natural regeneration.
        p.getFoodData().setFoodLevel(17);p.getFoodData().setSaturation(0);
        p.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(x,2,z))));h.getLevel().addNewPlayer(p);h.onEachTick(()->{if(!p.isRemoved())p.doTick();});return p;
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40,batch="toad")
    public static void tongueHitsFirstBodyOnceAndPullsRoughlyOneBlock(GameTestHelper h){
        var mob=toad(h);var front=enemy(h,7,9);var rear=enemy(h,7,10);
        front.setNoAi(false);front.getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(0);var original=front.position();
        h.assertTrue(mob.startSkill(ArmySkills.TOAD_TONGUE,front),"Grounded toad starts actual tongue");
        h.runAfterDelay(8,()->h.assertTrue(front.getHealth()==200,"Ten-tick tell is harmless"));
        h.runAfterDelay(22,()->{
            double pulled=original.z-front.getZ();
            h.assertTrue(front.getHealth()==194&&rear.getHealth()==200,"Only nearest intersecting body receives one bite");
            h.assertTrue(pulled>.5&&pulled<1.4,"Finite native velocity pull covers about one block: "+pulled);
            h.assertTrue(mob.tongueReach()>2&&mob.tongueReach()<5,"Tracked visual reach ends at actual collision");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=35,batch="toad")
    public static void tongueTellCanBeDodgedAndDoesNotHome(GameTestHelper h){
        var mob=toad(h);var cow=enemy(h,7,9);h.assertTrue(mob.startSkill(ArmySkills.TOAD_TONGUE,cow),"Tongue starts");
        h.runAfterDelay(8,()->cow.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(12,2,9)))));
        h.runAfterDelay(25,()->{h.assertTrue(cow.getHealth()==200,"Moving out of the locked ray dodges tongue");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=35,batch="toad")
    public static void tongueStopsAtNewWallAndUpdatesTrackedReach(GameTestHelper h){
        var mob=toad(h);var cow=enemy(h,7,9);h.assertTrue(mob.startSkill(ArmySkills.TOAD_TONGUE,cow),"Tongue starts before obstruction");
        h.runAfterDelay(8,()->{for(int x=6;x<9;x++)for(int y=2;y<6;y++)h.setBlock(x,y,7,Blocks.STONE);});
        h.runAfterDelay(20,()->{h.assertTrue(cow.getHealth()==200&&mob.tongueReach()<=1.6,"New wall blocks real hit and visual length");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=170,batch="toad_ai")
    public static void autonomousToadWaitsThenLeapsAndTonguesWithoutWalking(GameTestHelper h){
        var mob=toad(h);var cow=enemy(h,7,15);var initial=mob.position();mob.setNoAi(false);mob.setTarget(cow);boolean[] high={false},landed={false};double[] firstLanding={0};
        h.onEachTick(()->{if(h.getTick()%20==0)com.mojang.logging.LogUtils.getLogger().info("TOAD_FLIGHT tick={} relative={} enemy={} target={} skill={} age={} hp={} ground={}",h.getTick(),mob.position().subtract(initial),cow.position().subtract(initial),mob.getTarget()==cow,mob.skillId(),mob.actionAge(0),cow.getHealth(),mob.onGround());if(mob.getY()>initial.y+1)high[0]=true;if(high[0]&&!landed[0]&&mob.onGround()){landed[0]=true;firstLanding[0]=mob.position().subtract(initial).horizontalDistance();}});
        h.runAfterDelay(8,()->h.assertTrue(mob.position().distanceTo(initial)<.15,"Waits through crouched take-off tell"));
        h.runAfterDelay(140,()->{
            h.assertTrue(high[0]&&landed[0]&&mob.position().distanceTo(initial)>4&&cow.getHealth()<200,
                "Actual AI jumps under gravity, lands and attacks; high="+high[0]+" landed="+landed[0]+" at="+mob.position()+" hp="+cow.getHealth());
            h.assertTrue(firstLanding[0]>5&&firstLanding[0]<7,"First real landing is approximately six blocks away: "+firstLanding[0]);
            h.assertTrue(!mob.noPhysics&&!mob.isNoGravity()&&mob.getNavigation() instanceof net.minecraft.world.entity.ai.navigation.AmphibiousPathNavigation,"Amphibious navigation retains normal gravity/collision");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=130,batch="toad")
    public static void heavyHitQueuesSixPhysicalVenomBoltsAndCooldownSurvivesReload(GameTestHelper h){
        var mob=toad(h);var cow=enemy(h,7,9);
        h.assertTrue(!mob.startSkill(ArmySkills.TOAD_BURST,cow),"Burst cannot be invoked without heavy injury");
        mob.hurt(mob.damageSources().mobAttack(cow),1);h.assertTrue(!mob.startSkill(ArmySkills.TOAD_BURST,cow),"Light hit cannot spray venom");
        // Existing Dynasty morale reduces incoming damage before armour. Twelve raw
        // damage, unlike eight, is a genuine >=6HP heavy hit after both reductions.
        mob.invulnerableTime=0;float before=mob.getHealth();mob.hurt(mob.damageSources().mobAttack(cow),12);mob.setDeltaMovement(Vec3.ZERO);
        h.assertTrue(before-mob.getHealth()>=6,"Fixture lands a real post-armour heavy hit");
        h.assertTrue(mob.startSkill(ArmySkills.TOAD_BURST,cow),"Heavy actual health loss arms burst");
        h.runAfterDelay(10,()->h.assertTrue(h.getLevel().getEntitiesOfClass(TemplateProjectile.class,mob.getBoundingBox().inflate(10),p->p.armyMode()==3).isEmpty(),"No early projectiles"));
        h.runAfterDelay(14,()->{
            var shots=h.getLevel().getEntitiesOfClass(TemplateProjectile.class,mob.getBoundingBox().inflate(10),p->p.armyMode()==3);
            h.assertTrue(shots.size()==6&&shots.stream().allMatch(p->p.getOwner()==mob),"Exactly six logical projectiles retain real owner identity");
            var tag=new CompoundTag();mob.save(tag);mob.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            var copy=BlueprintEntities.CHIMU_ZHUHA.get().create(h.getLevel());copy.load(tag);h.getLevel().addFreshEntity(copy);
            copy.invulnerableTime=0;copy.hurt(copy.damageSources().mobAttack(cow),12);
            h.assertTrue(!copy.startSkill(ArmySkills.TOAD_BURST,cow),"Reload cannot re-arm reserved cooldown");
            h.runAfterDelay(30,()->{
                var pools=h.getLevel().getEntitiesOfClass(CorpseMiasma.class,copy.getBoundingBox().inflate(16),CorpseMiasma::isFiery);
                h.assertTrue(!pools.isEmpty()&&pools.size()<=6,"Real projectile floor impacts create capped fiery poison areas");
                h.runAfterDelay(80,()->{h.assertTrue(h.getLevel().getEntitiesOfClass(CorpseMiasma.class,copy.getBoundingBox().inflate(16),CorpseMiasma::isFiery).isEmpty(),"All venom areas expire");h.succeed();});
            });
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=180,batch="toad_effects",setupTicks=20)
    public static void firePoisonAffectsNearbyEnemyOnlyAndExpiresAcrossUnload(GameTestHelper h){
        var owner=toad(h);
        // This fixture measures poison/fire expiry, not attacks by naturally spawned assassins.
        for(int n=0;n<16;n++)for(int y=2;y<10;y++){h.setBlock(0,y,n,Blocks.STONE);h.setBlock(15,y,n,Blocks.STONE);h.setBlock(n,y,0,Blocks.STONE);h.setBlock(n,y,15,Blocks.STONE);}
        var a=player(h,7,8);var b=player(h,12,8);var ally=h.spawn(BlueprintEntities.SHANJING_SHANXIAO.get(),new BlockPos(7,2,8));ally.setNoAi(true);
        var pool=new CorpseMiasma(BlueprintEntities.TOAD_VENOM_POOL.get(),h.getLevel());var saved=new CompoundTag();
        h.runAfterDelay(65,()->{pool.setPos(a.position());pool.setOwner(owner);pool.activateFirePoison(h.getLevel().getGameTime());h.getLevel().addFreshEntity(pool);});
        h.runAfterDelay(93,()->{
            h.assertTrue(a.getHealth()<20&&a.hasEffect(net.minecraft.world.effect.MobEffects.POISON)&&a.isOnFire(),"Real player receives both timed damage types: hp="+a.getHealth()+", fire="+a.isOnFire()+", poison="+a.hasEffect(net.minecraft.world.effect.MobEffects.POISON)+", distance="+a.distanceTo(pool)+", tracked="+(h.getLevel().getEntity(pool.getUUID())==pool));
            h.assertTrue(b.getHealth()==20&&!b.isOnFire()&&!b.hasEffect(net.minecraft.world.effect.MobEffects.POISON),"Other player outside radius is safe");
            h.assertTrue(!ally.isOnFire()&&!ally.hasEffect(net.minecraft.world.effect.MobEffects.POISON),"Woodland allies are immune");
            pool.save(saved);pool.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);a.setInvulnerable(true);b.setInvulnerable(true);a.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(12,2,12))));
        });
        h.runAfterDelay(160,()->{
            var restored=new CorpseMiasma(BlueprintEntities.TOAD_VENOM_POOL.get(),h.getLevel());restored.load(saved);h.getLevel().addFreshEntity(restored);
            h.runAfterDelay(3,()->{h.assertTrue(restored.isRemoved()&&!a.isOnFire()&&!a.hasEffect(net.minecraft.world.effect.MobEffects.POISON),"Expired area leaves no residual effects: removed="+restored.isRemoved()+" alive="+a.isAlive()+" fire="+a.isOnFire()+" poison="+a.getEffect(net.minecraft.world.effect.MobEffects.POISON));a.discard();b.discard();h.succeed();});
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40,batch="toad_ecology")
    public static void registeredEcologyRejectsSinglePuddleAndHonoursBiomeAndLocalCap(GameTestHelper h){
        var fixture=toad(h);fixture.discard();var level=h.getLevel();var pos=h.absolutePos(new BlockPos(7,2,7));
        var a=h.absolutePos(new BlockPos(0,0,0));var b=h.absolutePos(new BlockPos(15,9,15));
        level.getServer().getCommands().performPrefixedCommand(level.getServer().createCommandSourceStack().withLevel(level).withPermission(4).withSuppressedOutput(),
            "fillbiome "+a.getX()+" "+a.getY()+" "+a.getZ()+" "+b.getX()+" "+b.getY()+" "+b.getZ()+" minecraft:swamp");
        h.setBlock(8,1,7,Blocks.WATER);
        var type=BlueprintEntities.CHIMU_ZHUHA.get();
        h.assertTrue(!net.minecraft.world.entity.SpawnPlacements.checkSpawnRules(type,level,net.minecraft.world.entity.MobSpawnType.NATURAL,pos,level.random),"Registered predicate rejects one water block");
        for(int x=8;x<=11;x++)for(int z=6;z<=9;z++)h.setBlock(x,1,z,Blocks.WATER);
        h.assertTrue(net.minecraft.world.entity.SpawnPlacements.checkSpawnRules(type,level,net.minecraft.world.entity.MobSpawnType.NATURAL,pos,level.random),"Connected shoreline water passes actual registered ecology");
        var entries=level.getBiome(pos).value().getMobSettings().getMobs(net.minecraft.world.entity.MobCategory.MONSTER).unwrap();
        h.assertTrue(entries.stream().anyMatch(e->e.type==type&&e.minCount==1&&e.maxCount==2&&e.getWeight().asInt()==4),"Forge biome modifier really enters natural monster spawn pool");
        var first=type.spawn(level,pos,net.minecraft.world.entity.MobSpawnType.NATURAL);var second=type.spawn(level,pos.offset(-2,0,0),net.minecraft.world.entity.MobSpawnType.NATURAL);
        h.assertTrue(first!=null&&second!=null&&!first.isNoAi(),"Real entity spawn initializes active toad AI");
        h.assertTrue(!net.minecraft.world.entity.SpawnPlacements.checkSpawnRules(type,level,net.minecraft.world.entity.MobSpawnType.NATURAL,pos,level.random),"Two local toads close the natural spawn gate");
        h.assertTrue(!BlueprintSpawns.toadHabitat(level.getServer().getLevel(net.minecraft.world.level.Level.NETHER),pos),"Cannot spill into another dimension");first.discard();second.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="toad")
    public static void toadClipsLoadThroughActualAnimationParser(GameTestHelper h) throws Exception {
        var gson=new com.google.gson.GsonBuilder().registerTypeAdapter(software.bernie.geckolib.loading.object.BakedAnimations.class,new software.bernie.geckolib.loading.json.typeadapter.BakedAnimationsAdapter()).create();
        try(var stream=ToadGameTests.class.getResourceAsStream("/assets/dynasty/animations/blueprint/chimu_zhuha.animation.json")){
            var json=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(stream,java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject();
            var clips=gson.fromJson(json.getAsJsonObject("animations"),software.bernie.geckolib.loading.object.BakedAnimations.class);
            for(var name:java.util.List.of("idle","walk","run","attack","leap","burst","hurt","death"))h.assertTrue(clips.getAnimation("animation.chimu_zhuha."+name).boneAnimations().length>0,"Actual GeckoLib parser accepts "+name);
            h.assertTrue(clips.getAnimation("animation.chimu_zhuha.leap").length()==40&&clips.getAnimation("animation.chimu_zhuha.burst").length()==32,"Movement and burst clocks match server skills");
        }
        h.succeed();
    }
}
