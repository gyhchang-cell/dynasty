package dev.melix.damagenumbers;

import com.mojang.brigadier.arguments.FloatArgumentType;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.minecraft.commands.Commands;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.arguments.EntityArgument;
import net.minecraft.commands.arguments.coordinates.Vec3Argument;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;

import java.lang.reflect.Method;

final class ShowDamageCommand {
    private ShowDamageCommand() {
    }

    static void register() {
        CommandRegistrationCallback.EVENT.register((dispatcher, registryAccess, environment) -> {
            var value = Commands.argument("value", FloatArgumentType.floatArg(0.0F))
                    .executes(ShowDamageCommand::execute);
            var position = Commands.argument("position", Vec3Argument.vec3()).then(value);
            var preset = Commands.argument("presetName", StringArgumentType.string()).then(position);
            var target = Commands.argument("target", EntityArgument.players()).then(preset);
            dispatcher.register(Commands.literal("showDamage")
                    .requires(source -> !(source.getEntity() instanceof ServerPlayer player)
                            || isOperator(source.getServer().getPlayerList(), player))
                    .then(target));
        });
    }

    private static int execute(CommandContext<CommandSourceStack> context) throws CommandSyntaxException {
        String presetName = StringArgumentType.getString(context, "presetName");
        Vec3 position = Vec3Argument.getVec3(context, "position");
        float value = FloatArgumentType.getFloat(context, "value");
        int sent = 0;
        for (ServerPlayer player : EntityArgument.getPlayers(context, "target")) {
            ShowDamageNetworking.send(player, presetName, position, value);
            sent++;
        }
        int targetCount = sent;
        context.getSource().sendSuccess(() -> Component.literal(
                "Damage number sent to " + targetCount + " player(s)"), false);
        return sent;
    }

    private static boolean isOperator(Object playerList, ServerPlayer player) {
        Object profile = player.getGameProfile();
        Object nameAndId = null;
        try {
            nameAndId = player.getClass().getMethod("nameAndId").invoke(player);
        } catch (ReflectiveOperationException ignored) {
        }
        for (Method method : playerList.getClass().getMethods()) {
            if (!method.getName().equals("isOp") || method.getParameterCount() != 1) {
                continue;
            }
            Class<?> parameter = method.getParameterTypes()[0];
            Object identity = parameter.isInstance(profile) ? profile
                    : parameter.isInstance(nameAndId) ? nameAndId : null;
            if (identity != null) {
                try {
                    return Boolean.TRUE.equals(method.invoke(playerList, identity));
                } catch (ReflectiveOperationException ignored) {
                }
            }
        }
        return false;
    }
}
