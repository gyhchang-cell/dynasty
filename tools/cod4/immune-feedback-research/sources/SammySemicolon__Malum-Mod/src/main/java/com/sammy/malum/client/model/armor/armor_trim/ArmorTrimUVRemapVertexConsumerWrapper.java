package com.sammy.malum.client.model.armor.armor_trim;

import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.util.Mth;
import net.minecraft.world.item.armortrim.TrimMaterials;
import org.jetbrains.annotations.NotNull;
import team.lodestar.lodestone.systems.rendering.wrapper.LodestoneVertexConsumerWrapper;

/**
 * A {@link VertexConsumer} that allows for an offset to be applied to the UV coordinates.
 */
@SuppressWarnings("unused")
public class ArmorTrimUVRemapVertexConsumerWrapper extends LodestoneVertexConsumerWrapper {

    private final TextureAtlasSprite sprite;
    private final boolean isInner;

    public ArmorTrimUVRemapVertexConsumerWrapper(VertexConsumer buffer, TextureAtlasSprite sprite, boolean isInner) {
        super(buffer);
        this.sprite = sprite;
        this.isInner = isInner;
    }

    @Override
    public @NotNull VertexConsumer setUv(float u, float v) {

        float v0 = sprite.getV0();
        float v1 = sprite.getV1();
        float delta = (v - v0) / (v1 - v0);
        if (isInner) {
            delta -= 0.25f;
        }
        delta *= 2f;
        v = Mth.lerp(delta, v0, v1);

        return super.setUv(u, v);
    }
}