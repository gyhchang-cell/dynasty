package artifacts.registry;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.gameevent.GameEvent;

import java.util.HashMap;
import java.util.Map;

public class ModGameEvents {

    public static final Map<RegistryHolder<GameEvent, GameEvent>, Integer> VIBRATION_FREQUENCIES = new HashMap<>();

    public static final Register<GameEvent> GAME_EVENTS = Register.create(Registries.GAME_EVENT);

    public static final RegistryHolder<GameEvent, GameEvent> FART = register("fart", 3);

    private static RegistryHolder<GameEvent, GameEvent> register(String id, int frequency) {
        RegistryHolder<GameEvent, GameEvent> holder = GAME_EVENTS.register(id, () -> new GameEvent(16));
        VIBRATION_FREQUENCIES.put(holder, frequency);
        return holder;
    }
}
