package com.dynasty.client;

import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.VertexFormat;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.Util;
import java.util.function.Function;

/** Translucent shared meshes write color only, so a ghost cannot occlude the real world. */
final class Cod3GhostRenderType extends RenderType {
    private static final Function<ResourceLocation,RenderType> TYPES=Util.memoize(texture->create("dynasty_cod3_afterimage",DefaultVertexFormat.NEW_ENTITY,VertexFormat.Mode.QUADS,256,false,true,
        CompositeState.builder().setShaderState(RENDERTYPE_ENTITY_TRANSLUCENT_SHADER)
            .setTextureState(new TextureStateShard(texture,false,false)).setTransparencyState(TRANSLUCENT_TRANSPARENCY)
            .setCullState(NO_CULL).setLightmapState(LIGHTMAP).setOverlayState(OVERLAY)
            .setDepthTestState(LEQUAL_DEPTH_TEST).setWriteMaskState(COLOR_WRITE).createCompositeState(false)));
    static RenderType of(ResourceLocation texture){return TYPES.apply(texture);}
    private Cod3GhostRenderType(){super("unused",DefaultVertexFormat.NEW_ENTITY,VertexFormat.Mode.QUADS,256,false,true,()->{},()->{});}
}
