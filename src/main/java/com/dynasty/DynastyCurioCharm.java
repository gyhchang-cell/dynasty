package com.dynasty;

import com.google.common.collect.Multimap;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.item.ItemStack;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.type.capability.ICurio;
import top.theillusivec4.curios.api.type.capability.ICurioItem;

import javax.annotation.Nullable;
import java.util.UUID;

/**
 * 饰品接入 Curios：本模组饰品直接使用 Curios 的槽位（charm / necklace / ring / belt / head / curio）。
 * 数值与效果统一由 DynastyTrinkets 每秒结算（饰品放在 Curios 槽、副手或背包都生效），
 * 因此这里只负责「能被 Curios 装备 / 右键自动佩戴 / 装备音效」。
 *
 * Curios integration: our trinkets use Curios' own slots. All numbers and effects are resolved
 * once per second by DynastyTrinkets (works in Curios slots, in the pouch or in the inventory).
 */
public class DynastyCurioCharm implements ICurioItem {

    public static final DynastyCurioCharm INSTANCE = new DynastyCurioCharm();

    @Override
    public boolean canEquipFromUse(SlotContext slotContext, ItemStack stack) {
        return true;
    }

    @Override
    public ICurio.SoundInfo getEquipSound(SlotContext slotContext, ItemStack stack) {
        return new ICurio.SoundInfo(SoundEvents.ARMOR_EQUIP_GOLD, 1.0F, 1.1F);
    }

    /** 数值统一由 DynastyTrinkets 结算，避免重复叠加 / attributes are applied by DynastyTrinkets */
    @Override
    public Multimap<Attribute, AttributeModifier> getAttributeModifiers(SlotContext slotContext,
                                                                       @Nullable UUID uuid, ItemStack stack) {
        return com.google.common.collect.ImmutableMultimap.of();
    }

    @Override
    public void curioTick(SlotContext slotContext, ItemStack stack) {
        // 由 DynastyTrinkets.tick 统一处理 / handled centrally by DynastyTrinkets.tick
    }
}
