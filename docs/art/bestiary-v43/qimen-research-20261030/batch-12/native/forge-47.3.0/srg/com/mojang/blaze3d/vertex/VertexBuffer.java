package com.mojang.blaze3d.vertex;

import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.platform.Window;
import com.mojang.blaze3d.systems.RenderSystem;
import java.nio.ByteBuffer;
import javax.annotation.Nullable;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.ShaderInstance;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Matrix4f;

@OnlyIn(Dist.CLIENT)
public class VertexBuffer implements AutoCloseable {
   private final VertexBuffer.Usage f_285574_;
   private int f_231217_;
   private int f_166860_;
   private int f_166862_;
   @Nullable
   private VertexFormat f_85917_;
   @Nullable
   private RenderSystem.AutoStorageIndexBuffer f_166865_;
   private VertexFormat.IndexType f_166861_;
   private int f_166863_;
   private VertexFormat.Mode f_166864_;

   public VertexBuffer(VertexBuffer.Usage p_286252_) {
      this.f_285574_ = p_286252_;
      RenderSystem.assertOnRenderThread();
      this.f_231217_ = GlStateManager._glGenBuffers();
      this.f_166860_ = GlStateManager._glGenBuffers();
      this.f_166862_ = GlStateManager._glGenVertexArrays();
   }

   public void m_231221_(BufferBuilder.RenderedBuffer p_231222_) {
      if (!this.m_231230_()) {
         RenderSystem.assertOnRenderThread();

         try {
            BufferBuilder.DrawState bufferbuilder$drawstate = p_231222_.m_231198_();
            this.f_85917_ = this.m_231218_(bufferbuilder$drawstate, p_231222_.m_231196_());
            this.f_166865_ = this.m_231223_(bufferbuilder$drawstate, p_231222_.m_231197_());
            this.f_166863_ = bufferbuilder$drawstate.f_166797_();
            this.f_166861_ = bufferbuilder$drawstate.f_166798_();
            this.f_166864_ = bufferbuilder$drawstate.f_85735_();
         } finally {
            p_231222_.m_231200_();
         }

      }
   }

   private VertexFormat m_231218_(BufferBuilder.DrawState p_231219_, ByteBuffer p_231220_) {
      boolean flag = false;
      if (!p_231219_.f_85733_().equals(this.f_85917_)) {
         if (this.f_85917_ != null) {
            this.f_85917_.m_86024_();
         }

         GlStateManager._glBindBuffer(34962, this.f_231217_);
         p_231219_.f_85733_().m_166912_();
         flag = true;
      }

      if (!p_231219_.f_166799_()) {
         if (!flag) {
            GlStateManager._glBindBuffer(34962, this.f_231217_);
         }

         RenderSystem.glBufferData(34962, p_231220_, this.f_285574_.f_285654_);
      }

      return p_231219_.f_85733_();
   }

   @Nullable
   private RenderSystem.AutoStorageIndexBuffer m_231223_(BufferBuilder.DrawState p_231224_, ByteBuffer p_231225_) {
      if (!p_231224_.f_166800_()) {
         GlStateManager._glBindBuffer(34963, this.f_166860_);
         RenderSystem.glBufferData(34963, p_231225_, this.f_285574_.f_285654_);
         return null;
      } else {
         RenderSystem.AutoStorageIndexBuffer rendersystem$autostorageindexbuffer = RenderSystem.getSequentialBuffer(p_231224_.f_85735_());
         if (rendersystem$autostorageindexbuffer != this.f_166865_ || !rendersystem$autostorageindexbuffer.m_221944_(p_231224_.f_166797_())) {
            rendersystem$autostorageindexbuffer.m_221946_(p_231224_.f_166797_());
         }

         return rendersystem$autostorageindexbuffer;
      }
   }

   public void m_85921_() {
      BufferUploader.m_231208_();
      GlStateManager._glBindVertexArray(this.f_166862_);
   }

   public static void m_85931_() {
      BufferUploader.m_231208_();
      GlStateManager._glBindVertexArray(0);
   }

   public void m_166882_() {
      RenderSystem.drawElements(this.f_166864_.f_166946_, this.f_166863_, this.m_231231_().f_166923_);
   }

