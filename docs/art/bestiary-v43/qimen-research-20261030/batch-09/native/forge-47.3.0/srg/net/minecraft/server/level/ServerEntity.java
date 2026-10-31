package net.minecraft.server.level;

import com.google.common.collect.Lists;
import com.mojang.datafixers.util.Pair;
import com.mojang.logging.LogUtils;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.function.Consumer;
import java.util.stream.Stream;
import javax.annotation.Nullable;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBundlePacket;
import net.minecraft.network.protocol.game.ClientboundMoveEntityPacket;
import net.minecraft.network.protocol.game.ClientboundRemoveEntitiesPacket;
import net.minecraft.network.protocol.game.ClientboundRotateHeadPacket;
import net.minecraft.network.protocol.game.ClientboundSetEntityDataPacket;
import net.minecraft.network.protocol.game.ClientboundSetEntityLinkPacket;
import net.minecraft.network.protocol.game.ClientboundSetEntityMotionPacket;
import net.minecraft.network.protocol.game.ClientboundSetEquipmentPacket;
import net.minecraft.network.protocol.game.ClientboundSetPassengersPacket;
import net.minecraft.network.protocol.game.ClientboundTeleportEntityPacket;
import net.minecraft.network.protocol.game.ClientboundUpdateAttributesPacket;
import net.minecraft.network.protocol.game.VecDeltaCodec;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.decoration.ItemFrame;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.MapItem;
import net.minecraft.world.level.saveddata.maps.MapItemSavedData;
import net.minecraft.world.phys.Vec3;
import org.slf4j.Logger;

public class ServerEntity {
   private static final Logger f_8508_ = LogUtils.getLogger();
   private static final int f_143241_ = 1;
   private final ServerLevel f_8509_;
   private final Entity f_8510_;
   private final int f_8511_;
   private final boolean f_8512_;
   private final Consumer<Packet<?>> f_8513_;
   private final VecDeltaCodec f_214995_ = new VecDeltaCodec();
   private int f_8517_;
   private int f_8518_;
   private int f_8519_;
   private Vec3 f_8520_ = Vec3.f_82478_;
   private int f_8521_;
   private int f_8522_;
   private List<Entity> f_8523_ = Collections.emptyList();
   private boolean f_8524_;
   private boolean f_8525_;
   @Nullable
   private List<SynchedEntityData.DataValue<?>> f_263120_;

   public ServerEntity(ServerLevel p_8528_, Entity p_8529_, int p_8530_, boolean p_8531_, Consumer<Packet<?>> p_8532_) {
      this.f_8509_ = p_8528_;
      this.f_8513_ = p_8532_;
      this.f_8510_ = p_8529_;
      this.f_8511_ = p_8530_;
      this.f_8512_ = p_8531_;
      this.f_214995_.m_238033_(p_8529_.m_213870_());
      this.f_8517_ = Mth.m_14143_(p_8529_.m_146908_() * 256.0F / 360.0F);
      this.f_8518_ = Mth.m_14143_(p_8529_.m_146909_() * 256.0F / 360.0F);
      this.f_8519_ = Mth.m_14143_(p_8529_.m_6080_() * 256.0F / 360.0F);
      this.f_8525_ = p_8529_.m_20096_();
      this.f_263120_ = p_8529_.m_20088_().m_252804_();
   }

