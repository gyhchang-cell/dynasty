package com.mojang.blaze3d.vertex;

import java.nio.ByteBuffer;
import java.nio.IntBuffer;
import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.core.Vec3i;
import net.minecraft.util.FastColor;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import org.joml.Vector4f;
import org.lwjgl.system.MemoryStack;

@OnlyIn(Dist.CLIENT)
public interface VertexConsumer extends net.minecraftforge.client.extensions.IForgeVertexConsumer {
   VertexConsumer m_5483_(double p_85945_, double p_85946_, double p_85947_);

   VertexConsumer m_6122_(int p_85973_, int p_85974_, int p_85975_, int p_85976_);

   VertexConsumer m_7421_(float p_85948_, float p_85949_);

   VertexConsumer m_7122_(int p_85971_, int p_85972_);

   VertexConsumer m_7120_(int p_86010_, int p_86011_);

   VertexConsumer m_5601_(float p_86005_, float p_86006_, float p_86007_);

   void m_5752_();

   default void m_5954_(float p_85955_, float p_85956_, float p_85957_, float p_85958_, float p_85959_, float p_85960_, float p_85961_, float p_85962_, float p_85963_, int p_85964_, int p_85965_, float p_85966_, float p_85967_, float p_85968_) {
      this.m_5483_((double)p_85955_, (double)p_85956_, (double)p_85957_);
      this.m_85950_(p_85958_, p_85959_, p_85960_, p_85961_);
      this.m_7421_(p_85962_, p_85963_);
      this.m_86008_(p_85964_);
      this.m_85969_(p_85965_);
      this.m_5601_(p_85966_, p_85967_, p_85968_);
      this.m_5752_();
   }

   void m_7404_(int p_166901_, int p_166902_, int p_166903_, int p_166904_);

   void m_141991_();

   default VertexConsumer m_85950_(float p_85951_, float p_85952_, float p_85953_, float p_85954_) {
      return this.m_6122_((int)(p_85951_ * 255.0F), (int)(p_85952_ * 255.0F), (int)(p_85953_ * 255.0F), (int)(p_85954_ * 255.0F));
   }

   default VertexConsumer m_193479_(int p_193480_) {
      return this.m_6122_(FastColor.ARGB32.m_13665_(p_193480_), FastColor.ARGB32.m_13667_(p_193480_), FastColor.ARGB32.m_13669_(p_193480_), FastColor.ARGB32.m_13655_(p_193480_));
   }

   default VertexConsumer m_85969_(int p_85970_) {
      return this.m_7120_(p_85970_ & '\uffff', p_85970_ >> 16 & '\uffff');
   }

   default VertexConsumer m_86008_(int p_86009_) {
      return this.m_7122_(p_86009_ & '\uffff', p_86009_ >> 16 & '\uffff');
   }

   default void m_85987_(PoseStack.Pose p_85988_, BakedQuad p_85989_, float p_85990_, float p_85991_, float p_85992_, int p_85993_, int p_85994_) {
      this.m_85995_(p_85988_, p_85989_, new float[]{1.0F, 1.0F, 1.0F, 1.0F}, p_85990_, p_85991_, p_85992_, new int[]{p_85993_, p_85993_, p_85993_, p_85993_}, p_85994_, false);
   }

   default void m_85995_(PoseStack.Pose p_85996_, BakedQuad p_85997_, float[] p_85998_, float p_85999_, float p_86000_, float p_86001_, int[] p_86002_, int p_86003_, boolean p_86004_) {
      putBulkData(p_85996_, p_85997_, p_85998_, p_85999_, p_86000_, p_86001_, 1, p_86002_, p_86003_, p_86004_);
   }

   default void putBulkData(PoseStack.Pose p_85996_, BakedQuad p_85997_, float[] p_85998_, float p_85999_, float p_86000_, float p_86001_, float alpha, int[] p_86002_, int p_86003_, boolean p_86004_) {
      float[] afloat = new float[]{p_85998_[0], p_85998_[1], p_85998_[2], p_85998_[3]};
      int[] aint = new int[]{p_86002_[0], p_86002_[1], p_86002_[2], p_86002_[3]};
      int[] aint1 = p_85997_.m_111303_();
      Vec3i vec3i = p_85997_.m_111306_().m_122436_();
      Matrix4f matrix4f = p_85996_.m_252922_();
      Vector3f vector3f = p_85996_.m_252943_().transform(new Vector3f((float)vec3i.m_123341_(), (float)vec3i.m_123342_(), (float)vec3i.m_123343_()));
      int i = 8;
      int j = aint1.length / 8;

      try (MemoryStack memorystack = MemoryStack.stackPush()) {
         ByteBuffer bytebuffer = memorystack.malloc(DefaultVertexFormat.f_85811_.m_86020_());
         IntBuffer intbuffer = bytebuffer.asIntBuffer();

         for(int k = 0; k < j; ++k) {
            intbuffer.clear();
            intbuffer.put(aint1, k * 8, 8);
            float f = bytebuffer.getFloat(0);
            float f1 = bytebuffer.getFloat(4);
            float f2 = bytebuffer.getFloat(8);
            float f3;
            float f4;
            float f5;
            if (p_86004_) {
               float f6 = (float)(bytebuffer.get(12) & 255) / 255.0F;
               float f7 = (float)(bytebuffer.get(13) & 255) / 255.0F;
               float f8 = (float)(bytebuffer.get(14) & 255) / 255.0F;
               f3 = f6 * afloat[k] * p_85999_;
               f4 = f7 * afloat[k] * p_86000_;
               f5 = f8 * afloat[k] * p_86001_;
            } else {
               f3 = afloat[k] * p_85999_;
               f4 = afloat[k] * p_86000_;
               f5 = afloat[k] * p_86001_;
            }

            int l = applyBakedLighting(p_86002_[k], bytebuffer);
            float f9 = bytebuffer.getFloat(16);
            float f10 = bytebuffer.getFloat(20);
            Vector4f vector4f = matrix4f.transform(new Vector4f(f, f1, f2, 1.0F));
            applyBakedNormals(vector3f, bytebuffer, p_85996_.m_252943_());
            float vertexAlpha = p_86004_ ? alpha * (float) (bytebuffer.get(15) & 255) / 255.0F : alpha;
            this.m_5954_(vector4f.x(), vector4f.y(), vector4f.z(), f3, f4, f5, vertexAlpha, f9, f10, p_86003_, l, vector3f.x(), vector3f.y(), vector3f.z());
         }
      }

   }

   default VertexConsumer m_252986_(Matrix4f p_254075_, float p_254519_, float p_253869_, float p_253980_) {
      Vector4f vector4f = p_254075_.transform(new Vector4f(p_254519_, p_253869_, p_253980_, 1.0F));
      return this.m_5483_((double)vector4f.x(), (double)vector4f.y(), (double)vector4f.z());
   }

   default VertexConsumer m_252939_(Matrix3f p_253747_, float p_254430_, float p_253877_, float p_254167_) {
      Vector3f vector3f = p_253747_.transform(new Vector3f(p_254430_, p_253877_, p_254167_));
      return this.m_5601_(vector3f.x(), vector3f.y(), vector3f.z());
   }
}
