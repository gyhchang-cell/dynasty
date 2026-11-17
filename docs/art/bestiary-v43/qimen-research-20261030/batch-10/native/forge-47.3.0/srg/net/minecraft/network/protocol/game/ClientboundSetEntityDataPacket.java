package net.minecraft.network.protocol.game;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.syncher.SynchedEntityData;

public record ClientboundSetEntityDataPacket(int f_133143_, List<SynchedEntityData.DataValue<?>> f_133144_) implements Packet<ClientGamePacketListener> {
   public static final int f_252513_ = 255;

   public ClientboundSetEntityDataPacket(FriendlyByteBuf p_179290_) {
      this(p_179290_.m_130242_(), m_252908_(p_179290_));
   }

   private static void m_252763_(List<SynchedEntityData.DataValue<?>> p_253940_, FriendlyByteBuf p_253901_) {
      for(SynchedEntityData.DataValue<?> datavalue : p_253940_) {
         datavalue.m_252897_(p_253901_);
      }

      p_253901_.writeByte(255);
   }

   private static List<SynchedEntityData.DataValue<?>> m_252908_(FriendlyByteBuf p_253726_) {
      List<SynchedEntityData.DataValue<?>> list = new ArrayList<>();

      int i;
      while((i = p_253726_.readUnsignedByte()) != 255) {
         list.add(SynchedEntityData.DataValue.m_252860_(p_253726_, i));
      }

      return list;
   }

   public void m_5779_(FriendlyByteBuf p_133158_) {
      p_133158_.m_130130_(this.f_133143_);
      m_252763_(this.f_133144_, p_133158_);
   }

   public void m_5797_(ClientGamePacketListener p_133155_) {
      p_133155_.m_6455_(this);
   }
}
