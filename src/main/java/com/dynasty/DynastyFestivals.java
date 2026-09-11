package com.dynasty;

import com.dynasty.entity.DynastyEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.animal.Rabbit;
import net.minecraft.world.entity.projectile.FireworkRocketEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;

import java.time.LocalDate;
import java.time.MonthDay;
import java.util.List;

/**
 * 王朝节日系统：春节、端午、中秋、重阳、除夕。
 * Dynasty festival system: Spring Festival, Dragon Boat, Mid-Autumn, Double Ninth and New Year's Eve.
 */
@SuppressWarnings("null")
public final class DynastyFestivals {

    private DynastyFestivals() {
    }

    public static final String[] IDS = {"spring", "dragonboat", "midautumn", "double9", "newyear"};

    public static String nameZh(String id) {
        return switch (id) {
            case "dragonboat" -> "端午节";
            case "midautumn" -> "中秋节";
            case "double9" -> "重阳节";
            case "newyear" -> "除夕";
            default -> "春节";
        };
    }

    public static String nameEn(String id) {
        return switch (id) {
            case "dragonboat" -> "Dragon Boat Festival";
            case "midautumn" -> "Mid-Autumn Festival";
            case "double9" -> "Double Ninth Festival";
            case "newyear" -> "New Year's Eve";
            default -> "Spring Festival";
        };
    }

    /** 今天是什么节日（无则 null）。/ Today's festival id, or null. */
    public static String today() {
        MonthDay now = MonthDay.from(LocalDate.now());
        if (inRange(now, 2, 1, 2, 20)) {
            return "spring";
        }
        if (inRange(now, 6, 1, 6, 10)) {
            return "dragonboat";
        }
        if (inRange(now, 9, 15, 9, 25)) {
            return "midautumn";
        }
        if (inRange(now, 10, 1, 10, 10)) {
            return "double9";
        }
        if ((now.getMonthValue() == 12 && now.getDayOfMonth() >= 31)
                || (now.getMonthValue() == 1 && now.getDayOfMonth() <= 2)) {
            return "newyear";
        }
        return null;
    }

    private static boolean inRange(MonthDay now, int m1, int d1, int m2, int d2) {
        return now.compareTo(MonthDay.of(m1, d1)) >= 0 && now.compareTo(MonthDay.of(m2, d2)) <= 0;
    }

