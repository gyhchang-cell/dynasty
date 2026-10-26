package net.sam.simple_combat_indicators.render;

import com.mojang.blaze3d.platform.GlStateManager;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import com.mojang.math.Axis;
import net.minecraft.client.Camera;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec2;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ViewportEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.sam.simple_combat_indicators.SimpleCombatIndicators;
import org.joml.Matrix4f;
import org.joml.Quaternionf;
import org.joml.Vector3f;
import org.joml.Vector4f;

@Mod.EventBusSubscriber(modid = SimpleCombatIndicators.MOD_ID, value = Dist.CLIENT)
public class CustomHudRenderer {

    public static double currentFov = 0.0;

    public static void renderCustomHudObject(ResourceLocation texture, float x, float y, float width, float height, float rotationDeg, int r, int g, int b, int a) {

        float scale_gui = 1.0f/(float) Minecraft.getInstance().getWindow().getGuiScale(); // e.g. 2.0

        PoseStack poseStack = new PoseStack();
        float pixelScale = 3.0f;
        poseStack.pushPose();
        poseStack.scale(scale_gui, scale_gui, 1);
        poseStack.translate(x, y, 0);
        poseStack.scale(pixelScale, pixelScale, 1);
        poseStack.mulPose(Axis.ZP.rotation(rotationDeg * (float)(Math.PI/180)));
        poseStack.translate(-(width) / 2, -(height) / 2, 0);

        RenderSystem.disableCull();
        RenderSystem.enableBlend();
        RenderSystem.depthMask(true);
        RenderSystem.setShader(GameRenderer::getPositionTexShader);
        RenderSystem.blendFunc(GlStateManager.SourceFactor.SRC_ALPHA, GlStateManager.DestFactor.ONE_MINUS_SRC_ALPHA);
        RenderSystem.setShaderTexture(0, texture);
        float r_f = r/255.0f;
        float g_f = g/255.0f;
        float b_f = b/255.0f;
        float a_f = a/255.0f;

        RenderSystem.setShaderColor(r_f,g_f,b_f,a_f);

        Matrix4f matrix = poseStack.last().pose();
        Tesselator tesselator = Tesselator.getInstance();
        BufferBuilder buffer = tesselator.getBuilder();

        buffer.begin(VertexFormat.Mode.QUADS, DefaultVertexFormat.POSITION_TEX);
        buffer.vertex(matrix, 0,0, 0).uv(0, 0).endVertex();
        buffer.vertex(matrix, width,0,        0).uv(1, 0).endVertex();
        buffer.vertex(matrix, width,   height,   0).uv(1, 1).endVertex();
        buffer.vertex(matrix, 0,       height,   0).uv(0, 1).endVertex();
        tesselator.end();
        poseStack.popPose();
        RenderSystem.disableBlend();
        RenderSystem.enableCull();
        RenderSystem.setShaderColor(1.0f,1.0f,1.0f,1.0f);
    }

    public static void renderText(GuiGraphics guiGraphics, String text, float x, float y, int r, int g, int b, int a, float size, float rotationDeg){
        int color = rgba(r,g,b,a);
        Minecraft mc = Minecraft.getInstance();
        Font font = mc.font;
        double guiScale = mc.getWindow().getGuiScale();
        double scaledX = (x / guiScale);
        double scaledY = (y / guiScale);

        int textWidth = font.width(text);
        int textHeight = font.lineHeight;

        PoseStack poseStack = guiGraphics.pose();
        poseStack.pushPose();

        poseStack.translate(scaledX, scaledY, 0);
        poseStack.mulPose(Axis.ZP.rotation(rotationDeg * (float)(Math.PI/180)));
        poseStack.scale(size, size, 1.0f);
        guiGraphics.drawString(font, text, -textWidth / 2, -textHeight / 2, color, true);
        poseStack.popPose();
    }

    public static Vec2 worldToScreen(Vec3 worldPos) {
        Minecraft mc = Minecraft.getInstance();
        Camera camera = mc.gameRenderer.getMainCamera();

        // Get camera position
        Vec3 camPos = camera.getPosition();

        // Calculate relative position
        float relX = (float)(worldPos.x - camPos.x);
        float relY = (float)(worldPos.y - camPos.y);
        float relZ = (float)(worldPos.z - camPos.z);

        // Create view matrix using lookAt approach
        Matrix4f viewMatrix = new Matrix4f();

        // Get camera's forward, up, and right vectors from rotation
        Quaternionf cameraRotation = camera.rotation();
        Vector3f forward = new Vector3f(0, 0, 1);
        Vector3f up = new Vector3f(0, 1, 0);
        Vector3f right = new Vector3f(1, 0, 0);

        // Apply camera rotation to get actual directions
        cameraRotation.transform(forward);
        cameraRotation.transform(up);
        cameraRotation.transform(right);

        // Create view matrix manually
        viewMatrix.setLookAt(
                0, 0, 0,
                forward.x, forward.y, forward.z,
                up.x, up.y, up.z
        );

        // Get projection matrix
        Matrix4f projectionMatrix = new Matrix4f();


        float aspectRatio = (float) mc.getWindow().getScreenWidth() / (float) mc.getWindow().getScreenHeight();
        float nearPlane = 0.05f;
        float farPlane = mc.gameRenderer.getRenderDistance() * 16.0f;
        projectionMatrix.perspective((float) Math.toRadians(currentFov), aspectRatio, nearPlane, farPlane);

        // Transform the relative position
        Vector4f pos = new Vector4f(relX, relY, relZ, 1.0f);

        // Apply view matrix
        pos.mul(viewMatrix);

        // Apply projection matrix
        pos.mul(projectionMatrix);

        // Check if behind camera
        if (pos.w() <= 0.0f) {
            return null;
        }

        // Perspective divide
        pos.div(pos.w());

        // Convert normalized device coordinates to screen coordinates
        int screenWidth = mc.getWindow().getScreenWidth();
        int screenHeight = mc.getWindow().getScreenHeight();

        float screenX = (pos.x() * 0.5f + 0.5f) * screenWidth;
        float screenY = (1.0f - (pos.y() * 0.5f + 0.5f)) * screenHeight;

        return new Vec2(screenX, screenY);
    }

    @SubscribeEvent
    public static void updateFov(ViewportEvent.ComputeFov event){
        if (!event.usedConfiguredFov()) return;
        currentFov = event.getFOV();
    }

    public static int rgba(int r, int g, int b, int a) {
        return ((a) << 24) |
                ((r) << 16) |
                ((g) << 8)  |
                ((b));
    }


}
