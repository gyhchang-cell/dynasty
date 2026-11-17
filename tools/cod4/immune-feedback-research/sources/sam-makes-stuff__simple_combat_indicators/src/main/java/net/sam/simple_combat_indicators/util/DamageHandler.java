package net.sam.simple_combat_indicators.util;

import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.sam.simple_combat_indicators.networking.ModPackets;
import net.sam.simple_combat_indicators.networking.packets.S2CAttackedPacket;

public class DamageHandler {
    @SubscribeEvent
    public void onEntityHurt(LivingDamageEvent event) {
        if (event.getEntity().level().isClientSide) return;

        if(event.getSource().getEntity() == null){return;}
//         Send packet to client
        ModPackets.sendToTracking(event.getEntity(), new S2CAttackedPacket(
                event.getSource().getEntity().getId(), event.getEntity().getId(), event.getAmount()
        ));
    }
}
