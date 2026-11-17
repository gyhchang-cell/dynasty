package com.yellowbrossproductions.illageandspillage.util;

import com.yellowbrossproductions.illageandspillage.access.LivingEntityAccess;
import com.yellowbrossproductions.illageandspillage.Config;
import com.yellowbrossproductions.illageandspillage.entities.*;
import com.yellowbrossproductions.illageandspillage.entities.projectile.AxeEntity;
import com.yellowbrossproductions.illageandspillage.entities.projectile.BoneEntity;
import com.yellowbrossproductions.illageandspillage.init.ModEntityTypes;
import com.yellowbrossproductions.illageandspillage.packet.MobFollowingSoundPacket;
import com.yellowbrossproductions.illageandspillage.packet.PacketHandler;
import com.yellowbrossproductions.illageandspillage.packet.ParticlePacket;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.raid.Raider;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.VoxelShape;
import net.minecraftforge.network.PacketDistributor;
import org.jetbrains.annotations.NotNull;

import java.util.Iterator;
import java.util.List;

public class EntityUtil {
    public static boolean displayBossBar(Raider boss) {
        if (Config.CommonConfig.bossbar_type.get() == 1) {
            return !boss.hasActiveRaid();
        }

        return Config.CommonConfig.bossbar_type.get() == 2;
    }

    public static boolean isEntityCrazyRagno(Entity entity) {
        return entity instanceof RagnoEntity && ((RagnoEntity) entity).isCrazy();
    }

    public static boolean canHurtThisMob(Entity target, Mob attacker) {
        if ((attacker.getTeam() != null || target.getTeam() != null) && (isEntityCrazyRagno(target) || !(target instanceof IllagerAttack) || target instanceof FunnyboneEntity || target instanceof EyesoreEntity || target instanceof TrickOrTreatEntity || target instanceof EngineerMachine || target instanceof FactoryMinion) && !(target instanceof AxeEntity) && !(target instanceof BoneEntity)) {
            return attacker.getTeam() != target.getTeam();
        } else if ((!(target instanceof Raider) || isEntityCrazyRagno(attacker)) && (isEntityCrazyRagno(target) || !(target instanceof IllagerAttack) || target instanceof FunnyboneEntity || target instanceof EyesoreEntity || target instanceof TrickOrTreatEntity || target instanceof EngineerMachine || target instanceof FactoryMinion) && !(target instanceof AxeEntity) && !(target instanceof BoneEntity)) {
            return attacker != target;
        } else {
            return attacker.getTarget() == target;
        }
    }

    public static boolean isMobNotOnOtherTeam(Entity target, Mob attacker) {
        if (attacker.getTeam() == null && target.getTeam() == null) {
            return true;
        } else {
            return attacker.getTeam() == target.getTeam();
        }
    }

    public static boolean isMobOnOtherTeam2(Entity target, Mob attacker) {
        if (attacker.getTeam() == null && target.getTeam() == null) {
            return true;
        } else {
            return attacker.getTeam() != target.getTeam();
        }
    }

    public static void createLineImpsAttack(BlockPos pos, @NotNull LivingEntity attacker, double x, double y, double z, Level level) {
        List<ImpEntity> list = level.getEntitiesOfClass(ImpEntity.class, attacker.getBoundingBox().inflate(100.0), (predicate) -> predicate.getOwner() == attacker);
        if (list.size() < 48) {
            double d0 = Math.min(pos.getY(), y);
            double d1 = Math.max(pos.getY(), y) + 1.0;
            float f = (float) Mth.atan2((double) pos.getZ() - z, (double) pos.getX() - x);

            for (int l = 0; l < 16; ++l) {
                double d2 = 1.25 * (double) (l + 1);
                createSpellEntity(x + (double) Mth.cos(f) * d2, z + (double) Mth.sin(f) * d2, d0, d1, l, attacker, level);
            }
        }

    }

