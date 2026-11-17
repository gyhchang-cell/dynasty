package artifacts.neoforge.mixin.ability.slipresistance;

import artifacts.event.ArtifactHooks;
import com.llamalad7.mixinextras.injector.wrapoperation.Operation;
import com.llamalad7.mixinextras.injector.wrapoperation.WrapOperation;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;

@Mixin(LivingEntity.class)
public abstract class LivingEntityMixin extends Entity {

    public LivingEntityMixin(EntityType<?> entityType, Level level) {
        super(entityType, level);
        throw new UnsupportedOperationException();
    }

    @WrapOperation(method = "travelInAir", at = @At(value = "INVOKE", target = "Lnet/minecraft/world/level/block/state/BlockState;getFriction(Lnet/minecraft/world/level/LevelReader;Lnet/minecraft/core/BlockPos;Lnet/minecraft/world/entity/Entity;)F"))
    public float travel(BlockState state, LevelReader level, BlockPos pos, Entity entity, Operation<Float> original) {
        return ArtifactHooks.getModifiedFriction(
                original.call(state, level, pos, entity),
                (LivingEntity) (Object) this,
                state.getBlock()
        );
    }
}
