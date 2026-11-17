package artifacts.extensions.mobeffect.magnetism;

import net.minecraft.world.entity.LivingEntity;

public interface ItemEntityExtensions {

    void artifacts$setThrower(LivingEntity entity);

    boolean artifacts$wasThrownBy(LivingEntity entity);
}
