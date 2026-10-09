package com.dynasty.infusion;
import net.minecraft.ChatFormatting;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.entity.player.ItemTooltipEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class InfusionTooltips {
    @SubscribeEvent public static void tooltip(ItemTooltipEvent e){
        boolean present=false;
        for(String id:InfusionTraits.slots(e.getItemStack())){var t=InfusionTraits.get(id);if(t!=null){present=true;e.getToolTip().add(Component.translatable("infusion.dynasty.tooltip",t.name()).withStyle(ChatFormatting.DARK_AQUA));if(Screen.hasShiftDown())e.getToolTip().add(t.description().copy().withStyle(ChatFormatting.GRAY));}}
        var material=InfusionTraits.material(e.getItemStack());
        if(material!=null){present=true;e.getToolTip().add(Component.translatable("infusion.dynasty.material_hint",material.name()).withStyle(ChatFormatting.DARK_AQUA));if(Screen.hasShiftDown()){e.getToolTip().add(material.description().copy().withStyle(ChatFormatting.GRAY));e.getToolTip().add(material.applicability().copy().withStyle(ChatFormatting.GRAY));}}
        if(present&&!Screen.hasShiftDown())e.getToolTip().add(Component.translatable("infusion.dynasty.shift").withStyle(ChatFormatting.DARK_GRAY));
    }
}
