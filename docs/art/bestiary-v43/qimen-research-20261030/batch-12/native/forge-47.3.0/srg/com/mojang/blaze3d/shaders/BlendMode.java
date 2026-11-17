package com.mojang.blaze3d.shaders;

import com.mojang.blaze3d.systems.RenderSystem;
import java.util.Locale;
import javax.annotation.Nullable;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class BlendMode {
   @Nullable
   private static BlendMode f_85499_;
   private final int f_85500_;
   private final int f_85501_;
   private final int f_85502_;
   private final int f_85503_;
   private final int f_85504_;
   private final boolean f_85505_;
   private final boolean f_85506_;

   private BlendMode(boolean p_85519_, boolean p_85520_, int p_85521_, int p_85522_, int p_85523_, int p_85524_, int p_85525_) {
      this.f_85505_ = p_85519_;
      this.f_85500_ = p_85521_;
      this.f_85502_ = p_85522_;
      this.f_85501_ = p_85523_;
      this.f_85503_ = p_85524_;
      this.f_85506_ = p_85520_;
      this.f_85504_ = p_85525_;
   }

   public BlendMode() {
      this(false, true, 1, 0, 1, 0, 32774);
   }

   public BlendMode(int p_85509_, int p_85510_, int p_85511_) {
      this(false, false, p_85509_, p_85510_, p_85509_, p_85510_, p_85511_);
   }

   public BlendMode(int p_85513_, int p_85514_, int p_85515_, int p_85516_, int p_85517_) {
      this(true, false, p_85513_, p_85514_, p_85515_, p_85516_, p_85517_);
   }

   public void m_85526_() {
      if (!this.equals(f_85499_)) {
         if (f_85499_ == null || this.f_85506_ != f_85499_.m_85529_()) {
            f_85499_ = this;
            if (this.f_85506_) {
               RenderSystem.disableBlend();
               return;
            }

            RenderSystem.enableBlend();
         }

         RenderSystem.blendEquation(this.f_85504_);
         if (this.f_85505_) {
            RenderSystem.blendFuncSeparate(this.f_85500_, this.f_85502_, this.f_85501_, this.f_85503_);
         } else {
            RenderSystem.blendFunc(this.f_85500_, this.f_85502_);
         }

      }
   }

   public boolean equals(Object p_85533_) {
      if (this == p_85533_) {
         return true;
      } else if (!(p_85533_ instanceof BlendMode)) {
         return false;
      } else {
         BlendMode blendmode = (BlendMode)p_85533_;
         if (this.f_85504_ != blendmode.f_85504_) {
            return false;
         } else if (this.f_85503_ != blendmode.f_85503_) {
            return false;
         } else if (this.f_85502_ != blendmode.f_85502_) {
            return false;
         } else if (this.f_85506_ != blendmode.f_85506_) {
            return false;
         } else if (this.f_85505_ != blendmode.f_85505_) {
            return false;
         } else if (this.f_85501_ != blendmode.f_85501_) {
            return false;
         } else {
            return this.f_85500_ == blendmode.f_85500_;
         }
      }
   }

   public int hashCode() {
      int i = this.f_85500_;
      i = 31 * i + this.f_85501_;
      i = 31 * i + this.f_85502_;
      i = 31 * i + this.f_85503_;
      i = 31 * i + this.f_85504_;
      i = 31 * i + (this.f_85505_ ? 1 : 0);
      return 31 * i + (this.f_85506_ ? 1 : 0);
   }

   public boolean m_85529_() {
      return this.f_85506_;
   }

   public static int m_85527_(String p_85528_) {
      String s = p_85528_.trim().toLowerCase(Locale.ROOT);
      if ("add".equals(s)) {
         return 32774;
      } else if ("subtract".equals(s)) {
         return 32778;
      } else if ("reversesubtract".equals(s)) {
         return 32779;
      } else if ("reverse_subtract".equals(s)) {
         return 32779;
      } else if ("min".equals(s)) {
         return 32775;
      } else {
         return "max".equals(s) ? '\u8008' : '\u8006';
      }
   }

   public static int m_85530_(String p_85531_) {
      String s = p_85531_.trim().toLowerCase(Locale.ROOT);
      s = s.replaceAll("_", "");
      s = s.replaceAll("one", "1");
      s = s.replaceAll("zero", "0");
      s = s.replaceAll("minus", "-");
      if ("0".equals(s)) {
         return 0;
      } else if ("1".equals(s)) {
         return 1;
      } else if ("srccolor".equals(s)) {
         return 768;
      } else if ("1-srccolor".equals(s)) {
         return 769;
      } else if ("dstcolor".equals(s)) {
         return 774;
      } else if ("1-dstcolor".equals(s)) {
         return 775;
      } else if ("srcalpha".equals(s)) {
         return 770;
      } else if ("1-srcalpha".equals(s)) {
         return 771;
      } else if ("dstalpha".equals(s)) {
         return 772;
      } else {
         return "1-dstalpha".equals(s) ? 773 : -1;
      }
   }
}
