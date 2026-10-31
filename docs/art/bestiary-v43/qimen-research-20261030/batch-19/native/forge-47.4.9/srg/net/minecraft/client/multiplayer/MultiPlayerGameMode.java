package net.minecraft.client.multiplayer;

import com.google.common.collect.Lists;
import com.mojang.logging.LogUtils;
import it.unimi.dsi.fastutil.ints.Int2ObjectMap;
import it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap;
import java.util.List;
import javax.annotation.Nullable;
import net.minecraft.client.ClientRecipeBook;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.prediction.BlockStatePredictionHandler;
import net.minecraft.client.multiplayer.prediction.PredictiveAction;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.NonNullList;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ServerGamePacketListener;
import net.minecraft.network.protocol.game.ServerboundContainerButtonClickPacket;
import net.minecraft.network.protocol.game.ServerboundContainerClickPacket;
import net.minecraft.network.protocol.game.ServerboundInteractPacket;
import net.minecraft.network.protocol.game.ServerboundMovePlayerPacket;
import net.minecraft.network.protocol.game.ServerboundPickItemPacket;
import net.minecraft.network.protocol.game.ServerboundPlaceRecipePacket;
import net.minecraft.network.protocol.game.ServerboundPlayerActionPacket;
import net.minecraft.network.protocol.game.ServerboundSetCarriedItemPacket;
import net.minecraft.network.protocol.game.ServerboundSetCreativeModeSlotPacket;
import net.minecraft.network.protocol.game.ServerboundUseItemOnPacket;
import net.minecraft.network.protocol.game.ServerboundUseItemPacket;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.StatsCounter;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.HasCustomInventoryScreen;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ClickType;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.GameMasterBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.apache.commons.lang3.mutable.MutableObject;
import org.slf4j.Logger;

@OnlyIn(Dist.CLIENT)
public class MultiPlayerGameMode {
   private static final Logger f_105188_ = LogUtils.getLogger();
   private final Minecraft f_105189_;
   private final ClientPacketListener f_105190_;
   private BlockPos f_105191_ = new BlockPos(-1, -1, -1);
   private ItemStack f_105192_ = ItemStack.f_41583_;
   private float f_105193_;
   private float f_105194_;
   private int f_105195_;
   private boolean f_105196_;
   private GameType f_105197_ = GameType.f_151492_;
   @Nullable
   private GameType f_105198_;
   private int f_105200_;

   public MultiPlayerGameMode(Minecraft p_105203_, ClientPacketListener p_105204_) {
      this.f_105189_ = p_105203_;
      this.f_105190_ = p_105204_;
   }

   public void m_105221_(Player p_105222_) {
      this.f_105197_.m_46398_(p_105222_.m_150110_());
   }

   public void m_171805_(GameType p_171806_, @Nullable GameType p_171807_) {
      this.f_105197_ = p_171806_;
      this.f_105198_ = p_171807_;
      this.f_105197_.m_46398_(this.f_105189_.f_91074_.m_150110_());
   }

   public void m_105279_(GameType p_105280_) {
      if (p_105280_ != this.f_105197_) {
         this.f_105198_ = this.f_105197_;
      }

      this.f_105197_ = p_105280_;
      this.f_105197_.m_46398_(this.f_105189_.f_91074_.m_150110_());
   }

   public boolean m_105205_() {
      return this.f_105197_.m_46409_();
   }

   public boolean m_105267_(BlockPos p_105268_) {
      if (f_105189_.f_91074_.m_21205_().onBlockStartBreak(p_105268_, f_105189_.f_91074_)) return false;
      if (this.f_105189_.f_91074_.m_36187_(this.f_105189_.f_91073_, p_105268_, this.f_105197_)) {
         return false;
      } else {
         Level level = this.f_105189_.f_91073_;
         BlockState blockstate = level.m_8055_(p_105268_);
         if (!this.f_105189_.f_91074_.m_21205_().m_41720_().m_6777_(blockstate, level, p_105268_, this.f_105189_.f_91074_)) {
            return false;
         } else {
            Block block = blockstate.m_60734_();
            if (block instanceof GameMasterBlock && !this.f_105189_.f_91074_.m_36337_()) {
               return false;
            } else if (blockstate.m_60795_()) {
               return false;
            } else {
               FluidState fluidstate = level.m_6425_(p_105268_);
               boolean flag = blockstate.onDestroyedByPlayer(level, p_105268_, f_105189_.f_91074_, false, fluidstate);
               if (flag) {
                  block.m_6786_(level, p_105268_, blockstate);
               }

               return flag;
            }
         }
      }
   }

