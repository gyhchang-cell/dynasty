package net.minecraft.client.multiplayer;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Maps;
import com.google.common.collect.Queues;
import com.mojang.logging.LogUtils;
import it.unimi.dsi.fastutil.objects.Object2ObjectArrayMap;
import java.util.Deque;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.BooleanSupplier;
import java.util.function.Supplier;
import javax.annotation.Nullable;
import net.minecraft.CrashReport;
import net.minecraft.CrashReportCategory;
import net.minecraft.ReportedException;
import net.minecraft.Util;
import net.minecraft.client.Minecraft;
import net.minecraft.client.color.block.BlockTintCache;
import net.minecraft.client.multiplayer.prediction.BlockStatePredictionHandler;
import net.minecraft.client.particle.FireworkParticles;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.BiomeColors;
import net.minecraft.client.renderer.DimensionSpecialEffects;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.resources.sounds.EntityBoundSoundInstance;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Cursor3D;
import net.minecraft.core.Direction;
import net.minecraft.core.Holder;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.Packet;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.MinecraftServer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.CubicSampler;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.flag.FeatureFlagSet;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.RecipeManager;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.ColorResolver;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelHeightAccessor;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.BiomeManager;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.chunk.LevelChunk;
import net.minecraft.world.level.dimension.DimensionType;
import net.minecraft.world.level.entity.EntityTickList;
import net.minecraft.world.level.entity.LevelCallback;
import net.minecraft.world.level.entity.LevelEntityGetter;
import net.minecraft.world.level.entity.TransientEntitySectionManager;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.level.saveddata.maps.MapItemSavedData;
import net.minecraft.world.level.storage.WritableLevelData;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.minecraft.world.scores.Scoreboard;
import net.minecraft.world.ticks.BlackholeTickAccess;
import net.minecraft.world.ticks.LevelTickAccess;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.slf4j.Logger;

@OnlyIn(Dist.CLIENT)
public class ClientLevel extends Level {
   private static final Logger f_233600_ = LogUtils.getLogger();
   private static final double f_171629_ = 0.05D;
   private static final int f_194125_ = 10;
   private static final int f_194126_ = 1000;
   final EntityTickList f_171630_ = new EntityTickList();
   private final TransientEntitySectionManager<Entity> f_171631_ = new TransientEntitySectionManager<>(Entity.class, new ClientLevel.EntityCallbacks());
   private final ClientPacketListener f_104561_;
   private final LevelRenderer f_104562_;
   private final ClientLevel.ClientLevelData f_104563_;
   private final DimensionSpecialEffects f_104564_;
   private final Minecraft f_104565_ = Minecraft.m_91087_();
   final List<AbstractClientPlayer> f_104566_ = Lists.newArrayList();
   private Scoreboard f_104555_ = new Scoreboard();
   private final Map<String, MapItemSavedData> f_104556_ = Maps.newHashMap();
   private static final long f_171628_ = 16777215L;
   private int f_104557_;
   private final Object2ObjectArrayMap<ColorResolver, BlockTintCache> f_104558_ = Util.m_137469_(new Object2ObjectArrayMap<>(3), (p_194170_) -> {
      p_194170_.put(BiomeColors.f_108789_, new BlockTintCache((p_194181_) -> {
         return this.m_104762_(p_194181_, BiomeColors.f_108789_);
      }));
      p_194170_.put(BiomeColors.f_108790_, new BlockTintCache((p_194177_) -> {
         return this.m_104762_(p_194177_, BiomeColors.f_108790_);
      }));
      p_194170_.put(BiomeColors.f_108791_, new BlockTintCache((p_194168_) -> {
         return this.m_104762_(p_194168_, BiomeColors.f_108791_);
      }));
   });
   private final ClientChunkCache f_104559_;
   private final Deque<Runnable> f_194122_ = Queues.newArrayDeque();
   private int f_194123_;
   private final BlockStatePredictionHandler f_233599_ = new BlockStatePredictionHandler();
   private static final Set<Item> f_194124_ = Set.of(Items.f_42127_, Items.f_151033_);

   public void m_233651_(int p_233652_) {
      this.f_233599_.m_233856_(p_233652_, this);
   }

   public void m_233653_(BlockPos p_233654_, BlockState p_233655_, int p_233656_) {
      if (!this.f_233599_.m_233864_(p_233654_, p_233655_)) {
         super.m_6933_(p_233654_, p_233655_, p_233656_, 512);
      }

   }

   public void m_233647_(BlockPos p_233648_, BlockState p_233649_, Vec3 p_233650_) {
      BlockState blockstate = this.m_8055_(p_233648_);
      if (blockstate != p_233649_) {
         this.m_7731_(p_233648_, p_233649_, 19);
         Player player = this.f_104565_.f_91074_;
         if (this == player.m_9236_() && player.m_20039_(p_233648_, p_233649_)) {
            player.m_20248_(p_233650_.f_82479_, p_233650_.f_82480_, p_233650_.f_82481_);
         }
      }

   }

