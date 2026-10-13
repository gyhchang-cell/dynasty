package com.dynasty.blueprint.boss;

import com.dynasty.blueprint.combat.CombatGeometry;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.syncher.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.*;
import net.minecraft.world.level.*;
import net.minecraft.world.phys.*;
import net.minecraftforge.network.NetworkHooks;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.*;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.util.UUID;

/** A real slow falling bomb. Only actual floor contact arms its short, visible fuse. */
public final class WoodKiteBomb extends Entity implements GeoEntity {
    private static final EntityDataAccessor<Boolean> LANDED = SynchedEntityData.defineId(WoodKiteBomb.class, EntityDataSerializers.BOOLEAN);
    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
    private UUID owner;
    private long born = -1, epoch = -1, lastTick = -1, contact = -1;
    private int fuse = 12;
    private float damage;
    private boolean spent;

    public WoodKiteBomb(EntityType<? extends WoodKiteBomb> type, Level world) { super(type, world); }
    @Override protected void defineSynchedData() { entityData.define(LANDED, false); }
    public boolean landed() { return entityData.get(LANDED); }
    public boolean ownedBy(WoodKite caster) { return caster.getUUID().equals(owner); }
    public void begin(WoodKite caster, int index) {
        owner = caster.getUUID(); born = level().getGameTime(); lastTick = born - 1;
        epoch = caster.bombEpoch(); fuse = 12 + 2 * Math.max(0, Math.min(7, index));
        double amount = caster.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.ATTACK_DAMAGE) * .8;
        damage = Double.isFinite(amount) ? (float)Math.max(0, Math.min(512, amount)) : 0;
        var forward = caster.getLookAngle().multiply(1, 0, 1).normalize();
        setPos(caster.position().subtract(forward.scale(.1875)).add(0, .35, 0));
        setDeltaMovement(0, -.035, 0);
    }
    @Override public void tick() {
        baseTick();
        if (!(level() instanceof ServerLevel world)) return;
        long now = world.getGameTime();
        var source = owner == null ? null : world.getEntity(owner);
        if (!(source instanceof WoodKite caster) || !caster.isAlive() || caster.bombEpoch() != epoch
                || spent || damage <= 0 || born < 0 || now < born || now - born >= 160
                || now < lastTick || lastTick >= 0 && now - lastTick > 1
                || caster.arenaCentre() == null || position().distanceToSqr(caster.centre()) > 32 * 32) {
            discard(); return;
        }
        lastTick = now;
        var fall = new Vec3(0, Math.max(-.18, getDeltaMovement().y - .035), 0);
        if (!caster.loaded(getBoundingBox().expandTowards(fall).inflate(3, 2, 3))) { discard(); return; }
        if (!landed()) {
            setDeltaMovement(fall); move(MoverType.SELF, fall);
            if (onGround()) { entityData.set(LANDED, true); contact = now; setDeltaMovement(Vec3.ZERO); }
        } else {
            // A removed or collapsed floor does not leave a floating armed mine.
            if (world.noCollision(this, getBoundingBox().move(0, -.06, 0))) { discard(); return; }
            if (contact < 0 || now < contact) { discard(); return; }
            if (now - contact >= fuse) { detonate(world, caster); return; }
            if ((now - contact) % 3 == 0) world.sendParticles(ParticleTypes.ELECTRIC_SPARK, getX(), getY() + .7, getZ(), 2, .1, .05, .1, .01);
        }
    }
    private void detonate(ServerLevel world, WoodKite caster) {
        spent = true; // Consumed before any damage callback, including thorns or caster death.
        var origin = position().add(0, .5, 0);
        for (var victim : CombatGeometry.query(world, origin, new Vec3(0, 0, 1), CombatGeometry.Shape.CIRCLE, 3, 0, 360, 1.5, caster::enemy).stream().limit(16).toList()) {
            if (!caster.isAlive() || caster.bombEpoch() != epoch || isRemoved()) break;
            if (victim.position().subtract(caster.centre()).multiply(1, 0, 1).lengthSqr() > 20 * 20
                    || world.clip(new ClipContext(origin, victim.getEyePosition(), ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, this)).getType() != HitResult.Type.MISS) continue;
            if (victim.hurt(caster.damageSources().explosion(this, caster), damage)) victim.knockback(.4, getX() - victim.getX(), getZ() - victim.getZ());
        }
        world.sendParticles(ParticleTypes.EXPLOSION, getX(), getY() + .5, getZ(), 1, 0, 0, 0, 0);
        world.sendParticles(ParticleTypes.ELECTRIC_SPARK, getX(), getY() + .5, getZ(), 8, .7, .4, .7, .03);
        discard();
    }
    @Override protected void addAdditionalSaveData(CompoundTag tag) {
        if (owner != null) tag.putUUID("Owner", owner);
        tag.putLong("Born", born); tag.putLong("Epoch", epoch); tag.putLong("LastTick", lastTick);
        tag.putLong("Contact", contact); tag.putInt("Fuse", fuse); tag.putFloat("Damage", damage);
        tag.putBoolean("Spent", spent); tag.putBoolean("Landed", landed());
    }
    @Override protected void readAdditionalSaveData(CompoundTag tag) {
        // Projectiles deliberately expire after reload; a delayed blast must never replay.
        owner = tag.hasUUID("Owner") ? tag.getUUID("Owner") : null;
        born = -1; epoch = -1; spent = true; setDeltaMovement(Vec3.ZERO);
    }
    @Override public boolean shouldRenderAtSqrDistance(double distance) { return Double.isFinite(distance) && distance < 96 * 96; }
    @Override protected MovementEmission getMovementEmission() { return MovementEmission.NONE; }
    @Override public Packet<ClientGamePacketListener> getAddEntityPacket() { return NetworkHooks.getEntitySpawningPacket(this); }
    @Override public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<WoodKiteBomb>(this, "bomb", 0, state -> {
            state.setAnimation(landed() ? RawAnimation.begin().thenPlayAndHold("animation.wood_kite_thunder_bomb.rest") : RawAnimation.begin().thenLoop("animation.wood_kite_thunder_bomb.idle"));
            return software.bernie.geckolib.core.object.PlayState.CONTINUE;
        }));
    }
    @Override public AnimatableInstanceCache getAnimatableInstanceCache() { return cache; }
}
