public class bpx extends bqf {
   public brs e;
   public brs f;
   public brs g;
   public brs h;
   public brs i;
   public brs j;
   public brs k;
   public bpx.a l = bpx.a.a;
   public bpx.a m = bpx.a.a;
   public boolean n;

   public bpx() {
      this(0.0F);
   }

   public bpx(float var1) {
      this(var1, 0.0F, 64, 32);
   }

   public bpx(float var1, float var2, int var3, int var4) {
      this.s = var3;
      this.t = var4;
      this.e = new brs(this, 0, 0);
      this.e.a(-4.0F, -8.0F, -4.0F, 8, 8, 8, var1);
      this.e.a(0.0F, 0.0F + var2, 0.0F);
      this.f = new brs(this, 32, 0);
      this.f.a(-4.0F, -8.0F, -4.0F, 8, 8, 8, var1 + 0.5F);
      this.f.a(0.0F, 0.0F + var2, 0.0F);
      this.g = new brs(this, 16, 16);
      this.g.a(-4.0F, 0.0F, -2.0F, 8, 12, 4, var1);
      this.g.a(0.0F, 0.0F + var2, 0.0F);
      this.h = new brs(this, 40, 16);
      this.h.a(-3.0F, -2.0F, -2.0F, 4, 12, 4, var1);
      this.h.a(-5.0F, 2.0F + var2, 0.0F);
      this.i = new brs(this, 40, 16);
      this.i.i = true;
      this.i.a(-1.0F, -2.0F, -2.0F, 4, 12, 4, var1);
      this.i.a(5.0F, 2.0F + var2, 0.0F);
      this.j = new brs(this, 0, 16);
      this.j.a(-2.0F, 0.0F, -2.0F, 4, 12, 4, var1);
      this.j.a(-1.9F, 12.0F + var2, 0.0F);
      this.k = new brs(this, 0, 16);
      this.k.i = true;
      this.k.a(-2.0F, 0.0F, -2.0F, 4, 12, 4, var1);
      this.k.a(1.9F, 12.0F + var2, 0.0F);
   }

   public void a(vg var1, float var2, float var3, float var4, float var5, float var6, float var7) {
      this.a(var2, var3, var4, var5, var6, var7, var1);
      bus.G();
      if (this.q) {
         float var8 = 2.0F;
         bus.b(0.75F, 0.75F, 0.75F);
         bus.c(0.0F, 16.0F * var7, 0.0F);
         this.e.a(var7);
         bus.H();
         bus.G();
         bus.b(0.5F, 0.5F, 0.5F);
         bus.c(0.0F, 24.0F * var7, 0.0F);
         this.g.a(var7);
         this.h.a(var7);
         this.i.a(var7);
         this.j.a(var7);
         this.k.a(var7);
         this.f.a(var7);
      } else {
         if (var1.aU()) {
            bus.c(0.0F, 0.2F, 0.0F);
         }

         this.e.a(var7);
         this.g.a(var7);
         this.h.a(var7);
         this.i.a(var7);
         this.j.a(var7);
         this.k.a(var7);
         this.f.a(var7);
      }

      bus.H();
   }

