package net.minecraft.client.renderer.entity;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class TippableArrowRenderer extends ArrowRenderer<Arrow> {
   public static final ResourceLocation f_116132_ = new ResourceLocation("textures/entity/projectiles/arrow.png");
   public static final ResourceLocation f_116133_ = new ResourceLocation("textures/entity/projectiles/tipped_arrow.png");

   public TippableArrowRenderer(EntityRendererProvider.Context p_174422_) {
      super(p_174422_);
   }

   public ResourceLocation m_5478_(Arrow p_116140_) {
      return p_116140_.m_36889_() > 0 ? f_116133_ : f_116132_;
   }
}
