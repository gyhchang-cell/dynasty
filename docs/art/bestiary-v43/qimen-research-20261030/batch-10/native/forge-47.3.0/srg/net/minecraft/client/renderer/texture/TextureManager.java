package net.minecraft.client.renderer.texture;

import com.google.common.collect.Maps;
import com.google.common.collect.Sets;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.logging.LogUtils;
import com.mojang.realmsclient.RealmsMainScreen;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Iterator;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executor;
import net.minecraft.CrashReport;
import net.minecraft.CrashReportCategory;
import net.minecraft.ReportedException;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.PreparableReloadListener;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.slf4j.Logger;

@OnlyIn(Dist.CLIENT)
public class TextureManager implements PreparableReloadListener, Tickable, AutoCloseable {
   private static final Logger f_118467_ = LogUtils.getLogger();
   public static final ResourceLocation f_118466_ = new ResourceLocation("");
   private final Map<ResourceLocation, AbstractTexture> f_118468_ = Maps.newHashMap();
   private final Set<Tickable> f_118469_ = Sets.newHashSet();
   private final Map<String, Integer> f_118470_ = Maps.newHashMap();
   private final ResourceManager f_118471_;

   public TextureManager(ResourceManager p_118474_) {
      this.f_118471_ = p_118474_;
   }

   public void m_174784_(ResourceLocation p_174785_) {
      if (!RenderSystem.isOnRenderThread()) {
         RenderSystem.recordRenderCall(() -> {
            this.m_118519_(p_174785_);
         });
      } else {
         this.m_118519_(p_174785_);
      }

   }

   private void m_118519_(ResourceLocation p_118520_) {
      AbstractTexture abstracttexture = this.f_118468_.get(p_118520_);
      if (abstracttexture == null) {
         abstracttexture = new SimpleTexture(p_118520_);
         this.m_118495_(p_118520_, abstracttexture);
      }

      abstracttexture.m_117966_();
   }

   public void m_118495_(ResourceLocation p_118496_, AbstractTexture p_118497_) {
      p_118497_ = this.m_118515_(p_118496_, p_118497_);
      AbstractTexture abstracttexture = this.f_118468_.put(p_118496_, p_118497_);
      if (abstracttexture != p_118497_) {
         if (abstracttexture != null && abstracttexture != MissingTextureAtlasSprite.m_118080_()) {
            this.m_118508_(p_118496_, abstracttexture);
         }

         if (p_118497_ instanceof Tickable) {
            this.f_118469_.add((Tickable)p_118497_);
         }
      }

   }

   private void m_118508_(ResourceLocation p_118509_, AbstractTexture p_118510_) {
      if (p_118510_ != MissingTextureAtlasSprite.m_118080_()) {
         this.f_118469_.remove(p_118510_);

         try {
            p_118510_.close();
         } catch (Exception exception) {
            f_118467_.warn("Failed to close texture {}", p_118509_, exception);
         }
      }

      p_118510_.m_117964_();
   }

   private AbstractTexture m_118515_(ResourceLocation p_118516_, AbstractTexture p_118517_) {
      try {
         p_118517_.m_6704_(this.f_118471_);
         return p_118517_;
      } catch (IOException ioexception) {
         if (p_118516_ != f_118466_) {
            f_118467_.warn("Failed to load texture: {}", p_118516_, ioexception);
         }

         return MissingTextureAtlasSprite.m_118080_();
      } catch (Throwable throwable) {
         CrashReport crashreport = CrashReport.m_127521_(throwable, "Registering texture");
         CrashReportCategory crashreportcategory = crashreport.m_127514_("Resource location being registered");
         crashreportcategory.m_128159_("Resource location", p_118516_);
         crashreportcategory.m_128165_("Texture object class", () -> {
            return p_118517_.getClass().getName();
         });
         throw new ReportedException(crashreport);
      }
   }

   public AbstractTexture m_118506_(ResourceLocation p_118507_) {
      AbstractTexture abstracttexture = this.f_118468_.get(p_118507_);
      if (abstracttexture == null) {
         abstracttexture = new SimpleTexture(p_118507_);
         this.m_118495_(p_118507_, abstracttexture);
      }

      return abstracttexture;
   }

   public AbstractTexture m_174786_(ResourceLocation p_174787_, AbstractTexture p_174788_) {
      return this.f_118468_.getOrDefault(p_174787_, p_174788_);
   }

