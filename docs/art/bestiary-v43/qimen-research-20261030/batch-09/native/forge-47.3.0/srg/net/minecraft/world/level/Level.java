package net.minecraft.world.level;

import com.google.common.collect.Lists;
import com.mojang.serialization.Codec;
import java.io.IOException;
import java.util.Iterator;
import java.util.List;
import java.util.function.Consumer;
import java.util.function.Predicate;
import java.util.function.Supplier;
import javax.annotation.Nullable;
import net.minecraft.CrashReport;
import net.minecraft.CrashReportCategory;
import net.minecraft.ReportedException;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.Holder;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.SectionPos;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.FullChunkStatus;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.AbortableIterationConsumer;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageSources;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.boss.EnderDragonPart;
import net.minecraft.world.entity.boss.enderdragon.EnderDragon;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.RecipeManager;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.BiomeManager;
import net.minecraft.world.level.block.BaseFireBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.TickingBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.border.WorldBorder;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.chunk.ChunkStatus;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.dimension.DimensionType;
import net.minecraft.world.level.entity.EntityTypeTest;
import net.minecraft.world.level.entity.LevelEntityGetter;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.lighting.LevelLightEngine;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.level.material.Fluids;
import net.minecraft.world.level.redstone.CollectingNeighborUpdater;
import net.minecraft.world.level.redstone.NeighborUpdater;
import net.minecraft.world.level.saveddata.maps.MapItemSavedData;
import net.minecraft.world.level.storage.LevelData;
import net.minecraft.world.level.storage.WritableLevelData;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.scores.Scoreboard;

public abstract class Level extends net.minecraftforge.common.capabilities.CapabilityProvider<Level> implements LevelAccessor, AutoCloseable, net.minecraftforge.common.extensions.IForgeLevel {
   public static final Codec<ResourceKey<Level>> f_46427_ = ResourceKey.m_195966_(Registries.f_256858_);
   public static final ResourceKey<Level> f_46428_ = ResourceKey.m_135785_(Registries.f_256858_, new ResourceLocation("overworld"));
   public static final ResourceKey<Level> f_46429_ = ResourceKey.m_135785_(Registries.f_256858_, new ResourceLocation("the_nether"));
   public static final ResourceKey<Level> f_46430_ = ResourceKey.m_135785_(Registries.f_256858_, new ResourceLocation("the_end"));
   public static final int f_151505_ = 30000000;
   public static final int f_151506_ = 512;
   public static final int f_151507_ = 32;
   public static final int f_151508_ = 15;
   public static final int f_151509_ = 24000;
   public static final int f_151510_ = 20000000;
   public static final int f_151511_ = -20000000;
   protected final List<TickingBlockEntity> f_151512_ = Lists.newArrayList();
   protected final NeighborUpdater f_220350_;
   private final List<TickingBlockEntity> f_151503_ = Lists.newArrayList();
   private boolean f_151504_;
   private final Thread f_46423_;
   private final boolean f_46424_;
   private int f_46425_;
   protected int f_46435_ = RandomSource.m_216327_().m_188502_();
   protected final int f_46436_ = 1013904223;
   public float f_46437_;
   public float f_46438_;
   public float f_46439_;
   public float f_46440_;
   public final RandomSource f_46441_ = RandomSource.m_216327_();
   /** @deprecated */
   @Deprecated
   private final RandomSource f_220348_ = RandomSource.m_216337_();
   private final ResourceKey<DimensionType> f_220349_;
   private final Holder<DimensionType> f_204147_;
   protected final WritableLevelData f_46442_;
   private final Supplier<ProfilerFiller> f_46446_;
   public final boolean f_46443_;
   private final WorldBorder f_46447_;
   private final BiomeManager f_46420_;
   private final ResourceKey<Level> f_46421_;
   private final RegistryAccess f_268710_;
   private final DamageSources f_268497_;
   private long f_186455_;
   public boolean restoringBlockSnapshots = false;
   public boolean captureBlockSnapshots = false;
   public java.util.ArrayList<net.minecraftforge.common.util.BlockSnapshot> capturedBlockSnapshots = new java.util.ArrayList<>();
   private final java.util.ArrayList<BlockEntity> freshBlockEntities = new java.util.ArrayList<>();
   private final java.util.ArrayList<BlockEntity> pendingFreshBlockEntities = new java.util.ArrayList<>();

   protected Level(WritableLevelData p_270739_, ResourceKey<Level> p_270683_, RegistryAccess p_270200_, Holder<DimensionType> p_270240_, Supplier<ProfilerFiller> p_270692_, boolean p_270904_, boolean p_270470_, long p_270248_, int p_270466_) {
      super(Level.class);
      this.f_46446_ = p_270692_;
      this.f_46442_ = p_270739_;
      this.f_204147_ = p_270240_;
      this.f_220349_ = p_270240_.m_203543_().orElseThrow(() -> {
         return new IllegalArgumentException("Dimension must be registered, got " + p_270240_);
      });
      final DimensionType dimensiontype = p_270240_.m_203334_();
      this.f_46421_ = p_270683_;
      this.f_46443_ = p_270904_;
      if (dimensiontype.f_63859_() != 1.0D) {
         this.f_46447_ = new WorldBorder() {
            public double m_6347_() {
               return super.m_6347_() / dimensiontype.f_63859_();
            }

            public double m_6345_() {
               return super.m_6345_() / dimensiontype.f_63859_();
            }
         };
      } else {
         this.f_46447_ = new WorldBorder();
      }

      this.f_46423_ = Thread.currentThread();
      this.f_46420_ = new BiomeManager(this, p_270248_);
      this.f_46424_ = p_270470_;
      this.f_220350_ = new CollectingNeighborUpdater(this, p_270466_);
      this.f_268710_ = p_270200_;
      this.f_268497_ = new DamageSources(p_270200_);
   }

