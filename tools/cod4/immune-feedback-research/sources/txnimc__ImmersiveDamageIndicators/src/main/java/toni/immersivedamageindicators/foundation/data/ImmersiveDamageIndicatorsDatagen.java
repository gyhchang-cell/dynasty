package toni.immersivedamageindicators.foundation.data;

#if FABRIC
import net.fabricmc.fabric.api.datagen.v1.DataGeneratorEntrypoint;
import net.fabricmc.fabric.api.datagen.v1.FabricDataGenerator;
import toni.immersivedamageindicators.ImmersiveDamageIndicators;

public class ImmersiveDamageIndicatorsDatagen  implements DataGeneratorEntrypoint {

    @Override
    public String getEffectiveModId() {
        return ImmersiveDamageIndicators.ID;
    }

    @Override
    public void onInitializeDataGenerator(FabricDataGenerator fabricDataGenerator) {
        var pack = fabricDataGenerator.createPack();
        pack.addProvider(ConfigLangDatagen::new);
    }
}
#endif