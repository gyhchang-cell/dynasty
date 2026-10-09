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
        if(e.getItemStack().is(com.dynasty.expansion.ExpansionContent.item("qimen_cable")))e.getToolTip().add(Component.translatable("tooltip.dynasty.qimen_cable").withStyle(ChatFormatting.GRAY));
        if(e.getItemStack().is(com.dynasty.expansion.ExpansionContent.item("qimen_gear")))e.getToolTip().add(Component.translatable("tooltip.dynasty.qimen_gear").withStyle(ChatFormatting.GRAY));
        if(e.getItemStack().is(com.dynasty.DynastyBlocks.IMPERIAL_LANTERN.get().asItem()))e.getToolTip().add(Component.translatable("tooltip.dynasty.oil_lantern").withStyle(ChatFormatting.GRAY));
        if(e.getItemStack().is(com.dynasty.DynastyBlocks.INCENSE_BURNER.get().asItem()))e.getToolTip().add(Component.translatable("tooltip.dynasty.oil_incense").withStyle(ChatFormatting.GRAY));
        boolean present=false;
        for(String id:InfusionTraits.slots(e.getItemStack())){var t=InfusionTraits.get(id);if(t!=null){present=true;e.getToolTip().add(Component.translatable("infusion.dynasty.tooltip",t.name()).withStyle(ChatFormatting.DARK_AQUA));if(Screen.hasShiftDown())e.getToolTip().add(t.description().copy().withStyle(ChatFormatting.GRAY));}}
        var material=InfusionTraits.material(e.getItemStack());
        if(material!=null){present=true;e.getToolTip().add(Component.translatable("infusion.dynasty.material_hint",material.name()).withStyle(ChatFormatting.DARK_AQUA));if(Screen.hasShiftDown()){e.getToolTip().add(material.description().copy().withStyle(ChatFormatting.GRAY));e.getToolTip().add(material.applicability().copy().withStyle(ChatFormatting.GRAY));}}
        if(present&&!Screen.hasShiftDown())e.getToolTip().add(Component.translatable("infusion.dynasty.shift").withStyle(ChatFormatting.DARK_GRAY));
    }
}
