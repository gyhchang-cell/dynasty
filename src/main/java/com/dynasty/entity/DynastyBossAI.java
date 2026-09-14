package com.dynasty.entity;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.entity.projectile.WitherSkull;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

/**
 * Boss 战斗工具箱：预警、冲锋、瞬移、落雷、远程、召唤上限、狂暴。
 *
 * 目标是让 Boss 战从「站着互砍」变成有节奏的对抗：大招前 1 秒先给预警
 * （粒子 + 音效）让玩家有机会躲；玩家放风筝时 Boss 会瞬移追上来；
 * 召唤小怪有数量上限，避免卡顿。
 *
 * Boss combat toolbox: telegraphed attacks, dashes, blinks, lightning, ranged
 * pressure, summon caps and enrage.
 */
@SuppressWarnings("null")
public final class DynastyBossAI {

    private DynastyBossAI() {
    }

    /** 攻击预警：粒子 + 低吼，给玩家 1 秒反应时间 / warning before a big hit */
    public static void telegraph(Level level, LivingEntity boss, double radius, SoundEvent sound) {
        if (!(level instanceof ServerLevel server)) {
            return;
        }
        server.sendParticles(ParticleTypes.CRIT, boss.getX(), boss.getY() + 1.2D, boss.getZ(),
                40, radius * 0.6D, 0.4D, radius * 0.6D, 0.05D);
        server.sendParticles(ParticleTypes.SMOKE, boss.getX(), boss.getY() + 0.3D, boss.getZ(),
                25, radius * 0.5D, 0.2D, radius * 0.5D, 0.01D);
        boss.playSound(sound, 1.6F, 0.8F);
    }

    /** 冲锋：朝目标突进并撞飞 / dash into the target */
    public static void dash(LivingEntity boss, LivingEntity target, double power) {
        Vec3 dir = new Vec3(target.getX() - boss.getX(), 0.0D, target.getZ() - boss.getZ());
        if (dir.lengthSqr() < 1.0E-4D) {
            return;
        }
        dir = dir.normalize().scale(power);
        boss.setDeltaMovement(dir.x, Math.max(0.35D, boss.getDeltaMovement().y), dir.z);
        boss.hurtMarked = true;
        target.knockback(1.2D, boss.getX() - target.getX(), boss.getZ() - target.getZ());
        boss.playSound(SoundEvents.RAVAGER_ROAR, 2.0F, 1.1F);
    }

    /** 追到目标身后（防止被一直放风筝）/ blink behind a fleeing target */
    public static void blinkBehind(LivingEntity boss, LivingEntity target) {
        Vec3 look = target.getLookAngle();
        double x = target.getX() + look.x * 2.0D;
        double z = target.getZ() + look.z * 2.0D;
        if (boss.randomTeleport(x, target.getY(), z, true)) {
            boss.playSound(SoundEvents.ENDERMAN_TELEPORT, 1.5F, 0.7F);
            if (boss.level() instanceof ServerLevel server) {
                server.sendParticles(ParticleTypes.PORTAL, target.getX(), target.getY() + 1.0D,
                        target.getZ(), 40, 0.6D, 0.8D, 0.6D, 0.2D);
            }
        }
    }

    /** 脱离：被贴身时闪开一段距离 / blink away when someone hugs the boss */
    public static void blinkAway(LivingEntity boss, LivingEntity from, double distance) {
        double dx = boss.getX() - from.getX();
        double dz = boss.getZ() - from.getZ();
        if (Math.abs(dx) < 1.0E-3D && Math.abs(dz) < 1.0E-3D) {
            dx = boss.getRandom().nextDouble() - 0.5D;
            dz = boss.getRandom().nextDouble() - 0.5D;
        }
        double len = Math.max(1.0E-3D, Math.sqrt(dx * dx + dz * dz));
        if (boss.randomTeleport(boss.getX() + dx / len * distance, boss.getY(),
                boss.getZ() + dz / len * distance, true)) {
            boss.playSound(SoundEvents.ENDERMAN_TELEPORT, 1.4F, 1.3F);
        }
    }

    /** 落雷：目标脚下劈一道雷（带伤害）/ lightning strike under the target */
    public static void callLightning(Level level, LivingEntity target, float damage) {
        if (!(level instanceof ServerLevel server)) {
            return;
        }
        var lightning = net.minecraft.world.entity.EntityType.LIGHTNING_BOLT.create(server);
        if (lightning != null) {
            lightning.moveTo(target.getX(), target.getY(), target.getZ());
            lightning.setVisualOnly(true);
            server.addFreshEntity(lightning);
        }
        target.hurt(server.damageSources().lightningBolt(), damage);
    }

