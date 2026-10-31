package net.minecraft.server.network;

import com.google.common.collect.Lists;
import com.google.common.primitives.Floats;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.ParseResults;
import com.mojang.brigadier.StringReader;
import com.mojang.logging.LogUtils;
import it.unimi.dsi.fastutil.ints.Int2ObjectMap;
import it.unimi.dsi.fastutil.ints.Int2ObjectMaps;
import it.unimi.dsi.fastutil.objects.Object2ObjectOpenHashMap;
import java.net.SocketAddress;
import java.time.Duration;
import java.time.Instant;
import java.util.Collections;
import java.util.EnumSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.CancellationException;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.BiFunction;
import java.util.function.Consumer;
import java.util.function.UnaryOperator;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.CrashReport;
import net.minecraft.CrashReportCategory;
import net.minecraft.ReportedException;
import net.minecraft.SharedConstants;
import net.minecraft.Util;
import net.minecraft.advancements.Advancement;
import net.minecraft.advancements.CriteriaTriggers;
import net.minecraft.commands.CommandSigningContext;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.StringTag;
import net.minecraft.network.Connection;
import net.minecraft.network.PacketSendListener;
import net.minecraft.network.TickablePacketListener;
import net.minecraft.network.chat.ChatType;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.LastSeenMessages;
import net.minecraft.network.chat.LastSeenMessagesValidator;
import net.minecraft.network.chat.MessageSignature;
import net.minecraft.network.chat.MessageSignatureCache;
import net.minecraft.network.chat.PlayerChatMessage;
import net.minecraft.network.chat.RemoteChatSession;
import net.minecraft.network.chat.SignableCommand;
import net.minecraft.network.chat.SignedMessageBody;
import net.minecraft.network.chat.SignedMessageChain;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.PacketUtils;
import net.minecraft.network.protocol.game.ClientboundBlockChangedAckPacket;
import net.minecraft.network.protocol.game.ClientboundBlockUpdatePacket;
import net.minecraft.network.protocol.game.ClientboundCommandSuggestionsPacket;
import net.minecraft.network.protocol.game.ClientboundContainerSetSlotPacket;
import net.minecraft.network.protocol.game.ClientboundDisconnectPacket;
import net.minecraft.network.protocol.game.ClientboundDisguisedChatPacket;
import net.minecraft.network.protocol.game.ClientboundKeepAlivePacket;
import net.minecraft.network.protocol.game.ClientboundMoveVehiclePacket;
import net.minecraft.network.protocol.game.ClientboundPlayerChatPacket;
import net.minecraft.network.protocol.game.ClientboundPlayerInfoUpdatePacket;
import net.minecraft.network.protocol.game.ClientboundPlayerPositionPacket;
import net.minecraft.network.protocol.game.ClientboundSetCarriedItemPacket;
import net.minecraft.network.protocol.game.ClientboundSystemChatPacket;
import net.minecraft.network.protocol.game.ClientboundTagQueryPacket;
import net.minecraft.network.protocol.game.ServerGamePacketListener;
import net.minecraft.network.protocol.game.ServerboundAcceptTeleportationPacket;
import net.minecraft.network.protocol.game.ServerboundBlockEntityTagQuery;
import net.minecraft.network.protocol.game.ServerboundChangeDifficultyPacket;
import net.minecraft.network.protocol.game.ServerboundChatAckPacket;
import net.minecraft.network.protocol.game.ServerboundChatCommandPacket;
import net.minecraft.network.protocol.game.ServerboundChatPacket;
import net.minecraft.network.protocol.game.ServerboundChatSessionUpdatePacket;
import net.minecraft.network.protocol.game.ServerboundClientCommandPacket;
import net.minecraft.network.protocol.game.ServerboundClientInformationPacket;
import net.minecraft.network.protocol.game.ServerboundCommandSuggestionPacket;
import net.minecraft.network.protocol.game.ServerboundContainerButtonClickPacket;
import net.minecraft.network.protocol.game.ServerboundContainerClickPacket;
import net.minecraft.network.protocol.game.ServerboundContainerClosePacket;
import net.minecraft.network.protocol.game.ServerboundCustomPayloadPacket;
import net.minecraft.network.protocol.game.ServerboundEditBookPacket;
import net.minecraft.network.protocol.game.ServerboundEntityTagQuery;
import net.minecraft.network.protocol.game.ServerboundInteractPacket;
import net.minecraft.network.protocol.game.ServerboundJigsawGeneratePacket;
import net.minecraft.network.protocol.game.ServerboundKeepAlivePacket;
import net.minecraft.network.protocol.game.ServerboundLockDifficultyPacket;
import net.minecraft.network.protocol.game.ServerboundMovePlayerPacket;
import net.minecraft.network.protocol.game.ServerboundMoveVehiclePacket;
import net.minecraft.network.protocol.game.ServerboundPaddleBoatPacket;
import net.minecraft.network.protocol.game.ServerboundPickItemPacket;
import net.minecraft.network.protocol.game.ServerboundPlaceRecipePacket;
import net.minecraft.network.protocol.game.ServerboundPlayerAbilitiesPacket;
import net.minecraft.network.protocol.game.ServerboundPlayerActionPacket;
import net.minecraft.network.protocol.game.ServerboundPlayerCommandPacket;
import net.minecraft.network.protocol.game.ServerboundPlayerInputPacket;
import net.minecraft.network.protocol.game.ServerboundPongPacket;
import net.minecraft.network.protocol.game.ServerboundRecipeBookChangeSettingsPacket;
import net.minecraft.network.protocol.game.ServerboundRecipeBookSeenRecipePacket;
import net.minecraft.network.protocol.game.ServerboundRenameItemPacket;
import net.minecraft.network.protocol.game.ServerboundResourcePackPacket;
import net.minecraft.network.protocol.game.ServerboundSeenAdvancementsPacket;
import net.minecraft.network.protocol.game.ServerboundSelectTradePacket;
import net.minecraft.network.protocol.game.ServerboundSetBeaconPacket;
import net.minecraft.network.protocol.game.ServerboundSetCarriedItemPacket;
import net.minecraft.network.protocol.game.ServerboundSetCommandBlockPacket;
import net.minecraft.network.protocol.game.ServerboundSetCommandMinecartPacket;
import net.minecraft.network.protocol.game.ServerboundSetCreativeModeSlotPacket;
import net.minecraft.network.protocol.game.ServerboundSetJigsawBlockPacket;
import net.minecraft.network.protocol.game.ServerboundSetStructureBlockPacket;
import net.minecraft.network.protocol.game.ServerboundSignUpdatePacket;
import net.minecraft.network.protocol.game.ServerboundSwingPacket;
import net.minecraft.network.protocol.game.ServerboundTeleportToEntityPacket;
import net.minecraft.network.protocol.game.ServerboundUseItemOnPacket;
import net.minecraft.network.protocol.game.ServerboundUseItemPacket;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.FutureChain;
import net.minecraft.util.Mth;
import net.minecraft.util.SignatureValidator;
import net.minecraft.util.StringUtil;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.ExperienceOrb;
import net.minecraft.world.entity.HasCustomInventoryScreen;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.PlayerRideableJumping;
import net.minecraft.world.entity.RelativeMovement;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.ChatVisiblity;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.player.ProfilePublicKey;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.vehicle.Boat;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.AnvilMenu;
import net.minecraft.world.inventory.BeaconMenu;
import net.minecraft.world.inventory.MerchantMenu;
import net.minecraft.world.inventory.RecipeBookMenu;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.BucketItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.BaseCommandBlock;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.CommandBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.CommandBlockEntity;
import net.minecraft.world.level.block.entity.JigsawBlockEntity;
import net.minecraft.world.level.block.entity.SignBlockEntity;
import net.minecraft.world.level.block.entity.StructureBlockEntity;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.BooleanOp;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.slf4j.Logger;

public class ServerGamePacketListenerImpl implements ServerPlayerConnection, TickablePacketListener, ServerGamePacketListener {
   static final Logger f_9744_ = LogUtils.getLogger();
   private static final int f_143608_ = 15000;
   /**
    * Forge: Deprecated in favor of range/reach attributes.
    * @see net.minecraftforge.common.ForgeMod#BLOCK_REACH
    * @see net.minecraftforge.common.ForgeMod#ENTITY_REACH
    */
   @Deprecated
   public static final double f_215198_ = Mth.m_144952_(6.0D);
   private static final int f_215199_ = -1;
   private static final int f_244471_ = 4096;
   private static final Component f_244304_ = Component.m_237115_("multiplayer.disconnect.chat_validation_failed");
   public final Connection f_9742_;
   private final MinecraftServer f_9745_;
   public ServerPlayer f_9743_;
   private int f_9746_;
   private int f_215200_ = -1;
   private long f_9747_;
   private boolean f_9748_;
   private long f_9749_;
   private int f_9750_;
   private int f_9751_;
   private double f_9753_;
   private double f_9754_;
   private double f_9755_;
   private double f_9756_;
   private double f_9757_;
   private double f_9758_;
   @Nullable
   private Entity f_9759_;
   private double f_9760_;
   private double f_9761_;
   private double f_9762_;
   private double f_9763_;
   private double f_9764_;
   private double f_9765_;
   @Nullable
   private Vec3 f_9766_;
   private int f_9767_;
   private int f_9735_;
   private boolean f_9736_;
   private int f_9737_;
   private boolean f_9738_;
   private int f_9739_;
   private int f_9740_;
   private int f_9741_;
   private final AtomicReference<Instant> f_215197_ = new AtomicReference<>(Instant.EPOCH);
   @Nullable
   private RemoteChatSession f_252494_;
   private SignedMessageChain.Decoder f_240889_;
   private final LastSeenMessagesValidator f_244262_ = new LastSeenMessagesValidator(20);
   private final MessageSignatureCache f_243718_ = MessageSignatureCache.m_246587_();
   private final FutureChain f_241681_;

   public ServerGamePacketListenerImpl(MinecraftServer p_9770_, Connection p_9771_, ServerPlayer p_9772_) {
      this.f_9745_ = p_9770_;
      this.f_9742_ = p_9771_;
      p_9771_.m_129505_(this);
      this.f_9743_ = p_9772_;
      p_9772_.f_8906_ = this;
      this.f_9747_ = Util.m_137550_();
      p_9772_.m_8967_().m_7674_();
      this.f_240889_ = p_9770_.m_214005_() ? SignedMessageChain.Decoder.f_252472_ : SignedMessageChain.Decoder.m_246683_(p_9772_.m_20148_());
      this.f_241681_ = new FutureChain(p_9770_);
   }

