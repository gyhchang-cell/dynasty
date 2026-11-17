package net.minecraft.client.model;

import com.google.common.collect.ImmutableList;
import com.mojang.blaze3d.vertex.PoseStack;
import java.util.function.Function;
import net.minecraft.client.model.HumanoidModel.1;
import net.minecraft.client.model.HumanoidModel.ArmPose;
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
   private static final float f_170671_ = (float) (Math.PI / 12);
   private static final float f_170672_ = 1.9198622F;
   private static final float f_170675_ = (float) (Math.PI / 12);
   private static final float f_302316_ = (float) (-Math.PI * 4.0 / 9.0);
   private static final float f_303337_ = 0.43633232F;
   private static final float f_302399_ = (float) (Math.PI / 6);
   public static final float f_233401_ = 1.4835298F;
   public static final float f_233402_ = (float) (Math.PI / 6);
   public final ModelPart f_102808_;
   public final ModelPart f_102809_;
   public final ModelPart f_102810_;
   public final ModelPart f_102811_;
   public final ModelPart f_102812_;
   public final ModelPart f_102813_;
   public final ModelPart f_102814_;
   public ArmPose f_102815_ = ArmPose.EMPTY;
   public ArmPose f_102816_ = ArmPose.EMPTY;
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
      MeshDefinition $$2 = new MeshDefinition();
      PartDefinition $$3 = $$2.m_171576_();
      $$3.m_171599_(
         "head",
         CubeListBuilder.m_171558_().m_171514_(0, 0).m_171488_(-4.0F, -8.0F, -4.0F, 8.0F, 8.0F, 8.0F, p_170682_),
         PartPose.m_171419_(0.0F, 0.0F + p_170683_, 0.0F)
      );
      $$3.m_171599_(
         "hat",
         CubeListBuilder.m_171558_().m_171514_(32, 0).m_171488_(-4.0F, -8.0F, -4.0F, 8.0F, 8.0F, 8.0F, p_170682_.m_171469_(0.5F)),
         PartPose.m_171419_(0.0F, 0.0F + p_170683_, 0.0F)
      );
      $$3.m_171599_(
         "body",
         CubeListBuilder.m_171558_().m_171514_(16, 16).m_171488_(-4.0F, 0.0F, -2.0F, 8.0F, 12.0F, 4.0F, p_170682_),
         PartPose.m_171419_(0.0F, 0.0F + p_170683_, 0.0F)
      );
      $$3.m_171599_(
         "right_arm",
         CubeListBuilder.m_171558_().m_171514_(40, 16).m_171488_(-3.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, p_170682_),
         PartPose.m_171419_(-5.0F, 2.0F + p_170683_, 0.0F)
      );
      $$3.m_171599_(
         "left_arm",
         CubeListBuilder.m_171558_().m_171514_(40, 16).m_171480_().m_171488_(-1.0F, -2.0F, -2.0F, 4.0F, 12.0F, 4.0F, p_170682_),
         PartPose.m_171419_(5.0F, 2.0F + p_170683_, 0.0F)
      );
      $$3.m_171599_(
         "right_leg",
         CubeListBuilder.m_171558_().m_171514_(0, 16).m_171488_(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, p_170682_),
         PartPose.m_171419_(-1.9F, 12.0F + p_170683_, 0.0F)
      );
      $$3.m_171599_(
         "left_leg",
         CubeListBuilder.m_171558_().m_171514_(0, 16).m_171480_().m_171488_(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, p_170682_),
         PartPose.m_171419_(1.9F, 12.0F + p_170683_, 0.0F)
      );
      return $$2;
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
      boolean $$6 = p_102866_.m_21256_() > 4;
      boolean $$7 = p_102866_.m_6067_();
      this.f_102808_.f_104204_ = p_102870_ * (float) (Math.PI / 180.0);
      if ($$6) {
         this.f_102808_.f_104203_ = (float) (-Math.PI / 4);
      } else if (this.f_102818_ > 0.0F) {
         if ($$7) {
            this.f_102808_.f_104203_ = this.m_102835_(this.f_102818_, this.f_102808_.f_104203_, (float) (-Math.PI / 4));
         } else {
            this.f_102808_.f_104203_ = this.m_102835_(this.f_102818_, this.f_102808_.f_104203_, p_102871_ * (float) (Math.PI / 180.0));
         }
      } else {
         this.f_102808_.f_104203_ = p_102871_ * (float) (Math.PI / 180.0);
      }

      this.f_102810_.f_104204_ = 0.0F;
      this.f_102811_.f_104202_ = 0.0F;
      this.f_102811_.f_104200_ = -5.0F;
      this.f_102812_.f_104202_ = 0.0F;
      this.f_102812_.f_104200_ = 5.0F;
      float $$8 = 1.0F;
      if ($$6) {
         $$8 = (float)p_102866_.m_20184_().m_82556_();
         $$8 /= 0.2F;
         $$8 *= $$8 * $$8;
      }

      if ($$8 < 1.0F) {
         $$8 = 1.0F;
      }

      this.f_102811_.f_104203_ = Mth.m_14089_(p_102867_ * 0.6662F + (float) Math.PI) * 2.0F * p_102868_ * 0.5F / $$8;
      this.f_102812_.f_104203_ = Mth.m_14089_(p_102867_ * 0.6662F) * 2.0F * p_102868_ * 0.5F / $$8;
      this.f_102811_.f_104205_ = 0.0F;
      this.f_102812_.f_104205_ = 0.0F;
      this.f_102813_.f_104203_ = Mth.m_14089_(p_102867_ * 0.6662F) * 1.4F * p_102868_ / $$8;
      this.f_102814_.f_104203_ = Mth.m_14089_(p_102867_ * 0.6662F + (float) Math.PI) * 1.4F * p_102868_ / $$8;
      this.f_102813_.f_104204_ = 0.005F;
      this.f_102814_.f_104204_ = -0.005F;
      this.f_102813_.f_104205_ = 0.005F;
      this.f_102814_.f_104205_ = -0.005F;
      if (this.f_102609_) {
         this.f_102811_.f_104203_ += (float) (-Math.PI / 5);
         this.f_102812_.f_104203_ += (float) (-Math.PI / 5);
         this.f_102813_.f_104203_ = -1.4137167F;
         this.f_102813_.f_104204_ = (float) (Math.PI / 10);
         this.f_102813_.f_104205_ = 0.07853982F;
         this.f_102814_.f_104203_ = -1.4137167F;
         this.f_102814_.f_104204_ = (float) (-Math.PI / 10);
         this.f_102814_.f_104205_ = -0.07853982F;
      }

      this.f_102811_.f_104204_ = 0.0F;
      this.f_102812_.f_104204_ = 0.0F;
      boolean $$9 = p_102866_.m_5737_() == HumanoidArm.RIGHT;
      if (p_102866_.m_6117_()) {
         boolean $$10 = p_102866_.m_7655_() == InteractionHand.MAIN_HAND;
         if ($$10 == $$9) {
            this.m_102875_(p_102866_);
         } else {
            this.m_102878_(p_102866_);
         }
      } else {
         boolean $$11 = $$9 ? this.f_102815_.m_102897_() : this.f_102816_.m_102897_();
         if ($$9 != $$11) {
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

      if (this.f_102816_ != ArmPose.SPYGLASS) {
         AnimationUtils.m_170341_(this.f_102811_, p_102869_, 1.0F);
      }

      if (this.f_102815_ != ArmPose.SPYGLASS) {
         AnimationUtils.m_170341_(this.f_102812_, p_102869_, -1.0F);
      }

      if (this.f_102818_ > 0.0F) {
         float $$12 = p_102867_ % 26.0F;
         HumanoidArm $$13 = this.m_102856_(p_102866_);
         float $$14 = $$13 == HumanoidArm.RIGHT && this.f_102608_ > 0.0F ? 0.0F : this.f_102818_;
         float $$15 = $$13 == HumanoidArm.LEFT && this.f_102608_ > 0.0F ? 0.0F : this.f_102818_;
         if (!p_102866_.m_6117_()) {
            if ($$12 < 14.0F) {
               this.f_102812_.f_104203_ = this.m_102835_($$15, this.f_102812_.f_104203_, 0.0F);
               this.f_102811_.f_104203_ = Mth.m_14179_($$14, this.f_102811_.f_104203_, 0.0F);
               this.f_102812_.f_104204_ = this.m_102835_($$15, this.f_102812_.f_104204_, (float) Math.PI);
               this.f_102811_.f_104204_ = Mth.m_14179_($$14, this.f_102811_.f_104204_, (float) Math.PI);
               this.f_102812_.f_104205_ = this.m_102835_(
                  $$15, this.f_102812_.f_104205_, (float) Math.PI + 1.8707964F * this.m_102833_($$12) / this.m_102833_(14.0F)
               );
               this.f_102811_.f_104205_ = Mth.m_14179_(
                  $$14, this.f_102811_.f_104205_, (float) Math.PI - 1.8707964F * this.m_102833_($$12) / this.m_102833_(14.0F)
               );
            } else if ($$12 >= 14.0F && $$12 < 22.0F) {
               float $$16 = ($$12 - 14.0F) / 8.0F;
               this.f_102812_.f_104203_ = this.m_102835_($$15, this.f_102812_.f_104203_, (float) (Math.PI / 2) * $$16);
               this.f_102811_.f_104203_ = Mth.m_14179_($$14, this.f_102811_.f_104203_, (float) (Math.PI / 2) * $$16);
               this.f_102812_.f_104204_ = this.m_102835_($$15, this.f_102812_.f_104204_, (float) Math.PI);
               this.f_102811_.f_104204_ = Mth.m_14179_($$14, this.f_102811_.f_104204_, (float) Math.PI);
               this.f_102812_.f_104205_ = this.m_102835_($$15, this.f_102812_.f_104205_, 5.012389F - 1.8707964F * $$16);
               this.f_102811_.f_104205_ = Mth.m_14179_($$14, this.f_102811_.f_104205_, 1.2707963F + 1.8707964F * $$16);
            } else if ($$12 >= 22.0F && $$12 < 26.0F) {
               float $$17 = ($$12 - 22.0F) / 4.0F;
               this.f_102812_.f_104203_ = this.m_102835_($$15, this.f_102812_.f_104203_, (float) (Math.PI / 2) - (float) (Math.PI / 2) * $$17);
               this.f_102811_.f_104203_ = Mth.m_14179_($$14, this.f_102811_.f_104203_, (float) (Math.PI / 2) - (float) (Math.PI / 2) * $$17);
               this.f_102812_.f_104204_ = this.m_102835_($$15, this.f_102812_.f_104204_, (float) Math.PI);
               this.f_102811_.f_104204_ = Mth.m_14179_($$14, this.f_102811_.f_104204_, (float) Math.PI);
               this.f_102812_.f_104205_ = this.m_102835_($$15, this.f_102812_.f_104205_, (float) Math.PI);
               this.f_102811_.f_104205_ = Mth.m_14179_($$14, this.f_102811_.f_104205_, (float) Math.PI);
            }
         }

         float $$18 = 0.3F;
         float $$19 = 0.33333334F;
         this.f_102814_.f_104203_ = Mth.m_14179_(this.f_102818_, this.f_102814_.f_104203_, 0.3F * Mth.m_14089_(p_102867_ * 0.33333334F + (float) Math.PI));
         this.f_102813_.f_104203_ = Mth.m_14179_(this.f_102818_, this.f_102813_.f_104203_, 0.3F * Mth.m_14089_(p_102867_ * 0.33333334F));
      }

      this.f_102809_.m_104315_(this.f_102808_);
   }

   // $VF: Unable to simplify switch on enum
   // Please report this to the Vineflower issue tracker, at https://github.com/Vineflower/vineflower/issues with a copy of the class file (if you have the rights to distribute it!)
   private void m_102875_(T p_102876_) {
      switch (1.f_102881_[this.f_102816_.ordinal()]) {
         case 1:
            this.f_102811_.f_104204_ = 0.0F;
            break;
         case 2:
            this.m_307799_(this.f_102811_, true);
            break;
         case 3:
            this.f_102811_.f_104203_ = this.f_102811_.f_104203_ * 0.5F - (float) (Math.PI / 10);
            this.f_102811_.f_104204_ = 0.0F;
            break;
         case 4:
            this.f_102811_.f_104203_ = this.f_102811_.f_104203_ * 0.5F - (float) Math.PI;
            this.f_102811_.f_104204_ = 0.0F;
            break;
         case 5:
            this.f_102811_.f_104204_ = -0.1F + this.f_102808_.f_104204_;
            this.f_102812_.f_104204_ = 0.1F + this.f_102808_.f_104204_ + 0.4F;
            this.f_102811_.f_104203_ = (float) (-Math.PI / 2) + this.f_102808_.f_104203_;
            this.f_102812_.f_104203_ = (float) (-Math.PI / 2) + this.f_102808_.f_104203_;
            break;
         case 6:
            AnimationUtils.m_102086_(this.f_102811_, this.f_102812_, p_102876_, true);
            break;
         case 7:
            AnimationUtils.m_102097_(this.f_102811_, this.f_102812_, this.f_102808_, true);
            break;
         case 8:
            this.f_102811_.f_104203_ = this.f_102811_.f_104203_ * 0.5F - (float) (Math.PI / 5);
            this.f_102811_.f_104204_ = 0.0F;
            break;
         case 9:
            this.f_102811_.f_104203_ = Mth.m_14036_(this.f_102808_.f_104203_ - 1.9198622F - (p_102876_.m_6047_() ? (float) (Math.PI / 12) : 0.0F), -2.4F, 3.3F);
            this.f_102811_.f_104204_ = this.f_102808_.f_104204_ - (float) (Math.PI / 12);
            break;
         case 10:
            this.f_102811_.f_104203_ = Mth.m_14036_(this.f_102808_.f_104203_, -1.2F, 1.2F) - 1.4835298F;
            this.f_102811_.f_104204_ = this.f_102808_.f_104204_ - (float) (Math.PI / 6);
      }
   }

   // $VF: Unable to simplify switch on enum
   // Please report this to the Vineflower issue tracker, at https://github.com/Vineflower/vineflower/issues with a copy of the class file (if you have the rights to distribute it!)
   private void m_102878_(T p_102879_) {
      switch (1.f_102881_[this.f_102815_.ordinal()]) {
         case 1:
            this.f_102812_.f_104204_ = 0.0F;
            break;
         case 2:
            this.m_307799_(this.f_102812_, false);
            break;
         case 3:
            this.f_102812_.f_104203_ = this.f_102812_.f_104203_ * 0.5F - (float) (Math.PI / 10);
            this.f_102812_.f_104204_ = 0.0F;
            break;
         case 4:
            this.f_102812_.f_104203_ = this.f_102812_.f_104203_ * 0.5F - (float) Math.PI;
            this.f_102812_.f_104204_ = 0.0F;
            break;
         case 5:
            this.f_102811_.f_104204_ = -0.1F + this.f_102808_.f_104204_ - 0.4F;
            this.f_102812_.f_104204_ = 0.1F + this.f_102808_.f_104204_;
            this.f_102811_.f_104203_ = (float) (-Math.PI / 2) + this.f_102808_.f_104203_;
            this.f_102812_.f_104203_ = (float) (-Math.PI / 2) + this.f_102808_.f_104203_;
            break;
         case 6:
            AnimationUtils.m_102086_(this.f_102811_, this.f_102812_, p_102879_, false);
            break;
         case 7:
            AnimationUtils.m_102097_(this.f_102811_, this.f_102812_, this.f_102808_, false);
            break;
         case 8:
            this.f_102812_.f_104203_ = this.f_102812_.f_104203_ * 0.5F - (float) (Math.PI / 5);
            this.f_102812_.f_104204_ = 0.0F;
            break;
         case 9:
            this.f_102812_.f_104203_ = Mth.m_14036_(this.f_102808_.f_104203_ - 1.9198622F - (p_102879_.m_6047_() ? (float) (Math.PI / 12) : 0.0F), -2.4F, 3.3F);
            this.f_102812_.f_104204_ = this.f_102808_.f_104204_ + (float) (Math.PI / 12);
            break;
         case 10:
            this.f_102812_.f_104203_ = Mth.m_14036_(this.f_102808_.f_104203_, -1.2F, 1.2F) - 1.4835298F;
            this.f_102812_.f_104204_ = this.f_102808_.f_104204_ + (float) (Math.PI / 6);
      }
   }

   private void m_307799_(ModelPart p_312070_, boolean p_311335_) {
      p_312070_.f_104203_ = p_312070_.f_104203_ * 0.5F - 0.9424779F + Mth.m_14036_(this.f_102808_.f_104203_, (float) (-Math.PI * 4.0 / 9.0), 0.43633232F);
      p_312070_.f_104204_ = (p_311335_ ? -30.0F : 30.0F) * (float) (Math.PI / 180.0)
         + Mth.m_14036_(this.f_102808_.f_104204_, (float) (-Math.PI / 6), (float) (Math.PI / 6));
   }

   protected void m_7884_(T p_102858_, float p_102859_) {
      if (!(this.f_102608_ <= 0.0F)) {
         HumanoidArm $$2 = this.m_102856_(p_102858_);
         ModelPart $$3 = this.m_102851_($$2);
         float $$4 = this.f_102608_;
         this.f_102810_.f_104204_ = Mth.m_14031_(Mth.m_14116_($$4) * (float) (Math.PI * 2)) * 0.2F;
         if ($$2 == HumanoidArm.LEFT) {
            this.f_102810_.f_104204_ *= -1.0F;
         }

         this.f_102811_.f_104202_ = Mth.m_14031_(this.f_102810_.f_104204_) * 5.0F;
         this.f_102811_.f_104200_ = -Mth.m_14089_(this.f_102810_.f_104204_) * 5.0F;
         this.f_102812_.f_104202_ = -Mth.m_14031_(this.f_102810_.f_104204_) * 5.0F;
         this.f_102812_.f_104200_ = Mth.m_14089_(this.f_102810_.f_104204_) * 5.0F;
         this.f_102811_.f_104204_ = this.f_102811_.f_104204_ + this.f_102810_.f_104204_;
         this.f_102812_.f_104204_ = this.f_102812_.f_104204_ + this.f_102810_.f_104204_;
         this.f_102812_.f_104203_ = this.f_102812_.f_104203_ + this.f_102810_.f_104204_;
         $$4 = 1.0F - this.f_102608_;
         $$4 *= $$4;
         $$4 *= $$4;
         $$4 = 1.0F - $$4;
         float $$5 = Mth.m_14031_($$4 * (float) Math.PI);
         float $$6 = Mth.m_14031_(this.f_102608_ * (float) Math.PI) * -(this.f_102808_.f_104203_ - 0.7F) * 0.75F;
         $$3.f_104203_ -= $$5 * 1.2F + $$6;
         $$3.f_104204_ = $$3.f_104204_ + this.f_102810_.f_104204_ * 2.0F;
         $$3.f_104205_ = $$3.f_104205_ + Mth.m_14031_(this.f_102608_ * (float) Math.PI) * -0.4F;
      }
   }

   protected float m_102835_(float p_102836_, float p_102837_, float p_102838_) {
      float $$3 = (p_102838_ - p_102837_) % (float) (Math.PI * 2);
      if ($$3 < (float) -Math.PI) {
         $$3 += (float) (Math.PI * 2);
      }

      if ($$3 >= (float) Math.PI) {
         $$3 -= (float) (Math.PI * 2);
      }

      return p_102837_ + p_102836_ * $$3;
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
      HumanoidArm $$1 = p_102857_.m_5737_();
      return p_102857_.f_20912_ == InteractionHand.MAIN_HAND ? $$1 : $$1.m_20828_();
   }
}
