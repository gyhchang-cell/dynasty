package artifacts.neoforge.platform;

import artifacts.component.SwimData;
import artifacts.neoforge.registry.ModAttachmentTypes;
import artifacts.neoforge.registry.NeoForgeRegister;
import artifacts.platform.PlatformHelper;
import artifacts.registry.Register;
import net.minecraft.core.Holder;
import net.minecraft.core.Registry;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.item.ItemStack;
import net.neoforged.fml.loading.FMLLoader;
import net.neoforged.fml.loading.FMLPaths;
import net.neoforged.neoforge.common.ItemAbilities;
import net.neoforged.neoforge.common.NeoForgeMod;
import org.jetbrains.annotations.Nullable;

import java.nio.file.Path;

public class NeoForgePlatformHelper implements PlatformHelper {

    @Nullable
    @Override
    public SwimData getSwimData(LivingEntity entity) {
        return entity.getData(ModAttachmentTypes.SWIM_DATA);
    }

    @Override
    public Holder<Attribute> getSwimSpeedAttribute() {
        return NeoForgeMod.SWIM_SPEED;
    }

    @Override
    public boolean isFishingRod(ItemStack stack) {
        return stack.canPerformAction(ItemAbilities.FISHING_ROD_CAST);
    }

    @Override
    public boolean isDedicatedServer() {
        return FMLLoader.getCurrent().getDist().isDedicatedServer();
    }

    @Override
    public Path getConfigDir() {
        return FMLPaths.CONFIGDIR.get();
    }

    @Override
    public <R> Register<R> createRegister(ResourceKey<Registry<R>> registry) {
        return new NeoForgeRegister<>(registry);
    }
}