   BlockStatePredictionHandler m_233601_() {
      return this.f_233599_;
   }

   public boolean m_6933_(BlockPos p_233643_, BlockState p_233644_, int p_233645_, int p_233646_) {
      if (this.f_233599_.m_233872_()) {
         BlockState blockstate = this.m_8055_(p_233643_);
         boolean flag = super.m_6933_(p_233643_, p_233644_, p_233645_, p_233646_);
         if (flag) {
            this.f_233599_.m_233867_(p_233643_, blockstate, this.f_104565_.f_91074_);
         }

         return flag;
      } else {
         return super.m_6933_(p_233643_, p_233644_, p_233645_, p_233646_);
      }
   }

   public ClientLevel(ClientPacketListener p_205505_, ClientLevel.ClientLevelData p_205506_, ResourceKey<Level> p_205507_, Holder<DimensionType> p_205508_, int p_205509_, int p_205510_, Supplier<ProfilerFiller> p_205511_, LevelRenderer p_205512_, boolean p_205513_, long p_205514_) {
      super(p_205506_, p_205507_, p_205505_.m_105152_(), p_205508_, p_205511_, true, p_205513_, p_205514_, 1000000);
      this.f_104561_ = p_205505_;
      this.f_104559_ = new ClientChunkCache(this, p_205509_);
      this.f_104563_ = p_205506_;
      this.f_104562_ = p_205512_;
      this.f_104564_ = DimensionSpecialEffects.m_108876_(p_205508_.m_203334_());
      this.m_104752_(new BlockPos(8, 64, 8), 0.0F);
      this.f_194123_ = p_205510_;
      this.m_46465_();
      this.m_46466_();
   }

   public void m_194171_(Runnable p_194172_) {
      this.f_194122_.add(p_194172_);
   }

   public void m_194141_() {
      int i = this.f_194122_.size();
      int j = i < 1000 ? Math.max(10, i / 10) : i;

      for(int k = 0; k < j; ++k) {
         Runnable runnable = this.f_194122_.poll();
         if (runnable == null) {
            break;
         }

         runnable.run();
      }

   }

   public boolean m_194173_() {
      return this.f_194122_.isEmpty();
   }

   public DimensionSpecialEffects m_104583_() {
      return this.f_104564_;
   }

   public void m_104726_(BooleanSupplier p_104727_) {
      this.m_6857_().m_61969_();
      this.m_104826_();
      if (this.f_104557_ > 0) {
         this.m_6580_(this.f_104557_ - 1);
      }

      this.m_46473_().m_6180_("blocks");
      this.f_104559_.m_201698_(p_104727_, true);
      this.m_46473_().m_7238_();
   }

   private void m_104826_() {
      this.m_104637_(this.f_46442_.m_6793_() + 1L);
      if (this.f_46442_.m_5470_().m_46207_(GameRules.f_46140_)) {
         this.m_104746_(this.f_46442_.m_6792_() + 1L);
      }

   }

   public void m_104637_(long p_104638_) {
      this.f_104563_.m_104849_(p_104638_);
   }

   public void m_104746_(long p_104747_) {
      if (p_104747_ < 0L) {
         p_104747_ = -p_104747_;
         this.m_46469_().m_46170_(GameRules.f_46140_).m_46246_(false, (MinecraftServer)null);
      } else {
         this.m_46469_().m_46170_(GameRules.f_46140_).m_46246_(true, (MinecraftServer)null);
      }

      this.f_104563_.m_104863_(p_104747_);
   }

   public Iterable<Entity> m_104735_() {
      return this.m_142646_().m_142273_();
   }

   public void m_104804_() {
      ProfilerFiller profilerfiller = this.m_46473_();
      profilerfiller.m_6180_("entities");
      this.f_171630_.m_156910_((p_194183_) -> {
         if (!p_194183_.m_213877_() && !p_194183_.m_20159_()) {
            this.m_46653_(this::m_104639_, p_194183_);
         }
      });
      profilerfiller.m_7238_();
      this.m_46463_();
   }

   public boolean m_183599_(Entity p_194185_) {
      return p_194185_.m_146902_().m_45594_(this.f_104565_.f_91074_.m_146902_()) <= this.f_194123_;
   }

   public void m_104639_(Entity p_104640_) {
      p_104640_.m_146867_();
      ++p_104640_.f_19797_;
      this.m_46473_().m_6521_(() -> {
         return BuiltInRegistries.f_256780_.m_7981_(p_104640_.m_6095_()).toString();
      });
      p_104640_.m_8119_();
      this.m_46473_().m_7238_();

      for(Entity entity : p_104640_.m_20197_()) {
         this.m_104641_(p_104640_, entity);
      }

   }