   public boolean m_5776_() {
      return this.f_46443_;
   }

   @Nullable
   public MinecraftServer m_7654_() {
      return null;
   }

   public boolean m_46739_(BlockPos p_46740_) {
      return !this.m_151570_(p_46740_) && m_46457_(p_46740_);
   }

   public static boolean m_46741_(BlockPos p_46742_) {
      return !m_46724_(p_46742_.m_123342_()) && m_46457_(p_46742_);
   }

   private static boolean m_46457_(BlockPos p_46458_) {
      return p_46458_.m_123341_() >= -30000000 && p_46458_.m_123343_() >= -30000000 && p_46458_.m_123341_() < 30000000 && p_46458_.m_123343_() < 30000000;
   }

   private static boolean m_46724_(int p_46725_) {
      return p_46725_ < -20000000 || p_46725_ >= 20000000;
   }

   public LevelChunk m_46745_(BlockPos p_46746_) {
      return this.m_6325_(SectionPos.m_123171_(p_46746_.m_123341_()), SectionPos.m_123171_(p_46746_.m_123343_()));
   }

   public LevelChunk m_6325_(int p_46727_, int p_46728_) {
      return (LevelChunk)this.m_46819_(p_46727_, p_46728_, ChunkStatus.f_62326_);
   }

   @Nullable
   public ChunkAccess m_6522_(int p_46502_, int p_46503_, ChunkStatus p_46504_, boolean p_46505_) {
      ChunkAccess chunkaccess = this.m_7726_().m_7587_(p_46502_, p_46503_, p_46504_, p_46505_);
      if (chunkaccess == null && p_46505_) {
         throw new IllegalStateException("Should always be able to create a chunk!");
      } else {
         return chunkaccess;
      }
   }

   public boolean m_7731_(BlockPos p_46601_, BlockState p_46602_, int p_46603_) {
      return this.m_6933_(p_46601_, p_46602_, p_46603_, 512);
   }

   public boolean m_6933_(BlockPos p_46605_, BlockState p_46606_, int p_46607_, int p_46608_) {
      if (this.m_151570_(p_46605_)) {
         return false;
      } else if (!this.f_46443_ && this.m_46659_()) {
         return false;
      } else {
         LevelChunk levelchunk = this.m_46745_(p_46605_);
         Block block = p_46606_.m_60734_();

         p_46605_ = p_46605_.m_7949_(); // Forge - prevent mutable BlockPos leaks
         net.minecraftforge.common.util.BlockSnapshot blockSnapshot = null;
         if (this.captureBlockSnapshots && !this.f_46443_) {
             blockSnapshot = net.minecraftforge.common.util.BlockSnapshot.create(this.f_46421_, this, p_46605_, p_46607_);
             this.capturedBlockSnapshots.add(blockSnapshot);
         }

         BlockState old = m_8055_(p_46605_);
         int oldLight = old.getLightEmission(this, p_46605_);
         int oldOpacity = old.m_60739_(this, p_46605_);

         BlockState blockstate = levelchunk.m_6978_(p_46605_, p_46606_, (p_46607_ & 64) != 0);
         if (blockstate == null) {
            if (blockSnapshot != null) this.capturedBlockSnapshots.remove(blockSnapshot);
            return false;
         } else {
            BlockState blockstate1 = this.m_8055_(p_46605_);

            if (blockSnapshot == null) { // Don't notify clients or update physics while capturing blockstates
               this.markAndNotifyBlock(p_46605_, levelchunk, blockstate, p_46606_, p_46607_, p_46608_);
            }

            return true;
         }
      }
   }

   // Split off from original setBlockState(BlockPos, BlockState, int, int) method in order to directly send client and physic updates
   public void markAndNotifyBlock(BlockPos p_46605_, @Nullable LevelChunk levelchunk, BlockState blockstate, BlockState p_46606_, int p_46607_, int p_46608_) {
      Block block = p_46606_.m_60734_();
      BlockState blockstate1 = m_8055_(p_46605_);
      {
         {
            if (blockstate1 == p_46606_) {
               if (blockstate != blockstate1) {
                  this.m_6550_(p_46605_, blockstate, blockstate1);
               }

               if ((p_46607_ & 2) != 0 && (!this.f_46443_ || (p_46607_ & 4) == 0) && (this.f_46443_ || levelchunk.m_287138_() != null && levelchunk.m_287138_().m_287205_(FullChunkStatus.BLOCK_TICKING))) {
                  this.m_7260_(p_46605_, blockstate, p_46606_, p_46607_);
               }

               if ((p_46607_ & 1) != 0) {
                  this.m_6289_(p_46605_, blockstate.m_60734_());
                  if (!this.f_46443_ && p_46606_.m_60807_()) {
                     this.m_46717_(p_46605_, block);
                  }
               }

               if ((p_46607_ & 16) == 0 && p_46608_ > 0) {
                  int i = p_46607_ & -34;
                  blockstate.m_60762_(this, p_46605_, i, p_46608_ - 1);
                  p_46606_.m_60705_(this, p_46605_, i, p_46608_ - 1);
                  p_46606_.m_60762_(this, p_46605_, i, p_46608_ - 1);
               }

               this.m_6559_(p_46605_, blockstate, blockstate1);
               p_46606_.onBlockStateChange(this, p_46605_, blockstate);
            }
         }
      }
   }

