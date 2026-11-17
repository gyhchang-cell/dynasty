package toni.immersivedamageindicators.api;

import net.fabricmc.fabric.api.event.Event;
import net.fabricmc.fabric.api.event.EventFactory;
import toni.immersivedamageindicators.particle.DamageParticle;
import toni.immersivemessages.api.ImmersiveMessage;

public interface CreateDamageIndicator {
    Event<CreateDamageIndicator> EVENT = EventFactory.createArrayBacked(CreateDamageIndicator.class, (listeners) -> (particle, message) -> {
        for (CreateDamageIndicator event : listeners) {
            event.onCreateDamageIndicator(particle, message);
        }
    });

    void onCreateDamageIndicator(DamageParticle particle, ImmersiveMessage message);
}