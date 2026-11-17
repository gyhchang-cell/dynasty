package net.minecraft.server.level;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import com.mojang.datafixers.DataFixer;
import com.mojang.datafixers.util.Either;
import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executor;
import java.util.function.BooleanSupplier;
import java.util.function.Consumer;
import java.util.function.Supplier;
import javax.annotation.Nullable;
import net.minecraft.Util;
import net.minecraft.core.BlockPos;
import net.minecraft.core.SectionPos;
import net.minecraft.network.protocol.Packet;
import net.minecraft.server.level.progress.ChunkProgressListener;
import net.minecraft.util.VisibleForDebug;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.util.thread.BlockableEventLoop;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.ai.village.poi.PoiManager;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.level.LocalMobCapCalculator;
import net.minecraft.world.level.NaturalSpawner;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.chunk.ChunkGeneratorStructureState;
import net.minecraft.world.level.chunk.ChunkSource;
import net.minecraft.world.level.chunk.ChunkStatus;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.LightChunk;
import net.minecraft.world.level.chunk.storage.ChunkScanAccess;
import net.minecraft.world.level.entity.ChunkStatusUpdateListener;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplateManager;
import net.minecraft.world.level.storage.DimensionDataStorage;
import net.minecraft.world.level.storage.LevelData;
import net.minecraft.world.level.storage.LevelStorageSource;

public class ServerChunkCache extends ChunkSource {
   private static final List<ChunkStatus> f_8326_ = ChunkStatus.m_62349_();
   private final DistanceManager f_8327_;
   public final ServerLevel f_8329_;
   final Thread f_8330_;
   final ThreadedLevelLightEngine f_8331_;
   private final ServerChunkCache.MainThreadExecutor f_8332_;
   public final ChunkMap f_8325_;
   private final DimensionDataStorage f_8333_;
   private long f_8334_;
   private boolean f_8335_ = true;
   private boolean f_8336_ = true;
   private static final int f_143226_ = 4;
   private final long[] f_8337_ = new long[4];
   private final ChunkStatus[] f_8338_ = new ChunkStatus[4];
   private final ChunkAccess[] f_8339_ = new ChunkAccess[4];
   @Nullable
   @VisibleForDebug
   private NaturalSpawner.SpawnState f_8340_;

   public ServerChunkCache(ServerLevel p_214982_, LevelStorageSource.LevelStorageAccess p_214983_, DataFixer p_214984_, StructureTemplateManager p_214985_, Executor p_214986_, ChunkGenerator p_214987_, int p_214988_, int p_214989_, boolean p_214990_, ChunkProgressListener p_214991_, ChunkStatusUpdateListener p_214992_, Supplier<DimensionDataStorage> p_214993_) {
      this.f_8329_ = p_214982_;
      this.f_8332_ = new ServerChunkCache.MainThreadExecutor(p_214982_);
      this.f_8330_ = Thread.currentThread();
      File file1 = p_214983_.m_197394_(p_214982_.m_46472_()).resolve("data").toFile();
      file1.mkdirs();
      this.f_8333_ = new DimensionDataStorage(file1, p_214984_);
      this.f_8325_ = new ChunkMap(p_214982_, p_214983_, p_214984_, p_214985_, p_214986_, this.f_8332_, this, p_214987_, p_214991_, p_214992_, p_214993_, p_214988_, p_214990_);
      this.f_8331_ = this.f_8325_.m_140166_();
      this.f_8327_ = this.f_8325_.m_143145_();
      this.f_8327_.m_183911_(p_214989_);
      this.m_8488_();
   }

   public ThreadedLevelLightEngine m_7827_() {
      return this.f_8331_;
   }

   @Nullable
   private ChunkHolder m_8364_(long p_8365_) {
      return this.f_8325_.m_140327_(p_8365_);
   }

   public int m_8427_() {
      return this.f_8325_.m_140368_();
   }

   private void m_8366_(long p_8367_, ChunkAccess p_8368_, ChunkStatus p_8369_) {
      for(int i = 3; i > 0; --i) {
         this.f_8337_[i] = this.f_8337_[i - 1];
         this.f_8338_[i] = this.f_8338_[i - 1];
         this.f_8339_[i] = this.f_8339_[i - 1];
      }

      this.f_8337_[0] = p_8367_;
      this.f_8338_[0] = p_8369_;
      this.f_8339_[0] = p_8368_;
   }

