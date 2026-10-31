package net.minecraft.client.renderer.entity;

import com.google.common.collect.ImmutableMap;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import java.util.Map;
import javax.annotation.Nullable;
import net.minecraft.CrashReport;
import net.minecraft.CrashReportCategory;
import net.minecraft.ReportedException;
import net.minecraft.client.Camera;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Options;
import net.minecraft.client.gui.Font;
import net.minecraft.client.model.geom.EntityModelSet;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.ItemInHandRenderer;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.Sheets;
import net.minecraft.client.renderer.block.BlockRenderDispatcher;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.client.renderer.texture.TextureManager;
import net.minecraft.client.resources.model.ModelBakery;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.server.packs.resources.ResourceManagerReloadListener;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.boss.EnderDragonPart;
import net.minecraft.world.entity.boss.enderdragon.EnderDragon;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;

@OnlyIn(Dist.CLIENT)
public class EntityRenderDispatcher implements ResourceManagerReloadListener {
   private static final RenderType f_114361_ = RenderType.m_110485_(new ResourceLocation("textures/misc/shadow.png"));
   private static final float f_276493_ = 32.0F;
   private static final float f_276586_ = 0.5F;
   public Map<EntityType<?>, EntityRenderer<?>> f_114362_ = ImmutableMap.of();
   private Map<String, EntityRenderer<? extends Player>> f_114363_ = ImmutableMap.of();
   public final TextureManager f_114357_;
   private Level f_114366_;
   public Camera f_114358_;
   private Quaternionf f_114367_;
   public Entity f_114359_;
   private final ItemRenderer f_173995_;
   private final BlockRenderDispatcher f_234576_;
   private final ItemInHandRenderer f_234577_;
   private final Font f_114365_;
   public final Options f_114360_;
   private final EntityModelSet f_173996_;
   private boolean f_114368_ = true;
   private boolean f_114369_;

   public <E extends Entity> int m_114394_(E p_114395_, float p_114396_) {
      return this.m_114382_(p_114395_).m_114505_(p_114395_, p_114396_);
   }

   public EntityRenderDispatcher(Minecraft p_234579_, TextureManager p_234580_, ItemRenderer p_234581_, BlockRenderDispatcher p_234582_, Font p_234583_, Options p_234584_, EntityModelSet p_234585_) {
      this.f_114357_ = p_234580_;
      this.f_173995_ = p_234581_;
      this.f_234577_ = new ItemInHandRenderer(p_234579_, this, p_234581_);
      this.f_234576_ = p_234582_;
      this.f_114365_ = p_234583_;
      this.f_114360_ = p_234584_;
      this.f_173996_ = p_234585_;
   }

   public <T extends Entity> EntityRenderer<? super T> m_114382_(T p_114383_) {
      if (p_114383_ instanceof AbstractClientPlayer) {
         String s = ((AbstractClientPlayer)p_114383_).m_108564_();
         EntityRenderer<? extends Player> entityrenderer = this.f_114363_.get(s);
         return (EntityRenderer) (entityrenderer != null ? entityrenderer : this.f_114363_.get("default"));
      } else {
         return (EntityRenderer) this.f_114362_.get(p_114383_.m_6095_());
      }
   }

   public void m_114408_(Level p_114409_, Camera p_114410_, Entity p_114411_) {
      this.f_114366_ = p_114409_;
      this.f_114358_ = p_114410_;
      this.f_114367_ = p_114410_.m_253121_();
      this.f_114359_ = p_114411_;
   }

   public void m_252923_(Quaternionf p_254264_) {
      this.f_114367_ = p_254264_;
   }

   public void m_114468_(boolean p_114469_) {
      this.f_114368_ = p_114469_;
   }

   public void m_114473_(boolean p_114474_) {
      this.f_114369_ = p_114474_;
   }

   public boolean m_114377_() {
      return this.f_114369_;
   }

