package com.dynasty.client;

import com.dynasty.network.DynastyNetwork;
import com.dynasty.network.QuestRequestPacket;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.network.chat.Component;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/**
 * 客户端 Forge 总线事件：在背包界面左上角加上「王朝任务」按钮（类似任务模组的入口）。
 * Client Forge-bus events: adds a "Dynasty Quests" button to the top-left of the inventory screen.
 */
@Mod.EventBusSubscriber(modid = com.dynasty.Dynasty.MODID, value = Dist.CLIENT)
public class DynastyClientForgeEvents {

    @SubscribeEvent
    public static void onScreenInit(ScreenEvent.Init.Post event) {
        if (event.getScreen() instanceof InventoryScreen) {
            event.addListener(Button.builder(Component.literal("§6✦ 王朝任务"),
                            b -> DynastyNetwork.CHANNEL.sendToServer(new QuestRequestPacket()))
                    .bounds(6, 6, 74, 18).build());
        }
    }
}
