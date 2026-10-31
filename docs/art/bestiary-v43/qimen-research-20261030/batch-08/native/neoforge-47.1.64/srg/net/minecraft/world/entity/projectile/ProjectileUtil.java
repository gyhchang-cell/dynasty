package net.minecraft.world.entity.projectile;

import java.util.Optional;
import java.util.function.Predicate;
import javax.annotation.Nullable;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ArrowItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

public final class ProjectileUtil {
   public static HitResult m_278158_(Entity p_278228_, Predicate<Entity> p_278315_) {
      Vec3 vec3 = p_278228_.m_20184_();
      Level level = p_278228_.m_9236_();
      Vec3 vec31 = p_278228_.m_20182_();
      return m_278167_(vec31, p_278228_, p_278315_, vec3, level);
   }

   public static HitResult m_278180_(Entity p_278281_, Predicate<Entity> p_278306_, double p_278293_) {
      Vec3 vec3 = p_278281_.m_20252_(0.0F).m_82490_(p_278293_);
      Level level = p_278281_.m_9236_();
      Vec3 vec31 = p_278281_.m_146892_();
      return m_278167_(vec31, p_278281_, p_278306_, vec3, level);
   }

   private static HitResult m_278167_(Vec3 p_278237_, Entity p_278320_, Predicate<Entity> p_278257_, Vec3 p_278342_, Level p_278321_) {
      Vec3 vec3 = p_278237_.m_82549_(p_278342_);
      HitResult hitresult = p_278321_.m_45547_(new ClipContext(p_278237_, vec3, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, p_278320_));
      if (hitresult.m_6662_() != HitResult.Type.MISS) {
         vec3 = hitresult.m_82450_();
      }

      HitResult hitresult1 = m_37304_(p_278321_, p_278320_, p_278237_, vec3, p_278320_.m_20191_().m_82369_(p_278342_).m_82400_(1.0D), p_278257_);
      if (hitresult1 != null) {
         hitresult = hitresult1;
      }

      return hitresult;
   }

   @Nullable
   public static EntityHitResult m_37287_(Entity p_37288_, Vec3 p_37289_, Vec3 p_37290_, AABB p_37291_, Predicate<Entity> p_37292_, double p_37293_) {
      Level level = p_37288_.m_9236_();
      double d0 = p_37293_;
      Entity entity = null;
      Vec3 vec3 = null;

      for(Entity entity1 : level.m_6249_(p_37288_, p_37291_, p_37292_)) {
         AABB aabb = entity1.m_20191_().m_82400_((double)entity1.m_6143_());
         Optional<Vec3> optional = aabb.m_82371_(p_37289_, p_37290_);
         if (aabb.m_82390_(p_37289_)) {
            if (d0 >= 0.0D) {
               entity = entity1;
               vec3 = optional.orElse(p_37289_);
               d0 = 0.0D;
            }
         } else if (optional.isPresent()) {
            Vec3 vec31 = optional.get();
            double d1 = p_37289_.m_82557_(vec31);
            if (d1 < d0 || d0 == 0.0D) {
               if (entity1.m_20201_() == p_37288_.m_20201_() && !entity1.canRiderInteract()) {
                  if (d0 == 0.0D) {
                     entity = entity1;
                     vec3 = vec31;
                  }
               } else {
                  entity = entity1;
                  vec3 = vec31;
                  d0 = d1;
               }
            }
         }
      }

      return entity == null ? null : new EntityHitResult(entity, vec3);
   }

   @Nullable
   public static EntityHitResult m_37304_(Level p_37305_, Entity p_37306_, Vec3 p_37307_, Vec3 p_37308_, AABB p_37309_, Predicate<Entity> p_37310_) {
      return m_150175_(p_37305_, p_37306_, p_37307_, p_37308_, p_37309_, p_37310_, 0.3F);
   }

   @Nullable
   public static EntityHitResult m_150175_(Level p_150176_, Entity p_150177_, Vec3 p_150178_, Vec3 p_150179_, AABB p_150180_, Predicate<Entity> p_150181_, float p_150182_) {
      double d0 = Double.MAX_VALUE;
      Entity entity = null;

      for(Entity entity1 : p_150176_.m_6249_(p_150177_, p_150180_, p_150181_)) {
         AABB aabb = entity1.m_20191_().m_82400_((double)p_150182_);
         Optional<Vec3> optional = aabb.m_82371_(p_150178_, p_150179_);
         if (optional.isPresent()) {
            double d1 = p_150178_.m_82557_(optional.get());
            if (d1 < d0) {
               entity = entity1;
               d0 = d1;
            }
         }
      }

      return entity == null ? null : new EntityHitResult(entity);
   }

   public static void m_37284_(Entity p_37285_, float p_37286_) {
      Vec3 vec3 = p_37285_.m_20184_();
      if (vec3.m_82556_() != 0.0D) {
         double d0 = vec3.m_165924_();
         p_37285_.m_146922_((float)(Mth.m_14136_(vec3.f_82481_, vec3.f_82479_) * (double)(180F / (float)Math.PI)) + 90.0F);
         p_37285_.m_146926_((float)(Mth.m_14136_(d0, vec3.f_82480_) * (double)(180F / (float)Math.PI)) - 90.0F);

         while(p_37285_.m_146909_() - p_37285_.f_19860_ < -180.0F) {
            p_37285_.f_19860_ -= 360.0F;
         }

         while(p_37285_.m_146909_() - p_37285_.f_19860_ >= 180.0F) {
            p_37285_.f_19860_ += 360.0F;
         }

         while(p_37285_.m_146908_() - p_37285_.f_19859_ < -180.0F) {
            p_37285_.f_19859_ -= 360.0F;
         }

         while(p_37285_.m_146908_() - p_37285_.f_19859_ >= 180.0F) {
            p_37285_.f_19859_ += 360.0F;
         }

         p_37285_.m_146926_(Mth.m_14179_(p_37286_, p_37285_.f_19860_, p_37285_.m_146909_()));
         p_37285_.m_146922_(Mth.m_14179_(p_37286_, p_37285_.f_19859_, p_37285_.m_146908_()));
      }
   }

   @Deprecated // Forge: Use the version below that takes in a Predicate<Item> instead of an Item
   public static InteractionHand m_37297_(LivingEntity p_37298_, Item p_37299_) {
      return p_37298_.m_21205_().m_150930_(p_37299_) ? InteractionHand.MAIN_HAND : InteractionHand.OFF_HAND;
   }

   public static InteractionHand getWeaponHoldingHand(LivingEntity livingEntity, Predicate<Item> itemPredicate) {
      return itemPredicate.test(livingEntity.m_21205_().m_41720_()) ? InteractionHand.MAIN_HAND : InteractionHand.OFF_HAND;
   }

   public static AbstractArrow m_37300_(LivingEntity p_37301_, ItemStack p_37302_, float p_37303_) {
      ArrowItem arrowitem = (ArrowItem)(p_37302_.m_41720_() instanceof ArrowItem ? p_37302_.m_41720_() : Items.f_42412_);
      AbstractArrow abstractarrow = arrowitem.m_6394_(p_37301_.m_9236_(), p_37302_, p_37301_);
      abstractarrow.m_36745_(p_37301_, p_37303_);
      if (p_37302_.m_150930_(Items.f_42738_) && abstractarrow instanceof Arrow) {
         ((Arrow)abstractarrow).m_36878_(p_37302_);
      }

      return abstractarrow;
   }
}