   private void m_104641_(Entity p_104642_, Entity p_104643_) {
      if (!p_104643_.m_213877_() && p_104643_.m_20202_() == p_104642_) {
         if (p_104643_ instanceof Player || this.f_171630_.m_156914_(p_104643_)) {
            p_104643_.m_146867_();
            ++p_104643_.f_19797_;
            p_104643_.m_6083_();

            for(Entity entity : p_104643_.m_20197_()) {
               this.m_104641_(p_104643_, entity);
            }

         }
      } else {
         p_104643_.m_8127_();
      }
   }

   public void m_104665_(LevelChunk p_104666_) {
      p_104666_.m_187957_();
      this.f_104559_.m_7827_().m_9335_(p_104666_.m_7697_(), false);
      this.f_171631_.m_157658_(p_104666_.m_7697_());
   }

   public void m_171649_(ChunkPos p_171650_) {
      this.f_104558_.forEach((p_194154_, p_194155_) -> {
         p_194155_.m_92655_(p_171650_.f_45578_, p_171650_.f_45579_);
      });
      this.f_171631_.m_157651_(p_171650_);
   }

   public void m_104810_() {
      this.f_104558_.forEach((p_194157_, p_194158_) -> {
         p_194158_.m_92654_();
      });
   }

   public boolean m_7232_(int p_104737_, int p_104738_) {
      return true;
   }

   public int m_104813_() {
      return this.f_171631_.m_157657_();
   }

   public void m_104630_(int p_104631_, AbstractClientPlayer p_104632_) {
      this.m_104739_(p_104631_, p_104632_);
   }

   public void m_104627_(int p_104628_, Entity p_104629_) {
      this.m_104739_(p_104628_, p_104629_);
   }

   private void m_104739_(int p_104740_, Entity p_104741_) {
      this.m_171642_(p_104740_, Entity.RemovalReason.DISCARDED);
      this.f_171631_.m_157653_(p_104741_);
   }

   public void m_171642_(int p_171643_, Entity.RemovalReason p_171644_) {
      Entity entity = this.m_142646_().m_142597_(p_171643_);
      if (entity != null) {
         entity.m_142467_(p_171644_);
         entity.m_142036_();
      }

   }

   @Nullable
   public Entity m_6815_(int p_104609_) {
      return this.m_142646_().m_142597_(p_104609_);
   }

   public void m_7462_() {
      this.f_104561_.m_104910_().m_129507_(Component.m_237115_("multiplayer.status.quitting"));
   }

   public void m_104784_(int p_104785_, int p_104786_, int p_104787_) {
      int i = 32;
      RandomSource randomsource = RandomSource.m_216327_();
      Block block = this.m_194187_();
      BlockPos.MutableBlockPos blockpos$mutableblockpos = new BlockPos.MutableBlockPos();

      for(int j = 0; j < 667; ++j) {
         this.m_233612_(p_104785_, p_104786_, p_104787_, 16, randomsource, block, blockpos$mutableblockpos);
         this.m_233612_(p_104785_, p_104786_, p_104787_, 32, randomsource, block, blockpos$mutableblockpos);
      }

   }

   @Nullable
   private Block m_194187_() {
      if (this.f_104565_.f_91072_.m_105295_() == GameType.CREATIVE) {
         ItemStack itemstack = this.f_104565_.f_91074_.m_21205_();
         Item item = itemstack.m_41720_();
         if (f_194124_.contains(item) && item instanceof BlockItem) {
            BlockItem blockitem = (BlockItem)item;
            return blockitem.m_40614_();
         }
      }

      return null;
   }

   public void m_233612_(int p_233613_, int p_233614_, int p_233615_, int p_233616_, RandomSource p_233617_, @Nullable Block p_233618_, BlockPos.MutableBlockPos p_233619_) {
      int i = p_233613_ + this.f_46441_.m_188503_(p_233616_) - this.f_46441_.m_188503_(p_233616_);
      int j = p_233614_ + this.f_46441_.m_188503_(p_233616_) - this.f_46441_.m_188503_(p_233616_);
      int k = p_233615_ + this.f_46441_.m_188503_(p_233616_) - this.f_46441_.m_188503_(p_233616_);
      p_233619_.m_122178_(i, j, k);
      BlockState blockstate = this.m_8055_(p_233619_);
      blockstate.m_60734_().m_214162_(blockstate, this, p_233619_, p_233617_);
      FluidState fluidstate = this.m_6425_(p_233619_);
      if (!fluidstate.m_76178_()) {
         fluidstate.m_230558_(this, p_233619_, p_233617_);
         ParticleOptions particleoptions = fluidstate.m_76189_();
         if (particleoptions != null && this.f_46441_.m_188503_(10) == 0) {
            boolean flag = blockstate.m_60783_(this, p_233619_, Direction.DOWN);
            BlockPos blockpos = p_233619_.m_7495_();
            this.m_104689_(blockpos, this.m_8055_(blockpos), particleoptions, flag);
         }
      }

      if (p_233618_ == blockstate.m_60734_()) {
         this.m_7106_(new BlockParticleOption(ParticleTypes.f_194652_, blockstate), (double)i + 0.5D, (double)j + 0.5D, (double)k + 0.5D, 0.0D, 0.0D, 0.0D);
      }

      if (!blockstate.m_60838_(this, p_233619_)) {
         this.m_204166_(p_233619_).m_203334_().m_47562_().ifPresent((p_264703_) -> {
            if (p_264703_.m_220527_(this.f_46441_)) {
               this.m_7106_(p_264703_.m_47419_(), (double)p_233619_.m_123341_() + this.f_46441_.m_188500_(), (double)p_233619_.m_123342_() + this.f_46441_.m_188500_(), (double)p_233619_.m_123343_() + this.f_46441_.m_188500_(), 0.0D, 0.0D, 0.0D);
            }

         });
      }

   }

