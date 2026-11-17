import bpx.a;

public class bpx extends bqf {
   public brs e;
   public brs f;
   public brs g;
   public brs h;
   public brs i;
   public brs j;
   public brs k;
   public a l = a.a;
   public a m = a.a;
   public boolean n;

   public bpx() {
      this(0.0F);
   }

   public bpx(float var1) {
      this(☃, 0.0F, 64, 32);
   }

   public bpx(float var1, float var2, int var3, int var4) {
      this.s = ☃;
      this.t = ☃;
      this.e = new brs(this, 0, 0);
      this.e.a(-4.0F, -8.0F, -4.0F, 8, 8, 8, ☃);
      this.e.a(0.0F, 0.0F + ☃, 0.0F);
      this.f = new brs(this, 32, 0);
      this.f.a(-4.0F, -8.0F, -4.0F, 8, 8, 8, ☃ + 0.5F);
      this.f.a(0.0F, 0.0F + ☃, 0.0F);
      this.g = new brs(this, 16, 16);
      this.g.a(-4.0F, 0.0F, -2.0F, 8, 12, 4, ☃);
      this.g.a(0.0F, 0.0F + ☃, 0.0F);
      this.h = new brs(this, 40, 16);
      this.h.a(-3.0F, -2.0F, -2.0F, 4, 12, 4, ☃);
      this.h.a(-5.0F, 2.0F + ☃, 0.0F);
      this.i = new brs(this, 40, 16);
      this.i.i = true;
      this.i.a(-1.0F, -2.0F, -2.0F, 4, 12, 4, ☃);
      this.i.a(5.0F, 2.0F + ☃, 0.0F);
      this.j = new brs(this, 0, 16);
      this.j.a(-2.0F, 0.0F, -2.0F, 4, 12, 4, ☃);
      this.j.a(-1.9F, 12.0F + ☃, 0.0F);
      this.k = new brs(this, 0, 16);
      this.k.i = true;
      this.k.a(-2.0F, 0.0F, -2.0F, 4, 12, 4, ☃);
      this.k.a(1.9F, 12.0F + ☃, 0.0F);
   }

   public void a(vg var1, float var2, float var3, float var4, float var5, float var6, float var7) {
      this.a(☃, ☃, ☃, ☃, ☃, ☃, ☃);
      bus.G();
      if (this.q) {
         float ☃ = 2.0F;
         bus.b(0.75F, 0.75F, 0.75F);
         bus.c(0.0F, 16.0F * ☃, 0.0F);
         this.e.a(☃);
         bus.H();
         bus.G();
         bus.b(0.5F, 0.5F, 0.5F);
         bus.c(0.0F, 24.0F * ☃, 0.0F);
         this.g.a(☃);
         this.h.a(☃);
         this.i.a(☃);
         this.j.a(☃);
         this.k.a(☃);
         this.f.a(☃);
      } else {
         if (☃.aU()) {
            bus.c(0.0F, 0.2F, 0.0F);
         }

         this.e.a(☃);
         this.g.a(☃);
         this.h.a(☃);
         this.i.a(☃);
         this.j.a(☃);
         this.k.a(☃);
         this.f.a(☃);
      }

      bus.H();
   }

