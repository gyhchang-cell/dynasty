package de.njlent.damagenumbers.client;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Camera;
import net.minecraft.client.gui.Font;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.network.chat.Style;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.world.phys.Vec3;

public final class TextParticle {
    private static final int FULL_BRIGHT = 0xF000F0;

    private String text = "";
    private Vec3 previousPos;
    private Vec3 pos;
    private Vec3 velocity;
    private int color = 0xFFFFFFFF;
    private int age;
    private final int lifetime;

    public TextParticle(Vec3 pos, Vec3 velocity, int lifetime) {
        this.previousPos = pos;
        this.pos = pos;
        this.velocity = velocity;
        this.lifetime = lifetime;
    }

    public void setText(String text) {
        this.text = text;
    }

    public void setColor(int color) {
        this.color = color;
    }

    public boolean tick() {
        previousPos = pos;
        velocity = velocity.add(0.0, -0.03, 0.0);
        pos = pos.add(velocity);
        velocity = velocity.scale(0.99);
        age++;
        return age >= lifetime;
    }

    public void remove() {
        age = lifetime;
    }

    public void render(
        Font font,
        PoseStack poseStack,
        SubmitNodeCollector submitNodeCollector,
        Camera camera,
        CameraRenderState cameraRenderState,
        float tickDelta
    ) {
        Vec3 cameraPos = camera.position();
        Vec3 renderPos = previousPos.lerp(pos, tickDelta).subtract(cameraPos);

        poseStack.pushPose();
        poseStack.translate(renderPos.x, renderPos.y, renderPos.z);
        poseStack.mulPose(cameraRenderState.orientation);
        poseStack.scale(0.025F, -0.025F, 0.025F);

        submitNodeCollector.submitText(
            poseStack,
            font.width(text) / -2.0F,
            0.0F,
            FormattedCharSequence.forward(text, Style.EMPTY),
            false,
            Font.DisplayMode.SEE_THROUGH,
            FULL_BRIGHT,
            color,
            0,
            0
        );

        poseStack.popPose();
    }
}
