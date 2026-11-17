package net.minecraft.world.level;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.Lists;
import java.util.List;
import java.util.UUID;
import java.util.function.Predicate;
import javax.annotation.Nullable;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntitySelector;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.targeting.TargetingConditions;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.entity.EntityTypeTest;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.shapes.BooleanOp;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

public interface EntityGetter {
   List<Entity> m_6249_(@Nullable Entity p_45936_, AABB p_45937_, Predicate<? super Entity> p_45938_);

   <T extends Entity> List<T> m_142425_(EntityTypeTest<Entity, T> p_151464_, AABB p_151465_, Predicate<? super T> p_151466_);

   default <T extends Entity> List<T> m_6443_(Class<T> p_45979_, AABB p_45980_, Predicate<? super T> p_45981_) {
      return this.m_142425_(EntityTypeTest.m_156916_(p_45979_), p_45980_, p_45981_);
   }

   List<? extends Player> m_6907_();

   default List<Entity> m_45933_(@Nullable Entity p_45934_, AABB p_45935_) {
      return this.m_6249_(p_45934_, p_45935_, EntitySelector.f_20408_);
   }

   default boolean m_5450_(@Nullable Entity p_45939_, VoxelShape p_45940_) {
      if (p_45940_.m_83281_()) {
         return true;
      } else {
         for(Entity entity : this.m_45933_(p_45939_, p_45940_.m_83215_())) {
            if (!entity.m_213877_() && entity.f_19850_ && (p_45939_ == null || !entity.m_20365_(p_45939_)) && Shapes.m_83157_(p_45940_, Shapes.m_83064_(entity.m_20191_()), BooleanOp.f_82689_)) {
               return false;
            }
         }

         return true;
      }
   }

   default <T extends Entity> List<T> m_45976_(Class<T> p_45977_, AABB p_45978_) {
      return this.m_6443_(p_45977_, p_45978_, EntitySelector.f_20408_);
   }

   default List<VoxelShape> m_183134_(@Nullable Entity p_186451_, AABB p_186452_) {
      if (p_186452_.m_82309_() < 1.0E-7D) {
         return List.of();
      } else {
         Predicate<Entity> predicate = p_186451_ == null ? EntitySelector.f_185987_ : EntitySelector.f_20408_.and(p_186451_::m_7337_);
         List<Entity> list = this.m_6249_(p_186451_, p_186452_.m_82400_(1.0E-7D), predicate);
         if (list.isEmpty()) {
            return List.of();
         } else {
            ImmutableList.Builder<VoxelShape> builder = ImmutableList.builderWithExpectedSize(list.size());

            for(Entity entity : list) {
               builder.add(Shapes.m_83064_(entity.m_20191_()));
            }

            return builder.build();
         }
      }
   }

   @Nullable
   default Player m_5788_(double p_45919_, double p_45920_, double p_45921_, double p_45922_, @Nullable Predicate<Entity> p_45923_) {
      double d0 = -1.0D;
      Player player = null;

      for(Player player1 : this.m_6907_()) {
         if (p_45923_ == null || p_45923_.test(player1)) {
            double d1 = player1.m_20275_(p_45919_, p_45920_, p_45921_);
            if ((p_45922_ < 0.0D || d1 < p_45922_ * p_45922_) && (d0 == -1.0D || d1 < d0)) {
               d0 = d1;
               player = player1;
            }
         }
      }

      return player;
   }

   @Nullable
   default Player m_45930_(Entity p_45931_, double p_45932_) {
      return this.m_45924_(p_45931_.m_20185_(), p_45931_.m_20186_(), p_45931_.m_20189_(), p_45932_, false);
   }

   @Nullable
   default Player m_45924_(double p_45925_, double p_45926_, double p_45927_, double p_45928_, boolean p_45929_) {
      Predicate<Entity> predicate = p_45929_ ? EntitySelector.f_20406_ : EntitySelector.f_20408_;
      return this.m_5788_(p_45925_, p_45926_, p_45927_, p_45928_, predicate);
   }

   default boolean m_45914_(double p_45915_, double p_45916_, double p_45917_, double p_45918_) {
      for(Player player : this.m_6907_()) {
         if (EntitySelector.f_20408_.test(player) && EntitySelector.f_20403_.test(player)) {
            double d0 = player.m_20275_(p_45915_, p_45916_, p_45917_);
            if (p_45918_ < 0.0D || d0 < p_45918_ * p_45918_) {
               return true;
            }
         }
      }

      return false;
   }

   @Nullable
   default Player m_45946_(TargetingConditions p_45947_, LivingEntity p_45948_) {
      return this.m_45982_(this.m_6907_(), p_45947_, p_45948_, p_45948_.m_20185_(), p_45948_.m_20186_(), p_45948_.m_20189_());
   }

   @Nullable
   default Player m_45949_(TargetingConditions p_45950_, LivingEntity p_45951_, double p_45952_, double p_45953_, double p_45954_) {
      return this.m_45982_(this.m_6907_(), p_45950_, p_45951_, p_45952_, p_45953_, p_45954_);
   }

   @Nullable
   default Player m_45941_(TargetingConditions p_45942_, double p_45943_, double p_45944_, double p_45945_) {
      return this.m_45982_(this.m_6907_(), p_45942_, (LivingEntity)null, p_45943_, p_45944_, p_45945_);
   }

   @Nullable
   default <T extends LivingEntity> T m_45963_(Class<? extends T> p_45964_, TargetingConditions p_45965_, @Nullable LivingEntity p_45966_, double p_45967_, double p_45968_, double p_45969_, AABB p_45970_) {
      return this.m_45982_(this.m_6443_(p_45964_, p_45970_, (p_186454_) -> {
         return true;
      }), p_45965_, p_45966_, p_45967_, p_45968_, p_45969_);
   }

   @Nullable
   default <T extends LivingEntity> T m_45982_(List<? extends T> p_45983_, TargetingConditions p_45984_, @Nullable LivingEntity p_45985_, double p_45986_, double p_45987_, double p_45988_) {
      double d0 = -1.0D;
      T t = null;

      for(T t1 : p_45983_) {
         if (p_45984_.m_26885_(p_45985_, t1)) {
            double d1 = t1.m_20275_(p_45986_, p_45987_, p_45988_);
            if (d0 == -1.0D || d1 < d0) {
               d0 = d1;
               t = t1;
            }
         }
      }

      return t;
   }

   default List<Player> m_45955_(TargetingConditions p_45956_, LivingEntity p_45957_, AABB p_45958_) {
      List<Player> list = Lists.newArrayList();

      for(Player player : this.m_6907_()) {
         if (p_45958_.m_82393_(player.m_20185_(), player.m_20186_(), player.m_20189_()) && p_45956_.m_26885_(p_45957_, player)) {
            list.add(player);
         }
      }

      return list;
   }

   default <T extends LivingEntity> List<T> m_45971_(Class<T> p_45972_, TargetingConditions p_45973_, LivingEntity p_45974_, AABB p_45975_) {
      List<T> list = this.m_6443_(p_45972_, p_45975_, (p_186450_) -> {
         return true;
      });
      List<T> list1 = Lists.newArrayList();

      for(T t : list) {
         if (p_45973_.m_26885_(p_45974_, t)) {
            list1.add(t);
         }
      }

      return list1;
   }

   @Nullable
   default Player m_46003_(UUID p_46004_) {
      for(int i = 0; i < this.m_6907_().size(); ++i) {
         Player player = this.m_6907_().get(i);
         if (p_46004_.equals(player.m_20148_())) {
            return player;
         }
      }

      return null;
   }
}
