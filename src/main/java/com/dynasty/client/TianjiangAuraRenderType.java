package com.dynasty.client;

import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.VertexFormat;
import net.minecraft.client.renderer.RenderType;

/** Luminous, depth-tested ribbons. Color-only writes never turn the aura into an opaque wall. */
final class TianjiangAuraRenderType extends RenderType {
    static final RenderType VEIL=make(false), LIGHT=make(true);
    private static RenderType make(boolean additive){
        return create(additive?"dynasty_tianjiang_light":"dynasty_tianjiang_veil",
                DefaultVertexFormat.POSITION_COLOR_TEX,VertexFormat.Mode.QUADS,65536,false,true,
                CompositeState.builder().setShaderState(POSITION_COLOR_TEX_SHADER)
                        .setTextureState(new TextureStateShard(TianjiangAura.STREAM,false,false))
                        .setTransparencyState(additive?LIGHTNING_TRANSPARENCY:TRANSLUCENT_TRANSPARENCY)
                        .setCullState(NO_CULL).setDepthTestState(LEQUAL_DEPTH_TEST)
                        .setWriteMaskState(COLOR_WRITE).createCompositeState(false));
    }
    private TianjiangAuraRenderType(){super("unused",DefaultVertexFormat.POSITION_COLOR_TEX,VertexFormat.Mode.QUADS,256,false,true,()->{},()->{});}
}
