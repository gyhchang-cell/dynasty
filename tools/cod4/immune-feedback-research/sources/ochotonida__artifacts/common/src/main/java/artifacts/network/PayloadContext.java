package artifacts.network;

import net.minecraft.world.entity.player.Player;
import org.jetbrains.annotations.Nullable;

import java.util.function.Consumer;

public class PayloadContext {

    private final @Nullable Player player;
    private final Consumer<Runnable> workQueue;

    private PayloadContext(@Nullable Player player, Consumer<Runnable> workQueue) {
        this.player = player;
        this.workQueue = workQueue;
    }

    public static PayloadContext of(Consumer<Runnable> workQueue) {
        return new PayloadContext(null, workQueue);
    }

    public static PayloadContext of(Player player, Consumer<Runnable> workQueue) {
        return new PayloadContext(player, workQueue);
    }

    public Player player() {
        if (player == null) {
            throw new UnsupportedOperationException("No player is available during the configuration phase");
        }
        return player;
    }

    public void queue(Runnable runnable) {
        workQueue.accept(runnable);
    }
}
