package com.dynasty;
import net.minecraft.network.chat.Component;
import java.util.List;
/** Existing single-use talismans: one list for native discovery and optional JEI information. */
public final class TalismanDiscovery {
    public static final List<String> IDS=List.of("fire_talisman","thunder_talisman","wind_talisman","stealth_talisman","vajra_talisman","soul_talisman","return_talisman");
    public static Component[] details(String id){
        if(!IDS.contains(id))return new Component[0];
        return new Component[]{Component.translatable("jei.dynasty.talisman.source."+id),Component.translatable("jei.dynasty.talisman.use."+id),Component.translatable("jei.dynasty.talisman.single_use")};
    }
    private TalismanDiscovery(){}
}
