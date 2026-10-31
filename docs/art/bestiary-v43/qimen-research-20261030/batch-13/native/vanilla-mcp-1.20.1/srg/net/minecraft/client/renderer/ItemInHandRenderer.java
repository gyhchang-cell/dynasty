package net.minecraft.client.renderer;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.MoreObjects;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.renderer.entity.EntityRenderDispatcher;
import net.minecraft.client.renderer.entity.ItemRenderer;
import net.minecraft.client.renderer.entity.player.PlayerRenderer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.CrossbowItem;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.MapItem;
import net.minecraft.world.level.saveddata.maps.MapItemSavedData;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Matrix4f;

@OnlyIn(Dist.CLIENT)
public class ItemInHandRenderer {
   private static final RenderType f_109297_ = RenderType.m_110497_(new ResourceLocation("textures/map/map_background.png"));
   private static final RenderType f_109298_ = RenderType.m_110497_(new ResourceLocation("textures/map/map_background_checkerboard.png"));
   private static final float f_172888_ = -0.4F;
   private static final float f_172889_ = 0.2F;
   private static final float f_172890_ = -0.2F;
   private static final float f_172891_ = -0.6F;
   private static final float f_172892_ = 0.56F;
   private static final float f_172893_ = -0.52F;
   private static final float f_172894_ = -0.72F;
   private static final float f_172895_ = 45.0F;
   private static final float f_172896_ = -80.0F;
   private static final float f_172897_ = -20.0F;
   private static final float f_172898_ = -20.0F;
   private static final float f_172899_ = 10.0F;
   private static final float f_172900_ = 90.0F;
   private static final float f_172901_ = 30.0F;
   private static final float f_172902_ = 0.6F;
   private static final float f_172903_ = -0.5F;
   private static final float f_172904_ = 0.0F;
   private static final double f_172905_ = 27.0D;
   private static final float f_172906_ = 0.8F;
   private static final float f_172907_ = 0.1F;
   private static final float f_172908_ = -0.3F;
   private static final float f_172909_ = 0.4F;
   private static final float f_172910_ = -0.4F;
   private static final float f_172911_ = 70.0F;
   private static final float f_172842_ = -20.0F;
   private static final float f_172843_ = -0.6F;
   private static final float f_172844_ = 0.8F;
   private static final float f_172845_ = 0.8F;
   private static final float f_172846_ = -0.75F;
   private static final float f_172847_ = -0.9F;
   private static final float f_172848_ = 45.0F;
   private static final float f_172849_ = -1.0F;
   private static final float f_172850_ = 3.6F;
   private static final float f_172851_ = 3.5F;
   private static final float f_172852_ = 5.6F;
   private static final int f_172853_ = 200;
   private static final int f_172854_ = -135;
   private static final int f_172855_ = 120;
   private static final float f_172856_ = -0.4F;
   private static final float f_172857_ = -0.2F;
   private static final float f_172858_ = 0.0F;
   private static final float f_172859_ = 0.04F;
   private static final float f_172860_ = -0.72F;
   private static final float f_172861_ = -1.2F;
   private static final float f_172862_ = -0.5F;
   private static final float f_172863_ = 45.0F;
   private static final float f_172864_ = -85.0F;
   private static final float f_172865_ = 45.0F;
   private static final float f_172866_ = 92.0F;
   private static final float f_172867_ = -41.0F;
   private static final float f_172868_ = 0.3F;
   private static final float f_172869_ = -1.1F;
   private static final float f_172870_ = 0.45F;
   private static final float f_172871_ = 20.0F;
   private static final float f_172872_ = 0.38F;
   private static final float f_172873_ = -0.5F;
   private static final float f_172874_ = -0.5F;
   private static final float f_172875_ = 0.0F;
   private static final float f_172876_ = 0.0078125F;
   private static final int f_172877_ = 7;
   private static final int f_172878_ = 128;
   private static final int f_172879_ = 128;
   private static final float f_172880_ = 0.0F;
   private static final float f_172881_ = 0.0F;
   private static final float f_172882_ = 0.04F;
   private static final float f_172883_ = 0.0F;
   private static final float f_172884_ = 0.004F;
   private static final float f_172885_ = 0.0F;
   private static final float f_172886_ = 0.2F;
   private static final float f_172887_ = 0.1F;
   private final Minecraft f_109299_;
   private ItemStack f_109300_ = ItemStack.f_41583_;
   private ItemStack f_109301_ = ItemStack.f_41583_;
   private float f_109302_;
   private float f_109303_;
   private float f_109304_;
   private float f_109305_;
   private final EntityRenderDispatcher f_109306_;
   private final ItemRenderer f_109307_;

