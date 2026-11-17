package net.minecraft.client.renderer.entity.player;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.model.HumanoidArmorModel;
import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.model.HumanoidModel.ArmPose;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider.Context;
import net.minecraft.client.renderer.entity.layers.ArrowLayer;
import net.minecraft.client.renderer.entity.layers.BeeStingerLayer;
import net.minecraft.client.renderer.entity.layers.CapeLayer;
import net.minecraft.client.renderer.entity.layers.CustomHeadLayer;
import net.minecraft.client.renderer.entity.layers.Deadmau5EarsLayer;
import net.minecraft.client.renderer.entity.layers.ElytraLayer;
import net.minecraft.client.renderer.entity.layers.HumanoidArmorLayer;
import net.minecraft.client.renderer.entity.layers.ParrotOnShoulderLayer;
import net.minecraft.client.renderer.entity.layers.PlayerItemInHandLayer;
import net.minecraft.client.renderer.entity.layers.SpinAttackEffectLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.network.chat.CommonComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.numbers.StyledFormat;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.player.PlayerModelPart;
import net.minecraft.world.item.CrossbowItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.UseAnim;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.scores.DisplaySlot;
import net.minecraft.world.scores.Objective;
import net.minecraft.world.scores.ReadOnlyScoreInfo;
import net.minecraft.world.scores.Scoreboard;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class PlayerRenderer extends LivingEntityRenderer<AbstractClientPlayer, PlayerModel<AbstractClientPlayer>> {
   public PlayerRenderer(Context p_174557_, boolean p_174558_) {
      super(p_174557_, new PlayerModel(p_174557_.m_174023_(p_174558_ ? ModelLayers.f_171166_ : ModelLayers.f_171162_), p_174558_), 0.5F);
      this.m_115326_(
         new HumanoidArmorLayer(
            this,
            new HumanoidArmorModel(p_174557_.m_174023_(p_174558_ ? ModelLayers.f_171167_ : ModelLayers.f_171164_)),
            new HumanoidArmorModel(p_174557_.m_174023_(p_174558_ ? ModelLayers.f_171168_ : ModelLayers.f_171165_)),
            p_174557_.m_266367_()
         )
      );
      this.m_115326_(new PlayerItemInHandLayer(this, p_174557_.m_234598_()));
      this.m_115326_(new ArrowLayer(p_174557_, this));
      this.m_115326_(new Deadmau5EarsLayer(this));
      this.m_115326_(new CapeLayer(this));
      this.m_115326_(new CustomHeadLayer(this, p_174557_.m_174027_(), p_174557_.m_234598_()));
      this.m_115326_(new ElytraLayer(this, p_174557_.m_174027_()));
      this.m_115326_(new ParrotOnShoulderLayer(this, p_174557_.m_174027_()));
      this.m_115326_(new SpinAttackEffectLayer(this, p_174557_.m_174027_()));
      this.m_115326_(new BeeStingerLayer(this));
   }

   public void m_7392_(AbstractClientPlayer p_117788_, float p_117789_, float p_117790_, PoseStack p_117791_, MultiBufferSource p_117792_, int p_117793_) {
      this.m_117818_(p_117788_);
      super.m_7392_(p_117788_, p_117789_, p_117790_, p_117791_, p_117792_, p_117793_);
   }

   public Vec3 m_7860_(AbstractClientPlayer p_117785_, float p_117786_) {
      return p_117785_.m_6047_() ? new Vec3(0.0, -0.125, 0.0) : super.m_7860_(p_117785_, p_117786_);
   }

   private void m_117818_(AbstractClientPlayer p_117819_) {
      PlayerModel<AbstractClientPlayer> $$1 = (PlayerModel<AbstractClientPlayer>)this.m_7200_();
      if (p_117819_.m_5833_()) {
         $$1.m_8009_(false);
         $$1.f_102808_.f_104207_ = true;
         $$1.f_102809_.f_104207_ = true;
      } else {
         $$1.m_8009_(true);
         $$1.f_102809_.f_104207_ = p_117819_.m_36170_(PlayerModelPart.HAT);
         $$1.f_103378_.f_104207_ = p_117819_.m_36170_(PlayerModelPart.JACKET);
         $$1.f_103376_.f_104207_ = p_117819_.m_36170_(PlayerModelPart.LEFT_PANTS_LEG);
         $$1.f_103377_.f_104207_ = p_117819_.m_36170_(PlayerModelPart.RIGHT_PANTS_LEG);
         $$1.f_103374_.f_104207_ = p_117819_.m_36170_(PlayerModelPart.LEFT_SLEEVE);
         $$1.f_103375_.f_104207_ = p_117819_.m_36170_(PlayerModelPart.RIGHT_SLEEVE);
         $$1.f_102817_ = p_117819_.m_6047_();
         ArmPose $$2 = m_117794_(p_117819_, InteractionHand.MAIN_HAND);
         ArmPose $$3 = m_117794_(p_117819_, InteractionHand.OFF_HAND);
         if ($$2.m_102897_()) {
            $$3 = p_117819_.m_21206_().m_41619_() ? ArmPose.EMPTY : ArmPose.ITEM;
         }

         if (p_117819_.m_5737_() == HumanoidArm.RIGHT) {
            $$1.f_102816_ = $$2;
            $$1.f_102815_ = $$3;
         } else {
            $$1.f_102816_ = $$3;
            $$1.f_102815_ = $$2;
         }
      }
   }

   private static ArmPose m_117794_(AbstractClientPlayer p_117795_, InteractionHand p_117796_) {
      ItemStack $$2 = p_117795_.m_21120_(p_117796_);
      if ($$2.m_41619_()) {
         return ArmPose.EMPTY;
      } else {
         if (p_117795_.m_7655_() == p_117796_ && p_117795_.m_21212_() > 0) {
            UseAnim $$3 = $$2.m_41780_();
            if ($$3 == UseAnim.BLOCK) {
               return ArmPose.BLOCK;
            }

            if ($$3 == UseAnim.BOW) {
               return ArmPose.BOW_AND_ARROW;
            }

            if ($$3 == UseAnim.SPEAR) {
               return ArmPose.THROW_SPEAR;
            }

            if ($$3 == UseAnim.CROSSBOW && p_117796_ == p_117795_.m_7655_()) {
               return ArmPose.CROSSBOW_CHARGE;
            }

            if ($$3 == UseAnim.SPYGLASS) {
               return ArmPose.SPYGLASS;
            }

            if ($$3 == UseAnim.TOOT_HORN) {
               return ArmPose.TOOT_HORN;
            }

            if ($$3 == UseAnim.BRUSH) {
               return ArmPose.BRUSH;
            }
         } else if (!p_117795_.f_20911_ && $$2.m_150930_(Items.f_42717_) && CrossbowItem.m_40932_($$2)) {
            return ArmPose.CROSSBOW_HOLD;
         }

         return ArmPose.ITEM;
      }
   }

   public ResourceLocation m_5478_(AbstractClientPlayer p_117783_) {
      return p_117783_.m_294544_().f_290339_();
   }

   protected void m_7546_(AbstractClientPlayer p_117798_, PoseStack p_117799_, float p_117800_) {
      float $$3 = 0.9375F;
      p_117799_.m_85841_(0.9375F, 0.9375F, 0.9375F);
   }

   protected void m_7649_(AbstractClientPlayer p_117808_, Component p_117809_, PoseStack p_117810_, MultiBufferSource p_117811_, int p_117812_) {
      double $$5 = this.f_114476_.m_114471_(p_117808_);
      p_117810_.m_85836_();
      if ($$5 < 100.0) {
         Scoreboard $$6 = p_117808_.m_36329_();
         Objective $$7 = $$6.m_83416_(DisplaySlot.BELOW_NAME);
         if ($$7 != null) {
            ReadOnlyScoreInfo $$8 = $$6.m_305759_(p_117808_, $$7);
            Component $$9 = ReadOnlyScoreInfo.m_305849_($$8, $$7.m_305063_(StyledFormat.f_302669_));
            super.m_7649_(
               p_117808_, Component.m_237119_().m_7220_($$9).m_7220_(CommonComponents.f_263701_).m_7220_($$7.m_83322_()), p_117810_, p_117811_, p_117812_
            );
            p_117810_.m_252880_(0.0F, 9.0F * 1.15F * 0.025F, 0.0F);
         }
      }

      super.m_7649_(p_117808_, p_117809_, p_117810_, p_117811_, p_117812_);
      p_117810_.m_85849_();
   }

   public void m_117770_(PoseStack p_117771_, MultiBufferSource p_117772_, int p_117773_, AbstractClientPlayer p_117774_) {
      this.m_117775_(p_117771_, p_117772_, p_117773_, p_117774_, ((PlayerModel)this.f_115290_).f_102811_, ((PlayerModel)this.f_115290_).f_103375_);
   }

   public void m_117813_(PoseStack p_117814_, MultiBufferSource p_117815_, int p_117816_, AbstractClientPlayer p_117817_) {
      this.m_117775_(p_117814_, p_117815_, p_117816_, p_117817_, ((PlayerModel)this.f_115290_).f_102812_, ((PlayerModel)this.f_115290_).f_103374_);
   }

   private void m_117775_(
      PoseStack p_117776_, MultiBufferSource p_117777_, int p_117778_, AbstractClientPlayer p_117779_, ModelPart p_117780_, ModelPart p_117781_
   ) {
      PlayerModel<AbstractClientPlayer> $$6 = (PlayerModel<AbstractClientPlayer>)this.m_7200_();
      this.m_117818_(p_117779_);
      $$6.f_102608_ = 0.0F;
      $$6.f_102817_ = false;
      $$6.f_102818_ = 0.0F;
      $$6.m_6973_(p_117779_, 0.0F, 0.0F, 0.0F, 0.0F, 0.0F);
      p_117780_.f_104203_ = 0.0F;
      ResourceLocation $$7 = p_117779_.m_294544_().f_290339_();
      p_117780_.m_104301_(p_117776_, p_117777_.m_6299_(RenderType.m_110446_($$7)), p_117778_, OverlayTexture.f_118083_);
      p_117781_.f_104203_ = 0.0F;
      p_117781_.m_104301_(p_117776_, p_117777_.m_6299_(RenderType.m_110473_($$7)), p_117778_, OverlayTexture.f_118083_);
   }

   protected void m_7523_(AbstractClientPlayer p_117802_, PoseStack p_117803_, float p_117804_, float p_117805_, float p_117806_) {
      float $$5 = p_117802_.m_20998_(p_117806_);
      float $$6 = p_117802_.m_5686_(p_117806_);
      if (p_117802_.m_21255_()) {
         super.m_7523_(p_117802_, p_117803_, p_117804_, p_117805_, p_117806_);
         float $$7 = (float)p_117802_.m_21256_() + p_117806_;
         float $$8 = Mth.m_14036_($$7 * $$7 / 100.0F, 0.0F, 1.0F);
         if (!p_117802_.m_21209_()) {
            p_117803_.m_252781_(Axis.f_252529_.m_252977_($$8 * (-90.0F - $$6)));
         }

         Vec3 $$9 = p_117802_.m_20252_(p_117806_);
         Vec3 $$10 = p_117802_.m_272267_(p_117806_);
         double $$11 = $$10.m_165925_();
         double $$12 = $$9.m_165925_();
         if ($$11 > 0.0 && $$12 > 0.0) {
            double $$13 = ($$10.f_82479_ * $$9.f_82479_ + $$10.f_82481_ * $$9.f_82481_) / Math.sqrt($$11 * $$12);
            double $$14 = $$10.f_82479_ * $$9.f_82481_ - $$10.f_82481_ * $$9.f_82479_;
            p_117803_.m_252781_(Axis.f_252436_.m_252961_((float)(Math.signum($$14) * Math.acos($$13))));
         }
      } else if ($$5 > 0.0F) {
         super.m_7523_(p_117802_, p_117803_, p_117804_, p_117805_, p_117806_);
         float $$15 = p_117802_.m_20069_() ? -90.0F - $$6 : -90.0F;
         float $$16 = Mth.m_14179_($$5, 0.0F, $$15);
         p_117803_.m_252781_(Axis.f_252529_.m_252977_($$16));
         if (p_117802_.m_6067_()) {
            p_117803_.m_252880_(0.0F, -1.0F, 0.3F);
         }
      } else {
         super.m_7523_(p_117802_, p_117803_, p_117804_, p_117805_, p_117806_);
      }
   }
}
