package toni.immersivedamageindicators.foundation.config;

import net.minecraft.core.Vec3i;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.StringUtil;
import toni.lib.config.ConfigBase;
import toni.lib.utils.ColorUtils;
import toni.lib.utils.PlatformUtils;
import toni.lib.utils.VersionUtils;

#if mc >= 211
import net.neoforged.neoforge.common.ModConfigSpec.*;
#else
import net.minecraftforge.common.ForgeConfigSpec.*;
#endif

public class CClient extends ConfigBase {

    public final CValue<String, ConfigValue<String>> customFont = new CValue<>("Custom Font", builder -> builder.define("Custom Font", "anton"), "Custom Immersive Messages font to use, or blank if null.");
    public final ConfigInt textColor = i(ColorUtils.color(255, 255, 255, 255), "Text Color", "ARGB, Default color for indicators - https://argb-int-calculator.netlify.app/");
    public final ConfigInt hurtColor = i(ColorUtils.color(255, 255, 10, 10), "Hurt Color", "RGB, Default color for hurt effects - https://argb-int-calculator.netlify.app/");
    public final ConfigInt alpha = i(255, "Alpha", "0-255 Alpha value");

    public final ConfigBool showExclamationPoint = b(true, "Show Exclamation Point", "If true, critical hits will add exclamation points.");
    public final ConfigBool doSizeEffects = b(true, "Do Size Effects", "If true, hits will change size based on how strong they are.");
    public final ConfigBool doColorEffects = b(true, "Do Color Effects", "If true, hits will turn red based on how strong they are.");
    public final ConfigBool doShakeEffects = b(true, "Do Shake Effects", "If true, hits will shake based on how strong they are.");

    public ResourceLocation getFont() {
        return (StringUtil.isNullOrEmpty(customFont.get()) || !PlatformUtils.isModLoaded("caxton")) ? VersionUtils.resource("minecraft", "font/default") : VersionUtils.resource("immersivemessages", this.customFont.get());
    }

    @Override
    public String getName() {
        return "client";
    }
}