   public <E extends Entity> boolean m_114397_(E p_114398_, Frustum p_114399_, double p_114400_, double p_114401_, double p_114402_) {
      EntityRenderer<? super E> entityrenderer = this.m_114382_(p_114398_);
      return entityrenderer.m_5523_(p_114398_, p_114399_, p_114400_, p_114401_, p_114402_);
   }

   public <E extends Entity> void m_114384_(E p_114385_, double p_114386_, double p_114387_, double p_114388_, float p_114389_, float p_114390_, PoseStack p_114391_, MultiBufferSource p_114392_, int p_114393_) {
      EntityRenderer<? super E> entityrenderer = this.m_114382_(p_114385_);

      try {
         Vec3 vec3 = entityrenderer.m_7860_(p_114385_, p_114390_);
         double d2 = p_114386_ + vec3.m_7096_();
         double d3 = p_114387_ + vec3.m_7098_();
         double d0 = p_114388_ + vec3.m_7094_();
         p_114391_.m_85836_();
         p_114391_.m_85837_(d2, d3, d0);
         entityrenderer.m_7392_(p_114385_, p_114389_, p_114390_, p_114391_, p_114392_, p_114393_);
         if (p_114385_.m_6051_()) {
            this.m_114453_(p_114391_, p_114392_, p_114385_);
         }

         p_114391_.m_85837_(-vec3.m_7096_(), -vec3.m_7098_(), -vec3.m_7094_());
         if (this.f_114360_.m_231818_().m_231551_() && this.f_114368_ && entityrenderer.f_114477_ > 0.0F && !p_114385_.m_20145_()) {
            double d1 = this.m_114378_(p_114385_.m_20185_(), p_114385_.m_20186_(), p_114385_.m_20189_());
            float f = (float)((1.0D - d1 / 256.0D) * (double)entityrenderer.f_114478_);
            if (f > 0.0F) {
               m_114457_(p_114391_, p_114392_, p_114385_, f, p_114390_, this.f_114366_, Math.min(entityrenderer.f_114477_, 32.0F));
            }
         }

         if (this.f_114369_ && !p_114385_.m_20145_() && !Minecraft.m_91087_().m_91299_()) {
            m_114441_(p_114391_, p_114392_.m_6299_(RenderType.m_110504_()), p_114385_, p_114390_);
         }

         p_114391_.m_85849_();
      } catch (Throwable throwable) {
         CrashReport crashreport = CrashReport.m_127521_(throwable, "Rendering entity in world");
         CrashReportCategory crashreportcategory = crashreport.m_127514_("Entity being rendered");
         p_114385_.m_7976_(crashreportcategory);
         CrashReportCategory crashreportcategory1 = crashreport.m_127514_("Renderer details");
         crashreportcategory1.m_128159_("Assigned renderer", entityrenderer);
         crashreportcategory1.m_128159_("Location", CrashReportCategory.m_178937_(this.f_114366_, p_114386_, p_114387_, p_114388_));
         crashreportcategory1.m_128159_("Rotation", p_114389_);
         crashreportcategory1.m_128159_("Delta", p_114390_);
         throw new ReportedException(crashreport);
      }
   }

