package com.dynasty;

import java.util.UUID;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.*;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

/** Per-stack kill experience. Vanilla smithing_transform copies this NBT during evolution. */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class DynastyWeaponProgression {
    public static final String KEY = "dynastyWeaponGrowth";
    private static final String SHOT = "dynastyGrowthShot";
    private DynastyWeaponProgression() {}

    public static boolean eligible(ItemStack stack) {
        var id = ForgeRegistries.ITEMS.getKey(stack.getItem());
        return id != null && id.getNamespace().equals(Dynasty.MODID)
                && (stack.getItem() instanceof SwordItem || stack.getItem() instanceof AxeItem
                    || stack.getItem() instanceof BowItem || stack.getItem() instanceof CrossbowItem || stack.getItem() instanceof TridentItem);
    }
    public static int level(ItemStack stack) {
        return stack.hasTag() ? Math.max(1, stack.getTag().getCompound(KEY).getInt("level")) : 1;
    }
    public static long progress(ItemStack stack) {
        return stack.hasTag() ? Math.max(0, stack.getTag().getCompound(KEY).getLong("xp")) : 0;
    }
    public static long required(int level) {
        return (long) Math.min(Long.MAX_VALUE / 4.0, 6 + 4.0 * level * level);
    }
    public static double multiplier(int level) {
        return Math.min(1.0e10, 1 + 0.10 * (level - 1.0) + 0.005 * (level - 1.0) * (level - 1.0));
    }
    public static ItemStack attackWeapon(Player player, DamageSource source) {
        if (source.getDirectEntity() instanceof AbstractArrow arrow)
            return ItemStack.of(arrow.getPersistentData().getCompound(SHOT));
        return source.getDirectEntity() == player ? player.getMainHandItem() : ItemStack.EMPTY;
    }
    @SubscribeEvent
    public static void onArrow(EntityJoinLevelEvent event) {
        if (event.getLevel().isClientSide || !(event.getEntity() instanceof AbstractArrow arrow)
                || !(arrow.getOwner() instanceof Player player) || arrow.getPersistentData().contains(SHOT)) return;
        ItemStack bow = player.getUseItem();
        if (!(bow.getItem() instanceof BowItem || bow.getItem() instanceof CrossbowItem)) bow = player.getMainHandItem();
        if (!(bow.getItem() instanceof BowItem || bow.getItem() instanceof CrossbowItem)) bow = player.getOffhandItem();
        if (!eligible(bow) || !(bow.getItem() instanceof BowItem || bow.getItem() instanceof CrossbowItem)) return;
        CompoundTag growth = bow.getOrCreateTagElement(KEY);
        if (!growth.hasUUID("identity")) growth.putUUID("identity", UUID.randomUUID());
        arrow.getPersistentData().put(SHOT, bow.save(new CompoundTag()));
    }
    public static void reward(Player player, DamageSource source, String school, int points) {
        ItemStack stack = attackWeapon(player, source);
        if (!eligible(stack)) return;
        if (source.getDirectEntity() instanceof AbstractArrow) {
            CompoundTag snapshot = stack.getTagElement(KEY);
            if (snapshot == null || !snapshot.hasUUID("identity")) return;
            UUID identity = snapshot.getUUID("identity");
            stack = ItemStack.EMPTY;
            for (int slot = 0; slot < player.getInventory().getContainerSize(); slot++) {
                ItemStack candidate = player.getInventory().getItem(slot);
                CompoundTag data = candidate.getTagElement(KEY);
                if (eligible(candidate) && data != null && data.hasUUID("identity")
                        && data.getUUID("identity").equals(identity)) { stack = candidate; break; }
            }
            if (stack.isEmpty()) return; // Never grant a replacement item or upgrade the newly held weapon.
        }
        int old = level(stack), next = old;
        long xp = Math.min(Long.MAX_VALUE / 2, progress(stack) + points);
        while (next < Integer.MAX_VALUE && xp >= required(next)) {
            xp -= required(next);
            next++;
        }
        CompoundTag data = stack.getOrCreateTagElement(KEY);
        data.putInt("level", next);
        data.putLong("xp", xp);
        data.putString("school", school);
        if (next > old) player.displayClientMessage(net.minecraft.network.chat.Component.translatable(
                "message.dynasty.weapon.level", stack.getHoverName(), next), true);
    }
    public static String storedSchool(ItemStack stack) {
        CompoundTag data = stack.getTagElement(KEY);
        return data == null ? "" : data.getString("school");
    }
}
