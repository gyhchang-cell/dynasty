package net.sam.simple_combat_indicators.init;

import net.minecraftforge.eventbus.api.IEventBus;
import net.sam.simple_combat_indicators.util.ModParticles;

public class Init {

    public static void registerAll(IEventBus bus){

        ModParticles.PARTICLES.register(bus);

    }

}
