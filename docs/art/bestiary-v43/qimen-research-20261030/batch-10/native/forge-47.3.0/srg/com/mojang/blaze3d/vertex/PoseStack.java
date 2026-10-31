package com.mojang.blaze3d.vertex;

import com.google.common.collect.Queues;
import java.util.Deque;
import net.minecraft.Util;
import net.minecraft.util.Mth;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import org.joml.Quaternionf;

@OnlyIn(Dist.CLIENT)
public class PoseStack implements net.minecraftforge.client.extensions.IForgePoseStack {
   private final Deque<PoseStack.Pose> f_85834_ = Util.m_137469_(Queues.newArrayDeque(), (p_85848_) -> {
      Matrix4f matrix4f = new Matrix4f();
      Matrix3f matrix3f = new Matrix3f();
      p_85848_.add(new PoseStack.Pose(matrix4f, matrix3f));
   });

   public void m_85837_(double p_85838_, double p_85839_, double p_85840_) {
      this.m_252880_((float)p_85838_, (float)p_85839_, (float)p_85840_);
   }

   public void m_252880_(float p_254202_, float p_253782_, float p_254238_) {
      PoseStack.Pose posestack$pose = this.f_85834_.getLast();
      posestack$pose.f_85852_.translate(p_254202_, p_253782_, p_254238_);
   }

   public void m_85841_(float p_85842_, float p_85843_, float p_85844_) {
      PoseStack.Pose posestack$pose = this.f_85834_.getLast();
      posestack$pose.f_85852_.scale(p_85842_, p_85843_, p_85844_);
      if (p_85842_ == p_85843_ && p_85843_ == p_85844_) {
         if (p_85842_ > 0.0F) {
            return;
         }

         posestack$pose.f_85853_.scale(-1.0F);
      }

      float f = 1.0F / p_85842_;
      float f1 = 1.0F / p_85843_;
      float f2 = 1.0F / p_85844_;
      float f3 = Mth.m_14199_(f * f1 * f2);
      posestack$pose.f_85853_.scale(f3 * f, f3 * f1, f3 * f2);
   }

   public void m_252781_(Quaternionf p_254385_) {
      PoseStack.Pose posestack$pose = this.f_85834_.getLast();
      posestack$pose.f_85852_.rotate(p_254385_);
      posestack$pose.f_85853_.rotate(p_254385_);
   }

   public void m_272245_(Quaternionf p_272904_, float p_273581_, float p_272655_, float p_273275_) {
      PoseStack.Pose posestack$pose = this.f_85834_.getLast();
      posestack$pose.f_85852_.rotateAround(p_272904_, p_273581_, p_272655_, p_273275_);
      posestack$pose.f_85853_.rotate(p_272904_);
   }

   public void m_85836_() {
      PoseStack.Pose posestack$pose = this.f_85834_.getLast();
      this.f_85834_.addLast(new PoseStack.Pose(new Matrix4f(posestack$pose.f_85852_), new Matrix3f(posestack$pose.f_85853_)));
   }

   public void m_85849_() {
      this.f_85834_.removeLast();
   }

   public PoseStack.Pose m_85850_() {
      return this.f_85834_.getLast();
   }

   public boolean m_85851_() {
      return this.f_85834_.size() == 1;
   }

   public void m_166856_() {
      PoseStack.Pose posestack$pose = this.f_85834_.getLast();
      posestack$pose.f_85852_.identity();
      posestack$pose.f_85853_.identity();
   }

   public void m_252931_(Matrix4f p_254128_) {
      (this.f_85834_.getLast()).f_85852_.mul(p_254128_);
   }

   @OnlyIn(Dist.CLIENT)
   public static final class Pose {
      final Matrix4f f_85852_;
      final Matrix3f f_85853_;

      Pose(Matrix4f p_254509_, Matrix3f p_254348_) {
         this.f_85852_ = p_254509_;
         this.f_85853_ = p_254348_;
      }

      public Matrix4f m_252922_() {
         return this.f_85852_;
      }

      public Matrix3f m_252943_() {
         return this.f_85853_;
      }
   }
}
