package com.dynasty.expansion;

import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;
import java.util.UUID;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class SecondarySkillGameTests {
    private static SecondaryMob mob(GameTestHelper h,String id,BlockPos pos){
        var mob=SecondaryMobs.TYPES.get(id).get().create(h.getLevel());mob.setNoAi(true);mob.setNoGravity(true);
        mob.setPos(Vec3.atBottomCenterOf(h.absolutePos(pos)));h.getLevel().addFreshEntity(mob);return mob;
    }
    private static Zombie victim(GameTestHelper h,BlockPos pos){
        var z=new Zombie(h.getLevel());z.setNoAi(true);z.setNoGravity(true);z.getAttribute(Attributes.MAX_HEALTH).setBaseValue(500);z.setHealth(500);
        z.setPos(Vec3.atBottomCenterOf(h.absolutePos(pos)));h.getLevel().addFreshEntity(z);return z;
    }
    private static void corridor(GameTestHelper h){
        for(int x=1;x<=12;x++)for(int z=1;z<=5;z++)for(int y=1;y<=6;y++)h.setBlock(x,y,z,y==1||y==6?Blocks.STONE:Blocks.AIR);
    }
    @GameTest(template="bow_ritual_test",batch="cod4_projectile_wall",timeoutTicks=80)
    public static void lanternCannotBlindBeforeHitOrThroughWall(GameTestHelper h){
        corridor(h);var mob=mob(h,"lantern_ghost",new BlockPos(3,2,3));var z=victim(h,new BlockPos(9,2,3));
        var ball=mob.fireSkillProjectile(z);
        h.assertTrue(ball!=null&&ball.kind()==SecondaryProjectile.LIGHT&&!z.hasEffect(MobEffects.BLINDNESS),"Launching a light ball does not directly blind a target");
        for(int y=2;y<6;y++)for(int dz=2;dz<=4;dz++)h.setBlock(6,y,dz,Blocks.STONE);
        h.runAfterDelay(12,()->{try{
            h.assertTrue(ball.isRemoved()&&!z.hasEffect(MobEffects.BLINDNESS)&&!z.hasEffect(ExpansionEffects.SOUL.get()),"Wall consumes actual projectile before any hit effect");
            h.assertTrue(mob.fireSkillProjectile(z)==null,"Occluded targets cannot initiate another shot");h.succeed();
        }finally{mob.discard();z.discard();ball.discard();}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_projectile_hit",timeoutTicks=100)
    public static void realLanternProjectileAppliesEffectsOnlyAtContact(GameTestHelper h){
        corridor(h);var mob=mob(h,"lantern_ghost",new BlockPos(3,2,3));var z=victim(h,new BlockPos(9,2,3));var ball=mob.fireSkillProjectile(z);
        h.assertTrue(ball!=null&&!z.hasEffect(MobEffects.BLINDNESS),"No instant ranged status");
        h.startSequence().thenWaitUntil(()->h.assertTrue(ball.isRemoved(),"Wait for actual projectile collision"))
        .thenExecute(()->{try{
            h.assertTrue(z.hasEffect(MobEffects.BLINDNESS)&&z.hasEffect(ExpansionEffects.SOUL.get())&&z.getHealth()<500,"Real hit owns damage, blindness and soul burn");
            h.succeed();
        }finally{mob.discard();z.discard();ball.discard();}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_projectile_variants")
    public static void seedWaterAndStoneKeepDistinctKindsAndBoundedLifetime(GameTestHelper h){
        corridor(h);var target=victim(h,new BlockPos(9,2,3));
        String[] names={"tree_spirit","river_imp","jingwei_bird"};int[] kinds={SecondaryProjectile.SEED,SecondaryProjectile.WATER,SecondaryProjectile.STONE};
        for(int i=0;i<names.length;i++){
            var source=mob(h,names[i],new BlockPos(3,2,3));var shot=source.fireSkillProjectile(target);
            try{
                h.assertTrue(shot!=null&&shot.kind()==kinds[i],"Authored skill has its own real projectile kind: "+names[i]);
                var tag=new net.minecraft.nbt.CompoundTag();shot.addAdditionalSaveData(tag);tag.putInt("Cod4ProjectileAge",40);shot.readAdditionalSaveData(tag);shot.tick();
                h.assertTrue(shot.isRemoved(),"Reloaded projectiles retain their forty-tick lifetime");
            }finally{source.discard();if(shot!=null)shot.discard();}
        }
        target.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_projectile_windup")
    public static void rangedAnimationWindupHasOneLaunchAndCanBeOccluded(GameTestHelper h){
        corridor(h);var source=mob(h,"lantern_ghost",new BlockPos(3,2,3));var target=victim(h,new BlockPos(9,2,3));
        try{
            h.assertTrue(source.beginRangedSkill(target),"Visible target starts a telegraphed action");
            for(int i=0;i<5;i++)source.tickRangedSkill();
            h.assertTrue(h.getLevel().getEntitiesOfClass(SecondaryProjectile.class,source.getBoundingBox().inflate(2)).isEmpty(),"No projectile before the six-tick animation release frame");
            source.tickRangedSkill();var shots=h.getLevel().getEntitiesOfClass(SecondaryProjectile.class,source.getBoundingBox().inflate(2),p->p.getOwner()==source);
            h.assertTrue(shots.size()==1,"Release frame creates one logical projectile");for(var shot:shots)shot.discard();
            for(int i=0;i<10;i++)source.tickRangedSkill();h.assertTrue(!target.hasEffect(MobEffects.BLINDNESS),"Finishing animation does not manufacture direct damage");
            h.assertTrue(source.beginRangedSkill(target),"A later action starts independently");for(int y=2;y<6;y++)for(int z=2;z<=4;z++)h.setBlock(6,y,z,Blocks.STONE);
            for(int i=0;i<6;i++)source.tickRangedSkill();
            h.assertTrue(h.getLevel().getEntitiesOfClass(SecondaryProjectile.class,source.getBoundingBox().inflate(2),p->p.getOwner()==source).isEmpty(),"A wall placed during windup cancels the launch");h.succeed();
        }finally{source.discard();target.discard();}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_seed_contact",timeoutTicks=100)
    public static void actualSeedContactRootsInsteadOfUsingAnArrow(GameTestHelper h){
        corridor(h);var source=mob(h,"tree_spirit",new BlockPos(3,2,3));var target=victim(h,new BlockPos(9,2,3));var seed=source.fireSkillProjectile(target);
        h.startSequence().thenWaitUntil(()->h.assertTrue(seed.isRemoved(),"Wait for real seed contact"))
        .thenExecute(()->{try{h.assertTrue(target.hasEffect(ExpansionEffects.STAGGER.get())&&target.getHealth()<500,"Seed hit owns root restriction and real damage");h.succeed();}
            finally{source.discard();target.discard();seed.discard();}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_water_drag",timeoutTicks=100)
    public static void shoreDragMovesTowardRealWaterAndStopsAfterFiniteWindow(GameTestHelper h){
        corridor(h);var source=mob(h,"river_imp",new BlockPos(3,2,3));var target=victim(h,new BlockPos(7,2,3));
        h.assertTrue(!source.beginWaterDrag(target),"Dry ground cannot invent a water destination");
        h.setBlock(3,2,3,Blocks.WATER);h.setBlock(3,1,3,Blocks.STONE);
        h.assertTrue(source.beginWaterDrag(target),"Shore target binds to a loaded visible water site");
        for(int i=0;i<30;i++)source.tickWaterDrag();
        h.assertTrue(target.getDeltaMovement().x<0&&target.getDeltaMovement().horizontalDistance()<=.25001,"Pull is toward water with finite bounded force");
        target.setDeltaMovement(Vec3.ZERO);source.tickWaterDrag();h.assertTrue(target.getDeltaMovement().lengthSqr()==0,"Expired drag cannot keep controlling movement");
        source.discard();target.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_guard_asset")
    public static void oldAccessoryLeaseCannotDiscardPurchasedCarrier(GameTestHelper h){
        var owner=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"guard-owner"));
        var soldier=com.dynasty.entity.DynastyEntities.IMPERIAL_SOLDIER.get().create(h.getLevel());soldier.setOwner(owner);
        soldier.getPersistentData().putUUID("ArmySoldier",UUID.randomUUID());soldier.getPersistentData().putLong("cod4TallyExpires",h.getLevel().getGameTime()-1);
        AccessoryActions.expire(new net.minecraftforge.event.entity.living.LivingEvent.LivingTickEvent(soldier));
        h.assertTrue(!soldier.isRemoved()&&!soldier.getPersistentData().contains("cod4TallyExpires"),"Paid roster assets ignore and clear old summon timers");
        var legacy=com.dynasty.entity.DynastyEntities.IMPERIAL_SOLDIER.get().create(h.getLevel());legacy.getPersistentData().putLong("cod4TallyExpires",h.getLevel().getGameTime()-1);
        AccessoryActions.expire(new net.minecraftforge.event.entity.living.LivingEvent.LivingTickEvent(legacy));h.assertTrue(legacy.isRemoved(),"Genuine old temporary summons still expire");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_water_entry",timeoutTicks=100)
    public static void realShoreDragEntersWaterAndDoesNotPullBosses(GameTestHelper h){
        corridor(h);var source=mob(h,"drowning_ghost",new BlockPos(3,2,3));var target=victim(h,new BlockPos(6,2,3));
        // NoAI also disables vanilla travel; retain actual physics but remove autonomous goals.
        target.setNoAi(false);target.goalSelector.removeAllGoals(g->true);target.targetSelector.removeAllGoals(g->true);
        target.getAttribute(Attributes.MOVEMENT_SPEED).setBaseValue(0);
        for(int x=2;x<=4;x++)for(int z=2;z<=4;z++)h.setBlock(x,2,z,Blocks.WATER);
        var boss=com.dynasty.entity.DynastyEntities.DRAGON_KING.get().create(h.getLevel());boss.setPos(target.position());
        h.assertTrue(!source.beginWaterDrag(boss)&&boss.getDeltaMovement().lengthSqr()==0,"Boss control immunity rejects the pull before binding");
        h.assertTrue(source.beginWaterDrag(target),"Actual shore victim binds to authored water");
        h.startSequence().thenWaitUntil(()->h.assertTrue(target.isInWater(),"Real server movement brings the shore victim into water"))
        .thenExecute(()->{try{h.assertTrue(target.getX()<h.absolutePos(new BlockPos(6,2,3)).getX()+.5,"Water entry came from bounded movement toward the pool");h.succeed();}finally{source.discard();target.discard();boss.discard();}});
    }
    private SecondarySkillGameTests(){}
}
