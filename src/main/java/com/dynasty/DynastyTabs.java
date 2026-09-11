package com.dynasty;

import com.dynasty.Dynasty;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.RegistryObject;

/**
 * Dynasty 创造模式物品栏 / Dynasty creative tab.
 */
@SuppressWarnings("null")
public class DynastyTabs {

    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, Dynasty.MODID);

    public static final RegistryObject<CreativeModeTab> DYNASTY_TAB = TABS.register("dynasty", () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.dynasty.dynasty"))
            .withTabsBefore(CreativeModeTabs.COMBAT)
            .icon(() -> new ItemStack(DynastyItems.JADE_SEAL.get()))
            .displayItems((params, output) -> {
                // 方块 / blocks
                output.accept(DynastyBlocks.JADE_ORE.get());
                output.accept(DynastyBlocks.DEEPSLATE_JADE_ORE.get());
                output.accept(DynastyBlocks.DRAGON_CRYSTAL_ORE.get());
                output.accept(DynastyBlocks.JADE_BLOCK.get());
                output.accept(DynastyBlocks.BRONZE_BLOCK.get());
                output.accept(DynastyBlocks.PALACE_BRICKS.get());
                output.accept(DynastyBlocks.MARBLE_BLOCK.get());
                output.accept(DynastyBlocks.CRIMSON_PILLAR.get());
                output.accept(DynastyBlocks.IMPERIAL_LANTERN.get());

                // 货币 / currency
                output.accept(DynastyItems.COPPER_COIN.get());
                output.accept(DynastyItems.SILVER_COIN.get());
                output.accept(DynastyItems.GOLD_COIN.get());
                output.accept(DynastyItems.JADE_COIN.get());
                output.accept(DynastyItems.DRAGON_COIN.get());

                // 材料 / materials
                output.accept(DynastyItems.BRONZE_INGOT.get());
                output.accept(DynastyItems.SILVER_INGOT.get());
                output.accept(DynastyItems.JADE.get());
                output.accept(DynastyItems.DRAGON_SCALE.get());
                output.accept(DynastyItems.DRAGON_CRYSTAL.get());
                output.accept(DynastyItems.CINNABAR.get());
                output.accept(DynastyItems.TALISMAN_PAPER.get());

                // 玺印文书 / seals & documents
                output.accept(DynastyItems.JADE_SEAL.get());
                output.accept(DynastyItems.OFFICIAL_SEAL.get());
                output.accept(DynastyItems.EDICT.get());
                output.accept(DynastyItems.TIGER_TALLY.get());
                output.accept(DynastyItems.EXAM_PAPER.get());

                // 食物 / food
                output.accept(DynastyItems.MOONCAKE.get());
                output.accept(DynastyItems.DUMPLING.get());
                output.accept(DynastyItems.TEA.get());

                // 武器工具 / weapons & tools
                output.accept(DynastyGear.SWORD_BRONZE.get());
                output.accept(DynastyGear.SWORD_SILVER.get());
                output.accept(DynastyGear.SWORD_JADE.get());
                output.accept(DynastyGear.SWORD_DRAGON_CRYSTAL.get());
                output.accept(DynastyGear.HALBERD_FANGTIAN.get());
                output.accept(DynastyGear.PICKAXE_JADE.get());
                output.accept(DynastyGear.PICKAXE_DRAGON_CRYSTAL.get());

                // 盔甲 / armor
                output.accept(DynastyGear.JADE_HELMET.get());
                output.accept(DynastyGear.JADE_CHESTPLATE.get());
                output.accept(DynastyGear.JADE_LEGGINGS.get());
                output.accept(DynastyGear.JADE_BOOTS.get());
                output.accept(DynastyGear.DRAGON_SCALE_HELMET.get());
                output.accept(DynastyGear.DRAGON_SCALE_CHESTPLATE.get());
                output.accept(DynastyGear.DRAGON_SCALE_LEGGINGS.get());
                output.accept(DynastyGear.DRAGON_SCALE_BOOTS.get());
                output.accept(DynastyGear.GENERAL_HELMET.get());
                output.accept(DynastyGear.GENERAL_CHESTPLATE.get());
                output.accept(DynastyGear.GENERAL_LEGGINGS.get());
                output.accept(DynastyGear.GENERAL_BOOTS.get());

                // 刷怪蛋 / spawn eggs
                output.accept(DynastyItems.TERRACOTTA_WARRIOR_SPAWN_EGG.get());
                output.accept(DynastyItems.IMPERIAL_SOLDIER_SPAWN_EGG.get());
                output.accept(DynastyItems.UNDEAD_FIRST_EMPEROR_SPAWN_EGG.get());

                // 传送门 / portals
                output.accept(DynastyBlocks.JADE_PORTAL.get());
                output.accept(DynastyBlocks.UNDERWORLD_PORTAL.get());

                // 宫廷装饰 / decoration
                output.accept(DynastyBlocks.DRAGON_THRONE.get());
                output.accept(DynastyBlocks.ALTAR.get());
                output.accept(DynastyBlocks.CHIME_BELL.get());
                output.accept(DynastyBlocks.TAIKO_DRUM.get());
                output.accept(DynastyBlocks.INCENSE_BURNER.get());
                output.accept(DynastyBlocks.SCREEN.get());
                output.accept(DynastyBlocks.PLAQUE.get());

                // 更多食物与丹药 / more food & pills
                output.accept(DynastyItems.CANDIED_HAWTHORN.get());
                output.accept(DynastyItems.DRAGON_BEARD_CANDY.get());
                output.accept(DynastyItems.HOTPOT.get());
                output.accept(DynastyItems.WINE.get());
                output.accept(DynastyItems.IMMORTAL_PEACH.get());
                output.accept(DynastyItems.PILL_LONGEVITY.get());
                output.accept(DynastyItems.PILL_FOCUS.get());
                output.accept(DynastyItems.HEALING_SALVE.get());

                // 药水 / potions
                output.accept(net.minecraft.world.item.alchemy.PotionUtils.setPotion(
                        new net.minecraft.world.item.ItemStack(DynastyItems.DYNASTY_POTION.get()),
                        DynastyPotions.DRAGON_MIGHT.get()));
                output.accept(net.minecraft.world.item.alchemy.PotionUtils.setPotion(
                        new net.minecraft.world.item.ItemStack(DynastyItems.DYNASTY_POTION.get()),
                        DynastyPotions.IRON_WALL.get()));
                output.accept(net.minecraft.world.item.alchemy.PotionUtils.setPotion(
                        new net.minecraft.world.item.ItemStack(DynastyItems.DYNASTY_POTION.get()),
                        DynastyPotions.SWIFT_WIND.get()));
                output.accept(net.minecraft.world.item.alchemy.PotionUtils.setPotion(
                        new net.minecraft.world.item.ItemStack(DynastyItems.DYNASTY_SPLASH_POTION.get()),
                        DynastyPotions.DRAGON_MIGHT.get()));
                output.accept(net.minecraft.world.item.alchemy.PotionUtils.setPotion(
                        new net.minecraft.world.item.ItemStack(DynastyItems.DYNASTY_LINGERING_POTION.get()),
                        DynastyPotions.LOYALTY.get()));

                // 神兽材料与刷怪蛋 / beast materials & spawn eggs
                output.accept(DynastyItems.QILIN_HORN.get());
                output.accept(DynastyItems.PHOENIX_FEATHER.get());
                output.accept(DynastyItems.FOX_TAIL.get());
                output.accept(DynastyItems.DYNASTY_GUIDE.get());
                output.accept(DynastyItems.MINISTER_SPAWN_EGG.get());
                output.accept(DynastyItems.ASSASSIN_SPAWN_EGG.get());
                output.accept(DynastyItems.ARCHER_SPAWN_EGG.get());
                output.accept(DynastyItems.ROYAL_GUARD_SPAWN_EGG.get());
                output.accept(DynastyItems.REBEL_SOLDIER_SPAWN_EGG.get());
                output.accept(DynastyItems.NIAN_BEAST_SPAWN_EGG.get());
                output.accept(DynastyItems.QILIN_SPAWN_EGG.get());
                output.accept(DynastyItems.PHOENIX_SPAWN_EGG.get());
                output.accept(DynastyItems.NINE_TAILED_FOX_SPAWN_EGG.get());
                output.accept(DynastyItems.DRAGON_EMPEROR_SPAWN_EGG.get());
                output.accept(DynastyItems.REBEL_GENERAL_SPAWN_EGG.get());
                output.accept(DynastyItems.EUNUCH_MASTERMIND_SPAWN_EGG.get());

                // 新增：美食 / 材料 / 符箓 / 手札与节令灯
                output.accept(DynastyFineItems.ZONGZI.get());
                output.accept(DynastyFineItems.TANGYUAN.get());
                output.accept(DynastyFineItems.NIANGao.get());
                output.accept(DynastyFineItems.OSMANTHUS_CAKE.get());
                output.accept(DynastyFineItems.CURED_MEAT.get());
                output.accept(DynastyFineItems.ROAST_DUCK.get());
                output.accept(DynastyFineItems.LONGEVITY_NOODLES.get());
                output.accept(DynastyFineItems.BAIJIU.get());
                output.accept(DynastyFineItems.RAW_SILK.get());
                output.accept(DynastyFineItems.SILK.get());
                output.accept(DynastyFineItems.BROCADE.get());
                output.accept(DynastyFineItems.BAMBOO_SLIP.get());
                output.accept(DynastyFineItems.INK_STICK.get());
                output.accept(DynastyFineItems.INK_BRUSH.get());
                output.accept(DynastyFineItems.BRONZE_MIRROR.get());
                output.accept(DynastyFineItems.ROOF_TILE.get());
                output.accept(DynastyFineItems.WIND_TALISMAN.get());
                output.accept(DynastyFineItems.STEALTH_TALISMAN.get());
                output.accept(DynastyFineItems.HEALING_TALISMAN.get());
                output.accept(DynastyFineItems.FIRE_TALISMAN.get());
                output.accept(DynastyFineItems.THUNDER_TALISMAN.get());
                output.accept(DynastyFineItems.RETURN_TALISMAN.get());
                output.accept(DynastyFineItems.QUEST_LEDGER.get());
                output.accept(DynastyFineItems.FESTIVAL_LANTERN.get());

                // 兵器谱（进化链）
                output.accept(DynastyWeapons.TANG_DAO.get());
                output.accept(DynastyWeapons.HUAN_SHOU_DAO.get());
                output.accept(DynastyWeapons.CHANG_QIANG.get());
                output.accept(DynastyWeapons.YU_DI.get());
                output.accept(DynastyWeapons.JUQUE_SWORD.get());
                output.accept(DynastyWeapons.POJUN_AXE.get());
                output.accept(DynastyWeapons.DRAGON_BOW.get());

                // 饰品与说明书
                output.accept(DynastyTrinkets.TRINKET_BOX.get());
                output.accept(DynastyTrinkets.JADE_PENDANT.get());
                output.accept(DynastyTrinkets.JADE_BI_DISC.get());
                output.accept(DynastyTrinkets.GOLD_SEAL_CHARM.get());
                output.accept(DynastyTrinkets.DRAGON_SCALE_CHARM.get());
                output.accept(DynastyTrinkets.PHOENIX_FEATHER_CHARM.get());
                output.accept(DynastyTrinkets.QILIN_HORN_CHARM.get());
                output.accept(DynastyTrinkets.FOX_TAIL_CHARM.get());
                output.accept(DynastyTrinkets.SILK_POUCH.get());
                output.accept(DynastyTrinkets.SOUTH_POINTING_COMPASS.get());
                output.accept(DynastyManual.MANUAL.get());
            }).build());
}
