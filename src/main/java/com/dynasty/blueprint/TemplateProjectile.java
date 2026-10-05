package com.dynasty.blueprint;

import com.dynasty.DynastyItems;
import com.dynasty.blueprint.combat.CombatGeometry;
import com.dynasty.blueprint.combat.Combatant;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.NetworkHooks;
import java.util.UUID;

/** Shared, bounded server projectile; the item renderer is only a visual representation. */
public final class TemplateProjectile extends ThrowableItemProjectile implements net.minecraftforge.entity.IEntityAdditionalSpawnData {
    private static final EntityDataAccessor<Boolean> ROCK = SynchedEntityData.defineId(TemplateProjectile.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Integer> ARMY_MODE = SynchedEntityData.defineId(TemplateProjectile.class, EntityDataSerializers.INT);
    private long actionEpoch=-1;
    private UUID target;
    private float damage = 4;
    private int lived;
    private boolean spent;

    public TemplateProjectile(EntityType<? extends TemplateProjectile> type, Level level) { super(type, level); }

    public static TemplateProjectile shoot(TemplateMob owner, LivingEntity victim, boolean rock, float damage) {
        TemplateProjectile projectile = new TemplateProjectile(BlueprintEntities.TEMPLATE_PROJECTILE.get(), owner.level());
        projectile.setOwner(owner);
        projectile.entityData.set(ROCK, rock);
        projectile.target = victim.getUUID();
        projectile.damage = damage;
        projectile.setItem(new ItemStack(rock ? Items.COBBLESTONE : DynastyItems.TALISMAN_PAPER.get()));
        projectile.setPos(owner.getX(), owner.getEyeY() - .1, owner.getZ());
        Vec3 aim = victim.getBoundingBox().getCenter().subtract(projectile.position());
        // The ballistic arc does not change terrain or turn into a reusable dropped item.
        if (rock) aim = aim.add(0, Math.sqrt(aim.horizontalDistanceSqr()) * .15, 0);
        projectile.shoot(aim.x, aim.y, aim.z, rock ? 1.05F : .7F, rock ? 1.5F : 2F);
        owner.level().addFreshEntity(projectile);
        return projectile;
    }

    public static TemplateProjectile shootArmy(TemplateMob owner,LivingEntity victim,boolean hook) {
        var projectile=new TemplateProjectile(BlueprintEntities.TEMPLATE_PROJECTILE.get(),owner.level());
        projectile.setOwner(owner);projectile.entityData.set(ARMY_MODE,hook?2:1);
        projectile.actionEpoch=owner.skillStartTime();projectile.target=victim.getUUID();
        projectile.damage=(float)owner.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.ATTACK_DAMAGE);
        projectile.setItem(new ItemStack(hook?Items.IRON_NUGGET:Items.ARROW));
        projectile.setPos(owner.getX(),owner.getEyeY()-.3,owner.getZ());
        Vec3 aim=(hook?victim.position().add(0,.25,0):victim.getBoundingBox().getCenter()).subtract(projectile.position());
        projectile.shoot(aim.x,aim.y,aim.z,hook?1.35F:1.65F,0);
        owner.level().addFreshEntity(projectile);return projectile;
    }
    public int armyMode(){return entityData.get(ARMY_MODE);}
    @Override protected void defineSynchedData() { super.defineSynchedData(); entityData.define(ROCK, false);entityData.define(ARMY_MODE,0); }
    @Override protected Item getDefaultItem() { return Items.PAPER; }
    public boolean isRock() { return entityData.get(ROCK); }
    @Override protected float getGravity() { return isRock() ? .045F : 0; }
    @Override public Packet<ClientGamePacketListener> getAddEntityPacket() { return NetworkHooks.getEntitySpawningPacket(this); }
    // Forge's custom spawn packet does not invoke vanilla Projectile.recreateFromPacket's
    // owner-data path. Supply it explicitly, so both observing clients know the thrower.
    @Override public void writeSpawnData(net.minecraft.network.FriendlyByteBuf buffer) {
        buffer.writeInt(getOwner() == null ? -1 : getOwner().getId());
    }
    @Override public void readSpawnData(net.minecraft.network.FriendlyByteBuf buffer) {
        int ownerId = buffer.readInt();
        if (ownerId >= 0) setOwner(level().getEntity(ownerId));
    }

