package net.minecraft.world.entity;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.Iterables;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import com.mojang.logging.LogUtils;
import it.unimi.dsi.fastutil.objects.Object2DoubleArrayMap;
import it.unimi.dsi.fastutil.objects.Object2DoubleMap;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.BiConsumer;
import java.util.function.Predicate;
import java.util.stream.Stream;
import javax.annotation.Nullable;
import net.minecraft.BlockUtil;
import net.minecraft.CrashReport;
import net.minecraft.CrashReportCategory;
import net.minecraft.ReportedException;
import net.minecraft.Util;
import net.minecraft.advancements.CriteriaTriggers;
import net.minecraft.commands.CommandSource;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.arguments.EntityAnchorArgument;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.SectionPos;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.DoubleTag;
import net.minecraft.nbt.FloatTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.HoverEvent;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundAddEntityPacket;
import net.minecraft.network.protocol.game.VecDeltaCodec;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.TicketType;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.tags.EntityTypeTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.tags.TagKey;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.Nameable;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageSources;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.vehicle.Boat;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.item.enchantment.ProtectionEnchantment;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Explosion;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.ItemLike;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.FenceGateBlock;
import net.minecraft.world.level.block.HoneyBlock;
import net.minecraft.world.level.block.Mirror;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.border.WorldBorder;
import net.minecraft.world.level.dimension.DimensionType;
import net.minecraft.world.level.entity.EntityAccess;
import net.minecraft.world.level.entity.EntityInLevelCallback;
import net.minecraft.world.level.gameevent.DynamicGameEventListener;
import net.minecraft.world.level.gameevent.GameEvent;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.material.Fluid;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.level.material.PushReaction;
import net.minecraft.world.level.portal.PortalInfo;
import net.minecraft.world.level.portal.PortalShape;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec2;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.BooleanOp;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.minecraft.world.scores.PlayerTeam;
import net.minecraft.world.scores.Team;
import org.slf4j.Logger;

public abstract class Entity extends net.minecraftforge.common.capabilities.CapabilityProvider<Entity> implements Nameable, EntityAccess, CommandSource, net.minecraftforge.common.extensions.IForgeEntity {
   private static final Logger f_19849_ = LogUtils.getLogger();
   public static final String f_146815_ = "id";
   public static final String f_146816_ = "Passengers";
   protected static final AtomicInteger f_19843_ = new AtomicInteger();
   private static final List<ItemStack> f_19844_ = Collections.emptyList();
   public static final int f_146817_ = 60;
   public static final int f_146818_ = 300;
   public static final int f_146819_ = 1024;
   public static final float f_286980_ = 0.2F;
   public static final double f_286994_ = 0.500001D;
   public static final double f_287009_ = 0.999999D;
   public static final float f_146821_ = 0.11111111F;
   public static final int f_146822_ = 140;
   public static final int f_146823_ = 40;
   private static final AABB f_19845_ = new AABB(0.0D, 0.0D, 0.0D, 0.0D, 0.0D, 0.0D);
   private static final double f_146814_ = 0.014D;
   private static final double f_146811_ = 0.007D;
   private static final double f_146812_ = 0.0023333333333333335D;
   public static final String f_146824_ = "UUID";
   private static double f_19846_ = 1.0D;
   @Deprecated // Forge: Use the getter to allow overriding in mods
   private final EntityType<?> f_19847_;
   private int f_19848_ = f_19843_.incrementAndGet();
   public boolean f_19850_;
   private ImmutableList<Entity> f_19823_ = ImmutableList.of();
   protected int f_19851_;
   @Nullable
   private Entity f_19824_;
   private Level f_19853_;
   public double f_19854_;
   public double f_19855_;
   public double f_19856_;
   private Vec3 f_19825_;
   private BlockPos f_19826_;
   private ChunkPos f_185933_;
   private Vec3 f_19827_ = Vec3.f_82478_;
   private float f_19857_;
   private float f_19858_;
   public float f_19859_;
   public float f_19860_;
   private AABB f_19828_ = f_19845_;
   private boolean f_19861_;
   public boolean f_19862_;
   public boolean f_19863_;
   public boolean f_201939_;
   public boolean f_185931_;
   public boolean f_19864_;
   protected Vec3 f_19865_ = Vec3.f_82478_;
   @Nullable
   private Entity.RemovalReason f_146795_;
   public static final float f_146792_ = 0.6F;
   public static final float f_146793_ = 1.8F;
   public float f_19867_;
   public float f_19787_;
   public float f_19788_;
   public float f_146794_;
   public float f_19789_;
   private float f_19829_ = 1.0F;
   public double f_19790_;
   public double f_19791_;
   public double f_19792_;
   private float f_19793_;
   public boolean f_19794_;
   protected final RandomSource f_19796_ = RandomSource.m_216327_();
   public int f_19797_;
   private int f_19831_ = -this.m_6101_();
   protected boolean f_19798_;
   @Deprecated // Forge: Use forgeFluidTypeHeight instead
   protected Object2DoubleMap<TagKey<Fluid>> f_19799_ = new Object2DoubleArrayMap<>(2);
   protected boolean f_19800_;
   @Deprecated // Forge: Use forgeFluidTypeOnEyes instead
   private final Set<TagKey<Fluid>> f_19801_ = new HashSet<>();
   public int f_19802_;
   protected boolean f_19803_ = true;
   protected final SynchedEntityData f_19804_;
   protected static final EntityDataAccessor<Byte> f_19805_ = SynchedEntityData.m_135353_(Entity.class, EntityDataSerializers.f_135027_);
   protected static final int f_146805_ = 0;
   private static final int f_146796_ = 1;
   private static final int f_146797_ = 3;
   private static final int f_146798_ = 4;
   private static final int f_146799_ = 5;
   protected static final int f_146806_ = 6;
   protected static final int f_146807_ = 7;
   private static final EntityDataAccessor<Integer> f_19832_ = SynchedEntityData.m_135353_(Entity.class, EntityDataSerializers.f_135028_);
   private static final EntityDataAccessor<Optional<Component>> f_19833_ = SynchedEntityData.m_135353_(Entity.class, EntityDataSerializers.f_135032_);
   private static final EntityDataAccessor<Boolean> f_19834_ = SynchedEntityData.m_135353_(Entity.class, EntityDataSerializers.f_135035_);
   private static final EntityDataAccessor<Boolean> f_19835_ = SynchedEntityData.m_135353_(Entity.class, EntityDataSerializers.f_135035_);
   private static final EntityDataAccessor<Boolean> f_19836_ = SynchedEntityData.m_135353_(Entity.class, EntityDataSerializers.f_135035_);
   protected static final EntityDataAccessor<Pose> f_19806_ = SynchedEntityData.m_135353_(Entity.class, EntityDataSerializers.f_135045_);
   private static final EntityDataAccessor<Integer> f_146800_ = SynchedEntityData.m_135353_(Entity.class, EntityDataSerializers.f_135028_);
   private EntityInLevelCallback f_146801_ = EntityInLevelCallback.f_156799_;
   private final VecDeltaCodec f_216985_ = new VecDeltaCodec();
   public boolean f_19811_;
   public boolean f_19812_;
   private int f_19839_;
   protected boolean f_19817_;
   protected int f_19818_;
   protected BlockPos f_19819_;
   private boolean f_19840_;
   protected UUID f_19820_ = Mth.m_216261_(this.f_19796_);
   protected String f_19821_ = this.f_19820_.toString();
   private boolean f_146802_;
   private final Set<String> f_19841_ = Sets.newHashSet();
   private final double[] f_19813_ = new double[]{0.0D, 0.0D, 0.0D};
   private long f_19814_;
   private EntityDimensions f_19815_;
   private float f_19816_;
   public boolean f_146808_;
   public boolean f_146809_;
   public boolean f_146810_;
   public Optional<BlockPos> f_285638_ = Optional.empty();
   private boolean f_286942_ = false;
   private float f_146803_;
   private int f_146804_;
   private boolean f_146813_;
   @Nullable
   private BlockState f_185934_ = null;

