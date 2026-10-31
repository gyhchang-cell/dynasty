package net.minecraft.client.renderer;

import com.google.common.collect.Lists;
import com.google.common.collect.Maps;
import com.google.gson.JsonSyntaxException;
import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.platform.Lighting;
import com.mojang.blaze3d.platform.NativeImage;
import com.mojang.blaze3d.platform.Window;
import com.mojang.blaze3d.shaders.Program;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.mojang.blaze3d.vertex.VertexSorting;
import com.mojang.datafixers.util.Pair;
import com.mojang.logging.LogUtils;
import com.mojang.math.Axis;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.function.Consumer;
import javax.annotation.Nullable;
import net.minecraft.CrashReport;
import net.minecraft.CrashReportCategory;
import net.minecraft.ReportedException;
import net.minecraft.Util;
import net.minecraft.client.Camera;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.MapRenderer;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.server.IntegratedServer;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.PreparableReloadListener;
import net.minecraft.server.packs.resources.Resource;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.ResourceProvider;
import net.minecraft.server.packs.resources.SimplePreparableReloadListener;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.decoration.ItemFrame;
import net.minecraft.world.entity.monster.Creeper;
import net.minecraft.world.entity.monster.EnderMan;
import net.minecraft.world.entity.monster.Spider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.ProjectileUtil;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.pattern.BlockInWorld;
import net.minecraft.world.level.material.FogType;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import org.slf4j.Logger;

@OnlyIn(Dist.CLIENT)
public class GameRenderer implements AutoCloseable {
   private static final ResourceLocation f_109057_ = new ResourceLocation("textures/misc/nausea.png");
   static final Logger f_109058_ = LogUtils.getLogger();
   private static final boolean f_172636_ = false;
   public static final float f_172592_ = 0.05F;
   private static final float f_289032_ = 1000.0F;
   final Minecraft f_109059_;
   private final ResourceManager f_109060_;
   private final RandomSource f_109061_ = RandomSource.m_216327_();
   private float f_109062_;
   public final ItemInHandRenderer f_109055_;
   private final MapRenderer f_109063_;
   private final RenderBuffers f_109064_;
   private int f_109065_;
   private float f_109066_;
   private float f_109067_;
   private float f_109068_;
   private float f_109069_;
   private boolean f_109070_ = true;
   private boolean f_109071_ = true;
   private long f_109072_;
   private boolean f_182638_;
   private long f_109073_ = Util.m_137550_();
   private final LightTexture f_109074_;
   private final OverlayTexture f_109075_ = new OverlayTexture();
   private boolean f_109076_;
   private float f_109077_ = 1.0F;
   private float f_109078_;
   private float f_109079_;
   public static final int f_172634_ = 40;
   @Nullable
   private ItemStack f_109080_;
   private int f_109047_;
   private float f_109048_;
   private float f_109049_;
   @Nullable
   PostChain f_109050_;
   static final ResourceLocation[] f_109051_ = new ResourceLocation[]{new ResourceLocation("shaders/post/notch.json"), new ResourceLocation("shaders/post/fxaa.json"), new ResourceLocation("shaders/post/art.json"), new ResourceLocation("shaders/post/bumpy.json"), new ResourceLocation("shaders/post/blobs2.json"), new ResourceLocation("shaders/post/pencil.json"), new ResourceLocation("shaders/post/color_convolve.json"), new ResourceLocation("shaders/post/deconverge.json"), new ResourceLocation("shaders/post/flip.json"), new ResourceLocation("shaders/post/invert.json"), new ResourceLocation("shaders/post/ntsc.json"), new ResourceLocation("shaders/post/outline.json"), new ResourceLocation("shaders/post/phosphor.json"), new ResourceLocation("shaders/post/scan_pincushion.json"), new ResourceLocation("shaders/post/sobel.json"), new ResourceLocation("shaders/post/bits.json"), new ResourceLocation("shaders/post/desaturate.json"), new ResourceLocation("shaders/post/green.json"), new ResourceLocation("shaders/post/blur.json"), new ResourceLocation("shaders/post/wobble.json"), new ResourceLocation("shaders/post/blobs.json"), new ResourceLocation("shaders/post/antialias.json"), new ResourceLocation("shaders/post/creeper.json"), new ResourceLocation("shaders/post/spider.json")};
   public static final int f_109056_ = f_109051_.length;
   int f_109052_ = f_109056_;
   private boolean f_109053_;
   private final Camera f_109054_ = new Camera();
   public ShaderInstance f_172635_;
   private final Map<String, ShaderInstance> f_172578_ = Maps.newHashMap();
   @Nullable
   private static ShaderInstance f_172579_;
   @Nullable
   private static ShaderInstance f_172580_;
   @Nullable
   private static ShaderInstance f_172581_;
   @Nullable
   private static ShaderInstance f_172582_;
   @Nullable
   private static ShaderInstance f_172583_;
   @Nullable
   private static ShaderInstance f_172586_;
   @Nullable
   private static ShaderInstance f_172587_;
   @Nullable
   private static ShaderInstance f_172588_;
   @Nullable
   private static ShaderInstance f_172589_;
   @Nullable
   private static ShaderInstance f_172590_;
   @Nullable
   private static ShaderInstance f_172591_;
   @Nullable
   private static ShaderInstance f_172608_;
   @Nullable
   private static ShaderInstance f_172609_;
   @Nullable
   private static ShaderInstance f_172610_;
   @Nullable
   private static ShaderInstance f_172611_;
   @Nullable
   private static ShaderInstance f_172612_;
   @Nullable
   private static ShaderInstance f_172613_;
   @Nullable
   private static ShaderInstance f_172614_;
   @Nullable
   private static ShaderInstance f_172615_;
   @Nullable
   private static ShaderInstance f_172616_;
   @Nullable
   private static ShaderInstance f_172617_;
   @Nullable
   private static ShaderInstance f_172618_;
   @Nullable
   private static ShaderInstance f_172619_;
   @Nullable
   private static ShaderInstance f_172620_;
   @Nullable
   private static ShaderInstance f_234217_;
   @Nullable
   private static ShaderInstance f_172621_;
   @Nullable
   private static ShaderInstance f_172622_;
   @Nullable
   private static ShaderInstance f_172623_;
   @Nullable
   private static ShaderInstance f_172624_;
   @Nullable
   private static ShaderInstance f_172625_;
   @Nullable
   private static ShaderInstance f_172626_;
   @Nullable
   private static ShaderInstance f_172627_;
   @Nullable
   private static ShaderInstance f_172628_;
   @Nullable
   private static ShaderInstance f_172629_;
   @Nullable
   private static ShaderInstance f_172630_;
   @Nullable
   private static ShaderInstance f_172631_;
   @Nullable
   private static ShaderInstance f_172632_;
   @Nullable
   private static ShaderInstance f_172633_;
   @Nullable
   private static ShaderInstance f_172593_;
   @Nullable
   private static ShaderInstance f_172594_;
   @Nullable
   private static ShaderInstance f_172595_;
   @Nullable
   private static ShaderInstance f_172596_;
   @Nullable
   private static ShaderInstance f_172597_;
   @Nullable
   private static ShaderInstance f_172598_;
   @Nullable
   private static ShaderInstance f_268423_;
   @Nullable
   private static ShaderInstance f_172599_;
   @Nullable
   private static ShaderInstance f_172600_;
   @Nullable
   private static ShaderInstance f_268525_;
   @Nullable
   private static ShaderInstance f_172601_;
   @Nullable
   private static ShaderInstance f_172602_;
   @Nullable
   private static ShaderInstance f_172603_;
   @Nullable
   private static ShaderInstance f_172604_;
   @Nullable
   private static ShaderInstance f_172605_;
   @Nullable
   private static ShaderInstance f_172606_;
   @Nullable
   private static ShaderInstance f_172607_;
   @Nullable
   private static ShaderInstance f_285653_;
   @Nullable
   private static ShaderInstance f_285598_;
   @Nullable
   private static ShaderInstance f_285623_;
   @Nullable
   private static ShaderInstance f_285569_;

