package net.minecraft.client.model.geom;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.blaze3d.vertex.PoseStack.Pose;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.Set;
import java.util.stream.Stream;
import net.minecraft.client.model.geom.ModelPart.Visitor;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Matrix3f;
import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;
import org.joml.Vector4f;

@OnlyIn(Dist.CLIENT)
public final class ModelPart {
   public static final float f_233552_ = 1.0F;
   public float f_104200_;
   public float f_104201_;
   public float f_104202_;
   public float f_104203_;
   public float f_104204_;
   public float f_104205_;
   public float f_233553_ = 1.0F;
   public float f_233554_ = 1.0F;
   public float f_233555_ = 1.0F;
   public boolean f_104207_ = true;
   public boolean f_233556_;
   private final List<ModelPart.Cube> f_104212_;
   private final Map<String, ModelPart> f_104213_;
   private PartPose f_233557_ = PartPose.f_171404_;

   public ModelPart(List<ModelPart.Cube> p_171306_, Map<String, ModelPart> p_171307_) {
      this.f_104212_ = p_171306_;
      this.f_104213_ = p_171307_;
   }

   public PartPose m_171308_() {
      return PartPose.m_171423_(this.f_104200_, this.f_104201_, this.f_104202_, this.f_104203_, this.f_104204_, this.f_104205_);
   }

   public PartPose m_233566_() {
      return this.f_233557_;
   }

   public void m_233560_(PartPose p_233561_) {
      this.f_233557_ = p_233561_;
   }

   public void m_233569_() {
      this.m_171322_(this.f_233557_);
   }

   public void m_171322_(PartPose p_171323_) {
      this.f_104200_ = p_171323_.f_171405_;
      this.f_104201_ = p_171323_.f_171406_;
      this.f_104202_ = p_171323_.f_171407_;
      this.f_104203_ = p_171323_.f_171408_;
      this.f_104204_ = p_171323_.f_171409_;
      this.f_104205_ = p_171323_.f_171410_;
      this.f_233553_ = 1.0F;
      this.f_233554_ = 1.0F;
      this.f_233555_ = 1.0F;
   }

   public void m_104315_(ModelPart p_104316_) {
      this.f_233553_ = p_104316_.f_233553_;
      this.f_233554_ = p_104316_.f_233554_;
      this.f_233555_ = p_104316_.f_233555_;
      this.f_104203_ = p_104316_.f_104203_;
      this.f_104204_ = p_104316_.f_104204_;
      this.f_104205_ = p_104316_.f_104205_;
      this.f_104200_ = p_104316_.f_104200_;
      this.f_104201_ = p_104316_.f_104201_;
      this.f_104202_ = p_104316_.f_104202_;
   }

   public boolean m_233562_(String p_233563_) {
      return this.f_104213_.containsKey(p_233563_);
   }

   public ModelPart m_171324_(String p_171325_) {
      ModelPart $$1 = this.f_104213_.get(p_171325_);
      if ($$1 == null) {
         throw new NoSuchElementException("Can't find part " + p_171325_);
      } else {
         return $$1;
      }
   }

   public void m_104227_(float p_104228_, float p_104229_, float p_104230_) {
      this.f_104200_ = p_104228_;
      this.f_104201_ = p_104229_;
      this.f_104202_ = p_104230_;
   }

   public void m_171327_(float p_171328_, float p_171329_, float p_171330_) {
      this.f_104203_ = p_171328_;
      this.f_104204_ = p_171329_;
      this.f_104205_ = p_171330_;
   }

   public void m_104301_(PoseStack p_104302_, VertexConsumer p_104303_, int p_104304_, int p_104305_) {
      this.m_104306_(p_104302_, p_104303_, p_104304_, p_104305_, 1.0F, 1.0F, 1.0F, 1.0F);
   }

   public void m_104306_(
      PoseStack p_104307_, VertexConsumer p_104308_, int p_104309_, int p_104310_, float p_104311_, float p_104312_, float p_104313_, float p_104314_
   ) {
      if (this.f_104207_) {
         if (!this.f_104212_.isEmpty() || !this.f_104213_.isEmpty()) {
            p_104307_.m_85836_();
            this.m_104299_(p_104307_);
            if (!this.f_233556_) {
               this.m_104290_(p_104307_.m_85850_(), p_104308_, p_104309_, p_104310_, p_104311_, p_104312_, p_104313_, p_104314_);
            }

            for (ModelPart $$8 : this.f_104213_.values()) {
               $$8.m_104306_(p_104307_, p_104308_, p_104309_, p_104310_, p_104311_, p_104312_, p_104313_, p_104314_);
            }

            p_104307_.m_85849_();
         }
      }
   }

