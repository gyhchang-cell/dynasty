package artifacts.integration.accessories;

import artifacts.client.item.renderer.ArtifactRenderer;
import artifacts.equipment.client.EquipmentRenderingHandler;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.world.entity.HumanoidArm;
import net.minecraft.world.item.Item;
import org.jetbrains.annotations.Nullable;

import java.util.function.Supplier;

public class AccessoriesRenderingHandler implements EquipmentRenderingHandler {

    @Override
    public void registerArtifactRenderer(Item item, Supplier<ArtifactRenderer> rendererSupplier) {
        /* FIXME: Accessories 26.1+
        Identifier id = BuiltInRegistries.ITEM.getKey(item);
        AccessoriesRendererRegistry.bindItemToRenderer(item, id, () -> new ArtifactAccessoryRenderer(rendererSupplier.get()));
        */
    }

    @Override
    public @Nullable ArtifactRenderer getArtifactRenderer(Item item) {
        /* FIXME: Accessories 26.1+
        AccessoryRenderer renderer = AccessoriesRendererRegistry.getRenderer(item);
        if (renderer instanceof ArtifactAccessoryRenderer artifactAccessoryRenderer) {
            return artifactAccessoryRenderer.renderer();
        }
        */
        return null;
    }

    @Override
    public void renderArm(PoseStack poseStack, SubmitNodeCollector submitNodeCollector, int packedLight, AbstractClientPlayer player, HumanoidArm side) {
        // NO-OP SEE shouldRenderInFirstPerson below
    }

    /* FIXME: Accessories 26.1+
    public record ArtifactAccessoryRenderer(ArtifactRenderer renderer) implements AccessoryRenderer {

        @Override
        public <S extends LivingEntityRenderState> void render(ItemStack stack, SlotPath path, PoseStack matrices, EntityModel<S> model, S renderState, MultiBufferSource multiBufferSource, int packedLight, float partialTicks) {
            renderer.renderVisible(stack, reference.entity(), reference.slot(), matrices, multiBufferSource, packedLight, limbSwing, limbSwingAmount, partialTicks, ageInTicks, netHeadYaw, headPitch);
        }

        @Override
        public <S extends LivingEntityRenderState> void renderOnFirstPerson(HumanoidArm side, ItemStack stack, SlotPath path, PoseStack matrices, EntityModel<S> model, S renderState, MultiBufferSource multiBufferSource, int packedLight, float partialTicks) {
            if (!(reference.entity() instanceof LocalPlayer player)) {
                return;
            }
            InteractionHand hand = side == player.getMainArm() ? InteractionHand.MAIN_HAND : InteractionHand.OFF_HAND;

            GloveArtifactRenderer gloveRenderer = GloveArtifactRenderer.getGloveRenderer(stack);

            if (gloveRenderer != null && path.index() % 2 == (hand == InteractionHand.MAIN_HAND ? 0 : 1)) {
                gloveRenderer.renderFirstPersonArm(matrices, multiBufferSource, packedLight, (AbstractClientPlayer) reference.entity(), side, stack.hasFoil());
            }
        }
    }
    */
}
