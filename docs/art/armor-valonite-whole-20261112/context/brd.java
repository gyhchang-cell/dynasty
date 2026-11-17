public class brd {
   public bhe a;
   public float b;
   public float c;

   public brd(float var1, float var2, float var3, float var4, float var5) {
      this(new bhe((double)var1, (double)var2, (double)var3), var4, var5);
   }

   public brd a(float var1, float var2) {
      return new brd(this, var1, var2);
   }

   public brd(brd var1, float var2, float var3) {
      this.a = var1.a;
      this.b = var2;
      this.c = var3;
   }

   public brd(bhe var1, float var2, float var3) {
      this.a = var1;
      this.b = var2;
      this.c = var3;
   }
}
