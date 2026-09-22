package com.dynasty.puzzle;

import com.mojang.brigadier.arguments.IntegerArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraft.core.BlockPos;

import java.util.List;

/**
 * 管理员用的模板放置命令（权限等级 2）。
 *
 *   /dynasty_puzzle list
 *   /dynasty_puzzle place <star_room|bell_room|lamp_room> [0..2]
 *
 * 只接受白名单里的模板 ID，不接受任意结构路径、也不接受任何奖励参数
 * （奖励永远来自模组自带的战利品表），因此无法通过命令注入奖励数据。
 */
@Mod.EventBusSubscriber(modid = com.dynasty.Dynasty.MODID)
public final class PuzzleCommand {

    private PuzzleCommand() {
    }

    @SubscribeEvent
    public static void onRegisterCommands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("dynasty_puzzle")
                .requires(source -> source.hasPermission(2))
                .then(Commands.literal("list").executes(context -> {
                    context.getSource().sendSuccess(() -> Component.translatable(
                            "dynasty.puzzle.cmd.list", String.join(", ", PuzzleTemplates.ids())), false);
                    return 1;
                }))
                .then(Commands.literal("place")
                        .then(Commands.argument("template", StringArgumentType.word())
                                .executes(context -> place(context.getSource().getPlayerOrException(),
                                        StringArgumentType.getString(context, "template"), 0))
                                .then(Commands.argument("variant", IntegerArgumentType.integer(0, 2))
                                        .executes(context -> place(context.getSource().getPlayerOrException(),
                                                StringArgumentType.getString(context, "template"),
                                                IntegerArgumentType.getInteger(context, "variant")))))));
    }

    private static int place(ServerPlayer player, String templateId, int variant) {
        PuzzleTemplates.Room room = PuzzleTemplates.Room.byId(templateId);
        if (room == null) {
            player.displayClientMessage(Component.translatable("dynasty.puzzle.cmd.unknown",
                    String.join(", ", PuzzleTemplates.ids())), false);
            return 0;
        }
        if (!(player.level() instanceof ServerLevel level)) {
            return 0;
        }
        HitResult hit = player.pick(12.0D, 0.0F, false);
        if (!(hit instanceof BlockHitResult blockHit) || hit.getType() != HitResult.Type.BLOCK) {
            player.displayClientMessage(Component.translatable("dynasty.puzzle.cmd.look"), false);
            return 0;
        }
        BlockPos origin = blockHit.getBlockPos().above();
        PuzzleTemplates.build(level, origin, room, variant);
        player.displayClientMessage(Component.translatable("dynasty.puzzle.cmd.placed",
                room.id, origin.getX(), origin.getY(), origin.getZ()), false);
        return 1;
    }

    /** 供文档与测试引用：命令接受的模板白名单 */
    public static List<String> allowedTemplates() {
        return PuzzleTemplates.ids();
    }
}
