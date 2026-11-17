package net.minecraft.world.item;

import com.google.common.collect.Lists;
import java.util.List;
import java.util.function.Predicate;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.advancements.CriteriaTriggers;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.network.chat.CommonComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.stats.Stats;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.CrossbowAttackMob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.FireworkRocketEntity;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.item.enchantment.Enchantments;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.joml.Quaternionf;
import org.joml.Vector3f;

public class CrossbowItem extends ProjectileWeaponItem implements Vanishable {
   private static final String f_150790_ = "Charged";
   private static final String f_150791_ = "ChargedProjectiles";
   private static final int f_150792_ = 25;
   public static final int f_150789_ = 8;
   private boolean f_40847_ = false;
   private boolean f_40848_ = false;
   private static final float f_150793_ = 0.2F;
   private static final float f_150794_ = 0.5F;
   private static final float f_150795_ = 3.15F;
   private static final float f_150796_ = 1.6F;

   public CrossbowItem(Item.Properties p_40850_) {
      super(p_40850_);
   }

   public Predicate<ItemStack> m_6442_() {
      return f_43006_;
   }

   public Predicate<ItemStack> m_6437_() {
      return f_43005_;
   }

   public InteractionResultHolder<ItemStack> m_7203_(Level p_40920_, Player p_40921_, InteractionHand p_40922_) {
      ItemStack itemstack = p_40921_.m_21120_(p_40922_);
      if (m_40932_(itemstack)) {
         m_40887_(p_40920_, p_40921_, p_40922_, itemstack, m_40945_(itemstack), 1.0F);
         m_40884_(itemstack, false);
         return InteractionResultHolder.m_19096_(itemstack);
      } else if (!p_40921_.m_6298_(itemstack).m_41619_()) {
         if (!m_40932_(itemstack)) {
            this.f_40847_ = false;
            this.f_40848_ = false;
            p_40921_.m_6672_(p_40922_);
         }

         return InteractionResultHolder.m_19096_(itemstack);
      } else {
         return InteractionResultHolder.m_19100_(itemstack);
      }
   }

   private static float m_40945_(ItemStack p_40946_) {
      return m_40871_(p_40946_, Items.f_42688_) ? 1.6F : 3.15F;
   }

   public void m_5551_(ItemStack p_40875_, Level p_40876_, LivingEntity p_40877_, int p_40878_) {
      int i = this.m_8105_(p_40875_) - p_40878_;
      float f = m_40853_(i, p_40875_);
      if (f >= 1.0F && !m_40932_(p_40875_) && m_40859_(p_40877_, p_40875_)) {
         m_40884_(p_40875_, true);
         SoundSource soundsource = p_40877_ instanceof Player ? SoundSource.PLAYERS : SoundSource.HOSTILE;
         p_40876_.m_6263_((Player)null, p_40877_.m_20185_(), p_40877_.m_20186_(), p_40877_.m_20189_(), SoundEvents.f_11841_, soundsource, 1.0F, 1.0F / (p_40876_.m_213780_().m_188501_() * 0.5F + 1.0F) + 0.2F);
      }

   }

   private static boolean m_40859_(LivingEntity p_40860_, ItemStack p_40861_) {
      int i = EnchantmentHelper.m_44843_(Enchantments.f_44959_, p_40861_);
      int j = i == 0 ? 1 : 3;
      boolean flag = p_40860_ instanceof Player && ((Player)p_40860_).m_150110_().f_35937_;
      ItemStack itemstack = p_40860_.m_6298_(p_40861_);
      ItemStack itemstack1 = itemstack.m_41777_();

      for(int k = 0; k < j; ++k) {
         if (k > 0) {
            itemstack = itemstack1.m_41777_();
         }

         if (itemstack.m_41619_() && flag) {
            itemstack = new ItemStack(Items.f_42412_);
            itemstack1 = itemstack.m_41777_();
         }

         if (!m_40862_(p_40860_, p_40861_, itemstack, k > 0, flag)) {
            return false;
         }
      }

      return true;
   }