   private static void m_114441_(PoseStack p_114442_, VertexConsumer p_114443_, Entity p_114444_, float p_114445_) {
      AABB aabb = p_114444_.m_20191_().m_82386_(-p_114444_.m_20185_(), -p_114444_.m_20186_(), -p_114444_.m_20189_());
      LevelRenderer.m_109646_(p_114442_, p_114443_, aabb, 1.0F, 1.0F, 1.0F, 1.0F);
      if (p_114444_.isMultipartEntity()) {
         double d0 = -Mth.m_14139_((double)p_114445_, p_114444_.f_19790_, p_114444_.m_20185_());
         double d1 = -Mth.m_14139_((double)p_114445_, p_114444_.f_19791_, p_114444_.m_20186_());
         double d2 = -Mth.m_14139_((double)p_114445_, p_114444_.f_19792_, p_114444_.m_20189_());

         for(net.minecraftforge.entity.PartEntity<?> enderdragonpart : p_114444_.getParts()) {
            p_114442_.m_85836_();
            double d3 = d0 + Mth.m_14139_((double)p_114445_, enderdragonpart.f_19790_, enderdragonpart.m_20185_());
            double d4 = d1 + Mth.m_14139_((double)p_114445_, enderdragonpart.f_19791_, enderdragonpart.m_20186_());
            double d5 = d2 + Mth.m_14139_((double)p_114445_, enderdragonpart.f_19792_, enderdragonpart.m_20189_());
            p_114442_.m_85837_(d3, d4, d5);
            LevelRenderer.m_109646_(p_114442_, p_114443_, enderdragonpart.m_20191_().m_82386_(-enderdragonpart.m_20185_(), -enderdragonpart.m_20186_(), -enderdragonpart.m_20189_()), 0.25F, 1.0F, 0.0F, 1.0F);
            p_114442_.m_85849_();
         }
      }

      if (p_114444_ instanceof LivingEntity) {
         float f = 0.01F;
         LevelRenderer.m_109608_(p_114442_, p_114443_, aabb.f_82288_, (double)(p_114444_.m_20192_() - 0.01F), aabb.f_82290_, aabb.f_82291_, (double)(p_114444_.m_20192_() + 0.01F), aabb.f_82293_, 1.0F, 0.0F, 0.0F, 1.0F);
      }

      Vec3 vec3 = p_114444_.m_20252_(p_114445_);
      Matrix4f matrix4f = p_114442_.m_85850_().m_252922_();
      Matrix3f matrix3f = p_114442_.m_85850_().m_252943_();
      p_114443_.m_252986_(matrix4f, 0.0F, p_114444_.m_20192_(), 0.0F).m_6122_(0, 0, 255, 255).m_252939_(matrix3f, (float)vec3.f_82479_, (float)vec3.f_82480_, (float)vec3.f_82481_).m_5752_();
      p_114443_.m_252986_(matrix4f, (float)(vec3.f_82479_ * 2.0D), (float)((double)p_114444_.m_20192_() + vec3.f_82480_ * 2.0D), (float)(vec3.f_82481_ * 2.0D)).m_6122_(0, 0, 255, 255).m_252939_(matrix3f, (float)vec3.f_82479_, (float)vec3.f_82480_, (float)vec3.f_82481_).m_5752_();
   }

   private void m_114453_(PoseStack p_114454_, MultiBufferSource p_114455_, Entity p_114456_) {
      TextureAtlasSprite textureatlassprite = ModelBakery.f_119219_.m_119204_();
      TextureAtlasSprite textureatlassprite1 = ModelBakery.f_119220_.m_119204_();
      p_114454_.m_85836_();
      float f = p_114456_.m_20205_() * 1.4F;
      p_114454_.m_85841_(f, f, f);
      float f1 = 0.5F;
      float f2 = 0.0F;
      float f3 = p_114456_.m_20206_() / f;
      float f4 = 0.0F;
      p_114454_.m_252781_(Axis.f_252436_.m_252977_(-this.f_114358_.m_90590_()));
      p_114454_.m_252880_(0.0F, 0.0F, -0.3F + (float)((int)f3) * 0.02F);
      float f5 = 0.0F;
      int i = 0;
      VertexConsumer vertexconsumer = p_114455_.m_6299_(Sheets.m_110790_());

      for(PoseStack.Pose posestack$pose = p_114454_.m_85850_(); f3 > 0.0F; ++i) {
         TextureAtlasSprite textureatlassprite2 = i % 2 == 0 ? textureatlassprite : textureatlassprite1;
         float f6 = textureatlassprite2.m_118409_();
         float f7 = textureatlassprite2.m_118411_();
         float f8 = textureatlassprite2.m_118410_();
         float f9 = textureatlassprite2.m_118412_();
         if (i / 2 % 2 == 0) {
            float f10 = f8;
            f8 = f6;
            f6 = f10;
         }

         m_114414_(posestack$pose, vertexconsumer, f1 - 0.0F, 0.0F - f4, f5, f8, f9);
         m_114414_(posestack$pose, vertexconsumer, -f1 - 0.0F, 0.0F - f4, f5, f6, f9);
         m_114414_(posestack$pose, vertexconsumer, -f1 - 0.0F, 1.4F - f4, f5, f6, f7);
         m_114414_(posestack$pose, vertexconsumer, f1 - 0.0F, 1.4F - f4, f5, f8, f7);
         f3 -= 0.45F;
         f4 -= 0.45F;
         f1 *= 0.9F;
         f5 += 0.03F;
      }

      p_114454_.m_85849_();
   }