   public boolean m_105269_(BlockPos p_105270_, Direction p_105271_) {
      if (this.f_105189_.f_91074_.m_36187_(this.f_105189_.f_91073_, p_105270_, this.f_105197_)) {
         return false;
      } else if (!this.f_105189_.f_91073_.m_6857_().m_61937_(p_105270_)) {
         return false;
      } else {
         if (this.f_105197_.m_46408_()) {
            BlockState blockstate = this.f_105189_.f_91073_.m_8055_(p_105270_);
            this.f_105189_.m_91301_().m_120581_(this.f_105189_.f_91073_, p_105270_, blockstate, 1.0F);
            this.m_233729_(this.f_105189_.f_91073_, (p_233757_) -> {
               if (!net.minecraftforge.common.ForgeHooks.onLeftClickBlock(this.f_105189_.f_91074_, p_105270_, p_105271_, ServerboundPlayerActionPacket.Action.START_DESTROY_BLOCK).isCanceled())
               this.m_105267_(p_105270_);
               return new ServerboundPlayerActionPacket(ServerboundPlayerActionPacket.Action.START_DESTROY_BLOCK, p_105270_, p_105271_, p_233757_);
            });
            this.f_105195_ = 5;
         } else if (!this.f_105196_ || !this.m_105281_(p_105270_)) {
            if (this.f_105196_) {
               this.f_105190_.m_104955_(new ServerboundPlayerActionPacket(ServerboundPlayerActionPacket.Action.ABORT_DESTROY_BLOCK, this.f_105191_, p_105271_));
            }
            net.minecraftforge.event.entity.player.PlayerInteractEvent.LeftClickBlock event = net.minecraftforge.common.ForgeHooks.onLeftClickBlock(this.f_105189_.f_91074_, p_105270_, p_105271_, ServerboundPlayerActionPacket.Action.START_DESTROY_BLOCK);

            BlockState blockstate1 = this.f_105189_.f_91073_.m_8055_(p_105270_);
            this.f_105189_.m_91301_().m_120581_(this.f_105189_.f_91073_, p_105270_, blockstate1, 0.0F);
            this.m_233729_(this.f_105189_.f_91073_, (p_233728_) -> {
               boolean flag = !blockstate1.m_60795_();
               if (flag && this.f_105193_ == 0.0F) {
                  if (event.getUseBlock() != net.minecraftforge.eventbus.api.Event.Result.DENY)
                  blockstate1.m_60686_(this.f_105189_.f_91073_, p_105270_, this.f_105189_.f_91074_);
               }

               ServerboundPlayerActionPacket packet = new ServerboundPlayerActionPacket(ServerboundPlayerActionPacket.Action.START_DESTROY_BLOCK, p_105270_, p_105271_, p_233728_);
               if (event.getUseItem() == net.minecraftforge.eventbus.api.Event.Result.DENY) return packet;
               if (flag && blockstate1.m_60625_(this.f_105189_.f_91074_, this.f_105189_.f_91074_.m_9236_(), p_105270_) >= 1.0F) {
                  this.m_105267_(p_105270_);
               } else {
                  this.f_105196_ = true;
                  this.f_105191_ = p_105270_;
                  this.f_105192_ = this.f_105189_.f_91074_.m_21205_();
                  this.f_105193_ = 0.0F;
                  this.f_105194_ = 0.0F;
                  this.f_105189_.f_91073_.m_6801_(this.f_105189_.f_91074_.m_19879_(), this.f_105191_, this.m_287167_());
               }

               return packet;
            });
         }

         return true;
      }
   }

   public void m_105276_() {
      if (this.f_105196_) {
         BlockState blockstate = this.f_105189_.f_91073_.m_8055_(this.f_105191_);
         this.f_105189_.m_91301_().m_120581_(this.f_105189_.f_91073_, this.f_105191_, blockstate, -1.0F);
         this.f_105190_.m_104955_(new ServerboundPlayerActionPacket(ServerboundPlayerActionPacket.Action.ABORT_DESTROY_BLOCK, this.f_105191_, Direction.DOWN));
         this.f_105196_ = false;
         this.f_105193_ = 0.0F;
         this.f_105189_.f_91073_.m_6801_(this.f_105189_.f_91074_.m_19879_(), this.f_105191_, -1);
         this.f_105189_.f_91074_.m_36334_();
      }

   }