   private static boolean m_40862_(LivingEntity p_40863_, ItemStack p_40864_, ItemStack p_40865_, boolean p_40866_, boolean p_40867_) {
      if (p_40865_.m_41619_()) {
         return false;
      } else {
         boolean flag = p_40867_ && p_40865_.m_41720_() instanceof ArrowItem;
         ItemStack itemstack;
         if (!flag && !p_40867_ && !p_40866_) {
            itemstack = p_40865_.m_41620_(1);
            if (p_40865_.m_41619_() && p_40863_ instanceof Player) {
               ((Player)p_40863_).m_150109_().m_36057_(p_40865_);
            }
         } else {
            itemstack = p_40865_.m_41777_();
         }

         m_40928_(p_40864_, itemstack);
         return true;
      }
   }

   public static boolean m_40932_(ItemStack p_40933_) {
      CompoundTag compoundtag = p_40933_.m_41783_();
      return compoundtag != null && compoundtag.m_128471_("Charged");
   }

   public static void m_40884_(ItemStack p_40885_, boolean p_40886_) {
      CompoundTag compoundtag = p_40885_.m_41784_();
      compoundtag.m_128379_("Charged", p_40886_);
   }

   private static void m_40928_(ItemStack p_40929_, ItemStack p_40930_) {
      CompoundTag compoundtag = p_40929_.m_41784_();
      ListTag listtag;
      if (compoundtag.m_128425_("ChargedProjectiles", 9)) {
         listtag = compoundtag.m_128437_("ChargedProjectiles", 10);
      } else {
         listtag = new ListTag();
      }

      CompoundTag compoundtag1 = new CompoundTag();
      p_40930_.m_41739_(compoundtag1);
      listtag.add(compoundtag1);
      compoundtag.m_128365_("ChargedProjectiles", listtag);
   }

   private static List<ItemStack> m_40941_(ItemStack p_40942_) {
      List<ItemStack> list = Lists.newArrayList();
      CompoundTag compoundtag = p_40942_.m_41783_();
      if (compoundtag != null && compoundtag.m_128425_("ChargedProjectiles", 9)) {
         ListTag listtag = compoundtag.m_128437_("ChargedProjectiles", 10);
         if (listtag != null) {
            for(int i = 0; i < listtag.size(); ++i) {
               CompoundTag compoundtag1 = listtag.m_128728_(i);
               list.add(ItemStack.m_41712_(compoundtag1));
            }
         }
      }

      return list;
   }

   private static void m_40943_(ItemStack p_40944_) {
      CompoundTag compoundtag = p_40944_.m_41783_();
      if (compoundtag != null) {
         ListTag listtag = compoundtag.m_128437_("ChargedProjectiles", 9);
         listtag.clear();
         compoundtag.m_128365_("ChargedProjectiles", listtag);
      }

   }

   public static boolean m_40871_(ItemStack p_40872_, Item p_40873_) {
      return m_40941_(p_40872_).stream().anyMatch((p_40870_) -> {
         return p_40870_.m_150930_(p_40873_);
      });
   }

