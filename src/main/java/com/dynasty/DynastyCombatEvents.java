package com.dynasty;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 战斗数值：玩家套装减伤（60%–80%）、铁壁额外减伤、附魔加伤，以及敌方「士气」减伤。
 * Combat maths: player set damage reduction (60-80%), Iron Wall, enchantment damage,
 * and enemy morale-based reduction (the 1024 vanilla HP cap is compensated by reduction).
 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public class DynastyCombatEvents {

    private static final Map<UUID, Long> HINT_TIME = new HashMap<>();

    @SubscribeEvent
    public static void onLivingHurt(LivingHurtEvent event) {
        float amount = event.getAmount();
        LivingEntity attacker = event.getSource().getEntity() instanceof LivingEntity living ? living : null;

        // 1) 攻击方：附魔加伤 + 武器独有机制 / attacker: enchantments + weapon gimmicks
        boolean armorPierce = false;
        if (attacker != null) {
            ItemStack weapon = attacker.getMainHandItem();
            int breaker = weapon.getEnchantmentLevel(DynastyEnchantments.BREAKER.get());
            if (breaker > 0) {
                amount += breaker * 150.0F;
            }
            int beheading = weapon.getEnchantmentLevel(DynastyEnchantments.BEHEADING.get());
            if (beheading > 0 && event.getEntity() instanceof Mob mob && mob.isInvertedHealAndHarm()) {
                amount *= 1.5F;
            }
            String weaponId = DynastyTrinkets.idOf(weapon);
            if (weaponId != null) {
                // 名器特攻：原版攻击力上限 2048，超出部分在这里补
                amount += (float) DynastyBalance.weaponBonus(weaponId);
                switch (weaponId) {
                    case "tang_dao" -> attacker.addEffect(new net.minecraft.world.effect.MobEffectInstance(
                            net.minecraft.world.effect.MobEffects.MOVEMENT_SPEED, 60, 0, true, false));
                    case "juque_sword" -> {
                        event.getEntity().addEffect(new net.minecraft.world.effect.MobEffectInstance(
                                net.minecraft.world.effect.MobEffects.MOVEMENT_SLOWDOWN, 60, 1));
                        event.getEntity().push(0.0D, 0.4D, 0.0D);
                    }
                    case "pojun_axe" -> armorPierce = true;
                    case "xuantian_axe" -> {
                        armorPierce = true;
                        event.getEntity().addEffect(new net.minecraft.world.effect.MobEffectInstance(
                                net.minecraft.world.effect.MobEffects.MOVEMENT_SLOWDOWN, 80, 1));
                    }
                    case "tianzi_sword" -> {
                        // 天子剑：命中回气（回复 2% 最大生命）+ 对王朝敌人额外 20% 伤害
                        attacker.heal((float) (attacker.getMaxHealth() * 0.02D));
                        if (DynastyBalance.isDynastyMob(event.getEntity().getType())) {
                            amount *= 1.2F;
                        }
                    }
                    case "halberd_fangtian" -> {
                        double yaw = Math.toRadians(attacker.getYRot());
                        event.getEntity().push(-Math.sin(yaw) * 0.8D, 0.25D, Math.cos(yaw) * 0.8D);
                        sweep(attacker, event.getEntity(), amount * 0.6F);
                    }
                    default -> {
                    }
                }
            }
        }

        // 1.5) 饰品命中触发（加伤部分）：会心 / 突袭 / 连击 —— 参数写在饰品表第 12~14 格
        if (attacker instanceof Player attackerPlayer) {
            amount = DynastyTrinketOnHit.bonus(attackerPlayer, event.getEntity(), amount);
        }

        // 2) 环首刀：受击反击 / Huan Shou Dao: counter attack
        if (event.getEntity() instanceof Player counter
                && ("huan_shou_dao".equals(DynastyTrinkets.idOf(counter.getMainHandItem()))
                || "huan_shou_dao".equals(DynastyTrinkets.idOf(counter.getOffhandItem())))) {
            counter.addEffect(new net.minecraft.world.effect.MobEffectInstance(
                    net.minecraft.world.effect.MobEffects.DAMAGE_BOOST, 100, 1, true, false));
        }

        // 2) 王朝生物对玩家的伤害按玩家体质缩放，避免开局被一击秒杀（数字依旧很大）
        // dynasty mobs' damage scales with the victim's max health so early game stays playable
        LivingEntity victim = event.getEntity();
        if (victim instanceof Player victimPlayer && attacker != null
                && DynastyBalance.isDynastyMob(attacker.getType())) {
            float capFactor = DynastyBalance.playerDamageCapFactor(attacker.getType());
            float cap = (float) (victimPlayer.getMaxHealth() * capFactor);
            if (amount > cap) {
                amount = cap;
            }
        }

        // 3) 挨打方：王朝套装减伤 / victim: dynasty armor set reduction
        if (victim instanceof Player player) {
            List<String> worn = DynastySetBonus.wornArmorIds(player);
            float reduction = DynastyBalance.setDamageReduction(worn);
            reduction += DynastyTrinkets.extraDamageReduction(player);   // 玉佩
            if (reduction > 0.0F) {
                amount *= 1.0F - Math.min(0.92F, reduction);
            }
        }

        // 3) 铁壁效果：额外 30% 减伤 / Iron Wall: extra 30% reduction
        if (victim.hasEffect(DynastyEffects.IRON_WALL.get())) {
            amount *= 0.7F;
        }

        // 4) 铁壁附魔 / Bulwark enchantment
        int bulwark = 0;
        for (ItemStack piece : victim.getArmorSlots()) {
            bulwark += piece.getEnchantmentLevel(DynastyEnchantments.BULWARK.get());
        }
        if (bulwark > 0) {
            amount *= Math.max(0.2F, 1.0F - bulwark * 0.12F);
        }

        // 6) 敌方「士气」减伤 / enemy morale reduction
        double toughness = DynastyBalance.mobToughness(victim.getType());
        if (armorPierce) {
            toughness *= 0.5D;   // 破军战斧：无视一半士气减伤
        }
        if (toughness > 0.0D) {
            amount *= (float) (1.0D - toughness);
            if (attacker instanceof ServerPlayer serverPlayer
                    && DynastyBalance.isBossOrBeast(victim.getType())) {
                long now = System.currentTimeMillis();
                if (now - HINT_TIME.getOrDefault(serverPlayer.getUUID(), 0L) > 4000L) {
                    HINT_TIME.put(serverPlayer.getUUID(), now);
                    serverPlayer.displayClientMessage(Component.literal(
                            "§7目标气势如虹：需更高攻击力的神兵"), true);
                }
            }
        }

        event.setAmount(Math.max(1.0F, amount));

        // 7) 饰品命中触发（结算后）：吸血 / 斩杀 / 雷罚 —— 吸血按**最终**伤害算
        if (attacker instanceof Player attackerPlayer) {
            DynastyTrinketOnHit.after(attackerPlayer, event.getEntity(), event.getAmount());
        }

        // 8) 伤势：玩家被重击就累积（生命上限会掉，丹药 / 睡觉能治，见 DynastyInjury）
        if (victim instanceof Player injured) {
            DynastyInjury.onHurt(injured, event.getAmount());
        }
    }

    /** 方天画戟横扫：对主目标周围的敌人造成额外伤害 / Fangtian halberd sweep */
    private static void sweep(LivingEntity attacker, LivingEntity main, float damage) {
        for (LivingEntity nearby : attacker.level().getEntitiesOfClass(LivingEntity.class,
                main.getBoundingBox().inflate(3.0D),
                e -> e != attacker && e != main && e.isAlive())) {
            nearby.hurt(attacker.damageSources().mobAttack(attacker), damage);
        }
    }
}