   public void m_9933_() {
      if (this.f_215200_ > -1) {
         this.m_9829_(new ClientboundBlockChangedAckPacket(this.f_215200_));
         this.f_215200_ = -1;
      }

      this.m_9953_();
      this.f_9743_.f_19854_ = this.f_9743_.m_20185_();
      this.f_9743_.f_19855_ = this.f_9743_.m_20186_();
      this.f_9743_.f_19856_ = this.f_9743_.m_20189_();
      this.f_9743_.m_9240_();
      this.f_9743_.m_19890_(this.f_9753_, this.f_9754_, this.f_9755_, this.f_9743_.m_146908_(), this.f_9743_.m_146909_());
      ++this.f_9746_;
      this.f_9741_ = this.f_9740_;
      if (this.f_9736_ && !this.f_9743_.m_5803_() && !this.f_9743_.m_20159_() && !this.f_9743_.m_21224_()) {
         if (++this.f_9737_ > 80) {
            f_9744_.warn("{} was kicked for floating too long!", (Object)this.f_9743_.m_7755_().getString());
            this.m_9942_(Component.m_237115_("multiplayer.disconnect.flying"));
            return;
         }
      } else {
         this.f_9736_ = false;
         this.f_9737_ = 0;
      }

      this.f_9759_ = this.f_9743_.m_20201_();
      if (this.f_9759_ != this.f_9743_ && this.f_9759_.m_6688_() == this.f_9743_) {
         this.f_9760_ = this.f_9759_.m_20185_();
         this.f_9761_ = this.f_9759_.m_20186_();
         this.f_9762_ = this.f_9759_.m_20189_();
         this.f_9763_ = this.f_9759_.m_20185_();
         this.f_9764_ = this.f_9759_.m_20186_();
         this.f_9765_ = this.f_9759_.m_20189_();
         if (this.f_9738_ && this.f_9743_.m_20201_().m_6688_() == this.f_9743_) {
            if (++this.f_9739_ > 80) {
               f_9744_.warn("{} was kicked for floating a vehicle too long!", (Object)this.f_9743_.m_7755_().getString());
               this.m_9942_(Component.m_237115_("multiplayer.disconnect.flying"));
               return;
            }
         } else {
            this.f_9738_ = false;
            this.f_9739_ = 0;
         }
      } else {
         this.f_9759_ = null;
         this.f_9738_ = false;
         this.f_9739_ = 0;
      }

      this.f_9745_.m_129905_().m_6180_("keepAlive");
      long i = Util.m_137550_();
      if (i - this.f_9747_ >= 15000L) {
         if (this.f_9748_) {
            this.m_9942_(Component.m_237115_("disconnect.timeout"));
         } else {
            this.f_9748_ = true;
            this.f_9747_ = i;
            this.f_9749_ = i;
            this.m_9829_(new ClientboundKeepAlivePacket(this.f_9749_));
         }
      }

      this.f_9745_.m_129905_().m_7238_();
      if (this.f_9750_ > 0) {
         --this.f_9750_;
      }

      if (this.f_9751_ > 0) {
         --this.f_9751_;
      }

      if (this.f_9743_.m_8956_() > 0L && this.f_9745_.m_129924_() > 0 && Util.m_137550_() - this.f_9743_.m_8956_() > (long)this.f_9745_.m_129924_() * 1000L * 60L) {
         this.m_9942_(Component.m_237115_("multiplayer.disconnect.idling"));
      }

   }

   public void m_9953_() {
      this.f_9753_ = this.f_9743_.m_20185_();
      this.f_9754_ = this.f_9743_.m_20186_();
      this.f_9755_ = this.f_9743_.m_20189_();
      this.f_9756_ = this.f_9743_.m_20185_();
      this.f_9757_ = this.f_9743_.m_20186_();
      this.f_9758_ = this.f_9743_.m_20189_();
   }

   public boolean m_6198_() {
      return this.f_9742_.m_129536_();
   }

   private boolean m_9956_() {
      return this.f_9745_.m_7779_(this.f_9743_.m_36316_());
   }

   public void m_9942_(Component p_9943_) {
      this.f_9742_.m_243124_(new ClientboundDisconnectPacket(p_9943_), PacketSendListener.m_243092_(() -> {
         this.f_9742_.m_129507_(p_9943_);
      }));
      this.f_9742_.m_129540_();
      this.f_9745_.m_18709_(this.f_9742_::m_129541_);
   }

   private <T, R> CompletableFuture<R> m_243080_(T p_243240_, BiFunction<TextFilter, T, CompletableFuture<R>> p_243271_) {
      return p_243271_.apply(this.f_9743_.m_8967_(), p_243240_).thenApply((p_264862_) -> {
         if (!this.m_6198_()) {
            f_9744_.debug("Ignoring packet due to disconnection");
            throw new CancellationException("disconnected");
         } else {
            return p_264862_;
         }
      });
   }

   private CompletableFuture<FilteredText> m_243132_(String p_243213_) {
      return this.m_243080_(p_243213_, TextFilter::m_6770_);
   }

   private CompletableFuture<List<FilteredText>> m_243065_(List<String> p_243258_) {
      return this.m_243080_(p_243258_, TextFilter::m_5925_);
   }

   public void m_5918_(ServerboundPlayerInputPacket p_9893_) {
      PacketUtils.m_131359_(p_9893_, this, this.f_9743_.m_284548_());
      this.f_9743_.m_8980_(p_9893_.m_134355_(), p_9893_.m_134358_(), p_9893_.m_134359_(), p_9893_.m_134360_());
   }

   private static boolean m_143663_(double p_143664_, double p_143665_, double p_143666_, float p_143667_, float p_143668_) {
      return Double.isNaN(p_143664_) || Double.isNaN(p_143665_) || Double.isNaN(p_143666_) || !Floats.isFinite(p_143668_) || !Floats.isFinite(p_143667_);
   }

   private static double m_143609_(double p_143610_) {
      return Mth.m_14008_(p_143610_, -3.0E7D, 3.0E7D);
   }

   private static double m_143653_(double p_143654_) {
      return Mth.m_14008_(p_143654_, -2.0E7D, 2.0E7D);
   }

   public void m_5659_(ServerboundMoveVehiclePacket p_9876_) {
      PacketUtils.m_131359_(p_9876_, this, this.f_9743_.m_284548_());
      if (m_143663_(p_9876_.m_134199_(), p_9876_.m_134202_(), p_9876_.m_134203_(), p_9876_.m_134204_(), p_9876_.m_134205_())) {
         this.m_9942_(Component.m_237115_("multiplayer.disconnect.invalid_vehicle_movement"));
      } else {
         Entity entity = this.f_9743_.m_20201_();
         if (entity != this.f_9743_ && entity.m_6688_() == this.f_9743_ && entity == this.f_9759_) {
            ServerLevel serverlevel = this.f_9743_.m_284548_();
            double d0 = entity.m_20185_();
            double d1 = entity.m_20186_();
            double d2 = entity.m_20189_();
            double d3 = m_143609_(p_9876_.m_134199_());
            double d4 = m_143653_(p_9876_.m_134202_());
            double d5 = m_143609_(p_9876_.m_134203_());
            float f = Mth.m_14177_(p_9876_.m_134204_());
            float f1 = Mth.m_14177_(p_9876_.m_134205_());
            double d6 = d3 - this.f_9760_;
            double d7 = d4 - this.f_9761_;
            double d8 = d5 - this.f_9762_;
            double d9 = entity.m_20184_().m_82556_();
            double d10 = d6 * d6 + d7 * d7 + d8 * d8;
            if (d10 - d9 > 100.0D && !this.m_9956_()) {
               f_9744_.warn("{} (vehicle of {}) moved too quickly! {},{},{}", entity.m_7755_().getString(), this.f_9743_.m_7755_().getString(), d6, d7, d8);
               this.f_9742_.m_129512_(new ClientboundMoveVehiclePacket(entity));
               return;
            }

            boolean flag = serverlevel.m_45756_(entity, entity.m_20191_().m_82406_(0.0625D));
            d6 = d3 - this.f_9763_;
            d7 = d4 - this.f_9764_ - 1.0E-6D;
            d8 = d5 - this.f_9765_;
            boolean flag1 = entity.f_201939_;
            if (entity instanceof LivingEntity) {
               LivingEntity livingentity = (LivingEntity)entity;
               if (livingentity.m_6147_()) {
                  livingentity.m_183634_();
               }
            }

            entity.m_6478_(MoverType.PLAYER, new Vec3(d6, d7, d8));
            d6 = d3 - entity.m_20185_();
            d7 = d4 - entity.m_20186_();
            if (d7 > -0.5D || d7 < 0.5D) {
               d7 = 0.0D;
            }

            d8 = d5 - entity.m_20189_();
            d10 = d6 * d6 + d7 * d7 + d8 * d8;
            boolean flag2 = false;
            if (d10 > 0.0625D) {
               flag2 = true;
               f_9744_.warn("{} (vehicle of {}) moved wrongly! {}", entity.m_7755_().getString(), this.f_9743_.m_7755_().getString(), Math.sqrt(d10));
            }

            entity.m_19890_(d3, d4, d5, f, f1);
            boolean flag3 = serverlevel.m_45756_(entity, entity.m_20191_().m_82406_(0.0625D));
            if (flag && (flag2 || !flag3)) {
               entity.m_19890_(d0, d1, d2, f, f1);
               this.f_9742_.m_129512_(new ClientboundMoveVehiclePacket(entity));
               return;
            }

            this.f_9743_.m_284548_().m_7726_().m_8385_(this.f_9743_);
            this.f_9743_.m_36378_(this.f_9743_.m_20185_() - d0, this.f_9743_.m_20186_() - d1, this.f_9743_.m_20189_() - d2);
            this.f_9738_ = d7 >= -0.03125D && !flag1 && !this.f_9745_.m_129915_() && !entity.m_20068_() && this.m_9793_(entity);
            this.f_9763_ = entity.m_20185_();
            this.f_9764_ = entity.m_20186_();
            this.f_9765_ = entity.m_20189_();
         }

      }
   }

   private boolean m_9793_(Entity p_9794_) {
      return p_9794_.m_9236_().m_45556_(p_9794_.m_20191_().m_82400_(0.0625D).m_82363_(0.0D, -0.55D, 0.0D)).allMatch(BlockBehaviour.BlockStateBase::m_60795_);
   }

   public void m_7376_(ServerboundAcceptTeleportationPacket p_9835_) {
      PacketUtils.m_131359_(p_9835_, this, this.f_9743_.m_284548_());
      if (p_9835_.m_133795_() == this.f_9767_) {
         if (this.f_9766_ == null) {
            this.m_9942_(Component.m_237115_("multiplayer.disconnect.invalid_player_movement"));
            return;
         }

         this.f_9743_.m_19890_(this.f_9766_.f_82479_, this.f_9766_.f_82480_, this.f_9766_.f_82481_, this.f_9743_.m_146908_(), this.f_9743_.m_146909_());
         this.f_9756_ = this.f_9766_.f_82479_;
         this.f_9757_ = this.f_9766_.f_82480_;
         this.f_9758_ = this.f_9766_.f_82481_;
         if (this.f_9743_.m_8958_()) {
            this.f_9743_.m_8959_();
         }

         this.f_9766_ = null;
      }

   }

