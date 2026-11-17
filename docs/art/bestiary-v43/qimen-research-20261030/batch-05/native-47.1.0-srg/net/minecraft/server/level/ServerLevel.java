package net.minecraft.server.level;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import com.mojang.datafixers.DataFixer;
import com.mojang.datafixers.util.Pair;
import com.mojang.logging.LogUtils;
import it.unimi.dsi.fastutil.ints.Int2ObjectMap;
import it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap;
import it.unimi.dsi.fastutil.longs.LongSet;
import it.unimi.dsi.fastutil.longs.LongSets;
import it.unimi.dsi.fastutil.objects.Object2IntMap;
import it.unimi.dsi.fastutil.objects.Object2IntOpenHashMap;
import it.unimi.dsi.fastutil.objects.ObjectArrayList;
import it.unimi.dsi.fastutil.objects.ObjectLinkedOpenHashSet;
import it.unimi.dsi.fastutil.objects.ObjectOpenHashSet;
import java.io.IOException;
import java.io.Writer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Executor;
import java.util.function.BooleanSupplier;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import net.minecraft.CrashReport;
import net.minecraft.Util;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.core.SectionPos;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientboundBlockDestructionPacket;
import net.minecraft.network.protocol.game.ClientboundBlockEventPacket;
import net.minecraft.network.protocol.game.ClientboundDamageEventPacket;
import net.minecraft.network.protocol.game.ClientboundEntityEventPacket;
import net.minecraft.network.protocol.game.ClientboundExplodePacket;
import net.minecraft.network.protocol.game.ClientboundGameEventPacket;
import net.minecraft.network.protocol.game.ClientboundLevelEventPacket;
import net.minecraft.network.protocol.game.ClientboundLevelParticlesPacket;
import net.minecraft.network.protocol.game.ClientboundSetDefaultSpawnPositionPacket;
import net.minecraft.network.protocol.game.ClientboundSoundEntityPacket;
import net.minecraft.network.protocol.game.ClientboundSoundPacket;
import net.minecraft.network.protocol.game.DebugPackets;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.ServerScoreboard;
import net.minecraft.server.level.progress.ChunkProgressListener;
import net.minecraft.server.players.SleepStatus;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.util.AbortableIterationConsumer;
import net.minecraft.util.CsvOutput;
import net.minecraft.util.Mth;
import net.minecraft.util.ProgressListener;
import net.minecraft.util.RandomSource;
import net.minecraft.util.Unit;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.util.valueproviders.IntProvider;
import net.minecraft.util.valueproviders.UniformInt;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.RandomSequences;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.ReputationEventHandler;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.ai.village.ReputationEventType;
import net.minecraft.world.entity.ai.village.poi.PoiManager;
import net.minecraft.world.entity.ai.village.poi.PoiType;
import net.minecraft.world.entity.ai.village.poi.PoiTypes;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.animal.WaterAnimal;
import net.minecraft.world.entity.animal.horse.SkeletonHorse;
import net.minecraft.world.entity.boss.EnderDragonPart;
import net.minecraft.world.entity.boss.enderdragon.EnderDragon;
import net.minecraft.world.entity.npc.Npc;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.raid.Raid;
import net.minecraft.world.entity.raid.Raids;
import net.minecraft.world.flag.FeatureFlagSet;
import net.minecraft.world.item.crafting.RecipeManager;
import net.minecraft.world.level.BlockEventData;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.CustomSpawner;
import net.minecraft.world.level.Explosion;
import net.minecraft.world.level.ExplosionDamageCalculator;
import net.minecraft.world.level.ForcedChunksSavedData;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.NaturalSpawner;
import net.minecraft.world.level.StructureManager;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.SnowLayerBlock;
import net.minecraft.world.level.block.entity.TickingBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.chunk.LevelChunkSection;
import net.minecraft.world.level.chunk.storage.EntityStorage;
import net.minecraft.world.level.dimension.BuiltinDimensionTypes;
import net.minecraft.world.level.dimension.LevelStem;
import net.minecraft.world.level.dimension.end.EndDragonFight;
import net.minecraft.world.level.entity.EntityPersistentStorage;
import net.minecraft.world.level.entity.EntityTickList;
import net.minecraft.world.level.entity.EntityTypeTest;
import net.minecraft.world.level.entity.LevelCallback;
import net.minecraft.world.level.entity.LevelEntityGetter;
import net.minecraft.world.level.entity.PersistentEntitySectionManager;
import net.minecraft.world.level.gameevent.DynamicGameEventListener;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraft.world.level.gameevent.GameEventDispatcher;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructureCheck;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplateManager;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.level.portal.PortalForcer;
import net.minecraft.world.level.saveddata.maps.MapIndex;
import net.minecraft.world.level.saveddata.maps.MapItemSavedData;
import net.minecraft.world.level.storage.DimensionDataStorage;
import net.minecraft.world.level.storage.LevelStorageSource;
import net.minecraft.world.level.storage.ServerLevelData;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.BooleanOp;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.minecraft.world.ticks.LevelTicks;
import org.slf4j.Logger;

public class ServerLevel extends Level implements WorldGenLevel {
   public static final BlockPos f_8562_ = new BlockPos(100, 50, 0);
   public static final IntProvider f_263704_ = UniformInt.m_146622_(12000, 180000);
   public static final IntProvider f_263681_ = UniformInt.m_146622_(12000, 24000);
   private static final IntProvider f_263684_ = UniformInt.m_146622_(12000, 180000);
   public static final IntProvider f_263755_ = UniformInt.m_146622_(3600, 15600);
   private static final Logger f_8566_ = LogUtils.getLogger();
   private static final int f_143242_ = 300;
   private static final int f_184046_ = 65536;
   final List<ServerPlayer> f_8546_ = Lists.newArrayList();
   private final ServerChunkCache f_8547_;
   private final MinecraftServer f_8548_;
   private final ServerLevelData f_8549_;
   final EntityTickList f_143243_ = new EntityTickList();
   private final PersistentEntitySectionManager<Entity> f_143244_;
   private final GameEventDispatcher f_243695_;
   public boolean f_8564_;
   private final SleepStatus f_143245_;
   private int f_8551_;
   private final PortalForcer f_8552_;
   private final LevelTicks<Block> f_8553_ = new LevelTicks<>(this::m_184110_, this.m_46658_());
   private final LevelTicks<Fluid> f_184047_ = new LevelTicks<>(this::m_184110_, this.m_46658_());
   final Set<Mob> f_143246_ = new ObjectOpenHashSet<>();
   volatile boolean f_200893_;
   protected final Raids f_8565_;
   private final ObjectLinkedOpenHashSet<BlockEventData> f_8556_ = new ObjectLinkedOpenHashSet<>();
   private final List<BlockEventData> f_184048_ = new ArrayList<>(64);
   private boolean f_8557_;
   private final List<CustomSpawner> f_8558_;
   @Nullable
   private EndDragonFight f_8559_;
   final Int2ObjectMap<net.minecraftforge.entity.PartEntity<?>> f_143247_ = new Int2ObjectOpenHashMap<>();
   private final StructureManager f_214997_;
   private final StructureCheck f_196556_;
   private final boolean f_8561_;
   private final RandomSequences f_286969_;
   private net.minecraftforge.common.util.LevelCapabilityData capabilityData;

