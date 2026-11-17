package net.minecraft.network.syncher;

import com.mojang.logging.LogUtils;
import io.netty.handler.codec.DecoderException;
import io.netty.handler.codec.EncoderException;
import it.unimi.dsi.fastutil.ints.Int2ObjectMap;
import it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap;
import it.unimi.dsi.fastutil.objects.Object2IntMap;
import it.unimi.dsi.fastutil.objects.Object2IntOpenHashMap;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import javax.annotation.Nullable;
import net.minecraft.CrashReport;
import net.minecraft.CrashReportCategory;
import net.minecraft.ReportedException;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.Entity;
import org.apache.commons.lang3.ObjectUtils;
import org.slf4j.Logger;

public class SynchedEntityData {
   private static final Logger f_135342_ = LogUtils.getLogger();
   private static final Object2IntMap<Class<? extends Entity>> f_135343_ = new Object2IntOpenHashMap<>();
   private static final int f_179843_ = 254;
   private final Entity f_135344_;
   private final Int2ObjectMap<SynchedEntityData.DataItem<?>> f_135345_ = new Int2ObjectOpenHashMap<>();
   private final ReadWriteLock f_135346_ = new ReentrantReadWriteLock();
   private boolean f_135348_;

   public SynchedEntityData(Entity p_135351_) {
      this.f_135344_ = p_135351_;
   }

   public static <T> EntityDataAccessor<T> m_135353_(Class<? extends Entity> p_135354_, EntityDataSerializer<T> p_135355_) {
      if (true || f_135342_.isDebugEnabled()) { // Forge: This is very useful for mods that register keys on classes that are not their own
         try {
            Class<?> oclass = Class.forName(Thread.currentThread().getStackTrace()[2].getClassName());
            if (!oclass.equals(p_135354_)) {
               // Forge: log at warn, mods should not add to classes that they don't own, and only add stacktrace when in debug is enabled as it is mostly not needed and consumes time
               if (f_135342_.isDebugEnabled()) f_135342_.warn("defineId called for: {} from {}", p_135354_, oclass, new RuntimeException());
               else f_135342_.warn("defineId called for: {} from {}", p_135354_, oclass);
            }
         } catch (ClassNotFoundException classnotfoundexception) {
         }
      }

      int j;
      if (f_135343_.containsKey(p_135354_)) {
         j = f_135343_.getInt(p_135354_) + 1;
      } else {
         int i = 0;
         Class<?> oclass1 = p_135354_;

         while(oclass1 != Entity.class) {
            oclass1 = oclass1.getSuperclass();
            if (f_135343_.containsKey(oclass1)) {
               i = f_135343_.getInt(oclass1) + 1;
               break;
            }
         }

         j = i;
      }

      if (j > 254) {
         throw new IllegalArgumentException("Data value id is too big with " + j + "! (Max is 254)");
      } else {
         f_135343_.put(p_135354_, j);
         return p_135355_.m_135021_(j);
      }
   }

   public <T> void m_135372_(EntityDataAccessor<T> p_135373_, T p_135374_) {
      int i = p_135373_.m_135015_();
      if (i > 254) {
         throw new IllegalArgumentException("Data value id is too big with " + i + "! (Max is 254)");
      } else if (this.f_135345_.containsKey(i)) {
         throw new IllegalArgumentException("Duplicate id value for " + i + "!");
      } else if (EntityDataSerializers.m_135052_(p_135373_.m_135016_()) < 0) {
         throw new IllegalArgumentException("Unregistered serializer " + p_135373_.m_135016_() + " for " + i + "!");
      } else {
         this.m_135385_(p_135373_, p_135374_);
      }
   }

   private <T> void m_135385_(EntityDataAccessor<T> p_135386_, T p_135387_) {
      SynchedEntityData.DataItem<T> dataitem = new SynchedEntityData.DataItem<>(p_135386_, p_135387_);
      this.f_135346_.writeLock().lock();
      this.f_135345_.put(p_135386_.m_135015_(), dataitem);
      this.f_135346_.writeLock().unlock();
   }

   public <T> boolean m_285897_(EntityDataAccessor<T> p_286294_) {
      return this.f_135345_.containsKey(p_286294_.m_135015_());
   }

   private <T> SynchedEntityData.DataItem<T> m_135379_(EntityDataAccessor<T> p_135380_) {
      this.f_135346_.readLock().lock();

      SynchedEntityData.DataItem<T> dataitem;
      try {
         dataitem = (SynchedEntityData.DataItem<T>)this.f_135345_.get(p_135380_.m_135015_());
      } catch (Throwable throwable) {
         CrashReport crashreport = CrashReport.m_127521_(throwable, "Getting synched entity data");
         CrashReportCategory crashreportcategory = crashreport.m_127514_("Synched entity data");
         crashreportcategory.m_128159_("Data ID", p_135380_);
         throw new ReportedException(crashreport);
      } finally {
         this.f_135346_.readLock().unlock();
      }

      return dataitem;
   }

   public <T> T m_135370_(EntityDataAccessor<T> p_135371_) {
      return this.m_135379_(p_135371_).m_135403_();
   }

   public <T> void m_135381_(EntityDataAccessor<T> p_135382_, T p_135383_) {
      this.m_276349_(p_135382_, p_135383_, false);
   }

   public <T> void m_276349_(EntityDataAccessor<T> p_276368_, T p_276363_, boolean p_276370_) {
      SynchedEntityData.DataItem<T> dataitem = this.m_135379_(p_276368_);
      if (p_276370_ || ObjectUtils.notEqual(p_276363_, dataitem.m_135403_())) {
         dataitem.m_135397_(p_276363_);
         this.f_135344_.m_7350_(p_276368_);
         dataitem.m_135401_(true);
         this.f_135348_ = true;
      }

   }

