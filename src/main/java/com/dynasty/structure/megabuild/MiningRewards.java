package com.dynasty.structure.megabuild;

import net.minecraft.world.Container;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.util.RandomSource;

/** Only called when a NEW mining chest is created. Never refills an existing inventory. */
final class MiningRewards {
    private static final Item[] ORES={Items.RAW_IRON,Items.RAW_COPPER,Items.RAW_IRON,Items.COAL,
            Items.RAW_GOLD,Items.IRON_ORE,Items.COPPER_ORE,Items.REDSTONE,Items.LAPIS_LAZULI};
    private static final Item[] SUPPLIES={Items.FLINT,Items.CHARCOAL,Items.AMETHYST_SHARD};
    static void fillNew(Container chest,long seed) {
        if(!chest.isEmpty())return;
        var random=RandomSource.create(seed);
        var slots=new java.util.ArrayList<Integer>();
        for(int i=0;i<chest.getContainerSize();i++)slots.add(i);
        int count=chest.getContainerSize()/3;
        for(int i=0;i<count;i++) {
            int slot=slots.remove(random.nextInt(slots.size()));
            Item[] pool=i<(count*3+3)/4?ORES:SUPPLIES;
            chest.setItem(slot,new ItemStack(pool[random.nextInt(pool.length)],8+random.nextInt(5)));
        }
        chest.setChanged();
    }
    private MiningRewards(){}
}
