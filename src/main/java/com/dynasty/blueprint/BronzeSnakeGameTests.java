package com.dynasty.blueprint;

import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class BronzeSnakeGameTests {
    private static TemplateMob snake(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=8;y++)h.setBlock(x,y,z,y==1?Blocks.STONE:Blocks.AIR);
        var mob=h.spawn(BlueprintEntities.QINGTONG_SHUANGTOUSHEKUI.get(),new BlockPos(7,2,7));mob.setNoAi(true);mob.setNoGravity(true);mob.setYRot(0);mob.yBodyRot=0;return mob;
    }
    private static net.minecraft.world.entity.animal.Cow enemy(GameTestHelper h,int z){
        var e=h.spawn(EntityType.COW,new BlockPos(7,2,z));e.setNoAi(true);e.setNoGravity(true);e.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);e.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);e.setHealth(200);return e;
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40,batch="bronze_snake")
    public static void rearHeadStrikesBehindWithoutSpinningTheBody(GameTestHelper h){
        var mob=snake(h);var rear=enemy(h,5);var front=enemy(h,9);
        h.assertTrue(mob.startSkill(ArmySkills.BRONZE_REAR_STAB,rear),"Starts independent rear head");
        h.runAfterDelay(8,()->h.assertTrue(rear.getHealth()==200,"Ten tick warning before rear stab"));
        h.runAfterDelay(16,()->h.assertTrue(Math.abs(net.minecraft.util.Mth.wrapDegrees(mob.yBodyRot))<1,"Body remains oriented forward while rear head attacks"));
        h.runAfterDelay(29,()->{h.assertTrue(rear.getHealth()==194&&front.getHealth()==200,"One rear contact, no opposite-head phantom hit");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=150,batch="bronze_fire")
    public static void fireBreathIsTelegraphedBoundedAndStopsAfterThreeSeconds(GameTestHelper h){
        var mob=snake(h);var front=enemy(h,11);var rear=enemy(h,3);var ally=h.spawn(BlueprintEntities.XUNSHAN_MUJIAQUAN.get(),new BlockPos(7,2,10));ally.setNoAi(true);float allyHp=ally.getHealth();
        h.startSequence().thenWaitUntil(()->h.assertTrue(mob.tickCount>=2&&front.tickCount>=2&&h.getLevel().getEntity(front.getUUID())==front,"Real caster and damage targets visible and ticking before breath"))
        .thenExecute(()->{
            h.assertTrue(mob.startSkill(ArmySkills.BRONZE_FIRE,front),"Starts fire cone");
            h.runAfterDelay(16,()->h.assertTrue(front.getHealth()==200&&!front.isOnFire(),"No hidden early fire"));
            h.runAfterDelay(22,()->h.assertTrue(front.getHealth()<200&&front.isOnFire()&&rear.getHealth()==200&&ally.getHealth()==allyHp,"Only enemies in forward cone burn"));
        })
        .thenWaitUntil(()->h.assertTrue(mob.attack().state(h.getLevel().getGameTime())==com.dynasty.blueprint.combat.AttackState.RECOVERY,"Actual original breath enters recovery after18+60 native ticks"))
        .thenExecute(()->{front.clearFire();float hp=front.getHealth();h.runAfterDelay(20,()->{
            try{var damage=front.getLastDamageSource();h.assertTrue(front.getHealth()==hp,"No breath damage in recovery: before="+hp+", after="+front.getHealth()+", skill="+mob.skillId()+", age="+mob.actionAge(0)+", fire="+front.getRemainingFireTicks()+", source="+(damage==null?"none":damage.getMsgId())+", direct="+(damage==null?null:damage.getDirectEntity()));h.succeed();}
            finally{mob.discard();front.discard();rear.discard();ally.discard();}
        });});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60,batch="bronze_snake")
    public static void wallAndSharedReloadCooldownPreventBreathExploits(GameTestHelper h){
        var mob=snake(h);var e=enemy(h,11);mob.startSkill(ArmySkills.BRONZE_POISON,e);
        h.runAfterDelay(14,()->{for(int x=5;x<=9;x++)for(int y=2;y<=5;y++)h.setBlock(x,y,9,Blocks.STONE);});
        h.runAfterDelay(35,()->{
            h.assertTrue(e.getHealth()==200&&!e.hasEffect(net.minecraft.world.effect.MobEffects.POISON),"New wall blocks every poison pulse");
            mob.interruptAttack(1);var tag=new CompoundTag();mob.save(tag);mob.discard();var restored=BlueprintEntities.QINGTONG_SHUANGTOUSHEKUI.get().create(h.getLevel());restored.load(tag);h.getLevel().addFreshEntity(restored);
            h.runAfterDelay(4,()->{for(int x=5;x<=9;x++)for(int y=2;y<=5;y++)h.setBlock(x,y,9,Blocks.AIR);
                h.assertTrue(!restored.startSkill(ArmySkills.BRONZE_FIRE,e),"Swapping heads and reloading cannot bypass common breath cooldown");h.succeed();});
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=45,batch="bronze_snake")
    public static void realIronBarCollisionPermitsClimbAndStoneDoesNot(GameTestHelper h){
        var mob=snake(h);mob.setNoAi(false);mob.setPos(mob.getX(),mob.getY(),mob.getZ()+.25);var target=enemy(h,9);target.setPos(target.getX(),target.getY()+4,target.getZ());mob.setTarget(target);var start=mob.getY();
        for(int y=2;y<=7;y++)h.setBlock(7,y,8,Blocks.IRON_BARS);
        h.onEachTick(()->{if(h.getTick()<18){var v=mob.getDeltaMovement();mob.setDeltaMovement(v.x,v.y,.2);}});
        h.runAfterDelay(16,()->h.assertTrue(mob.getY()>start+.4&&mob.onClimbable()&&!mob.noPhysics,"Actual iron-bar contact gives bounded ascent: y="+mob.getY()));
        h.runAfterDelay(18,()->{for(int y=2;y<=7;y++)h.setBlock(7,y,8,Blocks.STONE);});
        h.runAfterDelay(24,()->{h.assertTrue(!mob.onClimbable(),"Stone replacement removes bar-only climbing state");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="bronze_snake")
    public static void twinHeadRigAndThreeSecondClipsLoadThroughGeckoLib(GameTestHelper h) throws Exception {
        var gson=new com.google.gson.GsonBuilder().registerTypeAdapter(software.bernie.geckolib.loading.object.BakedAnimations.class,new software.bernie.geckolib.loading.json.typeadapter.BakedAnimationsAdapter()).create();
        try(var stream=BronzeSnakeGameTests.class.getResourceAsStream("/assets/dynasty/animations/blueprint/qingtong_shuangtoushekui.animation.json")){
            var json=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(stream,java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject();
            var clips=gson.fromJson(json.getAsJsonObject("animations"),software.bernie.geckolib.loading.object.BakedAnimations.class);
            for(var name:java.util.List.of("idle","walk","run","climb","attack","rear_attack","fire","poison","hurt","death"))h.assertTrue(clips.getAnimation("animation.qingtong_shuangtoushekui."+name).boneAnimations().length>0,"Parsed "+name);
            h.assertTrue(clips.getAnimation("animation.qingtong_shuangtoushekui.fire").length()==102,"18 tell +60 active +24 recovery");
        }h.succeed();
    }
}
