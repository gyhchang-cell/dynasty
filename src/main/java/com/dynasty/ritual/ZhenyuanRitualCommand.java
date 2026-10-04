package com.dynasty.ritual;

import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Escape/status/resume are deliberately available without operator permissions. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class ZhenyuanRitualCommand {
    private ZhenyuanRitualCommand() {}
    @SubscribeEvent public static void commands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("dynasty_ritual")
                .then(Commands.literal("join").then(Commands.argument("player",net.minecraft.commands.arguments.EntityArgument.player())
                        .executes(c->ZhenyuanRitualService.join(c.getSource().getPlayerOrException(),net.minecraft.commands.arguments.EntityArgument.getPlayer(c,"player")))))
                .then(Commands.literal("status").executes(c->ZhenyuanRitualService.status(c.getSource().getPlayerOrException())))
                .then(Commands.literal("escape").executes(c->ZhenyuanRitualService.escape(c.getSource().getPlayerOrException())))
                .then(Commands.literal("resume").executes(c->ZhenyuanRitualService.resume(c.getSource().getPlayerOrException())))
                .then(Commands.literal("claim").executes(c->ZhenyuanRitualService.claim(c.getSource().getPlayerOrException())))
                .then(Commands.literal("place").requires(s->s.hasPermission(2)).executes(c->{
                    ServerPlayer p=c.getSource().getPlayerOrException();
                    // Player feet = altar ground plane; the command does not infer/overwrite a dragon build.
                    BlockPos core=p.blockPosition();
                    return ZhenyuanRitualService.install(p,core);
                })));
    }
}
