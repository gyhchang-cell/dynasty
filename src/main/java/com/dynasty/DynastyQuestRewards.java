package com.dynasty;

import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

/**
 * 任务奖励表（与 DynastyQuests 中的 index 对应）。
 * Quest reward table, indexed the same way as DynastyQuests.
 */
public final class DynastyQuestRewards {

    private DynastyQuestRewards() {
    }

    public static ItemStack[] build(int index) {
        return switch (index) {
            case 0 -> new ItemStack[]{new ItemStack(DynastyItems.JADE.get(), 2),
                    new ItemStack(DynastyItems.COPPER_COIN.get(), 4)};
            case 1 -> new ItemStack[]{new ItemStack(DynastyItems.COPPER_COIN.get(), 8)};
            case 2 -> new ItemStack[]{new ItemStack(DynastyItems.BRONZE_INGOT.get(), 3)};
            case 3 -> new ItemStack[]{new ItemStack(DynastyItems.SILVER_COIN.get(), 4),
                    new ItemStack(DynastyItems.PILL_FOCUS.get(), 1)};
            case 4 -> new ItemStack[]{new ItemStack(DynastyFineItems.INK_STICK.get(), 2),
                    new ItemStack(DynastyItems.TALISMAN_PAPER.get(), 3)};
            case 5 -> new ItemStack[]{new ItemStack(DynastyFineItems.INK_BRUSH.get(), 1),
                    new ItemStack(Items.EXPERIENCE_BOTTLE, 4)};
            case 6 -> new ItemStack[]{new ItemStack(DynastyItems.OFFICIAL_SEAL.get(), 1),
                    new ItemStack(DynastyItems.GOLD_COIN.get(), 4)};
            case 7 -> new ItemStack[]{new ItemStack(DynastyFineItems.BAMBOO_SLIP.get(), 4),
                    new ItemStack(DynastyItems.EDICT.get(), 1)};
            case 8 -> new ItemStack[]{new ItemStack(DynastyItems.JADE.get(), 4),
                    new ItemStack(DynastyFineItems.ROOF_TILE.get(), 8)};
            case 9 -> new ItemStack[]{new ItemStack(DynastyItems.TIGER_TALLY.get(), 1),
                    new ItemStack(DynastyItems.BRONZE_INGOT.get(), 8)};
            case 10 -> new ItemStack[]{new ItemStack(DynastyItems.DRAGON_SCALE.get(), 3)};
            case 11 -> new ItemStack[]{new ItemStack(DynastyItems.GOLD_COIN.get(), 8),
                    new ItemStack(DynastyItems.BRONZE_INGOT.get(), 6)};
            case 12 -> new ItemStack[]{new ItemStack(DynastyItems.DYNASTY_GUIDE.get(), 1),
                    new ItemStack(DynastyFineItems.SILK.get(), 4)};
            case 13 -> new ItemStack[]{new ItemStack(DynastyBlocks.JADE_PORTAL.get(), 4),
                    new ItemStack(DynastyItems.DRAGON_CRYSTAL.get(), 2)};
            case 14 -> new ItemStack[]{new ItemStack(DynastyItems.DRAGON_CRYSTAL.get(), 3)};
            case 15 -> new ItemStack[]{new ItemStack(DynastyBlocks.PALACE_BRICKS.get(), 16)};
            case 16 -> new ItemStack[]{new ItemStack(DynastyBlocks.MARBLE_BLOCK.get(), 16),
                    new ItemStack(DynastyBlocks.BRONZE_BLOCK.get(), 8)};
            case 17 -> new ItemStack[]{new ItemStack(DynastyBlocks.UNDERWORLD_PORTAL.get(), 4),
                    new ItemStack(DynastyItems.CINNABAR.get(), 4)};
            case 18 -> new ItemStack[]{new ItemStack(DynastyFineItems.THUNDER_TALISMAN.get(), 2),
                    new ItemStack(DynastyItems.DRAGON_SCALE.get(), 3)};
            case 19 -> new ItemStack[]{new ItemStack(DynastyItems.DRAGON_COIN.get(), 4),
                    new ItemStack(DynastyFineItems.BRONZE_MIRROR.get(), 1)};
            case 20 -> new ItemStack[]{new ItemStack(DynastyItems.IMMORTAL_PEACH.get(), 3),
                    new ItemStack(DynastyItems.PILL_LONGEVITY.get(), 2)};
            case 21 -> new ItemStack[]{new ItemStack(DynastyFineItems.BROCADE.get(), 4),
                    new ItemStack(DynastyItems.GOLD_COIN.get(), 8)};
            case 22 -> new ItemStack[]{new ItemStack(DynastyItems.JADE_SEAL.get(), 1),
                    new ItemStack(DynastyItems.DRAGON_CRYSTAL.get(), 6)};
            default -> new ItemStack[]{new ItemStack(DynastyItems.GOLD_COIN.get(), 16),
                    new ItemStack(DynastyFineItems.BROCADE.get(), 8)};
        };
    }
}
