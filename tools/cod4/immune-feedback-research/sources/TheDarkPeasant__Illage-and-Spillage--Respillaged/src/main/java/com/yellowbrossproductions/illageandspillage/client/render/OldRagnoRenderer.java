package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.client.model.OldRagnoModel;
import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.entities.OldRagnoEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class OldRagnoRenderer extends MobRenderer<OldRagnoEntity, OldRagnoModel<OldRagnoEntity>> {
    private static final ResourceLocation TEXTURE = new ResourceLocation("illageandspillage", "textures/entity/freakager/old/freakager.png");
    private static final ResourceLocation ARACHNOPHOBE = new ResourceLocation("illageandspillage", "textures/entity/freakager/old/freakager_arachnophobe.png");
    private static final ResourceLocation CRAZY = new ResourceLocation("illageandspillage", "textures/entity/freakager/old/freakager_phase2.png");

    public OldRagnoRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new OldRagnoModel<>(renderManagerIn.bakeLayer(OldRagnoModel.LAYER_LOCATION)), 1.6F);
    }

    public Vec3 getRenderOffset(OldRagnoEntity ragno, float p_114337_) {
        float craziness = ragno.isCrazy() ? 2.0F : 1.0F;
        return new Vec3(ragno.getRandom().nextGaussian() * 0.02 * (double) craziness, 0.0 + Math.min((double) ragno.deathTime / 10.0, 1.0) * 2.2, ragno.getRandom().nextGaussian() * 0.02 * (double) craziness);
    }

    protected float getFlipDegrees(OldRagnoEntity p_115337_) {
        return 180.0F;
    }

    public ResourceLocation getTextureLocation(OldRagnoEntity p_110775_1_) {
        return Config.ClientConfig.arachnophobeMode.get() ? ARACHNOPHOBE : (p_110775_1_.isCrazy() ? CRAZY : TEXTURE);
    }
}