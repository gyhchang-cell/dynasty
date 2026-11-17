package net.minecraft.client.renderer.entity;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Matrix3f;
import org.joml.Matrix4f;

@OnlyIn(Dist.CLIENT)
public abstract class ArrowRenderer<T extends AbstractArrow> extends EntityRenderer<T> {
   public ArrowRenderer(EntityRendererProvider.Context p_173917_) {
      super(p_173917_);
   }

   public void m_7392_(T p_113839_, float p_113840_, float p_113841_, PoseStack p_113842_, MultiBufferSource p_113843_, int p_113844_) {
      p_113842_.m_85836_();
      p_113842_.m_252781_(Axis.f_252436_.m_252977_(Mth.m_14179_(p_113841_, p_113839_.f_19859_, p_113839_.m_146908_()) - 90.0F));
      p_113842_.m_252781_(Axis.f_252403_.m_252977_(Mth.m_14179_(p_113841_, p_113839_.f_19860_, p_113839_.m_146909_())));
      int i = 0;
      float f = 0.0F;
      float f1 = 0.5F;
      float f2 = 0.0F;
      float f3 = 0.15625F;
      float f4 = 0.0F;
      float f5 = 0.15625F;
      float f6 = 0.15625F;
      float f7 = 0.3125F;
      float f8 = 0.05625F;
      float f9 = (float)p_113839_.f_36706_ - p_113841_;
      if (f9 > 0.0F) {
         float f10 = -Mth.m_14031_(f9 * 3.0F) * f9;
         p_113842_.m_252781_(Axis.f_252403_.m_252977_(f10));
      }

      p_113842_.m_252781_(Axis.f_252529_.m_252977_(45.0F));
      p_113842_.m_85841_(0.05625F, 0.05625F, 0.05625F);
      p_113842_.m_252880_(-4.0F, 0.0F, 0.0F);
      VertexConsumer vertexconsumer = p_113843_.m_6299_(RenderType.m_110452_(this.m_5478_(p_113839_)));
      PoseStack.Pose posestack$pose = p_113842_.m_85850_();
      Matrix4f matrix4f = posestack$pose.m_252922_();
      Matrix3f matrix3f = posestack$pose.m_252943_();
      this.m_253099_(matrix4f, matrix3f, vertexconsumer, -7, -2, -2, 0.0F, 0.15625F, -1, 0, 0, p_113844_);
      this.m_253099_(matrix4f, matrix3f, vertexconsumer, -7, -2, 2, 0.15625F, 0.15625F, -1, 0, 0, p_113844_);
      this.m_253099_(matrix4f, matrix3f, vertexconsumer, -7, 2, 2, 0.15625F, 0.3125F, -1, 0, 0, p_113844_);
      this.m_253099_(matrix4f, matrix3f, vertexconsumer, -7, 2, -2, 0.0F, 0.3125F, -1, 0, 0, p_113844_);
      this.m_253099_(matrix4f, matrix3f, vertexconsumer, -7, 2, -2, 0.0F, 0.15625F, 1, 0, 0, p_113844_);
      this.m_253099_(matrix4f, matrix3f, vertexconsumer, -7, 2, 2, 0.15625F, 0.15625F, 1, 0, 0, p_113844_);
      this.m_253099_(matrix4f, matrix3f, vertexconsumer, -7, -2, 2, 0.15625F, 0.3125F, 1, 0, 0, p_113844_);
      this.m_253099_(matrix4f, matrix3f, vertexconsumer, -7, -2, -2, 0.0F, 0.3125F, 1, 0, 0, p_113844_);

      for(int j = 0; j < 4; ++j) {
         p_113842_.m_252781_(Axis.f_252529_.m_252977_(90.0F));
         this.m_253099_(matrix4f, matrix3f, vertexconsumer, -8, -2, 0, 0.0F, 0.0F, 0, 1, 0, p_113844_);
         this.m_253099_(matrix4f, matrix3f, vertexconsumer, 8, -2, 0, 0.5F, 0.0F, 0, 1, 0, p_113844_);
         this.m_253099_(matrix4f, matrix3f, vertexconsumer, 8, 2, 0, 0.5F, 0.15625F, 0, 1, 0, p_113844_);
         this.m_253099_(matrix4f, matrix3f, vertexconsumer, -8, 2, 0, 0.0F, 0.15625F, 0, 1, 0, p_113844_);
      }

      p_113842_.m_85849_();
      super.m_7392_(p_113839_, p_113840_, p_113841_, p_113842_, p_113843_, p_113844_);
   }

   public void m_253099_(Matrix4f p_254392_, Matrix3f p_254011_, VertexConsumer p_253902_, int p_254058_, int p_254338_, int p_254196_, float p_254003_, float p_254165_, int p_253982_, int p_254037_, int p_254038_, int p_254271_) {
      p_253902_.m_252986_(p_254392_, (float)p_254058_, (float)p_254338_, (float)p_254196_).m_6122_(255, 255, 255, 255).m_7421_(p_254003_, p_254165_).m_86008_(OverlayTexture.f_118083_).m_85969_(p_254271_).m_252939_(p_254011_, (float)p_253982_, (float)p_254038_, (float)p_254037_).m_5752_();
   }
}
