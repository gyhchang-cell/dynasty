package de.njlent.damagenumbers.modules.combat;

import de.njlent.damagenumbers.client.TextParticle;
import meteordevelopment.meteorclient.events.world.TickEvent;
import meteordevelopment.meteorclient.settings.BoolSetting;
import meteordevelopment.meteorclient.settings.ColorSetting;
import meteordevelopment.meteorclient.settings.IntSetting;
import meteordevelopment.meteorclient.settings.Setting;
import meteordevelopment.meteorclient.settings.SettingGroup;
import meteordevelopment.meteorclient.systems.modules.Categories;
import meteordevelopment.meteorclient.systems.modules.Module;
import meteordevelopment.meteorclient.utils.render.color.Color;
import meteordevelopment.meteorclient.utils.render.color.SettingColor;
import meteordevelopment.orbit.EventHandler;
import net.fabricmc.fabric.api.client.rendering.v1.level.LevelRenderContext;
import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayDeque;
import java.util.Deque;

public class DamageNumbersModule extends Module {
    private static final int DEFAULT_COLOR = 0xFFFFFFFF;
    private static DamageNumbersModule instance;

    private final SettingGroup sgGeneral = settings.getDefaultGroup();
    private final SettingGroup sgColors = settings.createGroup("Colors");

    private final Setting<Boolean> showPlayerDamage = sgGeneral.add(new BoolSetting.Builder()
        .name("show-player-damage")
        .description("Shows damage numbers when you take damage.")
        .defaultValue(false)
        .build()
    );

    private final Setting<Boolean> textFeedback = sgGeneral.add(new BoolSetting.Builder()
        .name("text-feedback")
        .description("Prints damage numbers to Meteor chat feedback.")
        .defaultValue(false)
        .build()
    );

    private final Setting<Integer> displayTicks = sgGeneral.add(new IntSetting.Builder()
        .name("display-ticks")
        .description("How long damage numbers stay visible, in ticks.")
        .defaultValue(40)
        .range(5, 200)
        .sliderRange(5, 200)
        .build()
    );

    private final Setting<Boolean> customColors = sgColors.add(new BoolSetting.Builder()
        .name("custom-colors")
        .description("Uses the configured damage number colors.")
        .defaultValue(true)
        .build()
    );

    private final Setting<SettingColor> smallColor = sgColors.add(new ColorSetting.Builder()
        .name("small-color")
        .description("Color for damage below 2.")
        .defaultValue(new SettingColor(255, 170, 0, 255))
        .build()
    );

    private final Setting<SettingColor> mediumColor = sgColors.add(new ColorSetting.Builder()
        .name("medium-color")
        .description("Color for damage around 8.")
        .defaultValue(new SettingColor(255, 0, 0, 255))
        .build()
    );

    private final Setting<SettingColor> largeColor = sgColors.add(new ColorSetting.Builder()
        .name("large-color")
        .description("Color for damage around 16.")
        .defaultValue(new SettingColor(170, 0, 0, 255))
        .build()
    );

    private final Setting<SettingColor> criticalColor = sgColors.add(new ColorSetting.Builder()
        .name("critical-color")
        .description("Color for damage above 15.")
        .defaultValue(new SettingColor(255, 64, 255, 255))
        .build()
    );

    private final Deque<TextParticle> particles = new ArrayDeque<>();

    public DamageNumbersModule() {
        super(Categories.Combat, "damage-numbers", "Shows floating damage numbers when entities take damage.");
        instance = this;
    }

    @Override
    public void onDeactivate() {
        particles.forEach(TextParticle::remove);
        particles.clear();
    }

    @EventHandler
    private void onTick(TickEvent.Pre event) {
        particles.removeIf(TextParticle::tick);
    }

    public static void onEntityHealthChange(LivingEntity entity, float oldHealth, float newHealth) {
        if (instance != null) instance.handleEntityHealthChange(entity, oldHealth, newHealth);
    }

    public static void renderParticles(LevelRenderContext context) {
        if (instance != null) instance.render(context);
    }

    private void handleEntityHealthChange(LivingEntity entity, float oldHealth, float newHealth) {
        if (!isActive()) return;

        float damage = oldHealth - newHealth;
        if (damage <= 0.0F) return;

        Minecraft client = Minecraft.getInstance();
        if (entity == client.player && !showPlayerDamage.get()) return;

        if (client.level == null || client.level != entity.level()) return;
        if (client.player == null) return;
        if (entity.distanceToSqr(client.player) > 2304.0) return;

        int particleLimit = switch (client.options.particles().get()) {
            case ALL -> 256;
            case DECREASED -> 64;
            case MINIMAL -> 16;
        };
        while (particles.size() >= particleLimit) {
            TextParticle particle = particles.poll();
            if (particle != null) particle.remove();
        }

        Vec3 particlePos = entity.position().add(0.0, entity.getBbHeight() + 0.25, 0.0);
        Vec3 cameraPos = client.gameRenderer.mainCamera().position();
        Vec3 cameraDirection = cameraPos.subtract(entity.position()).normalize();
        Vec3 particleVelocity = entity.getDeltaMovement()
            .scale(0.1)
            .add(cameraDirection.x * 0.025, 0.08, cameraDirection.z * 0.025);

        String text = formatDamage(damage);
        TextParticle particle = new TextParticle(particlePos, particleVelocity, displayTicks.get());
        particle.setText(text);
        particle.setColor(getColor(damage));
        particles.add(particle);

        if (textFeedback.get()) {
            info("%s took %s damage.", entity.getName().getString(), text);
        }
    }

    private void render(LevelRenderContext context) {
        if (!isActive()) return;

        Minecraft client = Minecraft.getInstance();
        float tickDelta = client.getDeltaTracker().getGameTimeDeltaPartialTick(false);
        particles.forEach(particle -> particle.render(
            client.font,
            context.poseStack(),
            context.submitNodeCollector(),
            context.gameRenderer().mainCamera(),
            context.levelState().cameraRenderState,
            tickDelta
        ));
    }

    private String formatDamage(float damage) {
        String text = String.format("%.1f", damage);
        return text.endsWith(".0") ? text.substring(0, text.length() - 2) : text;
    }

    private int getColor(float damage) {
        if (!customColors.get()) return DEFAULT_COLOR;

        if (damage > 15.0F) {
            return criticalColor.get().getPacked();
        } else if (damage >= 8.0F) {
            return lerp(mediumColor.get(), largeColor.get(), (damage - 8.0F) / 8.0F).getPacked();
        } else if (damage >= 2.0F) {
            return lerp(smallColor.get(), mediumColor.get(), (damage - 2.0F) / 6.0F).getPacked();
        }
        return smallColor.get().getPacked();
    }

    private Color lerp(SettingColor from, SettingColor to, float delta) {
        return new Color(
            from.r + Math.round((to.r - from.r) * delta),
            from.g + Math.round((to.g - from.g) * delta),
            from.b + Math.round((to.b - from.b) * delta),
            from.a + Math.round((to.a - from.a) * delta)
        );
    }
}
