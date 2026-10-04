package com.dynasty.ritual;

import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.UUID;

@GameTestHolder("dynasty") @PrefixGameTestTemplate(false)
public final class ZhenyuanPhaseOneGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=40)
    public static void finalCeremonyNeverPullsOrZerosPlayers(GameTestHelper h) {
        var level=h.getLevel();var p=new FakePlayer(level,new GameProfile(UUID.randomUUID(),"ritual-free-movement"));
        level.addNewPlayer(p);
        var core=h.absolutePos(new BlockPos(3,3,3));
        var s=new ZhenyuanRitualSavedData.Session(level.dimension().location().toString(),core);
        s.mask=31;s.owner=p.getUUID();s.ritualRunning=true;s.ritualStage="FINAL_RITUAL";s.ritualTicks=169;
        var data=new ZhenyuanRitualSavedData();
        try {
            for(int t=0;t<70;t++) {
                var at=net.minecraft.world.phys.Vec3.atCenterOf(core).add(4+t*.025,.2,1);
                var velocity=new net.minecraft.world.phys.Vec3(.2,.42,.13);
                p.moveTo(at.x,at.y,at.z,42,-17);p.setDeltaMovement(velocity);
                ZhenyuanPhaseOne.tick(level,s,data,p);
                h.assertTrue(p.position().equals(at)&&p.getDeltaMovement().equals(velocity),"Final offering pulled/froze player");
                h.assertTrue(p.getYRot()==42&&p.getXRot()==-17,"Final offering changed look");
            }
            h.assertTrue(s.ritualTicks==239,"Fixture did not exercise the complete pre-transfer timeline");
        } finally {p.discard();}h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40)
    public static void unorderedAnimationsPersistAndDoNotActivateEarly(GameTestHelper h) {
        var s=new ZhenyuanRitualSavedData.Session("minecraft:overworld",BlockPos.ZERO);s.phaseOne=true;
        for(int slot:new int[]{3,1,0,2}) {
            s.pendingMask|=1<<slot;
            for(int t=0;t<ZhenyuanPhaseOne.DURATIONS[slot]-1;t++) {
                ZhenyuanPhaseOne.advance(s);
                s=ZhenyuanRitualSavedData.Session.load(s.save());
                h.assertTrue((s.mask&(1<<slot))==0,"Activated before animation finished/reload lost reservation");
            }
            ZhenyuanPhaseOne.advance(s);
            h.assertTrue((s.mask&(1<<slot))!=0&&(s.pendingMask&(1<<slot))==0,"Animation failed to commit exactly once");
            if(Integer.bitCount(s.mask)==3) {
                h.assertTrue(s.ritualStage.equals("THIRD_OMEN"),"Missing third omen");
                for(int i=0;i<40;i++)ZhenyuanPhaseOne.advance(s);
            }
        }
        h.assertTrue(s.ritualStage.equals("FOURTH_CONVERGENCE")&&!s.finalOfferingReady,"Fourth must finish choreography first");
        for(int i=0;i<89;i++)ZhenyuanPhaseOne.advance(s);
        h.assertTrue(!s.finalOfferingReady,"Fourth convergence ended early");ZhenyuanPhaseOne.advance(s);
        h.assertTrue(s.finalOfferingReady&&s.ritualStage.equals("FINAL_OFFERING_READY"),"Final offering not enabled");
        s.mask|=16;s.ritualRunning=true;ZhenyuanPhaseOne.stage(s,"FINAL_RITUAL");
        for(int i=0;i<239;i++) {ZhenyuanPhaseOne.advance(s);s=ZhenyuanRitualSavedData.Session.load(s.save());}
        h.assertTrue(s.ritualStage.equals("FINAL_RITUAL")&&!s.bossFightStarted,"Premature dimension transfer");
        ZhenyuanPhaseOne.advance(s);h.assertTrue(s.ritualStage.equals("TRANSFER_READY"),"Final sequence never completed");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40)
    public static void concurrentCompletionsCannotSkipOmen(GameTestHelper h) {
        var s=new ZhenyuanRitualSavedData.Session("minecraft:overworld",BlockPos.ZERO);
        s.pendingMask=15;s.offeringTicks=new int[]{100,64,110,160};
        ZhenyuanPhaseOne.advance(s);h.assertTrue(Integer.bitCount(s.mask)==3&&s.pendingMask!=0,"Concurrent fourth skipped third omen");
        for(int i=0;i<40;i++)ZhenyuanPhaseOne.advance(s);
        ZhenyuanPhaseOne.advance(s);h.assertTrue(s.mask==15&&s.ritualStage.equals("FOURTH_CONVERGENCE"),"Queued fourth activation lost");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40)
    public static void phaseOneReservationsAreMultiplayerSafe(GameTestHelper h) {
        var level=h.getLevel();var data=ZhenyuanRitualSavedData.get(level);
        var a=new FakePlayer(level,new GameProfile(UUID.randomUUID(),"phase-one-a"));
        var b=new FakePlayer(level,new GameProfile(UUID.randomUUID(),"phase-one-b"));
        var core=h.absolutePos(new BlockPos(3,3,3));var s=new ZhenyuanRitualSavedData.Session(level.dimension().location().toString(),core);
        s.phaseOne=true;data.sessions.put(s.key,s);
        try {
            for(int slot=0;slot<5;slot++) {
                var pos=core.offset(slot,0,0);level.setBlockAndUpdate(pos,ZhenyuanRitualContent.NODE.get().defaultBlockState().setValue(ZhenyuanNodeBlock.SLOT,slot));
                var node=(ZhenyuanNodeBlockEntity)level.getBlockEntity(pos);node.configure(core,slot);s.nodes.put(slot,pos);
            }
            var node=(ZhenyuanNodeBlockEntity)level.getBlockEntity(core);
            a.setPos(core.getX(),core.getY(),core.getZ());b.setPos(a.position());
            a.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.DIAMOND,5));ZhenyuanRitualService.interact(a,node);
            h.assertTrue(a.getMainHandItem().getCount()==5&&s.pendingMask==0,"Wrong item consumed");
            var scale=ForgeRegistries.ITEMS.getValue(new ResourceLocation("dynasty:qinglong_scale"));
            a.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(scale,5));b.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(scale,5));
            ZhenyuanRitualService.interact(a,node);ZhenyuanRitualService.interact(a,node);ZhenyuanRitualService.interact(b,node);
            h.assertTrue(s.mask==0&&s.pendingMask==1&&a.getMainHandItem().getCount()==4&&b.getMainHandItem().getCount()==5,"Reservation duplicated/activated early");
            var west=(ZhenyuanNodeBlockEntity)level.getBlockEntity(s.nodes.get(1));
            b.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ForgeRegistries.ITEMS.getValue(new ResourceLocation("dynasty:baihu_fang")),2));
            ZhenyuanRitualService.interact(b,west);h.assertTrue(s.pendingMask==3&&b.getMainHandItem().getCount()==1,"Other player cannot contribute to a different pillar");
            var center=(ZhenyuanNodeBlockEntity)level.getBlockEntity(s.nodes.get(4));a.setPos(center.getBlockPos().getX(),core.getY(),core.getZ());
            a.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ZhenyuanRitualContent.TIANMING_JADE.get(),3));
            ZhenyuanRitualService.interact(a,center);h.assertTrue(a.getMainHandItem().getCount()==3,"Early jade consumed");
            s.pendingMask=0;s.mask=15;s.finalOfferingReady=true;s.ritualStage="FINAL_OFFERING_READY";
            ZhenyuanRitualService.interact(a,center);ZhenyuanRitualService.interact(a,center);
            h.assertTrue(a.getMainHandItem().getCount()==2&&s.mask==31&&s.ritualRunning&&s.ritualTicks==0,"Final ritual duplicated or skipped");
            h.assertTrue(a.serverLevel()==level&&s.boss==null,"Right click immediately spawned/transferred");
        } finally {data.sessions.remove(s.key);a.discard();b.discard();}
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40)
    public static void oldIdleAltarsMigrateButActiveBossesDoNot(GameTestHelper h) {
        var s=new ZhenyuanRitualSavedData.Session("minecraft:overworld",BlockPos.ZERO);s.mask=15;
        var n=s.save();n.remove("PhaseOne");n.remove("RitualStage");n.remove("BossIntroTick");
        var migrated=ZhenyuanRitualSavedData.Session.load(n);
        h.assertTrue(migrated.phaseOne&&migrated.finalOfferingReady&&migrated.mask==15,"Old paid offerings lost");
        n.putString("Phase","active");var active=ZhenyuanRitualSavedData.Session.load(n);
        h.assertTrue(!active.phaseOne&&active.is("active")&&active.bossFightStarted,"Legacy fight was reset");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=40)
    public static void offlineOwnerCannotAdvanceOrLoseFinalOffering(GameTestHelper h) {
        var s=new ZhenyuanRitualSavedData.Session(h.getLevel().dimension().location().toString(),h.absolutePos(new BlockPos(2,2,2)));
        s.phaseOne=true;s.mask=31;s.owner=UUID.randomUUID();s.ritualRunning=true;s.ritualStage="FINAL_RITUAL";s.ritualTicks=188;
        var data=new ZhenyuanRitualSavedData();data.sessions.put(s.key,s);
        for(int i=0;i<100;i++)h.assertTrue(!ZhenyuanPhaseOne.tick(h.getLevel(),s,data,null),"Offline owner initiated encounter");
        var loaded=ZhenyuanRitualSavedData.load(data.save(new CompoundTag())).sessions.get(s.key);
        h.assertTrue(loaded.ritualTicks==188&&loaded.mask==31&&loaded.ritualRunning&&loaded.owner.equals(s.owner),"Offline final ritual lost progress/payment");
        h.succeed();
    }
}
