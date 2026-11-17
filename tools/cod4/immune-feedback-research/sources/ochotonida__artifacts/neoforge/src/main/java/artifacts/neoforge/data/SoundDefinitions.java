package artifacts.neoforge.data;

import artifacts.Artifacts;
import artifacts.registry.ModSoundEvents;
import net.minecraft.data.PackOutput;
import net.minecraft.resources.Identifier;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.neoforged.neoforge.common.data.SoundDefinition;
import net.neoforged.neoforge.common.data.SoundDefinitionsProvider;

public class SoundDefinitions extends SoundDefinitionsProvider {

    public SoundDefinitions(PackOutput output) {
        super(output, Artifacts.MOD_ID);
    }

    @Override
    public void registerSounds() {
        addSubtitled(ModSoundEvents.MIMIC_OPEN.value()).with(sound(SoundEvents.CHEST_OPEN));
        addSubtitled(ModSoundEvents.MIMIC_CLOSE.value()).with(sound(SoundEvents.CHEST_CLOSE));
        addSubtitled(ModSoundEvents.MIMIC_HURT.value()).with(sounds("mimic/hurt", 3));
        addSubtitled(ModSoundEvents.MIMIC_DEATH.value()).with(sounds("mimic/death", 2));

        add(ModSoundEvents.WATER_STEP.value())
                .with(sound(SoundEvents.COD_FLOP))
                .subtitle("subtitles.block.generic.footsteps");

        addSubtitled(ModSoundEvents.FART.value()).with(sounds("fart", 2));

        add(ModSoundEvents.POP.value()).with(sound(Identifier.withDefaultNamespace("random/pop")).pitch(0.75).volume(0.5));

    }

    protected static SoundDefinition.Sound sound(SoundEvent soundEvent) {
        return sound(soundEvent.location(), SoundDefinition.SoundType.EVENT);
    }

    protected static SoundDefinition.Sound sound(String path) {
        return sound(Artifacts.id(path));
    }

    protected static SoundDefinition.Sound[] sounds(String path, int count) {
        SoundDefinition.Sound[] result = new SoundDefinition.Sound[count];
        for (int i = 0; i < count; i++) {
            result[i] = sound(path + (i + 1));
        }
        return result;
    }

    private SoundDefinition add(SoundEvent soundEvent) {
        SoundDefinition result = definition();
        add(soundEvent, result);
        return result;
    }

    private SoundDefinition addSubtitled(SoundEvent soundEvent) {
        return add(soundEvent).subtitle("%s.subtitles.%s".formatted(Artifacts.MOD_ID, soundEvent.location().getPath()));
    }
}
