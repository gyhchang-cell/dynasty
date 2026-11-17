package net.mehvahdjukaar.dummmmmmy.client;

import com.mojang.blaze3d.vertex.PoseStack;
import net.mehvahdjukaar.dummmmmmy.DummmmmmyClient;
import net.mehvahdjukaar.dummmmmmy.common.TargetDummyEntity;
import net.mehvahdjukaar.dummmmmmy.configs.ClientConfigs;
import net.mehvahdjukaar.moonlight.api.platform.PlatHelper;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.debug.DebugRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.HumanoidMobRenderer;
import net.minecraft.client.renderer.entity.layers.ElytraLayer;
import net.minecraft.client.renderer.entity.layers.ItemInHandLayer;
import net.minecraft.resources.ResourceLocation;

public class TargetDummyRenderer extends HumanoidMobRenderer<TargetDummyEntity, TargetDummyModel<TargetDummyEntity>> {

    public TargetDummyRenderer(EntityRendererProvider.Context context) {
        super(context, new TargetDummyModel<>(context.bakeLayer(DummmmmmyClient.DUMMY_BODY)), 0);
        this.addLayer(new LayerDummyArmor<>(this,
                new TargetDummyModel<>(context.bakeLayer(DummmmmmyClient.DUMMY_ARMOR_INNER)),
                new TargetDummyModel<>(context.bakeLayer(DummmmmmyClient.DUMMY_ARMOR_OUTER)),
                context.getModelManager()));
        this.layers.removeIf(layer -> (layer instanceof ItemInHandLayer || layer instanceof ElytraLayer));
        this.addLayer(new LayerDummyShield(this, context.getItemInHandRenderer()));
        this.addLayer(new LayerDummyCape(this, context, context.getItemRenderer()));
        this.addLayer(new LayerDummyElytra(this, context.getModelSet()));
    }

    @Override
    public void render(TargetDummyEntity entity, float entityYaw, float partialTicks, PoseStack poseStack, MultiBufferSource buffer, int packedLight) {
        super.render(entity, entityYaw, partialTicks, poseStack, buffer, packedLight);

        if (PlatHelper.isDev()) {
            //DebugRenderer.renderFloatingText(poseStack, buffer, entity.getMobType().name(), entity.xo, entity.yo + 5, entity.zo, -1);
        }
    }

    @Override
    public ResourceLocation getTextureLocation(TargetDummyEntity entity) {
        return ClientConfigs.SKIN.get().getSkin(entity.isSheared());
    }

}
