package toni.immersivedamageindicators.foundation;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.FormattedText;
import net.minecraft.util.CommonColors;
import net.minecraft.util.FastColor;
import toni.immersivedamageindicators.particle.DamageParticle;
import toni.immersivemessages.api.ImmersiveMessage;
import toni.lib.utils.ColorUtils;
import xyz.flirora.caxton.layout.CaxtonText;
import xyz.flirora.caxton.render.CaxtonTextRenderer;

public class CaxtonRenderer {
    public static void renderMessageCaxton(DamageParticle particle, ImmersiveMessage tooltip, GuiGraphics graphics, CaxtonTextRenderer renderer, CaxtonText text, int yOffset) {
        if (IrisCompat.areShadersEnabled()) {
            return;
        }

        float fade = FastColor.ARGB32.alpha(tooltip.animation.getColor()) / 255f;
        int alpha = (int) Math.max(0, Math.min(particle.opacity, fade * particle.opacity));
        var color = tooltip.animation.getColor();

        renderer.draw(text, 0, yOffset,
            ColorUtils.color(alpha, ColorUtils.red(color), ColorUtils.green(color), ColorUtils.blue(color)),
            false,
            graphics.pose().last().pose(),
            graphics.bufferSource(),
            false,
            0,
            255,
            0,
            1000f);

        graphics.pose().translate(0.5f, 0.5f, +0.03);

        renderer.draw(text, 0, yOffset,
            FastColor.ARGB32.color(alpha, 40, 40, 40),
            false,
            graphics.pose().last().pose(),
            graphics.bufferSource(),
            false,
            0,
            50,
            0,
            1000f);

        //graphics.fill(0, 0, 10, 10, CommonColors.RED);

        graphics.flush();
    }
}
