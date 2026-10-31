package net.minecraft.client.renderer.entity;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.renderer.LightTexture;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.culling.Frustum;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Matrix4f;

@OnlyIn(Dist.CLIENT)
public abstract class EntityRenderer<T extends Entity> {
   protected static final float f_174006_ = 0.025F;
   protected final EntityRenderDispatcher f_114476_;
   private final Font f_174005_;
   protected float f_114477_;
   protected float f_114478_ = 1.0F;

   protected EntityRenderer(EntityRendererProvider.Context p_174008_) {
      this.f_114476_ = p_174008_.m_174022_();
      this.f_174005_ = p_174008_.m_174028_();
   }

   public final int m_114505_(T p_114506_, float p_114507_) {
      BlockPos blockpos = BlockPos.m_274446_(p_114506_.m_7371_(p_114507_));
      return LightTexture.m_109885_(this.m_6086_(p_114506_, blockpos), this.m_114508_(p_114506_, blockpos));
   }

   protected int m_114508_(T p_114509_, BlockPos p_114510_) {
      return p_114509_.m_9236_().m_45517_(LightLayer.SKY, p_114510_);
   }

   protected int m_6086_(T p_114496_, BlockPos p_114497_) {
      return p_114496_.m_6060_() ? 15 : p_114496_.m_9236_().m_45517_(LightLayer.BLOCK, p_114497_);
   }

   public boolean m_5523_(T p_114491_, Frustum p_114492_, double p_114493_, double p_114494_, double p_114495_) {
      if (!p_114491_.m_6000_(p_114493_, p_114494_, p_114495_)) {
         return false;
      } else if (p_114491_.f_19811_) {
         return true;
      } else {
         AABB aabb = p_114491_.m_6921_().m_82400_(0.5D);
         if (aabb.m_82392_() || aabb.m_82309_() == 0.0D) {
            aabb = new AABB(p_114491_.m_20185_() - 2.0D, p_114491_.m_20186_() - 2.0D, p_114491_.m_20189_() - 2.0D, p_114491_.m_20185_() + 2.0D, p_114491_.m_20186_() + 2.0D, p_114491_.m_20189_() + 2.0D);
         }

         return p_114492_.m_113029_(aabb);
      }
   }

   public Vec3 m_7860_(T p_114483_, float p_114484_) {
      return Vec3.f_82478_;
   }

   public void m_7392_(T p_114485_, float p_114486_, float p_114487_, PoseStack p_114488_, MultiBufferSource p_114489_, int p_114490_) {
      var renderNameTagEvent = new net.minecraftforge.client.event.RenderNameTagEvent(p_114485_, p_114485_.m_5446_(), this, p_114488_, p_114489_, p_114490_, p_114487_);
      net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(renderNameTagEvent);
      if (renderNameTagEvent.getResult() != net.minecraftforge.eventbus.api.Event.Result.DENY && (renderNameTagEvent.getResult() == net.minecraftforge.eventbus.api.Event.Result.ALLOW || this.m_6512_(p_114485_))) {
         this.m_7649_(p_114485_, renderNameTagEvent.getContent(), p_114488_, p_114489_, p_114490_);
      }
   }

   protected boolean m_6512_(T p_114504_) {
      return p_114504_.m_6052_() && p_114504_.m_8077_();
   }

   public abstract ResourceLocation m_5478_(T p_114482_);

   public Font m_114481_() {
      return this.f_174005_;
   }

   protected void m_7649_(T p_114498_, Component p_114499_, PoseStack p_114500_, MultiBufferSource p_114501_, int p_114502_) {
      double d0 = this.f_114476_.m_114471_(p_114498_);
      if (net.minecraftforge.client.ForgeHooksClient.isNameplateInRenderDistance(p_114498_, d0)) {
         boolean flag = !p_114498_.m_20163_();
         float f = p_114498_.m_278726_();
         int i = "deadmau5".equals(p_114499_.getString()) ? -10 : 0;
         p_114500_.m_85836_();
         p_114500_.m_252880_(0.0F, f, 0.0F);
         p_114500_.m_252781_(this.f_114476_.m_253208_());
         p_114500_.m_85841_(-0.025F, -0.025F, 0.025F);
         Matrix4f matrix4f = p_114500_.m_85850_().m_252922_();
         float f1 = Minecraft.m_91087_().f_91066_.m_92141_(0.25F);
         int j = (int)(f1 * 255.0F) << 24;
         Font font = this.m_114481_();
         float f2 = (float)(-font.m_92852_(p_114499_) / 2);
         font.m_272077_(p_114499_, f2, (float)i, 553648127, false, matrix4f, p_114501_, flag ? Font.DisplayMode.SEE_THROUGH : Font.DisplayMode.NORMAL, j, p_114502_);
         if (flag) {
            font.m_272077_(p_114499_, f2, (float)i, -1, false, matrix4f, p_114501_, Font.DisplayMode.NORMAL, 0, p_114502_);
         }

         p_114500_.m_85849_();
      }
   }
}