   public void a(float var1, float var2, float var3, float var4, float var5, float var6, vg var7) {
      boolean ☃ = ☃ instanceof vp && ((vp)☃).cQ() > 4;
      this.e.g = ☃ * (float) (Math.PI / 180.0);
      if (☃) {
         this.e.f = (float) (-Math.PI / 4);
      } else {
         this.e.f = ☃ * (float) (Math.PI / 180.0);
      }

      this.g.g = 0.0F;
      this.h.e = 0.0F;
      this.h.c = -5.0F;
      this.i.e = 0.0F;
      this.i.c = 5.0F;
      float ☃x = 1.0F;
      if (☃) {
         ☃x = (float)(☃.s * ☃.s + ☃.t * ☃.t + ☃.u * ☃.u);
         ☃x /= 0.2F;
         ☃x *= ☃x * ☃x;
      }

      if (☃x < 1.0F) {
         ☃x = 1.0F;
      }

      this.h.f = rk.b(☃ * 0.6662F + (float) Math.PI) * 2.0F * ☃ * 0.5F / ☃x;
      this.i.f = rk.b(☃ * 0.6662F) * 2.0F * ☃ * 0.5F / ☃x;
      this.h.h = 0.0F;
      this.i.h = 0.0F;
      this.j.f = rk.b(☃ * 0.6662F) * 1.4F * ☃ / ☃x;
      this.k.f = rk.b(☃ * 0.6662F + (float) Math.PI) * 1.4F * ☃ / ☃x;
      this.j.g = 0.0F;
      this.k.g = 0.0F;
      this.j.h = 0.0F;
      this.k.h = 0.0F;
      if (this.p) {
         this.h.f += (float) (-Math.PI / 5);
         this.i.f += (float) (-Math.PI / 5);
         this.j.f = -1.4137167F;
         this.j.g = (float) (Math.PI / 10);
         this.j.h = 0.07853982F;
         this.k.f = -1.4137167F;
         this.k.g = (float) (-Math.PI / 10);
         this.k.h = -0.07853982F;
      }

      this.h.g = 0.0F;
      this.h.h = 0.0F;
      switch (this.l) {
         case a:
            this.i.g = 0.0F;
            break;
         case c:
            this.i.f = this.i.f * 0.5F - 0.9424779F;
            this.i.g = (float) (Math.PI / 6);
            break;
         case b:
            this.i.f = this.i.f * 0.5F - (float) (Math.PI / 10);
            this.i.g = 0.0F;
      }

      switch (this.m) {
         case a:
            this.h.g = 0.0F;
            break;
         case c:
            this.h.f = this.h.f * 0.5F - 0.9424779F;
            this.h.g = (float) (-Math.PI / 6);
            break;
         case b:
            this.h.f = this.h.f * 0.5F - (float) (Math.PI / 10);
            this.h.g = 0.0F;
      }

      if (this.o > 0.0F) {
         vo ☃xx = this.a(☃);
         brs ☃xxx = this.a(☃xx);
         float ☃xxxx = this.o;
         this.g.g = rk.a(rk.c(☃xxxx) * (float) (Math.PI * 2)) * 0.2F;
         if (☃xx == vo.a) {
            this.g.g *= -1.0F;
         }

         this.h.e = rk.a(this.g.g) * 5.0F;
         this.h.c = -rk.b(this.g.g) * 5.0F;
         this.i.e = -rk.a(this.g.g) * 5.0F;
         this.i.c = rk.b(this.g.g) * 5.0F;
         this.h.g = this.h.g + this.g.g;
         this.i.g = this.i.g + this.g.g;
         this.i.f = this.i.f + this.g.g;
         ☃xxxx = 1.0F - this.o;
         ☃xxxx *= ☃xxxx;
         ☃xxxx *= ☃xxxx;
         ☃xxxx = 1.0F - ☃xxxx;
         float ☃xxxxx = rk.a(☃xxxx * (float) Math.PI);
         float ☃xxxxxx = rk.a(this.o * (float) Math.PI) * -(this.e.f - 0.7F) * 0.75F;
         ☃xxx.f = (float)((double)☃xxx.f - ((double)☃xxxxx * 1.2 + (double)☃xxxxxx));
         ☃xxx.g = ☃xxx.g + this.g.g * 2.0F;
         ☃xxx.h = ☃xxx.h + rk.a(this.o * (float) Math.PI) * -0.4F;
      }

      if (this.n) {
         this.g.f = 0.5F;
         this.h.f += 0.4F;
         this.i.f += 0.4F;
         this.j.e = 4.0F;
         this.k.e = 4.0F;
         this.j.d = 9.0F;
         this.k.d = 9.0F;
         this.e.d = 1.0F;
      } else {
         this.g.f = 0.0F;
         this.j.e = 0.1F;
         this.k.e = 0.1F;
         this.j.d = 12.0F;
         this.k.d = 12.0F;
         this.e.d = 0.0F;
      }

      this.h.h = this.h.h + rk.b(☃ * 0.09F) * 0.05F + 0.05F;
      this.i.h = this.i.h - (rk.b(☃ * 0.09F) * 0.05F + 0.05F);
      this.h.f = this.h.f + rk.a(☃ * 0.067F) * 0.05F;
      this.i.f = this.i.f - rk.a(☃ * 0.067F) * 0.05F;
      if (this.m == a.d) {
         this.h.g = -0.1F + this.e.g;
         this.i.g = 0.1F + this.e.g + 0.4F;
         this.h.f = (float) (-Math.PI / 2) + this.e.f;
         this.i.f = (float) (-Math.PI / 2) + this.e.f;
      } else if (this.l == a.d) {
         this.h.g = -0.1F + this.e.g - 0.4F;
         this.i.g = 0.1F + this.e.g;
         this.h.f = (float) (-Math.PI / 2) + this.e.f;
         this.i.f = (float) (-Math.PI / 2) + this.e.f;
      }

      a(this.e, this.f);
   }

   public void a(bqf var1) {
      super.a(☃);
      if (☃ instanceof bpx) {
         bpx ☃ = (bpx)☃;
         this.l = ☃.l;
         this.m = ☃.m;
         this.n = ☃.n;
      }
   }

   public void a(boolean var1) {
      this.e.j = ☃;
      this.f.j = ☃;
      this.g.j = ☃;
      this.h.j = ☃;
      this.i.j = ☃;
      this.j.j = ☃;
      this.k.j = ☃;
   }

   public void a(float var1, vo var2) {
      this.a(☃).c(☃);
   }

   protected brs a(vo var1) {
      return ☃ == vo.a ? this.i : this.h;
   }

   protected vo a(vg var1) {
      if (☃ instanceof vp) {
         vp ☃ = (vp)☃;
         vo ☃x = ☃.cF();
         return ☃.av == ub.a ? ☃x : ☃x.a();
      } else {
         return vo.b;
      }
   }
}
