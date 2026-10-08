package com.dynasty.cod3;

import com.dynasty.Dynasty;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.*;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Ten world flags; consumers update only their own loaded region, never scan/edit the world. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class Cod3WorldState extends SavedData {
    private final CompoundTag states=new CompoundTag();
    public static Cod3WorldState get(ServerLevel l){return l.getServer().overworld().getDataStorage().computeIfAbsent(Cod3WorldState::load,Cod3WorldState::new,"dynasty_cod3_world");}
    private static Cod3WorldState load(CompoundTag tag){var s=new Cod3WorldState();s.states.merge(tag.getCompound("States"));return s;}
    @Override public CompoundTag save(CompoundTag tag){tag.put("States",states.copy());return tag;}
    public boolean unlocked(String id){return states.getBoolean(id);}
    public boolean unlock(ServerLevel level,String id){
        Cod3Catalog.find("worldStates",id);if(unlocked(id))return false;states.putBoolean(id,true);setDirty();
        for(var p:level.getServer().getPlayerList().getPlayers())p.displayClientMessage(Component.translatable("cod3.dynasty.world."+id),false);
        return true;
    }
    public static void bossDefeated(ServerLevel level,String boss){
        // Only verified storyline links are enabled. Other states are exposed to structure controllers.
        String id=switch(boss){case "dynasty:rebel_general"->"world_01";case "dynasty:undead_first_emperor"->"world_09";default->null;};
        if(id!=null)get(level).unlock(level,id);
    }
    @SubscribeEvent public static void victory(com.dynasty.ritual.ZhenyuanVictoryEvent event){
        var server=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();if(server!=null)get(server.overworld()).unlock(server.overworld(),"world_10");
    }
}
