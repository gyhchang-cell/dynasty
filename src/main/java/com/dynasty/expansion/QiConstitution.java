package com.dynasty.expansion;

import com.dynasty.Dynasty;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.event.entity.living.LivingEquipmentChangeEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.living.MobEffectEvent;
import net.minecraftforge.eventbus.api.Event;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** A live affinity of the existing day/night sets, not another saved status system. */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class QiConstitution {
    public static boolean immune(LivingEntity target, MobEffect effect) {
        if (!(target instanceof ServerPlayer player)) return false;
        if (effect == ExpansionEffects.YIN.get())
            return player.level().isDay() && EquipmentBehaviors.pieces(player, "tiangang") == 4;
        if (effect == ExpansionEffects.YANG.get())
            return !player.level().isDay() && EquipmentBehaviors.pieces(player, "disha") == 4;
        return false;
    }

    /** Covers native /effect, potions and other callers as well as ExpansionEffects.apply. */
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void applicable(MobEffectEvent.Applicable event) {
        if (immune(event.getEntity(), event.getEffectInstance().getEffect())) {
            event.setResult(Event.Result.DENY);
            CombatFeedback.send(event.getEntity(), CombatFeedback.IMMUNE);
        }
    }

    public static void cleanse(ServerPlayer player) {
        if (player.hasEffect(ExpansionEffects.YIN.get()) && immune(player, ExpansionEffects.YIN.get()))
            player.removeEffect(ExpansionEffects.YIN.get());
        if (player.hasEffect(ExpansionEffects.YANG.get()) && immune(player, ExpansionEffects.YANG.get()))
            player.removeEffect(ExpansionEffects.YANG.get());
    }

    @SubscribeEvent
    public static void equipment(LivingEquipmentChangeEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) cleanse(player);
    }

    /** Before native effect ticking: also handles login, dawn/dusk and a dimension change. */
    @SubscribeEvent(priority = EventPriority.HIGHEST)
    public static void tick(LivingEvent.LivingTickEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) cleanse(player);
    }

    private QiConstitution() { }
}
