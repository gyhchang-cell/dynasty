package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.DispenserModel;
import com.yellowbrossproductions.illageandspillage.entities.DispenserEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

import java.util.Calendar;

@OnlyIn(Dist.CLIENT)
public class DispenserRenderer extends MobRenderer<DispenserEntity, DispenserModel<DispenserEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/magispeller/dispenser.png");
    private static final ResourceLocation CHRISTMAS = new ResourceLocation("illageandspillage", "textures/entity/magispeller/christmas/dispenser_christmas.png");

    public DispenserRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new DispenserModel<>(renderManagerIn.bakeLayer(DispenserModel.LAYER_LOCATION)), 0.5F);
    }

    @Override
    protected float getFlipDegrees(DispenserEntity p_115337_) {
        return 0;
    }

    public ResourceLocation getTextureLocation(DispenserEntity p_110775_1_) {
        Calendar calendar = Calendar.getInstance();
        return calendar.get(Calendar.MONTH) + 1 == 12 ? CHRISTMAS : TEXTURE;
    }
}
