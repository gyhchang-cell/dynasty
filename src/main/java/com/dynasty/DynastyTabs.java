package com.dynasty;

import com.dynasty.Dynasty;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
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
            // 封面 = 「金龙抱玉印」（ChatGPT 出的成品画，tools/art/gen_tab_icon.py 转成贴图）。
            // 标签页图标只能是一个 ItemStack，所以专门注册了 DynastyItems.DYNASTY_EMBLEM，
            // 它不在下面的列表里（玩家拿不到），只当封面。/ tab icon needs an ItemStack, hence the emblem item.
            .icon(() -> new ItemStack(DynastyItems.DYNASTY_EMBLEM.get()))
            .displayItems((params, output) -> {
                // Optional navigation tools: also visible in Dynasty's creative/search tab.
                for (String mod : new String[]{"naturescompass", "explorerscompass"}) {
                    var key = new net.minecraft.resources.ResourceLocation(mod, mod);
                    if (net.minecraftforge.registries.ForgeRegistries.ITEMS.containsKey(key)) {
                        output.accept(net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(key));
                    }
                }
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
                output.accept(DynastyWeapons.MU_MAO.get());
                output.accept(DynastyWeapons.SHI_GE.get());
                output.accept(DynastyWeapons.TONG_DAO.get());
                output.accept(DynastyWeapons.TIE_JIAN.get());
                output.accept(DynastyWeapons.LIE_GONG.get());
                output.accept(DynastyGear.SWORD_BRONZE.get());
                output.accept(DynastyWeapons.TANG_DAO.get());
                output.accept(DynastyWeapons.HUAN_SHOU_DAO.get());
                output.accept(DynastyWeapons.CHANG_GONG.get());
                output.accept(DynastyWeapons.SHENBI_BOW.get());
                output.accept(DynastyWeapons.LUOYAN_BOW.get());
                output.accept(DynastyWeapons.TIANLANG_BOW.get());
                output.accept(DynastyWeapons.CHANG_QIANG.get());
                output.accept(DynastyWeapons.YU_DI.get());
                output.accept(DynastyGear.SWORD_SILVER.get());
                output.accept(DynastyGear.SWORD_JADE.get());
                output.accept(DynastyWeapons.JUQUE_SWORD.get());
                output.accept(DynastyWeapons.POJUN_AXE.get());
                output.accept(DynastyWeapons.DRAGON_BOW.get());
                output.accept(DynastyGear.SWORD_DRAGON_CRYSTAL.get());
                output.accept(DynastyGear.HALBERD_FANGTIAN.get());
                output.accept(DynastyWeapons.XUANTIAN_AXE.get());
                output.accept(DynastyWeapons.TIANZI_SWORD.get());
                output.accept(DynastyGear.PICKAXE_JADE.get());
                output.accept(DynastyGear.PICKAXE_DRAGON_CRYSTAL.get());

                // 盔甲 / armor（进化链：布衣 → 将军铠 → 玉甲 → 龙鳞甲 → 玄天甲）
                output.accept(DynastyGear.CLOTH_HELMET.get());
                output.accept(DynastyGear.CLOTH_CHESTPLATE.get());
                output.accept(DynastyGear.CLOTH_LEGGINGS.get());
                output.accept(DynastyGear.CLOTH_BOOTS.get());
                output.accept(DynastyGear.GENERAL_HELMET.get());
                output.accept(DynastyGear.GENERAL_CHESTPLATE.get());
                output.accept(DynastyGear.GENERAL_LEGGINGS.get());
                output.accept(DynastyGear.GENERAL_BOOTS.get());
                output.accept(DynastyGear.JADE_HELMET.get());
                output.accept(DynastyGear.JADE_CHESTPLATE.get());
                output.accept(DynastyGear.JADE_LEGGINGS.get());
                output.accept(DynastyGear.JADE_BOOTS.get());
                output.accept(DynastyGear.DRAGON_SCALE_HELMET.get());
                output.accept(DynastyGear.DRAGON_SCALE_CHESTPLATE.get());
                output.accept(DynastyGear.DRAGON_SCALE_LEGGINGS.get());
                output.accept(DynastyGear.DRAGON_SCALE_BOOTS.get());
                output.accept(DynastyGear.XUANTIAN_HELMET.get());
                output.accept(DynastyGear.XUANTIAN_CHESTPLATE.get());
                output.accept(DynastyGear.XUANTIAN_LEGGINGS.get());
                output.accept(DynastyGear.XUANTIAN_BOOTS.get());

                // 第二十轮扩充的 10 套新盔甲（表格注册，这里直接铺出来）
                for (net.minecraftforge.registries.RegistryObject<net.minecraft.world.item.Item> piece
                        : DynastyGear.EXTRA_ARMOR) {
                    output.accept(piece.get());
                }

                // 帝兵材料与信物 / relics & imperial tokens
                output.accept(DynastyRelics.BLUEPRINT.get());
                output.accept(DynastyRelics.REFINED_STEEL.get());
                output.accept(DynastyRelics.REBEL_HEAD.get());
                output.accept(DynastyRelics.EUNUCH_TOKEN.get());
                output.accept(DynastyRelics.EMPEROR_BONE.get());
                output.accept(DynastyRelics.DRAGON_EMPEROR_SEAL.get());
                output.accept(DynastyRelics.XUANTIAN_JADE.get());

                // 刷怪蛋 / spawn eggs
                output.accept(DynastyItems.TERRACOTTA_WARRIOR_SPAWN_EGG.get());
                output.accept(DynastyItems.IMPERIAL_SOLDIER_SPAWN_EGG.get());
                output.accept(DynastyItems.UNDEAD_FIRST_EMPEROR_SPAWN_EGG.get());

                // 传送门 / portals（四个维度都要能在这里找到）
                output.accept(DynastyBlocks.JADE_PORTAL.get());
                output.accept(DynastyBlocks.UNDERWORLD_PORTAL.get());
                output.accept(DynastyBlocks.CLOUD_PORTAL.get());
                output.accept(DynastyBlocks.DRAGON_GATE.get());

                // 宫廷装饰 / decoration
                output.accept(DynastyBlocks.DRAGON_THRONE.get());
                output.accept(DynastyBlocks.ALTAR.get());
                output.accept(DynastyBlocks.RITUAL_ALTAR.get());
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
                output.accept(DynastyBasicFoods.GRILLED_MEAT_SKEWER.get());
                output.accept(DynastyBasicFoods.WHEAT_CAKE.get());
                output.accept(DynastyBasicFoods.HONEY_ROAST.get());
                output.accept(DynastyBasicFoods.COUNTRYSIDE_STEW.get());
                output.accept(DynastyBasicFoods.MUSHROOM_FISH_SOUP.get());
                output.accept(DynastyBasicFoods.PUMPKIN_SWEET_CAKE.get());
                output.accept(DynastyFineItems.ZONGZI.get());
                output.accept(DynastyFineItems.TANGYUAN.get());
                output.accept(DynastyFineItems.NIANGao.get());
                output.accept(DynastyFineItems.OSMANTHUS_CAKE.get());
                output.accept(DynastyFineItems.CURED_MEAT.get());
                output.accept(DynastyBlocks.BOUNTY_BOARD.get());
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
                output.accept(DynastyFineItems.FIRE_TALISMAN.get());
                output.accept(DynastyFineItems.THUNDER_TALISMAN.get());
                output.accept(DynastyFineItems.WIND_TALISMAN.get());
                output.accept(DynastyFineItems.STEALTH_TALISMAN.get());
                output.accept(DynastyFineItems.VAJRA_TALISMAN.get());
                output.accept(DynastyFineItems.SOUL_TALISMAN.get());
                output.accept(DynastyFineItems.RETURN_TALISMAN.get());
                output.accept(DynastyFineItems.FESTIVAL_LANTERN.get());

                // 兵器谱（进化链）
                output.accept(DynastyWeapons.TANG_DAO.get());
                output.accept(DynastyWeapons.HUAN_SHOU_DAO.get());
                output.accept(DynastyWeapons.CHANG_QIANG.get());
                output.accept(DynastyWeapons.YU_DI.get());
                output.accept(DynastyWeapons.JUQUE_SWORD.get());
                output.accept(DynastyWeapons.POJUN_AXE.get());
                output.accept(DynastyWeapons.DRAGON_BOW.get());
                output.accept(DynastyWeapons.SHENBI_BOW.get());
                output.accept(DynastyWeapons.LUOYAN_BOW.get());
                output.accept(DynastyWeapons.TIANLANG_BOW.get());

                // 饰品与说明书
                output.accept(DynastyTrinkets.JADE_PENDANT.get());
                output.accept(DynastyTrinkets.JADE_BI_DISC.get());
                output.accept(DynastyTrinkets.GOLD_SEAL_CHARM.get());
                output.accept(DynastyTrinkets.DRAGON_SCALE_CHARM.get());
                output.accept(DynastyTrinkets.PHOENIX_FEATHER_CHARM.get());
                output.accept(DynastyTrinkets.QILIN_HORN_CHARM.get());
                output.accept(DynastyTrinkets.FOX_TAIL_CHARM.get());
                output.accept(DynastyTrinkets.SILK_POUCH.get());
                output.accept(DynastyTrinkets.SOUTH_POINTING_COMPASS.get());
                output.accept(DynastyTrinkets.HEART_MIRROR.get());
                output.accept(DynastyTrinkets.JADE_CROWN.get());
                output.accept(DynastyTrinkets.JADE_CICADA.get());
                output.accept(DynastyTrinkets.DRAGON_PEARL.get());
                output.accept(DynastyTrinkets.PHOENIX_RING.get());
                output.accept(DynastyTrinkets.STORM_CHARM.get());
                output.accept(DynastyTrinkets.MOON_PENDANT.get());
                output.accept(DynastyTrinkets.TIGER_CREST.get());
                output.accept(DynastyTrinkets.JADE_TORTOISE.get());
                output.accept(DynastyTrinkets.WAR_DRUM_CHARM.get());
                output.accept(DynastyTrinkets.CINNABAR_POUCH.get());
                output.accept(DynastyTrinkets.DRAGON_WHISKER.get());
                output.accept(DynastyTrinkets.TIGER_TOKEN.get());
                output.accept(DynastyTrinkets.SUN_FEATHER.get());
                output.accept(DynastyTrinkets.WAR_HORSE_BELL.get());
                output.accept(DynastyTrinkets.IRON_WAIST_TOKEN.get());
                output.accept(DynastyTrinkets.AUSPICIOUS_BELL.get());
                output.accept(DynastyManual.MANUAL.get());

                // ----------------------------------------------------------------
                // 第三十四轮补：此前**注册了但没进创造栏**的物品（玩家在创造模式里看不到）
                // 表驱动饰品（gen_trinkets3/4/5 共 130 件）整批循环进来
                for (RegistryObject<Item> charm : DynastyTrinkets.EXTRA_CHARMS) {
                    output.accept(charm.get());
                }
                // DynastyItems（16 件）
                output.accept(DynastyItems.PEACH_BUN.get());
                output.accept(DynastyItems.LOTUS_CAKE.get());
                output.accept(DynastyItems.SESAME_BALL.get());
                output.accept(DynastyItems.SWEET_SOUP_CAKE.get());
                output.accept(DynastyItems.BAMBOO_RICE.get());
                output.accept(DynastyItems.EIGHT_TREASURE_PORRIDGE.get());
                output.accept(DynastyItems.DRIED_PERSIMMON.get());
                output.accept(DynastyItems.CHRYSANTHEMUM_WINE.get());
                output.accept(DynastyItems.JADE_GUARD_SPAWN_EGG.get());
                output.accept(DynastyItems.SOUL_SOLDIER_SPAWN_EGG.get());
                output.accept(DynastyItems.THUNDER_ENVOY_SPAWN_EGG.get());
                output.accept(DynastyItems.MERFOLK_SPAWN_EGG.get());
                output.accept(DynastyItems.NINE_HEAVEN_GENERAL_SPAWN_EGG.get());
                output.accept(DynastyItems.SKY_TOKEN.get());
                output.accept(DynastyItems.SEA_TOKEN.get());
                output.accept(DynastyItems.DRAGON_KING_SPAWN_EGG.get());
                // DynastyRelics（7 件）
                output.accept(DynastyRelics.XUANWU_SHELL.get());
                output.accept(DynastyRelics.QINGLONG_SCALE.get());
                output.accept(DynastyRelics.BAIHU_FANG.get());
                output.accept(DynastyRelics.ZHUQUE_FEATHER.get());
                output.accept(DynastyRelics.TAIYI_JADE.get());
                output.accept(DynastyRelics.THUNDER_TOKEN.get());
                output.accept(DynastyRelics.HUNYUAN_PEARL.get());
                // DynastyWeapons（26 件）
                output.accept(DynastyWeapons.ZHANMA_DAO.get());
                output.accept(DynastyWeapons.YUCHANG_DAGGER.get());
                output.accept(DynastyWeapons.QINGGANG_SWORD.get());
                output.accept(DynastyWeapons.GILDED_MACE.get());
                output.accept(DynastyWeapons.YITIAN_SWORD.get());
                output.accept(DynastyWeapons.DRAGON_SPEAR.get());
                output.accept(DynastyWeapons.SUNBOW.get());
                output.accept(DynastyWeapons.SEVEN_STAR_SABER.get());
                output.accept(DynastyWeapons.DRAGON_SLAYER.get());
                output.accept(DynastyWeapons.SUPREME_SWORD.get());
                output.accept(DynastyWeapons.LONGYUAN_SWORD.get());
                output.accept(DynastyWeapons.JULING_AXE.get());
                output.accept(DynastyWeapons.QINGLONG_DAO.get());
                output.accept(DynastyWeapons.BAWANG_SPEAR.get());
                output.accept(DynastyWeapons.HOUYI_BOW.get());
                output.accept(DynastyWeapons.LEITING_HAMMER.get());
                output.accept(DynastyWeapons.TAIYI_WHISK.get());
                output.accept(DynastyWeapons.XUANWU_BLADE.get());
                output.accept(DynastyWeapons.ZHUQUE_FAN.get());
                output.accept(DynastyWeapons.HUNYUAN_STAFF.get());
                output.accept(DynastyWeapons.QILIN_WAR_AXE.get());
                output.accept(DynastyWeapons.TAIYI_SWORD.get());
                output.accept(DynastyWeapons.BAIHU_GLAIVE.get());
                output.accept(DynastyWeapons.THUNDER_SPEAR.get());
                output.accept(DynastyWeapons.ZIWEI_SABER.get());
                output.accept(DynastyWeapons.ZHUQUE_BOW.get());
                // DynastyGear（9 件）
                output.accept(DynastyGear.SEA_TRIDENT.get());
                output.accept(DynastyGear.SEA_SILK_HELMET.get());
                output.accept(DynastyGear.SEA_SILK_CHESTPLATE.get());
                output.accept(DynastyGear.SEA_SILK_LEGGINGS.get());
                output.accept(DynastyGear.SEA_SILK_BOOTS.get());
                output.accept(DynastyGear.DARK_IRON_HELMET.get());
                output.accept(DynastyGear.DARK_IRON_CHESTPLATE.get());
                output.accept(DynastyGear.DARK_IRON_LEGGINGS.get());
                output.accept(DynastyGear.DARK_IRON_BOOTS.get());
                // DynastyTrinkets（13 件）
                output.accept(DynastyTrinkets.SEA_PEARL.get());
                output.accept(DynastyTrinkets.DRAGON_BONE_RING.get());
                output.accept(DynastyTrinkets.CLOUD_BROCADE.get());
                output.accept(DynastyTrinkets.STAR_COMPASS.get());
                output.accept(DynastyTrinkets.DRAGON_KING_SCALE.get());
                output.accept(DynastyTrinkets.SKY_FEATHER.get());
                output.accept(DynastyTrinkets.IMPERIAL_SEAL_CHARM.get());
                output.accept(DynastyTrinkets.TOMB_CANDLE.get());
                output.accept(DynastyTrinkets.INKSTONE.get());
                output.accept(DynastyTrinkets.BAMBOO_FLUTE.get());
                output.accept(DynastyTrinkets.MERIT_BADGE.get());
                output.accept(DynastyTrinkets.SEA_CONCH.get());
                output.accept(DynastyTrinkets.TRINKET_BOX.get());
            }).build());
}
