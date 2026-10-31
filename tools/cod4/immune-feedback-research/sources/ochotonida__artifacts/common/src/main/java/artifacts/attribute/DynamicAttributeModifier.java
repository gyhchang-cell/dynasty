package artifacts.attribute;

import artifacts.Artifacts;
import artifacts.component.ability.EntityCondition;
import artifacts.item.UmbrellaHelper;
import artifacts.registry.ModAttributes;
import net.minecraft.core.Holder;
import net.minecraft.resources.Identifier;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.OwnableEntity;
import net.minecraft.world.entity.PlayerRideable;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;

import java.util.Objects;

public abstract class DynamicAttributeModifier {

    private static final DynamicAttributeModifier MOUNT_SPEED = new DynamicAttributeModifier(
            Artifacts.id("mount_speed"),
            Attributes.MOVEMENT_SPEED,
            AttributeModifier.Operation.ADD_MULTIPLIED_BASE
    ) {
        @Override
        protected boolean shouldApply(LivingEntity entity) {
            return entity.getControllingPassenger() != null;
        }

        @Override
        protected double getAmount(LivingEntity entity) {
            return Objects.requireNonNull(entity.getControllingPassenger()).getAttributeValue(ModAttributes.MOUNT_SPEED) - 1;
        }
    };

    private static final DynamicAttributeModifier SPRINTING_SPEED = new DynamicAttributeModifier(
            Artifacts.id("sprinting_speed"),
            Attributes.MOVEMENT_SPEED,
            AttributeModifier.Operation.ADD_MULTIPLIED_BASE
    ) {
        @Override
        protected boolean shouldApply(LivingEntity entity) {
            return entity.isSprinting();
        }

        @Override
        protected double getAmount(LivingEntity entity) {
            return entity.getAttributeValue(ModAttributes.SPRINTING_SPEED) - 1;
        }
    };

    private static final DynamicAttributeModifier SPRINTING_STEP_HEIGHT = new DynamicAttributeModifier(
            Artifacts.id("sprinting_step_height"),
            Attributes.STEP_HEIGHT,
            AttributeModifier.Operation.ADD_VALUE
    ) {
        @Override
        protected boolean shouldApply(LivingEntity entity) {
            return entity.isSprinting();
        }

        @Override
        protected double getAmount(LivingEntity entity) {
            return entity.getAttributeValue(ModAttributes.SPRINTING_STEP_HEIGHT);
        }
    };

    private static final DynamicAttributeModifier UMBRELLA_GRAVITY = new DynamicAttributeModifier(
            Artifacts.id("umbrella_gravity"),
            Attributes.GRAVITY,
            AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL
    ) {
        @Override
        protected boolean shouldApply(LivingEntity entity) {
            return UmbrellaHelper.shouldGlide(entity);
        }

        @Override
        protected double getAmount(LivingEntity entity) {
            return -0.875D;
        }
    };

    private static final DynamicAttributeModifier MOVEMENT_SPEED_ON_SNOW = new DynamicAttributeModifier(
            Artifacts.id("movement_speed_on_snow"),
            Attributes.MOVEMENT_SPEED,
            AttributeModifier.Operation.ADD_MULTIPLIED_BASE
    ) {
        @Override
        protected boolean shouldApply(LivingEntity entity) {
            if (entity.getAttributeValue(ModAttributes.MOVEMENT_SPEED_ON_SNOW) != 1) {
                return EntityCondition.ON_SNOW.test(entity);
            }
            return false;
        }

        @Override
        protected double getAmount(LivingEntity entity) {
            return entity.getAttributeValue(ModAttributes.MOVEMENT_SPEED_ON_SNOW) - 1;
        }
    };

    private final Holder<Attribute> attribute;
    private final AttributeModifier.Operation operation;
    private final Identifier id;

    public DynamicAttributeModifier(Identifier id, Holder<Attribute> attribute, AttributeModifier.Operation operation) {
        this.attribute = attribute;
        this.operation = operation;
        this.id = id;
    }

    protected abstract boolean shouldApply(LivingEntity entity);

    protected abstract double getAmount(LivingEntity entity);

    private void tick(LivingEntity entity) {
        AttributeInstance attributeInstance = entity.getAttribute(attribute);
        if (attributeInstance == null) {
            return;
        }
        if (shouldApply(entity)) {
            double amount = getAmount(entity);
            AttributeModifier modifier = attributeInstance.getModifier(id);
            if (modifier == null || modifier.amount() != amount) {
                attributeInstance.addOrUpdateTransientModifier(new AttributeModifier(id, amount, operation));
            }
        } else if (attributeInstance.hasModifier(id)) {
            attributeInstance.removeModifier(id);
        }
    }

    private static boolean shouldUpdateModifiers(LivingEntity entity) {
        if (entity.tickCount % 10 != 0) {
            return entity instanceof Player || entity.getControllingPassenger() instanceof Player;
        } else if (
                entity instanceof Mob mob && mob.getTarget() != null
                || entity instanceof OwnableEntity ownable && ownable.getOwner() instanceof Player
        ) {
            return true;
        } else {
            return entity.tickCount % 20 == 0;
        }
    }

    public static void tickModifiers(LivingEntity entity) {
        if (!shouldUpdateModifiers(entity)) {
            return;
        }
        if (entity.canSprint()) {
            SPRINTING_SPEED.tick(entity);
            SPRINTING_STEP_HEIGHT.tick(entity);
        }
        if (entity instanceof Player player && player.getAbilities().flying || entity.onGround() || entity.isFallFlying()) {
            MOVEMENT_SPEED_ON_SNOW.tick(entity);
        }
        if (entity instanceof Player) {
            UMBRELLA_GRAVITY.tick(entity);
        }
        if (entity instanceof PlayerRideable) {
            MOUNT_SPEED.tick(entity);
        }
    }
}
