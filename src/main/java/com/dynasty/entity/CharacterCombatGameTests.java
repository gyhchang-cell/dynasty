package com.dynasty.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty") @PrefixGameTestTemplate(false)
public final class CharacterCombatGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=50)
    public static void remasteredMeleeHasOneAuthoritativeImpactAfterWindup(GameTestHelper h) {
        var fighter=DynastyEntities.REBEL_SOLDIER.get().create(h.getLevel());
        int[] hits={0};var victim=new Zombie(h.getLevel()) {
            @Override public boolean hurt(DamageSource source,float damage){hits[0]++;return true;}
        };
        var at=h.absolutePos(new BlockPos(3,4,3));fighter.setPos(at.getX(),at.getY(),at.getZ());victim.setPos(fighter.position());
        var goal=new CharacterMeleeGoal(fighter,1);
        goal.checkAndPerformAttack(victim,0);
        h.assertTrue(hits[0]==0,"Damage before visible windup");
        h.runAfterDelay(4,()->{
            goal.checkAndPerformAttack(victim,0);
            h.assertTrue(hits[0]==0&&fighter.characterAttackProgress(0)>0,"Missing synced windup or premature hit");
        });
        h.runAfterDelay(7,()->{
            goal.checkAndPerformAttack(victim,0);goal.checkAndPerformAttack(victim,0);
            h.assertTrue(hits[0]==1,"Impact missing or duplicated");goal.stop();
            h.assertTrue(fighter.characterAttackProgress(0)==0,"Cancelled goal retained animation");
            fighter.discard();victim.discard();h.succeed();
        });
    }
}