   public void m_171309_(PoseStack p_171310_, Visitor p_171311_) {
      this.m_171312_(p_171310_, p_171311_, "");
   }

   private void m_171312_(PoseStack p_171313_, Visitor p_171314_, String p_171315_) {
      if (!this.f_104212_.isEmpty() || !this.f_104213_.isEmpty()) {
         p_171313_.m_85836_();
         this.m_104299_(p_171313_);
         Pose $$3 = p_171313_.m_85850_();

         for (int $$4 = 0; $$4 < this.f_104212_.size(); $$4++) {
            p_171314_.m_171341_($$3, p_171315_, $$4, this.f_104212_.get($$4));
         }

         String $$5 = p_171315_ + "/";
         this.f_104213_.forEach((p_171320_, p_171321_) -> p_171321_.m_171312_(p_171313_, p_171314_, $$5 + p_171320_));
         p_171313_.m_85849_();
      }
   }

   public void m_104299_(PoseStack p_104300_) {
      p_104300_.m_252880_(this.f_104200_ / 16.0F, this.f_104201_ / 16.0F, this.f_104202_ / 16.0F);
      if (this.f_104203_ != 0.0F || this.f_104204_ != 0.0F || this.f_104205_ != 0.0F) {
         p_104300_.m_252781_(new Quaternionf().rotationZYX(this.f_104205_, this.f_104204_, this.f_104203_));
      }

      if (this.f_233553_ != 1.0F || this.f_233554_ != 1.0F || this.f_233555_ != 1.0F) {
         p_104300_.m_85841_(this.f_233553_, this.f_233554_, this.f_233555_);
      }
   }

   private void m_104290_(
      Pose p_104291_, VertexConsumer p_104292_, int p_104293_, int p_104294_, float p_104295_, float p_104296_, float p_104297_, float p_104298_
   ) {
      for (ModelPart.Cube $$8 : this.f_104212_) {
         $$8.m_171332_(p_104291_, p_104292_, p_104293_, p_104294_, p_104295_, p_104296_, p_104297_, p_104298_);
      }
   }

   public ModelPart.Cube m_233558_(RandomSource p_233559_) {
      return this.f_104212_.get(p_233559_.m_188503_(this.f_104212_.size()));
   }

   public boolean m_171326_() {
      return this.f_104212_.isEmpty();
   }

   public void m_252854_(Vector3f p_253873_) {
      this.f_104200_ = this.f_104200_ + p_253873_.x();
      this.f_104201_ = this.f_104201_ + p_253873_.y();
      this.f_104202_ = this.f_104202_ + p_253873_.z();
   }

   public void m_252899_(Vector3f p_253983_) {
      this.f_104203_ = this.f_104203_ + p_253983_.x();
      this.f_104204_ = this.f_104204_ + p_253983_.y();
      this.f_104205_ = this.f_104205_ + p_253983_.z();
   }

   public void m_253072_(Vector3f p_253957_) {
      this.f_233553_ = this.f_233553_ + p_253957_.x();
      this.f_233554_ = this.f_233554_ + p_253957_.y();
      this.f_233555_ = this.f_233555_ + p_253957_.z();
   }

   public Stream<ModelPart> m_171331_() {
      return Stream.concat(Stream.of(this), this.f_104213_.values().stream().flatMap(ModelPart::m_171331_));
   }

   @OnlyIn(Dist.CLIENT)
   public static class Cube {
      private final ModelPart.Polygon[] f_104341_;
      public final float f_104335_;
      public final float f_104336_;
      public final float f_104337_;
      public final float f_104338_;
      public final float f_104339_;
      public final float f_104340_;