   public ResourceLocation m_118490_(String p_118491_, DynamicTexture p_118492_) {
      Integer integer = this.f_118470_.get(p_118491_);
      if (integer == null) {
         integer = 1;
      } else {
         integer = integer + 1;
      }

      this.f_118470_.put(p_118491_, integer);
      ResourceLocation resourcelocation = new ResourceLocation(String.format(Locale.ROOT, "dynamic/%s_%d", p_118491_, integer));
      this.m_118495_(resourcelocation, p_118492_);
      return resourcelocation;
   }

   public CompletableFuture<Void> m_118501_(ResourceLocation p_118502_, Executor p_118503_) {
      if (!this.f_118468_.containsKey(p_118502_)) {
         PreloadedTexture preloadedtexture = new PreloadedTexture(this.f_118471_, p_118502_, p_118503_);
         this.f_118468_.put(p_118502_, preloadedtexture);
         return preloadedtexture.m_118105_().thenRunAsync(() -> {
            this.m_118495_(p_118502_, preloadedtexture);
         }, TextureManager::m_118488_);
      } else {
         return CompletableFuture.completedFuture((Void)null);
      }
   }

   private static void m_118488_(Runnable p_118489_) {
      Minecraft.m_91087_().execute(() -> {
         RenderSystem.recordRenderCall(p_118489_::run);
      });
   }

   public void m_7673_() {
      for(Tickable tickable : this.f_118469_) {
         tickable.m_7673_();
      }

   }

   public void m_118513_(ResourceLocation p_118514_) {
      AbstractTexture abstracttexture = this.f_118468_.remove(p_118514_);
      if (abstracttexture != null) {
         this.f_118468_.remove(p_118514_); // Forge: fix MC-98707
         this.m_118508_(p_118514_, abstracttexture);
      }

   }

   public void close() {
      this.f_118468_.forEach(this::m_118508_);
      this.f_118468_.clear();
      this.f_118469_.clear();
      this.f_118470_.clear();
   }

   public CompletableFuture<Void> m_5540_(PreparableReloadListener.PreparationBarrier p_118476_, ResourceManager p_118477_, ProfilerFiller p_118478_, ProfilerFiller p_118479_, Executor p_118480_, Executor p_118481_) {
      CompletableFuture<Void> completablefuture = new CompletableFuture<>();
      CompletableFuture.allOf(TitleScreen.m_96754_(this, p_118480_), this.m_118501_(AbstractWidget.f_93617_, p_118480_)).thenCompose(p_118476_::m_6769_).thenAcceptAsync((p_247950_) -> {
         MissingTextureAtlasSprite.m_118080_();
         RealmsMainScreen.m_86406_(this.f_118471_);
         Iterator<Map.Entry<ResourceLocation, AbstractTexture>> iterator = this.f_118468_.entrySet().iterator();

         while(iterator.hasNext()) {
            Map.Entry<ResourceLocation, AbstractTexture> entry = iterator.next();
            ResourceLocation resourcelocation = entry.getKey();
            AbstractTexture abstracttexture = entry.getValue();
            if (abstracttexture == MissingTextureAtlasSprite.m_118080_() && !resourcelocation.equals(MissingTextureAtlasSprite.m_118071_())) {
               iterator.remove();
            } else {
               abstracttexture.m_6479_(this, p_118477_, resourcelocation, p_118481_);
            }
         }

         Minecraft.m_91087_().m_6937_(() -> {
            completablefuture.complete((Void)null);
         });
      }, (p_118505_) -> {
         RenderSystem.recordRenderCall(p_118505_::run);
      });
      return completablefuture;
   }

   public void m_276085_(Path p_276129_) {
      if (!RenderSystem.isOnRenderThread()) {
         RenderSystem.recordRenderCall(() -> {
            this.m_276083_(p_276129_);
         });
      } else {
         this.m_276083_(p_276129_);
      }

   }

   private void m_276083_(Path p_276128_) {
      try {
         Files.createDirectories(p_276128_);
      } catch (IOException ioexception) {
         f_118467_.error("Failed to create directory {}", p_276128_, ioexception);
         return;
      }

      this.f_118468_.forEach((p_276101_, p_276102_) -> {
         if (p_276102_ instanceof Dumpable dumpable) {
            try {
               dumpable.m_276079_(p_276101_, p_276128_);
            } catch (IOException ioexception1) {
               f_118467_.error("Failed to dump texture {}", p_276101_, ioexception1);
            }
         }

      });
   }
}
