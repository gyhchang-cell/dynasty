package com.sammy.malum.core.handlers;

import com.sammy.malum.*;
import com.sammy.malum.client.VoidRevelationHandler;
import com.sammy.malum.common.data.attachment.*;
import com.sammy.malum.common.entity.FloatingItemEntity;
import com.sammy.malum.common.payloads.VoidRejectionPayload;
import com.sammy.malum.registry.common.*;
import com.sammy.malum.registry.common.MalumContent;
import com.sammy.malum.registry.common.magic.*;
import com.sammy.malum.registry.common.sound.*;
import net.minecraft.client.resources.sounds.Sound;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.*;
import net.minecraft.server.level.*;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.Mth;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.neoforged.neoforge.event.tick.EntityTickEvent;
import net.neoforged.neoforge.network.*;
import team.lodestar.lodestone.helpers.*;
import team.lodestar.lodestone.modules.toolkit.sound.SoundPlayer;

import static com.sammy.malum.client.VoidRevelationHandler.RevelationType.BLACK_CRYSTAL;

public class WeepingWellRejectionHandler {

    public static final ResourceLocation GRAVITY_MODIFIER_ID = MalumMod.malumPath("weeping_well_reduced_gravity");

    public static void handlePrimordialSoupContact(Entity entity) {
        if (entity instanceof LivingEntity livingEntity) {
            TouchOfDarknessHandler.handlePrimordialSoupContact(livingEntity);
            var data = livingEntity.getData(MalumAttachmentTypes.WEEPING_WELL_INFO);
            if (data.isInRejectedState) {
                return;
            }
            data.setGoopStatus();
        }
        if (entity instanceof FloatingItemEntity) {
            return;
        }
        entity.setDeltaMovement(entity.getDeltaMovement().scale(0.3f));
    }

    public static void entityTick(EntityTickEvent.Pre event) {
        if (event.getEntity() instanceof LivingEntity living) {
            var level = living.level();
            if (living.hasData(MalumAttachmentTypes.WEEPING_WELL_INFO) || living instanceof Player) {
                var data = living.getData(MalumAttachmentTypes.WEEPING_WELL_INFO);
                data.update(living);
                updateGravity(living);
                if (data.isInGoop()) {
                    handleRejectionState(level, living);
                }
            }
        }
    }

    public static void updateGravity(LivingEntity entity) {
        var gravity = entity.getAttribute(Attributes.GRAVITY);
        if (gravity != null) {
            var data = entity.getData(MalumAttachmentTypes.WEEPING_WELL_INFO);
            if (gravity.hasModifier(GRAVITY_MODIFIER_ID)) {
                gravity.removeModifier(GRAVITY_MODIFIER_ID);
            }
            if (data.isInRejectedState) {
                gravity.addTransientModifier(getEntityGravityAttributeModifier(entity));
            }
        }
    }

    public static void handleRejectionState(Level level, LivingEntity living) {
        var data = living.getData(MalumAttachmentTypes.WEEPING_WELL_INFO);
        int rejection = data.voidRejection;
        if (!level.isClientSide) {
            if (living instanceof Player && level.getGameTime() % 6L == 0) {
                SoundPlayer.create(MalumSoundEvents.SONG_OF_THE_VOID).volume(0.5f + rejection * 0.02f).pitch(0.5f + rejection * 0.03f).play(living);
            }
            if (data.wasJustRejected()) {
                if (!(living instanceof Player player)) {
                    living.remove(Entity.RemovalReason.DISCARDED);
                    return;
                }
                launchPlayer(player);
            }
        }
        if (data.isInRejectedState && rejection > 0) {
            float intensity = rejection / WeepingWellData.MAX_REJECTION;
            Vec3 movement = living.getDeltaMovement();
            living.setDeltaMovement(movement.x, Math.pow(intensity, 2)/2f, movement.z);
        }
    }

    public static void launchPlayer(Player player) {
        var progression = player.getData(MalumAttachmentTypes.PROGRESSION_DATA);
        var level = player.level();
        if (level instanceof ServerLevel serverLevel) {
            WeepingWellData.checkForWeepingWell(player).ifPresent(weepingWell -> {
                BlockPos worldPosition = weepingWell.getBlockPos();
                MalumParticleEffectTypes.WEEPING_WELL_REACTS.createEffect(worldPosition.getCenter()).spawn(serverLevel);
            });
            MalumParticleEffectTypes.WEEPING_WELL_REACTS.createEffect(player).spawn(serverLevel);
            if (!player.isCreative()) {
                player.hurt(DamageTypeHelper.create(level, MalumDamageTypes.VOID), 4);
            }
            if (!progression.hasBeenRejected) {
                SoulHarvestHandler.spawnSpirits(player)
                        .setCustomItems(MalumContent.Spirits.UMBRAL_SPIRIT.get())
                        .setPreferredCollector(player)
                        .spawnSpirits(level);
            }
            PacketDistributor.sendToPlayersTrackingEntityAndSelf(player, new VoidRejectionPayload(player.getId()));
            SoundPlayer.create(MalumSoundEvents.VOID_REJECTION).volume(2f).pitch(0.5f, 0.8f).play(player);
        } else {
            VoidRevelationHandler.seeTheRevelation(BLACK_CRYSTAL);
        }

        progression.hasBeenRejected = true;
        player.addEffect(new MobEffectInstance(MalumMobEffects.REJECTED, 400, 0));
    }

    public static AttributeModifier getEntityGravityAttributeModifier(LivingEntity livingEntity) {
        return new AttributeModifier(GRAVITY_MODIFIER_ID, updateEntityGravity(livingEntity), AttributeModifier.Operation.ADD_MULTIPLIED_TOTAL);
    }

    public static double updateEntityGravity(LivingEntity living) {
        var data = living.getData(MalumAttachmentTypes.WEEPING_WELL_INFO);
        if (data.voidRejection > 0) {
            return -Math.min(60, data.voidRejection) / 60f;
        }
        return 0;
    }
}