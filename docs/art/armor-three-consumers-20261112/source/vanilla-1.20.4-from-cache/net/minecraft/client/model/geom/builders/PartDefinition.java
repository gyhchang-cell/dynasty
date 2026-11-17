package net.minecraft.client.model.geom.builders;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.Maps;
import it.unimi.dsi.fastutil.objects.Object2ObjectArrayMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class PartDefinition {
   private final List<CubeDefinition> f_171577_;
   private final PartPose f_171578_;
   private final Map<String, PartDefinition> f_171579_ = Maps.newHashMap();

   PartDefinition(List<CubeDefinition> p_171581_, PartPose p_171582_) {
      this.f_171577_ = p_171581_;
      this.f_171578_ = p_171582_;
   }

   public PartDefinition m_171599_(String p_171600_, CubeListBuilder p_171601_, PartPose p_171602_) {
      PartDefinition partdefinition = new PartDefinition(p_171601_.m_171557_(), p_171602_);
      PartDefinition partdefinition1 = this.f_171579_.put(p_171600_, partdefinition);
      if (partdefinition1 != null) {
         partdefinition.f_171579_.putAll(partdefinition1.f_171579_);
      }

      return partdefinition;
   }

   public ModelPart m_171583_(int p_171584_, int p_171585_) {
      Object2ObjectArrayMap<String, ModelPart> object2objectarraymap = this.f_171579_.entrySet().stream().collect(Collectors.toMap(Map.Entry::getKey, (p_171593_) -> {
         return p_171593_.getValue().m_171583_(p_171584_, p_171585_);
      }, (p_171595_, p_171596_) -> {
         return p_171595_;
      }, Object2ObjectArrayMap::new));
      List<ModelPart.Cube> list = this.f_171577_.stream().map((p_171589_) -> {
         return p_171589_.m_171455_(p_171584_, p_171585_);
      }).collect(ImmutableList.toImmutableList());
      ModelPart modelpart = new ModelPart(list, object2objectarraymap);
      modelpart.m_233560_(this.f_171578_);
      modelpart.m_171322_(this.f_171578_);
      return modelpart;
   }

   public PartDefinition m_171597_(String p_171598_) {
      return this.f_171579_.get(p_171598_);
   }
}
