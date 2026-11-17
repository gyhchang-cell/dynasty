package net.minecraft.world.entity.projectile;

import java.util.OptionalInt;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

public class FireworkRocketEntity extends Projectile implements ItemSupplier {
   private static final EntityDataAccessor<ItemStack> f_37019_ = SynchedEntityData.m_135353_(FireworkRocketEntity.class, EntityDataSerializers.f_135033_);
   private static final EntityDataAccessor<OptionalInt> f_37020_ = SynchedEntityData.m_135353_(FireworkRocketEntity.class, EntityDataSerializers.f_135044_);
   private static final EntityDataAccessor<Boolean> f_37021_ = SynchedEntityData.m_135353_(FireworkRocketEntity.class, EntityDataSerializers.f_135035_);
   private int f_37022_;
   private int f_37023_;
   @Nullable
   private LivingEntity f_37024_;

   public FireworkRocketEntity(EntityType<? extends FireworkRocketEntity> p_37027_, Level p_37028_) {
      super(p_37027_, p_37028_);
   }

   public FireworkRocketEntity(Level p_37030_, double p_37031_, double p_37032_, double p_37033_, ItemStack p_37034_) {
      super(EntityType.f_20451_, p_37030_);
      this.f_37022_ = 0;
      this.m_6034_(p_37031_, p_37032_, p_37033_);
      int i = 1;
      if (!p_37034_.m_41619_() && p_37034_.m_41782_()) {
         this.f_19804_.m_135381_(f_37019_, p_37034_.m_41777_());
         i += p_37034_.m_41698_("Fireworks").m_128445_("Flight");
      }

      this.m_20334_(this.f_19796_.m_216328_(0.0D, 0.002297D), 0.05D, this.f_19796_.m_216328_(0.0D, 0.002297D));
      this.f_37023_ = 10 * i + this.f_19796_.m_188503_(6) + this.f_19796_.m_188503_(7);
   }

   public FireworkRocketEntity(Level p_37036_, @Nullable Entity p_37037_, double p_37038_, double p_37039_, double p_37040_, ItemStack p_37041_) {
      this(p_37036_, p_37038_, p_37039_, p_37040_, p_37041_);
      this.m_5602_(p_37037_);
   }

   public FireworkRocketEntity(Level p_37058_, ItemStack p_37059_, LivingEntity p_37060_) {
      this(p_37058_, p_37060_, p_37060_.m_20185_(), p_37060_.m_20186_(), p_37060_.m_20189_(), p_37059_);
      this.f_19804_.m_135381_(f_37020_, OptionalInt.of(p_37060_.m_19879_()));
      this.f_37024_ = p_37060_;
   }

   public FireworkRocketEntity(Level p_37043_, ItemStack p_37044_, double p_37045_, double p_37046_, double p_37047_, boolean p_37048_) {
      this(p_37043_, p_37045_, p_37046_, p_37047_, p_37044_);
      this.f_19804_.m_135381_(f_37021_, p_37048_);
   }

   public FireworkRocketEntity(Level p_37050_, ItemStack p_37051_, Entity p_37052_, double p_37053_, double p_37054_, double p_37055_, boolean p_37056_) {
      this(p_37050_, p_37051_, p_37053_, p_37054_, p_37055_, p_37056_);
      this.m_5602_(p_37052_);
   }

   protected void m_8097_() {
      this.f_19804_.m_135372_(f_37019_, ItemStack.f_41583_);
      this.f_19804_.m_135372_(f_37020_, OptionalInt.empty());
      this.f_19804_.m_135372_(f_37021_, false);
   }

   public boolean m_6783_(double p_37065_) {
      return p_37065_ < 4096.0D && !this.m_37088_();
   }

   public boolean m_6000_(double p_37083_, double p_37084_, double p_37085_) {
      return super.m_6000_(p_37083_, p_37084_, p_37085_) && !this.m_37088_();
   }

