package net.minecraft.world.damagesource;

import javax.annotation.Nullable;
import net.minecraft.core.Registry;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Fireball;
import net.minecraft.world.entity.projectile.FireworkRocketEntity;
import net.minecraft.world.entity.projectile.WitherSkull;
import net.minecraft.world.level.Explosion;
import net.minecraft.world.phys.Vec3;

public class DamageSources {
   private final Registry<DamageType> f_268645_;
   private final DamageSource f_268567_;
   private final DamageSource f_268551_;
   private final DamageSource f_268475_;
   private final DamageSource f_268418_;
   private final DamageSource f_268602_;
   private final DamageSource f_268605_;
   private final DamageSource f_268691_;
   private final DamageSource f_268611_;
   private final DamageSource f_268742_;
   private final DamageSource f_268499_;
   private final DamageSource f_268729_;
   private final DamageSource f_268623_;
   private final DamageSource f_268726_;
   private final DamageSource f_268521_;
   private final DamageSource f_268591_;
   private final DamageSource f_268438_;
   private final DamageSource f_268582_;
   private final DamageSource f_268426_;
   private final DamageSource f_268561_;
   private final DamageSource f_268733_;
   private final DamageSource f_268610_;
   private final DamageSource f_287008_;
   private final DamageSource f_286964_;

   public DamageSources(RegistryAccess p_270740_) {
      this.f_268645_ = p_270740_.m_175515_(Registries.f_268580_);
      this.f_268567_ = this.m_269079_(DamageTypes.f_268631_);
      this.f_268551_ = this.m_269079_(DamageTypes.f_268450_);
      this.f_268475_ = this.m_269079_(DamageTypes.f_268468_);
      this.f_268418_ = this.m_269079_(DamageTypes.f_268546_);
      this.f_268602_ = this.m_269079_(DamageTypes.f_268434_);
      this.f_268605_ = this.m_269079_(DamageTypes.f_268612_);
      this.f_268691_ = this.m_269079_(DamageTypes.f_268613_);
      this.f_268611_ = this.m_269079_(DamageTypes.f_268722_);
      this.f_268742_ = this.m_269079_(DamageTypes.f_268441_);
      this.f_268499_ = this.m_269079_(DamageTypes.f_268585_);
      this.f_268729_ = this.m_269079_(DamageTypes.f_268671_);
      this.f_268623_ = this.m_269079_(DamageTypes.f_268576_);
      this.f_268726_ = this.m_269079_(DamageTypes.f_268724_);
      this.f_268521_ = this.m_269079_(DamageTypes.f_268433_);
      this.f_268591_ = this.m_269079_(DamageTypes.f_268515_);
      this.f_268438_ = this.m_269079_(DamageTypes.f_268493_);
      this.f_268582_ = this.m_269079_(DamageTypes.f_268482_);
      this.f_268426_ = this.m_269079_(DamageTypes.f_268752_);
      this.f_268561_ = this.m_269079_(DamageTypes.f_268469_);
      this.f_268733_ = this.m_269079_(DamageTypes.f_268444_);
      this.f_268610_ = this.m_269079_(DamageTypes.f_268669_);
      this.f_287008_ = this.m_269079_(DamageTypes.f_286973_);
      this.f_286964_ = this.m_269079_(DamageTypes.f_286979_);
   }

   private DamageSource m_269079_(ResourceKey<DamageType> p_270957_) {
      return new DamageSource(this.f_268645_.m_246971_(p_270957_));
   }

   private DamageSource m_269298_(ResourceKey<DamageType> p_270142_, @Nullable Entity p_270696_) {
      return new DamageSource(this.f_268645_.m_246971_(p_270142_), p_270696_);
   }

   private DamageSource m_268998_(ResourceKey<DamageType> p_270076_, @Nullable Entity p_270656_, @Nullable Entity p_270242_) {
      return new DamageSource(this.f_268645_.m_246971_(p_270076_), p_270656_, p_270242_);
   }

   public DamageSource m_269387_() {
      return this.f_268567_;
   }

   public DamageSource m_269548_() {
      return this.f_268551_;
   }

   public DamageSource m_269549_() {
      return this.f_268475_;
   }

   public DamageSource m_269233_() {
      return this.f_268418_;
   }

   public DamageSource m_269047_() {
      return this.f_268602_;
   }

   public DamageSource m_269318_() {
      return this.f_268605_;
   }

   public DamageSource m_269354_() {
      return this.f_268691_;
   }

   public DamageSource m_269063_() {
      return this.f_268611_;
   }

   public DamageSource m_269064_() {
      return this.f_268742_;
   }

   public DamageSource m_269325_() {
      return this.f_268499_;
   }

