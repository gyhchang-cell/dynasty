package com.dynasty.client;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.entity.player.ItemTooltipEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;

/** Chest sources are generated from the actual loot tables, not inferred from item lore. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class DynastyAccessorySources {
    private static final Map<String,List<String>> SOURCES=load();
    private static Map<String,List<String>> load(){
        try(var in=DynastyAccessorySources.class.getResourceAsStream("/assets/dynasty/accessory_sources.json")){
            if(in==null)return Map.of();
            return new Gson().fromJson(new java.io.InputStreamReader(in,StandardCharsets.UTF_8),new TypeToken<Map<String,List<String>>>(){}.getType());
        }catch(java.io.IOException ex){throw new IllegalStateException("Cannot read chest sources",ex);}
    }
    @SubscribeEvent public static void append(ItemTooltipEvent e){
        if(!(e.getItemStack().getItem() instanceof com.dynasty.DynastyTrinketTips.Charm))return;
        var id=ForgeRegistries.ITEMS.getKey(e.getItemStack().getItem());
        var keys=SOURCES.getOrDefault(id.toString(),List.of());
        if(keys.isEmpty())return;
        var names=keys.stream().map(k->Component.translatable(k).getString()).toList();
        var tip=e.getToolTip();
        int at=Math.min(1,tip.size());
        tip.add(at,Component.literal((DynastyItemInfo.chinese()?"宝箱：":"Chests: ")
                +String.join(DynastyItemInfo.chinese()?"、":", ",names.subList(0,Math.min(3,names.size()))))
                .withStyle(ChatFormatting.GRAY));
        if(names.size()>3 && DynastyTooltipGate.shiftDown())tip.add(at+1,Component.literal(
                String.join(DynastyItemInfo.chinese()?"、":", ",names.subList(3,names.size()))).withStyle(ChatFormatting.GRAY));
    }
}