   public void a(float var1, float var2, float var3, float var4, float var5, float var6, vg var7) {
      boolean var8 = var7 instanceof vp && ((vp)var7).cQ() > 4;
      this.e.g = var4 * (float) (Math.PI / 180.0);
      if (var8) {
         this.e.f = (float) (-Math.PI / 4);
      } else {
         this.e.f = var5 * (float) (Math.PI / 180.0);
      }

      this.g.g = 0.0F;
      this.h.e = 0.0F;
      this.h.c = -5.0F;
      this.i.e = 0.0F;
      this.i.c = 5.0F;
      float var9 = 1.0F;
      if (var8) {
         var9 = (float)(var7.s * var7.s + var7.t * var7.t + var7.u * var7.u);
         var9 /= 0.2F;
         var9 *= var9 * var9;
      }

      if (var9 < 1.0F) {
         var9 = 1.0F;
      }

      this.h.f = rk.b(var1 * 0.6662F + (float) Math.PI) * 2.0F * var2 * 0.5F / var9;
      this.i.f = rk.b(var1 * 0.6662F) * 2.0F * var2 * 0.5F / var9;
      this.h.h = 0.0F;
      this.i.h = 0.0F;
      this.j.f = rk.b(var1 * 0.6662F) * 1.4F * var2 / var9;
      this.k.f = rk.b(var1 * 0.6662F + (float) Math.PI) * 1.4F * var2 / var9;
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
         vo var10 = this.a(var7);
         brs var11 = this.a(var10);
         float var12 = this.o;
         this.g.g = rk.a(rk.c(var12) * (float) (Math.PI * 2)) * 0.2F;
         if (var10 == vo.a) {
            this.g.g *= -1.0F;
         }

         this.h.e = rk.a(this.g.g) * 5.0F;
         this.h.c = -rk.b(this.g.g) * 5.0F;
         this.i.e = -rk.a(this.g.g) * 5.0F;
         this.i.c = rk.b(this.g.g) * 5.0F;
         this.h.g = this.h.g + this.g.g;
         this.i.g = this.i.g + this.g.g;
         this.i.f = this.i.f + this.g.g;
         var12 = 1.0F - this.o;
         var12 *= var12;
         var12 *= var12;
         var12 = 1.0F - var12;
         float var13 = rk.a(var12 * (float) Math.PI);
         float var14 = rk.a(this.o * (float) Math.PI) * -(this.e.f - 0.7F) * 0.75F;
         var11.f = (float)((double)var11.f - ((double)var13 * 1.2 + (double)var14));
         var11.g = var11.g + this.g.g * 2.0F;
         var11.h = var11.h + rk.a(this.o * (float) Math.PI) * -0.4F;
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

      this.h.h = this.h.h + rk.b(var3 * 0.09F) * 0.05F + 0.05F;
      this.i.h = this.i.h - (rk.b(var3 * 0.09F) * 0.05F + 0.05F);
      this.h.f = this.h.f + rk.a(var3 * 0.067F) * 0.05F;
      this.i.f = this.i.f - rk.a(var3 * 0.067F) * 0.05F;
      if (this.m == bpx.a.d) {
         this.h.g = -0.1F + this.e.g;
         this.i.g = 0.1F + this.e.g + 0.4F;
         this.h.f = (float) (-Math.PI / 2) + this.e.f;
         this.i.f = (float) (-Math.PI / 2) + this.e.f;
      } else if (this.l == bpx.a.d) {
         this.h.g = -0.1F + this.e.g - 0.4F;
         this.i.g = 0.1F + this.e.g;
         this.h.f = (float) (-Math.PI / 2) + this.e.f;
         this.i.f = (float) (-Math.PI / 2) + this.e.f;
      }

      a(this.e, this.f);
   }

   public void a(bqf var1) {
      super.a(var1);
      if (var1 instanceof bpx) {
         bpx var2 = (bpx)var1;
         this.l = var2.l;
         this.m = var2.m;
         this.n = var2.n;
      }
   }

   public void a(boolean var1) {
      this.e.j = var1;
      this.f.j = var1;
      this.g.j = var1;
      this.h.j = var1;
      this.i.j = var1;
      this.j.j = var1;
      this.k.j = var1;
   }

   public void a(float var1, vo var2) {
      this.a(var2).c(var1);
   }

   protected brs a(vo var1) {
      return var1 == vo.a ? this.i : this.h;
   }

   protected vo a(vg var1) {
      if (var1 instanceof vp) {
         vp var2 = (vp)var1;
         vo var3 = var2.cF();
         return var2.av == ub.a ? var3 : var3.a();
      } else {
         return vo.b;
      }
   }

   public static enum a {
      a,
      b,
      c,
      d;
   }
}
