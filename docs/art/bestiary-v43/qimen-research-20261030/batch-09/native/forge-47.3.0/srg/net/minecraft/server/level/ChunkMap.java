package net.minecraft.server.level;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.Iterables;
import com.google.common.collect.Lists;
import com.google.common.collect.Queues;
import com.google.common.collect.Sets;
import com.google.gson.JsonElement;
import com.mojang.datafixers.DataFixer;
import com.mojang.datafixers.util.Either;
import com.mojang.logging.LogUtils;
import com.mojang.serialization.DataResult;
import com.mojang.serialization.JsonOps;
import it.unimi.dsi.fastutil.ints.Int2ObjectMap;
import it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap;
import it.unimi.dsi.fastutil.longs.Long2ByteMap;
import it.unimi.dsi.fastutil.longs.Long2ByteOpenHashMap;
import it.unimi.dsi.fastutil.longs.Long2LongMap;
import it.unimi.dsi.fastutil.longs.Long2LongOpenHashMap;
import it.unimi.dsi.fastutil.longs.Long2ObjectLinkedOpenHashMap;
import it.unimi.dsi.fastutil.longs.Long2ObjectMap;
import it.unimi.dsi.fastutil.longs.LongIterator;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import it.unimi.dsi.fastutil.longs.LongSet;
import it.unimi.dsi.fastutil.objects.ObjectIterator;
import java.io.IOException;
import java.io.Writer;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.BitSet;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Queue;
import java.util.Set;
import java.util.concurrent.CancellationException;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.Executor;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.BooleanSupplier;
import java.util.function.Consumer;
import java.util.function.IntFunction;
import java.util.function.IntSupplier;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import javax.annotation.Nullable;
import net.minecraft.CrashReport;
import net.minecraft.CrashReportCategory;
import net.minecraft.ReportedException;
import net.minecraft.Util;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.SectionPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientboundChunksBiomesPacket;
import net.minecraft.network.protocol.game.ClientboundLevelChunkWithLightPacket;
import net.minecraft.network.protocol.game.ClientboundSetChunkCacheCenterPacket;
import net.minecraft.network.protocol.game.ClientboundSetEntityLinkPacket;
import net.minecraft.network.protocol.game.ClientboundSetPassengersPacket;
import net.minecraft.network.protocol.game.DebugPackets;
import net.minecraft.server.level.progress.ChunkProgressListener;
import net.minecraft.server.network.ServerPlayerConnection;
import net.minecraft.util.CsvOutput;
import net.minecraft.util.Mth;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.util.thread.BlockableEventLoop;
import net.minecraft.util.thread.ProcessorHandle;
import net.minecraft.util.thread.ProcessorMailbox;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.village.poi.PoiManager;
import net.minecraft.world.entity.boss.EnderDragonPart;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.chunk.ChunkGeneratorStructureState;
import net.minecraft.world.level.chunk.ChunkStatus;
import net.minecraft.world.level.chunk.ImposterProtoChunk;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.LightChunkGetter;
import net.minecraft.world.level.chunk.ProtoChunk;
import net.minecraft.world.level.chunk.UpgradeData;
import net.minecraft.world.level.chunk.storage.ChunkSerializer;
import net.minecraft.world.level.chunk.storage.ChunkStorage;
import net.minecraft.world.level.entity.ChunkStatusUpdateListener;
import net.minecraft.world.level.levelgen.NoiseBasedChunkGenerator;
import net.minecraft.world.level.levelgen.NoiseGeneratorSettings;
import net.minecraft.world.level.levelgen.RandomState;
import net.minecraft.world.level.levelgen.blending.BlendingData;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplateManager;
import net.minecraft.world.level.storage.DimensionDataStorage;
import net.minecraft.world.level.storage.LevelStorageSource;
import net.minecraft.world.phys.Vec3;
import org.apache.commons.lang3.mutable.MutableBoolean;
import org.apache.commons.lang3.mutable.MutableObject;
import org.slf4j.Logger;

public class ChunkMap extends ChunkStorage implements ChunkHolder.PlayerProvider {
   private static final byte f_143034_ = -1;
   private static final byte f_143035_ = 0;
   private static final byte f_143036_ = 1;
   private static final Logger f_140128_ = LogUtils.getLogger();
   private static final int f_143037_ = 200;
   private static final int f_198789_ = 20;
   private static final int f_202982_ = 10000;
   private static final int f_143038_ = 2;
   public static final int f_143032_ = 32;
   public static final int f_143033_ = ChunkLevel.m_287154_(FullChunkStatus.ENTITY_TICKING);
   private final Long2ObjectLinkedOpenHashMap<ChunkHolder> f_140129_ = new Long2ObjectLinkedOpenHashMap<>();
   private volatile Long2ObjectLinkedOpenHashMap<ChunkHolder> f_140130_ = this.f_140129_.clone();
   private final Long2ObjectLinkedOpenHashMap<ChunkHolder> f_140131_ = new Long2ObjectLinkedOpenHashMap<>();
   private final LongSet f_140132_ = new LongOpenHashSet();
   final ServerLevel f_140133_;
   private final ThreadedLevelLightEngine f_140134_;
   private final BlockableEventLoop<Runnable> f_140135_;
   private ChunkGenerator f_140136_;
   private final RandomState f_214834_;
   private final ChunkGeneratorStructureState f_254626_;
   private final Supplier<DimensionDataStorage> f_140137_;
   private final PoiManager f_140138_;
   final LongSet f_140139_ = new LongOpenHashSet();
   private boolean f_140140_;
   private final ChunkTaskPriorityQueueSorter f_140141_;
   private final ProcessorHandle<ChunkTaskPriorityQueueSorter.Message<Runnable>> f_140142_;
   private final ProcessorHandle<ChunkTaskPriorityQueueSorter.Message<Runnable>> f_140143_;
   private final ChunkProgressListener f_140144_;
   private final ChunkStatusUpdateListener f_143031_;
   private final ChunkMap.DistanceManager f_140145_;
   private final AtomicInteger f_140146_ = new AtomicInteger();
   private final StructureTemplateManager f_214833_;
   private final String f_182284_;
   private final PlayerMap f_140149_ = new PlayerMap();
   private final Int2ObjectMap<ChunkMap.TrackedEntity> f_140150_ = new Int2ObjectOpenHashMap<>();
   private final Long2ByteMap f_140151_ = new Long2ByteOpenHashMap();
   private final Long2LongMap f_202981_ = new Long2LongOpenHashMap();
   private final Queue<Runnable> f_140125_ = Queues.newConcurrentLinkedQueue();
   int f_140126_;

   public ChunkMap(ServerLevel p_214836_, LevelStorageSource.LevelStorageAccess p_214837_, DataFixer p_214838_, StructureTemplateManager p_214839_, Executor p_214840_, BlockableEventLoop<Runnable> p_214841_, LightChunkGetter p_214842_, ChunkGenerator p_214843_, ChunkProgressListener p_214844_, ChunkStatusUpdateListener p_214845_, Supplier<DimensionDataStorage> p_214846_, int p_214847_, boolean p_214848_) {
      super(p_214837_.m_197394_(p_214836_.m_46472_()).resolve("region"), p_214838_, p_214848_);
      this.f_214833_ = p_214839_;
      Path path = p_214837_.m_197394_(p_214836_.m_46472_());
      this.f_182284_ = path.getFileName().toString();
      this.f_140133_ = p_214836_;
      this.f_140136_ = p_214843_;
      RegistryAccess registryaccess = p_214836_.m_9598_();
      long i = p_214836_.m_7328_();
      if (p_214843_ instanceof NoiseBasedChunkGenerator noisebasedchunkgenerator) {
         this.f_214834_ = RandomState.m_255302_(noisebasedchunkgenerator.m_224341_().m_203334_(), registryaccess.m_255025_(Registries.f_256865_), i);
      } else {
         this.f_214834_ = RandomState.m_255302_(NoiseGeneratorSettings.m_238396_(), registryaccess.m_255025_(Registries.f_256865_), i);
      }

      this.f_254626_ = p_214843_.m_255169_(registryaccess.m_255025_(Registries.f_256998_), this.f_214834_, i);
      this.f_140135_ = p_214841_;
      ProcessorMailbox<Runnable> processormailbox1 = ProcessorMailbox.m_18751_(p_214840_, "worldgen");
      ProcessorHandle<Runnable> processorhandle = ProcessorHandle.m_18714_("main", p_214841_::m_6937_);
      this.f_140144_ = p_214844_;
      this.f_143031_ = p_214845_;
      ProcessorMailbox<Runnable> processormailbox = ProcessorMailbox.m_18751_(p_214840_, "light");
      this.f_140141_ = new ChunkTaskPriorityQueueSorter(ImmutableList.of(processormailbox1, processorhandle, processormailbox), p_214840_, Integer.MAX_VALUE);
      this.f_140142_ = this.f_140141_.m_140604_(processormailbox1, false);
      this.f_140143_ = this.f_140141_.m_140604_(processorhandle, false);
      this.f_140134_ = new ThreadedLevelLightEngine(p_214842_, this, this.f_140133_.m_6042_().f_223549_(), processormailbox, this.f_140141_.m_140604_(processormailbox, false));
      this.f_140145_ = new ChunkMap.DistanceManager(p_214840_, p_214841_);
      this.f_140137_ = p_214846_;
      this.f_140138_ = new PoiManager(path.resolve("poi"), p_214838_, p_214848_, registryaccess, p_214836_);
      this.m_140167_(p_214847_);
   }