   private void m_104689_(BlockPos p_104690_, BlockState p_104691_, ParticleOptions p_104692_, boolean p_104693_) {
      if (p_104691_.m_60819_().m_76178_()) {
         VoxelShape voxelshape = p_104691_.m_60812_(this, p_104690_);
         double d0 = voxelshape.m_83297_(Direction.Axis.Y);
         if (d0 < 1.0D) {
            if (p_104693_) {
               this.m_104592_((double)p_104690_.m_123341_(), (double)(p_104690_.m_123341_() + 1), (double)p_104690_.m_123343_(), (double)(p_104690_.m_123343_() + 1), (double)(p_104690_.m_123342_() + 1) - 0.05D, p_104692_);
            }
         } else if (!p_104691_.m_204336_(BlockTags.f_13049_)) {
            double d1 = voxelshape.m_83288_(Direction.Axis.Y);
            if (d1 > 0.0D) {
               this.m_104694_(p_104690_, p_104692_, voxelshape, (double)p_104690_.m_123342_() + d1 - 0.05D);
            } else {
               BlockPos blockpos = p_104690_.m_7495_();
               BlockState blockstate = this.m_8055_(blockpos);
               VoxelShape voxelshape1 = blockstate.m_60812_(this, blockpos);
               double d2 = voxelshape1.m_83297_(Direction.Axis.Y);
               if (d2 < 1.0D && blockstate.m_60819_().m_76178_()) {
                  this.m_104694_(p_104690_, p_104692_, voxelshape, (double)p_104690_.m_123342_() - 0.05D);
               }
            }
         }

      }
   }

   private void m_104694_(BlockPos p_104695_, ParticleOptions p_104696_, VoxelShape p_104697_, double p_104698_) {
      this.m_104592_((double)p_104695_.m_123341_() + p_104697_.m_83288_(Direction.Axis.X), (double)p_104695_.m_123341_() + p_104697_.m_83297_(Direction.Axis.X), (double)p_104695_.m_123343_() + p_104697_.m_83288_(Direction.Axis.Z), (double)p_104695_.m_123343_() + p_104697_.m_83297_(Direction.Axis.Z), p_104698_, p_104696_);
   }

   private void m_104592_(double p_104593_, double p_104594_, double p_104595_, double p_104596_, double p_104597_, ParticleOptions p_104598_) {
      this.m_7106_(p_104598_, Mth.m_14139_(this.f_46441_.m_188500_(), p_104593_, p_104594_), p_104597_, Mth.m_14139_(this.f_46441_.m_188500_(), p_104595_, p_104596_), 0.0D, 0.0D, 0.0D);
   }

   public CrashReportCategory m_6026_(CrashReport p_104729_) {
      CrashReportCategory crashreportcategory = super.m_6026_(p_104729_);
      crashreportcategory.m_128165_("Server brand", () -> {
         return this.f_104565_.f_91074_.m_108629_();
      });
      crashreportcategory.m_128165_("Server type", () -> {
         return this.f_104565_.m_91092_() == null ? "Non-integrated multiplayer server" : "Integrated singleplayer server";
      });
      return crashreportcategory;
   }

   public void m_262808_(@Nullable Player p_263381_, double p_263372_, double p_263404_, double p_263365_, Holder<SoundEvent> p_263335_, SoundSource p_263417_, float p_263416_, float p_263349_, long p_263408_) {
      if (p_263381_ == this.f_104565_.f_91074_) {
         this.m_233602_(p_263372_, p_263404_, p_263365_, p_263335_.m_203334_(), p_263417_, p_263416_, p_263349_, false, p_263408_);
      }

   }

   public void m_213890_(@Nullable Player p_263514_, Entity p_263536_, Holder<SoundEvent> p_263518_, SoundSource p_263487_, float p_263538_, float p_263524_, long p_263509_) {
      if (p_263514_ == this.f_104565_.f_91074_) {
         this.f_104565_.m_91106_().m_120367_(new EntityBoundSoundInstance(p_263518_.m_203334_(), p_263487_, p_263538_, p_263524_, p_263536_, p_263509_));
      }

   }

