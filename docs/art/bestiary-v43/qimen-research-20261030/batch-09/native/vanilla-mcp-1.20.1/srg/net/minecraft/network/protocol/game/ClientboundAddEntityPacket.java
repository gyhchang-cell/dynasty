package net.minecraft.network.protocol.game;

import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.protocol.Packet;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.phys.Vec3;

public class ClientboundAddEntityPacket implements Packet<ClientGamePacketListener> {
   private static final double f_178559_ = 8000.0D;
   private static final double f_178560_ = 3.9D;
   private final int f_131456_;
   private final UUID f_131457_;
   private final EntityType<?> f_131466_;
   private final double f_131458_;
   private final double f_131459_;
   private final double f_131460_;
   private final int f_131461_;
   private final int f_131462_;
   private final int f_131463_;
   private final byte f_131464_;
   private final byte f_131465_;
   private final byte f_237544_;
   private final int f_131467_;

   public ClientboundAddEntityPacket(Entity p_131481_) {
      this(p_131481_, 0);
   }

   public ClientboundAddEntityPacket(Entity p_131483_, int p_131484_) {
      this(p_131483_.m_19879_(), p_131483_.m_20148_(), p_131483_.m_20185_(), p_131483_.m_20186_(), p_131483_.m_20189_(), p_131483_.m_146909_(), p_131483_.m_146908_(), p_131483_.m_6095_(), p_131484_, p_131483_.m_20184_(), (double)p_131483_.m_6080_());
   }

   public ClientboundAddEntityPacket(Entity p_237558_, int p_237559_, BlockPos p_237560_) {
      this(p_237558_.m_19879_(), p_237558_.m_20148_(), (double)p_237560_.m_123341_(), (double)p_237560_.m_123342_(), (double)p_237560_.m_123343_(), p_237558_.m_146909_(), p_237558_.m_146908_(), p_237558_.m_6095_(), p_237559_, p_237558_.m_20184_(), (double)p_237558_.m_6080_());
   }

   public ClientboundAddEntityPacket(int p_237546_, UUID p_237547_, double p_237548_, double p_237549_, double p_237550_, float p_237551_, float p_237552_, EntityType<?> p_237553_, int p_237554_, Vec3 p_237555_, double p_237556_) {
      this.f_131456_ = p_237546_;
      this.f_131457_ = p_237547_;
      this.f_131458_ = p_237548_;
      this.f_131459_ = p_237549_;
      this.f_131460_ = p_237550_;
      this.f_131464_ = (byte)Mth.m_14143_(p_237551_ * 256.0F / 360.0F);
      this.f_131465_ = (byte)Mth.m_14143_(p_237552_ * 256.0F / 360.0F);
      this.f_237544_ = (byte)Mth.m_14107_(p_237556_ * 256.0D / 360.0D);
      this.f_131466_ = p_237553_;
      this.f_131467_ = p_237554_;
      this.f_131461_ = (int)(Mth.m_14008_(p_237555_.f_82479_, -3.9D, 3.9D) * 8000.0D);
      this.f_131462_ = (int)(Mth.m_14008_(p_237555_.f_82480_, -3.9D, 3.9D) * 8000.0D);
      this.f_131463_ = (int)(Mth.m_14008_(p_237555_.f_82481_, -3.9D, 3.9D) * 8000.0D);
   }

   public ClientboundAddEntityPacket(FriendlyByteBuf p_178562_) {
      this.f_131456_ = p_178562_.m_130242_();
      this.f_131457_ = p_178562_.m_130259_();
      this.f_131466_ = p_178562_.m_236816_(BuiltInRegistries.f_256780_);
      this.f_131458_ = p_178562_.readDouble();
      this.f_131459_ = p_178562_.readDouble();
      this.f_131460_ = p_178562_.readDouble();
      this.f_131464_ = p_178562_.readByte();
      this.f_131465_ = p_178562_.readByte();
      this.f_237544_ = p_178562_.readByte();
      this.f_131467_ = p_178562_.m_130242_();
      this.f_131461_ = p_178562_.readShort();
      this.f_131462_ = p_178562_.readShort();
      this.f_131463_ = p_178562_.readShort();
   }

   public void m_5779_(FriendlyByteBuf p_131498_) {
      p_131498_.m_130130_(this.f_131456_);
      p_131498_.m_130077_(this.f_131457_);
      p_131498_.m_236818_(BuiltInRegistries.f_256780_, this.f_131466_);
      p_131498_.writeDouble(this.f_131458_);
      p_131498_.writeDouble(this.f_131459_);
      p_131498_.writeDouble(this.f_131460_);
      p_131498_.writeByte(this.f_131464_);
      p_131498_.writeByte(this.f_131465_);
      p_131498_.writeByte(this.f_237544_);
      p_131498_.m_130130_(this.f_131467_);
      p_131498_.writeShort(this.f_131461_);
      p_131498_.writeShort(this.f_131462_);
      p_131498_.writeShort(this.f_131463_);
   }

   public void m_5797_(ClientGamePacketListener p_131495_) {
      p_131495_.m_6771_(this);
   }

   public int m_131496_() {
      return this.f_131456_;
   }

   public UUID m_131499_() {
      return this.f_131457_;
   }

   public EntityType<?> m_131508_() {
      return this.f_131466_;
   }

   public double m_131500_() {
      return this.f_131458_;
   }

   public double m_131501_() {
      return this.f_131459_;
   }

   public double m_131502_() {
      return this.f_131460_;
   }

   public double m_131503_() {
      return (double)this.f_131461_ / 8000.0D;
   }

   public double m_131504_() {
      return (double)this.f_131462_ / 8000.0D;
   }

   public double m_131505_() {
      return (double)this.f_131463_ / 8000.0D;
   }

   public float m_237566_() {
      return (float)(this.f_131464_ * 360) / 256.0F;
   }

   public float m_237567_() {
      return (float)(this.f_131465_ * 360) / 256.0F;
   }

   public float m_237568_() {
      return (float)(this.f_237544_ * 360) / 256.0F;
   }

   public int m_131509_() {
      return this.f_131467_;
   }
}