   public GameRenderer(Minecraft p_234219_, ItemInHandRenderer p_234220_, ResourceManager p_234221_, RenderBuffers p_234222_) {
      this.f_109059_ = p_234219_;
      this.f_109060_ = p_234221_;
      this.f_109055_ = p_234220_;
      this.f_109063_ = new MapRenderer(p_234219_.m_91097_());
      this.f_109074_ = new LightTexture(this, p_234219_);
      this.f_109064_ = p_234222_;
      this.f_109050_ = null;
   }

   public void close() {
      this.f_109074_.close();
      this.f_109063_.close();
      this.f_109075_.close();
      this.m_109086_();
      this.m_172759_();
      if (this.f_172635_ != null) {
         this.f_172635_.close();
      }

   }

   public void m_172736_(boolean p_172737_) {
      this.f_109070_ = p_172737_;
   }

   public void m_172775_(boolean p_172776_) {
      this.f_109071_ = p_172776_;
   }

   public void m_172779_(boolean p_172780_) {
      this.f_109076_ = p_172780_;
   }

   public boolean m_172715_() {
      return this.f_109076_;
   }

   public void m_109086_() {
      if (this.f_109050_ != null) {
         this.f_109050_.close();
      }

      this.f_109050_ = null;
      this.f_109052_ = f_109056_;
   }

   public void m_109130_() {
      this.f_109053_ = !this.f_109053_;
   }

   public void m_109106_(@Nullable Entity p_109107_) {
      if (this.f_109050_ != null) {
         this.f_109050_.close();
      }

      this.f_109050_ = null;
      if (p_109107_ instanceof Creeper) {
         this.m_109128_(new ResourceLocation("shaders/post/creeper.json"));
      } else if (p_109107_ instanceof Spider) {
         this.m_109128_(new ResourceLocation("shaders/post/spider.json"));
         this.m_109128_(new ResourceLocation("shaders/post/spider.json"));
      } else if (p_109107_ instanceof EnderMan) {
         this.m_109128_(new ResourceLocation("shaders/post/invert.json"));
      } else {
         net.minecraftforge.client.ForgeHooksClient.loadEntityShader(p_109107_, this);
      }

   }

   public void m_172783_() {
      if (this.f_109059_.m_91288_() instanceof Player) {
         if (this.f_109050_ != null) {
            this.f_109050_.close();
         }

         this.f_109052_ = (this.f_109052_ + 1) % (f_109051_.length + 1);
         if (this.f_109052_ == f_109056_) {
            this.f_109050_ = null;
         } else {
            this.m_109128_(f_109051_[this.f_109052_]);
         }

      }
   }

   public void m_109128_(ResourceLocation p_109129_) {
      if (this.f_109050_ != null) {
         this.f_109050_.close();
      }

      try {
         this.f_109050_ = new PostChain(this.f_109059_.m_91097_(), this.f_109060_, this.f_109059_.m_91385_(), p_109129_);
         this.f_109050_.m_110025_(this.f_109059_.m_91268_().m_85441_(), this.f_109059_.m_91268_().m_85442_());
         this.f_109053_ = true;
      } catch (IOException ioexception) {
         f_109058_.warn("Failed to load shader: {}", p_109129_, ioexception);
         this.f_109052_ = f_109056_;
         this.f_109053_ = false;
      } catch (JsonSyntaxException jsonsyntaxexception) {
         f_109058_.warn("Failed to parse shader: {}", p_109129_, jsonsyntaxexception);
         this.f_109052_ = f_109056_;
         this.f_109053_ = false;
      }

   }

   public PreparableReloadListener m_247116_() {
      return new SimplePreparableReloadListener<GameRenderer.ResourceCache>() {
         protected GameRenderer.ResourceCache m_5944_(ResourceManager p_251213_, ProfilerFiller p_251006_) {
            Map<ResourceLocation, Resource> map = p_251213_.m_214159_("shaders", (p_251575_) -> {
               String s = p_251575_.m_135815_();
               return s.endsWith(".json") || s.endsWith(Program.Type.FRAGMENT.m_85569_()) || s.endsWith(Program.Type.VERTEX.m_85569_()) || s.endsWith(".glsl");
            });
            Map<ResourceLocation, Resource> map1 = new HashMap<>();
            map.forEach((p_250354_, p_250712_) -> {
               try (InputStream inputstream = p_250712_.m_215507_()) {
                  byte[] abyte = inputstream.readAllBytes();
                  map1.put(p_250354_, new Resource(p_250712_.m_247173_(), () -> {
                     return new ByteArrayInputStream(abyte);
                  }));
               } catch (Exception exception) {
                  GameRenderer.f_109058_.warn("Failed to read resource {}", p_250354_, exception);
               }

            });
            return new GameRenderer.ResourceCache(p_251213_, map1);
         }

         protected void m_5787_(GameRenderer.ResourceCache p_251168_, ResourceManager p_248902_, ProfilerFiller p_251909_) {
            GameRenderer.this.m_172767_(p_251168_);
            if (GameRenderer.this.f_109050_ != null) {
               GameRenderer.this.f_109050_.close();
            }

            GameRenderer.this.f_109050_ = null;
            if (GameRenderer.this.f_109052_ == GameRenderer.f_109056_) {
               GameRenderer.this.m_109106_(GameRenderer.this.f_109059_.m_91288_());
            } else {
               GameRenderer.this.m_109128_(GameRenderer.f_109051_[GameRenderer.this.f_109052_]);
            }

         }

         public String m_7812_() {
            return "Shader Loader";
         }
      };
   }

   public void m_172722_(ResourceProvider p_172723_) {
      if (this.f_172635_ != null) {
         throw new RuntimeException("Blit shader already preloaded");
      } else {
         try {
            this.f_172635_ = new ShaderInstance(p_172723_, "blit_screen", DefaultVertexFormat.f_166850_);
         } catch (IOException ioexception) {
            throw new RuntimeException("could not preload blit shader", ioexception);
         }

         f_285653_ = this.m_172724_(p_172723_, "rendertype_gui", DefaultVertexFormat.f_85815_);
         f_285598_ = this.m_172724_(p_172723_, "rendertype_gui_overlay", DefaultVertexFormat.f_85815_);
         f_172579_ = this.m_172724_(p_172723_, "position", DefaultVertexFormat.f_85814_);
         f_172580_ = this.m_172724_(p_172723_, "position_color", DefaultVertexFormat.f_85815_);
         f_172581_ = this.m_172724_(p_172723_, "position_color_tex", DefaultVertexFormat.f_85818_);
         f_172582_ = this.m_172724_(p_172723_, "position_tex", DefaultVertexFormat.f_85817_);
         f_172583_ = this.m_172724_(p_172723_, "position_tex_color", DefaultVertexFormat.f_85819_);
         f_172598_ = this.m_172724_(p_172723_, "rendertype_text", DefaultVertexFormat.f_85820_);
      }
   }

   private ShaderInstance m_172724_(ResourceProvider p_172725_, String p_172726_, VertexFormat p_172727_) {
      try {
         ShaderInstance shaderinstance = new ShaderInstance(p_172725_, p_172726_, p_172727_);
         this.f_172578_.put(p_172726_, shaderinstance);
         return shaderinstance;
      } catch (Exception exception) {
         throw new IllegalStateException("could not preload shader " + p_172726_, exception);
      }
   }