   public void m_7785_(double p_104600_, double p_104601_, double p_104602_, SoundEvent p_104603_, SoundSource p_104604_, float p_104605_, float p_104606_, boolean p_104607_) {
      this.m_233602_(p_104600_, p_104601_, p_104602_, p_104603_, p_104604_, p_104605_, p_104606_, p_104607_, this.f_46441_.m_188505_());
   }

   private void m_233602_(double p_233603_, double p_233604_, double p_233605_, SoundEvent p_233606_, SoundSource p_233607_, float p_233608_, float p_233609_, boolean p_233610_, long p_233611_) {
      double d0 = this.f_104565_.f_91063_.m_109153_().m_90583_().m_82531_(p_233603_, p_233604_, p_233605_);
      SimpleSoundInstance simplesoundinstance = new SimpleSoundInstance(p_233606_, p_233607_, p_233608_, p_233609_, RandomSource.m_216335_(p_233611_), p_233603_, p_233604_, p_233605_);
      if (p_233610_ && d0 > 100.0D) {
         double d1 = Math.sqrt(d0) / 40.0D;
         this.f_104565_.m_91106_().m_120369_(simplesoundinstance, (int)(d1 * 20.0D));
      } else {
         this.f_104565_.m_91106_().m_120367_(simplesoundinstance);
      }

   }

   public void m_7228_(double p_104585_, double p_104586_, double p_104587_, double p_104588_, double p_104589_, double p_104590_, @Nullable CompoundTag p_104591_) {
      this.f_104565_.f_91061_.m_107344_(new FireworkParticles.Starter(this, p_104585_, p_104586_, p_104587_, p_104588_, p_104589_, p_104590_, this.f_104565_.f_91061_, p_104591_));
   }

   public void m_5503_(Packet<?> p_104734_) {
      this.f_104561_.m_104955_(p_104734_);
   }

   public RecipeManager m_7465_() {
      return this.f_104561_.m_105141_();
   }

   public void m_104669_(Scoreboard p_104670_) {
      this.f_104555_ = p_104670_;
   }

   public LevelTickAccess<Block> m_183326_() {
      return BlackholeTickAccess.m_193145_();
   }

   public LevelTickAccess<Fluid> m_183324_() {
      return BlackholeTickAccess.m_193145_();
   }

   public ClientChunkCache m_7726_() {
      return this.f_104559_;
   }

   @Nullable
   public MapItemSavedData m_7489_(String p_104725_) {
      return this.f_104556_.get(p_104725_);
   }

   public void m_257583_(String p_259652_, MapItemSavedData p_259308_) {
      this.f_104556_.put(p_259652_, p_259308_);
   }

   public void m_142325_(String p_171670_, MapItemSavedData p_171671_) {
   }

   public int m_7354_() {
      return 0;
   }

   public Scoreboard m_6188_() {
      return this.f_104555_;
   }

   public void m_7260_(BlockPos p_104685_, BlockState p_104686_, BlockState p_104687_, int p_104688_) {
      this.f_104562_.m_109544_(this, p_104685_, p_104686_, p_104687_, p_104688_);
   }

   public void m_6550_(BlockPos p_104759_, BlockState p_104760_, BlockState p_104761_) {
      this.f_104562_.m_109721_(p_104759_, p_104760_, p_104761_);
   }

   public void m_104793_(int p_104794_, int p_104795_, int p_104796_) {
      this.f_104562_.m_109490_(p_104794_, p_104795_, p_104796_);
   }

   public void m_6801_(int p_104634_, BlockPos p_104635_, int p_104636_) {
      this.f_104562_.m_109774_(p_104634_, p_104635_, p_104636_);
   }

   public void m_6798_(int p_104743_, BlockPos p_104744_, int p_104745_) {
      this.f_104562_.m_109506_(p_104743_, p_104744_, p_104745_);
   }

   public void m_5898_(@Nullable Player p_104654_, int p_104655_, BlockPos p_104656_, int p_104657_) {
      try {
         this.f_104562_.m_234304_(p_104655_, p_104656_, p_104657_);
      } catch (Throwable throwable) {
         CrashReport crashreport = CrashReport.m_127521_(throwable, "Playing level event");
         CrashReportCategory crashreportcategory = crashreport.m_127514_("Level event being played");
         crashreportcategory.m_128159_("Block coordinates", CrashReportCategory.m_178947_(this, p_104656_));
         crashreportcategory.m_128159_("Event source", p_104654_);
         crashreportcategory.m_128159_("Event type", p_104655_);
         crashreportcategory.m_128159_("Event data", p_104657_);
         throw new ReportedException(crashreport);
      }
   }

   public void m_7106_(ParticleOptions p_104706_, double p_104707_, double p_104708_, double p_104709_, double p_104710_, double p_104711_, double p_104712_) {
      this.f_104562_.m_109743_(p_104706_, p_104706_.m_6012_().m_123742_(), p_104707_, p_104708_, p_104709_, p_104710_, p_104711_, p_104712_);
   }