   protected ChunkGenerator m_183719_() {
      return this.f_140136_;
   }

   protected ChunkGeneratorStructureState m_255435_() {
      return this.f_254626_;
   }

   protected RandomState m_214914_() {
      return this.f_214834_;
   }

   public void m_183825_() {
      DataResult<JsonElement> dataresult = ChunkGenerator.f_62136_.encodeStart(JsonOps.INSTANCE, this.f_140136_);
      DataResult<ChunkGenerator> dataresult1 = dataresult.flatMap((p_183804_) -> {
         return ChunkGenerator.f_62136_.parse(JsonOps.INSTANCE, p_183804_);
      });
      dataresult1.result().ifPresent((p_183808_) -> {
         this.f_140136_ = p_183808_;
      });
   }

   private static double m_140226_(ChunkPos p_140227_, Entity p_140228_) {
      double d0 = (double)SectionPos.m_175554_(p_140227_.f_45578_, 8);
      double d1 = (double)SectionPos.m_175554_(p_140227_.f_45579_, 8);
      double d2 = d0 - p_140228_.m_20185_();
      double d3 = d1 - p_140228_.m_20189_();
      return d2 * d2 + d3 * d3;
   }

   public static boolean m_200878_(int p_200879_, int p_200880_, int p_200881_, int p_200882_, int p_200883_) {
      int i = Math.max(0, Math.abs(p_200879_ - p_200881_) - 1);
      int j = Math.max(0, Math.abs(p_200880_ - p_200882_) - 1);
      long k = (long)Math.max(0, Math.max(i, j) - 1);
      long l = (long)Math.min(i, j);
      long i1 = l * l + k * k;
      int j1 = p_200883_ * p_200883_;
      return i1 < (long)j1;
   }

   private static boolean m_183828_(int p_183829_, int p_183830_, int p_183831_, int p_183832_, int p_183833_) {
      if (!m_200878_(p_183829_, p_183830_, p_183831_, p_183832_, p_183833_)) {
         return false;
      } else {
         return !m_200878_(p_183829_ + 1, p_183830_ + 1, p_183831_, p_183832_, p_183833_) || !m_200878_(p_183829_ - 1, p_183830_ + 1, p_183831_, p_183832_, p_183833_) || !m_200878_(p_183829_ + 1, p_183830_ - 1, p_183831_, p_183832_, p_183833_) || !m_200878_(p_183829_ - 1, p_183830_ - 1, p_183831_, p_183832_, p_183833_);
      }
   }

   protected ThreadedLevelLightEngine m_140166_() {
      return this.f_140134_;
   }

   @Nullable
   protected ChunkHolder m_140174_(long p_140175_) {
      return this.f_140129_.get(p_140175_);
   }

   @Nullable
   protected ChunkHolder m_140327_(long p_140328_) {
      return this.f_140130_.get(p_140328_);
   }

   protected IntSupplier m_140371_(long p_140372_) {
      return () -> {
         ChunkHolder chunkholder = this.m_140327_(p_140372_);
         return chunkholder == null ? ChunkTaskPriorityQueue.f_140508_ - 1 : Math.min(chunkholder.m_140094_(), ChunkTaskPriorityQueue.f_140508_ - 1);
      };
   }

   public String m_140204_(ChunkPos p_140205_) {
      ChunkHolder chunkholder = this.m_140327_(p_140205_.m_45588_());
      if (chunkholder == null) {
         return "null";
      } else {
         String s = chunkholder.m_140093_() + "\n";
         ChunkStatus chunkstatus = chunkholder.m_140088_();
         ChunkAccess chunkaccess = chunkholder.m_140089_();
         if (chunkstatus != null) {
            s = s + "St: \u00a7" + chunkstatus.m_62445_() + chunkstatus + "\u00a7r\n";
         }

         if (chunkaccess != null) {
            s = s + "Ch: \u00a7" + chunkaccess.m_6415_().m_62445_() + chunkaccess.m_6415_() + "\u00a7r\n";
         }

         FullChunkStatus fullchunkstatus = chunkholder.m_287213_();
         s = s + "\u00a7" + fullchunkstatus.ordinal() + fullchunkstatus;
         return s + "\u00a7r";
      }
   }

   private CompletableFuture<Either<List<ChunkAccess>, ChunkHolder.ChunkLoadingFailure>> m_280541_(ChunkHolder p_281446_, int p_282030_, IntFunction<ChunkStatus> p_282923_) {
      if (p_282030_ == 0) {
         ChunkStatus chunkstatus1 = p_282923_.apply(0);
         return p_281446_.m_140049_(chunkstatus1, this).thenApply((p_214893_) -> {
            return p_214893_.mapLeft(List::of);
         });
      } else {
         List<CompletableFuture<Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure>>> list = new ArrayList<>();
         List<ChunkHolder> list1 = new ArrayList<>();
         ChunkPos chunkpos = p_281446_.m_140092_();
         int i = chunkpos.f_45578_;
         int j = chunkpos.f_45579_;

         for(int k = -p_282030_; k <= p_282030_; ++k) {
            for(int l = -p_282030_; l <= p_282030_; ++l) {
               int i1 = Math.max(Math.abs(l), Math.abs(k));
               final ChunkPos chunkpos1 = new ChunkPos(i + l, j + k);
               long j1 = chunkpos1.m_45588_();
               ChunkHolder chunkholder = this.m_140174_(j1);
               if (chunkholder == null) {
                  return CompletableFuture.completedFuture(Either.right(new ChunkHolder.ChunkLoadingFailure() {
                     public String toString() {
                        return "Unloaded " + chunkpos1;
                     }
                  }));
               }

               ChunkStatus chunkstatus = p_282923_.apply(i1);
               CompletableFuture<Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure>> completablefuture = chunkholder.m_140049_(chunkstatus, this);
               list1.add(chunkholder);
               list.add(completablefuture);
            }
         }

         CompletableFuture<List<Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure>>> completablefuture1 = Util.m_137567_(list);
         CompletableFuture<Either<List<ChunkAccess>, ChunkHolder.ChunkLoadingFailure>> completablefuture2 = completablefuture1.thenApply((p_183730_) -> {
            List<ChunkAccess> list2 = Lists.newArrayList();
            int k1 = 0;

            for(final Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure> either : p_183730_) {
               if (either == null) {
                  throw this.m_203751_(new IllegalStateException("At least one of the chunk futures were null"), "n/a");
               }

               Optional<ChunkAccess> optional = either.left();
               if (!optional.isPresent()) {
                  final int l1 = k1;
                  return Either.right(new ChunkHolder.ChunkLoadingFailure() {
                     public String toString() {
                        return "Unloaded " + new ChunkPos(i + l1 % (p_282030_ * 2 + 1), j + l1 / (p_282030_ * 2 + 1)) + " " + either.right().get();
                     }
                  });
               }

               list2.add(optional.get());
               ++k1;
            }

            return Either.left(list2);
         });

         for(ChunkHolder chunkholder1 : list1) {
            chunkholder1.m_200416_("getChunkRangeFuture " + chunkpos + " " + p_282030_, completablefuture2);
         }

         return completablefuture2;
      }
   }

