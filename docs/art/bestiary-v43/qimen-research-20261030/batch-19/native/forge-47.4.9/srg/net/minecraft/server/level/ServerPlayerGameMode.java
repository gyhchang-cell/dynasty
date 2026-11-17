package net.minecraft.server.level;

import com.mojang.logging.LogUtils;
import java.util.Objects;
import javax.annotation.Nullable;
import net.minecraft.advancements.CriteriaTriggers;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.protocol.game.ClientboundBlockUpdatePacket;
import net.minecraft.network.protocol.game.ClientboundPlayerInfoUpdatePacket;
import net.minecraft.network.protocol.game.ServerboundPlayerActionPacket;
import net.minecraft.server.network.ServerGamePacketListenerImpl;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.GameMasterBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import org.slf4j.Logger;

public class ServerPlayerGameMode {
   private static final Logger f_9246_ = LogUtils.getLogger();
   protected ServerLevel f_9244_;
   protected final ServerPlayer f_9245_;
   private GameType f_9247_ = GameType.f_151492_;
   @Nullable
   private GameType f_9248_;
   private boolean f_9249_;
   private int f_9250_;
   private BlockPos f_9251_ = BlockPos.f_121853_;
   private int f_9252_;
   private boolean f_9253_;
   private BlockPos f_9254_ = BlockPos.f_121853_;
   private int f_9255_;
   private int f_9256_ = -1;

   public ServerPlayerGameMode(ServerPlayer p_143472_) {
      this.f_9245_ = p_143472_;
      this.f_9244_ = p_143472_.m_284548_();
   }

   public boolean m_143473_(GameType p_143474_) {
      if (p_143474_ == this.f_9247_) {
         return false;
      } else {
         this.m_9273_(p_143474_, this.f_9248_);
         this.f_9245_.m_6885_();
         this.f_9245_.f_8924_.m_6846_().m_11268_(new ClientboundPlayerInfoUpdatePacket(ClientboundPlayerInfoUpdatePacket.Action.UPDATE_GAME_MODE, this.f_9245_));
         this.f_9244_.m_8878_();
         return true;
      }
   }

   protected void m_9273_(GameType p_9274_, @Nullable GameType p_9275_) {
      this.f_9248_ = p_9275_;
      this.f_9247_ = p_9274_;
      p_9274_.m_46398_(this.f_9245_.m_150110_());
   }

   public GameType m_9290_() {
      return this.f_9247_;
   }

   @Nullable
   public GameType m_9293_() {
      return this.f_9248_;
   }

   public boolean m_9294_() {
      return this.f_9247_.m_46409_();
   }

   public boolean m_9295_() {
      return this.f_9247_.m_46408_();
   }

   public void m_7712_() {
      ++this.f_9252_;
      if (this.f_9253_) {
         BlockState blockstate = this.f_9244_.m_8055_(this.f_9254_);
         if (blockstate.m_60795_()) {
            this.f_9253_ = false;
         } else {
            float f = this.m_9276_(blockstate, this.f_9254_, this.f_9255_);
            if (f >= 1.0F) {
               this.f_9253_ = false;
               this.m_9280_(this.f_9254_);
            }
         }
      } else if (this.f_9249_) {
         BlockState blockstate1 = this.f_9244_.m_8055_(this.f_9251_);
         if (blockstate1.m_60795_()) {
            this.f_9244_.m_6801_(this.f_9245_.m_19879_(), this.f_9251_, -1);
            this.f_9256_ = -1;
            this.f_9249_ = false;
         } else {
            this.m_9276_(blockstate1, this.f_9251_, this.f_9250_);
         }
      }

   }

   private float m_9276_(BlockState p_9277_, BlockPos p_9278_, int p_9279_) {
      int i = this.f_9252_ - p_9279_;
      float f = p_9277_.m_60625_(this.f_9245_, this.f_9245_.m_9236_(), p_9278_) * (float)(i + 1);
      int j = (int)(f * 10.0F);
      if (j != this.f_9256_) {
         this.f_9244_.m_6801_(this.f_9245_.m_19879_(), p_9278_, j);
         this.f_9256_ = j;
      }

      return f;
   }

   private void m_215125_(BlockPos p_215126_, boolean p_215127_, int p_215128_, String p_215129_) {
   }

