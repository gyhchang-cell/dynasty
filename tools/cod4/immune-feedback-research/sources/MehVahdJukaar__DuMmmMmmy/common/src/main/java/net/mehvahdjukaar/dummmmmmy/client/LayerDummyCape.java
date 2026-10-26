package net.mehvahdjukaar.dummmmmmy.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.mehvahdjukaar.dummmmmmy.common.TargetDummyEntity;
import net.mehvahdjukaar.dummmmmmy.configs.ClientConfigs;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.blockentity.BannerRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.ItemRenderer;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.resources.model.ModelBakery;
import net.minecraft.core.component.DataComponents;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.item.BannerItem;
import net.minecraft.world.item.DyeColor;
import net.minecraft.world.item.ElytraItem;
import net.minecraft.world.item.ItemStack;

public class LayerDummyCape extends RenderLayer<TargetDummyEntity, TargetDummyModel<TargetDummyEntity>> {

    private final ItemRenderer itemRenderer;
    private final ModelPart flag;

    public LayerDummyCape(RenderLayerParent<TargetDummyEntity, TargetDummyModel<TargetDummyEntity>> renderer,
                          EntityRendererProvider.Context context,
                          ItemRenderer itemRenderer) {
        super(renderer);
        this.itemRenderer = itemRenderer;

        ModelPart modelPart = context.bakeLayer(ModelLayers.BANNER);
        this.flag = modelPart.getChild("flag");
    }

    @Override
    public void render(PoseStack poseStack, MultiBufferSource bufferSource, int packedLight,
                       TargetDummyEntity livingEntity, float limbSwing, float limbSwingAmount, float partialTicks,
                       float ageInTicks, float netHeadYaw, float headPitch) {
        if (!livingEntity.isInvisible()) {
            ItemStack banner = livingEntity.getOffhandItem();

            if (banner.getItem() instanceof BannerItem bi) {

                poseStack.pushPose();
                float scale = 0.5f;
                var head = getParentModel().getHead();
                poseStack.translate(head.x / 16.0F, head.y / 16.0F, head.z / 16.0F);
                poseStack.translate(0, 0, 2 / 16f);


                float bodyXRot = getParentModel().getBody().xRot;

                float capeRest = 0.08f;

                float phase = livingEntity.getShake(partialTicks);
                float unscaledSwingAmount = livingEntity.getAnimationPosition(partialTicks);
                float swingAmount = Math.min((float) (unscaledSwingAmount * ClientConfigs.ANIMATION_INTENSITY.get()), 40f);
                float capeSwingAngle = capeRest + (1 - capeRest - Mth.sin(phase)) * 0.02f * swingAmount;

                float naturalSwayPhase = ((float) Math.floorMod(livingEntity.tickCount, 100L) + partialTicks) / 100.0F;
                float naturalSway = 0.005F * Mth.cos(Mth.TWO_PI * naturalSwayPhase) * Mth.PI;
                capeSwingAngle += naturalSway;

                poseStack.mulPose(Axis.XP.rotation((bodyXRot + Mth.PI + Math.max(0, capeSwingAngle))));
                poseStack.scale(-scale, -scale, 1);
                float dz;
                ItemStack chestSlot = livingEntity.getItemBySlot(EquipmentSlot.CHEST);
                if(chestSlot.isEmpty() || (chestSlot.getItem() instanceof ElytraItem)){
                    dz = 1/16f;
                }
                else dz = 0;
                poseStack.translate(0, 0, dz);

                DyeColor dyeColor = bi.getColor();
                var patterns = banner.get(DataComponents.BANNER_PATTERNS);

                BannerRenderer.renderPatterns(poseStack, bufferSource, packedLight, OverlayTexture.NO_OVERLAY, this.flag,
                        ModelBakery.BANNER_BASE, true, dyeColor, patterns);

                poseStack.popPose();
            }
        }
    }


}