    @Override public void tick() {
        if (level().isClientSide && armyMode()==0 && !isRock() && tickCount % 3 == 0)
            level().addParticle(net.minecraft.core.particles.ParticleTypes.SOUL_FIRE_FLAME, getX(), getY(), getZ(), 0, .005, 0);
        if (!level().isClientSide) {
            if (++lived > 100 || spent || getOwner() == null || !getOwner().isAlive()) { discard(); return; }
            if (armyMode()==0 && !isRock() && lived < 35 && target != null && level() instanceof ServerLevel server
                    && server.getEntity(target) instanceof LivingEntity victim && victim.isAlive()
                    && distanceToSqr(victim) < 32 * 32 && !Combatant.allied(getOwner(), victim)) {
                Vec3 desired = victim.getBoundingBox().getCenter().subtract(position()).normalize().scale(.7);
                // Small course corrections preserve a clear sidestep window instead of guaranteed hits.
                setDeltaMovement(getDeltaMovement().scale(.96).add(desired.scale(.04)));
            }
        }
        super.tick();
    }

    @Override protected boolean canHitEntity(Entity candidate) {
        return super.canHitEntity(candidate) && (getOwner() == null || !Combatant.allied(getOwner(), candidate));
    }

    @Override protected void onHit(HitResult result) {
        if (!(level() instanceof ServerLevel server) || spent || result.getType() == HitResult.Type.MISS) return;
        spent = true;
        Entity owner = getOwner();
        if (owner == null) { discard(); return; }
        if (armyMode()!=0) {
            if(result instanceof EntityHitResult hit&&hit.getEntity() instanceof LivingEntity living&&!Combatant.allied(owner,living)){
                if(armyMode()==2&&owner instanceof TemplateMob mob)mob.onArmyHookHit(living,actionEpoch);
                else {living.invulnerableTime=0;living.hurt(damageSources().thrown(this,owner),damage);}
            }
        } else if (isRock()) {
            for (LivingEntity hit : CombatGeometry.query(server, result.getLocation(), getDeltaMovement(), CombatGeometry.Shape.CIRCLE,
                    2.3, 0, 360, 2.0, e -> !Combatant.allied(owner, e) && !e.isInvulnerable())) {
                if (hit.hurt(damageSources().thrown(this, owner), damage)) {
                    Vec3 away = hit.position().subtract(result.getLocation());
                    hit.knockback(.9, -away.x, -away.z);
                    hit.stopUsingItem();
                    if (hit instanceof TemplateMob mob) mob.interruptAttack(8);
                }
            }
            server.sendParticles(net.minecraft.core.particles.ParticleTypes.POOF, getX(), getY(), getZ(), 9, .5, .25, .5, .05);
            playSound(net.minecraft.sounds.SoundEvents.STONE_BREAK, .8F, .8F);
        } else if (result instanceof EntityHitResult hit && hit.getEntity() instanceof LivingEntity living
                && !Combatant.allied(owner, living)) {
            living.hurt(damageSources().indirectMagic(this, owner), damage);
        }
        discard();
    }

    @Override public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("Rock", isRock()); tag.putFloat("Damage", damage); tag.putInt("Lived", lived); tag.putBoolean("Spent", spent);
        tag.putInt("ArmyMode",armyMode());tag.putLong("ArmyEpoch",actionEpoch);
        if (target != null) tag.putUUID("Target", target);
    }
    @Override public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        entityData.set(ROCK, tag.getBoolean("Rock")); damage = Math.max(0, Math.min(30, tag.getFloat("Damage")));
        lived = Math.max(0, tag.getInt("Lived")); spent = tag.getBoolean("Spent"); target = tag.hasUUID("Target") ? tag.getUUID("Target") : null;
        entityData.set(ARMY_MODE,Math.max(0,Math.min(2,tag.getInt("ArmyMode"))));actionEpoch=tag.contains("ArmyEpoch")?tag.getLong("ArmyEpoch"):-1;
    }
}