   public void m_6559_(BlockPos p_46609_, BlockState p_46610_, BlockState p_46611_) {
   }

   public boolean m_7471_(BlockPos p_46623_, boolean p_46624_) {
      FluidState fluidstate = this.m_6425_(p_46623_);
      return this.m_7731_(p_46623_, fluidstate.m_76188_(), 3 | (p_46624_ ? 64 : 0));
   }

   public boolean m_7740_(BlockPos p_46626_, boolean p_46627_, @Nullable Entity p_46628_, int p_46629_) {
      BlockState blockstate = this.m_8055_(p_46626_);
      if (blockstate.m_60795_()) {
         return false;
      } else {
         FluidState fluidstate = this.m_6425_(p_46626_);
         if (!(blockstate.m_60734_() instanceof BaseFireBlock)) {
            this.m_46796_(2001, p_46626_, Block.m_49956_(blockstate));
         }

         if (p_46627_) {
            BlockEntity blockentity = blockstate.m_155947_() ? this.m_7702_(p_46626_) : null;
            Block.m_49881_(blockstate, this, p_46626_, blockentity, p_46628_, ItemStack.f_41583_);
         }

         boolean flag = this.m_6933_(p_46626_, fluidstate.m_76188_(), 3, p_46629_);
         if (flag) {
            this.m_220407_(GameEvent.f_157794_, p_46626_, GameEvent.Context.m_223719_(p_46628_, blockstate));
         }

         return flag;
      }
   }

   public void m_142052_(BlockPos p_151531_, BlockState p_151532_) {
   }

   public boolean m_46597_(BlockPos p_46598_, BlockState p_46599_) {
      return this.m_7731_(p_46598_, p_46599_, 3);
   }

   public abstract void m_7260_(BlockPos p_46612_, BlockState p_46613_, BlockState p_46614_, int p_46615_);

   public void m_6550_(BlockPos p_46678_, BlockState p_46679_, BlockState p_46680_) {
   }

   public void m_46672_(BlockPos p_46673_, Block p_46674_) {
      net.minecraftforge.event.ForgeEventFactory.onNeighborNotify(this, p_46673_, this.m_8055_(p_46673_), java.util.EnumSet.allOf(Direction.class), false).isCanceled();
   }

   public void m_46590_(BlockPos p_46591_, Block p_46592_, Direction p_46593_) {
   }

   public void m_46586_(BlockPos p_46587_, Block p_46588_, BlockPos p_46589_) {
   }

   public void m_213960_(BlockState p_220379_, BlockPos p_220380_, Block p_220381_, BlockPos p_220382_, boolean p_220383_) {
   }

   public void m_213683_(Direction p_220385_, BlockState p_220386_, BlockPos p_220387_, BlockPos p_220388_, int p_220389_, int p_220390_) {
      this.f_220350_.m_213547_(p_220385_, p_220386_, p_220387_, p_220388_, p_220389_, p_220390_);
   }

   public int m_6924_(Heightmap.Types p_46571_, int p_46572_, int p_46573_) {
      int i;
      if (p_46572_ >= -30000000 && p_46573_ >= -30000000 && p_46572_ < 30000000 && p_46573_ < 30000000) {
         if (this.m_7232_(SectionPos.m_123171_(p_46572_), SectionPos.m_123171_(p_46573_))) {
            i = this.m_6325_(SectionPos.m_123171_(p_46572_), SectionPos.m_123171_(p_46573_)).m_5885_(p_46571_, p_46572_ & 15, p_46573_ & 15) + 1;
         } else {
            i = this.m_141937_();
         }
      } else {
         i = this.m_5736_() + 1;
      }

      return i;
   }

   public LevelLightEngine m_5518_() {
      return this.m_7726_().m_7827_();
   }

   public BlockState m_8055_(BlockPos p_46732_) {
      if (this.m_151570_(p_46732_)) {
         return Blocks.f_50626_.m_49966_();
      } else {
         LevelChunk levelchunk = this.m_6325_(SectionPos.m_123171_(p_46732_.m_123341_()), SectionPos.m_123171_(p_46732_.m_123343_()));
         return levelchunk.m_8055_(p_46732_);
      }
   }

