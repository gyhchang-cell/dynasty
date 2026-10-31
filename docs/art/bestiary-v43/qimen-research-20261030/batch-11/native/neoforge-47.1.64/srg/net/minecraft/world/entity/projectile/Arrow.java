package net.minecraft.world.entity.projectile;

import com.google.common.collect.Sets;
import java.util.Collection;
import java.util.Set;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.alchemy.Potion;
import net.minecraft.world.item.alchemy.PotionUtils;
import net.minecraft.world.item.alchemy.Potions;
import net.minecraft.world.level.Level;

public class Arrow extends AbstractArrow {
   private static final int f_150131_ = 600;
   private static final int f_150129_ = -1;
   private static final EntityDataAccessor<Integer> f_36854_ = SynchedEntityData.m_135353_(Arrow.class, EntityDataSerializers.f_135028_);
   private static final byte f_150130_ = 0;
   private Potion f_36855_ = Potions.f_43598_;
   private final Set<MobEffectInstance> f_36852_ = Sets.newHashSet();
   private boolean f_36853_;

   public Arrow(EntityType<? extends Arrow> p_36858_, Level p_36859_) {
      super(p_36858_, p_36859_);
   }

   public Arrow(Level p_36861_, double p_36862_, double p_36863_, double p_36864_) {
      super(EntityType.f_20548_, p_36862_, p_36863_, p_36864_, p_36861_);
   }

   public Arrow(Level p_36866_, LivingEntity p_36867_) {
      super(EntityType.f_20548_, p_36867_, p_36866_);
   }

   public void m_36878_(ItemStack p_36879_) {
      if (p_36879_.m_150930_(Items.f_42738_)) {
         this.f_36855_ = PotionUtils.m_43579_(p_36879_);
         Collection<MobEffectInstance> collection = PotionUtils.m_43571_(p_36879_);
         if (!collection.isEmpty()) {
            for(MobEffectInstance mobeffectinstance : collection) {
               this.f_36852_.add(new MobEffectInstance(mobeffectinstance));
            }
         }

         int i = m_36884_(p_36879_);
         if (i == -1) {
            this.m_36890_();
         } else {
            this.m_36882_(i);
         }
      } else if (p_36879_.m_150930_(Items.f_42412_)) {
         this.f_36855_ = Potions.f_43598_;
         this.f_36852_.clear();
         this.f_19804_.m_135381_(f_36854_, -1);
      }

   }

   public static int m_36884_(ItemStack p_36885_) {
      CompoundTag compoundtag = p_36885_.m_41783_();
      return compoundtag != null && compoundtag.m_128425_("CustomPotionColor", 99) ? compoundtag.m_128451_("CustomPotionColor") : -1;
   }

   private void m_36890_() {
      this.f_36853_ = false;
      if (this.f_36855_ == Potions.f_43598_ && this.f_36852_.isEmpty()) {
         this.f_19804_.m_135381_(f_36854_, -1);
      } else {
         this.f_19804_.m_135381_(f_36854_, PotionUtils.m_43564_(PotionUtils.m_43561_(this.f_36855_, this.f_36852_)));
      }

   }

   public void m_36870_(MobEffectInstance p_36871_) {
      this.f_36852_.add(p_36871_);
      this.m_20088_().m_135381_(f_36854_, PotionUtils.m_43564_(PotionUtils.m_43561_(this.f_36855_, this.f_36852_)));
   }

   protected void m_8097_() {
      super.m_8097_();
      this.f_19804_.m_135372_(f_36854_, -1);
   }

   public void m_8119_() {
      super.m_8119_();
      if (this.m_9236_().f_46443_) {
         if (this.f_36703_) {
            if (this.f_36704_ % 5 == 0) {
               this.m_36876_(1);
            }
         } else {
            this.m_36876_(2);
         }
      } else if (this.f_36703_ && this.f_36704_ != 0 && !this.f_36852_.isEmpty() && this.f_36704_ >= 600) {
         this.m_9236_().m_7605_(this, (byte)0);
         this.f_36855_ = Potions.f_43598_;
         this.f_36852_.clear();
         this.f_19804_.m_135381_(f_36854_, -1);
      }

   }

