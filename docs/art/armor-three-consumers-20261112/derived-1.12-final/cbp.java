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
      this.a = var1;
      this.M_();
   }

   public void a(vp var1, float var2, float var3, float var4, float var5, float var6, float var7, float var8) {
      this.a(var1, var2, var3, var4, var5, var6, var7, var8, vl.e);
      this.a(var1, var2, var3, var4, var5, var6, var7, var8, vl.d);
      this.a(var1, var2, var3, var4, var5, var6, var7, var8, vl.c);
      this.a(var1, var2, var3, var4, var5, var6, var7, var8, vl.f);
   }

   public boolean a() {
      return false;
   }

   private void a(vp var1, float var2, float var3, float var4, float var5, float var6, float var7, float var8, vl var9) {
      aip var10 = var1.b(var9);
      if (var10.c() instanceof agv) {
         agv var11 = (agv)var10.c();
         if (var11.E_() == var9) {
            bqf var12 = this.a(var9);
            var12.a(this.a.b());
            var12.a(var1, var2, var3, var4);
            this.a((T)var12, var9);
            boolean var13 = this.b(var9);
            this.a.a(this.a(var11, var13));
            switch (var11.d()) {
               case a:
                  int var14 = var11.c(var10);
                  float var15 = (float)(var14 >> 16 & 0xFF) / 255.0F;
                  float var16 = (float)(var14 >> 8 & 0xFF) / 255.0F;
                  float var17 = (float)(var14 & 0xFF) / 255.0F;
                  bus.c(this.f * var15, this.g * var16, this.h * var17, this.e);
                  var12.a(var1, var2, var3, var5, var6, var7, var8);
                  this.a.a(this.a(var11, var13, "overlay"));
               case b:
               case c:
               case d:
               case e:
                  bus.c(this.f, this.g, this.h, this.e);
                  var12.a(var1, var2, var3, var5, var6, var7, var8);
               default:
                  if (!this.i && var10.x()) {
                     a(this.a, var1, var12, var2, var3, var4, var5, var6, var7, var8);
                  }
            }
         }
      }
   }

   public T a(vl var1) {
      return this.b(var1) ? this.c : this.d;
   }

   private boolean b(vl var1) {
      return var1 == vl.d;
   }

   public static void a(caa<?> var0, vp var1, bqf var2, float var3, float var4, float var5, float var6, float var7, float var8, float var9) {
      float var10 = (float)var1.T + var5;
      var0.a(b);
      bib.z().o.d(true);
      bus.m();
      bus.c(514);
      bus.a(false);
      float var11 = 0.5F;
      bus.c(0.5F, 0.5F, 0.5F, 1.0F);

      for (int var12 = 0; var12 < 2; var12++) {
         bus.g();
         bus.a(r.n, l.e);
         float var13 = 0.76F;
         bus.c(0.38F, 0.19F, 0.608F, 1.0F);
         bus.n(5890);
         bus.F();
         float var14 = 0.33333334F;
         bus.b(0.33333334F, 0.33333334F, 0.33333334F);
         bus.b(30.0F - (float)var12 * 60.0F, 0.0F, 0.0F, 1.0F);
         bus.c(0.0F, var10 * (0.001F + (float)var12 * 0.003F) * 20.0F, 0.0F);
         bus.n(5888);
         var2.a(var1, var3, var4, var6, var7, var8, var9);
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
      return this.a(var1, var2, null);
   }

   private nf a(agv var1, boolean var2, String var3) {
      String var4 = String.format("textures/models/armor/%s_layer_%d%s.png", var1.d().d(), var2 ? 2 : 1, var3 == null ? "" : String.format("_%s", var3));
      nf var5 = j.get(var4);
      if (var5 == null) {
         var5 = new nf(var4);
         j.put(var4, var5);
      }

      return var5;
   }

   protected abstract void M_();

   protected abstract void a(T var1, vl var2);
}
