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
                return triggerNearest(c.getSource(),com.mojang.brigadier.arguments.StringArgumentType.getString(c,"id"));
            }))))));
    }
    private static DungeonMechanismBlockEntity nearby(CommandSourceStack source,java.util.function.Predicate<DungeonMechanismBlockEntity> matches){
        var center=net.minecraft.core.BlockPos.containing(source.getPosition());var level=source.getLevel();
        DungeonMechanismBlockEntity nearest=null;double distance=Double.MAX_VALUE;
        // Bounded debug search only; never an ambient world tick scan.
        for(var pos:net.minecraft.core.BlockPos.betweenClosed(center.offset(-8,-8,-8),center.offset(8,8,8)))
            if(level.hasChunkAt(pos)&&level.getBlockEntity(pos) instanceof DungeonMechanismBlockEntity be&&be.validBinding()&&matches.test(be)){
                double candidate=pos.distToCenterSqr(source.getPosition());
                if(candidate<distance){nearest=be;distance=candidate;}
            }
        return nearest;
    }
    private static int room(CommandSourceStack source,String id,boolean complete){
        var be=nearby(source,b->b.roomId().equals(id));if(be==null){source.sendFailure(Component.literal("附近没有房间 "+id+" 的已加载机关。"));return 0;}
        var store=DungeonStateStore.get(source.getLevel());var room=store.room(be.instance(),id);
        if(complete)room.complete();else room.reset();store.setDirty();be.syncVisual(room);
        source.sendSuccess(()->Component.literal(complete?"房间已完成":"房间已重置；唯一奖励记录保留"),false);return 1;
    }
    private static int triggerNearest(CommandSourceStack source,String id){
        var be=nearby(source,b->(b.kind()==DungeonMechanismBlock.Kind.TRAP||b.kind()==DungeonMechanismBlock.Kind.FLOOR)
            &&(b.mechanismId().equals(id)||id.equals("poison_arrow")&&b.mechanismId().startsWith("poison_arrow_")));
        if(be==null){source.sendFailure(Component.literal("附近没有陷阱 "+id+"。"));return 0;}
        be.trigger();return 1;
    }
}