   public void m_214168_(BlockPos p_215120_, ServerboundPlayerActionPacket.Action p_215121_, Direction p_215122_, int p_215123_, int p_215124_) {
      net.minecraftforge.event.entity.player.PlayerInteractEvent.LeftClickBlock event = net.minecraftforge.common.ForgeHooks.onLeftClickBlock(f_9245_, p_215120_, p_215122_, p_215121_);
      if (event.isCanceled() || (!this.m_9295_() && event.getResult() == net.minecraftforge.eventbus.api.Event.Result.DENY)) {
         return;
      }
      if (!this.f_9245_.canReachRaw(p_215120_, 1.5)) { // Vanilla uses ServerGamePacketListenerImpl.MAX_INTERACTION_DISTANCE which is 6*6, default Block reach is 4.5 so add 1.5 padding
         this.m_215125_(p_215120_, false, p_215124_, "too far");
      } else if (p_215120_.m_123342_() >= p_215123_) {
         this.f_9245_.f_8906_.m_9829_(new ClientboundBlockUpdatePacket(p_215120_, this.f_9244_.m_8055_(p_215120_)));
         this.m_215125_(p_215120_, false, p_215124_, "too high");
      } else {
         if (p_215121_ == ServerboundPlayerActionPacket.Action.START_DESTROY_BLOCK) {
            if (!this.f_9244_.m_7966_(this.f_9245_, p_215120_)) {
               this.f_9245_.f_8906_.m_9829_(new ClientboundBlockUpdatePacket(p_215120_, this.f_9244_.m_8055_(p_215120_)));
               this.m_215125_(p_215120_, false, p_215124_, "may not interact");
               return;
            }

            if (this.m_9295_()) {
               this.m_215116_(p_215120_, p_215124_, "creative destroy");
               return;
            }

            if (this.f_9245_.m_36187_(this.f_9244_, p_215120_, this.f_9247_)) {
               this.f_9245_.f_8906_.m_9829_(new ClientboundBlockUpdatePacket(p_215120_, this.f_9244_.m_8055_(p_215120_)));
               this.m_215125_(p_215120_, false, p_215124_, "block action restricted");
               return;
            }

            this.f_9250_ = this.f_9252_;
            float f = 1.0F;
            BlockState blockstate = this.f_9244_.m_8055_(p_215120_);
            if (!blockstate.m_60795_()) {
               if (event.getUseBlock() != net.minecraftforge.eventbus.api.Event.Result.DENY)
               blockstate.m_60686_(this.f_9244_, p_215120_, this.f_9245_);
               f = blockstate.m_60625_(this.f_9245_, this.f_9245_.m_9236_(), p_215120_);
            }

            if (!blockstate.m_60795_() && f >= 1.0F) {
               this.m_215116_(p_215120_, p_215124_, "insta mine");
            } else {
               if (this.f_9249_) {
                  this.f_9245_.f_8906_.m_9829_(new ClientboundBlockUpdatePacket(this.f_9251_, this.f_9244_.m_8055_(this.f_9251_)));
                  this.m_215125_(p_215120_, false, p_215124_, "abort destroying since another started (client insta mine, server disagreed)");
               }

               this.f_9249_ = true;
               this.f_9251_ = p_215120_.m_7949_();
               int i = (int)(f * 10.0F);
               this.f_9244_.m_6801_(this.f_9245_.m_19879_(), p_215120_, i);
               this.m_215125_(p_215120_, true, p_215124_, "actual start of destroying");
               this.f_9256_ = i;
            }
         } else if (p_215121_ == ServerboundPlayerActionPacket.Action.STOP_DESTROY_BLOCK) {
            if (p_215120_.equals(this.f_9251_)) {
               int j = this.f_9252_ - this.f_9250_;
               BlockState blockstate1 = this.f_9244_.m_8055_(p_215120_);
               if (!blockstate1.m_60795_()) {
                  float f1 = blockstate1.m_60625_(this.f_9245_, this.f_9245_.m_9236_(), p_215120_) * (float)(j + 1);
                  if (f1 >= 0.7F) {
                     this.f_9249_ = false;
                     this.f_9244_.m_6801_(this.f_9245_.m_19879_(), p_215120_, -1);
                     this.m_215116_(p_215120_, p_215124_, "destroyed");
                     return;
                  }

                  if (!this.f_9253_) {
                     this.f_9249_ = false;
                     this.f_9253_ = true;
                     this.f_9254_ = p_215120_;
                     this.f_9255_ = this.f_9250_;
                  }
               }
            }

            this.m_215125_(p_215120_, true, p_215124_, "stopped destroying");
         } else if (p_215121_ == ServerboundPlayerActionPacket.Action.ABORT_DESTROY_BLOCK) {
            this.f_9249_ = false;
            if (!Objects.equals(this.f_9251_, p_215120_)) {
               f_9246_.warn("Mismatch in destroy block pos: {} {}", this.f_9251_, p_215120_);
               this.f_9244_.m_6801_(this.f_9245_.m_19879_(), this.f_9251_, -1);
               this.m_215125_(p_215120_, true, p_215124_, "aborted mismatched destroying");
            }

            this.f_9244_.m_6801_(this.f_9245_.m_19879_(), p_215120_, -1);
            this.m_215125_(p_215120_, true, p_215124_, "aborted destroying");
         }

      }
   }

