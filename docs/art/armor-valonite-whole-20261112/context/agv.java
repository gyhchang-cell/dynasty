import com.google.common.base.Predicates;
import com.google.common.collect.Multimap;
import java.util.List;
import java.util.UUID;

public class agv extends ain {
   private static final int[] n = new int[]{13, 15, 16, 11};
   private static final UUID[] o = new UUID[]{
      UUID.fromString("845DB27C-C624-495F-8C9F-6020A9A58B6B"),
      UUID.fromString("D8499B04-0E66-4726-AB29-64469D734E0D"),
      UUID.fromString("9F3D476D-C118-4544-8365-64846904B48E"),
      UUID.fromString("2AD3F246-FEE1-4E67-B886-69FD380BB150")
   };
   public static final String[] a = new String[]{
      "minecraft:items/empty_armor_slot_boots",
      "minecraft:items/empty_armor_slot_leggings",
      "minecraft:items/empty_armor_slot_chestplate",
      "minecraft:items/empty_armor_slot_helmet"
   };
   public static final fb b = new ex() {
      protected aip b(eu var1, aip var2) {
         aip var3 = agv.a(var1, var2);
         return var3.b() ? super.b(var1, var2) : var3;
      }
   };
   public final vl c;
   public final int d;
   public final float e;
   public final int f;
   private final agv.a p;

   public static aip a(eu var0, aip var1) {
      et var2 = var0.d().a((fa)var0.e().c(apz.a));
      List var3 = var0.h().a(vp.class, new bhb(var2), Predicates.and(vk.e, new vk.a(var1)));
      if (var3.isEmpty()) {
         return aip.a;
      } else {
         vp var4 = (vp)var3.get(0);
         vl var5 = vq.d(var1);
         aip var6 = var1.a(1);
         var4.a(var5, var6);
         if (var4 instanceof vq) {
            ((vq)var4).a(var5, 2.0F);
         }

         return var1;
      }
   }

   public agv(agv.a var1, int var2, vl var3) {
      this.p = var1;
      this.c = var3;
      this.f = var2;
      this.d = var1.b(var3);
      this.e(var1.a(var3));
      this.e = var1.e();
      this.k = 1;
      this.b(ahp.j);
      apz.c.a(this, b);
   }

   public vl E_() {
      return this.c;
   }

   public int c() {
      return this.p.a();
   }

   public agv.a d() {
      return this.p;
   }

   public boolean e_(aip var1) {
      if (this.p != agv.a.a) {
         return false;
      } else {
         fy var2 = var1.p();
         return var2 != null && var2.b("display", 10) ? var2.p("display").b("color", 3) : false;
      }
   }

   public int c(aip var1) {
      if (this.p != agv.a.a) {
         return 16777215;
      } else {
         fy var2 = var1.p();
         if (var2 != null) {
            fy var3 = var2.p("display");
            if (var3 != null && var3.b("color", 3)) {
               return var3.h("color");
            }
         }

         return 10511680;
      }
   }

   public void d(aip var1) {
      if (this.p == agv.a.a) {
         fy var2 = var1.p();
         if (var2 != null) {
            fy var3 = var2.p("display");
            if (var3.e("color")) {
               var3.r("color");
            }
         }
      }
   }

   public void a(aip var1, int var2) {
      if (this.p != agv.a.a) {
         throw new UnsupportedOperationException("Can't dye non-leather!");
      } else {
         fy var3 = var1.p();
         if (var3 == null) {
            var3 = new fy();
            var1.b(var3);
         }

         fy var4 = var3.p("display");
         if (!var3.b("display", 10)) {
            var3.a("display", var4);
         }

         var4.a("color", var2);
      }
   }

   public boolean a(aip var1, aip var2) {
      return this.p.c() == var2.c() ? true : super.a(var1, var2);
   }

   public ue<aip> a(amu var1, aed var2, ub var3) {
      aip var4 = var2.b(var3);
      vl var5 = vq.d(var4);
      aip var6 = var2.b(var5);
      if (var6.b()) {
         var2.a(var5, var4.l());
         var4.e(0);
         return new ue(ud.a, var4);
      } else {
         return new ue(ud.c, var4);
      }
   }

   public Multimap<String, we> a(vl var1) {
      Multimap var2 = super.a(var1);
      if (var1 == this.c) {
         var2.put(adh.h.a(), new we(o[var1.b()], "Armor modifier", (double)this.d, 0));
         var2.put(adh.i.a(), new we(o[var1.b()], "Armor toughness", (double)this.e, 0));
      }

      return var2;
   }

   public static enum a {
      a("leather", 5, new int[]{1, 2, 3, 1}, 15, qf.t, 0.0F),
      b("chainmail", 15, new int[]{1, 4, 5, 2}, 12, qf.n, 0.0F),
      c("iron", 15, new int[]{2, 5, 6, 2}, 9, qf.s, 0.0F),
      d("gold", 7, new int[]{1, 3, 5, 2}, 25, qf.r, 0.0F),
      e("diamond", 33, new int[]{3, 6, 8, 3}, 10, qf.o, 2.0F);

      private final String f;
      private final int g;
      private final int[] h;
      private final int i;
      private final qe j;
      private final float k;

      private a(String var3, int var4, int[] var5, int var6, qe var7, float var8) {
         this.f = var3;
         this.g = var4;
         this.h = var5;
         this.i = var6;
         this.j = var7;
         this.k = var8;
      }

      public int a(vl var1) {
         return agv.n[var1.b()] * this.g;
      }

      public int b(vl var1) {
         return this.h[var1.b()];
      }

      public int a() {
         return this.i;
      }

      public qe b() {
         return this.j;
      }

      public ain c() {
         if (this == a) {
            return air.aN;
         } else if (this == b) {
            return air.m;
         } else if (this == d) {
            return air.n;
         } else if (this == c) {
            return air.m;
         } else {
            return this == e ? air.l : null;
         }
      }

      public String d() {
         return this.f;
      }

      public float e() {
         return this.k;
      }
   }
}
