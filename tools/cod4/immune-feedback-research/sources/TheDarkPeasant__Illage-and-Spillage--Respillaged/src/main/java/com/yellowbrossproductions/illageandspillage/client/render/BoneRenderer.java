package com.yellowbrossproductions.illageandspillage.client.render;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.yellowbrossproductions.illageandspillage.IllageAndSpillage;
import com.yellowbrossproductions.illageandspillage.client.model.BoneModel;
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
public class BoneRenderer extends EntityRenderer<BoneEntity> {
    private static final ResourceLocation TEXTURE = new ResourceLocation(IllageAndSpillage.MOD_ID, "textures/entity/freakager/bone.png");
    private final BoneModel<Entity> model;

    public BoneRenderer(EntityRendererProvider.Context p_174008_) {
        super(p_174008_);
        this.model = new BoneModel<>(p_174008_.bakeLayer(BoneModel.LAYER_LOCATION));
    }

    public void render(BoneEntity bone, float p_116485_, float p_116486_, PoseStack p_116487_, MultiBufferSource p_116488_, int p_116489_) {
        p_116487_.pushPose();
        p_116487_.scale(1.0F, 1.0F, 1.0F);
        float f = Mth.lerp(p_116486_, bone.yRotO, bone.getYRot());
        f = Mth.wrapDegrees(f);
        float f1 = Mth.lerp(p_116486_, bone.xRotO, bone.getXRot());
        VertexConsumer vertexconsumer = p_116488_.getBuffer(this.model.renderType(this.getTextureLocation(bone)));
        float f7 = this.getBob(bone, p_116486_);
        this.model.setupAnim(bone, f, 0.0F, f7, f, f1);
        this.model.renderToBuffer(p_116487_, vertexconsumer, p_116489_, OverlayTexture.NO_OVERLAY, 1.0F, 1.0F, 1.0F, 1.0F);
        p_116487_.popPose();
        super.render(bone, p_116485_, p_116486_, p_116487_, p_116488_, p_116489_);
    }

    protected float getBob(Entity p_115305_, float p_115306_) {
        return (float) p_115305_.tickCount + p_115306_;
    }

    @Override
    public Vec3 getRenderOffset(BoneEntity p_114483_, float p_114484_) {
        return new Vec3(0, -1.45, 0);
    }

    @Override
    public ResourceLocation getTextureLocation(BoneEntity bone) {
        return TEXTURE;
    }
}