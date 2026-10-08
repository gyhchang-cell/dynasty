package com.dynasty.blueprint;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class DrownerGameTests {
    private static TemplateMob ghost(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=8;y++)h.setBlock(x,y,z,y==1||y==8||x==0||x==15||z==0||z==15?Blocks.STONE:y<=4?Blocks.WATER:Blocks.AIR);
        var mob=h.spawn(BlueprintEntities.SHASHUI_FUNIGUI.get(),new BlockPos(7,3,7));mob.setNoAi(true);mob.setNoGravity(true);return mob;
    }
    private static net.minecraft.world.entity.animal.Cow cow(GameTestHelper h){var c=h.spawn(EntityType.COW,new BlockPos(8,3,7));c.setNoAi(true);c.setNoGravity(true);return c;}
    @GameTest(template="bow_ritual_test",timeoutTicks=90,batch="drowner")
    public static void poolUsesSameEntityMatchesHitboxAndLetsVictimSwimOut(GameTestHelper h){
        var mob=ghost(h);h.assertTrue(mob.checkSpawnObstruction(h.getLevel()),"Vanilla final obstruction check permits water spawn");var victim=cow(h);var uuid=mob.getUUID();
        h.runAfterDelay(3,()->h.assertTrue(mob.startSkill(ArmySkills.DROWNER_POOL,victim),"Actual deep water permits cast"));
        h.runAfterDelay(24,()->h.assertTrue(!victim.hasEffect(BlueprintEntities.DROWNING_BIND.get())&&!mob.waterPool(),"Full tell remains escapable"));
        h.runAfterDelay(35,()->{
            h.assertTrue(mob.waterPool()&&mob.getUUID().equals(uuid)&&mob.getBbHeight()<.4&&mob.getBbWidth()>3.5,"Same identity, real shallow4x4hitbox");
            h.assertTrue(victim.hasEffect(BlueprintEntities.DROWNING_BIND.get())&&mob.canBreatheUnderwater(),"Water bind and native water breathing");
            victim.setPos(victim.getX()+5,victim.getY(),victim.getZ());
        });
        h.runAfterDelay(52,()->{h.assertTrue(!victim.hasEffect(BlueprintEntities.DROWNING_BIND.get())&&!mob.waterPool()&&mob.getBbHeight()>1.8,"Lateral escape ends bind and restores body");h.assertBlockPresent(Blocks.WATER,new BlockPos(7,3,7));h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=70,batch="drowner")
    public static void removingWaterInterruptsAndDryLandCannotStart(GameTestHelper h){
        var mob=ghost(h);var victim=cow(h);
        h.runAfterDelay(3,()->mob.startSkill(ArmySkills.DROWNER_POOL,victim));
        h.runAfterDelay(18,()->{for(int x=4;x<=10;x++)for(int z=4;z<=10;z++)for(int y=2;y<=4;y++)h.setBlock(x,y,z,Blocks.STONE);mob.setPos(mob.getX(),h.absolutePos(new BlockPos(7,5,7)).getY(),mob.getZ());});
        h.runAfterDelay(40,()->{h.assertTrue(!mob.waterPool()&&!victim.hasEffect(BlueprintEntities.DROWNING_BIND.get())&&!mob.startSkill(ArmySkills.DROWNER_WHIP,victim),"Lost water interrupts and forbids land attacks");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=125,batch="drowner")
    public static void readSaveDoesNotExtendPoolWindow(GameTestHelper h){
        var mob=ghost(h);var victim=cow(h);
        h.runAfterDelay(3,()->mob.startSkill(ArmySkills.DROWNER_POOL,victim));
        h.runAfterDelay(40,()->{var tag=new CompoundTag();mob.save(tag);mob.discard();var restored=BlueprintEntities.SHASHUI_FUNIGUI.get().create(h.getLevel());restored.load(tag);h.getLevel().addFreshEntity(restored);
            h.runAfterDelay(60,()->{h.assertTrue(!restored.waterPool()&&!victim.hasEffect(BlueprintEntities.DROWNING_BIND.get()),"Original absolute attack clock expires after reload");h.succeed();});});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30,batch="drowner")
    public static void waterBindCapsUpwardVelocityButRetainsHorizontalEscape(GameTestHelper h){
        ghost(h);var victim=cow(h);
        h.runAfterDelay(3,()->{victim.setDeltaMovement(.2,.4,.1);new DrowningBindEffect().applyEffectTick(victim,0);h.assertTrue(victim.getDeltaMovement().y==0&&victim.getDeltaMovement().x==.2&&victim.getDeltaMovement().z==.1,"Only upward swim is capped");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="drowner")
    public static void softBodyAndWaterClipsLoadThroughGecko(GameTestHelper h)throws Exception{
        var gson=new com.google.gson.GsonBuilder().registerTypeAdapter(software.bernie.geckolib.loading.object.BakedAnimations.class,new software.bernie.geckolib.loading.json.typeadapter.BakedAnimationsAdapter()).create();
        try(var in=DrownerGameTests.class.getResourceAsStream("/assets/dynasty/animations/blueprint/shashui_funigui.animation.json")){
            var json=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(in)).getAsJsonObject();var clips=gson.fromJson(json.get("animations"),software.bernie.geckolib.loading.object.BakedAnimations.class);
            for(var n:java.util.List.of("idle","walk","run","attack","pool","hurt","death"))h.assertTrue(clips.getAnimation("animation.shashui_funigui."+n).boneAnimations().length>0,"Parses "+n);
            h.assertTrue(clips.getAnimation("animation.shashui_funigui.pool").length()==104,"Water form matches authoritative104tick lifecycle");
        }h.succeed();
    }
}
