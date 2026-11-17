package artifacts.effect;

import artifacts.extensions.mobeffect.magnetism.ItemEntityExtensions;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

import java.util.List;

public class MagnetismMobEffect extends MobEffect {

    public MagnetismMobEffect() {
        super(MobEffectCategory.BENEFICIAL, 0x943dba);
    }

    @Override
    public boolean shouldApplyEffectTickThisTick(int duration, int amplifier) {
        return true;
    }

    @Override
    public boolean applyEffectTick(ServerLevel level, LivingEntity entity, int amplifier) {
        Vec3 pos = entity.position().add(0, 0.75, 0);

        int range = Math.min(1 + amplifier, 10);
        List<ItemEntity> items = entity.level().getEntitiesOfClass(ItemEntity.class, new AABB(pos.x - range, pos.y - range, pos.z - range, pos.x + range, pos.y + range, pos.z + range));
        int amountPulled = 0;
        for (ItemEntity item : items) {
            if (item.isAlive() && !item.hasPickUpDelay() && !((ItemEntityExtensions) item).artifacts$wasThrownBy(entity)) {
                if (amountPulled++ > 50) {
                    break;
                }

                Vec3 motion = pos.subtract(item.position().add(0, item.getBbHeight() / 2, 0));
                if (Math.sqrt(motion.x * motion.x + motion.y * motion.y + motion.z * motion.z) > 1) {
                    motion = motion.normalize();
                }
                item.setDeltaMovement(motion.scale(1));
            }
        }
        return true;
    }
}
