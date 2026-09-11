package com.dynasty;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.SmallFireball;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * 符箓：御风、隐身、回春、火符、雷符、归乡符（右键使用，无需任何指令）。
 * Talismans: wind, stealth, healing, fire, thunder and return. Right-click to use, no commands needed.
 */
@SuppressWarnings("null")
public class TalismanCharmItem extends Item {

    public TalismanCharmItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (level.isClientSide() || !(player instanceof ServerPlayer serverPlayer)) {
            return InteractionResultHolder.success(stack);
        }
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(this);
        String name = id == null ? "" : id.getPath();
        ServerLevel serverLevel = serverPlayer.serverLevel();
        Vec3 look = serverPlayer.getLookAngle();
        Vec3 eye = serverPlayer.getEyePosition();

        switch (name) {
            case "wind_talisman" -> {
                serverPlayer.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 20 * 40, 1));
                serverPlayer.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 20 * 40, 0));
                serverPlayer.addEffect(new MobEffectInstance(MobEffects.JUMP, 20 * 40, 1));
                serverPlayer.sendSystemMessage(Component.literal("§b[御风符] §r脚下生风，飘然而起。"));
            }
            case "stealth_talisman" -> {
                serverPlayer.addEffect(new MobEffectInstance(MobEffects.INVISIBILITY, 20 * 30, 0));
                serverPlayer.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 20 * 30, 0));
                serverPlayer.sendSystemMessage(Component.literal("§7[隐身符] §r气息全无。"));
            }
            case "healing_talisman" -> {
                serverPlayer.addEffect(new MobEffectInstance(MobEffects.HEAL, 1, 1));
                serverPlayer.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 20 * 15, 1));
                serverPlayer.sendSystemMessage(Component.literal("§a[回春符] §r伤痛尽消。"));
            }
            case "fire_talisman" -> {
                SmallFireball fireball = new SmallFireball(serverLevel, serverPlayer,
                        look.x * 1.6D, look.y * 1.6D, look.z * 1.6D);
                fireball.moveTo(eye.x, eye.y - 0.2D, eye.z, serverPlayer.getYRot(), serverPlayer.getXRot());
                serverLevel.addFreshEntity(fireball);
                serverLevel.playSound(null, serverPlayer.blockPosition(), SoundEvents.BLAZE_SHOOT,
                        SoundSource.PLAYERS, 1.5F, 1.2F);
                serverPlayer.getCooldowns().addCooldown(this, 20);
            }
            case "thunder_talisman" -> {
                Vec3 target = eye.add(look.scale(24.0D));
                HitResult hit = serverPlayer.pick(24.0D, 0.0F, false);
                if (hit.getType() == HitResult.Type.BLOCK) {
                    target = ((BlockHitResult) hit).getLocation();
                }
                BlockPos pos = BlockPos.containing(target);
                LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(serverLevel);
                if (bolt != null) {
                    bolt.moveTo(Vec3.atBottomCenterOf(pos));
                    bolt.setCause(serverPlayer);
                    serverLevel.addFreshEntity(bolt);
                }
                serverLevel.playSound(null, pos, SoundEvents.LIGHTNING_BOLT_THUNDER,
                        SoundSource.WEATHER, 2.0F, 1.0F);
                serverPlayer.getCooldowns().addCooldown(this, 60);
            }
            case "return_talisman" -> {
                BlockPos spawn = serverLevel.getSharedSpawnPos();
                serverPlayer.teleportTo(spawn.getX() + 0.5D, spawn.getY() + 0.5D, spawn.getZ() + 0.5D);
                serverLevel.playSound(null, spawn, SoundEvents.ENDERMAN_TELEPORT, SoundSource.PLAYERS, 1.0F, 1.0F);
                serverPlayer.sendSystemMessage(Component.literal("§d[归乡符] §r一瞬千里，回到城郭。"));
            }
            default -> {
                serverPlayer.sendSystemMessage(Component.literal("§e符箓无声无息。"));
            }
        }
        serverLevel.sendParticles(ParticleTypes.ENCHANT, serverPlayer.getX(), serverPlayer.getY() + 1.0D,
                serverPlayer.getZ(), 24, 0.6D, 0.8D, 0.6D, 0.4D);
        if (!serverPlayer.getAbilities().instabuild) {
            stack.shrink(1);
        }
        return InteractionResultHolder.consume(stack);
    }
}