   public ItemInHandRenderer(Minecraft p_234241_, EntityRenderDispatcher p_234242_, ItemRenderer p_234243_) {
      this.f_109299_ = p_234241_;
      this.f_109306_ = p_234242_;
      this.f_109307_ = p_234243_;
   }

   public void m_269530_(LivingEntity p_270072_, ItemStack p_270793_, ItemDisplayContext p_270837_, boolean p_270203_, PoseStack p_270974_, MultiBufferSource p_270686_, int p_270103_) {
      if (!p_270793_.m_41619_()) {
         this.f_109307_.m_269491_(p_270072_, p_270793_, p_270837_, p_270203_, p_270974_, p_270686_, p_270072_.m_9236_(), p_270103_, OverlayTexture.f_118083_, p_270072_.m_19879_() + p_270837_.ordinal());
      }
   }

   private float m_109312_(float p_109313_) {
      float f = 1.0F - p_109313_ / 45.0F + 0.1F;
      f = Mth.m_14036_(f, 0.0F, 1.0F);
      return -Mth.m_14089_(f * (float)Math.PI) * 0.5F + 0.5F;
   }

   private void m_109361_(PoseStack p_109362_, MultiBufferSource p_109363_, int p_109364_, HumanoidArm p_109365_) {
      RenderSystem.setShaderTexture(0, this.f_109299_.f_91074_.m_108560_());
      PlayerRenderer playerrenderer = (PlayerRenderer)this.f_109306_.<AbstractClientPlayer>m_114382_(this.f_109299_.f_91074_);
      p_109362_.m_85836_();
      float f = p_109365_ == HumanoidArm.RIGHT ? 1.0F : -1.0F;
      p_109362_.m_252781_(Axis.f_252436_.m_252977_(92.0F));
      p_109362_.m_252781_(Axis.f_252529_.m_252977_(45.0F));
      p_109362_.m_252781_(Axis.f_252403_.m_252977_(f * -41.0F));
      p_109362_.m_252880_(f * 0.3F, -1.1F, 0.45F);
      if (p_109365_ == HumanoidArm.RIGHT) {
         playerrenderer.m_117770_(p_109362_, p_109363_, p_109364_, this.f_109299_.f_91074_);
      } else {
         playerrenderer.m_117813_(p_109362_, p_109363_, p_109364_, this.f_109299_.f_91074_);
      }

      p_109362_.m_85849_();
   }

   private void m_109353_(PoseStack p_109354_, MultiBufferSource p_109355_, int p_109356_, float p_109357_, HumanoidArm p_109358_, float p_109359_, ItemStack p_109360_) {
      float f = p_109358_ == HumanoidArm.RIGHT ? 1.0F : -1.0F;
      p_109354_.m_252880_(f * 0.125F, -0.125F, 0.0F);
      if (!this.f_109299_.f_91074_.m_20145_()) {
         p_109354_.m_85836_();
         p_109354_.m_252781_(Axis.f_252403_.m_252977_(f * 10.0F));
         this.m_109346_(p_109354_, p_109355_, p_109356_, p_109357_, p_109359_, p_109358_);
         p_109354_.m_85849_();
      }

      p_109354_.m_85836_();
      p_109354_.m_252880_(f * 0.51F, -0.08F + p_109357_ * -1.2F, -0.75F);
      float f1 = Mth.m_14116_(p_109359_);
      float f2 = Mth.m_14031_(f1 * (float)Math.PI);
      float f3 = -0.5F * f2;
      float f4 = 0.4F * Mth.m_14031_(f1 * ((float)Math.PI * 2F));
      float f5 = -0.3F * Mth.m_14031_(p_109359_ * (float)Math.PI);
      p_109354_.m_252880_(f * f3, f4 - 0.3F * f2, f5);
      p_109354_.m_252781_(Axis.f_252529_.m_252977_(f2 * -45.0F));
      p_109354_.m_252781_(Axis.f_252436_.m_252977_(f * f2 * -30.0F));
      this.m_109366_(p_109354_, p_109355_, p_109356_, p_109360_);
      p_109354_.m_85849_();
   }

