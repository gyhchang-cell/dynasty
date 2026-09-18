package com.dynasty.command;

import com.dynasty.Dynasty;
import com.dynasty.entity.DynastyEntities;
import com.dynasty.entity.ImperialSoldier;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.IntegerArgumentType;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.RegisterCommandsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 王朝命令系统：科举 GUI / 调兵 / 开国。
 * Dynasty commands: Keju GUI, raising troops, founding your empire.
 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public class DynastyCommands {

    @SubscribeEvent
    public static void onRegisterCommands(RegisterCommandsEvent event) {
        CommandDispatcher<CommandSourceStack> dispatcher = event.getDispatcher();
        dispatcher.register(Commands.literal("dynasty")
                .then(Commands.literal("help").executes(ctx -> {
                    ctx.getSource().sendSuccess(() -> Component.literal(
                            "§6[王朝]§r /dynasty keju 参加科举 | /dynasty answer <1-3> 作答 | "
                                    + "/dynasty army <1-10> 调兵 | /dynasty found 开国"), false);
                    return 1;
                }))
                .then(Commands.literal("keju").executes(ctx -> {
                    if (!(ctx.getSource().getEntity() instanceof ServerPlayer player)) {
                        return 0;
                    }
                    com.dynasty.DynastyKeju.openExam(player);
                    return 1;
                }))
                .then(Commands.literal("answer")
                        .requires(source -> source.hasPermission(2))
                        .then(Commands.argument("choice", IntegerArgumentType.integer(1, 3)).executes(ctx -> {
                            if (!(ctx.getSource().getEntity() instanceof ServerPlayer player)) {
                                return 0;
                            }
                            Integer idx = com.dynasty.DynastyKeju.pending(player);
                            if (idx == null) {
                                player.sendSystemMessage(Component.literal("§c[科举] 请先使用科举试卷或在界面中开始考试"));
                                return 0;
                            }
                            com.dynasty.DynastyKeju.handleAnswer(player,
                                    idx, ctx.getArgument("choice", Integer.class));
                            return 1;
                        })))
                .then(Commands.literal("army")
                        .then(Commands.literal("formation")
                                .then(Commands.argument("formation", com.mojang.brigadier.arguments.StringArgumentType.word())
                                        .suggests((ctx, builder) -> {
                                            for (String f : com.dynasty.DynastyArmy.FORMATIONS) {
                                                builder.suggest(f);
                                            }
                                            return builder.buildFuture();
                                        })
                                        .executes(ctx -> formArmy(ctx, 8))
                                        .then(Commands.argument("count", IntegerArgumentType.integer(1, 64))
                                                .executes(ctx -> formArmy(ctx, ctx.getArgument("count", Integer.class))))))
                        .then(Commands.argument("count", IntegerArgumentType.integer(1, 10)).executes(ctx -> {
                            if (!(ctx.getSource().getEntity() instanceof ServerPlayer player)) {
                                return 0;
                            }
                            int count = ctx.getArgument("count", Integer.class);
                            var level = ctx.getSource().getLevel();
                            for (int i = 0; i < count; i++) {
                                ImperialSoldier soldier = DynastyEntities.IMPERIAL_SOLDIER.get().create(level);
                                if (soldier == null) {
                                    continue;
                                }
                                double dx = (player.getRandom().nextDouble() - 0.5D) * 4.0D;
                                double dz = (player.getRandom().nextDouble() - 0.5D) * 4.0D;
                                soldier.setOwner(player);
                                soldier.moveTo(player.getX() + dx, player.getY(), player.getZ() + dz, player.getYRot(), 0.0F);
                                level.addFreshEntity(soldier);
                            }
                            player.sendSystemMessage(Component.literal("§6[虎符]§r 已调动 " + count + " 名帝国士兵！"));
                            return 1;
                        })))
                .then(Commands.literal("found").executes(ctx -> {
                    if (!(ctx.getSource().getEntity() instanceof ServerPlayer player)) {
                        return 0;
                    }
                    player.addEffect(new net.minecraft.world.effect.MobEffectInstance(
                            com.dynasty.DynastyEffects.LOYALTY.get(), 20 * 300, 0));
                    player.addEffect(new net.minecraft.world.effect.MobEffectInstance(
                            com.dynasty.DynastyEffects.MANDATE_OF_HEAVEN.get(), 20 * 300, 0));
                    player.sendSystemMessage(Component.literal("§6[开国]§r 王朝已立！万民归心，天命在身。"));
                    return 1;
                }))
                .then(Commands.literal("stats").executes(ctx -> {
                    if (!(ctx.getSource().getEntity() instanceof ServerPlayer player)) {
                        return 0;
                    }
                    com.dynasty.DynastyStats.showStats(player);
                    return 1;
                }))
                .then(Commands.literal("guide").executes(ctx -> {
                    if (!(ctx.getSource().getEntity() instanceof ServerPlayer player)) {
                        return 0;
                    }
                    player.getInventory().add(new net.minecraft.world.item.ItemStack(
                            com.dynasty.DynastyItems.DYNASTY_GUIDE.get()));
                    player.sendSystemMessage(Component.literal("§6[图鉴]§r 已获得《王朝图鉴》，右键打开。"));
                    return 1;
                }))
                .then(Commands.literal("merit")
                        .requires(source -> source.hasPermission(2))
                        .then(Commands.argument("amount", IntegerArgumentType.integer(-10000, 10000)).executes(ctx -> {
                            if (!(ctx.getSource().getEntity() instanceof ServerPlayer player)) {
                                return 0;
                            }
                            com.dynasty.DynastyStats.addMerit(player, ctx.getArgument("amount", Integer.class));
                            player.sendSystemMessage(Component.literal("§6[功名]§r 当前功名 "
                                    + com.dynasty.DynastyStats.getMerit(player)
                                    + "（" + com.dynasty.DynastyStats.rankName(player, true) + "）"));
                            return 1;
                        })))
                .then(Commands.literal("unlock_curio")
                        .requires(source -> source.hasPermission(2))
                        .then(Commands.argument("milestone", com.mojang.brigadier.arguments.StringArgumentType.word())
                                .suggests((ctx, builder) -> {
                                    com.dynasty.DynastySlotProgression.milestoneIds().forEach(builder::suggest);
                                    return builder.buildFuture();
                                })
                                .executes(ctx -> {
                                    if (!(ctx.getSource().getEntity() instanceof ServerPlayer player)) {
                                        return 0;
                                    }
                                    return com.dynasty.DynastySlotProgression.unlock(player,
                                            ctx.getArgument("milestone", String.class));
                                })))
                .then(Commands.literal("rank")
                        .requires(source -> source.hasPermission(2))
                        .then(Commands.argument("level", IntegerArgumentType.integer(0, 19)).executes(ctx -> {
                            if (!(ctx.getSource().getEntity() instanceof ServerPlayer player)) {
                                return 0;
                            }
                            com.dynasty.DynastyStats.setRank(player, ctx.getArgument("level", Integer.class));
                            com.dynasty.DynastyRankPerks.apply(player);
                            player.sendSystemMessage(Component.literal("§6[官职]§r 官阶已设为 "
                                    + com.dynasty.DynastyStats.rankName(player, true)));
                            return 1;
                        })))
                .then(Commands.literal("rebellion")
                        .then(Commands.argument("value", IntegerArgumentType.integer(-100, 100)).executes(ctx -> {
                            if (!(ctx.getSource().getEntity() instanceof ServerPlayer player)) {
                                return 0;
                            }
                            com.dynasty.DynastyStats.addRebellion(player, ctx.getArgument("value", Integer.class));
                            player.sendSystemMessage(Component.literal("§6[民心]§r 叛乱值已调整为 "
                                    + com.dynasty.DynastyStats.getRebellion(player) + "%"));
                            return 1;
                        })))
                .then(Commands.literal("festival")
                        .requires(source -> source.hasPermission(2))
                        .then(Commands.argument("id", com.mojang.brigadier.arguments.StringArgumentType.word())
                                .suggests((ctx, builder) -> {
                                    for (String id : com.dynasty.DynastyFestivals.IDS) {
                                        builder.suggest(id);
                                    }
                                    return builder.buildFuture();
                                })
                                .executes(ctx -> {
                                    if (!(ctx.getSource().getEntity() instanceof ServerPlayer player)) {
                                        return 0;
                                    }
                                    com.dynasty.DynastyFestivals.trigger(
                                            (net.minecraft.server.level.ServerLevel) player.level(),
                                            ctx.getArgument("id", String.class), player);
                                    return 1;
                                })))
        );
    }

    /** 列阵 / forms up an army formation */
    private static int formArmy(com.mojang.brigadier.context.CommandContext<CommandSourceStack> ctx, int count) {
        if (!(ctx.getSource().getEntity() instanceof ServerPlayer player)) {
            return 0;
        }
        com.dynasty.DynastyArmy.formUp(player,
                ctx.getArgument("formation", String.class), count);
        return 1;
    }
}
