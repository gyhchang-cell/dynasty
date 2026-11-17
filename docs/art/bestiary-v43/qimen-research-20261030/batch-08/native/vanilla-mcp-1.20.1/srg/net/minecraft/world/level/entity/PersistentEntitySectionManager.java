package net.minecraft.world.level.entity;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.Queues;
import com.google.common.collect.Sets;
import com.mojang.logging.LogUtils;
import it.unimi.dsi.fastutil.longs.Long2ObjectMap;
import it.unimi.dsi.fastutil.longs.Long2ObjectMaps;
import it.unimi.dsi.fastutil.longs.Long2ObjectOpenHashMap;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import it.unimi.dsi.fastutil.longs.LongSet;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.io.Writer;
import java.util.List;
import java.util.Queue;
import java.util.Set;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import net.minecraft.core.BlockPos;
import net.minecraft.core.SectionPos;
import net.minecraft.server.level.FullChunkStatus;
import net.minecraft.util.CsvOutput;
import net.minecraft.util.VisibleForDebug;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.ChunkPos;
import org.slf4j.Logger;

public class PersistentEntitySectionManager<T extends EntityAccess> implements AutoCloseable {
   static final Logger f_157490_ = LogUtils.getLogger();
   final Set<UUID> f_157491_ = Sets.newHashSet();
   final LevelCallback<T> f_157492_;
   private final EntityPersistentStorage<T> f_157493_;
   private final EntityLookup<T> f_157494_;
   final EntitySectionStorage<T> f_157495_;
   private final LevelEntityGetter<T> f_157496_;
   private final Long2ObjectMap<Visibility> f_157497_ = new Long2ObjectOpenHashMap<>();
   private final Long2ObjectMap<PersistentEntitySectionManager.ChunkLoadStatus> f_157498_ = new Long2ObjectOpenHashMap<>();
   private final LongSet f_157499_ = new LongOpenHashSet();
   private final Queue<ChunkEntities<T>> f_157500_ = Queues.newConcurrentLinkedQueue();

   public PersistentEntitySectionManager(Class<T> p_157503_, LevelCallback<T> p_157504_, EntityPersistentStorage<T> p_157505_) {
      this.f_157494_ = new EntityLookup<>();
      this.f_157495_ = new EntitySectionStorage<>(p_157503_, this.f_157497_);
      this.f_157497_.defaultReturnValue(Visibility.HIDDEN);
      this.f_157498_.defaultReturnValue(PersistentEntitySectionManager.ChunkLoadStatus.FRESH);
      this.f_157492_ = p_157504_;
      this.f_157493_ = p_157505_;
      this.f_157496_ = new LevelEntityGetterAdapter<>(this.f_157494_, this.f_157495_);
   }

   void m_157509_(long p_157510_, EntitySection<T> p_157511_) {
      if (p_157511_.m_156833_()) {
         this.f_157495_.m_156897_(p_157510_);
      }

   }

   private boolean m_157557_(T p_157558_) {
      if (!this.f_157491_.add(p_157558_.m_20148_())) {
         f_157490_.warn("UUID of added entity already exists: {}", (Object)p_157558_);
         return false;
      } else {
         return true;
      }
   }

   public boolean m_157533_(T p_157534_) {
      return this.m_157538_(p_157534_, false);
   }

   private boolean m_157538_(T p_157539_, boolean p_157540_) {
      if (!this.m_157557_(p_157539_)) {
         return false;
      } else {
         long i = SectionPos.m_175568_(p_157539_.m_20183_());
         EntitySection<T> entitysection = this.f_157495_.m_156893_(i);
         entitysection.m_188346_(p_157539_);
         p_157539_.m_141960_(new PersistentEntitySectionManager.Callback(p_157539_, i, entitysection));
         if (!p_157540_) {
            this.f_157492_.m_141989_(p_157539_);
         }

         Visibility visibility = m_157535_(p_157539_, entitysection.m_156848_());
         if (visibility.m_157694_()) {
            this.m_157575_(p_157539_);
         }

         if (visibility.m_157691_()) {
            this.m_157564_(p_157539_);
         }

         return true;
      }
   }

   static <T extends EntityAccess> Visibility m_157535_(T p_157536_, Visibility p_157537_) {
      return p_157536_.m_142389_() ? Visibility.TICKING : p_157537_;
   }

   public void m_157552_(Stream<T> p_157553_) {
      p_157553_.forEach((p_157607_) -> {
         this.m_157538_(p_157607_, true);
      });
   }