   private void m_109339_(PoseStack p_109340_, MultiBufferSource p_109341_, int p_109342_, float p_109343_, float p_109344_, float p_109345_) {
      float f = Mth.m_14116_(p_109345_);
      float f1 = -0.2F * Mth.m_14031_(p_109345_ * (float)Math.PI);
      float f2 = -0.4F * Mth.m_14031_(f * (float)Math.PI);
      p_109340_.m_252880_(0.0F, -f1 / 2.0F, f2);
      float f3 = this.m_109312_(p_109343_);
      p_109340_.m_252880_(0.0F, 0.04F + p_109344_ * -1.2F + f3 * -0.5F, -0.72F);
      p_109340_.m_252781_(Axis.f_252529_.m_252977_(f3 * -85.0F));
      if (!this.f_109299_.f_91074_.m_20145_()) {
         p_109340_.m_85836_();
         p_109340_.m_252781_(Axis.f_252436_.m_252977_(90.0F));
         this.m_109361_(p_109340_, p_109341_, p_109342_, HumanoidArm.RIGHT);
         this.m_109361_(p_109340_, p_109341_, p_109342_, HumanoidArm.LEFT);
         p_109340_.m_85849_();
      }

      float f4 = Mth.m_14031_(f * (float)Math.PI);
      p_109340_.m_252781_(Axis.f_252529_.m_252977_(f4 * 20.0F));
      p_109340_.m_85841_(2.0F, 2.0F, 2.0F);
      this.m_109366_(p_109340_, p_109341_, p_109342_, this.f_109300_);
   }

   private void m_109366_(PoseStack p_109367_, MultiBufferSource p_109368_, int p_109369_, ItemStack p_109370_) {
      p_109367_.m_252781_(Axis.f_252436_.m_252977_(180.0F));
      p_109367_.m_252781_(Axis.f_252403_.m_252977_(180.0F));
      p_109367_.m_85841_(0.38F, 0.38F, 0.38F);
      p_109367_.m_252880_(-0.5F, -0.5F, 0.0F);
      p_109367_.m_85841_(0.0078125F, 0.0078125F, 0.0078125F);
      Integer integer = MapItem.m_151131_(p_109370_);
      MapItemSavedData mapitemsaveddata = MapItem.m_151128_(integer, this.f_109299_.f_91073_);
      VertexConsumer vertexconsumer = p_109368_.m_6299_(mapitemsaveddata == null ? f_109297_ : f_109298_);
      Matrix4f matrix4f = p_109367_.m_85850_().m_252922_();
      vertexconsumer.m_252986_(matrix4f, -7.0F, 135.0F, 0.0F).m_6122_(255, 255, 255, 255).m_7421_(0.0F, 1.0F).m_85969_(p_109369_).m_5752_();
      vertexconsumer.m_252986_(matrix4f, 135.0F, 135.0F, 0.0F).m_6122_(255, 255, 255, 255).m_7421_(1.0F, 1.0F).m_85969_(p_109369_).m_5752_();
      vertexconsumer.m_252986_(matrix4f, 135.0F, -7.0F, 0.0F).m_6122_(255, 255, 255, 255).m_7421_(1.0F, 0.0F).m_85969_(p_109369_).m_5752_();
      vertexconsumer.m_252986_(matrix4f, -7.0F, -7.0F, 0.0F).m_6122_(255, 255, 255, 255).m_7421_(0.0F, 0.0F).m_85969_(p_109369_).m_5752_();
      if (mapitemsaveddata != null) {
         this.f_109299_.f_91063_.m_109151_().m_168771_(p_109367_, p_109368_, integer, mapitemsaveddata, false, p_109369_);
      }

   }

