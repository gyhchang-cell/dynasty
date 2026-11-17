public class bql {
   public brd[] a;
   public int b;
   private boolean c;

   public bql(brd[] var1) {
      this.a = var1;
      this.b = var1.length;
   }

   public bql(brd[] var1, int var2, int var3, int var4, int var5, float var6, float var7) {
      this(var1);
      float var8 = 0.0F / var6;
      float var9 = 0.0F / var7;
      var1[0] = var1[0].a((float)var4 / var6 - var8, (float)var3 / var7 + var9);
      var1[1] = var1[1].a((float)var2 / var6 + var8, (float)var3 / var7 + var9);
      var1[2] = var1[2].a((float)var2 / var6 + var8, (float)var5 / var7 - var9);
      var1[3] = var1[3].a((float)var4 / var6 - var8, (float)var5 / var7 - var9);
   }

   public void a() {
      brd[] var1 = new brd[this.a.length];

      for (int var2 = 0; var2 < this.a.length; var2++) {
         var1[var2] = this.a[this.a.length - var2 - 1];
      }

      this.a = var1;
   }

   public void a(buk var1, float var2) {
      bhe var3 = this.a[1].a.a(this.a[0].a);
      bhe var4 = this.a[1].a.a(this.a[2].a);
      bhe var5 = var4.c(var3).a();
      float var6 = (float)var5.b;
      float var7 = (float)var5.c;
      float var8 = (float)var5.d;
      if (this.c) {
         var6 = -var6;
         var7 = -var7;
         var8 = -var8;
      }

      var1.a(7, cdy.c);

      for (int var9 = 0; var9 < 4; var9++) {
         brd var10 = this.a[var9];
         var1.b(var10.a.b * (double)var2, var10.a.c * (double)var2, var10.a.d * (double)var2).a((double)var10.b, (double)var10.c).c(var6, var7, var8).d();
      }

      bve.a().b();
   }
}
