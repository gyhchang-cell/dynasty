package net.minecraft.client.renderer.entity.layers;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.model.ArmedModel;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.ItemInHandRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class ItemInHandLayer<T extends LivingEntity, M extends EntityModel<T> & ArmedModel> extends RenderLayer<T, M> {
   private final ItemInHandRenderer f_234844_;

   public ItemInHandLayer(RenderLayerParent<T, M> p_234846_, ItemInHandRenderer p_234847_) {
      super(p_234846_);
      this.f_234844_ = p_234847_;
   }

   public void m_6494_(PoseStack p_117204_, MultiBufferSource p_117205_, int p_117206_, T p_117207_, float p_117208_, float p_117209_, float p_117210_, float p_117211_, float p_117212_, float p_117213_) {
      boolean flag = p_117207_.m_5737_() == HumanoidArm.RIGHT;
      ItemStack itemstack = flag ? p_117207_.m_21206_() : p_117207_.m_21205_();
      ItemStack itemstack1 = flag ? p_117207_.m_21205_() : p_117207_.m_21206_();
      if (!itemstack.m_41619_() || !itemstack1.m_41619_()) {
         p_117204_.m_85836_();
         if (this.m_117386_().f_102610_) {
            float f = 0.5F;
            p_117204_.m_252880_(0.0F, 0.75F, 0.0F);
            p_117204_.m_85841_(0.5F, 0.5F, 0.5F);
         }

         this.m_117184_(p_117207_, itemstack1, ItemDisplayContext.THIRD_PERSON_RIGHT_HAND, HumanoidArm.RIGHT, p_117204_, p_117205_, p_117206_);
         this.m_117184_(p_117207_, itemstack, ItemDisplayContext.THIRD_PERSON_LEFT_HAND, HumanoidArm.LEFT, p_117204_, p_117205_, p_117206_);
         p_117204_.m_85849_();
      }
   }

   protected void m_117184_(LivingEntity p_117185_, ItemStack p_117186_, ItemDisplayContext p_270970_, HumanoidArm p_117188_, PoseStack p_117189_, MultiBufferSource p_117190_, int p_117191_) {
      if (!p_117186_.m_41619_()) {
         p_117189_.m_85836_();
         this.m_117386_().m_6002_(p_117188_, p_117189_);
         p_117189_.m_252781_(Axis.f_252529_.m_252977_(-90.0F));
         p_117189_.m_252781_(Axis.f_252436_.m_252977_(180.0F));
         boolean flag = p_117188_ == HumanoidArm.LEFT;
         p_117189_.m_252880_((float)(flag ? -1 : 1) / 16.0F, 0.125F, -0.625F);
         this.f_234844_.m_269530_(p_117185_, p_117186_, p_270970_, flag, p_117189_, p_117190_, p_117191_);
         p_117189_.m_85849_();
      }
   }
}
