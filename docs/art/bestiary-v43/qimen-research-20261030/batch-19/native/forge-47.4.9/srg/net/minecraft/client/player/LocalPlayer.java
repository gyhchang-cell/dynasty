package net.minecraft.client.player;

import com.google.common.collect.Lists;
import com.mojang.logging.LogUtils;
import java.util.Iterator;
import java.util.List;
import java.util.Objects;
import java.util.stream.StreamSupport;
import javax.annotation.Nullable;
import net.minecraft.client.ClientRecipeBook;
import net.minecraft.client.KeyMapping;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.DeathScreen;
import net.minecraft.client.gui.screens.ReceivingLevelScreen;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.client.gui.screens.inventory.BookEditScreen;
import net.minecraft.client.gui.screens.inventory.CommandBlockEditScreen;
import net.minecraft.client.gui.screens.inventory.HangingSignEditScreen;
import net.minecraft.client.gui.screens.inventory.JigsawBlockEditScreen;
import net.minecraft.client.gui.screens.inventory.MinecartCommandBlockEditScreen;
import net.minecraft.client.gui.screens.inventory.SignEditScreen;
import net.minecraft.client.gui.screens.inventory.StructureBlockEditScreen;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.multiplayer.ClientPacketListener;
import net.minecraft.client.resources.sounds.AmbientSoundHandler;
import net.minecraft.client.resources.sounds.BiomeAmbientSoundsHandler;
import net.minecraft.client.resources.sounds.BubbleColumnAmbientSoundHandler;
import net.minecraft.client.resources.sounds.ElytraOnPlayerSoundInstance;
import net.minecraft.client.resources.sounds.RidingMinecartSoundInstance;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.client.resources.sounds.UnderwaterAmbientSoundHandler;
import net.minecraft.client.resources.sounds.UnderwaterAmbientSoundInstances;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ServerboundClientCommandPacket;
import net.minecraft.network.protocol.game.ServerboundContainerClosePacket;
import net.minecraft.network.protocol.game.ServerboundMovePlayerPacket;
import net.minecraft.network.protocol.game.ServerboundMoveVehiclePacket;
import net.minecraft.network.protocol.game.ServerboundPlayerAbilitiesPacket;
import net.minecraft.network.protocol.game.ServerboundPlayerActionPacket;
import net.minecraft.network.protocol.game.ServerboundPlayerCommandPacket;
import net.minecraft.network.protocol.game.ServerboundPlayerInputPacket;
import net.minecraft.network.protocol.game.ServerboundRecipeBookSeenRecipePacket;
import net.minecraft.network.protocol.game.ServerboundSwingPacket;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.StatsCounter;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.PlayerRideableJumping;
import net.minecraft.world.entity.Pose;
import net.minecraft.world.entity.vehicle.AbstractMinecart;
import net.minecraft.world.entity.vehicle.Boat;
import net.minecraft.world.inventory.ClickAction;
import net.minecraft.world.item.ElytraItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.level.BaseCommandBlock;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.entity.CommandBlockEntity;
import net.minecraft.world.level.block.entity.HangingSignBlockEntity;
import net.minecraft.world.level.block.entity.JigsawBlockEntity;
import net.minecraft.world.level.block.entity.SignBlockEntity;
import net.minecraft.world.level.block.entity.StructureBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec2;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.slf4j.Logger;

@OnlyIn(Dist.CLIENT)
public class LocalPlayer extends AbstractClientPlayer {
   public static final Logger f_234121_ = LogUtils.getLogger();
   private static final int f_172525_ = 20;
   private static final int f_172526_ = 600;
   private static final int f_172527_ = 100;
   private static final float f_172528_ = 0.6F;
   private static final double f_172529_ = 0.35D;
   private static final double f_197409_ = (double)0.13962634F;
   private static final float f_234120_ = 0.3F;
   public final ClientPacketListener f_108617_;
   private final StatsCounter f_108591_;
   private final ClientRecipeBook f_108592_;
   private final List<AmbientSoundHandler> f_108593_ = Lists.newArrayList();
   private int f_108594_ = 0;
   private double f_108595_;
   private double f_108596_;
   private double f_108597_;
   private float f_108598_;
   private float f_108599_;
   private boolean f_108600_;
   private boolean f_108601_;
   private boolean f_108602_;
   private boolean f_108603_;
   private int f_108604_;
   private boolean f_108605_;
   @Nullable
   private String f_108606_;
   public Input f_108618_;
   protected final Minecraft f_108619_;
   protected int f_108583_;
   public float f_108585_;
   public float f_108586_;
   public float f_108587_;
   public float f_108588_;
   private int f_108607_;
   private float f_108608_;
   public float f_108589_;
   public float f_108590_;
   private boolean f_108609_;
   @Nullable
   private InteractionHand f_108610_;
   private boolean f_108611_;
   private boolean f_108612_ = true;
   private int f_108613_;
   private boolean f_108614_;
   private int f_108615_;
   private boolean f_108616_ = true;

   public LocalPlayer(Minecraft p_108621_, ClientLevel p_108622_, ClientPacketListener p_108623_, StatsCounter p_108624_, ClientRecipeBook p_108625_, boolean p_108626_, boolean p_108627_) {
      super(p_108622_, p_108623_.m_105144_());
      this.f_108619_ = p_108621_;
      this.f_108617_ = p_108623_;
      this.f_108591_ = p_108624_;
      this.f_108592_ = p_108625_;
      this.f_108602_ = p_108626_;
      this.f_108603_ = p_108627_;
      this.f_108593_.add(new UnderwaterAmbientSoundHandler(this, p_108621_.m_91106_()));
      this.f_108593_.add(new BubbleColumnAmbientSoundHandler(this));
      this.f_108593_.add(new BiomeAmbientSoundsHandler(this, p_108621_.m_91106_(), p_108622_.m_7062_()));
   }

