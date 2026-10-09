package com.dynasty.blueprint;

import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class MiningSpiderGameTests {
    private static TemplateMob spider(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=8;y++)h.setBlock(x,y,z,y==1||y==7?Blocks.STONE:Blocks.AIR);
        var mob=h.spawn(BlueprintEntities.BAZU_DIGONGZHU.get(),new BlockPos(7,5,7));mob.setPos(mob.getX(),h.absolutePos(new BlockPos(0,5,0)).getY()+.6,mob.getZ());mob.setNoAi(true);return mob;
    }
    private static net.minecraft.world.entity.animal.Cow cow(GameTestHelper h,int x){
        var cow=h.spawn(EntityType.COW,new BlockPos(x,2,7));cow.setNoAi(true);cow.setNoGravity(true);cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);cow.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);cow.setHealth(200);return cow;
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=90,batch="mining_spider")
    public static void ceilingDropWaitsForActualLandingAndHitsOnlyOnce(GameTestHelper h){
        var mob=spider(h);mob.setNoAi(false);var target=cow(h,7);var outside=cow(h,13);
        h.runAfterDelay(3,()->{h.assertTrue(mob.hanging()&&mob.isNoGravity()&&!mob.noPhysics,"Real roof supports one physical hanging body");h.assertTrue(mob.startSkill(ArmySkills.SPIDER_DROP,target),"Starts ceiling drop");});
        h.runAfterDelay(21,()->h.assertTrue(target.getHealth()==200&&mob.hanging(),"Full warning remains harmless"));
        h.runAfterDelay(42,()->h.assertTrue(mob.onGround()&&!mob.hanging()&&!mob.isNoGravity()&&Math.abs(target.getHealth()-190.2)<.01&&outside.getHealth()==200,"Actual floor contact causes one bounded impact: ground="+mob.onGround()+" hanging="+mob.hanging()+" gravity="+mob.isNoGravity()+" hp="+target.getHealth()+" outside="+outside.getHealth()+" at="+mob.position()+" skill="+mob.skillId()));
        h.runAfterDelay(75,()->{h.assertTrue(Math.abs(target.getHealth()-190.2)<.01,"Grounded corpse/idle ticks cannot repeat impact");h.assertBlockPresent(Blocks.STONE,new BlockPos(7,1,7));h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=55,batch="mining_spider")
    public static void removingCeilingCancelsWindupWithoutDelayedExplosion(GameTestHelper h){
        var mob=spider(h);var target=cow(h,7);
        h.runAfterDelay(3,()->mob.startSkill(ArmySkills.SPIDER_DROP,target));
        h.runAfterDelay(10,()->{for(int x=5;x<=9;x++)for(int z=5;z<=9;z++)h.setBlock(x,7,z,Blocks.AIR);});
        h.runAfterDelay(40,()->{h.assertTrue(!mob.hanging()&&!mob.isNoGravity()&&target.getHealth()==200,"Lost support falls normally and cancels pending attack");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=65,batch="mining_spider")
    public static void ceilingCrawlerMovesUnderRoofWithoutCrossingSolidWalls(GameTestHelper h){
        var mob=spider(h);var target=cow(h,12);var original=mob.position();mob.setNoAi(false);mob.setTarget(target);
        h.runAfterDelay(17,()->{h.assertTrue(mob.getX()>original.x+.5&&Math.abs(mob.getY()-original.y)<.1&&!mob.noPhysics,"Moves across real ceiling with ordinary collision");mob.setNoAi(true);h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=25,batch="mining_spider")
    public static void authoredSpawnRejectsMissingCeilingAndRetainsEncounterCap(GameTestHelper h){
        // Native population cap uses a32-block AABB. Other simultaneous fixture spiders
        // are legitimate occupants: prepare this encounter above their physical region.
        var level=h.getLevel();var p=h.absolutePos(new BlockPos(7,55,7));
        for(int x=-4;x<=4;x++)for(int z=-4;z<=4;z++)for(int y=-4;y<=3;y++)level.setBlock(p.offset(x,y,z),(y==-4||y==2?Blocks.STONE:Blocks.AIR).defaultBlockState(),3);
        var entrant=p.offset(8,0,0);String key="test-spider-"+java.util.UUID.randomUUID();
        h.assertTrue(level.getEntitiesOfClass(TemplateMob.class,new net.minecraft.world.phys.AABB(p).inflate(32),e->e.isAlive()&&e.getType()==BlueprintEntities.BAZU_DIGONGZHU.get()).isEmpty(),"Actual isolated fixture contains no other native capped spiders");
        level.setBlock(p.above(2),Blocks.AIR.defaultBlockState(),3);h.assertTrue(!BlueprintSpawns.spawnMiningSpiders(level,key,java.util.List.of(p),entrant),"Missing support forbids ceiling spawn");level.setBlock(p.above(2),Blocks.STONE.defaultBlockState(),3);
        h.assertTrue(BlueprintSpawns.spawnMiningSpiders(level,key,java.util.List.of(p),entrant),"Legal loaded roof permits authored spider");
        h.assertTrue(!BlueprintSpawns.spawnMiningSpiders(level,key,java.util.List.of(p),entrant),"Encounter cap prevents duplicate spawn");
        level.getEntitiesOfClass(TemplateMob.class,new net.minecraft.world.phys.AABB(p).inflate(3),e->e.getType()==BlueprintEntities.BAZU_DIGONGZHU.get()).forEach(net.minecraft.world.entity.Entity::discard);h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="mining_spider")
    public static void eightLegRigClipsLoadThroughActualParser(GameTestHelper h) throws Exception {
        var gson=new com.google.gson.GsonBuilder().registerTypeAdapter(software.bernie.geckolib.loading.object.BakedAnimations.class,new software.bernie.geckolib.loading.json.typeadapter.BakedAnimationsAdapter()).create();
        try(var stream=MiningSpiderGameTests.class.getResourceAsStream("/assets/dynasty/animations/blueprint/bazu_digongzhu.animation.json")){
            var json=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(stream,java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject();
            var clips=gson.fromJson(json.getAsJsonObject("animations"),software.bernie.geckolib.loading.object.BakedAnimations.class);
            for(var name:java.util.List.of("idle","walk","run","attack","drop","hurt","death"))h.assertTrue(clips.getAnimation("animation.bazu_digongzhu."+name).boneAnimations().length>0,"Parsed "+name);
            h.assertTrue(clips.getAnimation("animation.bazu_digongzhu.drop").length()==100,"Ceiling-drop clock matches server definition");
        }h.succeed();
    }
}
