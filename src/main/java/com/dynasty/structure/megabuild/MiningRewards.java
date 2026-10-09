package com.dynasty.structure.megabuild;

import com.dynasty.DynastyItems;
import net.minecraft.world.Container;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.util.RandomSource;

/** Only called for NEW mine chests; retain the original common chest's fixed jade reward. */
final class MiningRewards {
    private static final Item[] ORES={Items.RAW_IRON,Items.RAW_COPPER,Items.RAW_IRON,Items.COAL,
            Items.RAW_GOLD,Items.IRON_ORE,Items.COPPER_ORE,Items.REDSTONE,Items.LAPIS_LAZULI};
    private static final Item[] SUPPLIES={Items.FLINT,Items.CHARCOAL,Items.AMETHYST_SHARD};
    static void fillNew(Container chest,long seed) {
        if(!chest.isEmpty())return;
        int count=chest.getContainerSize()/3;if(count==0)return;
        var random=RandomSource.create(seed);
        var slots=new java.util.ArrayList<Integer>();
        for(int i=0;i<chest.getContainerSize();i++)slots.add(i);
        // The original tiangong_common guarantees one jade. Reserve its slot first;
        // unopened/player-filled old chests never enter the new-placement caller.
        chest.setItem(slots.remove(random.nextInt(slots.size())),new ItemStack(DynastyItems.JADE.get()));
        int remaining=count-1,oreSlots=(remaining*3+3)/4;
        // In a27-slot chest the eight resource stacks average11 and jade is1:
        // nine occupied slots average89/9=9.89 units. No smelted ingots are added.
        for(int i=0;i<remaining;i++) {
            int slot=slots.remove(random.nextInt(slots.size()));Item[] pool=i<oreSlots?ORES:SUPPLIES;
            chest.setItem(slot,new ItemStack(pool[random.nextInt(pool.length)],10+random.nextInt(3)));
        }
        chest.setChanged();
    }
    private MiningRewards(){}
}