   public void m_157559_(Stream<T> p_157560_) {
      p_157560_.forEach((p_157605_) -> {
         this.m_157538_(p_157605_, false);
      });
   }

   void m_157564_(T p_157565_) {
      this.f_157492_.m_141987_(p_157565_);
   }

   void m_157570_(T p_157571_) {
      this.f_157492_.m_141983_(p_157571_);
   }

   void m_157575_(T p_157576_) {
      this.f_157494_.m_156814_(p_157576_);
      this.f_157492_.m_141985_(p_157576_);
   }

   void m_157580_(T p_157581_) {
      this.f_157492_.m_141981_(p_157581_);
      this.f_157494_.m_156822_(p_157581_);
   }

   public void m_287207_(ChunkPos p_287590_, FullChunkStatus p_287623_) {
      Visibility visibility = Visibility.m_287140_(p_287623_);
      this.m_157527_(p_287590_, visibility);
   }

   public void m_157527_(ChunkPos p_157528_, Visibility p_157529_) {
      long i = p_157528_.m_45588_();
      if (p_157529_ == Visibility.HIDDEN) {
         this.f_157497_.remove(i);
         this.f_157499_.add(i);
      } else {
         this.f_157497_.put(i, p_157529_);
         this.f_157499_.remove(i);
         this.m_157555_(i);
      }

      this.f_157495_.m_156888_(i).forEach((p_157545_) -> {
         Visibility visibility = p_157545_.m_156838_(p_157529_);
         boolean flag = visibility.m_157694_();
         boolean flag1 = p_157529_.m_157694_();
         boolean flag2 = visibility.m_157691_();
         boolean flag3 = p_157529_.m_157691_();
         if (flag2 && !flag3) {
            p_157545_.m_156845_().filter((p_157603_) -> {
               return !p_157603_.m_142389_();
            }).forEach(this::m_157570_);
         }

         if (flag && !flag1) {
            p_157545_.m_156845_().filter((p_157601_) -> {
               return !p_157601_.m_142389_();
            }).forEach(this::m_157580_);
         } else if (!flag && flag1) {
            p_157545_.m_156845_().filter((p_157599_) -> {
               return !p_157599_.m_142389_();
            }).forEach(this::m_157575_);
         }

         if (!flag2 && flag3) {
            p_157545_.m_156845_().filter((p_157597_) -> {
               return !p_157597_.m_142389_();
            }).forEach(this::m_157564_);
         }

      });
   }

   private void m_157555_(long p_157556_) {
      PersistentEntitySectionManager.ChunkLoadStatus persistententitysectionmanager$chunkloadstatus = this.f_157498_.get(p_157556_);
      if (persistententitysectionmanager$chunkloadstatus == PersistentEntitySectionManager.ChunkLoadStatus.FRESH) {
         this.m_157562_(p_157556_);
      }

   }

   private boolean m_157512_(long p_157513_, Consumer<T> p_157514_) {
      PersistentEntitySectionManager.ChunkLoadStatus persistententitysectionmanager$chunkloadstatus = this.f_157498_.get(p_157513_);
      if (persistententitysectionmanager$chunkloadstatus == PersistentEntitySectionManager.ChunkLoadStatus.PENDING) {
         return false;
      } else {
         List<T> list = this.f_157495_.m_156888_(p_157513_).flatMap((p_157542_) -> {
            return p_157542_.m_156845_().filter(EntityAccess::m_142391_);
         }).collect(Collectors.toList());
         if (list.isEmpty()) {
            if (persistententitysectionmanager$chunkloadstatus == PersistentEntitySectionManager.ChunkLoadStatus.LOADED) {
               this.f_157493_.m_141971_(new ChunkEntities<>(new ChunkPos(p_157513_), ImmutableList.of()));
            }

            return true;
         } else if (persistententitysectionmanager$chunkloadstatus == PersistentEntitySectionManager.ChunkLoadStatus.FRESH) {
            this.m_157562_(p_157513_);
            return false;
         } else {
            this.f_157493_.m_141971_(new ChunkEntities<>(new ChunkPos(p_157513_), list));
            list.forEach(p_157514_);
            return true;
         }
      }
   }

   private void m_157562_(long p_157563_) {
      this.f_157498_.put(p_157563_, PersistentEntitySectionManager.ChunkLoadStatus.PENDING);
      ChunkPos chunkpos = new ChunkPos(p_157563_);
      this.f_157493_.m_141930_(chunkpos).thenAccept(this.f_157500_::add).exceptionally((p_157532_) -> {
         f_157490_.error("Failed to read chunk {}", chunkpos, p_157532_);
         return null;
      });
   }