   private void m_109346_(PoseStack p_109347_, MultiBufferSource p_109348_, int p_109349_, float p_109350_, float p_109351_, HumanoidArm p_109352_) {
      boolean flag = p_109352_ != HumanoidArm.LEFT;
      float f = flag ? 1.0F : -1.0F;
      float f1 = Mth.m_14116_(p_109351_);
      float f2 = -0.3F * Mth.m_14031_(f1 * (float)Math.PI);
      float f3 = 0.4F * Mth.m_14031_(f1 * ((float)Math.PI * 2F));
      float f4 = -0.4F * Mth.m_14031_(p_109351_ * (float)Math.PI);
      p_109347_.m_252880_(f * (f2 + 0.64000005F), f3 + -0.6F + p_109350_ * -0.6F, f4 + -0.71999997F);
      p_109347_.m_252781_(Axis.f_252436_.m_252977_(f * 45.0F));
      float f5 = Mth.m_14031_(p_109351_ * p_109351_ * (float)Math.PI);
      float f6 = Mth.m_14031_(f1 * (float)Math.PI);
      p_109347_.m_252781_(Axis.f_252436_.m_252977_(f * f6 * 70.0F));
      p_109347_.m_252781_(Axis.f_252403_.m_252977_(f * f5 * -20.0F));
      AbstractClientPlayer abstractclientplayer = this.f_109299_.f_91074_;
      RenderSystem.setShaderTexture(0, abstractclientplayer.m_108560_());
      p_109347_.m_252880_(f * -1.0F, 3.6F, 3.5F);
      p_109347_.m_252781_(Axis.f_252403_.m_252977_(f * 120.0F));
      p_109347_.m_252781_(Axis.f_252529_.m_252977_(200.0F));
      p_109347_.m_252781_(Axis.f_252436_.m_252977_(f * -135.0F));
      p_109347_.m_252880_(f * 5.6F, 0.0F, 0.0F);
      PlayerRenderer playerrenderer = (PlayerRenderer)this.f_109306_.<AbstractClientPlayer>m_114382_(abstractclientplayer);
      if (flag) {
         playerrenderer.m_117770_(p_109347_, p_109348_, p_109349_, abstractclientplayer);
      } else {
         playerrenderer.m_117813_(p_109347_, p_109348_, p_109349_, abstractclientplayer);
      }

   }

   private void m_109330_(PoseStack p_109331_, float p_109332_, HumanoidArm p_109333_, ItemStack p_109334_) {
      float f = (float)this.f_109299_.f_91074_.m_21212_() - p_109332_ + 1.0F;
      float f1 = f / (float)p_109334_.m_41779_();
      if (f1 < 0.8F) {
         float f2 = Mth.m_14154_(Mth.m_14089_(f / 4.0F * (float)Math.PI) * 0.1F);
         p_109331_.m_252880_(0.0F, f2, 0.0F);
      }

      float f3 = 1.0F - (float)Math.pow((double)f1, 27.0D);
      int i = p_109333_ == HumanoidArm.RIGHT ? 1 : -1;
      p_109331_.m_252880_(f3 * 0.6F * (float)i, f3 * -0.5F, f3 * 0.0F);
      p_109331_.m_252781_(Axis.f_252436_.m_252977_((float)i * f3 * 90.0F));
      p_109331_.m_252781_(Axis.f_252529_.m_252977_(f3 * 10.0F));
      p_109331_.m_252781_(Axis.f_252403_.m_252977_((float)i * f3 * 30.0F));
   }

   private void m_271982_(PoseStack p_273513_, float p_273245_, HumanoidArm p_273726_, ItemStack p_272809_, float p_273333_) {
      this.m_109382_(p_273513_, p_273726_, p_273333_);
      float f = (float)(this.f_109299_.f_91074_.m_21212_() % 10);
      float f1 = f - p_273245_ + 1.0F;
      float f2 = 1.0F - f1 / 10.0F;
      float f3 = -90.0F;
      float f4 = 60.0F;
      float f5 = 150.0F;
      float f6 = -15.0F;
      int i = 2;
      float f7 = -15.0F + 75.0F * Mth.m_14089_(f2 * 2.0F * (float)Math.PI);
      if (p_273726_ != HumanoidArm.RIGHT) {
         p_273513_.m_85837_(0.1D, 0.83D, 0.35D);
         p_273513_.m_252781_(Axis.f_252529_.m_252977_(-80.0F));
         p_273513_.m_252781_(Axis.f_252436_.m_252977_(-90.0F));
         p_273513_.m_252781_(Axis.f_252529_.m_252977_(f7));
         p_273513_.m_85837_(-0.3D, 0.22D, 0.35D);
      } else {
         p_273513_.m_85837_(-0.25D, 0.22D, 0.35D);
         p_273513_.m_252781_(Axis.f_252529_.m_252977_(-80.0F));
         p_273513_.m_252781_(Axis.f_252436_.m_252977_(90.0F));
         p_273513_.m_252781_(Axis.f_252403_.m_252977_(0.0F));
         p_273513_.m_252781_(Axis.f_252529_.m_252977_(f7));
      }

   }

