package com.dynasty;

import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.living.ShieldBlockEvent;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/** Four opt-in, bounded combat loops; server-only state, no recursive damage or world edits. */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class DynastySchoolCombat {
    public static final String STAR_ARROW = "dynasty_star_arrow", FIRING_WEAPON = "dynasty_star_weapon";
    private static final String PROCESSED = "dynasty_star_processed";
    private static final UUID SILK_RESISTANCE = UUID.fromString("e48ea587-a708-43e5-ab60-c427ed51bcf9");
    private static final Map<UUID, State> STATES = new HashMap<>();
    static final Set<String> ACCESSORIES = Set.of("zhenguan_mirror", "huben_bracer", "liancheng_tassel", "tayun_pendant",
            "guanxing_pendant", "mingxian_ring", "sitian_seal", "dingfeng_silk");

    private DynastySchoolCombat() { }
    static final class State {
        UUID attacked, comboTarget, marked;
        long attackTick = -1, counterUntil = -1, comboTick = -1, markedTick = -1, chargeStart = -1, edictUntil = -1;
        float attackStrength;
        int combo;
        String attackWeapon = "", held = "";
        Vec3 origin;
        boolean edictHadTarget;
    }
    static State state(Player player) { return STATES.computeIfAbsent(player.getUUID(), key -> new State()); }
    static long now(Player player) { return player.level().getGameTime(); }
    static boolean has(Player player, String id) { return DynastyTrinkets.activeIds(player).contains(id); }
    static String weapon(Player player) { return String.valueOf(DynastyTrinkets.idOf(player.getMainHandItem())); }
    static boolean hostile(Player player, LivingEntity target) {
        return target.isAlive() && target instanceof Enemy && !(target instanceof Player)
                && target != player && !target.isAlliedTo(player) && !player.isAlliedTo(target);
    }
    static boolean boss(LivingEntity target) {
        // Boss identity is not a toughness threshold: the First Emperor has 0.84 toughness.
        return target instanceof DynastyBossCombat.BarHolder
                || !target.canChangeDimensions() || DynastyBalance.isBossOrBeast(target.getType());
    }
    public static boolean isStarArrow(DamageSource source) {
        return source.getDirectEntity() instanceof AbstractArrow arrow && arrow.getPersistentData().getBoolean(STAR_ARROW);
    }
    public static ItemStack firingWeapon(DamageSource source, ItemStack held) {
        if(source.getDirectEntity() instanceof AbstractArrow a && a.getPersistentData().contains("cod4FiringWeapon"))
            return ItemStack.of(a.getPersistentData().getCompound("cod4FiringWeapon"));
        if (!isStarArrow(source)) {
            if(source.getDirectEntity() instanceof AbstractArrow && source.getEntity() instanceof Player player) {
                var snapshot=DynastyWeaponProgression.attackWeapon(player,source);
                if(!snapshot.isEmpty())return snapshot;
            }
            return held;
        }
        return ItemStack.of(source.getDirectEntity().getPersistentData().getCompound(FIRING_WEAPON));
    }

    @SubscribeEvent
    public static void attack(AttackEntityEvent event) {
        Player player = event.getEntity();
        if (player.level().isClientSide) return;
        State s = state(player);
        String held = weapon(player);
        if (!held.equals(s.held)) resetOnSwap(player, s, held);
        // Vanilla resets attackStrengthTicker before LivingHurtEvent: capture before Player.attack instead.
        s.attacked = event.getTarget().getUUID();
        s.attackTick = now(player);
        s.attackStrength = player.getAttackStrengthScale(0.5F);
        s.attackWeapon = held;
        if (!held.equals("liuyun_sword") || !SchoolCombatRules.fullAttack(s.attackStrength)
                || !event.getTarget().getUUID().equals(s.comboTarget)) s.combo = 0;
    }

    @SubscribeEvent(priority = EventPriority.LOW)
    public static void block(ShieldBlockEvent event) {
        if (!(event.getEntity() instanceof Player player) || player.level().isClientSide
                || !(player.getUseItem().getItem() instanceof DynastySchoolWeapons.GuardBlade)) return;
        event.setBlockedDamage(event.getOriginalBlockedDamage() * 0.5F);
        event.setShieldTakesDamage(false); // The sword is not a ShieldItem; charge one durability explicitly.
        if (event.getBlockedDamage() <= 0) return;
        player.getUseItem().hurtAndBreak(1, player, p -> p.broadcastBreakEvent(p.getUsedItemHand()));
        if (event.getDamageSource().getEntity() instanceof LivingEntity attacker && hostile(player, attacker)) {
            State s = state(player);
            s.held = weapon(player);
            s.counterUntil = now(player) + SchoolCombatRules.counterWindow(has(player, "zhenguan_mirror"));
            cue(player, "guard_ready");
        }
    }

    @SubscribeEvent(priority = EventPriority.LOW)
    public static void hurt(LivingHurtEvent event) {
        if (DynastyTrinketOnHit.isSyntheticDamage() || event.isCanceled() || event.getAmount() <= 0 || event.getEntity().level().isClientSide
                || !(event.getSource().getEntity() instanceof Player player)) return;
        LivingEntity target = event.getEntity();
        if (!hostile(player, target)) return;
        if (isStarArrow(event.getSource())) {
            starHit(player, target, (AbstractArrow) event.getSource().getDirectEntity(), event);
            return;
        }
        // Do not trigger on swept secondaries, thorns, trinket lightning, bow hits or synthetic recursive damage.
        if (!event.getSource().is(DamageTypes.PLAYER_ATTACK) || event.getSource().getDirectEntity() != player) return;
        State s = STATES.get(player.getUUID());
        if (s == null || s.attackTick != now(player) || !target.getUUID().equals(s.attacked)) return;
        s.attacked = null; // exactly once, and only the explicit attack target
        String held = weapon(player);
        if (!held.equals(s.attackWeapon) || !SchoolCombatRules.fullAttack(s.attackStrength) || !player.hasLineOfSight(target)) return;
        if (held.equals("zhenyue_blade") && s.counterUntil >= now(player)) {
            s.counterUntil = -1;
            event.setAmount(event.getAmount() * 1.35F);
            if (has(player, "huben_bracer")) {
                if (boss(target)) target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 0));
                else target.knockback(0.7, player.getX() - target.getX(), player.getZ() - target.getZ());
            }
            trial(player, "guard");
            impact(target);
        } else if (held.equals("liuyun_sword")) {
            s.combo = SchoolCombatRules.combo(s.combo, target.getUUID().equals(s.comboTarget), now(player) - s.comboTick,
                    SchoolCombatRules.comboWindow(has(player, "liancheng_tassel")), s.attackStrength);
            s.comboTarget = target.getUUID();
            s.comboTick = now(player);
            if (s.combo == 3) {
                s.combo = 0;
                event.setAmount(event.getAmount() * 1.5F);
                if (has(player, "tayun_pendant")) player.addEffect(new MobEffectInstance(DynastyEffects.SWIFT_WIND.get(), 40, 0));
                trial(player, "sword");
                impact(target);
            } else cue(player, "combo_" + s.combo);
        } else if (held.equals("chiling_brush") && s.edictUntil >= now(player)) {
            s.edictUntil = -1;
            event.setAmount(event.getAmount() * 1.5F);
            if (s.edictHadTarget) trial(player, "talisman");
            s.edictHadTarget = false;
            impact(target);
        }
    }

    private static void starHit(Player player, LivingEntity target, AbstractArrow arrow, LivingHurtEvent event) {
        if (!arrow.isCritArrow() || arrow.getOwner() != player || arrow.getPersistentData().getBoolean(PROCESSED)) return;
        arrow.getPersistentData().putBoolean(PROCESSED, true);
        State s = state(player);
        if (target.getUUID().equals(s.marked) && SchoolCombatRules.within(now(player), s.markedTick, SchoolCombatRules.MARK_WINDOW)) {
            s.marked = null;
            event.setAmount(event.getAmount() * 1.4F);
            if (has(player, "mingxian_ring")) target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, boss(target) ? 20 : 40, 0));
            trial(player, "archer");
            impact(target);
        } else {
            s.marked = target.getUUID();
            s.markedTick = now(player);
            if (has(player, "guanxing_pendant")) target.addEffect(new MobEffectInstance(MobEffects.GLOWING, 60, 0));
            cue(player, "star_marked");
        }
    }

    static int startEdict(Player player) {
        if (player.level().isClientSide || !weapon(player).equals("chiling_brush")
                || player.getCooldowns().isOnCooldown(DynastyWeapons.CHILING_BRUSH.get())) return 0;
        State s = state(player);
        s.held = weapon(player);
        s.origin = player.position();
        s.chargeStart = now(player);
        s.edictUntil = -1;
        player.getCooldowns().addCooldown(DynastyWeapons.CHILING_BRUSH.get(), SchoolCombatRules.EDICT_COOLDOWN);
        boolean seal = has(player, "sitian_seal");
        var targets = player.level().getEntitiesOfClass(LivingEntity.class,
                player.getBoundingBox().inflate(SchoolCombatRules.EDICT_RADIUS),
                target -> hostile(player, target) && player.distanceToSqr(target) <= 25 && player.hasLineOfSight(target));
        targets.sort(Comparator.comparingDouble(player::distanceToSqr));
        int count = Math.min(SchoolCombatRules.EDICT_LIMIT, targets.size());
        for (int i = 0; i < count; i++) {
            LivingEntity target = targets.get(i);
            target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, SchoolCombatRules.edictDuration(boss(target), seal), boss(target) ? 0 : 1));
        }
        s.edictHadTarget = count > 0;
        cue(player, "edict_cast");
        player.level().playSound(null, player.blockPosition(), SoundEvents.ENCHANTMENT_TABLE_USE, SoundSource.PLAYERS, 0.6F, 1.25F);
        return count;
    }

    static void chargeEdict(Player player) {
        State s = STATES.get(player.getUUID());
        if (s == null || s.chargeStart < 0) return;
        if (!charging(player, s)) { endCharge(player); return; }
        silkResistance(player, has(player, "dingfeng_silk"));
        if (now(player) - s.chargeStart >= SchoolCombatRules.EDICT_CHARGE) {
            s.edictUntil = now(player) + SchoolCombatRules.EDICT_WINDOW + (DynastySchoolProgression.equippedSynergy(player, "talisman") ? SchoolCombatRules.EDICT_WINDOW / 5 : 0);
            endCharge(player);
            player.stopUsingItem();
            cue(player, "edict_ready");
        }
    }
    private static boolean charging(Player player, State s) {
        return player.isUsingItem() && player.getUsedItemHand() == net.minecraft.world.InteractionHand.MAIN_HAND
                && player.getUseItem().getItem() instanceof DynastySchoolWeapons.EdictBrush
                && s.origin != null && player.position().distanceToSqr(s.origin) <= SchoolCombatRules.STATIONARY_DISTANCE_SQUARED;
    }
    static void endCharge(Player player) {
        State s = STATES.get(player.getUUID());
        if (s != null) s.chargeStart = -1;
        silkResistance(player, false);
    }
    private static void silkResistance(Player player, boolean enable) {
        var attribute = player.getAttribute(Attributes.KNOCKBACK_RESISTANCE);
        if (attribute == null) return;
        if (enable && attribute.getModifier(SILK_RESISTANCE) == null)
            attribute.addTransientModifier(new AttributeModifier(SILK_RESISTANCE, "dynasty_edict_charge", 0.5, AttributeModifier.Operation.ADDITION));
        else if (!enable) attribute.removeModifier(SILK_RESISTANCE);
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent event) {
        Player player = event.player;
        if (event.phase != TickEvent.Phase.END || player.level().isClientSide) return;
        State s = STATES.get(player.getUUID());
        if (s == null) return;
        String held = weapon(player);
        if (!held.equals(s.held)) resetOnSwap(player, s, held);
        if (s.chargeStart >= 0 && !charging(player, s)) endCharge(player);
        if (s.chargeStart < 0 || !has(player, "dingfeng_silk")) silkResistance(player, false);
    }
    private static void resetOnSwap(Player player, State s, String held) {
        s.held = held;
        s.combo = 0;
        s.comboTarget = null;
        s.counterUntil = -1;
        s.edictUntil = -1;
        s.attacked = null;
        endCharge(player);
        // A projectile already in flight retains its one-target mark even after a weapon swap.
    }
    static void forget(Player player) { silkResistance(player, false); STATES.remove(player.getUUID()); }
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent event) { forget(event.getEntity()); }
    @SubscribeEvent public static void dimension(PlayerEvent.PlayerChangedDimensionEvent event) { forget(event.getEntity()); }
    @SubscribeEvent public static void death(LivingDeathEvent event) { if (event.getEntity() instanceof Player player) forget(player); }
    @SubscribeEvent public static void stop(ServerStoppedEvent event) { STATES.clear(); }
    private static void cue(Player player, String name) {
        player.displayClientMessage(net.minecraft.network.chat.Component.translatable("message.dynasty.school." + name), true);
    }
    private static void impact(LivingEntity target) {
        if (target.level() instanceof ServerLevel level)
            level.sendParticles(ParticleTypes.ENCHANTED_HIT, target.getX(), target.getY() + target.getBbHeight() * .6, target.getZ(), 8, .25, .3, .25, .02);
    }
    private static void trial(Player player, String school) {
        // The introductory milestone is now awarded by a school kill in DynastySchoolProgression.
        // Technique effects remain available without being a progression requirement.
    }
}
