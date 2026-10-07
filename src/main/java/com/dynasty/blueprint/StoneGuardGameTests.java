package com.dynasty.blueprint;

import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class StoneGuardGameTests {
    private static TemplateMob guard(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=7;y++)h.setBlock(x,y,z,y==1?Blocks.STONE:Blocks.AIR);
        var mob=h.spawn(BlueprintEntities.JUBI_SHIGANDANG.get(),new BlockPos(7,2,5));mob.setNoAi(true);mob.setNoGravity(true);return mob;
    }
    private static net.minecraft.world.entity.animal.Cow cow(GameTestHelper h,int x,int z){
        var e=h.spawn(EntityType.COW,new BlockPos(x,2,z));e.setNoAi(true);e.setNoGravity(true);
        e.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);e.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);e.setHealth(200);return e;
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=70,batch="stone_guard")
    public static void thirtyTickSlamHitsOnlyThreeBlockStripOnceAndNeverBreaksTerrain(GameTestHelper h){
        var mob=guard(h);var front=cow(h,7,8);var side=cow(h,9,7);var rear=cow(h,7,3);var far=cow(h,7,10);
        h.assertTrue(mob.startSkill(ArmySkills.STONE_SLAM,front),"Starts actual heavy slam");
        h.runAfterDelay(28,()->h.assertTrue(front.getHealth()==200,"Full 1.5-second tell has no damage"));
        h.runAfterDelay(34,()->h.assertTrue(Math.abs(front.getHealth()-187.2)<.01&&side.getHealth()==200&&rear.getHealth()==200&&far.getHealth()==200,"One 12.8 damage contact, bounded strip only"));
        h.runAfterDelay(63,()->{h.assertTrue(Math.abs(front.getHealth()-187.2)<.01&&mob.skillId()==0,"No recovery damage");h.assertBlockPresent(Blocks.STONE,new BlockPos(7,1,8));h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=55,batch="stone_guard")
    public static void dodgingSlamTellLeavesAttackDirectionLocked(GameTestHelper h){
        var mob=guard(h);var target=cow(h,7,8);mob.startSkill(ArmySkills.STONE_SLAM,target);
        h.runAfterDelay(25,()->target.setPos(mob.position().add(2,0,1)));
        h.runAfterDelay(36,()->{h.assertTrue(target.getHealth()==200,"Sidestep escapes line rather than rotating warning toward player");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=55,batch="stone_guard")
    public static void heavyWindupHitCancelsPendingSlam(GameTestHelper h){
        var mob=guard(h);var target=cow(h,7,8);mob.startSkill(ArmySkills.STONE_SLAM,target);
        h.runAfterDelay(15,()->mob.hurt(mob.damageSources().mobAttack(target),20));
        h.runAfterDelay(40,()->{h.assertTrue(target.getHealth()==200&&!mob.startSkill(ArmySkills.STONE_SLAM,target),"Stagger cancels contact without clearing cooldown");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=50,batch="stone_guard")
    public static void wallBuiltDuringTellBlocksShockwave(GameTestHelper h){
        var mob=guard(h);var target=cow(h,7,8);mob.startSkill(ArmySkills.STONE_SLAM,target);
        h.runAfterDelay(24,()->{for(int x=6;x<=8;x++)for(int y=2;y<=5;y++)h.setBlock(x,y,7,Blocks.STONE);});
        h.runAfterDelay(36,()->{h.assertTrue(target.getHealth()==200,"New solid wall blocks contact");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30,batch="stone_guard")
    public static void authoredStructureSpawnHonoursMembershipAndSolidFloor(GameTestHelper h){
        var fixture=guard(h);fixture.discard();var level=h.getLevel();var pos=h.absolutePos(new BlockPos(7,2,7));var entrant=pos.offset(8,0,0);String key="test-stone-"+UUID.randomUUID();
        h.setBlock(7,1,7,Blocks.AIR);h.assertTrue(!BlueprintSpawns.spawnStoneGuard(level,key,pos,entrant),"No floating stone warden");h.setBlock(7,1,7,Blocks.STONE);
        h.assertTrue(BlueprintSpawns.spawnStoneGuard(level,key,pos,entrant),"Loaded authored forecourt spawns one warden");
        h.assertTrue(!BlueprintSpawns.spawnStoneGuard(level,key,pos,entrant),"Marker prevents duplicate/repeated entrant spawns");
        var state=BlueprintSpawnState.get(level);h.assertTrue(state.markers.get(key).members.size()==1,"Exactly one encounter member is recorded");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60,batch="stone_guard")
    public static void heavyContactDisablesRaisedShieldOnlyAtImpact(GameTestHelper h){
        var mob=guard(h);
        var player=new net.minecraft.server.level.ServerPlayer(h.getLevel().getServer(),h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"stone-shield"));
        player.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),player);
        player.moveTo(mob.position().add(0,0,2.5));player.setYRot(180);
        h.getLevel().addNewPlayer(player);h.onEachTick(()->{if(!player.isRemoved())player.doTick();});
        player.setItemInHand(net.minecraft.world.InteractionHand.OFF_HAND,new net.minecraft.world.item.ItemStack(net.minecraft.world.item.Items.SHIELD));
        player.startUsingItem(net.minecraft.world.InteractionHand.OFF_HAND);
        h.runAfterDelay(8,()->{h.assertTrue(player.isBlocking(),"Player raises real off-hand shield");h.assertTrue(mob.startSkill(ArmySkills.STONE_SLAM,player),"Starts against shield");});
        h.runAfterDelay(32,()->h.assertTrue(player.isBlocking()&&!player.getCooldowns().isOnCooldown(net.minecraft.world.item.Items.SHIELD),"Tell never disables shield early"));
        h.runAfterDelay(42,()->{h.assertTrue(!player.isBlocking()&&player.getCooldowns().isOnCooldown(net.minecraft.world.item.Items.SHIELD),"Authored heavy contact breaks raised shield");player.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="stone_guard")
    public static void stoneRigClipsLoadThroughGeckoLib(GameTestHelper h) throws Exception {
        var gson=new com.google.gson.GsonBuilder().registerTypeAdapter(software.bernie.geckolib.loading.object.BakedAnimations.class,new software.bernie.geckolib.loading.json.typeadapter.BakedAnimationsAdapter()).create();
        try(var stream=StoneGuardGameTests.class.getResourceAsStream("/assets/dynasty/animations/blueprint/jubi_shigandang.animation.json")){
            var json=com.google.gson.JsonParser.parseReader(new java.io.InputStreamReader(stream,java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject();
            var clips=gson.fromJson(json.getAsJsonObject("animations"),software.bernie.geckolib.loading.object.BakedAnimations.class);
            for(var name:java.util.List.of("idle","walk","run","attack","slam","hurt","death"))h.assertTrue(clips.getAnimation("animation.jubi_shigandang."+name).boneAnimations().length>0,"Parsed "+name);
            h.assertTrue(clips.getAnimation("animation.jubi_shigandang.slam").length()==60,"Slam clip matches server clock");
        }h.succeed();
    }
}
