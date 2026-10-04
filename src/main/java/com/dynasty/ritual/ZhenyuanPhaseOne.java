package com.dynasty.ritual;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundSetTitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetSubtitleTextPacket;
import net.minecraft.network.protocol.game.ClientboundSetTitlesAnimationPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.registries.ForgeRegistries;
import static com.dynasty.ritual.ZhenyuanRitualSavedData.Session;

/** Phase 1 only: durable tick choreography; the existing encounter owns everything after handoff. */
public final class ZhenyuanPhaseOne {
    public static final int[] DURATIONS={100,64,110,160};
    public static final int FINAL_DURATION=240;
    private ZhenyuanPhaseOne() {}
    public static InteractionResult interact(ServerPlayer p,ZhenyuanNodeBlockEntity node,Session s,ZhenyuanRitualSavedData data) {
        int slot=node.getSlot(), bit=1<<slot;
        var held=p.getMainHandItem();
        if(s.ritualRunning || ((s.mask|s.pendingMask)&bit)!=0) {
            ZhenyuanRitualService.hint(p,"此处已接受贡品，不能重复献祭。"); return InteractionResult.CONSUME;
        }
        String expected=slot==4?"dynasty:tianming_jade":"dynasty:"+ZhenyuanRitualRules.OFFERINGS[slot];
        if(!expected.equals(String.valueOf(ForgeRegistries.ITEMS.getKey(held.getItem())))) {
            p.serverLevel().sendParticles(ParticleTypes.SMOKE,node.getBlockPos().getX()+.5,node.getBlockPos().getY()+1.1,node.getBlockPos().getZ()+.5,6,.15,.1,.15,.01);
            p.serverLevel().playSound(null,node.getBlockPos(),SoundEvents.NOTE_BLOCK_BASS.value(),SoundSource.BLOCKS,.5f,.5f);
            ZhenyuanRitualService.hint(p,slot==4?"最终贡品：天命玉。":"此柱需要："+ZhenyuanRitualRules.NAMES[slot]);
            return InteractionResult.CONSUME;
        }
        if(slot==4&&!s.finalOfferingReady) { ZhenyuanRitualService.hint(p,"四象尚未归位。"); return InteractionResult.CONSUME; }
        if(slot==4) {
            Session other=data.forOwner(p.getUUID());
            if(other!=null&&other!=s) { ZhenyuanRitualService.hint(p,"请先结束你已有的挑战。"); return InteractionResult.CONSUME; }
            if(p.server.getLevel(ZhenyuanArena.DIMENSION)==null) { ZhenyuanRitualService.hint(p,"现有战场维度不可用，祭品未消耗。"); return InteractionResult.CONSUME; }
            s.owner=p.getUUID(); s.yaw=p.getYRot(); s.mask|=16;
            stage(s,"FINAL_RITUAL"); s.ritualRunning=true; s.finalOfferingReady=false;
            ZhenyuanRitualService.hint(p,"四象归位，天门将启。");
            RitualQuestProgress.grant(p,"ritual_final_offering");
        } else { s.pendingMask|=bit; s.offeringTicks[slot]=0; s.offeringPlayers[slot]=p.getUUID(); }
        // A reservation is authoritative immediately, activation occurs only on the last animation tick.
        held.shrink(1);
        data.setDirty(); ZhenyuanRitualService.syncNodes(p.serverLevel(),s);
        return InteractionResult.CONSUME;
    }
    public static void stage(Session s,String stage) { s.ritualStage=stage; s.ritualTicks=0; }
    /** Single-tick deterministic transition function, also exercised by save/reload regression tests. */
    public static void advance(Session s) {
        for(int slot=0;slot<4;slot++) if((s.pendingMask&(1<<slot))!=0)
            s.offeringTicks[slot]=Math.min(DURATIONS[slot],s.offeringTicks[slot]+1);
        if(s.ritualStage.equals("OFFERINGS")) {
            for(int slot=0;slot<4;slot++) if((s.pendingMask&(1<<slot))!=0&&s.offeringTicks[slot]>=DURATIONS[slot]) {
                s.pendingMask&=~(1<<slot); s.mask|=1<<slot;
                int count=Integer.bitCount(s.mask&15); s.completionOrder[slot]=count;
                if(count==3) { stage(s,"THIRD_OMEN"); break; }
                if(count==4) { stage(s,"FOURTH_CONVERGENCE"); break; }
            }
        } else if(s.ritualStage.equals("THIRD_OMEN")) { if(++s.ritualTicks>=40) stage(s,"OFFERINGS"); }
        else if(s.ritualStage.equals("FOURTH_CONVERGENCE")) {
            if(++s.ritualTicks>=90) { stage(s,"FINAL_OFFERING_READY"); s.finalOfferingReady=true; }
        } else if(s.ritualStage.equals("FINAL_RITUAL")&&++s.ritualTicks>=FINAL_DURATION) stage(s,"TRANSFER_READY");
    }
    public static boolean tick(ServerLevel level,Session s,ZhenyuanRitualSavedData data,ServerPlayer owner) {
        // No forced chunk loads: unloaded ceremonies freeze, retaining their exact clocks.
        if(s.nodes.values().stream().anyMatch(pos->!level.hasChunkAt(pos))) return false;
        if(level.players().stream().noneMatch(p->p.distanceToSqr(Vec3.atCenterOf(s.core))<96*96)) return false;
        if(s.ritualRunning&&(owner==null||!owner.isAlive()||owner.serverLevel()!=level||owner.distanceToSqr(Vec3.atCenterOf(s.core))>64*64)) return false;
        if(s.pendingMask==0&&(s.ritualStage.equals("OFFERINGS")||s.finalOfferingReady)) return false;
        String before=s.ritualStage; int mask=s.mask;
        advance(s); data.setDirty();
        if((s.pendingMask&2)!=0&&s.offeringTicks[1]==16)
            level.playSound(null,s.nodes.get(1),SoundEvents.TRIDENT_THROW,SoundSource.BLOCKS,.8f,1.5f);
        if((s.pendingMask&4)!=0&&s.offeringTicks[2]==20)
            level.playSound(null,s.nodes.get(2),SoundEvents.FIRECHARGE_USE,SoundSource.BLOCKS,.6f,.8f);
        if(s.ritualStage.equals("THIRD_OMEN")&&s.ritualTicks==10)
            level.playSound(null,s.core,SoundEvents.WARDEN_HEARTBEAT,SoundSource.BLOCKS,1.3f,.55f);
        if(s.ritualStage.equals("FOURTH_CONVERGENCE")&&s.ritualTicks==42) {
            level.playSound(null,s.core,SoundEvents.BEACON_POWER_SELECT,SoundSource.BLOCKS,1.5f,.6f);
            for(var p:level.players()) if(p.distanceToSqr(Vec3.atCenterOf(s.core))<64*64) {
                p.connection.send(new ClientboundSetTitlesAnimationPacket(10,60,20));
                p.connection.send(new ClientboundSetSubtitleTextPacket(Component.literal("献上最后的祭品。")));
                p.connection.send(new ClientboundSetTitleTextPacket(Component.literal("§6四象归位")));
            }
        }
        if(mask!=s.mask) {
            RitualQuestProgress.restore(level.getServer(),s);
            int slot=Integer.numberOfTrailingZeros(mask^s.mask);
            if(slot<4) level.playSound(null,s.nodes.get(slot),switch(slot) {
                case 0->SoundEvents.AMETHYST_BLOCK_CHIME; case 1->SoundEvents.TRIDENT_HIT;
                case 2->SoundEvents.BLAZE_SHOOT; default->SoundEvents.WARDEN_SONIC_BOOM;
            },SoundSource.BLOCKS,1f,slot==3?.5f:1f);
        }
        if(s.ritualStage.equals("FINAL_RITUAL")&&s.ritualTicks==170&&owner!=null)
            level.playSound(null,s.core,SoundEvents.GENERIC_EXPLODE,SoundSource.BLOCKS,1.2f,.65f);
        if(level.getGameTime()%4==0||mask!=s.mask||!before.equals(s.ritualStage)) ZhenyuanRitualService.syncNodes(level,s);
        if(s.ritualStage.equals("TRANSFER_READY")&&owner!=null) {
            s.ritualRunning=false; stage(s,"COMPLETE"); data.setDirty(); return true;
        }
        return false;
    }
}