   private void m_109335_(PoseStack p_109336_, HumanoidArm p_109337_, float p_109338_) {
      int i = p_109337_ == HumanoidArm.RIGHT ? 1 : -1;
      float f = Mth.m_14031_(p_109338_ * p_109338_ * (float)Math.PI);
      p_109336_.m_252781_(Axis.f_252436_.m_252977_((float)i * (45.0F + f * -20.0F)));
      float f1 = Mth.m_14031_(Mth.m_14116_(p_109338_) * (float)Math.PI);
      p_109336_.m_252781_(Axis.f_252403_.m_252977_((float)i * f1 * -20.0F));
      p_109336_.m_252781_(Axis.f_252529_.m_252977_(f1 * -80.0F));
      p_109336_.m_252781_(Axis.f_252436_.m_252977_((float)i * -45.0F));
   }

   private void m_109382_(PoseStack p_109383_, HumanoidArm p_109384_, float p_109385_) {
      int i = p_109384_ == HumanoidArm.RIGHT ? 1 : -1;
      p_109383_.m_252880_((float)i * 0.56F, -0.52F + p_109385_ * -0.6F, -0.72F);
   }

   public void m_109314_(float p_109315_, PoseStack p_109316_, MultiBufferSource.BufferSource p_109317_, LocalPlayer p_109318_, int p_109319_) {
      float f = p_109318_.m_21324_(p_109315_);
      InteractionHand interactionhand = MoreObjects.firstNonNull(p_109318_.f_20912_, InteractionHand.MAIN_HAND);
      float f1 = Mth.m_14179_(p_109315_, p_109318_.f_19860_, p_109318_.m_146909_());
      ItemInHandRenderer.HandRenderSelection iteminhandrenderer$handrenderselection = m_172914_(p_109318_);
      float f2 = Mth.m_14179_(p_109315_, p_109318_.f_108588_, p_109318_.f_108586_);
      float f3 = Mth.m_14179_(p_109315_, p_109318_.f_108587_, p_109318_.f_108585_);
      p_109316_.m_252781_(Axis.f_252529_.m_252977_((p_109318_.m_5686_(p_109315_) - f2) * 0.1F));
      p_109316_.m_252781_(Axis.f_252436_.m_252977_((p_109318_.m_5675_(p_109315_) - f3) * 0.1F));
      if (iteminhandrenderer$handrenderselection.f_172921_) {
         float f4 = interactionhand == InteractionHand.MAIN_HAND ? f : 0.0F;
         float f5 = 1.0F - Mth.m_14179_(p_109315_, this.f_109303_, this.f_109302_);
         this.m_109371_(p_109318_, p_109315_, f1, InteractionHand.MAIN_HAND, f4, this.f_109300_, f5, p_109316_, p_109317_, p_109319_);
      }

      if (iteminhandrenderer$handrenderselection.f_172922_) {
         float f6 = interactionhand == InteractionHand.OFF_HAND ? f : 0.0F;
         float f7 = 1.0F - Mth.m_14179_(p_109315_, this.f_109305_, this.f_109304_);
         this.m_109371_(p_109318_, p_109315_, f1, InteractionHand.OFF_HAND, f6, this.f_109301_, f7, p_109316_, p_109317_, p_109319_);
      }

      p_109317_.m_109911_();
   }

   @VisibleForTesting
   static ItemInHandRenderer.HandRenderSelection m_172914_(LocalPlayer p_172915_) {
      ItemStack itemstack = p_172915_.m_21205_();
      ItemStack itemstack1 = p_172915_.m_21206_();
      boolean flag = itemstack.m_150930_(Items.f_42411_) || itemstack1.m_150930_(Items.f_42411_);
      boolean flag1 = itemstack.m_150930_(Items.f_42717_) || itemstack1.m_150930_(Items.f_42717_);
      if (!flag && !flag1) {
         return ItemInHandRenderer.HandRenderSelection.RENDER_BOTH_HANDS;
      } else if (p_172915_.m_6117_()) {
         return m_172916_(p_172915_);
      } else {
         return m_172912_(itemstack) ? ItemInHandRenderer.HandRenderSelection.RENDER_MAIN_HAND_ONLY : ItemInHandRenderer.HandRenderSelection.RENDER_BOTH_HANDS;
      }
   }

