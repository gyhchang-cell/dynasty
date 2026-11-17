package net.minecraft.world.entity.projectile;

import com.google.common.base.MoreObjects;
import java.util.UUID;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundAddEntityPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.TraceableEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

public abstract class Projectile extends Entity implements TraceableEntity {
   @Nullable
   private UUID f_37244_;
   @Nullable
   private Entity f_150163_;
   private boolean f_37246_;
   private boolean f_150164_;

   protected Projectile(EntityType<? extends Projectile> p_37248_, Level p_37249_) {
      super(p_37248_, p_37249_);
   }

   public void m_5602_(@Nullable Entity p_37263_) {
      if (p_37263_ != null) {
         this.f_37244_ = p_37263_.m_20148_();
         this.f_150163_ = p_37263_;
      }

   }

   @Nullable
   public Entity m_19749_() {
      if (this.f_150163_ != null && !this.f_150163_.m_213877_()) {
         return this.f_150163_;
      } else if (this.f_37244_ != null && this.m_9236_() instanceof ServerLevel) {
         this.f_150163_ = ((ServerLevel)this.m_9236_()).m_8791_(this.f_37244_);
         return this.f_150163_;
      } else {
         return null;
      }
   }

   public Entity m_150173_() {
      return MoreObjects.firstNonNull(this.m_19749_(), this);
   }

   protected void m_7380_(CompoundTag p_37265_) {
      if (this.f_37244_ != null) {
         p_37265_.m_128362_("Owner", this.f_37244_);
      }

      if (this.f_37246_) {
         p_37265_.m_128379_("LeftOwner", true);
      }

      p_37265_.m_128379_("HasBeenShot", this.f_150164_);
   }

   protected boolean m_150171_(Entity p_150172_) {
      return p_150172_.m_20148_().equals(this.f_37244_);
   }

   protected void m_7378_(CompoundTag p_37262_) {
      if (p_37262_.m_128403_("Owner")) {
         this.f_37244_ = p_37262_.m_128342_("Owner");
         this.f_150163_ = null;
      }

      this.f_37246_ = p_37262_.m_128471_("LeftOwner");
      this.f_150164_ = p_37262_.m_128471_("HasBeenShot");
   }

   public void m_8119_() {
      if (!this.f_150164_) {
         this.m_146852_(GameEvent.f_157778_, this.m_19749_());
         this.f_150164_ = true;
      }

      if (!this.f_37246_) {
         this.f_37246_ = this.m_37276_();
      }

      super.m_8119_();
   }

   private boolean m_37276_() {
      Entity entity = this.m_19749_();
      if (entity != null) {
         for(Entity entity1 : this.m_9236_().m_6249_(this, this.m_20191_().m_82369_(this.m_20184_()).m_82400_(1.0D), (p_37272_) -> {
            return !p_37272_.m_5833_() && p_37272_.m_6087_();
         })) {
            if (entity1.m_20201_() == entity.m_20201_()) {
               return false;
            }
         }
      }

      return true;
   }

   public void m_6686_(double p_37266_, double p_37267_, double p_37268_, float p_37269_, float p_37270_) {
      Vec3 vec3 = (new Vec3(p_37266_, p_37267_, p_37268_)).m_82541_().m_82520_(this.f_19796_.m_216328_(0.0D, 0.0172275D * (double)p_37270_), this.f_19796_.m_216328_(0.0D, 0.0172275D * (double)p_37270_), this.f_19796_.m_216328_(0.0D, 0.0172275D * (double)p_37270_)).m_82490_((double)p_37269_);
      this.m_20256_(vec3);
      double d0 = vec3.m_165924_();
      this.m_146922_((float)(Mth.m_14136_(vec3.f_82479_, vec3.f_82481_) * (double)(180F / (float)Math.PI)));
      this.m_146926_((float)(Mth.m_14136_(vec3.f_82480_, d0) * (double)(180F / (float)Math.PI)));
      this.f_19859_ = this.m_146908_();
      this.f_19860_ = this.m_146909_();
   }

   public void m_37251_(Entity p_37252_, float p_37253_, float p_37254_, float p_37255_, float p_37256_, float p_37257_) {
      float f = -Mth.m_14031_(p_37254_ * ((float)Math.PI / 180F)) * Mth.m_14089_(p_37253_ * ((float)Math.PI / 180F));
      float f1 = -Mth.m_14031_((p_37253_ + p_37255_) * ((float)Math.PI / 180F));
      float f2 = Mth.m_14089_(p_37254_ * ((float)Math.PI / 180F)) * Mth.m_14089_(p_37253_ * ((float)Math.PI / 180F));
      this.m_6686_((double)f, (double)f1, (double)f2, p_37256_, p_37257_);
      Vec3 vec3 = p_37252_.m_20184_();
      this.m_20256_(this.m_20184_().m_82520_(vec3.f_82479_, p_37252_.m_20096_() ? 0.0D : vec3.f_82480_, vec3.f_82481_));
   }

