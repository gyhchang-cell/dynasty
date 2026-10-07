package com.dynasty.blueprint;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.*;
@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class YechaGameTests {
    private static TemplateMob yecha(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=14;y++)h.setBlock(x,y,z,y==1||y==14||x==0||x==15||z==0||z==15?Blocks.STONE:Blocks.AIR);
        return h.spawn(BlueprintEntities.TONGBI_FEITIAN_YECHA.get(),new BlockPos(7,6,5));
    }
    private static net.minecraft.world.entity.animal.Cow cow(GameTestHelper h){var c=h.spawn(EntityType.COW,new BlockPos(7,2,10));c.setNoAi(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);c.setHealth(200);c.getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(0);return c;}
    @GameTest(template="bow_ritual_test",timeoutTicks=130,batch="yecha")
    public static void physicalGrabHasWarningHeightTimeLimitAndFallProtection(GameTestHelper h){
        var mob=yecha(h);var target=cow(h);target.setNoAi(false);var base=target.getY();h.assertTrue(mob.startSkill(ArmySkills.YECHA_GRAB,target),"Starts locked approach");
        h.runAfterDelay(18,()->h.assertTrue(target.getHealth()==200&&!target.hasEffect(MobEffects.SLOW_FALLING),"Windup no contact"));
        h.onEachTick(()->h.assertTrue(target.getY()<=base+6.2,"Hard six block lifting limit"));
        h.startSequence().thenWaitUntil(()->h.assertTrue(mob.hookTargetId()==target.getId(),"Actual body reaches and captures victim"))
            .thenExecute(()->h.assertTrue(target.hasEffect(MobEffects.SLOW_FALLING)&&!target.isPassenger(),"Independent protection, no forced riding"))
            .thenIdle(45).thenExecute(()->h.assertTrue(mob.hookTargetId()<0&&target.hasEffect(MobEffects.SLOW_FALLING)&&target.getHealth()>=190,"Capture time bounded and release protected")).thenSucceed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="yecha")
    public static void crouchEscapesAndReadSaveNeverResumesCaptive(GameTestHelper h){
        var mob=yecha(h);var target=cow(h);mob.startSkill(ArmySkills.YECHA_GRAB,target);
        h.startSequence().thenWaitUntil(()->h.assertTrue(mob.hookTargetId()==target.getId(),"Capture reached"))
            .thenExecute(()->target.setShiftKeyDown(true)).thenIdle(3).thenExecute(()->{
                h.assertTrue(mob.hookTargetId()<0&&target.hasEffect(MobEffects.SLOW_FALLING),"Crouch immediately releases with safety");
                var tag=new CompoundTag();mob.save(tag);mob.discard();var copy=BlueprintEntities.TONGBI_FEITIAN_YECHA.get().create(h.getLevel());copy.load(tag);h.getLevel().addFreshEntity(copy);
                h.assertTrue(copy.hookTargetId()<0&&!copy.startSkill(ArmySkills.YECHA_GRAB,target),"Reload retains cooldown without restoring forced movement");
            }).thenSucceed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="yecha")
    public static void teammateDamageBreaksCaptureWithoutRemovingSafety(GameTestHelper h){
        var mob=yecha(h);var target=cow(h);mob.startSkill(ArmySkills.YECHA_GRAB,target);
        h.startSequence().thenWaitUntil(()->h.assertTrue(mob.hookTargetId()==target.getId(),"Capture reached"))
            .thenExecute(()->mob.hurt(mob.damageSources().mobAttack(target),8)).thenIdle(3)
            .thenExecute(()->h.assertTrue(mob.hookTargetId()<0&&target.hasEffect(MobEffects.SLOW_FALLING),"Rescue damage interrupts and preserves fall safety")).thenSucceed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60,batch="yecha")
    public static void lateWallStopsDiveBeforeAnyRemoteGrab(GameTestHelper h){
        var mob=yecha(h);var target=cow(h);mob.startSkill(ArmySkills.YECHA_GRAB,target);
        h.runAfterDelay(16,()->{for(int x=4;x<11;x++)for(int y=2;y<12;y++)h.setBlock(x,y,7,Blocks.STONE);});
        h.runAfterDelay(43,()->{h.assertTrue(target.getHealth()==200&&mob.hookTargetId()<0&&!mob.noPhysics,"Wall blocks the actual grab");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="yecha")
    public static void nativeFiveJointArmAndWingClipsLoad(GameTestHelper h)throws Exception{
        var gson=new com.google.gson.GsonBuilder().registerTypeAdapter(software.bernie.geckolib.loading.object.BakedAnimations.class,new software.bernie.geckolib.loading.json.typeadapter.BakedAnimationsAdapter()).create();
        try(var in=YechaGameTests.class.getResourceAsStream("/assets/dynasty/animations/blueprint/tongbi_feitian_yecha.animation.json")){
            var json=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(in)).getAsJsonObject();var clips=gson.fromJson(json.get("animations"),software.bernie.geckolib.loading.object.BakedAnimations.class);
            for(var n:java.util.List.of("idle","walk","run","attack","grab","hurt","death"))h.assertTrue(clips.getAnimation("animation.tongbi_feitian_yecha."+n).boneAnimations().length>0,"Parses "+n);
        }h.succeed();
    }
}
