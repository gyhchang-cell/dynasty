package com.dynasty.client;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.entity.player.ItemTooltipEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;

/** Search metadata is indexed by both creative search and JEI, without visible tooltip clutter. */
@Mod.EventBusSubscriber(modid="dynasty", value=Dist.CLIENT)
public final class DynastySearchAliases {
    private static final Map<String,List<String>> ALIASES = load();
    private static Map<String,List<String>> load() {
        try (var input=DynastySearchAliases.class.getResourceAsStream("/assets/dynasty/search_aliases.json")) {
            if(input==null)return Map.of();
            return new Gson().fromJson(new InputStreamReader(input,StandardCharsets.UTF_8),
                    new TypeToken<Map<String,List<String>>>(){}.getType());
        } catch(java.io.IOException ex) { throw new IllegalStateException("Cannot read item search aliases",ex); }
    }
    public static List<String> aliases(ItemStack stack) {
        return ALIASES.getOrDefault(stack.getDescriptionId(),List.of());
    }
    @SubscribeEvent public static void indexCreative(ItemTooltipEvent event) {
        // Forge's creative search tree requests NORMAL.asCreative() with no player.
        // Real inventory/creative hover tooltips retain their short visible descriptions.
        if(event.getEntity()==null && event.getFlags().isCreative())
            for(String alias:aliases(event.getItemStack()))event.getToolTip().add(Component.literal(alias));
    }
}