   public ServerLevel(MinecraftServer p_214999_, Executor p_215000_, LevelStorageSource.LevelStorageAccess p_215001_, ServerLevelData p_215002_, ResourceKey<Level> p_215003_, LevelStem p_215004_, ChunkProgressListener p_215005_, boolean p_215006_, long p_215007_, List<CustomSpawner> p_215008_, boolean p_215009_, @Nullable RandomSequences p_288977_) {
      super(p_215002_, p_215003_, p_214999_.m_206579_(), p_215004_.f_63975_(), p_214999_::m_129905_, false, p_215006_, p_215007_, p_214999_.m_213994_());
      this.f_8561_ = p_215009_;
      this.f_8548_ = p_214999_;
      this.f_8558_ = p_215008_;
      this.f_8549_ = p_215002_;
      ChunkGenerator chunkgenerator = p_215004_.f_63976_();
      boolean flag = p_214999_.m_6365_();
      DataFixer datafixer = p_214999_.m_129933_();
      EntityPersistentStorage<Entity> entitypersistentstorage = new EntityStorage(this, p_215001_.m_197394_(p_215003_).resolve("entities"), datafixer, flag, p_214999_);
      this.f_143244_ = new PersistentEntitySectionManager<>(Entity.class, new ServerLevel.EntityCallbacks(), entitypersistentstorage);
      this.f_8547_ = new ServerChunkCache(this, p_215001_, datafixer, p_214999_.m_236738_(), p_215000_, chunkgenerator, p_214999_.m_6846_().m_11312_(), p_214999_.m_6846_().m_184213_(), flag, p_215005_, this.f_143244_::m_287207_, () -> {
         return p_214999_.m_129783_().m_8895_();
      });
      this.f_8547_.m_255415_().m_254958_();
      this.f_8552_ = new PortalForcer(this);
      this.m_46465_();
      this.m_46466_();
      this.m_6857_().m_61923_(p_214999_.m_6329_());
      this.f_8565_ = this.m_8895_().m_164861_((p_184095_) -> {
         return Raids.m_150235_(this, p_184095_);
      }, () -> {
         return new Raids(this);
      }, Raids.m_211596_(this.m_204156_()));
      if (!p_214999_.m_129792_()) {
         p_215002_.m_5458_(p_214999_.m_130008_());
      }

      long i = p_214999_.m_129910_().m_246337_().m_245499_();
      this.f_196556_ = new StructureCheck(this.f_8547_.m_196555_(), this.m_9598_(), p_214999_.m_236738_(), p_215003_, chunkgenerator, this.f_8547_.m_214994_(), this, chunkgenerator.m_62218_(), i, datafixer);
      this.f_214997_ = new StructureManager(this, p_214999_.m_129910_().m_246337_(), this.f_196556_);
      if (this.m_46472_() == Level.f_46430_ && this.m_204156_().m_203565_(BuiltinDimensionTypes.f_223540_)) {
         this.f_8559_ = new EndDragonFight(this, i, p_214999_.m_129910_().m_6564_());
      } else {
         this.f_8559_ = null;
      }

      this.f_143245_ = new SleepStatus();
      this.f_243695_ = new GameEventDispatcher(this);
      this.f_286969_ = Objects.requireNonNullElseGet(p_288977_, () -> {
         return this.m_8895_().m_164861_((p_287374_) -> {
            return RandomSequences.m_287187_(i, p_287374_);
         }, () -> {
            return new RandomSequences(i);
         }, "random_sequences");
      });
      this.initCapabilities();
   }

   /** @deprecated */
   @Deprecated
   @VisibleForTesting
   public void m_287200_(@Nullable EndDragonFight p_287779_) {
      this.f_8559_ = p_287779_;
   }

   public void m_8606_(int p_8607_, int p_8608_, boolean p_8609_, boolean p_8610_) {
      this.f_8549_.m_6393_(p_8607_);
      this.f_8549_.m_6399_(p_8608_);
      this.f_8549_.m_6398_(p_8608_);
      this.f_8549_.m_5565_(p_8609_);
      this.f_8549_.m_5557_(p_8610_);
   }

   public Holder<Biome> m_203675_(int p_203775_, int p_203776_, int p_203777_) {
      return this.m_7726_().m_8481_().m_62218_().m_203407_(p_203775_, p_203776_, p_203777_, this.m_7726_().m_214994_().m_224579_());
   }

   public StructureManager m_215010_() {
      return this.f_214997_;
   }

   public void m_8793_(BooleanSupplier p_8794_) {
      ProfilerFiller profilerfiller = this.m_46473_();
      this.f_8557_ = true;
      profilerfiller.m_6180_("world border");
      this.m_6857_().m_61969_();
      profilerfiller.m_6182_("weather");
      this.m_184096_();
      int i = this.m_46469_().m_46215_(GameRules.f_151486_);
      if (this.f_143245_.m_144002_(i) && this.f_143245_.m_144004_(i, this.f_8546_)) {
         if (this.m_46469_().m_46207_(GameRules.f_46140_)) {
            long j = this.m_46468_() + 24000L;
            this.m_8615_(net.minecraftforge.event.ForgeEventFactory.onSleepFinished(this, j - j % 24000L, this.m_46468_()));
         }

         this.m_8804_();
         if (this.m_46469_().m_46207_(GameRules.f_46150_) && this.m_46471_()) {
            this.m_184097_();
         }
      }

      this.m_46465_();
      this.m_8809_();
      profilerfiller.m_6182_("tickPending");
      if (!this.m_46659_()) {
         long k = this.m_46467_();
         profilerfiller.m_6180_("blockTicks");
         this.f_8553_.m_193225_(k, 65536, this::m_184112_);
         profilerfiller.m_6182_("fluidTicks");
         this.f_184047_.m_193225_(k, 65536, this::m_184076_);
         profilerfiller.m_7238_();
      }

      profilerfiller.m_6182_("raid");
      this.f_8565_.m_37957_();
      profilerfiller.m_6182_("chunkSource");
      this.m_7726_().m_201698_(p_8794_, true);
      profilerfiller.m_6182_("blockEvents");
      this.m_8807_();
      this.f_8557_ = false;
      profilerfiller.m_7238_();
      boolean flag = !this.f_8546_.isEmpty() || net.minecraftforge.common.world.ForgeChunkManager.hasForcedChunks(this); //Forge: Replace vanilla's has forced chunk check with forge's that checks both the vanilla and forge added ones
      if (flag) {
         this.m_8886_();
      }

      if (flag || this.f_8551_++ < 300) {
         profilerfiller.m_6180_("entities");
         if (this.f_8559_ != null) {
            profilerfiller.m_6180_("dragonFight");
            this.f_8559_.m_64095_();
            profilerfiller.m_7238_();
         }

         this.f_143243_.m_156910_((p_184065_) -> {
            if (!p_184065_.m_213877_()) {
               if (this.m_143342_(p_184065_)) {
                  p_184065_.m_146870_();
               } else {
                  profilerfiller.m_6180_("checkDespawn");
                  p_184065_.m_6043_();
                  profilerfiller.m_7238_();
                  if (this.f_8547_.f_8325_.m_143145_().m_183913_(p_184065_.m_146902_().m_45588_())) {
                     Entity entity = p_184065_.m_20202_();
                     if (entity != null) {
                        if (!entity.m_213877_() && entity.m_20363_(p_184065_)) {
                           return;
                        }

                        p_184065_.m_8127_();
                     }

                     profilerfiller.m_6180_("tick");
                     if (!p_184065_.m_213877_() && !(p_184065_ instanceof net.minecraftforge.entity.PartEntity)) {
                        this.m_46653_(this::m_8647_, p_184065_);
                     }
                     profilerfiller.m_7238_();
                  }
               }
            }
         });
         profilerfiller.m_7238_();
         this.m_46463_();
      }

      profilerfiller.m_6180_("entityManagement");
      this.f_143244_.m_157506_();
      profilerfiller.m_7238_();
   }

   public boolean m_183438_(long p_184059_) {
      return this.f_8547_.f_8325_.m_143145_().m_183916_(p_184059_);
   }

   protected void m_8809_() {
      if (this.f_8561_) {
         long i = this.f_46442_.m_6793_() + 1L;
         this.f_8549_.m_6253_(i);
         this.f_8549_.m_7540_().m_82256_(this.f_8548_, i);
         if (this.f_46442_.m_5470_().m_46207_(GameRules.f_46140_)) {
            this.m_8615_(this.f_46442_.m_6792_() + 1L);
         }

      }
   }

   public void m_8615_(long p_8616_) {
      this.f_8549_.m_6247_(p_8616_);
   }

   public void m_8799_(boolean p_8800_, boolean p_8801_) {
      for(CustomSpawner customspawner : this.f_8558_) {
         customspawner.m_7995_(this, p_8800_, p_8801_);
      }

   }

   private boolean m_143342_(Entity p_143343_) {
      if (this.f_8548_.m_6998_() || !(p_143343_ instanceof Animal) && !(p_143343_ instanceof WaterAnimal)) {
         return !this.f_8548_.m_6997_() && p_143343_ instanceof Npc;
      } else {
         return true;
      }
   }

   private void m_8804_() {
      this.f_143245_.m_144001_();
      this.f_8546_.stream().filter(LivingEntity::m_5803_).collect(Collectors.toList()).forEach((p_184116_) -> {
         p_184116_.m_6145_(false, false);
      });
   }