   public void m_8119_() {
      super.m_8119_();
      if (this.m_37088_()) {
         if (this.f_37024_ == null) {
            this.f_19804_.m_135370_(f_37020_).ifPresent((p_289492_) -> {
               Entity entity = this.m_9236_().m_6815_(p_289492_);
               if (entity instanceof LivingEntity) {
                  this.f_37024_ = (LivingEntity)entity;
               }

            });
         }

         if (this.f_37024_ != null) {
            Vec3 vec3;
            if (this.f_37024_.m_21255_()) {
               Vec3 vec31 = this.f_37024_.m_20154_();
               double d0 = 1.5D;
               double d1 = 0.1D;
               Vec3 vec32 = this.f_37024_.m_20184_();
               this.f_37024_.m_20256_(vec32.m_82520_(vec31.f_82479_ * 0.1D + (vec31.f_82479_ * 1.5D - vec32.f_82479_) * 0.5D, vec31.f_82480_ * 0.1D + (vec31.f_82480_ * 1.5D - vec32.f_82480_) * 0.5D, vec31.f_82481_ * 0.1D + (vec31.f_82481_ * 1.5D - vec32.f_82481_) * 0.5D));
               vec3 = this.f_37024_.m_204034_(Items.f_42688_);
            } else {
               vec3 = Vec3.f_82478_;
            }

            this.m_6034_(this.f_37024_.m_20185_() + vec3.f_82479_, this.f_37024_.m_20186_() + vec3.f_82480_, this.f_37024_.m_20189_() + vec3.f_82481_);
            this.m_20256_(this.f_37024_.m_20184_());
         }
      } else {
         if (!this.m_37079_()) {
            double d2 = this.f_19862_ ? 1.0D : 1.15D;
            this.m_20256_(this.m_20184_().m_82542_(d2, 1.0D, d2).m_82520_(0.0D, 0.04D, 0.0D));
         }

         Vec3 vec33 = this.m_20184_();
         this.m_6478_(MoverType.SELF, vec33);
         this.m_20256_(vec33);
      }

      HitResult hitresult = ProjectileUtil.m_278158_(this, this::m_5603_);
      if (!this.f_19794_) {
         this.m_6532_(hitresult);
         this.f_19812_ = true;
      }

      this.m_37283_();
      if (this.f_37022_ == 0 && !this.m_20067_()) {
         this.m_9236_().m_6263_((Player)null, this.m_20185_(), this.m_20186_(), this.m_20189_(), SoundEvents.f_11932_, SoundSource.AMBIENT, 3.0F, 1.0F);
      }

      ++this.f_37022_;
      if (this.m_9236_().f_46443_ && this.f_37022_ % 2 < 2) {
         this.m_9236_().m_7106_(ParticleTypes.f_123815_, this.m_20185_(), this.m_20186_(), this.m_20189_(), this.f_19796_.m_188583_() * 0.05D, -this.m_20184_().f_82480_ * 0.5D, this.f_19796_.m_188583_() * 0.05D);
      }

      if (!this.m_9236_().f_46443_ && this.f_37022_ > this.f_37023_) {
         this.m_37080_();
      }

   }

   private void m_37080_() {
      this.m_9236_().m_7605_(this, (byte)17);
      this.m_146852_(GameEvent.f_157812_, this.m_19749_());
      this.m_37087_();
      this.m_146870_();
   }

   protected void m_5790_(EntityHitResult p_37071_) {
      super.m_5790_(p_37071_);
      if (!this.m_9236_().f_46443_) {
         this.m_37080_();
      }
   }

   protected void m_8060_(BlockHitResult p_37069_) {
      BlockPos blockpos = new BlockPos(p_37069_.m_82425_());
      this.m_9236_().m_8055_(blockpos).m_60682_(this.m_9236_(), blockpos, this);
      if (!this.m_9236_().m_5776_() && this.m_37086_()) {
         this.m_37080_();
      }

      super.m_8060_(p_37069_);
   }

   private boolean m_37086_() {
      ItemStack itemstack = this.f_19804_.m_135370_(f_37019_);
      CompoundTag compoundtag = itemstack.m_41619_() ? null : itemstack.m_41737_("Fireworks");
      ListTag listtag = compoundtag != null ? compoundtag.m_128437_("Explosions", 10) : null;
      return listtag != null && !listtag.isEmpty();
   }

