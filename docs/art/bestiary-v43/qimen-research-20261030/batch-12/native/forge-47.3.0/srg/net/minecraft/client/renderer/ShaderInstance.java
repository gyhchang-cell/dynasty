package net.minecraft.client.renderer;

import com.google.common.collect.Lists;
import com.google.common.collect.Maps;
import com.google.common.collect.Sets;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.mojang.blaze3d.pipeline.RenderTarget;
import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.preprocessor.GlslPreprocessor;
import com.mojang.blaze3d.shaders.AbstractUniform;
import com.mojang.blaze3d.shaders.BlendMode;
import com.mojang.blaze3d.shaders.Program;
import com.mojang.blaze3d.shaders.ProgramManager;
import com.mojang.blaze3d.shaders.Shader;
import com.mojang.blaze3d.shaders.Uniform;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.mojang.logging.LogUtils;
import it.unimi.dsi.fastutil.ints.IntArrayList;
import it.unimi.dsi.fastutil.ints.IntList;
import java.io.IOException;
import java.io.InputStream;
import java.io.Reader;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Set;
import javax.annotation.Nullable;
import net.minecraft.FileUtil;
import net.minecraft.client.renderer.texture.AbstractTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.ChainedJsonException;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.server.packs.resources.ResourceProvider;
import net.minecraft.util.GsonHelper;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.apache.commons.io.IOUtils;
import org.slf4j.Logger;

@OnlyIn(Dist.CLIENT)
public class ShaderInstance implements Shader, AutoCloseable {
   public static final String f_173321_ = "shaders";
   private static final String f_244364_ = "shaders/core/";
   private static final String f_173322_ = "shaders/include/";
   static final Logger f_173323_ = LogUtils.getLogger();
   private static final AbstractUniform f_173324_ = new AbstractUniform();
   private static final boolean f_173325_ = true;
   private static ShaderInstance f_173326_;
   private static int f_173327_ = -1;
   private final Map<String, Object> f_173328_ = Maps.newHashMap();
   private final List<String> f_173329_ = Lists.newArrayList();
   private final List<Integer> f_173330_ = Lists.newArrayList();
   private final List<Uniform> f_173331_ = Lists.newArrayList();
   private final List<Integer> f_173332_ = Lists.newArrayList();
   private final Map<String, Uniform> f_173333_ = Maps.newHashMap();
   private final int f_173299_;
   private final String f_173300_;
   private boolean f_173301_;
   private final BlendMode f_173302_;
   private final List<Integer> f_173303_;
   private final List<String> f_173304_;
   private final Program f_173305_;
   private final Program f_173306_;
   private final VertexFormat f_173307_;
   @Nullable
   public final Uniform f_173308_;
   @Nullable
   public final Uniform f_173309_;
   @Nullable
   public final Uniform f_200956_;
   @Nullable
   public final Uniform f_173310_;
   @Nullable
   public final Uniform f_173311_;
   @Nullable
   public final Uniform f_173312_;
   @Nullable
   public final Uniform f_173313_;
   @Nullable
   public final Uniform f_173314_;
   @Nullable
   public final Uniform f_267422_;
   @Nullable
   public final Uniform f_173315_;
   @Nullable
   public final Uniform f_173316_;
   @Nullable
   public final Uniform f_173317_;
   @Nullable
   public final Uniform f_202432_;
   @Nullable
   public final Uniform f_173318_;
   @Nullable
   public final Uniform f_173319_;
   @Nullable
   public final Uniform f_173320_;

