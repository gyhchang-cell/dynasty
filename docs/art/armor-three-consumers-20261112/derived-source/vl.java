public enum vl {
   a(vl.a.a, 0, 0, "mainhand"),
   b(vl.a.a, 1, 5, "offhand"),
   c(vl.a.b, 0, 1, "feet"),
   d(vl.a.b, 1, 2, "legs"),
   e(vl.a.b, 2, 3, "chest"),
   f(vl.a.b, 3, 4, "head");

   private final vl.a g;
   private final int h;
   private final int i;
   private final String j;

   private vl(vl.a var3, int var4, int var5, String var6) {
      this.g = ☃;
      this.h = ☃;
      this.i = ☃;
      this.j = ☃;
   }

   public vl.a a() {
      return this.g;
   }

   public int b() {
      return this.h;
   }

   public int c() {
      return this.i;
   }

   public String d() {
      return this.j;
   }

   public static vl a(String var0) {
      for (vl ☃ : values()) {
         if (☃.d().equals(☃)) {
            return ☃;
         }
      }

      throw new IllegalArgumentException("Invalid slot '" + ☃ + "'");
   }

   public static enum a {
      a,
      b;
   }
}