   public void m_7411_(ServerboundRecipeBookSeenRecipePacket p_9897_) {
      PacketUtils.m_131359_(p_9897_, this, this.f_9743_.m_284548_());
      this.f_9745_.m_129894_().m_44043_(p_9897_.m_134390_()).ifPresent(this.f_9743_.m_8952_()::m_12721_);
   }

   public void m_7982_(ServerboundRecipeBookChangeSettingsPacket p_9895_) {
      PacketUtils.m_131359_(p_9895_, this, this.f_9743_.m_284548_());
      this.f_9743_.m_8952_().m_12696_(p_9895_.m_134375_(), p_9895_.m_134378_(), p_9895_.m_134379_());
   }

   public void m_6947_(ServerboundSeenAdvancementsPacket p_9903_) {
      PacketUtils.m_131359_(p_9903_, this, this.f_9743_.m_284548_());
      if (p_9903_.m_134447_() == ServerboundSeenAdvancementsPacket.Action.OPENED_TAB) {
         ResourceLocation resourcelocation = p_9903_.m_134448_();
         Advancement advancement = this.f_9745_.m_129889_().m_136041_(resourcelocation);
         if (advancement != null) {
            this.f_9743_.m_8960_().m_135983_(advancement);
         }
      }

   }

   public void m_7741_(ServerboundCommandSuggestionPacket p_9847_) {
      PacketUtils.m_131359_(p_9847_, this, this.f_9743_.m_284548_());
      StringReader stringreader = new StringReader(p_9847_.m_133904_());
      if (stringreader.canRead() && stringreader.peek() == '/') {
         stringreader.skip();
      }

      ParseResults<CommandSourceStack> parseresults = this.f_9745_.m_129892_().m_82094_().parse(stringreader, this.f_9743_.m_20203_());
      this.f_9745_.m_129892_().m_82094_().getCompletionSuggestions(parseresults).thenAccept((p_238197_) -> {
         this.f_9742_.m_129512_(new ClientboundCommandSuggestionsPacket(p_9847_.m_133901_(), p_238197_));
      });
   }

   public void m_7192_(ServerboundSetCommandBlockPacket p_9911_) {
      PacketUtils.m_131359_(p_9911_, this, this.f_9743_.m_284548_());
      if (!this.f_9745_.m_6993_()) {
         this.f_9743_.m_213846_(Component.m_237115_("advMode.notEnabled"));
      } else if (!this.f_9743_.m_36337_()) {
         this.f_9743_.m_213846_(Component.m_237115_("advMode.notAllowed"));
      } else {
         BaseCommandBlock basecommandblock = null;
         CommandBlockEntity commandblockentity = null;
         BlockPos blockpos = p_9911_.m_134521_();
         BlockEntity blockentity = this.f_9743_.m_9236_().m_7702_(blockpos);
         if (blockentity instanceof CommandBlockEntity) {
            commandblockentity = (CommandBlockEntity)blockentity;
            basecommandblock = commandblockentity.m_59141_();
         }

         String s = p_9911_.m_134524_();
         boolean flag = p_9911_.m_134525_();
         if (basecommandblock != null) {
            CommandBlockEntity.Mode commandblockentity$mode = commandblockentity.m_59148_();
            BlockState blockstate = this.f_9743_.m_9236_().m_8055_(blockpos);
            Direction direction = blockstate.m_61143_(CommandBlock.f_51793_);
            BlockState blockstate1;
            switch (p_9911_.m_134528_()) {
               case SEQUENCE:
                  blockstate1 = Blocks.f_50448_.m_49966_();
                  break;
               case AUTO:
                  blockstate1 = Blocks.f_50447_.m_49966_();
                  break;
               case REDSTONE:
               default:
                  blockstate1 = Blocks.f_50272_.m_49966_();
            }

            BlockState blockstate2 = blockstate1.m_61124_(CommandBlock.f_51793_, direction).m_61124_(CommandBlock.f_51794_, Boolean.valueOf(p_9911_.m_134526_()));
            if (blockstate2 != blockstate) {
               this.f_9743_.m_9236_().m_7731_(blockpos, blockstate2, 2);
               blockentity.m_155250_(blockstate2);
               this.f_9743_.m_9236_().m_46745_(blockpos).m_142169_(blockentity);
            }

            basecommandblock.m_6590_(s);
            basecommandblock.m_45428_(flag);
            if (!flag) {
               basecommandblock.m_45433_((Component)null);
            }

            commandblockentity.m_59137_(p_9911_.m_134527_());
            if (commandblockentity$mode != p_9911_.m_134528_()) {
               commandblockentity.m_59144_();
            }

            basecommandblock.m_7368_();
            if (!StringUtil.m_14408_(s)) {
               this.f_9743_.m_213846_(Component.m_237110_("advMode.setCommand.success", s));
            }
         }

      }
   }

   public void m_6629_(ServerboundSetCommandMinecartPacket p_9913_) {
      PacketUtils.m_131359_(p_9913_, this, this.f_9743_.m_284548_());
      if (!this.f_9745_.m_6993_()) {
         this.f_9743_.m_213846_(Component.m_237115_("advMode.notEnabled"));
      } else if (!this.f_9743_.m_36337_()) {
         this.f_9743_.m_213846_(Component.m_237115_("advMode.notAllowed"));
      } else {
         BaseCommandBlock basecommandblock = p_9913_.m_134537_(this.f_9743_.m_9236_());
         if (basecommandblock != null) {
            basecommandblock.m_6590_(p_9913_.m_134545_());
            basecommandblock.m_45428_(p_9913_.m_134548_());
            if (!p_9913_.m_134548_()) {
               basecommandblock.m_45433_((Component)null);
            }

            basecommandblock.m_7368_();
            this.f_9743_.m_213846_(Component.m_237110_("advMode.setCommand.success", p_9913_.m_134545_()));
         }

      }
   }

   public void m_7965_(ServerboundPickItemPacket p_9880_) {
      PacketUtils.m_131359_(p_9880_, this, this.f_9743_.m_284548_());
      this.f_9743_.m_150109_().m_36038_(p_9880_.m_134232_());
      this.f_9743_.f_8906_.m_9829_(new ClientboundContainerSetSlotPacket(-2, 0, this.f_9743_.m_150109_().f_35977_, this.f_9743_.m_150109_().m_8020_(this.f_9743_.m_150109_().f_35977_)));
      this.f_9743_.f_8906_.m_9829_(new ClientboundContainerSetSlotPacket(-2, 0, p_9880_.m_134232_(), this.f_9743_.m_150109_().m_8020_(p_9880_.m_134232_())));
      this.f_9743_.f_8906_.m_9829_(new ClientboundSetCarriedItemPacket(this.f_9743_.m_150109_().f_35977_));
   }

   public void m_5591_(ServerboundRenameItemPacket p_9899_) {
      PacketUtils.m_131359_(p_9899_, this, this.f_9743_.m_284548_());
      AbstractContainerMenu abstractcontainermenu = this.f_9743_.f_36096_;
      if (abstractcontainermenu instanceof AnvilMenu anvilmenu) {
         if (!anvilmenu.m_6875_(this.f_9743_)) {
            f_9744_.debug("Player {} interacted with invalid menu {}", this.f_9743_, anvilmenu);
            return;
         }

         anvilmenu.m_39020_(p_9899_.m_134403_());
      }

   }

   public void m_5712_(ServerboundSetBeaconPacket p_9907_) {
      PacketUtils.m_131359_(p_9907_, this, this.f_9743_.m_284548_());
      AbstractContainerMenu abstractcontainermenu = this.f_9743_.f_36096_;
      if (abstractcontainermenu instanceof BeaconMenu beaconmenu) {
         if (!this.f_9743_.f_36096_.m_6875_(this.f_9743_)) {
            f_9744_.debug("Player {} interacted with invalid menu {}", this.f_9743_, this.f_9743_.f_36096_);
            return;
         }

         beaconmenu.m_219972_(p_9907_.m_237994_(), p_9907_.m_238000_());
      }

   }

   public void m_7424_(ServerboundSetStructureBlockPacket p_9919_) {
      PacketUtils.m_131359_(p_9919_, this, this.f_9743_.m_284548_());
      if (this.f_9743_.m_36337_()) {
         BlockPos blockpos = p_9919_.m_134629_();
         BlockState blockstate = this.f_9743_.m_9236_().m_8055_(blockpos);
         BlockEntity blockentity = this.f_9743_.m_9236_().m_7702_(blockpos);
         if (blockentity instanceof StructureBlockEntity) {
            StructureBlockEntity structureblockentity = (StructureBlockEntity)blockentity;
            structureblockentity.m_59860_(p_9919_.m_134633_());
            structureblockentity.m_59868_(p_9919_.m_134634_());
            structureblockentity.m_59885_(p_9919_.m_134635_());
            structureblockentity.m_155797_(p_9919_.m_179787_());
            structureblockentity.m_59881_(p_9919_.m_134637_());
            structureblockentity.m_59883_(p_9919_.m_134638_());
            structureblockentity.m_59887_(p_9919_.m_134639_());
            structureblockentity.m_59876_(p_9919_.m_134640_());
            structureblockentity.m_59896_(p_9919_.m_134641_());
            structureblockentity.m_59898_(p_9919_.m_134642_());
            structureblockentity.m_59838_(p_9919_.m_134643_());
            structureblockentity.m_59840_(p_9919_.m_134644_());
            if (structureblockentity.m_59901_()) {
               String s = structureblockentity.m_59895_();
               if (p_9919_.m_134632_() == StructureBlockEntity.UpdateType.SAVE_AREA) {
                  if (structureblockentity.m_59830_()) {
                     this.f_9743_.m_5661_(Component.m_237110_("structure_block.save_success", s), false);
                  } else {
                     this.f_9743_.m_5661_(Component.m_237110_("structure_block.save_failure", s), false);
                  }
               } else if (p_9919_.m_134632_() == StructureBlockEntity.UpdateType.LOAD_AREA) {
                  if (!structureblockentity.m_59832_()) {
                     this.f_9743_.m_5661_(Component.m_237110_("structure_block.load_not_found", s), false);
                  } else if (structureblockentity.m_59842_(this.f_9743_.m_284548_())) {
                     this.f_9743_.m_5661_(Component.m_237110_("structure_block.load_success", s), false);
                  } else {
                     this.f_9743_.m_5661_(Component.m_237110_("structure_block.load_prepare", s), false);
                  }
               } else if (p_9919_.m_134632_() == StructureBlockEntity.UpdateType.SCAN_AREA) {
                  if (structureblockentity.m_59829_()) {
                     this.f_9743_.m_5661_(Component.m_237110_("structure_block.size_success", s), false);
                  } else {
                     this.f_9743_.m_5661_(Component.m_237115_("structure_block.size_failure"), false);
                  }
               }
            } else {
               this.f_9743_.m_5661_(Component.m_237110_("structure_block.invalid_structure_name", p_9919_.m_134634_()), false);
            }

            structureblockentity.m_6596_();
            this.f_9743_.m_9236_().m_7260_(blockpos, blockstate, blockstate, 3);
         }

      }
   }

