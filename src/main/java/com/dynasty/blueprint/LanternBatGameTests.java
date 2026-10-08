package com.dynasty.blueprint;

import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class LanternBatGameTests {
    private static TemplateMob bat(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=11;y++)
            h.setBlock(x,y,z,y==1||y==11||x==0||x==15||z==0||z==15?Blocks.STONE:Blocks.AIR);
        var mob=h.spawn(BlueprintEntities.YOUDENG_GUIMIANFU.get(),new BlockPos(7,6,5));mob.setNoAi(true);return mob;
    }
    private static net.minecraft.world.entity.animal.Cow cow(GameTestHelper h,int x,int z){
        var cow=h.spawn(EntityType.COW,new BlockPos(x,2,z));cow.setNoAi(true);cow.setNoGravity(true);cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);cow.setHealth(200);return cow;
    }
    private static void look(net.minecraft.world.entity.LivingEntity target,net.minecraft.world.phys.Vec3 p){
        var d=p.subtract(target.getEyePosition());target.setYRot((float)Math.toDegrees(Math.atan2(-d.x,d.z)));
        target.setXRot((float)-Math.toDegrees(Math.atan2(d.y,d.horizontalDistance())));
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=85,batch="lantern_bat")
    public static void physicalDiveContactsOnceAndReloadKeepsConsumedHit(GameTestHelper h){
        var mob=bat(h);var target=cow(h,7,10);mob.setNoAi(false);h.assertTrue(mob.startSkill(ArmySkills.BAT_DIVE,target),"Starts locked dive");
        h.runAfterDelay(16,()->h.assertTrue(target.getHealth()==200,"18 tick aim is harmless"));
        h.startSequence().thenWaitUntil(()->h.assertTrue(target.getHealth()==195,"Actual body reaches victim"))
            .thenExecute(()->{
                h.assertTrue(mob.actionAge(0)>=18&&mob.actionAge(0)<32&&!mob.noPhysics,"Only dive phase contacts, normal collision");
                var tag=new CompoundTag();mob.save(tag);mob.discard();var restored=BlueprintEntities.YOUDENG_GUIMIANFU.get().create(h.getLevel());restored.load(tag);h.getLevel().addFreshEntity(restored);target.invulnerableTime=0;
            }).thenIdle(25).thenExecute(()->h.assertTrue(target.getHealth()==195,"Pass/reload cannot hit twice")).thenSucceed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60,batch="lantern_bat")
    public static void movingTargetDodgesAndLateWallBlocksDive(GameTestHelper h){
        var mob=bat(h);var target=cow(h,7,10);mob.setNoAi(false);mob.startSkill(ArmySkills.BAT_DIVE,target);
        h.runAfterDelay(12,()->{
            target.setPos(target.getX()+4,target.getY(),target.getZ());
            for(int x=5;x<=9;x++)for(int y=2;y<=9;y++)h.setBlock(x,y,7,Blocks.STONE);
        });
        h.runAfterDelay(42,()->{h.assertTrue(target.getHealth()==200&&mob.getZ()<h.absolutePos(new BlockPos(7,2,7)).getZ(),"Late wall stops physical flight and locked course cannot follow relocated target");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=110,batch="lantern_bat")
    public static void glareRequiresFacingSightAndExpiresWithoutBlindness(GameTestHelper h){
        var mob=bat(h);var facing=cow(h,7,10);var away=cow(h,10,10);var hidden=cow(h,4,10);
        look(facing,mob.getEyePosition());look(hidden,mob.getEyePosition());look(away,away.getEyePosition().add(0,0,10));
        h.assertTrue(mob.startSkill(ArmySkills.BAT_GLARE,facing),"Glare starts");
        h.runAfterDelay(10,()->{for(int x=2;x<=5;x++)for(int y=2;y<=9;y++)h.setBlock(x,y,8,Blocks.STONE);});
        h.runAfterDelay(22,()->h.assertTrue(!facing.hasEffect(BlueprintEntities.LANTERN_GLARE.get()),"No effect during windup"));
        h.runAfterDelay(28,()->h.assertTrue(facing.hasEffect(BlueprintEntities.LANTERN_GLARE.get())&&!away.hasEffect(BlueprintEntities.LANTERN_GLARE.get())&&!hidden.hasEffect(BlueprintEntities.LANTERN_GLARE.get())&&!facing.hasEffect(net.minecraft.world.effect.MobEffects.BLINDNESS),"Only visible facing victim gets finite coloured edge glare"));
        h.runAfterDelay(92,()->{h.assertTrue(!facing.hasEffect(BlueprintEntities.LANTERN_GLARE.get()),"Native effect expires after60ticks");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=25,batch="lantern_bat")
    public static void habitatRequiresActualLargeDryPocketAndLocalCap(GameTestHelper h){
        var mob=bat(h);mob.discard();var p=h.absolutePos(new BlockPos(7,4,7));
        h.assertTrue(BlueprintSpawns.batHabitat(h.getLevel(),p),"Real covered large cave accepted");
        h.setBlock(7,5,7,Blocks.STONE);h.assertTrue(!BlueprintSpawns.batHabitat(h.getLevel(),p),"Low ceiling/solid pocket rejected");h.setBlock(7,5,7,Blocks.AIR);
        h.setBlock(7,4,7,Blocks.WATER);h.assertTrue(!BlueprintSpawns.batHabitat(h.getLevel(),p),"Submerged pocket rejected");h.setBlock(7,4,7,Blocks.AIR);
        for(int i=0;i<3;i++){var b=h.spawn(BlueprintEntities.YOUDENG_GUIMIANFU.get(),new BlockPos(7+i,6,7));b.setNoAi(true);}
        h.assertTrue(!BlueprintSpawns.batHabitat(h.getLevel(),p),"Three loaded bats cap local population");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="lantern_bat")
    public static void actualAnimationParserLoadsAllFlightAndDeathClips(GameTestHelper h)throws Exception{
        var gson=new com.google.gson.GsonBuilder().registerTypeAdapter(software.bernie.geckolib.loading.object.BakedAnimations.class,new software.bernie.geckolib.loading.json.typeadapter.BakedAnimationsAdapter()).create();
        try(var in=LanternBatGameTests.class.getResourceAsStream("/assets/dynasty/animations/blueprint/youdeng_guimianfu.animation.json")){
            var json=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(in)).getAsJsonObject();var clips=gson.fromJson(json.get("animations"),software.bernie.geckolib.loading.object.BakedAnimations.class);
            for(var n:java.util.List.of("idle","walk","run","attack","glare","hurt","death"))h.assertTrue(clips.getAnimation("animation.youdeng_guimianfu."+n).boneAnimations().length>0,"Parses "+n);
            h.assertTrue(clips.getAnimation("animation.youdeng_guimianfu.attack").length()==60,"Flight animation matches authoritative action clock");
        }h.succeed();
    }
}