   public FluidState m_6425_(BlockPos p_46671_) {
      if (this.m_151570_(p_46671_)) {
         return Fluids.f_76191_.m_76145_();
      } else {
         LevelChunk levelchunk = this.m_46745_(p_46671_);
         return levelchunk.m_6425_(p_46671_);
      }
   }

   public boolean m_46461_() {
      return !this.m_6042_().m_63967_() && this.f_46425_ < 4;
   }

   public boolean m_46462_() {
      return !this.m_6042_().m_63967_() && !this.m_46461_();
   }

   public void m_245803_(@Nullable Entity p_252137_, BlockPos p_251749_, SoundEvent p_248842_, SoundSource p_251104_, float p_249531_, float p_250763_) {
      Player player1;
      if (p_252137_ instanceof Player player) {
         player1 = player;
      } else {
         player1 = null;
      }

      this.m_5594_(player1, p_251749_, p_248842_, p_251104_, p_249531_, p_250763_);
   }

   public void m_5594_(@Nullable Player p_46560_, BlockPos p_46561_, SoundEvent p_46562_, SoundSource p_46563_, float p_46564_, float p_46565_) {
      this.m_6263_(p_46560_, (double)p_46561_.m_123341_() + 0.5D, (double)p_46561_.m_123342_() + 0.5D, (double)p_46561_.m_123343_() + 0.5D, p_46562_, p_46563_, p_46564_, p_46565_);
   }

   public abstract void m_262808_(@Nullable Player p_262953_, double p_263004_, double p_263398_, double p_263376_, Holder<SoundEvent> p_263359_, SoundSource p_263020_, float p_263055_, float p_262914_, long p_262991_);

   public void m_214150_(@Nullable Player p_220363_, double p_220364_, double p_220365_, double p_220366_, SoundEvent p_220367_, SoundSource p_220368_, float p_220369_, float p_220370_, long p_220371_) {
      this.m_262808_(p_220363_, p_220364_, p_220365_, p_220366_, BuiltInRegistries.f_256894_.m_263177_(p_220367_), p_220368_, p_220369_, p_220370_, p_220371_);
   }

   public abstract void m_213890_(@Nullable Player p_220372_, Entity p_220373_, Holder<SoundEvent> p_263500_, SoundSource p_220375_, float p_220376_, float p_220377_, long p_220378_);

   public void m_6263_(@Nullable Player p_46543_, double p_46544_, double p_46545_, double p_46546_, SoundEvent p_46547_, SoundSource p_46548_, float p_46549_, float p_46550_) {
      this.m_214150_(p_46543_, p_46544_, p_46545_, p_46546_, p_46547_, p_46548_, p_46549_, p_46550_, this.f_220348_.m_188505_());
   }

   public void m_6269_(@Nullable Player p_46551_, Entity p_46552_, SoundEvent p_46553_, SoundSource p_46554_, float p_46555_, float p_46556_) {
      this.m_213890_(p_46551_, p_46552_, BuiltInRegistries.f_256894_.m_263177_(p_46553_), p_46554_, p_46555_, p_46556_, this.f_220348_.m_188505_());
   }

   public void m_245747_(BlockPos p_250938_, SoundEvent p_252209_, SoundSource p_249161_, float p_249980_, float p_250277_, boolean p_250151_) {
      this.m_7785_((double)p_250938_.m_123341_() + 0.5D, (double)p_250938_.m_123342_() + 0.5D, (double)p_250938_.m_123343_() + 0.5D, p_252209_, p_249161_, p_249980_, p_250277_, p_250151_);
   }

   public void m_7785_(double p_46482_, double p_46483_, double p_46484_, SoundEvent p_46485_, SoundSource p_46486_, float p_46487_, float p_46488_, boolean p_46489_) {
   }

   public void m_7106_(ParticleOptions p_46631_, double p_46632_, double p_46633_, double p_46634_, double p_46635_, double p_46636_, double p_46637_) {
   }

   public void m_6493_(ParticleOptions p_46638_, boolean p_46639_, double p_46640_, double p_46641_, double p_46642_, double p_46643_, double p_46644_, double p_46645_) {
   }

   public void m_7107_(ParticleOptions p_46684_, double p_46685_, double p_46686_, double p_46687_, double p_46688_, double p_46689_, double p_46690_) {
   }

   public void m_6485_(ParticleOptions p_46691_, boolean p_46692_, double p_46693_, double p_46694_, double p_46695_, double p_46696_, double p_46697_, double p_46698_) {
   }

   public float m_46490_(float p_46491_) {
      float f = this.m_46942_(p_46491_);
      return f * ((float)Math.PI * 2F);
   }

   public void m_151525_(TickingBlockEntity p_151526_) {
      (this.f_151504_ ? this.f_151503_ : this.f_151512_).add(p_151526_);
   }

   public void addFreshBlockEntities(java.util.Collection<BlockEntity> beList) {
      if (this.f_151504_) {
         this.pendingFreshBlockEntities.addAll(beList);
      } else {
         this.freshBlockEntities.addAll(beList);
      }
   }

