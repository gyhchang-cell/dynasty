package com.dynasty.blueprint;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.*;
@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class CentipedeGameTests {
    private static TemplateMob worm(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=8;y++)h.setBlock(x,y,z,y==1||y==8||x==0||x==15||z==0||z==15?Blocks.STONE:Blocks.AIR);
        var mob=h.spawn(BlueprintEntities.BAIMU_MOWU.get(),new BlockPos(7,2,7));mob.setNoAi(true);return mob;
    }
    private static net.minecraft.world.entity.animal.Cow cow(GameTestHelper h,int x,int z){var c=h.spawn(EntityType.COW,new BlockPos(x,2,z));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);c.setHealth(200);return c;}
    private static void look(net.minecraft.world.entity.LivingEntity e,net.minecraft.world.phys.Vec3 p){var d=p.subtract(e.getEyePosition());e.setYRot((float)Math.toDegrees(Math.atan2(-d.x,d.z)));e.setXRot((float)-Math.toDegrees(Math.atan2(d.y,d.horizontalDistance())));}
    @GameTest(template="bow_ritual_test",timeoutTicks=115,batch="centipede")
    public static void gazeHasTellFacingGateAndFiniteYellowSlow(GameTestHelper h){
        var mob=worm(h);var front=cow(h,7,11);var away=cow(h,11,7);look(front,mob.position().add(0,.85,0));look(away,away.position().add(8,1,0));mob.startSkill(ArmySkills.CENTIPEDE_GAZE,front);
        h.runAfterDelay(24,()->h.assertTrue(!front.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"No gaze before26ticks"));
        h.runAfterDelay(30,()->h.assertTrue(front.getEffect(MobEffects.MOVEMENT_SLOWDOWN)!=null&&front.getEffect(MobEffects.MOVEMENT_SLOWDOWN).getAmplifier()==3&&front.getEffect(BlueprintEntities.LANTERN_GLARE.get()).getAmplifier()==2&&!away.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Only facing enemy gets60percent slow and yellow edge glare"));
        h.runAfterDelay(100,()->{h.assertTrue(!front.hasEffect(MobEffects.MOVEMENT_SLOWDOWN)&&!front.hasEffect(BlueprintEntities.LANTERN_GLARE.get()),"Effects expire without camera changes");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=75,batch="centipede")
    public static void solidWallBlocksLateGazeAndBiteHasSinglePoisonContact(GameTestHelper h){
        var mob=worm(h);var target=cow(h,7,9);look(target,mob.position().add(0,.85,0));mob.startSkill(ArmySkills.CENTIPEDE_BITE,target);
        h.runAfterDelay(10,()->h.assertTrue(target.getHealth()==200,"Bite telegraph harmless"));
        h.runAfterDelay(15,()->h.assertTrue(target.getHealth()==195&&target.hasEffect(MobEffects.POISON),"Actual magic bite plus finite poison"));
        h.runAfterDelay(34,()->{mob.startSkill(ArmySkills.CENTIPEDE_GAZE,target);h.setBlock(7,2,8,Blocks.STONE);h.setBlock(7,3,8,Blocks.STONE);});
        h.runAfterDelay(64,()->{h.assertTrue(!target.hasEffect(BlueprintEntities.LANTERN_GLARE.get()),"New solid wall blocks gaze");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=55,batch="centipede")
    public static void ceilingCrawlKeepsCollisionAndDropsWhenRoofRemoved(GameTestHelper h){
        var mob=worm(h);mob.setPos(mob.getX(),h.absolutePos(new BlockPos(7,7,7)).getY()+.15,mob.getZ());var target=cow(h,12,7);mob.setNoAi(false);mob.setTarget(target);var original=mob.position();
        // Long initial recovery isolates locomotion from gaze without replacing its normal travel.
        mob.interruptAttack(30);
        h.runAfterDelay(12,()->h.assertTrue(mob.hanging()&&mob.isNoGravity()&&!mob.noPhysics&&mob.getX()>original.x+.3,"Physical supported ceiling movement"));
        h.runAfterDelay(15,()->{for(int x=1;x<15;x++)for(int z=1;z<15;z++)h.setBlock(x,8,z,Blocks.AIR);});
        h.runAfterDelay(32,()->{h.assertTrue(!mob.hanging()&&!mob.isNoGravity()&&mob.getY()<original.y-.3,"Removing roof causes normal gravity, not hovering/noclip");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=45,batch="centipede_ecology")
    public static void singleBodyCapAndSixteenSegmentClips(GameTestHelper h)throws Exception{
        var level=h.getLevel();var pos=h.absolutePos(new BlockPos(7,2,7)).atY(level.getMinBuildHeight()+4);
        for(int x=-3;x<=3;x++)for(int z=-3;z<=3;z++){level.getChunk(pos.offset(x,0,z));for(int y=-1;y<=5;y++)level.setBlock(pos.offset(x,y,z),(y==-1||y==5||Math.abs(x)==3||Math.abs(z)==3?Blocks.STONE:Blocks.AIR).defaultBlockState(),3);}
        // This separate batch runs after or before the combat batch, never alongside it.
        // Clear completed centipede fixtures in this test's cap radius, then use a ticking test chunk.
        for(var old:level.getEntitiesOfClass(TemplateMob.class,new net.minecraft.world.phys.AABB(pos).inflate(32),m->m.kind()==TemplateMob.Kind.CENTIPEDE))old.discard();
        h.runAfterDelay(12,()->{
            h.assertTrue(BlueprintSpawns.centipedeHabitat(level,pos),"Empty isolated deep cave accepts spawn");
            var mob=BlueprintEntities.BAIMU_MOWU.get().create(level);mob.setPos(pos.getX()+.5,pos.getY(),pos.getZ()+.5);mob.setNoAi(true);mob.setPersistenceRequired();
            h.assertTrue(level.addFreshEntity(mob),"Fixture entity added");
            h.runAfterDelay(3,()->{
                h.assertTrue(level.getEntity(mob.getUUID())==mob,"Fixture is actually accessible");
                h.assertTrue(!BlueprintSpawns.centipedeHabitat(level,pos),"One loaded worm caps population");
                mob.discard();h.assertTrue(BlueprintSpawns.centipedeHabitat(level,pos),"Removing sole worm restores spawn eligibility");h.succeed();
            });
        });
        var gson=new com.google.gson.GsonBuilder().registerTypeAdapter(software.bernie.geckolib.loading.object.BakedAnimations.class,new software.bernie.geckolib.loading.json.typeadapter.BakedAnimationsAdapter()).create();
        try(var in=CentipedeGameTests.class.getResourceAsStream("/assets/dynasty/animations/blueprint/baimu_mowu.animation.json")){
            var json=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(in)).getAsJsonObject();var clips=gson.fromJson(json.get("animations"),software.bernie.geckolib.loading.object.BakedAnimations.class);
            for(var n:java.util.List.of("idle","walk","run","attack","gaze","hurt","death"))h.assertTrue(clips.getAnimation("animation.baimu_mowu."+n).boneAnimations().length>0,"Parses "+n);
            h.assertTrue(json.getAsJsonObject("animations").getAsJsonObject("animation.baimu_mowu.walk").getAsJsonObject("bones").size()==48,"16body+32legs drive the phase wave");
        }
    }
}