   @Deprecated // FORGE: Use the ResourceLocation variant below
   public ShaderInstance(ResourceProvider p_173336_, String p_173337_, VertexFormat p_173338_) throws IOException {
      this(p_173336_, new ResourceLocation(p_173337_), p_173338_);
   }
   public ShaderInstance(ResourceProvider p_173336_, ResourceLocation shaderLocation, VertexFormat p_173338_) throws IOException {
      this.f_173300_ = shaderLocation.m_135827_().equals("minecraft") ? shaderLocation.m_135815_() : shaderLocation.toString();
      this.f_173307_ = p_173338_;
      ResourceLocation resourcelocation = new ResourceLocation(shaderLocation.m_135827_(), "shaders/core/" + shaderLocation.m_135815_() + ".json");

      try (Reader reader = p_173336_.m_215597_(resourcelocation)) {
         JsonObject jsonobject = GsonHelper.m_13859_(reader);
         String s1 = GsonHelper.m_13906_(jsonobject, "vertex");
         String s = GsonHelper.m_13906_(jsonobject, "fragment");
         JsonArray jsonarray = GsonHelper.m_13832_(jsonobject, "samplers", (JsonArray)null);
         if (jsonarray != null) {
            int i = 0;

            for(JsonElement jsonelement : jsonarray) {
               try {
                  this.m_173344_(jsonelement);
               } catch (Exception exception2) {
                  ChainedJsonException chainedjsonexception1 = ChainedJsonException.m_135906_(exception2);
                  chainedjsonexception1.m_135908_("samplers[" + i + "]");
                  throw chainedjsonexception1;
               }

               ++i;
            }
         }

         JsonArray jsonarray1 = GsonHelper.m_13832_(jsonobject, "attributes", (JsonArray)null);
         if (jsonarray1 != null) {
            int j = 0;
            this.f_173303_ = Lists.newArrayListWithCapacity(jsonarray1.size());
            this.f_173304_ = Lists.newArrayListWithCapacity(jsonarray1.size());

            for(JsonElement jsonelement1 : jsonarray1) {
               try {
                  this.f_173304_.add(GsonHelper.m_13805_(jsonelement1, "attribute"));
               } catch (Exception exception1) {
                  ChainedJsonException chainedjsonexception2 = ChainedJsonException.m_135906_(exception1);
                  chainedjsonexception2.m_135908_("attributes[" + j + "]");
                  throw chainedjsonexception2;
               }

               ++j;
            }
         } else {
            this.f_173303_ = null;
            this.f_173304_ = null;
         }

         JsonArray jsonarray2 = GsonHelper.m_13832_(jsonobject, "uniforms", (JsonArray)null);
         if (jsonarray2 != null) {
            int k = 0;

            for(JsonElement jsonelement2 : jsonarray2) {
               try {
                  this.m_173354_(jsonelement2);
               } catch (Exception exception) {
                  ChainedJsonException chainedjsonexception3 = ChainedJsonException.m_135906_(exception);
                  chainedjsonexception3.m_135908_("uniforms[" + k + "]");
                  throw chainedjsonexception3;
               }

               ++k;
            }
         }

         this.f_173302_ = m_173346_(GsonHelper.m_13841_(jsonobject, "blend", (JsonObject)null));
         this.f_173305_ = m_173340_(p_173336_, Program.Type.VERTEX, s1);
         this.f_173306_ = m_173340_(p_173336_, Program.Type.FRAGMENT, s);
         this.f_173299_ = ProgramManager.m_85577_();
         if (this.f_173304_ != null) {
            int l = 0;

            for(String s2 : p_173338_.m_166911_()) {
               Uniform.m_166710_(this.f_173299_, l, s2);
               this.f_173303_.add(l);
               ++l;
            }
         }

         ProgramManager.m_166623_(this);
         this.m_173366_();
      } catch (Exception exception3) {
         ChainedJsonException chainedjsonexception = ChainedJsonException.m_135906_(exception3);
         chainedjsonexception.m_135910_(resourcelocation.m_135815_());
         throw chainedjsonexception;
      }

      this.m_108957_();
      this.f_173308_ = this.m_173348_("ModelViewMat");
      this.f_173309_ = this.m_173348_("ProjMat");
      this.f_200956_ = this.m_173348_("IViewRotMat");
      this.f_173310_ = this.m_173348_("TextureMat");
      this.f_173311_ = this.m_173348_("ScreenSize");
      this.f_173312_ = this.m_173348_("ColorModulator");
      this.f_173313_ = this.m_173348_("Light0_Direction");
      this.f_173314_ = this.m_173348_("Light1_Direction");
      this.f_267422_ = this.m_173348_("GlintAlpha");
      this.f_173315_ = this.m_173348_("FogStart");
      this.f_173316_ = this.m_173348_("FogEnd");
      this.f_173317_ = this.m_173348_("FogColor");
      this.f_202432_ = this.m_173348_("FogShape");
      this.f_173318_ = this.m_173348_("LineWidth");
      this.f_173319_ = this.m_173348_("GameTime");
      this.f_173320_ = this.m_173348_("ChunkOffset");
   }