   private static void m_40894_(Level p_40895_, LivingEntity p_40896_, InteractionHand p_40897_, ItemStack p_40898_, ItemStack p_40899_, float p_40900_, boolean p_40901_, float p_40902_, float p_40903_, float p_40904_) {
      if (!p_40895_.f_46443_) {
         boolean flag = p_40899_.m_150930_(Items.f_42688_);
         Projectile projectile;
         if (flag) {
            projectile = new FireworkRocketEntity(p_40895_, p_40899_, p_40896_, p_40896_.m_20185_(), p_40896_.m_20188_() - (double)0.15F, p_40896_.m_20189_(), true);
         } else {
            projectile = m_40914_(p_40895_, p_40896_, p_40898_, p_40899_);
            if (p_40901_ || p_40904_ != 0.0F) {
               ((AbstractArrow)projectile).f_36705_ = AbstractArrow.Pickup.CREATIVE_ONLY;
            }
         }

         if (p_40896_ instanceof CrossbowAttackMob) {
            CrossbowAttackMob crossbowattackmob = (CrossbowAttackMob)p_40896_;
            crossbowattackmob.m_5811_(crossbowattackmob.m_5448_(), p_40898_, projectile, p_40904_);
         } else {
            Vec3 vec31 = p_40896_.m_20289_(1.0F);
            Quaternionf quaternionf = (new Quaternionf()).setAngleAxis((double)(p_40904_ * ((float)Math.PI / 180F)), vec31.f_82479_, vec31.f_82480_, vec31.f_82481_);
            Vec3 vec3 = p_40896_.m_20252_(1.0F);
            Vector3f vector3f = vec3.m_252839_().rotate(quaternionf);
            projectile.m_6686_((double)vector3f.x(), (double)vector3f.y(), (double)vector3f.z(), p_40902_, p_40903_);
         }

         p_40898_.m_41622_(flag ? 3 : 1, p_40896_, (p_40858_) -> {
            p_40858_.m_21190_(p_40897_);
         });
         p_40895_.m_7967_(projectile);
         p_40895_.m_6263_((Player)null, p_40896_.m_20185_(), p_40896_.m_20186_(), p_40896_.m_20189_(), SoundEvents.f_11847_, SoundSource.PLAYERS, 1.0F, p_40900_);
      }
   }

   private static AbstractArrow m_40914_(Level p_40915_, LivingEntity p_40916_, ItemStack p_40917_, ItemStack p_40918_) {
      ArrowItem arrowitem = (ArrowItem)(p_40918_.m_41720_() instanceof ArrowItem ? p_40918_.m_41720_() : Items.f_42412_);
      AbstractArrow abstractarrow = arrowitem.m_6394_(p_40915_, p_40918_, p_40916_);
      if (p_40916_ instanceof Player) {
         abstractarrow.m_36762_(true);
      }

      abstractarrow.m_36740_(SoundEvents.f_11840_);
      abstractarrow.m_36793_(true);
      int i = EnchantmentHelper.m_44843_(Enchantments.f_44961_, p_40917_);
      if (i > 0) {
         abstractarrow.m_36767_((byte)i);
      }

      return abstractarrow;
   }

   public static void m_40887_(Level p_40888_, LivingEntity p_40889_, InteractionHand p_40890_, ItemStack p_40891_, float p_40892_, float p_40893_) {
      List<ItemStack> list = m_40941_(p_40891_);
      float[] afloat = m_220023_(p_40889_.m_217043_());

      for(int i = 0; i < list.size(); ++i) {
         ItemStack itemstack = list.get(i);
         boolean flag = p_40889_ instanceof Player && ((Player)p_40889_).m_150110_().f_35937_;
         if (!itemstack.m_41619_()) {
            if (i == 0) {
               m_40894_(p_40888_, p_40889_, p_40890_, p_40891_, itemstack, afloat[i], flag, p_40892_, p_40893_, 0.0F);
            } else if (i == 1) {
               m_40894_(p_40888_, p_40889_, p_40890_, p_40891_, itemstack, afloat[i], flag, p_40892_, p_40893_, -10.0F);
            } else if (i == 2) {
               m_40894_(p_40888_, p_40889_, p_40890_, p_40891_, itemstack, afloat[i], flag, p_40892_, p_40893_, 10.0F);
            }
         }
      }

      m_40905_(p_40888_, p_40889_, p_40891_);
   }

   private static float[] m_220023_(RandomSource p_220024_) {
      boolean flag = p_220024_.m_188499_();
      return new float[]{1.0F, m_220025_(flag, p_220024_), m_220025_(!flag, p_220024_)};
   }

   private static float m_220025_(boolean p_220026_, RandomSource p_220027_) {
      float f = p_220026_ ? 0.63F : 0.43F;
      return 1.0F / (p_220027_.m_188501_() * 0.5F + 1.8F) + f;
   }