   public boolean m_105283_(BlockPos p_105284_, Direction p_105285_) {
      this.m_105297_();
      if (this.f_105195_ > 0) {
         --this.f_105195_;
         return true;
      } else if (this.f_105197_.m_46408_() && this.f_105189_.f_91073_.m_6857_().m_61937_(p_105284_)) {
         this.f_105195_ = 5;
         BlockState blockstate1 = this.f_105189_.f_91073_.m_8055_(p_105284_);
         this.f_105189_.m_91301_().m_120581_(this.f_105189_.f_91073_, p_105284_, blockstate1, 1.0F);
         this.m_233729_(this.f_105189_.f_91073_, (p_233753_) -> {
            if (!net.minecraftforge.common.ForgeHooks.onLeftClickBlock(this.f_105189_.f_91074_, p_105284_, p_105285_, ServerboundPlayerActionPacket.Action.START_DESTROY_BLOCK).isCanceled())
            this.m_105267_(p_105284_);
            return new ServerboundPlayerActionPacket(ServerboundPlayerActionPacket.Action.START_DESTROY_BLOCK, p_105284_, p_105285_, p_233753_);
         });
         return true;
      } else if (this.m_105281_(p_105284_)) {
         BlockState blockstate = this.f_105189_.f_91073_.m_8055_(p_105284_);
         if (blockstate.m_60795_()) {
            this.f_105196_ = false;
            return false;
         } else {
            this.f_105193_ += blockstate.m_60625_(this.f_105189_.f_91074_, this.f_105189_.f_91074_.m_9236_(), p_105284_);
            if (this.f_105194_ % 4.0F == 0.0F) {
               SoundType soundtype = blockstate.getSoundType(this.f_105189_.f_91073_, p_105284_, this.f_105189_.f_91074_);
               this.f_105189_.m_91106_().m_120367_(new SimpleSoundInstance(soundtype.m_56778_(), SoundSource.BLOCKS, (soundtype.m_56773_() + 1.0F) / 8.0F, soundtype.m_56774_() * 0.5F, SoundInstance.m_235150_(), p_105284_));
            }

            ++this.f_105194_;
            this.f_105189_.m_91301_().m_120581_(this.f_105189_.f_91073_, p_105284_, blockstate, Mth.m_14036_(this.f_105193_, 0.0F, 1.0F));
            if (net.minecraftforge.common.ForgeHooks.onClientMineHold(this.f_105189_.f_91074_, p_105284_, p_105285_).getUseItem() == net.minecraftforge.eventbus.api.Event.Result.DENY) return true;
            if (this.f_105193_ >= 1.0F) {
               this.f_105196_ = false;
               this.m_233729_(this.f_105189_.f_91073_, (p_233739_) -> {
                  this.m_105267_(p_105284_);
                  return new ServerboundPlayerActionPacket(ServerboundPlayerActionPacket.Action.STOP_DESTROY_BLOCK, p_105284_, p_105285_, p_233739_);
               });
               this.f_105193_ = 0.0F;
               this.f_105194_ = 0.0F;
               this.f_105195_ = 5;
            }

            this.f_105189_.f_91073_.m_6801_(this.f_105189_.f_91074_.m_19879_(), this.f_105191_, this.m_287167_());
            return true;
         }
      } else {
         return this.m_105269_(p_105284_, p_105285_);
      }
   }

   private void m_233729_(ClientLevel p_233730_, PredictiveAction p_233731_) {
      try (BlockStatePredictionHandler blockstatepredictionhandler = p_233730_.m_233601_().m_233855_()) {
         int i = blockstatepredictionhandler.m_233871_();
         Packet<ServerGamePacketListener> packet = p_233731_.m_233885_(i);
         this.f_105190_.m_104955_(packet);
      }

   }

   public float m_105286_() {
      return (float) this.f_105189_.f_91074_.getBlockReach();
   }

   public void m_105287_() {
      this.m_105297_();
      if (this.f_105190_.m_104910_().m_129536_()) {
         this.f_105190_.m_104910_().m_129483_();
      } else {
         this.f_105190_.m_104910_().m_129541_();
      }

   }