   public void m_8019_(ServerboundSetJigsawBlockPacket p_9917_) {
      PacketUtils.m_131359_(p_9917_, this, this.f_9743_.m_284548_());
      if (this.f_9743_.m_36337_()) {
         BlockPos blockpos = p_9917_.m_134585_();
         BlockState blockstate = this.f_9743_.m_9236_().m_8055_(blockpos);
         BlockEntity blockentity = this.f_9743_.m_9236_().m_7702_(blockpos);
         if (blockentity instanceof JigsawBlockEntity) {
            JigsawBlockEntity jigsawblockentity = (JigsawBlockEntity)blockentity;
            jigsawblockentity.m_59435_(p_9917_.m_134588_());
            jigsawblockentity.m_59438_(p_9917_.m_134589_());
            jigsawblockentity.m_222763_(ResourceKey.m_135785_(Registries.f_256948_, p_9917_.m_134590_()));
            jigsawblockentity.m_59431_(p_9917_.m_134591_());
            jigsawblockentity.m_59424_(p_9917_.m_134592_());
            jigsawblockentity.m_6596_();
            this.f_9743_.m_9236_().m_7260_(blockpos, blockstate, blockstate, 3);
         }

      }
   }

   public void m_6449_(ServerboundJigsawGeneratePacket p_9868_) {
      PacketUtils.m_131359_(p_9868_, this, this.f_9743_.m_284548_());
      if (this.f_9743_.m_36337_()) {
         BlockPos blockpos = p_9868_.m_134087_();
         BlockEntity blockentity = this.f_9743_.m_9236_().m_7702_(blockpos);
         if (blockentity instanceof JigsawBlockEntity) {
            JigsawBlockEntity jigsawblockentity = (JigsawBlockEntity)blockentity;
            jigsawblockentity.m_59420_(this.f_9743_.m_284548_(), p_9868_.m_134090_(), p_9868_.m_134091_());
         }

      }
   }

   public void m_6321_(ServerboundSelectTradePacket p_9905_) {
      PacketUtils.m_131359_(p_9905_, this, this.f_9743_.m_284548_());
      int i = p_9905_.m_134469_();
      AbstractContainerMenu abstractcontainermenu = this.f_9743_.f_36096_;
      if (abstractcontainermenu instanceof MerchantMenu merchantmenu) {
         if (!merchantmenu.m_6875_(this.f_9743_)) {
            f_9744_.debug("Player {} interacted with invalid menu {}", this.f_9743_, merchantmenu);
            return;
         }

         merchantmenu.m_40063_(i);
         merchantmenu.m_40072_(i);
      }

   }

   public void m_6829_(ServerboundEditBookPacket p_9862_) {
      int i = p_9862_.m_134013_();
      if (Inventory.m_36045_(i) || i == 40) {
         List<String> list = Lists.newArrayList();
         Optional<String> optional = p_9862_.m_182761_();
         optional.ifPresent(list::add);
         p_9862_.m_182755_().stream().limit(100L).forEach(list::add);
         Consumer<List<FilteredText>> consumer = optional.isPresent() ? (p_238198_) -> {
            this.m_215208_(p_238198_.get(0), p_238198_.subList(1, p_238198_.size()), i);
         } : (p_143627_) -> {
            this.m_9812_(p_143627_, i);
         };
         this.m_243065_(list).thenAcceptAsync(consumer, this.f_9745_);
      }
   }

   private void m_9812_(List<FilteredText> p_9813_, int p_9814_) {
      ItemStack itemstack = this.f_9743_.m_150109_().m_8020_(p_9814_);
      if (itemstack.m_150930_(Items.f_42614_)) {
         this.m_143634_(p_9813_, UnaryOperator.identity(), itemstack);
      }
   }

   private void m_215208_(FilteredText p_215209_, List<FilteredText> p_215210_, int p_215211_) {
      ItemStack itemstack = this.f_9743_.m_150109_().m_8020_(p_215211_);
      if (itemstack.m_150930_(Items.f_42614_)) {
         ItemStack itemstack1 = new ItemStack(Items.f_42615_);
         CompoundTag compoundtag = itemstack.m_41783_();
         if (compoundtag != null) {
            itemstack1.m_41751_(compoundtag.m_6426_());
         }

         itemstack1.m_41700_("author", StringTag.m_129297_(this.f_9743_.m_7755_().getString()));
         if (this.f_9743_.m_143387_()) {
            itemstack1.m_41700_("title", StringTag.m_129297_(p_215209_.m_243113_()));
         } else {
            itemstack1.m_41700_("filtered_title", StringTag.m_129297_(p_215209_.m_243113_()));
            itemstack1.m_41700_("title", StringTag.m_129297_(p_215209_.f_215168_()));
         }

         this.m_143634_(p_215210_, (p_238206_) -> {
            return Component.Serializer.m_130703_(Component.m_237113_(p_238206_));
         }, itemstack1);
         this.f_9743_.m_150109_().m_6836_(p_215211_, itemstack1);
      }
   }

   private void m_143634_(List<FilteredText> p_143635_, UnaryOperator<String> p_143636_, ItemStack p_143637_) {
      ListTag listtag = new ListTag();
      if (this.f_9743_.m_143387_()) {
         p_143635_.stream().map((p_238209_) -> {
            return StringTag.m_129297_(p_143636_.apply(p_238209_.m_243113_()));
         }).forEach(listtag::add);
      } else {
         CompoundTag compoundtag = new CompoundTag();
         int i = 0;

         for(int j = p_143635_.size(); i < j; ++i) {
            FilteredText filteredtext = p_143635_.get(i);
            String s = filteredtext.f_215168_();
            listtag.add(StringTag.m_129297_(p_143636_.apply(s)));
            if (filteredtext.m_215174_()) {
               compoundtag.m_128359_(String.valueOf(i), p_143636_.apply(filteredtext.m_243113_()));
            }
         }

         if (!compoundtag.m_128456_()) {
            p_143637_.m_41700_("filtered_pages", compoundtag);
         }
      }

      p_143637_.m_41700_("pages", listtag);
   }

   public void m_7548_(ServerboundEntityTagQuery p_9864_) {
      PacketUtils.m_131359_(p_9864_, this, this.f_9743_.m_284548_());
      if (this.f_9743_.m_20310_(2)) {
         Entity entity = this.f_9743_.m_9236_().m_6815_(p_9864_.m_134029_());
         if (entity != null) {
            CompoundTag compoundtag = entity.m_20240_(new CompoundTag());
            this.f_9743_.f_8906_.m_9829_(new ClientboundTagQueryPacket(p_9864_.m_134026_(), compoundtag));
         }

      }
   }

   public void m_6780_(ServerboundBlockEntityTagQuery p_9837_) {
      PacketUtils.m_131359_(p_9837_, this, this.f_9743_.m_284548_());
      if (this.f_9743_.m_20310_(2)) {
         BlockEntity blockentity = this.f_9743_.m_9236_().m_7702_(p_9837_.m_133813_());
         CompoundTag compoundtag = blockentity != null ? blockentity.m_187482_() : null;
         this.f_9743_.f_8906_.m_9829_(new ClientboundTagQueryPacket(p_9837_.m_133810_(), compoundtag));
      }
   }