   @Nullable
   public ChunkAccess m_7587_(int p_8360_, int p_8361_, ChunkStatus p_8362_, boolean p_8363_) {
      if (Thread.currentThread() != this.f_8330_) {
         return CompletableFuture.supplyAsync(() -> {
            return this.m_7587_(p_8360_, p_8361_, p_8362_, p_8363_);
         }, this.f_8332_).join();
      } else {
         ProfilerFiller profilerfiller = this.f_8329_.m_46473_();
         profilerfiller.m_6174_("getChunk");
         long i = ChunkPos.m_45589_(p_8360_, p_8361_);

         for(int j = 0; j < 4; ++j) {
            if (i == this.f_8337_[j] && p_8362_ == this.f_8338_[j]) {
               ChunkAccess chunkaccess = this.f_8339_[j];
               if (chunkaccess != null || !p_8363_) {
                  return chunkaccess;
               }
            }
         }

         profilerfiller.m_6174_("getChunkCacheMiss");
         CompletableFuture<Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure>> completablefuture = this.m_8456_(p_8360_, p_8361_, p_8362_, p_8363_);
         this.f_8332_.m_18701_(completablefuture::isDone);
         ChunkAccess chunkaccess1 = completablefuture.join().map((p_8406_) -> {
            return p_8406_;
         }, (p_8423_) -> {
            if (p_8363_) {
               throw (IllegalStateException)Util.m_137570_(new IllegalStateException("Chunk not there when requested: " + p_8423_));
            } else {
               return null;
            }
         });
         this.m_8366_(i, chunkaccess1, p_8362_);
         return chunkaccess1;
      }
   }

   @Nullable
   public LevelChunk m_7131_(int p_8357_, int p_8358_) {
      if (Thread.currentThread() != this.f_8330_) {
         return null;
      } else {
         this.f_8329_.m_46473_().m_6174_("getChunkNow");
         long i = ChunkPos.m_45589_(p_8357_, p_8358_);

         for(int j = 0; j < 4; ++j) {
            if (i == this.f_8337_[j] && this.f_8338_[j] == ChunkStatus.f_62326_) {
               ChunkAccess chunkaccess = this.f_8339_[j];
               return chunkaccess instanceof LevelChunk ? (LevelChunk)chunkaccess : null;
            }
         }

         ChunkHolder chunkholder = this.m_8364_(i);
         if (chunkholder == null) {
            return null;
         } else {
            if (chunkholder.currentlyLoading != null) return chunkholder.currentlyLoading; // Forge: If the requested chunk is loading, bypass the future chain to prevent a deadlock.
            Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure> either = chunkholder.m_140080_(ChunkStatus.f_62326_).getNow((Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure>)null);
            if (either == null) {
               return null;
            } else {
               ChunkAccess chunkaccess1 = either.left().orElse((ChunkAccess)null);
               if (chunkaccess1 != null) {
                  this.m_8366_(i, chunkaccess1, ChunkStatus.f_62326_);
                  if (chunkaccess1 instanceof LevelChunk) {
                     return (LevelChunk)chunkaccess1;
                  }
               }

               return null;
            }
         }
      }
   }

   private void m_8488_() {
      Arrays.fill(this.f_8337_, ChunkPos.f_45577_);
      Arrays.fill(this.f_8338_, (Object)null);
      Arrays.fill(this.f_8339_, (Object)null);
   }

   public CompletableFuture<Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure>> m_8431_(int p_8432_, int p_8433_, ChunkStatus p_8434_, boolean p_8435_) {
      boolean flag = Thread.currentThread() == this.f_8330_;
      CompletableFuture<Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure>> completablefuture;
      if (flag) {
         completablefuture = this.m_8456_(p_8432_, p_8433_, p_8434_, p_8435_);
         this.f_8332_.m_18701_(completablefuture::isDone);
      } else {
         completablefuture = CompletableFuture.supplyAsync(() -> {
            return this.m_8456_(p_8432_, p_8433_, p_8434_, p_8435_);
         }, this.f_8332_).thenCompose((p_8413_) -> {
            return p_8413_;
         });
      }

      return completablefuture;
   }