   private boolean m_105281_(BlockPos p_105282_) {
      ItemStack itemstack = this.f_105189_.f_91074_.m_21205_();
      // FORGE: Remove this method call, but keep the bytecode intact for hacks that target it
      if (Boolean.FALSE)
         ItemStack.m_150942_(itemstack, this.f_105192_);
      return p_105282_.equals(this.f_105191_) && !f_105192_.shouldCauseBlockBreakReset(itemstack);
   }

   private void m_105297_() {
      int i = this.f_105189_.f_91074_.m_150109_().f_35977_;
      if (i != this.f_105200_) {
         this.f_105200_ = i;
         this.f_105190_.m_104955_(new ServerboundSetCarriedItemPacket(this.f_105200_));
      }

   }

   public InteractionResult m_233732_(LocalPlayer p_233733_, InteractionHand p_233734_, BlockHitResult p_233735_) {
      this.m_105297_();
      if (!this.f_105189_.f_91073_.m_6857_().m_61937_(p_233735_.m_82425_())) {
         return InteractionResult.FAIL;
      } else {
         MutableObject<InteractionResult> mutableobject = new MutableObject<>();
         this.m_233729_(this.f_105189_.f_91073_, (p_233745_) -> {
            mutableobject.setValue(this.m_233746_(p_233733_, p_233734_, p_233735_));
            return new ServerboundUseItemOnPacket(p_233734_, p_233735_, p_233745_);
         });
         return mutableobject.getValue();
      }
   }

   private InteractionResult m_233746_(LocalPlayer p_233747_, InteractionHand p_233748_, BlockHitResult p_233749_) {
      BlockPos blockpos = p_233749_.m_82425_();
      ItemStack itemstack = p_233747_.m_21120_(p_233748_);
      net.minecraftforge.event.entity.player.PlayerInteractEvent.RightClickBlock event = net.minecraftforge.common.ForgeHooks.onRightClickBlock(p_233747_, p_233748_, blockpos, p_233749_);
      if (event.isCanceled()) {
         return event.getCancellationResult();
      }
      if (this.f_105197_ == GameType.SPECTATOR) {
         return InteractionResult.SUCCESS;
      } else {
         UseOnContext useoncontext = new UseOnContext(p_233747_, p_233748_, p_233749_);
         if (event.getUseItem() != net.minecraftforge.eventbus.api.Event.Result.DENY) {
            InteractionResult result = itemstack.onItemUseFirst(useoncontext);
            if (result != InteractionResult.PASS) {
               return result;
            }
         }
         boolean flag = !p_233747_.m_21205_().doesSneakBypassUse(p_233747_.m_9236_(), blockpos, p_233747_) || !p_233747_.m_21206_().doesSneakBypassUse(p_233747_.m_9236_(), blockpos, p_233747_);
         boolean flag1 = p_233747_.m_36341_() && flag;
            BlockState blockstate = this.f_105189_.f_91073_.m_8055_(blockpos);
            if (!this.f_105190_.m_246351_(blockstate.m_60734_().m_245183_())) {
               return InteractionResult.FAIL;
            }

         if (event.getUseBlock() == net.minecraftforge.eventbus.api.Event.Result.ALLOW || (event.getUseBlock() != net.minecraftforge.eventbus.api.Event.Result.DENY && !flag1)) {
            InteractionResult interactionresult = blockstate.m_60664_(this.f_105189_.f_91073_, p_233747_, p_233748_, p_233749_);
            if (interactionresult.m_19077_()) {
               return interactionresult;
            }
         }

         if (event.getUseItem() == net.minecraftforge.eventbus.api.Event.Result.DENY) {
            return InteractionResult.PASS;
         }
         if (event.getUseItem() == net.minecraftforge.eventbus.api.Event.Result.ALLOW || (!itemstack.m_41619_() && !p_233747_.m_36335_().m_41519_(itemstack.m_41720_()))) {
            InteractionResult interactionresult1;
            if (this.f_105197_.m_46408_()) {
               int i = itemstack.m_41613_();
               interactionresult1 = itemstack.m_41661_(useoncontext);
               itemstack.m_41764_(i);
            } else {
               interactionresult1 = itemstack.m_41661_(useoncontext);
            }

            return interactionresult1;
         } else {
            return InteractionResult.PASS;
         }
      }
   }