      public Cube(
         int p_273701_,
         int p_273034_,
         float p_272824_,
         float p_273777_,
         float p_273748_,
         float p_273722_,
         float p_273763_,
         float p_272823_,
         float p_272945_,
         float p_272790_,
         float p_272870_,
         boolean p_273589_,
         float p_273591_,
         float p_273313_,
         Set<Direction> p_273291_
      ) {
         this.f_104335_ = p_272824_;
         this.f_104336_ = p_273777_;
         this.f_104337_ = p_273748_;
         this.f_104338_ = p_272824_ + p_273722_;
         this.f_104339_ = p_273777_ + p_273763_;
         this.f_104340_ = p_273748_ + p_272823_;
         this.f_104341_ = new ModelPart.Polygon[p_273291_.size()];
         float $$15 = p_272824_ + p_273722_;
         float $$16 = p_273777_ + p_273763_;
         float $$17 = p_273748_ + p_272823_;
         p_272824_ -= p_272945_;
         p_273777_ -= p_272790_;
         p_273748_ -= p_272870_;
         $$15 += p_272945_;
         $$16 += p_272790_;
         $$17 += p_272870_;
         if (p_273589_) {
            float $$18 = $$15;
            $$15 = p_272824_;
            p_272824_ = $$18;
         }

         ModelPart.Vertex $$19 = new ModelPart.Vertex(p_272824_, p_273777_, p_273748_, 0.0F, 0.0F);
         ModelPart.Vertex $$20 = new ModelPart.Vertex($$15, p_273777_, p_273748_, 0.0F, 8.0F);
         ModelPart.Vertex $$21 = new ModelPart.Vertex($$15, $$16, p_273748_, 8.0F, 8.0F);
         ModelPart.Vertex $$22 = new ModelPart.Vertex(p_272824_, $$16, p_273748_, 8.0F, 0.0F);
         ModelPart.Vertex $$23 = new ModelPart.Vertex(p_272824_, p_273777_, $$17, 0.0F, 0.0F);
         ModelPart.Vertex $$24 = new ModelPart.Vertex($$15, p_273777_, $$17, 0.0F, 8.0F);
         ModelPart.Vertex $$25 = new ModelPart.Vertex($$15, $$16, $$17, 8.0F, 8.0F);
         ModelPart.Vertex $$26 = new ModelPart.Vertex(p_272824_, $$16, $$17, 8.0F, 0.0F);
         float $$27 = (float)p_273701_;
         float $$28 = (float)p_273701_ + p_272823_;
         float $$29 = (float)p_273701_ + p_272823_ + p_273722_;
         float $$30 = (float)p_273701_ + p_272823_ + p_273722_ + p_273722_;
         float $$31 = (float)p_273701_ + p_272823_ + p_273722_ + p_272823_;
         float $$32 = (float)p_273701_ + p_272823_ + p_273722_ + p_272823_ + p_273722_;
         float $$33 = (float)p_273034_;
         float $$34 = (float)p_273034_ + p_272823_;
         float $$35 = (float)p_273034_ + p_272823_ + p_273763_;
         int $$36 = 0;
         if (p_273291_.contains(Direction.DOWN)) {
            this.f_104341_[$$36++] = new ModelPart.Polygon(
               new ModelPart.Vertex[]{$$24, $$23, $$19, $$20}, $$28, $$33, $$29, $$34, p_273591_, p_273313_, p_273589_, Direction.DOWN
            );
         }

         if (p_273291_.contains(Direction.UP)) {
            this.f_104341_[$$36++] = new ModelPart.Polygon(
               new ModelPart.Vertex[]{$$21, $$22, $$26, $$25}, $$29, $$34, $$30, $$33, p_273591_, p_273313_, p_273589_, Direction.UP
            );
         }

         if (p_273291_.contains(Direction.WEST)) {
            this.f_104341_[$$36++] = new ModelPart.Polygon(
               new ModelPart.Vertex[]{$$19, $$23, $$26, $$22}, $$27, $$34, $$28, $$35, p_273591_, p_273313_, p_273589_, Direction.WEST
            );
         }

         if (p_273291_.contains(Direction.NORTH)) {
            this.f_104341_[$$36++] = new ModelPart.Polygon(
               new ModelPart.Vertex[]{$$20, $$19, $$22, $$21}, $$28, $$34, $$29, $$35, p_273591_, p_273313_, p_273589_, Direction.NORTH
            );
         }

         if (p_273291_.contains(Direction.EAST)) {
            this.f_104341_[$$36++] = new ModelPart.Polygon(
               new ModelPart.Vertex[]{$$24, $$20, $$21, $$25}, $$29, $$34, $$31, $$35, p_273591_, p_273313_, p_273589_, Direction.EAST
            );
         }

         if (p_273291_.contains(Direction.SOUTH)) {
            this.f_104341_[$$36] = new ModelPart.Polygon(
               new ModelPart.Vertex[]{$$23, $$24, $$25, $$26}, $$31, $$34, $$32, $$35, p_273591_, p_273313_, p_273589_, Direction.SOUTH
            );
         }
      }

