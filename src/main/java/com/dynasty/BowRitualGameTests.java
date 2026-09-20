package com.dynasty;

import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.GameType;
import net.minecraftforge.event.entity.ProjectileImpactEvent;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public final class BowRitualGameTests {
    private static net.minecraftforge.common.util.FakePlayer testPlayer(GameTestHelper helper) {
        var player = new net.minecraftforge.common.util.FakePlayer(helper.getLevel(),
                new com.mojang.authlib.GameProfile(java.util.UUID.randomUUID(), "bow-test")) {
            @Override public boolean isInvulnerableTo(net.minecraft.world.damagesource.DamageSource source) { return false; }
            @Override public boolean hurt(net.minecraft.world.damagesource.DamageSource source, float amount) {
                if (DynastyBowRitual.isSolarDamage(source)) {
                    getPersistentData().putInt("solar_attempts",getPersistentData().getInt("solar_attempts")+1);
                }
                return super.hurt(source,amount);
            }
        };
        helper.getLevel().addNewPlayer(player);
        return player;
    }
    @GameTest(template = "bow_ritual_test", timeoutTicks = 60)
    public static void impactHalfHealthOnceAndExcludePlayer(GameTestHelper helper) {
        var level = helper.getLevel();
        var player = testPlayer(helper);
        player.setGameMode(GameType.SURVIVAL);
        Vec3 center = Vec3.atCenterOf(helper.absolutePos(new BlockPos(4,2,4)));
        player.setPos(center); player.setNoGravity(true);
        float initialPlayerHealth = player.getHealth();
        var sheep = helper.spawn(EntityType.SHEEP, 5,2,4);
        sheep.setNoAi(true); sheep.setNoGravity(true);
        sheep.getAttribute(Attributes.ARMOR).setBaseValue(20);
        var outside = helper.spawn(EntityType.SHEEP, 14,2,4);
        outside.setNoAi(true); outside.setNoGravity(true);
        float outsideHealth = outside.getHealth();
        Arrow arrow = new Arrow(level, player);
        arrow.setPos(center); arrow.setPierceLevel((byte)4);
        DynastyBowRitual.trackArrow(arrow, DynastyWeapons.HOUYI_BOW.get(), 308);
        var hit = new ProjectileImpactEvent(arrow,new EntityHitResult(sheep,center));
        DynastyBowRitual.onArrowImpact(hit);
        DynastyBowRitual.onArrowImpact(hit);
        helper.runAfterDelay(3, () -> {
            helper.assertTrue(Math.abs(sheep.getHealth()-sheep.getMaxHealth()*0.5F)<0.01F,
                    "A piercing arrow must deal exactly one half-health blast, including against armor");
            helper.assertTrue(player.getHealth()==initialPlayerHealth,"Area seal must exclude players");
            helper.assertTrue(player.getPersistentData().getInt("solar_attempts")==0,
                    "The area seal must not even attempt to damage a player");
            helper.assertTrue(outside.getHealth()==outsideHealth,"Outside targets must not be damaged");
            player.discard();
            helper.succeed();
        });
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void airborneWardStillProtects(GameTestHelper helper) {
        var player = helper.makeMockSurvivalPlayer();
        player.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(DynastyWeapons.HOUYI_BOW.get()));
        player.startUsingItem(InteractionHand.MAIN_HAND);
        player.setOnGround(false);
        DynastyBowRitual.onCharge(helper.getLevel(),player,DynastyWeapons.HOUYI_BOW.get(),20,308);
        LivingAttackEvent damage = new LivingAttackEvent(player,helper.getLevel().damageSources().generic(),5);
        DynastyBowRitual.onLivingAttack(damage);
        helper.assertTrue(damage.isCanceled(),"Airborne fully drawn bow must retain its ward");
        helper.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void homingRequiresVisibleEnemy(GameTestHelper helper) {
        var level = helper.getLevel();
        var player = testPlayer(helper);
        player.setPos(Vec3.atCenterOf(helper.absolutePos(new BlockPos(3,2,6))));
        var zombie = helper.spawn(EntityType.ZOMBIE,6,2,8);
        zombie.setNoAi(true); zombie.setNoGravity(true);
        Arrow arrow = new Arrow(level,player);
        arrow.setPos(Vec3.atCenterOf(helper.absolutePos(new BlockPos(4,2,4))));
        arrow.setDeltaMovement(0,0,3);
        DynastyBowRitual.home(level,arrow);
        helper.assertTrue(arrow.getDeltaMovement().x > 0,"Arrow must steer toward the nearby enemy");
        helper.assertTrue(Math.abs(arrow.getDeltaMovement().length()-3)<0.001,"Homing must preserve arrow speed");
        helper.setBlock(5,2,6,Blocks.STONE);
        helper.setBlock(5,3,6,Blocks.STONE);
        arrow.setDeltaMovement(0,0,3);
        DynastyBowRitual.home(level,arrow);
        helper.assertTrue(Math.abs(arrow.getDeltaMovement().x)<0.001,"Homing must not seek an enemy through a wall");
        player.discard(); helper.succeed();
    }

    @GameTest(template = "bow_ritual_test", timeoutTicks = 30)
    public static void avatarClearsOnlyItsShape(GameTestHelper helper) {
        var level = helper.getLevel();
        var player = testPlayer(helper);
        player.setGameMode(GameType.SURVIVAL);
        player.setYRot(0);
        player.setPos(Vec3.atBottomCenterOf(helper.absolutePos(new BlockPos(8,1,10))));
        BlockPos stone = helper.absolutePos(new BlockPos(8,6,6));
        BlockPos chest = helper.absolutePos(new BlockPos(8,7,6));
        BlockPos bedrock = helper.absolutePos(new BlockPos(8,8,6));
        BlockPos outside = helper.absolutePos(new BlockPos(3,6,6));
        level.setBlockAndUpdate(stone,Blocks.STONE.defaultBlockState());
        level.setBlockAndUpdate(chest,Blocks.CHEST.defaultBlockState());
        level.setBlockAndUpdate(bedrock,Blocks.BEDROCK.defaultBlockState());
        level.setBlockAndUpdate(outside,Blocks.STONE.defaultBlockState());
        DynastyBowRitual.clearAvatarSpace(level,player,1);
        helper.assertTrue(level.getBlockState(stone).isAir(),"Solid obstruction inside the apparition must be cleared");
        helper.assertTrue(level.getBlockState(chest).is(Blocks.CHEST),"Containers must survive");
        helper.assertTrue(level.getBlockState(bedrock).is(Blocks.BEDROCK),"Unbreakable blocks must survive");
        helper.assertTrue(level.getBlockState(outside).is(Blocks.STONE),"Blocks outside the silhouette must survive");
        player.discard();
        helper.succeed();
    }
}