   public void m_6493_(ParticleOptions p_104714_, boolean p_104715_, double p_104716_, double p_104717_, double p_104718_, double p_104719_, double p_104720_, double p_104721_) {
      this.f_104562_.m_109743_(p_104714_, p_104714_.m_6012_().m_123742_() || p_104715_, p_104716_, p_104717_, p_104718_, p_104719_, p_104720_, p_104721_);
   }

   public void m_7107_(ParticleOptions p_104766_, double p_104767_, double p_104768_, double p_104769_, double p_104770_, double p_104771_, double p_104772_) {
      this.f_104562_.m_109752_(p_104766_, false, true, p_104767_, p_104768_, p_104769_, p_104770_, p_104771_, p_104772_);
   }

   public void m_6485_(ParticleOptions p_104774_, boolean p_104775_, double p_104776_, double p_104777_, double p_104778_, double p_104779_, double p_104780_, double p_104781_) {
      this.f_104562_.m_109752_(p_104774_, p_104774_.m_6012_().m_123742_() || p_104775_, true, p_104776_, p_104777_, p_104778_, p_104779_, p_104780_, p_104781_);
   }

   public List<AbstractClientPlayer> m_6907_() {
      return this.f_104566_;
   }

   public Holder<Biome> m_203675_(int p_205516_, int p_205517_, int p_205518_) {
      return this.m_9598_().m_175515_(Registries.f_256952_).m_246971_(Biomes.f_48202_);
   }

   public float m_104805_(float p_104806_) {
      float f = this.m_46942_(p_104806_);
      float f1 = 1.0F - (Mth.m_14089_(f * ((float)Math.PI * 2F)) * 2.0F + 0.2F);
      f1 = Mth.m_14036_(f1, 0.0F, 1.0F);
      f1 = 1.0F - f1;
      f1 *= 1.0F - this.m_46722_(p_104806_) * 5.0F / 16.0F;
      f1 *= 1.0F - this.m_46661_(p_104806_) * 5.0F / 16.0F;
      return f1 * 0.8F + 0.2F;
   }

   public Vec3 m_171660_(Vec3 p_171661_, float p_171662_) {
      float f = this.m_46942_(p_171662_);
      Vec3 vec3 = p_171661_.m_82492_(2.0D, 2.0D, 2.0D).m_82490_(0.25D);
      BiomeManager biomemanager = this.m_7062_();
      Vec3 vec31 = CubicSampler.m_130038_(vec3, (p_194161_, p_194162_, p_194163_) -> {
         return Vec3.m_82501_(biomemanager.m_204210_(p_194161_, p_194162_, p_194163_).m_203334_().m_47463_());
      });
      float f1 = Mth.m_14089_(f * ((float)Math.PI * 2F)) * 2.0F + 0.5F;
      f1 = Mth.m_14036_(f1, 0.0F, 1.0F);
      float f2 = (float)vec31.f_82479_ * f1;
      float f3 = (float)vec31.f_82480_ * f1;
      float f4 = (float)vec31.f_82481_ * f1;
      float f5 = this.m_46722_(p_171662_);
      if (f5 > 0.0F) {
         float f6 = (f2 * 0.3F + f3 * 0.59F + f4 * 0.11F) * 0.6F;
         float f7 = 1.0F - f5 * 0.75F;
         f2 = f2 * f7 + f6 * (1.0F - f7);
         f3 = f3 * f7 + f6 * (1.0F - f7);
         f4 = f4 * f7 + f6 * (1.0F - f7);
      }

      float f9 = this.m_46661_(p_171662_);
      if (f9 > 0.0F) {
         float f10 = (f2 * 0.3F + f3 * 0.59F + f4 * 0.11F) * 0.2F;
         float f8 = 1.0F - f9 * 0.75F;
         f2 = f2 * f8 + f10 * (1.0F - f8);
         f3 = f3 * f8 + f10 * (1.0F - f8);
         f4 = f4 * f8 + f10 * (1.0F - f8);
      }

      int i = this.m_104819_();
      if (i > 0) {
         float f11 = (float)i - p_171662_;
         if (f11 > 1.0F) {
            f11 = 1.0F;
         }

         f11 *= 0.45F;
         f2 = f2 * (1.0F - f11) + 0.8F * f11;
         f3 = f3 * (1.0F - f11) + 0.8F * f11;
         f4 = f4 * (1.0F - f11) + 1.0F * f11;
      }

      return new Vec3((double)f2, (double)f3, (double)f4);
   }