   private static ItemInHandRenderer.HandRenderSelection m_172916_(LocalPlayer p_172917_) {
      ItemStack itemstack = p_172917_.m_21211_();
      InteractionHand interactionhand = p_172917_.m_7655_();
      if (!itemstack.m_150930_(Items.f_42411_) && !itemstack.m_150930_(Items.f_42717_)) {
         return interactionhand == InteractionHand.MAIN_HAND && m_172912_(p_172917_.m_21206_()) ? ItemInHandRenderer.HandRenderSelection.RENDER_MAIN_HAND_ONLY : ItemInHandRenderer.HandRenderSelection.RENDER_BOTH_HANDS;
      } else {
         return ItemInHandRenderer.HandRenderSelection.m_172931_(interactionhand);
      }
   }

   private static boolean m_172912_(ItemStack p_172913_) {
      return p_172913_.m_150930_(Items.f_42717_) && CrossbowItem.m_40932_(p_172913_);
   }

   private void m_109371_(AbstractClientPlayer p_109372_, float p_109373_, float p_109374_, InteractionHand p_109375_, float p_109376_, ItemStack p_109377_, float p_109378_, PoseStack p_109379_, MultiBufferSource p_109380_, int p_109381_) {
      if (!p_109372_.m_150108_()) {
         boolean flag = p_109375_ == InteractionHand.MAIN_HAND;
         HumanoidArm humanoidarm = flag ? p_109372_.m_5737_() : p_109372_.m_5737_().m_20828_();
         p_109379_.m_85836_();
         if (p_109377_.m_41619_()) {
            if (flag && !p_109372_.m_20145_()) {
               this.m_109346_(p_109379_, p_109380_, p_109381_, p_109378_, p_109376_, humanoidarm);
            }
         } else if (p_109377_.m_150930_(Items.f_42573_)) {
            if (flag && this.f_109301_.m_41619_()) {
               this.m_109339_(p_109379_, p_109380_, p_109381_, p_109374_, p_109378_, p_109376_);
            } else {
               this.m_109353_(p_109379_, p_109380_, p_109381_, p_109378_, humanoidarm, p_109376_, p_109377_);
            }
         } else if (p_109377_.m_150930_(Items.f_42717_)) {
            boolean flag1 = CrossbowItem.m_40932_(p_109377_);
            boolean flag2 = humanoidarm == HumanoidArm.RIGHT;
            int i = flag2 ? 1 : -1;
            if (p_109372_.m_6117_() && p_109372_.m_21212_() > 0 && p_109372_.m_7655_() == p_109375_) {
               this.m_109382_(p_109379_, humanoidarm, p_109378_);
               p_109379_.m_252880_((float)i * -0.4785682F, -0.094387F, 0.05731531F);
               p_109379_.m_252781_(Axis.f_252529_.m_252977_(-11.935F));
               p_109379_.m_252781_(Axis.f_252436_.m_252977_((float)i * 65.3F));
               p_109379_.m_252781_(Axis.f_252403_.m_252977_((float)i * -9.785F));
               float f9 = (float)p_109377_.m_41779_() - ((float)this.f_109299_.f_91074_.m_21212_() - p_109373_ + 1.0F);
               float f13 = f9 / (float)CrossbowItem.m_40939_(p_109377_);
               if (f13 > 1.0F) {
                  f13 = 1.0F;
               }

               if (f13 > 0.1F) {
                  float f16 = Mth.m_14031_((f9 - 0.1F) * 1.3F);
                  float f3 = f13 - 0.1F;
                  float f4 = f16 * f3;
                  p_109379_.m_252880_(f4 * 0.0F, f4 * 0.004F, f4 * 0.0F);
               }

               p_109379_.m_252880_(f13 * 0.0F, f13 * 0.0F, f13 * 0.04F);
               p_109379_.m_85841_(1.0F, 1.0F, 1.0F + f13 * 0.2F);
               p_109379_.m_252781_(Axis.f_252392_.m_252977_((float)i * 45.0F));
            } else {
               float f = -0.4F * Mth.m_14031_(Mth.m_14116_(p_109376_) * (float)Math.PI);
               float f1 = 0.2F * Mth.m_14031_(Mth.m_14116_(p_109376_) * ((float)Math.PI * 2F));
               float f2 = -0.2F * Mth.m_14031_(p_109376_ * (float)Math.PI);
               p_109379_.m_252880_((float)i * f, f1, f2);
               this.m_109382_(p_109379_, humanoidarm, p_109378_);
               this.m_109335_(p_109379_, humanoidarm, p_109376_);
               if (flag1 && p_109376_ < 0.001F && flag) {
                  p_109379_.m_252880_((float)i * -0.641864F, 0.0F, 0.0F);
                  p_109379_.m_252781_(Axis.f_252436_.m_252977_((float)i * 10.0F));
               }
            }

            this.m_269530_(p_109372_, p_109377_, flag2 ? ItemDisplayContext.FIRST_PERSON_RIGHT_HAND : ItemDisplayContext.FIRST_PERSON_LEFT_HAND, !flag2, p_109379_, p_109380_, p_109381_);
         } else {
            boolean flag3 = humanoidarm == HumanoidArm.RIGHT;
            if (p_109372_.m_6117_() && p_109372_.m_21212_() > 0 && p_109372_.m_7655_() == p_109375_) {
               int k = flag3 ? 1 : -1;
               switch (p_109377_.m_41780_()) {
                  case NONE:
                     this.m_109382_(p_109379_, humanoidarm, p_109378_);
                     break;
                  case EAT:
                  case DRINK:
                     this.m_109330_(p_109379_, p_109373_, humanoidarm, p_109377_);
                     this.m_109382_(p_109379_, humanoidarm, p_109378_);
                     break;
                  case BLOCK:
                     this.m_109382_(p_109379_, humanoidarm, p_109378_);
                     break;
                  case BOW:
                     this.m_109382_(p_109379_, humanoidarm, p_109378_);
                     p_109379_.m_252880_((float)k * -0.2785682F, 0.18344387F, 0.15731531F);
                     p_109379_.m_252781_(Axis.f_252529_.m_252977_(-13.935F));
                     p_109379_.m_252781_(Axis.f_252436_.m_252977_((float)k * 35.3F));
                     p_109379_.m_252781_(Axis.f_252403_.m_252977_((float)k * -9.785F));
                     float f8 = (float)p_109377_.m_41779_() - ((float)this.f_109299_.f_91074_.m_21212_() - p_109373_ + 1.0F);
                     float f12 = f8 / 20.0F;
                     f12 = (f12 * f12 + f12 * 2.0F) / 3.0F;
                     if (f12 > 1.0F) {
                        f12 = 1.0F;
                     }

                     if (f12 > 0.1F) {
                        float f15 = Mth.m_14031_((f8 - 0.1F) * 1.3F);
                        float f18 = f12 - 0.1F;
                        float f20 = f15 * f18;
                        p_109379_.m_252880_(f20 * 0.0F, f20 * 0.004F, f20 * 0.0F);
                     }

                     p_109379_.m_252880_(f12 * 0.0F, f12 * 0.0F, f12 * 0.04F);
                     p_109379_.m_85841_(1.0F, 1.0F, 1.0F + f12 * 0.2F);
                     p_109379_.m_252781_(Axis.f_252392_.m_252977_((float)k * 45.0F));
                     break;
                  case SPEAR:
                     this.m_109382_(p_109379_, humanoidarm, p_109378_);
                     p_109379_.m_252880_((float)k * -0.5F, 0.7F, 0.1F);
                     p_109379_.m_252781_(Axis.f_252529_.m_252977_(-55.0F));
                     p_109379_.m_252781_(Axis.f_252436_.m_252977_((float)k * 35.3F));
                     p_109379_.m_252781_(Axis.f_252403_.m_252977_((float)k * -9.785F));
                     float f7 = (float)p_109377_.m_41779_() - ((float)this.f_109299_.f_91074_.m_21212_() - p_109373_ + 1.0F);
                     float f11 = f7 / 10.0F;
                     if (f11 > 1.0F) {
                        f11 = 1.0F;
                     }

                     if (f11 > 0.1F) {
                        float f14 = Mth.m_14031_((f7 - 0.1F) * 1.3F);
                        float f17 = f11 - 0.1F;
                        float f19 = f14 * f17;
                        p_109379_.m_252880_(f19 * 0.0F, f19 * 0.004F, f19 * 0.0F);
                     }

                     p_109379_.m_252880_(0.0F, 0.0F, f11 * 0.2F);
                     p_109379_.m_85841_(1.0F, 1.0F, 1.0F + f11 * 0.2F);
                     p_109379_.m_252781_(Axis.f_252392_.m_252977_((float)k * 45.0F));
                     break;
                  case BRUSH:
                     this.m_271982_(p_109379_, p_109373_, humanoidarm, p_109377_, p_109378_);
               }
            } else if (p_109372_.m_21209_()) {
               this.m_109382_(p_109379_, humanoidarm, p_109378_);
               int j = flag3 ? 1 : -1;
               p_109379_.m_252880_((float)j * -0.4F, 0.8F, 0.3F);
               p_109379_.m_252781_(Axis.f_252436_.m_252977_((float)j * 65.0F));
               p_109379_.m_252781_(Axis.f_252403_.m_252977_((float)j * -85.0F));
            } else {
               float f5 = -0.4F * Mth.m_14031_(Mth.m_14116_(p_109376_) * (float)Math.PI);
               float f6 = 0.2F * Mth.m_14031_(Mth.m_14116_(p_109376_) * ((float)Math.PI * 2F));
               float f10 = -0.2F * Mth.m_14031_(p_109376_ * (float)Math.PI);
               int l = flag3 ? 1 : -1;
               p_109379_.m_252880_((float)l * f5, f6, f10);
               this.m_109382_(p_109379_, humanoidarm, p_109378_);
               this.m_109335_(p_109379_, humanoidarm, p_109376_);
            }

            this.m_269530_(p_109372_, p_109377_, flag3 ? ItemDisplayContext.FIRST_PERSON_RIGHT_HAND : ItemDisplayContext.FIRST_PERSON_LEFT_HAND, !flag3, p_109379_, p_109380_, p_109381_);
         }

         p_109379_.m_85849_();
      }
   }