   public DamageSource m_268989_() {
      return this.f_268729_;
   }

   public DamageSource m_269515_() {
      return this.f_268623_;
   }

   public DamageSource m_269341_() {
      return this.f_268726_;
   }

   public DamageSource m_269264_() {
      return this.f_268521_;
   }

   public DamageSource m_269425_() {
      return this.f_268591_;
   }

   public DamageSource m_269251_() {
      return this.f_268438_;
   }

   public DamageSource m_269254_() {
      return this.f_268582_;
   }

   public DamageSource m_269483_() {
      return this.f_268426_;
   }

   public DamageSource m_269555_() {
      return this.f_268561_;
   }

   public DamageSource m_269109_() {
      return this.f_268733_;
   }

   public DamageSource m_269571_() {
      return this.f_268610_;
   }

   public DamageSource m_269564_(Entity p_270643_) {
      return this.m_269298_(DamageTypes.f_268659_, p_270643_);
   }

   public DamageSource m_269230_(Entity p_270112_) {
      return this.m_269298_(DamageTypes.f_268526_, p_270112_);
   }

   public DamageSource m_269103_(Entity p_270720_) {
      return this.m_269298_(DamageTypes.f_268513_, p_270720_);
   }

   public DamageSource m_269396_(LivingEntity p_270689_) {
      return this.m_269298_(DamageTypes.f_268656_, p_270689_);
   }

   public DamageSource m_269333_(LivingEntity p_270357_) {
      return this.m_269298_(DamageTypes.f_268566_, p_270357_);
   }

   public DamageSource m_269364_(LivingEntity p_270502_) {
      return this.m_269298_(DamageTypes.f_268511_, p_270502_);
   }

   public DamageSource m_269075_(Player p_270723_) {
      return this.m_269298_(DamageTypes.f_268464_, p_270723_);
   }

   public DamageSource m_269418_(AbstractArrow p_270570_, @Nullable Entity p_270857_) {
      return this.m_268998_(DamageTypes.f_268739_, p_270570_, p_270857_);
   }

   public DamageSource m_269525_(Entity p_270146_, @Nullable Entity p_270358_) {
      return this.m_268998_(DamageTypes.f_268714_, p_270146_, p_270358_);
   }

   public DamageSource m_269299_(Entity p_270210_, @Nullable LivingEntity p_270757_) {
      return this.m_268998_(DamageTypes.f_268534_, p_270210_, p_270757_);
   }

   public DamageSource m_268994_(FireworkRocketEntity p_270571_, @Nullable Entity p_270768_) {
      return this.m_268998_(DamageTypes.f_268428_, p_270571_, p_270768_);
   }

   public DamageSource m_269453_(Fireball p_270147_, @Nullable Entity p_270824_) {
      return p_270824_ == null ? this.m_269298_(DamageTypes.f_268556_, p_270147_) : this.m_268998_(DamageTypes.f_268684_, p_270147_, p_270824_);
   }

   public DamageSource m_269383_(WitherSkull p_270367_, Entity p_270887_) {
      return this.m_268998_(DamageTypes.f_268641_, p_270367_, p_270887_);
   }

   public DamageSource m_269390_(Entity p_270388_, @Nullable Entity p_270485_) {
      return this.m_268998_(DamageTypes.f_268425_, p_270388_, p_270485_);
   }

   public DamageSource m_269104_(Entity p_270560_, @Nullable Entity p_270646_) {
      return this.m_268998_(DamageTypes.f_268530_, p_270560_, p_270646_);
   }

   public DamageSource m_269374_(Entity p_270917_) {
      return this.m_269298_(DamageTypes.f_268440_, p_270917_);
   }

   public DamageSource m_269093_(@Nullable Explosion p_270369_) {
      return p_270369_ != null ? this.m_269036_(p_270369_.m_253049_(), p_270369_.m_252906_()) : this.m_269036_((Entity)null, (Entity)null);
   }

   public DamageSource m_269036_(@Nullable Entity p_271016_, @Nullable Entity p_270814_) {
      return this.m_268998_(p_270814_ != null && p_271016_ != null ? DamageTypes.f_268448_ : DamageTypes.f_268565_, p_271016_, p_270814_);
   }

   public DamageSource m_269285_(Entity p_270401_) {
      return this.m_269298_(DamageTypes.f_268679_, p_270401_);
   }

   public DamageSource m_269488_(Vec3 p_270175_) {
      return new DamageSource(this.f_268645_.m_246971_(DamageTypes.f_268650_), p_270175_);
   }

   public DamageSource m_287287_() {
      return this.f_287008_;
   }

   public DamageSource m_287172_() {
      return this.f_286964_;
   }
}
