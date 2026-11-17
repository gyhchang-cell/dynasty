package com.sammy.malum.client.extensions;

import com.sammy.malum.client.scarf.*;
import com.sammy.malum.config.*;
import com.sammy.malum.registry.client.*;
import com.sammy.malum.registry.common.item.*;
import net.minecraft.client.model.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.item.*;
import org.jetbrains.annotations.*;
import team.lodestar.lodestone.modules.rendering.model.entity.armor.*;
import team.lodestar.lodestone.systems.rendering.rendeertype.*;

import java.awt.*;
import java.util.function.*;

public class MalignantArmorItemExtensions extends LodestoneArmorClientItemExtensions {
    public MalignantArmorItemExtensions(Supplier<LodestoneArmorModel> model) {
        super(model);
    }

    @Override
    public @NotNull Model getGenericArmorModel(@NotNull LivingEntity entity, @NotNull ItemStack itemStack, @NotNull EquipmentSlot armorSlot, @NotNull HumanoidModel playerModel) {
        var model = super.getGenericArmorModel(entity, itemStack, armorSlot, playerModel);
        if (armorSlot.equals(EquipmentSlot.CHEST)) {
            var skin = itemStack.get(MalumDataComponents.APPLIED_ITEM_SKIN);
            RenderTypeToken scarfToken = skin != null ?
                    RenderTypeToken.createToken(skin.name().withPrefix("textures/vfx/scarf/").withSuffix(".png"))
                    : MalumRenderTypeTokens.SCARF;
            ScarfRenderHandler.addScarfRenderer(entity, (consumer) -> {
                boolean noSkin = skin == null;
                int scarfCount = noSkin ? 2 : 1;
                float scale = noSkin ? 0.35f : 0.4f;
                float endingScale = noSkin ? 0.45f : 1f;
                float offset = noSkin ? 0.25f : 0.2f;
                for (int i = 0; i < scarfCount; i++) {
                    var data = new ScarfRenderHandler.ScarfRenderData(scarfToken, ClientConfig.SCARF_LENGTH.getConfigValue())
                            .setPredicate(() -> {
                                ItemStack stack = entity.getItemBySlot(armorSlot);
                                return !stack.isEmpty() && stack.is(itemStack.getItem());
                            })
                            .setScale(scale)
                            .setEndingScale(endingScale)
                            .setHorizontalOffset(i == 0 ? -offset : offset);
                    if (noSkin) {
                        data.setSecondaryColor(new Color(150, 150, 150));
                    }
                    consumer.accept(data);
                }
            });
        }
        return model;
    }
}