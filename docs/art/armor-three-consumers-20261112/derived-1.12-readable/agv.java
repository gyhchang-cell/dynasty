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
         aip ☃ = agv.a(☃, ☃);
         return ☃.b() ? super.b(☃, ☃) : ☃;
      }
   };
   public final vl c;
   public final int d;
   public final float e;
   public final int f;
   private final agv.a p;

   public static aip a(eu var0, aip var1) {
      et ☃ = ☃.d().a((fa)☃.e().c(apz.a));
      List ☃x = ☃.h().a(vp.class, new bhb(☃), Predicates.and(vk.e, new vk.a(☃)));
      if (☃x.isEmpty()) {
         return aip.a;
      } else {
         vp ☃xx = ☃x.get(0);
         vl ☃xxx = vq.d(☃);
         aip ☃xxxx = ☃.a(1);
         ☃xx.a(☃xxx, ☃xxxx);
         if (☃xx instanceof vq) {
            ((vq)☃xx).a(☃xxx, 2.0F);
         }

         return ☃;
      }
   }

   public agv(agv.a var1, int var2, vl var3) {
      this.p = ☃;
      this.c = ☃;
      this.f = ☃;
      this.d = ☃.b(☃);
      this.e(☃.a(☃));
      this.e = ☃.e();
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
         fy ☃ = ☃.p();
         return ☃ != null && ☃.b("display", 10) ? ☃.p("display").b("color", 3) : false;
      }
   }

   public int c(aip var1) {
      if (this.p != agv.a.a) {
         return 16777215;
      } else {
         fy ☃ = ☃.p();
         if (☃ != null) {
            fy ☃x = ☃.p("display");
            if (☃x != null && ☃x.b("color", 3)) {
               return ☃x.h("color");
            }
         }

         return 10511680;
      }
   }

   public void d(aip var1) {
      if (this.p == agv.a.a) {
         fy ☃ = ☃.p();
         if (☃ != null) {
            fy ☃x = ☃.p("display");
            if (☃x.e("color")) {
               ☃x.r("color");
            }
         }
      }
   }

   public void a(aip var1, int var2) {
      if (this.p != agv.a.a) {
         throw new UnsupportedOperationException("Can't dye non-leather!");
      } else {
         fy ☃ = ☃.p();
         if (☃ == null) {
            ☃ = new fy();
            ☃.b(☃);
         }

         fy ☃x = ☃.p("display");
         if (!☃.b("display", 10)) {
            ☃.a("display", ☃x);
         }

         ☃x.a("color", ☃);
      }
   }

   public boolean a(aip var1, aip var2) {
      return this.p.c() == ☃.c() ? true : super.a(☃, ☃);
   }

   public ue<aip> a(amu var1, aed var2, ub var3) {
      aip ☃ = ☃.b(☃);
      vl ☃x = vq.d(☃);
      aip ☃xx = ☃.b(☃x);
      if (☃xx.b()) {
         ☃.a(☃x, ☃.l());
         ☃.e(0);
         return new ue(ud.a, ☃);
      } else {
         return new ue(ud.c, ☃);
      }
   }

   public Multimap<String, we> a(vl var1) {
      Multimap ☃ = super.a(☃);
      if (☃ == this.c) {
         ☃.put(adh.h.a(), new we(o[☃.b()], "Armor modifier", (double)this.d, 0));
         ☃.put(adh.i.a(), new we(o[☃.b()], "Armor toughness", (double)this.e, 0));
      }

      return ☃;
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
         this.f = ☃;
         this.g = ☃;
         this.h = ☃;
         this.i = ☃;
         this.j = ☃;
         this.k = ☃;
      }

      public int a(vl var1) {
         return agv.n[☃.b()] * this.g;
      }

      public int b(vl var1) {
         return this.h[☃.b()];
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
