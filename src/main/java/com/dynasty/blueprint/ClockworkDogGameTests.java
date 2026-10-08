package com.dynasty.blueprint;

import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class ClockworkDogGameTests {
    private static TemplateMob dog(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=7;y++)h.setBlock(x,y,z,y==1?Blocks.STONE:Blocks.AIR);
        var mob=h.spawn(BlueprintEntities.XUNSHAN_MUJIAQUAN.get(),new BlockPos(7,2,5));mob.setNoAi(true);mob.bindEncounter("dynasty:tiangong_citadel@42:dogs");return mob;
    }
    private static net.minecraft.world.entity.animal.Cow enemy(GameTestHelper h,int x,int z){
        var e=h.spawn(EntityType.COW,new BlockPos(x,2,z));e.setNoAi(true);e.setNoGravity(true);e.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);e.setHealth(200);return e;
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=35,batch="clockwork")
    public static void shearJawHasSingleEightTickContact(GameTestHelper h){
        var mob=dog(h);var e=enemy(h,7,7);h.assertTrue(mob.startSkill(ArmySkills.DOG_BITE,e),"Starts shear bite");
        h.runAfterDelay(6,()->h.assertTrue(e.getHealth()==200,"No windup damage"));
        h.runAfterDelay(25,()->{h.assertTrue(e.getHealth()==195,"One contact only");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40,batch="clockwork")
    public static void alarmUsesSameStructureIdentityWithoutWakingOtherSitesOrNoAi(GameTestHelper h){
        var mob=dog(h);var e=enemy(h,7,12);
        var ally=h.spawn(BlueprintEntities.ZUWU_DAOSHOU.get(),new BlockPos(5,2,5));ally.bindEncounter("dynasty:tiangong_citadel@42:army");
        var other=h.spawn(BlueprintEntities.ZUWU_DAOSHOU.get(),new BlockPos(10,2,5));other.bindEncounter("dynasty:tiangong_citadel@43:army");
        var frozen=h.spawn(BlueprintEntities.JUBI_SHIGANDANG.get(),new BlockPos(4,2,8));frozen.bindEncounter("dynasty:tiangong_citadel@42:stone_guard");frozen.setNoAi(true);
        h.assertTrue(com.dynasty.blueprint.combat.Combatant.allied(mob,ally),"Same-site constructs and soldiers are allies");
        h.assertTrue(!com.dynasty.blueprint.combat.Combatant.allied(mob,other),"Different site is not silently added to alliance");
        h.assertTrue(mob.startSkill(ArmySkills.DOG_ALARM,e),"Starts real alarm");
        h.runAfterDelay(18,()->h.assertTrue(ally.getTarget()==null,"Windup has not broadcast yet"));
        h.runAfterDelay(23,()->{h.assertTrue(ally.getTarget()==e&&other.getTarget()==null&&frozen.getTarget()==null&&frozen.isNoAi(),"Only eligible local encounter members acquire target");
            h.assertTrue(mob.hasEffect(MobEffects.MOVEMENT_SPEED),"Alarm grants finite speed boost");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40,batch="clockwork")
    public static void interruptedAlarmDoesNotBroadcastAndRetainsCooldown(GameTestHelper h){
        var mob=dog(h);var e=enemy(h,7,10);mob.startSkill(ArmySkills.DOG_ALARM,e);
        h.runAfterDelay(10,()->mob.hurt(mob.damageSources().mobAttack(e),15));
        h.runAfterDelay(27,()->{h.assertTrue(!mob.hasEffect(MobEffects.MOVEMENT_SPEED)&&!mob.startSkill(ArmySkills.DOG_ALARM,e),"Stagger stops warning and does not reset cooldown");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=25,batch="clockwork")
    public static void mechanicalImmunityAndPatrolHomeSurviveRealNbtReload(GameTestHelper h){
        var mob=dog(h);var home=mob.getRestrictCenter();
        h.assertTrue(!mob.addEffect(new MobEffectInstance(MobEffects.POISON,100))&&!mob.addEffect(new MobEffectInstance(com.dynasty.DynastyEffects.INTERNAL_INJURY.get(),100)),"Wood and gears do not bleed or become poisoned");
        h.assertTrue(mob.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,100)),"Mechanical immunity does not erase unrelated debuffs");
        var saved=new CompoundTag();mob.save(saved);mob.discard();var copy=BlueprintEntities.XUNSHAN_MUJIAQUAN.get().create(h.getLevel());copy.load(saved);h.getLevel().addFreshEntity(copy);
        h.assertTrue(copy.encounterSite().equals("dynasty:tiangong_citadel@42")&&copy.getRestrictCenter().equals(home)&&copy.hasRestriction(),"Site and patrol origin persist");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=150,batch="clockwork_patrol")
    public static void idleHoundActuallyPatrolsWithoutLeavingHomeRadius(GameTestHelper h){
        var mob=dog(h);mob.setNoAi(false);var home=mob.position();boolean[] moved={false};
        h.onEachTick(()->{if(mob.position().distanceToSqr(home)>1)moved[0]=true;h.assertTrue(mob.position().distanceToSqr(home)<145,"Patrol remains near authored home");});
        h.runAfterDelay(130,()->{h.assertTrue(moved[0],"Native navigation moves idle hound around home");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="clockwork")
    public static void rigAndAlarmClipsLoadThroughActualGeckoParser(GameTestHelper h) throws Exception {
        var gson=new com.google.gson.GsonBuilder().registerTypeAdapter(software.bernie.geckolib.loading.object.BakedAnimations.class,new software.bernie.geckolib.loading.json.typeadapter.BakedAnimationsAdapter()).create();
        try(var stream=ClockworkDogGameTests.class.getResourceAsStream("/assets/dynasty/animations/blueprint/xunshan_mujiaquan.animation.json")){
            var json=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(stream,java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject();
            var clips=gson.fromJson(json.getAsJsonObject("animations"),software.bernie.geckolib.loading.object.BakedAnimations.class);
            for(var name:java.util.List.of("idle","walk","run","attack","alarm","hurt","death"))h.assertTrue(clips.getAnimation("animation.xunshan_mujiaquan."+name).boneAnimations().length>0,"Parsed "+name);
            h.assertTrue(clips.getAnimation("animation.xunshan_mujiaquan.alarm").length()==40,"Alarm matches authoritative action clock");
        }h.succeed();
    }
}