   public ReportedException m_203751_(IllegalStateException p_203752_, String p_203753_) {
      StringBuilder stringbuilder = new StringBuilder();
      Consumer<ChunkHolder> consumer = (p_203756_) -> {
         p_203756_.m_202980_().forEach((p_203760_) -> {
            ChunkStatus chunkstatus = p_203760_.getFirst();
            CompletableFuture<Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure>> completablefuture = p_203760_.getSecond();
            if (completablefuture != null && completablefuture.isDone() && completablefuture.join() == null) {
               stringbuilder.append((Object)p_203756_.m_140092_()).append(" - status: ").append((Object)chunkstatus).append(" future: ").append((Object)completablefuture).append(System.lineSeparator());
            }

         });
      };
      stringbuilder.append("Updating:").append(System.lineSeparator());
      this.f_140129_.values().forEach(consumer);
      stringbuilder.append("Visible:").append(System.lineSeparator());
      this.f_140130_.values().forEach(consumer);
      CrashReport crashreport = CrashReport.m_127521_(p_203752_, "Chunk loading");
      CrashReportCategory crashreportcategory = crashreport.m_127514_("Chunk loading");
      crashreportcategory.m_128159_("Details", p_203753_);
      crashreportcategory.m_128159_("Futures", stringbuilder);
      return new ReportedException(crashreport);
   }

   public CompletableFuture<Either<LevelChunk, ChunkHolder.ChunkLoadingFailure>> m_280208_(ChunkHolder p_281455_) {
      return this.m_280541_(p_281455_, 2, (p_203078_) -> {
         return ChunkStatus.f_62326_;
      }).thenApplyAsync((p_212878_) -> {
         return p_212878_.mapLeft((p_203092_) -> {
            return (LevelChunk)p_203092_.get(p_203092_.size() / 2);
         });
      }, this.f_140135_);
   }

   @Nullable
   ChunkHolder m_140176_(long p_140177_, int p_140178_, @Nullable ChunkHolder p_140179_, int p_140180_) {
      if (!ChunkLevel.m_287217_(p_140180_) && !ChunkLevel.m_287217_(p_140178_)) {
         return p_140179_;
      } else {
         if (p_140179_ != null) {
            p_140179_.m_140027_(p_140178_);
         }

         if (p_140179_ != null) {
            if (!ChunkLevel.m_287217_(p_140178_)) {
               this.f_140139_.add(p_140177_);
            } else {
               this.f_140139_.remove(p_140177_);
            }
         }

         if (ChunkLevel.m_287217_(p_140178_) && p_140179_ == null) {
            p_140179_ = this.f_140131_.remove(p_140177_);
            if (p_140179_ != null) {
               p_140179_.m_140027_(p_140178_);
            } else {
               p_140179_ = new ChunkHolder(new ChunkPos(p_140177_), p_140178_, this.f_140133_, this.f_140134_, this.f_140141_, this);
            }

            this.f_140129_.put(p_140177_, p_140179_);
            this.f_140140_ = true;
         }

         net.minecraftforge.event.ForgeEventFactory.fireChunkTicketLevelUpdated(this.f_140133_, p_140177_, p_140180_, p_140178_, p_140179_);
         return p_140179_;
      }
   }

   public void close() throws IOException {
      try {
         this.f_140141_.close();
         this.f_140138_.close();
      } finally {
         super.close();
      }

   }

   protected void m_140318_(boolean p_140319_) {
      if (p_140319_) {
         List<ChunkHolder> list = this.f_140130_.values().stream().filter(ChunkHolder::m_140095_).peek(ChunkHolder::m_140096_).collect(Collectors.toList());
         MutableBoolean mutableboolean = new MutableBoolean();

         do {
            mutableboolean.setFalse();
            list.stream().map((p_203102_) -> {
               CompletableFuture<ChunkAccess> completablefuture;
               do {
                  completablefuture = p_203102_.m_140090_();
                  this.f_140135_.m_18701_(completablefuture::isDone);
               } while(completablefuture != p_203102_.m_140090_());

               return completablefuture.join();
            }).filter((p_203088_) -> {
               return p_203088_ instanceof ImposterProtoChunk || p_203088_ instanceof LevelChunk;
            }).filter(this::m_140258_).forEach((p_203051_) -> {
               mutableboolean.setTrue();
            });
         } while(mutableboolean.isTrue());

         this.m_140353_(() -> {
            return true;
         });
         this.m_63514_();
      } else {
         this.f_140130_.values().forEach(this::m_198874_);
      }

   }

   protected void m_140280_(BooleanSupplier p_140281_) {
      ProfilerFiller profilerfiller = this.f_140133_.m_46473_();
      profilerfiller.m_6180_("poi");
      this.f_140138_.m_6202_(p_140281_);
      profilerfiller.m_6182_("chunk_unload");
      if (!this.f_140133_.m_7441_()) {
         this.m_140353_(p_140281_);
      }

      profilerfiller.m_7238_();
   }

   public boolean m_201907_() {
      return this.f_140134_.m_75808_() || !this.f_140131_.isEmpty() || !this.f_140129_.isEmpty() || this.f_140138_.m_202164_() || !this.f_140139_.isEmpty() || !this.f_140125_.isEmpty() || this.f_140141_.m_201909_() || this.f_140145_.m_201911_();
   }

   private void m_140353_(BooleanSupplier p_140354_) {
      LongIterator longiterator = this.f_140139_.iterator();

      for(int i = 0; longiterator.hasNext() && (p_140354_.getAsBoolean() || i < 200 || this.f_140139_.size() > 2000); longiterator.remove()) {
         long j = longiterator.nextLong();
         ChunkHolder chunkholder = this.f_140129_.remove(j);
         if (chunkholder != null) {
            this.f_140131_.put(j, chunkholder);
            this.f_140140_ = true;
            ++i;
            this.m_140181_(j, chunkholder);
         }
      }

      int k = Math.max(0, this.f_140125_.size() - 2000);

      Runnable runnable;
      while((p_140354_.getAsBoolean() || k > 0) && (runnable = this.f_140125_.poll()) != null) {
         --k;
         runnable.run();
      }

      int l = 0;
      ObjectIterator<ChunkHolder> objectiterator = this.f_140130_.values().iterator();

      while(l < 20 && p_140354_.getAsBoolean() && objectiterator.hasNext()) {
         if (this.m_198874_(objectiterator.next())) {
            ++l;
         }
      }

   }