   public boolean m_6469_(DamageSource p_108662_, float p_108663_) {
      net.minecraftforge.common.ForgeHooks.onPlayerAttack(this, p_108662_, p_108663_);
      return false;
   }

   public void m_5634_(float p_108708_) {
   }

   public boolean m_7998_(Entity p_108667_, boolean p_108668_) {
      if (!super.m_7998_(p_108667_, p_108668_)) {
         return false;
      } else {
         if (p_108667_ instanceof AbstractMinecart) {
            this.f_108619_.m_91106_().m_120367_(new RidingMinecartSoundInstance(this, (AbstractMinecart)p_108667_, true));
            this.f_108619_.m_91106_().m_120367_(new RidingMinecartSoundInstance(this, (AbstractMinecart)p_108667_, false));
         }

         return true;
      }
   }

   public void m_6038_() {
      super.m_6038_();
      this.f_108611_ = false;
   }

   public float m_5686_(float p_108742_) {
      return this.m_146909_();
   }

   public float m_5675_(float p_108753_) {
      return this.m_20159_() ? super.m_5675_(p_108753_) : this.m_146908_();
   }

   public void m_8119_() {
      if (this.m_9236_().m_151577_(this.m_146903_(), this.m_146907_())) {
         super.m_8119_();
         if (this.m_20159_()) {
            this.f_108617_.m_104955_(new ServerboundMovePlayerPacket.Rot(this.m_146908_(), this.m_146909_(), this.m_20096_()));
            this.f_108617_.m_104955_(new ServerboundPlayerInputPacket(this.f_20900_, this.f_20902_, this.f_108618_.f_108572_, this.f_108618_.f_108573_));
            Entity entity = this.m_20201_();
            if (entity != this && entity.m_6109_()) {
               this.f_108617_.m_104955_(new ServerboundMoveVehiclePacket(entity));
               this.m_254869_();
            }
         } else {
            this.m_108640_();
         }

         for(AmbientSoundHandler ambientsoundhandler : this.f_108593_) {
            ambientsoundhandler.m_7551_();
         }

      }
   }

   public float m_108762_() {
      for(AmbientSoundHandler ambientsoundhandler : this.f_108593_) {
         if (ambientsoundhandler instanceof BiomeAmbientSoundsHandler) {
            return ((BiomeAmbientSoundsHandler)ambientsoundhandler).m_119654_();
         }
      }

      return 0.0F;
   }

   private void m_108640_() {
      this.m_254869_();
      boolean flag = this.m_6144_();
      if (flag != this.f_108602_) {
         ServerboundPlayerCommandPacket.Action serverboundplayercommandpacket$action = flag ? ServerboundPlayerCommandPacket.Action.PRESS_SHIFT_KEY : ServerboundPlayerCommandPacket.Action.RELEASE_SHIFT_KEY;
         this.f_108617_.m_104955_(new ServerboundPlayerCommandPacket(this, serverboundplayercommandpacket$action));
         this.f_108602_ = flag;
      }

      if (this.m_108636_()) {
         double d4 = this.m_20185_() - this.f_108595_;
         double d0 = this.m_20186_() - this.f_108596_;
         double d1 = this.m_20189_() - this.f_108597_;
         double d2 = (double)(this.m_146908_() - this.f_108598_);
         double d3 = (double)(this.m_146909_() - this.f_108599_);
         ++this.f_108604_;
         boolean flag1 = Mth.m_211592_(d4, d0, d1) > Mth.m_144952_(2.0E-4D) || this.f_108604_ >= 20;
         boolean flag2 = d2 != 0.0D || d3 != 0.0D;
         if (this.m_20159_()) {
            Vec3 vec3 = this.m_20184_();
            this.f_108617_.m_104955_(new ServerboundMovePlayerPacket.PosRot(vec3.f_82479_, -999.0D, vec3.f_82481_, this.m_146908_(), this.m_146909_(), this.m_20096_()));
            flag1 = false;
         } else if (flag1 && flag2) {
            this.f_108617_.m_104955_(new ServerboundMovePlayerPacket.PosRot(this.m_20185_(), this.m_20186_(), this.m_20189_(), this.m_146908_(), this.m_146909_(), this.m_20096_()));
         } else if (flag1) {
            this.f_108617_.m_104955_(new ServerboundMovePlayerPacket.Pos(this.m_20185_(), this.m_20186_(), this.m_20189_(), this.m_20096_()));
         } else if (flag2) {
            this.f_108617_.m_104955_(new ServerboundMovePlayerPacket.Rot(this.m_146908_(), this.m_146909_(), this.m_20096_()));
         } else if (this.f_108600_ != this.m_20096_()) {
            this.f_108617_.m_104955_(new ServerboundMovePlayerPacket.StatusOnly(this.m_20096_()));
         }

         if (flag1) {
            this.f_108595_ = this.m_20185_();
            this.f_108596_ = this.m_20186_();
            this.f_108597_ = this.m_20189_();
            this.f_108604_ = 0;
         }

         if (flag2) {
            this.f_108598_ = this.m_146908_();
            this.f_108599_ = this.m_146909_();
         }

         this.f_108600_ = this.m_20096_();
         this.f_108612_ = this.f_108619_.f_91066_.m_231812_().m_231551_();
      }

   }

   private void m_254869_() {
      boolean flag = this.m_20142_();
      if (flag != this.f_108603_) {
         ServerboundPlayerCommandPacket.Action serverboundplayercommandpacket$action = flag ? ServerboundPlayerCommandPacket.Action.START_SPRINTING : ServerboundPlayerCommandPacket.Action.STOP_SPRINTING;
         this.f_108617_.m_104955_(new ServerboundPlayerCommandPacket(this, serverboundplayercommandpacket$action));
         this.f_108603_ = flag;
      }

   }

