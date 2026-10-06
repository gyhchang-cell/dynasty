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
public final class TreeGameTests {
    private static TemplateMob tree(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=10;y++)h.setBlock(x,y,z,y==1||y==10?Blocks.STONE:Blocks.AIR);
        var mob=h.spawn(BlueprintEntities.KUMU_SHUJING.get(),new BlockPos(7,2,5));mob.setNoAi(true);mob.setOnGround(true);return mob;
    }
    private static net.minecraft.world.entity.animal.Cow enemy(GameTestHelper h,int x,int z){
        var cow=h.spawn(EntityType.COW,new BlockPos(x,2,z));cow.setNoAi(true);cow.setNoGravity(true);
        cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);cow.setHealth(200);return cow;
    }
    private static net.minecraft.server.level.ServerPlayer player(GameTestHelper h,int x,int z){
        var p=new net.minecraft.server.level.ServerPlayer(h.getLevel().getServer(),h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"tree-test"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(x,2,z))));h.getLevel().addNewPlayer(p);h.onEachTick(()->{if(!p.isRemoved())p.doTick();});return p;
    }
    private static RootSnare cage(GameTestHelper h,TemplateMob owner,Vec3 at){
        var cage=new RootSnare(BlueprintEntities.ROOT_SNARE.get(),h.getLevel());cage.setPos(at);cage.activate(owner);h.getLevel().addFreshEntity(cage);return cage;
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=90,batch="tree_ai")
    public static void dormantTreeStaysStillThenSameEntityAwakensAndPersists(GameTestHelper h){
        var mob=tree(h);var p=player(h,7,14);var id=mob.getUUID();var origin=mob.position();mob.setNoAi(false);
        h.runAfterDelay(20,()->{
            h.assertTrue(!mob.treeAwake()&&mob.visualAnimation().equals("camouflage")&&mob.position().distanceTo(origin)<.01,"Faraway player cannot move or wake disguised tree");
            h.assertTrue(!mob.startSkill(ArmySkills.TREE_ROOTS,p),"Dormant tree cannot bypass awakening");p.moveTo(origin.add(0,0,4));
        });
        h.runAfterDelay(35,()->h.assertTrue(mob.treeAwake()&&mob.skillId()==ArmySkills.TREE_WAKE&&mob.getUUID().equals(id),"Proximity starts same entity's harmless awakening tell"));
        h.runAfterDelay(65,()->{
            var tag=new CompoundTag();mob.save(tag);mob.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            var restored=BlueprintEntities.KUMU_SHUJING.get().create(h.getLevel());restored.load(tag);h.getLevel().addFreshEntity(restored);
            h.assertTrue(restored.treeAwake()&&restored.getUUID().equals(id)&&!restored.visualAnimation().equals("camouflage"),"Awakened state survives actual entity unload/load");p.discard();h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=50,batch="tree")
    public static void sweepHasHarmlessTellFrontArcAndOnlyOneHit(GameTestHelper h){
        var mob=tree(h);mob.setTreeAwake(true);var front=enemy(h,7,8);var rear=enemy(h,7,2);
        h.assertTrue(mob.startSkill(ArmySkills.TREE_SWEEP,front),"Awakened tree sweeps");
        h.runAfterDelay(16,()->h.assertTrue(front.getHealth()==200,"Eighteen-tick windup does no damage"));
        h.runAfterDelay(40,()->{h.assertTrue(front.getHealth()==192&&rear.getHealth()==200,"Locked front sector hits once; rear remains safe");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=110,batch="tree")
    public static void rootsKeepWarnedPositionAcrossReloadAndCanBeDodged(GameTestHelper h){
        var mob=tree(h);mob.setTreeAwake(true);var cow=enemy(h,7,11);var point=cow.blockPosition();
        h.assertTrue(mob.startSkill(ArmySkills.TREE_ROOTS,cow),"Root cast starts");
        h.runAfterDelay(15,()->{
            h.assertTrue(h.getLevel().getEntitiesOfClass(RootSnare.class,mob.getBoundingBox().inflate(12)).isEmpty(),"No root cage before warning ends");
            cow.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(12,2,11))));
            var tag=new CompoundTag();mob.save(tag);mob.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            var restored=BlueprintEntities.KUMU_SHUJING.get().create(h.getLevel());restored.load(tag);h.getLevel().addFreshEntity(restored);
        });
        h.runAfterDelay(43,()->{
            var roots=h.getLevel().getEntitiesOfClass(RootSnare.class,new net.minecraft.world.phys.AABB(point).inflate(2));
            h.assertTrue(roots.size()==1&&roots.get(0).blockPosition().equals(point),"One cage appears at original locked point after reload");
            h.assertTrue(cow.getHealth()==200&&!cow.hasEffect(BlueprintEntities.ROOT_GRIP.get()),"Walking away during warning avoids roots");
        });
        h.runAfterDelay(95,()->{h.assertTrue(h.getLevel().getEntitiesOfClass(RootSnare.class,new net.minecraft.world.phys.AABB(point).inflate(2)).isEmpty(),"Finite cage cleans itself up");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=50,batch="tree")
    public static void wallBuiltDuringWarningBlocksRootCast(GameTestHelper h){
        var mob=tree(h);mob.setTreeAwake(true);var cow=enemy(h,7,11);h.assertTrue(mob.startSkill(ArmySkills.TREE_ROOTS,cow),"Clear cast starts");
        h.runAfterDelay(20,()->{for(int x=5;x<10;x++)for(int y=2;y<7;y++)h.setBlock(x,y,8,Blocks.STONE);});
        h.runAfterDelay(40,()->{h.assertTrue(h.getLevel().getEntitiesOfClass(RootSnare.class,mob.getBoundingBox().inflate(12)).isEmpty(),"New solid wall blocks roots, not merely their damage");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=145,batch="tree_effects")
    public static void twoPlayersCanBreakCageAndFiniteBindingLeavesOtherEffectsIntact(GameTestHelper h){
        var owner=tree(h);owner.setTreeAwake(true);var a=player(h,7,10);var b=player(h,12,10);RootSnare[] root={null};
        h.runAfterDelay(65,()->{
            b.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.IRON_AXE));
            root[0]=cage(h,owner,a.position());
        });
        h.runAfterDelay(92,()->{
            h.assertTrue(a.getHealth()<20&&a.hasEffect(BlueprintEntities.ROOT_GRIP.get()),"Nearby real player receives binding and suffocation");
            h.assertTrue(b.getHealth()==20&&!b.hasEffect(BlueprintEntities.ROOT_GRIP.get()),"Other player outside radius remains unaffected");
            h.assertTrue(!root[0].hurt(owner.damageSources().mobAttack(owner),20),"Woodland owner cannot break allied cage");
            a.addEffect(new net.minecraft.world.effect.MobEffectInstance(BlueprintEntities.SOUL_BIND.get(),60));
            h.assertTrue(root[0].hurt(a.damageSources().playerAttack(a),6)&&!root[0].isRemoved(),"Trapped player can damage physical cage");
            h.assertTrue(b.getAttributeValue(Attributes.ATTACK_DAMAGE)>=6,"Equipped axe attributes have reached native living tick");
            b.moveTo(a.position().add(1.5,0,0));b.attack(root[0]);
            h.assertTrue(root[0].isRemoved(),"Another player breaks same cage through real weapon attack");
        });
        h.runAfterDelay(110,()->{
            h.assertTrue(!a.hasEffect(BlueprintEntities.ROOT_GRIP.get())&&a.hasEffect(BlueprintEntities.SOUL_BIND.get()),"Broken cage stops refreshing grip without clearing unrelated bind");
            h.assertTrue(a.getAttributeValue(Attributes.MOVEMENT_SPEED)<.01,"Separate effect modifier still applies");
            a.removeEffect(BlueprintEntities.SOUL_BIND.get());h.assertTrue(a.getAttributeValue(Attributes.MOVEMENT_SPEED)>.09,"Movement restores after both bindings end");a.discard();b.discard();h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="tree")
    public static void expiredUnloadedCageCannotCatchUpAndOwnerDeathCleansLiveCage(GameTestHelper h){
        var owner=tree(h);var cow=enemy(h,7,10);var root=cage(h,owner,cow.position());var saved=new CompoundTag();
        root.save(saved);root.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
        h.runAfterDelay(70,()->{
            var restored=new RootSnare(BlueprintEntities.ROOT_SNARE.get(),h.getLevel());restored.load(saved);h.getLevel().addFreshEntity(restored);
            var live=cage(h,owner,cow.position());owner.kill();
            h.runAfterDelay(3,()->{h.assertTrue(restored.isRemoved()&&live.isRemoved()&&cow.getHealth()==200,"Expired and orphaned cages disappear before damage, with no catch-up pulses");h.succeed();});
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=80,batch="tree_caps")
    public static void livingCageReloadPreservesDamageExpiryAndSharedCap(GameTestHelper h){
        var owner=tree(h);owner.setTreeAwake(true);var cow=enemy(h,7,11);
        var first=cage(h,owner,Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(3,2,7))));
        var second=cage(h,owner,Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(11,2,7))));
        h.assertTrue(first.hurt(cow.damageSources().mobAttack(cow),7),"Existing cage accepts partial damage");
        var tag=new CompoundTag();first.save(tag);first.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
        var copy=new RootSnare(BlueprintEntities.ROOT_SNARE.get(),h.getLevel());copy.load(tag);h.getLevel().addFreshEntity(copy);
        h.assertTrue(owner.startSkill(ArmySkills.TREE_ROOTS,cow),"Cast begins while two existing cages are loaded");
        h.runAfterDelay(35,()->{
            h.assertTrue(h.getLevel().getEntitiesOfClass(RootSnare.class,owner.getBoundingBox().inflate(16)).size()==2,"Shared two-cage cap prevents another cast creating a third");
            h.assertTrue(copy.hurt(cow.damageSources().mobAttack(cow),5)&&copy.isRemoved(),"Reload preserves cage health instead of refreshing it");
        });
        h.runAfterDelay(65,()->{h.assertTrue(second.isRemoved(),"Remaining cage expires on original absolute deadline");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30,batch="tree_ecology")
    public static void realForestEcologyRequiresDirtLogsAndLocalCap(GameTestHelper h){
        tree(h).discard();var level=h.getLevel();var pos=h.absolutePos(new BlockPos(7,2,7));var a=h.absolutePos(new BlockPos(0,0,0));var b=h.absolutePos(new BlockPos(15,9,15));
        level.getServer().getCommands().performPrefixedCommand(level.getServer().createCommandSourceStack().withLevel(level).withPermission(4).withSuppressedOutput(),
            "fillbiome "+a.getX()+" "+a.getY()+" "+a.getZ()+" "+b.getX()+" "+b.getY()+" "+b.getZ()+" minecraft:dark_forest");
        var type=BlueprintEntities.KUMU_SHUJING.get();
        h.assertTrue(!BlueprintSpawns.treeHabitat(level,pos),"Bare stone does not host a tree spirit");h.setBlock(7,1,7,Blocks.DIRT);
        h.assertTrue(!BlueprintSpawns.treeHabitat(level,pos),"Dirt alone does not replace real woodland");for(int y=2;y<5;y++)h.setBlock(10,y,7,Blocks.DARK_OAK_LOG);
        h.assertTrue(net.minecraft.world.entity.SpawnPlacements.checkSpawnRules(type,level,net.minecraft.world.entity.MobSpawnType.NATURAL,pos,level.random),"Registered predicate accepts dry dark forest by logs");
        h.assertTrue(level.getBiome(pos).value().getMobSettings().getMobs(net.minecraft.world.entity.MobCategory.MONSTER).unwrap().stream().anyMatch(e->e.type==type&&e.minCount==1&&e.maxCount==1&&e.getWeight().asInt()==3),"Actual biome monster list contains authored weight and group size");
        var first=type.spawn(level,pos,net.minecraft.world.entity.MobSpawnType.NATURAL);var second=type.spawn(level,pos.offset(-3,0,0),net.minecraft.world.entity.MobSpawnType.NATURAL);
        h.assertTrue(first!=null&&second!=null&&!first.treeAwake()&&!first.isNoAi(),"Natural spawn creates active AI in camouflage");
        h.assertTrue(!BlueprintSpawns.treeHabitat(level,pos),"Two local trees prevent more spawns");first.discard();second.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=65,batch="tree_food")
    public static void mushroomConsumesNormallyAndBarkIsRealFurnaceFuel(GameTestHelper h){
        tree(h).discard();var p=player(h,7,7);p.getFoodData().setFoodLevel(18);var item=BlueprintSalvage.GLOWING_PARASITE_MUSHROOM.get();
        p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new net.minecraft.world.item.ItemStack(item,2));item.use(h.getLevel(),p,net.minecraft.world.InteractionHand.MAIN_HAND);
        h.runAfterDelay(40,()->{
            h.assertTrue(p.getMainHandItem().getCount()==1&&p.hasEffect(net.minecraft.world.effect.MobEffects.NIGHT_VISION)&&p.getFoodData().getFoodLevel()==20,"Actual completed use consumes one mushroom, feeds player and grants finite night vision");
            var bark=new net.minecraft.world.item.ItemStack(BlueprintSalvage.HARDENED_DEAD_BARK.get());
            h.assertTrue(net.minecraftforge.common.ForgeHooks.getBurnTime(bark,net.minecraft.world.item.crafting.RecipeType.SMELTING)==600,"Furnace hook accepts dead bark for three smelts");p.discard();h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="tree")
    public static void treeAndCageClipsParseWithMatchingServerClocks(GameTestHelper h) throws Exception {
        var gson=new com.google.gson.GsonBuilder().registerTypeAdapter(software.bernie.geckolib.loading.object.BakedAnimations.class,new software.bernie.geckolib.loading.json.typeadapter.BakedAnimationsAdapter()).create();
        for(String id:java.util.List.of("kumu_shujing","root_snare"))try(var stream=TreeGameTests.class.getResourceAsStream("/assets/dynasty/animations/blueprint/"+id+".animation.json")){
            var json=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(stream,java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject();
            var clips=gson.fromJson(json.getAsJsonObject("animations"),software.bernie.geckolib.loading.object.BakedAnimations.class);
            for(var name:id.equals("root_snare")?java.util.List.of("grow"):java.util.List.of("camouflage","wake","idle","walk","run","attack","roots","hurt","death"))
                h.assertTrue(clips.getAnimation("animation."+id+"."+name).boneAnimations().length>0,"Actual GeckoLib parser accepts "+id+" "+name);
            if(id.equals("root_snare"))h.assertTrue(clips.getAnimation("animation.root_snare.grow").length()==60,"Cage animation ends at server expiry");
            else h.assertTrue(clips.getAnimation("animation.kumu_shujing.attack").length()==42&&clips.getAnimation("animation.kumu_shujing.roots").length()==60,"Sweep and roots match server action lengths");
        }
        h.succeed();
    }
}