   public InteractionResult m_233721_(Player p_233722_, InteractionHand p_233723_) {
      if (this.f_105197_ == GameType.SPECTATOR) {
         return InteractionResult.PASS;
      } else {
         this.m_105297_();
         this.f_105190_.m_104955_(new ServerboundMovePlayerPacket.PosRot(p_233722_.m_20185_(), p_233722_.m_20186_(), p_233722_.m_20189_(), p_233722_.m_146908_(), p_233722_.m_146909_(), p_233722_.m_20096_()));
         MutableObject<InteractionResult> mutableobject = new MutableObject<>();
         this.m_233729_(this.f_105189_.f_91073_, (p_233720_) -> {
            ServerboundUseItemPacket serverbounduseitempacket = new ServerboundUseItemPacket(p_233723_, p_233720_);
            ItemStack itemstack = p_233722_.m_21120_(p_233723_);
            if (p_233722_.m_36335_().m_41519_(itemstack.m_41720_())) {
               mutableobject.setValue(InteractionResult.PASS);
               return serverbounduseitempacket;
            } else {
               InteractionResult cancelResult = net.minecraftforge.common.ForgeHooks.onItemRightClick(p_233722_, p_233723_);
               if (cancelResult != null) {
                  mutableobject.setValue(cancelResult);
                  return serverbounduseitempacket;
               }
               InteractionResultHolder<ItemStack> interactionresultholder = itemstack.m_41682_(this.f_105189_.f_91073_, p_233722_, p_233723_);
               ItemStack itemstack1 = interactionresultholder.m_19095_();
               if (itemstack1 != itemstack) {
                  p_233722_.m_21008_(p_233723_, itemstack1);
                  if (itemstack1.m_41619_())
                     net.minecraftforge.event.ForgeEventFactory.onPlayerDestroyItem(p_233722_, itemstack, p_233723_);
               }

               mutableobject.setValue(interactionresultholder.m_19089_());
               return serverbounduseitempacket;
            }
         });
         return mutableobject.getValue();
      }
   }

   public LocalPlayer m_105246_(ClientLevel p_105247_, StatsCounter p_105248_, ClientRecipeBook p_105249_) {
      return this.m_105250_(p_105247_, p_105248_, p_105249_, false, false);
   }

   public LocalPlayer m_105250_(ClientLevel p_105251_, StatsCounter p_105252_, ClientRecipeBook p_105253_, boolean p_105254_, boolean p_105255_) {
      return new LocalPlayer(this.f_105189_, p_105251_, this.f_105190_, p_105252_, p_105253_, p_105254_, p_105255_);
   }

   public void m_105223_(Player p_105224_, Entity p_105225_) {
      this.m_105297_();
      this.f_105190_.m_104955_(ServerboundInteractPacket.m_179605_(p_105225_, p_105224_.m_6144_()));
      if (this.f_105197_ != GameType.SPECTATOR) {
         p_105224_.m_5706_(p_105225_);
         p_105224_.m_36334_();
      }

   }

   public InteractionResult m_105226_(Player p_105227_, Entity p_105228_, InteractionHand p_105229_) {
      this.m_105297_();
      this.f_105190_.m_104955_(ServerboundInteractPacket.m_179608_(p_105228_, p_105227_.m_6144_(), p_105229_));
      return this.f_105197_ == GameType.SPECTATOR ? InteractionResult.PASS : p_105227_.m_36157_(p_105228_, p_105229_);
   }

   public InteractionResult m_105230_(Player p_105231_, Entity p_105232_, EntityHitResult p_105233_, InteractionHand p_105234_) {
      this.m_105297_();
      Vec3 vec3 = p_105233_.m_82450_().m_82492_(p_105232_.m_20185_(), p_105232_.m_20186_(), p_105232_.m_20189_());
      this.f_105190_.m_104955_(ServerboundInteractPacket.m_179612_(p_105232_, p_105231_.m_6144_(), p_105234_, vec3));
      if (this.f_105197_ == GameType.SPECTATOR) return InteractionResult.PASS; // don't fire for spectators to match non-specific EntityInteract
      InteractionResult cancelResult = net.minecraftforge.common.ForgeHooks.onInteractEntityAt(p_105231_, p_105232_, p_105233_, p_105234_);
      if(cancelResult != null) return cancelResult;
      return this.f_105197_ == GameType.SPECTATOR ? InteractionResult.PASS : p_105232_.m_7111_(p_105231_, vec3, p_105234_);
   }