   private static void m_114414_(PoseStack.Pose p_114415_, VertexConsumer p_114416_, float p_114417_, float p_114418_, float p_114419_, float p_114420_, float p_114421_) {
      p_114416_.m_252986_(p_114415_.m_252922_(), p_114417_, p_114418_, p_114419_).m_6122_(255, 255, 255, 255).m_7421_(p_114420_, p_114421_).m_7122_(0, 10).m_85969_(240).m_252939_(p_114415_.m_252943_(), 0.0F, 1.0F, 0.0F).m_5752_();
   }

   private static void m_114457_(PoseStack p_114458_, MultiBufferSource p_114459_, Entity p_114460_, float p_114461_, float p_114462_, LevelReader p_114463_, float p_114464_) {
      float f = p_114464_;
      if (p_114460_ instanceof Mob mob) {
         if (mob.m_6162_()) {
            f = p_114464_ * 0.5F;
         }
      }

      double d2 = Mth.m_14139_((double)p_114462_, p_114460_.f_19790_, p_114460_.m_20185_());
      double d0 = Mth.m_14139_((double)p_114462_, p_114460_.f_19791_, p_114460_.m_20186_());
      double d1 = Mth.m_14139_((double)p_114462_, p_114460_.f_19792_, p_114460_.m_20189_());
      float f1 = Math.min(p_114461_ / 0.5F, f);
      int i = Mth.m_14107_(d2 - (double)f);
      int j = Mth.m_14107_(d2 + (double)f);
      int k = Mth.m_14107_(d0 - (double)f1);
      int l = Mth.m_14107_(d0);
      int i1 = Mth.m_14107_(d1 - (double)f);
      int j1 = Mth.m_14107_(d1 + (double)f);
      PoseStack.Pose posestack$pose = p_114458_.m_85850_();
      VertexConsumer vertexconsumer = p_114459_.m_6299_(f_114361_);
      BlockPos.MutableBlockPos blockpos$mutableblockpos = new BlockPos.MutableBlockPos();

      for(int k1 = i1; k1 <= j1; ++k1) {
         for(int l1 = i; l1 <= j; ++l1) {
            blockpos$mutableblockpos.m_122178_(l1, 0, k1);
            ChunkAccess chunkaccess = p_114463_.m_46865_(blockpos$mutableblockpos);

            for(int i2 = k; i2 <= l; ++i2) {
               blockpos$mutableblockpos.m_142448_(i2);
               float f2 = p_114461_ - (float)(d0 - (double)blockpos$mutableblockpos.m_123342_()) * 0.5F;
               m_277056_(posestack$pose, vertexconsumer, chunkaccess, p_114463_, blockpos$mutableblockpos, d2, d0, d1, f, f2);
            }
         }
      }

   }

