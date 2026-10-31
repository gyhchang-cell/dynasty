package artifacts.fabric.mixin.ability.creeperrepellent;

import artifacts.registry.ModDataComponents;
import artifacts.registry.ModTags;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.ai.goal.target.TargetGoal;
import net.minecraft.world.entity.ai.targeting.TargetingConditions;
import net.minecraft.world.entity.player.Player;
import org.jetbrains.annotations.Nullable;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

@Mixin(NearestAttackableTargetGoal.class)
public abstract class NearestAttackableTargetGoalMixin<T extends LivingEntity> extends TargetGoal {

    @Unique
    private static final TargetingConditions.Selector NOT_WEARING_KITTY_SLIPPERS = (entity, _) ->
            !ModDataComponents.CREEPER_REPELLENT.on(entity).findAny();

    @Shadow
    @Final
    protected Class<T> targetType;

    public NearestAttackableTargetGoalMixin(Mob mob, boolean checkVisibility) {
        super(mob, checkVisibility);
        throw new UnsupportedOperationException();
    }

    @ModifyArg(method = "<init>(Lnet/minecraft/world/entity/Mob;Ljava/lang/Class;IZZLnet/minecraft/world/entity/ai/targeting/TargetingConditions$Selector;)V", at = @At(value = "INVOKE", target = "Lnet/minecraft/world/entity/ai/targeting/TargetingConditions;selector(Lnet/minecraft/world/entity/ai/targeting/TargetingConditions$Selector;)Lnet/minecraft/world/entity/ai/targeting/TargetingConditions;"))
    private TargetingConditions.Selector addCreeperTargetPredicate(@Nullable TargetingConditions.Selector selector) {
        if (mob.is(ModTags.CREEPERS) && this.targetType == Player.class) {
            return selector == null
                    ? NOT_WEARING_KITTY_SLIPPERS
                    : (entity, level) -> selector.test(entity, level) && NOT_WEARING_KITTY_SLIPPERS.test(entity, level);
        }
        return selector;
    }
}
