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
      this.v = ☃;
      ☃.r.add(this);
      this.n = ☃;
      this.b(☃.s, ☃.t);
   }

   public brs(bqf var1) {
      this(☃, null);
   }

   public brs(bqf var1, int var2, int var3) {
      this(☃);
      this.a(☃, ☃);
   }

   public void a(brs var1) {
      if (this.m == null) {
         this.m = Lists.newArrayList();
      }

      this.m.add(☃);
   }

   public brs a(int var1, int var2) {
      this.r = ☃;
      this.s = ☃;
      return this;
   }

   public brs a(String var1, float var2, float var3, float var4, int var5, int var6, int var7) {
      ☃ = this.n + "." + ☃;
      brt ☃ = this.v.a(☃);
      this.a(☃.a, ☃.b);
      this.l.add(new brq(this, this.r, this.s, ☃, ☃, ☃, ☃, ☃, ☃, 0.0F).a(☃));
      return this;
   }

   public brs a(float var1, float var2, float var3, int var4, int var5, int var6) {
      this.l.add(new brq(this, this.r, this.s, ☃, ☃, ☃, ☃, ☃, ☃, 0.0F));
      return this;
   }

   public brs a(float var1, float var2, float var3, int var4, int var5, int var6, boolean var7) {
      this.l.add(new brq(this, this.r, this.s, ☃, ☃, ☃, ☃, ☃, ☃, 0.0F, ☃));
      return this;
   }

   public void a(float var1, float var2, float var3, int var4, int var5, int var6, float var7) {
      this.l.add(new brq(this, this.r, this.s, ☃, ☃, ☃, ☃, ☃, ☃, ☃));
   }

   public void a(float var1, float var2, float var3) {
      this.c = ☃;
      this.d = ☃;
      this.e = ☃;
   }

   public void a(float var1) {
      if (!this.k) {
         if (this.j) {
            if (!this.t) {
               this.d(☃);
            }

            bus.c(this.o, this.p, this.q);
            if (this.f != 0.0F || this.g != 0.0F || this.h != 0.0F) {
               bus.G();
               bus.c(this.c * ☃, this.d * ☃, this.e * ☃);
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
                  for (int ☃ = 0; ☃ < this.m.size(); ☃++) {
                     this.m.get(☃).a(☃);
                  }
               }

               bus.H();
            } else if (this.c == 0.0F && this.d == 0.0F && this.e == 0.0F) {
               bus.s(this.u);
               if (this.m != null) {
                  for (int ☃ = 0; ☃ < this.m.size(); ☃++) {
                     this.m.get(☃).a(☃);
                  }
               }
            } else {
               bus.c(this.c * ☃, this.d * ☃, this.e * ☃);
               bus.s(this.u);
               if (this.m != null) {
                  for (int ☃ = 0; ☃ < this.m.size(); ☃++) {
                     this.m.get(☃).a(☃);
                  }
               }

               bus.c(-this.c * ☃, -this.d * ☃, -this.e * ☃);
            }

            bus.c(-this.o, -this.p, -this.q);
         }
      }
   }

   public void b(float var1) {
      if (!this.k) {
         if (this.j) {
            if (!this.t) {
               this.d(☃);
            }

            bus.G();
            bus.c(this.c * ☃, this.d * ☃, this.e * ☃);
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
               this.d(☃);
            }

            if (this.f != 0.0F || this.g != 0.0F || this.h != 0.0F) {
               bus.c(this.c * ☃, this.d * ☃, this.e * ☃);
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
               bus.c(this.c * ☃, this.d * ☃, this.e * ☃);
            }
         }
      }
   }

   private void d(float var1) {
      this.u = bia.a(1);
      bus.f(this.u, 4864);
      buk ☃ = bve.a().c();

      for (int ☃x = 0; ☃x < this.l.size(); ☃x++) {
         this.l.get(☃x).a(☃, ☃);
      }

      bus.K();
      this.t = true;
   }

   public brs b(int var1, int var2) {
      this.a = (float)☃;
      this.b = (float)☃;
      return this;
   }
}
