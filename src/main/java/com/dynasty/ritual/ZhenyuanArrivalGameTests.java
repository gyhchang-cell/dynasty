package com.dynasty.ritual;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import java.util.UUID;
@GameTestHolder("dynasty") @PrefixGameTestTemplate(false)
public final class ZhenyuanArrivalGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=40)
    public static void arrivalGatesPersistAtEveryKeyframe(GameTestHelper h) {
        var level=h.getLevel();var data=ZhenyuanRitualSavedData.get(level);
        var boss=ZhenyuanBosses.FINAL_BOSS.get().create(level);
        var s=new ZhenyuanRitualSavedData.Session(level.dimension().location().toString(),h.absolutePos(BlockPos.ZERO));
        s.owner=UUID.randomUUID();s.boss=boss.getUUID();s.phase="active";s.participants.add(UUID.randomUUID());data.sessions.put(s.key,s);
        try {
            for(int t=0;t<=280;t++) {
                s.bossIntroTick=t;s=ZhenyuanRitualSavedData.Session.load(s.save());data.sessions.put(s.key,s);
                boss.applyEncounterGate(true);
                h.assertTrue(boss.introTick()==t&&s.participants.size()==1,"Intro/party lost on reload");
                h.assertTrue(boss.isNoAi()==(t<280)&&boss.isInvulnerable()==(t<280),"AI or damage gate opened early");
                if(t<280)h.assertTrue(!boss.hurt(boss.damageSources().genericKill(),Float.MAX_VALUE),"Even bypass damage must not kill intro boss");
            }
            boss.applyEncounterGate(false);h.assertTrue(boss.isNoAi()&&boss.isInvulnerable(),"Paused combat unsafe");
            var loaded=ZhenyuanBosses.FINAL_BOSS.get().create(level);loaded.load(boss.saveWithoutId(new CompoundTag()));
            h.assertTrue(loaded.introTick()==280,"Entity snapshot forgot intro");loaded.discard();
            h.assertTrue(ZhenyuanSovereign.stageAt(59)==ZhenyuanSovereign.ArrivalStage.SEALED&&ZhenyuanSovereign.stageAt(60)==ZhenyuanSovereign.ArrivalStage.AWAKENING
                    &&ZhenyuanSovereign.stageAt(140)==ZhenyuanSovereign.ArrivalStage.INTRO&&ZhenyuanSovereign.stageAt(280)==ZhenyuanSovereign.ArrivalStage.COMBAT,"Incorrect state boundaries");
        } finally {data.sessions.remove(s.key);data.setDirty();boss.discard();}h.succeed();
    }
}
