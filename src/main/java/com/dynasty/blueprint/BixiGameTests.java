package com.dynasty.blueprint;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.*;
@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class BixiGameTests {
    private static TemplateMob bixi(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=8;y++)h.setBlock(x,y,z,y==1||y==8||x==0||x==15||z==0||z==15?Blocks.STONE:Blocks.AIR);
        var mob=h.spawn(BlueprintEntities.JULI_BIXI_KUILEI.get(),new BlockPos(7,2,7));mob.setNoAi(true);mob.setNoGravity(true);return mob;
    }
    private static net.minecraft.world.entity.animal.Cow cow(GameTestHelper h,int x,int z){var c=h.spawn(EntityType.COW,new BlockPos(x,2,z));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);c.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);c.setHealth(200);return c;}
    @GameTest(template="bow_ritual_test",timeoutTicks=85,batch="bixi")
    public static void stompWarnsHitsCircleOnceAndReleasesShortStagger(GameTestHelper h){
        var mob=bixi(h);var front=cow(h,7,10);var rear=cow(h,7,3);var outside=cow(h,14,7);
        h.assertTrue(mob.startSkill(ArmySkills.BIXI_STOMP,front),"Starts32tick stomp");
        h.runAfterDelay(30,()->h.assertTrue(front.getHealth()==200&&rear.getHealth()==200,"Long tell is harmless"));
        h.runAfterDelay(36,()->h.assertTrue(front.getHealth()==188&&rear.getHealth()==188&&outside.getHealth()==200&&front.hasEffect(BlueprintEntities.HEAVY_STAGGER.get()),"Single circular contact5blocks and finite stagger"));
        h.runAfterDelay(75,()->{h.assertTrue(front.getHealth()==188&&!front.hasEffect(BlueprintEntities.HEAVY_STAGGER.get()),"No repeated damage or permanent movement impairment: hp="+front.getHealth()+" stagger="+front.hasEffect(BlueprintEntities.HEAVY_STAGGER.get()));h.assertBlockPresent(Blocks.STONE,new BlockPos(7,1,10));h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60,batch="bixi")
    public static void lateWallAndLeavingRadiusAvoidStomp(GameTestHelper h){
        var mob=bixi(h);var blocked=cow(h,7,10);var dodge=cow(h,4,7);mob.startSkill(ArmySkills.BIXI_STOMP,blocked);
        h.runAfterDelay(25,()->{for(int x=5;x<10;x++)for(int y=2;y<6;y++)h.setBlock(x,y,9,Blocks.STONE);dodge.setPos(mob.getX()+6,dodge.getY(),dodge.getZ());});
        h.runAfterDelay(40,()->{h.assertTrue(blocked.getHealth()==200&&dodge.getHealth()==200,"Wall and actual dodge both evade contact: blocked="+blocked.getHealth()+" dodge="+dodge.getHealth());h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30,batch="bixi")
    public static void statuePresetNeverOverwritesBlocksOrTrapsAnOccupant(GameTestHelper h){
        bixi(h).discard();var level=h.getLevel();var p=h.absolutePos(new BlockPos(7,2,7));String site="dynasty:imperial_tomb@1";
        h.assertTrue(!BixiBehavior.placeRemnant(level,p,""),"Spawn eggs cannot manufacture permanent ruins");
        h.setBlock(7,2,7,Blocks.CHEST);h.assertTrue(!BixiBehavior.placeRemnant(level,p,site),"Never overwrite player's block entity");h.setBlock(7,2,7,Blocks.AIR);
        var occupant=cow(h,7,7);h.assertTrue(!BixiBehavior.placeRemnant(level,p,site),"Never place inside a living occupant");occupant.discard();
        h.assertTrue(BixiBehavior.placeRemnant(level,p,site),"Free floor becomes ordinary two-block preset");
        h.assertTrue(level.getBlockState(p).is(com.dynasty.DynastyBlocks.BIXI_STELE.get())&&level.getBlockState(p.above()).is(com.dynasty.DynastyBlocks.BIXI_STELE.get()),"Actual registered monument blocks");
        h.assertTrue(!BixiBehavior.placeRemnant(level,p,site),"Repeated death load cannot place another remnant");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=80,batch="bixi")
    public static void deathPlacesOneRemnantAndRemovesMobAfterReload(GameTestHelper h){
        var mob=bixi(h);mob.bindEncounter("dynasty:imperial_tomb@2:bixi");var p=mob.blockPosition();
        mob.hurt(mob.damageSources().genericKill(),10000);var saved=new CompoundTag();
        h.runAfterDelay(34,()->{h.assertTrue(h.getLevel().getBlockState(p).is(com.dynasty.DynastyBlocks.BIXI_STELE.get()),"Death converts to preset");mob.save(saved);mob.discard();var copy=BlueprintEntities.JULI_BIXI_KUILEI.get().create(h.getLevel());copy.load(saved);h.getLevel().addFreshEntity(copy);
            h.runAfterDelay(20,()->{h.assertTrue(copy.isRemoved()&&saved.getCompound("ArmyActionState").getBoolean("RemnantAttempted"),"Dead entity cleanup and persisted one-shot conversion");h.succeed();});});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="bixi")
    public static void nativeRigClipsAndSingleEncounterCap(GameTestHelper h)throws Exception{
        bixi(h).discard();var p=h.absolutePos(new BlockPos(7,2,7));var key="bixi-test-"+java.util.UUID.randomUUID();
        h.assertTrue(BlueprintSpawns.spawnBixi(h.getLevel(),key,p,p.offset(8,0,0)),"One real authored guardian");h.assertTrue(!BlueprintSpawns.spawnBixi(h.getLevel(),key,p,p.offset(8,0,0)),"Persisted cap prevents duplicate");
        var gson=new com.google.gson.GsonBuilder().registerTypeAdapter(software.bernie.geckolib.loading.object.BakedAnimations.class,new software.bernie.geckolib.loading.json.typeadapter.BakedAnimationsAdapter()).create();
        try(var in=BixiGameTests.class.getResourceAsStream("/assets/dynasty/animations/blueprint/juli_bixi_kuilei.animation.json")){
            var json=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(in)).getAsJsonObject();var clips=gson.fromJson(json.get("animations"),software.bernie.geckolib.loading.object.BakedAnimations.class);
            for(var n:java.util.List.of("idle","walk","run","attack","stomp","hurt","death"))h.assertTrue(clips.getAnimation("animation.juli_bixi_kuilei."+n).boneAnimations().length>0,"Parses "+n);
        }h.succeed();
    }
}
