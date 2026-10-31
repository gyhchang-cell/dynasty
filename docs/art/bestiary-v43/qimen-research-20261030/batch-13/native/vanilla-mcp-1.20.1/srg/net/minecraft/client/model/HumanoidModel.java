package net.minecraft.client.model;

import com.google.common.collect.ImmutableList;
import com.mojang.blaze3d.vertex.PoseStack;
import java.util.function.Function;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class HumanoidModel<T extends LivingEntity> extends AgeableListModel<T> implements ArmedModel, HeadedModel {
   public static final float f_170673_ = 0.25F;
   public static final float f_170674_ = 0.5F;
   public static final float f_268570_ = -0.1F;
   private static final float f_268560_ = 0.005F;
   private static final float f_170671_ = 0.2617994F;
   private static final float f_170672_ = 1.9198622F;
   private static final float f_170675_ = 0.2617994F;
   public static final float f_233401_ = 1.4835298F;
   public static final float f_233402_ = ((float)Math.PI / 6F);
   public final ModelPart f_102808_;
   public final ModelPart f_102809_;
   public final ModelPart f_102810_;
   public final ModelPart f_102811_;
   public final ModelPart f_102812_;
   public final ModelPart f_102813_;
   public final ModelPart f_102814_;
   public HumanoidModel.ArmPose f_102815_ = HumanoidModel.ArmPose.EMPTY;
   public HumanoidModel.ArmPose f_102816_ = HumanoidModel.ArmPose.EMPTY;
   public boolean f_102817_;
   public float f_102818_;

   public HumanoidModel(ModelPart p_170677_) {
      this(p_170677_, RenderType::m_110458_);
   }

   public HumanoidModel(ModelPart p_170679_, Function<ResourceLocation, RenderType> p_170680_) {
      super(p_170680_, true, 16.0F, 0.0F, 2.0F, 2.0F, 24.0F);
      this.f_102808_ = p_170679_.m_171324_("head");
      this.f_102809_ = p_170679_.m_171324_("hat");
      this.f_102810_ = p_170679_.m_171324_("body");
      this.f_102811_ = p_170679_.m_171324_("right_arm");
      this.f_102812_ = p_170679_.m_171324_("left_arm");
      this.f_102813_ = p_170679_.m_171324_("right_leg");
      this.f_102814_ = p_170679_.m_171324_("left_leg");
   }

   public static MeshDefinition m_170681_(CubeDeformation p_170682_, float p_170683_) {
      MeshDefinition meshdefinition = new MeshDefinition();
      PartDefinition partdefinition = meshdefinition.m_171576_();
      partdefinition.m_171599_("head", CubeListBuilder.m_171558_().m_171514_(0, 0).m_171488_(-4.0F, -8.0F, -4.0F, 8.0F, 8.0F, 8.0F, p_170682_), PartPose.m_171419_(0.0F, 0.0F + p_170683_, 0.0F));
      partdefinition.m_171599_("hat", CubeListBuilder.m_171558_().m_171514_(32, 0).m_171488_(-4.0F, -8.0F, -4.0F, 8.0F, 8.0F, 8.0F, p_170682_.m_171469_(0.5F)), PartPose.m_171419_(0.0F, 0.0F + p_170683_, 0.0F));
      partdefinition.m_171599_("body", CubeListBuilder.m_171558_().m_171514_(16, 16).m_171488_(-4.0F, 0.0F, -2.0F, 8.0F, 12.0F, 4.0F, p_170682_), PartPose.m_171419_(0.0F, 0.0F + p_170683_, 0.0F));
      partdefinition.m_171599_("right_arm", CubeListBuilder.m_171558_().m_171514_(40, 16).m_171488_(-3.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, p_170682_), PartPose.m_171419_(-5.0F, 2.0F + p_170683_, 0.0F));
      partdefinition.m_171599_("left_arm", CubeListBuilder.m_171558_().m_171514_(40, 16).m_171480_().m_171488_(-1.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, p_170682_), PartPose.m_171419_(5.0F, 2.0F + p_170683_, 0.0F));
      partdefinition.m_171599_("right_leg", CubeListBuilder.m_171558_().m_171514_(0, 16).m_171488_(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, p_170682_), PartPose.m_171419_(-1.9F, 12.0F + p_170683_, 0.0F));
      partdefinition.m_171599_("left_leg", CubeListBuilder.m_171558_().m_171514_(0, 16).m_171480_().m_171488_(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, p_170682_), PartPose.m_171419_(1.9F, 12.0F + p_170683_, 0.0F));
      return meshdefinition;
   }

   protected Iterable<ModelPart> m_5607_() {
      return ImmutableList.of(this.f_102808_);
   }

   protected Iterable<ModelPart> m_5608_() {
      return ImmutableList.of(this.f_102810_, this.f_102811_, this.f_102812_, this.f_102813_, this.f_102814_, this.f_102809_);
   }

   public void m_6839_(T p_102861_, float p_102862_, float p_102863_, float p_102864_) {
      this.f_102818_ = p_102861_.m_20998_(p_102864_);
      super.m_6839_(p_102861_, p_102862_, p_102863_, p_102864_);
   }

   public void m_6973_(T p_102866_, float p_102867_, float p_102868_, float p_102869_, float p_102870_, float p_102871_) {
      boolean flag = p_102866_.m_21256_() > 4;
      boolean flag1 = p_102866_.m_6067_();
      this.f_102808_.f_104204_ = p_102870_ * ((float)Math.PI / 180F);
      if (flag) {
         this.f_102808_.f_104203_ = (-(float)Math.PI / 4F);
      } else if (this.f_102818_ > 0.0F) {
         if (flag1) {
            this.f_102808_.f_104203_ = this.m_102835_(this.f_102818_, this.f_102808_.f_104203_, (-(float)Math.PI / 4F));
         } else {
            this.f_102808_.f_104203_ = this.m_102835_(this.f_102818_, this.f_102808_.f_104203_, p_102871_ * ((float)Math.PI / 180F));
         }
      } else {
         this.f_102808_.f_104203_ = p_102871_ * ((float)Math.PI / 180F);
      }

      this.f_102810_.f_104204_ = 0.0F;
      this.f_102811_.f_104202_ = 0.0F;
      this.f_102811_.f_104200_ = -5.0F;
      this.f_102812_.f_104202_ = 0.0F;
      this.f_102812_.f_104200_ = 5.0F;
      float f = 1.0F;
      if (flag) {
         f = (float)p_102866_.m_20184_().m_82556_();
         f /= 0.2F;
         f *= f * f;
      }

      if (f < 1.0F) {
         f = 1.0F;
      }

      this.f_102811_.f_104203_ = Mth.m_14089_(p_102867_ * 0.6662F + (float)Math.PI) * 2.0F * p_102868_ * 0.5F / f;
      this.f_102812_.f_104203_ = Mth.m_14089_(p_102867_ * 0.6662F) * 2.0F * p_102868_ * 0.5F / f;
      this.f_102811_.f_104205_ = 0.0F;
      this.f_102812_.f_104205_ = 0.0F;
      this.f_102813_.f_104203_ = Mth.m_14089_(p_102867_ * 0.6662F) * 1.4F * p_102868_ / f;
      this.f_102814_.f_104203_ = Mth.m_14089_(p_102867_ * 0.6662F + (float)Math.PI) * 1.4F * p_102868_ / f;
      this.f_102813_.f_104204_ = 0.005F;
      this.f_102814_.f_104204_ = -0.005F;
      this.f_102813_.f_104205_ = 0.005F;
      this.f_102814_.f_104205_ = -0.005F;
      if (this.f_102609_) {
         this.f_102811_.f_104203_ += (-(float)Math.PI / 5F);
         this.f_102812_.f_104203_ += (-(float)Math.PI / 5F);
         this.f_102813_.f_104203_ = -1.4137167F;
         this.f_102813_.f_104204_ = ((float)Math.PI / 10F);
         this.f_102813_.f_104205_ = 0.07853982F;
         this.f_102814_.f_104203_ = -1.4137167F;
         this.f_102814_.f_104204_ = (-(float)Math.PI / 10F);
         this.f_102814_.f_104205_ = -0.07853982F;
      }

      this.f_102811_.f_104204_ = 0.0F;
      this.f_102812_.f_104204_ = 0.0F;
      boolean flag2 = p_102866_.m_5737_() == HumanoidArm.RIGHT;
      if (p_102866_.m_6117_()) {
         boolean flag3 = p_102866_.m_7655_() == InteractionHand.MAIN_HAND;
         if (flag3 == flag2) {
            this.m_102875_(p_102866_);
         } else {
            this.m_102878_(p_102866_);
         }
      } else {
         boolean flag4 = flag2 ? this.f_102815_.m_102897_() : this.f_102816_.m_102897_();
         if (flag2 != flag4) {
            this.m_102878_(p_102866_);
            this.m_102875_(p_102866_);
         } else {
            this.m_102875_(p_102866_);
            this.m_102878_(p_102866_);
         }
      }

      this.m_7884_(p_102866_, p_102869_);
      if (this.f_102817_) {
         this.f_102810_.f_104203_ = 0.5F;
         this.f_102811_.f_104203_ += 0.4F;
         this.f_102812_.f_104203_ += 0.4F;
         this.f_102813_.f_104202_ = 4.0F;
         this.f_102814_.f_104202_ = 4.0F;
         this.f_102813_.f_104201_ = 12.2F;
         this.f_102814_.f_104201_ = 12.2F;
         this.f_102808_.f_104201_ = 4.2F;
         this.f_102810_.f_104201_ = 3.2F;
         this.f_102812_.f_104201_ = 5.2F;
         this.f_102811_.f_104201_ = 5.2F;
      } else {
         this.f_102810_.f_104203_ = 0.0F;
         this.f_102813_.f_104202_ = 0.0F;
         this.f_102814_.f_104202_ = 0.0F;
         this.f_102813_.f_104201_ = 12.0F;
         this.f_102814_.f_104201_ = 12.0F;
         this.f_102808_.f_104201_ = 0.0F;
         this.f_102810_.f_104201_ = 0.0F;
         this.f_102812_.f_104201_ = 2.0F;
         this.f_102811_.f_104201_ = 2.0F;
      }

      if (this.f_102816_ != HumanoidModel.ArmPose.SPYGLASS) {
         AnimationUtils.m_170341_(this.f_102811_, p_102869_, 1.0F);
      }

      if (this.f_102815_ != HumanoidModel.ArmPose.SPYGLASS) {
         AnimationUtils.m_170341_(this.f_102812_, p_102869_, -1.0F);
      }

      if (this.f_102818_ > 0.0F) {
         float f5 = p_102867_ % 26.0F;
         HumanoidArm humanoidarm = this.m_102856_(p_102866_);
         float f1 = humanoidarm == HumanoidArm.RIGHT && this.f_102608_ > 0.0F ? 0.0F : this.f_102818_;
         float f2 = humanoidarm == HumanoidArm.LEFT && this.f_102608_ > 0.0F ? 0.0F : this.f_102818_;
         if (!p_102866_.m_6117_()) {
            if (f5 < 14.0F) {
               this.f_102812_.f_104203_ = this.m_102835_(f2, this.f_102812_.f_104203_, 0.0F);
               this.f_102811_.f_104203_ = Mth.m_14179_(f1, this.f_102811_.f_104203_, 0.0F);
               this.f_102812_.f_104204_ = this.m_102835_(f2, this.f_102812_.f_104204_, (float)Math.PI);
               this.f_102811_.f_104204_ = Mth.m_14179_(f1, this.f_102811_.f_104204_, (float)Math.PI);
               this.f_102812_.f_104205_ = this.m_102835_(f2, this.f_102812_.f_104205_, (float)Math.PI + 1.8707964F * this.m_102833_(f5) / this.m_102833_(14.0F));
               this.f_102811_.f_104205_ = Mth.m_14179_(f1, this.f_102811_.f_104205_, (float)Math.PI - 1.8707964F * this.m_102833_(f5) / this.m_102833_(14.0F));
            } else if (f5 >= 14.0F && f5 < 22.0F) {
               float f6 = (f5 - 14.0F) / 8.0F;
               this.f_102812_.f_104203_ = this.m_102835_(f2, this.f_102812_.f_104203_, ((float)Math.PI / 2F) * f6);
               this.f_102811_.f_104203_ = Mth.m_14179_(f1, this.f_102811_.f_104203_, ((float)Math.PI / 2F) * f6);
               this.f_102812_.f_104204_ = this.m_102835_(f2, this.f_102812_.f_104204_, (float)Math.PI);
               this.f_102811_.f_104204_ = Mth.m_14179_(f1, this.f_102811_.f_104204_, (float)Math.PI);
               this.f_102812_.f_104205_ = this.m_102835_(f2, this.f_102812_.f_104205_, 5.012389F - 1.8707964F * f6);
               this.f_102811_.f_104205_ = Mth.m_14179_(f1, this.f_102811_.f_104205_, 1.2707963F + 1.8707964F * f6);
            } else if (f5 >= 22.0F && f5 < 26.0F) {
               float f3 = (f5 - 22.0F) / 4.0F;
               this.f_102812_.f_104203_ = this.m_102835_(f2, this.f_102812_.f_104203_, ((float)Math.PI / 2F) - ((float)Math.PI / 2F) * f3);
               this.f_102811_.f_104203_ = Mth.m_14179_(f1, this.f_102811_.f_104203_, ((float)Math.PI / 2F) - ((float)Math.PI / 2F) * f3);
               this.f_102812_.f_104204_ = this.m_102835_(f2, this.f_102812_.f_104204_, (float)Math.PI);
               this.f_102811_.f_104204_ = Mth.m_14179_(f1, this.f_102811_.f_104204_, (float)Math.PI);
               this.f_102812_.f_104205_ = this.m_102835_(f2, this.f_102812_.f_104205_, (float)Math.PI);
               this.f_102811_.f_104205_ = Mth.m_14179_(f1, this.f_102811_.f_104205_, (float)Math.PI);
            }
         }

         float f7 = 0.3F;
         float f4 = 0.33333334F;
         this.f_102814_.f_104203_ = Mth.m_14179_(this.f_102818_, this.f_102814_.f_104203_, 0.3F * Mth.m_14089_(p_102867_ * 0.33333334F + (float)Math.PI));
         this.f_102813_.f_104203_ = Mth.m_14179_(this.f_102818_, this.f_102813_.f_104203_, 0.3F * Mth.m_14089_(p_102867_ * 0.33333334F));
      }

      this.f_102809_.m_104315_(this.f_102808_);
   }

   private void m_102875_(T p_102876_) {
      switch (this.f_102816_) {
         case EMPTY:
            this.f_102811_.f_104204_ = 0.0F;
            break;
         case BLOCK:
            this.f_102811_.f_104203_ = this.f_102811_.f_104203_ * 0.5F - 0.9424779F;
            this.f_102811_.f_104204_ = (-(float)Math.PI / 6F);
            break;
         case ITEM:
            this.f_102811_.f_104203_ = this.f_102811_.f_104203_ * 0.5F - ((float)Math.PI / 10F);
            this.f_102811_.f_104204_ = 0.0F;
            break;
         case THROW_SPEAR:
            this.f_102811_.f_104203_ = this.f_102811_.f_104203_ * 0.5F - (float)Math.PI;
            this.f_102811_.f_104204_ = 0.0F;
            break;
         case BOW_AND_ARROW:
            this.f_102811_.f_104204_ = -0.1F + this.f_102808_.f_104204_;
            this.f_102812_.f_104204_ = 0.1F + this.f_102808_.f_104204_ + 0.4F;
            this.f_102811_.f_104203_ = (-(float)Math.PI / 2F) + this.f_102808_.f_104203_;
            this.f_102812_.f_104203_ = (-(float)Math.PI / 2F) + this.f_102808_.f_104203_;
            break;
         case CROSSBOW_CHARGE:
            AnimationUtils.m_102086_(this.f_102811_, this.f_102812_, p_102876_, true);
            break;
         case CROSSBOW_HOLD:
            AnimationUtils.m_102097_(this.f_102811_, this.f_102812_, this.f_102808_, true);
            break;
         case BRUSH:
            this.f_102811_.f_104203_ = this.f_102811_.f_104203_ * 0.5F - ((float)Math.PI / 5F);
            this.f_102811_.f_104204_ = 0.0F;
            break;
         case SPYGLASS:
            this.f_102811_.f_104203_ = Mth.m_14036_(this.f_102808_.f_104203_ - 1.9198622F - (p_102876_.m_6047_() ? 0.2617994F : 0.0F), -2.4F, 3.3F);
            this.f_102811_.f_104204_ = this.f_102808_.f_104204_ - 0.2617994F;
            break;
         case TOOT_HORN:
            this.f_102811_.f_104203_ = Mth.m_14036_(this.f_102808_.f_104203_, -1.2F, 1.2F) - 1.4835298F;
            this.f_102811_.f_104204_ = this.f_102808_.f_104204_ - ((float)Math.PI / 6F);
      }

   }

   private void m_102878_(T p_102879_) {
      switch (this.f_102815_) {
         case EMPTY:
            this.f_102812_.f_104204_ = 0.0F;
            break;
         case BLOCK:
            this.f_102812_.f_104203_ = this.f_102812_.f_104203_ * 0.5F - 0.9424779F;
            this.f_102812_.f_104204_ = ((float)Math.PI / 6F);
            break;
         case ITEM:
            this.f_102812_.f_104203_ = this.f_102812_.f_104203_ * 0.5F - ((float)Math.PI / 10F);
            this.f_102812_.f_104204_ = 0.0F;
            break;
         case THROW_SPEAR:
            this.f_102812_.f_104203_ = this.f_102812_.f_104203_ * 0.5F - (float)Math.PI;
            this.f_102812_.f_104204_ = 0.0F;
            break;
         case BOW_AND_ARROW:
            this.f_102811_.f_104204_ = -0.1F + this.f_102808_.f_104204_ - 0.4F;
            this.f_102812_.f_104204_ = 0.1F + this.f_102808_.f_104204_;
            this.f_102811_.f_104203_ = (-(float)Math.PI / 2F) + this.f_102808_.f_104203_;
            this.f_102812_.f_104203_ = (-(float)Math.PI / 2F) + this.f_102808_.f_104203_;
            break;
         case CROSSBOW_CHARGE:
            AnimationUtils.m_102086_(this.f_102811_, this.f_102812_, p_102879_, false);
            break;
         case CROSSBOW_HOLD:
            AnimationUtils.m_102097_(this.f_102811_, this.f_102812_, this.f_102808_, false);
            break;
         case BRUSH:
            this.f_102812_.f_104203_ = this.f_102812_.f_104203_ * 0.5F - ((float)Math.PI / 5F);
            this.f_102812_.f_104204_ = 0.0F;
            break;
         case SPYGLASS:
            this.f_102812_.f_104203_ = Mth.m_14036_(this.f_102808_.f_104203_ - 1.9198622F - (p_102879_.m_6047_() ? 0.2617994F : 0.0F), -2.4F, 3.3F);
            this.f_102812_.f_104204_ = this.f_102808_.f_104204_ + 0.2617994F;
            break;
         case TOOT_HORN:
            this.f_102812_.f_104203_ = Mth.m_14036_(this.f_102808_.f_104203_, -1.2F, 1.2F) - 1.4835298F;
            this.f_102812_.f_104204_ = this.f_102808_.f_104204_ + ((float)Math.PI / 6F);
      }

   }

   protected void m_7884_(T p_102858_, float p_102859_) {
      if (!(this.f_102608_ <= 0.0F)) {
         HumanoidArm humanoidarm = this.m_102856_(p_102858_);
         ModelPart modelpart = this.m_102851_(humanoidarm);
         float f = this.f_102608_;
         this.f_102810_.f_104204_ = Mth.m_14031_(Mth.m_14116_(f) * ((float)Math.PI * 2F)) * 0.2F;
         if (humanoidarm == HumanoidArm.LEFT) {
            this.f_102810_.f_104204_ *= -1.0F;
         }

         this.f_102811_.f_104202_ = Mth.m_14031_(this.f_102810_.f_104204_) * 5.0F;
         this.f_102811_.f_104200_ = -Mth.m_14089_(this.f_102810_.f_104204_) * 5.0F;
         this.f_102812_.f_104202_ = -Mth.m_14031_(this.f_102810_.f_104204_) * 5.0F;
         this.f_102812_.f_104200_ = Mth.m_14089_(this.f_102810_.f_104204_) * 5.0F;
         this.f_102811_.f_104204_ += this.f_102810_.f_104204_;
         this.f_102812_.f_104204_ += this.f_102810_.f_104204_;
         this.f_102812_.f_104203_ += this.f_102810_.f_104204_;
         f = 1.0F - this.f_102608_;
         f *= f;
         f *= f;
         f = 1.0F - f;
         float f1 = Mth.m_14031_(f * (float)Math.PI);
         float f2 = Mth.m_14031_(this.f_102608_ * (float)Math.PI) * -(this.f_102808_.f_104203_ - 0.7F) * 0.75F;
         modelpart.f_104203_ -= f1 * 1.2F + f2;
         modelpart.f_104204_ += this.f_102810_.f_104204_ * 2.0F;
         modelpart.f_104205_ += Mth.m_14031_(this.f_102608_ * (float)Math.PI) * -0.4F;
      }
   }

   protected float m_102835_(float p_102836_, float p_102837_, float p_102838_) {
      float f = (p_102838_ - p_102837_) % ((float)Math.PI * 2F);
      if (f < -(float)Math.PI) {
         f += ((float)Math.PI * 2F);
      }

      if (f >= (float)Math.PI) {
         f -= ((float)Math.PI * 2F);
      }

      return p_102837_ + p_102836_ * f;
   }

   private float m_102833_(float p_102834_) {
      return -65.0F * p_102834_ + p_102834_ * p_102834_;
   }

   public void m_102872_(HumanoidModel<T> p_102873_) {
      super.m_102624_(p_102873_);
      p_102873_.f_102815_ = this.f_102815_;
      p_102873_.f_102816_ = this.f_102816_;
      p_102873_.f_102817_ = this.f_102817_;
      p_102873_.f_102808_.m_104315_(this.f_102808_);
      p_102873_.f_102809_.m_104315_(this.f_102809_);
      p_102873_.f_102810_.m_104315_(this.f_102810_);
      p_102873_.f_102811_.m_104315_(this.f_102811_);
      p_102873_.f_102812_.m_104315_(this.f_102812_);
      p_102873_.f_102813_.m_104315_(this.f_102813_);
      p_102873_.f_102814_.m_104315_(this.f_102814_);
   }

   public void m_8009_(boolean p_102880_) {
      this.f_102808_.f_104207_ = p_102880_;
      this.f_102809_.f_104207_ = p_102880_;
      this.f_102810_.f_104207_ = p_102880_;
      this.f_102811_.f_104207_ = p_102880_;
      this.f_102812_.f_104207_ = p_102880_;
      this.f_102813_.f_104207_ = p_102880_;
      this.f_102814_.f_104207_ = p_102880_;
   }

   public void m_6002_(HumanoidArm p_102854_, PoseStack p_102855_) {
      this.m_102851_(p_102854_).m_104299_(p_102855_);
   }

   protected ModelPart m_102851_(HumanoidArm p_102852_) {
      return p_102852_ == HumanoidArm.LEFT ? this.f_102812_ : this.f_102811_;
   }

   public ModelPart m_5585_() {
      return this.f_102808_;
   }

   private HumanoidArm m_102856_(T p_102857_) {
      HumanoidArm humanoidarm = p_102857_.m_5737_();
      return p_102857_.f_20912_ == InteractionHand.MAIN_HAND ? humanoidarm : humanoidarm.m_20828_();
   }

   @OnlyIn(Dist.CLIENT)
   public static enum ArmPose {
      EMPTY(false),
      ITEM(false),
      BLOCK(false),
      BOW_AND_ARROW(true),
      THROW_SPEAR(false),
      CROSSBOW_CHARGE(true),
      CROSSBOW_HOLD(true),
      SPYGLASS(false),
      TOOT_HORN(false),
      BRUSH(false);

      private final boolean f_102890_;

      private ArmPose(boolean p_102896_) {
         this.f_102890_ = p_102896_;
      }

      public boolean m_102897_() {
         return this.f_102890_;
      }
   }
}