   private static Program m_173340_(final ResourceProvider p_173341_, Program.Type p_173342_, String p_173343_) throws IOException {
      Program program1 = p_173342_.m_85570_().get(p_173343_);
      Program program;
      if (program1 == null) {
         ResourceLocation loc = new ResourceLocation(p_173343_);
         String s = "shaders/core/" + loc.m_135815_() + p_173342_.m_85569_();
         ResourceLocation resourcelocation = new ResourceLocation(loc.m_135827_(), s);
         Resource resource = p_173341_.m_215593_(resourcelocation);

         try (InputStream inputstream = resource.m_215507_()) {
            final String s1 = FileUtil.m_179922_(s);
            program = Program.m_166604_(p_173342_, p_173343_, inputstream, resource.m_215506_(), new GlslPreprocessor() {
               private final Set<String> f_173369_ = Sets.newHashSet();

               public String m_142138_(boolean p_173374_, String p_173375_) {
                  // FORGE: use the mod's namespace to look up resources if specified
                  ResourceLocation resourcelocation = net.minecraftforge.client.ForgeHooksClient.getShaderImportLocation(s1, p_173374_, p_173375_);
                  if (!this.f_173369_.add(resourcelocation.toString())) {
                     return null;
                  } else {

                     try (Reader reader = p_173341_.m_215597_(resourcelocation)) {
                        return IOUtils.toString(reader);
                     } catch (IOException ioexception) {
                        // FORGE: specify the namespace of the failed import in case of duplicates from multiple mods
                        ShaderInstance.f_173323_.error("Could not open GLSL import {}: {}", resourcelocation, ioexception.getMessage());
                        return "#error " + ioexception.getMessage();
                     }
                  }
               }
            });
         }
      } else {
         program = program1;
      }

      return program;
   }

   public static BlendMode m_173346_(JsonObject p_173347_) {
      if (p_173347_ == null) {
         return new BlendMode();
      } else {
         int i = 32774;
         int j = 1;
         int k = 0;
         int l = 1;
         int i1 = 0;
         boolean flag = true;
         boolean flag1 = false;
         if (GsonHelper.m_13813_(p_173347_, "func")) {
            i = BlendMode.m_85527_(p_173347_.get("func").getAsString());
            if (i != 32774) {
               flag = false;
            }
         }

         if (GsonHelper.m_13813_(p_173347_, "srcrgb")) {
            j = BlendMode.m_85530_(p_173347_.get("srcrgb").getAsString());
            if (j != 1) {
               flag = false;
            }
         }

         if (GsonHelper.m_13813_(p_173347_, "dstrgb")) {
            k = BlendMode.m_85530_(p_173347_.get("dstrgb").getAsString());
            if (k != 0) {
               flag = false;
            }
         }

         if (GsonHelper.m_13813_(p_173347_, "srcalpha")) {
            l = BlendMode.m_85530_(p_173347_.get("srcalpha").getAsString());
            if (l != 1) {
               flag = false;
            }

            flag1 = true;
         }

         if (GsonHelper.m_13813_(p_173347_, "dstalpha")) {
            i1 = BlendMode.m_85530_(p_173347_.get("dstalpha").getAsString());
            if (i1 != 0) {
               flag = false;
            }

            flag1 = true;
         }

         if (flag) {
            return new BlendMode();
         } else {
            return flag1 ? new BlendMode(j, k, l, i1, i) : new BlendMode(j, k, i);
         }
      }
   }

   public void close() {
      for(Uniform uniform : this.f_173331_) {
         uniform.close();
      }

      ProgramManager.m_166621_(this);
   }

   public void m_173362_() {
      RenderSystem.assertOnRenderThread();
      ProgramManager.m_85578_(0);
      f_173327_ = -1;
      f_173326_ = null;
      int i = GlStateManager._getActiveTexture();

      for(int j = 0; j < this.f_173330_.size(); ++j) {
         if (this.f_173328_.get(this.f_173329_.get(j)) != null) {
            GlStateManager._activeTexture('\u84c0' + j);
            GlStateManager._bindTexture(0);
         }
      }

      GlStateManager._activeTexture(i);
   }

   public void m_173363_() {
      RenderSystem.assertOnRenderThread();
      this.f_173301_ = false;
      f_173326_ = this;
      this.f_173302_.m_85526_();
      if (this.f_173299_ != f_173327_) {
         ProgramManager.m_85578_(this.f_173299_);
         f_173327_ = this.f_173299_;
      }

      int i = GlStateManager._getActiveTexture();

      for(int j = 0; j < this.f_173330_.size(); ++j) {
         String s = this.f_173329_.get(j);
         if (this.f_173328_.get(s) != null) {
            int k = Uniform.m_85624_(this.f_173299_, s);
            Uniform.m_85616_(k, j);
            RenderSystem.activeTexture('\u84c0' + j);
            Object object = this.f_173328_.get(s);
            int l = -1;
            if (object instanceof RenderTarget) {
               l = ((RenderTarget)object).m_83975_();
            } else if (object instanceof AbstractTexture) {
               l = ((AbstractTexture)object).m_117963_();
            } else if (object instanceof Integer) {
               l = (Integer)object;
            }

            if (l != -1) {
               RenderSystem.bindTexture(l);
            }
         }
      }

      GlStateManager._activeTexture(i);

      for(Uniform uniform : this.f_173331_) {
         uniform.m_85633_();
      }

   }

