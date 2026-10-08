package com.dynasty.ritual;

import com.dynasty.Dynasty;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Receipts follow the actual depositor, not the final ritual leader. Saved UUIDs survive logout. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class RitualQuestProgress {
    private static final String[] IDS={"ritual_qinglong","ritual_baihu","ritual_zhuque","ritual_xuanwu"};
    static void grant(ServerPlayer p,String id){
        var a=p.server.getAdvancements().getAdvancement(new ResourceLocation(Dynasty.MODID,id));
        if(a!=null)for(String criterion:p.getAdvancements().getOrStartProgress(a).getRemainingCriteria())p.getAdvancements().award(a,criterion);
    }
    static void restore(MinecraftServer server,ZhenyuanRitualSavedData.Session s){
        if((s.mask&15)==15)com.dynasty.cod3.Cod3WorldState.get(server.overworld()).unlock(server.overworld(),"world_08");
        for(int i=0;i<4;i++)if((s.mask&(1<<i))!=0&&s.offeringPlayers[i]!=null){
            var player=server.getPlayerList().getPlayer(s.offeringPlayers[i]);if(player!=null)grant(player,IDS[i]);
        }
    }
    @SubscribeEvent public static void login(PlayerEvent.PlayerLoggedInEvent event){
        if(event.getEntity() instanceof ServerPlayer p)
            for(var s:ZhenyuanRitualSavedData.get(p.serverLevel()).sessions()){
                restore(p.server,s);
                if(p.getUUID().equals(s.owner)&&(s.mask&16)!=0)grant(p,"ritual_final_offering");
            }
    }
    private RitualQuestProgress(){}
}