   public void m_7185_(ServerboundMovePlayerPacket p_9874_) {
      PacketUtils.m_131359_(p_9874_, this, this.f_9743_.m_284548_());
      if (m_143663_(p_9874_.m_134129_(0.0D), p_9874_.m_134140_(0.0D), p_9874_.m_134146_(0.0D), p_9874_.m_134131_(0.0F), p_9874_.m_134142_(0.0F))) {
         this.m_9942_(Component.m_237115_("multiplayer.disconnect.invalid_player_movement"));
      } else {
         ServerLevel serverlevel = this.f_9743_.m_284548_();
         if (!this.f_9743_.f_8944_) {
            if (this.f_9746_ == 0) {
               this.m_9953_();
            }

            if (this.f_9766_ != null) {
               if (this.f_9746_ - this.f_9735_ > 20) {
                  this.f_9735_ = this.f_9746_;
                  this.m_9774_(this.f_9766_.f_82479_, this.f_9766_.f_82480_, this.f_9766_.f_82481_, this.f_9743_.m_146908_(), this.f_9743_.m_146909_());
               }

            } else {
               this.f_9735_ = this.f_9746_;
               double d0 = m_143609_(p_9874_.m_134129_(this.f_9743_.m_20185_()));
               double d1 = m_143653_(p_9874_.m_134140_(this.f_9743_.m_20186_()));
               double d2 = m_143609_(p_9874_.m_134146_(this.f_9743_.m_20189_()));
               float f = Mth.m_14177_(p_9874_.m_134131_(this.f_9743_.m_146908_()));
               float f1 = Mth.m_14177_(p_9874_.m_134142_(this.f_9743_.m_146909_()));
               if (this.f_9743_.m_20159_()) {
                  this.f_9743_.m_19890_(this.f_9743_.m_20185_(), this.f_9743_.m_20186_(), this.f_9743_.m_20189_(), f, f1);
                  this.f_9743_.m_284548_().m_7726_().m_8385_(this.f_9743_);
               } else {
                  double d3 = this.f_9743_.m_20185_();
                  double d4 = this.f_9743_.m_20186_();
                  double d5 = this.f_9743_.m_20189_();
                  double d6 = d0 - this.f_9753_;
                  double d7 = d1 - this.f_9754_;
                  double d8 = d2 - this.f_9755_;
                  double d9 = this.f_9743_.m_20184_().m_82556_();
                  double d10 = d6 * d6 + d7 * d7 + d8 * d8;
                  if (this.f_9743_.m_5803_()) {
                     if (d10 > 1.0D) {
                        this.m_9774_(this.f_9743_.m_20185_(), this.f_9743_.m_20186_(), this.f_9743_.m_20189_(), f, f1);
                     }

                  } else {
                     ++this.f_9740_;
                     int i = this.f_9740_ - this.f_9741_;
                     if (i > 5) {
                        f_9744_.debug("{} is sending move packets too frequently ({} packets since last tick)", this.f_9743_.m_7755_().getString(), i);
                        i = 1;
                     }

                     if (!this.f_9743_.m_8958_() && (!this.f_9743_.m_9236_().m_46469_().m_46207_(GameRules.f_46148_) || !this.f_9743_.m_21255_())) {
                        float f2 = this.f_9743_.m_21255_() ? 300.0F : 100.0F;
                        if (d10 - d9 > (double)(f2 * (float)i) && !this.m_9956_()) {
                           f_9744_.warn("{} moved too quickly! {},{},{}", this.f_9743_.m_7755_().getString(), d6, d7, d8);
                           this.m_9774_(this.f_9743_.m_20185_(), this.f_9743_.m_20186_(), this.f_9743_.m_20189_(), this.f_9743_.m_146908_(), this.f_9743_.m_146909_());
                           return;
                        }
                     }

                     AABB aabb = this.f_9743_.m_20191_();
                     d6 = d0 - this.f_9756_;
                     d7 = d1 - this.f_9757_;
                     d8 = d2 - this.f_9758_;
                     boolean flag = d7 > 0.0D;
                     if (this.f_9743_.m_20096_() && !p_9874_.m_134139_() && flag) {
                        this.f_9743_.m_6135_();
                     }

                     boolean flag1 = this.f_9743_.f_201939_;
                     this.f_9743_.m_6478_(MoverType.PLAYER, new Vec3(d6, d7, d8));
                     d6 = d0 - this.f_9743_.m_20185_();
                     d7 = d1 - this.f_9743_.m_20186_();
                     if (d7 > -0.5D || d7 < 0.5D) {
                        d7 = 0.0D;
                     }

                     d8 = d2 - this.f_9743_.m_20189_();
                     d10 = d6 * d6 + d7 * d7 + d8 * d8;
                     boolean flag2 = false;
                     if (!this.f_9743_.m_8958_() && d10 > 0.0625D && !this.f_9743_.m_5803_() && !this.f_9743_.f_8941_.m_9295_() && this.f_9743_.f_8941_.m_9290_() != GameType.SPECTATOR) {
                        flag2 = true;
                        f_9744_.warn("{} moved wrongly!", (Object)this.f_9743_.m_7755_().getString());
                     }

                     if (this.f_9743_.f_19794_ || this.f_9743_.m_5803_() || (!flag2 || !serverlevel.m_45756_(this.f_9743_, aabb)) && !this.m_288208_(serverlevel, aabb, d0, d1, d2)) {
                        this.f_9743_.m_19890_(d0, d1, d2, f, f1);
                        this.f_9736_ = d7 >= -0.03125D && !flag1 && this.f_9743_.f_8941_.m_9290_() != GameType.SPECTATOR && !this.f_9745_.m_129915_() && !this.f_9743_.m_150110_().f_35936_ && !this.f_9743_.m_21023_(MobEffects.f_19620_) && !this.f_9743_.m_21255_() && !this.f_9743_.m_21209_() && this.m_9793_(this.f_9743_);
                        this.f_9743_.m_284548_().m_7726_().m_8385_(this.f_9743_);
                        this.f_9743_.m_289599_(this.f_9743_.m_20185_() - d3, this.f_9743_.m_20186_() - d4, this.f_9743_.m_20189_() - d5, p_9874_.m_134139_());
                        this.f_9743_.m_289603_(p_9874_.m_134139_(), new Vec3(this.f_9743_.m_20185_() - d3, this.f_9743_.m_20186_() - d4, this.f_9743_.m_20189_() - d5));
                        if (flag) {
                           this.f_9743_.m_183634_();
                        }

                        this.f_9743_.m_36378_(this.f_9743_.m_20185_() - d3, this.f_9743_.m_20186_() - d4, this.f_9743_.m_20189_() - d5);
                        this.f_9756_ = this.f_9743_.m_20185_();
                        this.f_9757_ = this.f_9743_.m_20186_();
                        this.f_9758_ = this.f_9743_.m_20189_();
                     } else {
                        this.m_9774_(d3, d4, d5, f, f1);
                        this.f_9743_.m_289599_(this.f_9743_.m_20185_() - d3, this.f_9743_.m_20186_() - d4, this.f_9743_.m_20189_() - d5, p_9874_.m_134139_());
                     }
                  }
               }
            }
         }
      }
   }

   private boolean m_288208_(LevelReader p_289008_, AABB p_288986_, double p_288990_, double p_288991_, double p_288967_) {
      AABB aabb = this.f_9743_.m_20191_().m_82386_(p_288990_ - this.f_9743_.m_20185_(), p_288991_ - this.f_9743_.m_20186_(), p_288967_ - this.f_9743_.m_20189_());
      Iterable<VoxelShape> iterable = p_289008_.m_186431_(this.f_9743_, aabb.m_82406_((double)1.0E-5F));
      VoxelShape voxelshape = Shapes.m_83064_(p_288986_.m_82406_((double)1.0E-5F));

      for(VoxelShape voxelshape1 : iterable) {
         if (!Shapes.m_83157_(voxelshape1, voxelshape, BooleanOp.f_82689_)) {
            return true;
         }
      }

      return false;
   }

   public void m_9774_(double p_9775_, double p_9776_, double p_9777_, float p_9778_, float p_9779_) {
      this.m_9780_(p_9775_, p_9776_, p_9777_, p_9778_, p_9779_, Collections.emptySet());
   }

   public void m_9780_(double p_9781_, double p_9782_, double p_9783_, float p_9784_, float p_9785_, Set<RelativeMovement> p_9786_) {
      double d0 = p_9786_.contains(RelativeMovement.X) ? this.f_9743_.m_20185_() : 0.0D;
      double d1 = p_9786_.contains(RelativeMovement.Y) ? this.f_9743_.m_20186_() : 0.0D;
      double d2 = p_9786_.contains(RelativeMovement.Z) ? this.f_9743_.m_20189_() : 0.0D;
      float f = p_9786_.contains(RelativeMovement.Y_ROT) ? this.f_9743_.m_146908_() : 0.0F;
      float f1 = p_9786_.contains(RelativeMovement.X_ROT) ? this.f_9743_.m_146909_() : 0.0F;
      this.f_9766_ = new Vec3(p_9781_, p_9782_, p_9783_);
      if (++this.f_9767_ == Integer.MAX_VALUE) {
         this.f_9767_ = 0;
      }

      this.f_9735_ = this.f_9746_;
      this.f_9743_.m_19890_(p_9781_, p_9782_, p_9783_, p_9784_, p_9785_);
      this.f_9743_.f_8906_.m_9829_(new ClientboundPlayerPositionPacket(p_9781_ - d0, p_9782_ - d1, p_9783_ - d2, p_9784_ - f, p_9785_ - f1, p_9786_, this.f_9767_));
   }

   public void m_7502_(ServerboundPlayerActionPacket p_9889_) {
      PacketUtils.m_131359_(p_9889_, this, this.f_9743_.m_284548_());
      BlockPos blockpos = p_9889_.m_134281_();
      this.f_9743_.m_9243_();
      ServerboundPlayerActionPacket.Action serverboundplayeractionpacket$action = p_9889_.m_134285_();
      switch (serverboundplayeractionpacket$action) {
         case SWAP_ITEM_WITH_OFFHAND:
            if (!this.f_9743_.m_5833_()) {
               ItemStack itemstack = this.f_9743_.m_21120_(InteractionHand.OFF_HAND);
               var event = net.minecraftforge.common.ForgeHooks.onLivingSwapHandItems(this.f_9743_);
               if (event.isCanceled()) return;
               this.f_9743_.m_21008_(InteractionHand.OFF_HAND, event.getItemSwappedToOffHand());
               this.f_9743_.m_21008_(InteractionHand.MAIN_HAND, event.getItemSwappedToMainHand());
               this.f_9743_.m_5810_();
            }

            return;
         case DROP_ITEM:
            if (!this.f_9743_.m_5833_()) {
               this.f_9743_.m_182294_(false);
            }

            return;
         case DROP_ALL_ITEMS:
            if (!this.f_9743_.m_5833_()) {
               this.f_9743_.m_182294_(true);
            }

            return;
         case RELEASE_USE_ITEM:
            this.f_9743_.m_21253_();
            return;
         case START_DESTROY_BLOCK:
         case ABORT_DESTROY_BLOCK:
         case STOP_DESTROY_BLOCK:
            this.f_9743_.f_8941_.m_214168_(blockpos, serverboundplayeractionpacket$action, p_9889_.m_134284_(), this.f_9743_.m_9236_().m_151558_(), p_9889_.m_237987_());
            this.f_9743_.f_8906_.m_215201_(p_9889_.m_237987_());
            return;
         default:
            throw new IllegalArgumentException("Invalid player action");
      }
   }

   private static boolean m_9790_(ServerPlayer p_9791_, ItemStack p_9792_) {
      if (p_9792_.m_41619_()) {
         return false;
      } else {
         Item item = p_9792_.m_41720_();
         return (item instanceof BlockItem || item instanceof BucketItem) && !p_9791_.m_36335_().m_41519_(item);
      }
   }

   public void m_6371_(ServerboundUseItemOnPacket p_9930_) {
      PacketUtils.m_131359_(p_9930_, this, this.f_9743_.m_284548_());
      this.f_9743_.f_8906_.m_215201_(p_9930_.m_238008_());
      ServerLevel serverlevel = this.f_9743_.m_284548_();
      InteractionHand interactionhand = p_9930_.m_134703_();
      ItemStack itemstack = this.f_9743_.m_21120_(interactionhand);
      if (itemstack.m_246617_(serverlevel.m_246046_())) {
         BlockHitResult blockhitresult = p_9930_.m_134706_();
         Vec3 vec3 = blockhitresult.m_82450_();
         BlockPos blockpos = blockhitresult.m_82425_();
         Vec3 vec31 = Vec3.m_82512_(blockpos);
         if (this.f_9743_.canReachRaw(blockpos, 1.5)) { // Vanilla uses eye-to-center distance < ServerGamePacketListenerImpl which is 6*6, default block reach is 4.5, so add 1.5 padding
            Vec3 vec32 = vec3.m_82546_(vec31);
            double d0 = 1.0000001D;
            if (Math.abs(vec32.m_7096_()) < 1.0000001D && Math.abs(vec32.m_7098_()) < 1.0000001D && Math.abs(vec32.m_7094_()) < 1.0000001D) {
               Direction direction = blockhitresult.m_82434_();
               this.f_9743_.m_9243_();
               int i = this.f_9743_.m_9236_().m_151558_();
               if (blockpos.m_123342_() < i) {
                  if (this.f_9766_ == null && serverlevel.m_7966_(this.f_9743_, blockpos)) {
                     InteractionResult interactionresult = this.f_9743_.f_8941_.m_7179_(this.f_9743_, serverlevel, itemstack, interactionhand, blockhitresult);
                     if (direction == Direction.UP && !interactionresult.m_19077_() && blockpos.m_123342_() >= i - 1 && m_9790_(this.f_9743_, itemstack)) {
                        Component component = Component.m_237110_("build.tooHigh", i - 1).m_130940_(ChatFormatting.RED);
                        this.f_9743_.m_240418_(component, true);
                     } else if (interactionresult.m_19080_()) {
                        this.f_9743_.m_21011_(interactionhand, true);
                     }
                  }
               } else {
                  Component component1 = Component.m_237110_("build.tooHigh", i - 1).m_130940_(ChatFormatting.RED);
                  this.f_9743_.m_240418_(component1, true);
               }

               this.f_9743_.f_8906_.m_9829_(new ClientboundBlockUpdatePacket(serverlevel, blockpos));
               this.f_9743_.f_8906_.m_9829_(new ClientboundBlockUpdatePacket(serverlevel, blockpos.m_121945_(direction)));
            } else {
               f_9744_.warn("Rejecting UseItemOnPacket from {}: Location {} too far away from hit block {}.", this.f_9743_.m_36316_().getName(), vec3, blockpos);
            }
         }
      }
   }