   private CompletableFuture<Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure>> m_8456_(int p_8457_, int p_8458_, ChunkStatus p_8459_, boolean p_8460_) {
      ChunkPos chunkpos = new ChunkPos(p_8457_, p_8458_);
      long i = chunkpos.m_45588_();
      int j = ChunkLevel.m_287141_(p_8459_);
      ChunkHolder chunkholder = this.m_8364_(i);
      if (p_8460_) {
         this.f_8327_.m_140792_(TicketType.f_9449_, chunkpos, j, chunkpos);
         if (this.m_8416_(chunkholder, j)) {
            ProfilerFiller profilerfiller = this.f_8329_.m_46473_();
            profilerfiller.m_6180_("chunkLoad");
            this.m_8489_();
            chunkholder = this.m_8364_(i);
            profilerfiller.m_7238_();
            if (this.m_8416_(chunkholder, j)) {
               throw (IllegalStateException)Util.m_137570_(new IllegalStateException("No chunk holder after ticket has been added"));
            }
         }
      }

      return this.m_8416_(chunkholder, j) ? ChunkHolder.f_139996_ : chunkholder.m_140049_(p_8459_, this.f_8325_);
   }

   private boolean m_8416_(@Nullable ChunkHolder p_8417_, int p_8418_) {
      return p_8417_ == null || p_8417_.m_140093_() > p_8418_;
   }

   public boolean m_5563_(int p_8429_, int p_8430_) {
      ChunkHolder chunkholder = this.m_8364_((new ChunkPos(p_8429_, p_8430_)).m_45588_());
      int i = ChunkLevel.m_287141_(ChunkStatus.f_62326_);
      return !this.m_8416_(chunkholder, i);
   }

   @Nullable
   public LightChunk m_6196_(int p_8454_, int p_8455_) {
      long i = ChunkPos.m_45589_(p_8454_, p_8455_);
      ChunkHolder chunkholder = this.m_8364_(i);
      if (chunkholder == null) {
         return null;
      } else {
         int j = f_8326_.size() - 1;

         while(true) {
            ChunkStatus chunkstatus = f_8326_.get(j);
            Optional<ChunkAccess> optional = chunkholder.m_140047_(chunkstatus).getNow(ChunkHolder.f_139995_).left();
            if (optional.isPresent()) {
               return optional.get();
            }

            if (chunkstatus == ChunkStatus.f_279614_.m_62482_()) {
               return null;
            }

            --j;
         }
      }
   }

   public Level m_7653_() {
      return this.f_8329_;
   }

   public boolean m_8466_() {
      return this.f_8332_.m_7245_();
   }

   boolean m_8489_() {
      boolean flag = this.f_8327_.m_140805_(this.f_8325_);
      boolean flag1 = this.f_8325_.m_140324_();
      if (!flag && !flag1) {
         return false;
      } else {
         this.m_8488_();
         return true;
      }
   }

   public boolean m_143239_(long p_143240_) {
      ChunkHolder chunkholder = this.m_8364_(p_143240_);
      if (chunkholder == null) {
         return false;
      } else if (!this.f_8329_.m_183438_(p_143240_)) {
         return false;
      } else {
         Either<LevelChunk, ChunkHolder.ChunkLoadingFailure> either = chunkholder.m_140026_().getNow((Either<LevelChunk, ChunkHolder.ChunkLoadingFailure>)null);
         return either != null && either.left().isPresent();
      }
   }

   public void m_8419_(boolean p_8420_) {
      this.m_8489_();
      this.f_8325_.m_140318_(p_8420_);
   }

   public void close() throws IOException {
      this.m_8419_(true);
      this.f_8331_.close();
      this.f_8325_.close();
   }

   public void m_201698_(BooleanSupplier p_201913_, boolean p_201914_) {
      this.f_8329_.m_46473_().m_6180_("purge");
      this.f_8327_.m_140776_();
      this.m_8489_();
      this.f_8329_.m_46473_().m_6182_("chunks");
      if (p_201914_) {
         this.m_8490_();
      }

      this.f_8329_.m_46473_().m_6182_("unload");
      this.f_8325_.m_140280_(p_201913_);
      this.f_8329_.m_46473_().m_7238_();
      this.m_8488_();
   }

