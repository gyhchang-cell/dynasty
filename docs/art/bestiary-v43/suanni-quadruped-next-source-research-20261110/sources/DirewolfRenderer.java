package com.uavwaffle.creaturesofpetrichor.entity.client.renderer;

import com.uavwaffle.creaturesofpetrichor.entity.client.model.DirewolfModel;
import com.uavwaffle.creaturesofpetrichor.entity.custom.DirewolfEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.renderer.layer.AutoGlowingGeoLayer;

public class DirewolfRenderer extends GeoEntityRenderer<DirewolfEntity> {
    public DirewolfRenderer(EntityRendererProvider.Context context) {
        super(context, new DirewolfModel());
        this.addRenderLayer(new AutoGlowingGeoLayer<>(this));
    }
}