   public Entity(EntityType<?> p_19870_, Level p_19871_) {
      super(Entity.class);
      this.f_19847_ = p_19870_;
      this.f_19853_ = p_19871_;
      this.f_19815_ = p_19870_.m_20680_();
      this.f_19825_ = Vec3.f_82478_;
      this.f_19826_ = BlockPos.f_121853_;
      this.f_185933_ = ChunkPos.f_186419_;
      this.f_19804_ = new SynchedEntityData(this);
      this.f_19804_.m_135372_(f_19805_, (byte)0);
      this.f_19804_.m_135372_(f_19832_, this.m_6062_());
      this.f_19804_.m_135372_(f_19834_, false);
      this.f_19804_.m_135372_(f_19833_, Optional.empty());
      this.f_19804_.m_135372_(f_19835_, false);
      this.f_19804_.m_135372_(f_19836_, false);
      this.f_19804_.m_135372_(f_19806_, Pose.STANDING);
      this.f_19804_.m_135372_(f_146800_, 0);
      this.m_8097_();
      this.m_6034_(0.0D, 0.0D, 0.0D);
      net.minecraftforge.event.entity.EntityEvent.Size sizeEvent = net.minecraftforge.event.ForgeEventFactory.getEntitySizeForge(this, Pose.STANDING, this.f_19815_, this.m_6380_(Pose.STANDING, this.f_19815_));
      this.f_19815_ = sizeEvent.getNewSize();
      this.f_19816_ = sizeEvent.getNewEyeHeight();
      net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.EntityEvent.EntityConstructing(this));
      this.gatherCapabilities();
   }

   public boolean m_20039_(BlockPos p_20040_, BlockState p_20041_) {
      VoxelShape voxelshape = p_20041_.m_60742_(this.m_9236_(), p_20040_, CollisionContext.m_82750_(this));
      VoxelShape voxelshape1 = voxelshape.m_83216_((double)p_20040_.m_123341_(), (double)p_20040_.m_123342_(), (double)p_20040_.m_123343_());
      return Shapes.m_83157_(voxelshape1, Shapes.m_83064_(this.m_20191_()), BooleanOp.f_82689_);
   }

   public int m_19876_() {
      Team team = this.m_5647_();
      return team != null && team.m_7414_().m_126665_() != null ? team.m_7414_().m_126665_() : 16777215;
   }

   public boolean m_5833_() {
      return false;
   }

   public final void m_19877_() {
      if (this.m_20160_()) {
         this.m_20153_();
      }

      if (this.m_20159_()) {
         this.m_8127_();
      }

   }

   public void m_217006_(double p_217007_, double p_217008_, double p_217009_) {
      this.f_216985_.m_238033_(new Vec3(p_217007_, p_217008_, p_217009_));
   }

   public VecDeltaCodec m_217001_() {
      return this.f_216985_;
   }

   public EntityType<?> m_6095_() {
      return this.f_19847_;
   }

   public int m_19879_() {
      return this.f_19848_;
   }

   public void m_20234_(int p_20235_) {
      this.f_19848_ = p_20235_;
   }

   public Set<String> m_19880_() {
      return this.f_19841_;
   }

   public boolean m_20049_(String p_20050_) {
      return this.f_19841_.size() >= 1024 ? false : this.f_19841_.add(p_20050_);
   }

   public boolean m_20137_(String p_20138_) {
      return this.f_19841_.remove(p_20138_);
   }

   public void m_6074_() {
      this.m_142687_(Entity.RemovalReason.KILLED);
      this.m_146850_(GameEvent.f_223707_);
   }

   public final void m_146870_() {
      this.m_142687_(Entity.RemovalReason.DISCARDED);
   }

   protected abstract void m_8097_();

   public SynchedEntityData m_20088_() {
      return this.f_19804_;
   }

   public boolean equals(Object p_20245_) {
      if (p_20245_ instanceof Entity) {
         return ((Entity)p_20245_).f_19848_ == this.f_19848_;
      } else {
         return false;
      }
   }

   public int hashCode() {
      return this.f_19848_;
   }

   public void m_142687_(Entity.RemovalReason p_146834_) {
      this.m_142467_(p_146834_);
      this.invalidateCaps();
   }

   public void m_142036_() {
   }

   public void m_20124_(Pose p_20125_) {
      this.f_19804_.m_135381_(f_19806_, p_20125_);
   }

   public Pose m_20089_() {
      return this.f_19804_.m_135370_(f_19806_);
   }

   public boolean m_217003_(Pose p_217004_) {
      return this.m_20089_() == p_217004_;
   }

   public boolean m_19950_(Entity p_19951_, double p_19952_) {
      return this.m_20182_().m_82509_(p_19951_.m_20182_(), p_19952_);
   }

   public boolean m_216992_(Entity p_216993_, double p_216994_, double p_216995_) {
      double d0 = p_216993_.m_20185_() - this.m_20185_();
      double d1 = p_216993_.m_20186_() - this.m_20186_();
      double d2 = p_216993_.m_20189_() - this.m_20189_();
      return Mth.m_211589_(d0, d2) < Mth.m_144952_(p_216994_) && Mth.m_144952_(d1) < Mth.m_144952_(p_216995_);
   }

   protected void m_19915_(float p_19916_, float p_19917_) {
      this.m_146922_(p_19916_ % 360.0F);
      this.m_146926_(p_19917_ % 360.0F);
   }

   public final void m_146884_(Vec3 p_146885_) {
      this.m_6034_(p_146885_.m_7096_(), p_146885_.m_7098_(), p_146885_.m_7094_());
   }

   public void m_6034_(double p_20210_, double p_20211_, double p_20212_) {
      this.m_20343_(p_20210_, p_20211_, p_20212_);
      this.m_20011_(this.m_142242_());
   }

   protected AABB m_142242_() {
      return this.f_19815_.m_20393_(this.f_19825_);
   }

   protected void m_20090_() {
      this.m_6034_(this.f_19825_.f_82479_, this.f_19825_.f_82480_, this.f_19825_.f_82481_);
   }

   public void m_19884_(double p_19885_, double p_19886_) {
      float f = (float)p_19886_ * 0.15F;
      float f1 = (float)p_19885_ * 0.15F;
      this.m_146926_(this.m_146909_() + f);
      this.m_146922_(this.m_146908_() + f1);
      this.m_146926_(Mth.m_14036_(this.m_146909_(), -90.0F, 90.0F));
      this.f_19860_ += f;
      this.f_19859_ += f1;
      this.f_19860_ = Mth.m_14036_(this.f_19860_, -90.0F, 90.0F);
      if (this.f_19824_ != null) {
         this.f_19824_.m_7340_(this);
      }

   }

   public void m_8119_() {
      this.m_6075_();
   }

   public void m_6075_() {
      this.m_9236_().m_46473_().m_6180_("entityBaseTick");
      this.f_185934_ = null;
      if (this.m_20159_() && this.m_20202_().m_213877_()) {
         this.m_8127_();
      }

      if (this.f_19851_ > 0) {
         --this.f_19851_;
      }

      this.f_19867_ = this.f_19787_;
      this.f_19860_ = this.m_146909_();
      this.f_19859_ = this.m_146908_();
      this.m_20157_();
      if (this.m_5843_()) {
         this.m_20076_();
      }

      this.f_146809_ = this.f_146808_;
      this.f_146808_ = false;
      this.m_20073_();
      this.m_20323_();
      this.m_5844_();
      if (this.m_9236_().f_46443_) {
         this.m_20095_();
      } else if (this.f_19831_ > 0) {
         if (this.m_5825_()) {
            this.m_7311_(this.f_19831_ - 4);
            if (this.f_19831_ < 0) {
               this.m_20095_();
            }
         } else {
            if (this.f_19831_ % 20 == 0 && !this.m_20077_()) {
               this.m_6469_(this.m_269291_().m_269549_(), 1.0F);
            }

            this.m_7311_(this.f_19831_ - 1);
         }

         if (this.m_146888_() > 0) {
            this.m_146917_(0);
            this.m_9236_().m_5898_((Player)null, 1009, this.f_19826_, 1);
         }
      }

      if (this.m_20077_()) {
         this.m_20093_();
         this.f_19789_ *= this.getFluidFallDistanceModifier(net.minecraftforge.common.ForgeMod.LAVA_TYPE.get());
      }

      this.m_146871_();
      if (!this.m_9236_().f_46443_) {
         this.m_146868_(this.f_19831_ > 0);
      }

      this.f_19803_ = false;
      this.m_9236_().m_46473_().m_7238_();
   }

   public void m_146868_(boolean p_146869_) {
      this.m_20115_(0, p_146869_ || this.f_146813_);
   }

   public void m_146871_() {
      if (this.m_20186_() < (double)(this.m_9236_().m_141937_() - 64)) {
         this.m_6088_();
      }

   }

   public void m_20091_() {
      this.f_19839_ = this.m_6045_();
   }

   public void m_287199_(int p_287760_) {
      this.f_19839_ = p_287760_;
   }

   public int m_287157_() {
      return this.f_19839_;
   }

   public boolean m_20092_() {
      return this.f_19839_ > 0;
   }

   protected void m_8021_() {
      if (this.m_20092_()) {
         --this.f_19839_;
      }

   }

   public int m_6078_() {
      return 0;
   }

   public void m_20093_() {
      if (!this.m_5825_()) {
         this.m_20254_(15);
         if (this.m_6469_(this.m_269291_().m_269233_(), 4.0F)) {
            this.m_5496_(SoundEvents.f_11909_, 0.4F, 2.0F + this.f_19796_.m_188501_() * 0.4F);
         }

      }
   }

   public void m_20254_(int p_20255_) {
      int i = p_20255_ * 20;
      if (this instanceof LivingEntity) {
         i = ProtectionEnchantment.m_45138_((LivingEntity)this, i);
      }

      if (this.f_19831_ < i) {
         this.m_7311_(i);
      }

   }

   public void m_7311_(int p_20269_) {
      this.f_19831_ = p_20269_;
   }

   public int m_20094_() {
      return this.f_19831_;
   }

   public void m_20095_() {
      this.m_7311_(0);
   }

   protected void m_6088_() {
      this.m_146870_();
   }

   public boolean m_20229_(double p_20230_, double p_20231_, double p_20232_) {
      return this.m_20131_(this.m_20191_().m_82386_(p_20230_, p_20231_, p_20232_));
   }

   private boolean m_20131_(AABB p_20132_) {
      return this.m_9236_().m_45756_(this, p_20132_) && !this.m_9236_().m_46855_(p_20132_);
   }

   public void m_6853_(boolean p_20181_) {
      this.f_19861_ = p_20181_;
      this.m_289600_(p_20181_, (Vec3)null);
   }

   public void m_289603_(boolean p_289661_, Vec3 p_289653_) {
      this.f_19861_ = p_289661_;
      this.m_289600_(p_289661_, p_289653_);
   }

   public boolean m_287201_(BlockPos p_287613_) {
      return this.f_285638_.isPresent() && this.f_285638_.get().equals(p_287613_);
   }

   protected void m_289600_(boolean p_289694_, @Nullable Vec3 p_289680_) {
      if (p_289694_) {
         AABB aabb = this.m_20191_();
         AABB aabb1 = new AABB(aabb.f_82288_, aabb.f_82289_ - 1.0E-6D, aabb.f_82290_, aabb.f_82291_, aabb.f_82289_, aabb.f_82293_);
         Optional<BlockPos> optional = this.f_19853_.m_285750_(this, aabb1);
         if (!optional.isPresent() && !this.f_286942_) {
            if (p_289680_ != null) {
               AABB aabb2 = aabb1.m_82386_(-p_289680_.f_82479_, 0.0D, -p_289680_.f_82481_);
               optional = this.f_19853_.m_285750_(this, aabb2);
               this.f_285638_ = optional;
            }
         } else {
            this.f_285638_ = optional;
         }

         this.f_286942_ = optional.isEmpty();
      } else {
         this.f_286942_ = false;
         if (this.f_285638_.isPresent()) {
            this.f_285638_ = Optional.empty();
         }
      }

   }

   public boolean m_20096_() {
      return this.f_19861_;
   }

   public void m_6478_(MoverType p_19973_, Vec3 p_19974_) {
      if (this.f_19794_) {
         this.m_6034_(this.m_20185_() + p_19974_.f_82479_, this.m_20186_() + p_19974_.f_82480_, this.m_20189_() + p_19974_.f_82481_);
      } else {
         this.f_146810_ = this.m_6060_();
         if (p_19973_ == MoverType.PISTON) {
            p_19974_ = this.m_20133_(p_19974_);
            if (p_19974_.equals(Vec3.f_82478_)) {
               return;
            }
         }

         this.m_9236_().m_46473_().m_6180_("move");
         if (this.f_19865_.m_82556_() > 1.0E-7D) {
            p_19974_ = p_19974_.m_82559_(this.f_19865_);
            this.f_19865_ = Vec3.f_82478_;
            this.m_20256_(Vec3.f_82478_);
         }

         p_19974_ = this.m_5763_(p_19974_, p_19973_);
         Vec3 vec3 = this.m_20272_(p_19974_);
         double d0 = vec3.m_82556_();
         if (d0 > 1.0E-7D) {
            if (this.f_19789_ != 0.0F && d0 >= 1.0D) {
               BlockHitResult blockhitresult = this.m_9236_().m_45547_(new ClipContext(this.m_20182_(), this.m_20182_().m_82549_(vec3), ClipContext.Block.FALLDAMAGE_RESETTING, ClipContext.Fluid.WATER, this));
               if (blockhitresult.m_6662_() != HitResult.Type.MISS) {
                  this.m_183634_();
               }
            }

            this.m_6034_(this.m_20185_() + vec3.f_82479_, this.m_20186_() + vec3.f_82480_, this.m_20189_() + vec3.f_82481_);
         }

         this.m_9236_().m_46473_().m_7238_();
         this.m_9236_().m_46473_().m_6180_("rest");
         boolean flag4 = !Mth.m_14082_(p_19974_.f_82479_, vec3.f_82479_);
         boolean flag = !Mth.m_14082_(p_19974_.f_82481_, vec3.f_82481_);
         this.f_19862_ = flag4 || flag;
         this.f_19863_ = p_19974_.f_82480_ != vec3.f_82480_;
         this.f_201939_ = this.f_19863_ && p_19974_.f_82480_ < 0.0D;
         if (this.f_19862_) {
            this.f_185931_ = this.m_196406_(vec3);
         } else {
            this.f_185931_ = false;
         }

         this.m_289603_(this.f_201939_, vec3);
         BlockPos blockpos = this.m_216999_();
         BlockState blockstate = this.m_9236_().m_8055_(blockpos);
         this.m_7840_(vec3.f_82480_, this.m_20096_(), blockstate, blockpos);
         if (this.m_213877_()) {
            this.m_9236_().m_46473_().m_7238_();
         } else {
            if (this.f_19862_) {
               Vec3 vec31 = this.m_20184_();
               this.m_20334_(flag4 ? 0.0D : vec31.f_82479_, vec31.f_82480_, flag ? 0.0D : vec31.f_82481_);
            }

            Block block = blockstate.m_60734_();
            if (p_19974_.f_82480_ != vec3.f_82480_) {
               block.m_5548_(this.m_9236_(), this);
            }

            if (this.m_20096_()) {
               block.m_141947_(this.m_9236_(), blockpos, blockstate, this);
            }

            Entity.MovementEmission entity$movementemission = this.m_142319_();
            if (entity$movementemission.m_146944_() && !this.m_20159_()) {
               double d1 = vec3.f_82479_;
               double d2 = vec3.f_82480_;
               double d3 = vec3.f_82481_;
               this.f_146794_ = (float)((double)this.f_146794_ + vec3.m_82553_() * 0.6D);
               BlockPos blockpos1 = this.m_20097_();
               BlockState blockstate1 = this.m_9236_().m_8055_(blockpos1);
               boolean flag1 = this.m_285776_(blockstate1);
               if (!flag1) {
                  d2 = 0.0D;
               }

               this.f_19787_ += (float)vec3.m_165924_() * 0.6F;
               this.f_19788_ += (float)Math.sqrt(d1 * d1 + d2 * d2 + d3 * d3) * 0.6F;
               if (this.f_19788_ > this.f_19829_ && !blockstate1.m_60795_()) {
                  boolean flag2 = blockpos1.equals(blockpos);
                  boolean flag3 = this.m_286065_(blockpos, blockstate, entity$movementemission.m_146946_(), flag2, p_19974_);
                  if (!flag2) {
                     flag3 |= this.m_286065_(blockpos1, blockstate1, false, entity$movementemission.m_146945_(), p_19974_);
                  }

                  if (flag3) {
                     this.f_19829_ = this.m_6059_();
                  } else if (this.m_20069_()) {
                     this.f_19829_ = this.m_6059_();
                     if (entity$movementemission.m_146946_()) {
                        this.m_280447_();
                     }

                     if (entity$movementemission.m_146945_()) {
                        this.m_146850_(GameEvent.f_157786_);
                     }
                  }
               } else if (blockstate1.m_60795_()) {
                  this.m_146874_();
               }
            }

            this.m_146872_();
            float f = this.m_6041_();
            this.m_20256_(this.m_20184_().m_82542_((double)f, 1.0D, (double)f));
            if (this.m_9236_().m_46847_(this.m_20191_().m_82406_(1.0E-6D)).noneMatch((p_20127_) -> {
               return p_20127_.m_204336_(BlockTags.f_13076_) || p_20127_.m_60713_(Blocks.f_49991_);
            })) {
               if (this.f_19831_ <= 0) {
                  this.m_7311_(-this.m_6101_());
               }

               if (this.f_146810_ && (this.f_146808_ || this.m_20071_() || this.isInFluidType((fluidType, height) -> this.canFluidExtinguish(fluidType)))) {
                  this.m_146873_();
               }
            }

            if (this.m_6060_() && (this.f_146808_ || this.m_20071_() || this.isInFluidType((fluidType, height) -> this.canFluidExtinguish(fluidType)))) {
               this.m_7311_(-this.m_6101_());
            }

            this.f_19853_.m_46473_().m_7238_();
         }
      }
   }

   private boolean m_285776_(BlockState p_286733_) {
      return p_286733_.m_204336_(BlockTags.f_13082_) || p_286733_.m_60713_(Blocks.f_152499_);
   }

   private boolean m_286065_(BlockPos p_286221_, BlockState p_286549_, boolean p_286708_, boolean p_286543_, Vec3 p_286448_) {
      if (p_286549_.m_60795_()) {
         return false;
      } else {
         boolean flag = this.m_285776_(p_286549_);
         if ((this.m_20096_() || flag || this.m_6047_() && p_286448_.f_82480_ == 0.0D || this.m_288188_()) && !this.m_6069_()) {
            if (p_286708_) {
               this.m_280440_(p_286221_, p_286549_);
            }

            if (p_286543_) {
               this.m_9236_().m_214171_(GameEvent.f_157785_, this.m_20182_(), GameEvent.Context.m_223719_(this, p_286549_));
            }

            return true;
         } else {
            return false;
         }
      }
   }

   protected boolean m_196406_(Vec3 p_196625_) {
      return false;
   }

   protected void m_146872_() {
      try {
         this.m_20101_();
      } catch (Throwable throwable) {
         CrashReport crashreport = CrashReport.m_127521_(throwable, "Checking entity block collision");
         CrashReportCategory crashreportcategory = crashreport.m_127514_("Entity being checked for collision");
         this.m_7976_(crashreportcategory);
         throw new ReportedException(crashreport);
      }
   }

   protected void m_146873_() {
      this.m_5496_(SoundEvents.f_11914_, 0.7F, 1.6F + (this.f_19796_.m_188501_() - this.f_19796_.m_188501_()) * 0.4F);
   }

   public void m_252836_() {
      if (!this.m_9236_().f_46443_ && this.f_146810_) {
         this.m_146873_();
      }

      this.m_20095_();
   }

   protected void m_146874_() {
      if (this.m_142039_()) {
         this.m_142043_();
         if (this.m_142319_().m_146945_()) {
            this.m_146850_(GameEvent.f_157815_);
         }
      }

   }

   /** @deprecated */
   @Deprecated
   public BlockPos m_216999_() {
      return this.m_216986_(0.2F);
   }

   protected BlockPos m_20099_() {
      return this.m_216986_(0.500001F);
   }

   public BlockPos m_20097_() {
      return this.m_216986_(1.0E-5F);
   }

   protected BlockPos m_216986_(float p_216987_) {
      if (this.f_285638_.isPresent()) {
         BlockPos blockpos = this.f_285638_.get();
         if (!(p_216987_ > 1.0E-5F)) {
            return blockpos;
         } else {
            BlockState blockstate = this.m_9236_().m_8055_(blockpos);
            return (!((double)p_216987_ <= 0.5D) || !blockstate.collisionExtendsVertically(this.m_9236_(), blockpos, this)) ? blockpos.m_175288_(Mth.m_14107_(this.f_19825_.f_82480_ - (double)p_216987_)) : blockpos;
         }
      } else {
         int i = Mth.m_14107_(this.f_19825_.f_82479_);
         int j = Mth.m_14107_(this.f_19825_.f_82480_ - (double)p_216987_);
         int k = Mth.m_14107_(this.f_19825_.f_82481_);
         return new BlockPos(i, j, k);
      }
   }

   protected float m_20098_() {
      float f = this.m_9236_().m_8055_(this.m_20183_()).m_60734_().m_49964_();
      float f1 = this.m_9236_().m_8055_(this.m_20099_()).m_60734_().m_49964_();
      return (double)f == 1.0D ? f1 : f;
   }

   protected float m_6041_() {
      BlockState blockstate = this.m_9236_().m_8055_(this.m_20183_());
      float f = blockstate.m_60734_().m_49961_();
      if (!blockstate.m_60713_(Blocks.f_49990_) && !blockstate.m_60713_(Blocks.f_50628_)) {
         return (double)f == 1.0D ? this.m_9236_().m_8055_(this.m_20099_()).m_60734_().m_49961_() : f;
      } else {
         return f;
      }
   }

   protected Vec3 m_5763_(Vec3 p_20019_, MoverType p_20020_) {
      return p_20019_;
   }

   protected Vec3 m_20133_(Vec3 p_20134_) {
      if (p_20134_.m_82556_() <= 1.0E-7D) {
         return p_20134_;
      } else {
         long i = this.m_9236_().m_46467_();
         if (i != this.f_19814_) {
            Arrays.fill(this.f_19813_, 0.0D);
            this.f_19814_ = i;
         }

         if (p_20134_.f_82479_ != 0.0D) {
            double d2 = this.m_20042_(Direction.Axis.X, p_20134_.f_82479_);
            return Math.abs(d2) <= (double)1.0E-5F ? Vec3.f_82478_ : new Vec3(d2, 0.0D, 0.0D);
         } else if (p_20134_.f_82480_ != 0.0D) {
            double d1 = this.m_20042_(Direction.Axis.Y, p_20134_.f_82480_);
            return Math.abs(d1) <= (double)1.0E-5F ? Vec3.f_82478_ : new Vec3(0.0D, d1, 0.0D);
         } else if (p_20134_.f_82481_ != 0.0D) {
            double d0 = this.m_20042_(Direction.Axis.Z, p_20134_.f_82481_);
            return Math.abs(d0) <= (double)1.0E-5F ? Vec3.f_82478_ : new Vec3(0.0D, 0.0D, d0);
         } else {
            return Vec3.f_82478_;
         }
      }
   }

   private double m_20042_(Direction.Axis p_20043_, double p_20044_) {
      int i = p_20043_.ordinal();
      double d0 = Mth.m_14008_(p_20044_ + this.f_19813_[i], -0.51D, 0.51D);
      p_20044_ = d0 - this.f_19813_[i];
      this.f_19813_[i] = d0;
      return p_20044_;
   }

   private Vec3 m_20272_(Vec3 p_20273_) {
      AABB aabb = this.m_20191_();
      List<VoxelShape> list = this.m_9236_().m_183134_(this, aabb.m_82369_(p_20273_));
      Vec3 vec3 = p_20273_.m_82556_() == 0.0D ? p_20273_ : m_198894_(this, p_20273_, aabb, this.m_9236_(), list);
      boolean flag = p_20273_.f_82479_ != vec3.f_82479_;
      boolean flag1 = p_20273_.f_82480_ != vec3.f_82480_;
      boolean flag2 = p_20273_.f_82481_ != vec3.f_82481_;
      boolean flag3 = this.m_20096_() || flag1 && p_20273_.f_82480_ < 0.0D;
      float stepHeight = getStepHeight();
      if (stepHeight > 0.0F && flag3 && (flag || flag2)) {
         Vec3 vec31 = m_198894_(this, new Vec3(p_20273_.f_82479_, (double)stepHeight, p_20273_.f_82481_), aabb, this.f_19853_, list);
         Vec3 vec32 = m_198894_(this, new Vec3(0.0D, (double)stepHeight, 0.0D), aabb.m_82363_(p_20273_.f_82479_, 0.0D, p_20273_.f_82481_), this.f_19853_, list);
         if (vec32.f_82480_ < (double)stepHeight) {
            Vec3 vec33 = m_198894_(this, new Vec3(p_20273_.f_82479_, 0.0D, p_20273_.f_82481_), aabb.m_82383_(vec32), this.m_9236_(), list).m_82549_(vec32);
            if (vec33.m_165925_() > vec31.m_165925_()) {
               vec31 = vec33;
            }
         }

         if (vec31.m_165925_() > vec3.m_165925_()) {
            return vec31.m_82549_(m_198894_(this, new Vec3(0.0D, -vec31.f_82480_ + p_20273_.f_82480_, 0.0D), aabb.m_82383_(vec31), this.m_9236_(), list));
         }
      }

      return vec3;
   }

   public static Vec3 m_198894_(@Nullable Entity p_198895_, Vec3 p_198896_, AABB p_198897_, Level p_198898_, List<VoxelShape> p_198899_) {
      ImmutableList.Builder<VoxelShape> builder = ImmutableList.builderWithExpectedSize(p_198899_.size() + 1);
      if (!p_198899_.isEmpty()) {
         builder.addAll(p_198899_);
      }

      WorldBorder worldborder = p_198898_.m_6857_();
      boolean flag = p_198895_ != null && worldborder.m_187566_(p_198895_, p_198897_.m_82369_(p_198896_));
      if (flag) {
         builder.add(worldborder.m_61946_());
      }

      builder.addAll(p_198898_.m_186434_(p_198895_, p_198897_.m_82369_(p_198896_)));
      return m_198900_(p_198896_, p_198897_, builder.build());
   }

   private static Vec3 m_198900_(Vec3 p_198901_, AABB p_198902_, List<VoxelShape> p_198903_) {
      if (p_198903_.isEmpty()) {
         return p_198901_;
      } else {
         double d0 = p_198901_.f_82479_;
         double d1 = p_198901_.f_82480_;
         double d2 = p_198901_.f_82481_;
         if (d1 != 0.0D) {
            d1 = Shapes.m_193135_(Direction.Axis.Y, p_198902_, p_198903_, d1);
            if (d1 != 0.0D) {
               p_198902_ = p_198902_.m_82386_(0.0D, d1, 0.0D);
            }
         }

         boolean flag = Math.abs(d0) < Math.abs(d2);
         if (flag && d2 != 0.0D) {
            d2 = Shapes.m_193135_(Direction.Axis.Z, p_198902_, p_198903_, d2);
            if (d2 != 0.0D) {
               p_198902_ = p_198902_.m_82386_(0.0D, 0.0D, d2);
            }
         }

         if (d0 != 0.0D) {
            d0 = Shapes.m_193135_(Direction.Axis.X, p_198902_, p_198903_, d0);
            if (!flag && d0 != 0.0D) {
               p_198902_ = p_198902_.m_82386_(d0, 0.0D, 0.0D);
            }
         }

         if (!flag && d2 != 0.0D) {
            d2 = Shapes.m_193135_(Direction.Axis.Z, p_198902_, p_198903_, d2);
         }

         return new Vec3(d0, d1, d2);
      }
   }

   protected float m_6059_() {
      return (float)((int)this.f_19788_ + 1);
   }

   protected SoundEvent m_5501_() {
      return SoundEvents.f_11918_;
   }

   protected SoundEvent m_5509_() {
      return SoundEvents.f_11917_;
   }

   protected SoundEvent m_5508_() {
      return SoundEvents.f_11917_;
   }

   protected void m_20101_() {
      AABB aabb = this.m_20191_();
      BlockPos blockpos = BlockPos.m_274561_(aabb.f_82288_ + 1.0E-7D, aabb.f_82289_ + 1.0E-7D, aabb.f_82290_ + 1.0E-7D);
      BlockPos blockpos1 = BlockPos.m_274561_(aabb.f_82291_ - 1.0E-7D, aabb.f_82292_ - 1.0E-7D, aabb.f_82293_ - 1.0E-7D);
      if (this.m_9236_().m_46832_(blockpos, blockpos1)) {
         BlockPos.MutableBlockPos blockpos$mutableblockpos = new BlockPos.MutableBlockPos();

         for(int i = blockpos.m_123341_(); i <= blockpos1.m_123341_(); ++i) {
            for(int j = blockpos.m_123342_(); j <= blockpos1.m_123342_(); ++j) {
               for(int k = blockpos.m_123343_(); k <= blockpos1.m_123343_(); ++k) {
                  blockpos$mutableblockpos.m_122178_(i, j, k);
                  BlockState blockstate = this.m_9236_().m_8055_(blockpos$mutableblockpos);

                  try {
                     blockstate.m_60682_(this.m_9236_(), blockpos$mutableblockpos, this);
                     this.m_6763_(blockstate);
                  } catch (Throwable throwable) {
                     CrashReport crashreport = CrashReport.m_127521_(throwable, "Colliding entity with block");
                     CrashReportCategory crashreportcategory = crashreport.m_127514_("Block being collided with");
                     CrashReportCategory.m_178950_(crashreportcategory, this.m_9236_(), blockpos$mutableblockpos, blockstate);
                     throw new ReportedException(crashreport);
                  }
               }
            }
         }
      }

   }

   protected void m_6763_(BlockState p_20005_) {
   }

   public void m_146852_(GameEvent p_146853_, @Nullable Entity p_146854_) {
      this.m_9236_().m_220400_(p_146854_, p_146853_, this.f_19825_);
   }

   public void m_146850_(GameEvent p_146851_) {
      this.m_146852_(p_146851_, this);
   }

   private void m_280440_(BlockPos p_281828_, BlockState p_282118_) {
      this.m_7355_(p_281828_, p_282118_);
      if (this.m_277063_(p_282118_)) {
         this.m_277116_();
      }

   }

   protected void m_280447_() {
      Entity entity = (Entity)(this.m_20160_() && this.m_6688_() != null ? this.m_6688_() : this);
      float f = entity == this ? 0.35F : 0.4F;
      Vec3 vec3 = entity.m_20184_();
      float f1 = Math.min(1.0F, (float)Math.sqrt(vec3.f_82479_ * vec3.f_82479_ * (double)0.2F + vec3.f_82480_ * vec3.f_82480_ + vec3.f_82481_ * vec3.f_82481_ * (double)0.2F) * f);
      this.m_5625_(f1);
   }

   protected BlockPos m_276951_(BlockPos p_278049_) {
      BlockPos blockpos = p_278049_.m_7494_();
      BlockState blockstate = this.m_9236_().m_8055_(blockpos);
      return !blockstate.m_204336_(BlockTags.f_144271_) && !blockstate.m_204336_(BlockTags.f_276549_) ? p_278049_ : blockpos;
   }

   protected void playCombinationStepSounds(BlockState p_277472_, BlockState p_277630_, BlockPos primaryPos, BlockPos secondaryPos) {
      SoundType soundtype = p_277472_.getSoundType(this.f_19853_, primaryPos, this);
      SoundType soundtype1 = p_277630_.getSoundType(this.f_19853_, secondaryPos, this);
      this.m_5496_(soundtype.m_56776_(), soundtype.m_56773_() * 0.15F, soundtype.m_56774_());
      this.playMuffledStepSound(p_277630_, secondaryPos);
   }

   protected void playMuffledStepSound(BlockState p_283110_, BlockPos pos) {
      SoundType soundtype = p_283110_.getSoundType(this.f_19853_, pos, this);
      this.m_5496_(soundtype.m_56776_(), soundtype.m_56773_() * 0.05F, soundtype.m_56774_() * 0.8F);
   }

   protected void m_7355_(BlockPos p_20135_, BlockState p_20136_) {
      SoundType soundtype = p_20136_.getSoundType(this.f_19853_, p_20135_, this);
      this.m_5496_(soundtype.m_56776_(), soundtype.m_56773_() * 0.15F, soundtype.m_56774_());
   }

   private boolean m_277063_(BlockState p_278069_) {
      return p_278069_.m_204336_(BlockTags.f_144270_) && this.f_19797_ >= this.f_146804_ + 20;
   }

   private void m_277116_() {
      this.f_146803_ *= (float)Math.pow(0.997D, (double)(this.f_19797_ - this.f_146804_));
      this.f_146803_ = Math.min(1.0F, this.f_146803_ + 0.07F);
      float f = 0.5F + this.f_146803_ * this.f_19796_.m_188501_() * 1.2F;
      float f1 = 0.1F + this.f_146803_ * 1.2F;
      this.m_5496_(SoundEvents.f_144243_, f1, f);
      this.f_146804_ = this.f_19797_;
   }

   protected void m_5625_(float p_20213_) {
      this.m_5496_(this.m_5501_(), p_20213_, 1.0F + (this.f_19796_.m_188501_() - this.f_19796_.m_188501_()) * 0.4F);
   }

   protected void m_142043_() {
   }

   protected boolean m_142039_() {
      return false;
   }

   public void m_5496_(SoundEvent p_19938_, float p_19939_, float p_19940_) {
      if (!this.m_20067_()) {
         this.m_9236_().m_6263_((Player)null, this.m_20185_(), this.m_20186_(), this.m_20189_(), p_19938_, this.m_5720_(), p_19939_, p_19940_);
      }

   }

   public void m_216990_(SoundEvent p_216991_) {
      if (!this.m_20067_()) {
         this.m_5496_(p_216991_, 1.0F, 1.0F);
      }

   }

   public boolean m_20067_() {
      return this.f_19804_.m_135370_(f_19835_);
   }

   public void m_20225_(boolean p_20226_) {
      this.f_19804_.m_135381_(f_19835_, p_20226_);
   }

   public boolean m_20068_() {
      return this.f_19804_.m_135370_(f_19836_);
   }

   public void m_20242_(boolean p_20243_) {
      this.f_19804_.m_135381_(f_19836_, p_20243_);
   }

   protected Entity.MovementEmission m_142319_() {
      return Entity.MovementEmission.ALL;
   }

   public boolean m_213854_() {
      return false;
   }

   protected void m_7840_(double p_19911_, boolean p_19912_, BlockState p_19913_, BlockPos p_19914_) {
      if (p_19912_) {
         if (this.f_19789_ > 0.0F) {
            p_19913_.m_60734_().m_142072_(this.m_9236_(), p_19913_, p_19914_, this, this.f_19789_);
            this.m_9236_().m_214171_(GameEvent.f_157770_, this.f_19825_, GameEvent.Context.m_223719_(this, this.f_285638_.map((p_286200_) -> {
               return this.m_9236_().m_8055_(p_286200_);
            }).orElse(p_19913_)));
         }

         this.m_183634_();
      } else if (p_19911_ < 0.0D) {
         this.f_19789_ -= (float)p_19911_;
      }

   }

   public boolean m_5825_() {
      return this.m_6095_().m_20672_();
   }

   public boolean m_142535_(float p_146828_, float p_146829_, DamageSource p_146830_) {
      if (this.f_19847_.m_204039_(EntityTypeTags.f_273841_)) {
         return false;
      } else {
         if (this.m_20160_()) {
            for(Entity entity : this.m_20197_()) {
               entity.m_142535_(p_146828_, p_146829_, p_146830_);
            }
         }

         return false;
      }
   }

   public boolean m_20069_() {
      return this.f_19798_;
   }

   private boolean m_20285_() {
      BlockPos blockpos = this.m_20183_();
      return this.m_9236_().m_46758_(blockpos) || this.m_9236_().m_46758_(BlockPos.m_274561_((double)blockpos.m_123341_(), this.m_20191_().f_82292_, (double)blockpos.m_123343_()));
   }

   private boolean m_20305_() {
      return this.m_9236_().m_8055_(this.m_20183_()).m_60713_(Blocks.f_50628_);
   }

   public boolean m_20070_() {
      return this.m_20069_() || this.m_20285_();
   }

   public boolean m_20071_() {
      return this.m_20069_() || this.m_20285_() || this.m_20305_();
   }

   public boolean m_20072_() {
      return this.m_20069_() || this.m_20305_();
   }

   public boolean m_5842_() {
      return this.f_19800_ && this.m_20069_();
   }

   public void m_5844_() {
      if (this.m_6069_()) {
         this.m_20282_(this.m_20142_() && (this.m_20069_() || this.isInFluidType((fluidType, height) -> this.canSwimInFluidType(fluidType))) && !this.m_20159_());
      } else {
         this.m_20282_(this.m_20142_() && (this.m_5842_() || this.canStartSwimming()) && !this.m_20159_());
      }

   }

   protected boolean m_20073_() {
      this.f_19799_.clear();
      this.forgeFluidTypeHeight.clear();
      this.m_20074_();
      if (!(this.m_20202_() instanceof Boat)) {
         this.f_19789_ *= this.forgeFluidTypeHeight.object2DoubleEntrySet().stream().filter(e -> !e.getKey().isAir() && !e.getKey().isVanilla()).map(e -> this.getFluidFallDistanceModifier(e.getKey())).min(Float::compare).orElse(1F);
         if (this.isInFluidType((fluidType, height) -> !fluidType.isAir() && !fluidType.isVanilla() && this.canFluidExtinguish(fluidType))) this.m_20095_();
      }
      return this.isInFluidType();
   }

   void m_20074_() {
      Entity entity = this.m_20202_();
      if (entity instanceof Boat boat) {
         if (!boat.m_5842_()) {
            this.f_19798_ = false;
            return;
         }
      }

      if (this.m_204031_(FluidTags.f_13131_, 0.014D)) {
         if (!this.f_19798_ && !this.f_19803_) {
            this.m_5841_();
         }

         this.m_183634_();
         this.f_19798_ = true;
         this.m_20095_();
      } else {
         this.f_19798_ = false;
      }

   }

   private void m_20323_() {
      this.f_19800_ = this.m_204029_(FluidTags.f_13131_);
      this.f_19801_.clear();
      this.forgeFluidTypeOnEyes = net.minecraftforge.common.ForgeMod.EMPTY_TYPE.get();
      double d0 = this.m_20188_() - (double)0.11111111F;
      Entity entity = this.m_20202_();
      if (entity instanceof Boat boat) {
         if (!boat.m_5842_() && boat.m_20191_().f_82292_ >= d0 && boat.m_20191_().f_82289_ <= d0) {
            return;
         }
      }

      BlockPos blockpos = BlockPos.m_274561_(this.m_20185_(), d0, this.m_20189_());
      FluidState fluidstate = this.m_9236_().m_6425_(blockpos);
      double d1 = (double)((float)blockpos.m_123342_() + fluidstate.m_76155_(this.m_9236_(), blockpos));
      if (d1 > d0) {
         this.forgeFluidTypeOnEyes = fluidstate.getFluidType();
      }

   }

   protected void m_5841_() {
      Entity entity = (Entity)(this.m_20160_() && this.m_6688_() != null ? this.m_6688_() : this);
      float f = entity == this ? 0.2F : 0.9F;
      Vec3 vec3 = entity.m_20184_();
      float f1 = Math.min(1.0F, (float)Math.sqrt(vec3.f_82479_ * vec3.f_82479_ * (double)0.2F + vec3.f_82480_ * vec3.f_82480_ + vec3.f_82481_ * vec3.f_82481_ * (double)0.2F) * f);
      if (f1 < 0.25F) {
         this.m_5496_(this.m_5509_(), f1, 1.0F + (this.f_19796_.m_188501_() - this.f_19796_.m_188501_()) * 0.4F);
      } else {
         this.m_5496_(this.m_5508_(), f1, 1.0F + (this.f_19796_.m_188501_() - this.f_19796_.m_188501_()) * 0.4F);
      }

      float f2 = (float)Mth.m_14107_(this.m_20186_());

      for(int i = 0; (float)i < 1.0F + this.f_19815_.f_20377_ * 20.0F; ++i) {
         double d0 = (this.f_19796_.m_188500_() * 2.0D - 1.0D) * (double)this.f_19815_.f_20377_;
         double d1 = (this.f_19796_.m_188500_() * 2.0D - 1.0D) * (double)this.f_19815_.f_20377_;
         this.m_9236_().m_7106_(ParticleTypes.f_123795_, this.m_20185_() + d0, (double)(f2 + 1.0F), this.m_20189_() + d1, vec3.f_82479_, vec3.f_82480_ - this.f_19796_.m_188500_() * (double)0.2F, vec3.f_82481_);
      }

      for(int j = 0; (float)j < 1.0F + this.f_19815_.f_20377_ * 20.0F; ++j) {
         double d2 = (this.f_19796_.m_188500_() * 2.0D - 1.0D) * (double)this.f_19815_.f_20377_;
         double d3 = (this.f_19796_.m_188500_() * 2.0D - 1.0D) * (double)this.f_19815_.f_20377_;
         this.m_9236_().m_7106_(ParticleTypes.f_123769_, this.m_20185_() + d2, (double)(f2 + 1.0F), this.m_20189_() + d3, vec3.f_82479_, vec3.f_82480_, vec3.f_82481_);
      }

      this.m_146850_(GameEvent.f_157784_);
   }

   /** @deprecated */
   @Deprecated
   protected BlockState m_217002_() {
      return this.m_9236_().m_8055_(this.m_216999_());
   }

   public BlockState m_20075_() {
      return this.m_9236_().m_8055_(this.m_20097_());
   }

   public boolean m_5843_() {
      return this.m_20142_() && !this.m_20069_() && !this.m_5833_() && !this.m_6047_() && !this.m_20077_() && this.m_6084_() && !this.isInFluidType();
   }

   protected void m_20076_() {
      BlockPos blockpos = this.m_216999_();
      BlockState blockstate = this.m_9236_().m_8055_(blockpos);
      if(!blockstate.addRunningEffects(f_19853_, blockpos, this))
      if (blockstate.m_60799_() != RenderShape.INVISIBLE) {
         Vec3 vec3 = this.m_20184_();
         BlockPos blockpos1 = this.m_20183_();
         double d0 = this.m_20185_() + (this.f_19796_.m_188500_() - 0.5D) * (double)this.f_19815_.f_20377_;
         double d1 = this.m_20189_() + (this.f_19796_.m_188500_() - 0.5D) * (double)this.f_19815_.f_20377_;
         if (blockpos1.m_123341_() != blockpos.m_123341_()) {
            d0 = Mth.m_14008_(d0, (double)blockpos.m_123341_(), (double)blockpos.m_123341_() + 1.0D);
         }

         if (blockpos1.m_123343_() != blockpos.m_123343_()) {
            d1 = Mth.m_14008_(d1, (double)blockpos.m_123343_(), (double)blockpos.m_123343_() + 1.0D);
         }

         this.m_9236_().m_7106_(new BlockParticleOption(ParticleTypes.f_123794_, blockstate).setPos(blockpos), d0, this.m_20186_() + 0.1D, d1, vec3.f_82479_ * -4.0D, 1.5D, vec3.f_82481_ * -4.0D);
      }

   }

   @Deprecated // Forge: Use isEyeInFluidType instead
   public boolean m_204029_(TagKey<Fluid> p_204030_) {
      if (p_204030_ == FluidTags.f_13131_) return this.isEyeInFluidType(net.minecraftforge.common.ForgeMod.WATER_TYPE.get());
      else if (p_204030_ == FluidTags.f_13132_) return this.isEyeInFluidType(net.minecraftforge.common.ForgeMod.LAVA_TYPE.get());
      return this.f_19801_.contains(p_204030_);
   }

   public boolean m_20077_() {
      return !this.f_19803_ && this.forgeFluidTypeHeight.getDouble(net.minecraftforge.common.ForgeMod.LAVA_TYPE.get()) > 0.0D;
   }

   public void m_19920_(float p_19921_, Vec3 p_19922_) {
      Vec3 vec3 = m_20015_(p_19922_, p_19921_, this.m_146908_());
      this.m_20256_(this.m_20184_().m_82549_(vec3));
   }

   private static Vec3 m_20015_(Vec3 p_20016_, float p_20017_, float p_20018_) {
      double d0 = p_20016_.m_82556_();
      if (d0 < 1.0E-7D) {
         return Vec3.f_82478_;
      } else {
         Vec3 vec3 = (d0 > 1.0D ? p_20016_.m_82541_() : p_20016_).m_82490_((double)p_20017_);
         float f = Mth.m_14031_(p_20018_ * ((float)Math.PI / 180F));
         float f1 = Mth.m_14089_(p_20018_ * ((float)Math.PI / 180F));
         return new Vec3(vec3.f_82479_ * (double)f1 - vec3.f_82481_ * (double)f, vec3.f_82480_, vec3.f_82481_ * (double)f1 + vec3.f_82479_ * (double)f);
      }
   }

   /** @deprecated */
   @Deprecated
   public float m_213856_() {
      return this.m_9236_().m_151577_(this.m_146903_(), this.m_146907_()) ? this.m_9236_().m_220417_(BlockPos.m_274561_(this.m_20185_(), this.m_20188_(), this.m_20189_())) : 0.0F;
   }

   public void m_19890_(double p_19891_, double p_19892_, double p_19893_, float p_19894_, float p_19895_) {
      this.m_20248_(p_19891_, p_19892_, p_19893_);
      this.m_146922_(p_19894_ % 360.0F);
      this.m_146926_(Mth.m_14036_(p_19895_, -90.0F, 90.0F) % 360.0F);
      this.f_19859_ = this.m_146908_();
      this.f_19860_ = this.m_146909_();
   }

   public void m_20248_(double p_20249_, double p_20250_, double p_20251_) {
      double d0 = Mth.m_14008_(p_20249_, -3.0E7D, 3.0E7D);
      double d1 = Mth.m_14008_(p_20251_, -3.0E7D, 3.0E7D);
      this.f_19854_ = d0;
      this.f_19855_ = p_20250_;
      this.f_19856_ = d1;
      this.m_6034_(d0, p_20250_, d1);
   }

   public void m_20219_(Vec3 p_20220_) {
      this.m_6027_(p_20220_.f_82479_, p_20220_.f_82480_, p_20220_.f_82481_);
   }

   public void m_6027_(double p_20105_, double p_20106_, double p_20107_) {
      this.m_7678_(p_20105_, p_20106_, p_20107_, this.m_146908_(), this.m_146909_());
   }

   public void m_20035_(BlockPos p_20036_, float p_20037_, float p_20038_) {
      this.m_7678_((double)p_20036_.m_123341_() + 0.5D, (double)p_20036_.m_123342_(), (double)p_20036_.m_123343_() + 0.5D, p_20037_, p_20038_);
   }

   public void m_7678_(double p_20108_, double p_20109_, double p_20110_, float p_20111_, float p_20112_) {
      this.m_20343_(p_20108_, p_20109_, p_20110_);
      this.m_146922_(p_20111_);
      this.m_146926_(p_20112_);
      this.m_146867_();
      this.m_20090_();
   }

   public final void m_146867_() {
      double d0 = this.m_20185_();
      double d1 = this.m_20186_();
      double d2 = this.m_20189_();
      this.f_19854_ = d0;
      this.f_19855_ = d1;
      this.f_19856_ = d2;
      this.f_19790_ = d0;
      this.f_19791_ = d1;
      this.f_19792_ = d2;
      this.f_19859_ = this.m_146908_();
      this.f_19860_ = this.m_146909_();
   }

   public float m_20270_(Entity p_20271_) {
      float f = (float)(this.m_20185_() - p_20271_.m_20185_());
      float f1 = (float)(this.m_20186_() - p_20271_.m_20186_());
      float f2 = (float)(this.m_20189_() - p_20271_.m_20189_());
      return Mth.m_14116_(f * f + f1 * f1 + f2 * f2);
   }

   public double m_20275_(double p_20276_, double p_20277_, double p_20278_) {
      double d0 = this.m_20185_() - p_20276_;
      double d1 = this.m_20186_() - p_20277_;
      double d2 = this.m_20189_() - p_20278_;
      return d0 * d0 + d1 * d1 + d2 * d2;
   }

   public double m_20280_(Entity p_20281_) {
      return this.m_20238_(p_20281_.m_20182_());
   }

   public double m_20238_(Vec3 p_20239_) {
      double d0 = this.m_20185_() - p_20239_.f_82479_;
      double d1 = this.m_20186_() - p_20239_.f_82480_;
      double d2 = this.m_20189_() - p_20239_.f_82481_;
      return d0 * d0 + d1 * d1 + d2 * d2;
   }

   public void m_6123_(Player p_20081_) {
   }

   public void m_7334_(Entity p_20293_) {
      if (!this.m_20365_(p_20293_)) {
         if (!p_20293_.f_19794_ && !this.f_19794_) {
            double d0 = p_20293_.m_20185_() - this.m_20185_();
            double d1 = p_20293_.m_20189_() - this.m_20189_();
            double d2 = Mth.m_14005_(d0, d1);
            if (d2 >= (double)0.01F) {
               d2 = Math.sqrt(d2);
               d0 /= d2;
               d1 /= d2;
               double d3 = 1.0D / d2;
               if (d3 > 1.0D) {
                  d3 = 1.0D;
               }

               d0 *= d3;
               d1 *= d3;
               d0 *= (double)0.05F;
               d1 *= (double)0.05F;
               if (!this.m_20160_() && this.m_6094_()) {
                  this.m_5997_(-d0, 0.0D, -d1);
               }

               if (!p_20293_.m_20160_() && p_20293_.m_6094_()) {
                  p_20293_.m_5997_(d0, 0.0D, d1);
               }
            }

         }
      }
   }

   public void m_5997_(double p_20286_, double p_20287_, double p_20288_) {
      this.m_20256_(this.m_20184_().m_82520_(p_20286_, p_20287_, p_20288_));
      this.f_19812_ = true;
   }

   protected void m_5834_() {
      this.f_19864_ = true;
   }

   public boolean m_6469_(DamageSource p_19946_, float p_19947_) {
      if (this.m_6673_(p_19946_)) {
         return false;
      } else {
         this.m_5834_();
         return false;
      }
   }

   public final Vec3 m_20252_(float p_20253_) {
      return this.m_20171_(this.m_5686_(p_20253_), this.m_5675_(p_20253_));
   }

   public float m_5686_(float p_20268_) {
      return p_20268_ == 1.0F ? this.m_146909_() : Mth.m_14179_(p_20268_, this.f_19860_, this.m_146909_());
   }

   public float m_5675_(float p_20279_) {
      return p_20279_ == 1.0F ? this.m_146908_() : Mth.m_14179_(p_20279_, this.f_19859_, this.m_146908_());
   }

   protected final Vec3 m_20171_(float p_20172_, float p_20173_) {
      float f = p_20172_ * ((float)Math.PI / 180F);
      float f1 = -p_20173_ * ((float)Math.PI / 180F);
      float f2 = Mth.m_14089_(f1);
      float f3 = Mth.m_14031_(f1);
      float f4 = Mth.m_14089_(f);
      float f5 = Mth.m_14031_(f);
      return new Vec3((double)(f3 * f4), (double)(-f5), (double)(f2 * f4));
   }

   public final Vec3 m_20289_(float p_20290_) {
      return this.m_20214_(this.m_5686_(p_20290_), this.m_5675_(p_20290_));
   }

   protected final Vec3 m_20214_(float p_20215_, float p_20216_) {
      return this.m_20171_(p_20215_ - 90.0F, p_20216_);
   }

   public final Vec3 m_146892_() {
      return new Vec3(this.m_20185_(), this.m_20188_(), this.m_20189_());
   }

   public final Vec3 m_20299_(float p_20300_) {
      double d0 = Mth.m_14139_((double)p_20300_, this.f_19854_, this.m_20185_());
      double d1 = Mth.m_14139_((double)p_20300_, this.f_19855_, this.m_20186_()) + (double)this.m_20192_();
      double d2 = Mth.m_14139_((double)p_20300_, this.f_19856_, this.m_20189_());
      return new Vec3(d0, d1, d2);
   }

   public Vec3 m_7371_(float p_20309_) {
      return this.m_20299_(p_20309_);
   }

   public final Vec3 m_20318_(float p_20319_) {
      double d0 = Mth.m_14139_((double)p_20319_, this.f_19854_, this.m_20185_());
      double d1 = Mth.m_14139_((double)p_20319_, this.f_19855_, this.m_20186_());
      double d2 = Mth.m_14139_((double)p_20319_, this.f_19856_, this.m_20189_());
      return new Vec3(d0, d1, d2);
   }

   public HitResult m_19907_(double p_19908_, float p_19909_, boolean p_19910_) {
      Vec3 vec3 = this.m_20299_(p_19909_);
      Vec3 vec31 = this.m_20252_(p_19909_);
      Vec3 vec32 = vec3.m_82520_(vec31.f_82479_ * p_19908_, vec31.f_82480_ * p_19908_, vec31.f_82481_ * p_19908_);
      return this.m_9236_().m_45547_(new ClipContext(vec3, vec32, ClipContext.Block.OUTLINE, p_19910_ ? ClipContext.Fluid.ANY : ClipContext.Fluid.NONE, this));
   }

   public boolean m_271807_() {
      return this.m_6084_() && this.m_6087_();
   }

   public boolean m_6087_() {
      return false;
   }

   public boolean m_6094_() {
      return false;
   }

   public void m_5993_(Entity p_19953_, int p_19954_, DamageSource p_19955_) {
      if (p_19953_ instanceof ServerPlayer) {
         CriteriaTriggers.f_10569_.m_48104_((ServerPlayer)p_19953_, this, p_19955_);
      }

   }

   public boolean m_6000_(double p_20296_, double p_20297_, double p_20298_) {
      double d0 = this.m_20185_() - p_20296_;
      double d1 = this.m_20186_() - p_20297_;
      double d2 = this.m_20189_() - p_20298_;
      double d3 = d0 * d0 + d1 * d1 + d2 * d2;
      return this.m_6783_(d3);
   }

   public boolean m_6783_(double p_19883_) {
      double d0 = this.m_20191_().m_82309_();
      if (Double.isNaN(d0)) {
         d0 = 1.0D;
      }

      d0 *= 64.0D * f_19846_;
      return p_19883_ < d0 * d0;
   }

   public boolean m_20086_(CompoundTag p_20087_) {
      if (this.f_146795_ != null && !this.f_146795_.m_146966_()) {
         return false;
      } else {
         String s = this.m_20078_();
         if (s == null) {
            return false;
         } else {
            p_20087_.m_128359_("id", s);
            this.m_20240_(p_20087_);
            return true;
         }
      }
   }

   public boolean m_20223_(CompoundTag p_20224_) {
      return this.m_20159_() ? false : this.m_20086_(p_20224_);
   }

   public CompoundTag m_20240_(CompoundTag p_20241_) {
      try {
         if (this.f_19824_ != null) {
            p_20241_.m_128365_("Pos", this.m_20063_(this.f_19824_.m_20185_(), this.m_20186_(), this.f_19824_.m_20189_()));
         } else {
            p_20241_.m_128365_("Pos", this.m_20063_(this.m_20185_(), this.m_20186_(), this.m_20189_()));
         }

         Vec3 vec3 = this.m_20184_();
         p_20241_.m_128365_("Motion", this.m_20063_(vec3.f_82479_, vec3.f_82480_, vec3.f_82481_));
         p_20241_.m_128365_("Rotation", this.m_20065_(this.m_146908_(), this.m_146909_()));
         p_20241_.m_128350_("FallDistance", this.f_19789_);
         p_20241_.m_128376_("Fire", (short)this.f_19831_);
         p_20241_.m_128376_("Air", (short)this.m_20146_());
         p_20241_.m_128379_("OnGround", this.m_20096_());
         p_20241_.m_128379_("Invulnerable", this.f_19840_);
         p_20241_.m_128405_("PortalCooldown", this.f_19839_);
         p_20241_.m_128362_("UUID", this.m_20148_());
         Component component = this.m_7770_();
         if (component != null) {
            p_20241_.m_128359_("CustomName", Component.Serializer.m_130703_(component));
         }

         if (this.m_20151_()) {
            p_20241_.m_128379_("CustomNameVisible", this.m_20151_());
         }

         if (this.m_20067_()) {
            p_20241_.m_128379_("Silent", this.m_20067_());
         }

         if (this.m_20068_()) {
            p_20241_.m_128379_("NoGravity", this.m_20068_());
         }

         if (this.f_146802_) {
            p_20241_.m_128379_("Glowing", true);
         }

         int i = this.m_146888_();
         if (i > 0) {
            p_20241_.m_128405_("TicksFrozen", this.m_146888_());
         }

         if (this.f_146813_) {
            p_20241_.m_128379_("HasVisualFire", this.f_146813_);
         }

         p_20241_.m_128379_("CanUpdate", canUpdate);

         if (!this.f_19841_.isEmpty()) {
            ListTag listtag = new ListTag();

            for(String s : this.f_19841_) {
               listtag.add(StringTag.m_129297_(s));
            }

            p_20241_.m_128365_("Tags", listtag);
         }

         CompoundTag caps = serializeCaps();
         if (caps != null) p_20241_.m_128365_("ForgeCaps", caps);
         if (persistentData != null) p_20241_.m_128365_("ForgeData", persistentData.m_6426_());

         this.m_7380_(p_20241_);
         if (this.m_20160_()) {
            ListTag listtag1 = new ListTag();

            for(Entity entity : this.m_20197_()) {
               CompoundTag compoundtag = new CompoundTag();
               if (entity.m_20086_(compoundtag)) {
                  listtag1.add(compoundtag);
               }
            }

            if (!listtag1.isEmpty()) {
               p_20241_.m_128365_("Passengers", listtag1);
            }
         }

         return p_20241_;
      } catch (Throwable throwable) {
         CrashReport crashreport = CrashReport.m_127521_(throwable, "Saving entity NBT");
         CrashReportCategory crashreportcategory = crashreport.m_127514_("Entity being saved");
         this.m_7976_(crashreportcategory);
         throw new ReportedException(crashreport);
      }
   }

   public void m_20258_(CompoundTag p_20259_) {
      try {
         ListTag listtag = p_20259_.m_128437_("Pos", 6);
         ListTag listtag1 = p_20259_.m_128437_("Motion", 6);
         ListTag listtag2 = p_20259_.m_128437_("Rotation", 5);
         double d0 = listtag1.m_128772_(0);
         double d1 = listtag1.m_128772_(1);
         double d2 = listtag1.m_128772_(2);
         this.m_20334_(Math.abs(d0) > 10.0D ? 0.0D : d0, Math.abs(d1) > 10.0D ? 0.0D : d1, Math.abs(d2) > 10.0D ? 0.0D : d2);
         double d3 = 3.0000512E7D;
         this.m_20343_(Mth.m_14008_(listtag.m_128772_(0), -3.0000512E7D, 3.0000512E7D), Mth.m_14008_(listtag.m_128772_(1), -2.0E7D, 2.0E7D), Mth.m_14008_(listtag.m_128772_(2), -3.0000512E7D, 3.0000512E7D));
         this.m_146922_(listtag2.m_128775_(0));
         this.m_146926_(listtag2.m_128775_(1));
         this.m_146867_();
         this.m_5616_(this.m_146908_());
         this.m_5618_(this.m_146908_());
         this.f_19789_ = p_20259_.m_128457_("FallDistance");
         this.f_19831_ = p_20259_.m_128448_("Fire");
         if (p_20259_.m_128441_("Air")) {
            this.m_20301_(p_20259_.m_128448_("Air"));
         }

         this.f_19861_ = p_20259_.m_128471_("OnGround");
         this.f_19840_ = p_20259_.m_128471_("Invulnerable");
         this.f_19839_ = p_20259_.m_128451_("PortalCooldown");
         if (p_20259_.m_128403_("UUID")) {
            this.f_19820_ = p_20259_.m_128342_("UUID");
            this.f_19821_ = this.f_19820_.toString();
         }

         if (Double.isFinite(this.m_20185_()) && Double.isFinite(this.m_20186_()) && Double.isFinite(this.m_20189_())) {
            if (Double.isFinite((double)this.m_146908_()) && Double.isFinite((double)this.m_146909_())) {
               this.m_20090_();
               this.m_19915_(this.m_146908_(), this.m_146909_());
               if (p_20259_.m_128425_("CustomName", 8)) {
                  String s = p_20259_.m_128461_("CustomName");

                  try {
                     this.m_6593_(Component.Serializer.m_130701_(s));
                  } catch (Exception exception) {
                     f_19849_.warn("Failed to parse entity custom name {}", s, exception);
                  }
               }

               this.m_20340_(p_20259_.m_128471_("CustomNameVisible"));
               this.m_20225_(p_20259_.m_128471_("Silent"));
               this.m_20242_(p_20259_.m_128471_("NoGravity"));
               this.m_146915_(p_20259_.m_128471_("Glowing"));
               this.m_146917_(p_20259_.m_128451_("TicksFrozen"));
               this.f_146813_ = p_20259_.m_128471_("HasVisualFire");
               if (p_20259_.m_128425_("ForgeData", 10)) persistentData = p_20259_.m_128469_("ForgeData");
               if (p_20259_.m_128425_("CanUpdate", 99)) this.canUpdate(p_20259_.m_128471_("CanUpdate"));
               if (p_20259_.m_128425_("ForgeCaps", 10)) deserializeCaps(p_20259_.m_128469_("ForgeCaps"));
               if (p_20259_.m_128425_("Tags", 9)) {
                  this.f_19841_.clear();
                  ListTag listtag3 = p_20259_.m_128437_("Tags", 8);
                  int i = Math.min(listtag3.size(), 1024);

                  for(int j = 0; j < i; ++j) {
                     this.f_19841_.add(listtag3.m_128778_(j));
                  }
               }

               this.m_7378_(p_20259_);
               if (this.m_6093_()) {
                  this.m_20090_();
               }

            } else {
               throw new IllegalStateException("Entity has invalid rotation");
            }
         } else {
            throw new IllegalStateException("Entity has invalid position");
         }
      } catch (Throwable throwable) {
         CrashReport crashreport = CrashReport.m_127521_(throwable, "Loading entity NBT");
         CrashReportCategory crashreportcategory = crashreport.m_127514_("Entity being loaded");
         this.m_7976_(crashreportcategory);
         throw new ReportedException(crashreport);
      }
   }

   protected boolean m_6093_() {
      return true;
   }

   @Nullable
   public final String m_20078_() {
      EntityType<?> entitytype = this.m_6095_();
      ResourceLocation resourcelocation = EntityType.m_20613_(entitytype);
      return entitytype.m_20584_() && resourcelocation != null ? resourcelocation.toString() : null;
   }

   protected abstract void m_7378_(CompoundTag p_20052_);

   protected abstract void m_7380_(CompoundTag p_20139_);

   protected ListTag m_20063_(double... p_20064_) {
      ListTag listtag = new ListTag();

      for(double d0 : p_20064_) {
         listtag.add(DoubleTag.m_128500_(d0));
      }

      return listtag;
   }

   protected ListTag m_20065_(float... p_20066_) {
      ListTag listtag = new ListTag();

      for(float f : p_20066_) {
         listtag.add(FloatTag.m_128566_(f));
      }

      return listtag;
   }

   @Nullable
   public ItemEntity m_19998_(ItemLike p_19999_) {
      return this.m_20000_(p_19999_, 0);
   }

   @Nullable
   public ItemEntity m_20000_(ItemLike p_20001_, int p_20002_) {
      return this.m_5552_(new ItemStack(p_20001_), (float)p_20002_);
   }

   @Nullable
   public ItemEntity m_19983_(ItemStack p_19984_) {
      return this.m_5552_(p_19984_, 0.0F);
   }

   @Nullable
   public ItemEntity m_5552_(ItemStack p_19985_, float p_19986_) {
      if (p_19985_.m_41619_()) {
         return null;
      } else if (this.m_9236_().f_46443_) {
         return null;
      } else {
         ItemEntity itementity = new ItemEntity(this.m_9236_(), this.m_20185_(), this.m_20186_() + (double)p_19986_, this.m_20189_(), p_19985_);
         itementity.m_32060_();
         if (captureDrops() != null) captureDrops().add(itementity);
         else
         this.m_9236_().m_7967_(itementity);
         return itementity;
      }
   }

   public boolean m_6084_() {
      return !this.m_213877_();
   }

   public boolean m_5830_() {
      if (this.f_19794_) {
         return false;
      } else {
         float f = this.f_19815_.f_20377_ * 0.8F;
         AABB aabb = AABB.m_165882_(this.m_146892_(), (double)f, 1.0E-6D, (double)f);
         return BlockPos.m_121921_(aabb).anyMatch((p_201942_) -> {
            BlockState blockstate = this.m_9236_().m_8055_(p_201942_);
            return !blockstate.m_60795_() && blockstate.m_60828_(this.m_9236_(), p_201942_) && Shapes.m_83157_(blockstate.m_60812_(this.m_9236_(), p_201942_).m_83216_((double)p_201942_.m_123341_(), (double)p_201942_.m_123342_(), (double)p_201942_.m_123343_()), Shapes.m_83064_(aabb), BooleanOp.f_82689_);
         });
      }
   }

   public InteractionResult m_6096_(Player p_19978_, InteractionHand p_19979_) {
      return InteractionResult.PASS;
   }

   public boolean m_7337_(Entity p_20303_) {
      return p_20303_.m_5829_() && !this.m_20365_(p_20303_);
   }

   public boolean m_5829_() {
      return false;
   }

   public void m_6083_() {
      this.m_20256_(Vec3.f_82478_);
      if (canUpdate())
      this.m_8119_();
      if (this.m_20159_()) {
         this.m_20202_().m_7332_(this);
      }
   }

   public final void m_7332_(Entity p_20312_) {
      this.m_19956_(p_20312_, Entity::m_6034_);
   }

   protected void m_19956_(Entity p_19957_, Entity.MoveFunction p_19958_) {
      if (this.m_20363_(p_19957_)) {
         double d0 = this.m_20186_() + this.m_6048_() + p_19957_.m_6049_();
         p_19958_.m_20372_(p_19957_, this.m_20185_(), d0, this.m_20189_());
      }
   }

   public void m_7340_(Entity p_20320_) {
   }

   public double m_6049_() {
      return 0.0D;
   }

   public double m_6048_() {
      return (double)this.f_19815_.f_20378_ * 0.75D;
   }

   public boolean m_20329_(Entity p_20330_) {
      return this.m_7998_(p_20330_, false);
   }

   public boolean m_20152_() {
      return this instanceof LivingEntity;
   }

   public boolean m_7998_(Entity p_19966_, boolean p_19967_) {
      if (p_19966_ == this.f_19824_) {
         return false;
      } else if (!p_19966_.m_269011_()) {
         return false;
      } else {
         for(Entity entity = p_19966_; entity.f_19824_ != null; entity = entity.f_19824_) {
            if (entity.f_19824_ == this) {
               return false;
            }
         }

      if (!net.minecraftforge.event.ForgeEventFactory.canMountEntity(this, p_19966_, true)) return false;
         if (p_19967_ || this.m_7341_(p_19966_) && p_19966_.m_7310_(this)) {
            if (this.m_20159_()) {
               this.m_8127_();
            }

            this.m_20124_(Pose.STANDING);
            this.f_19824_ = p_19966_;
            this.f_19824_.m_20348_(this);
            p_19966_.m_146920_().filter((p_185984_) -> {
               return p_185984_ instanceof ServerPlayer;
            }).forEach((p_185982_) -> {
               CriteriaTriggers.f_145088_.m_160387_((ServerPlayer)p_185982_);
            });
            return true;
         } else {
            return false;
         }
      }
   }

   protected boolean m_7341_(Entity p_20339_) {
      return !this.m_6144_() && this.f_19851_ <= 0;
   }

   protected boolean m_20175_(Pose p_20176_) {
      return this.m_9236_().m_45756_(this, this.m_20217_(p_20176_).m_82406_(1.0E-7D));
   }

   public void m_20153_() {
      for(int i = this.f_19823_.size() - 1; i >= 0; --i) {
         this.f_19823_.get(i).m_8127_();
      }

   }

   public void m_6038_() {
      if (this.f_19824_ != null) {
         Entity entity = this.f_19824_;
         if (!net.minecraftforge.event.ForgeEventFactory.canMountEntity(this, entity, false)) return;
         this.f_19824_ = null;
         entity.m_20351_(this);
      }

   }

   public void m_8127_() {
      this.m_6038_();
   }

   protected void m_20348_(Entity p_20349_) {
      if (p_20349_.m_20202_() != this) {
         throw new IllegalStateException("Use x.startRiding(y), not y.addPassenger(x)");
      } else {
         if (this.f_19823_.isEmpty()) {
            this.f_19823_ = ImmutableList.of(p_20349_);
         } else {
            List<Entity> list = Lists.newArrayList(this.f_19823_);
            if (!this.m_9236_().f_46443_ && p_20349_ instanceof Player && !(this.m_146895_() instanceof Player)) {
               list.add(0, p_20349_);
            } else {
               list.add(p_20349_);
            }

            this.f_19823_ = ImmutableList.copyOf(list);
         }

         this.m_146852_(GameEvent.f_268500_, p_20349_);
      }
   }

   protected void m_20351_(Entity p_20352_) {
      if (p_20352_.m_20202_() == this) {
         throw new IllegalStateException("Use x.stopRiding(y), not y.removePassenger(x)");
      } else {
         if (this.f_19823_.size() == 1 && this.f_19823_.get(0) == p_20352_) {
            this.f_19823_ = ImmutableList.of();
         } else {
            this.f_19823_ = this.f_19823_.stream().filter((p_185980_) -> {
               return p_185980_ != p_20352_;
            }).collect(ImmutableList.toImmutableList());
         }

         p_20352_.f_19851_ = 60;
         this.m_146852_(GameEvent.f_268533_, p_20352_);
      }
   }

   protected boolean m_7310_(Entity p_20354_) {
      return this.f_19823_.isEmpty();
   }

   /** @deprecated Forge: Use {@link #canBeRiddenUnderFluidType(net.minecraftforge.fluids.FluidType, Entity) rider sensitive version} */
   @Deprecated
   protected boolean m_269011_() {
      return true;
   }

   public void m_6453_(double p_19896_, double p_19897_, double p_19898_, float p_19899_, float p_19900_, int p_19901_, boolean p_19902_) {
      this.m_6034_(p_19896_, p_19897_, p_19898_);
      this.m_19915_(p_19899_, p_19900_);
   }

   public void m_6541_(float p_19918_, int p_19919_) {
      this.m_5616_(p_19918_);
   }

   public float m_6143_() {
      return 0.0F;
   }

   public Vec3 m_20154_() {
      return this.m_20171_(this.m_146909_(), this.m_146908_());
   }

   public Vec3 m_204034_(Item p_204035_) {
      if (!(this instanceof Player player)) {
         return Vec3.f_82478_;
      } else {
         boolean flag = player.m_21206_().m_150930_(p_204035_) && !player.m_21205_().m_150930_(p_204035_);
         HumanoidArm humanoidarm = flag ? player.m_5737_().m_20828_() : player.m_5737_();
         return this.m_20171_(0.0F, this.m_146908_() + (float)(humanoidarm == HumanoidArm.RIGHT ? 80 : -80)).m_82490_(0.5D);
      }
   }

   public Vec2 m_20155_() {
      return new Vec2(this.m_146909_(), this.m_146908_());
   }

   public Vec3 m_20156_() {
      return Vec3.m_82503_(this.m_20155_());
   }

   public void m_20221_(BlockPos p_20222_) {
      if (this.m_20092_()) {
         this.m_20091_();
      } else {
         if (!this.m_9236_().f_46443_ && !p_20222_.equals(this.f_19819_)) {
            this.f_19819_ = p_20222_.m_7949_();
         }

         this.f_19817_ = true;
      }
   }

   protected void m_20157_() {
      if (this.m_9236_() instanceof ServerLevel) {
         int i = this.m_6078_();
         ServerLevel serverlevel = (ServerLevel)this.m_9236_();
         if (this.f_19817_) {
            MinecraftServer minecraftserver = serverlevel.m_7654_();
            ResourceKey<Level> resourcekey = this.m_9236_().m_46472_() == Level.f_46429_ ? Level.f_46428_ : Level.f_46429_;
            ServerLevel serverlevel1 = minecraftserver.m_129880_(resourcekey);
            if (serverlevel1 != null && minecraftserver.m_7079_() && !this.m_20159_() && this.f_19818_++ >= i) {
               this.m_9236_().m_46473_().m_6180_("portal");
               this.f_19818_ = i;
               this.m_20091_();
               this.m_5489_(serverlevel1);
               this.m_9236_().m_46473_().m_7238_();
            }

            this.f_19817_ = false;
         } else {
            if (this.f_19818_ > 0) {
               this.f_19818_ -= 4;
            }

            if (this.f_19818_ < 0) {
               this.f_19818_ = 0;
            }
         }

         this.m_8021_();
      }
   }

   public int m_6045_() {
      return 300;
   }

   public void m_6001_(double p_20306_, double p_20307_, double p_20308_) {
      this.m_20334_(p_20306_, p_20307_, p_20308_);
   }

   public void m_269138_(DamageSource p_270704_) {
   }

   public void m_7822_(byte p_19882_) {
      switch (p_19882_) {
         case 53:
            HoneyBlock.m_53986_(this);
         default:
      }
   }

   public void m_6053_(float p_265161_) {
   }

   public Iterable<ItemStack> m_6167_() {
      return f_19844_;
   }

   public Iterable<ItemStack> m_6168_() {
      return f_19844_;
   }

   public Iterable<ItemStack> m_20158_() {
      return Iterables.concat(this.m_6167_(), this.m_6168_());
   }

   public void m_8061_(EquipmentSlot p_19968_, ItemStack p_19969_) {
   }

   public boolean m_6060_() {
      boolean flag = this.m_9236_() != null && this.m_9236_().f_46443_;
      return !this.m_5825_() && (this.f_19831_ > 0 || flag && this.m_20291_(0));
   }

   public boolean m_20159_() {
      return this.m_20202_() != null;
   }

   public boolean m_20160_() {
      return !this.f_19823_.isEmpty();
   }

   public boolean m_275843_() {
      return this.m_6095_().m_204039_(EntityTypeTags.f_275751_);
   }

   public void m_20260_(boolean p_20261_) {
      this.m_20115_(1, p_20261_);
   }

   public boolean m_6144_() {
      return this.m_20291_(1);
   }

   public boolean m_20161_() {
      return this.m_6144_();
   }

   public boolean m_20162_() {
      return this.m_6144_();
   }

   public boolean m_20163_() {
      return this.m_6144_();
   }

   public boolean m_20164_() {
      return this.m_6144_();
   }

   public boolean m_6047_() {
      return this.m_217003_(Pose.CROUCHING);
   }

   public boolean m_20142_() {
      return this.m_20291_(3);
   }

   public void m_6858_(boolean p_20274_) {
      this.m_20115_(3, p_20274_);
   }

   public boolean m_6069_() {
      return this.m_20291_(4);
   }

   public boolean m_6067_() {
      return this.m_217003_(Pose.SWIMMING);
   }

   public boolean m_20143_() {
      return this.m_6067_() && !this.m_20069_() && !this.isInFluidType((fluidType, height) -> this.canSwimInFluidType(fluidType));
   }

   public void m_20282_(boolean p_20283_) {
      this.m_20115_(4, p_20283_);
   }

   public final boolean m_146886_() {
      return this.f_146802_;
   }

   public final void m_146915_(boolean p_146916_) {
      this.f_146802_ = p_146916_;
      this.m_20115_(6, this.m_142038_());
   }

   public boolean m_142038_() {
      return this.m_9236_().m_5776_() ? this.m_20291_(6) : this.f_146802_;
   }

   public boolean m_20145_() {
      return this.m_20291_(5);
   }

   public boolean m_20177_(Player p_20178_) {
      if (p_20178_.m_5833_()) {
         return false;
      } else {
         Team team = this.m_5647_();
         return team != null && p_20178_ != null && p_20178_.m_5647_() == team && team.m_6259_() ? false : this.m_20145_();
      }
   }

   public boolean m_288188_() {
      return false;
   }

   public void m_213651_(BiConsumer<DynamicGameEventListener<?>, ServerLevel> p_216996_) {
   }

   @Nullable
   public Team m_5647_() {
      return this.m_9236_().m_6188_().m_83500_(this.m_6302_());
   }

   public boolean m_7307_(Entity p_20355_) {
      return this.m_20031_(p_20355_.m_5647_());
   }

   public boolean m_20031_(Team p_20032_) {
      return this.m_5647_() != null ? this.m_5647_().m_83536_(p_20032_) : false;
   }

   public void m_6842_(boolean p_20304_) {
      this.m_20115_(5, p_20304_);
   }

   protected boolean m_20291_(int p_20292_) {
      return (this.f_19804_.m_135370_(f_19805_) & 1 << p_20292_) != 0;
   }

   protected void m_20115_(int p_20116_, boolean p_20117_) {
      byte b0 = this.f_19804_.m_135370_(f_19805_);
      if (p_20117_) {
         this.f_19804_.m_135381_(f_19805_, (byte)(b0 | 1 << p_20116_));
      } else {
         this.f_19804_.m_135381_(f_19805_, (byte)(b0 & ~(1 << p_20116_)));
      }

   }

   public int m_6062_() {
      return 300;
   }

   public int m_20146_() {
      return this.f_19804_.m_135370_(f_19832_);
   }

   public void m_20301_(int p_20302_) {
      this.f_19804_.m_135381_(f_19832_, p_20302_);
   }

   public int m_146888_() {
      return this.f_19804_.m_135370_(f_146800_);
   }

   public void m_146917_(int p_146918_) {
      this.f_19804_.m_135381_(f_146800_, p_146918_);
   }

   public float m_146889_() {
      int i = this.m_146891_();
      return (float)Math.min(this.m_146888_(), i) / (float)i;
   }

   public boolean m_146890_() {
      return this.m_146888_() >= this.m_146891_();
   }

   public int m_146891_() {
      return 140;
   }

   public void m_8038_(ServerLevel p_19927_, LightningBolt p_19928_) {
      this.m_7311_(this.f_19831_ + 1);
      if (this.f_19831_ == 0) {
         this.m_20254_(8);
      }

      this.m_6469_(this.m_269291_().m_269548_(), p_19928_.getDamage());
   }

   public void m_6845_(boolean p_20313_) {
      Vec3 vec3 = this.m_20184_();
      double d0;
      if (p_20313_) {
         d0 = Math.max(-0.9D, vec3.f_82480_ - 0.03D);
      } else {
         d0 = Math.min(1.8D, vec3.f_82480_ + 0.1D);
      }

      this.m_20334_(vec3.f_82479_, d0, vec3.f_82481_);
   }

   public void m_20321_(boolean p_20322_) {
      Vec3 vec3 = this.m_20184_();
      double d0;
      if (p_20322_) {
         d0 = Math.max(-0.3D, vec3.f_82480_ - 0.03D);
      } else {
         d0 = Math.min(0.7D, vec3.f_82480_ + 0.06D);
      }

      this.m_20334_(vec3.f_82479_, d0, vec3.f_82481_);
      this.m_183634_();
   }

   public boolean m_214076_(ServerLevel p_216988_, LivingEntity p_216989_) {
      return true;
   }

   public void m_245125_() {
      if (this.m_20184_().m_7098_() > -0.5D && this.f_19789_ > 1.0F) {
         this.f_19789_ = 1.0F;
      }

   }

   public void m_183634_() {
      this.f_19789_ = 0.0F;
   }

   protected void m_20314_(double p_20315_, double p_20316_, double p_20317_) {
      BlockPos blockpos = BlockPos.m_274561_(p_20315_, p_20316_, p_20317_);
      Vec3 vec3 = new Vec3(p_20315_ - (double)blockpos.m_123341_(), p_20316_ - (double)blockpos.m_123342_(), p_20317_ - (double)blockpos.m_123343_());
      BlockPos.MutableBlockPos blockpos$mutableblockpos = new BlockPos.MutableBlockPos();
      Direction direction = Direction.UP;
      double d0 = Double.MAX_VALUE;

      for(Direction direction1 : new Direction[]{Direction.NORTH, Direction.SOUTH, Direction.WEST, Direction.EAST, Direction.UP}) {
         blockpos$mutableblockpos.m_122159_(blockpos, direction1);
         if (!this.m_9236_().m_8055_(blockpos$mutableblockpos).m_60838_(this.m_9236_(), blockpos$mutableblockpos)) {
            double d1 = vec3.m_82507_(direction1.m_122434_());
            double d2 = direction1.m_122421_() == Direction.AxisDirection.POSITIVE ? 1.0D - d1 : d1;
            if (d2 < d0) {
               d0 = d2;
               direction = direction1;
            }
         }
      }

      float f = this.f_19796_.m_188501_() * 0.2F + 0.1F;
      float f1 = (float)direction.m_122421_().m_122540_();
      Vec3 vec31 = this.m_20184_().m_82490_(0.75D);
      if (direction.m_122434_() == Direction.Axis.X) {
         this.m_20334_((double)(f1 * f), vec31.f_82480_, vec31.f_82481_);
      } else if (direction.m_122434_() == Direction.Axis.Y) {
         this.m_20334_(vec31.f_82479_, (double)(f1 * f), vec31.f_82481_);
      } else if (direction.m_122434_() == Direction.Axis.Z) {
         this.m_20334_(vec31.f_82479_, vec31.f_82480_, (double)(f1 * f));
      }

   }

   public void m_7601_(BlockState p_20006_, Vec3 p_20007_) {
      this.m_183634_();
      this.f_19865_ = p_20007_;
   }

   private static Component m_20140_(Component p_20141_) {
      MutableComponent mutablecomponent = p_20141_.m_6879_().m_6270_(p_20141_.m_7383_().m_131142_((ClickEvent)null));

      for(Component component : p_20141_.m_7360_()) {
         mutablecomponent.m_7220_(m_20140_(component));
      }

      return mutablecomponent;
   }

   public Component m_7755_() {
      Component component = this.m_7770_();
      return component != null ? m_20140_(component) : this.m_5677_();
   }

   protected Component m_5677_() {
      return this.m_6095_().m_20676_(); // Forge: Use getter to allow overriding by mods
   }

   public boolean m_7306_(Entity p_20356_) {
      return this == p_20356_;
   }

   public float m_6080_() {
      return 0.0F;
   }

   public void m_5616_(float p_20328_) {
   }

   public void m_5618_(float p_20338_) {
   }

   public boolean m_6097_() {
      return true;
   }

   public boolean m_7313_(Entity p_20357_) {
      return false;
   }

   public String toString() {
      String s = this.m_9236_() == null ? "~NULL~" : this.m_9236_().toString();
      return this.f_146795_ != null ? String.format(Locale.ROOT, "%s['%s'/%d, l='%s', x=%.2f, y=%.2f, z=%.2f, removed=%s]", this.getClass().getSimpleName(), this.m_7755_().getString(), this.f_19848_, s, this.m_20185_(), this.m_20186_(), this.m_20189_(), this.f_146795_) : String.format(Locale.ROOT, "%s['%s'/%d, l='%s', x=%.2f, y=%.2f, z=%.2f]", this.getClass().getSimpleName(), this.m_7755_().getString(), this.f_19848_, s, this.m_20185_(), this.m_20186_(), this.m_20189_());
   }

   public boolean m_6673_(DamageSource p_20122_) {
      return this.m_213877_() || this.f_19840_ && !p_20122_.m_269533_(DamageTypeTags.f_268738_) && !p_20122_.m_19390_() || p_20122_.m_269533_(DamageTypeTags.f_268745_) && this.m_5825_() || p_20122_.m_269533_(DamageTypeTags.f_268549_) && this.m_6095_().m_204039_(EntityTypeTags.f_273841_);
   }

   public boolean m_20147_() {
      return this.f_19840_;
   }

   public void m_20331_(boolean p_20332_) {
      this.f_19840_ = p_20332_;
   }

   public void m_20359_(Entity p_20360_) {
      this.m_7678_(p_20360_.m_20185_(), p_20360_.m_20186_(), p_20360_.m_20189_(), p_20360_.m_146908_(), p_20360_.m_146909_());
   }

   public void m_20361_(Entity p_20362_) {
      CompoundTag compoundtag = p_20362_.m_20240_(new CompoundTag());
      compoundtag.m_128473_("Dimension");
      this.m_20258_(compoundtag);
      this.f_19839_ = p_20362_.f_19839_;
      this.f_19819_ = p_20362_.f_19819_;
   }

   @Nullable
   public Entity m_5489_(ServerLevel p_20118_) {
      return this.changeDimension(p_20118_, p_20118_.m_8871_());
   }
   @Nullable
   public Entity changeDimension(ServerLevel p_20118_, net.minecraftforge.common.util.ITeleporter teleporter) {
      if (!net.minecraftforge.common.ForgeHooks.onTravelToDimension(this, p_20118_.m_46472_())) return null;
      if (this.m_9236_() instanceof ServerLevel && !this.m_213877_()) {
         this.m_9236_().m_46473_().m_6180_("changeDimension");
         this.m_19877_();
         this.m_9236_().m_46473_().m_6180_("reposition");
         PortalInfo portalinfo = teleporter.getPortalInfo(this, p_20118_, this::m_7937_);
         if (portalinfo == null) {
            return null;
         } else {
            Entity transportedEntity = teleporter.placeEntity(this, (ServerLevel) this.f_19853_, p_20118_, this.f_19857_, spawnPortal -> { //Forge: Start vanilla logic
            this.m_9236_().m_46473_().m_6182_("reloading");
            Entity entity = this.m_6095_().m_20615_(p_20118_);
            if (entity != null) {
               entity.m_20361_(this);
               entity.m_7678_(portalinfo.f_77676_.f_82479_, portalinfo.f_77676_.f_82480_, portalinfo.f_77676_.f_82481_, portalinfo.f_77678_, entity.m_146909_());
               entity.m_20256_(portalinfo.f_77677_);
               p_20118_.m_143334_(entity);
               if (spawnPortal && p_20118_.m_46472_() == Level.f_46430_) {
                  ServerLevel.m_8617_(p_20118_);
               }
            }
            return entity;
            }); //Forge: End vanilla logic

            this.m_6089_();
            this.m_9236_().m_46473_().m_7238_();
            ((ServerLevel)this.m_9236_()).m_8886_();
            p_20118_.m_8886_();
            this.m_9236_().m_46473_().m_7238_();
            return transportedEntity;
         }
      } else {
         return null;
      }
   }

   protected void m_6089_() {
      this.m_142467_(Entity.RemovalReason.CHANGED_DIMENSION);
   }

   @Nullable
   protected PortalInfo m_7937_(ServerLevel p_19923_) {
      boolean flag = this.m_9236_().m_46472_() == Level.f_46430_ && p_19923_.m_46472_() == Level.f_46428_;
      boolean flag1 = p_19923_.m_46472_() == Level.f_46430_;
      if (!flag && !flag1) {
         boolean flag2 = p_19923_.m_46472_() == Level.f_46429_;
         if (this.m_9236_().m_46472_() != Level.f_46429_ && !flag2) {
            return null;
         } else {
            WorldBorder worldborder = p_19923_.m_6857_();
            double d0 = DimensionType.m_63908_(this.m_9236_().m_6042_(), p_19923_.m_6042_());
            BlockPos blockpos1 = worldborder.m_187569_(this.m_20185_() * d0, this.m_20186_(), this.m_20189_() * d0);
            return this.m_183318_(p_19923_, blockpos1, flag2, worldborder).map((p_258249_) -> {
               BlockState blockstate = this.m_9236_().m_8055_(this.f_19819_);
               Direction.Axis direction$axis;
               Vec3 vec3;
               if (blockstate.m_61138_(BlockStateProperties.f_61364_)) {
                  direction$axis = blockstate.m_61143_(BlockStateProperties.f_61364_);
                  BlockUtil.FoundRectangle blockutil$foundrectangle = BlockUtil.m_124334_(this.f_19819_, direction$axis, 21, Direction.Axis.Y, 21, (p_284700_) -> {
                     return this.m_9236_().m_8055_(p_284700_) == blockstate;
                  });
                  vec3 = this.m_7643_(direction$axis, blockutil$foundrectangle);
               } else {
                  direction$axis = Direction.Axis.X;
                  vec3 = new Vec3(0.5D, 0.0D, 0.0D);
               }

               return PortalShape.m_257966_(p_19923_, p_258249_, direction$axis, vec3, this, this.m_20184_(), this.m_146908_(), this.m_146909_());
            }).orElse((PortalInfo)null);
         }
      } else {
         BlockPos blockpos;
         if (flag1) {
            blockpos = ServerLevel.f_8562_;
         } else {
            blockpos = p_19923_.m_5452_(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, p_19923_.m_220360_());
         }

         return new PortalInfo(new Vec3((double)blockpos.m_123341_() + 0.5D, (double)blockpos.m_123342_(), (double)blockpos.m_123343_() + 0.5D), this.m_20184_(), this.m_146908_(), this.m_146909_());
      }
   }

   protected Vec3 m_7643_(Direction.Axis p_20045_, BlockUtil.FoundRectangle p_20046_) {
      return PortalShape.m_77738_(p_20046_, p_20045_, this.m_20182_(), this.m_6972_(this.m_20089_()));
   }

   protected Optional<BlockUtil.FoundRectangle> m_183318_(ServerLevel p_185935_, BlockPos p_185936_, boolean p_185937_, WorldBorder p_185938_) {
      return p_185935_.m_8871_().m_192985_(p_185936_, p_185937_, p_185938_);
   }

   public boolean m_6072_() {
      return !this.m_20159_() && !this.m_20160_();
   }

   public float m_7077_(Explosion p_19992_, BlockGetter p_19993_, BlockPos p_19994_, BlockState p_19995_, FluidState p_19996_, float p_19997_) {
      return p_19997_;
   }

   public boolean m_7349_(Explosion p_19987_, BlockGetter p_19988_, BlockPos p_19989_, BlockState p_19990_, float p_19991_) {
      return true;
   }

   public int m_6056_() {
      return 3;
   }

   public boolean m_6090_() {
      return false;
   }

   public void m_7976_(CrashReportCategory p_20051_) {
      p_20051_.m_128165_("Entity Type", () -> {
         return EntityType.m_20613_(this.m_6095_()) + " (" + this.getClass().getCanonicalName() + ")";
      });
      p_20051_.m_128159_("Entity ID", this.f_19848_);
      p_20051_.m_128165_("Entity Name", () -> {
         return this.m_7755_().getString();
      });
      p_20051_.m_128159_("Entity's Exact location", String.format(Locale.ROOT, "%.2f, %.2f, %.2f", this.m_20185_(), this.m_20186_(), this.m_20189_()));
      p_20051_.m_128159_("Entity's Block location", CrashReportCategory.m_178942_(this.m_9236_(), Mth.m_14107_(this.m_20185_()), Mth.m_14107_(this.m_20186_()), Mth.m_14107_(this.m_20189_())));
      Vec3 vec3 = this.m_20184_();
      p_20051_.m_128159_("Entity's Momentum", String.format(Locale.ROOT, "%.2f, %.2f, %.2f", vec3.f_82479_, vec3.f_82480_, vec3.f_82481_));
      p_20051_.m_128165_("Entity's Passengers", () -> {
         return this.m_20197_().toString();
      });
      p_20051_.m_128165_("Entity's Vehicle", () -> {
         return String.valueOf((Object)this.m_20202_());
      });
   }

   public boolean m_6051_() {
      return this.m_6060_() && !this.m_5833_();
   }

   public void m_20084_(UUID p_20085_) {
      this.f_19820_ = p_20085_;
      this.f_19821_ = this.f_19820_.toString();
   }

   public UUID m_20148_() {
      return this.f_19820_;
   }

   public String m_20149_() {
      return this.f_19821_;
   }

   public String m_6302_() {
      return this.f_19821_;
   }

   @Deprecated // Forge: Use FluidType sensitive version
   public boolean m_6063_() {
      return true;
   }

   public static double m_20150_() {
      return f_19846_;
   }

   public static void m_20103_(double p_20104_) {
      f_19846_ = p_20104_;
   }

   public Component m_5446_() {
      return PlayerTeam.m_83348_(this.m_5647_(), this.m_7755_()).m_130938_((p_185975_) -> {
         return p_185975_.m_131144_(this.m_20190_()).m_131138_(this.m_20149_());
      });
   }

   public void m_6593_(@Nullable Component p_20053_) {
      this.f_19804_.m_135381_(f_19833_, Optional.ofNullable(p_20053_));
   }

   @Nullable
   public Component m_7770_() {
      return this.f_19804_.m_135370_(f_19833_).orElse((Component)null);
   }

   public boolean m_8077_() {
      return this.f_19804_.m_135370_(f_19833_).isPresent();
   }

   public void m_20340_(boolean p_20341_) {
      this.f_19804_.m_135381_(f_19834_, p_20341_);
   }

   public boolean m_20151_() {
      return this.f_19804_.m_135370_(f_19834_);
   }

   public final void m_20324_(double p_20325_, double p_20326_, double p_20327_) {
      if (this.m_9236_() instanceof ServerLevel) {
         ChunkPos chunkpos = new ChunkPos(BlockPos.m_274561_(p_20325_, p_20326_, p_20327_));
         ((ServerLevel)this.m_9236_()).m_7726_().m_8387_(TicketType.f_9448_, chunkpos, 0, this.m_19879_());
         this.m_9236_().m_6325_(chunkpos.f_45578_, chunkpos.f_45579_);
         this.m_6021_(p_20325_, p_20326_, p_20327_);
      }
   }

   public boolean m_264318_(ServerLevel p_265257_, double p_265407_, double p_265727_, double p_265410_, Set<RelativeMovement> p_265083_, float p_265573_, float p_265094_) {
      float f = Mth.m_14036_(p_265094_, -90.0F, 90.0F);
      if (p_265257_ == this.m_9236_()) {
         this.m_7678_(p_265407_, p_265727_, p_265410_, p_265573_, f);
         this.m_276804_();
         this.m_5616_(p_265573_);
      } else {
         this.m_19877_();
         Entity entity = this.m_6095_().m_20615_(p_265257_);
         if (entity == null) {
            return false;
         }

         entity.m_20361_(this);
         entity.m_7678_(p_265407_, p_265727_, p_265410_, p_265573_, f);
         entity.m_5616_(p_265573_);
         this.m_142467_(Entity.RemovalReason.CHANGED_DIMENSION);
         p_265257_.m_143334_(entity);
      }

      return true;
   }

   public void m_142098_(double p_146825_, double p_146826_, double p_146827_) {
      this.m_6021_(p_146825_, p_146826_, p_146827_);
   }

   public void m_6021_(double p_19887_, double p_19888_, double p_19889_) {
      if (this.m_9236_() instanceof ServerLevel) {
         this.m_7678_(p_19887_, p_19888_, p_19889_, this.m_146908_(), this.m_146909_());
         this.m_276804_();
      }
   }

   private void m_276804_() {
      this.m_20199_().forEach((p_185977_) -> {
         for(Entity entity : p_185977_.f_19823_) {
            p_185977_.m_19956_(entity, Entity::m_6027_);
         }

      });
   }

   public void m_246847_(double p_249341_, double p_252229_, double p_252038_) {
      this.m_6021_(this.m_20185_() + p_249341_, this.m_20186_() + p_252229_, this.m_20189_() + p_252038_);
   }

   public boolean m_6052_() {
      return this.m_20151_();
   }

   public void m_269505_(List<SynchedEntityData.DataValue<?>> p_270372_) {
   }

   public void m_7350_(EntityDataAccessor<?> p_20059_) {
      if (f_19806_.equals(p_20059_)) {
         this.m_6210_();
      }

   }

   /** @deprecated */
   @Deprecated
   protected void m_252801_() {
      Pose pose = this.m_20089_();
      EntityDimensions entitydimensions = this.m_6972_(pose);
      this.f_19815_ = entitydimensions;
      this.f_19816_ = this.m_6380_(pose, entitydimensions);
   }

   public void m_6210_() {
      EntityDimensions entitydimensions = this.f_19815_;
      Pose pose = this.m_20089_();
      EntityDimensions entitydimensions1 = this.m_6972_(pose);
      net.minecraftforge.event.entity.EntityEvent.Size sizeEvent = net.minecraftforge.event.ForgeEventFactory.getEntitySizeForge(this, pose, entitydimensions, entitydimensions1, this.m_6380_(pose, entitydimensions1));
      entitydimensions1 = sizeEvent.getNewSize();
      this.f_19815_ = entitydimensions1;
      this.f_19816_ = sizeEvent.getNewEyeHeight();
      this.m_20090_();
      boolean flag = (double)entitydimensions1.f_20377_ <= 4.0D && (double)entitydimensions1.f_20378_ <= 4.0D;
      if (!this.m_9236_().f_46443_ && !this.f_19803_ && !this.f_19794_ && flag && (entitydimensions1.f_20377_ > entitydimensions.f_20377_ || entitydimensions1.f_20378_ > entitydimensions.f_20378_) && !(this instanceof Player)) {
         Vec3 vec3 = this.m_20182_().m_82520_(0.0D, (double)entitydimensions.f_20378_ / 2.0D, 0.0D);
         double d0 = (double)Math.max(0.0F, entitydimensions1.f_20377_ - entitydimensions.f_20377_) + 1.0E-6D;
         double d1 = (double)Math.max(0.0F, entitydimensions1.f_20378_ - entitydimensions.f_20378_) + 1.0E-6D;
         VoxelShape voxelshape = Shapes.m_83064_(AABB.m_165882_(vec3, d0, d1, d0));
         EntityDimensions finalEntitydimensions = entitydimensions1;
         this.m_9236_().m_151418_(this, voxelshape, vec3, (double)entitydimensions1.f_20377_, (double)entitydimensions1.f_20378_, (double)entitydimensions1.f_20377_).ifPresent((p_185956_) -> {
            this.m_146884_(p_185956_.m_82520_(0.0D, (double)(-finalEntitydimensions.f_20378_) / 2.0D, 0.0D));
         });
      }

   }

   public Direction m_6350_() {
      return Direction.m_122364_((double)this.m_146908_());
   }

   public Direction m_6374_() {
      return this.m_6350_();
   }

   protected HoverEvent m_20190_() {
      return new HoverEvent(HoverEvent.Action.f_130833_, new HoverEvent.EntityTooltipInfo(this.m_6095_(), this.m_20148_(), this.m_7755_()));
   }

   public boolean m_6459_(ServerPlayer p_19937_) {
      return true;
   }

   public final AABB m_20191_() {
      return this.f_19828_;
   }

   public AABB m_6921_() {
      return this.m_20191_();
   }

   protected AABB m_20217_(Pose p_20218_) {
      EntityDimensions entitydimensions = this.m_6972_(p_20218_);
      float f = entitydimensions.f_20377_ / 2.0F;
      Vec3 vec3 = new Vec3(this.m_20185_() - (double)f, this.m_20186_(), this.m_20189_() - (double)f);
      Vec3 vec31 = new Vec3(this.m_20185_() + (double)f, this.m_20186_() + (double)entitydimensions.f_20378_, this.m_20189_() + (double)f);
      return new AABB(vec3, vec31);
   }

   public final void m_20011_(AABB p_20012_) {
      this.f_19828_ = p_20012_;
   }

   protected float m_6380_(Pose p_19976_, EntityDimensions p_19977_) {
      return p_19977_.f_20378_ * 0.85F;
   }

   public float m_20236_(Pose p_20237_) {
      return this.m_6380_(p_20237_, this.m_6972_(p_20237_));
   }

   public final float m_20192_() {
      return this.f_19816_;
   }

   public Vec3 m_245894_(float p_249286_) {
      return this.m_7939_();
   }

   protected Vec3 m_7939_() {
      return new Vec3(0.0D, (double)this.m_20192_(), (double)(this.m_20205_() * 0.4F));
   }

   public SlotAccess m_141942_(int p_146919_) {
      return SlotAccess.f_147290_;
   }

   public void m_213846_(Component p_216998_) {
   }

   public Level m_20193_() {
      return this.m_9236_();
   }

   @Nullable
   public MinecraftServer m_20194_() {
      return this.m_9236_().m_7654_();
   }

   public InteractionResult m_7111_(Player p_19980_, Vec3 p_19981_, InteractionHand p_19982_) {
      return InteractionResult.PASS;
   }

   public boolean m_6128_() {
      return false;
   }

   public void m_19970_(LivingEntity p_19971_, Entity p_19972_) {
      if (p_19972_ instanceof LivingEntity) {
         EnchantmentHelper.m_44823_((LivingEntity)p_19972_, p_19971_);
      }

      EnchantmentHelper.m_44896_(p_19971_, p_19972_);
   }

   public void m_6457_(ServerPlayer p_20119_) {
   }

   public void m_6452_(ServerPlayer p_20174_) {
   }

   public float m_7890_(Rotation p_20004_) {
      float f = Mth.m_14177_(this.m_146908_());
      switch (p_20004_) {
         case CLOCKWISE_180:
            return f + 180.0F;
         case COUNTERCLOCKWISE_90:
            return f + 270.0F;
         case CLOCKWISE_90:
            return f + 90.0F;
         default:
            return f;
      }
   }

   public float m_6961_(Mirror p_20003_) {
      float f = Mth.m_14177_(this.m_146908_());
      switch (p_20003_) {
         case FRONT_BACK:
            return -f;
         case LEFT_RIGHT:
            return 180.0F - f;
         default:
            return f;
      }
   }

   public boolean m_6127_() {
      return false;
   }

   @Nullable
   public LivingEntity m_6688_() {
      return null;
   }

   public final boolean m_217005_() {
      return this.m_6688_() != null;
   }

   public final List<Entity> m_20197_() {
      return this.f_19823_;
   }

   @Nullable
   public Entity m_146895_() {
      return this.f_19823_.isEmpty() ? null : this.f_19823_.get(0);
   }

   public boolean m_20363_(Entity p_20364_) {
      return this.f_19823_.contains(p_20364_);
   }

   public boolean m_146862_(Predicate<Entity> p_146863_) {
      for(Entity entity : this.f_19823_) {
         if (p_146863_.test(entity)) {
            return true;
         }
      }

      return false;
   }

   private Stream<Entity> m_146920_() {
      return this.f_19823_.stream().flatMap(Entity::m_20199_);
   }

   public Stream<Entity> m_20199_() {
      return Stream.concat(Stream.of(this), this.m_146920_());
   }

   public Stream<Entity> m_142429_() {
      return Stream.concat(this.f_19823_.stream().flatMap(Entity::m_142429_), Stream.of(this));
   }

   public Iterable<Entity> m_146897_() {
      return () -> {
         return this.m_146920_().iterator();
      };
   }

   public boolean m_146898_() {
      return this.m_146920_().filter((p_185943_) -> {
         return p_185943_ instanceof Player;
      }).count() == 1L;
   }

   public Entity m_20201_() {
      Entity entity;
      for(entity = this; entity.m_20159_(); entity = entity.m_20202_()) {
      }

      return entity;
   }

   public boolean m_20365_(Entity p_20366_) {
      return this.m_20201_() == p_20366_.m_20201_();
   }

   public boolean m_20367_(Entity p_20368_) {
      if (!p_20368_.m_20159_()) {
         return false;
      } else {
         Entity entity = p_20368_.m_20202_();
         return entity == this ? true : this.m_20367_(entity);
      }
   }

   public boolean m_6109_() {
      LivingEntity livingentity = this.m_6688_();
      if (livingentity instanceof Player player) {
         return player.m_7578_();
      } else {
         return this.m_21515_();
      }
   }

   public boolean m_21515_() {
      return !this.m_9236_().f_46443_;
   }

   protected static Vec3 m_19903_(double p_19904_, double p_19905_, float p_19906_) {
      double d0 = (p_19904_ + p_19905_ + (double)1.0E-5F) / 2.0D;
      float f = -Mth.m_14031_(p_19906_ * ((float)Math.PI / 180F));
      float f1 = Mth.m_14089_(p_19906_ * ((float)Math.PI / 180F));
      float f2 = Math.max(Math.abs(f), Math.abs(f1));
      return new Vec3((double)f * d0 / (double)f2, 0.0D, (double)f1 * d0 / (double)f2);
   }

   public Vec3 m_7688_(LivingEntity p_20123_) {
      return new Vec3(this.m_20185_(), this.m_20191_().f_82292_, this.m_20189_());
   }

   @Nullable
   public Entity m_20202_() {
      return this.f_19824_;
   }

   @Nullable
   public Entity m_275832_() {
      return this.f_19824_ != null && this.f_19824_.m_6688_() == this ? this.f_19824_ : null;
   }

   public PushReaction m_7752_() {
      return PushReaction.NORMAL;
   }

   public SoundSource m_5720_() {
      return SoundSource.NEUTRAL;
   }

   protected int m_6101_() {
      return 1;
   }

   public CommandSourceStack m_20203_() {
      return new CommandSourceStack(this, this.m_20182_(), this.m_20155_(), this.m_9236_() instanceof ServerLevel ? (ServerLevel)this.m_9236_() : null, this.m_8088_(), this.m_7755_().getString(), this.m_5446_(), this.m_9236_().m_7654_(), this);
   }

   protected int m_8088_() {
      return 0;
   }

   public boolean m_20310_(int p_20311_) {
      return this.m_8088_() >= p_20311_;
   }

   public boolean m_6999_() {
      return this.m_9236_().m_46469_().m_46207_(GameRules.f_46144_);
   }

   public boolean m_7028_() {
      return true;
   }

   public boolean m_6102_() {
      return true;
   }

   public void m_7618_(EntityAnchorArgument.Anchor p_20033_, Vec3 p_20034_) {
      Vec3 vec3 = p_20033_.m_90377_(this);
      double d0 = p_20034_.f_82479_ - vec3.f_82479_;
      double d1 = p_20034_.f_82480_ - vec3.f_82480_;
      double d2 = p_20034_.f_82481_ - vec3.f_82481_;
      double d3 = Math.sqrt(d0 * d0 + d2 * d2);
      this.m_146926_(Mth.m_14177_((float)(-(Mth.m_14136_(d1, d3) * (double)(180F / (float)Math.PI)))));
      this.m_146922_(Mth.m_14177_((float)(Mth.m_14136_(d2, d0) * (double)(180F / (float)Math.PI)) - 90.0F));
      this.m_5616_(this.m_146908_());
      this.f_19860_ = this.m_146909_();
      this.f_19859_ = this.m_146908_();
   }

   @Deprecated // Forge: Use no parameter version instead, only for vanilla Tags
   public boolean m_204031_(TagKey<Fluid> p_204032_, double p_204033_) {
      this.updateFluidHeightAndDoFluidPushing();
      if(p_204032_ == FluidTags.f_13131_) return this.isInFluidType(net.minecraftforge.common.ForgeMod.WATER_TYPE.get());
      else if (p_204032_ == FluidTags.f_13132_) return this.isInFluidType(net.minecraftforge.common.ForgeMod.LAVA_TYPE.get());
      else return false;
   }

   public void updateFluidHeightAndDoFluidPushing() {
      if (this.m_146899_()) {
         return;
      } else {
         AABB aabb = this.m_20191_().m_82406_(0.001D);
         int i = Mth.m_14107_(aabb.f_82288_);
         int j = Mth.m_14165_(aabb.f_82291_);
         int k = Mth.m_14107_(aabb.f_82289_);
         int l = Mth.m_14165_(aabb.f_82292_);
         int i1 = Mth.m_14107_(aabb.f_82290_);
         int j1 = Mth.m_14165_(aabb.f_82293_);
         double d0 = 0.0D;
         boolean flag = this.m_6063_();
         boolean flag1 = false;
         Vec3 vec3 = Vec3.f_82478_;
         int k1 = 0;
         BlockPos.MutableBlockPos blockpos$mutableblockpos = new BlockPos.MutableBlockPos();
         it.unimi.dsi.fastutil.objects.Object2ObjectMap<net.minecraftforge.fluids.FluidType, org.apache.commons.lang3.tuple.MutableTriple<Double, Vec3, Integer>> interimCalcs = new it.unimi.dsi.fastutil.objects.Object2ObjectArrayMap<>(net.minecraftforge.fluids.FluidType.SIZE.get() - 1);

         for(int l1 = i; l1 < j; ++l1) {
            for(int i2 = k; i2 < l; ++i2) {
               for(int j2 = i1; j2 < j1; ++j2) {
                  blockpos$mutableblockpos.m_122178_(l1, i2, j2);
                  FluidState fluidstate = this.m_9236_().m_6425_(blockpos$mutableblockpos);
                  net.minecraftforge.fluids.FluidType fluidType = fluidstate.getFluidType();
                  if (!fluidType.isAir()) {
                     double d1 = (double)((float)i2 + fluidstate.m_76155_(this.m_9236_(), blockpos$mutableblockpos));
                     if (d1 >= aabb.f_82289_) {
                        flag1 = true;
                        org.apache.commons.lang3.tuple.MutableTriple<Double, Vec3, Integer> interim = interimCalcs.computeIfAbsent(fluidType, t -> org.apache.commons.lang3.tuple.MutableTriple.of(0.0D, Vec3.f_82478_, 0));
                        interim.setLeft(Math.max(d1 - aabb.f_82289_, interim.getLeft()));
                        if (this.isPushedByFluid(fluidType)) {
                           Vec3 vec31 = fluidstate.m_76179_(this.m_9236_(), blockpos$mutableblockpos);
                           if (interim.getLeft() < 0.4D) {
                              vec31 = vec31.m_82490_(interim.getLeft());
                           }

                           interim.setMiddle(interim.getMiddle().m_82549_(vec31));
                           interim.setRight(interim.getRight() + 1);
                        }
                     }
                  }
               }
            }
         }

         interimCalcs.forEach((fluidType, interim) -> {
         if (interim.getMiddle().m_82553_() > 0.0D) {
            if (interim.getRight() > 0) {
               interim.setMiddle(interim.getMiddle().m_82490_(1.0D / (double)interim.getRight()));
            }

            if (!(this instanceof Player)) {
               interim.setMiddle(interim.getMiddle().m_82541_());
            }

            Vec3 vec32 = this.m_20184_();
            interim.setMiddle(interim.getMiddle().m_82490_(this.getFluidMotionScale(fluidType)));
            double d2 = 0.003D;
            if (Math.abs(vec32.f_82479_) < 0.003D && Math.abs(vec32.f_82481_) < 0.003D && interim.getMiddle().m_82553_() < 0.0045000000000000005D) {
               interim.setMiddle(interim.getMiddle().m_82541_().m_82490_(0.0045000000000000005D));
            }

            this.m_20256_(this.m_20184_().m_82549_(interim.getMiddle()));
         }

         this.setFluidTypeHeight(fluidType, interim.getLeft());
         });
      }
   }

   public boolean m_146899_() {
      AABB aabb = this.m_20191_().m_82400_(1.0D);
      int i = Mth.m_14107_(aabb.f_82288_);
      int j = Mth.m_14165_(aabb.f_82291_);
      int k = Mth.m_14107_(aabb.f_82290_);
      int l = Mth.m_14165_(aabb.f_82293_);
      return !this.m_9236_().m_151572_(i, k, j, l);
   }

   @Deprecated // Forge: Use getFluidTypeHeight instead
   public double m_204036_(TagKey<Fluid> p_204037_) {
      if (p_204037_ == FluidTags.f_13131_) return getFluidTypeHeight(net.minecraftforge.common.ForgeMod.WATER_TYPE.get());
      else if (p_204037_ == FluidTags.f_13132_) return getFluidTypeHeight(net.minecraftforge.common.ForgeMod.LAVA_TYPE.get());
      return this.f_19799_.getDouble(p_204037_);
   }

   public double m_20204_() {
      return (double)this.m_20192_() < 0.4D ? 0.0D : 0.4D;
   }

   public final float m_20205_() {
      return this.f_19815_.f_20377_;
   }

   public final float m_20206_() {
      return this.f_19815_.f_20378_;
   }

   public float m_278726_() {
      return this.m_20206_() + 0.5F;
   }

   public Packet<ClientGamePacketListener> m_5654_() {
      return new ClientboundAddEntityPacket(this);
   }

   public EntityDimensions m_6972_(Pose p_19975_) {
      return this.f_19847_.m_20680_();
   }

   public Vec3 m_20182_() {
      return this.f_19825_;
   }

   public Vec3 m_213870_() {
      return this.m_20182_();
   }

   public BlockPos m_20183_() {
      return this.f_19826_;
   }

   public BlockState m_146900_() {
      if (this.f_185934_ == null) {
         this.f_185934_ = this.m_9236_().m_8055_(this.m_20183_());
      }

      return this.f_185934_;
   }

   public ChunkPos m_146902_() {
      return this.f_185933_;
   }

   public Vec3 m_20184_() {
      return this.f_19827_;
   }

   public void m_20256_(Vec3 p_20257_) {
      this.f_19827_ = p_20257_;
   }

   public void m_246865_(Vec3 p_250128_) {
      this.m_20256_(this.m_20184_().m_82549_(p_250128_));
   }

   public void m_20334_(double p_20335_, double p_20336_, double p_20337_) {
      this.m_20256_(new Vec3(p_20335_, p_20336_, p_20337_));
   }

   public final int m_146903_() {
      return this.f_19826_.m_123341_();
   }

   public final double m_20185_() {
      return this.f_19825_.f_82479_;
   }

   public double m_20165_(double p_20166_) {
      return this.f_19825_.f_82479_ + (double)this.m_20205_() * p_20166_;
   }

   public double m_20208_(double p_20209_) {
      return this.m_20165_((2.0D * this.f_19796_.m_188500_() - 1.0D) * p_20209_);
   }

   public final int m_146904_() {
      return this.f_19826_.m_123342_();
   }

   public final double m_20186_() {
      return this.f_19825_.f_82480_;
   }

   public double m_20227_(double p_20228_) {
      return this.f_19825_.f_82480_ + (double)this.m_20206_() * p_20228_;
   }

   public double m_20187_() {
      return this.m_20227_(this.f_19796_.m_188500_());
   }

   public double m_20188_() {
      return this.f_19825_.f_82480_ + (double)this.f_19816_;
   }

   public final int m_146907_() {
      return this.f_19826_.m_123343_();
   }

   public final double m_20189_() {
      return this.f_19825_.f_82481_;
   }

   public double m_20246_(double p_20247_) {
      return this.f_19825_.f_82481_ + (double)this.m_20205_() * p_20247_;
   }

   public double m_20262_(double p_20263_) {
      return this.m_20246_((2.0D * this.f_19796_.m_188500_() - 1.0D) * p_20263_);
   }

   public final void m_20343_(double p_20344_, double p_20345_, double p_20346_) {
      if (this.f_19825_.f_82479_ != p_20344_ || this.f_19825_.f_82480_ != p_20345_ || this.f_19825_.f_82481_ != p_20346_) {
         this.f_19825_ = new Vec3(p_20344_, p_20345_, p_20346_);
         int i = Mth.m_14107_(p_20344_);
         int j = Mth.m_14107_(p_20345_);
         int k = Mth.m_14107_(p_20346_);
         if (i != this.f_19826_.m_123341_() || j != this.f_19826_.m_123342_() || k != this.f_19826_.m_123343_()) {
            this.f_19826_ = new BlockPos(i, j, k);
            this.f_185934_ = null;
            if (SectionPos.m_123171_(i) != this.f_185933_.f_45578_ || SectionPos.m_123171_(k) != this.f_185933_.f_45579_) {
               this.f_185933_ = new ChunkPos(this.f_19826_);
            }
         }

         this.f_146801_.m_142044_();
      }
      if (this.isAddedToWorld() && !this.f_19853_.f_46443_ && !this.m_213877_()) this.f_19853_.m_6325_((int) Math.floor(p_20344_) >> 4, (int) Math.floor(p_20346_) >> 4); // Forge - ensure target chunk is loaded.

   }

   public void m_6043_() {
   }

   public Vec3 m_7398_(float p_20347_) {
      return this.m_20318_(p_20347_).m_82520_(0.0D, (double)this.f_19816_ * 0.7D, 0.0D);
   }

   public void m_141965_(ClientboundAddEntityPacket p_146866_) {
      int i = p_146866_.m_131496_();
      double d0 = p_146866_.m_131500_();
      double d1 = p_146866_.m_131501_();
      double d2 = p_146866_.m_131502_();
      this.m_217006_(d0, d1, d2);
      this.m_6027_(d0, d1, d2);
      this.m_146926_(p_146866_.m_237566_());
      this.m_146922_(p_146866_.m_237567_());
      this.m_20234_(i);
      this.m_20084_(p_146866_.m_131499_());
   }

   @Nullable
   public ItemStack m_142340_() {
      return null;
   }

   public void m_146924_(boolean p_146925_) {
      this.f_146808_ = p_146925_;
   }

   public boolean m_142079_() {
      return !this.m_6095_().m_204039_(EntityTypeTags.f_144294_);
   }

   public boolean m_203117_() {
      return (this.f_146808_ || this.f_146809_) && this.m_142079_();
   }

   public float m_146908_() {
      return this.f_19857_;
   }

   public float m_213816_() {
      return this.m_146908_();
   }

   public void m_146922_(float p_146923_) {
      if (!Float.isFinite(p_146923_)) {
         Util.m_143785_("Invalid entity rotation: " + p_146923_ + ", discarding.");
      } else {
         this.f_19857_ = p_146923_;
      }
   }

   public float m_146909_() {
      return this.f_19858_;
   }

   public void m_146926_(float p_146927_) {
      if (!Float.isFinite(p_146927_)) {
         Util.m_143785_("Invalid entity rotation: " + p_146927_ + ", discarding.");
      } else {
         this.f_19858_ = p_146927_;
      }
   }

   public boolean m_264410_() {
      return false;
   }

   @Deprecated /** Forge: Use {@link net.minecraftforge.common.extensions.IForgeEntity#getStepHeight()} */
   public float m_274421_() {
      return this.f_19793_;
   }

   public void m_274367_(float p_275672_) {
      this.f_19793_ = p_275672_;
   }

   public final boolean m_213877_() {
      return this.f_146795_ != null;
   }

   @Nullable
   public Entity.RemovalReason m_146911_() {
      return this.f_146795_;
   }

   public final void m_142467_(Entity.RemovalReason p_146876_) {
      if (this.f_146795_ == null) {
         this.f_146795_ = p_146876_;
      }

      if (this.f_146795_.m_146965_()) {
         this.m_8127_();
      }

      this.m_20197_().forEach(Entity::m_8127_);
      this.f_146801_.m_142472_(p_146876_);
   }

   protected void m_146912_() {
      this.f_146795_ = null;
   }

   public void m_141960_(EntityInLevelCallback p_146849_) {
      this.f_146801_ = p_146849_;
   }

   public boolean m_142391_() {
      if (this.f_146795_ != null && !this.f_146795_.m_146966_()) {
         return false;
      } else if (this.m_20159_()) {
         return false;
      } else {
         return !this.m_20160_() || !this.m_146898_();
      }
   }

   public boolean m_142389_() {
      return false;
   }

   public boolean m_142265_(Level p_146843_, BlockPos p_146844_) {
      return true;
   }

   /* ================================== Forge Start =====================================*/

   private boolean canUpdate = true;
   @Override
   public void canUpdate(boolean value) {
      this.canUpdate = value;
   }
   @Override
   public boolean canUpdate() {
      return this.canUpdate;
   }
   private java.util.Collection<ItemEntity> captureDrops = null;
   @Override
   public java.util.Collection<ItemEntity> captureDrops() {
      return captureDrops;
   }
   @Override
   public java.util.Collection<ItemEntity> captureDrops(java.util.Collection<ItemEntity> value) {
      java.util.Collection<ItemEntity> ret = captureDrops;
      this.captureDrops = value;
      return ret;
   }
   private CompoundTag persistentData;
   @Override
   public CompoundTag getPersistentData() {
      if (persistentData == null)
         persistentData = new CompoundTag();
      return persistentData;
   }
   @Override
   public boolean canTrample(BlockState state, BlockPos pos, float fallDistance) {
      return f_19853_.f_46441_.m_188501_() < fallDistance - 0.5F
          && this instanceof LivingEntity
          && (this instanceof Player || net.minecraftforge.event.ForgeEventFactory.getMobGriefingEvent(f_19853_, this))
          && this.m_20205_() * this.m_20205_() * this.m_20206_() > 0.512F;
   }

   /**
    * Internal use for keeping track of entities that are tracked by a world, to
    * allow guarantees that entity position changes will force a chunk load, avoiding
    * potential issues with entity desyncing and bad chunk data.
    */
   private boolean isAddedToWorld;

   @Override
   public final boolean isAddedToWorld() { return this.isAddedToWorld; }

   @Override
   public void onAddedToWorld() { this.isAddedToWorld = true; }

   @Override
   public void onRemovedFromWorld() { this.isAddedToWorld = false; }

   @Override
   public void revive() {
      this.m_146912_();
      this.reviveCaps();
   }

   // no AT because of overrides
   /**
    * Accessor method for {@link #getEyeHeight(Pose, EntityDimensions)}
    */
   public float getEyeHeightAccess(Pose pose, EntityDimensions size) {
      return this.m_6380_(pose, size);
   }

   protected Object2DoubleMap<net.minecraftforge.fluids.FluidType> forgeFluidTypeHeight = new Object2DoubleArrayMap<>(net.minecraftforge.fluids.FluidType.SIZE.get());
   private net.minecraftforge.fluids.FluidType forgeFluidTypeOnEyes = net.minecraftforge.common.ForgeMod.EMPTY_TYPE.get();
   protected final void setFluidTypeHeight(net.minecraftforge.fluids.FluidType type, double height) {
      this.forgeFluidTypeHeight.put(type, height);
   }
   @Override
   public final double getFluidTypeHeight(net.minecraftforge.fluids.FluidType type) {
      return this.forgeFluidTypeHeight.getDouble(type);
   }
   @Override
   public final boolean isInFluidType(java.util.function.BiPredicate<net.minecraftforge.fluids.FluidType, Double> predicate, boolean forAllTypes) {
      return forAllTypes ? this.forgeFluidTypeHeight.object2DoubleEntrySet().stream().allMatch(e -> predicate.test(e.getKey(), e.getDoubleValue()))
              : this.forgeFluidTypeHeight.object2DoubleEntrySet().stream().anyMatch(e -> predicate.test(e.getKey(), e.getDoubleValue()));
   }
   @Override
   public final boolean isInFluidType() {
      return this.forgeFluidTypeHeight.size() > 0;
   }
  @Override
  public final net.minecraftforge.fluids.FluidType getEyeInFluidType() {
      return forgeFluidTypeOnEyes;
   }
   @Override
   public net.minecraftforge.fluids.FluidType getMaxHeightFluidType() {
      return this.forgeFluidTypeHeight.object2DoubleEntrySet().stream().max(java.util.Comparator.comparingDouble(Object2DoubleMap.Entry::getDoubleValue)).map(Object2DoubleMap.Entry::getKey).orElseGet(net.minecraftforge.common.ForgeMod.EMPTY_TYPE);
   }

   /* ================================== Forge End =====================================*/


   public Level m_9236_() {
      return this.f_19853_;
   }

   protected void m_284535_(Level p_285201_) {
      this.f_19853_ = p_285201_;
   }

   public DamageSources m_269291_() {
      return this.m_9236_().m_269111_();
   }

   @FunctionalInterface
   public interface MoveFunction {
      void m_20372_(Entity p_20373_, double p_20374_, double p_20375_, double p_20376_);
   }

   public static enum MovementEmission {
      NONE(false, false),
      SOUNDS(true, false),
      EVENTS(false, true),
      ALL(true, true);

      final boolean f_146935_;
      final boolean f_146936_;

      private MovementEmission(boolean p_146942_, boolean p_146943_) {
         this.f_146935_ = p_146942_;
         this.f_146936_ = p_146943_;
      }

      public boolean m_146944_() {
         return this.f_146936_ || this.f_146935_;
      }

      public boolean m_146945_() {
         return this.f_146936_;
      }

      public boolean m_146946_() {
         return this.f_146935_;
      }
   }

   public static enum RemovalReason {
      KILLED(true, false),
      DISCARDED(true, false),
      UNLOADED_TO_CHUNK(false, true),
      UNLOADED_WITH_PLAYER(false, false),
      CHANGED_DIMENSION(false, false);

      private final boolean f_146956_;
      private final boolean f_146957_;

      private RemovalReason(boolean p_146963_, boolean p_146964_) {
         this.f_146956_ = p_146963_;
         this.f_146957_ = p_146964_;
      }

      public boolean m_146965_() {
         return this.f_146956_;
      }

      public boolean m_146966_() {
         return this.f_146957_;
      }
   }
}
