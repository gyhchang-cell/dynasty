package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.IllageAndSpillage;
import com.yellowbrossproductions.illageandspillage.client.model.AxeModel;
import com.yellowbrossproductions.illageandspillage.entities.projectile.AxeEntity;
import com.yellowbrossproductions.illageandspillage.entities.projectile.BoneEntity;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.EntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class AxeRenderer extends EntityRenderer<AxeEntity> {
    private static final ResourceLocation TEXTURE = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/axe.png");
    private final AxeModel<Entity> model;

    public AxeRenderer(EntityRendererProvider.Context p_174008_) {
        super(p_174008_);
        this.model = new AxeModel<>(p_174008_.bakeLayer(AxeModel.LAYER_LOCATION));
    }

    public void render(AxeEntity axe, float p_116485_, float p_116486_, PoseStack p_116487_, MultiBufferSource p_116488_, int p_116489_) {
        p_116487_.pushPose();
        p_116487_.scale(1.0F, 1.0F, 1.0F);
        float f = Mth.lerp(p_116486_, axe.yRotO, axe.getYRot());
        f = Mth.wrapDegrees(f);
        float f1 = Mth.lerp(p_116486_, axe.xRotO, axe.getXRot());
        VertexConsumer vertexconsumer = p_116488_.getBuffer(this.model.renderType(this.getTextureLocation(axe)));
        float f7 = this.getBob(axe, p_116486_);
        this.model.setupAnim(axe, f, 0.0F, f7, f, f1);
        this.model.renderToBuffer(p_116487_, vertexconsumer, p_116489_, OverlayTexture.NO_OVERLAY, 1.0F, 1.0F, 1.0F, 1.0F);
        p_116487_.popPose();
        super.render(axe, p_116485_, p_116486_, p_116487_, p_116488_, p_116489_);
    }

    protected float getBob(Entity p_115305_, float p_115306_) {
        return (float) p_115305_.tickCount + p_115306_;
    }

    @Override
    public Vec3 getRenderOffset(AxeEntity p_114483_, float p_114484_) {
        return new Vec3(0, -1.45, 0);
    }

    @Override
    public ResourceLocation getTextureLocation(AxeEntity axeEntity) {
        return TEXTURE;
    }
}