   public void m_5760_(ServerboundUseItemPacket p_9932_) {
      PacketUtils.m_131359_(p_9932_, this, this.f_9743_.m_284548_());
      this.m_215201_(p_9932_.m_238013_());
      ServerLevel serverlevel = this.f_9743_.m_284548_();
      InteractionHand interactionhand = p_9932_.m_134717_();
      ItemStack itemstack = this.f_9743_.m_21120_(interactionhand);
      this.f_9743_.m_9243_();
      if (!itemstack.m_41619_() && itemstack.m_246617_(serverlevel.m_246046_())) {
         InteractionResult interactionresult = this.f_9743_.f_8941_.m_6261_(this.f_9743_, serverlevel, itemstack, interactionhand);
         if (interactionresult.m_19080_()) {
            this.f_9743_.m_21011_(interactionhand, true);
         }

      }
   }

   public void m_6936_(ServerboundTeleportToEntityPacket p_9928_) {
      PacketUtils.m_131359_(p_9928_, this, this.f_9743_.m_284548_());
      if (this.f_9743_.m_5833_()) {
         for(ServerLevel serverlevel : this.f_9745_.m_129785_()) {
            Entity entity = p_9928_.m_134681_(serverlevel);
            if (entity != null) {
               this.f_9743_.m_8999_(serverlevel, entity.m_20185_(), entity.m_20186_(), entity.m_20189_(), entity.m_146908_(), entity.m_146909_());
               return;
            }
         }
      }

   }

   public void m_7529_(ServerboundResourcePackPacket p_9901_) {
      PacketUtils.m_131359_(p_9901_, this, this.f_9743_.m_284548_());
      if (p_9901_.m_179741_() == ServerboundResourcePackPacket.Action.DECLINED && this.f_9745_.m_142205_()) {
         f_9744_.info("Disconnecting {} due to resource pack rejection", (Object)this.f_9743_.m_7755_());
         this.m_9942_(Component.m_237115_("multiplayer.requiredTexturePrompt.disconnect"));
      }

   }

   public void m_5938_(ServerboundPaddleBoatPacket p_9878_) {
      PacketUtils.m_131359_(p_9878_, this, this.f_9743_.m_284548_());
      Entity entity = this.f_9743_.m_275832_();
      if (entity instanceof Boat boat) {
         boat.m_38339_(p_9878_.m_134218_(), p_9878_.m_134221_());
      }

   }

   public void m_142110_(ServerboundPongPacket p_143652_) {
   }

   public void m_7026_(Component p_9825_) {
      this.f_241681_.close();
      f_9744_.info("{} lost connection: {}", this.f_9743_.m_7755_().getString(), p_9825_.getString());
      this.f_9745_.m_129929_();
      this.f_9745_.m_6846_().m_240416_(Component.m_237110_("multiplayer.player.left", this.f_9743_.m_5446_()).m_130940_(ChatFormatting.YELLOW), false);
      this.f_9743_.m_9231_();
      this.f_9745_.m_6846_().m_11286_(this.f_9743_);
      this.f_9743_.m_8967_().m_7670_();
      if (this.m_9956_()) {
         f_9744_.info("Stopping singleplayer server as player logged out");
         this.f_9745_.m_7570_(false);
      }

   }

   public void m_215201_(int p_215202_) {
      if (p_215202_ < 0) {
         throw new IllegalArgumentException("Expected packet sequence nr >= 0");
      } else {
         this.f_215200_ = Math.max(p_215202_, this.f_215200_);
      }
   }

   public void m_9829_(Packet<?> p_9830_) {
      this.m_243119_(p_9830_, (PacketSendListener)null);
   }

   public void m_243119_(Packet<?> p_243227_, @Nullable PacketSendListener p_243273_) {
      try {
         this.f_9742_.m_243124_(p_243227_, p_243273_);
      } catch (Throwable throwable) {
         CrashReport crashreport = CrashReport.m_127521_(throwable, "Sending packet");
         CrashReportCategory crashreportcategory = crashreport.m_127514_("Packet being sent");
         crashreportcategory.m_128165_("Packet class", () -> {
            return p_243227_.getClass().getCanonicalName();
         });
         throw new ReportedException(crashreport);
      }
   }

   public void m_7798_(ServerboundSetCarriedItemPacket p_9909_) {
      PacketUtils.m_131359_(p_9909_, this, this.f_9743_.m_284548_());
      if (p_9909_.m_134498_() >= 0 && p_9909_.m_134498_() < Inventory.m_36059_()) {
         if (this.f_9743_.m_150109_().f_35977_ != p_9909_.m_134498_() && this.f_9743_.m_7655_() == InteractionHand.MAIN_HAND) {
            this.f_9743_.m_5810_();
         }

         this.f_9743_.m_150109_().f_35977_ = p_9909_.m_134498_();
         this.f_9743_.m_9243_();
      } else {
         f_9744_.warn("{} tried to set an invalid carried item", (Object)this.f_9743_.m_7755_().getString());
      }
   }

   public void m_7388_(ServerboundChatPacket p_9841_) {
      if (m_215214_(p_9841_.f_133827_())) {
         this.m_9942_(Component.m_237115_("multiplayer.disconnect.illegal_characters"));
      } else {
         Optional<LastSeenMessages> optional = this.m_247189_(p_9841_.f_133827_(), p_9841_.f_237950_(), p_9841_.f_241662_());
         if (optional.isPresent()) {
            this.f_9745_.m_18707_(() -> {
               PlayerChatMessage playerchatmessage;
               try {
                  playerchatmessage = this.m_247340_(p_9841_, optional.get());
               } catch (SignedMessageChain.DecodeException signedmessagechain$decodeexception) {
                  this.m_246889_(signedmessagechain$decodeexception);
                  return;
               }

               CompletableFuture<FilteredText> completablefuture = this.m_243132_(playerchatmessage.m_245728_());
               CompletableFuture<Component> completablefuture1 = net.minecraftforge.common.ForgeHooks.getServerChatSubmittedDecorator().m_236961_(this.f_9743_, playerchatmessage.m_245692_());
               this.f_241681_.m_241849_((p_248212_) -> {
                  return CompletableFuture.allOf(completablefuture, completablefuture1).thenAcceptAsync((p_248218_) -> {
                     Component decoratedContent = completablefuture1.join();
                     if (decoratedContent == null)
                        return; // Forge: ServerChatEvent was canceled if this is null.
                     PlayerChatMessage playerchatmessage1 = playerchatmessage.m_241956_(decoratedContent).m_243072_(completablefuture.join().f_243010_());
                     this.m_243086_(playerchatmessage1);
                  }, p_248212_);
               });
            });
         }

      }
   }

   public void m_214047_(ServerboundChatCommandPacket p_215225_) {
      if (m_215214_(p_215225_.f_237922_())) {
         this.m_9942_(Component.m_237115_("multiplayer.disconnect.illegal_characters"));
      } else {
         Optional<LastSeenMessages> optional = this.m_247189_(p_215225_.f_237922_(), p_215225_.f_237923_(), p_215225_.f_241638_());
         if (optional.isPresent()) {
            this.f_9745_.m_18707_(() -> {
               this.m_246958_(p_215225_, optional.get());
               this.m_215251_();
            });
         }

      }
   }

   private void m_246958_(ServerboundChatCommandPacket p_251139_, LastSeenMessages p_250484_) {
      ParseResults<CommandSourceStack> parseresults = this.m_242658_(p_251139_.f_237922_());

      Map<String, PlayerChatMessage> map;
      try {
         map = this.m_246206_(p_251139_, SignableCommand.m_246497_(parseresults), p_250484_);
      } catch (SignedMessageChain.DecodeException signedmessagechain$decodeexception) {
         this.m_246889_(signedmessagechain$decodeexception);
         return;
      }

      CommandSigningContext commandsigningcontext = new CommandSigningContext.SignedArguments(map);
      parseresults = Commands.m_242611_(parseresults, (p_242749_) -> {
         return p_242749_.m_230893_(commandsigningcontext);
      });
      this.f_9745_.m_129892_().m_242674_(parseresults, p_251139_.f_237922_());
   }

   private void m_246889_(SignedMessageChain.DecodeException p_252068_) {
      if (p_252068_.m_246459_()) {
         this.m_9942_(p_252068_.m_237308_());
      } else {
         this.f_9743_.m_213846_(p_252068_.m_237308_().m_6881_().m_130940_(ChatFormatting.RED));
      }

   }

   private Map<String, PlayerChatMessage> m_246206_(ServerboundChatCommandPacket p_249441_, SignableCommand<?> p_250039_, LastSeenMessages p_249207_) throws SignedMessageChain.DecodeException {
      Map<String, PlayerChatMessage> map = new Object2ObjectOpenHashMap<>();

      for(SignableCommand.Argument<?> argument : p_250039_.f_244150_()) {
         MessageSignature messagesignature = p_249441_.f_237924_().m_240943_(argument.m_246038_());
         SignedMessageBody signedmessagebody = new SignedMessageBody(argument.f_244218_(), p_249441_.f_237923_(), p_249441_.f_240858_(), p_249207_);
         map.put(argument.m_246038_(), this.f_240889_.m_240945_(messagesignature, signedmessagebody));
      }

      return map;
   }

   private ParseResults<CommandSourceStack> m_242658_(String p_242938_) {
      CommandDispatcher<CommandSourceStack> commanddispatcher = this.f_9745_.m_129892_().m_82094_();
      return commanddispatcher.parse(p_242938_, this.f_9743_.m_20203_());
   }

   private Optional<LastSeenMessages> m_247189_(String p_251364_, Instant p_248959_, LastSeenMessages.Update p_249613_) {
      if (!this.m_215236_(p_248959_)) {
         f_9744_.warn("{} sent out-of-order chat: '{}'", this.f_9743_.m_7755_().getString(), p_251364_);
         this.m_9942_(Component.m_237115_("multiplayer.disconnect.out_of_order_chat"));
         return Optional.empty();
      } else {
         Optional<LastSeenMessages> optional = this.m_245578_(p_249613_);
         if (this.f_9743_.m_9241_() == ChatVisiblity.HIDDEN) {
            this.m_9829_(new ClientboundSystemChatPacket(Component.m_237115_("chat.disabled.options").m_130940_(ChatFormatting.RED), false));
            return Optional.empty();
         } else {
            this.f_9743_.m_9243_();
            return optional;
         }
      }
   }

