package com.dynasty.dungeon;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.Level;
import java.util.List;

/** A consumed native crafting ingredient, distinct from the existing general blueprint. */
public final class HighGradeMechanismPlanItem extends Item {
    public HighGradeMechanismPlanItem(){super(new Properties().stacksTo(1).rarity(Rarity.RARE));}
    @Override public void appendHoverText(ItemStack stack,Level level,List<Component> lines,TooltipFlag flag){
        lines.add(Component.translatable("tooltip.dynasty.high_grade_mechanism_plan").withStyle(ChatFormatting.GRAY));
    }
}