   public void m_215116_(BlockPos p_215117_, int p_215118_, String p_215119_) {
      if (this.m_9280_(p_215117_)) {
         this.m_215125_(p_215117_, true, p_215118_, p_215119_);
      } else {
         this.f_9245_.f_8906_.m_9829_(new ClientboundBlockUpdatePacket(p_215117_, this.f_9244_.m_8055_(p_215117_)));
         this.m_215125_(p_215117_, false, p_215118_, p_215119_);
      }

   }

   public boolean m_9280_(BlockPos p_9281_) {
      BlockState blockstate = this.f_9244_.m_8055_(p_9281_);
      int exp = net.minecraftforge.common.ForgeHooks.onBlockBreakEvent(f_9244_, f_9247_, f_9245_, p_9281_);
      if (exp == -1) {
         return false;
      } else {
         BlockEntity blockentity = this.f_9244_.m_7702_(p_9281_);
         Block block = blockstate.m_60734_();
         if (block instanceof GameMasterBlock && !this.f_9245_.m_36337_()) {
            this.f_9244_.m_7260_(p_9281_, blockstate, blockstate, 3);
            return false;
         } else if (f_9245_.m_21205_().onBlockStartBreak(p_9281_, f_9245_)) {
            return false;
         } else if (this.f_9245_.m_36187_(this.f_9244_, p_9281_, this.f_9247_)) {
            return false;
         } else {
            if (this.m_9295_()) {
               removeBlock(p_9281_, false);
               return true;
            } else {
               ItemStack itemstack = this.f_9245_.m_21205_();
               ItemStack itemstack1 = itemstack.m_41777_();
               boolean flag1 = blockstate.canHarvestBlock(this.f_9244_, p_9281_, this.f_9245_); // previously player.hasCorrectToolForDrops(blockstate)
               itemstack.m_41686_(this.f_9244_, blockstate, p_9281_, this.f_9245_);
               if (itemstack.m_41619_() && !itemstack1.m_41619_())
                  net.minecraftforge.event.ForgeEventFactory.onPlayerDestroyItem(this.f_9245_, itemstack1, InteractionHand.MAIN_HAND);
               boolean flag = removeBlock(p_9281_, flag1);

               if (flag && flag1) {
                  block.m_6240_(this.f_9244_, this.f_9245_, p_9281_, blockstate, blockentity, itemstack1);
               }

               if (flag && exp > 0)
                  blockstate.m_60734_().m_49805_(f_9244_, p_9281_, exp);

               return true;
            }
         }
      }
   }

   private boolean removeBlock(BlockPos p_180235_1_, boolean canHarvest) {
      BlockState state = this.f_9244_.m_8055_(p_180235_1_);
      boolean removed = state.onDestroyedByPlayer(this.f_9244_, p_180235_1_, this.f_9245_, canHarvest, this.f_9244_.m_6425_(p_180235_1_));
      if (removed)
         state.m_60734_().m_6786_(this.f_9244_, p_180235_1_, state);
      return removed;
   }