   public Vec3 m_104808_(float p_104809_) {
      float f = this.m_46942_(p_104809_);
      float f1 = Mth.m_14089_(f * ((float)Math.PI * 2F)) * 2.0F + 0.5F;
      f1 = Mth.m_14036_(f1, 0.0F, 1.0F);
      float f2 = 1.0F;
      float f3 = 1.0F;
      float f4 = 1.0F;
      float f5 = this.m_46722_(p_104809_);
      if (f5 > 0.0F) {
         float f6 = (f2 * 0.3F + f3 * 0.59F + f4 * 0.11F) * 0.6F;
         float f7 = 1.0F - f5 * 0.95F;
         f2 = f2 * f7 + f6 * (1.0F - f7);
         f3 = f3 * f7 + f6 * (1.0F - f7);
         f4 = f4 * f7 + f6 * (1.0F - f7);
      }

      f2 *= f1 * 0.9F + 0.1F;
      f3 *= f1 * 0.9F + 0.1F;
      f4 *= f1 * 0.85F + 0.15F;
      float f9 = this.m_46661_(p_104809_);
      if (f9 > 0.0F) {
         float f10 = (f2 * 0.3F + f3 * 0.59F + f4 * 0.11F) * 0.2F;
         float f8 = 1.0F - f9 * 0.95F;
         f2 = f2 * f8 + f10 * (1.0F - f8);
         f3 = f3 * f8 + f10 * (1.0F - f8);
         f4 = f4 * f8 + f10 * (1.0F - f8);
      }

      return new Vec3((double)f2, (double)f3, (double)f4);
   }

   public float m_104811_(float p_104812_) {
      float f = this.m_46942_(p_104812_);
      float f1 = 1.0F - (Mth.m_14089_(f * ((float)Math.PI * 2F)) * 2.0F + 0.25F);
      f1 = Mth.m_14036_(f1, 0.0F, 1.0F);
      return f1 * f1 * 0.5F;
   }

   public int m_104819_() {
      return this.f_104565_.f_91066_.m_231935_().m_231551_() ? 0 : this.f_104557_;
   }

   public void m_6580_(int p_104783_) {
      this.f_104557_ = p_104783_;
   }

   public float m_7717_(Direction p_104703_, boolean p_104704_) {
      boolean flag = this.m_104583_().m_108885_();
      if (!p_104704_) {
         return flag ? 0.9F : 1.0F;
      } else {
         switch (p_104703_) {
            case DOWN:
               return flag ? 0.9F : 0.5F;
            case UP:
               return flag ? 0.9F : 1.0F;
            case NORTH:
            case SOUTH:
               return 0.8F;
            case WEST:
            case EAST:
               return 0.6F;
            default:
               return 1.0F;
         }
      }
   }

   public int m_6171_(BlockPos p_104700_, ColorResolver p_104701_) {
      BlockTintCache blocktintcache = this.f_104558_.get(p_104701_);
      return blocktintcache.m_193812_(p_104700_);
   }

   public int m_104762_(BlockPos p_104763_, ColorResolver p_104764_) {
      int i = Minecraft.m_91087_().f_91066_.m_232121_().m_231551_();
      if (i == 0) {
         return p_104764_.m_130045_(this.m_204166_(p_104763_).m_203334_(), (double)p_104763_.m_123341_(), (double)p_104763_.m_123343_());
      } else {
         int j = (i * 2 + 1) * (i * 2 + 1);
         int k = 0;
         int l = 0;
         int i1 = 0;
         Cursor3D cursor3d = new Cursor3D(p_104763_.m_123341_() - i, p_104763_.m_123342_(), p_104763_.m_123343_() - i, p_104763_.m_123341_() + i, p_104763_.m_123342_(), p_104763_.m_123343_() + i);

         int j1;
         for(BlockPos.MutableBlockPos blockpos$mutableblockpos = new BlockPos.MutableBlockPos(); cursor3d.m_122304_(); i1 += j1 & 255) {
            blockpos$mutableblockpos.m_122178_(cursor3d.m_122305_(), cursor3d.m_122306_(), cursor3d.m_122307_());
            j1 = p_104764_.m_130045_(this.m_204166_(blockpos$mutableblockpos).m_203334_(), (double)blockpos$mutableblockpos.m_123341_(), (double)blockpos$mutableblockpos.m_123343_());
            k += (j1 & 16711680) >> 16;
            l += (j1 & '\uff00') >> 8;
         }

         return (k / j & 255) << 16 | (l / j & 255) << 8 | i1 / j & 255;
      }
   }

   public void m_104752_(BlockPos p_104753_, float p_104754_) {
      this.f_46442_.m_7250_(p_104753_, p_104754_);
   }

   public String toString() {
      return "ClientLevel";
   }

   public ClientLevel.ClientLevelData m_6106_() {
      return this.f_104563_;
   }

   public void m_214171_(GameEvent p_233639_, Vec3 p_233640_, GameEvent.Context p_233641_) {
   }

   protected Map<String, MapItemSavedData> m_171684_() {
      return ImmutableMap.copyOf(this.f_104556_);
   }

