package com.dynasty;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.living.LivingDropsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/**
 * Boss 掉落（进化链的「条件」来源）。
 *
 * 想拿到破军战斧之后的兵器，就必须先击败对应的 Boss 拿信物：
 *   叛将 → 叛将首级    宦官首脑 → 内廷令牌
 *   不死始皇 → 帝骸骨  龙帝 → 龙帝玉玺
 *
 * Boss drops: the tokens that gate the late-game crafting chain.
 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public class DynastyBossDrops {

    @SubscribeEvent
    public static void onDrops(LivingDropsEvent event) {
        if (event.getEntity().level().isClientSide()) {
            return;
        }
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(event.getEntity().getType());
        if (id == null || !id.getNamespace().equals(Dynasty.MODID)) {
            return;
        }
        RandomSource rand = event.getEntity().getRandom();
        switch (id.getPath()) {
            case "dragon_emperor" -> {
                drop(event, DynastyRelics.DRAGON_EMPEROR_SEAL, 1, rand, 1.0F);
                drop(event, DynastyRelics.EMPEROR_BONE, 1, rand, 0.7F);
                drop(event, DynastyItems.DRAGON_CRYSTAL, 4, rand, 1.0F);
            }
            case "undead_first_emperor" -> {
                drop(event, DynastyRelics.EMPEROR_BONE, 1, rand, 1.0F);
                drop(event, DynastyItems.DRAGON_CRYSTAL, 2, rand, 0.8F);
                drop(event, DynastyWeapons.DRAGON_SPEAR, 1, rand, 1.0F);
            }
            case "rebel_general" -> {
                drop(event, DynastyRelics.REBEL_HEAD, 1, rand, 1.0F);
                drop(event, DynastyItems.BRONZE_INGOT, 3, rand, 0.8F);
                drop(event, DynastyWeapons.YITIAN_SWORD, 1, rand, 1.0F);
            }
            case "eunuch_mastermind" -> {
                drop(event, DynastyRelics.EUNUCH_TOKEN, 1, rand, 1.0F);
                drop(event, DynastyItems.SILVER_INGOT, 3, rand, 0.8F);
                drop(event, DynastyWeapons.QINGGANG_SWORD, 1, rand, 1.0F);
            }
            case "assassin" -> {
                // 刺客：稀有掉落鱼肠剑 / rare dagger drop
                drop(event, DynastyWeapons.YUCHANG_DAGGER, 1, rand, 0.04F);
                drop(event, DynastyItems.SILVER_INGOT, 1, rand, 0.2F);
            }
            case "nine_heaven_general" -> {
                drop(event, DynastyItems.SKY_TOKEN, 1, rand, 1.0F);
                drop(event, DynastyRelics.XUANTIAN_JADE, 1, rand, 0.5F);
                drop(event, DynastyItems.DRAGON_CRYSTAL, 3, rand, 1.0F);
            }
            case "dragon_king" -> {
                drop(event, DynastyItems.SEA_TOKEN, 1, rand, 1.0F);
                drop(event, DynastyItems.DRAGON_SCALE, 4, rand, 1.0F);
                drop(event, DynastyItems.DRAGON_CRYSTAL, 4, rand, 1.0F);
                drop(event, DynastyItems.GOLD_COIN, 16, rand, 0.8F);
            }
            case "phoenix" -> drop(event, DynastyItems.DRAGON_SCALE, 2, rand, 1.0F);
            case "nian_beast" -> drop(event, DynastyRelics.REFINED_STEEL, 2, rand, 0.8F);
            case "qilin" -> drop(event, DynastyItems.JADE, 2, rand, 0.8F);
            case "nine_tailed_fox" -> drop(event, DynastyFineItems.SILK, 3, rand, 0.8F);
            case "royal_guard" -> drop(event, DynastyRelics.BLUEPRINT, 1, rand, 0.25F);
            case "terracotta_warrior" -> drop(event, DynastyItems.BRONZE_INGOT, 1, rand, 0.15F);
            default -> {
            }
        }
    }

    private static void drop(LivingDropsEvent event, RegistryObject<Item> item, int count,
                             RandomSource rand, float chance) {
        if (rand.nextFloat() > chance) {
            return;
        }
        int amount = 1 + rand.nextInt(Math.max(1, count));
        ItemEntity entity = new ItemEntity(event.getEntity().level(),
                event.getEntity().getX(), event.getEntity().getY() + 0.5D, event.getEntity().getZ(),
                new ItemStack(item.get(), amount));
        event.getDrops().add(entity);
    }
}