   private boolean m_157568_(long p_157569_) {
      boolean flag = this.m_157512_(p_157569_, (p_157595_) -> {
         p_157595_.m_142429_().forEach(this::m_157585_);
      });
      if (!flag) {
         return false;
      } else {
         this.f_157498_.remove(p_157569_);
         return true;
      }
   }

   private void m_157585_(EntityAccess p_157586_) {
      p_157586_.m_142467_(Entity.RemovalReason.UNLOADED_TO_CHUNK);
      p_157586_.m_141960_(EntityInLevelCallback.f_156799_);
   }

   private void m_157577_() {
      this.f_157499_.removeIf((long p_157584_) -> {
         return this.f_157497_.get(p_157584_) != Visibility.HIDDEN ? true : this.m_157568_(p_157584_);
      });
   }

   private void m_157582_() {
      ChunkEntities<T> chunkentities;
      while((chunkentities = this.f_157500_.poll()) != null) {
         chunkentities.m_156792_().forEach((p_157593_) -> {
            this.m_157538_(p_157593_, true);
         });
         this.f_157498_.put(chunkentities.m_156791_().m_45588_(), PersistentEntitySectionManager.ChunkLoadStatus.LOADED);
      }

   }

   public void m_157506_() {
      this.m_157582_();
      this.m_157577_();
   }

   private LongSet m_157587_() {
      LongSet longset = this.f_157495_.m_156857_();

      for(Long2ObjectMap.Entry<PersistentEntitySectionManager.ChunkLoadStatus> entry : Long2ObjectMaps.fastIterable(this.f_157498_)) {
         if (entry.getValue() == PersistentEntitySectionManager.ChunkLoadStatus.LOADED) {
            longset.add(entry.getLongKey());
         }
      }

      return longset;
   }

   public void m_157554_() {
      this.m_157587_().forEach((long p_157579_) -> {
         boolean flag = this.f_157497_.get(p_157579_) == Visibility.HIDDEN;
         if (flag) {
            this.m_157568_(p_157579_);
         } else {
            this.m_157512_(p_157579_, (p_157591_) -> {
            });
         }

      });
   }

   public void m_157561_() {
      LongSet longset = this.m_157587_();

      while(!longset.isEmpty()) {
         this.f_157493_.m_182219_(false);
         this.m_157582_();
         longset.removeIf((long p_157574_) -> {
            boolean flag = this.f_157497_.get(p_157574_) == Visibility.HIDDEN;
            return flag ? this.m_157568_(p_157574_) : this.m_157512_(p_157574_, (p_157589_) -> {
            });
         });
      }

      this.f_157493_.m_182219_(true);
   }

   public void close() throws IOException {
      this.m_157561_();
      this.f_157493_.close();
   }

   public boolean m_157550_(UUID p_157551_) {
      return this.f_157491_.contains(p_157551_);
   }

   public LevelEntityGetter<T> m_157567_() {
      return this.f_157496_;
   }

   public boolean m_202167_(BlockPos p_202168_) {
      return this.f_157497_.get(ChunkPos.m_151388_(p_202168_)).m_157691_();
   }

   public boolean m_202165_(ChunkPos p_202166_) {
      return this.f_157497_.get(p_202166_.m_45588_()).m_157691_();
   }

   public boolean m_157507_(long p_157508_) {
      return this.f_157498_.get(p_157508_) == PersistentEntitySectionManager.ChunkLoadStatus.LOADED;
   }

   public void m_157548_(Writer p_157549_) throws IOException {
      CsvOutput csvoutput = CsvOutput.m_13619_().m_13630_("x").m_13630_("y").m_13630_("z").m_13630_("visibility").m_13630_("load_status").m_13630_("entity_count").m_13628_(p_157549_);
      this.f_157495_.m_156857_().forEach((long p_157517_) -> {
         PersistentEntitySectionManager.ChunkLoadStatus persistententitysectionmanager$chunkloadstatus = this.f_157498_.get(p_157517_);
         this.f_157495_.m_156861_(p_157517_).forEach((p_157521_) -> {
            EntitySection<T> entitysection = this.f_157495_.m_156895_(p_157521_);
            if (entitysection != null) {
               try {
                  csvoutput.m_13624_(SectionPos.m_123213_(p_157521_), SectionPos.m_123225_(p_157521_), SectionPos.m_123230_(p_157521_), entitysection.m_156848_(), persistententitysectionmanager$chunkloadstatus, entitysection.m_156849_());
               } catch (IOException ioexception) {
                  throw new UncheckedIOException(ioexception);
               }
            }

         });
      });
   }

