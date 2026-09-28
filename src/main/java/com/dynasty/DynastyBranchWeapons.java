package com.dynasty;

import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Side-path weapons: passive effects, no extra keys or movement trials. */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class DynastyBranchWeapons {
    private DynastyBranchWeapons() {}
    public static float bonus(String id, double toughness, boolean healthy) {
        return switch (id) {
            case "beichen_spear" -> (float)Math.min(.60, Math.max(0, toughness) * .008);
            case "chengying_sword" -> healthy ? .20F : 0;
            case "leifu_staff" -> .15F;
            default -> 0;
        };
    }
    @SubscribeEvent public static void onHurt(LivingHurtEvent event) {
        if (event.getEntity().level().isClientSide || event.getAmount() <= 0
                || DynastyTrinketOnHit.isSyntheticDamage()
                || !event.getSource().is(DamageTypes.PLAYER_ATTACK)
                || !(event.getSource().getDirectEntity() instanceof Player player)
                || event.getEntity().isAlliedTo(player) || player.isAlliedTo(event.getEntity())) return;
        String id = DynastySchoolCombat.weapon(player);
        float bonus = bonus(id, player.getAttributeValue(Attributes.ARMOR_TOUGHNESS),
                event.getEntity().getHealth() >= event.getEntity().getMaxHealth() * .9F);
        if (bonus > 0) event.setAmount(event.getAmount() * (1 + bonus));
        if (id.equals("leifu_staff")) event.getEntity().addEffect(
                new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 60, 0));
    }
}
