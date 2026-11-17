import com.google.common.collect.Lists;
import java.util.List;

public class brs {
   public float a = 64.0F;
   public float b = 32.0F;
   private int r;
   private int s;
   public float c;
   public float d;
   public float e;
   public float f;
   public float g;
   public float h;
   private boolean t;
   private int u;
   public boolean i;
   public boolean j = true;
   public boolean k;
   public List<brq> l = Lists.newArrayList();
   public List<brs> m;
   public final String n;
   private final bqf v;
   public float o;
   public float p;
   public float q;

   public brs(bqf var1, String var2) {
      this.v = var1;
      var1.r.add(this);
      this.n = var2;
      this.b(var1.s, var1.t);
   }

   public brs(bqf var1) {
      this(var1, null);
   }

   public brs(bqf var1, int var2, int var3) {
      this(var1);
      this.a(var2, var3);
   }

   public void a(brs var1) {
      if (this.m == null) {
         this.m = Lists.newArrayList();
      }

      this.m.add(var1);
   }

   public brs a(int var1, int var2) {
      this.r = var1;
      this.s = var2;
      return this;
   }

   public brs a(String var1, float var2, float var3, float var4, int var5, int var6, int var7) {
      var1 = this.n + "." + var1;
      brt var8 = this.v.a(var1);
      this.a(var8.a, var8.b);
      this.l.add(new brq(this, this.r, this.s, var2, var3, var4, var5, var6, var7, 0.0F).a(var1));
      return this;
   }

   public brs a(float var1, float var2, float var3, int var4, int var5, int var6) {
      this.l.add(new brq(this, this.r, this.s, var1, var2, var3, var4, var5, var6, 0.0F));
      return this;
   }

   public brs a(float var1, float var2, float var3, int var4, int var5, int var6, boolean var7) {
      this.l.add(new brq(this, this.r, this.s, var1, var2, var3, var4, var5, var6, 0.0F, var7));
      return this;
   }

   public void a(float var1, float var2, float var3, int var4, int var5, int var6, float var7) {
      this.l.add(new brq(this, this.r, this.s, var1, var2, var3, var4, var5, var6, var7));
   }

   public void a(float var1, float var2, float var3) {
      this.c = var1;
      this.d = var2;
      this.e = var3;
   }

   public void a(float var1) {
      if (!this.k) {
         if (this.j) {
            if (!this.t) {
               this.d(var1);
            }

            bus.c(this.o, this.p, this.q);
            if (this.f != 0.0F || this.g != 0.0F || this.h != 0.0F) {
               bus.G();
               bus.c(this.c * var1, this.d * var1, this.e * var1);
               if (this.h != 0.0F) {
                  bus.b(this.h * (180.0F / (float)Math.PI), 0.0F, 0.0F, 1.0F);
               }

               if (this.g != 0.0F) {
                  bus.b(this.g * (180.0F / (float)Math.PI), 0.0F, 1.0F, 0.0F);
               }

               if (this.f != 0.0F) {
                  bus.b(this.f * (180.0F / (float)Math.PI), 1.0F, 0.0F, 0.0F);
               }

               bus.s(this.u);
               if (this.m != null) {
                  for (int var4 = 0; var4 < this.m.size(); var4++) {
                     this.m.get(var4).a(var1);
                  }
               }

               bus.H();
            } else if (this.c == 0.0F && this.d == 0.0F && this.e == 0.0F) {
               bus.s(this.u);
               if (this.m != null) {
                  for (int var3 = 0; var3 < this.m.size(); var3++) {
                     this.m.get(var3).a(var1);
                  }
               }
            } else {
               bus.c(this.c * var1, this.d * var1, this.e * var1);
               bus.s(this.u);
               if (this.m != null) {
                  for (int var2 = 0; var2 < this.m.size(); var2++) {
                     this.m.get(var2).a(var1);
                  }
               }

               bus.c(-this.c * var1, -this.d * var1, -this.e * var1);
            }

            bus.c(-this.o, -this.p, -this.q);
         }
      }
   }

   public void b(float var1) {
      if (!this.k) {
         if (this.j) {
            if (!this.t) {
               this.d(var1);
            }

            bus.G();
            bus.c(this.c * var1, this.d * var1, this.e * var1);
            if (this.g != 0.0F) {
               bus.b(this.g * (180.0F / (float)Math.PI), 0.0F, 1.0F, 0.0F);
            }

            if (this.f != 0.0F) {
               bus.b(this.f * (180.0F / (float)Math.PI), 1.0F, 0.0F, 0.0F);
            }

            if (this.h != 0.0F) {
               bus.b(this.h * (180.0F / (float)Math.PI), 0.0F, 0.0F, 1.0F);
            }

            bus.s(this.u);
            bus.H();
         }
      }
   }

   public void c(float var1) {
      if (!this.k) {
         if (this.j) {
            if (!this.t) {
               this.d(var1);
            }

            if (this.f != 0.0F || this.g != 0.0F || this.h != 0.0F) {
               bus.c(this.c * var1, this.d * var1, this.e * var1);
               if (this.h != 0.0F) {
                  bus.b(this.h * (180.0F / (float)Math.PI), 0.0F, 0.0F, 1.0F);
               }

               if (this.g != 0.0F) {
                  bus.b(this.g * (180.0F / (float)Math.PI), 0.0F, 1.0F, 0.0F);
               }

               if (this.f != 0.0F) {
                  bus.b(this.f * (180.0F / (float)Math.PI), 1.0F, 0.0F, 0.0F);
               }
            } else if (this.c != 0.0F || this.d != 0.0F || this.e != 0.0F) {
               bus.c(this.c * var1, this.d * var1, this.e * var1);
            }
         }
      }
   }

   private void d(float var1) {
      this.u = bia.a(1);
      bus.f(this.u, 4864);
      buk var2 = bve.a().c();

      for (int var3 = 0; var3 < this.l.size(); var3++) {
         this.l.get(var3).a(var2, var1);
      }

      bus.K();
      this.t = true;
   }

   public brs b(int var1, int var2) {
      this.a = (float)var1;
      this.b = (float)var2;
      return this;
   }
}
