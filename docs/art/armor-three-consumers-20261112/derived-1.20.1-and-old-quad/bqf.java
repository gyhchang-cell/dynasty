import com.google.common.collect.Lists;
import com.google.common.collect.Maps;
import java.util.List;
import java.util.Map;
import java.util.Random;

public abstract class bqf {
   public float o;
   public boolean p;
   public boolean q = true;
   public List<brs> r = Lists.newArrayList();
   private final Map<String, brt> a = Maps.newHashMap();
   public int s = 64;
   public int t = 32;

   public void a(vg var1, float var2, float var3, float var4, float var5, float var6, float var7) {
   }

   public void a(float var1, float var2, float var3, float var4, float var5, float var6, vg var7) {
   }

   public void a(vp var1, float var2, float var3, float var4) {
   }

   public brs a(Random var1) {
      return this.r.get(var1.nextInt(this.r.size()));
   }

   protected void a(String var1, int var2, int var3) {
      this.a.put(var1, new brt(var2, var3));
   }

   public brt a(String var1) {
      return this.a.get(var1);
   }

   public static void a(brs var0, brs var1) {
      var1.f = var0.f;
      var1.g = var0.g;
      var1.h = var0.h;
      var1.c = var0.c;
      var1.d = var0.d;
      var1.e = var0.e;
   }

   public void a(bqf var1) {
      this.o = var1.o;
      this.p = var1.p;
      this.q = var1.q;
   }
}