   private VertexFormat.IndexType m_231231_() {
      RenderSystem.AutoStorageIndexBuffer rendersystem$autostorageindexbuffer = this.f_166865_;
      return rendersystem$autostorageindexbuffer != null ? rendersystem$autostorageindexbuffer.m_157483_() : this.f_166861_;
   }

   public void m_253207_(Matrix4f p_254480_, Matrix4f p_254555_, ShaderInstance p_253993_) {
      if (!RenderSystem.isOnRenderThread()) {
         RenderSystem.recordRenderCall(() -> {
            this.m_166876_(new Matrix4f(p_254480_), new Matrix4f(p_254555_), p_253993_);
         });
      } else {
         this.m_166876_(p_254480_, p_254555_, p_253993_);
      }

   }

   private void m_166876_(Matrix4f p_253705_, Matrix4f p_253737_, ShaderInstance p_166879_) {
      for(int i = 0; i < 12; ++i) {
         int j = RenderSystem.getShaderTexture(i);
         p_166879_.m_173350_("Sampler" + i, j);
      }

      if (p_166879_.f_173308_ != null) {
         p_166879_.f_173308_.m_5679_(p_253705_);
      }

      if (p_166879_.f_173309_ != null) {
         p_166879_.f_173309_.m_5679_(p_253737_);
      }

      if (p_166879_.f_200956_ != null) {
         p_166879_.f_200956_.m_200759_(RenderSystem.getInverseViewRotationMatrix());
      }

      if (p_166879_.f_173312_ != null) {
         p_166879_.f_173312_.m_5941_(RenderSystem.getShaderColor());
      }

      if (p_166879_.f_267422_ != null) {
         p_166879_.f_267422_.m_5985_(RenderSystem.getShaderGlintAlpha());
      }

      if (p_166879_.f_173315_ != null) {
         p_166879_.f_173315_.m_5985_(RenderSystem.getShaderFogStart());
      }

      if (p_166879_.f_173316_ != null) {
         p_166879_.f_173316_.m_5985_(RenderSystem.getShaderFogEnd());
      }

      if (p_166879_.f_173317_ != null) {
         p_166879_.f_173317_.m_5941_(RenderSystem.getShaderFogColor());
      }

      if (p_166879_.f_202432_ != null) {
         p_166879_.f_202432_.m_142617_(RenderSystem.getShaderFogShape().m_202324_());
      }

      if (p_166879_.f_173310_ != null) {
         p_166879_.f_173310_.m_5679_(RenderSystem.getTextureMatrix());
      }

      if (p_166879_.f_173319_ != null) {
         p_166879_.f_173319_.m_5985_(RenderSystem.getShaderGameTime());
      }

      if (p_166879_.f_173311_ != null) {
         Window window = Minecraft.m_91087_().m_91268_();
         p_166879_.f_173311_.m_7971_((float)window.m_85441_(), (float)window.m_85442_());
      }

      if (p_166879_.f_173318_ != null && (this.f_166864_ == VertexFormat.Mode.LINES || this.f_166864_ == VertexFormat.Mode.LINE_STRIP)) {
         p_166879_.f_173318_.m_5985_(RenderSystem.getShaderLineWidth());
      }

      RenderSystem.setupShaderLights(p_166879_);
      p_166879_.m_173363_();
      this.m_166882_();
      p_166879_.m_173362_();
   }

   public void close() {
      if (this.f_231217_ >= 0) {
         RenderSystem.glDeleteBuffers(this.f_231217_);
         this.f_231217_ = -1;
      }

      if (this.f_166860_ >= 0) {
         RenderSystem.glDeleteBuffers(this.f_166860_);
         this.f_166860_ = -1;
      }

      if (this.f_166862_ >= 0) {
         RenderSystem.glDeleteVertexArrays(this.f_166862_);
         this.f_166862_ = -1;
      }

   }

   public VertexFormat m_166892_() {
      return this.f_85917_;
   }

   public boolean m_231230_() {
      return this.f_166862_ == -1;
   }

   @OnlyIn(Dist.CLIENT)
   public static enum Usage {
      STATIC(35044),
      DYNAMIC(35048);

      final int f_285654_;

      private Usage(int p_286680_) {
         this.f_285654_ = p_286680_;
      }
   }
}
