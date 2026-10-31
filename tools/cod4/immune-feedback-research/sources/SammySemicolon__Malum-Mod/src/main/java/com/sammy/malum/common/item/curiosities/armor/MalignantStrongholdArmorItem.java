package com.sammy.malum.common.item.curiosities.armor;

import com.sammy.malum.MalumMod;
import com.sammy.malum.registry.common.MalumAttributes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EquipmentSlotGroup;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.item.component.ItemAttributeModifiers;
import team.lodestar.lodestone.registry.common.*;
import team.lodestar.wayward_attributes.core.registry.WaywardAttributeTypes;

import java.util.List;

import static com.sammy.malum.registry.common.item.MalumArmorTiers.MALIGNANT_ALLOY;

public class MalignantStrongholdArmorItem extends MalumArmorItem {

    public MalignantStrongholdArmorItem(Type slot, Properties builder) {
        super(MALIGNANT_ALLOY, slot, 42, builder);
    }

    @Override
    public List<ItemAttributeModifiers.Entry> createExtraAttributes() {
        var group = EquipmentSlotGroup.bySlot(getEquipmentSlot());
        var resourcelocation = MalumMod.malumPath("malignant_stronghold_armor." + type.getName());
        ItemAttributeModifiers.Builder attributes = ItemAttributeModifiers.builder();
        attributes.add(WaywardAttributeTypes.MAGIC_RESISTANCE, new AttributeModifier(resourcelocation, 0.25f, AttributeModifier.Operation.ADD_VALUE), group);
        attributes.add(MalumAttributes.MALIGNANT_CONVERSION, new AttributeModifier(resourcelocation, 0.25f, AttributeModifier.Operation.ADD_VALUE), group);
        return attributes.build().modifiers();
    }

    @Override
    public ResourceLocation getArmorTexture() {
        return MalumMod.malumPath("textures/armor/malignant_stronghold.png");
    }
}
