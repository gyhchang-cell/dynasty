package com.sammy.malum.client.renderer.entity.weapon.staff;

import com.sammy.malum.client.renderer.entity.AbstractBoltEntityRenderer;
import com.sammy.malum.common.entity.bolt.*;
import com.sammy.malum.registry.common.magic.*;
import net.minecraft.client.renderer.entity.*;

public class HexBoltRenderer extends AbstractBoltEntityRenderer<HexBolt> {
    public HexBoltRenderer(EntityRendererProvider.Context context) {
        super(context, MalumSpiritTypes.WICKED_SPIRIT.getPrimaryColor(), MalumSpiritTypes.WICKED_SPIRIT.getSecondaryColor());
    }
}
