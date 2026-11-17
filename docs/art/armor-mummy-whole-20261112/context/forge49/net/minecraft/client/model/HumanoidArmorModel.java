package net.minecraft.client.model;

import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class HumanoidArmorModel<T extends LivingEntity> extends HumanoidModel<T> {
   public HumanoidArmorModel(ModelPart p_270765_) {
      super(p_270765_);
   }

   public static MeshDefinition m_269566_(CubeDeformation p_270527_) {
      MeshDefinition meshdefinition = HumanoidModel.m_170681_(p_270527_, 0.0F);
      PartDefinition partdefinition = meshdefinition.m_171576_();
      partdefinition.m_171599_("right_leg", CubeListBuilder.m_171558_().m_171514_(0, 16).m_171488_(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, p_270527_.m_171469_(-0.1F)), PartPose.m_171419_(-1.9F, 12.0F, 0.0F));
      partdefinition.m_171599_("left_leg", CubeListBuilder.m_171558_().m_171514_(0, 16).m_171480_().m_171488_(-2.0F, 0.0F, -2.0F, 4.0F, 12.0F, 4.0F, p_270527_.m_171469_(-0.1F)), PartPose.m_171419_(1.9F, 12.0F, 0.0F));
      return meshdefinition;
   }
}