   public boolean m_108700_(boolean p_108701_) {
      ServerboundPlayerActionPacket.Action serverboundplayeractionpacket$action = p_108701_ ? ServerboundPlayerActionPacket.Action.DROP_ALL_ITEMS : ServerboundPlayerActionPacket.Action.DROP_ITEM;
      if (m_6117_() && m_7655_() == InteractionHand.MAIN_HAND && (p_108701_ || m_21211_().m_41613_() == 1)) m_5810_(); // Forge: fix MC-231097 on the clientside
      ItemStack itemstack = this.m_150109_().m_182403_(p_108701_);
      this.f_108617_.m_104955_(new ServerboundPlayerActionPacket(serverboundplayeractionpacket$action, BlockPos.f_121853_, Direction.DOWN));
      return !itemstack.m_41619_();
   }

   public void m_6674_(InteractionHand p_108660_) {
      super.m_6674_(p_108660_);
      this.f_108617_.m_104955_(new ServerboundSwingPacket(p_108660_));
   }

   public void m_7583_() {
      this.f_108617_.m_104955_(new ServerboundClientCommandPacket(ServerboundClientCommandPacket.Action.PERFORM_RESPAWN));
      KeyMapping.m_289723_();
   }

   protected void m_6475_(DamageSource p_108729_, float p_108730_) {
      if (!this.m_6673_(p_108729_)) {
         this.m_21153_(this.m_21223_() - p_108730_);
      }
   }

   public void m_6915_() {
      this.f_108617_.m_104955_(new ServerboundContainerClosePacket(this.f_36096_.f_38840_));
      this.m_108763_();
   }

   public void m_108763_() {
      super.m_6915_();
      this.f_108619_.m_91152_((Screen)null);
   }

   public void m_108760_(float p_108761_) {
      if (this.f_108605_) {
         float f = this.m_21223_() - p_108761_;
         if (f <= 0.0F) {
            this.m_21153_(p_108761_);
            if (f < 0.0F) {
               this.f_19802_ = 10;
            }
         } else {
            this.f_20898_ = f;
            this.f_19802_ = 20;
            this.m_21153_(p_108761_);
            this.f_20917_ = 10;
            this.f_20916_ = this.f_20917_;
         }
      } else {
         this.m_21153_(p_108761_);
         this.f_108605_ = true;
      }

   }

   public void m_6885_() {
      this.f_108617_.m_104955_(new ServerboundPlayerAbilitiesPacket(this.m_150110_()));
   }

   public boolean m_7578_() {
      return true;
   }

   public boolean m_5791_() {
      return !this.m_150110_().f_35935_ && super.m_5791_();
   }

   public boolean m_5843_() {
      return !this.m_150110_().f_35935_ && super.m_5843_();
   }

   public boolean m_6039_() {
      return !this.m_150110_().f_35935_ && super.m_6039_();
   }

   protected void m_108765_() {
      this.f_108617_.m_104955_(new ServerboundPlayerCommandPacket(this, ServerboundPlayerCommandPacket.Action.START_RIDING_JUMP, Mth.m_14143_(this.m_108634_() * 100.0F)));
   }

   public void m_108628_() {
      this.f_108617_.m_104955_(new ServerboundPlayerCommandPacket(this, ServerboundPlayerCommandPacket.Action.OPEN_INVENTORY));
   }

   public void m_108748_(@Nullable String p_108749_) {
      this.f_108606_ = p_108749_;
   }

   @Nullable
   public String m_108629_() {
      return this.f_108606_;
   }

   public StatsCounter m_108630_() {
      return this.f_108591_;
   }

   public ClientRecipeBook m_108631_() {
      return this.f_108592_;
   }

   public void m_108675_(Recipe<?> p_108676_) {
      if (this.f_108592_.m_12717_(p_108676_)) {
         this.f_108592_.m_12721_(p_108676_);
         this.f_108617_.m_104955_(new ServerboundRecipeBookSeenRecipePacket(p_108676_));
      }

   }

   public int m_8088_() {
      return this.f_108594_;
   }

   public void m_108648_(int p_108649_) {
      this.f_108594_ = p_108649_;
   }

   public void m_5661_(Component p_108696_, boolean p_108697_) {
      this.f_108619_.m_240442_().m_240494_(p_108696_, p_108697_);
   }

   private void m_108704_(double p_108705_, double p_108706_) {
      BlockPos blockpos = BlockPos.m_274561_(p_108705_, this.m_20186_(), p_108706_);
      if (this.m_108746_(blockpos)) {
         double d0 = p_108705_ - (double)blockpos.m_123341_();
         double d1 = p_108706_ - (double)blockpos.m_123343_();
         Direction direction = null;
         double d2 = Double.MAX_VALUE;
         Direction[] adirection = new Direction[]{Direction.WEST, Direction.EAST, Direction.NORTH, Direction.SOUTH};

         for(Direction direction1 : adirection) {
            double d3 = direction1.m_122434_().m_6150_(d0, 0.0D, d1);
            double d4 = direction1.m_122421_() == Direction.AxisDirection.POSITIVE ? 1.0D - d3 : d3;
            if (d4 < d2 && !this.m_108746_(blockpos.m_121945_(direction1))) {
               d2 = d4;
               direction = direction1;
            }
         }

         if (direction != null) {
            Vec3 vec3 = this.m_20184_();
            if (direction.m_122434_() == Direction.Axis.X) {
               this.m_20334_(0.1D * (double)direction.m_122429_(), vec3.f_82480_, vec3.f_82481_);
            } else {
               this.m_20334_(vec3.f_82479_, vec3.f_82480_, 0.1D * (double)direction.m_122431_());
            }
         }

      }
   }

