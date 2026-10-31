package net.minecraft.client.renderer;

import com.google.common.collect.ImmutableList;
import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.PoseStack;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalDouble;
import java.util.function.Supplier;
import net.minecraft.Util;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.texture.TextureAtlas;
import net.minecraft.client.renderer.texture.TextureManager;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.apache.commons.lang3.tuple.Triple;
import org.joml.Matrix4f;

@OnlyIn(Dist.CLIENT)
public abstract class RenderStateShard {
   private static final float f_173089_ = 0.99975586F;
   public static final double f_267492_ = 8.0D;
   protected final String f_110133_;
   protected Runnable f_110131_;
   private final Runnable f_110132_;
   protected static final RenderStateShard.TransparencyStateShard f_110134_ = new RenderStateShard.TransparencyStateShard("no_transparency", () -> {
      RenderSystem.disableBlend();
   }, () -> {
   });
   protected static final RenderStateShard.TransparencyStateShard f_110135_ = new RenderStateShard.TransparencyStateShard("additive_transparency", () -> {
      RenderSystem.enableBlend();
      RenderSystem.blendFunc(GlStateManager.SourceFactor.ONE, GlStateManager.DestFactor.ONE);
   }, () -> {
      RenderSystem.disableBlend();
      RenderSystem.defaultBlendFunc();
   });
   protected static final RenderStateShard.TransparencyStateShard f_110136_ = new RenderStateShard.TransparencyStateShard("lightning_transparency", () -> {
      RenderSystem.enableBlend();
      RenderSystem.blendFunc(GlStateManager.SourceFactor.SRC_ALPHA, GlStateManager.DestFactor.ONE);
   }, () -> {
      RenderSystem.disableBlend();
      RenderSystem.defaultBlendFunc();
   });
   protected static final RenderStateShard.TransparencyStateShard f_110137_ = new RenderStateShard.TransparencyStateShard("glint_transparency", () -> {
      RenderSystem.enableBlend();
      RenderSystem.blendFuncSeparate(GlStateManager.SourceFactor.SRC_COLOR, GlStateManager.DestFactor.ONE, GlStateManager.SourceFactor.ZERO, GlStateManager.DestFactor.ONE);
   }, () -> {
      RenderSystem.disableBlend();
      RenderSystem.defaultBlendFunc();
   });
   protected static final RenderStateShard.TransparencyStateShard f_110138_ = new RenderStateShard.TransparencyStateShard("crumbling_transparency", () -> {
      RenderSystem.enableBlend();
      RenderSystem.blendFuncSeparate(GlStateManager.SourceFactor.DST_COLOR, GlStateManager.DestFactor.SRC_COLOR, GlStateManager.SourceFactor.ONE, GlStateManager.DestFactor.ZERO);
   }, () -> {
      RenderSystem.disableBlend();
      RenderSystem.defaultBlendFunc();
   });
   protected static final RenderStateShard.TransparencyStateShard f_110139_ = new RenderStateShard.TransparencyStateShard("translucent_transparency", () -> {
      RenderSystem.enableBlend();
      RenderSystem.blendFuncSeparate(GlStateManager.SourceFactor.SRC_ALPHA, GlStateManager.DestFactor.ONE_MINUS_SRC_ALPHA, GlStateManager.SourceFactor.ONE, GlStateManager.DestFactor.ONE_MINUS_SRC_ALPHA);
   }, () -> {
      RenderSystem.disableBlend();
      RenderSystem.defaultBlendFunc();
   });
   protected static final RenderStateShard.ShaderStateShard f_173096_ = new RenderStateShard.ShaderStateShard();
   protected static final RenderStateShard.ShaderStateShard f_173099_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172832_);
   protected static final RenderStateShard.ShaderStateShard f_173100_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172808_);
   protected static final RenderStateShard.ShaderStateShard f_173101_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172814_);
   protected static final RenderStateShard.ShaderStateShard f_173102_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172817_);
   protected static final RenderStateShard.ShaderStateShard f_173103_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172835_);
   protected static final RenderStateShard.ShaderStateShard f_173104_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172811_);
   protected static final RenderStateShard.ShaderStateShard f_173105_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172640_);
   protected static final RenderStateShard.ShaderStateShard f_173106_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172643_);
   protected static final RenderStateShard.ShaderStateShard f_173107_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172646_);
   protected static final RenderStateShard.ShaderStateShard f_173108_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172649_);
   protected static final RenderStateShard.ShaderStateShard f_173109_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172652_);
   protected static final RenderStateShard.ShaderStateShard f_173110_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172655_);
   protected static final RenderStateShard.ShaderStateShard f_173111_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172658_);
   protected static final RenderStateShard.ShaderStateShard f_173112_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172661_);
   protected static final RenderStateShard.ShaderStateShard f_173113_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172664_);
   protected static final RenderStateShard.ShaderStateShard f_173114_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172667_);
   protected static final RenderStateShard.ShaderStateShard f_173063_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172670_);
   protected static final RenderStateShard.ShaderStateShard f_173064_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172673_);
   protected static final RenderStateShard.ShaderStateShard f_173065_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172676_);
   protected static final RenderStateShard.ShaderStateShard f_173066_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172679_);
   protected static final RenderStateShard.ShaderStateShard f_234323_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_234223_);
   protected static final RenderStateShard.ShaderStateShard f_173067_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172682_);
   protected static final RenderStateShard.ShaderStateShard f_173068_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172685_);
   protected static final RenderStateShard.ShaderStateShard f_173069_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172688_);
   protected static final RenderStateShard.ShaderStateShard f_173070_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172691_);
   protected static final RenderStateShard.ShaderStateShard f_173071_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172694_);
   protected static final RenderStateShard.ShaderStateShard f_173072_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172697_);
   protected static final RenderStateShard.ShaderStateShard f_173073_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172700_);
   protected static final RenderStateShard.ShaderStateShard f_173074_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172703_);
   protected static final RenderStateShard.ShaderStateShard f_173075_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172706_);
   protected static final RenderStateShard.ShaderStateShard f_173076_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172709_);
   protected static final RenderStateShard.ShaderStateShard f_173077_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172712_);
   protected static final RenderStateShard.ShaderStateShard f_173078_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172738_);
   protected static final RenderStateShard.ShaderStateShard f_173079_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172741_);
   protected static final RenderStateShard.ShaderStateShard f_173080_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172744_);
   protected static final RenderStateShard.ShaderStateShard f_173081_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172745_);
   protected static final RenderStateShard.ShaderStateShard f_173082_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172746_);
   protected static final RenderStateShard.ShaderStateShard f_173083_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172747_);
   protected static final RenderStateShard.ShaderStateShard f_173084_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172748_);
   protected static final RenderStateShard.ShaderStateShard f_173085_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172758_);
   protected static final RenderStateShard.ShaderStateShard f_173086_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172749_);
   protected static final RenderStateShard.ShaderStateShard f_268568_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_269563_);
   protected static final RenderStateShard.ShaderStateShard f_173087_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172750_);
   protected static final RenderStateShard.ShaderStateShard f_173088_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172751_);
   protected static final RenderStateShard.ShaderStateShard f_268491_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_269511_);
   protected static final RenderStateShard.ShaderStateShard f_173090_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172752_);
   protected static final RenderStateShard.ShaderStateShard f_173091_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172753_);
   protected static final RenderStateShard.ShaderStateShard f_173092_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172754_);
   protected static final RenderStateShard.ShaderStateShard f_173093_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172755_);
   protected static final RenderStateShard.ShaderStateShard f_173094_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172756_);
   protected static final RenderStateShard.ShaderStateShard f_173095_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_172757_);
   protected static final RenderStateShard.ShaderStateShard f_285573_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_285858_);
   protected static final RenderStateShard.ShaderStateShard f_285619_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_285975_);
   protected static final RenderStateShard.ShaderStateShard f_285642_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_285738_);
   protected static final RenderStateShard.ShaderStateShard f_285582_ = new RenderStateShard.ShaderStateShard(GameRenderer::m_285862_);
   protected static final RenderStateShard.TextureStateShard f_110145_ = new RenderStateShard.TextureStateShard(TextureAtlas.f_118259_, false, true);
   protected static final RenderStateShard.TextureStateShard f_110146_ = new RenderStateShard.TextureStateShard(TextureAtlas.f_118259_, false, false);
   protected static final RenderStateShard.EmptyTextureStateShard f_110147_ = new RenderStateShard.EmptyTextureStateShard();
   protected static final RenderStateShard.TexturingStateShard f_110148_ = new RenderStateShard.TexturingStateShard("default_texturing", () -> {
   }, () -> {
   });
   protected static final RenderStateShard.TexturingStateShard f_110150_ = new RenderStateShard.TexturingStateShard("glint_texturing", () -> {
      m_110186_(8.0F);
   }, () -> {
      RenderSystem.resetTextureMatrix();
   });
   protected static final RenderStateShard.TexturingStateShard f_110151_ = new RenderStateShard.TexturingStateShard("entity_glint_texturing", () -> {
      m_110186_(0.16F);
   }, () -> {
      RenderSystem.resetTextureMatrix();
   });
   protected static final RenderStateShard.LightmapStateShard f_110152_ = new RenderStateShard.LightmapStateShard(true);
   protected static final RenderStateShard.LightmapStateShard f_110153_ = new RenderStateShard.LightmapStateShard(false);
   protected static final RenderStateShard.OverlayStateShard f_110154_ = new RenderStateShard.OverlayStateShard(true);
   protected static final RenderStateShard.OverlayStateShard f_110155_ = new RenderStateShard.OverlayStateShard(false);
   protected static final RenderStateShard.CullStateShard f_110158_ = new RenderStateShard.CullStateShard(true);
   protected static final RenderStateShard.CullStateShard f_110110_ = new RenderStateShard.CullStateShard(false);
   protected static final RenderStateShard.DepthTestStateShard f_110111_ = new RenderStateShard.DepthTestStateShard("always", 519);
   protected static final RenderStateShard.DepthTestStateShard f_110112_ = new RenderStateShard.DepthTestStateShard("==", 514);
   protected static final RenderStateShard.DepthTestStateShard f_110113_ = new RenderStateShard.DepthTestStateShard("<=", 515);
   protected static final RenderStateShard.DepthTestStateShard f_285579_ = new RenderStateShard.DepthTestStateShard(">", 516);
   protected static final RenderStateShard.WriteMaskStateShard f_110114_ = new RenderStateShard.WriteMaskStateShard(true, true);
   protected static final RenderStateShard.WriteMaskStateShard f_110115_ = new RenderStateShard.WriteMaskStateShard(true, false);
   protected static final RenderStateShard.WriteMaskStateShard f_110116_ = new RenderStateShard.WriteMaskStateShard(false, true);
   protected static final RenderStateShard.LayeringStateShard f_110117_ = new RenderStateShard.LayeringStateShard("no_layering", () -> {
   }, () -> {
   });
   protected static final RenderStateShard.LayeringStateShard f_110118_ = new RenderStateShard.LayeringStateShard("polygon_offset_layering", () -> {
      RenderSystem.polygonOffset(-1.0F, -10.0F);
      RenderSystem.enablePolygonOffset();
   }, () -> {
      RenderSystem.polygonOffset(0.0F, 0.0F);
      RenderSystem.disablePolygonOffset();
   });
   protected static final RenderStateShard.LayeringStateShard f_110119_ = new RenderStateShard.LayeringStateShard("view_offset_z_layering", () -> {
      PoseStack posestack = RenderSystem.getModelViewStack();
      posestack.m_85836_();
      posestack.m_85841_(0.99975586F, 0.99975586F, 0.99975586F);
      RenderSystem.applyModelViewMatrix();
   }, () -> {
      PoseStack posestack = RenderSystem.getModelViewStack();
      posestack.m_85849_();
      RenderSystem.applyModelViewMatrix();
   });
   protected static final RenderStateShard.OutputStateShard f_110123_ = new RenderStateShard.OutputStateShard("main_target", () -> {
   }, () -> {
   });
   protected static final RenderStateShard.OutputStateShard f_110124_ = new RenderStateShard.OutputStateShard("outline_target", () -> {
      Minecraft.m_91087_().f_91060_.m_109827_().m_83947_(false);
   }, () -> {
      Minecraft.m_91087_().m_91385_().m_83947_(false);
   });
   protected static final RenderStateShard.OutputStateShard f_110125_ = new RenderStateShard.OutputStateShard("translucent_target", () -> {
      if (Minecraft.m_91085_()) {
         Minecraft.m_91087_().f_91060_.m_109828_().m_83947_(false);
      }

   }, () -> {
      if (Minecraft.m_91085_()) {
         Minecraft.m_91087_().m_91385_().m_83947_(false);
      }

   });
   protected static final RenderStateShard.OutputStateShard f_110126_ = new RenderStateShard.OutputStateShard("particles_target", () -> {
      if (Minecraft.m_91085_()) {
         Minecraft.m_91087_().f_91060_.m_109830_().m_83947_(false);
      }

   }, () -> {
      if (Minecraft.m_91085_()) {
         Minecraft.m_91087_().m_91385_().m_83947_(false);
      }

   });
   protected static final RenderStateShard.OutputStateShard f_110127_ = new RenderStateShard.OutputStateShard("weather_target", () -> {
      if (Minecraft.m_91085_()) {
         Minecraft.m_91087_().f_91060_.m_109831_().m_83947_(false);
      }

   }, () -> {
      if (Minecraft.m_91085_()) {
         Minecraft.m_91087_().m_91385_().m_83947_(false);
      }

   });
   protected static final RenderStateShard.OutputStateShard f_110128_ = new RenderStateShard.OutputStateShard("clouds_target", () -> {
      if (Minecraft.m_91085_()) {
         Minecraft.m_91087_().f_91060_.m_109832_().m_83947_(false);
      }

   }, () -> {
      if (Minecraft.m_91085_()) {
         Minecraft.m_91087_().m_91385_().m_83947_(false);
      }

   });
   protected static final RenderStateShard.OutputStateShard f_110129_ = new RenderStateShard.OutputStateShard("item_entity_target", () -> {
      if (Minecraft.m_91085_()) {
         Minecraft.m_91087_().f_91060_.m_109829_().m_83947_(false);
      }

   }, () -> {
      if (Minecraft.m_91085_()) {
         Minecraft.m_91087_().m_91385_().m_83947_(false);
      }

   });
   protected static final RenderStateShard.LineStateShard f_110130_ = new RenderStateShard.LineStateShard(OptionalDouble.of(1.0D));
   protected static final RenderStateShard.ColorLogicStateShard f_285585_ = new RenderStateShard.ColorLogicStateShard("no_color_logic", () -> {
      RenderSystem.disableColorLogicOp();
   }, () -> {
   });
   protected static final RenderStateShard.ColorLogicStateShard f_285603_ = new RenderStateShard.ColorLogicStateShard("or_reverse", () -> {
      RenderSystem.enableColorLogicOp();
      RenderSystem.logicOp(GlStateManager.LogicOp.OR_REVERSE);
   }, () -> {
      RenderSystem.disableColorLogicOp();
   });

   public RenderStateShard(String p_110161_, Runnable p_110162_, Runnable p_110163_) {
      this.f_110133_ = p_110161_;
      this.f_110131_ = p_110162_;
      this.f_110132_ = p_110163_;
   }

   public void m_110185_() {
      this.f_110131_.run();
   }

   public void m_110188_() {
      this.f_110132_.run();
   }

   public String toString() {
      return this.f_110133_;
   }

   private static void m_110186_(float p_110187_) {
      long i = (long)((double)Util.m_137550_() * Minecraft.m_91087_().f_91066_.m_267805_().m_231551_() * 8.0D);
      float f = (float)(i % 110000L) / 110000.0F;
      float f1 = (float)(i % 30000L) / 30000.0F;
      Matrix4f matrix4f = (new Matrix4f()).translation(-f, f1, 0.0F);
      matrix4f.rotateZ(0.17453292F).scale(p_110187_);
      RenderSystem.setTextureMatrix(matrix4f);
   }

   @OnlyIn(Dist.CLIENT)
   public static class BooleanStateShard extends RenderStateShard {
      private final boolean f_110227_;

      public BooleanStateShard(String p_110229_, Runnable p_110230_, Runnable p_110231_, boolean p_110232_) {
         super(p_110229_, p_110230_, p_110231_);
         this.f_110227_ = p_110232_;
      }

      public String toString() {
         return this.f_110133_ + "[" + this.f_110227_ + "]";
      }
   }

   @OnlyIn(Dist.CLIENT)
   protected static class ColorLogicStateShard extends RenderStateShard {
      public ColorLogicStateShard(String p_286784_, Runnable p_286884_, Runnable p_286375_) {
         super(p_286784_, p_286884_, p_286375_);
      }
   }

   @OnlyIn(Dist.CLIENT)
   public static class CullStateShard extends RenderStateShard.BooleanStateShard {
      public CullStateShard(boolean p_110238_) {
         super("cull", () -> {
            if (!p_110238_) {
               RenderSystem.disableCull();
            }

         }, () -> {
            if (!p_110238_) {
               RenderSystem.enableCull();
            }

         }, p_110238_);
      }
   }

   @OnlyIn(Dist.CLIENT)
   public static class DepthTestStateShard extends RenderStateShard {
      private final String f_110243_;

      public DepthTestStateShard(String p_110246_, int p_110247_) {
         super("depth_test", () -> {
            if (p_110247_ != 519) {
               RenderSystem.enableDepthTest();
               RenderSystem.depthFunc(p_110247_);
            }

         }, () -> {
            if (p_110247_ != 519) {
               RenderSystem.disableDepthTest();
               RenderSystem.depthFunc(515);
            }

         });
         this.f_110243_ = p_110246_;
      }

      public String toString() {
         return this.f_110133_ + "[" + this.f_110243_ + "]";
      }
   }

   @OnlyIn(Dist.CLIENT)
   public static class EmptyTextureStateShard extends RenderStateShard {
      public EmptyTextureStateShard(Runnable p_173117_, Runnable p_173118_) {
         super("texture", p_173117_, p_173118_);
      }

      EmptyTextureStateShard() {
         super("texture", () -> {
         }, () -> {
         });
      }

      protected Optional<ResourceLocation> m_142706_() {
         return Optional.empty();
      }
   }

   @OnlyIn(Dist.CLIENT)
   public static class LayeringStateShard extends RenderStateShard {
      public LayeringStateShard(String p_110267_, Runnable p_110268_, Runnable p_110269_) {
         super(p_110267_, p_110268_, p_110269_);
      }
   }

   @OnlyIn(Dist.CLIENT)
   public static class LightmapStateShard extends RenderStateShard.BooleanStateShard {
      public LightmapStateShard(boolean p_110271_) {
         super("lightmap", () -> {
            if (p_110271_) {
               Minecraft.m_91087_().f_91063_.m_109154_().m_109896_();
            }

         }, () -> {
            if (p_110271_) {
               Minecraft.m_91087_().f_91063_.m_109154_().m_109891_();
            }

         }, p_110271_);
      }
   }

   @OnlyIn(Dist.CLIENT)
   protected static class LineStateShard extends RenderStateShard {
      private final OptionalDouble f_110276_;

      public LineStateShard(OptionalDouble p_110278_) {
         super("line_width", () -> {
            if (!Objects.equals(p_110278_, OptionalDouble.of(1.0D))) {
               if (p_110278_.isPresent()) {
                  RenderSystem.lineWidth((float)p_110278_.getAsDouble());
               } else {
                  RenderSystem.lineWidth(Math.max(2.5F, (float)Minecraft.m_91087_().m_91268_().m_85441_() / 1920.0F * 2.5F));
               }
            }

         }, () -> {
            if (!Objects.equals(p_110278_, OptionalDouble.of(1.0D))) {
               RenderSystem.lineWidth(1.0F);
            }

         });
         this.f_110276_ = p_110278_;
      }

      public String toString() {
         return this.f_110133_ + "[" + (this.f_110276_.isPresent() ? this.f_110276_.getAsDouble() : "window_scale") + "]";
      }
   }

   @OnlyIn(Dist.CLIENT)
   public static class MultiTextureStateShard extends RenderStateShard.EmptyTextureStateShard {
      private final Optional<ResourceLocation> f_173121_;

      MultiTextureStateShard(ImmutableList<Triple<ResourceLocation, Boolean, Boolean>> p_173123_) {
         super(() -> {
            int i = 0;

            for(Triple<ResourceLocation, Boolean, Boolean> triple : p_173123_) {
               TextureManager texturemanager = Minecraft.m_91087_().m_91097_();
               texturemanager.m_118506_(triple.getLeft()).m_117960_(triple.getMiddle(), triple.getRight());
               RenderSystem.setShaderTexture(i++, triple.getLeft());
            }

         }, () -> {
         });
         this.f_173121_ = p_173123_.stream().findFirst().map(Triple::getLeft);
      }

      protected Optional<ResourceLocation> m_142706_() {
         return this.f_173121_;
      }

      public static RenderStateShard.MultiTextureStateShard.Builder m_173127_() {
         return new RenderStateShard.MultiTextureStateShard.Builder();
      }

      @OnlyIn(Dist.CLIENT)
      public static final class Builder {
         private final ImmutableList.Builder<Triple<ResourceLocation, Boolean, Boolean>> f_173129_ = new ImmutableList.Builder<>();

         public RenderStateShard.MultiTextureStateShard.Builder m_173132_(ResourceLocation p_173133_, boolean p_173134_, boolean p_173135_) {
            this.f_173129_.add(Triple.of(p_173133_, p_173134_, p_173135_));
            return this;
         }

         public RenderStateShard.MultiTextureStateShard m_173131_() {
            return new RenderStateShard.MultiTextureStateShard(this.f_173129_.build());
         }
      }
   }

   @OnlyIn(Dist.CLIENT)
   public static final class OffsetTexturingStateShard extends RenderStateShard.TexturingStateShard {
      public OffsetTexturingStateShard(float p_110290_, float p_110291_) {
         super("offset_texturing", () -> {
            RenderSystem.setTextureMatrix((new Matrix4f()).translation(p_110290_, p_110291_, 0.0F));
         }, () -> {
            RenderSystem.resetTextureMatrix();
         });
      }
   }

   @OnlyIn(Dist.CLIENT)
   public static class OutputStateShard extends RenderStateShard {
      public OutputStateShard(String p_110300_, Runnable p_110301_, Runnable p_110302_) {
         super(p_110300_, p_110301_, p_110302_);
      }
   }

   @OnlyIn(Dist.CLIENT)
   public static class OverlayStateShard extends RenderStateShard.BooleanStateShard {
      public OverlayStateShard(boolean p_110304_) {
         super("overlay", () -> {
            if (p_110304_) {
               Minecraft.m_91087_().f_91063_.m_109155_().m_118087_();
            }

         }, () -> {
            if (p_110304_) {
               Minecraft.m_91087_().f_91063_.m_109155_().m_118098_();
            }

         }, p_110304_);
      }
   }

   @OnlyIn(Dist.CLIENT)
   public static class ShaderStateShard extends RenderStateShard {
      private final Optional<Supplier<ShaderInstance>> f_173136_;

      public ShaderStateShard(Supplier<ShaderInstance> p_173139_) {
         super("shader", () -> {
            RenderSystem.setShader(p_173139_);
         }, () -> {
         });
         this.f_173136_ = Optional.of(p_173139_);
      }

      public ShaderStateShard() {
         super("shader", () -> {
            RenderSystem.setShader(() -> {
               return null;
            });
         }, () -> {
         });
         this.f_173136_ = Optional.empty();
      }

      public String toString() {
         return this.f_110133_ + "[" + this.f_173136_ + "]";
      }
   }

   @OnlyIn(Dist.CLIENT)
   public static class TextureStateShard extends RenderStateShard.EmptyTextureStateShard {
      private final Optional<ResourceLocation> f_110328_;
      protected boolean f_110329_;
      protected boolean f_110330_;

      public TextureStateShard(ResourceLocation p_110333_, boolean p_110334_, boolean p_110335_) {
         super(() -> {
            TextureManager texturemanager = Minecraft.m_91087_().m_91097_();
            texturemanager.m_118506_(p_110333_).m_117960_(p_110334_, p_110335_);
            RenderSystem.setShaderTexture(0, p_110333_);
         }, () -> {
         });
         this.f_110328_ = Optional.of(p_110333_);
         this.f_110329_ = p_110334_;
         this.f_110330_ = p_110335_;
      }

      public String toString() {
         return this.f_110133_ + "[" + this.f_110328_ + "(blur=" + this.f_110329_ + ", mipmap=" + this.f_110330_ + ")]";
      }

      protected Optional<ResourceLocation> m_142706_() {
         return this.f_110328_;
      }
   }

   @OnlyIn(Dist.CLIENT)
   public static class TexturingStateShard extends RenderStateShard {
      public TexturingStateShard(String p_110349_, Runnable p_110350_, Runnable p_110351_) {
         super(p_110349_, p_110350_, p_110351_);
      }
   }

   @OnlyIn(Dist.CLIENT)
   public static class TransparencyStateShard extends RenderStateShard {
      public TransparencyStateShard(String p_110353_, Runnable p_110354_, Runnable p_110355_) {
         super(p_110353_, p_110354_, p_110355_);
      }
   }

   @OnlyIn(Dist.CLIENT)
   public static class WriteMaskStateShard extends RenderStateShard {
      private final boolean f_110356_;
      private final boolean f_110357_;

      public WriteMaskStateShard(boolean p_110359_, boolean p_110360_) {
         super("write_mask_state", () -> {
            if (!p_110360_) {
               RenderSystem.depthMask(p_110360_);
            }

            if (!p_110359_) {
               RenderSystem.colorMask(p_110359_, p_110359_, p_110359_, p_110359_);
            }

         }, () -> {
            if (!p_110360_) {
               RenderSystem.depthMask(true);
            }

            if (!p_110359_) {
               RenderSystem.colorMask(true, true, true, true);
            }

         });
         this.f_110356_ = p_110359_;
         this.f_110357_ = p_110360_;
      }

      public String toString() {
         return this.f_110133_ + "[writeColor=" + this.f_110356_ + ", writeDepth=" + this.f_110357_ + "]";
      }
   }
}