   protected void m_171672_(Map<String, MapItemSavedData> p_171673_) {
      this.f_104556_.putAll(p_171673_);
   }

   protected LevelEntityGetter<Entity> m_142646_() {
      return this.f_171631_.m_157645_();
   }

   public String m_46464_() {
      return "Chunks[C] W: " + this.f_104559_.m_6754_() + " E: " + this.f_171631_.m_157664_();
   }

   public void m_142052_(BlockPos p_171667_, BlockState p_171668_) {
      this.f_104565_.f_91061_.m_107355_(p_171667_, p_171668_);
   }

   public void m_194174_(int p_194175_) {
      this.f_194123_ = p_194175_;
   }

   public int m_194186_() {
      return this.f_194123_;
   }

   public FeatureFlagSet m_246046_() {
      return this.f_104561_.m_247016_();
   }

   @OnlyIn(Dist.CLIENT)
   public static class ClientLevelData implements WritableLevelData {
      private final boolean f_104830_;
      private final GameRules f_104831_;
      private final boolean f_104832_;
      private int f_104833_;
      private int f_104834_;
      private int f_104835_;
      private float f_104836_;
      private long f_104837_;
      private long f_104838_;
      private boolean f_104839_;
      private Difficulty f_104840_;
      private boolean f_104841_;

      public ClientLevelData(Difficulty p_104843_, boolean p_104844_, boolean p_104845_) {
         this.f_104840_ = p_104843_;
         this.f_104830_ = p_104844_;
         this.f_104832_ = p_104845_;
         this.f_104831_ = new GameRules();
      }

      public int m_6789_() {
         return this.f_104833_;
      }

      public int m_6527_() {
         return this.f_104834_;
      }

      public int m_6526_() {
         return this.f_104835_;
      }

      public float m_6790_() {
         return this.f_104836_;
      }

      public long m_6793_() {
         return this.f_104837_;
      }

      public long m_6792_() {
         return this.f_104838_;
      }

      public void m_6395_(int p_104862_) {
         this.f_104833_ = p_104862_;
      }

      public void m_6397_(int p_104869_) {
         this.f_104834_ = p_104869_;
      }

      public void m_6400_(int p_104872_) {
         this.f_104835_ = p_104872_;
      }

      public void m_7113_(float p_104848_) {
         this.f_104836_ = p_104848_;
      }

      public void m_104849_(long p_104850_) {
         this.f_104837_ = p_104850_;
      }

      public void m_104863_(long p_104864_) {
         this.f_104838_ = p_104864_;
      }

      public void m_7250_(BlockPos p_104854_, float p_104855_) {
         this.f_104833_ = p_104854_.m_123341_();
         this.f_104834_ = p_104854_.m_123342_();
         this.f_104835_ = p_104854_.m_123343_();
         this.f_104836_ = p_104855_;
      }

      public boolean m_6534_() {
         return false;
      }

      public boolean m_6533_() {
         return this.f_104839_;
      }

      public void m_5565_(boolean p_104866_) {
         this.f_104839_ = p_104866_;
      }

      public boolean m_5466_() {
         return this.f_104830_;
      }

      public GameRules m_5470_() {
         return this.f_104831_;
      }

      public Difficulty m_5472_() {
         return this.f_104840_;
      }

      public boolean m_5474_() {
         return this.f_104841_;
      }

      public void m_142471_(CrashReportCategory p_171690_, LevelHeightAccessor p_171691_) {
         WritableLevelData.super.m_142471_(p_171690_, p_171691_);
      }

      public void m_104851_(Difficulty p_104852_) {
         this.f_104840_ = p_104852_;
      }

      public void m_104858_(boolean p_104859_) {
         this.f_104841_ = p_104859_;
      }

      public double m_171687_(LevelHeightAccessor p_171688_) {
         return this.f_104832_ ? (double)p_171688_.m_141937_() : 63.0D;
      }

      public float m_205519_() {
         return this.f_104832_ ? 1.0F : 0.03125F;
      }
   }

   @OnlyIn(Dist.CLIENT)
   final class EntityCallbacks implements LevelCallback<Entity> {
      public void m_141989_(Entity p_171696_) {
      }

      public void m_141986_(Entity p_171700_) {
      }

      public void m_141987_(Entity p_171704_) {
         ClientLevel.this.f_171630_.m_156908_(p_171704_);
      }

      public void m_141983_(Entity p_171708_) {
         ClientLevel.this.f_171630_.m_156912_(p_171708_);
      }

      public void m_141985_(Entity p_171712_) {
         if (p_171712_ instanceof AbstractClientPlayer) {
            ClientLevel.this.f_104566_.add((AbstractClientPlayer)p_171712_);
         }

      }

      public void m_141981_(Entity p_171716_) {
         p_171716_.m_19877_();
         ClientLevel.this.f_104566_.remove(p_171716_);
      }

      public void m_214006_(Entity p_233660_) {
      }
   }
}
