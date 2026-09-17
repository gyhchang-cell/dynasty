package com.dynasty;

import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * Dynasty 可使用物品：玉玺 / 圣旨 / 虎符 / 符纸。
 * Dynasty usable items: Jade Seal / Edict / Tiger Tally / Talisman.
 */
@SuppressWarnings("null")
public final class DynastyUsables {

    private DynastyUsables() {
    }

    private static void play(Level level, Player player) {
        if (!level.isClientSide) {
            level.playSound(null, player.blockPosition(), SoundEvents.AMETHYST_BLOCK_CHIME,
                    SoundSource.PLAYERS, 1.0F, 1.2F);
        }
    }

    /** 传国玉玺：赐予自身「铁壁」与「疾风」。/ Imperial Jade Seal: grants Iron Wall & Swift Wind. */
    /** 玉玺：右键查看王朝档案（潜行右键则为赐福）。*/
    public static class SealItem extends Item {
        public SealItem(Properties props) {
            super(props);
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            if (!player.isShiftKeyDown()) {
                if (level.isClientSide()) {
                    com.dynasty.client.ClientStats.requestAndOpen();
                }
                return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
            }
            player.addEffect(new MobEffectInstance(DynastyEffects.IRON_WALL.get(), 20 * 60, 0));
            player.addEffect(new MobEffectInstance(DynastyEffects.SWIFT_WIND.get(), 20 * 60, 0));
            play(level, player);
            player.getCooldowns().addCooldown(this, 20 * 30);
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
        }
    }

    /** 圣旨：为周围友军赐下「龙威」。/ Imperial Edict: grants Dragon's Might to nearby players. */
    public static class EdictItem extends Item {
        public EdictItem(Properties props) {
            super(props);
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            for (Player target : level.getEntitiesOfClass(Player.class, player.getBoundingBox().inflate(8.0D))) {
                target.addEffect(new MobEffectInstance(DynastyEffects.DRAGON_MIGHT.get(), 20 * 45, 0));
            }
            play(level, player);
            player.getCooldowns().addCooldown(this, 20 * 60);
            if (!player.getAbilities().instabuild) {
                stack.shrink(1);
            }
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
        }
    }

    /** 虎符：威慑周围敌人。 / Tiger Tally: intimidates nearby enemies. */
    /** 虎符：右键打开调兵界面（潜行右键则为威慑）。 / Tiger Tally: opens the army screen (sneak = intimidate). */
    public static class TallyItem extends Item {
        public TallyItem(Properties props) {
            super(props);
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            if (!player.isShiftKeyDown()) {
                if (level.isClientSide()) {
                    com.dynasty.client.ClientArmy.open();
                }
                return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
            }
            for (Mob mob : level.getEntitiesOfClass(Mob.class, player.getBoundingBox().inflate(10.0D))) {
                mob.addEffect(new MobEffectInstance(DynastyEffects.INTIMIDATION.get(), 20 * 20, 0));
            }
            play(level, player);
            player.getCooldowns().addCooldown(this, 20 * 45);
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
        }
    }

    /** 符纸：短暂获得「铁壁」。 / Talisman: short Iron Wall. */
    public static class TalismanItem extends Item {
        public TalismanItem(Properties props) {
            super(props);
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            player.addEffect(new MobEffectInstance(DynastyEffects.IRON_WALL.get(), 20 * 15, 0));
            play(level, player);
            if (!player.getAbilities().instabuild) {
                stack.shrink(1);
            }
            return InteractionResultHolder.sidedSuccess(stack, player.level().isClientSide());
        }
    }

    /** 丹药：使用后获得指定状态效果。 / Pill: applies a status effect when consumed. */
    public static class PillItem extends Item {

        private final net.minecraft.world.effect.MobEffect effect;
        private final int seconds;
        private final int amplifier;

        public PillItem(Properties props, net.minecraft.world.effect.MobEffect effect, int seconds, int amplifier) {
            super(props);
            this.effect = effect;
            this.seconds = seconds;
            this.amplifier = amplifier;
        }

        @Override
        public net.minecraft.world.item.ItemStack finishUsingItem(ItemStack stack, Level level, net.minecraft.world.entity.LivingEntity entity) {
            ItemStack result = super.finishUsingItem(stack, level, entity);
            if (!level.isClientSide) {
                entity.addEffect(new MobEffectInstance(this.effect, 20 * this.seconds, this.amplifier));
            }
            return result;
        }

        @Override
        public int getUseDuration(ItemStack stack) {
            return 24;
        }

        @Override
        public net.minecraft.world.InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            player.startUsingItem(hand);
            return net.minecraft.world.InteractionResultHolder.consume(player.getItemInHand(hand));
        }
    }

    /** 科举试卷：右键打开科举答题界面。 / Exam paper: opens the Keju GUI. */
    public static class ExamPaperItem extends Item {
        public ExamPaperItem(Properties props) {
            super(props);
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            if (player instanceof net.minecraft.server.level.ServerPlayer serverPlayer) {
                DynastyKeju.openExam(serverPlayer);
            }
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
        }
    }

    /** 王朝图鉴：右键打开内置指南界面。 / Dynasty Codex: opens the built-in guide GUI. */
    public static class GuideItem extends Item {
        public GuideItem(Properties props) {
            super(props);
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            if (level.isClientSide()) {
                com.dynasty.client.ClientGuide.open();
            }
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
        }
    }

    /**
     * 百宝妆匣：右键随机开出一件王朝饰品，开完即消耗。
     * Trinket Box: rolls one random accessory and is consumed on use.
     */
    public static class TrinketBoxItem extends Item {
        public TrinketBoxItem(Properties props) {
            super(props);
        }

        @Override
        public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
            ItemStack stack = player.getItemInHand(hand);
            if (!level.isClientSide()) {
                ItemStack gift = DynastyTrinkets.randomGift(player.getRandom());
                if (!player.getInventory().add(gift)) {
                    player.drop(gift, false);
                }
                level.playSound(null, player.blockPosition(), SoundEvents.PLAYER_LEVELUP,
                        SoundSource.PLAYERS, 0.8F, 1.4F);
                if (!player.getAbilities().instabuild) {
                    stack.shrink(1);
                }
            }
            return InteractionResultHolder.sidedSuccess(stack, level.isClientSide());
        }
    }
}