   void m_172767_(ResourceProvider p_250719_) {
      RenderSystem.assertOnRenderThread();
      List<Program> list = Lists.newArrayList();
      list.addAll(Program.Type.FRAGMENT.m_85570_().values());
      list.addAll(Program.Type.VERTEX.m_85570_().values());
      list.forEach(Program::m_85543_);
      List<Pair<ShaderInstance, Consumer<ShaderInstance>>> list1 = Lists.newArrayListWithCapacity(this.f_172578_.size());

      try {
         list1.add(Pair.of(new ShaderInstance(p_250719_, "particle", DefaultVertexFormat.f_85813_), (p_172714_) -> {
            f_172586_ = p_172714_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "position", DefaultVertexFormat.f_85814_), (p_172711_) -> {
            f_172579_ = p_172711_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "position_color", DefaultVertexFormat.f_85815_), (p_172708_) -> {
            f_172580_ = p_172708_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "position_color_lightmap", DefaultVertexFormat.f_85816_), (p_172705_) -> {
            f_172587_ = p_172705_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "position_color_tex", DefaultVertexFormat.f_85818_), (p_172702_) -> {
            f_172581_ = p_172702_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "position_color_tex_lightmap", DefaultVertexFormat.f_85820_), (p_172699_) -> {
            f_172588_ = p_172699_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "position_tex", DefaultVertexFormat.f_85817_), (p_172696_) -> {
            f_172582_ = p_172696_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "position_tex_color", DefaultVertexFormat.f_85819_), (p_172693_) -> {
            f_172583_ = p_172693_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "position_tex_color_normal", DefaultVertexFormat.f_85822_), (p_172690_) -> {
            f_172589_ = p_172690_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "position_tex_lightmap_color", DefaultVertexFormat.f_85821_), (p_172687_) -> {
            f_172590_ = p_172687_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_solid", DefaultVertexFormat.f_85811_), (p_172684_) -> {
            f_172591_ = p_172684_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_cutout_mipped", DefaultVertexFormat.f_85811_), (p_172681_) -> {
            f_172608_ = p_172681_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_cutout", DefaultVertexFormat.f_85811_), (p_172678_) -> {
            f_172609_ = p_172678_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_translucent", DefaultVertexFormat.f_85811_), (p_172675_) -> {
            f_172610_ = p_172675_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_translucent_moving_block", DefaultVertexFormat.f_85811_), (p_172672_) -> {
            f_172611_ = p_172672_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_translucent_no_crumbling", DefaultVertexFormat.f_85811_), (p_172669_) -> {
            f_172612_ = p_172669_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_armor_cutout_no_cull", DefaultVertexFormat.f_85812_), (p_172666_) -> {
            f_172613_ = p_172666_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_entity_solid", DefaultVertexFormat.f_85812_), (p_172663_) -> {
            f_172614_ = p_172663_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_entity_cutout", DefaultVertexFormat.f_85812_), (p_172660_) -> {
            f_172615_ = p_172660_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_entity_cutout_no_cull", DefaultVertexFormat.f_85812_), (p_172657_) -> {
            f_172616_ = p_172657_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_entity_cutout_no_cull_z_offset", DefaultVertexFormat.f_85812_), (p_172654_) -> {
            f_172617_ = p_172654_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_item_entity_translucent_cull", DefaultVertexFormat.f_85812_), (p_172651_) -> {
            f_172618_ = p_172651_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_entity_translucent_cull", DefaultVertexFormat.f_85812_), (p_172648_) -> {
            f_172619_ = p_172648_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_entity_translucent", DefaultVertexFormat.f_85812_), (p_172645_) -> {
            f_172620_ = p_172645_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_entity_translucent_emissive", DefaultVertexFormat.f_85812_), (p_172642_) -> {
            f_234217_ = p_172642_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_entity_smooth_cutout", DefaultVertexFormat.f_85812_), (p_172639_) -> {
            f_172621_ = p_172639_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_beacon_beam", DefaultVertexFormat.f_85811_), (p_172840_) -> {
            f_172622_ = p_172840_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_entity_decal", DefaultVertexFormat.f_85812_), (p_172837_) -> {
            f_172623_ = p_172837_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_entity_no_outline", DefaultVertexFormat.f_85812_), (p_172834_) -> {
            f_172624_ = p_172834_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_entity_shadow", DefaultVertexFormat.f_85812_), (p_172831_) -> {
            f_172625_ = p_172831_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_entity_alpha", DefaultVertexFormat.f_85812_), (p_172828_) -> {
            f_172626_ = p_172828_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_eyes", DefaultVertexFormat.f_85812_), (p_172825_) -> {
            f_172627_ = p_172825_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_energy_swirl", DefaultVertexFormat.f_85812_), (p_172822_) -> {
            f_172628_ = p_172822_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_leash", DefaultVertexFormat.f_85816_), (p_172819_) -> {
            f_172629_ = p_172819_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_water_mask", DefaultVertexFormat.f_85814_), (p_172816_) -> {
            f_172630_ = p_172816_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_outline", DefaultVertexFormat.f_85818_), (p_172813_) -> {
            f_172631_ = p_172813_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_armor_glint", DefaultVertexFormat.f_85817_), (p_172810_) -> {
            f_172632_ = p_172810_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_armor_entity_glint", DefaultVertexFormat.f_85817_), (p_172807_) -> {
            f_172633_ = p_172807_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_glint_translucent", DefaultVertexFormat.f_85817_), (p_172805_) -> {
            f_172593_ = p_172805_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_glint", DefaultVertexFormat.f_85817_), (p_172803_) -> {
            f_172594_ = p_172803_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_glint_direct", DefaultVertexFormat.f_85817_), (p_172801_) -> {
            f_172595_ = p_172801_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_entity_glint", DefaultVertexFormat.f_85817_), (p_172799_) -> {
            f_172596_ = p_172799_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_entity_glint_direct", DefaultVertexFormat.f_85817_), (p_172796_) -> {
            f_172597_ = p_172796_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_text", DefaultVertexFormat.f_85820_), (p_172794_) -> {
            f_172598_ = p_172794_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_text_background", DefaultVertexFormat.f_85816_), (p_269657_) -> {
            f_268423_ = p_269657_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_text_intensity", DefaultVertexFormat.f_85820_), (p_172792_) -> {
            f_172599_ = p_172792_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_text_see_through", DefaultVertexFormat.f_85820_), (p_172789_) -> {
            f_172600_ = p_172789_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_text_background_see_through", DefaultVertexFormat.f_85816_), (p_269656_) -> {
            f_268525_ = p_269656_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_text_intensity_see_through", DefaultVertexFormat.f_85820_), (p_172787_) -> {
            f_172601_ = p_172787_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_lightning", DefaultVertexFormat.f_85815_), (p_172785_) -> {
            f_172602_ = p_172785_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_tripwire", DefaultVertexFormat.f_85811_), (p_172782_) -> {
            f_172603_ = p_172782_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_end_portal", DefaultVertexFormat.f_85814_), (p_172778_) -> {
            f_172604_ = p_172778_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_end_gateway", DefaultVertexFormat.f_85814_), (p_172774_) -> {
            f_172605_ = p_172774_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_lines", DefaultVertexFormat.f_166851_), (p_172733_) -> {
            f_172606_ = p_172733_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_crumbling", DefaultVertexFormat.f_85811_), (p_234230_) -> {
            f_172607_ = p_234230_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_gui", DefaultVertexFormat.f_85815_), (p_286148_) -> {
            f_285653_ = p_286148_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_gui_overlay", DefaultVertexFormat.f_85815_), (p_286146_) -> {
            f_285598_ = p_286146_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_gui_text_highlight", DefaultVertexFormat.f_85815_), (p_286145_) -> {
            f_285623_ = p_286145_;
         }));
         list1.add(Pair.of(new ShaderInstance(p_250719_, "rendertype_gui_ghost_recipe_overlay", DefaultVertexFormat.f_85815_), (p_286147_) -> {
            f_285569_ = p_286147_;
         }));
         net.minecraftforge.fml.ModLoader.get().postEvent(new net.minecraftforge.client.event.RegisterShadersEvent(p_250719_, list1));
      } catch (IOException ioexception) {
         list1.forEach((p_172729_) -> {
            p_172729_.getFirst().close();
         });
         throw new RuntimeException("could not reload shaders", ioexception);
      }

      this.m_172759_();
      list1.forEach((p_234225_) -> {
         ShaderInstance shaderinstance = p_234225_.getFirst();
         this.f_172578_.put(shaderinstance.m_173365_(), shaderinstance);
         p_234225_.getSecond().accept(shaderinstance);
      });
   }

