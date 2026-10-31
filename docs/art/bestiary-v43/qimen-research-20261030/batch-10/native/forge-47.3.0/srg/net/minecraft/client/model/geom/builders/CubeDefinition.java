package net.minecraft.client.model.geom.builders;

import java.util.Set;
import javax.annotation.Nullable;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.core.Direction;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Vector3f;

@OnlyIn(Dist.CLIENT)
public final class CubeDefinition {
   @Nullable
   private final String f_171434_;
   private final Vector3f f_171435_;
   private final Vector3f f_171436_;
   private final CubeDeformation f_171437_;
   private final boolean f_171438_;
   private final UVPair f_171439_;
   private final UVPair f_171440_;
   private final Set<Direction> f_271491_;

   protected CubeDefinition(@Nullable String p_273024_, float p_273620_, float p_273436_, float p_273139_, float p_273013_, float p_272874_, float p_273100_, float p_273756_, float p_273105_, CubeDeformation p_272818_, boolean p_273585_, float p_272829_, float p_273119_, Set<Direction> p_273201_) {
      this.f_171434_ = p_273024_;
      this.f_171439_ = new UVPair(p_273620_, p_273436_);
      this.f_171435_ = new Vector3f(p_273139_, p_273013_, p_272874_);
      this.f_171436_ = new Vector3f(p_273100_, p_273756_, p_273105_);
      this.f_171437_ = p_272818_;
      this.f_171438_ = p_273585_;
      this.f_171440_ = new UVPair(p_272829_, p_273119_);
      this.f_271491_ = p_273201_;
   }

   public ModelPart.Cube m_171455_(int p_171456_, int p_171457_) {
      return new ModelPart.Cube((int)this.f_171439_.m_171612_(), (int)this.f_171439_.m_171613_(), this.f_171435_.x(), this.f_171435_.y(), this.f_171435_.z(), this.f_171436_.x(), this.f_171436_.y(), this.f_171436_.z(), this.f_171437_.f_171459_, this.f_171437_.f_171460_, this.f_171437_.f_171461_, this.f_171438_, (float)p_171456_ * this.f_171440_.m_171612_(), (float)p_171457_ * this.f_171440_.m_171613_(), this.f_271491_);
   }
}
