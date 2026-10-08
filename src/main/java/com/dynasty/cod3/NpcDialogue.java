package com.dynasty.cod3;

import com.dynasty.Dynasty;
import com.mojang.brigadier.arguments.StringArgumentType;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/** Server-held, per-player conversation session. Chat choices cannot address another player's NPC. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class NpcDialogue {
    private record Session(UUID npc,String dimension,long expires){}
    private static final Map<UUID,Session> SESSIONS=new HashMap<>();
    public static void open(ServerPlayer p,DynastyNpcEntity npc){
        String flag="cod3_npc_met_"+npc.role;var saved=p.getPersistentData().getCompound(net.minecraft.world.entity.player.Player.PERSISTED_NBT_TAG);p.getPersistentData().put(net.minecraft.world.entity.player.Player.PERSISTED_NBT_TAG,saved);boolean first=!saved.getBoolean(flag);saved.putBoolean(flag,true);
        var node=DialogueNode.greeting(npc.role,first);SESSIONS.put(p.getUUID(),new Session(npc.getUUID(),p.level().dimension().location().toString(),p.level().getGameTime()+200));
        p.sendSystemMessage(npc.getDisplayName().copy().append(Component.literal(": ")).append(Component.translatable(npc.worldChanged()?"cod3.dynasty.npc."+npc.role+".changed":node.textKey())));
        for(var choice:node.choices())p.sendSystemMessage(Component.translatable(choice.textKey()).withStyle(s->s.withColor(net.minecraft.ChatFormatting.GOLD).withClickEvent(new ClickEvent(ClickEvent.Action.RUN_COMMAND,"/dynasty_dialogue "+choice.action().name().toLowerCase(java.util.Locale.ROOT)))));
    }
    @SubscribeEvent public static void commands(RegisterCommandsEvent e){e.getDispatcher().register(Commands.literal("dynasty_dialogue").then(Commands.argument("choice",StringArgumentType.word()).executes(c->{
        var p=c.getSource().getPlayerOrException();var session=SESSIONS.get(p.getUUID());
        if(session==null||session.expires<p.level().getGameTime()||!session.dimension.equals(p.level().dimension().location().toString())){SESSIONS.remove(p.getUUID());return 0;}
        var entity=p.serverLevel().getEntity(session.npc);if(!(entity instanceof DynastyNpcEntity npc)||!npc.isAlive()||p.distanceToSqr(npc)>36){SESSIONS.remove(p.getUUID());return 0;}
        return switch(StringArgumentType.getString(c,"choice")){case "trade"->{npc.trade(p);yield 1;}case "talk"->{p.sendSystemMessage(Component.translatable("cod3.dynasty.npc."+npc.role+(npc.worldChanged()?".changed":".ordinary")));yield 1;}case "leave"->{SESSIONS.remove(p.getUUID());yield 1;}default->0;};
    })));}
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){SESSIONS.remove(e.getEntity().getUUID());}
    private NpcDialogue(){}
}