   public void m_8714_(LevelChunk p_8715_, int p_8716_) {
      ChunkPos chunkpos = p_8715_.m_7697_();
      boolean flag = this.m_46471_();
      int i = chunkpos.m_45604_();
      int j = chunkpos.m_45605_();
      ProfilerFiller profilerfiller = this.m_46473_();
      profilerfiller.m_6180_("thunder");
      if (flag && this.m_46470_() && this.f_46441_.m_188503_(100000) == 0) {
         BlockPos blockpos = this.m_143288_(this.m_46496_(i, 0, j, 15));
         if (this.m_46758_(blockpos)) {
            DifficultyInstance difficultyinstance = this.m_6436_(blockpos);
            boolean flag1 = this.m_46469_().m_46207_(GameRules.f_46134_) && this.f_46441_.m_188500_() < (double)difficultyinstance.m_19056_() * 0.01D && !this.m_8055_(blockpos.m_7495_()).m_60713_(Blocks.f_152587_);
            if (flag1) {
               SkeletonHorse skeletonhorse = EntityType.f_20525_.m_20615_(this);
               if (skeletonhorse != null) {
                  skeletonhorse.m_30923_(true);
                  skeletonhorse.m_146762_(0);
                  skeletonhorse.m_6034_((double)blockpos.m_123341_(), (double)blockpos.m_123342_(), (double)blockpos.m_123343_());
                  this.m_7967_(skeletonhorse);
               }
            }

            LightningBolt lightningbolt = EntityType.f_20465_.m_20615_(this);
            if (lightningbolt != null) {
               lightningbolt.m_20219_(Vec3.m_82539_(blockpos));
               lightningbolt.m_20874_(flag1);
               this.m_7967_(lightningbolt);
            }
         }
      }

      profilerfiller.m_6182_("iceandsnow");
      if (this.f_46441_.m_188503_(16) == 0) {
         BlockPos blockpos1 = this.m_5452_(Heightmap.Types.MOTION_BLOCKING, this.m_46496_(i, 0, j, 15));
         BlockPos blockpos2 = blockpos1.m_7495_();
         Biome biome = this.m_204166_(blockpos1).m_203334_();
         if (this.isAreaLoaded(blockpos2, 1)) // Forge: check area to avoid loading neighbors in unloaded chunks
         if (biome.m_47477_(this, blockpos2)) {
            this.m_46597_(blockpos2, Blocks.f_50126_.m_49966_());
         }

         if (flag) {
            int i1 = this.m_46469_().m_46215_(GameRules.f_254637_);
            if (i1 > 0 && biome.m_47519_(this, blockpos1)) {
               BlockState blockstate = this.m_8055_(blockpos1);
               if (blockstate.m_60713_(Blocks.f_50125_)) {
                  int k = blockstate.m_61143_(SnowLayerBlock.f_56581_);
                  if (k < Math.min(i1, 8)) {
                     BlockState blockstate1 = blockstate.m_61124_(SnowLayerBlock.f_56581_, Integer.valueOf(k + 1));
                     Block.m_49897_(blockstate, blockstate1, this, blockpos1);
                     this.m_46597_(blockpos1, blockstate1);
                  }
               } else {
                  this.m_46597_(blockpos1, Blocks.f_50125_.m_49966_());
               }
            }

            Biome.Precipitation biome$precipitation = biome.m_264600_(blockpos2);
            if (biome$precipitation != Biome.Precipitation.NONE) {
               BlockState blockstate3 = this.m_8055_(blockpos2);
               blockstate3.m_60734_().m_141997_(blockstate3, this, blockpos2, biome$precipitation);
            }
         }
      }

      profilerfiller.m_6182_("tickBlocks");
      if (p_8716_ > 0) {
         LevelChunkSection[] alevelchunksection = p_8715_.m_7103_();

         for(int l = 0; l < alevelchunksection.length; ++l) {
            LevelChunkSection levelchunksection = alevelchunksection[l];
            if (levelchunksection.m_63014_()) {
               int j1 = p_8715_.m_151568_(l);
               int k1 = SectionPos.m_123223_(j1);

               for(int l1 = 0; l1 < p_8716_; ++l1) {
                  BlockPos blockpos3 = this.m_46496_(i, k1, j, 15);
                  profilerfiller.m_6180_("randomTick");
                  BlockState blockstate2 = levelchunksection.m_62982_(blockpos3.m_123341_() - i, blockpos3.m_123342_() - k1, blockpos3.m_123343_() - j);
                  if (blockstate2.m_60823_()) {
                     blockstate2.m_222972_(this, blockpos3, this.f_46441_);
                  }

                  FluidState fluidstate = blockstate2.m_60819_();
                  if (fluidstate.m_76187_()) {
                     fluidstate.m_230562_(this, blockpos3, this.f_46441_);
                  }

                  profilerfiller.m_7238_();
               }
            }
         }
      }

      profilerfiller.m_7238_();
   }

   private Optional<BlockPos> m_143248_(BlockPos p_143249_) {
      Optional<BlockPos> optional = this.m_8904_().m_148658_((p_215059_) -> {
         return p_215059_.m_203565_(PoiTypes.f_218066_);
      }, (p_184055_) -> {
         return p_184055_.m_123342_() == this.m_6924_(Heightmap.Types.WORLD_SURFACE, p_184055_.m_123341_(), p_184055_.m_123343_()) - 1;
      }, p_143249_, 128, PoiManager.Occupancy.ANY);
      return optional.map((p_184053_) -> {
         return p_184053_.m_6630_(1);
      });
   }

   protected BlockPos m_143288_(BlockPos p_143289_) {
      BlockPos blockpos = this.m_5452_(Heightmap.Types.MOTION_BLOCKING, p_143289_);
      Optional<BlockPos> optional = this.m_143248_(blockpos);
      if (optional.isPresent()) {
         return optional.get();
      } else {
         AABB aabb = (new AABB(blockpos, new BlockPos(blockpos.m_123341_(), this.m_151558_(), blockpos.m_123343_()))).m_82400_(3.0D);
         List<LivingEntity> list = this.m_6443_(LivingEntity.class, aabb, (p_289308_) -> {
            return p_289308_ != null && p_289308_.m_6084_() && this.m_45527_(p_289308_.m_20183_());
         });
         if (!list.isEmpty()) {
            return list.get(this.f_46441_.m_188503_(list.size())).m_20183_();
         } else {
            if (blockpos.m_123342_() == this.m_141937_() - 1) {
               blockpos = blockpos.m_6630_(2);
            }

            return blockpos;
         }
      }
   }

   public boolean m_8874_() {
      return this.f_8557_;
   }

   public boolean m_143333_() {
      return this.m_46469_().m_46215_(GameRules.f_151486_) <= 100;
   }

   private void m_143315_() {
      if (this.m_143333_()) {
         if (!this.m_7654_().m_129792_() || this.m_7654_().m_6992_()) {
            int i = this.m_46469_().m_46215_(GameRules.f_151486_);
            Component component;
            if (this.f_143245_.m_144002_(i)) {
               component = Component.m_237115_("sleep.skipping_night");
            } else {
               component = Component.m_237110_("sleep.players_sleeping", this.f_143245_.m_144009_(), this.f_143245_.m_144010_(i));
            }

            for(ServerPlayer serverplayer : this.f_8546_) {
               serverplayer.m_5661_(component, true);
            }

         }
      }
   }

   public void m_8878_() {
      if (!this.f_8546_.isEmpty() && this.f_143245_.m_144007_(this.f_8546_)) {
         this.m_143315_();
      }

   }

   public ServerScoreboard m_6188_() {
      return this.f_8548_.m_129896_();
   }

