package com.dynasty.client;

import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.renderer.ShaderInstance;
import org.lwjgl.opengl.GL11;
import org.lwjgl.opengl.GL13;
import org.lwjgl.opengl.GL14;
import org.lwjgl.opengl.GL20;

/** Restore the caller's actual GL state, including non-default blend functions used by other mods. */
final class ImperialRenderState implements AutoCloseable {
    private final boolean blend=GL11.glIsEnabled(GL11.GL_BLEND),depth=GL11.glIsEnabled(GL11.GL_DEPTH_TEST),
            cull=GL11.glIsEnabled(GL11.GL_CULL_FACE),depthMask=GL11.glGetBoolean(GL11.GL_DEPTH_WRITEMASK);
    private final int srcRgb=GL11.glGetInteger(GL14.GL_BLEND_SRC_RGB),dstRgb=GL11.glGetInteger(GL14.GL_BLEND_DST_RGB),
            srcAlpha=GL11.glGetInteger(GL14.GL_BLEND_SRC_ALPHA),dstAlpha=GL11.glGetInteger(GL14.GL_BLEND_DST_ALPHA);
    private final int equationRgb=GL11.glGetInteger(GL20.GL_BLEND_EQUATION_RGB),
            equationAlpha=GL11.glGetInteger(GL20.GL_BLEND_EQUATION_ALPHA);
    private final ShaderInstance shader=RenderSystem.getShader();
    private final int texture0=RenderSystem.getShaderTexture(0);
    private final int activeTexture=GL11.glGetInteger(GL13.GL_ACTIVE_TEXTURE);
    private final int boundTexture0;
    ImperialRenderState() {
        // Query another unit without changing Minecraft's cached active-unit state.
        GL13.glActiveTexture(GL13.GL_TEXTURE0);
        boundTexture0=GL11.glGetInteger(GL11.GL_TEXTURE_BINDING_2D);
        GL13.glActiveTexture(activeTexture);
    }
    @Override public void close() {
        RenderSystem.depthMask(depthMask);
        if(depth)RenderSystem.enableDepthTest();else RenderSystem.disableDepthTest();
        if(cull)RenderSystem.enableCull();else RenderSystem.disableCull();
        RenderSystem.blendFuncSeparate(srcRgb,dstRgb,srcAlpha,dstAlpha);
        GL20.glBlendEquationSeparate(equationRgb,equationAlpha);
        if(blend)RenderSystem.enableBlend();else RenderSystem.disableBlend();
        RenderSystem.setShader(()->shader);
        RenderSystem.setShaderTexture(0,texture0);
        RenderSystem.activeTexture(GL13.GL_TEXTURE0);
        RenderSystem.bindTexture(boundTexture0);
        RenderSystem.activeTexture(activeTexture);
    }
}
