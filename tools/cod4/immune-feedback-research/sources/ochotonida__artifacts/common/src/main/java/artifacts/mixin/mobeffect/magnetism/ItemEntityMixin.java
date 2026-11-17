package artifacts.mixin.mobeffect.magnetism;

import artifacts.extensions.mobeffect.magnetism.ItemEntityExtensions;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.item.ItemEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;

import java.util.UUID;

@Mixin(ItemEntity.class)
public class ItemEntityMixin implements ItemEntityExtensions {

    @Unique
    private UUID artifacts$thrower;

    @Override
    public void artifacts$setThrower(LivingEntity entity) {
        artifacts$thrower = entity.getUUID();
    }

    @Override
    public boolean artifacts$wasThrownBy(LivingEntity entity) {
        return entity.getUUID().equals(artifacts$thrower);
    }
}
