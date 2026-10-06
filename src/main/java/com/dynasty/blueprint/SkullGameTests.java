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
public final class SkullGameTests {
    private static TemplateMob skull(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=11;y++)h.setBlock(x,y,z,y==1||y==11?Blocks.STONE:Blocks.AIR);
        var mob=h.spawn(BlueprintEntities.MUXUE_FEILU.get(),new BlockPos(7,6,5));mob.setNoAi(true);return mob;
    }
    private static net.minecraft.world.entity.animal.Cow enemy(GameTestHelper h){
        var cow=h.spawn(EntityType.COW,new BlockPos(7,2,9));cow.setNoAi(true);cow.setNoGravity(true);
        cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);cow.setHealth(200);return cow;
    }
    private static net.minecraft.server.level.ServerPlayer player(GameTestHelper h,int x,int z){
        var p=new net.minecraft.server.level.ServerPlayer(h.getLevel().getServer(),h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"skull-test"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(x,2,z))));p.getFoodData().setFoodLevel(10);p.getFoodData().setSaturation(0);h.getLevel().addNewPlayer(p);
        h.onEachTick(()->{if(!p.isRemoved())p.doTick();});return p;
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=65,batch="skull")
    public static void diveWarnsThenMakesOnePhysicalContactAcrossReload(GameTestHelper h){
        var mob=skull(h);mob.setNoAi(false);var cow=enemy(h);h.assertTrue(mob.startSkill(ArmySkills.SKULL_DIVE,cow),"Airborne skull starts actual dive");
        h.runAfterDelay(12,()->h.assertTrue(cow.getHealth()==200,"Fourteen-tick windup does no early damage"));
        h.startSequence().thenWaitUntil(()->h.assertTrue(cow.getHealth()==195,"Wait for actual moving body contact"))
            .thenExecute(()->{
                h.assertTrue(mob.actionAge(0)<26,"Contact must occur inside active dive window");
                var tag=new CompoundTag();mob.save(tag);mob.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
                var copy=BlueprintEntities.MUXUE_FEILU.get().create(h.getLevel());copy.load(tag);h.getLevel().addFreshEntity(copy);cow.invulnerableTime=0;
            }).thenIdle(15).thenExecute(()->h.assertTrue(cow.getHealth()==195,"Consumed bite remains consumed after reloading during ACTIVE")).thenSucceed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=55,batch="skull")
    public static void movingAfterTellDodgesLockedDivePoint(GameTestHelper h){
        var mob=skull(h);mob.setNoAi(false);var cow=enemy(h);var point=cow.position();h.assertTrue(mob.startSkill(ArmySkills.SKULL_DIVE,cow),"Dive starts");
        h.runAfterDelay(12,()->cow.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(12,2,9)))));
        h.runAfterDelay(35,()->{h.assertTrue(cow.getHealth()==200&&mob.position().distanceTo(point)<2,"Dive follows locked point, not a homing current player position");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=55,batch="skull")
    public static void newSolidWallStopsDiveWithoutRemoteDamage(GameTestHelper h){
        var mob=skull(h);mob.setNoAi(false);var cow=enemy(h);h.assertTrue(mob.startSkill(ArmySkills.SKULL_DIVE,cow),"Dive starts with clear sight");
        h.runAfterDelay(12,()->{for(int x=6;x<=8;x++)for(int y=2;y<=9;y++)h.setBlock(x,y,7,Blocks.STONE);});
        h.runAfterDelay(38,()->{h.assertTrue(cow.getHealth()==200&&mob.getZ()<h.absolutePos(new BlockPos(7,2,7)).getZ(),"Ray and ordinary collision stop skull before wall");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=45,batch="skull")
    public static void bloodCastUsesActualFloorAndSharesThreePoolCap(GameTestHelper h){
        var first=skull(h);var cow=enemy(h);first.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(7,6,7))));
        h.assertTrue(first.startSkill(ArmySkills.SKULL_BLOOD,cow),"Overhead blood starts");
        for(int i=0;i<4;i++){var other=h.spawn(BlueprintEntities.MUXUE_FEILU.get(),new BlockPos(7,6,7));other.setNoAi(true);h.assertTrue(other.startSkill(ArmySkills.SKULL_BLOOD,cow),"Independent skull cast starts");}
        h.runAfterDelay(18,()->h.assertTrue(h.getLevel().getEntitiesOfClass(SkullBloodPool.class,first.getBoundingBox().inflate(8)).isEmpty(),"No puddle during tell"));
        h.runAfterDelay(24,()->{
            var pools=h.getLevel().getEntitiesOfClass(SkullBloodPool.class,first.getBoundingBox().inflate(8));
            h.assertTrue(pools.size()==3,"Five casters cannot exceed three shared pools");
            for(var pool:pools)h.assertTrue(Math.abs(pool.getY()-(h.absolutePos(new BlockPos(7,2,7)).getY()+.03))<.01,"Puddle is on real solid floor, not suspended at skull height");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=130,batch="skull")
    public static void bloodCorrodesOnlyNearbyEnemyArmourAndExpiresAcrossUnload(GameTestHelper h){
        var owner=skull(h);var a=player(h,7,7);var b=player(h,12,7);
        var ally=h.spawn(BlueprintEntities.ZHIREN_JIANKE.get(),new BlockPos(7,2,7));ally.setNoAi(true);
        a.setItemSlot(net.minecraft.world.entity.EquipmentSlot.FEET,new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.IRON_BOOTS));
        b.setItemSlot(net.minecraft.world.entity.EquipmentSlot.FEET,new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.IRON_BOOTS));
        var pool=new SkullBloodPool(BlueprintEntities.SKULL_BLOOD_POOL.get(),h.getLevel());pool.setPos(a.position());pool.setOwner(owner);pool.activate(h.getLevel().getGameTime());h.getLevel().addFreshEntity(pool);var saved=new CompoundTag();
        h.runAfterDelay(23,()->{
            h.assertTrue(a.getItemBySlot(net.minecraft.world.entity.EquipmentSlot.FEET).getDamageValue()==1&&a.hasEffect(net.minecraft.world.effect.MobEffects.POISON),"One real corrosion pulse damages worn armour and poisons player");
            h.assertTrue(b.getItemBySlot(net.minecraft.world.entity.EquipmentSlot.FEET).getDamageValue()==0&&!b.hasEffect(net.minecraft.world.effect.MobEffects.POISON),"Second player outside radius is unaffected");
            h.assertTrue(!ally.hasEffect(net.minecraft.world.effect.MobEffects.POISON),"Allied spirit is immune to its faction's cloud");
        });
        h.runAfterDelay(45,()->{pool.save(saved);pool.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);a.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(12,2,11))));});
        h.runAfterDelay(95,()->{
            var restored=new SkullBloodPool(BlueprintEntities.SKULL_BLOOD_POOL.get(),h.getLevel());restored.load(saved);h.getLevel().addFreshEntity(restored);
            h.runAfterDelay(3,()->{h.assertTrue(restored.isRemoved()&&!a.hasEffect(net.minecraft.world.effect.MobEffects.POISON)
                &&a.getItemBySlot(net.minecraft.world.entity.EquipmentSlot.FEET).getDamageValue()==2,"Expired loaded pool cannot catch up corrosion, duplicate pulses or leave permanent poison");a.discard();b.discard();h.succeed();});
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=270,batch="skull")
    public static void autonomousFlightReturnsAboveVictimAndDeathFallsNormally(GameTestHelper h){
        var mob=skull(h);var cow=enemy(h);cow.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(7,2,13))));
        mob.setNoAi(false);mob.setTarget(cow);boolean[] rose={false};
        h.onEachTick(()->{if(cow.getHealth()<200&&mob.getY()>=cow.getY()+3)rose[0]=true;});
        h.runAfterDelay(220,()->{
            h.assertTrue(cow.getHealth()<200&&rose[0]&&mob.isNoGravity()&&!mob.noPhysics,"Real flight AI dives, hurts and climbs back to hover height; hp="+cow.getHealth()+" rose="+rose[0]+" at="+mob.position());
            h.assertTrue(mob.getNavigation() instanceof net.minecraft.world.entity.ai.navigation.FlyingPathNavigation
                &&mob.getMoveControl() instanceof net.minecraft.world.entity.ai.control.FlyingMoveControl,"Uses real vanilla flying navigation and control");
            mob.hurt(mob.damageSources().genericKill(),10000);
            h.assertTrue(!mob.isNoGravity(),"Death releases hovering gravity");
            h.runAfterDelay(46,()->{h.assertTrue(mob.isRemoved(),"Death cleanup completes");h.succeed();});
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=265,batch="skull")
    public static void airSacIsConsumedAndItsEffectsExpire(GameTestHelper h){
        skull(h);var p=player(h,3,3);p.setInvulnerable(true);p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new net.minecraft.world.item.ItemStack(BlueprintSalvage.YIN_AIR_SAC.get(),2));
        p.startUsingItem(net.minecraft.world.InteractionHand.MAIN_HAND);
        h.runAfterDelay(38,()->h.assertTrue(p.getMainHandItem().getCount()==1&&p.hasEffect(net.minecraft.world.effect.MobEffects.SLOW_FALLING)
            &&p.hasEffect(net.minecraft.world.effect.MobEffects.WATER_BREATHING)&&p.getFoodData().getFoodLevel()==10,"Actual use consumes one sac, grants timed effects, restores no hunger"));
        h.runAfterDelay(245,()->{h.assertTrue(p.isAlive(),"Consumption fixture survives unrelated mobs");h.assertTrue(!p.hasEffect(net.minecraft.world.effect.MobEffects.SLOW_FALLING)&&!p.hasEffect(net.minecraft.world.effect.MobEffects.WATER_BREATHING),"Both effects expire natively");p.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="skull")
    public static void skullClipsLoadThroughRealAnimationParser(GameTestHelper h) throws Exception {
        var gson=new com.google.gson.GsonBuilder().registerTypeAdapter(software.bernie.geckolib.loading.object.BakedAnimations.class,
            new software.bernie.geckolib.loading.json.typeadapter.BakedAnimationsAdapter()).create();
        try(var stream=SkullGameTests.class.getResourceAsStream("/assets/dynasty/animations/blueprint/muxue_feilu.animation.json")){
            h.assertTrue(stream!=null,"Skull animation ships on the runtime resource path");
            var resource=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(stream,java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject();
            var baked=gson.fromJson(resource.getAsJsonObject("animations"),software.bernie.geckolib.loading.object.BakedAnimations.class);
            for(var name:java.util.List.of("idle","walk","run","attack","blood","hurt","death")){
                var clip=baked.getAnimation("animation.muxue_feilu."+name);
                h.assertTrue(clip!=null&&clip.boneAnimations().length>0,"GeckoLib loads skull clip: "+name);
            }
            h.assertTrue(baked.getAnimation("animation.muxue_feilu.attack").length()==44
                &&baked.getAnimation("animation.muxue_feilu.blood").length()==50,"Client clips retain the actual server action lengths");
        }
        h.succeed();
    }

}
