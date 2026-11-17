package org.zala.crossbowmulticharge.client;

import com.mojang.blaze3d.systems.RenderSystem;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.rendering.v1.HudRenderCallback;
import net.minecraft.client.MinecraftClient;
import net.minecraft.client.item.ModelPredicateProviderRegistry;
import net.minecraft.client.util.math.MatrixStack;
import net.minecraft.enchantment.EnchantmentHelper;
import net.minecraft.item.CrossbowItem;
import net.minecraft.item.ItemStack;
import net.minecraft.item.Items;
import net.minecraft.nbt.NbtElement;
import net.minecraft.nbt.NbtList;
import net.minecraft.util.Colors;
import net.minecraft.util.Identifier;
import net.minecraft.util.math.ColorHelper;
import net.minecraft.util.math.MathHelper;
import org.zala.crossbowmulticharge.Crossbowmulticharge;
import org.zala.crossbowmulticharge.moditems.ModContent;

import java.util.Objects;

public class CrossbowmultichargeClient implements ClientModInitializer {
    private static final Identifier ICONS = new Identifier(Crossbowmulticharge.MOD_ID, "textures/gui/arrows.png");

    private int scaledWidth;
    private int scaledHeight;

    @Override
    public void onInitializeClient() {
        ModModelPredicate.initialize();

        //HUD
        HudRenderCallback.EVENT.register((context, tickDelta) -> {
            this.scaledWidth = context.getScaledWindowWidth();
            this.scaledHeight = context.getScaledWindowHeight();

            assert MinecraftClient.getInstance().player != null;
            ItemStack item = MinecraftClient.getInstance().player.getMainHandStack();
            int currentStorageSize = EnchantmentHelper.getLevel(ModContent.STORAGEUP, item) == 0 ? 6 : 10;
            int halfStorageSize = currentStorageSize / 2;

            if (item.getItem() instanceof CrossbowItem) {
                NbtList list = Objects.requireNonNull(item.getNbt()).getList("ChargedProjectiles", NbtElement.COMPOUND_TYPE);
                for (int i = 0; i < currentStorageSize - list.size(); i++) {
                    context.drawTexture(ICONS, this.scaledWidth / 2 + (halfStorageSize-i-1)*8, this.scaledHeight / 2 + 24, 0, 0, 8, 8, 32, 8);
                }
                for (int i = 0; i < list.size(); i++) {
                    if (ItemStack.fromNbt(list.getCompound(i)).isOf(Items.FIREWORK_ROCKET)) {
                        context.drawTexture(ICONS, this.scaledWidth / 2 + (i-halfStorageSize)*8, this.scaledHeight / 2 + 24, 16, 0, 8, 8, 32, 8);
                    }
                    else {
                        context.drawTexture(ICONS, this.scaledWidth / 2 + (i-halfStorageSize)*8, this.scaledHeight / 2 + 24, 8, 0, 8, 8, 32, 8);
                    }
                }
            }
        });
    }
}