   private void m_172759_() {
      RenderSystem.assertOnRenderThread();
      this.f_172578_.values().forEach(ShaderInstance::close);
      this.f_172578_.clear();
   }

   @Nullable
   public ShaderInstance m_172734_(@Nullable String p_172735_) {
      return p_172735_ == null ? null : this.f_172578_.get(p_172735_);
   }

   public void m_109148_() {
      this.m_109156_();
      this.f_109074_.m_109880_();
      if (this.f_109059_.m_91288_() == null) {
         this.f_109059_.m_91118_(this.f_109059_.f_91074_);
      }

      this.f_109054_.m_90565_();
      ++this.f_109065_;
      this.f_109055_.m_109311_();
      this.f_109059_.f_91060_.m_109693_(this.f_109054_);
      this.f_109069_ = this.f_109068_;
      if (this.f_109059_.f_91065_.m_93090_().m_93714_()) {
         this.f_109068_ += 0.05F;
         if (this.f_109068_ > 1.0F) {
            this.f_109068_ = 1.0F;
         }
      } else if (this.f_109068_ > 0.0F) {
         this.f_109068_ -= 0.0125F;
      }

      if (this.f_109047_ > 0) {
         --this.f_109047_;
         if (this.f_109047_ == 0) {
            this.f_109080_ = null;
         }
      }

   }

   @Nullable
   public PostChain m_109149_() {
      return this.f_109050_;
   }

   public void m_109097_(int p_109098_, int p_109099_) {
      if (this.f_109050_ != null) {
         this.f_109050_.m_110025_(p_109098_, p_109099_);
      }

      this.f_109059_.f_91060_.m_109487_(p_109098_, p_109099_);
   }

   public void m_109087_(float p_109088_) {
      Entity entity = this.f_109059_.m_91288_();
      if (entity != null) {
         if (this.f_109059_.f_91073_ != null) {
            this.f_109059_.m_91307_().m_6180_("pick");
            this.f_109059_.f_91076_ = null;
            double d0 = (double)this.f_109059_.f_91072_.m_105286_();
            double entityReach = this.f_109059_.f_91074_.getEntityReach(); // Note - MC-76493 - We must validate players cannot click-through objects.
            this.f_109059_.f_91077_ = entity.m_19907_(Math.max(d0, entityReach), p_109088_, false); // Run pick() with the max of the two, so we can prevent click-through.
            Vec3 vec3 = entity.m_20299_(p_109088_);
            boolean flag = false;
            int i = 3;
            double d1 = d0;
            if (false && this.f_109059_.f_91072_.m_105291_()) {
               d1 = 6.0D;
               d0 = d1;
            } else {
               if (d0 > 3.0D) {
                  flag = true;
               }

               d0 = d0;
            }
            d0 = d1 = Math.max(d0, entityReach); // Pick entities with the max of both for the same reason.

            d1 *= d1;
            // If we picked a block, we need to ignore entities past that block. Added != MISS check to not truncate on failed picks.
            // Also fixes MC-250858
            if (this.f_109059_.f_91077_ != null && this.f_109059_.f_91077_.m_6662_() != HitResult.Type.MISS) {
               d1 = this.f_109059_.f_91077_.m_82450_().m_82557_(vec3);
               double blockReach = this.f_109059_.f_91074_.getBlockReach();
               // Discard the result as a miss if it is outside the block reach.
               if (d1 > blockReach * blockReach) {
                  Vec3 pos = this.f_109059_.f_91077_.m_82450_();
                  this.f_109059_.f_91077_ = BlockHitResult.m_82426_(pos, Direction.m_122366_(vec3.f_82479_, vec3.f_82480_, vec3.f_82481_), BlockPos.m_274446_(pos));
               }
            }

            Vec3 vec31 = entity.m_20252_(1.0F);
            Vec3 vec32 = vec3.m_82520_(vec31.f_82479_ * d0, vec31.f_82480_ * d0, vec31.f_82481_ * d0);
            float f = 1.0F;
            AABB aabb = entity.m_20191_().m_82369_(vec31.m_82490_(d0)).m_82377_(1.0D, 1.0D, 1.0D);
            EntityHitResult entityhitresult = ProjectileUtil.m_37287_(entity, vec3, vec32, aabb, (p_234237_) -> {
               return !p_234237_.m_5833_() && p_234237_.m_6087_();
            }, d1);
            if (entityhitresult != null) {
               Entity entity1 = entityhitresult.m_82443_();
               Vec3 vec33 = entityhitresult.m_82450_();
               double d2 = vec3.m_82557_(vec33);
               if (d2 > d1 || d2 > entityReach * entityReach) { // Discard if the result is behind a block, or past the entity reach max. The var "flag" no longer has a use.
                  this.f_109059_.f_91077_ = BlockHitResult.m_82426_(vec33, Direction.m_122366_(vec31.f_82479_, vec31.f_82480_, vec31.f_82481_), BlockPos.m_274446_(vec33));
               } else if (d2 < d1 || this.f_109059_.f_91077_ == null) {
                  this.f_109059_.f_91077_ = entityhitresult;
                  if (entity1 instanceof LivingEntity || entity1 instanceof ItemFrame) {
                     this.f_109059_.f_91076_ = entity1;
                  }
               }
            }

            this.f_109059_.m_91307_().m_7238_();
         }
      }
   }

   private void m_109156_() {
      float f = 1.0F;
      if (this.f_109059_.m_91288_() instanceof AbstractClientPlayer) {
         AbstractClientPlayer abstractclientplayer = (AbstractClientPlayer)this.f_109059_.m_91288_();
         f = abstractclientplayer.m_108565_();
      }

      this.f_109067_ = this.f_109066_;
      this.f_109066_ += (f - this.f_109066_) * 0.5F;
      if (this.f_109066_ > 1.5F) {
         this.f_109066_ = 1.5F;
      }

      if (this.f_109066_ < 0.1F) {
         this.f_109066_ = 0.1F;
      }

   }

   private double m_109141_(Camera p_109142_, float p_109143_, boolean p_109144_) {
      if (this.f_109076_) {
         return 90.0D;
      } else {
         double d0 = 70.0D;
         if (p_109144_) {
            d0 = (double)this.f_109059_.f_91066_.m_231837_().m_231551_().intValue();
            d0 *= (double)Mth.m_14179_(p_109143_, this.f_109067_, this.f_109066_);
         }

         if (p_109142_.m_90592_() instanceof LivingEntity && ((LivingEntity)p_109142_.m_90592_()).m_21224_()) {
            float f = Math.min((float)((LivingEntity)p_109142_.m_90592_()).f_20919_ + p_109143_, 20.0F);
            d0 /= (double)((1.0F - 500.0F / (f + 500.0F)) * 2.0F + 1.0F);
         }

         FogType fogtype = p_109142_.m_167685_();
         if (fogtype == FogType.LAVA || fogtype == FogType.WATER) {
            d0 *= Mth.m_14139_(this.f_109059_.f_91066_.m_231925_().m_231551_(), 1.0D, (double)0.85714287F);
         }

         return net.minecraftforge.client.ForgeHooksClient.getFieldOfView(this, p_109142_, p_109143_, d0, p_109144_);
      }
   }

