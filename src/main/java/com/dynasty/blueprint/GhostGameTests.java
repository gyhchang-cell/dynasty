package com.dynasty.blueprint;

import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class GhostGameTests {
    private static TemplateMob ghost(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++){
            h.setBlock(x,1,z,Blocks.STONE);
            for(int y=2;y<=10;y++)h.setBlock(x,y,z,y==10?Blocks.STONE:Blocks.AIR);
        }
        var mob=h.spawn(BlueprintEntities.YINBING_GUIZU.get(),new BlockPos(7,2,7));mob.setNoAi(true);mob.setNoGravity(true);return mob;
    }
    private static Cow target(GameTestHelper h){
        var target=h.spawn(EntityType.COW,new BlockPos(7,2,9));target.setNoAi(true);target.setNoGravity(true);
        target.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);target.setHealth(200);target.setYRot(0);return target;
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40,batch="ghost")
    public static void physicalPhaseHasFiniteImmunityAndPersistentCooldown(GameTestHelper h){
        var ghost=ghost(h);var target=target(h);var initial=ghost.position();float hp=ghost.getHealth();
        h.assertTrue(net.minecraft.util.RandomSource.create(4096).nextFloat()<.35F,"Fixture seed selects the authored 35% branch");
        ghost.getRandom().setSeed(4096);
        h.assertTrue(!ghost.hurt(ghost.damageSources().mobAttack(target),4)&&ghost.isPhased(),"Real melee hit enters evasion");
        h.assertTrue(ghost.position().distanceTo(initial)>2&&!ghost.noPhysics,"Evasion selects a real standing point without noPhysics");
        h.assertTrue(!ghost.isPickable()&&!ghost.canBeHitByProjectile(),"Six-tick phase is untargetable");
        h.assertTrue(!ghost.hurt(ghost.damageSources().mobAttack(target),4)&&ghost.getHealth()==hp,"Active phase prevents duplicate hit");
        h.runAfterDelay(8,()->{
            h.assertTrue(!ghost.isPhased()&&ghost.isPickable(),"Targetability returns after six ticks");
            var saved=new CompoundTag();ghost.save(saved);var uuid=ghost.getUUID();ghost.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            var copy=BlueprintEntities.YINBING_GUIZU.get().create(h.getLevel());copy.load(saved);h.getLevel().addFreshEntity(copy);
            copy.getRandom().setSeed(4096);copy.invulnerableTime=0;
            h.assertTrue(copy.getUUID().equals(uuid)&&copy.hurt(copy.damageSources().mobAttack(target),4)&&!copy.isPhased(),"Reload retains cooldown; same chance roll cannot phase twice");
            h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=25,batch="ghost")
    public static void blockedPhaseCannotEscapeThroughSolidWalls(GameTestHelper h){
        var ghost=ghost(h);var target=target(h);var initial=ghost.position();
        for(int x:new int[]{4,10})for(int y=2;y<6;y++)for(int z=8;z<=10;z++)h.setBlock(x,y,z,Blocks.STONE);
        h.assertTrue(ArmyBehaviors.phaseLanding(ghost,target)==null,"Both side candidates blocked at all supported heights");
        ghost.getRandom().setSeed(4096);
        h.assertTrue(ghost.hurt(ghost.damageSources().mobAttack(target),4)&&!ghost.isPhased(),"No legal landing means ordinary accepted damage");
        h.assertTrue(ghost.position().equals(initial)&&!ghost.noPhysics,"Failed blink never clips or teleports");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=25,batch="ghost")
    public static void ghostPassesOrdinaryEntitiesButCollidesWithBlocksAndBosses(GameTestHelper h){
        var ghost=ghost(h);var cow=target(h);
        ghost.move(MoverType.SELF,new Vec3(0,0,2));
        h.assertTrue(ghost.getBoundingBox().intersects(cow.getBoundingBox()),"Ordinary body does not block ghost movement");
        ghost.push(cow);h.assertTrue(cow.getDeltaMovement().lengthSqr()==0,"Ghost does not shove ordinary entities");
        for(int x=6;x<=8;x++)for(int y=2;y<=5;y++)h.setBlock(x,y,11,Blocks.STONE);
        ghost.move(MoverType.SELF,new Vec3(0,0,4));
        h.assertTrue(ghost.getZ()<h.absolutePos(new BlockPos(7,2,11)).getZ(),"Solid wall still blocks physical movement");
        var boss=h.spawn(com.dynasty.entity.DynastyEntities.REBEL_GENERAL.get(),new BlockPos(11,2,7));boss.setNoAi(true);boss.setNoGravity(true);
        ghost.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(8,2,7))));ghost.move(MoverType.SELF,new Vec3(3,0,0));
        h.assertTrue(!ghost.getBoundingBox().intersects(boss.getBoundingBox()),"Boss body remains solid to the ghost");
        boss.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=85,batch="ghost")
    public static void frostThrustBypassesArmourAndAttackSpeedEffectExpires(GameTestHelper h){
        var ghost=ghost(h);var target=target(h);target.getAttribute(Attributes.ARMOR).setBaseValue(100);
        var player=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"ghost-chill")){
            @Override public boolean isCreative(){return true;}
        };
        player.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(2,2,2))));h.getLevel().addNewPlayer(player);
        // FakePlayer.tick is deliberately empty. Drive the real ServerPlayer living tick,
        // which normally comes from its network listener, to verify timed attribute expiry.
        h.onEachTick(()->{if(!player.isRemoved())player.doTick();});
        double original=player.getAttributeValue(Attributes.ATTACK_SPEED);
        player.addEffect(new net.minecraft.world.effect.MobEffectInstance(BlueprintEntities.SPIRIT_CHILL.get(),60));
        h.assertTrue(Math.abs(player.getAttributeValue(Attributes.ATTACK_SPEED)-original*.75)<.001,"Real attack speed drops by25%, not mining speed");
        h.assertTrue(ghost.startSkill(ArmySkills.GHOST_THRUST,target),"Server starts spectral thrust");
        h.runAfterDelay(12,()->h.assertTrue(target.getHealth()==200,"No damage during warning"));
        h.runAfterDelay(18,()->h.assertTrue(target.getHealth()==195&&target.hasEffect(BlueprintEntities.SPIRIT_CHILL.get()),"One magic contact bypasses100 armour and applies frost"));
        h.runAfterDelay(78,()->{
            h.assertTrue(target.getHealth()==195&&!target.hasEffect(BlueprintEntities.SPIRIT_CHILL.get()),"No repeat contact; frost expires");
            h.assertTrue(Math.abs(player.getAttributeValue(Attributes.ATTACK_SPEED)-original)<.001,"Actual player attribute is restored");
            player.discard();h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=25,batch="ghost")
    public static void ghostSalvageRecipeRunsInRealCraftingMenu(GameTestHelper h){
        var player=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"ghost-salvage"));
        var menu=new net.minecraft.world.inventory.CraftingMenu(0,player.getInventory(),
            net.minecraft.world.inventory.ContainerLevelAccess.create(h.getLevel(),h.absolutePos(new BlockPos(2,2,2))));
        for(int i=1;i<=4;i++)menu.getSlot(i).set(new net.minecraft.world.item.ItemStack(BlueprintSalvage.ANCIENT_COIN_RUST.get()));
        var output=menu.getSlot(0).getItem();
        h.assertTrue(output.is(com.dynasty.DynastyItems.COPPER_COIN.get())&&output.getCount()==1,"Recipe manager produces an actual coin from four fragments");
        output=menu.getSlot(0).remove(1);menu.getSlot(0).onTake(player,output);
        for(int i=1;i<=4;i++)h.assertTrue(menu.getSlot(i).getItem().isEmpty(),"Crafting consumes exactly four recovered fragments");
        h.succeed();
    }
}
