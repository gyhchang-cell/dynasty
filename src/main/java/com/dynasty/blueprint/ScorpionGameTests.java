package com.dynasty.blueprint;

import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class ScorpionGameTests {
    private static TemplateMob scorpion(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=0;y<=10;y++)h.setBlock(x,y,z,y==0||y==10?Blocks.STONE:y==1?Blocks.SAND:Blocks.AIR);
        var mob=h.spawn(BlueprintEntities.MINGSHA_SHIXIE.get(),new BlockPos(7,2,4));mob.setNoAi(true);mob.setOnGround(true);return mob;
    }
    private static net.minecraft.world.entity.animal.Cow enemy(GameTestHelper h,int x,int z){
        var cow=h.spawn(EntityType.COW,new BlockPos(x,2,z));cow.setNoAi(true);cow.setNoGravity(true);cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);cow.setHealth(200);return cow;
    }
    private static net.minecraft.server.level.ServerPlayer player(GameTestHelper h,int x,int z){
        var p=new net.minecraft.server.level.ServerPlayer(h.getLevel().getServer(),h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"scorpion-test"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(x,2,z))));h.getLevel().addNewPlayer(p);h.onEachTick(()->{if(!p.isRemoved())p.doTick();});return p;
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=220,batch="scorpion_ai")
    public static void realAiBurrowsEmergesWithTellAndAttacksUnderNormalCollision(GameTestHelper h){
        var mob=scorpion(h);var cow=enemy(h,7,14);mob.setNoAi(false);mob.setTarget(cow);var start=mob.position();boolean[] burrow={false},emerge={false};
        h.onEachTick(()->{if(mob.burrowed())burrow[0]=true;if(mob.skillId()==ArmySkills.SCORPION_EMERGE){emerge[0]=true;h.assertTrue(cow.getHealth()==200,"Emergence tell is harmless");}
            if(h.getTick()%30==0)com.mojang.logging.LogUtils.getLogger().info("SCORPION_AI tick={} distance={} buried={} skill={} hp={}",h.getTick(),mob.distanceTo(cow),mob.burrowed(),mob.skillId(),cow.getHealth());});
        h.runAfterDelay(200,()->{
            h.assertTrue(burrow[0]&&emerge[0]&&cow.getHealth()<200,"Autonomous approach uses burrow then emergence and real attack");
            h.assertTrue(mob.position().distanceTo(start)>4&&!mob.noPhysics&&!mob.isNoGravity()&&Math.abs(mob.getY()-start.y)<.2,"Burrowing keeps ordinary floor and wall collision");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=50,batch="scorpion")
    public static void burrowStatePersistsAndTerrainChangeUsesHarmlessEmergence(GameTestHelper h){
        var mob=scorpion(h);mob.setBurrowed(true);var cow=enemy(h,7,6);var saved=new CompoundTag();mob.save(saved);mob.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
        var copy=BlueprintEntities.MINGSHA_SHIXIE.get().create(h.getLevel());copy.load(saved);h.getLevel().addFreshEntity(copy);
        h.assertTrue(copy.burrowed()&&!copy.startSkill(ArmySkills.SCORPION_CLAW,cow),"Reloaded buried scorpion cannot skip emergence to attack");
        h.setBlock(7,1,4,Blocks.STONE);
        h.runAfterDelay(15,()->h.assertTrue(!copy.burrowed()&&copy.skillId()==ArmySkills.SCORPION_EMERGE&&cow.getHealth()==200,"Loss of sand starts real emergence clock even with no AI target"));
        h.runAfterDelay(40,()->{h.assertTrue(copy.skillId()==0&&copy.startSkill(ArmySkills.SCORPION_CLAW,cow),"Only completed emergence permits attack");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=50,batch="scorpion")
    public static void clawThenStingRetainsVictimAndSingleContactsAcrossReload(GameTestHelper h){
        var mob=scorpion(h);var cow=enemy(h,7,6);h.assertTrue(mob.startSkill(ArmySkills.SCORPION_CLAW,cow),"Pincer combo starts");
        h.runAfterDelay(10,()->h.assertTrue(cow.getHealth()==200,"Pincer warning precedes damage"));
        h.runAfterDelay(15,()->{
            h.assertTrue(cow.getHealth()==197&&cow.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Left pincer lands once and briefly restricts movement");
            var t=new CompoundTag();mob.save(t);mob.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);var copy=BlueprintEntities.MINGSHA_SHIXIE.get().create(h.getLevel());copy.load(t);h.getLevel().addFreshEntity(copy);
        });
        h.runAfterDelay(24,()->{h.assertTrue(cow.getHealth()==192&&cow.hasEffect(MobEffects.POISON),"Saved clamped identity receives exactly one five-damage tail strike");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40,batch="scorpion")
    public static void missingClawCannotDeliverHomingTailStrike(GameTestHelper h){
        var mob=scorpion(h);var cow=enemy(h,7,6);h.assertTrue(mob.startSkill(ArmySkills.SCORPION_CLAW,cow),"Combo begins");
        h.runAfterDelay(10,()->cow.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(12,2,6)))));
        h.runAfterDelay(16,()->cow.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(7,2,6)))));
        h.runAfterDelay(30,()->{h.assertTrue(cow.getHealth()==200&&!cow.hasEffect(MobEffects.POISON),"Dodging first pincer prevents tail from acquiring returning victim");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=200,batch="scorpion_effects")
    public static void songIsLocalFiniteAndDelaysNativeShieldRaising(GameTestHelper h){
        var mob=scorpion(h);var a=player(h,7,8);var outside=player(h,13,8);var wall=player(h,3,4);a.setInvulnerable(true);outside.setInvulnerable(true);wall.setInvulnerable(true);
        for(int z=2;z<=6;z++)for(int y=2;y<6;y++)h.setBlock(5,y,z,Blocks.STONE);
        h.assertTrue(mob.startSkill(ArmySkills.SCORPION_SONG,a),"Sound starts with a warning");
        h.runAfterDelay(18,()->h.assertTrue(!a.hasEffect(MobEffects.CONFUSION),"Sound warning has no early effect"));
        h.runAfterDelay(24,()->{
            h.assertTrue(a.hasEffect(MobEffects.CONFUSION)&&a.hasEffect(MobEffects.DIG_SLOWDOWN)&&a.hasEffect(BlueprintEntities.SAND_RESONANCE.get()),"Nearby player gets actual finite nausea, mining and shield debuffs");
            h.assertTrue(!outside.hasEffect(BlueprintEntities.SAND_RESONANCE.get())&&!wall.hasEffect(BlueprintEntities.SAND_RESONANCE.get()),"Distance and solid wall protect other players");
            a.setItemInHand(net.minecraft.world.InteractionHand.OFF_HAND,new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.SHIELD));a.startUsingItem(net.minecraft.world.InteractionHand.OFF_HAND);
        });
        h.runAfterDelay(33,()->h.assertTrue(a.isUsingItem()&&!a.isBlocking(),"Native shield use starts but cannot block after ordinary five ticks"));
        h.runAfterDelay(49,()->{h.assertTrue(a.isBlocking(),"Shield becomes usable after delayed raise; no disabled input");a.stopUsingItem();});
        h.runAfterDelay(166,()->{
            h.assertTrue(!a.hasEffect(MobEffects.CONFUSION)&&!a.hasEffect(MobEffects.DIG_SLOWDOWN)&&!a.hasEffect(BlueprintEntities.SAND_RESONANCE.get()),"Every effect expires without camera state cleanup");
            a.startUsingItem(net.minecraft.world.InteractionHand.OFF_HAND);
            h.runAfterDelay(7,()->{h.assertTrue(a.isBlocking(),"Original shield raising time returns");a.discard();outside.discard();wall.discard();h.succeed();});
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=35,batch="scorpion_ecology")
    public static void registeredDesertSpawnRequiresShallowDrySandAndCapsThree(GameTestHelper h){
        scorpion(h).discard();var level=h.getLevel();var base=h.absolutePos(new BlockPos(7,0,7));var pos=new BlockPos(base.getX(),132,base.getZ());
        for(int x=-4;x<=4;x++)for(int z=-4;z<=4;z++){
            level.setBlockAndUpdate(pos.offset(x,-2,z),Blocks.STONE.defaultBlockState());level.setBlockAndUpdate(pos.offset(x,-1,z),Blocks.SAND.defaultBlockState());
            for(int y=0;y<8;y++)level.setBlockAndUpdate(pos.offset(x,y,z),Blocks.AIR.defaultBlockState());
        }
        var a=pos.offset(-4,-2,-4);var b=pos.offset(4,7,4);
        level.getServer().getCommands().performPrefixedCommand(level.getServer().createCommandSourceStack().withLevel(level).withPermission(4).withSuppressedOutput(),
            "fillbiome "+a.getX()+" "+a.getY()+" "+a.getZ()+" "+b.getX()+" "+b.getY()+" "+b.getZ()+" minecraft:desert");
        var type=BlueprintEntities.MINGSHA_SHIXIE.get();
        h.assertTrue(net.minecraft.world.entity.SpawnPlacements.checkSpawnRules(type,level,net.minecraft.world.entity.MobSpawnType.NATURAL,pos,level.random),"Real registered predicate accepts dry desert sand surface");
        h.assertTrue(level.getBiome(pos).value().getMobSettings().getMobs(net.minecraft.world.entity.MobCategory.MONSTER).unwrap().stream().anyMatch(e->e.type==type&&e.minCount==1&&e.maxCount==2&&e.getWeight().asInt()==4),"Biome modifier enters actual weighted spawn list");
        level.setBlockAndUpdate(pos.below(),Blocks.STONE.defaultBlockState());h.assertTrue(!BlueprintSpawns.scorpionHabitat(level,pos),"Ordinary stone does not count as sand");level.setBlockAndUpdate(pos.below(),Blocks.SAND.defaultBlockState());
        var spawned=new java.util.ArrayList<TemplateMob>();for(int i=0;i<3;i++)spawned.add(type.spawn(level,pos.offset((i-1)*3,0,0),net.minecraft.world.entity.MobSpawnType.NATURAL));
        h.assertTrue(spawned.stream().allMatch(e->e!=null&&!e.isNoAi())&&!BlueprintSpawns.scorpionHabitat(level,pos),"Three real spawns reach local cap");spawned.forEach(Entity::discard);h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30,batch="scorpion")
    public static void scorpionSalvageUsesRealCraftingAndSmeltingRecipes(GameTestHelper h){
        var p=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"scorpion-salvage"));
        var menu=new net.minecraft.world.inventory.CraftingMenu(0,p.getInventory(),net.minecraft.world.inventory.ContainerLevelAccess.create(h.getLevel(),h.absolutePos(new BlockPos(2,2,2))));
        menu.getSlot(1).set(new net.minecraft.world.item.ItemStack(BlueprintSalvage.METAL_STING_NEEDLE.get()));menu.getSlot(2).set(new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.STICK));menu.getSlot(3).set(new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.FEATHER));
        h.assertTrue(menu.getSlot(0).getItem().is(net.minecraft.world.item.Items.ARROW)&&menu.getSlot(0).getItem().getCount()==4,"Needle crafts four real vanilla arrows");var arrows=menu.getSlot(0).remove(4);menu.getSlot(0).onTake(p,arrows);
        h.assertTrue(menu.getSlot(1).getItem().isEmpty()&&menu.getSlot(2).getItem().isEmpty()&&menu.getSlot(3).getItem().isEmpty(),"Craft consumes all components once");
        var input=new net.minecraft.world.SimpleContainer(new net.minecraft.world.item.ItemStack(BlueprintSalvage.RESONANT_SCORPION_SHELL.get()));
        var smelt=h.getLevel().getRecipeManager().getRecipeFor(net.minecraft.world.item.crafting.RecipeType.SMELTING,input,h.getLevel());
        h.assertTrue(smelt.isPresent()&&smelt.get().getResultItem(h.getLevel().registryAccess()).is(net.minecraft.world.item.Items.GLASS)&&smelt.get().getCookingTime()==200,"Shell has real furnace recipe and ordinary cooking time");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="scorpion")
    public static void scorpionClipsLoadThroughActualGeckoParser(GameTestHelper h) throws Exception {
        var gson=new com.google.gson.GsonBuilder().registerTypeAdapter(software.bernie.geckolib.loading.object.BakedAnimations.class,new software.bernie.geckolib.loading.json.typeadapter.BakedAnimationsAdapter()).create();
        try(var stream=ScorpionGameTests.class.getResourceAsStream("/assets/dynasty/animations/blueprint/mingsha_shixie.animation.json")){
            var json=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(stream,java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject();var clips=gson.fromJson(json.getAsJsonObject("animations"),software.bernie.geckolib.loading.object.BakedAnimations.class);
            for(var name:java.util.List.of("idle","walk","run","burrow","emerge","attack","song","hurt","death"))h.assertTrue(clips.getAnimation("animation.mingsha_shixie."+name).boneAnimations().length>0,"Parser accepts "+name);
            h.assertTrue(clips.getAnimation("animation.mingsha_shixie.emerge").length()==32&&clips.getAnimation("animation.mingsha_shixie.attack").length()==40&&clips.getAnimation("animation.mingsha_shixie.song").length()==48,"Server clocks match actual animation clips");
        }
        h.succeed();
    }
}
