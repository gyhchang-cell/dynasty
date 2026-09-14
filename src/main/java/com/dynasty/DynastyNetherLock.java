package com.dynasty;

import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraftforge.event.entity.EntityTravelToDimensionEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 关掉「原版地狱门」：王朝自己有一整套维度（地府 / 天朝 / 九霄 / 龙宫），
 * 不希望玩家绕过模组、用黑曜石门或现成的原版门直接进地狱。
 *
 * 做法两件事：
 *   1. 用地狱门框架点火要生成传送门时直接取消（{@link BlockEvent.PortalSpawnEvent}）；
 *   2. 任何「想要去原版地狱」的传送都拦下并给出提示（{@link EntityTravelToDimensionEvent}），
 *      这样即使是别人留下的旧传送门也进不去。
 *
 * 地狱里的东西不会因此缺：石英、萤石、灵魂沙、远古残骸、烈焰棒、恶魂之泪、岩浆膏
 * 现在都能在「地府」维度里找到（见 worldgen 里的地府配置）。
 *
 * Disables the vanilla Nether portal: the mod ships its own dimensions.
 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class DynastyNetherLock {

    private DynastyNetherLock() {
    }

    private static final String HINT = "§c[王朝] §r这里没有原版地狱门 —— 请用 §f地府传送门§r 进入地府。";

    @SubscribeEvent
    public static void onPortalSpawn(BlockEvent.PortalSpawnEvent event) {
        event.setCanceled(true);
        if (event.getLevel() instanceof ServerLevel level) {
            for (ServerPlayer player : level.getEntitiesOfClass(ServerPlayer.class,
                    new AABB(event.getPos()).inflate(8.0D))) {
                player.displayClientMessage(Component.literal(HINT), true);
            }
        }
    }

    @SubscribeEvent
    public static void onTravel(EntityTravelToDimensionEvent event) {
        if (event.getDimension() != Level.NETHER) {
            return;
        }
        event.setCanceled(true);
        if (event.getEntity() instanceof ServerPlayer player) {
            player.displayClientMessage(Component.literal(HINT), true);
        }
    }
}
