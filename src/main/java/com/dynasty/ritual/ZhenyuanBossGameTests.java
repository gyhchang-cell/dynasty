package com.dynasty.ritual;

import com.dynasty.Dynasty;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public final class ZhenyuanBossGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=40)
    public static void finalBossHasThreeReadablePhases(GameTestHelper h) {
        var boss=ZhenyuanBosses.FINAL_BOSS.get().create(h.getLevel());
        h.assertTrue(boss!=null,"final boss registered");
        h.assertTrue(boss.getMaxHealth()==60000F,"final boss health must not clamp to vanilla maximum");
        boss.setHealth(boss.getMaxHealth()); h.assertTrue(boss.ritualPhase()==0,"full phase");
        boss.setHealth(boss.getMaxHealth()*.5F); h.assertTrue(boss.ritualPhase()==1,"middle phase");
        boss.setHealth(boss.getMaxHealth()*.2F); h.assertTrue(boss.ritualPhase()==2,"last phase");
        h.assertTrue(boss.isPersistenceRequired(),"arena boss persistent");
        h.assertTrue(!boss.removeWhenFarAway(100000),"logout cannot despawn boss");
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40)
    public static void reloadRestartsFullWarningWithoutHealingBoss(GameTestHelper h) {
        var boss=ZhenyuanBosses.FINAL_BOSS.get().create(h.getLevel());
        boss.setHealth(10000);CompoundTag n=new CompoundTag();boss.addAdditionalSaveData(n);
        n.putInt("RitualWarning",1); n.putInt("RitualPattern",2);
        n.putDouble("CastX",5);n.putDouble("CastY",70);n.putDouble("CastZ",12);
        var restored=ZhenyuanBosses.FINAL_BOSS.get().create(h.getLevel());restored.readAdditionalSaveData(n);
        CompoundTag r=new CompoundTag();restored.addAdditionalSaveData(r);
        h.assertTrue(r.getInt("RitualWarning")==ZhenyuanAttackPattern.WARNING_TICKS,"full warning after reload");
        h.assertTrue(restored.getHealth()==10000,"reload must retain damaged health");
        h.assertTrue(r.getDouble("CastX")==5&&r.getDouble("CastZ")==12,"same visible warning target");
        h.succeed();
    }
}