   private boolean m_108746_(BlockPos p_108747_) {
      AABB aabb = this.m_20191_();
      AABB aabb1 = (new AABB((double)p_108747_.m_123341_(), aabb.f_82289_, (double)p_108747_.m_123343_(), (double)p_108747_.m_123341_() + 1.0D, aabb.f_82292_, (double)p_108747_.m_123343_() + 1.0D)).m_82406_(1.0E-7D);
      return this.m_9236_().m_186437_(this, aabb1);
   }

   public void m_108644_(float p_108645_, int p_108646_, int p_108647_) {
      this.f_36080_ = p_108645_;
      this.f_36079_ = p_108646_;
      this.f_36078_ = p_108647_;
   }

   public void m_213846_(Component p_234129_) {
      this.f_108619_.f_91065_.m_93076_().m_93785_(p_234129_);
   }

   public void m_7822_(byte p_108643_) {
      if (p_108643_ >= 24 && p_108643_ <= 28) {
         this.m_108648_(p_108643_ - 24);
      } else {
         super.m_7822_(p_108643_);
      }

   }

   public void m_108711_(boolean p_108712_) {
      this.f_108616_ = p_108712_;
   }

   public boolean m_108632_() {
      return this.f_108616_;
   }

   public void m_5496_(SoundEvent p_108651_, float p_108652_, float p_108653_) {
      net.minecraft.core.Holder<SoundEvent> holder = net.minecraft.core.registries.BuiltInRegistries.f_256894_.m_263177_(p_108651_);
      net.minecraftforge.event.PlayLevelSoundEvent.AtEntity event = net.minecraftforge.event.ForgeEventFactory.onPlaySoundAtEntity(this, holder, this.m_5720_(), p_108652_, p_108653_);
      if (event.isCanceled() || event.getSound() == null) return;
      p_108651_ = event.getSound().get();
      SoundSource source = event.getSource();
      p_108652_ = event.getNewVolume();
      p_108653_ = event.getNewPitch();
      this.m_9236_().m_7785_(this.m_20185_(), this.m_20186_(), this.m_20189_(), p_108651_, source, p_108652_, p_108653_, false);
   }

   public void m_6330_(SoundEvent p_108655_, SoundSource p_108656_, float p_108657_, float p_108658_) {
      this.m_9236_().m_7785_(this.m_20185_(), this.m_20186_(), this.m_20189_(), p_108655_, p_108656_, p_108657_, p_108658_, false);
   }

   public boolean m_21515_() {
      return true;
   }

   public void m_6672_(InteractionHand p_108718_) {
      ItemStack itemstack = this.m_21120_(p_108718_);
      if (!itemstack.m_41619_() && !this.m_6117_()) {
         super.m_6672_(p_108718_);
         this.f_108609_ = true;
         this.f_108610_ = p_108718_;
      }
   }

   public boolean m_6117_() {
      return this.f_108609_;
   }

   public void m_5810_() {
      super.m_5810_();
      this.f_108609_ = false;
   }

   public InteractionHand m_7655_() {
      return Objects.requireNonNullElse(this.f_108610_, InteractionHand.MAIN_HAND);
   }

   public void m_7350_(EntityDataAccessor<?> p_108699_) {
      super.m_7350_(p_108699_);
      if (f_20909_.equals(p_108699_)) {
         boolean flag = (this.f_19804_.m_135370_(f_20909_) & 1) > 0;
         InteractionHand interactionhand = (this.f_19804_.m_135370_(f_20909_) & 2) > 0 ? InteractionHand.OFF_HAND : InteractionHand.MAIN_HAND;
         if (flag && !this.f_108609_) {
            this.m_6672_(interactionhand);
         } else if (!flag && this.f_108609_) {
            this.m_5810_();
         }
      }

      if (f_19805_.equals(p_108699_) && this.m_21255_() && !this.f_108614_) {
         this.f_108619_.m_91106_().m_120367_(new ElytraOnPlayerSoundInstance(this));
      }

   }

   @Nullable
   public PlayerRideableJumping m_245714_() {
      Entity entity = this.m_275832_();
      if (entity instanceof PlayerRideableJumping playerrideablejumping) {
         if (playerrideablejumping.m_7132_()) {
            return playerrideablejumping;
         }
      }

      return null;
   }

   public float m_108634_() {
      return this.f_108608_;
   }

   public boolean m_143387_() {
      return this.f_108619_.m_167974_();
   }

   public void m_7739_(SignBlockEntity p_277970_, boolean p_277980_) {
      if (p_277970_ instanceof HangingSignBlockEntity hangingsignblockentity) {
         this.f_108619_.m_91152_(new HangingSignEditScreen(hangingsignblockentity, p_277980_, this.f_108619_.m_167974_()));
      } else {
         this.f_108619_.m_91152_(new SignEditScreen(p_277970_, p_277980_, this.f_108619_.m_167974_()));
      }

   }

   public void m_7907_(BaseCommandBlock p_108678_) {
      this.f_108619_.m_91152_(new MinecartCommandBlockEditScreen(p_108678_));
   }

   public void m_7698_(CommandBlockEntity p_108680_) {
      this.f_108619_.m_91152_(new CommandBlockEditScreen(p_108680_));
   }

   public void m_5966_(StructureBlockEntity p_108686_) {
      this.f_108619_.m_91152_(new StructureBlockEditScreen(p_108686_));
   }

   public void m_7569_(JigsawBlockEntity p_108682_) {
      this.f_108619_.m_91152_(new JigsawBlockEditScreen(p_108682_));
   }

   public void m_6986_(ItemStack p_108673_, InteractionHand p_108674_) {
      if (p_108673_.m_150930_(Items.f_42614_)) {
         this.f_108619_.m_91152_(new BookEditScreen(this, p_108673_, p_108674_));
      }

   }

   public void m_5704_(Entity p_108665_) {
      this.f_108619_.f_91061_.m_107329_(p_108665_, ParticleTypes.f_123797_);
   }

