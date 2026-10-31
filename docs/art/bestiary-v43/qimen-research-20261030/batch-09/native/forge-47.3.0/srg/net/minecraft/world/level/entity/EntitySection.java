package net.minecraft.world.level.entity;

import com.mojang.logging.LogUtils;
import java.util.Collection;
import java.util.stream.Stream;
import net.minecraft.util.AbortableIterationConsumer;
import net.minecraft.util.ClassInstanceMultiMap;
import net.minecraft.util.VisibleForDebug;
import net.minecraft.world.phys.AABB;
import org.slf4j.Logger;

public class EntitySection<T extends EntityAccess> {
   private static final Logger f_156826_ = LogUtils.getLogger();
   private final ClassInstanceMultiMap<T> f_156827_;
   private Visibility f_156828_;

   public EntitySection(Class<T> p_156831_, Visibility p_156832_) {
      this.f_156828_ = p_156832_;
      this.f_156827_ = new ClassInstanceMultiMap<>(p_156831_);
   }

   public void m_188346_(T p_188347_) {
      this.f_156827_.add(p_188347_);
   }

   public boolean m_188355_(T p_188356_) {
      return this.f_156827_.remove(p_188356_);
   }

   public AbortableIterationConsumer.Continuation m_260830_(AABB p_262016_, AbortableIterationConsumer<T> p_261863_) {
      for(T t : this.f_156827_) {
         if (t.m_20191_().m_82381_(p_262016_) && p_261863_.m_260972_(t).m_261146_()) {
            return AbortableIterationConsumer.Continuation.ABORT;
         }
      }

      return AbortableIterationConsumer.Continuation.CONTINUE;
   }

   public <U extends T> AbortableIterationConsumer.Continuation m_188348_(EntityTypeTest<T, U> p_188349_, AABB p_188350_, AbortableIterationConsumer<? super U> p_261535_) {
      Collection<? extends T> collection = this.f_156827_.m_13533_(p_188349_.m_142225_());
      if (collection.isEmpty()) {
         return AbortableIterationConsumer.Continuation.CONTINUE;
      } else {
         for(T t : collection) {
            U u = (U)((EntityAccess)p_188349_.m_141992_(t));
            if (u != null && t.m_20191_().m_82381_(p_188350_) && p_261535_.m_260972_(u).m_261146_()) {
               return AbortableIterationConsumer.Continuation.ABORT;
            }
         }

         return AbortableIterationConsumer.Continuation.CONTINUE;
      }
   }

   public boolean m_156833_() {
      return this.f_156827_.isEmpty();
   }

   public Stream<T> m_156845_() {
      return this.f_156827_.stream();
   }

   public Visibility m_156848_() {
      return this.f_156828_;
   }

   public Visibility m_156838_(Visibility p_156839_) {
      Visibility visibility = this.f_156828_;
      this.f_156828_ = p_156839_;
      return visibility;
   }

   @VisibleForDebug
   public int m_156849_() {
      return this.f_156827_.size();
   }
}