   private void m_109117_(PoseStack p_109118_, float p_109119_) {
      if (this.f_109059_.m_91288_() instanceof LivingEntity) {
         LivingEntity livingentity = (LivingEntity)this.f_109059_.m_91288_();
         float f = (float)livingentity.f_20916_ - p_109119_;
         if (livingentity.m_21224_()) {
            float f1 = Math.min((float)livingentity.f_20919_ + p_109119_, 20.0F);
            p_109118_.m_252781_(Axis.f_252403_.m_252977_(40.0F - 8000.0F / (f1 + 200.0F)));
         }

         if (f < 0.0F) {
            return;
         }

         f /= (float)livingentity.f_20917_;
         f = Mth.m_14031_(f * f * f * f * (float)Math.PI);
         float f3 = livingentity.m_264297_();
         p_109118_.m_252781_(Axis.f_252436_.m_252977_(-f3));
         float f2 = (float)((double)(-f) * 14.0D * this.f_109059_.f_91066_.m_269326_().m_231551_());
         p_109118_.m_252781_(Axis.f_252403_.m_252977_(f2));
         p_109118_.m_252781_(Axis.f_252436_.m_252977_(f3));
      }

   }

   private void m_109138_(PoseStack p_109139_, float p_109140_) {
      if (this.f_109059_.m_91288_() instanceof Player) {
         Player player = (Player)this.f_109059_.m_91288_();
         float f = player.f_19787_ - player.f_19867_;
         float f1 = -(player.f_19787_ + f * p_109140_);
         float f2 = Mth.m_14179_(p_109140_, player.f_36099_, player.f_36100_);
         p_109139_.m_252880_(Mth.m_14031_(f1 * (float)Math.PI) * f2 * 0.5F, -Math.abs(Mth.m_14089_(f1 * (float)Math.PI) * f2), 0.0F);
         p_109139_.m_252781_(Axis.f_252403_.m_252977_(Mth.m_14031_(f1 * (float)Math.PI) * f2 * 3.0F));
         p_109139_.m_252781_(Axis.f_252529_.m_252977_(Math.abs(Mth.m_14089_(f1 * (float)Math.PI - 0.2F) * f2) * 5.0F));
      }
   }

   public void m_172718_(float p_172719_, float p_172720_, float p_172721_) {
      this.f_109077_ = p_172719_;
      this.f_109078_ = p_172720_;
      this.f_109079_ = p_172721_;
      this.m_172775_(false);
      this.m_172736_(false);
      this.m_109089_(1.0F, 0L, new PoseStack());
      this.f_109077_ = 1.0F;
   }

   private void m_109120_(PoseStack p_109121_, Camera p_109122_, float p_109123_) {
      if (!this.f_109076_) {
         this.m_252879_(this.m_253088_(this.m_109141_(p_109122_, p_109123_, false)));
         p_109121_.m_166856_();
         p_109121_.m_85836_();
         this.m_109117_(p_109121_, p_109123_);
         if (this.f_109059_.f_91066_.m_231830_().m_231551_()) {
            this.m_109138_(p_109121_, p_109123_);
         }

         boolean flag = this.f_109059_.m_91288_() instanceof LivingEntity && ((LivingEntity)this.f_109059_.m_91288_()).m_5803_();
         if (this.f_109059_.f_91066_.m_92176_().m_90612_() && !flag && !this.f_109059_.f_91066_.f_92062_ && this.f_109059_.f_91072_.m_105295_() != GameType.SPECTATOR) {
            this.f_109074_.m_109896_();
            this.f_109055_.m_109314_(p_109123_, p_109121_, this.f_109064_.m_110104_(), this.f_109059_.f_91074_, this.f_109059_.m_91290_().m_114394_(this.f_109059_.f_91074_, p_109123_));
            this.f_109074_.m_109891_();
         }

         p_109121_.m_85849_();
         if (this.f_109059_.f_91066_.m_92176_().m_90612_() && !flag) {
            ScreenEffectRenderer.m_110718_(this.f_109059_, p_109121_);
            this.m_109117_(p_109121_, p_109123_);
         }

         if (this.f_109059_.f_91066_.m_231830_().m_231551_()) {
            this.m_109138_(p_109121_, p_109123_);
         }

      }
   }

   public void m_252879_(Matrix4f p_253668_) {
      RenderSystem.setProjectionMatrix(p_253668_, VertexSorting.f_276450_);
   }

   public Matrix4f m_253088_(double p_254507_) {
      PoseStack posestack = new PoseStack();
      posestack.m_85850_().m_252922_().identity();
      if (this.f_109077_ != 1.0F) {
         posestack.m_252880_(this.f_109078_, -this.f_109079_, 0.0F);
         posestack.m_85841_(this.f_109077_, this.f_109077_, 1.0F);
      }

      posestack.m_85850_().m_252922_().mul((new Matrix4f()).setPerspective((float)(p_254507_ * (double)((float)Math.PI / 180F)), (float)this.f_109059_.m_91268_().m_85441_() / (float)this.f_109059_.m_91268_().m_85442_(), 0.05F, this.m_172790_()));
      return posestack.m_85850_().m_252922_();
   }

   public float m_172790_() {
      return this.f_109062_ * 4.0F;
   }

   public static float m_109108_(LivingEntity p_109109_, float p_109110_) {
      MobEffectInstance mobeffectinstance = p_109109_.m_21124_(MobEffects.f_19611_);
      return !mobeffectinstance.m_267633_(200) ? 1.0F : 0.7F + Mth.m_14031_(((float)mobeffectinstance.m_19557_() - p_109110_) * (float)Math.PI * 0.2F) * 0.3F;
   }