   public void m_5700_(Entity p_108710_) {
      this.f_108619_.f_91061_.m_107329_(p_108710_, ParticleTypes.f_123808_);
   }

   public boolean m_6144_() {
      return this.f_108618_ != null && this.f_108618_.f_108573_;
   }

   public boolean m_6047_() {
      return this.f_108601_;
   }

   public boolean m_108635_() {
      return this.m_6047_() || this.m_20143_();
   }

   public void m_6140_() {
      super.m_6140_();
      if (this.m_108636_()) {
         this.f_20900_ = this.f_108618_.f_108566_;
         this.f_20902_ = this.f_108618_.f_108567_;
         this.f_20899_ = this.f_108618_.f_108572_;
         this.f_108587_ = this.f_108585_;
         this.f_108588_ = this.f_108586_;
         this.f_108586_ += (this.m_146909_() - this.f_108586_) * 0.5F;
         this.f_108585_ += (this.m_146908_() - this.f_108585_) * 0.5F;
      }

   }

   protected boolean m_108636_() {
      return this.f_108619_.m_91288_() == this;
   }

   public void m_172530_() {
      this.m_20124_(Pose.STANDING);
      if (this.m_9236_() != null) {
         for(double d0 = this.m_20186_(); d0 > (double)this.m_9236_().m_141937_() && d0 < (double)this.m_9236_().m_151558_(); ++d0) {
            this.m_6034_(this.m_20185_(), d0, this.m_20189_());
            if (this.m_9236_().m_45786_(this)) {
               break;
            }
         }

         this.m_20256_(Vec3.f_82478_);
         this.m_146926_(0.0F);
      }

      this.m_21153_(this.m_21233_());
      this.f_20919_ = 0;
   }

   public void m_8107_() {
      if (this.f_108583_ > 0) {
         --this.f_108583_;
      }

      if (!(this.f_108619_.f_91080_ instanceof ReceivingLevelScreen)) {
         this.m_108641_();
      }

      boolean flag = this.f_108618_.f_108572_;
      boolean flag1 = this.f_108618_.f_108573_;
      boolean flag2 = this.m_108733_();
      this.f_108601_ = !this.m_150110_().f_35935_ && !this.m_6069_() && this.m_20175_(Pose.CROUCHING) && (this.m_6144_() || !this.m_5803_() && !this.m_20175_(Pose.STANDING));
      float f = Mth.m_14036_(0.3F + EnchantmentHelper.m_220302_(this), 0.0F, 1.0F);
      this.f_108618_.m_214106_(this.m_108635_(), f);
      net.minecraftforge.client.ForgeHooksClient.onMovementInputUpdate(this, this.f_108618_);
      this.f_108619_.m_91301_().m_120586_(this.f_108618_);
      if (this.m_6117_() && !this.m_20159_()) {
         this.f_108618_.f_108566_ *= 0.2F;
         this.f_108618_.f_108567_ *= 0.2F;
         this.f_108583_ = 0;
      }

      boolean flag3 = false;
      if (this.f_108613_ > 0) {
         --this.f_108613_;
         flag3 = true;
         this.f_108618_.f_108572_ = true;
      }

      if (!this.f_19794_) {
         this.m_108704_(this.m_20185_() - (double)this.m_20205_() * 0.35D, this.m_20189_() + (double)this.m_20205_() * 0.35D);
         this.m_108704_(this.m_20185_() - (double)this.m_20205_() * 0.35D, this.m_20189_() - (double)this.m_20205_() * 0.35D);
         this.m_108704_(this.m_20185_() + (double)this.m_20205_() * 0.35D, this.m_20189_() - (double)this.m_20205_() * 0.35D);
         this.m_108704_(this.m_20185_() + (double)this.m_20205_() * 0.35D, this.m_20189_() + (double)this.m_20205_() * 0.35D);
      }

      if (flag1) {
         this.f_108583_ = 0;
      }

      boolean flag4 = this.m_264082_();
      boolean flag5 = this.m_20159_() ? this.m_20202_().m_20096_() : this.m_20096_();
      boolean flag6 = !flag1 && !flag2;
      if ((flag5 || this.m_5842_() || this.canStartSwimming()) && flag6 && flag4) {
         if (this.f_108583_ <= 0 && !this.f_108619_.f_91066_.f_92091_.m_90857_()) {
            this.f_108583_ = 7;
         } else {
            this.m_6858_(true);
         }
      }

      if (!this.m_20142_() && (!(this.m_20069_() || this.isInFluidType((fluidType, height) -> this.canSwimInFluidType(fluidType))) || (this.m_5842_() || this.canStartSwimming())) && this.m_108733_() && flag4 && !this.m_6117_() && !this.m_21023_(MobEffects.f_19610_) && this.f_108619_.f_91066_.f_92091_.m_90857_()) {
         this.m_6858_(true);
      }

      if (this.m_20142_()) {
         boolean flag7 = !this.f_108618_.m_108577_() || !this.m_255269_();
         boolean flag8 = flag7 || this.f_19862_ && !this.f_185931_ || this.m_20069_() && !this.m_5842_() || (this.isInFluidType((fluidType, height) -> this.canSwimInFluidType(fluidType)) && !this.canStartSwimming());
         if (this.m_6069_()) {
            if (!this.m_20096_() && !this.f_108618_.f_108573_ && flag7 || !(this.m_20069_() || this.isInFluidType((fluidType, height) -> this.canSwimInFluidType(fluidType)))) {
               this.m_6858_(false);
            }
         } else if (flag8) {
            this.m_6858_(false);
         }
      }

      boolean flag9 = false;
      if (this.m_150110_().f_35936_) {
         if (this.f_108619_.f_91072_.m_105293_()) {
            if (!this.m_150110_().f_35935_) {
               this.m_150110_().f_35935_ = true;
               flag9 = true;
               this.m_6885_();
            }
         } else if (!flag && this.f_108618_.f_108572_ && !flag3) {
            if (this.f_36098_ == 0) {
               this.f_36098_ = 7;
            } else if (!this.m_6069_()) {
               this.m_150110_().f_35935_ = !this.m_150110_().f_35935_;
               flag9 = true;
               this.m_6885_();
               this.f_36098_ = 0;
            }
         }
      }

      if (this.f_108618_.f_108572_ && !flag9 && !flag && !this.m_150110_().f_35935_ && !this.m_20159_() && !this.m_6147_()) {
         ItemStack itemstack = this.m_6844_(EquipmentSlot.CHEST);
         if (itemstack.canElytraFly(this) && this.m_36319_()) {
            this.f_108617_.m_104955_(new ServerboundPlayerCommandPacket(this, ServerboundPlayerCommandPacket.Action.START_FALL_FLYING));
         }
      }

      this.f_108614_ = this.m_21255_();
      net.minecraftforge.fluids.FluidType fluidType = this.getMaxHeightFluidType();
      if ((this.m_20069_() || (!fluidType.isAir() && this.canSwimInFluidType(fluidType))) && this.f_108618_.f_108573_ && this.m_6129_()) {
         this.sinkInFluid(this.m_20069_() ? net.minecraftforge.common.ForgeMod.WATER_TYPE.get() : fluidType);
      }

      if (this.m_204029_(FluidTags.f_13131_)) {
         int i = this.m_5833_() ? 10 : 1;
         this.f_108615_ = Mth.m_14045_(this.f_108615_ + i, 0, 600);
      } else if (this.f_108615_ > 0) {
         this.m_204029_(FluidTags.f_13131_);
         this.f_108615_ = Mth.m_14045_(this.f_108615_ - 10, 0, 600);
      }

      if (this.m_150110_().f_35935_ && this.m_108636_()) {
         int j = 0;
         if (this.f_108618_.f_108573_) {
            --j;
         }

         if (this.f_108618_.f_108572_) {
            ++j;
         }

         if (j != 0) {
            this.m_20256_(this.m_20184_().m_82520_(0.0D, (double)((float)j * this.m_150110_().m_35942_() * 3.0F), 0.0D));
         }
      }

      PlayerRideableJumping playerrideablejumping = this.m_245714_();
      if (playerrideablejumping != null && playerrideablejumping.m_245614_() == 0) {
         if (this.f_108607_ < 0) {
            ++this.f_108607_;
            if (this.f_108607_ == 0) {
               this.f_108608_ = 0.0F;
            }
         }

         if (flag && !this.f_108618_.f_108572_) {
            this.f_108607_ = -10;
            playerrideablejumping.m_7888_(Mth.m_14143_(this.m_108634_() * 100.0F));
            this.m_108765_();
         } else if (!flag && this.f_108618_.f_108572_) {
            this.f_108607_ = 0;
            this.f_108608_ = 0.0F;
         } else if (flag) {
            ++this.f_108607_;
            if (this.f_108607_ < 10) {
               this.f_108608_ = (float)this.f_108607_ * 0.1F;
            } else {
               this.f_108608_ = 0.8F + 2.0F / (float)(this.f_108607_ - 9) * 0.1F;
            }
         }
      } else {
         this.f_108608_ = 0.0F;
      }

      super.m_8107_();
      if (this.m_20096_() && this.m_150110_().f_35935_ && !this.f_108619_.f_91072_.m_105293_()) {
         this.m_150110_().f_35935_ = false;
         this.m_6885_();
      }

   }

