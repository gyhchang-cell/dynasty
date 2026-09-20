package com.dynasty;

import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceKey;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.AABB;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.ForgeHooks;
import net.minecraftforge.network.PacketDistributor;
import com.dynasty.network.BowEffectPacket;
import com.dynasty.network.DynastyNetwork;
import java.util.ArrayList;
import java.util.List;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.ProjectileImpactEvent;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Vector3f;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.UUID;

/** 服务端同步的弓蓄力法阵。箭仍使用原版视角发射，视觉瞄准阵跟随玩家的完整视线向量。 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class DynastyBowRitual {
    private static final DustParticleOptions GOLD = dust(1.0F, 0.70F, 0.18F, 1.0F);
    private static final DustParticleOptions RED = dust(1.0F, 0.21F, 0.10F, 1.0F);
    private static final DustParticleOptions CYAN = dust(0.22F, 0.78F, 1.0F, 0.8F);
    private static final Map<UUID, Ward> WARDS = new HashMap<>();
    private static final Map<UUID, Long> WARD_READY_AT = new HashMap<>();
    private static final Map<UUID, Shot> ARROWS = new HashMap<>();
    private static final Map<UUID, Long> LAST_SHOT = new HashMap<>();
    private static final int FORM_TICKS = 20;
    private static final int WARD_TICKS = 120;
    private static final int WARD_COOLDOWN_TICKS = 200;
    public static final double WARD_RADIUS = 6.5D;
    private static final ResourceKey<DamageType> SOLAR_DAMAGE = ResourceKey.create(
            Registries.DAMAGE_TYPE, new ResourceLocation(Dynasty.MODID, "solar_judgment"));
    private static final List<Blast> BLASTS = new ArrayList<>();

    private DynastyBowRitual() {
    }

    private static DustParticleOptions dust(float red, float green, float blue, float size) {
        return new DustParticleOptions(new Vector3f(red, green, blue), size);
    }

    /** 视觉档位由弓自身的预估箭伤决定，数值越高，阵纹和箭迹越完整。 */
    public static int tier(double score) {
        if (score >= 300.0D) return 4;
        if (score >= 280.0D) return 3;
        if (score >= 200.0D) return 2;
        if (score >= 70.0D) return 1;
        return 0;
    }

    static void onCharge(ServerLevel server, Player player, Item bow, int ticks, double score) {
        // 阵纹由客户端连续绘制；服务端只处理真实护盾和推斥。
        if (tier(score) == 4 && ticks == FORM_TICKS) {
            activateWard(server, player, bow);
        }
        if (bow == DynastyWeapons.HOUYI_BOW.get() && ticks >= 5 && ticks % 10 == 0
                && player instanceof ServerPlayer serverPlayer) {
            clearAvatarSpace(server, serverPlayer, Math.min(1, ticks / 40.0D));
        }
    }

    private static void activateWard(ServerLevel server, Player player, Item bow) {
        UUID id = player.getUUID();
        long now = server.getGameTime();
        if (now < WARD_READY_AT.getOrDefault(id, 0L)) return;
        WARDS.put(id, new Ward(server.dimension(), bow, now + WARD_TICKS));
        WARD_READY_AT.put(id, now + WARD_TICKS + WARD_COOLDOWN_TICKS);
        Vec3 center = player.position().add(0.0D, 0.15D, 0.0D);
        server.sendParticles(ParticleTypes.END_ROD, center.x, center.y, center.z,
                12, 0.5D, 0.3D, 0.5D, 0.03D);
    }

    static void onRelease(ServerLevel server, Player player, Item bow, int ticks, double score) {
        WARDS.remove(player.getUUID());
        if (ticks < 3 || LAST_SHOT.getOrDefault(player.getUUID(), -1L) < server.getGameTime() - 1L) return;
        int tier = tier(score);
        Vec3 look = player.getLookAngle().normalize();
        Vec3 center = player.getEyePosition().add(look.scale(2.35D));
        if (tier >= 3) {
            server.sendParticles(ParticleTypes.FIREWORK, center.x, center.y, center.z,
                    tier * 2, 0.15D, 0.15D, 0.15D, 0.04D);
        }
    }

    static void trackArrow(AbstractArrow arrow, Item bow, double score) {
        if (!(arrow.level() instanceof ServerLevel server)) return;
        int tier = tier(score);
        boolean phoenix = bow == DynastyWeapons.ZHUQUE_BOW.get();
        ARROWS.put(arrow.getUUID(), new Shot(server.dimension(), tier, phoenix, server.getGameTime()));
        if (arrow.getOwner() instanceof Player player) {
            LAST_SHOT.put(player.getUUID(), server.getGameTime());
        }
    }

    @SubscribeEvent
    public static void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player.level() instanceof ServerLevel server)) return;
        Player player = event.player;
        UUID id = player.getUUID();
        Ward ward = WARDS.get(id);
        if (ward == null) return;
        if (!wardActive(server, player, ward)) {
            WARDS.remove(id);
            return;
        }
        if (server.getGameTime() % 4 == 0) pushCreatures(server, player);
    }

    private static boolean wardActive(ServerLevel server, Player player, Ward ward) {
        return ward.dimension().equals(server.dimension())
                && server.getGameTime() < ward.expiresAt()
                && player.isAlive()
                && player.isUsingItem() && player.getUseItem().is(ward.bow());
    }

    private static void pushCreatures(ServerLevel server, Player player) {
        Vec3 origin = player.position();
        for (LivingEntity target : server.getEntitiesOfClass(LivingEntity.class,
                player.getBoundingBox().inflate(WARD_RADIUS, 2.5D, WARD_RADIUS),
                entity -> entity != player && !(entity instanceof Player))) {
            double dx = target.getX() - origin.x;
            double dz = target.getZ() - origin.z;
            double distance = Math.sqrt(dx * dx + dz * dz);
            if (distance >= WARD_RADIUS) continue;
            if (distance < 0.05D) {
                Vec3 facing = player.getLookAngle();
                dx = facing.x;
                dz = facing.z;
                distance = Math.sqrt(dx * dx + dz * dz);
                if (distance < 0.05D) {
                    dx = 1.0D;
                    dz = 0.0D;
                    distance = 1.0D;
                }
            }
            target.push(dx / distance * 0.65D, 0.12D, dz / distance * 0.65D);
            target.hurtMarked = true;
        }
    }

    @SubscribeEvent
    public static void onLivingAttack(LivingAttackEvent event) {
        if (!(event.getEntity() instanceof Player player)
                || !(player.level() instanceof ServerLevel server)
                || event.getSource().is(DamageTypeTags.BYPASSES_INVULNERABILITY)) return;
        Ward ward = WARDS.get(player.getUUID());
        if (ward == null || !wardActive(server, player, ward)) return;
        event.setCanceled(true);
        if (server.getGameTime() % 3 == 0) {
            Vec3 center = player.position().add(0.0D, 1.0D, 0.0D);
            server.sendParticles(ParticleTypes.ENCHANTED_HIT, center.x, center.y, center.z,
                    5, 0.5D, 0.7D, 0.5D, 0.02D);
        }
    }

    @SubscribeEvent
    public static void onLevelTick(TickEvent.LevelTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.level instanceof ServerLevel server)) return;
        Iterator<Blast> blasts = BLASTS.iterator();
        while (blasts.hasNext()) {
            Blast blast = blasts.next();
            if (!blast.dimension().equals(server.dimension()) || server.getGameTime() < blast.at()) continue;
            blasts.remove();
            double radius = blast.radius();
            for (LivingEntity target : server.getEntitiesOfClass(LivingEntity.class,
                    new AABB(blast.center(), blast.center()).inflate(radius, 3, radius),
                    entity -> entity.isAlive() && !(entity instanceof Player))) {
                double dx = target.getX() - blast.center().x, dz = target.getZ() - blast.center().z;
                if (dx * dx + dz * dz <= radius * radius) {
                    target.hurt(blast.source(), target.getMaxHealth() * 0.5F);
                }
            }
        }
        if (server.getGameTime() % 2 != 0) return;
        Iterator<Map.Entry<UUID, Shot>> iterator = ARROWS.entrySet().iterator();
        while (iterator.hasNext()) {
            Map.Entry<UUID, Shot> entry = iterator.next();
            Shot shot = entry.getValue();
            if (server.getGameTime() - shot.createdAt() > 200L) {
                iterator.remove();
                continue;
            }
            if (!shot.dimension().equals(server.dimension())) continue;
            Entity entity = server.getEntity(entry.getKey());
            if (!(entity instanceof AbstractArrow arrow) || !arrow.isAlive()) {
                if (server.getGameTime() - shot.createdAt() > 4L) iterator.remove();
                continue;
            }
            if (arrow.tickCount > 5 && arrow.getDeltaMovement().lengthSqr() < 0.0001D) {
                iterator.remove();
                continue;
            }
            Vec3 p = arrow.position();
            if (shot.tier() >= 2) home(server, arrow);
            if (arrow.tickCount <= 4 || arrow.tickCount % 10 == 0) {
                sendEffect(server, p, new BowEffectPacket(0, arrow.getId(), shot.tier(), shot.phoenix(), p.x, p.y, p.z));
            }
            DustParticleOptions color = shot.phoenix() ? RED : shot.tier() >= 3 ? GOLD : CYAN;
            server.sendParticles(color, p.x, p.y, p.z,
                    1 + shot.tier() / 2, 0.03D, 0.03D, 0.03D, 0.0D);
            if (shot.tier() >= 2) {
                server.sendParticles(shot.phoenix() ? ParticleTypes.FLAME : ParticleTypes.END_ROD,
                        p.x, p.y, p.z, 1, 0.05D, 0.05D, 0.05D, 0.0D);
            }
        }
    }

    @SubscribeEvent
    public static void onArrowImpact(ProjectileImpactEvent event) {
        if (!(event.getProjectile() instanceof AbstractArrow arrow)
                || !(arrow.level() instanceof ServerLevel server)) return;
        Shot shot = ARROWS.get(arrow.getUUID());
        if (shot == null) return;
        // 穿透箭碰到第一个生物后仍会飞行，尾迹应持续到撞上方块或失速。
        if (event.getRayTraceResult().getType() != HitResult.Type.ENTITY || arrow.getPierceLevel() <= 0) {
            ARROWS.remove(arrow.getUUID());
        }
        Vec3 center = event.getRayTraceResult().getLocation();
        // A piercing arrow may hit several entities; only its first impact detonates the area seal.
        if (!shot.detonated && shot.tier() >= 3) {
            shot.detonated = true;
            sendEffect(server, center, new BowEffectPacket(1, arrow.getId(), shot.tier(), shot.phoenix(),
                    center.x, center.y, center.z));
            DamageSource source = new DamageSource(server.registryAccess().registryOrThrow(Registries.DAMAGE_TYPE)
                    .getHolderOrThrow(SOLAR_DAMAGE), arrow, arrow.getOwner());
            BLASTS.add(new Blast(server.dimension(), center, impactRadius(shot.tier()), source, server.getGameTime() + 1));
        }
        Vec3 normal = arrow.getDeltaMovement();
        DustParticleOptions color = shot.phoenix() ? RED : shot.tier() >= 3 ? GOLD : CYAN;
        circle(server, center, normal, 0.30D + shot.tier() * 0.13D,
                8 + shot.tier() * 4, color, 0.0D);
        if (shot.tier() >= 3) {
            server.sendParticles(shot.phoenix() ? ParticleTypes.FLAME : ParticleTypes.FIREWORK,
                    center.x, center.y, center.z, 4 + shot.tier(), 0.2D, 0.2D, 0.2D, 0.03D);
        }
    }

    @SubscribeEvent
    public static void onLogout(PlayerEvent.PlayerLoggedOutEvent event) {
        UUID id = event.getEntity().getUUID();
        WARDS.remove(id);
        WARD_READY_AT.remove(id);
        LAST_SHOT.remove(id);
    }

    private static void circle(ServerLevel server, Vec3 center, Vec3 normal, double radius,
                               int points, DustParticleOptions color, double rotation) {
        Vec3 forward = normal.lengthSqr() < 0.0001D ? new Vec3(0.0D, 0.0D, 1.0D) : normal.normalize();
        Vec3 right = forward.cross(new Vec3(0.0D, 1.0D, 0.0D));
        if (right.lengthSqr() < 0.0001D) right = new Vec3(1.0D, 0.0D, 0.0D);
        right = right.normalize();
        Vec3 up = right.cross(forward).normalize();
        for (int i = 0; i < points; i++) {
            double angle = Math.PI * 2.0D * i / points + rotation;
            Vec3 p = center.add(right.scale(Math.cos(angle) * radius))
                    .add(up.scale(Math.sin(angle) * radius));
            server.sendParticles(color, p.x, p.y, p.z, 1, 0.0D, 0.0D, 0.0D, 0.0D);
        }
    }

    private record Ward(ResourceKey<Level> dimension, Item bow, long expiresAt) {}
    public static double impactRadius(int tier) { return tier >= 4 ? WARD_RADIUS : 1.25D + tier * 0.85D; }

    private static void sendEffect(ServerLevel server, Vec3 p, BowEffectPacket packet) {
        DynastyNetwork.CHANNEL.send(PacketDistributor.NEAR.with(() -> new PacketDistributor.TargetPoint(
                p.x, p.y, p.z, 80, server.dimension())), packet);
    }

    static void home(ServerLevel server, AbstractArrow arrow) {
        Vec3 velocity = arrow.getDeltaMovement();
        if (velocity.lengthSqr() < 0.04D) return;
        Vec3 forward = velocity.normalize();
        LivingEntity best = null;
        double bestDistance = 36;
        for (LivingEntity candidate : server.getEntitiesOfClass(LivingEntity.class, arrow.getBoundingBox().inflate(6),
                entity -> entity.isAlive() && !(entity instanceof Player)
                        && entity != arrow.getOwner() && (arrow.getOwner() == null || !entity.isAlliedTo(arrow.getOwner()))
                        && entity instanceof net.minecraft.world.entity.monster.Enemy)) {
            Vec3 delta = candidate.getBoundingBox().getCenter().subtract(arrow.position());
            double distance = delta.lengthSqr();
            if (distance >= bestDistance || delta.normalize().dot(forward) < 0.65D) continue;
            HitResult hit = server.clip(new net.minecraft.world.level.ClipContext(arrow.position(),
                    candidate.getBoundingBox().getCenter(), net.minecraft.world.level.ClipContext.Block.COLLIDER,
                    net.minecraft.world.level.ClipContext.Fluid.NONE, arrow));
            if (hit.getType() != HitResult.Type.MISS) continue;
            best = candidate; bestDistance = distance;
        }
        if (best != null) {
            Vec3 aim = best.getBoundingBox().getCenter().subtract(arrow.position()).normalize();
            arrow.setDeltaMovement(forward.scale(0.78D).add(aim.scale(0.22D)).normalize().scale(velocity.length()));
            arrow.hasImpulse = true;
            arrow.hurtMarked = true;
        }
    }

    static void clearAvatarSpace(ServerLevel server, ServerPlayer player, double formed) {
        if (!player.mayBuild() || player.isSpectator()) return;
        Vec3 aim = HouyiAvatarShape.forward(player.getYRot());
        Vec3 forward = aim.cross(new Vec3(0, 1, 0));
        Vec3 right = aim.scale(-1);
        Vec3 origin = HouyiAvatarShape.origin(player.position(), player.getYRot());
        for (BlockPos position : BlockPos.betweenClosed(BlockPos.containing(origin.add(-5,0,-5)),
                BlockPos.containing(origin.add(5, 10 * formed, 5)))) {
            if (!server.hasChunkAt(position) || !server.mayInteract(player, position)) continue;
            Vec3 local = Vec3.atCenterOf(position).subtract(origin);
            if (!HouyiAvatarShape.contains(local.dot(right), local.y, local.dot(forward), 10 * formed)) continue;
            BlockState state = server.getBlockState(position);
            if (state.isAir() || !state.getFluidState().isEmpty() || state.hasBlockEntity()
                    || state.getDestroySpeed(server, position) < 0) continue;
            BlockPos stable = position.immutable();
            if (ForgeHooks.onBlockBreakEvent(server, player.gameMode.getGameModeForPlayer(), player, stable) >= 0) {
                server.destroyBlock(stable, true, player);
            }
        }
    }

    private record Blast(ResourceKey<Level> dimension, Vec3 center, double radius, DamageSource source, long at) {}
    public static boolean isSolarDamage(DamageSource source) { return source.is(SOLAR_DAMAGE); }

    @SubscribeEvent
    public static void onServerStopped(net.minecraftforge.event.server.ServerStoppedEvent event) {
        WARDS.clear(); WARD_READY_AT.clear(); ARROWS.clear(); LAST_SHOT.clear(); BLASTS.clear();
    }
    private static final class Shot {
        private final ResourceKey<Level> dimension;
        private final int tier;
        private final boolean phoenix;
        private final long createdAt;
        private boolean detonated;
        Shot(ResourceKey<Level> dimension, int tier, boolean phoenix, long createdAt) {
            this.dimension = dimension; this.tier = tier; this.phoenix = phoenix; this.createdAt = createdAt;
        }
        ResourceKey<Level> dimension() { return dimension; }
        int tier() { return tier; }
        boolean phoenix() { return phoenix; }
        long createdAt() { return createdAt; }
    }
}
