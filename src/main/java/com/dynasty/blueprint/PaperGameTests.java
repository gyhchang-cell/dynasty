package com.dynasty.blueprint;

import java.util.List;
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
public final class PaperGameTests {
    private static TemplateMob paper(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=8;y++)h.setBlock(x,y,z,y==1||y==8?Blocks.STONE:Blocks.AIR);
        var mob=h.spawn(BlueprintEntities.ZHIREN_JIANKE.get(),new BlockPos(7,2,10));mob.setNoAi(true);return mob;
    }
    private static net.minecraft.world.entity.animal.Cow enemy(GameTestHelper h){
        var cow=h.spawn(EntityType.COW,new BlockPos(7,2,8));cow.setNoAi(true);cow.setYRot(0);cow.setXRot(0);cow.setNoGravity(true);
        cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);cow.setHealth(200);return cow;
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30,batch="paper")
    public static void finalDamageRescuesOnceAndReloadCannotRepeatIt(GameTestHelper h){
        var mob=paper(h);var cow=enemy(h);var initial=mob.position();
        h.assertTrue(!mob.startSkill(ArmySkills.PAPER_SHED,cow),"Re-form cannot be manually started to bypass substitution gates");
        // Neighboring native structure tests can already contain dropped items. Compare the
        // same real region before/after rescue, including entity identities, instead of global emptiness.
        var region=cow.getBoundingBox().inflate(15);
        var itemsBefore=h.getLevel().getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,region).stream().map(Entity::getUUID).collect(java.util.stream.Collectors.toSet());
        var papersBefore=h.getLevel().getEntitiesOfClass(TemplateMob.class,region).stream().map(Entity::getUUID).collect(java.util.stream.Collectors.toSet());
        mob.interruptAttack(30);
        h.assertTrue(mob.hurt(mob.damageSources().mobAttack(cow),100),"Real fatal attack enters normal damage pipeline");
        h.assertTrue(mob.isAlive()&&mob.getHealth()==1&&mob.skillId()==ArmySkills.PAPER_SHED,"Fatal hit leaves1HP and starts synchronized re-form action");
        h.assertTrue(Math.abs(mob.distanceTo(cow)-5)<.05&&mob.getZ()<cow.getZ(),"Safe real position is five blocks behind attacker's facing");
        h.assertTrue(mob.position().distanceTo(initial)>5&&h.getLevel().noCollision(mob),"Escape moves the same entity into free space");
        var itemsAfter=h.getLevel().getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,region).stream().map(Entity::getUUID).collect(java.util.stream.Collectors.toSet());
        var papersAfter=h.getLevel().getEntitiesOfClass(TemplateMob.class,region).stream().map(Entity::getUUID).collect(java.util.stream.Collectors.toSet());
        h.assertTrue(itemsAfter.equals(itemsBefore)&&papersAfter.equals(papersBefore),"Native rescue creates no corpse loot or attackable decoy entity and preserves neighboring pre-existing identities: before="+itemsBefore+", after="+itemsAfter);
        var tag=new CompoundTag();mob.save(tag);mob.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
        var copy=BlueprintEntities.ZHIREN_JIANKE.get().create(h.getLevel());copy.load(tag);h.getLevel().addFreshEntity(copy);copy.invulnerableTime=0;
        copy.hurt(copy.damageSources().mobAttack(cow),100);
        h.assertTrue(copy.isDeadOrDying(),"Reload retains the long cooldown and next fatal hit kills normally");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30,batch="paper")
    public static void armourAndAbsorptionAreAppliedBeforeFatalDecision(GameTestHelper h){
        var mob=paper(h);var cow=enemy(h);var at=mob.position();mob.getAttribute(Attributes.ARMOR).setBaseValue(100);mob.setAbsorptionAmount(20);
        mob.hurt(mob.damageSources().mobAttack(cow),40);
        h.assertTrue(mob.isAlive()&&mob.position().equals(at)&&mob.skillId()==0,"Raw40 damage is absorbed after armour; it must not consume substitution");
        mob.getAttribute(Attributes.ARMOR).setBaseValue(0);mob.setAbsorptionAmount(0);mob.invulnerableTime=0;mob.hurt(mob.damageSources().mobAttack(cow),100);
        h.assertTrue(mob.isAlive()&&mob.getHealth()==1&&!mob.position().equals(at),"First genuinely fatal final damage still rescues");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30,batch="paper")
    public static void blockedRearFallsBackToDiagonalButNeverUsesSolidOrWetSpace(GameTestHelper h){
        var mob=paper(h);var cow=enemy(h);
        for(int y=2;y<=5;y++)h.setBlock(7,y,3,Blocks.STONE);
        var diagonal=ArmyBehaviors.paperLanding(mob,cow);
        h.assertTrue(diagonal!=null&&Math.abs(diagonal.x-cow.getX())>3,"Blocked direct rear chooses a safe rear diagonal");
        for(int x=1;x<=13;x++)for(int z=1;z<=6;z++)for(int y=2;y<=5;y++)h.setBlock(x,y,z,Blocks.WATER);
        h.assertTrue(ArmyBehaviors.paperLanding(mob,cow)==null,"Water-filled candidates cannot be used as standing escape points");
        for(int x=1;x<=13;x++)for(int z=1;z<=6;z++)for(int y=2;y<=5;y++)h.setBlock(x,y,z,Blocks.STONE);
        h.assertTrue(ArmyBehaviors.paperLanding(mob,cow)==null,"Fully blocked rear search returns no unsafe candidate");
        var at=mob.position();mob.hurt(mob.damageSources().mobAttack(cow),100);
        h.assertTrue(mob.isDeadOrDying()&&mob.position().equals(at),"No legal landing means normal death, not noclip or repeated immunity");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=90,batch="paper")
    public static void paperCutHasOneContactAndFiniteBleeding(GameTestHelper h){
        var mob=paper(h);var cow=enemy(h);var side=h.spawn(EntityType.COW,new BlockPos(10,2,10));side.setNoAi(true);
        h.assertTrue(mob.startSkill(ArmySkills.PAPER_SLASH,cow),"Real paper slash starts");
        h.runAfterDelay(4,()->h.assertTrue(cow.getHealth()==200,"Six-tick tell has no early damage"));
        h.runAfterDelay(9,()->h.assertTrue(cow.getHealth()==195&&cow.hasEffect(net.minecraft.world.effect.MobEffects.WITHER)&&side.getHealth()==10,"One frontal cut deals5 and applies finite bleeding; flank is outside sector"));
        h.runAfterDelay(78,()->{h.assertTrue(cow.getHealth()<195&&!cow.hasEffect(net.minecraft.world.effect.MobEffects.WITHER)&&mob.skillId()==0,"Bleeding deals actual delayed damage, then both effect and action expire");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=180,batch="paper")
    public static void autonomousZigzagUsesNavigationAndReachesVictim(GameTestHelper h){
        var mob=paper(h);var cow=enemy(h);mob.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(7,2,2))));cow.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(7,2,13))));
        var at=mob.position();mob.setNoAi(false);mob.setTarget(cow);boolean[] zigzag={false};
        h.onEachTick(()->{if(Math.abs(mob.getX()-at.x)>.45&&mob.isSprinting())zigzag[0]=true;});
        h.runAfterDelay(145,()->{h.assertTrue(zigzag[0]&&cow.getHealth()<200&&!mob.noPhysics&&!mob.isNoGravity(),"Actual AI must move laterally, approach and cut using normal collision; lateral="+zigzag[0]+" hp="+cow.getHealth());cow.discard();mob.setTarget(null);
            h.runAfterDelay(2,()->{h.assertTrue(!mob.isSprinting(),"Lost target clears run flag");h.succeed();});});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="paper")
    public static void operatorKillCannotBeInterceptedAndDeathIsHalfSecond(GameTestHelper h){
        var mob=paper(h);mob.setTarget(enemy(h));mob.hurt(mob.damageSources().genericKill(),10000);
        h.assertTrue(mob.isDeadOrDying(),"Bypass-invulnerability kill is never substituted");
        h.runAfterDelay(12,()->{h.assertTrue(mob.isRemoved(),"Paper death completes in ten ticks");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="paper")
    public static void shippedPaperAnimationsLoadWithNativeSteppedJoints(GameTestHelper h) throws Exception {
        var gson=new com.google.gson.GsonBuilder().registerTypeAdapter(software.bernie.geckolib.loading.object.BakedAnimations.class,
            new software.bernie.geckolib.loading.json.typeadapter.BakedAnimationsAdapter()).create();
        try(var stream=PaperGameTests.class.getResourceAsStream("/assets/dynasty/animations/blueprint/zhiren_jianke.animation.json")){
            h.assertTrue(stream!=null,"Shipped animation is on runtime resource path");
            var resource=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(stream,java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject();
            // GeckoLib's resource loader passes only the animations object to its adapter.
            var baked=gson.fromJson(resource.getAsJsonObject("animations"),software.bernie.geckolib.loading.object.BakedAnimations.class);
            for(var name:List.of("idle","walk","run","attack","shed","hurt","death")){
                var animation=baked.getAnimation("animation.zhiren_jianke."+name);
                h.assertTrue(animation!=null&&animation.boneAnimations().length>0,"GeckoLib really parses nonempty clip: "+name);
            }
            var attack=baked.getAnimation("animation.zhiren_jianke.attack");boolean stepped=false;
            // GeckoLib's nested Molang library is runtime-only in the existing Forge classpath.
            // Inspect the real parsed keyframes without adding a compile-time library dependency.
            for(Object bone:attack.boneAnimations()){
                Object stack=bone.getClass().getMethod("rotationKeyFrames").invoke(bone);
                for(Object frame:(List<?>)stack.getClass().getMethod("xKeyframes").invoke(stack))
                    if(frame.getClass().getMethod("easingType").invoke(frame)==software.bernie.geckolib.core.animation.EasingType.STEP)stepped=true;
            }
            h.assertTrue(stepped,"GeckoLib parser retains actual step easing, not silently substituted linear curves");
            h.assertTrue(baked.getAnimation("animation.zhiren_jianke.death").length()==10,"Native animation timing matches ten-tick server death");
        }
        h.succeed();
    }

}