   protected void m_6153_() {
      ++this.f_20919_;
      if (this.f_20919_ == 20) {
         this.m_142687_(Entity.RemovalReason.KILLED);
      }

   }

   private void m_108641_() {
      this.f_108590_ = this.f_108589_;
      float f = 0.0F;
      if (this.f_19817_) {
         if (this.f_108619_.f_91080_ != null && !this.f_108619_.f_91080_.m_7043_() && !(this.f_108619_.f_91080_ instanceof DeathScreen)) {
            if (this.f_108619_.f_91080_ instanceof AbstractContainerScreen) {
               this.m_6915_();
            }

            this.f_108619_.m_91152_((Screen)null);
         }

         if (this.f_108589_ == 0.0F) {
            this.f_108619_.m_91106_().m_120367_(SimpleSoundInstance.m_119766_(SoundEvents.f_12288_, this.f_19796_.m_188501_() * 0.4F + 0.8F, 0.25F));
         }

         f = 0.0125F;
         this.f_19817_ = false;
      } else if (this.m_21023_(MobEffects.f_19604_) && !this.m_21124_(MobEffects.f_19604_).m_267633_(60)) {
         f = 0.006666667F;
      } else if (this.f_108589_ > 0.0F) {
         f = -0.05F;
      }

      this.f_108589_ = Mth.m_14036_(this.f_108589_ + f, 0.0F, 1.0F);
      this.m_8021_();
   }

   public void m_6083_() {
      super.m_6083_();
      if (this.m_36342_() && this.m_20159_()) this.f_108618_.f_108573_ = false;
      this.f_108611_ = false;
      Entity entity = this.m_275832_();
      if (entity instanceof Boat boat) {
         boat.m_38342_(this.f_108618_.f_108570_, this.f_108618_.f_108571_, this.f_108618_.f_108568_, this.f_108618_.f_108569_);
         this.f_108611_ |= this.f_108618_.f_108570_ || this.f_108618_.f_108571_ || this.f_108618_.f_108568_ || this.f_108618_.f_108569_;
      }

   }

   public boolean m_108637_() {
      return this.f_108611_;
   }

   @Nullable
   public MobEffectInstance m_6234_(@Nullable MobEffect p_108720_) {
      if (p_108720_ == MobEffects.f_19604_) {
         this.f_108590_ = 0.0F;
         this.f_108589_ = 0.0F;
      }

      return super.m_6234_(p_108720_);
   }