   private void m_184096_() {
      boolean flag = this.m_46471_();
      if (this.m_6042_().f_223549_()) {
         if (this.m_46469_().m_46207_(GameRules.f_46150_)) {
            int i = this.f_8549_.m_6537_();
            int j = this.f_8549_.m_6558_();
            int k = this.f_8549_.m_6531_();
            boolean flag1 = this.f_46442_.m_6534_();
            boolean flag2 = this.f_46442_.m_6533_();
            if (i > 0) {
               --i;
               j = flag1 ? 0 : 1;
               k = flag2 ? 0 : 1;
               flag1 = false;
               flag2 = false;
            } else {
               if (j > 0) {
                  --j;
                  if (j == 0) {
                     flag1 = !flag1;
                  }
               } else if (flag1) {
                  j = f_263755_.m_214085_(this.f_46441_);
               } else {
                  j = f_263684_.m_214085_(this.f_46441_);
               }

               if (k > 0) {
                  --k;
                  if (k == 0) {
                     flag2 = !flag2;
                  }
               } else if (flag2) {
                  k = f_263681_.m_214085_(this.f_46441_);
               } else {
                  k = f_263704_.m_214085_(this.f_46441_);
               }
            }

            this.f_8549_.m_6398_(j);
            this.f_8549_.m_6399_(k);
            this.f_8549_.m_6393_(i);
            this.f_8549_.m_5557_(flag1);
            this.f_8549_.m_5565_(flag2);
         }

         this.f_46439_ = this.f_46440_;
         if (this.f_46442_.m_6534_()) {
            this.f_46440_ += 0.01F;
         } else {
            this.f_46440_ -= 0.01F;
         }

         this.f_46440_ = Mth.m_14036_(this.f_46440_, 0.0F, 1.0F);
         this.f_46437_ = this.f_46438_;
         if (this.f_46442_.m_6533_()) {
            this.f_46438_ += 0.01F;
         } else {
            this.f_46438_ -= 0.01F;
         }

         this.f_46438_ = Mth.m_14036_(this.f_46438_, 0.0F, 1.0F);
      }

      if (this.f_46437_ != this.f_46438_) {
         this.f_8548_.m_6846_().m_11270_(new ClientboundGameEventPacket(ClientboundGameEventPacket.f_132160_, this.f_46438_), this.m_46472_());
      }

      if (this.f_46439_ != this.f_46440_) {
         this.f_8548_.m_6846_().m_11270_(new ClientboundGameEventPacket(ClientboundGameEventPacket.f_132161_, this.f_46440_), this.m_46472_());
      }

      /* The function in use here has been replaced in order to only send the weather info to players in the correct dimension,
       * rather than to all players on the server. This is what causes the client-side rain, as the
       * client believes that it has started raining locally, rather than in another dimension.
       */
      if (flag != this.m_46471_()) {
         if (flag) {
            this.f_8548_.m_6846_().m_11270_(new ClientboundGameEventPacket(ClientboundGameEventPacket.f_132155_, 0.0F), this.m_46472_());
         } else {
            this.f_8548_.m_6846_().m_11270_(new ClientboundGameEventPacket(ClientboundGameEventPacket.f_132154_, 0.0F), this.m_46472_());
         }

         this.f_8548_.m_6846_().m_11270_(new ClientboundGameEventPacket(ClientboundGameEventPacket.f_132160_, this.f_46438_), this.m_46472_());
         this.f_8548_.m_6846_().m_11270_(new ClientboundGameEventPacket(ClientboundGameEventPacket.f_132161_, this.f_46440_), this.m_46472_());
      }

   }

   private void m_184097_() {
      this.f_8549_.m_6399_(0);
      this.f_8549_.m_5565_(false);
      this.f_8549_.m_6398_(0);
      this.f_8549_.m_5557_(false);
   }

   public void m_8886_() {
      this.f_8551_ = 0;
   }

   private void m_184076_(BlockPos p_184077_, Fluid p_184078_) {
      FluidState fluidstate = this.m_6425_(p_184077_);
      if (fluidstate.m_192917_(p_184078_)) {
         fluidstate.m_76163_(this, p_184077_);
      }

   }

   private void m_184112_(BlockPos p_184113_, Block p_184114_) {
      BlockState blockstate = this.m_8055_(p_184113_);
      if (blockstate.m_60713_(p_184114_)) {
         blockstate.m_222963_(this, p_184113_, this.f_46441_);
      }

   }

   public void m_8647_(Entity p_8648_) {
      p_8648_.m_146867_();
      ProfilerFiller profilerfiller = this.m_46473_();
      ++p_8648_.f_19797_;
      this.m_46473_().m_6521_(() -> {
         return BuiltInRegistries.f_256780_.m_7981_(p_8648_.m_6095_()).toString();
      });
      profilerfiller.m_6174_("tickNonPassenger");
      p_8648_.m_8119_();
      this.m_46473_().m_7238_();

      for(Entity entity : p_8648_.m_20197_()) {
         this.m_8662_(p_8648_, entity);
      }

   }

   private void m_8662_(Entity p_8663_, Entity p_8664_) {
      if (!p_8664_.m_213877_() && p_8664_.m_20202_() == p_8663_) {
         if (p_8664_ instanceof Player || this.f_143243_.m_156914_(p_8664_)) {
            p_8664_.m_146867_();
            ++p_8664_.f_19797_;
            ProfilerFiller profilerfiller = this.m_46473_();
            profilerfiller.m_6521_(() -> {
               return BuiltInRegistries.f_256780_.m_7981_(p_8664_.m_6095_()).toString();
            });
            profilerfiller.m_6174_("tickPassenger");
            if (p_8664_.canUpdate())
            p_8664_.m_6083_();
            profilerfiller.m_7238_();

            for(Entity entity : p_8664_.m_20197_()) {
               this.m_8662_(p_8664_, entity);
            }

         }
      } else {
         p_8664_.m_8127_();
      }
   }

   public boolean m_7966_(Player p_8696_, BlockPos p_8697_) {
      return !this.f_8548_.m_7762_(this, p_8697_, p_8696_) && this.m_6857_().m_61937_(p_8697_);
   }