   @VisibleForDebug
   public String m_157572_() {
      return this.f_157491_.size() + "," + this.f_157494_.m_156821_() + "," + this.f_157495_.m_156887_() + "," + this.f_157498_.size() + "," + this.f_157497_.size() + "," + this.f_157500_.size() + "," + this.f_157499_.size();
   }

   class Callback implements EntityInLevelCallback {
      private final T f_157609_;
      private long f_157610_;
      private EntitySection<T> f_157611_;

      Callback(T p_157614_, long p_157615_, EntitySection<T> p_157616_) {
         this.f_157609_ = p_157614_;
         this.f_157610_ = p_157615_;
         this.f_157611_ = p_157616_;
      }

      public void m_142044_() {
         BlockPos blockpos = this.f_157609_.m_20183_();
         long i = SectionPos.m_175568_(blockpos);
         if (i != this.f_157610_) {
            Visibility visibility = this.f_157611_.m_156848_();
            if (!this.f_157611_.m_188355_(this.f_157609_)) {
               PersistentEntitySectionManager.f_157490_.warn("Entity {} wasn't found in section {} (moving to {})", this.f_157609_, SectionPos.m_123184_(this.f_157610_), i);
            }

            PersistentEntitySectionManager.this.m_157509_(this.f_157610_, this.f_157611_);
            EntitySection<T> entitysection = PersistentEntitySectionManager.this.f_157495_.m_156893_(i);
            entitysection.m_188346_(this.f_157609_);
            this.f_157611_ = entitysection;
            this.f_157610_ = i;
            this.m_157620_(visibility, entitysection.m_156848_());
         }

      }

      private void m_157620_(Visibility p_157621_, Visibility p_157622_) {
         Visibility visibility = PersistentEntitySectionManager.m_157535_(this.f_157609_, p_157621_);
         Visibility visibility1 = PersistentEntitySectionManager.m_157535_(this.f_157609_, p_157622_);
         if (visibility == visibility1) {
            if (visibility1.m_157694_()) {
               PersistentEntitySectionManager.this.f_157492_.m_214006_(this.f_157609_);
            }

         } else {
            boolean flag = visibility.m_157694_();
            boolean flag1 = visibility1.m_157694_();
            if (flag && !flag1) {
               PersistentEntitySectionManager.this.m_157580_(this.f_157609_);
            } else if (!flag && flag1) {
               PersistentEntitySectionManager.this.m_157575_(this.f_157609_);
            }

            boolean flag2 = visibility.m_157691_();
            boolean flag3 = visibility1.m_157691_();
            if (flag2 && !flag3) {
               PersistentEntitySectionManager.this.m_157570_(this.f_157609_);
            } else if (!flag2 && flag3) {
               PersistentEntitySectionManager.this.m_157564_(this.f_157609_);
            }

            if (flag1) {
               PersistentEntitySectionManager.this.f_157492_.m_214006_(this.f_157609_);
            }

         }
      }

      public void m_142472_(Entity.RemovalReason p_157619_) {
         if (!this.f_157611_.m_188355_(this.f_157609_)) {
            PersistentEntitySectionManager.f_157490_.warn("Entity {} wasn't found in section {} (destroying due to {})", this.f_157609_, SectionPos.m_123184_(this.f_157610_), p_157619_);
         }

         Visibility visibility = PersistentEntitySectionManager.m_157535_(this.f_157609_, this.f_157611_.m_156848_());
         if (visibility.m_157691_()) {
            PersistentEntitySectionManager.this.m_157570_(this.f_157609_);
         }

         if (visibility.m_157694_()) {
            PersistentEntitySectionManager.this.m_157580_(this.f_157609_);
         }

         if (p_157619_.m_146965_()) {
            PersistentEntitySectionManager.this.f_157492_.m_141986_(this.f_157609_);
         }

         PersistentEntitySectionManager.this.f_157491_.remove(this.f_157609_.m_20148_());
         this.f_157609_.m_141960_(f_156799_);
         PersistentEntitySectionManager.this.m_157509_(this.f_157610_, this.f_157611_);
      }
   }

   static enum ChunkLoadStatus {
      FRESH,
      PENDING,
      LOADED;
   }
}