   public void m_171799_(int p_171800_, int p_171801_, int p_171802_, ClickType p_171803_, Player p_171804_) {
      AbstractContainerMenu abstractcontainermenu = p_171804_.f_36096_;
      if (p_171800_ != abstractcontainermenu.f_38840_) {
         f_105188_.warn("Ignoring click in mismatching container. Click in {}, player has {}.", p_171800_, abstractcontainermenu.f_38840_);
      } else {
         NonNullList<Slot> nonnulllist = abstractcontainermenu.f_38839_;
         int i = nonnulllist.size();
         List<ItemStack> list = Lists.newArrayListWithCapacity(i);

         for(Slot slot : nonnulllist) {
            list.add(slot.m_7993_().m_41777_());
         }

         abstractcontainermenu.m_150399_(p_171801_, p_171802_, p_171803_, p_171804_);
         Int2ObjectMap<ItemStack> int2objectmap = new Int2ObjectOpenHashMap<>();

         for(int j = 0; j < i; ++j) {
            ItemStack itemstack = list.get(j);
            ItemStack itemstack1 = nonnulllist.get(j).m_7993_();
            if (!ItemStack.m_41728_(itemstack, itemstack1)) {
               int2objectmap.put(j, itemstack1.m_41777_());
            }
         }

         this.f_105190_.m_104955_(new ServerboundContainerClickPacket(p_171800_, abstractcontainermenu.m_182424_(), p_171801_, p_171802_, p_171803_, abstractcontainermenu.m_142621_().m_41777_(), int2objectmap));
      }
   }

   public void m_105217_(int p_105218_, Recipe<?> p_105219_, boolean p_105220_) {
      this.f_105190_.m_104955_(new ServerboundPlaceRecipePacket(p_105218_, p_105219_, p_105220_));
   }

   public void m_105208_(int p_105209_, int p_105210_) {
      this.f_105190_.m_104955_(new ServerboundContainerButtonClickPacket(p_105209_, p_105210_));
   }

   public void m_105241_(ItemStack p_105242_, int p_105243_) {
      if (this.f_105197_.m_46408_() && this.f_105190_.m_246351_(p_105242_.m_41720_().m_245183_())) {
         this.f_105190_.m_104955_(new ServerboundSetCreativeModeSlotPacket(p_105243_, p_105242_));
      }

   }

   public void m_105239_(ItemStack p_105240_) {
      if (this.f_105197_.m_46408_() && !p_105240_.m_41619_() && this.f_105190_.m_246351_(p_105240_.m_41720_().m_245183_())) {
         this.f_105190_.m_104955_(new ServerboundSetCreativeModeSlotPacket(-1, p_105240_));
      }

   }

   public void m_105277_(Player p_105278_) {
      this.m_105297_();
      this.f_105190_.m_104955_(new ServerboundPlayerActionPacket(ServerboundPlayerActionPacket.Action.RELEASE_USE_ITEM, BlockPos.f_121853_, Direction.DOWN));
      p_105278_.m_21253_();
   }

   public boolean m_105288_() {
      return this.f_105197_.m_46409_();
   }

   public boolean m_105289_() {
      return !this.f_105197_.m_46408_();
   }

   public boolean m_105290_() {
      return this.f_105197_.m_46408_();
   }

   public boolean m_105291_() {
      return this.f_105197_.m_46408_();
   }

   public boolean m_105292_() {
      return this.f_105189_.f_91074_.m_20159_() && this.f_105189_.f_91074_.m_20202_() instanceof HasCustomInventoryScreen;
   }

   public boolean m_105293_() {
      return this.f_105197_ == GameType.SPECTATOR;
   }

   @Nullable
   public GameType m_105294_() {
      return this.f_105198_;
   }

   public GameType m_105295_() {
      return this.f_105197_;
   }

   public boolean m_105296_() {
      return this.f_105196_;
   }

   public int m_287167_() {
      return this.f_105193_ > 0.0F ? (int)(this.f_105193_ * 10.0F) : -1;
   }

   public void m_105206_(int p_105207_) {
      this.f_105190_.m_104955_(new ServerboundPickItemPacket(p_105207_));
   }
}