   private void m_36876_(int p_36877_) {
      int i = this.m_36889_();
      if (i != -1 && p_36877_ > 0) {
         double d0 = (double)(i >> 16 & 255) / 255.0D;
         double d1 = (double)(i >> 8 & 255) / 255.0D;
         double d2 = (double)(i >> 0 & 255) / 255.0D;

         for(int j = 0; j < p_36877_; ++j) {
            this.m_9236_().m_7106_(ParticleTypes.f_123811_, this.m_20208_(0.5D), this.m_20187_(), this.m_20262_(0.5D), d0, d1, d2);
         }

      }
   }

   public int m_36889_() {
      return this.f_19804_.m_135370_(f_36854_);
   }

   private void m_36882_(int p_36883_) {
      this.f_36853_ = true;
      this.f_19804_.m_135381_(f_36854_, p_36883_);
   }

   public void m_7380_(CompoundTag p_36881_) {
      super.m_7380_(p_36881_);
      if (this.f_36855_ != Potions.f_43598_) {
         p_36881_.m_128359_("Potion", BuiltInRegistries.f_256980_.m_7981_(this.f_36855_).toString());
      }

      if (this.f_36853_) {
         p_36881_.m_128405_("Color", this.m_36889_());
      }

      if (!this.f_36852_.isEmpty()) {
         ListTag listtag = new ListTag();

         for(MobEffectInstance mobeffectinstance : this.f_36852_) {
            listtag.add(mobeffectinstance.m_19555_(new CompoundTag()));
         }

         p_36881_.m_128365_("CustomPotionEffects", listtag);
      }

   }

   public void m_7378_(CompoundTag p_36875_) {
      super.m_7378_(p_36875_);
      if (p_36875_.m_128425_("Potion", 8)) {
         this.f_36855_ = PotionUtils.m_43577_(p_36875_);
      }

      for(MobEffectInstance mobeffectinstance : PotionUtils.m_43573_(p_36875_)) {
         this.m_36870_(mobeffectinstance);
      }

      if (p_36875_.m_128425_("Color", 99)) {
         this.m_36882_(p_36875_.m_128451_("Color"));
      } else {
         this.m_36890_();
      }

   }

   protected void m_7761_(LivingEntity p_36873_) {
      super.m_7761_(p_36873_);
      Entity entity = this.m_150173_();

      for(MobEffectInstance mobeffectinstance : this.f_36855_.m_43488_()) {
         p_36873_.m_147207_(new MobEffectInstance(mobeffectinstance.m_19544_(), Math.max(mobeffectinstance.m_267696_((p_268168_) -> {
            return p_268168_ / 8;
         }), 1), mobeffectinstance.m_19564_(), mobeffectinstance.m_19571_(), mobeffectinstance.m_19572_()), entity);
      }

      if (!this.f_36852_.isEmpty()) {
         for(MobEffectInstance mobeffectinstance1 : this.f_36852_) {
            p_36873_.m_147207_(mobeffectinstance1, entity);
         }
      }

   }

   protected ItemStack m_7941_() {
      if (this.f_36852_.isEmpty() && this.f_36855_ == Potions.f_43598_) {
         return new ItemStack(Items.f_42412_);
      } else {
         ItemStack itemstack = new ItemStack(Items.f_42738_);
         PotionUtils.m_43549_(itemstack, this.f_36855_);
         PotionUtils.m_43552_(itemstack, this.f_36852_);
         if (this.f_36853_) {
            itemstack.m_41784_().m_128405_("CustomPotionColor", this.m_36889_());
         }

         return itemstack;
      }
   }

   public void m_7822_(byte p_36869_) {
      if (p_36869_ == 0) {
         int i = this.m_36889_();
         if (i != -1) {
            double d0 = (double)(i >> 16 & 255) / 255.0D;
            double d1 = (double)(i >> 8 & 255) / 255.0D;
            double d2 = (double)(i >> 0 & 255) / 255.0D;

            for(int j = 0; j < 20; ++j) {
               this.m_9236_().m_7106_(ParticleTypes.f_123811_, this.m_20208_(0.5D), this.m_20187_(), this.m_20262_(0.5D), d0, d1, d2);
            }
         }
      } else {
         super.m_7822_(p_36869_);
      }

   }
}
