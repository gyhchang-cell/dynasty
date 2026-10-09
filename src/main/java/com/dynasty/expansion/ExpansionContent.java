package com.dynasty.expansion;

import com.dynasty.Dynasty;
import net.minecraft.world.item.*;
import net.minecraftforge.registries.*;
import net.minecraftforge.eventbus.api.IEventBus;
import java.util.*;

/** Only new content; existing item IDs and registries are never replaced. */
public final class ExpansionContent {
    public static final DeferredRegister<Item> ITEMS=DeferredRegister.create(ForgeRegistries.ITEMS,Dynasty.MODID);
    public static final Map<String,RegistryObject<Item>> MATERIALS=new LinkedHashMap<>();
    static { for(String id:List.of("qimen_cable","qimen_gear","fox_pelt","wolf_fang","python_gall","crab_shell","kappa_scale","sprite_jade","lantern_oil","locust_dust")) MATERIALS.put(id, ITEMS.register(id,()->new Item(new Item.Properties()))); }
    public static final RegistryObject<Item> REPEATING=ITEMS.register("repeating_crossbow",()->new ExpansionWeapons.BurstCrossbow(false));
    public static final RegistryObject<Item> SIEGE=ITEMS.register("siege_crossbow",()->new ExpansionWeapons.BurstCrossbow(true));
    public static final RegistryObject<Item> ROPE=ITEMS.register("rope_dart",()->new ExpansionWeapons.QimenSword("rope_dart",420,-2.2F));
    public static final RegistryObject<Item> CLAW=ITEMS.register("flying_claw",()->new ExpansionWeapons.QimenSword("flying_claw",300,-2.4F));
    public static final RegistryObject<Item> DUCK=ITEMS.register("mandarin_duck_axe",()->new ExpansionWeapons.QimenSword("mandarin_duck_axe",380,-1.8F));
    public static final RegistryObject<Item> HAMMER=ITEMS.register("meteor_hammer",ExpansionWeapons.MeteorHammer::new);
    public static final Map<String,RegistryObject<Item>> AMMO=new LinkedHashMap<>();
    public static final Map<String,RegistryObject<Item>> SUPPLIES=new LinkedHashMap<>();
    static {
        for(String id:List.of("poison_arrow","pierce_arrow","thunder_arrow","heavy_bolt","repeating_bolt")) AMMO.put(id,ITEMS.register(id,()->new ExpansionWeapons.SpecialArrow(id)));
        for(String id:List.of("regen_pill","qi_pill","antidote_pill","zhuangyuan_wine","marching_wine","soul_incense","guide_incense","army_ration")) SUPPLIES.put(id,ITEMS.register(id,()->new ExpansionSupplies(id)));
    }
    public static void register(IEventBus bus) {
        ExpansionEffects.bootstrap();
        SecondaryMobs.bootstrap(bus);
        SmallInteractions.bootstrap(bus);
        ITEMS.register(bus);
    }
    public static Item item(String id) { return ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty",id)); }
    private ExpansionContent() { }
}
