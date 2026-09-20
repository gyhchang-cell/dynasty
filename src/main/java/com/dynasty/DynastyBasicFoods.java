package com.dynasty;

import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.BowlFoodItem;
import net.minecraft.world.item.Item;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * 六种基础料理 / six basic dishes.
 *
 * 设计约束（本轮）：
 *   * 全部是**普通食物机制**：只给饥饿与饱和度，不加状态效果、不给永久属性；
 *   * 饥饿值以「半个鸡腿 = 1 点」计；{@code saturationMod} 是 FoodProperties 的饱和度系数，
 *     不是最终回复的饱和度数值；
 *   * 两种汤沿用**原版炖菜机制**：<b>最多堆叠 1</b>，食用后由 {@link BowlFoodItem} 返还 1 个碗；
 *   * 蜜汁烤肉用**原版蜂蜜瓶**做原料，玻璃瓶由原版 {@code craftRemainder} 自动返还，
 *     配方里不再额外给瓶（重复给瓶会导致双份）。
 *
 * 贴图目前**复用原版贴图**（见 models/item/*.json），属于临时占位，不是新美术。
 * Basic dishes only: plain food values, no potion effects and no permanent attributes.
 */
@SuppressWarnings("null")
public final class DynastyBasicFoods {

    private DynastyBasicFoods() {
    }

    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, Dynasty.MODID);

    /** 普通食物 / plain food */
    private static RegistryObject<Item> food(String name, int nutrition, float saturation) {
        return ITEMS.register(name, () -> new Item(new Item.Properties().food(
                new FoodProperties.Builder().nutrition(nutrition).saturationMod(saturation).build())));
    }

    /**
     * 炖菜：最多堆叠 1，食用后返还碗（原版 {@link BowlFoodItem} 的行为）。
     * Stew bowl: single stack, bowl returned after eating.
     */
    private static RegistryObject<Item> stew(String name, int nutrition, float saturation) {
        return ITEMS.register(name, () -> new BowlFoodItem(new Item.Properties().stacksTo(1).food(
                new FoodProperties.Builder().nutrition(nutrition).saturationMod(saturation).build())));
    }

    /** 炙肉串：熟猪排 + 熟鸡肉 → ×2。饥饿 8，饱和度系数 0.6 */
    public static final RegistryObject<Item> GRILLED_MEAT_SKEWER = food("grilled_meat_skewer", 8, 0.6F);

    /** 麦香饼：小麦×2 + 鸡蛋 → ×2。饥饿 5，饱和度系数 0.5 */
    public static final RegistryObject<Item> WHEAT_CAKE = food("wheat_cake", 5, 0.5F);

    /** 蜜汁烤肉：熟猪排 + 蜂蜜瓶 → ×1（玻璃瓶由原版机制返还）。饥饿 10，饱和度系数 0.7 */
    public static final RegistryObject<Item> HONEY_ROAST = food("honey_roast", 10, 0.7F);

    /** 田园炖菜：胡萝卜 + 马铃薯 + 棕色蘑菇 + 碗 → ×1，堆叠 1，食用后返还碗。饥饿 8，饱和度系数 0.6 */
    public static final RegistryObject<Item> COUNTRYSIDE_STEW = stew("countryside_stew", 8, 0.6F);

    /** 菌菇鱼汤：熟鳕鱼 + 棕色蘑菇 + 碗 → ×1，堆叠 1，食用后返还碗。饥饿 10，饱和度系数 0.6 */
    public static final RegistryObject<Item> MUSHROOM_FISH_SOUP = stew("mushroom_fish_soup", 10, 0.6F);

    /** 南瓜甜饼：南瓜 + 小麦 + 糖 → ×2。饥饿 6，饱和度系数 0.5 */
    public static final RegistryObject<Item> PUMPKIN_SWEET_CAKE = food("pumpkin_sweet_cake", 6, 0.5F);
}
