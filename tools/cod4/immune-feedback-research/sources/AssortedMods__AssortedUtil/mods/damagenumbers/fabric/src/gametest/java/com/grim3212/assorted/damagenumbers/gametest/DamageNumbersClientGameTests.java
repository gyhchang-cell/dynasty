package com.grim3212.assorted.damagenumbers.gametest;

import com.grim3212.assorted.damagenumbers.Constants;
import com.grim3212.assorted.lib.test.ClientChecks;
import com.grim3212.assorted.damagenumbers.client.damage.DamageKind;
import com.grim3212.assorted.damagenumbers.client.damage.DamageNumbers;
import net.fabricmc.fabric.api.client.gametest.v1.FabricClientGameTest;
import net.fabricmc.fabric.api.client.gametest.v1.context.ClientGameTestContext;
import net.fabricmc.fabric.api.client.gametest.v1.context.TestSingleplayerContext;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityTypes;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.zombie.Husk;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.gamerules.GameRules;

/** What a server cannot see: a damage number off a real hit. {@code ./gradlew :damagenumbers:fabric:runClientGameTest} screenshots it. */
public class DamageNumbersClientGameTests implements FabricClientGameTest {

    @Override
    public void runTest(ClientGameTestContext context) {
        try (TestSingleplayerContext world = context.worldBuilder().create()) {
            ClientChecks.assertDrawsRight(context, Constants.MOD_ID);
            world.getConnection().waitForChunksRender();

            int husk = world.getServer().computeOnServer(server -> {
                ServerLevel level = server.overworld();
                level.getGameRules().set(GameRules.ADVANCE_TIME, false, server);
                server.getCommands().performPrefixedCommand(server.createCommandSourceStack(), "time set noon");
                ServerPlayer player = server.getPlayerList().getPlayers().get(0);
                player.connection.teleport(player.getX(), player.getY(), player.getZ(), 180.0F, 15.0F);
                player.setItemInHand(InteractionHand.MAIN_HAND, new ItemStack(Items.DIAMOND_SWORD));

                // A husk, not a zombie: at noon a zombie would burn, and its fire numbers would muddle the sword's.
                Husk entity = EntityTypes.HUSK.create(level, EntitySpawnReason.COMMAND);
                entity.snapTo(player.getX() + 2.5D, player.getY(), player.getZ() - 6.0D, 0.0F, 0.0F);
                entity.setNoAi(true);
                level.addFreshEntity(entity);
                return entity.getId();
            });

            context.waitFor(client -> client.level.getEntity(husk) != null);
            world.getServer().runOnServer(server -> {
                ServerLevel level = server.overworld();
                ServerPlayer player = server.getPlayerList().getPlayers().get(0);
                ((LivingEntity) level.getEntity(husk)).hurtServer(level, level.damageSources().playerAttack(player), 5.0F);
            });
            context.waitFor(client -> !DamageNumbers.popups().isEmpty());
            context.runOnClient(client -> {
                int color = DamageNumbers.popups().getFirst().color();
                if (color != DamageKind.MELEE.color()) {
                    throw new AssertionError("a sword hit came up in colour " + Integer.toHexString(color) + ", not melee's");
                }
            });
            context.waitTicks(3);
            context.takeScreenshot("assorteddamagenumbers_hit");
        }
    }
}
