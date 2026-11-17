package com.sammy.malum.client.model.armor;

import com.sammy.malum.client.model.armor.armor_trim.ArmorTrimUVRemapBufferSourceWrapper;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import team.lodestar.lodestone.modules.rendering.model.entity.armor.LodestoneArmorModel;

public class MalumArmorModel extends LodestoneArmorModel {
    public MalumArmorModel(ModelPart root) {
        super(root);
    }

    public MultiBufferSource updateTrimRendering(MultiBufferSource original, TextureAtlasSprite sprite, boolean isInner) {
        return new ArmorTrimUVRemapBufferSourceWrapper(original, sprite, isInner);
    }
}
