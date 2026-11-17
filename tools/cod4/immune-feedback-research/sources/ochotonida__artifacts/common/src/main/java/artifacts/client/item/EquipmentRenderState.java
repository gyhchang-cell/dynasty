package artifacts.client.item;

import artifacts.extensions.client.LivingEntityRenderStateExtensions;
import artifacts.extensions.item.pocketpiston.LivingEntityExtensions;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import net.minecraft.world.entity.LivingEntity;

public class EquipmentRenderState {

    public float pocketPistonExtensionLength;

    public static EquipmentRenderState from(LivingEntityRenderState renderState) {
        return ((LivingEntityRenderStateExtensions) renderState).artifacts$getEquipment();
    }

    public void extractPocketPistonExtensionLength(LivingEntity entity, float partialTicks) {
        pocketPistonExtensionLength = ((LivingEntityExtensions) entity).artifacts$getPocketPistonLength(partialTicks);
    }
}
