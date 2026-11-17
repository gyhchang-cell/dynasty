import bus.l;
import bus.r;
import com.google.common.collect.Maps;
import java.util.Map;

public abstract class cbp<T extends bqf> implements ccg<vp> {
   protected static final nf b = new nf("textures/misc/enchanted_item_glint.png");
   protected T c;
   protected T d;
   private final caa<?> a;
   private float e = 1.0F;
   private float f = 1.0F;
   private float g = 1.0F;
   private float h = 1.0F;
   private boolean i;
   private static final Map<String, nf> j = Maps.newHashMap();

   public cbp(caa<?> var1) {
      this.a = ☃;
      this.M_();
   }

   public void a(vp var1, float var2, float var3, float var4, float var5, float var6, float var7, float var8) {
      this.a(☃, ☃, ☃, ☃, ☃, ☃, ☃, ☃, vl.e);
      this.a(☃, ☃, ☃, ☃, ☃, ☃, ☃, ☃, vl.d);
      this.a(☃, ☃, ☃, ☃, ☃, ☃, ☃, ☃, vl.c);
      this.a(☃, ☃, ☃, ☃, ☃, ☃, ☃, ☃, vl.f);
   }

   public boolean a() {
      return false;
   }

   private void a(vp var1, float var2, float var3, float var4, float var5, float var6, float var7, float var8, vl var9) {
      aip ☃ = ☃.b(☃);
      if (☃.c() instanceof agv) {
         agv ☃x = (agv)☃.c();
         if (☃x.E_() == ☃) {
            bqf ☃xx = this.a(☃);
            ☃xx.a(this.a.b());
            ☃xx.a(☃, ☃, ☃, ☃);
            this.a(☃xx, ☃);
            boolean ☃xxx = this.b(☃);
            this.a.a(this.a(☃x, ☃xxx));
            switch (☃x.d()) {
               case a:
                  int ☃xxxx = ☃x.c(☃);
                  float ☃xxxxx = (float)(☃xxxx >> 16 & 0xFF) / 255.0F;
                  float ☃xxxxxx = (float)(☃xxxx >> 8 & 0xFF) / 255.0F;
                  float ☃xxxxxxx = (float)(☃xxxx & 0xFF) / 255.0F;
                  bus.c(this.f * ☃xxxxx, this.g * ☃xxxxxx, this.h * ☃xxxxxxx, this.e);
                  ☃xx.a(☃, ☃, ☃, ☃, ☃, ☃, ☃);
                  this.a.a(this.a(☃x, ☃xxx, "overlay"));
               case b:
               case c:
               case d:
               case e:
                  bus.c(this.f, this.g, this.h, this.e);
                  ☃xx.a(☃, ☃, ☃, ☃, ☃, ☃, ☃);
               default:
                  if (!this.i && ☃.x()) {
                     a(this.a, ☃, ☃xx, ☃, ☃, ☃, ☃, ☃, ☃, ☃);
                  }
            }
         }
      }
   }

   public T a(vl var1) {
      return this.b(☃) ? this.c : this.d;
   }

   private boolean b(vl var1) {
      return ☃ == vl.d;
   }

   public static void a(caa<?> var0, vp var1, bqf var2, float var3, float var4, float var5, float var6, float var7, float var8, float var9) {
      float ☃ = (float)☃.T + ☃;
      ☃.a(b);
      bib.z().o.d(true);
      bus.m();
      bus.c(514);
      bus.a(false);
      float ☃x = 0.5F;
      bus.c(0.5F, 0.5F, 0.5F, 1.0F);

      for (int ☃xx = 0; ☃xx < 2; ☃xx++) {
         bus.g();
         bus.a(r.n, l.e);
         float ☃xxx = 0.76F;
         bus.c(0.38F, 0.19F, 0.608F, 1.0F);
         bus.n(5890);
         bus.F();
         float ☃xxxx = 0.33333334F;
         bus.b(0.33333334F, 0.33333334F, 0.33333334F);
         bus.b(30.0F - (float)☃xx * 60.0F, 0.0F, 0.0F, 1.0F);
         bus.c(0.0F, ☃ * (0.001F + (float)☃xx * 0.003F) * 20.0F, 0.0F);
         bus.n(5888);
         ☃.a(☃, ☃, ☃, ☃, ☃, ☃, ☃);
         bus.a(r.e, l.n);
      }

      bus.n(5890);
      bus.F();
      bus.n(5888);
      bus.f();
      bus.a(true);
      bus.c(515);
      bus.l();
      bib.z().o.d(false);
   }

   private nf a(agv var1, boolean var2) {
      return this.a(☃, ☃, null);
   }

   private nf a(agv var1, boolean var2, String var3) {
      String ☃ = String.format("textures/models/armor/%s_layer_%d%s.png", ☃.d().d(), ☃ ? 2 : 1, ☃ == null ? "" : String.format("_%s", ☃));
      nf ☃x = j.get(☃);
      if (☃x == null) {
         ☃x = new nf(☃);
         j.put(☃, ☃x);
      }

      return ☃x;
   }

   protected abstract void M_();

   protected abstract void a(T var1, vl var2);
}
