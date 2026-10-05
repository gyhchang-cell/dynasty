package com.dynasty.dungeon;

import com.dynasty.Dynasty;
import com.mojang.brigadier.CommandDispatcher;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.network.chat.Component;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class DungeonCommands {
    @SubscribeEvent public static void register(RegisterCommandsEvent event){
        CommandDispatcher<CommandSourceStack> d=event.getDispatcher();
        d.register(Commands.literal("dynasty").then(Commands.literal("dungeon").requires(s->s.hasPermission(2))
            .then(Commands.literal("room").then(Commands.literal("reset").then(Commands.argument("roomId",com.mojang.brigadier.arguments.StringArgumentType.word()).executes(c->room(c.getSource(),com.mojang.brigadier.arguments.StringArgumentType.getString(c,"roomId"),false))))
                .then(Commands.literal("complete").then(Commands.argument("roomId",com.mojang.brigadier.arguments.StringArgumentType.word()).executes(c->room(c.getSource(),com.mojang.brigadier.arguments.StringArgumentType.getString(c,"roomId"),true)))))
            .then(Commands.literal("mechanism").then(Commands.literal("set").then(Commands.argument("pos",BlockPosArgument.blockPos())
                .then(Commands.argument("state",com.mojang.brigadier.arguments.StringArgumentType.word()).executes(c->{
                    var pos=BlockPosArgument.getLoadedBlockPos(c,"pos");
                    if(!(c.getSource().getLevel().getBlockEntity(pos) instanceof DungeonMechanismBlockEntity be)||!be.validBinding())return 0;
                    String value=com.mojang.brigadier.arguments.StringArgumentType.getString(c,"state");
                    var store=DungeonStateStore.get(c.getSource().getLevel());var state=store.room(be.instance(),be.roomId());
                    switch(value){case "trigger"->be.trigger();case "reset"->state.reset();case "complete"->state.complete();default->{c.getSource().sendFailure(Component.literal("状态：trigger / reset / complete"));return 0;}}
                    store.setDirty();be.syncVisual(state);return 1;
                })))))
            .then(Commands.literal("trap").then(Commands.literal("test").then(Commands.argument("id",com.mojang.brigadier.arguments.StringArgumentType.word()).executes(c->{
                if(!com.mojang.brigadier.arguments.StringArgumentType.getString(c,"id").equals("poison_arrow"))return 0;
                return triggerNearest(c.getSource());
            }))))));
    }
    private static DungeonMechanismBlockEntity nearby(CommandSourceStack source){
        var center=net.minecraft.core.BlockPos.containing(source.getPosition());var level=source.getLevel();
        // Bounded debug search only; never an ambient world tick scan.
        for(var pos:net.minecraft.core.BlockPos.betweenClosed(center.offset(-8,-8,-8),center.offset(8,8,8)))
            if(level.hasChunkAt(pos)&&level.getBlockEntity(pos) instanceof DungeonMechanismBlockEntity be&&be.validBinding())return be;
        return null;
    }
    private static int room(CommandSourceStack source,String id,boolean complete){
        var be=nearby(source);if(be==null||!be.roomId().equals(id)){source.sendFailure(Component.literal("请站在对应试验房机关附近；当前房间 ID 为 probe。"));return 0;}
        var store=DungeonStateStore.get(source.getLevel());var room=store.room(be.instance(),id);
        if(complete)room.complete();else room.reset();store.setDirty();be.syncVisual(room);
        source.sendSuccess(()->Component.literal(complete?"试验房已完成":"试验房已重置；唯一奖励记录保留"),false);return 1;
    }
    private static int triggerNearest(CommandSourceStack source){var be=nearby(source);if(be==null)return 0;be.trigger();return 1;}
}