   public boolean m_135352_() {
      return this.f_135348_;
   }

   @Nullable
   public List<SynchedEntityData.DataValue<?>> m_135378_() {
      List<SynchedEntityData.DataValue<?>> list = null;
      if (this.f_135348_) {
         this.f_135346_.readLock().lock();

         for(SynchedEntityData.DataItem<?> dataitem : this.f_135345_.values()) {
            if (dataitem.m_135406_()) {
               dataitem.m_135401_(false);
               if (list == null) {
                  list = new ArrayList<>();
               }

               list.add(dataitem.m_253123_());
            }
         }

         this.f_135346_.readLock().unlock();
      }

      this.f_135348_ = false;
      return list;
   }

   @Nullable
   public List<SynchedEntityData.DataValue<?>> m_252804_() {
      List<SynchedEntityData.DataValue<?>> list = null;
      this.f_135346_.readLock().lock();

      for(SynchedEntityData.DataItem<?> dataitem : this.f_135345_.values()) {
         if (!dataitem.m_252838_()) {
            if (list == null) {
               list = new ArrayList<>();
            }

            list.add(dataitem.m_253123_());
         }
      }

      this.f_135346_.readLock().unlock();
      return list;
   }

   public void m_135356_(List<SynchedEntityData.DataValue<?>> p_135357_) {
      this.f_135346_.writeLock().lock();

      try {
         for(SynchedEntityData.DataValue<?> datavalue : p_135357_) {
            SynchedEntityData.DataItem<?> dataitem = this.f_135345_.get(datavalue.f_252469_);
            if (dataitem != null) {
               this.m_135375_(dataitem, datavalue);
               this.f_135344_.m_7350_(dataitem.m_135396_());
            }
         }
      } finally {
         this.f_135346_.writeLock().unlock();
      }

      this.f_135344_.m_269505_(p_135357_);
   }

   private <T> void m_135375_(SynchedEntityData.DataItem<T> p_135376_, SynchedEntityData.DataValue<?> p_254484_) {
      if (!Objects.equals(p_254484_.f_252511_(), p_135376_.f_135390_.m_135016_())) {
         throw new IllegalStateException(String.format(Locale.ROOT, "Invalid entity data item type for field %d on entity %s: old=%s(%s), new=%s(%s)", p_135376_.f_135390_.m_135015_(), this.f_135344_, p_135376_.f_135391_, p_135376_.f_135391_.getClass(), p_254484_.f_252525_, p_254484_.f_252525_.getClass()));
      } else {
         p_135376_.m_135397_((T) p_254484_.f_252525_);
      }
   }

   public boolean m_135388_() {
      return this.f_135345_.isEmpty();
   }

   public static class DataItem<T> {
      final EntityDataAccessor<T> f_135390_;
      T f_135391_;
      private final T f_252454_;
      private boolean f_135392_;

      public DataItem(EntityDataAccessor<T> p_135394_, T p_135395_) {
         this.f_135390_ = p_135394_;
         this.f_252454_ = p_135395_;
         this.f_135391_ = p_135395_;
      }

      public EntityDataAccessor<T> m_135396_() {
         return this.f_135390_;
      }

      public void m_135397_(T p_135398_) {
         this.f_135391_ = p_135398_;
      }

      public T m_135403_() {
         return this.f_135391_;
      }

      public boolean m_135406_() {
         return this.f_135392_;
      }

      public void m_135401_(boolean p_135402_) {
         this.f_135392_ = p_135402_;
      }

      public boolean m_252838_() {
         return this.f_252454_.equals(this.f_135391_);
      }

      public SynchedEntityData.DataValue<T> m_253123_() {
         return SynchedEntityData.DataValue.m_252847_(this.f_135390_, this.f_135391_);
      }
   }

   public static record DataValue<T>(int f_252469_, EntityDataSerializer<T> f_252511_, T f_252525_) {
      public static <T> SynchedEntityData.DataValue<T> m_252847_(EntityDataAccessor<T> p_254543_, T p_254138_) {
         EntityDataSerializer<T> entitydataserializer = p_254543_.m_135016_();
         return new SynchedEntityData.DataValue<>(p_254543_.m_135015_(), entitydataserializer, entitydataserializer.m_7020_(p_254138_));
      }

      public void m_252897_(FriendlyByteBuf p_253709_) {
         int i = EntityDataSerializers.m_135052_(this.f_252511_);
         if (i < 0) {
            throw new EncoderException("Unknown serializer type " + this.f_252511_);
         } else {
            p_253709_.writeByte(this.f_252469_);
            p_253709_.m_130130_(i);
            this.f_252511_.m_6856_(p_253709_, this.f_252525_);
         }
      }

      public static SynchedEntityData.DataValue<?> m_252860_(FriendlyByteBuf p_254314_, int p_254356_) {
         int i = p_254314_.m_130242_();
         EntityDataSerializer<?> entitydataserializer = EntityDataSerializers.m_135048_(i);
         if (entitydataserializer == null) {
            throw new DecoderException("Unknown serializer type " + i);
         } else {
            return m_252951_(p_254314_, p_254356_, entitydataserializer);
         }
      }

      private static <T> SynchedEntityData.DataValue<T> m_252951_(FriendlyByteBuf p_254224_, int p_253899_, EntityDataSerializer<T> p_254222_) {
         return new SynchedEntityData.DataValue<>(p_253899_, p_254222_, p_254222_.m_6709_(p_254224_));
      }
   }
}
