package com.dynasty;

import com.dynasty.Dynasty;
import com.dynasty.entity.DynastyEntities;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.Mob;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 王朝世界事件：民怨叛乱、节日自动触发、战功（击杀奖励）。
 * Dynasty world events: rebellion uprisings, automatic festivals and battle merit rewards.
 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public class DynastyWorldEvents {

    private static int tickCounter = 0;

    @SubscribeEvent
    public static void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        if (++tickCounter < 200) {
            return;
        }
        tickCounter = 0;
        String festival = DynastyFestivals.today();
        for (ServerLevel level : event.getServer().getAllLevels()) {
            for (ServerPlayer player : level.players()) {
                // 1) 节日自动触发（每天一次）/ automatic festival, once per real day
                if (festival != null) {
                    String key = "dynasty_festival_day";
                    String stamp = festival + ":" + java.time.LocalDate.now();
                    if (!stamp.equals(player.getPersistentData().getString(key))) {
                        player.getPersistentData().putString(key, stamp);
                        DynastyFestivals.trigger(level, festival, player);
                    }
                }
                // 2) 叛乱爆发 / rebellion uprising
                int rebellion = DynastyStats.getRebellion(player);
                if (rebellion >= 100 && player.getRandom().nextInt(6) == 0) {
                    spawnRebellion(level, player);
                } else if (rebellion >= 60 && player.getRandom().nextInt(20) == 0) {
                    DynastyStats.addRebellion(player, 1);
                }
                // 3) 任务：维度探索 / quest: dimension visits
                var dim = level.dimension().location();
                if (dim.getNamespace().equals(com.dynasty.Dynasty.MODID)) {
                    if (dim.getPath().equals("celestial_dynasty")) {
                        DynastyQuestManager.notifyEvent(player, "dim_celestial");
                    } else if (dim.getPath().equals("underworld")) {
                        DynastyQuestManager.notifyEvent(player, "dim_underworld");
                    }
                }
                // 4) 饰品效果刷新 / refresh trinket effects
                DynastyTrinkets.tick(player);
            }
        }
    }

    private static void spawnRebellion(ServerLevel level, ServerPlayer player) {
        dynastySpawn(level, player, DynastyEntities.REBEL_SOLDIER.get(), 4);
        if (player.getRandom().nextInt(3) == 0) {
            dynastySpawn(level, player, DynastyEntities.REBEL_GENERAL.get(), 1);
        }
        DynastyStats.addRebellion(player, -35);
        level.playSound(null, player.blockPosition(), SoundEvents.RAVAGER_ROAR, SoundSource.HOSTILE, 2.0F, 0.8F);
        player.sendSystemMessage(Component.literal("§4[叛乱] §c叛军揭竿而起，叛将率众来袭！"));
    }

    private static void dynastySpawn(ServerLevel level, ServerPlayer player, net.minecraft.world.entity.EntityType<? extends Mob> type, int count) {
        for (int i = 0; i < count; i++) {
            Mob mob = type.create(level);
            if (mob == null) {
                continue;
            }
            double dx = (level.random.nextDouble() - 0.5D) * 24.0D;
            double dz = (level.random.nextDouble() - 0.5D) * 24.0D;
            mob.moveTo(player.getX() + dx, player.getY(), player.getZ() + dz,
                    level.random.nextFloat() * 360.0F, 0.0F);
            level.addFreshEntity(mob);
        }
    }

    /** 击杀王朝 Boss / 神兽可获得功名与忠诚。/ Killing dynasty bosses and beasts grants merit and loyalty. */
    /** 玩家登录：同步饰品 / on login: sync trinkets */
    @SubscribeEvent
    public static void onPlayerLogin(net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedInEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            DynastyTrinkets.tick(player);
            DynastyTrinketSync.send(player);
            DynastyManual.giveOnce(player);
        }
    }

    /** 服务器启动时校验任务数据 / validates quest data on server start */
    @SubscribeEvent
    public static void onServerStarted(net.minecraftforge.event.server.ServerStartedEvent event) {
        int problems = 0;
        for (DynastyQuests.Quest quest : DynastyQuests.all()) {
            net.minecraft.resources.ResourceLocation id = net.minecraft.resources.ResourceLocation.tryParse(quest.target);
            if (id == null) {
                continue;
            }
            if (quest.type == DynastyQuests.Type.ITEM
                    && net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(id) == null) {
                Dynasty.LOGGER.warn("[Dynasty] quest {} targets unknown item {}", quest.index, quest.target);
                problems++;
            } else if (quest.type == DynastyQuests.Type.KILL
                    && net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getValue(id) == null) {
                Dynasty.LOGGER.warn("[Dynasty] quest {} targets unknown entity {}", quest.index, quest.target);
                problems++;
            }
        }
        Dynasty.LOGGER.info("[Dynasty] quests validated: {} quests, {} problems",
                DynastyQuests.count(), problems);
    }

    @SubscribeEvent
    public static void onLivingDeath(LivingDeathEvent event) {
        if (!(event.getSource().getEntity() instanceof ServerPlayer player)) {
            return;
        }
        var type = event.getEntity().getType();
        // 任务：击杀计数 / quest kill counters
        net.minecraft.resources.ResourceLocation killId = net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getKey(type);
        if (killId != null) {
            DynastyQuestManager.onKill(player, killId.toString());
        }
        if (type == DynastyEntities.DRAGON_EMPEROR.get()) {
            DynastyStats.addMerit(player, 300);
            DynastyStats.addLoyalty(player, 25);
            DynastyStats.addRebellion(player, -50);
            player.sendSystemMessage(Component.literal("§6[战功] 龙帝伏诛！功名 +300"));
        } else if (type == DynastyEntities.UNDEAD_FIRST_EMPEROR.get()) {
            DynastyStats.addMerit(player, 200);
            DynastyStats.addLoyalty(player, 15);
            player.sendSystemMessage(Component.literal("§6[战功] 亡故始皇安息。功名 +200"));
        } else if (type == DynastyEntities.REBEL_GENERAL.get()) {
            DynastyStats.addMerit(player, 150);
            DynastyStats.addRebellion(player, -40);
            player.sendSystemMessage(Component.literal("§6[战功] 叛将授首！功名 +150，叛乱 -40"));
        } else if (type == DynastyEntities.EUNUCH_MASTERMIND.get()) {
            DynastyStats.addMerit(player, 160);
            DynastyStats.addLoyalty(player, 10);
            player.sendSystemMessage(Component.literal("§6[战功] 权阉伏法！功名 +160"));
        } else if (type == DynastyEntities.NIAN_BEAST.get()) {
            DynastyStats.addMerit(player, 120);
            DynastyStats.addLoyalty(player, 12);
            player.sendSystemMessage(Component.literal("§6[战功] 年兽驱除！功名 +120"));
        } else if (type == DynastyEntities.PHOENIX.get() || type == DynastyEntities.QILIN.get()
                || type == DynastyEntities.NINE_TAILED_FOX.get()) {
            DynastyStats.addMerit(player, 40);
        }
    }
}