   private Optional<LastSeenMessages> m_245578_(LastSeenMessages.Update p_249673_) {
      synchronized(this.f_244262_) {
         Optional<LastSeenMessages> optional = this.f_244262_.m_247119_(p_249673_);
         if (optional.isEmpty()) {
            f_9744_.warn("Failed to validate message acknowledgements from {}", (Object)this.f_9743_.m_7755_().getString());
            this.m_9942_(f_244304_);
         }

         return optional;
      }
   }

   private boolean m_215236_(Instant p_215237_) {
      Instant instant;
      do {
         instant = this.f_215197_.get();
         if (p_215237_.isBefore(instant)) {
            return false;
         }
      } while(!this.f_215197_.compareAndSet(instant, p_215237_));

      return true;
   }

   private static boolean m_215214_(String p_215215_) {
      for(int i = 0; i < p_215215_.length(); ++i) {
         if (!SharedConstants.m_136188_(p_215215_.charAt(i))) {
            return true;
         }
      }

      return false;
   }

   private PlayerChatMessage m_247340_(ServerboundChatPacket p_251061_, LastSeenMessages p_250566_) throws SignedMessageChain.DecodeException {
      SignedMessageBody signedmessagebody = new SignedMessageBody(p_251061_.f_133827_(), p_251061_.f_237950_(), p_251061_.f_240906_(), p_250566_);
      return this.f_240889_.m_240945_(p_251061_.f_240898_(), signedmessagebody);
   }

   private void m_243086_(PlayerChatMessage p_243277_) {
      this.f_9745_.m_6846_().m_243049_(p_243277_, this.f_9743_, ChatType.m_240980_(ChatType.f_130598_, this.f_9743_));
      this.m_215251_();
   }

   private void m_215251_() {
      this.f_9750_ += 20;
      if (this.f_9750_ > 200 && !this.f_9745_.m_6846_().m_11303_(this.f_9743_.m_36316_())) {
         this.m_9942_(Component.m_237115_("disconnect.spam"));
      }

   }

   public void m_241885_(ServerboundChatAckPacket p_242387_) {
      synchronized(this.f_244262_) {
         if (!this.f_244262_.m_245398_(p_242387_.f_244085_())) {
            f_9744_.warn("Failed to validate message acknowledgements from {}", (Object)this.f_9743_.m_7755_().getString());
            this.m_9942_(f_244304_);
         }

      }
   }

   public void m_7953_(ServerboundSwingPacket p_9926_) {
      PacketUtils.m_131359_(p_9926_, this, this.f_9743_.m_284548_());
      this.f_9743_.m_9243_();
      this.f_9743_.m_6674_(p_9926_.m_134674_());
   }

   public void m_5681_(ServerboundPlayerCommandPacket p_9891_) {
      PacketUtils.m_131359_(p_9891_, this, this.f_9743_.m_284548_());
      this.f_9743_.m_9243_();
      switch (p_9891_.m_134320_()) {
         case PRESS_SHIFT_KEY:
            this.f_9743_.m_20260_(true);
            break;
         case RELEASE_SHIFT_KEY:
            this.f_9743_.m_20260_(false);
            break;
         case START_SPRINTING:
            this.f_9743_.m_6858_(true);
            break;
         case STOP_SPRINTING:
            this.f_9743_.m_6858_(false);
            break;
         case STOP_SLEEPING:
            if (this.f_9743_.m_5803_()) {
               this.f_9743_.m_6145_(false, true);
               this.f_9766_ = this.f_9743_.m_20182_();
            }
            break;
         case START_RIDING_JUMP:
            Entity entity2 = this.f_9743_.m_275832_();
            if (entity2 instanceof PlayerRideableJumping playerrideablejumping1) {
               int i = p_9891_.m_134321_();
               if (playerrideablejumping1.m_7132_() && i > 0) {
                  playerrideablejumping1.m_7199_(i);
               }
            }
            break;
         case STOP_RIDING_JUMP:
            Entity entity1 = this.f_9743_.m_275832_();
            if (entity1 instanceof PlayerRideableJumping playerrideablejumping) {
               playerrideablejumping.m_8012_();
            }
            break;
         case OPEN_INVENTORY:
            Entity $$2 = this.f_9743_.m_20202_();
            if ($$2 instanceof HasCustomInventoryScreen hascustominventoryscreen) {
               hascustominventoryscreen.m_213583_(this.f_9743_);
            }
            break;
         case START_FALL_FLYING:
            if (!this.f_9743_.m_36319_()) {
               this.f_9743_.m_36321_();
            }
            break;
         default:
            throw new IllegalArgumentException("Invalid client command!");
      }

   }

   public void m_241992_(PlayerChatMessage p_242439_) {
      MessageSignature messagesignature = p_242439_.f_244279_();
      if (messagesignature != null) {
         this.f_243718_.m_247208_(p_242439_);
         int i;
         synchronized(this.f_244262_) {
            this.f_244262_.m_247482_(messagesignature);
            i = this.f_244262_.m_245741_();
         }

         if (i > 4096) {
            this.m_9942_(Component.m_237115_("multiplayer.disconnect.too_many_pending_chats"));
         }

      }
   }

   public void m_245431_(PlayerChatMessage p_250321_, ChatType.Bound p_250910_) {
      this.m_9829_(new ClientboundPlayerChatPacket(p_250321_.f_243882_().f_244443_(), p_250321_.f_243882_().f_244066_(), p_250321_.f_244279_(), p_250321_.f_240885_().m_253217_(this.f_243718_), p_250321_.f_237215_(), p_250321_.f_242992_(), p_250910_.m_240987_(this.f_9743_.m_9236_().m_9598_())));
      this.m_241992_(p_250321_);
   }

   public void m_245903_(Component p_251804_, ChatType.Bound p_250040_) {
      this.m_9829_(new ClientboundDisguisedChatPacket(p_251804_, p_250040_.m_240987_(this.f_9743_.m_9236_().m_9598_())));
   }

   public SocketAddress m_264262_() {
      return this.f_9742_.m_129523_();
   }

   public void m_6946_(ServerboundInteractPacket p_9866_) {
      PacketUtils.m_131359_(p_9866_, this, this.f_9743_.m_284548_());
      final ServerLevel serverlevel = this.f_9743_.m_284548_();
      final Entity entity = p_9866_.m_179603_(serverlevel);
      this.f_9743_.m_9243_();
      this.f_9743_.m_20260_(p_9866_.m_134061_());
      if (entity != null) {
         if (!serverlevel.m_6857_().m_61937_(entity.m_20183_())) {
            return;
         }

         AABB aabb = entity.m_20191_();
         if (this.f_9743_.canReachRaw(entity, 3.0)) { // Vanilla uses MAX_INTERACTION_DISTANCE which is 6*6 default entity reach is 3.0 so add 3.0 padding
            p_9866_.m_179617_(new ServerboundInteractPacket.Handler() {
               private void m_143678_(InteractionHand p_143679_, ServerGamePacketListenerImpl.EntityInteraction p_143680_) {
                  ItemStack itemstack = ServerGamePacketListenerImpl.this.f_9743_.m_21120_(p_143679_);
                  if (itemstack.m_246617_(serverlevel.m_246046_())) {
                     ItemStack itemstack1 = itemstack.m_41777_();
                     InteractionResult interactionresult = p_143680_.m_143694_(ServerGamePacketListenerImpl.this.f_9743_, entity, p_143679_);
                     if (interactionresult.m_19077_()) {
                        CriteriaTriggers.f_10565_.m_61494_(ServerGamePacketListenerImpl.this.f_9743_, itemstack1, entity);
                        if (interactionresult.m_19080_()) {
                           ServerGamePacketListenerImpl.this.f_9743_.m_21011_(p_143679_, true);
                        }
                     }

                  }
               }

               public void m_142299_(InteractionHand p_143677_) {
                  this.m_143678_(p_143677_, Player::m_36157_);
               }

               public void m_142143_(InteractionHand p_143682_, Vec3 p_143683_) {
                  this.m_143678_(p_143682_, (p_143686_, p_143687_, p_143688_) -> {
                     InteractionResult onInteractEntityAtResult = net.minecraftforge.common.ForgeHooks.onInteractEntityAt(f_9743_, entity, p_143683_, p_143682_);
                     if (onInteractEntityAtResult != null) return onInteractEntityAtResult;
                     return p_143687_.m_7111_(p_143686_, p_143683_, p_143688_);
                  });
               }

               public void m_141994_() {
                  if (!(entity instanceof ItemEntity) && !(entity instanceof ExperienceOrb) && !(entity instanceof AbstractArrow) && entity != ServerGamePacketListenerImpl.this.f_9743_) {
                     ItemStack itemstack = ServerGamePacketListenerImpl.this.f_9743_.m_21120_(InteractionHand.MAIN_HAND);
                     if (itemstack.m_246617_(serverlevel.m_246046_())) {
                        ServerGamePacketListenerImpl.this.f_9743_.m_5706_(entity);
                     }
                  } else {
                     ServerGamePacketListenerImpl.this.m_9942_(Component.m_237115_("multiplayer.disconnect.invalid_entity_attacked"));
                     ServerGamePacketListenerImpl.f_9744_.warn("Player {} tried to attack an invalid entity", (Object)ServerGamePacketListenerImpl.this.f_9743_.m_7755_().getString());
                  }
               }
            });
         }
      }

   }

   public void m_6272_(ServerboundClientCommandPacket p_9843_) {
      PacketUtils.m_131359_(p_9843_, this, this.f_9743_.m_284548_());
      this.f_9743_.m_9243_();
      ServerboundClientCommandPacket.Action serverboundclientcommandpacket$action = p_9843_.m_133850_();
      switch (serverboundclientcommandpacket$action) {
         case PERFORM_RESPAWN:
            if (this.f_9743_.f_8944_) {
               this.f_9743_.f_8944_ = false;
               this.f_9743_ = this.f_9745_.m_6846_().m_11236_(this.f_9743_, true);
               CriteriaTriggers.f_10588_.m_19757_(this.f_9743_, Level.f_46430_, Level.f_46428_);
            } else {
               if (this.f_9743_.m_21223_() > 0.0F) {
                  return;
               }

               this.f_9743_ = this.f_9745_.m_6846_().m_11236_(this.f_9743_, false);
               if (this.f_9745_.m_7035_()) {
                  this.f_9743_.m_143403_(GameType.SPECTATOR);
                  this.f_9743_.m_9236_().m_46469_().m_46170_(GameRules.f_46146_).m_46246_(false, this.f_9745_);
               }
            }
            break;
         case REQUEST_STATS:
            this.f_9743_.m_8951_().m_12819_(this.f_9743_);
      }

   }