   protected void m_46463_() {
      ProfilerFiller profilerfiller = this.m_46473_();
      profilerfiller.m_6180_("blockEntities");
      if (!this.pendingFreshBlockEntities.isEmpty()) {
         this.freshBlockEntities.addAll(this.pendingFreshBlockEntities);
         this.pendingFreshBlockEntities.clear();
      }
      this.f_151504_ = true;
      if (!this.freshBlockEntities.isEmpty()) {
         this.freshBlockEntities.forEach(BlockEntity::onLoad);
         this.freshBlockEntities.clear();
      }
      if (!this.f_151503_.isEmpty()) {
         this.f_151512_.addAll(this.f_151503_);
         this.f_151503_.clear();
      }

      Iterator<TickingBlockEntity> iterator = this.f_151512_.iterator();

      while(iterator.hasNext()) {
         TickingBlockEntity tickingblockentity = iterator.next();
         if (tickingblockentity.m_142220_()) {
            iterator.remove();
         } else if (this.m_220393_(tickingblockentity.m_142689_())) {
            tickingblockentity.m_142224_();
         }
      }

      this.f_151504_ = false;
      profilerfiller.m_7238_();
   }

   public <T extends Entity> void m_46653_(Consumer<T> p_46654_, T p_46655_) {
      try {
         net.minecraftforge.server.timings.TimeTracker.ENTITY_UPDATE.trackStart(p_46655_);
         p_46654_.accept(p_46655_);
      } catch (Throwable throwable) {
         CrashReport crashreport = CrashReport.m_127521_(throwable, "Ticking entity");
         CrashReportCategory crashreportcategory = crashreport.m_127514_("Entity being ticked");
         p_46655_.m_7976_(crashreportcategory);
         if (net.minecraftforge.common.ForgeConfig.SERVER.removeErroringEntities.get()) {
            com.mojang.logging.LogUtils.getLogger().error("{}", crashreport.m_127526_());
            p_46655_.m_146870_();
         } else
         throw new ReportedException(crashreport);
      } finally {
         net.minecraftforge.server.timings.TimeTracker.ENTITY_UPDATE.trackEnd(p_46655_);
      }
   }

   public boolean m_183599_(Entity p_186458_) {
      return true;
   }

   public boolean m_183438_(long p_186456_) {
      return true;
   }

   public boolean m_220393_(BlockPos p_220394_) {
      return this.m_183438_(ChunkPos.m_151388_(p_220394_));
   }

   public Explosion m_254849_(@Nullable Entity p_256599_, double p_255914_, double p_255684_, double p_255843_, float p_256310_, Level.ExplosionInteraction p_256178_) {
      return this.m_254877_(p_256599_, (DamageSource)null, (ExplosionDamageCalculator)null, p_255914_, p_255684_, p_255843_, p_256310_, false, p_256178_);
   }

   public Explosion m_255391_(@Nullable Entity p_255682_, double p_255803_, double p_256403_, double p_256538_, float p_255674_, boolean p_256634_, Level.ExplosionInteraction p_256111_) {
      return this.m_254877_(p_255682_, (DamageSource)null, (ExplosionDamageCalculator)null, p_255803_, p_256403_, p_256538_, p_255674_, p_256634_, p_256111_);
   }

   public Explosion m_254951_(@Nullable Entity p_255653_, @Nullable DamageSource p_256558_, @Nullable ExplosionDamageCalculator p_255929_, Vec3 p_256001_, float p_255963_, boolean p_256099_, Level.ExplosionInteraction p_256371_) {
      return this.m_254877_(p_255653_, p_256558_, p_255929_, p_256001_.m_7096_(), p_256001_.m_7098_(), p_256001_.m_7094_(), p_255963_, p_256099_, p_256371_);
   }

   public Explosion m_254877_(@Nullable Entity p_256145_, @Nullable DamageSource p_256004_, @Nullable ExplosionDamageCalculator p_255696_, double p_256208_, double p_256036_, double p_255746_, float p_256647_, boolean p_256098_, Level.ExplosionInteraction p_256104_) {
      return this.m_255278_(p_256145_, p_256004_, p_255696_, p_256208_, p_256036_, p_255746_, p_256647_, p_256098_, p_256104_, true);
   }

   public Explosion m_255278_(@Nullable Entity p_256233_, @Nullable DamageSource p_255861_, @Nullable ExplosionDamageCalculator p_255867_, double p_256447_, double p_255732_, double p_255717_, float p_256013_, boolean p_256228_, Level.ExplosionInteraction p_255784_, boolean p_256377_) {
      Explosion.BlockInteraction explosion$blockinteraction1;
      switch (p_255784_) {
         case NONE:
            explosion$blockinteraction1 = Explosion.BlockInteraction.KEEP;
            break;
         case BLOCK:
            explosion$blockinteraction1 = this.m_255157_(GameRules.f_254629_);
            break;
         case MOB:
            explosion$blockinteraction1 = net.minecraftforge.event.ForgeEventFactory.getMobGriefingEvent(this, p_256233_) ? this.m_255157_(GameRules.f_254692_) : Explosion.BlockInteraction.KEEP;
            break;
         case TNT:
            explosion$blockinteraction1 = this.m_255157_(GameRules.f_254705_);
            break;
         default:
            throw new IncompatibleClassChangeError();
      }

      Explosion.BlockInteraction explosion$blockinteraction = explosion$blockinteraction1;
      Explosion explosion = new Explosion(this, p_256233_, p_255861_, p_255867_, p_256447_, p_255732_, p_255717_, p_256013_, p_256228_, explosion$blockinteraction);
      if (net.minecraftforge.event.ForgeEventFactory.onExplosionStart(this, explosion)) return explosion;
      explosion.m_46061_();
      explosion.m_46075_(p_256377_);
      return explosion;
   }

