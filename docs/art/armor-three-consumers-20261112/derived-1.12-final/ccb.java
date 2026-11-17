public class ccb extends cbp<bpx> {
   public ccb(caa<?> var1) {
      super(var1);
   }

   @Override
   protected void M_() {
      this.c = new bpx(0.5F);
      this.d = new bpx(1.0F);
   }

   protected void a(bpx var1, vl var2) {
      this.a(var1);
      switch (var2) {
         case f:
            var1.e.j = true;
            var1.f.j = true;
            break;
         case e:
            var1.g.j = true;
            var1.h.j = true;
            var1.i.j = true;
            break;
         case d:
            var1.g.j = true;
            var1.j.j = true;
            var1.k.j = true;
            break;
         case c:
            var1.j.j = true;
            var1.k.j = true;
      }
   }

   protected void a(bpx var1) {
      var1.a(false);
   }
}