   private void m_8490_() {
      long i = this.f_8329_.m_46467_();
      long j = i - this.f_8334_;
      this.f_8334_ = i;
      boolean flag = this.f_8329_.m_46659_();
      if (flag) {
         this.f_8325_.m_140421_();
      } else {
         LevelData leveldata = this.f_8329_.m_6106_();
         ProfilerFiller profilerfiller = this.f_8329_.m_46473_();
         profilerfiller.m_6180_("pollingChunks");
         int k = this.f_8329_.m_46469_().m_46215_(GameRules.f_46143_);
         boolean flag1 = leveldata.m_6793_() % 400L == 0L;
         profilerfiller.m_6180_("naturalSpawnCount");
         int l = this.f_8327_.m_140816_();
         NaturalSpawner.SpawnState naturalspawner$spawnstate = NaturalSpawner.m_186524_(l, this.f_8329_.m_8583_(), this::m_8370_, new LocalMobCapCalculator(this.f_8325_));
         this.f_8340_ = naturalspawner$spawnstate;
         profilerfiller.m_6182_("filteringLoadedChunks");
         List<ServerChunkCache.ChunkAndHolder> list = Lists.newArrayListWithCapacity(l);

         for(ChunkHolder chunkholder : this.f_8325_.m_140416_()) {
            LevelChunk levelchunk = chunkholder.m_140085_();
            if (levelchunk != null) {
               list.add(new ServerChunkCache.ChunkAndHolder(levelchunk, chunkholder));
            }
         }

         profilerfiller.m_6182_("spawnAndTick");
         boolean flag2 = this.f_8329_.m_46469_().m_46207_(GameRules.f_46134_);
         Collections.shuffle(list);

         for(ServerChunkCache.ChunkAndHolder serverchunkcache$chunkandholder : list) {
            LevelChunk levelchunk1 = serverchunkcache$chunkandholder.f_184028_;
            ChunkPos chunkpos = levelchunk1.m_7697_();
            if ((this.f_8329_.m_201916_(chunkpos) && this.f_8325_.m_183879_(chunkpos)) || this.f_8327_.shouldForceTicks(chunkpos.m_45588_())) {
               levelchunk1.m_187632_(j);
               if (flag2 && (this.f_8335_ || this.f_8336_) && this.f_8329_.m_6857_().m_61927_(chunkpos)) {
                  NaturalSpawner.m_47029_(this.f_8329_, levelchunk1, naturalspawner$spawnstate, this.f_8336_, this.f_8335_, flag1);
               }

               if (this.f_8329_.m_183438_(chunkpos.m_45588_())) {
                  this.f_8329_.m_8714_(levelchunk1, k);
               }
            }
         }

         profilerfiller.m_6182_("customSpawners");
         if (flag2) {
            this.f_8329_.m_8799_(this.f_8335_, this.f_8336_);
         }

         profilerfiller.m_6182_("broadcast");
         list.forEach((p_184022_) -> {
            p_184022_.f_184029_.m_140054_(p_184022_.f_184028_);
         });
         profilerfiller.m_7238_();
         profilerfiller.m_7238_();
         this.f_8325_.m_140421_();
      }
   }

   private void m_8370_(long p_8371_, Consumer<LevelChunk> p_8372_) {
      ChunkHolder chunkholder = this.m_8364_(p_8371_);
      if (chunkholder != null) {
         chunkholder.m_140082_().getNow(ChunkHolder.f_139997_).left().ifPresent(p_8372_);
      }

   }

   public String m_6754_() {
      return Integer.toString(this.m_8482_());
   }

   @VisibleForTesting
   public int m_8480_() {
      return this.f_8332_.m_18696_();
   }

   public ChunkGenerator m_8481_() {
      return this.f_8325_.m_183719_();
   }

   public ChunkGeneratorStructureState m_255415_() {
      return this.f_8325_.m_255435_();
   }

   public RandomState m_214994_() {
      return this.f_8325_.m_214914_();
   }

   public int m_8482_() {
      return this.f_8325_.m_140394_();
   }

   public void m_8450_(BlockPos p_8451_) {
      int i = SectionPos.m_123171_(p_8451_.m_123341_());
      int j = SectionPos.m_123171_(p_8451_.m_123343_());
      ChunkHolder chunkholder = this.m_8364_(ChunkPos.m_45589_(i, j));
      if (chunkholder != null) {
         chunkholder.m_140056_(p_8451_);
      }

   }

