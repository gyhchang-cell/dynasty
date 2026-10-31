package com.sammy.malum.client.renderer.entity.nitrate;

import com.sammy.malum.common.entity.nitrate.VividNitrate;
import net.minecraft.client.*;
import net.minecraft.client.renderer.entity.EntityRendererProvider;

import java.awt.*;
import java.util.function.*;

public class VividNitrateRenderer extends AbstractNitrateEntityRenderer<VividNitrate> {

    public static final Function<Float, Color> COLOR_FUNCTION = f -> VividNitrate.COLOR_FUNCTION.apply(new VividNitrate.ColorFunctionData(Minecraft.getInstance().level, f));

    public VividNitrateRenderer(EntityRendererProvider.Context context) {
        super(context, COLOR_FUNCTION, COLOR_FUNCTION);
    }
}
