package com.yellowbrossproductions.illageandspillage.client.render;

import com.yellowbrossproductions.illageandspillage.IllageAndSpillage;
import com.yellowbrossproductions.illageandspillage.client.model.RagnoModel;
import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.entities.RagnoEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.MobRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class RagnoRenderer extends MobRenderer<RagnoEntity, RagnoModel<RagnoEntity>> {

    private static final ResourceLocation TEXTURE = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/ragno/ragno.png");
    private static final ResourceLocation PAIN = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/ragno/pain.png");
    private static final ResourceLocation SCREAM = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/ragno/scream.png");
    private static final ResourceLocation INSANE = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/ragno/insane.png");
    private static final ResourceLocation WOUNDED = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/ragno/wounded.png");

    private static final ResourceLocation TEXTURE_ARACH = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/ragno/arachnophobe/ragno.png");
    private static final ResourceLocation PAIN_ARACH = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/ragno/arachnophobe/pain.png");
    private static final ResourceLocation SCREAM_ARACH = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/ragno/arachnophobe/scream.png");
    private static final ResourceLocation WOUNDED_ARACH = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/ragno/arachnophobe/wounded.png");

    public RagnoRenderer(EntityRendererProvider.Context renderManagerIn) {
        super(renderManagerIn, new RagnoModel<>(renderManagerIn.bakeLayer(RagnoModel.LAYER_LOCATION)), 1.6F);
    }

    public Vec3 getRenderOffset(RagnoEntity p_114336_, float p_114337_) {
        float craziness = p_114336_.getShakeMultiplier() / 10.0F;
        return new Vec3(p_114336_.getRandom().nextGaussian() * 0.02D * craziness, 0.0, p_114336_.getRandom().nextGaussian() * 0.02D * craziness);
    }

    @Override
    protected float getFlipDegrees(RagnoEntity p_115337_) {
        return 0;
    }

    @Override
    public ResourceLocation getTextureLocation(RagnoEntity p_110775_1_) {
        return switch (p_110775_1_.getRagnoFace()) {
            case 1 -> Config.ClientConfig.arachnophobeMode.get() ? PAIN_ARACH : PAIN;
            case 2 -> Config.ClientConfig.arachnophobeMode.get() ? SCREAM_ARACH : SCREAM;
            case 3 -> Config.ClientConfig.arachnophobeMode.get() ? SCREAM_ARACH : INSANE;
            case 4 -> Config.ClientConfig.arachnophobeMode.get() ? WOUNDED_ARACH : WOUNDED;
            default -> Config.ClientConfig.arachnophobeMode.get() ? TEXTURE_ARACH : TEXTURE;
        };
    }
}