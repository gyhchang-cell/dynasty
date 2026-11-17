package com.dynasty.client;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.renderer.RenderType;
/** Keep the block atlas's mipmap contract while drawing a color-only translucent ghost. */
final class ScenicMirageRenderType extends RenderType {
    static final RenderType TYPE=create("dynasty_mirage_street",DefaultVertexFormat.NEW_ENTITY,VertexFormat.Mode.QUADS,1048576,false,true,
        CompositeState.builder().setShaderState(RENDERTYPE_ENTITY_TRANSLUCENT_SHADER).setTextureState(BLOCK_SHEET_MIPPED)
            .setTransparencyState(TRANSLUCENT_TRANSPARENCY).setCullState(NO_CULL).setLightmapState(LIGHTMAP).setOverlayState(OVERLAY)
            .setDepthTestState(LEQUAL_DEPTH_TEST).setWriteMaskState(COLOR_WRITE).createCompositeState(false));
    private ScenicMirageRenderType(){super("unused",DefaultVertexFormat.NEW_ENTITY,VertexFormat.Mode.QUADS,256,false,true,()->{},()->{});}
}
