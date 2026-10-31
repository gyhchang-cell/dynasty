package artifacts.mixin.client;

import artifacts.client.item.EquipmentRenderState;
import artifacts.extensions.client.LivingEntityRenderStateExtensions;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;

@Mixin(LivingEntityRenderState.class)
public abstract class LivingEntityRenderStateMixin implements LivingEntityRenderStateExtensions {

    @Unique
    private final EquipmentRenderState artifacts$equipment = new EquipmentRenderState();

    @Override
    public EquipmentRenderState artifacts$getEquipment() {
        return artifacts$equipment;
    }
}
