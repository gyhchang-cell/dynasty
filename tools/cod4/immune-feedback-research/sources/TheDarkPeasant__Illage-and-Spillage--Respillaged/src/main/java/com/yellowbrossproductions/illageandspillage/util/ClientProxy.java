package com.yellowbrossproductions.illageandspillage.util;

import com.yellowbrossproductions.illageandspillage.events.ClientEventHandler;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.eventbus.api.IEventBus;

@OnlyIn(Dist.CLIENT)
public class ClientProxy extends ServerProxy {
    public ClientProxy() {
    }

    public void init(IEventBus modbus) {
        super.init(modbus);
        MinecraftForge.EVENT_BUS.register(ClientEventHandler.INSTANCE);
    }
}
