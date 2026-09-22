package com.dynasty.keju;

import com.dynasty.Dynasty;
import com.dynasty.DynastyKeju;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.AddReloadListenerEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.server.ServerStoppingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 科举自己的一套事件订阅（不碰全局主类，也不复用其它系统的监听器）：
 *
 * 1. 服务端数据重载（{@code /reload} 与服务器启动）→ 挂上题库监听器；
 * 2. 服务器关闭 → 清空该实例的待答会话与服务端缓存；
 * 3. 玩家登出 → 丢弃该玩家的待答会话，并只清理**已过期**的冷却记录
 *    （仍在 30 秒内的记录保留，所以断线重连不能绕过冷却）。
 */
@Mod.EventBusSubscriber(modid = Dynasty.MODID)
public final class KejuEvents {

    private KejuEvents() {
    }

    @SubscribeEvent
    public static void onAddReloadListener(AddReloadListenerEvent event) {
        event.addListener(new KejuReloadListener(DynastyKeju.BANK_LOCATION, DynastyKeju::onBankReload));
    }

    @SubscribeEvent
    public static void onServerStopping(ServerStoppingEvent event) {
        DynastyKeju.shutdown(event.getServer());
    }

    @SubscribeEvent
    public static void onPlayerLoggedOut(PlayerEvent.PlayerLoggedOutEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            DynastyKeju.forgetPlayer(player);
        }
    }
}
