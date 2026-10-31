package artifacts;

import artifacts.platform.PlatformServices;
import org.objectweb.asm.tree.ClassNode;
import org.spongepowered.asm.mixin.extensibility.IMixinConfigPlugin;
import org.spongepowered.asm.mixin.extensibility.IMixinInfo;

import java.util.List;
import java.util.Set;

public class ArtifactsMixinPlugin implements IMixinConfigPlugin {

    // Base packages for mixins as defined in mixins.artifacts(.fabric/.neoforge).json
    private static final List<String> BASE_PACKAGES = List.of(
            "artifacts.mixin",
            "artifacts.fabric.mixin",
            "artifacts.neoforge.mixin"
    );

    @Override
    public void onLoad(String mixinPackage) {

    }

    @Override
    public String getRefMapperConfig() {
        return null;
    }

    @Override
    public boolean shouldApplyMixin(String targetClassName, String mixinClassName) {
        for (String basePackage : BASE_PACKAGES) {
            String compatPrefix = basePackage + ".compat.";
            if (mixinClassName.startsWith(compatPrefix)) {
                String modid = mixinClassName.substring(compatPrefix.length()).split("\\.")[0];
                return PlatformServices.getModList().isModLoaded(modid);
            }
        }

        return true;
    }

    @Override
    public void acceptTargets(Set<String> myTargets, Set<String> otherTargets) {

    }

    @Override
    public List<String> getMixins() {
        return null;
    }

    @Override
    public void preApply(String targetClassName, ClassNode targetClass, String mixinClassName, IMixinInfo mixinInfo) {

    }

    @Override
    public void postApply(String targetClassName, ClassNode targetClass, String mixinClassName, IMixinInfo mixinInfo) {

    }
}