   public void m_8533_() {
      List<Entity> list = this.f_8510_.m_20197_();
      if (!list.equals(this.f_8523_)) {
         this.f_8513_.accept(new ClientboundSetPassengersPacket(this.f_8510_));
         m_277180_(list, this.f_8523_).forEach((p_289307_) -> {
            if (p_289307_ instanceof ServerPlayer serverplayer1) {
               serverplayer1.f_8906_.m_9774_(serverplayer1.m_20185_(), serverplayer1.m_20186_(), serverplayer1.m_20189_(), serverplayer1.m_146908_(), serverplayer1.m_146909_());
            }

         });
         this.f_8523_ = list;
      }

      Entity $$11 = this.f_8510_;
      if ($$11 instanceof ItemFrame itemframe) {
         if (this.f_8521_ % 10 == 0) {
            ItemStack itemstack = itemframe.m_31822_();
         Integer integer = MapItem.m_151131_(itemstack);
         MapItemSavedData mapitemsaveddata = MapItem.m_42853_(itemstack, this.f_8509_);
         if (mapitemsaveddata != null) {
                  for(ServerPlayer serverplayer : this.f_8509_.m_6907_()) {
                     mapitemsaveddata.m_77918_(serverplayer, itemstack);
                     Packet<?> packet = mapitemsaveddata.m_164796_(integer, serverplayer);
                     if (packet != null) {
                        serverplayer.f_8906_.m_9829_(packet);
                     }
                  }
               }

            this.m_8543_();
         }
      }



      if (this.f_8521_ % this.f_8511_ == 0 || this.f_8510_.f_19812_ || this.f_8510_.m_20088_().m_135352_()) {
         if (this.f_8510_.m_20159_()) {
            int i1 = Mth.m_14143_(this.f_8510_.m_146908_() * 256.0F / 360.0F);
            int l1 = Mth.m_14143_(this.f_8510_.m_146909_() * 256.0F / 360.0F);
            boolean flag3 = Math.abs(i1 - this.f_8517_) >= 1 || Math.abs(l1 - this.f_8518_) >= 1;
            if (flag3) {
               this.f_8513_.accept(new ClientboundMoveEntityPacket.Rot(this.f_8510_.m_19879_(), (byte)i1, (byte)l1, this.f_8510_.m_20096_()));
               this.f_8517_ = i1;
               this.f_8518_ = l1;
            }

            this.f_214995_.m_238033_(this.f_8510_.m_213870_());
            this.m_8543_();
            this.f_8524_ = true;
         } else {
            ++this.f_8522_;
            int l = Mth.m_14143_(this.f_8510_.m_146908_() * 256.0F / 360.0F);
            int k1 = Mth.m_14143_(this.f_8510_.m_146909_() * 256.0F / 360.0F);
            Vec3 vec3 = this.f_8510_.m_213870_();
            boolean flag4 = this.f_214995_.m_238031_(vec3).m_82556_() >= (double)7.6293945E-6F;
            Packet<?> packet1 = null;
            boolean flag5 = flag4 || this.f_8521_ % 60 == 0;
            boolean flag6 = Math.abs(l - this.f_8517_) >= 1 || Math.abs(k1 - this.f_8518_) >= 1;
            boolean flag = false;
            boolean flag1 = false;
            if (this.f_8521_ > 0 || this.f_8510_ instanceof AbstractArrow) {
               long i = this.f_214995_.m_238025_(vec3);
               long j = this.f_214995_.m_238027_(vec3);
               long k = this.f_214995_.m_238029_(vec3);
               boolean flag2 = i < -32768L || i > 32767L || j < -32768L || j > 32767L || k < -32768L || k > 32767L;
               if (!flag2 && this.f_8522_ <= 400 && !this.f_8524_ && this.f_8525_ == this.f_8510_.m_20096_()) {
                  if ((!flag5 || !flag6) && !(this.f_8510_ instanceof AbstractArrow)) {
                     if (flag5) {
                        packet1 = new ClientboundMoveEntityPacket.Pos(this.f_8510_.m_19879_(), (short)((int)i), (short)((int)j), (short)((int)k), this.f_8510_.m_20096_());
                        flag = true;
                     } else if (flag6) {
                        packet1 = new ClientboundMoveEntityPacket.Rot(this.f_8510_.m_19879_(), (byte)l, (byte)k1, this.f_8510_.m_20096_());
                        flag1 = true;
                     }
                  } else {
                     packet1 = new ClientboundMoveEntityPacket.PosRot(this.f_8510_.m_19879_(), (short)((int)i), (short)((int)j), (short)((int)k), (byte)l, (byte)k1, this.f_8510_.m_20096_());
                     flag = true;
                     flag1 = true;
                  }
               } else {
                  this.f_8525_ = this.f_8510_.m_20096_();
                  this.f_8522_ = 0;
                  packet1 = new ClientboundTeleportEntityPacket(this.f_8510_);
                  flag = true;
                  flag1 = true;
               }
            }

            if ((this.f_8512_ || this.f_8510_.f_19812_ || this.f_8510_ instanceof LivingEntity && ((LivingEntity)this.f_8510_).m_21255_()) && this.f_8521_ > 0) {
               Vec3 vec31 = this.f_8510_.m_20184_();
               double d0 = vec31.m_82557_(this.f_8520_);
               if (d0 > 1.0E-7D || d0 > 0.0D && vec31.m_82556_() == 0.0D) {
                  this.f_8520_ = vec31;
                  this.f_8513_.accept(new ClientboundSetEntityMotionPacket(this.f_8510_.m_19879_(), this.f_8520_));
               }
            }

            if (packet1 != null) {
               this.f_8513_.accept(packet1);
            }

            this.m_8543_();
            if (flag) {
               this.f_214995_.m_238033_(vec3);
            }

            if (flag1) {
               this.f_8517_ = l;
               this.f_8518_ = k1;
            }

            this.f_8524_ = false;
         }

         int j1 = Mth.m_14143_(this.f_8510_.m_6080_() * 256.0F / 360.0F);
         if (Math.abs(j1 - this.f_8519_) >= 1) {
            this.f_8513_.accept(new ClientboundRotateHeadPacket(this.f_8510_, (byte)j1));
            this.f_8519_ = j1;
         }

         this.f_8510_.f_19812_ = false;
      }

      ++this.f_8521_;
      if (this.f_8510_.f_19864_) {
         this.m_8538_(new ClientboundSetEntityMotionPacket(this.f_8510_));
         this.f_8510_.f_19864_ = false;
      }

   }

