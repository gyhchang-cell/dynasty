package com.dynasty;

import net.minecraft.nbt.CompoundTag;
import java.util.UUID;

/** Real NBT behavior checks; no Minecraft bootstrap, player, server, window or world. */
public final class LegacyProgressionOfflineChecks {
    private static int checks;
    private static void check(boolean yes, String why) {
        checks++;
        if (!yes) throw new AssertionError(why);
    }
    public static void main(String[] args) {
        CompoundTag old = new CompoundTag(), next = new CompoundTag();
        old.putInt("dynasty_merit",420); old.putInt("dynasty_rank",3);
        old.putInt("dynasty_loyalty",10); old.putInt("dynasty_rebellion",11);
        old.putBoolean("dynasty_manual_given",true);
        old.putLong("dynasty_merit_kill_window",1700000000000L);old.putInt("dynasty_merit_kill_earned",119);
        old.putInt("dq_p_18",1);old.putBoolean("dq_c_18",false);old.putBoolean("dq_e_keju",true);
        old.putInt("dq_p_24",99);old.putBoolean("dq_e_unknown",true);
        old.putInt("DynastyEventMonsterKills",100);
        old.putInt("dynasty_injury",73);old.putLong("dynasty_injury_hit",900);
        old.putLong("DynastyArmyPermitUntil",12345);old.putInt("cod3_progress_1",200);
        old.putString("dynasty_boss_kinds_list","dragon_king,rebel_general");old.putInt("dynasty_boss_kinds",2);
        old.putBoolean("dynasty_gift_sunbow",true);old.putString("dynasty_festival_day","SPRING:2026-11-01");
        UUID blessing=UUID.fromString("c5f4a008-e16d-4d47-a370-1c2d707c6000");old.putUUID("DynastyXuanniaoBlessing",blessing);
        CompoundTag nested=new CompoundTag();nested.putBoolean("dynasty_firstkill_dragon_king",true);
        nested.putLong("guardsUntil",9999);old.put("PlayerPersisted",nested);
        // Model the native initial shared nested reference, without running native Clone.
        next.put("PlayerPersisted",nested);next.putInt("unrelated",987);
        CompoundTag original=old.copy();
        check(LegacyPlayerProgression.copyAuditedRoot(old,next).isEmpty(),"valid source should have no diagnostic");
        for(String key:new String[]{"dynasty_merit","dynasty_rank","dynasty_loyalty","dynasty_rebellion","dynasty_manual_given","dynasty_merit_kill_window","dynasty_merit_kill_earned","dq_p_18","dq_c_18","dq_e_keju","DynastyEventMonsterKills","dynasty_boss_kinds_list","dynasty_boss_kinds","dynasty_gift_sunbow","dynasty_festival_day","DynastyXuanniaoBlessing"}) {
            check(old.get(key).equals(next.get(key)),"typed fact changed: "+key);
        }
        check(next.getBoolean("dynasty_firstkill_dragon_king"),"nested-only firstkill must restore root consumer");
        check(!next.contains("dynasty_firstkill_phoenix"),"absent kill must remain absent");
        check(old.equals(original),"copier mutated original/shared nested state");
        check(next.getCompound("PlayerPersisted")==nested,"copier replaced inherited container");
        for(String key:new String[]{"dynasty_injury","dynasty_injury_hit","DynastyArmyPermitUntil","cod3_progress_1","dq_p_24","dq_e_unknown"})check(!next.contains(key),"unapproved state copied: "+key);
        check(next.getInt("dq_p_18")==1&&!next.getBoolean("dq_c_18"),"partial progress upgraded or reward claimed");
        check(next.getInt("unrelated")==987,"new root unrelated owner destroyed");
        CompoundTag once=next.copy();LegacyPlayerProgression.copyAuditedRoot(old,next);check(next.equals(once),"not idempotent");
        next.getIntArray("DynastyXuanniaoBlessing")[0]^=1;
        check(old.getUUID("DynastyXuanniaoBlessing").equals(blessing),"UUID array aliased original");
        CompoundTag replaced=next.getCompound("PlayerPersisted").copy();next.put("PlayerPersisted",replaced);
        check(next.getBoolean("dynasty_firstkill_dragon_king"),"later whole nested copy clobbered root alias");
        CompoundTag wrong=new CompoundTag(), untouched=new CompoundTag();
        wrong.putLong("dynasty_merit",420);wrong.putInt("dynasty_manual_given",1);wrong.putIntArray("DynastyXuanniaoBlessing",new int[]{1,2,3});
        var errors=LegacyPlayerProgression.copyAuditedRoot(wrong,untouched);
        check(errors.contains("dynasty_merit")&&errors.contains("dynasty_manual_given")&&errors.contains("DynastyXuanniaoBlessing"),"wrong-type diagnostics missing");
        check(untouched.isEmpty(),"wrong NBT type was coerced into a new fact");
        CompoundTag partial=new CompoundTag();partial.putInt("dynasty_merit_kill_earned",119);
        CompoundTag partialOut=new CompoundTag();var partialErrors=LegacyPlayerProgression.copyAuditedRoot(partial,partialOut);
        check(partialErrors.contains("dynasty_merit_kill_window/dynasty_merit_kill_earned"),"partial budget not diagnosed");
        check(partialOut.isEmpty(),"partial budget manufactured timestamp or amount");
        // This intentionally makes no claim that native consumers cannot reset a malformed budget.
        CompoundTag rootOnly=new CompoundTag(),rootOut=new CompoundTag();rootOnly.putBoolean("dynasty_firstkill_phoenix",true);
        LegacyPlayerProgression.copyAuditedRoot(rootOnly,rootOut);
        check(rootOut.getBoolean("dynasty_firstkill_phoenix")&&!rootOut.contains("PlayerPersisted"),"root-only alias writes nested");
        CompoundTag peer=new CompoundTag();peer.putInt("dynasty_merit",9);CompoundTag peerBefore=peer.copy();
        LegacyPlayerProgression.copyAuditedRoot(old,new CompoundTag());check(peer.equals(peerBefore),"unpassed peer changed");
        System.out.println("PASS "+checks+" real-NBT offline assertions; no player/Clone-event/TCP/world/remap runtime credit");
    }
}
