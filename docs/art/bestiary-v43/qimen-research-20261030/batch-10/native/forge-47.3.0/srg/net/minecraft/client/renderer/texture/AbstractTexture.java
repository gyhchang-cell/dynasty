package net.minecraft.client.renderer.texture;

import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.platform.TextureUtil;
import com.mojang.blaze3d.systems.RenderSystem;
import java.io.IOException;
import java.util.concurrent.Executor;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public abstract class AbstractTexture implements AutoCloseable {
   public static final int f_174680_ = -1;
   protected int f_117950_ = -1;
   protected boolean f_117951_;
   protected boolean f_117952_;

   public void m_117960_(boolean p_117961_, boolean p_117962_) {
      RenderSystem.assertOnRenderThreadOrInit();
      this.f_117951_ = p_117961_;
      this.f_117952_ = p_117962_;
      int i;
      int j;
      if (p_117961_) {
         i = p_117962_ ? 9987 : 9729;
         j = 9729;
      } else {
         i = p_117962_ ? 9986 : 9728;
         j = 9728;
      }

      this.m_117966_();
      GlStateManager._texParameter(3553, 10241, i);
      GlStateManager._texParameter(3553, 10240, j);
   }

   // FORGE: This seems to have been stripped out, but we need it
   private boolean lastBlur;
   private boolean lastMipmap;

   public void setBlurMipmap(boolean blur, boolean mipmap) {
      this.lastBlur = this.f_117951_;
      this.lastMipmap = this.f_117952_;
      m_117960_(blur, mipmap);
   }

   public void restoreLastBlurMipmap() {
      m_117960_(this.lastBlur, this.lastMipmap);
   }

   public int m_117963_() {
      RenderSystem.assertOnRenderThreadOrInit();
      if (this.f_117950_ == -1) {
         this.f_117950_ = TextureUtil.generateTextureId();
      }

      return this.f_117950_;
   }

   public void m_117964_() {
      if (!RenderSystem.isOnRenderThread()) {
         RenderSystem.recordRenderCall(() -> {
            if (this.f_117950_ != -1) {
               TextureUtil.releaseTextureId(this.f_117950_);
               this.f_117950_ = -1;
            }

         });
      } else if (this.f_117950_ != -1) {
         TextureUtil.releaseTextureId(this.f_117950_);
         this.f_117950_ = -1;
      }

   }

   public abstract void m_6704_(ResourceManager p_117955_) throws IOException;

   public void m_117966_() {
      if (!RenderSystem.isOnRenderThreadOrInit()) {
         RenderSystem.recordRenderCall(() -> {
            GlStateManager._bindTexture(this.m_117963_());
         });
      } else {
         GlStateManager._bindTexture(this.m_117963_());
      }

   }

   public void m_6479_(TextureManager p_117956_, ResourceManager p_117957_, ResourceLocation p_117958_, Executor p_117959_) {
      p_117956_.m_118495_(p_117958_, this);
   }

   public void close() {
   }
}
