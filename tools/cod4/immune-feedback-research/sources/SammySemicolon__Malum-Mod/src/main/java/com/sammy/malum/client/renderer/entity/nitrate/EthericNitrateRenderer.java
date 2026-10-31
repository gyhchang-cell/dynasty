package com.sammy.malum.client.renderer.entity.nitrate;

import com.sammy.malum.common.entity.nitrate.*;
import net.minecraft.client.renderer.entity.EntityRendererProvider;

public class EthericNitrateRenderer extends AbstractNitrateEntityRenderer<EthericNitrate> {

    public EthericNitrateRenderer(EntityRendererProvider.Context context) {
        super(context, EthericNitrate.AURIC_YELLOW, EthericNitrate.AURIC_PURPLE);
    }
}