   public void m_109093_(float p_109094_, long p_109095_, boolean p_109096_) {
      if (!this.f_109059_.m_91302_() && this.f_109059_.f_91066_.f_92126_ && (!this.f_109059_.f_91066_.m_231828_().m_231551_() || !this.f_109059_.f_91067_.m_91584_())) {
         if (Util.m_137550_() - this.f_109073_ > 500L) {
            this.f_109059_.m_91358_(false);
         }
      } else {
         this.f_109073_ = Util.m_137550_();
      }

      if (!this.f_109059_.f_91079_) {
         int i = (int)(this.f_109059_.f_91067_.m_91589_() * (double)this.f_109059_.m_91268_().m_85445_() / (double)this.f_109059_.m_91268_().m_85443_());
         int j = (int)(this.f_109059_.f_91067_.m_91594_() * (double)this.f_109059_.m_91268_().m_85446_() / (double)this.f_109059_.m_91268_().m_85444_());
         RenderSystem.viewport(0, 0, this.f_109059_.m_91268_().m_85441_(), this.f_109059_.m_91268_().m_85442_());
         if (p_109096_ && this.f_109059_.f_91073_ != null) {
            this.f_109059_.m_91307_().m_6180_("level");
            this.m_109089_(p_109094_, p_109095_, new PoseStack());
            this.m_182644_();
            this.f_109059_.f_91060_.m_109769_();
            if (this.f_109050_ != null && this.f_109053_) {
               RenderSystem.disableBlend();
               RenderSystem.disableDepthTest();
               RenderSystem.resetTextureMatrix();
               this.f_109050_.m_110023_(p_109094_);
            }

            this.f_109059_.m_91385_().m_83947_(true);
         }

         Window window = this.f_109059_.m_91268_();
         RenderSystem.clear(256, Minecraft.f_91002_);
         Matrix4f matrix4f = (new Matrix4f()).setOrtho(0.0F, (float)((double)window.m_85441_() / window.m_85449_()), (float)((double)window.m_85442_() / window.m_85449_()), 0.0F, 1000.0F, net.minecraftforge.client.ForgeHooksClient.getGuiFarPlane());
         RenderSystem.setProjectionMatrix(matrix4f, VertexSorting.f_276633_);
         PoseStack posestack = RenderSystem.getModelViewStack();
         posestack.m_85836_();
         posestack.m_166856_();
         posestack.m_85837_(0.0D, 0.0D, 1000F-net.minecraftforge.client.ForgeHooksClient.getGuiFarPlane());
         RenderSystem.applyModelViewMatrix();
         Lighting.m_84931_();
         GuiGraphics guigraphics = new GuiGraphics(this.f_109059_, this.f_109064_.m_110104_());
         if (p_109096_ && this.f_109059_.f_91073_ != null) {
            this.f_109059_.m_91307_().m_6182_("gui");
            if (this.f_109059_.f_91074_ != null) {
               float f = Mth.m_14179_(p_109094_, this.f_109059_.f_91074_.f_108590_, this.f_109059_.f_91074_.f_108589_);
               float f1 = this.f_109059_.f_91066_.m_231924_().m_231551_().floatValue();
               if (f > 0.0F && this.f_109059_.f_91074_.m_21023_(MobEffects.f_19604_) && f1 < 1.0F) {
                  this.m_280083_(guigraphics, f * (1.0F - f1));
               }
            }

            if (!this.f_109059_.f_91066_.f_92062_ || this.f_109059_.f_91080_ != null) {
               this.m_109100_(this.f_109059_.m_91268_().m_85445_(), this.f_109059_.m_91268_().m_85446_(), p_109094_);
               this.f_109059_.f_91065_.m_280421_(guigraphics, p_109094_);
               RenderSystem.clear(256, Minecraft.f_91002_);
            }

            this.f_109059_.m_91307_().m_7238_();
         }

         if (this.f_109059_.m_91265_() != null) {
            try {
               this.f_109059_.m_91265_().m_88315_(guigraphics, i, j, this.f_109059_.m_91297_());
            } catch (Throwable throwable2) {
               CrashReport crashreport = CrashReport.m_127521_(throwable2, "Rendering overlay");
               CrashReportCategory crashreportcategory = crashreport.m_127514_("Overlay render details");
               crashreportcategory.m_128165_("Overlay name", () -> {
                  return this.f_109059_.m_91265_().getClass().getCanonicalName();
               });
               throw new ReportedException(crashreport);
            }
         } else if (this.f_109059_.f_91080_ != null) {
            try {
               net.minecraftforge.client.ForgeHooksClient.drawScreen(this.f_109059_.f_91080_, guigraphics, i, j, this.f_109059_.m_91297_());
            } catch (Throwable throwable1) {
               CrashReport crashreport1 = CrashReport.m_127521_(throwable1, "Rendering screen");
               CrashReportCategory crashreportcategory1 = crashreport1.m_127514_("Screen render details");
               crashreportcategory1.m_128165_("Screen name", () -> {
                  return this.f_109059_.f_91080_.getClass().getCanonicalName();
               });
               crashreportcategory1.m_128165_("Mouse location", () -> {
                  return String.format(Locale.ROOT, "Scaled: (%d, %d). Absolute: (%f, %f)", i, j, this.f_109059_.f_91067_.m_91589_(), this.f_109059_.f_91067_.m_91594_());
               });
               crashreportcategory1.m_128165_("Screen size", () -> {
                  return String.format(Locale.ROOT, "Scaled: (%d, %d). Absolute: (%d, %d). Scale factor of %f", this.f_109059_.m_91268_().m_85445_(), this.f_109059_.m_91268_().m_85446_(), this.f_109059_.m_91268_().m_85441_(), this.f_109059_.m_91268_().m_85442_(), this.f_109059_.m_91268_().m_85449_());
               });
               throw new ReportedException(crashreport1);
            }

            try {
               if (this.f_109059_.f_91080_ != null) {
                  this.f_109059_.f_91080_.m_169417_();
               }
            } catch (Throwable throwable) {
               CrashReport crashreport2 = CrashReport.m_127521_(throwable, "Narrating screen");
               CrashReportCategory crashreportcategory2 = crashreport2.m_127514_("Screen details");
               crashreportcategory2.m_128165_("Screen name", () -> {
                  return this.f_109059_.f_91080_.getClass().getCanonicalName();
               });
               throw new ReportedException(crashreport2);
            }
         }

         this.f_109059_.m_91307_().m_6180_("toasts");
         this.f_109059_.m_91300_().m_94920_(guigraphics);
         this.f_109059_.m_91307_().m_7238_();
         guigraphics.m_280262_();
         posestack.m_85849_();
         RenderSystem.applyModelViewMatrix();
      }
   }

   private void m_182644_() {
      if (!this.f_182638_ && this.f_109059_.m_91090_()) {
         long i = Util.m_137550_();
         if (i - this.f_109072_ >= 1000L) {
            this.f_109072_ = i;
            IntegratedServer integratedserver = this.f_109059_.m_91092_();
            if (integratedserver != null && !integratedserver.m_129918_()) {
               integratedserver.m_182649_().ifPresent((p_234239_) -> {
                  if (Files.isRegularFile(p_234239_)) {
                     this.f_182638_ = true;
                  } else {
                     this.m_182642_(p_234239_);
                  }

               });
            }
         }
      }
   }

   private void m_182642_(Path p_182643_) {
      if (this.f_109059_.f_91060_.m_109821_() > 10 && this.f_109059_.f_91060_.m_109825_()) {
         NativeImage nativeimage = Screenshot.m_92279_(this.f_109059_.m_91385_());
         Util.m_183992_().execute(() -> {
            int i = nativeimage.m_84982_();
            int j = nativeimage.m_85084_();
            int k = 0;
            int l = 0;
            if (i > j) {
               k = (i - j) / 2;
               i = j;
            } else {
               l = (j - i) / 2;
               j = i;
            }

            try (NativeImage nativeimage1 = new NativeImage(64, 64, false)) {
               nativeimage.m_85034_(k, l, i, j, nativeimage1);
               nativeimage1.m_85066_(p_182643_);
            } catch (IOException ioexception) {
               f_109058_.warn("Couldn't save auto screenshot", (Throwable)ioexception);
            } finally {
               nativeimage.close();
            }

         });
      }

   }

   private boolean m_109158_() {
      if (!this.f_109071_) {
         return false;
      } else {
         Entity entity = this.f_109059_.m_91288_();
         boolean flag = entity instanceof Player && !this.f_109059_.f_91066_.f_92062_;
         if (flag && !((Player)entity).m_150110_().f_35938_) {
            ItemStack itemstack = ((LivingEntity)entity).m_21205_();
            HitResult hitresult = this.f_109059_.f_91077_;
            if (hitresult != null && hitresult.m_6662_() == HitResult.Type.BLOCK) {
               BlockPos blockpos = ((BlockHitResult)hitresult).m_82425_();
               BlockState blockstate = this.f_109059_.f_91073_.m_8055_(blockpos);
               if (this.f_109059_.f_91072_.m_105295_() == GameType.SPECTATOR) {
                  flag = blockstate.m_60750_(this.f_109059_.f_91073_, blockpos) != null;
               } else {
                  BlockInWorld blockinworld = new BlockInWorld(this.f_109059_.f_91073_, blockpos, false);
                  Registry<Block> registry = this.f_109059_.f_91073_.m_9598_().m_175515_(Registries.f_256747_);
                  flag = !itemstack.m_41619_() && (itemstack.m_204128_(registry, blockinworld) || itemstack.m_204121_(registry, blockinworld));
               }
            }
         }

         return flag;
      }
   }

