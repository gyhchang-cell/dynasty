package artifacts.registry;

import artifacts.effect.MagnetismMobEffect;
import com.google.common.base.Supplier;
import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.effect.MobEffect;

public class ModMobEffects {

    public static final Register<MobEffect> MOB_EFFECTS = Register.create(Registries.MOB_EFFECT);

    public static final Holder<MobEffect> MAGNETISM = register("magnetism", MagnetismMobEffect::new);

    private static Holder<MobEffect> register(String name, Supplier<MobEffect> factory) {
        return MOB_EFFECTS.register(name, factory).holder();
    }
}
