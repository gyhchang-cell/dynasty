package com.dynasty.client;

import com.dynasty.Dynasty;
import com.dynasty.cod3.BowDrawProgress;
import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.Component;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderGuiEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Small local aim hint, driven by the exact native bow release threshold. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID,value=Dist.CLIENT)
public final class BowChargeOverlay {
    @SubscribeEvent public static void render(RenderGuiEvent.Post event) {
        var mc=Minecraft.getInstance();
        if(mc.level==null || mc.screen!=null || mc.options.hideGui || mc.getCameraEntity()!=mc.player) return;
        var draw=BowDrawProgress.read(mc.player);if(draw==null) return;
        int x=event.getWindow().getGuiScaledWidth()/2, y=event.getWindow().getGuiScaledHeight()/2+20;
        var graphics=event.getGuiGraphics();
        graphics.fill(x-16,y-1,x+16,y+3,0xA0000000);
        graphics.fill(x-15,y,x-15+Math.round(30*draw.fraction()),y+2,draw.full()?0xFFEBC370:0xFF94B9CE);
        if(draw.full()) {
            var label=Component.translatable("hud.dynasty.bow.full_draw");
            graphics.drawString(mc.font,label,x-mc.font.width(label)/2,y+5,0xFFEBC370,true);
        }
    }
    private BowChargeOverlay() {}
}