   public void m_8643_(@Nullable ProgressListener p_8644_, boolean p_8645_, boolean p_8646_) {
      ServerChunkCache serverchunkcache = this.m_7726_();
      if (!p_8646_) {
         if (p_8644_ != null) {
            p_8644_.m_6309_(Component.m_237115_("menu.savingLevel"));
         }

         this.m_8806_();
         if (p_8644_ != null) {
            p_8644_.m_6307_(Component.m_237115_("menu.savingChunks"));
         }

         serverchunkcache.m_8419_(p_8645_);
         if (p_8645_) {
            this.f_143244_.m_157561_();
         } else {
            this.f_143244_.m_157554_();
         }

         net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.level.LevelEvent.Save(this));
      }
   }

   private void m_8806_() {
      if (this.f_8559_ != null) {
         this.f_8548_.m_129910_().m_5915_(this.f_8559_.m_289745_());
      }

      this.m_7726_().m_8483_().m_78151_();
   }

   public <T extends Entity> List<? extends T> m_143280_(EntityTypeTest<Entity, T> p_143281_, Predicate<? super T> p_143282_) {
      List<T> list = Lists.newArrayList();
      this.m_260813_(p_143281_, p_143282_, list);
      return list;
   }

   public <T extends Entity> void m_260813_(EntityTypeTest<Entity, T> p_262152_, Predicate<? super T> p_261808_, List<? super T> p_261583_) {
      this.m_261178_(p_262152_, p_261808_, p_261583_, Integer.MAX_VALUE);
   }

   public <T extends Entity> void m_261178_(EntityTypeTest<Entity, T> p_261842_, Predicate<? super T> p_262091_, List<? super T> p_261703_, int p_261907_) {
      this.m_142646_().m_142690_(p_261842_, (p_261428_) -> {
         if (p_262091_.test(p_261428_)) {
            p_261703_.add(p_261428_);
            if (p_261703_.size() >= p_261907_) {
               return AbortableIterationConsumer.Continuation.ABORT;
            }
         }

         return AbortableIterationConsumer.Continuation.CONTINUE;
      });
   }

   public List<? extends EnderDragon> m_8857_() {
      return this.m_143280_(EntityType.f_20565_, LivingEntity::m_6084_);
   }

   public List<ServerPlayer> m_8795_(Predicate<? super ServerPlayer> p_8796_) {
      return this.m_261156_(p_8796_, Integer.MAX_VALUE);
   }

   public List<ServerPlayer> m_261156_(Predicate<? super ServerPlayer> p_261698_, int p_262035_) {
      List<ServerPlayer> list = Lists.newArrayList();

      for(ServerPlayer serverplayer : this.f_8546_) {
         if (p_261698_.test(serverplayer)) {
            list.add(serverplayer);
            if (list.size() >= p_262035_) {
               return list;
            }
         }
      }

      return list;
   }

   @Nullable
   public ServerPlayer m_8890_() {
      List<ServerPlayer> list = this.m_8795_(LivingEntity::m_6084_);
      return list.isEmpty() ? null : list.get(this.f_46441_.m_188503_(list.size()));
   }

   public boolean m_7967_(Entity p_8837_) {
      return this.m_8872_(p_8837_);
   }

   public boolean m_8847_(Entity p_8848_) {
      return this.m_8872_(p_8848_);
   }

   public void m_143334_(Entity p_143335_) {
      this.m_8872_(p_143335_);
   }

   public void m_8622_(ServerPlayer p_8623_) {
      this.m_8853_(p_8623_);
   }

   public void m_8817_(ServerPlayer p_8818_) {
      this.m_8853_(p_8818_);
   }

   public void m_8834_(ServerPlayer p_8835_) {
      this.m_8853_(p_8835_);
   }

   public void m_8845_(ServerPlayer p_8846_) {
      this.m_8853_(p_8846_);
   }

   private void m_8853_(ServerPlayer p_8854_) {
      if (net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.EntityJoinLevelEvent(p_8854_, this))) return;
      Entity entity = this.m_142646_().m_142694_(p_8854_.m_20148_());
      if (entity != null) {
         f_8566_.warn("Force-added player with duplicate UUID {}", (Object)p_8854_.m_20148_().toString());
         entity.m_19877_();
         this.m_143261_((ServerPlayer)entity, Entity.RemovalReason.DISCARDED);
      }

      this.f_143244_.addNewEntityWithoutEvent(p_8854_);
      p_8854_.onAddedToWorld();
   }

   private boolean m_8872_(Entity p_8873_) {
      if (p_8873_.m_213877_()) {
         f_8566_.warn("Tried to add entity {} but it was marked as removed already", (Object)EntityType.m_20613_(p_8873_.m_6095_()));
         return false;
      } else {
         if (this.f_143244_.m_157533_(p_8873_)) {
            p_8873_.onAddedToWorld();
            return true;
         } else {
            return false;
         }
      }
   }

   public boolean m_8860_(Entity p_8861_) {
      if (p_8861_.m_20199_().map(Entity::m_20148_).anyMatch(this.f_143244_::m_157550_)) {
         return false;
      } else {
         this.m_47205_(p_8861_);
         return true;
      }
   }

   public void m_8712_(LevelChunk p_8713_) {
      p_8713_.m_187957_();
      p_8713_.m_187979_(this);
   }

   public void m_143261_(ServerPlayer p_143262_, Entity.RemovalReason p_143263_) {
      p_143262_.m_142687_(p_143263_);
   }

   public void m_6801_(int p_8612_, BlockPos p_8613_, int p_8614_) {
      for(ServerPlayer serverplayer : this.f_8548_.m_6846_().m_11314_()) {
         if (serverplayer != null && serverplayer.m_9236_() == this && serverplayer.m_19879_() != p_8612_) {
            double d0 = (double)p_8613_.m_123341_() - serverplayer.m_20185_();
            double d1 = (double)p_8613_.m_123342_() - serverplayer.m_20186_();
            double d2 = (double)p_8613_.m_123343_() - serverplayer.m_20189_();
            if (d0 * d0 + d1 * d1 + d2 * d2 < 1024.0D) {
               serverplayer.f_8906_.m_9829_(new ClientboundBlockDestructionPacket(p_8612_, p_8613_, p_8614_));
            }
         }
      }

   }

   public void m_262808_(@Nullable Player p_263330_, double p_263393_, double p_263369_, double p_263354_, Holder<SoundEvent> p_263412_, SoundSource p_263338_, float p_263352_, float p_263390_, long p_263403_) {
      net.minecraftforge.event.PlayLevelSoundEvent.AtPosition event = net.minecraftforge.event.ForgeEventFactory.onPlaySoundAtPosition(this, p_263393_, p_263369_, p_263354_, p_263412_, p_263338_, p_263352_, p_263390_);
      if (event.isCanceled() || event.getSound() == null) return;
      p_263412_ = event.getSound();
      p_263338_ = event.getSource();
      p_263352_ = event.getNewVolume();
      p_263390_ = event.getNewPitch();
      this.f_8548_.m_6846_().m_11241_(p_263330_, p_263393_, p_263369_, p_263354_, (double)p_263412_.m_203334_().m_215668_(p_263352_), this.m_46472_(), new ClientboundSoundPacket(p_263412_, p_263338_, p_263393_, p_263369_, p_263354_, p_263352_, p_263390_, p_263403_));
   }

   public void m_213890_(@Nullable Player p_263545_, Entity p_263544_, Holder<SoundEvent> p_263491_, SoundSource p_263542_, float p_263530_, float p_263520_, long p_263490_) {
      net.minecraftforge.event.PlayLevelSoundEvent.AtEntity event = net.minecraftforge.event.ForgeEventFactory.onPlaySoundAtEntity(p_263544_, p_263491_, p_263542_, p_263530_, p_263520_);
      if (event.isCanceled() || event.getSound() == null) return;
      p_263491_ = event.getSound();
      p_263542_ = event.getSource();
      p_263530_ = event.getNewVolume();
      p_263520_ = event.getNewPitch();
      this.f_8548_.m_6846_().m_11241_(p_263545_, p_263544_.m_20185_(), p_263544_.m_20186_(), p_263544_.m_20189_(), (double)p_263491_.m_203334_().m_215668_(p_263530_), this.m_46472_(), new ClientboundSoundEntityPacket(p_263491_, p_263542_, p_263544_, p_263530_, p_263520_, p_263490_));
   }

   public void m_6798_(int p_8811_, BlockPos p_8812_, int p_8813_) {
      if (this.m_46469_().m_46207_(GameRules.f_254630_)) {
         this.f_8548_.m_6846_().m_11268_(new ClientboundLevelEventPacket(p_8811_, p_8812_, p_8813_, true));
      } else {
         this.m_5898_((Player)null, p_8811_, p_8812_, p_8813_);
      }

   }

   public void m_5898_(@Nullable Player p_8684_, int p_8685_, BlockPos p_8686_, int p_8687_) {
      this.f_8548_.m_6846_().m_11241_(p_8684_, (double)p_8686_.m_123341_(), (double)p_8686_.m_123342_(), (double)p_8686_.m_123343_(), 64.0D, this.m_46472_(), new ClientboundLevelEventPacket(p_8685_, p_8686_, p_8687_, false));
   }

   public int m_143344_() {
      return this.m_6042_().f_63865_();
   }

   public void m_214171_(GameEvent p_215041_, Vec3 p_215042_, GameEvent.Context p_215043_) {
      if (!net.minecraftforge.common.ForgeHooks.onVanillaGameEvent(this, p_215041_, p_215042_, p_215043_)) return;
      this.f_243695_.m_245905_(p_215041_, p_215042_, p_215043_);
   }

   public void m_7260_(BlockPos p_8755_, BlockState p_8756_, BlockState p_8757_, int p_8758_) {
      if (this.f_200893_) {
         String s = "recursive call to sendBlockUpdated";
         Util.m_200890_("recursive call to sendBlockUpdated", new IllegalStateException("recursive call to sendBlockUpdated"));
      }

      this.m_7726_().m_8450_(p_8755_);
      VoxelShape voxelshape1 = p_8756_.m_60812_(this, p_8755_);
      VoxelShape voxelshape = p_8757_.m_60812_(this, p_8755_);
      if (Shapes.m_83157_(voxelshape1, voxelshape, BooleanOp.f_82687_)) {
         List<PathNavigation> list = new ObjectArrayList<>();

         for(Mob mob : this.f_143246_) {
            PathNavigation pathnavigation = mob.m_21573_();
            if (pathnavigation.m_200903_(p_8755_)) {
               list.add(pathnavigation);
            }
         }

         try {
            this.f_200893_ = true;

            for(PathNavigation pathnavigation1 : list) {
               pathnavigation1.m_26569_();
            }
         } finally {
            this.f_200893_ = false;
         }

      }
   }

   public void m_46672_(BlockPos p_215045_, Block p_215046_) {
      net.minecraftforge.event.ForgeEventFactory.onNeighborNotify(this, p_215045_, this.m_8055_(p_215045_), java.util.EnumSet.allOf(Direction.class), false).isCanceled();
      this.f_220350_.m_214152_(p_215045_, p_215046_, (Direction)null);
   }

   public void m_46590_(BlockPos p_215052_, Block p_215053_, Direction p_215054_) {
      java.util.EnumSet<Direction> directions = java.util.EnumSet.allOf(Direction.class);
      directions.remove(p_215054_);
      if (net.minecraftforge.event.ForgeEventFactory.onNeighborNotify(this, p_215052_, this.m_8055_(p_215052_), directions, false).isCanceled())
         return;
      this.f_220350_.m_214152_(p_215052_, p_215053_, p_215054_);
   }

   public void m_46586_(BlockPos p_215048_, Block p_215049_, BlockPos p_215050_) {
      this.f_220350_.m_214026_(p_215048_, p_215049_, p_215050_);
   }

   public void m_213960_(BlockState p_215035_, BlockPos p_215036_, Block p_215037_, BlockPos p_215038_, boolean p_215039_) {
      this.f_220350_.m_213858_(p_215035_, p_215036_, p_215037_, p_215038_, p_215039_);
   }

   public void m_7605_(Entity p_8650_, byte p_8651_) {
      this.m_7726_().m_8394_(p_8650_, new ClientboundEntityEventPacket(p_8650_, p_8651_));
   }

   public void m_269196_(Entity p_270420_, DamageSource p_270311_) {
      this.m_7726_().m_8394_(p_270420_, new ClientboundDamageEventPacket(p_270420_, p_270311_));
   }

   public ServerChunkCache m_7726_() {
      return this.f_8547_;
   }

   public Explosion m_254877_(@Nullable Entity p_256039_, @Nullable DamageSource p_255778_, @Nullable ExplosionDamageCalculator p_256002_, double p_256067_, double p_256370_, double p_256153_, float p_256045_, boolean p_255686_, Level.ExplosionInteraction p_255827_) {
      Explosion explosion = this.m_255278_(p_256039_, p_255778_, p_256002_, p_256067_, p_256370_, p_256153_, p_256045_, p_255686_, p_255827_, false);
      if (!explosion.m_254884_()) {
         explosion.m_46080_();
      }

      for(ServerPlayer serverplayer : this.f_8546_) {
         if (serverplayer.m_20275_(p_256067_, p_256370_, p_256153_) < 4096.0D) {
            serverplayer.f_8906_.m_9829_(new ClientboundExplodePacket(p_256067_, p_256370_, p_256153_, p_256045_, explosion.m_46081_(), explosion.m_46078_().get(serverplayer)));
         }
      }

      return explosion;
   }

   public void m_7696_(BlockPos p_8746_, Block p_8747_, int p_8748_, int p_8749_) {
      this.f_8556_.add(new BlockEventData(p_8746_, p_8747_, p_8748_, p_8749_));
   }

   private void m_8807_() {
      this.f_184048_.clear();

      while(!this.f_8556_.isEmpty()) {
         BlockEventData blockeventdata = this.f_8556_.removeFirst();
         if (this.m_220393_(blockeventdata.f_45529_())) {
            if (this.m_8698_(blockeventdata)) {
               this.f_8548_.m_6846_().m_11241_((Player)null, (double)blockeventdata.f_45529_().m_123341_(), (double)blockeventdata.f_45529_().m_123342_(), (double)blockeventdata.f_45529_().m_123343_(), 64.0D, this.m_46472_(), new ClientboundBlockEventPacket(blockeventdata.f_45529_(), blockeventdata.f_45530_(), blockeventdata.f_45531_(), blockeventdata.f_45532_()));
            }
         } else {
            this.f_184048_.add(blockeventdata);
         }
      }

      this.f_8556_.addAll(this.f_184048_);
   }

   private boolean m_8698_(BlockEventData p_8699_) {
      BlockState blockstate = this.m_8055_(p_8699_.f_45529_());
      return blockstate.m_60713_(p_8699_.f_45530_()) ? blockstate.m_60677_(this, p_8699_.f_45529_(), p_8699_.f_45531_(), p_8699_.f_45532_()) : false;
   }

   public LevelTicks<Block> m_183326_() {
      return this.f_8553_;
   }

   public LevelTicks<Fluid> m_183324_() {
      return this.f_184047_;
   }

   @Nonnull
   public MinecraftServer m_7654_() {
      return this.f_8548_;
   }

   public PortalForcer m_8871_() {
      return this.f_8552_;
   }

   public StructureTemplateManager m_215082_() {
      return this.f_8548_.m_236738_();
   }

   public <T extends ParticleOptions> int m_8767_(T p_8768_, double p_8769_, double p_8770_, double p_8771_, int p_8772_, double p_8773_, double p_8774_, double p_8775_, double p_8776_) {
      ClientboundLevelParticlesPacket clientboundlevelparticlespacket = new ClientboundLevelParticlesPacket(p_8768_, false, p_8769_, p_8770_, p_8771_, (float)p_8773_, (float)p_8774_, (float)p_8775_, (float)p_8776_, p_8772_);
      int i = 0;

      for(int j = 0; j < this.f_8546_.size(); ++j) {
         ServerPlayer serverplayer = this.f_8546_.get(j);
         if (this.m_8636_(serverplayer, false, p_8769_, p_8770_, p_8771_, clientboundlevelparticlespacket)) {
            ++i;
         }
      }

      return i;
   }

   public <T extends ParticleOptions> boolean m_8624_(ServerPlayer p_8625_, T p_8626_, boolean p_8627_, double p_8628_, double p_8629_, double p_8630_, int p_8631_, double p_8632_, double p_8633_, double p_8634_, double p_8635_) {
      Packet<?> packet = new ClientboundLevelParticlesPacket(p_8626_, p_8627_, p_8628_, p_8629_, p_8630_, (float)p_8632_, (float)p_8633_, (float)p_8634_, (float)p_8635_, p_8631_);
      return this.m_8636_(p_8625_, p_8627_, p_8628_, p_8629_, p_8630_, packet);
   }

   private boolean m_8636_(ServerPlayer p_8637_, boolean p_8638_, double p_8639_, double p_8640_, double p_8641_, Packet<?> p_8642_) {
      if (p_8637_.m_9236_() != this) {
         return false;
      } else {
         BlockPos blockpos = p_8637_.m_20183_();
         if (blockpos.m_203195_(new Vec3(p_8639_, p_8640_, p_8641_), p_8638_ ? 512.0D : 32.0D)) {
            p_8637_.f_8906_.m_9829_(p_8642_);
            return true;
         } else {
            return false;
         }
      }
   }

   @Nullable
   public Entity m_6815_(int p_8597_) {
      return this.m_142646_().m_142597_(p_8597_);
   }

   /** @deprecated */
   @Deprecated
   @Nullable
   public Entity m_143317_(int p_143318_) {
      Entity entity = this.m_142646_().m_142597_(p_143318_);
      return entity != null ? entity : this.f_143247_.get(p_143318_);
   }

   @Nullable
   public Entity m_8791_(UUID p_8792_) {
      return this.m_142646_().m_142694_(p_8792_);
   }

   @Nullable
   public BlockPos m_215011_(TagKey<Structure> p_215012_, BlockPos p_215013_, int p_215014_, boolean p_215015_) {
      if (!this.f_8548_.m_129910_().m_246337_().m_247749_()) {
         return null;
      } else {
         Optional<HolderSet.Named<Structure>> optional = this.m_9598_().m_175515_(Registries.f_256944_).m_203431_(p_215012_);
         if (optional.isEmpty()) {
            return null;
         } else {
            Pair<BlockPos, Holder<Structure>> pair = this.m_7726_().m_8481_().m_223037_(this, optional.get(), p_215013_, p_215014_, p_215015_);
            return pair != null ? pair.getFirst() : null;
         }
      }
   }

   @Nullable
   public Pair<BlockPos, Holder<Biome>> m_215069_(Predicate<Holder<Biome>> p_215070_, BlockPos p_215071_, int p_215072_, int p_215073_, int p_215074_) {
      return this.m_7726_().m_8481_().m_62218_().m_214004_(p_215071_, p_215072_, p_215073_, p_215074_, p_215070_, this.m_7726_().m_214994_().m_224579_(), this);
   }

   public RecipeManager m_7465_() {
      return this.f_8548_.m_129894_();
   }

   public boolean m_7441_() {
      return this.f_8564_;
   }

   public DimensionDataStorage m_8895_() {
      return this.m_7726_().m_8483_();
   }

   @Nullable
   public MapItemSavedData m_7489_(String p_8785_) {
      return this.m_7654_().m_129783_().m_8895_().m_164858_(MapItemSavedData::m_164807_, p_8785_);
   }

   public void m_142325_(String p_143305_, MapItemSavedData p_143306_) {
      this.m_7654_().m_129783_().m_8895_().m_164855_(p_143305_, p_143306_);
   }

   public int m_7354_() {
      return this.m_7654_().m_129783_().m_8895_().m_164861_(MapIndex::m_164762_, MapIndex::new, "idcounts").m_77880_();
   }

   public void m_8733_(BlockPos p_8734_, float p_8735_) {
      ChunkPos chunkpos = new ChunkPos(new BlockPos(this.f_46442_.m_6789_(), 0, this.f_46442_.m_6526_()));
      this.f_46442_.m_7250_(p_8734_, p_8735_);
      this.m_7726_().m_8438_(TicketType.f_9442_, chunkpos, 11, Unit.INSTANCE);
      this.m_7726_().m_8387_(TicketType.f_9442_, new ChunkPos(p_8734_), 11, Unit.INSTANCE);
      this.m_7654_().m_6846_().m_11268_(new ClientboundSetDefaultSpawnPositionPacket(p_8734_, p_8735_));
   }

   public LongSet m_8902_() {
      ForcedChunksSavedData forcedchunkssaveddata = this.m_8895_().m_164858_(ForcedChunksSavedData::m_151483_, "chunks");
      return (LongSet)(forcedchunkssaveddata != null ? LongSets.unmodifiable(forcedchunkssaveddata.m_46116_()) : LongSets.EMPTY_SET);
   }

   public boolean m_8602_(int p_8603_, int p_8604_, boolean p_8605_) {
      ForcedChunksSavedData forcedchunkssaveddata = this.m_8895_().m_164861_(ForcedChunksSavedData::m_151483_, ForcedChunksSavedData::new, "chunks");
      ChunkPos chunkpos = new ChunkPos(p_8603_, p_8604_);
      long i = chunkpos.m_45588_();
      boolean flag;
      if (p_8605_) {
         flag = forcedchunkssaveddata.m_46116_().add(i);
         if (flag) {
            this.m_6325_(p_8603_, p_8604_);
         }
      } else {
         flag = forcedchunkssaveddata.m_46116_().remove(i);
      }

      forcedchunkssaveddata.m_77760_(flag);
      if (flag) {
         this.m_7726_().m_6692_(chunkpos, p_8605_);
      }

      return flag;
   }

   public List<ServerPlayer> m_6907_() {
      return this.f_8546_;
   }

   public void m_6559_(BlockPos p_8751_, BlockState p_8752_, BlockState p_8753_) {
      Optional<Holder<PoiType>> optional = PoiTypes.m_218075_(p_8752_);
      Optional<Holder<PoiType>> optional1 = PoiTypes.m_218075_(p_8753_);
      if (!Objects.equals(optional, optional1)) {
         BlockPos blockpos = p_8751_.m_7949_();
         optional.ifPresent((p_215081_) -> {
            this.m_7654_().execute(() -> {
               this.m_8904_().m_27079_(blockpos);
               DebugPackets.m_133716_(this, blockpos);
            });
         });
         optional1.ifPresent((p_215057_) -> {
            this.m_7654_().execute(() -> {
               this.m_8904_().m_217919_(blockpos, p_215057_);
               DebugPackets.m_133679_(this, blockpos);
            });
         });
      }
   }

   public PoiManager m_8904_() {
      return this.m_7726_().m_8484_();
   }

   public boolean m_8802_(BlockPos p_8803_) {
      return this.m_8736_(p_8803_, 1);
   }

   public boolean m_8762_(SectionPos p_8763_) {
      return this.m_8802_(p_8763_.m_123250_());
   }

   public boolean m_8736_(BlockPos p_8737_, int p_8738_) {
      if (p_8738_ > 6) {
         return false;
      } else {
         return this.m_8828_(SectionPos.m_123199_(p_8737_)) <= p_8738_;
      }
   }

   public int m_8828_(SectionPos p_8829_) {
      return this.m_8904_().m_27098_(p_8829_);
   }

   public Raids m_8905_() {
      return this.f_8565_;
   }

   @Nullable
   public Raid m_8832_(BlockPos p_8833_) {
      return this.f_8565_.m_37970_(p_8833_, 9216);
   }

   public boolean m_8843_(BlockPos p_8844_) {
      return this.m_8832_(p_8844_) != null;
   }

   public void m_8670_(ReputationEventType p_8671_, Entity p_8672_, ReputationEventHandler p_8673_) {
      p_8673_.m_6814_(p_8671_, p_8672_);
   }

   public void m_8786_(Path p_8787_) throws IOException {
      ChunkMap chunkmap = this.m_7726_().f_8325_;

      try (Writer writer = Files.newBufferedWriter(p_8787_.resolve("stats.txt"))) {
         writer.write(String.format(Locale.ROOT, "spawning_chunks: %d\n", chunkmap.m_143145_().m_140816_()));
         NaturalSpawner.SpawnState naturalspawner$spawnstate = this.m_7726_().m_8485_();
         if (naturalspawner$spawnstate != null) {
            for(Object2IntMap.Entry<MobCategory> entry : naturalspawner$spawnstate.m_47148_().object2IntEntrySet()) {
               writer.write(String.format(Locale.ROOT, "spawn_count.%s: %d\n", entry.getKey().m_21607_(), entry.getIntValue()));
            }
         }

         writer.write(String.format(Locale.ROOT, "entities: %s\n", this.f_143244_.m_157572_()));
         writer.write(String.format(Locale.ROOT, "block_entity_tickers: %d\n", this.f_151512_.size()));
         writer.write(String.format(Locale.ROOT, "block_ticks: %d\n", this.m_183326_().m_183574_()));
         writer.write(String.format(Locale.ROOT, "fluid_ticks: %d\n", this.m_183324_().m_183574_()));
         writer.write("distance_manager: " + chunkmap.m_143145_().m_140837_() + "\n");
         writer.write(String.format(Locale.ROOT, "pending_tasks: %d\n", this.m_7726_().m_8480_()));
      }

      CrashReport crashreport = new CrashReport("Level dump", new Exception("dummy"));
      this.m_6026_(crashreport);

      try (Writer writer3 = Files.newBufferedWriter(p_8787_.resolve("example_crash.txt"))) {
         writer3.write(crashreport.m_127526_());
      }

      Path path = p_8787_.resolve("chunks.csv");

      try (Writer writer4 = Files.newBufferedWriter(path)) {
         chunkmap.m_140274_(writer4);
      }

      Path path1 = p_8787_.resolve("entity_chunks.csv");

      try (Writer writer5 = Files.newBufferedWriter(path1)) {
         this.f_143244_.m_157548_(writer5);
      }

      Path path2 = p_8787_.resolve("entities.csv");

      try (Writer writer1 = Files.newBufferedWriter(path2)) {
         m_8781_(writer1, this.m_142646_().m_142273_());
      }

      Path path3 = p_8787_.resolve("block_entities.csv");

      try (Writer writer2 = Files.newBufferedWriter(path3)) {
         this.m_143299_(writer2);
      }

   }

   private static void m_8781_(Writer p_8782_, Iterable<Entity> p_8783_) throws IOException {
      CsvOutput csvoutput = CsvOutput.m_13619_().m_13630_("x").m_13630_("y").m_13630_("z").m_13630_("uuid").m_13630_("type").m_13630_("alive").m_13630_("display_name").m_13630_("custom_name").m_13628_(p_8782_);

      for(Entity entity : p_8783_) {
         Component component = entity.m_7770_();
         Component component1 = entity.m_5446_();
         csvoutput.m_13624_(entity.m_20185_(), entity.m_20186_(), entity.m_20189_(), entity.m_20148_(), BuiltInRegistries.f_256780_.m_7981_(entity.m_6095_()), entity.m_6084_(), component1.getString(), component != null ? component.getString() : null);
      }

   }

   private void m_143299_(Writer p_143300_) throws IOException {
      CsvOutput csvoutput = CsvOutput.m_13619_().m_13630_("x").m_13630_("y").m_13630_("z").m_13630_("type").m_13628_(p_143300_);

      for(TickingBlockEntity tickingblockentity : this.f_151512_) {
         BlockPos blockpos = tickingblockentity.m_142689_();
         csvoutput.m_13624_(blockpos.m_123341_(), blockpos.m_123342_(), blockpos.m_123343_(), tickingblockentity.m_142280_());
      }

   }

   @VisibleForTesting
   public void m_8722_(BoundingBox p_8723_) {
      this.f_8556_.removeIf((p_207568_) -> {
         return p_8723_.m_71051_(p_207568_.f_45529_());
      });
   }

   public void m_6289_(BlockPos p_8743_, Block p_8744_) {
      if (!this.m_46659_()) {
         this.m_46672_(p_8743_, p_8744_);
      }

   }

   public float m_7717_(Direction p_8760_, boolean p_8761_) {
      return 1.0F;
   }

   public Iterable<Entity> m_8583_() {
      return this.m_142646_().m_142273_();
   }

   public String toString() {
      return "ServerLevel[" + this.f_8549_.m_5462_() + "]";
   }

   public boolean m_8584_() {
      return this.f_8548_.m_129910_().m_5961_();
   }

   public long m_7328_() {
      return this.f_8548_.m_129910_().m_246337_().m_245499_();
   }

   @Nullable
   public EndDragonFight m_8586_() {
      return this.f_8559_;
   }

   public ServerLevel m_6018_() {
      return this;
   }

   @VisibleForTesting
   public String m_8590_() {
      return String.format(Locale.ROOT, "players: %s, entities: %s [%s], block_entities: %d [%s], block_ticks: %d, fluid_ticks: %d, chunk_source: %s", this.f_8546_.size(), this.f_143244_.m_157572_(), m_143301_(this.f_143244_.m_157567_().m_142273_(), (p_258244_) -> {
         return BuiltInRegistries.f_256780_.m_7981_(p_258244_.m_6095_()).toString();
      }), this.f_151512_.size(), m_143301_(this.f_151512_, TickingBlockEntity::m_142280_), this.m_183326_().m_183574_(), this.m_183324_().m_183574_(), this.m_46464_());
   }

   private static <T> String m_143301_(Iterable<T> p_143302_, Function<T, String> p_143303_) {
      try {
         Object2IntOpenHashMap<String> object2intopenhashmap = new Object2IntOpenHashMap<>();

         for(T t : p_143302_) {
            String s = p_143303_.apply(t);
            object2intopenhashmap.addTo(s, 1);
         }

         return object2intopenhashmap.object2IntEntrySet().stream().sorted(Comparator.<Object2IntMap.Entry<String>,Integer>comparing(Object2IntMap.Entry::getIntValue).reversed()).limit(5L).map((p_207570_) -> {
            return (String)p_207570_.getKey() + ":" + p_207570_.getIntValue();
         }).collect(Collectors.joining(","));
      } catch (Exception exception) {
         return "";
      }
   }

   public static void m_8617_(ServerLevel p_8618_) {
      BlockPos blockpos = f_8562_;
      int i = blockpos.m_123341_();
      int j = blockpos.m_123342_() - 2;
      int k = blockpos.m_123343_();
      BlockPos.m_121976_(i - 2, j + 1, k - 2, i + 2, j + 3, k + 2).forEach((p_207578_) -> {
         p_8618_.m_46597_(p_207578_, Blocks.f_50016_.m_49966_());
      });
      BlockPos.m_121976_(i - 2, j, k - 2, i + 2, j, k + 2).forEach((p_184101_) -> {
         p_8618_.m_46597_(p_184101_, Blocks.f_50080_.m_49966_());
      });
   }

   protected void initCapabilities() {
      this.gatherCapabilities();
      capabilityData = this.m_8895_().m_164861_(e -> net.minecraftforge.common.util.LevelCapabilityData.load(e, getCapabilities()), () -> new net.minecraftforge.common.util.LevelCapabilityData(getCapabilities()), net.minecraftforge.common.util.LevelCapabilityData.ID);
      capabilityData.setCapabilities(getCapabilities());
   }

   public LevelEntityGetter<Entity> m_142646_() {
      return this.f_143244_.m_157567_();
   }

   public void m_143311_(Stream<Entity> p_143312_) {
      this.f_143244_.m_157552_(p_143312_);
   }

   public void m_143327_(Stream<Entity> p_143328_) {
      this.f_143244_.m_157559_(p_143328_);
   }

   public void m_184102_(LevelChunk p_184103_) {
      p_184103_.m_187985_(this.m_6106_().m_6793_());
   }

   public void m_196557_(ChunkAccess p_196558_) {
      this.f_8548_.execute(() -> {
         this.f_196556_.m_197282_(p_196558_.m_7697_(), p_196558_.m_6633_());
      });
   }

   public void close() throws IOException {
      super.close();
      this.f_143244_.close();
   }

   public String m_46464_() {
      return "Chunks[S] W: " + this.f_8547_.m_6754_() + " E: " + this.f_143244_.m_157572_();
   }

   public boolean m_143319_(long p_143320_) {
      return this.f_143244_.m_157507_(p_143320_);
   }

   private boolean m_184110_(long p_184111_) {
      return this.m_143319_(p_184111_) && this.f_8547_.m_143239_(p_184111_);
   }

   public boolean m_143340_(BlockPos p_143341_) {
      return this.f_143244_.m_202167_(p_143341_) && this.f_8547_.f_8325_.m_143145_().m_183913_(ChunkPos.m_151388_(p_143341_));
   }

   public boolean m_201918_(BlockPos p_201919_) {
      return this.f_143244_.m_202167_(p_201919_);
   }

   public boolean m_201916_(ChunkPos p_201917_) {
      return this.f_143244_.m_202165_(p_201917_);
   }

   public FeatureFlagSet m_246046_() {
      return this.f_8548_.m_129910_().m_247623_();
   }

   public RandomSource m_287143_(ResourceLocation p_287689_) {
      return this.f_286969_.m_287292_(p_287689_);
   }

   public RandomSequences m_288231_() {
      return this.f_286969_;
   }

   final class EntityCallbacks implements LevelCallback<Entity> {
      public void m_141989_(Entity p_143355_) {
      }

      public void m_141986_(Entity p_143359_) {
         ServerLevel.this.m_6188_().m_83420_(p_143359_);
      }

      public void m_141987_(Entity p_143363_) {
         ServerLevel.this.f_143243_.m_156908_(p_143363_);
      }

      public void m_141983_(Entity p_143367_) {
         ServerLevel.this.f_143243_.m_156912_(p_143367_);
      }

      public void m_141985_(Entity p_143371_) {
         ServerLevel.this.m_7726_().m_8463_(p_143371_);
         if (p_143371_ instanceof ServerPlayer serverplayer) {
            ServerLevel.this.f_8546_.add(serverplayer);
            ServerLevel.this.m_8878_();
         }

         if (p_143371_ instanceof Mob mob) {
            if (ServerLevel.this.f_200893_) {
               String s = "onTrackingStart called during navigation iteration";
               Util.m_200890_("onTrackingStart called during navigation iteration", new IllegalStateException("onTrackingStart called during navigation iteration"));
            }

            ServerLevel.this.f_143246_.add(mob);
         }

         if (p_143371_.isMultipartEntity()) {
            for(net.minecraftforge.entity.PartEntity<?> enderdragonpart : p_143371_.getParts()) {
               ServerLevel.this.f_143247_.put(enderdragonpart.m_19879_(), enderdragonpart);
            }
         }

         p_143371_.m_213651_(DynamicGameEventListener::m_223617_);
      }

      public void m_141981_(Entity p_143375_) {
         ServerLevel.this.m_7726_().m_8443_(p_143375_);
         if (p_143375_ instanceof ServerPlayer serverplayer) {
            ServerLevel.this.f_8546_.remove(serverplayer);
            ServerLevel.this.m_8878_();
         }

         if (p_143375_ instanceof Mob mob) {
            if (ServerLevel.this.f_200893_) {
               String s = "onTrackingStart called during navigation iteration";
               Util.m_200890_("onTrackingStart called during navigation iteration", new IllegalStateException("onTrackingStart called during navigation iteration"));
            }

            ServerLevel.this.f_143246_.remove(mob);
         }

         if (p_143375_.isMultipartEntity()) {
            for(net.minecraftforge.entity.PartEntity<?> enderdragonpart : p_143375_.getParts()) {
               ServerLevel.this.f_143247_.remove(enderdragonpart.m_19879_());
            }
         }

         p_143375_.m_213651_(DynamicGameEventListener::m_223634_);

         p_143375_.onRemovedFromWorld();
         net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.EntityLeaveLevelEvent(p_143375_, ServerLevel.this));
      }

      public void m_214006_(Entity p_215086_) {
         p_215086_.m_213651_(DynamicGameEventListener::m_223641_);
      }
   }

   @Override
   public java.util.Collection<net.minecraftforge.entity.PartEntity<?>> getPartEntities() {
      return this.f_143247_.values();
   }
}