   public void m_7951_(ServerboundContainerClosePacket p_9858_) {
      PacketUtils.m_131359_(p_9858_, this, this.f_9743_.m_284548_());
      this.f_9743_.m_9230_();
   }

   public void m_5914_(ServerboundContainerClickPacket p_9856_) {
      PacketUtils.m_131359_(p_9856_, this, this.f_9743_.m_284548_());
      this.f_9743_.m_9243_();
      if (this.f_9743_.f_36096_.f_38840_ == p_9856_.m_133959_()) {
         if (this.f_9743_.m_5833_()) {
            this.f_9743_.f_36096_.m_150429_();
         } else if (!this.f_9743_.f_36096_.m_6875_(this.f_9743_)) {
            f_9744_.debug("Player {} interacted with invalid menu {}", this.f_9743_, this.f_9743_.f_36096_);
         } else {
            int i = p_9856_.m_133962_();
            if (!this.f_9743_.f_36096_.m_207775_(i)) {
               f_9744_.debug("Player {} clicked invalid slot index: {}, available slots: {}", this.f_9743_.m_7755_(), i, this.f_9743_.f_36096_.f_38839_.size());
            } else {
               boolean flag = p_9856_.m_182741_() != this.f_9743_.f_36096_.m_182424_();
               this.f_9743_.f_36096_.m_150443_();
               this.f_9743_.f_36096_.m_150399_(i, p_9856_.m_133963_(), p_9856_.m_133966_(), this.f_9743_);

               for(Int2ObjectMap.Entry<ItemStack> entry : Int2ObjectMaps.fastIterable(p_9856_.m_179582_())) {
                  this.f_9743_.f_36096_.m_182414_(entry.getIntKey(), entry.getValue());
               }

               this.f_9743_.f_36096_.m_150422_(p_9856_.m_179581_());
               this.f_9743_.f_36096_.m_150444_();
               if (flag) {
                  this.f_9743_.f_36096_.m_182423_();
               } else {
                  this.f_9743_.f_36096_.m_38946_();
               }

            }
         }
      }
   }

   public void m_7191_(ServerboundPlaceRecipePacket p_9882_) {
      PacketUtils.m_131359_(p_9882_, this, this.f_9743_.m_284548_());
      this.f_9743_.m_9243_();
      if (!this.f_9743_.m_5833_() && this.f_9743_.f_36096_.f_38840_ == p_9882_.m_134249_() && this.f_9743_.f_36096_ instanceof RecipeBookMenu) {
         if (!this.f_9743_.f_36096_.m_6875_(this.f_9743_)) {
            f_9744_.debug("Player {} interacted with invalid menu {}", this.f_9743_, this.f_9743_.f_36096_);
         } else {
            this.f_9745_.m_129894_().m_44043_(p_9882_.m_134252_()).ifPresent((p_287379_) -> {
               ((RecipeBookMenu)this.f_9743_.f_36096_).m_6951_(p_9882_.m_134253_(), p_287379_, this.f_9743_);
            });
         }
      }
   }

   public void m_6557_(ServerboundContainerButtonClickPacket p_9854_) {
      PacketUtils.m_131359_(p_9854_, this, this.f_9743_.m_284548_());
      this.f_9743_.m_9243_();
      if (this.f_9743_.f_36096_.f_38840_ == p_9854_.m_133935_() && !this.f_9743_.m_5833_()) {
         if (!this.f_9743_.f_36096_.m_6875_(this.f_9743_)) {
            f_9744_.debug("Player {} interacted with invalid menu {}", this.f_9743_, this.f_9743_.f_36096_);
         } else {
            boolean flag = this.f_9743_.f_36096_.m_6366_(this.f_9743_, p_9854_.m_133938_());
            if (flag) {
               this.f_9743_.f_36096_.m_38946_();
            }

         }
      }
   }

   public void m_5964_(ServerboundSetCreativeModeSlotPacket p_9915_) {
      PacketUtils.m_131359_(p_9915_, this, this.f_9743_.m_284548_());
      if (this.f_9743_.f_8941_.m_9295_()) {
         boolean flag = p_9915_.m_134561_() < 0;
         ItemStack itemstack = p_9915_.m_134564_();
         if (!itemstack.m_246617_(this.f_9743_.m_9236_().m_246046_())) {
            return;
         }

         CompoundTag compoundtag = BlockItem.m_186336_(itemstack);
         if (!itemstack.m_41619_() && compoundtag != null && compoundtag.m_128441_("x") && compoundtag.m_128441_("y") && compoundtag.m_128441_("z")) {
            BlockPos blockpos = BlockEntity.m_187472_(compoundtag);
            if (this.f_9743_.m_9236_().m_46749_(blockpos)) {
               BlockEntity blockentity = this.f_9743_.m_9236_().m_7702_(blockpos);
               if (blockentity != null) {
                  blockentity.m_187476_(itemstack);
               }
            }
         }

         boolean flag1 = p_9915_.m_134561_() >= 1 && p_9915_.m_134561_() <= 45;
         boolean flag2 = itemstack.m_41619_() || itemstack.m_41773_() >= 0 && itemstack.m_41613_() <= 64 && !itemstack.m_41619_();
         if (flag1 && flag2) {
            this.f_9743_.f_36095_.m_38853_(p_9915_.m_134561_()).m_269060_(itemstack);
            this.f_9743_.f_36095_.m_38946_();
         } else if (flag && flag2 && this.f_9751_ < 200) {
            this.f_9751_ += 20;
            this.f_9743_.m_36176_(itemstack, true);
         }
      }

   }

   public void m_5527_(ServerboundSignUpdatePacket p_9921_) {
      List<String> list = Stream.of(p_9921_.m_134663_()).map(ChatFormatting::m_126649_).collect(Collectors.toList());
      this.m_243065_(list).thenAcceptAsync((p_215245_) -> {
         this.m_9922_(p_9921_, p_215245_);
      }, this.f_9745_);
   }

   private void m_9922_(ServerboundSignUpdatePacket p_9923_, List<FilteredText> p_9924_) {
      this.f_9743_.m_9243_();
      ServerLevel serverlevel = this.f_9743_.m_284548_();
      BlockPos blockpos = p_9923_.m_134660_();
      if (serverlevel.m_46805_(blockpos)) {
         BlockEntity blockentity = serverlevel.m_7702_(blockpos);
         if (!(blockentity instanceof SignBlockEntity)) {
            return;
         }

         SignBlockEntity signblockentity = (SignBlockEntity)blockentity;
         signblockentity.m_277134_(this.f_9743_, p_9923_.m_276788_(), p_9924_);
      }

   }

   public void m_5683_(ServerboundKeepAlivePacket p_9870_) {
      if (this.f_9748_ && p_9870_.m_134102_() == this.f_9749_) {
         int i = (int)(Util.m_137550_() - this.f_9747_);
         this.f_9743_.f_8943_ = (this.f_9743_.f_8943_ * 3 + i) / 4;
         this.f_9748_ = false;
      } else if (!this.m_9956_()) {
         this.m_9942_(Component.m_237115_("disconnect.timeout"));
      }

   }

   public void m_6828_(ServerboundPlayerAbilitiesPacket p_9887_) {
      PacketUtils.m_131359_(p_9887_, this, this.f_9743_.m_284548_());
      this.f_9743_.m_150110_().f_35935_ = p_9887_.m_134264_() && this.f_9743_.m_150110_().f_35936_;
   }

   public void m_5617_(ServerboundClientInformationPacket p_9845_) {
      PacketUtils.m_131359_(p_9845_, this, this.f_9743_.m_284548_());
      this.f_9743_.m_9156_(p_9845_);
   }

   public void m_7423_(ServerboundCustomPayloadPacket p_9860_) {
      net.minecraftforge.network.NetworkHooks.onCustomPayload(p_9860_, this.f_9742_);
   }

   public void m_7477_(ServerboundChangeDifficultyPacket p_9839_) {
      PacketUtils.m_131359_(p_9839_, this, this.f_9743_.m_284548_());
      if (this.f_9743_.m_20310_(2) || this.m_9956_()) {
         this.f_9745_.m_129827_(p_9839_.m_133824_(), false);
      }
   }

   public void m_7728_(ServerboundLockDifficultyPacket p_9872_) {
      PacketUtils.m_131359_(p_9872_, this, this.f_9743_.m_284548_());
      if (this.f_9743_.m_20310_(2) || this.m_9956_()) {
         this.f_9745_.m_129958_(p_9872_.m_134115_());
      }
   }

   public void m_252797_(ServerboundChatSessionUpdatePacket p_253950_) {
      PacketUtils.m_131359_(p_253950_, this, this.f_9743_.m_284548_());
      RemoteChatSession.Data remotechatsession$data = p_253950_.f_252446_();
      ProfilePublicKey.Data profilepublickey$data = this.f_252494_ != null ? this.f_252494_.f_243855_().f_219781_() : null;
      ProfilePublicKey.Data profilepublickey$data1 = remotechatsession$data.f_243937_();
      if (!Objects.equals(profilepublickey$data, profilepublickey$data1)) {
         if (profilepublickey$data != null && profilepublickey$data1.f_219799_().isBefore(profilepublickey$data.f_219799_())) {
            this.m_9942_(ProfilePublicKey.f_243346_);
         } else {
            try {
               SignatureValidator signaturevalidator = this.f_9745_.m_284385_();
               if (signaturevalidator == null) {
                  f_9744_.warn("Ignoring chat session from {} due to missing Services public key", (Object)this.f_9743_.m_36316_().getName());
                  return;
               }

               this.m_253005_(remotechatsession$data.m_247588_(this.f_9743_.m_36316_(), signaturevalidator, Duration.ZERO));
            } catch (ProfilePublicKey.ValidationException profilepublickey$validationexception) {
               f_9744_.error("Failed to validate profile key: {}", (Object)profilepublickey$validationexception.getMessage());
               this.m_9942_(profilepublickey$validationexception.m_237308_());
            }

         }
      }
   }

   private void m_253005_(RemoteChatSession p_253823_) {
      this.f_252494_ = p_253823_;
      this.f_240889_ = p_253823_.m_245959_(this.f_9743_.m_20148_());
      this.f_241681_.m_241849_((p_253488_) -> {
         this.f_9743_.m_252981_(p_253823_);
         this.f_9745_.m_6846_().m_11268_(new ClientboundPlayerInfoUpdatePacket(EnumSet.of(ClientboundPlayerInfoUpdatePacket.Action.INITIALIZE_CHAT), List.of(this.f_9743_)));
         return CompletableFuture.completedFuture((Object)null);
      });
   }

   public ServerPlayer m_142253_() {
      return this.f_9743_;
   }

   @FunctionalInterface
   interface EntityInteraction {
      InteractionResult m_143694_(ServerPlayer p_143695_, Entity p_143696_, InteractionHand p_143697_);
   }
}
