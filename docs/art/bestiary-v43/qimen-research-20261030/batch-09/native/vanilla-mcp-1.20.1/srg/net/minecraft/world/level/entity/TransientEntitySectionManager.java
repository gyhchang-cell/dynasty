package net.minecraft.world.level.entity;

import com.mojang.logging.LogUtils;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import it.unimi.dsi.fastutil.longs.LongSet;
import net.minecraft.core.BlockPos;
import net.minecraft.core.SectionPos;
import net.minecraft.util.VisibleForDebug;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.ChunkPos;
import org.slf4j.Logger;

public class TransientEntitySectionManager<T extends EntityAccess> {
   static final Logger f_157635_ = LogUtils.getLogger();
   final LevelCallback<T> f_157636_;
   final EntityLookup<T> f_157637_;
   final EntitySectionStorage<T> f_157638_;
   private final LongSet f_157639_ = new LongOpenHashSet();
   private final LevelEntityGetter<T> f_157640_;

   public TransientEntitySectionManager(Class<T> p_157643_, LevelCallback<T> p_157644_) {
      this.f_157637_ = new EntityLookup<>();
      this.f_157638_ = new EntitySectionStorage<>(p_157643_, (p_157647_) -> {
         return this.f_157639_.contains(p_157647_) ? Visibility.TICKING : Visibility.TRACKED;
      });
      this.f_157636_ = p_157644_;
      this.f_157640_ = new LevelEntityGetterAdapter<>(this.f_157637_, this.f_157638_);
   }

   public void m_157651_(ChunkPos p_157652_) {
      long i = p_157652_.m_45588_();
      this.f_157639_.add(i);
      this.f_157638_.m_156888_(i).forEach((p_157663_) -> {
         Visibility visibility = p_157663_.m_156838_(Visibility.TICKING);
         if (!visibility.m_157691_()) {
            p_157663_.m_156845_().filter((p_157666_) -> {
               return !p_157666_.m_142389_();
            }).forEach(this.f_157636_::m_141987_);
         }

      });
   }

   public void m_157658_(ChunkPos p_157659_) {
      long i = p_157659_.m_45588_();
      this.f_157639_.remove(i);
      this.f_157638_.m_156888_(i).forEach((p_157656_) -> {
         Visibility visibility = p_157656_.m_156838_(Visibility.TRACKED);
         if (visibility.m_157691_()) {
            p_157656_.m_156845_().filter((p_157661_) -> {
               return !p_157661_.m_142389_();
            }).forEach(this.f_157636_::m_141983_);
         }

      });
   }

   public LevelEntityGetter<T> m_157645_() {
      return this.f_157640_;
   }

   public void m_157653_(T p_157654_) {
      this.f_157637_.m_156814_(p_157654_);
      long i = SectionPos.m_175568_(p_157654_.m_20183_());
      EntitySection<T> entitysection = this.f_157638_.m_156893_(i);
      entitysection.m_188346_(p_157654_);
      p_157654_.m_141960_(new TransientEntitySectionManager.Callback(p_157654_, i, entitysection));
      this.f_157636_.m_141989_(p_157654_);
      this.f_157636_.m_141985_(p_157654_);
      if (p_157654_.m_142389_() || entitysection.m_156848_().m_157691_()) {
         this.f_157636_.m_141987_(p_157654_);
      }

   }

   @VisibleForDebug
   public int m_157657_() {
      return this.f_157637_.m_156821_();
   }

   void m_157648_(long p_157649_, EntitySection<T> p_157650_) {
      if (p_157650_.m_156833_()) {
         this.f_157638_.m_156897_(p_157649_);
      }

   }

   @VisibleForDebug
   public String m_157664_() {
      return this.f_157637_.m_156821_() + "," + this.f_157638_.m_156887_() + "," + this.f_157639_.size();
   }

   class Callback implements EntityInLevelCallback {
      private final T f_157668_;
      private long f_157669_;
      private EntitySection<T> f_157670_;

      Callback(T p_157673_, long p_157674_, EntitySection<T> p_157675_) {
         this.f_157668_ = p_157673_;
         this.f_157669_ = p_157674_;
         this.f_157670_ = p_157675_;
      }

      public void m_142044_() {
         BlockPos blockpos = this.f_157668_.m_20183_();
         long i = SectionPos.m_175568_(blockpos);
         if (i != this.f_157669_) {
            Visibility visibility = this.f_157670_.m_156848_();
            if (!this.f_157670_.m_188355_(this.f_157668_)) {
               TransientEntitySectionManager.f_157635_.warn("Entity {} wasn't found in section {} (moving to {})", this.f_157668_, SectionPos.m_123184_(this.f_157669_), i);
            }

            TransientEntitySectionManager.this.m_157648_(this.f_157669_, this.f_157670_);
            EntitySection<T> entitysection = TransientEntitySectionManager.this.f_157638_.m_156893_(i);
            entitysection.m_188346_(this.f_157668_);
            this.f_157670_ = entitysection;
            this.f_157669_ = i;
            TransientEntitySectionManager.this.f_157636_.m_214006_(this.f_157668_);
            if (!this.f_157668_.m_142389_()) {
               boolean flag = visibility.m_157691_();
               boolean flag1 = entitysection.m_156848_().m_157691_();
               if (flag && !flag1) {
                  TransientEntitySectionManager.this.f_157636_.m_141983_(this.f_157668_);
               } else if (!flag && flag1) {
                  TransientEntitySectionManager.this.f_157636_.m_141987_(this.f_157668_);
               }
            }
         }

      }

      public void m_142472_(Entity.RemovalReason p_157678_) {
         if (!this.f_157670_.m_188355_(this.f_157668_)) {
            TransientEntitySectionManager.f_157635_.warn("Entity {} wasn't found in section {} (destroying due to {})", this.f_157668_, SectionPos.m_123184_(this.f_157669_), p_157678_);
         }

         Visibility visibility = this.f_157670_.m_156848_();
         if (visibility.m_157691_() || this.f_157668_.m_142389_()) {
            TransientEntitySectionManager.this.f_157636_.m_141983_(this.f_157668_);
         }

         TransientEntitySectionManager.this.f_157636_.m_141981_(this.f_157668_);
         TransientEntitySectionManager.this.f_157636_.m_141986_(this.f_157668_);
         TransientEntitySectionManager.this.f_157637_.m_156822_(this.f_157668_);
         this.f_157668_.m_141960_(f_156799_);
         TransientEntitySectionManager.this.m_157648_(this.f_157669_, this.f_157670_);
      }
   }
}