   public void m_109089_(float p_109090_, long p_109091_, PoseStack p_109092_) {
      this.f_109074_.m_109881_(p_109090_);
      if (this.f_109059_.m_91288_() == null) {
         this.f_109059_.m_91118_(this.f_109059_.f_91074_);
      }

      this.m_109087_(p_109090_);
      this.f_109059_.m_91307_().m_6180_("center");
      boolean flag = this.m_109158_();
      this.f_109059_.m_91307_().m_6182_("camera");
      Camera camera = this.f_109054_;
      this.f_109062_ = (float)(this.f_109059_.f_91066_.m_193772_() * 16);
      PoseStack posestack = new PoseStack();
      double d0 = this.m_109141_(camera, p_109090_, true);
      posestack.m_252931_(this.m_253088_(d0));
      this.m_109117_(posestack, p_109090_);
      if (this.f_109059_.f_91066_.m_231830_().m_231551_()) {
         this.m_109138_(posestack, p_109090_);
      }

      float f = this.f_109059_.f_91066_.m_231924_().m_231551_().floatValue();
      float f1 = Mth.m_14179_(p_109090_, this.f_109059_.f_91074_.f_108590_, this.f_109059_.f_91074_.f_108589_) * f * f;
      if (f1 > 0.0F) {
         int i = this.f_109059_.f_91074_.m_21023_(MobEffects.f_19604_) ? 7 : 20;
         float f2 = 5.0F / (f1 * f1 + 5.0F) - f1 * 0.04F;
         f2 *= f2;
         Axis axis = Axis.m_253057_(new Vector3f(0.0F, Mth.f_13994_ / 2.0F, Mth.f_13994_ / 2.0F));
         posestack.m_252781_(axis.m_252977_(((float)this.f_109065_ + p_109090_) * (float)i));
         posestack.m_85841_(1.0F / f2, 1.0F, 1.0F);
         float f3 = -((float)this.f_109065_ + p_109090_) * (float)i;
         posestack.m_252781_(axis.m_252977_(f3));
      }

      Matrix4f matrix4f = posestack.m_85850_().m_252922_();
      this.m_252879_(matrix4f);
      camera.m_90575_(this.f_109059_.f_91073_, (Entity)(this.f_109059_.m_91288_() == null ? this.f_109059_.f_91074_ : this.f_109059_.m_91288_()), !this.f_109059_.f_91066_.m_92176_().m_90612_(), this.f_109059_.f_91066_.m_92176_().m_90613_(), p_109090_);

      net.minecraftforge.client.event.ViewportEvent.ComputeCameraAngles cameraSetup = net.minecraftforge.client.ForgeHooksClient.onCameraSetup(this, camera, p_109090_);
      camera.setAnglesInternal(cameraSetup.getYaw(), cameraSetup.getPitch());
      p_109092_.m_252781_(Axis.f_252403_.m_252977_(cameraSetup.getRoll()));

      p_109092_.m_252781_(Axis.f_252529_.m_252977_(camera.m_90589_()));
      p_109092_.m_252781_(Axis.f_252436_.m_252977_(camera.m_90590_() + 180.0F));
      Matrix3f matrix3f = (new Matrix3f(p_109092_.m_85850_().m_252943_())).invert();
      RenderSystem.setInverseViewRotationMatrix(matrix3f);
      this.f_109059_.f_91060_.m_253210_(p_109092_, camera.m_90583_(), this.m_253088_(Math.max(d0, (double)this.f_109059_.f_91066_.m_231837_().m_231551_().intValue())));
      this.f_109059_.f_91060_.m_109599_(p_109092_, p_109090_, p_109091_, flag, camera, this, this.f_109074_, matrix4f);
      this.f_109059_.m_91307_().m_6182_("forge_render_last");
      net.minecraftforge.client.ForgeHooksClient.dispatchRenderStage(net.minecraftforge.client.event.RenderLevelStageEvent.Stage.AFTER_LEVEL, this.f_109059_.f_91060_, posestack, matrix4f, this.f_109059_.f_91060_.getTicks(), camera, this.f_109059_.f_91060_.getFrustum());
      this.f_109059_.m_91307_().m_6182_("hand");
      if (this.f_109070_) {
         RenderSystem.clear(256, Minecraft.f_91002_);
         this.m_109120_(p_109092_, camera, p_109090_);
      }

      this.f_109059_.m_91307_().m_7238_();
   }

   public void m_109150_() {
      this.f_109080_ = null;
      this.f_109063_.m_93260_();
      this.f_109054_.m_90598_();
      this.f_182638_ = false;
   }

   public MapRenderer m_109151_() {
      return this.f_109063_;
   }

   public void m_109113_(ItemStack p_109114_) {
      this.f_109080_ = p_109114_;
      this.f_109047_ = 40;
      this.f_109048_ = this.f_109061_.m_188501_() * 2.0F - 1.0F;
      this.f_109049_ = this.f_109061_.m_188501_() * 2.0F - 1.0F;
   }

   private void m_109100_(int p_109101_, int p_109102_, float p_109103_) {
      if (this.f_109080_ != null && this.f_109047_ > 0) {
         int i = 40 - this.f_109047_;
         float f = ((float)i + p_109103_) / 40.0F;
         float f1 = f * f;
         float f2 = f * f1;
         float f3 = 10.25F * f2 * f1 - 24.95F * f1 * f1 + 25.5F * f2 - 13.8F * f1 + 4.0F * f;
         float f4 = f3 * (float)Math.PI;
         float f5 = this.f_109048_ * (float)(p_109101_ / 4);
         float f6 = this.f_109049_ * (float)(p_109102_ / 4);
         RenderSystem.enableDepthTest();
         RenderSystem.disableCull();
         PoseStack posestack = new PoseStack();
         posestack.m_85836_();
         posestack.m_252880_((float)(p_109101_ / 2) + f5 * Mth.m_14154_(Mth.m_14031_(f4 * 2.0F)), (float)(p_109102_ / 2) + f6 * Mth.m_14154_(Mth.m_14031_(f4 * 2.0F)), -50.0F);
         float f7 = 50.0F + 175.0F * Mth.m_14031_(f4);
         posestack.m_85841_(f7, -f7, f7);
         posestack.m_252781_(Axis.f_252436_.m_252977_(900.0F * Mth.m_14154_(Mth.m_14031_(f4))));
         posestack.m_252781_(Axis.f_252529_.m_252977_(6.0F * Mth.m_14089_(f * 8.0F)));
         posestack.m_252781_(Axis.f_252403_.m_252977_(6.0F * Mth.m_14089_(f * 8.0F)));
         MultiBufferSource.BufferSource multibuffersource$buffersource = this.f_109064_.m_110104_();
         this.f_109059_.m_91291_().m_269128_(this.f_109080_, ItemDisplayContext.FIXED, 15728880, OverlayTexture.f_118083_, posestack, multibuffersource$buffersource, this.f_109059_.f_91073_, 0);
         posestack.m_85849_();
         multibuffersource$buffersource.m_109911_();
         RenderSystem.enableCull();
         RenderSystem.disableDepthTest();
      }
   }