   public void m_6478_(MoverType p_108670_, Vec3 p_108671_) {
      double d0 = this.m_20185_();
      double d1 = this.m_20189_();
      super.m_6478_(p_108670_, p_108671_);
      this.m_108743_((float)(this.m_20185_() - d0), (float)(this.m_20189_() - d1));
   }

   public boolean m_108638_() {
      return this.f_108612_;
   }

   protected void m_108743_(float p_108744_, float p_108745_) {
      if (this.m_108731_()) {
         Vec3 vec3 = this.m_20182_();
         Vec3 vec31 = vec3.m_82520_((double)p_108744_, 0.0D, (double)p_108745_);
         Vec3 vec32 = new Vec3((double)p_108744_, 0.0D, (double)p_108745_);
         float f = this.m_6113_();
         float f1 = (float)vec32.m_82556_();
         if (f1 <= 0.001F) {
            Vec2 vec2 = this.f_108618_.m_108575_();
            float f2 = f * vec2.f_82470_;
            float f3 = f * vec2.f_82471_;
            float f4 = Mth.m_14031_(this.m_146908_() * ((float)Math.PI / 180F));
            float f5 = Mth.m_14089_(this.m_146908_() * ((float)Math.PI / 180F));
            vec32 = new Vec3((double)(f2 * f5 - f3 * f4), vec32.f_82480_, (double)(f3 * f5 + f2 * f4));
            f1 = (float)vec32.m_82556_();
            if (f1 <= 0.001F) {
               return;
            }
         }

         float f12 = Mth.m_264536_(f1);
         Vec3 vec312 = vec32.m_82490_((double)f12);
         Vec3 vec313 = this.m_20156_();
         float f13 = (float)(vec313.f_82479_ * vec312.f_82479_ + vec313.f_82481_ * vec312.f_82481_);
         if (!(f13 < -0.15F)) {
            CollisionContext collisioncontext = CollisionContext.m_82750_(this);
            BlockPos blockpos = BlockPos.m_274561_(this.m_20185_(), this.m_20191_().f_82292_, this.m_20189_());
            BlockState blockstate = this.m_9236_().m_8055_(blockpos);
            if (blockstate.m_60742_(this.m_9236_(), blockpos, collisioncontext).m_83281_()) {
               blockpos = blockpos.m_7494_();
               BlockState blockstate1 = this.m_9236_().m_8055_(blockpos);
               if (blockstate1.m_60742_(this.m_9236_(), blockpos, collisioncontext).m_83281_()) {
                  float f6 = 7.0F;
                  float f7 = 1.2F;
                  if (this.m_21023_(MobEffects.f_19603_)) {
                     f7 += (float)(this.m_21124_(MobEffects.f_19603_).m_19564_() + 1) * 0.75F;
                  }

                  float f8 = Math.max(f * 7.0F, 1.0F / f12);
                  Vec3 vec34 = vec31.m_82549_(vec312.m_82490_((double)f8));
                  float f9 = this.m_20205_();
                  float f10 = this.m_20206_();
                  AABB aabb = (new AABB(vec3, vec34.m_82520_(0.0D, (double)f10, 0.0D))).m_82377_((double)f9, 0.0D, (double)f9);
                  Vec3 $$23 = vec3.m_82520_(0.0D, (double)0.51F, 0.0D);
                  vec34 = vec34.m_82520_(0.0D, (double)0.51F, 0.0D);
                  Vec3 vec35 = vec312.m_82537_(new Vec3(0.0D, 1.0D, 0.0D));
                  Vec3 vec36 = vec35.m_82490_((double)(f9 * 0.5F));
                  Vec3 vec37 = $$23.m_82546_(vec36);
                  Vec3 vec38 = vec34.m_82546_(vec36);
                  Vec3 vec39 = $$23.m_82549_(vec36);
                  Vec3 vec310 = vec34.m_82549_(vec36);
                  Iterable<VoxelShape> iterable = this.m_9236_().m_186431_(this, aabb);
                  Iterator<AABB> iterator = StreamSupport.stream(iterable.spliterator(), false).flatMap((p_234124_) -> {
                     return p_234124_.m_83299_().stream();
                  }).iterator();
                  float f11 = Float.MIN_VALUE;

                  while(iterator.hasNext()) {
                     AABB aabb1 = iterator.next();
                     if (aabb1.m_82335_(vec37, vec38) || aabb1.m_82335_(vec39, vec310)) {
                        f11 = (float)aabb1.f_82292_;
                        Vec3 vec311 = aabb1.m_82399_();
                        BlockPos blockpos1 = BlockPos.m_274446_(vec311);

                        for(int i = 1; (float)i < f7; ++i) {
                           BlockPos blockpos2 = blockpos1.m_6630_(i);
                           BlockState blockstate2 = this.m_9236_().m_8055_(blockpos2);
                           VoxelShape voxelshape;
                           if (!(voxelshape = blockstate2.m_60742_(this.m_9236_(), blockpos2, collisioncontext)).m_83281_()) {
                              f11 = (float)voxelshape.m_83297_(Direction.Axis.Y) + (float)blockpos2.m_123342_();
                              if ((double)f11 - this.m_20186_() > (double)f7) {
                                 return;
                              }
                           }

                           if (i > 1) {
                              blockpos = blockpos.m_7494_();
                              BlockState blockstate3 = this.m_9236_().m_8055_(blockpos);
                              if (!blockstate3.m_60742_(this.m_9236_(), blockpos, collisioncontext).m_83281_()) {
                                 return;
                              }
                           }
                        }
                        break;
                     }
                  }

                  if (f11 != Float.MIN_VALUE) {
                     float f14 = (float)((double)f11 - this.m_20186_());
                     if (!(f14 <= 0.5F) && !(f14 > f7)) {
                        this.f_108613_ = 1;
                     }
                  }
               }
            }
         }
      }
   }