   protected void m_6532_(HitResult p_37260_) {
      HitResult.Type hitresult$type = p_37260_.m_6662_();
      if (hitresult$type == HitResult.Type.ENTITY) {
         this.m_5790_((EntityHitResult)p_37260_);
         this.m_9236_().m_214171_(GameEvent.f_157777_, p_37260_.m_82450_(), GameEvent.Context.m_223719_(this, (BlockState)null));
      } else if (hitresult$type == HitResult.Type.BLOCK) {
         BlockHitResult blockhitresult = (BlockHitResult)p_37260_;
         this.m_8060_(blockhitresult);
         BlockPos blockpos = blockhitresult.m_82425_();
         this.m_9236_().m_220407_(GameEvent.f_157777_, blockpos, GameEvent.Context.m_223719_(this, this.m_9236_().m_8055_(blockpos)));
      }

   }

   protected void m_5790_(EntityHitResult p_37259_) {
   }

   protected void m_8060_(BlockHitResult p_37258_) {
      BlockState blockstate = this.m_9236_().m_8055_(p_37258_.m_82425_());
      blockstate.m_60669_(this.m_9236_(), blockstate, p_37258_, this);
   }

   public void m_6001_(double p_37279_, double p_37280_, double p_37281_) {
      this.m_20334_(p_37279_, p_37280_, p_37281_);
      if (this.f_19860_ == 0.0F && this.f_19859_ == 0.0F) {
         double d0 = Math.sqrt(p_37279_ * p_37279_ + p_37281_ * p_37281_);
         this.m_146926_((float)(Mth.m_14136_(p_37280_, d0) * (double)(180F / (float)Math.PI)));
         this.m_146922_((float)(Mth.m_14136_(p_37279_, p_37281_) * (double)(180F / (float)Math.PI)));
         this.f_19860_ = this.m_146909_();
         this.f_19859_ = this.m_146908_();
         this.m_7678_(this.m_20185_(), this.m_20186_(), this.m_20189_(), this.m_146908_(), this.m_146909_());
      }

   }

   protected boolean m_5603_(Entity p_37250_) {
      if (!p_37250_.m_271807_()) {
         return false;
      } else {
         Entity entity = this.m_19749_();
         return entity == null || this.f_37246_ || !entity.m_20365_(p_37250_);
      }
   }

   protected void m_37283_() {
      Vec3 vec3 = this.m_20184_();
      double d0 = vec3.m_165924_();
      this.m_146926_(m_37273_(this.f_19860_, (float)(Mth.m_14136_(vec3.f_82480_, d0) * (double)(180F / (float)Math.PI))));
      this.m_146922_(m_37273_(this.f_19859_, (float)(Mth.m_14136_(vec3.f_82479_, vec3.f_82481_) * (double)(180F / (float)Math.PI))));
   }

   protected static float m_37273_(float p_37274_, float p_37275_) {
      while(p_37275_ - p_37274_ < -180.0F) {
         p_37274_ -= 360.0F;
      }

      while(p_37275_ - p_37274_ >= 180.0F) {
         p_37274_ += 360.0F;
      }

      return Mth.m_14179_(0.2F, p_37274_, p_37275_);
   }

   public Packet<ClientGamePacketListener> m_5654_() {
      Entity entity = this.m_19749_();
      return new ClientboundAddEntityPacket(this, entity == null ? 0 : entity.m_19879_());
   }

   public void m_141965_(ClientboundAddEntityPacket p_150170_) {
      super.m_141965_(p_150170_);
      Entity entity = this.m_9236_().m_6815_(p_150170_.m_131509_());
      if (entity != null) {
         this.m_5602_(entity);
      }

   }

   public boolean m_142265_(Level p_150167_, BlockPos p_150168_) {
      Entity entity = this.m_19749_();
      if (entity instanceof Player) {
         return entity.m_142265_(p_150167_, p_150168_);
      } else {
         return entity == null || net.minecraftforge.event.ForgeEventFactory.getMobGriefingEvent(p_150167_, entity);
      }
   }
}