   public void m_108957_() {
      this.f_173301_ = true;
   }

   @Nullable
   public Uniform m_173348_(String p_173349_) {
      RenderSystem.assertOnRenderThread();
      return this.f_173333_.get(p_173349_);
   }

   public AbstractUniform m_173356_(String p_173357_) {
      RenderSystem.assertOnGameThread();
      Uniform uniform = this.m_173348_(p_173357_);
      return (AbstractUniform)(uniform == null ? f_173324_ : uniform);
   }

   private void m_173366_() {
      RenderSystem.assertOnRenderThread();
      IntList intlist = new IntArrayList();

      for(int i = 0; i < this.f_173329_.size(); ++i) {
         String s = this.f_173329_.get(i);
         int j = Uniform.m_85624_(this.f_173299_, s);
         if (j == -1) {
            f_173323_.warn("Shader {} could not find sampler named {} in the specified shader program.", this.f_173300_, s);
            this.f_173328_.remove(s);
            intlist.add(i);
         } else {
            this.f_173330_.add(j);
         }
      }

      for(int l = intlist.size() - 1; l >= 0; --l) {
         int i1 = intlist.getInt(l);
         this.f_173329_.remove(i1);
      }

      for(Uniform uniform : this.f_173331_) {
         String s1 = uniform.m_85599_();
         int k = Uniform.m_85624_(this.f_173299_, s1);
         if (k == -1) {
            f_173323_.warn("Shader {} could not find uniform named {} in the specified shader program.", this.f_173300_, s1);
         } else {
            this.f_173332_.add(k);
            uniform.m_85614_(k);
            this.f_173333_.put(s1, uniform);
         }
      }

   }

   private void m_173344_(JsonElement p_173345_) {
      JsonObject jsonobject = GsonHelper.m_13918_(p_173345_, "sampler");
      String s = GsonHelper.m_13906_(jsonobject, "name");
      if (!GsonHelper.m_13813_(jsonobject, "file")) {
         this.f_173328_.put(s, (Object)null);
         this.f_173329_.add(s);
      } else {
         this.f_173329_.add(s);
      }
   }

   public void m_173350_(String p_173351_, Object p_173352_) {
      this.f_173328_.put(p_173351_, p_173352_);
      this.m_108957_();
   }

   private void m_173354_(JsonElement p_173355_) throws ChainedJsonException {
      JsonObject jsonobject = GsonHelper.m_13918_(p_173355_, "uniform");
      String s = GsonHelper.m_13906_(jsonobject, "name");
      int i = Uniform.m_85629_(GsonHelper.m_13906_(jsonobject, "type"));
      int j = GsonHelper.m_13927_(jsonobject, "count");
      float[] afloat = new float[Math.max(j, 16)];
      JsonArray jsonarray = GsonHelper.m_13933_(jsonobject, "values");
      if (jsonarray.size() != j && jsonarray.size() > 1) {
         throw new ChainedJsonException("Invalid amount of values specified (expected " + j + ", found " + jsonarray.size() + ")");
      } else {
         int k = 0;

         for(JsonElement jsonelement : jsonarray) {
            try {
               afloat[k] = GsonHelper.m_13888_(jsonelement, "value");
            } catch (Exception exception) {
               ChainedJsonException chainedjsonexception = ChainedJsonException.m_135906_(exception);
               chainedjsonexception.m_135908_("values[" + k + "]");
               throw chainedjsonexception;
            }

            ++k;
         }

         if (j > 1 && jsonarray.size() == 1) {
            while(k < j) {
               afloat[k] = afloat[0];
               ++k;
            }
         }

         int l = j > 1 && j <= 4 && i < 8 ? j - 1 : 0;
         Uniform uniform = new Uniform(s, i + l, j, this);
         if (i <= 3) {
            uniform.m_7401_((int)afloat[0], (int)afloat[1], (int)afloat[2], (int)afloat[3]);
         } else if (i <= 7) {
            uniform.m_5808_(afloat[0], afloat[1], afloat[2], afloat[3]);
         } else {
            uniform.m_5941_(Arrays.copyOfRange(afloat, 0, j));
         }

         this.f_173331_.add(uniform);
      }
   }

   public Program m_108962_() {
      return this.f_173305_;
   }

   public Program m_108964_() {
      return this.f_173306_;
   }

   public void m_142662_() {
      this.f_173306_.m_166610_(this);
      this.f_173305_.m_166610_(this);
   }

   public VertexFormat m_173364_() {
      return this.f_173307_;
   }

   public String m_173365_() {
      return this.f_173300_;
   }

   public int m_108943_() {
      return this.f_173299_;
   }
}
