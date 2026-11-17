package com.sammy.malum.client.model.armor.armor_trim;

import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderStateShard;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import team.lodestar.lodestone.systems.rendering.rendeertype.RenderTypeToken;

public class ArmorTrimUVRemapBufferSourceWrapper implements MultiBufferSource {

    protected final MultiBufferSource original;
    private final TextureAtlasSprite sprite;
    protected final boolean isInner;

    public ArmorTrimUVRemapBufferSourceWrapper(MultiBufferSource original, TextureAtlasSprite sprite, boolean isInner) {
        this.original = original;
        this.isInner = isInner;
        this.sprite = sprite;
    }

    @Override
    public VertexConsumer getBuffer(RenderType renderType) {
        return new ArmorTrimUVRemapVertexConsumerWrapper(original.getBuffer(renderType), sprite, isInner);
    }
}
