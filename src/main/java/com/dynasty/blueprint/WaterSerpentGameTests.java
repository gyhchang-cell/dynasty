package com.dynasty.blueprint;

import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class WaterSerpentGameTests {
    private static TemplateMob serpent(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=0;y<=8;y++)h.setBlock(x,y,z,y==0||y==1||y==8?Blocks.STONE:Blocks.AIR);
        var mob=h.spawn(BlueprintEntities.BISHUI_XUANJIAO_YOUZI.get(),new BlockPos(7,2,5));mob.setNoAi(true);mob.setNoGravity(true);return mob;
    }
    private static Cow target(GameTestHelper h){
        var cow=h.spawn(EntityType.COW,new BlockPos(7,2,7));cow.setNoAi(true);cow.setNoGravity(true);
        cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);cow.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);cow.setHealth(200);return cow;
    }
    private static void water(GameTestHelper h){for(int x=8;x<=11;x++)for(int z=5;z<=9;z++)for(int y=0;y<=2;y++)h.setBlock(x,y,z,Blocks.WATER);}
    @GameTest(template="bow_ritual_test",timeoutTicks=50,batch="serpent")
    public static void biteHasTwelveTickTellOneContactAndChill(GameTestHelper h){
        var mob=serpent(h);var target=target(h);h.assertTrue(mob.startSkill(ArmySkills.SERPENT_BITE,target),"Starts bite");
        h.runAfterDelay(10,()->h.assertTrue(target.getHealth()==200,"Tell cannot damage"));
        h.runAfterDelay(15,()->h.assertTrue(target.getHealth()==194&&target.hasEffect(net.minecraft.world.effect.MobEffects.MOVEMENT_SLOWDOWN),"Single authored contact applies chill"));
        h.runAfterDelay(33,()->{h.assertTrue(target.getHealth()==194&&mob.skillId()==0,"Recovery causes no repeated damage");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40,batch="serpent")
    public static void dodgingLockedBitePreventsContact(GameTestHelper h){
        var mob=serpent(h);var target=target(h);h.assertTrue(mob.startSkill(ArmySkills.SERPENT_BITE,target),"Starts bite");
        h.runAfterDelay(8,()->target.setPos(mob.position().add(2,0,0)));
        h.runAfterDelay(18,()->{h.assertTrue(target.getHealth()==200,"Bite does not home during tell");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=70,batch="serpent")
    public static void coilNeedsDeepWaterAndExpiresWithoutInputLock(GameTestHelper h){
        var mob=serpent(h);var target=target(h);h.assertTrue(!mob.startSkill(ArmySkills.SERPENT_COIL,target),"Dry ground rejects coil");water(h);
        h.assertTrue(mob.startSkill(ArmySkills.SERPENT_COIL,target),"Deep adjacent pool permits coil");
        h.runAfterDelay(16,()->h.assertTrue(!target.hasEffect(BlueprintEntities.COLD_POOL_COIL.get()),"Coil tell is escapable"));
        h.runAfterDelay(21,()->h.assertTrue(target.hasEffect(BlueprintEntities.COLD_POOL_COIL.get())&&mob.hookTargetId()==target.getId(),"Real contact publishes finite captive identity"));
        h.runAfterDelay(48,()->{h.assertTrue(!target.hasEffect(BlueprintEntities.COLD_POOL_COIL.get())&&mob.hookTargetId()==-1,"Hold terminates automatically");h.assertTrue(!target.noPhysics&&!target.isPassenger(),"No riding or collision bypass");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=45,batch="serpent")
    public static void fiveSneakTicksEscapeCoil(GameTestHelper h){
        var mob=serpent(h);var target=target(h);water(h);h.assertTrue(mob.startSkill(ArmySkills.SERPENT_COIL,target),"Starts coil");
        h.runAfterDelay(21,()->{h.assertTrue(target.hasEffect(BlueprintEntities.COLD_POOL_COIL.get()),"Contact captured target");target.setShiftKeyDown(true);});
        h.runAfterDelay(29,()->{h.assertTrue(!target.hasEffect(BlueprintEntities.COLD_POOL_COIL.get())&&mob.hookTargetId()==-1,"Five sneak ticks break the hold");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40,batch="serpent")
    public static void woundingCasterReleasesCaptiveImmediately(GameTestHelper h){
        var mob=serpent(h);var target=target(h);water(h);mob.startSkill(ArmySkills.SERPENT_COIL,target);
        h.runAfterDelay(21,()->{
            h.assertTrue(target.hasEffect(BlueprintEntities.COLD_POOL_COIL.get()),"Contact captured target");
            mob.hurt(mob.damageSources().mobAttack(target),12);
            h.assertTrue(!target.hasEffect(BlueprintEntities.COLD_POOL_COIL.get())&&mob.hookTargetId()==-1,"Actual accepted health damage breaks hold");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=80,batch="serpent")
    public static void unloadNeverRestartsHoldOrErasesCooldown(GameTestHelper h){
        var mob=serpent(h);var target=target(h);water(h);mob.startSkill(ArmySkills.SERPENT_COIL,target);var saved=new CompoundTag();
        h.runAfterDelay(21,()->{mob.save(saved);mob.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);});
        h.runAfterDelay(55,()->{
            var copy=BlueprintEntities.BISHUI_XUANJIAO_YOUZI.get().create(h.getLevel());copy.load(saved);h.getLevel().addFreshEntity(copy);
            h.runAfterDelay(3,()->{h.assertTrue(!target.hasEffect(BlueprintEntities.COLD_POOL_COIL.get())&&copy.hookTargetId()==-1,"Expired captive is never restored");
                h.assertTrue(!copy.startSkill(ArmySkills.SERPENT_COIL,target),"Reload retains 180-tick cooldown");h.succeed();});
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30,batch="serpent")
    public static void waterEcologyHonoursActualBiomePoolAndTwoMobCap(GameTestHelper h){
        var mob=serpent(h);mob.discard();var level=h.getLevel();var pos=h.absolutePos(new BlockPos(9,2,7));
        var a=h.absolutePos(new BlockPos(0,0,0));var b=h.absolutePos(new BlockPos(15,8,15));
        level.getServer().getCommands().performPrefixedCommand(level.getServer().createCommandSourceStack().withLevel(level).withPermission(4).withSuppressedOutput(),
            "fillbiome "+a.getX()+" "+a.getY()+" "+a.getZ()+" "+b.getX()+" "+b.getY()+" "+b.getZ()+" minecraft:lush_caves");
        h.setBlock(9,2,7,Blocks.WATER);h.assertTrue(!BlueprintSpawns.serpentHabitat(level,pos),"Shallow puddle is insufficient");water(h);
        var type=BlueprintEntities.BISHUI_XUANJIAO_YOUZI.get();
        h.assertTrue(net.minecraft.world.entity.SpawnPlacements.checkSpawnRules(type,level,net.minecraft.world.entity.MobSpawnType.NATURAL,pos,level.random),"Deep covered pool passes registered predicate");
        h.assertTrue(level.getBiome(pos).value().getMobSettings().getMobs(net.minecraft.world.entity.MobCategory.MONSTER).unwrap().stream().anyMatch(e->e.type==type&&e.maxCount==1),"Actual biome spawn pool contains serpent");
        var first=type.spawn(level,pos,net.minecraft.world.entity.MobSpawnType.NATURAL);var second=type.spawn(level,pos.offset(1,0,0),net.minecraft.world.entity.MobSpawnType.NATURAL);
        h.assertTrue(first!=null&&second!=null&&first.canBreatheUnderwater(),"Actual entity initializes amphibious body");
        h.assertTrue(!BlueprintSpawns.serpentHabitat(level,pos),"Two local serpents close spawn gate");first.discard();second.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=180,batch="serpent_ai")
    public static void autonomousSerpentSwimsToShoreAndBites(GameTestHelper h){
        var mob=serpent(h);var target=target(h);target.setPos(mob.position().add(0,0,8));
        for(int x=3;x<=10;x++)for(int z=2;z<=9;z++)for(int y=0;y<=3;y++)h.setBlock(x,y,z,Blocks.WATER);
        mob.setNoGravity(false);mob.setNoAi(false);mob.setTarget(target);var start=mob.position();boolean[] swam={false};
        h.onEachTick(()->{if(mob.isInWater()&&mob.position().distanceToSqr(start)>1)swam[0]=true;});
        h.runAfterDelay(150,()->{
            h.assertTrue(swam[0]&&target.getHealth()<200,"Actual AI crosses water and attacks shore target: swim="+swam[0]+" health="+target.getHealth()+" pos="+mob.position());
            h.assertTrue(!mob.noPhysics&&!mob.isNoGravity(),"Swimming retains ordinary collision and gravity");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="serpent")
    public static void coilCancelsRealForgeUseEventsForBothHandsAndReleases(GameTestHelper h){
        var player=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(java.util.UUID.randomUUID(),"coil-use"));
        player.addEffect(new net.minecraft.world.effect.MobEffectInstance(BlueprintEntities.COLD_POOL_COIL.get(),24));
        for(var hand:net.minecraft.world.InteractionHand.values()){
            var item=new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.SHIELD);player.setItemInHand(hand,item);
            var click=new net.minecraftforge.event.entity.player.PlayerInteractEvent.RightClickItem(player,hand);
            net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(click);
            var start=new net.minecraftforge.event.entity.living.LivingEntityUseItemEvent.Start(player,item,72000);
            net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(start);
            h.assertTrue(click.isCanceled()&&start.isCanceled(),"Registered server events deny item use in "+hand);
        }
        player.removeEffect(BlueprintEntities.COLD_POOL_COIL.get());
        var released=new net.minecraftforge.event.entity.player.PlayerInteractEvent.RightClickItem(player,net.minecraft.world.InteractionHand.OFF_HAND);
        net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(released);
        h.assertTrue(!released.isCanceled(),"Removing finite debuff restores normal use");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="serpent")
    public static void articulatedRigClipsLoadThroughGeckoLib(GameTestHelper h) throws Exception {
        var gson=new com.google.gson.GsonBuilder().registerTypeAdapter(software.bernie.geckolib.loading.object.BakedAnimations.class,new software.bernie.geckolib.loading.json.typeadapter.BakedAnimationsAdapter()).create();
        try(var stream=WaterSerpentGameTests.class.getResourceAsStream("/assets/dynasty/animations/blueprint/bishui_xuanjiao_youzi.animation.json")){
            var json=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(stream,java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject();
            var clips=gson.fromJson(json.getAsJsonObject("animations"),software.bernie.geckolib.loading.object.BakedAnimations.class);
            for(var name:java.util.List.of("idle","walk","run","attack","coil","hurt","death"))h.assertTrue(clips.getAnimation("animation.bishui_xuanjiao_youzi."+name).boneAnimations().length>0,"Parsed "+name);
            h.assertTrue(clips.getAnimation("animation.bishui_xuanjiao_youzi.coil").length()==64,"Animation matches authoritative clock");
        }h.succeed();
    }
}
