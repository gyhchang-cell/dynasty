package net.minecraft.client.model.geom.builders;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.Lists;
import java.util.EnumSet;
import java.util.List;
import java.util.Set;
import net.minecraft.core.Direction;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class CubeListBuilder {
   private static final Set<Direction> f_271199_ = EnumSet.allOf(Direction.class);
   private final List<CubeDefinition> f_171475_ = Lists.newArrayList();
   private int f_171476_;
   private int f_171477_;
   private boolean f_171478_;

   public CubeListBuilder m_171514_(int p_171515_, int p_171516_) {
      this.f_171476_ = p_171515_;
      this.f_171477_ = p_171516_;
      return this;
   }

   public CubeListBuilder m_171480_() {
      return this.m_171555_(true);
   }

   public CubeListBuilder m_171555_(boolean p_171556_) {
      this.f_171478_ = p_171556_;
      return this;
   }

   public CubeListBuilder m_171544_(String p_171545_, float p_171546_, float p_171547_, float p_171548_, int p_171549_, int p_171550_, int p_171551_, CubeDeformation p_171552_, int p_171553_, int p_171554_) {
      this.m_171514_(p_171553_, p_171554_);
      this.f_171475_.add(new CubeDefinition(p_171545_, (float)this.f_171476_, (float)this.f_171477_, p_171546_, p_171547_, p_171548_, (float)p_171549_, (float)p_171550_, (float)p_171551_, p_171552_, this.f_171478_, 1.0F, 1.0F, f_271199_));
      return this;
   }

   public CubeListBuilder m_171534_(String p_171535_, float p_171536_, float p_171537_, float p_171538_, int p_171539_, int p_171540_, int p_171541_, int p_171542_, int p_171543_) {
      this.m_171514_(p_171542_, p_171543_);
      this.f_171475_.add(new CubeDefinition(p_171535_, (float)this.f_171476_, (float)this.f_171477_, p_171536_, p_171537_, p_171538_, (float)p_171539_, (float)p_171540_, (float)p_171541_, CubeDeformation.f_171458_, this.f_171478_, 1.0F, 1.0F, f_271199_));
      return this;
   }

   public CubeListBuilder m_171481_(float p_171482_, float p_171483_, float p_171484_, float p_171485_, float p_171486_, float p_171487_) {
      this.f_171475_.add(new CubeDefinition((String)null, (float)this.f_171476_, (float)this.f_171477_, p_171482_, p_171483_, p_171484_, p_171485_, p_171486_, p_171487_, CubeDeformation.f_171458_, this.f_171478_, 1.0F, 1.0F, f_271199_));
      return this;
   }

   public CubeListBuilder m_271786_(float p_272653_, float p_273044_, float p_272720_, float p_273739_, float p_273613_, float p_273328_, Set<Direction> p_273277_) {
      this.f_171475_.add(new CubeDefinition((String)null, (float)this.f_171476_, (float)this.f_171477_, p_272653_, p_273044_, p_272720_, p_273739_, p_273613_, p_273328_, CubeDeformation.f_171458_, this.f_171478_, 1.0F, 1.0F, p_273277_));
      return this;
   }

   public CubeListBuilder m_171517_(String p_171518_, float p_171519_, float p_171520_, float p_171521_, float p_171522_, float p_171523_, float p_171524_) {
      this.f_171475_.add(new CubeDefinition(p_171518_, (float)this.f_171476_, (float)this.f_171477_, p_171519_, p_171520_, p_171521_, p_171522_, p_171523_, p_171524_, CubeDeformation.f_171458_, this.f_171478_, 1.0F, 1.0F, f_271199_));
      return this;
   }

   public CubeListBuilder m_171525_(String p_171526_, float p_171527_, float p_171528_, float p_171529_, float p_171530_, float p_171531_, float p_171532_, CubeDeformation p_171533_) {
      this.f_171475_.add(new CubeDefinition(p_171526_, (float)this.f_171476_, (float)this.f_171477_, p_171527_, p_171528_, p_171529_, p_171530_, p_171531_, p_171532_, p_171533_, this.f_171478_, 1.0F, 1.0F, f_271199_));
      return this;
   }

   public CubeListBuilder m_171506_(float p_171507_, float p_171508_, float p_171509_, float p_171510_, float p_171511_, float p_171512_, boolean p_171513_) {
      this.f_171475_.add(new CubeDefinition((String)null, (float)this.f_171476_, (float)this.f_171477_, p_171507_, p_171508_, p_171509_, p_171510_, p_171511_, p_171512_, CubeDeformation.f_171458_, p_171513_, 1.0F, 1.0F, f_271199_));
      return this;
   }

   public CubeListBuilder m_171496_(float p_171497_, float p_171498_, float p_171499_, float p_171500_, float p_171501_, float p_171502_, CubeDeformation p_171503_, float p_171504_, float p_171505_) {
      this.f_171475_.add(new CubeDefinition((String)null, (float)this.f_171476_, (float)this.f_171477_, p_171497_, p_171498_, p_171499_, p_171500_, p_171501_, p_171502_, p_171503_, this.f_171478_, p_171504_, p_171505_, f_271199_));
      return this;
   }

   public CubeListBuilder m_171488_(float p_171489_, float p_171490_, float p_171491_, float p_171492_, float p_171493_, float p_171494_, CubeDeformation p_171495_) {
      this.f_171475_.add(new CubeDefinition((String)null, (float)this.f_171476_, (float)this.f_171477_, p_171489_, p_171490_, p_171491_, p_171492_, p_171493_, p_171494_, p_171495_, this.f_171478_, 1.0F, 1.0F, f_271199_));
      return this;
   }

   public List<CubeDefinition> m_171557_() {
      return ImmutableList.copyOf(this.f_171475_);
   }

   public static CubeListBuilder m_171558_() {
      return new CubeListBuilder();
   }
}