   public void m_109311_() {
      this.f_109303_ = this.f_109302_;
      this.f_109305_ = this.f_109304_;
      LocalPlayer localplayer = this.f_109299_.f_91074_;
      ItemStack itemstack = localplayer.m_21205_();
      ItemStack itemstack1 = localplayer.m_21206_();
      if (ItemStack.m_41728_(this.f_109300_, itemstack)) {
         this.f_109300_ = itemstack;
      }

      if (ItemStack.m_41728_(this.f_109301_, itemstack1)) {
         this.f_109301_ = itemstack1;
      }

      if (localplayer.m_108637_()) {
         this.f_109302_ = Mth.m_14036_(this.f_109302_ - 0.4F, 0.0F, 1.0F);
         this.f_109304_ = Mth.m_14036_(this.f_109304_ - 0.4F, 0.0F, 1.0F);
      } else {
         float f = localplayer.m_36403_(1.0F);
         this.f_109302_ += Mth.m_14036_((this.f_109300_ == itemstack ? f * f * f : 0.0F) - this.f_109302_, -0.4F, 0.4F);
         this.f_109304_ += Mth.m_14036_((float)(this.f_109301_ == itemstack1 ? 1 : 0) - this.f_109304_, -0.4F, 0.4F);
      }

      if (this.f_109302_ < 0.1F) {
         this.f_109300_ = itemstack;
      }

      if (this.f_109304_ < 0.1F) {
         this.f_109301_ = itemstack1;
      }

   }

   public void m_109320_(InteractionHand p_109321_) {
      if (p_109321_ == InteractionHand.MAIN_HAND) {
         this.f_109302_ = 0.0F;
      } else {
         this.f_109304_ = 0.0F;
      }

   }

   @OnlyIn(Dist.CLIENT)
   @VisibleForTesting
   static enum HandRenderSelection {
      RENDER_BOTH_HANDS(true, true),
      RENDER_MAIN_HAND_ONLY(true, false),
      RENDER_OFF_HAND_ONLY(false, true);

      final boolean f_172921_;
      final boolean f_172922_;

      private HandRenderSelection(boolean p_172928_, boolean p_172929_) {
         this.f_172921_ = p_172928_;
         this.f_172922_ = p_172929_;
      }

      public static ItemInHandRenderer.HandRenderSelection m_172931_(InteractionHand p_172932_) {
         return p_172932_ == InteractionHand.MAIN_HAND ? RENDER_MAIN_HAND_ONLY : RENDER_OFF_HAND_ONLY;
      }
   }
}