   private Explosion.BlockInteraction m_255157_(GameRules.Key<GameRules.BooleanValue> p_256250_) {
      return this.m_46469_().m_46207_(p_256250_) ? Explosion.BlockInteraction.DESTROY_WITH_DECAY : Explosion.BlockInteraction.DESTROY;
   }

   public abstract String m_46464_();

   @Nullable
   public BlockEntity m_7702_(BlockPos p_46716_) {
      if (this.m_151570_(p_46716_)) {
         return null;
      } else {
         return !this.f_46443_ && Thread.currentThread() != this.f_46423_ ? null : this.m_46745_(p_46716_).m_5685_(p_46716_, LevelChunk.EntityCreationType.IMMEDIATE);
      }
   }

   public void m_151523_(BlockEntity p_151524_) {
      BlockPos blockpos = p_151524_.m_58899_();
      if (!this.m_151570_(blockpos)) {
         this.m_46745_(blockpos).m_142170_(p_151524_);
      }
   }

   public void m_46747_(BlockPos p_46748_) {
      if (!this.m_151570_(p_46748_)) {
         this.m_46745_(p_46748_).m_8114_(p_46748_);
      }
      this.m_46717_(p_46748_, m_8055_(p_46748_).m_60734_()); //Notify neighbors of changes
   }

   public boolean m_46749_(BlockPos p_46750_) {
      return this.m_151570_(p_46750_) ? false : this.m_7726_().m_5563_(SectionPos.m_123171_(p_46750_.m_123341_()), SectionPos.m_123171_(p_46750_.m_123343_()));
   }

   public boolean m_46578_(BlockPos p_46579_, Entity p_46580_, Direction p_46581_) {
      if (this.m_151570_(p_46579_)) {
         return false;
      } else {
         ChunkAccess chunkaccess = this.m_6522_(SectionPos.m_123171_(p_46579_.m_123341_()), SectionPos.m_123171_(p_46579_.m_123343_()), ChunkStatus.f_62326_, false);
         return chunkaccess == null ? false : chunkaccess.m_8055_(p_46579_).m_60638_(this, p_46579_, p_46580_, p_46581_);
      }
   }

   public boolean m_46575_(BlockPos p_46576_, Entity p_46577_) {
      return this.m_46578_(p_46576_, p_46577_, Direction.UP);
   }

   public void m_46465_() {
      double d0 = 1.0D - (double)(this.m_46722_(1.0F) * 5.0F) / 16.0D;
      double d1 = 1.0D - (double)(this.m_46661_(1.0F) * 5.0F) / 16.0D;
      double d2 = 0.5D + 2.0D * Mth.m_14008_((double)Mth.m_14089_(this.m_46942_(1.0F) * ((float)Math.PI * 2F)), -0.25D, 0.25D);
      this.f_46425_ = (int)((1.0D - d2 * d0 * d1) * 11.0D);
   }

   public void m_46703_(boolean p_46704_, boolean p_46705_) {
      this.m_7726_().m_6707_(p_46704_, p_46705_);
   }

   public BlockPos m_220360_() {
      BlockPos blockpos = new BlockPos(this.f_46442_.m_6789_(), this.f_46442_.m_6527_(), this.f_46442_.m_6526_());
      if (!this.m_6857_().m_61937_(blockpos)) {
         blockpos = this.m_5452_(Heightmap.Types.MOTION_BLOCKING, BlockPos.m_274561_(this.m_6857_().m_6347_(), 0.0D, this.m_6857_().m_6345_()));
      }

      return blockpos;
   }

   public float m_220361_() {
      return this.f_46442_.m_6790_();
   }

   protected void m_46466_() {
      if (this.f_46442_.m_6533_()) {
         this.f_46438_ = 1.0F;
         if (this.f_46442_.m_6534_()) {
            this.f_46440_ = 1.0F;
         }
      }

   }

   public void close() throws IOException {
      this.m_7726_().close();
   }

   @Nullable
   public BlockGetter m_7925_(int p_46711_, int p_46712_) {
      return this.m_6522_(p_46711_, p_46712_, ChunkStatus.f_62326_, false);
   }

   public List<Entity> m_6249_(@Nullable Entity p_46536_, AABB p_46537_, Predicate<? super Entity> p_46538_) {
      this.m_46473_().m_6174_("getEntities");
      List<Entity> list = Lists.newArrayList();
      this.m_142646_().m_142232_(p_46537_, (p_151522_) -> {
         if (p_151522_ != p_46536_ && p_46538_.test(p_151522_)) {
            list.add(p_151522_);
         }

         if (false)
         if (p_151522_ instanceof EnderDragon) {
            for(EnderDragonPart enderdragonpart : ((EnderDragon)p_151522_).m_31156_()) {
               if (p_151522_ != p_46536_ && p_46538_.test(enderdragonpart)) {
                  list.add(enderdragonpart);
               }
            }
         }

      });
      for (net.minecraftforge.entity.PartEntity<?> p : this.getPartEntities()) {
         if (p != p_46536_ && p.m_20191_().m_82381_(p_46537_) && p_46538_.test(p)) {
            list.add(p);
         }
      }
      return list;
   }