   private static void m_40905_(Level p_40906_, LivingEntity p_40907_, ItemStack p_40908_) {
      if (p_40907_ instanceof ServerPlayer serverplayer) {
         if (!p_40906_.f_46443_) {
            CriteriaTriggers.f_10555_.m_65462_(serverplayer, p_40908_);
         }

         serverplayer.m_36246_(Stats.f_12982_.m_12902_(p_40908_.m_41720_()));
      }

      m_40943_(p_40908_);
   }

   public void m_5929_(Level p_40910_, LivingEntity p_40911_, ItemStack p_40912_, int p_40913_) {
      if (!p_40910_.f_46443_) {
         int i = EnchantmentHelper.m_44843_(Enchantments.f_44960_, p_40912_);
         SoundEvent soundevent = this.m_40851_(i);
         SoundEvent soundevent1 = i == 0 ? SoundEvents.f_11842_ : null;
         float f = (float)(p_40912_.m_41779_() - p_40913_) / (float)m_40939_(p_40912_);
         if (f < 0.2F) {
            this.f_40847_ = false;
            this.f_40848_ = false;
         }

         if (f >= 0.2F && !this.f_40847_) {
            this.f_40847_ = true;
            p_40910_.m_6263_((Player)null, p_40911_.m_20185_(), p_40911_.m_20186_(), p_40911_.m_20189_(), soundevent, SoundSource.PLAYERS, 0.5F, 1.0F);
         }

         if (f >= 0.5F && soundevent1 != null && !this.f_40848_) {
            this.f_40848_ = true;
            p_40910_.m_6263_((Player)null, p_40911_.m_20185_(), p_40911_.m_20186_(), p_40911_.m_20189_(), soundevent1, SoundSource.PLAYERS, 0.5F, 1.0F);
         }
      }

   }

   public int m_8105_(ItemStack p_40938_) {
      return m_40939_(p_40938_) + 3;
   }

   public static int m_40939_(ItemStack p_40940_) {
      int i = EnchantmentHelper.m_44843_(Enchantments.f_44960_, p_40940_);
      return i == 0 ? 25 : 25 - 5 * i;
   }

   public UseAnim m_6164_(ItemStack p_40935_) {
      return UseAnim.CROSSBOW;
   }

   private SoundEvent m_40851_(int p_40852_) {
      switch (p_40852_) {
         case 1:
            return SoundEvents.f_11844_;
         case 2:
            return SoundEvents.f_11845_;
         case 3:
            return SoundEvents.f_11846_;
         default:
            return SoundEvents.f_11843_;
      }
   }

   private static float m_40853_(int p_40854_, ItemStack p_40855_) {
      float f = (float)p_40854_ / (float)m_40939_(p_40855_);
      if (f > 1.0F) {
         f = 1.0F;
      }

      return f;
   }

   public void m_7373_(ItemStack p_40880_, @Nullable Level p_40881_, List<Component> p_40882_, TooltipFlag p_40883_) {
      List<ItemStack> list = m_40941_(p_40880_);
      if (m_40932_(p_40880_) && !list.isEmpty()) {
         ItemStack itemstack = list.get(0);
         p_40882_.add(Component.m_237115_("item.minecraft.crossbow.projectile").m_7220_(CommonComponents.f_263701_).m_7220_(itemstack.m_41611_()));
         if (p_40883_.m_7050_() && itemstack.m_150930_(Items.f_42688_)) {
            List<Component> list1 = Lists.newArrayList();
            Items.f_42688_.m_7373_(itemstack, p_40881_, list1, p_40883_);
            if (!list1.isEmpty()) {
               for(int i = 0; i < list1.size(); ++i) {
                  list1.set(i, Component.m_237113_("  ").m_7220_(list1.get(i)).m_130940_(ChatFormatting.GRAY));
               }

               p_40882_.addAll(list1);
            }
         }

      }
   }

   public boolean m_41463_(ItemStack p_150801_) {
      return p_150801_.m_150930_(this);
   }

   public int m_6615_() {
      return 8;
   }
}