   private void m_37087_() {
      float f = 0.0F;
      ItemStack itemstack = this.f_19804_.m_135370_(f_37019_);
      CompoundTag compoundtag = itemstack.m_41619_() ? null : itemstack.m_41737_("Fireworks");
      ListTag listtag = compoundtag != null ? compoundtag.m_128437_("Explosions", 10) : null;
      if (listtag != null && !listtag.isEmpty()) {
         f = 5.0F + (float)(listtag.size() * 2);
      }

      if (f > 0.0F) {
         if (this.f_37024_ != null) {
            this.f_37024_.m_6469_(this.m_269291_().m_268994_(this, this.m_19749_()), 5.0F + (float)(listtag.size() * 2));
         }

         double d0 = 5.0D;
         Vec3 vec3 = this.m_20182_();

         for(LivingEntity livingentity : this.m_9236_().m_45976_(LivingEntity.class, this.m_20191_().m_82400_(5.0D))) {
            if (livingentity != this.f_37024_ && !(this.m_20280_(livingentity) > 25.0D)) {
               boolean flag = false;

               for(int i = 0; i < 2; ++i) {
                  Vec3 vec31 = new Vec3(livingentity.m_20185_(), livingentity.m_20227_(0.5D * (double)i), livingentity.m_20189_());
                  HitResult hitresult = this.m_9236_().m_45547_(new ClipContext(vec3, vec31, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, this));
                  if (hitresult.m_6662_() == HitResult.Type.MISS) {
                     flag = true;
                     break;
                  }
               }

               if (flag) {
                  float f1 = f * (float)Math.sqrt((5.0D - (double)this.m_20270_(livingentity)) / 5.0D);
                  livingentity.m_6469_(this.m_269291_().m_268994_(this, this.m_19749_()), f1);
               }
            }
         }
      }

   }

   private boolean m_37088_() {
      return this.f_19804_.m_135370_(f_37020_).isPresent();
   }

   public boolean m_37079_() {
      return this.f_19804_.m_135370_(f_37021_);
   }

   public void m_7822_(byte p_37063_) {
      if (p_37063_ == 17 && this.m_9236_().f_46443_) {
         if (!this.m_37086_()) {
            for(int i = 0; i < this.f_19796_.m_188503_(3) + 2; ++i) {
               this.m_9236_().m_7106_(ParticleTypes.f_123759_, this.m_20185_(), this.m_20186_(), this.m_20189_(), this.f_19796_.m_188583_() * 0.05D, 0.005D, this.f_19796_.m_188583_() * 0.05D);
            }
         } else {
            ItemStack itemstack = this.f_19804_.m_135370_(f_37019_);
            CompoundTag compoundtag = itemstack.m_41619_() ? null : itemstack.m_41737_("Fireworks");
            Vec3 vec3 = this.m_20184_();
            this.m_9236_().m_7228_(this.m_20185_(), this.m_20186_(), this.m_20189_(), vec3.f_82479_, vec3.f_82480_, vec3.f_82481_, compoundtag);
         }
      }

      super.m_7822_(p_37063_);
   }

   public void m_7380_(CompoundTag p_37075_) {
      super.m_7380_(p_37075_);
      p_37075_.m_128405_("Life", this.f_37022_);
      p_37075_.m_128405_("LifeTime", this.f_37023_);
      ItemStack itemstack = this.f_19804_.m_135370_(f_37019_);
      if (!itemstack.m_41619_()) {
         p_37075_.m_128365_("FireworksItem", itemstack.m_41739_(new CompoundTag()));
      }

      p_37075_.m_128379_("ShotAtAngle", this.f_19804_.m_135370_(f_37021_));
   }

   public void m_7378_(CompoundTag p_37073_) {
      super.m_7378_(p_37073_);
      this.f_37022_ = p_37073_.m_128451_("Life");
      this.f_37023_ = p_37073_.m_128451_("LifeTime");
      ItemStack itemstack = ItemStack.m_41712_(p_37073_.m_128469_("FireworksItem"));
      if (!itemstack.m_41619_()) {
         this.f_19804_.m_135381_(f_37019_, itemstack);
      }

      if (p_37073_.m_128441_("ShotAtAngle")) {
         this.f_19804_.m_135381_(f_37021_, p_37073_.m_128471_("ShotAtAngle"));
      }

   }

   public ItemStack m_7846_() {
      ItemStack itemstack = this.f_19804_.m_135370_(f_37019_);
      return itemstack.m_41619_() ? new ItemStack(Items.f_42688_) : itemstack;
   }

   public boolean m_6097_() {
      return false;
   }
}
