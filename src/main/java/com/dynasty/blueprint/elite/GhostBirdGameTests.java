package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.*;
import com.dynasty.blueprint.combat.AttackState;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class GhostBirdGameTests {
    private static GhostCarriageBird bird(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++){
            h.setBlock(x,1,z,Blocks.STONE);for(int y=2;y<=13;y++)h.setBlock(x,y,z,Blocks.AIR);
        }
        var bird=h.spawn(EliteContent.BIRD.get(),new BlockPos(7,5,7));bird.setNoAi(true);return bird;
    }
    private static Cow target(GameTestHelper h,int x,int z){var cow=h.spawn(EntityType.COW,new BlockPos(x,2,z));cow.setNoAi(true);cow.setNoGravity(true);cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);cow.setHealth(1000);return cow;}
    @GameTest(template="bow_ritual_test",timeoutTicks=110,batch="ghost_bird")
    public static void sixteenPecksHaveAFullTellAndARealSideEscape(GameTestHelper h){
        var bird=bird(h);var hit=target(h,7,7);var side=target(h,12,7);
        h.assertTrue(bird.startSkill(311,hit),"Real bird peck starts above target");
        h.runAfterDelay(10,()->h.assertTrue(hit.getHealth()==1000,"No contact during the 0.6-second neck contraction"));
        h.runAfterDelay(78,()->h.assertTrue(Math.abs(hit.getHealth()-936)<.01&&side.getHealth()==1000,"Exactly sixteen independent pecks and no hit beyond the locked 2.5-block circle; hp="+hit.getHealth()));
        h.runAfterDelay(101,()->{h.assertTrue(bird.skillId()==0&&!bird.startSkill(311,hit),"Peck recovery ends and cooldown remains spent");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=115,batch="ghost_bird")
    public static void eightBloodCellsAreOwnedFiniteAndNeverReplayedOnReload(GameTestHelper h){
        var bird=bird(h);var hit=target(h,7,13);h.assertTrue(bird.startSkill(312,hit),"One-second blood warning starts");
        h.runAfterDelay(18,()->h.assertTrue(h.getLevel().getEntitiesOfClass(SkullBloodPool.class,bird.getBoundingBox().inflate(16)).isEmpty(),"No early blood cloud"));
        h.runAfterDelay(23,()->{
            var cells=h.getLevel().getEntitiesOfClass(SkullBloodPool.class,bird.getBoundingBox().inflate(16),p->p.ownedBy(bird));
            h.assertTrue(cells.size()==8,"Eight actual bounded landing cells, not eight persistent projectile actors; count="+cells.size());
            var saved=new CompoundTag();bird.save(saved);var id=bird.getUUID();bird.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            var restored=EliteContent.BIRD.get().create(h.getLevel());restored.load(saved);h.getLevel().addFreshEntity(restored);
            h.runAtTickTime(55,()->{h.assertTrue(restored.getUUID().equals(id)&&h.getLevel().getEntitiesOfClass(SkullBloodPool.class,restored.getBoundingBox().inflate(20),p->p.ownedBy(restored)).size()==8,"NBT restores the same owner without replaying the consumed barrage");});
            h.runAtTickTime(110,()->{h.assertTrue(h.getLevel().getEntitiesOfClass(SkullBloodPool.class,restored.getBoundingBox().inflate(24),p->p.ownedBy(restored)).isEmpty(),"Absolute four-second expiry survives owner reload");h.succeed();});
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=65,batch="ghost_bird")
    public static void CaptiveCanBreakFreeWithAnAcceptedHitAndKeepsFallProtection(GameTestHelper h){
        var bird=bird(h);var hit=target(h,7,13);h.assertTrue(bird.startSkill(313,hit),"Native diving action begins");
        h.runAfterDelay(40,()->{
            h.assertTrue(bird.captiveId()==hit.getId()&&hit.hasEffect(MobEffects.SLOW_FALLING),"Actual collision catches one target and grants finite fall protection");
            h.assertTrue(bird.hurt(bird.damageSources().mobAttack(hit),4),"Real counter hit accepted");
            h.assertTrue(bird.captiveId()==-1&&bird.phase()==AttackState.STUN&&hit.hasEffect(MobEffects.SLOW_FALLING),"Counter breaks the grab and leaves a two-second punish window");
        });
        h.runAfterDelay(61,()->{h.assertTrue(bird.captiveId()==-1&&hit.getHealth()>=990,"Cancelled capture has no delayed throw damage");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=55,batch="ghost_bird")
    public static void DiveCannotPassThroughARealWallAndMissLeavesTwoSecondStun(GameTestHelper h){
        var bird=bird(h);var hit=target(h,7,13);h.assertTrue(bird.startSkill(313,hit),"Open path initially passes line-of-sight validation");
        h.runAfterDelay(15,()->{for(int x=5;x<=9;x++)for(int y=2;y<=13;y++)h.setBlock(x,y,10,Blocks.STONE);});
        h.runAfterDelay(42,()->{h.assertTrue(bird.phase()==AttackState.STUN&&bird.captiveId()==-1&&hit.getHealth()==1000,"Ordinary movement collides with the wall; no remote grab through it");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=130,batch="ghost_bird_death")
    public static void DeathActuallyFallsAndSavedCorpseExpiresWithoutRepeatingLoot(GameTestHelper h){
        var bird=bird(h);var origin=bird.position();bird.hurt(bird.damageSources().genericKill(),10000);
        h.assertTrue(bird.isDeadOrDying()&&!bird.isNoGravity(),"Death enters the authored fall, not an immediate discard");
        h.runAfterDelay(24,()->{
            h.assertTrue(bird.onGround()&&bird.getY()<=h.absolutePos(new BlockPos(7,2,7)).getY()+.02,"Flying corpse must reach the actual collision floor");
            var bounds=new net.minecraft.world.phys.AABB(origin,origin).inflate(10);
            int count=h.getLevel().getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,bounds).stream().mapToInt(i->i.getItem().getCount()).sum();
            h.assertTrue(count>=3,"Native death loot pools emit actual registered material stacks");
            var state=new CompoundTag();bird.save(state);var uuid=bird.getUUID();bird.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            var restored=EliteContent.BIRD.get().create(h.getLevel());restored.load(state);h.getLevel().addFreshEntity(restored);
            h.runAtTickTime(60,()->h.assertTrue(h.getLevel().getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,bounds).stream().mapToInt(i->i.getItem().getCount()).sum()==count,"Loading the dying entity cannot repeat its native loot"));
            h.runAtTickTime(115,()->{h.assertTrue(h.getLevel().getEntity(uuid)==null,"Absolute death clock removes the saved corpse without extending the fall");h.succeed();});
        });
    }
}
