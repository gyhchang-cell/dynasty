package com.mojang.blaze3d.vertex;

import com.mojang.blaze3d.systems.RenderSystem;
import javax.annotation.Nullable;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class BufferUploader {
   @Nullable
   private static VertexBuffer f_231201_;

   public static void m_166835_() {
      if (f_231201_ != null) {
         m_231208_();
         VertexBuffer.m_85931_();
      }

   }

   public static void m_231208_() {
      f_231201_ = null;
   }

   public static void m_231202_(BufferBuilder.RenderedBuffer p_231203_) {
      if (!RenderSystem.isOnRenderThreadOrInit()) {
         RenderSystem.recordRenderCall(() -> {
            m_231211_(p_231203_);
         });
      } else {
         m_231211_(p_231203_);
      }

   }

   private static void m_231211_(BufferBuilder.RenderedBuffer p_231212_) {
      VertexBuffer vertexbuffer = m_231213_(p_231212_);
      if (vertexbuffer != null) {
         vertexbuffer.m_253207_(RenderSystem.getModelViewMatrix(), RenderSystem.getProjectionMatrix(), RenderSystem.getShader());
      }

   }

   public static void m_231209_(BufferBuilder.RenderedBuffer p_231210_) {
      VertexBuffer vertexbuffer = m_231213_(p_231210_);
      if (vertexbuffer != null) {
         vertexbuffer.m_166882_();
      }

   }

   @Nullable
   private static VertexBuffer m_231213_(BufferBuilder.RenderedBuffer p_231214_) {
      RenderSystem.assertOnRenderThread();
      if (p_231214_.m_231199_()) {
         p_231214_.m_231200_();
         return null;
      } else {
         VertexBuffer vertexbuffer = m_231206_(p_231214_.m_231198_().f_85733_());
         vertexbuffer.m_231221_(p_231214_);
         return vertexbuffer;
      }
   }

   private static VertexBuffer m_231206_(VertexFormat p_231207_) {
      VertexBuffer vertexbuffer = p_231207_.m_231233_();
      m_231204_(vertexbuffer);
      return vertexbuffer;
   }

   private static void m_231204_(VertexBuffer p_231205_) {
      if (p_231205_ != f_231201_) {
         p_231205_.m_85921_();
         f_231201_ = p_231205_;
      }

   }
}