   private static Stream<Entity> m_277180_(List<Entity> p_277592_, List<Entity> p_277658_) {
      return p_277658_.stream().filter((p_275361_) -> {
         return !p_277592_.contains(p_275361_);
      });
   }

   public void m_8534_(ServerPlayer p_8535_) {
      this.f_8510_.m_6452_(p_8535_);
      p_8535_.f_8906_.m_9829_(new ClientboundRemoveEntitiesPacket(this.f_8510_.m_19879_()));
      net.minecraftforge.event.ForgeEventFactory.onStopEntityTracking(this.f_8510_, p_8535_);
   }

   public void m_8541_(ServerPlayer p_8542_) {
      List<Packet<ClientGamePacketListener>> list = new ArrayList<>();
      this.m_289200_(p_8542_, list::add);
      p_8542_.f_8906_.m_9829_(new ClientboundBundlePacket(list));
      this.f_8510_.m_6457_(p_8542_);
      net.minecraftforge.event.ForgeEventFactory.onStartEntityTracking(this.f_8510_, p_8542_);
   }

   public void m_289200_(ServerPlayer p_289562_, Consumer<Packet<ClientGamePacketListener>> p_289563_) {
      if (this.f_8510_.m_213877_()) {
         f_8508_.warn("Fetching packet for removed entity {}", (Object)this.f_8510_);
      }

      Packet<ClientGamePacketListener> packet = this.f_8510_.m_5654_();
      this.f_8519_ = Mth.m_14143_(this.f_8510_.m_6080_() * 256.0F / 360.0F);
      p_289563_.accept(packet);
      if (this.f_263120_ != null) {
         p_289563_.accept(new ClientboundSetEntityDataPacket(this.f_8510_.m_19879_(), this.f_263120_));
      }

      boolean flag = this.f_8512_;
      if (this.f_8510_ instanceof LivingEntity) {
         Collection<AttributeInstance> collection = ((LivingEntity)this.f_8510_).m_21204_().m_22170_();
         if (!collection.isEmpty()) {
            p_289563_.accept(new ClientboundUpdateAttributesPacket(this.f_8510_.m_19879_(), collection));
         }

         if (((LivingEntity)this.f_8510_).m_21255_()) {
            flag = true;
         }
      }

      this.f_8520_ = this.f_8510_.m_20184_();
      if (flag && !(this.f_8510_ instanceof LivingEntity)) {
         p_289563_.accept(new ClientboundSetEntityMotionPacket(this.f_8510_.m_19879_(), this.f_8520_));
      }

      if (this.f_8510_ instanceof LivingEntity) {
         List<Pair<EquipmentSlot, ItemStack>> list = Lists.newArrayList();

         for(EquipmentSlot equipmentslot : EquipmentSlot.values()) {
            ItemStack itemstack = ((LivingEntity)this.f_8510_).m_6844_(equipmentslot);
            if (!itemstack.m_41619_()) {
               list.add(Pair.of(equipmentslot, itemstack.m_41777_()));
            }
         }

         if (!list.isEmpty()) {
            p_289563_.accept(new ClientboundSetEquipmentPacket(this.f_8510_.m_19879_(), list));
         }
      }

      if (!this.f_8510_.m_20197_().isEmpty()) {
         p_289563_.accept(new ClientboundSetPassengersPacket(this.f_8510_));
      }

      if (this.f_8510_.m_20159_()) {
         p_289563_.accept(new ClientboundSetPassengersPacket(this.f_8510_.m_20202_()));
      }

      if (this.f_8510_ instanceof Mob) {
         Mob mob = (Mob)this.f_8510_;
         if (mob.m_21523_()) {
            p_289563_.accept(new ClientboundSetEntityLinkPacket(mob, mob.m_21524_()));
         }
      }

   }

   private void m_8543_() {
      SynchedEntityData synchedentitydata = this.f_8510_.m_20088_();
      List<SynchedEntityData.DataValue<?>> list = synchedentitydata.m_135378_();
      if (list != null) {
         this.f_263120_ = synchedentitydata.m_252804_();
         this.m_8538_(new ClientboundSetEntityDataPacket(this.f_8510_.m_19879_(), list));
      }

      if (this.f_8510_ instanceof LivingEntity) {
         Set<AttributeInstance> set = ((LivingEntity)this.f_8510_).m_21204_().m_22145_();
         if (!set.isEmpty()) {
            this.m_8538_(new ClientboundUpdateAttributesPacket(this.f_8510_.m_19879_(), set));
         }

         set.clear();
      }

   }

   private void m_8538_(Packet<?> p_8539_) {
      this.f_8513_.accept(p_8539_);
      if (this.f_8510_ instanceof ServerPlayer) {
         ((ServerPlayer)this.f_8510_).f_8906_.m_9829_(p_8539_);
      }

   }
}
