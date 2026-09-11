package com.dynasty;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.registries.RegistryObject;
import top.theillusivec4.curios.api.CuriosApi;

import java.util.Set;

/**
 * 真正碰 Curios 类的桥接层：只有在确认 Curios 存在时才会被 {@link DynastyCuriosSetup} 反射加载，
 * 这样没有 Curios 的环境（例如纯本体或开发环境）不会因为类校验而报 NoClassDefFoundError。
 *
 * The bridge that actually touches Curios classes. It is only loaded reflectively when Curios exists.
 */
public final class DynastyCuriosBridge {

    private DynastyCuriosBridge() {
    }

    /** 挂上 common setup 监听 / attaches the common-setup listener */
    public static void attach(IEventBus modEventBus) {
        modEventBus.addListener(DynastyCuriosBridge::onCommonSetup);
    }

    private static void onCommonSetup(FMLCommonSetupEvent event) {
        event.enqueueWork(() -> {
            for (RegistryObject<Item> item : DynastyTrinkets.accessoryItems()) {
                CuriosApi.registerCurio(item.get(), DynastyCurioCharm.INSTANCE);
            }
            Dynasty.LOGGER.info("[Dynasty] registered {} curio items with Curios (trinket slots)",
                    DynastyTrinkets.accessoryItems().size());
        });
    }

    /** 收集玩家身上（含 Curios 槽位）的饰品 id / collects trinket ids worn in Curios slots */
    public static void collectEquipped(LivingEntity entity, Set<String> out) {
        CuriosApi.getCuriosInventory(entity).ifPresent(handler -> {
            net.minecraftforge.items.IItemHandler equipped = handler.getEquippedCurios();
            for (int i = 0; i < equipped.getSlots(); i++) {
                String id = DynastyTrinkets.idOf(equipped.getStackInSlot(i));
                if (id != null) {
                    out.add(id);
                }
            }
        });
    }
}
