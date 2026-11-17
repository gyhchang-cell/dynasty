package net.minecraft.world.entity.projectile;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.TheEndGatewayBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

public abstract class ThrowableProjectile extends Projectile {
   protected ThrowableProjectile(EntityType<? extends ThrowableProjectile> p_37466_, Level p_37467_) {
      super(p_37466_, p_37467_);
   }

   protected ThrowableProjectile(EntityType<? extends ThrowableProjectile> p_37456_, double p_37457_, double p_37458_, double p_37459_, Level p_37460_) {
      this(p_37456_, p_37460_);
      this.m_6034_(p_37457_, p_37458_, p_37459_);
   }

   protected ThrowableProjectile(EntityType<? extends ThrowableProjectile> p_37462_, LivingEntity p_37463_, Level p_37464_) {
      this(p_37462_, p_37463_.m_20185_(), p_37463_.m_20188_() - (double)0.1F, p_37463_.m_20189_(), p_37464_);
      this.m_5602_(p_37463_);
   }

   public boolean m_6783_(double p_37470_) {
      double d0 = this.m_20191_().m_82309_() * 4.0D;
      if (Double.isNaN(d0)) {
         d0 = 4.0D;
      }

      d0 *= 64.0D;
      return p_37470_ < d0 * d0;
   }

   public void m_8119_() {
      super.m_8119_();
      HitResult hitresult = ProjectileUtil.m_278158_(this, this::m_5603_);
      boolean flag = false;
      if (hitresult.m_6662_() == HitResult.Type.BLOCK) {
         BlockPos blockpos = ((BlockHitResult)hitresult).m_82425_();
         BlockState blockstate = this.m_9236_().m_8055_(blockpos);
         if (blockstate.m_60713_(Blocks.f_50142_)) {
            this.m_20221_(blockpos);
            flag = true;
         } else if (blockstate.m_60713_(Blocks.f_50446_)) {
            BlockEntity blockentity = this.m_9236_().m_7702_(blockpos);
            if (blockentity instanceof TheEndGatewayBlockEntity && TheEndGatewayBlockEntity.m_59940_(this)) {
               TheEndGatewayBlockEntity.m_155828_(this.m_9236_(), blockpos, blockstate, this, (TheEndGatewayBlockEntity)blockentity);
            }

            flag = true;
         }
      }

      if (hitresult.m_6662_() != HitResult.Type.MISS && !flag && !net.minecraftforge.event.ForgeEventFactory.onProjectileImpact(this, hitresult)) {
         this.m_6532_(hitresult);
      }

      this.m_20101_();
      Vec3 vec3 = this.m_20184_();
      double d2 = this.m_20185_() + vec3.f_82479_;
      double d0 = this.m_20186_() + vec3.f_82480_;
      double d1 = this.m_20189_() + vec3.f_82481_;
      this.m_37283_();
      float f;
      if (this.m_20069_()) {
         for(int i = 0; i < 4; ++i) {
            float f1 = 0.25F;
            this.m_9236_().m_7106_(ParticleTypes.f_123795_, d2 - vec3.f_82479_ * 0.25D, d0 - vec3.f_82480_ * 0.25D, d1 - vec3.f_82481_ * 0.25D, vec3.f_82479_, vec3.f_82480_, vec3.f_82481_);
         }

         f = 0.8F;
      } else {
         f = 0.99F;
      }

      this.m_20256_(vec3.m_82490_((double)f));
      if (!this.m_20068_()) {
         Vec3 vec31 = this.m_20184_();
         this.m_20334_(vec31.f_82479_, vec31.f_82480_ - (double)this.m_7139_(), vec31.f_82481_);
      }

      this.m_6034_(d2, d0, d1);
   }

   protected float m_7139_() {
      return 0.03F;
   }
}