   private void m_280083_(GuiGraphics p_282460_, float p_282656_) {
      int i = p_282460_.m_280182_();
      int j = p_282460_.m_280206_();
      p_282460_.m_280168_().m_85836_();
      float f = Mth.m_14179_(p_282656_, 2.0F, 1.0F);
      p_282460_.m_280168_().m_252880_((float)i / 2.0F, (float)j / 2.0F, 0.0F);
      p_282460_.m_280168_().m_85841_(f, f, f);
      p_282460_.m_280168_().m_252880_((float)(-i) / 2.0F, (float)(-j) / 2.0F, 0.0F);
      float f1 = 0.2F * p_282656_;
      float f2 = 0.4F * p_282656_;
      float f3 = 0.2F * p_282656_;
      RenderSystem.disableDepthTest();
      RenderSystem.depthMask(false);
      RenderSystem.enableBlend();
      RenderSystem.blendFuncSeparate(GlStateManager.SourceFactor.ONE, GlStateManager.DestFactor.ONE, GlStateManager.SourceFactor.ONE, GlStateManager.DestFactor.ONE);
      p_282460_.m_280246_(f1, f2, f3, 1.0F);
      p_282460_.m_280398_(f_109057_, 0, 0, -90, 0.0F, 0.0F, i, j, i, j);
      p_282460_.m_280246_(1.0F, 1.0F, 1.0F, 1.0F);
      RenderSystem.defaultBlendFunc();
      RenderSystem.disableBlend();
      RenderSystem.depthMask(true);
      RenderSystem.enableDepthTest();
      p_282460_.m_280168_().m_85849_();
   }

   public Minecraft m_172797_() {
      return this.f_109059_;
   }

   public float m_109131_(float p_109132_) {
      return Mth.m_14179_(p_109132_, this.f_109069_, this.f_109068_);
   }

   public float m_109152_() {
      return this.f_109062_;
   }

   public Camera m_109153_() {
      return this.f_109054_;
   }

   public LightTexture m_109154_() {
      return this.f_109074_;
   }

   public OverlayTexture m_109155_() {
      return this.f_109075_;
   }

   @Nullable
   public static ShaderInstance m_172808_() {
      return f_172579_;
   }

   @Nullable
   public static ShaderInstance m_172811_() {
      return f_172580_;
   }

   @Nullable
   public static ShaderInstance m_172814_() {
      return f_172581_;
   }

   @Nullable
   public static ShaderInstance m_172817_() {
      return f_172582_;
   }

   @Nullable
   public static ShaderInstance m_172820_() {
      return f_172583_;
   }

   @Nullable
   public static ShaderInstance m_172829_() {
      return f_172586_;
   }

   @Nullable
   public static ShaderInstance m_172832_() {
      return f_172587_;
   }

   @Nullable
   public static ShaderInstance m_172835_() {
      return f_172588_;
   }

   @Nullable
   public static ShaderInstance m_172838_() {
      return f_172589_;
   }

   @Nullable
   public static ShaderInstance m_172637_() {
      return f_172590_;
   }

   @Nullable
   public static ShaderInstance m_172640_() {
      return f_172591_;
   }

   @Nullable
   public static ShaderInstance m_172643_() {
      return f_172608_;
   }

   @Nullable
   public static ShaderInstance m_172646_() {
      return f_172609_;
   }

   @Nullable
   public static ShaderInstance m_172649_() {
      return f_172610_;
   }

   @Nullable
   public static ShaderInstance m_172652_() {
      return f_172611_;
   }

   @Nullable
   public static ShaderInstance m_172655_() {
      return f_172612_;
   }

   @Nullable
   public static ShaderInstance m_172658_() {
      return f_172613_;
   }

   @Nullable
   public static ShaderInstance m_172661_() {
      return f_172614_;
   }

   @Nullable
   public static ShaderInstance m_172664_() {
      return f_172615_;
   }

   @Nullable
   public static ShaderInstance m_172667_() {
      return f_172616_;
   }

   @Nullable
   public static ShaderInstance m_172670_() {
      return f_172617_;
   }

   @Nullable
   public static ShaderInstance m_172673_() {
      return f_172618_;
   }

   @Nullable
   public static ShaderInstance m_172676_() {
      return f_172619_;
   }

   @Nullable
   public static ShaderInstance m_172679_() {
      return f_172620_;
   }

   @Nullable
   public static ShaderInstance m_234223_() {
      return f_234217_;
   }

   @Nullable
   public static ShaderInstance m_172682_() {
      return f_172621_;
   }

   @Nullable
   public static ShaderInstance m_172685_() {
      return f_172622_;
   }

   @Nullable
   public static ShaderInstance m_172688_() {
      return f_172623_;
   }

   @Nullable
   public static ShaderInstance m_172691_() {
      return f_172624_;
   }

   @Nullable
   public static ShaderInstance m_172694_() {
      return f_172625_;
   }

   @Nullable
   public static ShaderInstance m_172697_() {
      return f_172626_;
   }

   @Nullable
   public static ShaderInstance m_172700_() {
      return f_172627_;
   }

   @Nullable
   public static ShaderInstance m_172703_() {
      return f_172628_;
   }

   @Nullable
   public static ShaderInstance m_172706_() {
      return f_172629_;
   }

   @Nullable
   public static ShaderInstance m_172709_() {
      return f_172630_;
   }

   @Nullable
   public static ShaderInstance m_172712_() {
      return f_172631_;
   }

   @Nullable
   public static ShaderInstance m_172738_() {
      return f_172632_;
   }

   @Nullable
   public static ShaderInstance m_172741_() {
      return f_172633_;
   }

   @Nullable
   public static ShaderInstance m_172744_() {
      return f_172593_;
   }

   @Nullable
   public static ShaderInstance m_172745_() {
      return f_172594_;
   }

   @Nullable
   public static ShaderInstance m_172746_() {
      return f_172595_;
   }

   @Nullable
   public static ShaderInstance m_172747_() {
      return f_172596_;
   }

   @Nullable
   public static ShaderInstance m_172748_() {
      return f_172597_;
   }

   @Nullable
   public static ShaderInstance m_172749_() {
      return f_172598_;
   }

   @Nullable
   public static ShaderInstance m_269563_() {
      return f_268423_;
   }

   @Nullable
   public static ShaderInstance m_172750_() {
      return f_172599_;
   }

   @Nullable
   public static ShaderInstance m_172751_() {
      return f_172600_;
   }

   @Nullable
   public static ShaderInstance m_269511_() {
      return f_268525_;
   }

   @Nullable
   public static ShaderInstance m_172752_() {
      return f_172601_;
   }

   @Nullable
   public static ShaderInstance m_172753_() {
      return f_172602_;
   }

   @Nullable
   public static ShaderInstance m_172754_() {
      return f_172603_;
   }

   @Nullable
   public static ShaderInstance m_172755_() {
      return f_172604_;
   }

   @Nullable
   public static ShaderInstance m_172756_() {
      return f_172605_;
   }

   @Nullable
   public static ShaderInstance m_172757_() {
      return f_172606_;
   }

   @Nullable
   public static ShaderInstance m_172758_() {
      return f_172607_;
   }

   @Nullable
   public static ShaderInstance m_285858_() {
      return f_285653_;
   }

   @Nullable
   public static ShaderInstance m_285975_() {
      return f_285598_;
   }

   @Nullable
   public static ShaderInstance m_285738_() {
      return f_285623_;
   }

   @Nullable
   public static ShaderInstance m_285862_() {
      return f_285569_;
   }

   @OnlyIn(Dist.CLIENT)
   public static record ResourceCache(ResourceProvider f_244315_, Map<ResourceLocation, Resource> f_243825_) implements ResourceProvider {
      public Optional<Resource> m_213713_(ResourceLocation p_251007_) {
         Resource resource = this.f_243825_.get(p_251007_);
         return resource != null ? Optional.of(resource) : this.f_244315_.m_213713_(p_251007_);
      }
   }
}