   public void m_6506_(LightLayer p_8403_, SectionPos p_8404_) {
      this.f_8332_.execute(() -> {
         ChunkHolder chunkholder = this.m_8364_(p_8404_.m_123251_().m_45588_());
         if (chunkholder != null) {
            chunkholder.m_140036_(p_8403_, p_8404_.m_123206_());
         }

      });
   }

   public <T> void m_8387_(TicketType<T> p_8388_, ChunkPos p_8389_, int p_8390_, T p_8391_) {
      addRegionTicket(p_8388_, p_8389_, p_8390_, p_8391_, false);
   }
   public <T> void addRegionTicket(TicketType<T> p_8388_, ChunkPos p_8389_, int p_8390_, T p_8391_, boolean forceTicks) {
      this.f_8327_.addRegionTicket(p_8388_, p_8389_, p_8390_, p_8391_, forceTicks);
   }

   public <T> void m_8438_(TicketType<T> p_8439_, ChunkPos p_8440_, int p_8441_, T p_8442_) {
      removeRegionTicket(p_8439_, p_8440_, p_8441_, p_8442_, false);
   }
   public <T> void removeRegionTicket(TicketType<T> p_8439_, ChunkPos p_8440_, int p_8441_, T p_8442_, boolean forceTicks) {
      this.f_8327_.removeRegionTicket(p_8439_, p_8440_, p_8441_, p_8442_, forceTicks);
   }

   public void m_6692_(ChunkPos p_8400_, boolean p_8401_) {
      this.f_8327_.m_140799_(p_8400_, p_8401_);
   }

   public void m_8385_(ServerPlayer p_8386_) {
      if (!p_8386_.m_213877_()) {
         this.f_8325_.m_140184_(p_8386_);
      }

   }

   public void m_8443_(Entity p_8444_) {
      this.f_8325_.m_140331_(p_8444_);
   }

   public void m_8463_(Entity p_8464_) {
      this.f_8325_.m_140199_(p_8464_);
   }

   public void m_8394_(Entity p_8395_, Packet<?> p_8396_) {
      this.f_8325_.m_140333_(p_8395_, p_8396_);
   }

   public void m_8445_(Entity p_8446_, Packet<?> p_8447_) {
      this.f_8325_.m_140201_(p_8446_, p_8447_);
   }

   public void m_8354_(int p_8355_) {
      this.f_8325_.m_140167_(p_8355_);
   }

   public void m_184026_(int p_184027_) {
      this.f_8327_.m_183911_(p_184027_);
   }

   public void m_6707_(boolean p_8425_, boolean p_8426_) {
      this.f_8335_ = p_8425_;
      this.f_8336_ = p_8426_;
   }

   public String m_8448_(ChunkPos p_8449_) {
      return this.f_8325_.m_140204_(p_8449_);
   }

   public DimensionDataStorage m_8483_() {
      return this.f_8333_;
   }

   public PoiManager m_8484_() {
      return this.f_8325_.m_140424_();
   }

   public ChunkScanAccess m_196555_() {
      return this.f_8325_.m_196922_();
   }

   @Nullable
   @VisibleForDebug
   public NaturalSpawner.SpawnState m_8485_() {
      return this.f_8340_;
   }

   public void m_201915_() {
      this.f_8327_.m_201910_();
   }

   static record ChunkAndHolder(LevelChunk f_184028_, ChunkHolder f_184029_) {
   }

   final class MainThreadExecutor extends BlockableEventLoop<Runnable> {
      MainThreadExecutor(Level p_8494_) {
         super("Chunk source main thread executor for " + p_8494_.m_46472_().m_135782_());
      }

      protected Runnable m_6681_(Runnable p_8506_) {
         return p_8506_;
      }

      protected boolean m_6362_(Runnable p_8504_) {
         return true;
      }

      protected boolean m_5660_() {
         return true;
      }

      protected Thread m_6304_() {
         return ServerChunkCache.this.f_8330_;
      }

      protected void m_6367_(Runnable p_8502_) {
         ServerChunkCache.this.f_8329_.m_46473_().m_6174_("runTask");
         super.m_6367_(p_8502_);
      }

      public boolean m_7245_() {
         if (ServerChunkCache.this.m_8489_()) {
            return true;
         } else {
            ServerChunkCache.this.f_8331_.m_9409_();
            return super.m_7245_();
         }
      }
   }
}
