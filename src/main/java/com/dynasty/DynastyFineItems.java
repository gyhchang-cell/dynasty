package com.dynasty;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.SmallFireball;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * 王朝扩展物品：美食、工艺材料、符箓、任务手札与节令灯。
 * Dynasty extended items: delicacies, craft materials, talismans, the quest ledger and the festival lantern.
 */
@SuppressWarnings("null")
public class DynastyFineItems {

    public static final DeferredRegister<Item> ITEMS =
            DeferredRegister.create(ForgeRegistries.ITEMS, Dynasty.MODID);

    private static RegistryObject<Item> basic(String name) {
        return ITEMS.register(name, () -> new Item(new Item.Properties()));
    }

    private static RegistryObject<Item> food(String name, int nutrition, float saturation, boolean fast) {
        return ITEMS.register(name, () -> new Item(new Item.Properties().food(new FoodProperties.Builder()
                .nutrition(nutrition).saturationMod(saturation).fast().build())));
    }

    /** 带状态效果的食物 / food with an effect */
    private static RegistryObject<Item> effectFood(String name, int nutrition, float saturation,
                                                   net.minecraft.world.effect.MobEffect effect, int seconds, int amp) {
        return ITEMS.register(name, () -> new Item(new Item.Properties().food(new FoodProperties.Builder()
                .nutrition(nutrition).saturationMod(saturation)
                .effect(() -> new MobEffectInstance(effect, 20 * seconds, amp), 1.0F).build())));
    }

    // ---------------------------------------------------------------- 美食
    public static final RegistryObject<Item> ZONGZI = food("zongzi", 6, 0.7F, false);
    public static final RegistryObject<Item> TANGYUAN = effectFood("tangyuan", 5, 0.6F,
            MobEffects.REGENERATION, 6, 0);
    public static final RegistryObject<Item> NIANGao = effectFood("niangao", 6, 0.7F,
            MobEffects.DAMAGE_RESISTANCE, 20, 0);
    public static final RegistryObject<Item> OSMANTHUS_CAKE = effectFood("osmanthus_cake", 4, 0.5F,
            MobEffects.LUCK, 60, 0);
    public static final RegistryObject<Item> CURED_MEAT = food("cured_meat", 8, 0.8F, false);
    public static final RegistryObject<Item> ROAST_DUCK = food("roast_duck", 10, 1.0F, false);
    public static final RegistryObject<Item> LONGEVITY_NOODLES = effectFood("longevity_noodles", 8, 0.9F,
            MobEffects.HEALTH_BOOST, 120, 1);
    public static final RegistryObject<Item> BAIJIU = ITEMS.register("baijiu",
            () -> new Item(new Item.Properties().food(new FoodProperties.Builder()
                    .nutrition(3).saturationMod(0.2F).alwaysEat()
                    .effect(() -> new MobEffectInstance(MobEffects.DAMAGE_BOOST, 20 * 30, 0), 1.0F)
                    .effect(() -> new MobEffectInstance(MobEffects.CONFUSION, 20 * 10, 0), 0.6F)
                    .build())));

    // ---------------------------------------------------------------- 材料与工艺
    public static final RegistryObject<Item> RAW_SILK = basic("raw_silk");
    public static final RegistryObject<Item> SILK = basic("silk");
    public static final RegistryObject<Item> BROCADE = basic("brocade");
    public static final RegistryObject<Item> BAMBOO_SLIP = basic("bamboo_slip");
    public static final RegistryObject<Item> INK_STICK = basic("ink_stick");
    public static final RegistryObject<Item> INK_BRUSH = ITEMS.register("ink_brush",
            () -> new Item(new Item.Properties().stacksTo(1).durability(64)));
    public static final RegistryObject<Item> BRONZE_MIRROR = basic("bronze_mirror");
    public static final RegistryObject<Item> ROOF_TILE = basic("roof_tile");

    // ---------------------------------------------------------------- 符箓
    /** 火符：爆炎（一次性，600+攻击×3）*/
    public static final RegistryObject<Item> FIRE_TALISMAN = charm("fire_talisman");
    /** 雷符：三道落雷（一次性，800+攻击×4）*/
    public static final RegistryObject<Item> THUNDER_TALISMAN = charm("thunder_talisman");
    /** 御风符：罡风击飞 + 疾风 */
    public static final RegistryObject<Item> WIND_TALISMAN = charm("wind_talisman");
    /** 隐身符：隐身 60 秒并清除仇恨 */
    public static final RegistryObject<Item> STEALTH_TALISMAN = charm("stealth_talisman");
    /** 金刚符：抗性 III + 力量 II（替代原来的回春符，不回血）*/
    public static final RegistryObject<Item> VAJRA_TALISMAN = charm("vajra_talisman");
    /** 摄魂符：范围 500+攻击×3 伤害 + 失明 + 虚弱 */
    public static final RegistryObject<Item> SOUL_TALISMAN = charm("soul_talisman");
    /** 归乡符：回出生点并净化 */
    public static final RegistryObject<Item> RETURN_TALISMAN = charm("return_talisman");

    // ---------------------------------------------------------------- 特殊功能物品
    public static final RegistryObject<Item> FESTIVAL_LANTERN = ITEMS.register("festival_lantern",
            () -> new FestivalLanternItem(new Item.Properties().stacksTo(1)));

    private static RegistryObject<Item> charm(String name) {
        return ITEMS.register(name, () -> new TalismanCharmItem(new Item.Properties().stacksTo(16)));
    }
}
