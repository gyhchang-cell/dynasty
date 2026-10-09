package com.dynasty.blueprint;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class BlindFishGameTests {
    private static TemplateMob fish(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=11;y++)h.setBlock(x,y,z,y==1||y==11||x==0||x==15||z==0||z==15?Blocks.STONE:Blocks.AIR);
        var mob=h.spawn(BlueprintEntities.XUEJU_MANGGUYU.get(),new BlockPos(7,4,5));mob.setNoAi(true);return mob;
    }
    private static net.minecraft.world.entity.animal.Cow target(GameTestHelper h){
        var c=h.spawn(EntityType.COW,new BlockPos(7,2,9));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);c.setHealth(200);return c;
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=115,batch="blind_fish")
    public static void threeWhirlsPullGentlyThenExpireAcrossReload(GameTestHelper h){
        var mob=fish(h);var victim=target(h);h.assertTrue(mob.startSkill(ArmySkills.FISH_RESONANCE,victim),"Starts30tick tell");
        h.runAfterDelay(28,()->h.assertTrue(victim.getDeltaMovement().horizontalDistanceSqr()==0,"No premature pull"));
        h.runAfterDelay(38,()->{
            var tag=new CompoundTag();mob.save(tag);var state=tag.getCompound("ArmyActionState");
            h.assertTrue(state.getList("Whirls",10).size()==3,"Exactly three finite centres");
            h.assertTrue(victim.getDeltaMovement().horizontalDistance()>0&&victim.getDeltaMovement().horizontalDistance()<.2&&victim.getHealth()==200,"Bounded horizontal velocity only");
            mob.discard();var copy=BlueprintEntities.XUEJU_MANGGUYU.get().create(h.getLevel());copy.load(tag);h.getLevel().addFreshEntity(copy);
            h.runAfterDelay(62,()->{victim.setDeltaMovement(Vec3.ZERO);h.runAfterDelay(6,()->{
                var saved=new CompoundTag();copy.save(saved);h.assertTrue(saved.getCompound("ArmyActionState").getList("Whirls",10).isEmpty()&&victim.getDeltaMovement().equals(Vec3.ZERO),"Reload cannot refresh expired whirl lifetime");h.succeed();});});
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=70,batch="blind_fish")
    public static void wallAndDeathCancelPullWithoutInputOrTeleportChanges(GameTestHelper h){
        var mob=fish(h);var victim=target(h);mob.startSkill(ArmySkills.FISH_RESONANCE,victim);
        h.runAfterDelay(34,()->{for(int x=3;x<=11;x++)for(int y=2;y<=9;y++)h.setBlock(x,y,7,Blocks.STONE);victim.setDeltaMovement(Vec3.ZERO);});
        h.runAfterDelay(44,()->{h.assertTrue(victim.getDeltaMovement().equals(Vec3.ZERO),"New wall blocks pull");mob.hurt(mob.damageSources().genericKill(),10000);});
        h.runAfterDelay(49,()->{var tag=new CompoundTag();mob.save(tag);h.assertTrue(tag.getCompound("ArmyActionState").getList("Whirls",10).isEmpty(),"Owner death clears zones");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=55,batch="blind_fish")
    public static void tailContactsOnceAfterTell(GameTestHelper h){
        var mob=fish(h);var victim=target(h);mob.setPos(victim.getX(),victim.getY()+.2,victim.getZ()-2);mob.startSkill(ArmySkills.FISH_TAIL,victim);
        h.runAfterDelay(14,()->h.assertTrue(victim.getHealth()==200,"Windup harmless"));h.runAfterDelay(42,()->{h.assertTrue(victim.getHealth()==194,"One actual tail contact");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=110,batch="blind_fish",setupTicks=20)
    public static void realFlightMovesWithoutCrossingSolidWalls(GameTestHelper h){
        var mob=fish(h);var victim=target(h);mob.setNoAi(false);mob.setTarget(victim);var start=mob.position();boolean[] wall={false};
        // Wait for native navigation/entity ticking, then retain the same 23-tick
        // collision probe. Do not manufacture movement or bypass the flight AI.
        h.startSequence().thenWaitUntil(()->h.assertTrue(mob.position().distanceToSqr(start)>.05,"Actual flight moves before wall; pos="+mob.position()+", target="+mob.getTarget()+", skill="+mob.skillId()))
        .thenExecute(()->{for(int x=1;x<15;x++)for(int y=2;y<11;y++)h.setBlock(x,y,7,Blocks.STONE);wall[0]=true;})
        .thenIdle(23).thenExecute(()->{try{h.assertTrue(!mob.noPhysics&&mob.getZ()<h.absolutePos(new BlockPos(7,2,7)).getZ(),"Physical flight cannot cross a newly placed wall");h.succeed();}finally{mob.discard();victim.discard();}});
        h.onEachTick(()->{if(wall[0])mob.setDeltaMovement(0,0,.3);});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="blind_fish")
    public static void eightSpineClipsAndDeepCaveHabitatAreReal(GameTestHelper h)throws Exception{
        var mob=fish(h);mob.discard();h.assertTrue(BlueprintSpawns.fishHabitat(h.getLevel(),h.absolutePos(new BlockPos(7,4,7))),"Actual deep cave accepted");
        var gson=new com.google.gson.GsonBuilder().registerTypeAdapter(software.bernie.geckolib.loading.object.BakedAnimations.class,new software.bernie.geckolib.loading.json.typeadapter.BakedAnimationsAdapter()).create();
        try(var in=BlindFishGameTests.class.getResourceAsStream("/assets/dynasty/animations/blueprint/xueju_mangguyu.animation.json")){
            var json=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(in)).getAsJsonObject();var clips=gson.fromJson(json.get("animations"),software.bernie.geckolib.loading.object.BakedAnimations.class);
            for(var n:java.util.List.of("idle","walk","run","attack","resonance","hurt","death"))h.assertTrue(clips.getAnimation("animation.xueju_mangguyu."+n).boneAnimations().length>0,"Parses "+n);
        }h.succeed();
    }
}