   private static void m_277056_(PoseStack.Pose p_277956_, VertexConsumer p_277533_, ChunkAccess p_277501_, LevelReader p_277622_, BlockPos p_277911_, double p_277682_, double p_278099_, double p_277806_, float p_277844_, float p_277496_) {
      BlockPos blockpos = p_277911_.m_7495_();
      BlockState blockstate = p_277501_.m_8055_(blockpos);
      if (blockstate.m_60799_() != RenderShape.INVISIBLE && p_277622_.m_46803_(p_277911_) > 3) {
         if (blockstate.m_60838_(p_277501_, blockpos)) {
            VoxelShape voxelshape = blockstate.m_60808_(p_277501_, blockpos);
            if (!voxelshape.m_83281_()) {
               float f = LightTexture.m_234316_(p_277622_.m_6042_(), p_277622_.m_46803_(p_277911_));
               float f1 = p_277496_ * 0.5F * f;
               if (f1 >= 0.0F) {
                  if (f1 > 1.0F) {
                     f1 = 1.0F;
                  }

                  AABB aabb = voxelshape.m_83215_();
                  double d0 = (double)p_277911_.m_123341_() + aabb.f_82288_;
                  double d1 = (double)p_277911_.m_123341_() + aabb.f_82291_;
                  double d2 = (double)p_277911_.m_123342_() + aabb.f_82289_;
                  double d3 = (double)p_277911_.m_123343_() + aabb.f_82290_;
                  double d4 = (double)p_277911_.m_123343_() + aabb.f_82293_;
                  float f2 = (float)(d0 - p_277682_);
                  float f3 = (float)(d1 - p_277682_);
                  float f4 = (float)(d2 - p_278099_);
                  float f5 = (float)(d3 - p_277806_);
                  float f6 = (float)(d4 - p_277806_);
                  float f7 = -f2 / 2.0F / p_277844_ + 0.5F;
                  float f8 = -f3 / 2.0F / p_277844_ + 0.5F;
                  float f9 = -f5 / 2.0F / p_277844_ + 0.5F;
                  float f10 = -f6 / 2.0F / p_277844_ + 0.5F;
                  m_114422_(p_277956_, p_277533_, f1, f2, f4, f5, f7, f9);
                  m_114422_(p_277956_, p_277533_, f1, f2, f4, f6, f7, f10);
                  m_114422_(p_277956_, p_277533_, f1, f3, f4, f6, f8, f10);
                  m_114422_(p_277956_, p_277533_, f1, f3, f4, f5, f8, f9);
               }

            }
         }
      }
   }

   private static void m_114422_(PoseStack.Pose p_114423_, VertexConsumer p_114424_, float p_114425_, float p_114426_, float p_114427_, float p_114428_, float p_114429_, float p_114430_) {
      Vector3f vector3f = p_114423_.m_252922_().transformPosition(p_114426_, p_114427_, p_114428_, new Vector3f());
      p_114424_.m_5954_(vector3f.x(), vector3f.y(), vector3f.z(), 1.0F, 1.0F, 1.0F, p_114425_, p_114429_, p_114430_, OverlayTexture.f_118083_, 15728880, 0.0F, 1.0F, 0.0F);
   }

   public void m_114406_(@Nullable Level p_114407_) {
      this.f_114366_ = p_114407_;
      if (p_114407_ == null) {
         this.f_114358_ = null;
      }

   }

   public double m_114471_(Entity p_114472_) {
      return this.f_114358_.m_90583_().m_82557_(p_114472_.m_20182_());
   }

   public double m_114378_(double p_114379_, double p_114380_, double p_114381_) {
      return this.f_114358_.m_90583_().m_82531_(p_114379_, p_114380_, p_114381_);
   }

   public Quaternionf m_253208_() {
      return this.f_114367_;
   }

   public ItemInHandRenderer m_234586_() {
      return this.f_234577_;
   }

   public Map<String, EntityRenderer<? extends Player>> getSkinMap() {
      return java.util.Collections.unmodifiableMap(f_114363_);
   }

   public void m_6213_(ResourceManager p_174004_) {
      EntityRendererProvider.Context entityrendererprovider$context = new EntityRendererProvider.Context(this, this.f_173995_, this.f_234576_, this.f_234577_, p_174004_, this.f_173996_, this.f_114365_);
      this.f_114362_ = EntityRenderers.m_174049_(entityrendererprovider$context);
      this.f_114363_ = EntityRenderers.m_174051_(entityrendererprovider$context);
      net.minecraftforge.fml.ModLoader.get().postEvent(new net.minecraftforge.client.event.EntityRenderersEvent.AddLayers(f_114362_, f_114363_, entityrendererprovider$context));
   }
}