   protected boolean m_196406_(Vec3 p_197411_) {
      float f = this.m_146908_() * ((float)Math.PI / 180F);
      double d0 = (double)Mth.m_14031_(f);
      double d1 = (double)Mth.m_14089_(f);
      double d2 = (double)this.f_20900_ * d1 - (double)this.f_20902_ * d0;
      double d3 = (double)this.f_20902_ * d1 + (double)this.f_20900_ * d0;
      double d4 = Mth.m_144952_(d2) + Mth.m_144952_(d3);
      double d5 = Mth.m_144952_(p_197411_.f_82479_) + Mth.m_144952_(p_197411_.f_82481_);
      if (!(d4 < (double)1.0E-5F) && !(d5 < (double)1.0E-5F)) {
         double d6 = d2 * p_197411_.f_82479_ + d3 * p_197411_.f_82481_;
         double d7 = Math.acos(d6 / Math.sqrt(d4 * d5));
         return d7 < (double)0.13962634F;
      } else {
         return false;
      }
   }

   private boolean m_108731_() {
      return this.m_108638_() && this.f_108613_ <= 0 && this.m_20096_() && !this.m_36343_() && !this.m_20159_() && this.m_108732_() && (double)this.m_20098_() >= 1.0D;
   }

   private boolean m_108732_() {
      Vec2 vec2 = this.f_108618_.m_108575_();
      return vec2.f_82470_ != 0.0F || vec2.f_82471_ != 0.0F;
   }

   private boolean m_264082_() {
      return !this.m_20142_() && this.m_108733_() && this.m_255269_() && !this.m_6117_() && !this.m_21023_(MobEffects.f_19610_) && (!this.m_20159_() || this.m_264231_(this.m_20202_())) && !this.m_21255_();
   }

   private boolean m_264231_(Entity p_265184_) {
      return p_265184_.m_264410_() && p_265184_.m_6109_();
   }

   private boolean m_108733_() {
      double d0 = 0.8D;
      return this.m_5842_() ? this.f_108618_.m_108577_() : (double)this.f_108618_.f_108567_ >= 0.8D;
   }

   private boolean m_255269_() {
      return this.m_20159_() || (float)this.m_36324_().m_38702_() > 6.0F || this.m_150110_().f_35936_;
   }

   public float m_108639_() {
      if (!this.m_204029_(FluidTags.f_13131_)) {
         return 0.0F;
      } else {
         float f = 600.0F;
         float f1 = 100.0F;
         if ((float)this.f_108615_ >= 600.0F) {
            return 1.0F;
         } else {
            float f2 = Mth.m_14036_((float)this.f_108615_ / 100.0F, 0.0F, 1.0F);
            float f3 = (float)this.f_108615_ < 100.0F ? 0.0F : Mth.m_14036_(((float)this.f_108615_ - 100.0F) / 500.0F, 0.0F, 1.0F);
            return f2 * 0.6F + f3 * 0.39999998F;
         }
      }
   }

   public void m_287171_(GameType p_287675_) {
      if (p_287675_ == GameType.SPECTATOR) {
         this.m_20256_(this.m_20184_().m_193103_(Direction.Axis.Y, 0.0D));
      }

   }

   public boolean m_5842_() {
      return this.f_36076_;
   }

   protected boolean m_7602_() {
      boolean flag = this.f_36076_;
      boolean flag1 = super.m_7602_();
      if (this.m_5833_()) {
         return this.f_36076_;
      } else {
         if (!flag && flag1) {
            this.m_9236_().m_7785_(this.m_20185_(), this.m_20186_(), this.m_20189_(), SoundEvents.f_12537_, SoundSource.AMBIENT, 1.0F, 1.0F, false);
            this.f_108619_.m_91106_().m_120367_(new UnderwaterAmbientSoundInstances.UnderwaterAmbientSoundInstance(this));
         }

         if (flag && !flag1) {
            this.m_9236_().m_7785_(this.m_20185_(), this.m_20186_(), this.m_20189_(), SoundEvents.f_12590_, SoundSource.AMBIENT, 1.0F, 1.0F, false);
         }

         return this.f_36076_;
      }
   }

   public Vec3 m_7398_(float p_108758_) {
      if (this.f_108619_.f_91066_.m_92176_().m_90612_()) {
         float f = Mth.m_14179_(p_108758_ * 0.5F, this.m_146908_(), this.f_19859_) * ((float)Math.PI / 180F);
         float f1 = Mth.m_14179_(p_108758_ * 0.5F, this.m_146909_(), this.f_19860_) * ((float)Math.PI / 180F);
         double d0 = this.m_5737_() == HumanoidArm.RIGHT ? -1.0D : 1.0D;
         Vec3 vec3 = new Vec3(0.39D * d0, -0.6D, 0.3D);
         return vec3.m_82496_(-f1).m_82524_(-f).m_82549_(this.m_20299_(p_108758_));
      } else {
         return super.m_7398_(p_108758_);
      }
   }

   public void updateSyncFields(LocalPlayer old) {
      this.f_108595_ = old.f_108595_;
      this.f_108596_ = old.f_108596_;
      this.f_108597_ = old.f_108597_;
      this.f_108598_ = old.f_108598_;
      this.f_108599_ = old.f_108599_;
      this.f_108600_ = old.f_108600_;
      this.f_108602_ = old.f_108602_;
      this.f_108603_ = old.f_108603_;
      this.f_108604_ = old.f_108604_;
   }

   public void m_141945_(ItemStack p_172532_, ItemStack p_172533_, ClickAction p_172534_) {
      this.f_108619_.m_91301_().m_175024_(p_172532_, p_172533_, p_172534_);
   }

   public float m_213816_() {
      return this.m_146908_();
   }
}
