package com.dynasty;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.ItemTags;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.registries.RegistryObject;
import top.theillusivec4.curios.api.CuriosApi;

import java.util.Set;
import java.util.UUID;

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
            CuriosApi.registerCurioPredicate(new ResourceLocation(Dynasty.MODID, "accessory"), result ->
                    result.stack().is(ItemTags.create(new ResourceLocation(Dynasty.MODID, "accessories")))
                    || result.stack().getTags().anyMatch(tag -> tag.location().getNamespace().equals("curios")));
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

    private static final UUID QUEST_SLOTS = UUID.fromString("d1a5c0de-0000-4000-8000-000000000010");

    /** 只更新自己的加槽修饰符，不覆盖其他模组的奖励；同一进度重复同步不会叠加。 */
    public static void syncQuestSlots(LivingEntity entity, int bonus) {
        CuriosApi.getCuriosInventory(entity).ifPresent(handler ->
                handler.getStacksHandler("curio").ifPresent(stacks -> {
                    AttributeModifier previous = stacks.getModifiers().get(QUEST_SLOTS);
                    if (previous != null && previous.getAmount() == bonus) {
                        return;
                    }
                    if (previous != null) {
                        stacks.removeModifier(QUEST_SLOTS);
                    }
                    if (bonus > 0) {
                        stacks.addPermanentModifier(new AttributeModifier(QUEST_SLOTS,
                                "dynasty_quest_slots", bonus, AttributeModifier.Operation.ADDITION));
                    }
                }));
    }
}