   public InteractionResult m_6261_(ServerPlayer p_9262_, Level p_9263_, ItemStack p_9264_, InteractionHand p_9265_) {
      if (this.f_9247_ == GameType.SPECTATOR) {
         return InteractionResult.PASS;
      } else if (p_9262_.m_36335_().m_41519_(p_9264_.m_41720_())) {
         return InteractionResult.PASS;
      } else {
         InteractionResult cancelResult = net.minecraftforge.common.ForgeHooks.onItemRightClick(p_9262_, p_9265_);
         if (cancelResult != null) return cancelResult;
         int i = p_9264_.m_41613_();
         int j = p_9264_.m_41773_();
         InteractionResultHolder<ItemStack> interactionresultholder = p_9264_.m_41682_(p_9263_, p_9262_, p_9265_);
         ItemStack itemstack = interactionresultholder.m_19095_();
         if (itemstack == p_9264_ && itemstack.m_41613_() == i && itemstack.m_41779_() <= 0 && itemstack.m_41773_() == j) {
            return interactionresultholder.m_19089_();
         } else if (interactionresultholder.m_19089_() == InteractionResult.FAIL && itemstack.m_41779_() > 0 && !p_9262_.m_6117_()) {
            return interactionresultholder.m_19089_();
         } else {
            if (p_9264_ != itemstack) {
               p_9262_.m_21008_(p_9265_, itemstack);
            }

            if (this.m_9295_() && itemstack != ItemStack.f_41583_) {
               itemstack.m_41764_(i);
               if (itemstack.m_41763_() && itemstack.m_41773_() != j) {
                  itemstack.m_41721_(j);
               }
            }

            if (itemstack.m_41619_()) {
               p_9262_.m_21008_(p_9265_, ItemStack.f_41583_);
            }

            if (!p_9262_.m_6117_()) {
               p_9262_.f_36095_.m_150429_();
            }

            return interactionresultholder.m_19089_();
         }
      }
   }

   public InteractionResult m_7179_(ServerPlayer p_9266_, Level p_9267_, ItemStack p_9268_, InteractionHand p_9269_, BlockHitResult p_9270_) {
      BlockPos blockpos = p_9270_.m_82425_();
      BlockState blockstate = p_9267_.m_8055_(blockpos);
      if (!blockstate.m_60734_().m_245993_(p_9267_.m_246046_())) {
         return InteractionResult.FAIL;
      }
      net.minecraftforge.event.entity.player.PlayerInteractEvent.RightClickBlock event = net.minecraftforge.common.ForgeHooks.onRightClickBlock(p_9266_, p_9269_, blockpos, p_9270_);
      if (event.isCanceled()) return event.getCancellationResult();
      if (this.f_9247_ == GameType.SPECTATOR) {
         MenuProvider menuprovider = blockstate.m_60750_(p_9267_, blockpos);
         if (menuprovider != null) {
            p_9266_.m_5893_(menuprovider);
            return InteractionResult.SUCCESS;
         } else {
            return InteractionResult.PASS;
         }
      } else {
         UseOnContext useoncontext = new UseOnContext(p_9266_, p_9269_, p_9270_);
         if (event.getUseItem() != net.minecraftforge.eventbus.api.Event.Result.DENY) {
            InteractionResult result = p_9268_.onItemUseFirst(useoncontext);
            if (result != InteractionResult.PASS) return result;
         }
         boolean flag = !p_9266_.m_21205_().m_41619_() || !p_9266_.m_21206_().m_41619_();
         boolean flag1 = (p_9266_.m_36341_() && flag) && !(p_9266_.m_21205_().doesSneakBypassUse(p_9267_, blockpos, p_9266_) && p_9266_.m_21206_().doesSneakBypassUse(p_9267_, blockpos, p_9266_));
         ItemStack itemstack = p_9268_.m_41777_();
         if (event.getUseBlock() == net.minecraftforge.eventbus.api.Event.Result.ALLOW || (event.getUseBlock() != net.minecraftforge.eventbus.api.Event.Result.DENY && !flag1)) {
            InteractionResult interactionresult = blockstate.m_60664_(p_9267_, p_9266_, p_9269_, p_9270_);
            if (interactionresult.m_19077_()) {
               CriteriaTriggers.f_10562_.m_285767_(p_9266_, blockpos, itemstack);
               return interactionresult;
            }
         }

         if (event.getUseItem() == net.minecraftforge.eventbus.api.Event.Result.ALLOW || (!p_9268_.m_41619_() && !p_9266_.m_36335_().m_41519_(p_9268_.m_41720_()))) {
            if (event.getUseItem() == net.minecraftforge.eventbus.api.Event.Result.DENY) return InteractionResult.PASS;
            InteractionResult interactionresult1;
            if (this.m_9295_()) {
               int i = p_9268_.m_41613_();
               interactionresult1 = p_9268_.m_41661_(useoncontext);
               p_9268_.m_41764_(i);
            } else {
               interactionresult1 = p_9268_.m_41661_(useoncontext);
            }

            if (interactionresult1.m_19077_()) {
               CriteriaTriggers.f_10562_.m_285767_(p_9266_, blockpos, itemstack);
            }

            return interactionresult1;
         } else {
            return InteractionResult.PASS;
         }
      }
   }

   public void m_9260_(ServerLevel p_9261_) {
      this.f_9244_ = p_9261_;
   }
}
