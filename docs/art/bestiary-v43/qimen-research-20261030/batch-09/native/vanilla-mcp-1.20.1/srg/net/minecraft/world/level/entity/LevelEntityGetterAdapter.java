package net.minecraft.world.level.entity;

import java.util.UUID;
import java.util.function.Consumer;
import javax.annotation.Nullable;
import net.minecraft.util.AbortableIterationConsumer;
import net.minecraft.world.phys.AABB;

public class LevelEntityGetterAdapter<T extends EntityAccess> implements LevelEntityGetter<T> {
   private final EntityLookup<T> f_156940_;
   private final EntitySectionStorage<T> f_156941_;

   public LevelEntityGetterAdapter(EntityLookup<T> p_156943_, EntitySectionStorage<T> p_156944_) {
      this.f_156940_ = p_156943_;
      this.f_156941_ = p_156944_;
   }

   @Nullable
   public T m_142597_(int p_156947_) {
      return this.f_156940_.m_156812_(p_156947_);
   }

   @Nullable
   public T m_142694_(UUID p_156959_) {
      return this.f_156940_.m_156819_(p_156959_);
   }

   public Iterable<T> m_142273_() {
      return this.f_156940_.m_156811_();
   }

   public <U extends T> void m_142690_(EntityTypeTest<T, U> p_261718_, AbortableIterationConsumer<U> p_262009_) {
      this.f_156940_.m_260822_(p_261718_, p_262009_);
   }

   public void m_142232_(AABB p_156956_, Consumer<T> p_156957_) {
      this.f_156941_.m_261111_(p_156956_, AbortableIterationConsumer.m_260908_(p_156957_));
   }

   public <U extends T> void m_142137_(EntityTypeTest<T, U> p_261696_, AABB p_261693_, AbortableIterationConsumer<U> p_261719_) {
      this.f_156941_.m_261191_(p_261696_, p_261693_, p_261719_);
   }
}