      public void m_171332_(
         Pose p_171333_, VertexConsumer p_171334_, int p_171335_, int p_171336_, float p_171337_, float p_171338_, float p_171339_, float p_171340_
      ) {
         Matrix4f $$8 = p_171333_.m_252922_();
         Matrix3f $$9 = p_171333_.m_252943_();

         for (ModelPart.Polygon $$10 : this.f_104341_) {
            Vector3f $$11 = $$9.transform(new Vector3f($$10.f_104360_));
            float $$12 = $$11.x();
            float $$13 = $$11.y();
            float $$14 = $$11.z();

            for (ModelPart.Vertex $$15 : $$10.f_104359_) {
               float $$16 = $$15.f_104371_.x() / 16.0F;
               float $$17 = $$15.f_104371_.y() / 16.0F;
               float $$18 = $$15.f_104371_.z() / 16.0F;
               Vector4f $$19 = $$8.transform(new Vector4f($$16, $$17, $$18, 1.0F));
               p_171334_.m_5954_(
                  $$19.x(),
                  $$19.y(),
                  $$19.z(),
                  p_171337_,
                  p_171338_,
                  p_171339_,
                  p_171340_,
                  $$15.f_104372_,
                  $$15.f_104373_,
                  p_171336_,
                  p_171335_,
                  $$12,
                  $$13,
                  $$14
               );
            }
         }
      }
   }

   @OnlyIn(Dist.CLIENT)
   static class Polygon {
      public final ModelPart.Vertex[] f_104359_;
      public final Vector3f f_104360_;

      public Polygon(
         ModelPart.Vertex[] p_104362_,
         float p_104363_,
         float p_104364_,
         float p_104365_,
         float p_104366_,
         float p_104367_,
         float p_104368_,
         boolean p_104369_,
         Direction p_104370_
      ) {
         this.f_104359_ = p_104362_;
         float $$9 = 0.0F / p_104367_;
         float $$10 = 0.0F / p_104368_;
         p_104362_[0] = p_104362_[0].m_104384_(p_104365_ / p_104367_ - $$9, p_104364_ / p_104368_ + $$10);
         p_104362_[1] = p_104362_[1].m_104384_(p_104363_ / p_104367_ + $$9, p_104364_ / p_104368_ + $$10);
         p_104362_[2] = p_104362_[2].m_104384_(p_104363_ / p_104367_ + $$9, p_104366_ / p_104368_ - $$10);
         p_104362_[3] = p_104362_[3].m_104384_(p_104365_ / p_104367_ - $$9, p_104366_ / p_104368_ - $$10);
         if (p_104369_) {
            int $$11 = p_104362_.length;

            for (int $$12 = 0; $$12 < $$11 / 2; $$12++) {
               ModelPart.Vertex $$13 = p_104362_[$$12];
               p_104362_[$$12] = p_104362_[$$11 - 1 - $$12];
               p_104362_[$$11 - 1 - $$12] = $$13;
            }
         }

         this.f_104360_ = p_104370_.m_253071_();
         if (p_104369_) {
            this.f_104360_.mul(-1.0F, 1.0F, 1.0F);
         }
      }
   }

   @OnlyIn(Dist.CLIENT)
   static class Vertex {
      public final Vector3f f_104371_;
      public final float f_104372_;
      public final float f_104373_;

      public Vertex(float p_104375_, float p_104376_, float p_104377_, float p_104378_, float p_104379_) {
         this(new Vector3f(p_104375_, p_104376_, p_104377_), p_104378_, p_104379_);
      }

      public ModelPart.Vertex m_104384_(float p_104385_, float p_104386_) {
         return new ModelPart.Vertex(this.f_104371_, p_104385_, p_104386_);
      }

      public Vertex(Vector3f p_253667_, float p_253662_, float p_254308_) {
         this.f_104371_ = p_253667_;
         this.f_104372_ = p_253662_;
         this.f_104373_ = p_254308_;
      }
   }
}
