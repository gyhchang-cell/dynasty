package com.dynasty;

import com.dynasty.Dynasty;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.alchemy.Potion;
import net.minecraft.world.item.alchemy.PotionUtils;
import net.minecraft.world.item.alchemy.Potions;
import net.minecraftforge.event.brewing.PotionBrewEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * Dynasty 酿造配方：通过 Forge 的 PotionBrewEvent 把材料酿成王朝药水（无需 AccessTransformer）。
 * Dynasty brewing recipes implemented through Forge's PotionBrewEvent.
 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public class DynastyBrewing {

    /** 材料 → 药水 / ingredient -> potion */
    private static Potion resultFor(ItemStack ingredient) {
        if (ingredient.is(DynastyItems.DRAGON_CRYSTAL.get())) {
            return DynastyPotions.DRAGON_MIGHT.get();
        }
        if (ingredient.is(DynastyItems.JADE.get())) {
            return DynastyPotions.IRON_WALL.get();
        }
        if (ingredient.is(DynastyItems.TALISMAN_PAPER.get())) {
            return DynastyPotions.SWIFT_WIND.get();
        }
        if (ingredient.is(DynastyItems.DRAGON_SCALE.get())) {
            return DynastyPotions.INTIMIDATION.get();
        }
        if (ingredient.is(DynastyItems.CINNABAR.get())) {
            return DynastyPotions.LOYALTY.get();
        }
        return null;
    }

    @SubscribeEvent
    public static void onPotionBrew(PotionBrewEvent.Pre event) {
        ItemStack ingredient = event.getItem(3);
        if (ingredient.isEmpty()) {
            return;
        }
        Potion direct = resultFor(ingredient);

        for (int i = 0; i < 3; i++) {
            ItemStack bottle = event.getItem(i);
            if (bottle.isEmpty() || !(bottle.getItem() instanceof net.minecraft.world.item.PotionItem)) {
                continue;
            }
            Potion current = PotionUtils.getPotion(bottle);

            if (direct != null && current == Potions.AWKWARD) {
                // 粗制的药水 + 王朝材料 → 王朝药水
                event.setItem(i, PotionUtils.setPotion(new ItemStack(bottle.getItem()), direct));
            } else if (ingredient.is(Items.GLOWSTONE_DUST) && current == DynastyPotions.DRAGON_MIGHT.get()) {
                // 荧石粉强化 → 天命药水（长时效）
                event.setItem(i, PotionUtils.setPotion(new ItemStack(bottle.getItem()),
                        DynastyPotions.MANDATE_OF_HEAVEN.get()));
            }
        }
    }
}
