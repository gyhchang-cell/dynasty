package com.dynasty;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.SwordItem;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import java.util.Set;

/**
 * Four equipment paths grow through successful combat. Progress is owned by the player, so
 * changing weapons never destroys it; a path's two Curios pieces also strengthen its passive.
 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class DynastySchoolProgression {
    private static final String SAVE_KEY = "dynastySchoolProgression";
    private static final String[] PATHS = {"guard", "sword", "archer", "talisman"};
    private static final int[] MILESTONES = {1, 3, 6, 10};

    private DynastySchoolProgression() { }

    static long requiredForNext(int rank) {
        double next = (double) rank + 1.0;
        return (long) Math.min(Long.MAX_VALUE / 4.0, 5.0 + 3.0 * next * next);
    }

    static double masteryMultiplier(int rank) {
        double value = 1.0 + 0.12 * rank + 0.02 * (double) rank * rank;
        return Math.min(value, 1.0e20); // Keep the float damage event finite at extreme save values.
    }

    static int practicePoints(float targetMaxHealth) {
        if (!Float.isFinite(targetMaxHealth)) return 1;
        return Math.min(8, 1 + (int) Math.max(0, targetMaxHealth / 80.0f));
    }

    public static int rank(Player player, String path) {
        if (!valid(path)) return 0;
        return Math.max(0, player.getPersistentData().getCompound(SAVE_KEY).getCompound(path).getInt("rank"));
    }

    public static long progress(Player player, String path) {
        if (!valid(path)) return 0;
        return Math.max(0, player.getPersistentData().getCompound(SAVE_KEY).getCompound(path).getLong("progress"));
    }

    public static void showProgress(ServerPlayer player) {
        player.sendSystemMessage(Component.literal("§6[王朝流派]§r 击杀敌人提升熟练度和武器等级；强敌提供更多历练。"));
        for (String path : PATHS) {
            int current = rank(player, path);
            long earned = progress(player, path);
            player.sendSystemMessage(Component.literal("§e" + Component.translatable("school.dynasty." + path).getString()
                    + "§r " + current + "阶 · " + earned + "/" + requiredForNext(current)
                    + " · 伤害 ×" + String.format(java.util.Locale.ROOT, "%.2f", masteryMultiplier(current))));
        }
    }

    private static boolean valid(String path) {
        for (String entry : PATHS) if (entry.equals(path)) return true;
        return false;
    }

    private static void practice(ServerPlayer player, String path, LivingEntity target) {
        CompoundTag root = player.getPersistentData().getCompound(SAVE_KEY);
        CompoundTag state = root.getCompound(path);
        int previous = Math.max(0, state.getInt("rank"));
        if (previous == Integer.MAX_VALUE) return;
        long points = Math.max(0, state.getLong("progress"));
        points = Math.min(Long.MAX_VALUE / 2, points + practicePoints(target.getMaxHealth()));
        int next = previous;
        while (next < Integer.MAX_VALUE && points >= requiredForNext(next)) {
            next++;
            points -= requiredForNext(next - 1);
        }
        state.putInt("rank", next);
        state.putLong("progress", points);
        root.put(path, state);
        player.getPersistentData().put(SAVE_KEY, root);
        if (next != previous) {
            player.displayClientMessage(Component.translatable("message.dynasty.school.mastery",
                    Component.translatable("school.dynasty." + path), next), true);
            for (int milestone : MILESTONES) if (previous < milestone && next >= milestone) {
                var advancement = player.server.getAdvancements().getAdvancement(
                        new ResourceLocation(Dynasty.MODID, "school_" + path + "_rank_" + milestone));
                if (advancement != null) player.getAdvancements().award(advancement, "attained");
            }
        }
    }

    private static String school(Player player, LivingEntity target,
                                 net.minecraft.world.damagesource.DamageSource source) {
        if (!(target instanceof net.minecraft.world.entity.monster.Enemy)
                || target.isAlliedTo(player) || player.isAlliedTo(target)) return null;
        Set<String> ornaments = DynastyTrinkets.activeIds(player);
        var used = DynastyWeaponProgression.attackWeapon(player, source);
        String stored = DynastyWeaponProgression.storedSchool(used);
        boolean arrow = source.getDirectEntity() instanceof AbstractArrow projectile
                && projectile.getOwner() == player;
        if (arrow) {
            return DynastyWeaponProgression.eligible(used)
                    || ornaments.contains("guanxing_pendant") || ornaments.contains("mingxian_ring")
                    || DynastySchoolAccessories.count(ornaments, "archer") > 0
                    ? "archer" : null;
        }
        if (!source.is(DamageTypes.PLAYER_ATTACK) || source.getDirectEntity() != player
                || !DynastyWeaponProgression.eligible(used)) return null;
        String weapon = DynastySchoolCombat.weapon(player);
        if (weapon.equals("zhenyue_blade")) return "guard";
        if (weapon.equals("liuyun_sword")) return "sword";
        if (weapon.equals("chiling_brush")) return "talisman";
        if (weapon.equals("beichen_spear")) return "guard";
        if (weapon.equals("chengying_sword")) return "sword";
        if (weapon.equals("leifu_staff")) return "talisman";
        // Other swords are viable for every melee path. The equipped Curios set chooses the path.
        int guard = count(ornaments, "zhenguan_mirror", "huben_bracer") + DynastySchoolAccessories.count(ornaments, "guard");
        int sword = count(ornaments, "liancheng_tassel", "tayun_pendant") + DynastySchoolAccessories.count(ornaments, "sword");
        int talisman = count(ornaments, "sitian_seal", "dingfeng_silk") + DynastySchoolAccessories.count(ornaments, "talisman");
        int best = Math.max(guard, Math.max(sword, talisman));
        if (best == 0) {
            if (valid(stored)) return stored;
            return switch (weapon) {
                case "juque_sword", "qinglong_dao", "xuanwu_blade", "pojun_axe", "juling_axe", "leiting_hammer" -> "guard";
                case "taiyi_sword", "taiyi_whisk", "hunyuan_staff", "zhuque_fan" -> "talisman";
                default -> "sword";
            };
        }
        if (guard == best) return "guard";
        return sword == best ? "sword" : "talisman";
    }

    private static int count(Set<String> ids, String first, String second) {
        return (ids.contains(first) ? 1 : 0) + (ids.contains(second) ? 1 : 0);
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onHurt(LivingHurtEvent event) {
        if (event.isCanceled() || event.getAmount() <= 0 || event.getEntity().level().isClientSide
                || DynastyTrinketOnHit.isSyntheticDamage()
                || !(event.getSource().getEntity() instanceof Player player)) return;
        String path = school(player, event.getEntity(), event.getSource());
        Set<String> ornaments = DynastyTrinkets.activeIds(player);
        double bonus = 1.0 + DynastySchoolAccessories.bonus(player, event.getSource(), ornaments)
                + DynastyAccessoryRefining.damageBonus(player,event.getSource());
        if (path == null) {
            // Generic melee and arrow bonuses also work with vanilla equipment; no school XP implied.
            event.setAmount((float) Math.min(1.0e30, event.getAmount() * bonus));
            return;
        }
        switch (path) {
            case "guard" -> {
                // Armour toughness now has an offensive route as well as reducing incoming damage.
                if (ornaments.contains("zhenguan_mirror")) {
                    double toughness = Math.max(0, player.getAttributeValue(Attributes.ARMOR_TOUGHNESS));
                    bonus += Math.min(2.0, toughness * 0.016);
                }
                if (ornaments.contains("huben_bracer")) bonus += 0.12;
            }
            case "sword" -> {
                if (ornaments.contains("liancheng_tassel")) bonus += 0.16;
                if (ornaments.contains("tayun_pendant"))
                    bonus += 0.12;
            }
            case "archer" -> {
                if (ornaments.contains("guanxing_pendant")) bonus += event.getEntity().isCurrentlyGlowing() ? 0.25 : 0.10;
                if (ornaments.contains("mingxian_ring")) bonus += 0.12;
            }
            case "talisman" -> {
                if (ornaments.contains("sitian_seal"))
                    bonus += 0.25;
                if (ornaments.contains("dingfeng_silk"))
                    bonus += 0.15;
            }
            default -> { return; }
        }
        double result = event.getAmount() * masteryMultiplier(rank(player, path)) * bonus
                * DynastyWeaponProgression.multiplier(DynastyWeaponProgression.level(
                        DynastyWeaponProgression.attackWeapon(player, event.getSource())));
        event.setAmount((float) Math.min(1.0e30, result));
    }

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public static void onKill(LivingDeathEvent event) {
        if (event.isCanceled() || event.getEntity().level().isClientSide
                || !(event.getSource().getEntity() instanceof ServerPlayer player)) return;
        String path = school(player, event.getEntity(), event.getSource());
        if (path == null) return;
        // Forge death callbacks can be invoked again by other mods; one victim awards once.
        if (event.getEntity().getPersistentData().getBoolean("dynastyGrowthAwarded")) return;
        event.getEntity().getPersistentData().putBoolean("dynastyGrowthAwarded", true);
        practice(player, path, event.getEntity());
        DynastyWeaponProgression.reward(player, event.getSource(), path, practicePoints(event.getEntity().getMaxHealth()));
        var advancement = player.server.getAdvancements().getAdvancement(
                new ResourceLocation(Dynasty.MODID, "build_" + path + "_trial"));
        if (advancement != null) player.getAdvancements().award(advancement, "performed");
    }

    @SubscribeEvent
    public static void onClone(PlayerEvent.Clone event) {
        CompoundTag previous = event.getOriginal().getPersistentData();
        if (previous.contains(SAVE_KEY))
            event.getEntity().getPersistentData().put(SAVE_KEY, previous.getCompound(SAVE_KEY).copy());
    }
}
