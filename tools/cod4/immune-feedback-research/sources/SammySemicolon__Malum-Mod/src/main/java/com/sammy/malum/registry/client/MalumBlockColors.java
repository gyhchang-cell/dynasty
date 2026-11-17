package com.sammy.malum.registry.client;

import com.sammy.malum.common.block.ether.*;
import com.sammy.malum.registry.common.MalumContent;
import net.minecraft.world.level.block.entity.*;
import net.neoforged.neoforge.client.event.*;

public class MalumBlockColors {

    public static void setBlockColors(RegisterColorHandlersEvent.Block event) {
        event.register((s, l, p, c) -> {
            if (l == null) {
                return -1;
            }
            BlockEntity blockEntity = l.getBlockEntity(p);
            if (blockEntity instanceof EtherBlockEntity etherBlockEntity) {
                if (etherBlockEntity.firstColor != null) {
                    return c == 0 ? etherBlockEntity.firstColor.rgb() : -1;
                }
            }
            return -1;
        }, MalumContent.BuildingBlocks.ETHER.get(), MalumContent.BuildingBlocks.IRIDESCENT_ETHER.get());
    }
}
