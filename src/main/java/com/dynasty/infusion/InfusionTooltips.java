package com.dynasty.infusion;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraftforge.event.entity.player.ItemTooltipEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid="dynasty")
public final class InfusionTooltips {
    @SubscribeEvent public static void tooltip(ItemTooltipEvent e){
        // Original material tooltip remains untouched; the table provides material explanations.
        var ids=InfusionTraits.slots(e.getItemStack());
        for(String id:ids){var t=InfusionTraits.get(id);if(t!=null)e.getToolTip().add(Component.literal("炼入 · "+t.name()+"："+t.description()).withStyle(ChatFormatting.DARK_AQUA));}
    }
}