   private void m_140181_(long p_140182_, ChunkHolder p_140183_) {
      CompletableFuture<ChunkAccess> completablefuture = p_140183_.m_140090_();
      completablefuture.thenAcceptAsync((p_203002_) -> {
         CompletableFuture<ChunkAccess> completablefuture1 = p_140183_.m_140090_();
         if (completablefuture1 != completablefuture) {
            this.m_140181_(p_140182_, p_140183_);
         } else {
            if (this.f_140131_.remove(p_140182_, p_140183_) && p_203002_ != null) {
               if (p_203002_ instanceof LevelChunk) {
                  ((LevelChunk)p_203002_).m_62913_(false);
                  net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.level.ChunkEvent.Unload(p_203002_));
               }

               this.m_140258_(p_203002_);
               if (this.f_140132_.remove(p_140182_) && p_203002_ instanceof LevelChunk) {
                  LevelChunk levelchunk = (LevelChunk)p_203002_;
                  this.f_140133_.m_8712_(levelchunk);
               }

               this.f_140134_.m_9330_(p_203002_.m_7697_());
               this.f_140134_.m_9409_();
               this.f_140144_.m_5511_(p_203002_.m_7697_(), (ChunkStatus)null);
               this.f_202981_.remove(p_203002_.m_7697_().m_45588_());
            }

         }
      }, this.f_140125_::add).whenComplete((p_202996_, p_202997_) -> {
         if (p_202997_ != null) {
            f_140128_.error("Failed to save chunk {}", p_140183_.m_140092_(), p_202997_);
         }

      });
   }

   protected boolean m_140324_() {
      if (!this.f_140140_) {
         return false;
      } else {
         this.f_140130_ = this.f_140129_.clone();
         this.f_140140_ = false;
         return true;
      }
   }

   public CompletableFuture<Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure>> m_140292_(ChunkHolder p_140293_, ChunkStatus p_140294_) {
      ChunkPos chunkpos = p_140293_.m_140092_();
      if (p_140294_ == ChunkStatus.f_62314_) {
         return this.m_140417_(chunkpos);
      } else {
         if (p_140294_ == ChunkStatus.f_62323_) {
            this.f_140145_.m_140792_(TicketType.f_9446_, chunkpos, ChunkLevel.m_287141_(ChunkStatus.f_62323_), chunkpos);
         }

         if (!p_140294_.m_280148_()) {
            Optional<ChunkAccess> optional = p_140293_.m_140049_(p_140294_.m_62482_(), this).getNow(ChunkHolder.f_139995_).left();
            if (optional.isPresent() && optional.get().m_6415_().m_62427_(p_140294_)) {
               CompletableFuture<Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure>> completablefuture = p_140294_.m_223244_(this.f_140133_, this.f_214833_, this.f_140134_, (p_203081_) -> {
                  return this.m_140383_(p_140293_);
               }, optional.get());
               this.f_140144_.m_5511_(chunkpos, p_140294_);
               return completablefuture;
            }
         }

         return this.m_140360_(p_140293_, p_140294_);
      }
   }

   private CompletableFuture<Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure>> m_140417_(ChunkPos p_140418_) {
      return this.m_214963_(p_140418_).thenApply((p_214925_) -> {
         return p_214925_.filter((p_214928_) -> {
            boolean flag = m_214940_(p_214928_);
            if (!flag) {
               f_140128_.error("Chunk file at {} is missing level data, skipping", (Object)p_140418_);
            }

            return flag;
         });
      }).<Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure>>thenApplyAsync((p_269770_) -> {
         this.f_140133_.m_46473_().m_6174_("chunkLoad");
         if (p_269770_.isPresent()) {
            ChunkAccess chunkaccess = ChunkSerializer.m_188230_(this.f_140133_, this.f_140138_, p_140418_, p_269770_.get());
            this.m_140229_(p_140418_, chunkaccess.m_6415_().m_62494_());
            return Either.left(chunkaccess);
         } else {
            return Either.left(this.m_214961_(p_140418_));
         }
      }, this.f_140135_).exceptionallyAsync((p_214888_) -> {
         return this.m_214901_(p_214888_, p_140418_);
      }, this.f_140135_);
   }

   private static boolean m_214940_(CompoundTag p_214941_) {
      return p_214941_.m_128425_("Status", 8);
   }

   private Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure> m_214901_(Throwable p_214902_, ChunkPos p_214903_) {
      if (p_214902_ instanceof ReportedException reportedexception) {
         Throwable throwable = reportedexception.getCause();
         if (!(throwable instanceof IOException)) {
            this.m_140422_(p_214903_);
            throw reportedexception;
         }

         f_140128_.error("Couldn't load chunk {}", p_214903_, throwable);
      } else if (p_214902_ instanceof IOException) {
         f_140128_.error("Couldn't load chunk {}", p_214903_, p_214902_);
      }

      return Either.left(this.m_214961_(p_214903_));
   }

   private ChunkAccess m_214961_(ChunkPos p_214962_) {
      this.m_140422_(p_214962_);
      return new ProtoChunk(p_214962_, UpgradeData.f_63320_, this.f_140133_, this.f_140133_.m_9598_().m_175515_(Registries.f_256952_), (BlendingData)null);
   }

   private void m_140422_(ChunkPos p_140423_) {
      this.f_140151_.put(p_140423_.m_45588_(), (byte)-1);
   }

   private byte m_140229_(ChunkPos p_140230_, ChunkStatus.ChunkType p_140231_) {
      return this.f_140151_.put(p_140230_.m_45588_(), (byte)(p_140231_ == ChunkStatus.ChunkType.PROTOCHUNK ? -1 : 1));
   }

   private CompletableFuture<Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure>> m_140360_(ChunkHolder p_140361_, ChunkStatus p_140362_) {
      ChunkPos chunkpos = p_140361_.m_140092_();
      CompletableFuture<Either<List<ChunkAccess>, ChunkHolder.ChunkLoadingFailure>> completablefuture = this.m_280541_(p_140361_, p_140362_.m_62488_(), (p_214935_) -> {
         return this.m_140262_(p_140362_, p_214935_);
      });
      this.f_140133_.m_46473_().m_6525_(() -> {
         return "chunkGenerate " + p_140362_;
      });
      Executor executor = (p_214958_) -> {
         this.f_140142_.m_6937_(ChunkTaskPriorityQueueSorter.m_140642_(p_140361_, p_214958_));
      };
      return completablefuture.thenComposeAsync((p_214873_) -> {
         return p_214873_.map((p_280971_) -> {
            try {
               ChunkAccess chunkaccess = p_280971_.get(p_280971_.size() / 2);
               CompletableFuture<Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure>> completablefuture1;
               if (chunkaccess.m_6415_().m_62427_(p_140362_)) {
                  completablefuture1 = p_140362_.m_223244_(this.f_140133_, this.f_214833_, this.f_140134_, (p_214919_) -> {
                     return this.m_140383_(p_140361_);
                  }, chunkaccess);
               } else {
                  completablefuture1 = p_140362_.m_280308_(executor, this.f_140133_, this.f_140136_, this.f_214833_, this.f_140134_, (p_280966_) -> {
                     return this.m_140383_(p_140361_);
                  }, p_280971_);
               }

               this.f_140144_.m_5511_(chunkpos, p_140362_);
               return completablefuture1;
            } catch (Exception exception) {
               exception.getStackTrace();
               CrashReport crashreport = CrashReport.m_127521_(exception, "Exception generating new chunk");
               CrashReportCategory crashreportcategory = crashreport.m_127514_("Chunk to be generated");
               crashreportcategory.m_128159_("Location", String.format(Locale.ROOT, "%d,%d", chunkpos.f_45578_, chunkpos.f_45579_));
               crashreportcategory.m_128159_("Position hash", ChunkPos.m_45589_(chunkpos.f_45578_, chunkpos.f_45579_));
               crashreportcategory.m_128159_("Generator", this.f_140136_);
               this.f_140135_.execute(() -> {
                  throw new ReportedException(crashreport);
               });
               throw new ReportedException(crashreport);
            }
         }, (p_214867_) -> {
            this.m_140375_(chunkpos);
            return CompletableFuture.completedFuture(Either.right(p_214867_));
         });
      }, executor);
   }

   protected void m_140375_(ChunkPos p_140376_) {
      this.f_140135_.m_6937_(Util.m_137474_(() -> {
         this.f_140145_.m_140823_(TicketType.f_9446_, p_140376_, ChunkLevel.m_287141_(ChunkStatus.f_62323_), p_140376_);
      }, () -> {
         return "release light ticket " + p_140376_;
      }));
   }

   private ChunkStatus m_140262_(ChunkStatus p_140263_, int p_140264_) {
      ChunkStatus chunkstatus;
      if (p_140264_ == 0) {
         chunkstatus = p_140263_.m_62482_();
      } else {
         chunkstatus = ChunkStatus.m_156185_(ChunkStatus.m_62370_(p_140263_) + p_140264_);
      }

      return chunkstatus;
   }

   private static void m_143064_(ServerLevel p_143065_, List<CompoundTag> p_143066_) {
      if (!p_143066_.isEmpty()) {
         p_143065_.m_143327_(EntityType.m_147045_(p_143066_, p_143065_));
      }

   }

   private CompletableFuture<Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure>> m_140383_(ChunkHolder p_140384_) {
      CompletableFuture<Either<ChunkAccess, ChunkHolder.ChunkLoadingFailure>> completablefuture = p_140384_.m_140047_(ChunkStatus.f_62326_.m_62482_());
      return completablefuture.thenApplyAsync((p_287363_) -> {
         ChunkStatus chunkstatus = ChunkLevel.m_287158_(p_140384_.m_140093_());
         return !chunkstatus.m_62427_(ChunkStatus.f_62326_) ? ChunkHolder.f_139995_ : p_287363_.mapLeft((p_214856_) -> {
            ChunkPos chunkpos = p_140384_.m_140092_();
            ProtoChunk protochunk = (ProtoChunk)p_214856_;
            LevelChunk levelchunk;
            if (protochunk instanceof ImposterProtoChunk) {
               levelchunk = ((ImposterProtoChunk)protochunk).m_62768_();
            } else {
               levelchunk = new LevelChunk(this.f_140133_, protochunk, (p_214900_) -> {
                  m_143064_(this.f_140133_, protochunk.m_63293_());
               });
               p_140384_.m_140052_(new ImposterProtoChunk(levelchunk, false));
            }

            levelchunk.m_62879_(() -> {
               return ChunkLevel.m_287264_(p_140384_.m_140093_());
            });
            levelchunk.m_62952_();
            if (this.f_140132_.add(chunkpos.m_45588_())) {
               levelchunk.m_62913_(true);
               try {
               p_140384_.currentlyLoading = levelchunk; // Forge - bypass the future chain when getChunk is called, this prevents deadlocks.
               levelchunk.m_156369_();
               levelchunk.m_187958_(this.f_140133_);
               net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.level.ChunkEvent.Load(levelchunk, !(protochunk instanceof ImposterProtoChunk)));
               } finally {
                   p_140384_.currentlyLoading = null; // Forge - Stop bypassing the future chain.
               }
            }

            return levelchunk;
         });
      }, (p_214951_) -> {
         this.f_140143_.m_6937_(ChunkTaskPriorityQueueSorter.m_140624_(p_214951_, p_140384_.m_140092_().m_45588_(), p_140384_::m_140093_));
      });
   }

   public CompletableFuture<Either<LevelChunk, ChunkHolder.ChunkLoadingFailure>> m_143053_(ChunkHolder p_143054_) {
      CompletableFuture<Either<List<ChunkAccess>, ChunkHolder.ChunkLoadingFailure>> completablefuture = this.m_280541_(p_143054_, 1, (p_214916_) -> {
         return ChunkStatus.f_62326_;
      });
      CompletableFuture<Either<LevelChunk, ChunkHolder.ChunkLoadingFailure>> completablefuture1 = completablefuture.thenApplyAsync((p_280964_) -> {
         return p_280964_.mapLeft((p_214939_) -> {
            return (LevelChunk)p_214939_.get(p_214939_.size() / 2);
         });
      }, (p_214944_) -> {
         this.f_140143_.m_6937_(ChunkTaskPriorityQueueSorter.m_140642_(p_143054_, p_214944_));
      }).thenApplyAsync((p_214930_) -> {
         return p_214930_.ifLeft((p_214960_) -> {
            p_214960_.m_62812_();
            this.f_140133_.m_184102_(p_214960_);
         });
      }, this.f_140135_);
      completablefuture1.handle((p_287364_, p_287365_) -> {
         this.f_140146_.getAndIncrement();
         return null;
      });
      completablefuture1.thenAcceptAsync((p_214882_) -> {
         p_214882_.ifLeft((p_287368_) -> {
            MutableObject<ClientboundLevelChunkWithLightPacket> mutableobject = new MutableObject<>();
            this.m_183262_(p_143054_.m_140092_(), false).forEach((p_214911_) -> {
               this.m_183760_(p_214911_, mutableobject, p_287368_);
            });
         });
      }, (p_214922_) -> {
         this.f_140143_.m_6937_(ChunkTaskPriorityQueueSorter.m_140642_(p_143054_, p_214922_));
      });
      return completablefuture1;
   }

   public CompletableFuture<Either<LevelChunk, ChunkHolder.ChunkLoadingFailure>> m_143109_(ChunkHolder p_143110_) {
      return this.m_280541_(p_143110_, 1, ChunkStatus::m_156185_).thenApplyAsync((p_203086_) -> {
         return p_203086_.mapLeft((p_214905_) -> {
            return (LevelChunk)p_214905_.get(p_214905_.size() / 2);
         });
      }, (p_214859_) -> {
         this.f_140143_.m_6937_(ChunkTaskPriorityQueueSorter.m_140642_(p_143110_, p_214859_));
      });
   }

   public int m_140368_() {
      return this.f_140146_.get();
   }

   private boolean m_198874_(ChunkHolder p_198875_) {
      if (!p_198875_.m_140095_()) {
         return false;
      } else {
         ChunkAccess chunkaccess = p_198875_.m_140090_().getNow((ChunkAccess)null);
         if (!(chunkaccess instanceof ImposterProtoChunk) && !(chunkaccess instanceof LevelChunk)) {
            return false;
         } else {
            long i = chunkaccess.m_7697_().m_45588_();
            long j = this.f_202981_.getOrDefault(i, -1L);
            long k = System.currentTimeMillis();
            if (k < j) {
               return false;
            } else {
               boolean flag = this.m_140258_(chunkaccess);
               p_198875_.m_140096_();
               if (flag) {
                  this.f_202981_.put(i, k + 10000L);
               }

               return flag;
            }
         }
      }
   }

   private boolean m_140258_(ChunkAccess p_140259_) {
      this.f_140138_.m_63796_(p_140259_.m_7697_());
      if (!p_140259_.m_6344_()) {
         return false;
      } else {
         p_140259_.m_8092_(false);
         ChunkPos chunkpos = p_140259_.m_7697_();

         try {
            ChunkStatus chunkstatus = p_140259_.m_6415_();
            if (chunkstatus.m_62494_() != ChunkStatus.ChunkType.LEVELCHUNK) {
               if (this.m_140425_(chunkpos)) {
                  return false;
               }

               if (chunkstatus == ChunkStatus.f_62314_ && p_140259_.m_6633_().values().stream().noneMatch(StructureStart::m_73603_)) {
                  return false;
               }
            }

            this.f_140133_.m_46473_().m_6174_("chunkSave");
            CompoundTag compoundtag = ChunkSerializer.m_63454_(this.f_140133_, p_140259_);
            net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.level.ChunkDataEvent.Save(p_140259_, p_140259_.getWorldForge() != null ? p_140259_.getWorldForge() : this.f_140133_, compoundtag));
            this.m_63502_(chunkpos, compoundtag);
            this.m_140229_(chunkpos, chunkstatus.m_62494_());
            return true;
         } catch (Exception exception) {
            f_140128_.error("Failed to save chunk {},{}", chunkpos.f_45578_, chunkpos.f_45579_, exception);
            return false;
         }
      }
   }

   private boolean m_140425_(ChunkPos p_140426_) {
      byte b0 = this.f_140151_.get(p_140426_.m_45588_());
      if (b0 != 0) {
         return b0 == 1;
      } else {
         CompoundTag compoundtag;
         try {
            compoundtag = this.m_214963_(p_140426_).join().orElse((CompoundTag)null);
            if (compoundtag == null) {
               this.m_140422_(p_140426_);
               return false;
            }
         } catch (Exception exception) {
            f_140128_.error("Failed to read chunk {}", p_140426_, exception);
            this.m_140422_(p_140426_);
            return false;
         }

         ChunkStatus.ChunkType chunkstatus$chunktype = ChunkSerializer.m_63485_(compoundtag);
         return this.m_140229_(p_140426_, chunkstatus$chunktype) == 1;
      }
   }

   protected void m_140167_(int p_140168_) {
      int i = Mth.m_14045_(p_140168_, 2, 32);
      if (i != this.f_140126_) {
         int j = this.f_140126_;
         this.f_140126_ = i;
         this.f_140145_.m_140777_(this.f_140126_);

         for(ChunkHolder chunkholder : this.f_140129_.values()) {
            ChunkPos chunkpos = chunkholder.m_140092_();
            MutableObject<ClientboundLevelChunkWithLightPacket> mutableobject = new MutableObject<>();
            this.m_183262_(chunkpos, false).forEach((p_214864_) -> {
               SectionPos sectionpos = p_214864_.m_8965_();
               boolean flag = m_200878_(chunkpos.f_45578_, chunkpos.f_45579_, sectionpos.m_123170_(), sectionpos.m_123222_(), j);
               boolean flag1 = m_200878_(chunkpos.f_45578_, chunkpos.f_45579_, sectionpos.m_123170_(), sectionpos.m_123222_(), this.f_140126_);
               this.m_183754_(p_214864_, chunkpos, mutableobject, flag, flag1);
            });
         }
      }

   }

   protected void m_183754_(ServerPlayer p_183755_, ChunkPos p_183756_, MutableObject<ClientboundLevelChunkWithLightPacket> p_183757_, boolean p_183758_, boolean p_183759_) {
      if (p_183755_.m_9236_() == this.f_140133_) {
         if (p_183759_ && !p_183758_) {
            ChunkHolder chunkholder = this.m_140327_(p_183756_.m_45588_());
            if (chunkholder != null) {
               LevelChunk levelchunk = chunkholder.m_140085_();
               if (levelchunk != null) {
                  this.m_183760_(p_183755_, p_183757_, levelchunk);
               }

               DebugPackets.m_133676_(this.f_140133_, p_183756_);
            }
         }

         if (!p_183759_ && p_183758_) {
            p_183755_.m_9088_(p_183756_);
            net.minecraftforge.event.ForgeEventFactory.fireChunkUnWatch(p_183755_, p_183756_, this.f_140133_);
         }

      }
   }

   public int m_140394_() {
      return this.f_140130_.size();
   }

   public net.minecraft.server.level.DistanceManager m_143145_() {
      return this.f_140145_;
   }

   protected Iterable<ChunkHolder> m_140416_() {
      return Iterables.unmodifiableIterable(this.f_140130_.values());
   }

   void m_140274_(Writer p_140275_) throws IOException {
      CsvOutput csvoutput = CsvOutput.m_13619_().m_13630_("x").m_13630_("z").m_13630_("level").m_13630_("in_memory").m_13630_("status").m_13630_("full_status").m_13630_("accessible_ready").m_13630_("ticking_ready").m_13630_("entity_ticking_ready").m_13630_("ticket").m_13630_("spawning").m_13630_("block_entity_count").m_13630_("ticking_ticket").m_13630_("ticking_level").m_13630_("block_ticks").m_13630_("fluid_ticks").m_13628_(p_140275_);
      TickingTracker tickingtracker = this.f_140145_.m_183915_();

      for(Long2ObjectMap.Entry<ChunkHolder> entry : this.f_140130_.long2ObjectEntrySet()) {
         long i = entry.getLongKey();
         ChunkPos chunkpos = new ChunkPos(i);
         ChunkHolder chunkholder = entry.getValue();
         Optional<ChunkAccess> optional = Optional.ofNullable(chunkholder.m_140089_());
         Optional<LevelChunk> optional1 = optional.flatMap((p_214932_) -> {
            return p_214932_ instanceof LevelChunk ? Optional.of((LevelChunk)p_214932_) : Optional.empty();
         });
         csvoutput.m_13624_(chunkpos.f_45578_, chunkpos.f_45579_, chunkholder.m_140093_(), optional.isPresent(), optional.map(ChunkAccess::m_6415_).orElse((ChunkStatus)null), optional1.map(LevelChunk::m_287138_).orElse((FullChunkStatus)null), m_140278_(chunkholder.m_140082_()), m_140278_(chunkholder.m_140026_()), m_140278_(chunkholder.m_140073_()), this.f_140145_.m_140838_(i), this.m_183879_(chunkpos), optional1.map((p_214953_) -> {
            return p_214953_.m_62954_().size();
         }).orElse(0), tickingtracker.m_184175_(i), tickingtracker.m_6172_(i), optional1.map((p_214946_) -> {
            return p_214946_.m_183531_().m_183574_();
         }).orElse(0), optional1.map((p_214937_) -> {
            return p_214937_.m_183526_().m_183574_();
         }).orElse(0));
      }

   }

   private static String m_140278_(CompletableFuture<Either<LevelChunk, ChunkHolder.ChunkLoadingFailure>> p_140279_) {
      try {
         Either<LevelChunk, ChunkHolder.ChunkLoadingFailure> either = p_140279_.getNow((Either<LevelChunk, ChunkHolder.ChunkLoadingFailure>)null);
         return either != null ? either.map((p_214897_) -> {
            return "done";
         }, (p_214850_) -> {
            return "unloaded";
         }) : "not completed";
      } catch (CompletionException completionexception) {
         return "failed " + completionexception.getCause().getMessage();
      } catch (CancellationException cancellationexception) {
         return "cancelled";
      }
   }

   private CompletableFuture<Optional<CompoundTag>> m_214963_(ChunkPos p_214964_) {
      return this.m_223454_(p_214964_).thenApplyAsync((p_214907_) -> {
         return p_214907_.map(this::m_214947_);
      }, Util.m_183991_());
   }

   private CompoundTag m_214947_(CompoundTag p_214948_) {
      return this.m_188288_(this.f_140133_.m_46472_(), this.f_140137_, p_214948_, this.f_140136_.m_187743_());
   }

   boolean m_183879_(ChunkPos p_183880_) {
      long i = p_183880_.m_45588_();
      if (!this.f_140145_.m_140847_(i)) {
         return false;
      } else {
         for(ServerPlayer serverplayer : this.f_140149_.m_183926_(i)) {
            if (this.m_183751_(serverplayer, p_183880_)) {
               return true;
            }
         }

         return false;
      }
   }

   public List<ServerPlayer> m_183888_(ChunkPos p_183889_) {
      long i = p_183889_.m_45588_();
      if (!this.f_140145_.m_140847_(i)) {
         return List.of();
      } else {
         ImmutableList.Builder<ServerPlayer> builder = ImmutableList.builder();

         for(ServerPlayer serverplayer : this.f_140149_.m_183926_(i)) {
            if (this.m_183751_(serverplayer, p_183889_)) {
               builder.add(serverplayer);
            }
         }

         return builder.build();
      }
   }

   private boolean m_183751_(ServerPlayer p_183752_, ChunkPos p_183753_) {
      if (p_183752_.m_5833_()) {
         return false;
      } else {
         double d0 = m_140226_(p_183753_, p_183752_);
         return d0 < 16384.0D;
      }
   }

   private boolean m_140329_(ServerPlayer p_140330_) {
      return p_140330_.m_5833_() && !this.f_140133_.m_46469_().m_46207_(GameRules.f_46146_);
   }

   void m_140192_(ServerPlayer p_140193_, boolean p_140194_) {
      boolean flag = this.m_140329_(p_140193_);
      boolean flag1 = this.f_140149_.m_8260_(p_140193_);
      int i = SectionPos.m_123171_(p_140193_.m_146903_());
      int j = SectionPos.m_123171_(p_140193_.m_146907_());
      if (p_140194_) {
         this.f_140149_.m_8252_(ChunkPos.m_45589_(i, j), p_140193_, flag);
         this.m_140373_(p_140193_);
         if (!flag) {
            this.f_140145_.m_140802_(SectionPos.m_235861_(p_140193_), p_140193_);
         }
      } else {
         SectionPos sectionpos = p_140193_.m_8965_();
         this.f_140149_.m_8249_(sectionpos.m_123251_().m_45588_(), p_140193_);
         if (!flag1) {
            this.f_140145_.m_140828_(sectionpos, p_140193_);
         }
      }

      for(int l = i - this.f_140126_ - 1; l <= i + this.f_140126_ + 1; ++l) {
         for(int k = j - this.f_140126_ - 1; k <= j + this.f_140126_ + 1; ++k) {
            if (m_200878_(l, k, i, j, this.f_140126_)) {
               ChunkPos chunkpos = new ChunkPos(l, k);
               this.m_183754_(p_140193_, chunkpos, new MutableObject<>(), !p_140194_, p_140194_);
            }
         }
      }

   }

   private SectionPos m_140373_(ServerPlayer p_140374_) {
      SectionPos sectionpos = SectionPos.m_235861_(p_140374_);
      p_140374_.m_9119_(sectionpos);
      p_140374_.f_8906_.m_9829_(new ClientboundSetChunkCacheCenterPacket(sectionpos.m_123170_(), sectionpos.m_123222_()));
      return sectionpos;
   }

   public void m_140184_(ServerPlayer p_140185_) {
      for(ChunkMap.TrackedEntity chunkmap$trackedentity : this.f_140150_.values()) {
         if (chunkmap$trackedentity.f_140472_ == p_140185_) {
            chunkmap$trackedentity.m_140487_(this.f_140133_.m_6907_());
         } else {
            chunkmap$trackedentity.m_140497_(p_140185_);
         }
      }

      int j2 = SectionPos.m_123171_(p_140185_.m_146903_());
      int k2 = SectionPos.m_123171_(p_140185_.m_146907_());
      SectionPos sectionpos = p_140185_.m_8965_();
      SectionPos sectionpos1 = SectionPos.m_235861_(p_140185_);
      long i = sectionpos.m_123251_().m_45588_();
      long j = sectionpos1.m_123251_().m_45588_();
      boolean flag = this.f_140149_.m_8262_(p_140185_);
      boolean flag1 = this.m_140329_(p_140185_);
      boolean flag2 = sectionpos.m_123252_() != sectionpos1.m_123252_();
      if (flag2 || flag != flag1) {
         this.m_140373_(p_140185_);
         if (!flag) {
            this.f_140145_.m_140828_(sectionpos, p_140185_);
         }

         if (!flag1) {
            this.f_140145_.m_140802_(sectionpos1, p_140185_);
         }

         if (!flag && flag1) {
            this.f_140149_.m_8256_(p_140185_);
         }

         if (flag && !flag1) {
            this.f_140149_.m_8258_(p_140185_);
         }

         if (i != j) {
            this.f_140149_.m_8245_(i, j, p_140185_);
         }
      }

      int k = sectionpos.m_123170_();
      int l = sectionpos.m_123222_();
      int i1 = this.f_140126_ + 1;
      if (Math.abs(k - j2) <= i1 * 2 && Math.abs(l - k2) <= i1 * 2) {
         int i3 = Math.min(j2, k) - i1;
         int k3 = Math.min(k2, l) - i1;
         int l3 = Math.max(j2, k) + i1;
         int i4 = Math.max(k2, l) + i1;

         for(int l1 = i3; l1 <= l3; ++l1) {
            for(int i2 = k3; i2 <= i4; ++i2) {
               boolean flag5 = m_200878_(l1, i2, k, l, this.f_140126_);
               boolean flag6 = m_200878_(l1, i2, j2, k2, this.f_140126_);
               this.m_183754_(p_140185_, new ChunkPos(l1, i2), new MutableObject<>(), flag5, flag6);
            }
         }
      } else {
         for(int j1 = k - i1; j1 <= k + i1; ++j1) {
            for(int k1 = l - i1; k1 <= l + i1; ++k1) {
               if (m_200878_(j1, k1, k, l, this.f_140126_)) {
                  boolean flag3 = true;
                  boolean flag4 = false;
                  this.m_183754_(p_140185_, new ChunkPos(j1, k1), new MutableObject<>(), true, false);
               }
            }
         }

         for(int l2 = j2 - i1; l2 <= j2 + i1; ++l2) {
            for(int j3 = k2 - i1; j3 <= k2 + i1; ++j3) {
               if (m_200878_(l2, j3, j2, k2, this.f_140126_)) {
                  boolean flag7 = false;
                  boolean flag8 = true;
                  this.m_183754_(p_140185_, new ChunkPos(l2, j3), new MutableObject<>(), false, true);
               }
            }
         }
      }

   }

   public List<ServerPlayer> m_183262_(ChunkPos p_183801_, boolean p_183802_) {
      Set<ServerPlayer> set = this.f_140149_.m_183926_(p_183801_.m_45588_());
      ImmutableList.Builder<ServerPlayer> builder = ImmutableList.builder();

      for(ServerPlayer serverplayer : set) {
         SectionPos sectionpos = serverplayer.m_8965_();
         if (p_183802_ && m_183828_(p_183801_.f_45578_, p_183801_.f_45579_, sectionpos.m_123170_(), sectionpos.m_123222_(), this.f_140126_) || !p_183802_ && m_200878_(p_183801_.f_45578_, p_183801_.f_45579_, sectionpos.m_123170_(), sectionpos.m_123222_(), this.f_140126_)) {
            builder.add(serverplayer);
         }
      }

      return builder.build();
   }

   protected void m_140199_(Entity p_140200_) {
      if (!(p_140200_ instanceof net.minecraftforge.entity.PartEntity)) {
         EntityType<?> entitytype = p_140200_.m_6095_();
         int i = entitytype.m_20681_() * 16;
         if (i != 0) {
            int j = entitytype.m_20682_();
            if (this.f_140150_.containsKey(p_140200_.m_19879_())) {
               throw (IllegalStateException)Util.m_137570_(new IllegalStateException("Entity is already tracked!"));
            } else {
               ChunkMap.TrackedEntity chunkmap$trackedentity = new ChunkMap.TrackedEntity(p_140200_, i, j, entitytype.m_20683_());
               this.f_140150_.put(p_140200_.m_19879_(), chunkmap$trackedentity);
               chunkmap$trackedentity.m_140487_(this.f_140133_.m_6907_());
               if (p_140200_ instanceof ServerPlayer) {
                  ServerPlayer serverplayer = (ServerPlayer)p_140200_;
                  this.m_140192_(serverplayer, true);

                  for(ChunkMap.TrackedEntity chunkmap$trackedentity1 : this.f_140150_.values()) {
                     if (chunkmap$trackedentity1.f_140472_ != serverplayer) {
                        chunkmap$trackedentity1.m_140497_(serverplayer);
                     }
                  }
               }

            }
         }
      }
   }

   protected void m_140331_(Entity p_140332_) {
      if (p_140332_ instanceof ServerPlayer serverplayer) {
         this.m_140192_(serverplayer, false);

         for(ChunkMap.TrackedEntity chunkmap$trackedentity : this.f_140150_.values()) {
            chunkmap$trackedentity.m_140485_(serverplayer);
         }
      }

      ChunkMap.TrackedEntity chunkmap$trackedentity1 = this.f_140150_.remove(p_140332_.m_19879_());
      if (chunkmap$trackedentity1 != null) {
         chunkmap$trackedentity1.m_140482_();
      }

   }

   protected void m_140421_() {
      List<ServerPlayer> list = Lists.newArrayList();
      List<ServerPlayer> list1 = this.f_140133_.m_6907_();

      for(ChunkMap.TrackedEntity chunkmap$trackedentity : this.f_140150_.values()) {
         SectionPos sectionpos = chunkmap$trackedentity.f_140474_;
         SectionPos sectionpos1 = SectionPos.m_235861_(chunkmap$trackedentity.f_140472_);
         boolean flag = !Objects.equals(sectionpos, sectionpos1);
         if (flag) {
            chunkmap$trackedentity.m_140487_(list1);
            Entity entity = chunkmap$trackedentity.f_140472_;
            if (entity instanceof ServerPlayer) {
               list.add((ServerPlayer)entity);
            }

            chunkmap$trackedentity.f_140474_ = sectionpos1;
         }

         if (flag || this.f_140145_.m_183913_(sectionpos1.m_123251_().m_45588_())) {
            chunkmap$trackedentity.f_140471_.m_8533_();
         }
      }

      if (!list.isEmpty()) {
         for(ChunkMap.TrackedEntity chunkmap$trackedentity1 : this.f_140150_.values()) {
            chunkmap$trackedentity1.m_140487_(list);
         }
      }

   }

   public void m_140201_(Entity p_140202_, Packet<?> p_140203_) {
      ChunkMap.TrackedEntity chunkmap$trackedentity = this.f_140150_.get(p_140202_.m_19879_());
      if (chunkmap$trackedentity != null) {
         chunkmap$trackedentity.m_140489_(p_140203_);
      }

   }

   protected void m_140333_(Entity p_140334_, Packet<?> p_140335_) {
      ChunkMap.TrackedEntity chunkmap$trackedentity = this.f_140150_.get(p_140334_.m_19879_());
      if (chunkmap$trackedentity != null) {
         chunkmap$trackedentity.m_140499_(p_140335_);
      }

   }

   public void m_274524_(List<ChunkAccess> p_275577_) {
      Map<ServerPlayer, List<LevelChunk>> map = new HashMap<>();

      for(ChunkAccess chunkaccess : p_275577_) {
         ChunkPos chunkpos = chunkaccess.m_7697_();
         LevelChunk levelchunk;
         if (chunkaccess instanceof LevelChunk levelchunk1) {
            levelchunk = levelchunk1;
         } else {
            levelchunk = this.f_140133_.m_6325_(chunkpos.f_45578_, chunkpos.f_45579_);
         }

         for(ServerPlayer serverplayer : this.m_183262_(chunkpos, false)) {
            map.computeIfAbsent(serverplayer, (p_274834_) -> {
               return new ArrayList();
            }).add(levelchunk);
         }
      }

      map.forEach((p_274835_, p_274836_) -> {
         p_274835_.f_8906_.m_9829_(ClientboundChunksBiomesPacket.m_274415_(p_274836_));
      });
   }

   private void m_183760_(ServerPlayer p_183761_, MutableObject<ClientboundLevelChunkWithLightPacket> p_183762_, LevelChunk p_183763_) {
      if (p_183762_.getValue() == null) {
         p_183762_.setValue(new ClientboundLevelChunkWithLightPacket(p_183763_, this.f_140134_, (BitSet)null, (BitSet)null));
      }

      p_183761_.m_184135_(p_183763_.m_7697_(), p_183762_.getValue());
      DebugPackets.m_133676_(this.f_140133_, p_183763_.m_7697_());
      List<Entity> list = Lists.newArrayList();
      List<Entity> list1 = Lists.newArrayList();

      for(ChunkMap.TrackedEntity chunkmap$trackedentity : this.f_140150_.values()) {
         Entity entity = chunkmap$trackedentity.f_140472_;
         if (entity != p_183761_ && entity.m_146902_().equals(p_183763_.m_7697_())) {
            chunkmap$trackedentity.m_140497_(p_183761_);
            if (entity instanceof Mob && ((Mob)entity).m_21524_() != null) {
               list.add(entity);
            }

            if (!entity.m_20197_().isEmpty()) {
               list1.add(entity);
            }
         }
      }

      if (!list.isEmpty()) {
         for(Entity entity1 : list) {
            p_183761_.f_8906_.m_9829_(new ClientboundSetEntityLinkPacket(entity1, ((Mob)entity1).m_21524_()));
         }
      }

      if (!list1.isEmpty()) {
         for(Entity entity2 : list1) {
            p_183761_.f_8906_.m_9829_(new ClientboundSetPassengersPacket(entity2));
         }
      }

      net.minecraftforge.event.ForgeEventFactory.fireChunkWatch(p_183761_, p_183763_, this.f_140133_);
   }

   protected PoiManager m_140424_() {
      return this.f_140138_;
   }

   public String m_182285_() {
      return this.f_182284_;
   }

   void m_287285_(ChunkPos p_287612_, FullChunkStatus p_287685_) {
      this.f_143031_.m_156794_(p_287612_, p_287685_);
   }

   class DistanceManager extends net.minecraft.server.level.DistanceManager {
      protected DistanceManager(Executor p_140459_, Executor p_140460_) {
         super(p_140459_, p_140460_);
      }

      protected boolean m_7009_(long p_140462_) {
         return ChunkMap.this.f_140139_.contains(p_140462_);
      }

      @Nullable
      protected ChunkHolder m_7316_(long p_140469_) {
         return ChunkMap.this.m_140174_(p_140469_);
      }

      @Nullable
      protected ChunkHolder m_7288_(long p_140464_, int p_140465_, @Nullable ChunkHolder p_140466_, int p_140467_) {
         return ChunkMap.this.m_140176_(p_140464_, p_140465_, p_140466_, p_140467_);
      }
   }

   class TrackedEntity {
      final ServerEntity f_140471_;
      final Entity f_140472_;
      private final int f_140473_;
      SectionPos f_140474_;
      private final Set<ServerPlayerConnection> f_140475_ = Sets.newIdentityHashSet();

      public TrackedEntity(Entity p_140478_, int p_140479_, int p_140480_, boolean p_140481_) {
         this.f_140471_ = new ServerEntity(ChunkMap.this.f_140133_, p_140478_, p_140480_, p_140481_, this::m_140489_);
         this.f_140472_ = p_140478_;
         this.f_140473_ = p_140479_;
         this.f_140474_ = SectionPos.m_235861_(p_140478_);
      }

      public boolean equals(Object p_140506_) {
         if (p_140506_ instanceof ChunkMap.TrackedEntity) {
            return ((ChunkMap.TrackedEntity)p_140506_).f_140472_.m_19879_() == this.f_140472_.m_19879_();
         } else {
            return false;
         }
      }

      public int hashCode() {
         return this.f_140472_.m_19879_();
      }

      public void m_140489_(Packet<?> p_140490_) {
         for(ServerPlayerConnection serverplayerconnection : this.f_140475_) {
            serverplayerconnection.m_9829_(p_140490_);
         }

      }

      public void m_140499_(Packet<?> p_140500_) {
         this.m_140489_(p_140500_);
         if (this.f_140472_ instanceof ServerPlayer) {
            ((ServerPlayer)this.f_140472_).f_8906_.m_9829_(p_140500_);
         }

      }

      public void m_140482_() {
         for(ServerPlayerConnection serverplayerconnection : this.f_140475_) {
            this.f_140471_.m_8534_(serverplayerconnection.m_142253_());
         }

      }

      public void m_140485_(ServerPlayer p_140486_) {
         if (this.f_140475_.remove(p_140486_.f_8906_)) {
            this.f_140471_.m_8534_(p_140486_);
         }

      }

      public void m_140497_(ServerPlayer p_140498_) {
         if (p_140498_ != this.f_140472_) {
            Vec3 vec3 = p_140498_.m_20182_().m_82546_(this.f_140472_.m_20182_());
            double d0 = (double)Math.min(this.m_140496_(), ChunkMap.this.f_140126_ * 16);
            double d1 = vec3.f_82479_ * vec3.f_82479_ + vec3.f_82481_ * vec3.f_82481_;
            double d2 = d0 * d0;
            boolean flag = d1 <= d2 && this.f_140472_.m_6459_(p_140498_);
            if (flag) {
               if (this.f_140475_.add(p_140498_.f_8906_)) {
                  this.f_140471_.m_8541_(p_140498_);
               }
            } else if (this.f_140475_.remove(p_140498_.f_8906_)) {
               this.f_140471_.m_8534_(p_140498_);
            }

         }
      }

      private int m_140483_(int p_140484_) {
         return ChunkMap.this.f_140133_.m_7654_().m_7186_(p_140484_);
      }

      private int m_140496_() {
         int i = this.f_140473_;

         for(Entity entity : this.f_140472_.m_146897_()) {
            int j = entity.m_6095_().m_20681_() * 16;
            if (j > i) {
               i = j;
            }
         }

         return this.m_140483_(i);
      }

      public void m_140487_(List<ServerPlayer> p_140488_) {
         for(ServerPlayer serverplayer : p_140488_) {
            this.m_140497_(serverplayer);
         }

      }
   }
}
