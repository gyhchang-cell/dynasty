package artifacts.component.ability;

import artifacts.integration.ModCompat;
import artifacts.integration.origins.OriginsCompat;
import artifacts.registry.ModTags;
import com.mojang.serialization.Codec;
import io.netty.buffer.ByteBuf;
import net.minecraft.core.BlockPos;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.tags.TagKey;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.Fluid;

import java.util.function.Predicate;

public enum EntityCondition implements StringRepresentable {
    ALWAYS("always", _ -> true),
    NEVER("never", _ -> false),
    ABOVE_WATER("above_water", entity -> !entity.isUnderWater()),
    IN_WATER("in_water", Entity::isInWater),
    UNDER_WATER("under_water", Entity::isUnderWater),
    REPLENISHING_AIR("replenishing_air", EntityCondition::canBreathe),
    LOSING_AIR("losing_air", entity -> !canBreathe(entity)),
    SWIMMING("swimming", Entity::isSwimming),
    SWIM_FLYING("swim_flying", entity -> entity.isSwimming() && !entity.isInWater()),
    ON_GRASS("on_grass", entity -> entity.onGround() && entity.getBlockStateOn().is(ModTags.ROOTED_BOOTS_GRASS)),
    ON_SNOW("on_snow", EntityCondition::isOnSnow),
    ON_WATER("on_water", entity -> isOnFluid(entity, FluidTags.WATER)),
    ON_LAVA("on_lava", entity -> isOnFluid(entity, FluidTags.LAVA)),
    SNEAKING("sneaking", Entity::isCrouching),
    SPRINTING("sprinting", entity -> entity.isSprinting() && !entity.isUsingItem() && !entity.isCrouching()),
    RIDING_MOUNT("riding_mount", entity -> entity.getControlledVehicle() instanceof LivingEntity);

    public static final Codec<EntityCondition> CODEC = StringRepresentable.fromValues(EntityCondition::values);
    public static final StreamCodec<ByteBuf, EntityCondition> STREAM_CODEC = ByteBufCodecs.idMapper(i -> EntityCondition.values()[i], EntityCondition::ordinal);

    private final String name;
    private final Predicate<LivingEntity> predicate;

    EntityCondition(String name, Predicate<LivingEntity> predicate) {
        this.name = name;
        this.predicate = predicate;
    }

    public boolean test(LivingEntity entity) {
        return predicate.test(entity);
    }

    @Override
    public String getSerializedName() {
        return toString();
    }

    @Override
    public String toString() {
        return name;
    }

    private static boolean canBreathe(LivingEntity entity) {
        return entity.isUnderWater() == (ModCompat.ORIGINS.isLoaded() && OriginsCompat.hasWaterBreathing(entity));
    }

    private static boolean isOnFluid(LivingEntity entity, TagKey<Fluid> fluidTag) {
        BlockPos pos = entity.getOnPos();
        BlockState blockState = entity.getBlockStateOn();
        if (!entity.onGround() || entity.isInWater() || entity.isInLava() || !blockState.getFluidState().is(fluidTag)) {
            return false;
        }
        // Check that we're not standing on the dry part of a waterlogged block
        float fluidHeight = blockState.getFluidState().getHeight(entity.level(), pos);
        // Mth.equal is too precise, compensate for fudge factor added by expandability
        return Math.abs(entity.getY() % 1 - fluidHeight) < 1E-4F;
    }

    private static boolean isOnSnow(LivingEntity entity) {
        if (!entity.onGround()) {
            return false;
        }
        BlockState inState = entity.level().getBlockState(entity.getBlockPosBelowThatAffectsMyMovement().above());
        if (!inState.isAir() && inState.is(ModTags.SNOW_LAYERS)) {
            return true;
        }
        BlockState onState = entity.level().getBlockState(entity.getBlockPosBelowThatAffectsMyMovement());
        return onState.is(BlockTags.SNOW);
    }
}