    /** 触发节日。/ Triggers a festival for the whole level. */
    public static void trigger(ServerLevel level, String id, ServerPlayer host) {
        BlockPos origin = host != null ? host.blockPosition() : level.getSharedSpawnPos();
        List<ServerPlayer> players = level.players();
        switch (id) {
            case "dragonboat" -> {
                for (ServerPlayer p : players) {
                    p.addEffect(new MobEffectInstance(MobEffects.WATER_BREATHING, 20 * 300, 0));
                    p.addEffect(new MobEffectInstance(MobEffects.DOLPHINS_GRACE, 20 * 300, 0));
                    give(p, DynastyItems.DUMPLING.get(), 3);
                }
                broadcast(level, "§b[端午] §f龙舟竞渡，艾草飘香！");
            }
            case "midautumn" -> {
                for (ServerPlayer p : players) {
                    p.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION, 20 * 600, 0));
                    give(p, DynastyItems.MOONCAKE.get(), 3);
                }
                for (int i = 0; i < 4; i++) {
                    Rabbit rabbit = EntityType.RABBIT.create(level);
                    if (rabbit != null) {
                        rabbit.moveTo(origin.getX() + level.random.nextInt(9) - 4, origin.getY(),
                                origin.getZ() + level.random.nextInt(9) - 4, 0.0F, 0.0F);
                        level.addFreshEntity(rabbit);
                    }
                }
                broadcast(level, "§e[中秋] §f月满人间，共赏婵娟！");
            }
            case "double9" -> {
                for (ServerPlayer p : players) {
                    p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE, 20 * 300, 0));
                    p.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 20 * 120, 0));
                    give(p, DynastyItems.WINE.get(), 2);
                }
                broadcast(level, "§6[重阳] §f登高望远，遍插茱萸！");
            }
            case "newyear" -> {
                for (ServerPlayer p : players) {
                    give(p, DynastyItems.GOLD_COIN.get(), 8);
                    give(p, DynastyItems.CANDIED_HAWTHORN.get(), 4);
                    p.addEffect(new MobEffectInstance(MobEffects.LUCK, 20 * 600, 1));
                }
                fireworks(level, origin);
                broadcast(level, "§c[除夕] §f爆竹声中一岁除，春风送暖入屠苏！");
            }
            default -> {
                for (ServerPlayer p : players) {
                    p.addEffect(new MobEffectInstance(MobEffects.REGENERATION, 20 * 300, 0));
                    p.addEffect(new MobEffectInstance(MobEffects.LUCK, 20 * 900, 0));
                    DynastyStats.addLoyalty(p, 5);
                    give(p, DynastyItems.DUMPLING.get(), 4);
                    give(p, DynastyItems.GOLD_COIN.get(), 6);
                }
                fireworks(level, origin);
                spawnNianBeast(level, origin);
                broadcast(level, "§4[春节] §f新春大吉！年兽已现，备好爆竹（爆炸伤害加倍）！");
            }
        }
        level.playSound(null, origin, SoundEvents.BELL_BLOCK, SoundSource.AMBIENT, 3.0F, 0.6F);
    }

    /** 年兽出没 / spawns a Nian Beast near the origin */
    private static void spawnNianBeast(ServerLevel level, BlockPos origin) {
        long nearby = level.getEntitiesOfClass(com.dynasty.entity.DynastyMobs.NianBeast.class,
                net.minecraft.world.phys.AABB.ofSize(net.minecraft.world.phys.Vec3.atCenterOf(origin),
                        96.0D, 64.0D, 96.0D)).size();
        if (nearby >= 2) {
            return;
        }
        Mob nian = DynastyEntities.NIAN_BEAST.get().create(level);
        if (nian != null) {
            nian.moveTo(origin.getX() + 3, origin.getY() + 1, origin.getZ() + 3, 0.0F, 0.0F);
            level.addFreshEntity(nian);
        }
    }

    /** 烟花 / spawns a firework rocket with the given colours */
    public static void fireworks(ServerLevel level, BlockPos pos) {
        int[][] colors = {{0xFF5555, 0xFFAA00}, {0x55FF55, 0x55FFFF}, {0xAA00FF, 0xFFFFFF}};
        for (int i = 0; i < 6; i++) {
            ItemStack rocket = new ItemStack(Items.FIREWORK_ROCKET);
            CompoundTag fireworks = rocket.getOrCreateTagElement("Fireworks");
            ListTag explosions = new ListTag();
            CompoundTag explosion = new CompoundTag();
            explosion.putInt("Type", 1);
            explosion.putIntArray("Colors", colors[i % colors.length]);
            explosion.putBoolean("Flicker", true);
            explosion.putBoolean("Trail", true);
            explosions.add(explosion);
            fireworks.putByte("Flight", (byte) 1);
            fireworks.put("Explosions", explosions);
            BlockPos at = pos.offset(level.random.nextInt(9) - 4, 1, level.random.nextInt(9) - 4);
            level.addFreshEntity(new FireworkRocketEntity(level, at.getX() + 0.5D, at.getY(),
                    at.getZ() + 0.5D, rocket));
        }
    }

    private static void give(ServerPlayer player, Item item, int count) {
        player.getInventory().add(new ItemStack(item, count));
    }

    private static void broadcast(ServerLevel level, String message) {
        for (ServerPlayer player : level.players()) {
            player.sendSystemMessage(Component.literal(message));
        }
    }

    /** 通用刷怪工具 / generic mob spawn helper */
    public static void spawnFestivalMob(ServerLevel level, EntityType<? extends Mob> type, BlockPos pos) {
        Mob mob = type.create(level);
        if (mob != null) {
            mob.moveTo(pos.getX(), pos.getY(), pos.getZ(), 0.0F, 0.0F);
            level.addFreshEntity(mob);
        }
    }
}