   public <T extends Entity> List<T> m_142425_(EntityTypeTest<Entity, T> p_151528_, AABB p_151529_, Predicate<? super T> p_151530_) {
      List<T> list = Lists.newArrayList();
      this.m_261153_(p_151528_, p_151529_, p_151530_, list);
      return list;
   }

   public <T extends Entity> void m_261153_(EntityTypeTest<Entity, T> p_261899_, AABB p_261837_, Predicate<? super T> p_261519_, List<? super T> p_262046_) {
      this.m_260826_(p_261899_, p_261837_, p_261519_, p_262046_, Integer.MAX_VALUE);
   }

   public <T extends Entity> void m_260826_(EntityTypeTest<Entity, T> p_261885_, AABB p_262086_, Predicate<? super T> p_261688_, List<? super T> p_262071_, int p_261858_) {
      this.m_46473_().m_6174_("getEntities");
      this.m_142646_().m_142137_(p_261885_, p_262086_, (p_261454_) -> {
         if (p_261688_.test(p_261454_)) {
            p_262071_.add(p_261454_);
            if (p_262071_.size() >= p_261858_) {
               return AbortableIterationConsumer.Continuation.ABORT;
            }
         }


         if (false)
         if (p_261454_ instanceof EnderDragon enderdragon) {
            for(EnderDragonPart enderdragonpart : enderdragon.m_31156_()) {
               T t = p_261885_.m_141992_(enderdragonpart);
               if (t != null && p_261688_.test(t)) {
                  p_262071_.add(t);
                  if (p_262071_.size() >= p_261858_) {
                     return AbortableIterationConsumer.Continuation.ABORT;
                  }
               }
            }
         }

         return AbortableIterationConsumer.Continuation.CONTINUE;
      });
      for (net.minecraftforge.entity.PartEntity<?> p : this.getPartEntities()) {
         T t = p_261885_.m_141992_(p);
         if (t != null && t.m_20191_().m_82381_(p_262086_) && p_261688_.test(t)) {
            p_262071_.add(t);
            if (p_262071_.size() >= p_261858_) {
               break;
            }
         }
      }
   }

   @Nullable
   public abstract Entity m_6815_(int p_46492_);

   public void m_151543_(BlockPos p_151544_) {
      if (this.m_46805_(p_151544_)) {
         this.m_46745_(p_151544_).m_8092_(true);
      }

   }

   public int m_5736_() {
      return 63;
   }

   public void m_7462_() {
   }

   public long m_46467_() {
      return this.f_46442_.m_6793_();
   }

   public long m_46468_() {
      return this.f_46442_.m_6792_();
   }

   public boolean m_7966_(Player p_46557_, BlockPos p_46558_) {
      return true;
   }

   public void m_7605_(Entity p_46509_, byte p_46510_) {
   }

   public void m_269196_(Entity p_270831_, DamageSource p_270361_) {
   }

   public void m_7696_(BlockPos p_46582_, Block p_46583_, int p_46584_, int p_46585_) {
      this.m_8055_(p_46582_).m_60677_(this, p_46582_, p_46584_, p_46585_);
   }

   public LevelData m_6106_() {
      return this.f_46442_;
   }

   public GameRules m_46469_() {
      return this.f_46442_.m_5470_();
   }

   public float m_46661_(float p_46662_) {
      return Mth.m_14179_(p_46662_, this.f_46439_, this.f_46440_) * this.m_46722_(p_46662_);
   }

   public void m_46707_(float p_46708_) {
      float f = Mth.m_14036_(p_46708_, 0.0F, 1.0F);
      this.f_46439_ = f;
      this.f_46440_ = f;
   }

   public float m_46722_(float p_46723_) {
      return Mth.m_14179_(p_46723_, this.f_46437_, this.f_46438_);
   }

   public void m_46734_(float p_46735_) {
      float f = Mth.m_14036_(p_46735_, 0.0F, 1.0F);
      this.f_46437_ = f;
      this.f_46438_ = f;
   }

   public boolean m_46470_() {
      if (this.m_6042_().f_223549_() && !this.m_6042_().f_63856_()) {
         return (double)this.m_46661_(1.0F) > 0.9D;
      } else {
         return false;
      }
   }

   public boolean m_46471_() {
      return (double)this.m_46722_(1.0F) > 0.2D;
   }

   public boolean m_46758_(BlockPos p_46759_) {
      if (!this.m_46471_()) {
         return false;
      } else if (!this.m_45527_(p_46759_)) {
         return false;
      } else if (this.m_5452_(Heightmap.Types.MOTION_BLOCKING, p_46759_).m_123342_() > p_46759_.m_123342_()) {
         return false;
      } else {
         Biome biome = this.m_204166_(p_46759_).m_203334_();
         return biome.m_264600_(p_46759_) == Biome.Precipitation.RAIN;
      }
   }

