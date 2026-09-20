package com.dynasty;

import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.List;

/**
 * 符箓（重制版）：一次性消耗，但每一张都「值这个钱」。
 *
 * | 符 | 效果 |
 * | --- | --- |
 * | 火符   | 爆炎：准星落点半径 4.5 内 600+攻击×3 火焰伤害、点燃 8 秒 |
 * | 雷符   | 天雷：三道落雷，半径 5 内 800+攻击×4 伤害、缓慢 + 虚弱 5 秒 |
 * | 御风符 | 罡风：半径 8 内 200+攻击×2 伤害、全部击飞；自身疾风 + 缓降 45 秒 |
 * | 隐身符 | 隐身 60 秒 + 速度 II + 夜视，并清除 16 格内怪物对你的仇恨 |
 * | 金刚符 | 抗性 III + 力量 II 15 秒、抗火 60 秒（原「回春符」，不再回血） |
 * | 摄魂符 | 半径 6 内 500+攻击×3 伤害 + 失明 + 虚弱 8 秒 |
 * | 归乡符 | 传送回出生点并净化所有负面效果 |
 *
 * Talismans (reworked): single use, but every one of them hits hard and comes with its own VFX.
 */
@SuppressWarnings({"null", "removal"})
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
        ServerLevel world = serverPlayer.serverLevel();
        double attack = serverPlayer.getAttributeValue(Attributes.ATTACK_DAMAGE);

        switch (name) {
            case "fire_talisman" -> fireTalisman(serverPlayer, world, attack);
            case "thunder_talisman" -> thunderTalisman(serverPlayer, world, attack);
            case "wind_talisman" -> windTalisman(serverPlayer, world, attack);
            case "stealth_talisman" -> stealthTalisman(serverPlayer, world);
            case "vajra_talisman" -> vajraTalisman(serverPlayer, world);
            case "soul_talisman" -> soulTalisman(serverPlayer, world, attack);
            case "return_talisman" -> returnTalisman(serverPlayer, world);
            default -> serverPlayer.sendSystemMessage(Component.literal("§e符箓无声无息。"));
        }
        if (!serverPlayer.getAbilities().instabuild) {
            stack.shrink(1);
        }
        return InteractionResultHolder.consume(stack);
    }

    // ---------------------------------------------------------------- 单张符箓
    /** 火符：爆炎 / Fire talisman: blazing detonation */
    private void fireTalisman(ServerPlayer player, ServerLevel world, double attack) {
        Vec3 center = aim(player, 26.0D);
        float damage = (float) (600.0D + attack * 3.0D);
        int hits = burnArea(player, world, center, 4.5D, damage, true, MobEffects.MOVEMENT_SLOWDOWN, 0);
        smoke(world, center, 5.5D, ParticleTypes.FLAME, 90);
        smoke(world, center, 5.5D, ParticleTypes.LAVA, 24);
        world.sendParticles(ParticleTypes.EXPLOSION_EMITTER, center.x, center.y + 0.4D, center.z, 2, 0.6D, 0.3D, 0.6D, 0.0D);
        play(world, center, SoundEvents.GENERIC_EXPLODE, 2.2F, 0.9F);
        play(world, center, SoundEvents.FIREWORK_ROCKET_BLAST, 1.6F, 0.7F);
        player.sendSystemMessage(Component.literal("§c[火符] §r爆炎焚天，命中 " + hits + " 名敌人。"));
    }

    /** 雷符：三道落雷 + 麻痹 / Thunder talisman: triple lightning strike */
    private void thunderTalisman(ServerPlayer player, ServerLevel world, double attack) {
        Vec3 center = aim(player, 28.0D);
        float damage = (float) (800.0D + attack * 4.0D);
        for (int i = 0; i < 3; i++) {
            BlockPos pos = BlockPos.containing(center.add(
                    (world.random.nextDouble() - 0.5D) * 6.0D, 0.0D,
                    (world.random.nextDouble() - 0.5D) * 6.0D));
            LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(world);
            if (bolt != null) {
                bolt.moveTo(Vec3.atBottomCenterOf(pos));
                bolt.setVisualOnly(true);
                bolt.setCause(player);
                world.addFreshEntity(bolt);
            }
        }
        int hits = burnArea(player, world, center, 5.0D, damage, false,
                MobEffects.MOVEMENT_SLOWDOWN, 1);
        areaDebuff(player, world, center, 5.0D, MobEffects.WEAKNESS, 100, 1);
        smoke(world, center, 5.0D, ParticleTypes.ELECTRIC_SPARK, 120);
        smoke(world, center, 5.0D, ParticleTypes.END_ROD, 30);
        play(world, center, SoundEvents.LIGHTNING_BOLT_THUNDER, 2.5F, 1.0F);
        play(world, center, SoundEvents.LIGHTNING_BOLT_IMPACT, 2.0F, 1.2F);
        player.sendSystemMessage(Component.literal("§b[雷符] §r三雷齐落，命中 " + hits + " 名敌人。"));
    }

    /** 御风符：罡风击飞 + 自身疾风 / Wind talisman: gale knock-up */
    private void windTalisman(ServerPlayer player, ServerLevel world, double attack) {
        Vec3 center = player.position();
        float damage = (float) (200.0D + attack * 2.0D);
        List<LivingEntity> targets = enemies(player, world, center, 8.0D);
        for (LivingEntity target : targets) {
            Vec3 push = target.position().subtract(center);
            Vec3 flat = new Vec3(push.x, 0.0D, push.z);
            if (flat.length() < 0.1D) {
                flat = new Vec3(1.0D, 0.0D, 0.0D);
            }
            flat = flat.normalize().scale(1.6D);
            target.push(flat.x, 1.25D, flat.z);
            target.hurt(player.damageSources().indirectMagic(player, player), damage);
            target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 80, 1));
        }
        player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 20 * 45, 2));
        player.addEffect(new MobEffectInstance(MobEffects.SLOW_FALLING, 20 * 45, 0));
        player.addEffect(new MobEffectInstance(MobEffects.JUMP, 20 * 45, 1));
        smoke(world, center, 8.0D, ParticleTypes.CLOUD, 140);
        smoke(world, center, 6.0D, ParticleTypes.SWEEP_ATTACK, 30);
        play(world, center, SoundEvents.ENDER_DRAGON_FLAP, 1.6F, 1.4F);
        play(world, center, SoundEvents.PHANTOM_FLAP, 1.4F, 1.2F);
        player.sendSystemMessage(Component.literal("§f[御风符] §r罡风大起，掀翻 " + targets.size() + " 名敌人。"));
    }

    /** 隐身符：隐身 + 清除仇恨 / Stealth talisman: vanish and drop all aggro */
    private void stealthTalisman(ServerPlayer player, ServerLevel world) {
        player.addEffect(new MobEffectInstance(MobEffects.INVISIBILITY, 20 * 60, 0));
        player.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 20 * 60, 1));
        player.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 20 * 60, 0));
        int cleared = 0;
        for (Mob mob : world.getEntitiesOfClass(Mob.class, player.getBoundingBox().inflate(16.0D),
                m -> m.getTarget() == player)) {
            mob.setTarget(null);
            cleared++;
        }
        smoke(world, player.position(), 2.5D, ParticleTypes.SMOKE, 60);
        smoke(world, player.position(), 2.5D, ParticleTypes.SQUID_INK, 20);
        play(world, player.position(), SoundEvents.ILLUSIONER_MIRROR_MOVE, 1.2F, 1.0F);
        player.sendSystemMessage(Component.literal("§7[隐身符] §r气息全无，摆脱了 " + cleared + " 名追兵。"));
    }

    /** 金刚符：抗性 + 力量 + 抗火（原「回春符」，不再回血）/ Vajra talisman */
    private void vajraTalisman(ServerPlayer player, ServerLevel world) {
        player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 20 * 15, 2));
        player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST, 20 * 15, 1));
        player.addEffect(new MobEffectInstance(MobEffects.FIRE_RESISTANCE, 20 * 60, 0));
        smoke(world, player.position(), 2.0D, ParticleTypes.ENCHANT, 60);
        smoke(world, player.position(), 2.0D, ParticleTypes.TOTEM_OF_UNDYING, 30);
        play(world, player.position(), SoundEvents.TOTEM_USE, 1.0F, 1.4F);
        play(world, player.position(), SoundEvents.ANVIL_LAND, 0.6F, 1.6F);
        player.sendSystemMessage(Component.literal("§6[金刚符] §r金刚护体：抗性 III + 力量 II，刀枪难入。"));
    }

    /** 摄魂符：大范围伤害 + 失明虚弱 / Soul talisman */
    private void soulTalisman(ServerPlayer player, ServerLevel world, double attack) {
        Vec3 center = aim(player, 22.0D);
        float damage = (float) (500.0D + attack * 3.0D);
        int hits = burnArea(player, world, center, 6.0D, damage, false, MobEffects.BLINDNESS, 0);
        areaDebuff(player, world, center, 6.0D, MobEffects.WEAKNESS, 160, 1);
        smoke(world, center, 6.0D, ParticleTypes.SOUL, 90);
        smoke(world, center, 6.0D, ParticleTypes.SOUL_FIRE_FLAME, 40);
        play(world, center, SoundEvents.SOUL_ESCAPE, 1.8F, 0.8F);
        play(world, center, SoundEvents.WITHER_SHOOT, 1.2F, 1.4F);
        player.sendSystemMessage(Component.literal("§5[摄魂符] §r魂飞魄散，命中 " + hits + " 名敌人。"));
    }

    /** 归乡符：回程并净化 / Return talisman */
    private void returnTalisman(ServerPlayer player, ServerLevel world) {
        ServerLevel home = player.server.overworld();
        BlockPos spawn = home.getSharedSpawnPos();
        BlockPos arrival = com.dynasty.block.DynastyPortalBlock.findArrival(home, spawn.getX(), spawn.getZ());
        play(world, player.position(), SoundEvents.ENDERMAN_TELEPORT, 1.2F, 0.8F);
        smoke(world, player.position(), 2.0D, ParticleTypes.PORTAL, 80);
        player.teleportTo(home, arrival.getX() + 0.5D, arrival.getY(), arrival.getZ() + 0.5D,
                player.getYRot(), player.getXRot());
        player.fallDistance = 0.0F;
        player.getActiveEffects().stream()
                .filter(effect -> !effect.getEffect().isBeneficial())
                .map(effect -> effect.getEffect())
                .toList()
                .forEach(player::removeEffect);
        smoke(home, player.position(), 2.0D, ParticleTypes.REVERSE_PORTAL, 60);
        play(home, player.position(), SoundEvents.ENDERMAN_TELEPORT, 1.2F, 1.4F);
        player.sendSystemMessage(Component.literal("§d[归乡符] §r一瞬千里，回到城郭，身心俱净。"));
    }

    // ---------------------------------------------------------------- 工具
    /** 准星落点（打到方块就用方块位置）/ aim point */
    private static Vec3 aim(ServerPlayer player, double distance) {
        HitResult hit = player.pick(distance, 0.0F, false);
        if (hit.getType() == HitResult.Type.BLOCK) {
            return ((BlockHitResult) hit).getLocation();
        }
        return player.getEyePosition().add(player.getLookAngle().scale(distance));
    }

    /** 范围内敌人（不含玩家）/ enemies around the point */
    private static List<LivingEntity> enemies(ServerPlayer player, ServerLevel world, Vec3 center, double radius) {
        net.minecraft.world.phys.AABB box =
                new net.minecraft.world.phys.AABB(center, center).inflate(radius);
        return world.getEntitiesOfClass(LivingEntity.class, box,
                e -> e != player && e.isAlive() && !(e instanceof Player));
    }

    /** 范围伤害（可选点燃 / 可选附加负面）/ area damage */
    private static int burnArea(ServerPlayer player, ServerLevel world, Vec3 center, double radius,
                                float damage, boolean ignite,
                                net.minecraft.world.effect.MobEffect debuff, int amp) {
        int hits = 0;
        for (LivingEntity target : enemies(player, world, center, radius)) {
            if (target.position().distanceTo(center) > radius) {
                continue;
            }
            target.hurt(player.damageSources().indirectMagic(player, player), damage);
            if (ignite) {
                target.setSecondsOnFire(8);
            }
            if (debuff != null) {
                target.addEffect(new MobEffectInstance(debuff, 160, amp));
            }
            hits++;
        }
        return hits;
    }

    private static void areaDebuff(ServerPlayer player, ServerLevel world, Vec3 center, double radius,
                                   net.minecraft.world.effect.MobEffect effect, int ticks, int amp) {
        for (LivingEntity target : enemies(player, world, center, radius)) {
            if (target.position().distanceTo(center) <= radius) {
                target.addEffect(new MobEffectInstance(effect, ticks, amp));
            }
        }
    }

    private static void smoke(ServerLevel world, Vec3 center, double radius, ParticleOptions particle, int count) {
        world.sendParticles(particle, center.x, center.y + 0.5D, center.z, count,
                radius * 0.5D, radius * 0.35D, radius * 0.5D, 0.02D);
    }

    private static void play(ServerLevel world, Vec3 pos, SoundEvent sound, float volume, float pitch) {
        world.playSound(null, BlockPos.containing(pos), sound, SoundSource.PLAYERS, volume, pitch);
    }
}
