package com.sammy.malum.client.renderer.block.redstone;

import com.sammy.malum.MalumMod;
import com.sammy.malum.common.block.curiosities.artifice.waveform.wavemaker.WaveMakerBlockEntity;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import team.lodestar.lodestone.modules.core.easing.Easing;


public class WaveMakerRenderer extends SpiritDiodeRenderer<WaveMakerBlockEntity> {

    public WaveMakerRenderer(BlockEntityRendererProvider.Context context) {
        super(context, MalumMod.malumPath("textures/block/waveform_artifice/wavemaker_overlay.png"), "malum.waveform_artifice.wavemaker");
    }

    @Override
    public float getGlowDelta(WaveMakerBlockEntity blockEntityIn, float delta) {
        if (blockEntityIn.cachedInputSignal != 0) {
            return Easing.EXPO_OUT.ease(delta);
        }
        return Easing.EXPO_IN.ease(delta);
    }
}