   @Nullable
   public abstract MapItemSavedData m_7489_(String p_46650_);

   public abstract void m_142325_(String p_151533_, MapItemSavedData p_151534_);

   public abstract int m_7354_();

   public void m_6798_(int p_46665_, BlockPos p_46666_, int p_46667_) {
   }

   public CrashReportCategory m_6026_(CrashReport p_46656_) {
      CrashReportCategory crashreportcategory = p_46656_.m_127516_("Affected level", 1);
      crashreportcategory.m_128165_("All players", () -> {
         return this.m_6907_().size() + " total; " + this.m_6907_();
      });
      crashreportcategory.m_128165_("Chunk stats", this.m_7726_()::m_6754_);
      crashreportcategory.m_128165_("Level dimension", () -> {
         return this.m_46472_().m_135782_().toString();
      });

      try {
         this.f_46442_.m_142471_(crashreportcategory, this);
      } catch (Throwable throwable) {
         crashreportcategory.m_128162_("Level Data Unobtainable", throwable);
      }

      return crashreportcategory;
   }

   public abstract void m_6801_(int p_46506_, BlockPos p_46507_, int p_46508_);

   public void m_7228_(double p_46475_, double p_46476_, double p_46477_, double p_46478_, double p_46479_, double p_46480_, @Nullable CompoundTag p_46481_) {
   }

   public abstract Scoreboard m_6188_();

   public void m_46717_(BlockPos p_46718_, Block p_46719_) {
      for(Direction direction : Direction.values()) {
         BlockPos blockpos = p_46718_.m_121945_(direction);
         if (this.m_46805_(blockpos)) {
            BlockState blockstate = this.m_8055_(blockpos);
            blockstate.onNeighborChange(this, blockpos, p_46718_);
            if (blockstate.m_60796_(this, blockpos)) {
               blockpos = blockpos.m_121945_(direction);
               blockstate = this.m_8055_(blockpos);
               if (blockstate.getWeakChanges(this, blockpos)) {
                  this.m_213960_(blockstate, blockpos, p_46719_, p_46718_, false);
               }
            }
         }
      }

   }

   public DifficultyInstance m_6436_(BlockPos p_46730_) {
      long i = 0L;
      float f = 0.0F;
      if (this.m_46805_(p_46730_)) {
         f = this.m_46940_();
         i = this.m_46745_(p_46730_).m_6319_();
      }

      return new DifficultyInstance(this.m_46791_(), this.m_46468_(), i, f);
   }

   public int m_7445_() {
      return this.f_46425_;
   }

   public void m_6580_(int p_46709_) {
   }

   public WorldBorder m_6857_() {
      return this.f_46447_;
   }

   public void m_5503_(Packet<?> p_46657_) {
      throw new UnsupportedOperationException("Can't send packets to server unless you're on the client.");
   }

   public DimensionType m_6042_() {
      return this.f_204147_.m_203334_();
   }

   public ResourceKey<DimensionType> m_220362_() {
      return this.f_220349_;
   }

   public Holder<DimensionType> m_204156_() {
      return this.f_204147_;
   }

   public ResourceKey<Level> m_46472_() {
      return this.f_46421_;
   }

   public RandomSource m_213780_() {
      return this.f_46441_;
   }

   public boolean m_7433_(BlockPos p_46620_, Predicate<BlockState> p_46621_) {
      return p_46621_.test(this.m_8055_(p_46620_));
   }

   public boolean m_142433_(BlockPos p_151541_, Predicate<FluidState> p_151542_) {
      return p_151542_.test(this.m_6425_(p_151541_));
   }

   public abstract RecipeManager m_7465_();

   public BlockPos m_46496_(int p_46497_, int p_46498_, int p_46499_, int p_46500_) {
      this.f_46435_ = this.f_46435_ * 3 + 1013904223;
      int i = this.f_46435_ >> 2;
      return new BlockPos(p_46497_ + (i & 15), p_46498_ + (i >> 16 & p_46500_), p_46499_ + (i >> 8 & 15));
   }

   public boolean m_7441_() {
      return false;
   }

   public ProfilerFiller m_46473_() {
      return this.f_46446_.get();
   }

   public Supplier<ProfilerFiller> m_46658_() {
      return this.f_46446_;
   }

   public BiomeManager m_7062_() {
      return this.f_46420_;
   }

   private double maxEntityRadius = 2.0D;
   @Override
   public double getMaxEntityRadius() {
      return maxEntityRadius;
   }
   @Override
   public double increaseMaxEntityRadius(double value) {
      if (value > maxEntityRadius)
         maxEntityRadius = value;
      return maxEntityRadius;
   }

   public final boolean m_46659_() {
      return this.f_46424_;
   }

   protected abstract LevelEntityGetter<Entity> m_142646_();

   public long m_183596_() {
      return (long)(this.f_186455_++);
   }

   public RegistryAccess m_9598_() {
      return this.f_268710_;
   }

   public DamageSources m_269111_() {
      return this.f_268497_;
   }

   public static enum ExplosionInteraction {
      NONE,
      BLOCK,
      MOB,
      TNT;
   }
}