    private static void createSpellEntity(double p_190876_1_, double p_190876_3_, double p_190876_5_, double p_190876_7_, int time, LivingEntity attacker, Level level) {
        BlockPos blockpos = BlockPos.containing(p_190876_1_, p_190876_7_, p_190876_3_);
        boolean flag = false;
        double d0 = 0.0;

        do {
            BlockPos blockpos1 = blockpos.below();
            BlockState blockstate = level.getBlockState(blockpos1);
            if (blockstate.isFaceSturdy(level, blockpos1, Direction.UP)) {
                if (!level.isEmptyBlock(blockpos)) {
                    BlockState blockstate1 = level.getBlockState(blockpos);
                    VoxelShape voxelshape = blockstate1.getCollisionShape(level, blockpos);
                    if (!voxelshape.isEmpty()) {
                        d0 = voxelshape.max(Direction.Axis.Y);
                    }
                }

                flag = true;
                break;
            }

            blockpos = blockpos.below();
        } while (blockpos.getY() >= Mth.floor(p_190876_5_) - 1);

        if (flag) {
            ImpEntity imp = ModEntityTypes.Imp.get().create(level);

            assert imp != null;

            imp.setPos((double) blockpos.getX() + 0.5, (double) blockpos.getY() + d0, (double) blockpos.getZ() + 0.5);
            imp.setOwner(attacker);
            imp.setWaitTime(time);
            imp.setInvisible(true);
            imp.setPlayerOwned(true);
            if (attacker.getTeam() != null) {
                level.getScoreboard().addPlayerToTeam(imp.getStringUUID(), level.getScoreboard().getPlayerTeam(attacker.getTeam().getName()));
            }

            level.addFreshEntity(imp);
        }

    }

    public static void disableShield(LivingEntity livingEntity, int ticks) {
        if (livingEntity instanceof Player && livingEntity.isBlocking()) {
            ((Player) livingEntity).getCooldowns().addCooldown(livingEntity.getUseItem().getItem(), ticks);
            livingEntity.stopUsingItem();
            livingEntity.level().broadcastEntityEvent(livingEntity, (byte) 30);
        }
    }

    public static void mobFollowingSound(Level level, Entity entity, SoundEvent sound, float volume, float pitch, boolean loop) {
        if (!level.isClientSide) {
            PacketHandler.CHANNEL.send(PacketDistributor.TRACKING_ENTITY_AND_SELF.with(() -> entity), new MobFollowingSoundPacket(entity.getId(), sound, volume, pitch, loop));
        }
    }

    public static void makeCircleParticles(Level level, LivingEntity spawner, ParticleOptions particleType, int amount, double y, float velocity) {
        if (!level.isClientSide) {
            for (ServerPlayer serverPlayer : ((ServerLevel) level).players()) {
                if (serverPlayer.distanceToSqr(spawner) < 4096.0D) {
                    ParticlePacket packet = new ParticlePacket();

                    for (int i = 0; i < amount; i++) {
                        float TAU = (float) (2 * StrictMath.PI);

                        float yaw = i * (TAU / amount);
                        float vy = spawner.getRandom().nextFloat() * 0.1F - 0.05f;
                        float vx = velocity * Mth.cos(yaw);
                        float vz = velocity * Mth.sin(yaw);
                        packet.queueParticle(particleType, false, new Vec3(spawner.getX(), spawner.getY() + y, spawner.getZ()), new Vec3(vx, vy, vz));
                    }

                    PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> serverPlayer), packet);
                }
            }
        }
    }

    public static void makeWebParticles(Level level, Entity caught) {
        ParticleOptions particle = new ItemParticleOption(ParticleTypes.ITEM, Items.COBWEB.getDefaultInstance());
        if (!level.isClientSide) {
            Iterator<ServerPlayer> var4 = ((ServerLevel) level).players().iterator();

            while (true) {
                ServerPlayer serverPlayer;
                do {
                    if (!var4.hasNext()) {
                        return;
                    }

                    serverPlayer = var4.next();
                } while (!(serverPlayer.distanceToSqr(caught) < 4096.0));

                ParticlePacket packet = new ParticlePacket();

                for (int i = 0; i < 2; ++i) {
                    double d0 = (-0.5 + serverPlayer.getRandom().nextGaussian()) / 10.0;
                    double d1 = (-0.5 + serverPlayer.getRandom().nextGaussian()) / 10.0;
                    double d2 = (-0.5 + serverPlayer.getRandom().nextGaussian()) / 10.0;
                    packet.queueParticle(particle, false, new Vec3(caught.getRandomX(0.5), caught.getRandomY(), caught.getRandomZ(0.5)), new Vec3(d0, d1, d2));
                }

                ServerPlayer finalServerPlayer = serverPlayer;
                PacketHandler.CHANNEL.send(PacketDistributor.PLAYER.with(() -> finalServerPlayer), packet);
            }
        }
    }

    public static boolean isWebbed(LivingEntity entity) {
        return ((LivingEntityAccess) entity).callIsWebbed();
    }

    public static void setWebbed(LivingEntity entity, boolean isWebbed) {
        ((LivingEntityAccess) entity).callSetWebbed(isWebbed);
    }

    public static boolean isPreserved(LivingEntity entity) {
        return ((LivingEntityAccess) entity).callIsPreserved();
    }

    public static void setPreserved(LivingEntity entity, boolean isPreserved) {
        ((LivingEntityAccess) entity).callSetPreserved(isPreserved);
    }
}