    /** 掷矛：远程消耗 / thrown spear */
    public static void shootSpear(LivingEntity boss, LivingEntity target, float damage) {
        Arrow arrow = new Arrow(boss.level(), boss);
        arrow.setBaseDamage(damage);
        arrow.setKnockback(2);
        Vec3 dir = new Vec3(target.getX() - boss.getX(), target.getEyeY() - boss.getEyeY() - 0.2D,
                target.getZ() - boss.getZ());
        arrow.shoot(dir.x, dir.y, dir.z, 2.2F, 1.0F);
        boss.level().addFreshEntity(arrow);
        boss.playSound(SoundEvents.ARROW_SHOOT, 1.4F, 0.8F);
    }

    /** 凋零之首：亡灵系远程 / wither skull */
    public static void shootWitherSkull(LivingEntity boss, LivingEntity target) {
        Vec3 dir = new Vec3(target.getX() - boss.getX(), target.getEyeY() - boss.getEyeY(),
                target.getZ() - boss.getZ()).normalize();
        WitherSkull skull = new WitherSkull(boss.level(), boss, dir.x, dir.y, dir.z);
        skull.moveTo(boss.getX(), boss.getEyeY() - 0.2D, boss.getZ(), 0.0F, 0.0F);
        boss.level().addFreshEntity(skull);
        boss.playSound(SoundEvents.WITHER_SHOOT, 1.5F, 0.9F);
    }

    /** 毒雾：范围中毒 + 减速 / poison cloud */
    public static void poisonCloud(Level level, LivingEntity boss, double radius) {
        for (Player player : level.getEntitiesOfClass(Player.class, boss.getBoundingBox().inflate(radius))) {
            player.addEffect(new MobEffectInstance(MobEffects.POISON, 140, 0));
            player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 120, 0));
        }
        if (level instanceof ServerLevel server) {
            server.sendParticles(ParticleTypes.ENTITY_EFFECT, boss.getX(), boss.getY() + 1.0D, boss.getZ(),
                    80, radius * 0.5D, 0.6D, radius * 0.5D, 0.0D);
        }
        boss.playSound(SoundEvents.WITCH_DRINK, 1.4F, 0.7F);
    }

    /** 召唤上限：附近小弟太多就不再召 / summon cap so fights stay smooth */
    public static boolean tooManyMinions(Level level, LivingEntity boss, double radius, int cap) {
        var nearby = level.getEntitiesOfClass(Mob.class, boss.getBoundingBox().inflate(radius),
                mob -> mob != boss && mob.isAlive() && mob.getType() != boss.getType() && isAlly(mob));
        return nearby.size() >= cap;
    }

    /** 激励：附近友军获得力量 / rally allied mobs */
    public static void rally(Level level, LivingEntity boss, double radius) {
        for (Mob mob : level.getEntitiesOfClass(Mob.class, boss.getBoundingBox().inflate(radius),
                mob -> mob.isAlive() && isAlly(mob))) {
            mob.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 200, 1, false, false));
        }
        boss.playSound(SoundEvents.RAVAGER_ROAR, 2.0F, 0.7F);
    }

    /** 狂暴：残血时提速增伤 / enrage at low health */
    public static void enrage(LivingEntity boss, int amplifier) {
        boss.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, Integer.MAX_VALUE, amplifier, false, false));
        boss.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, Integer.MAX_VALUE,
                amplifier / 2 + 1, false, false));
        boss.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, Integer.MAX_VALUE, 0, false, false));
        if (boss.level() instanceof ServerLevel server) {
            server.sendParticles(ParticleTypes.ANGRY_VILLAGER, boss.getX(), boss.getY() + 2.0D, boss.getZ(),
                    30, 0.6D, 0.6D, 0.6D, 0.0D);
        }
        boss.playSound(SoundEvents.WITHER_SPAWN, 1.6F, 0.8F);
    }

    /** 本次攻击的伤害（按攻击力比例）/ damage for one hit */
    public static float damage(LivingEntity boss, float factor) {
        // 没有攻击力属性的实体（盔甲架之类）也走这里，取不到就按 1 点算，绝不抛异常
        double attack = com.dynasty.DynastyAttributes.value(boss, Attributes.ATTACK_DAMAGE, 1.0D);
        return (float) Math.max(1.0D, attack * factor);
    }

    /** 同一个模组的生物算友军 / same-mod mobs count as allies */
    private static boolean isAlly(Mob mob) {
        var id = net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getKey(mob.getType());
        return id != null && id.getNamespace().equals(com.dynasty.Dynasty.MODID);
    }
}

