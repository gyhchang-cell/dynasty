package com.dynasty;

import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraftforge.common.ToolAction;
import net.minecraftforge.common.ToolActions;

import java.util.List;

/** Optional mid-game combat tools. Deliberately independent of the end-game bow ritual. */
public final class DynastySchoolWeapons {
    private DynastySchoolWeapons() { }

    public static class SchoolBlade extends SwordItem {
        private final String id;
        SchoolBlade(String id, int damage, float speed) {
            super(DynastyTiers.BRONZE, damage, speed, new Item.Properties());
            this.id = id;
        }
        @Override public void appendHoverText(ItemStack stack, Level level, List<Component> lines, TooltipFlag flag) {
            super.appendHoverText(stack, level, lines, flag);
            // Client tooltip event supplies the concise view and Shift details once.
        }
    }

    public static final class GuardBlade extends SchoolBlade {
        public GuardBlade() { super("zhenyue_blade", 157, -2.6F); }
        @Override public UseAnim getUseAnimation(ItemStack stack) { return UseAnim.BLOCK; }
        @Override public int getUseDuration(ItemStack stack) { return 72000; }
        @Override public boolean canPerformAction(ItemStack stack, ToolAction action) {
            return action == ToolActions.SHIELD_BLOCK || super.canPerformAction(stack, action);
        }
        @Override public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            if (hand != InteractionHand.MAIN_HAND || player.getCooldowns().isOnCooldown(this))
                return InteractionResultHolder.fail(stack);
            player.startUsingItem(hand);
            return InteractionResultHolder.consume(stack);
        }
        @Override public void onUseTick(Level level, LivingEntity user, ItemStack stack, int remaining) {
            if (!level.isClientSide && user instanceof Player player && getUseDuration(stack) - remaining >= SchoolCombatRules.GUARD_TICKS) {
                player.stopUsingItem();
            }
        }
        @Override public void releaseUsing(ItemStack stack, Level level, LivingEntity user, int remaining) {
            guardCooldown(user);
        }
        @Override public void onStopUsing(ItemStack stack, LivingEntity user, int remaining) {
            // Hotbar changes and offhand swaps call stopUsingItem(), not releaseUsing().
            guardCooldown(user);
        }
        private void guardCooldown(LivingEntity user) {
            if (!user.level().isClientSide && user instanceof Player player && !player.getCooldowns().isOnCooldown(this))
                player.getCooldowns().addCooldown(this, SchoolCombatRules.GUARD_COOLDOWN);
        }
    }

    public static final class EdictBrush extends SchoolBlade {
        public EdictBrush() { super("chiling_brush", 112, -2.4F); }
        @Override public UseAnim getUseAnimation(ItemStack stack) { return UseAnim.BOW; }
        @Override public int getUseDuration(ItemStack stack) { return 72000; }
        @Override public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            if (hand != InteractionHand.MAIN_HAND || player.getCooldowns().isOnCooldown(this))
                return InteractionResultHolder.fail(stack);
            player.startUsingItem(hand);
            if (!level.isClientSide) DynastySchoolCombat.startEdict(player);
            return InteractionResultHolder.consume(stack);
        }
        @Override public void onUseTick(Level level, LivingEntity user, ItemStack stack, int remaining) {
            if (!level.isClientSide && user instanceof Player player) DynastySchoolCombat.chargeEdict(player);
        }
        @Override public void releaseUsing(ItemStack stack, Level level, LivingEntity user, int remaining) {
            if (!level.isClientSide && user instanceof Player player) DynastySchoolCombat.endCharge(player);
        }
        @Override public void onStopUsing(ItemStack stack, LivingEntity user, int remaining) {
            if (!user.level().isClientSide && user instanceof Player player) DynastySchoolCombat.endCharge(player);
        }
    }

    public static class StarBow extends BowItem {
        public StarBow() { super(new Item.Properties().durability(3000)); }
        @Override public AbstractArrow customArrow(AbstractArrow arrow) {
            arrow.setBaseDamage(arrow.getBaseDamage() * 2.0D + 30.0D);
            arrow.getPersistentData().putBoolean(DynastySchoolCombat.STAR_ARROW, true);
            // Capture the firing weapon: switching to an imperial weapon in flight must not borrow its damage.
            if (arrow.getOwner() instanceof Player player) {
                ItemStack firing = player.getUseItem();
                if (!(firing.getItem() instanceof StarBow)) firing = player.getMainHandItem();
                if (firing.getItem() instanceof StarBow)
                    arrow.getPersistentData().put(DynastySchoolCombat.FIRING_WEAPON, firing.save(new net.minecraft.nbt.CompoundTag()));
            }
            return arrow;
        }
        @Override public void appendHoverText(ItemStack stack, Level level, List<Component> lines, TooltipFlag flag) {
            super.appendHoverText(stack, level, lines, flag);
            // Client tooltip event supplies the concise view and Shift details once.
        }
    }

    /** Uses the vanilla aiming/release path, including the captured firing stack. */
    public static final class WindBow extends StarBow {
        @Override public AbstractArrow customArrow(AbstractArrow arrow) {
            super.customArrow(arrow);
            arrow.setBaseDamage(arrow.getBaseDamage() * 1.25D);
            arrow.setPierceLevel((byte)Math.max(1, arrow.getPierceLevel()));
            return arrow;
        }
    }
}
