package com.uavwaffle.creaturesofpetrichor.entity.client.model;

import com.uavwaffle.creaturesofpetrichor.CreaturesOfPetrichor;
import com.uavwaffle.creaturesofpetrichor.entity.custom.DirewolfEntity;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import software.bernie.geckolib.constant.DataTickets;
import software.bernie.geckolib.core.animatable.model.CoreGeoBone;
import software.bernie.geckolib.core.animation.AnimationState;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.model.data.EntityModelData;

public class DirewolfModel extends GeoModel<DirewolfEntity> {
    private final ResourceLocation model = new ResourceLocation(CreaturesOfPetrichor.MODID, "geo/direwolf.geo.json");
    private final ResourceLocation texture = new ResourceLocation(CreaturesOfPetrichor.MODID, "textures/entity/direwolf.png");
    private final ResourceLocation animations = new ResourceLocation(CreaturesOfPetrichor.MODID, "animations/direwolf.animation.json");





    @Override
    public ResourceLocation getModelResource(DirewolfEntity object) {
        return this.model;
    }

    @Override
    public ResourceLocation getTextureResource(DirewolfEntity object) {
        return this.texture;
    }

    @Override
    public ResourceLocation getAnimationResource(DirewolfEntity object) {
        return this.animations;
    }

    @Override
    public void setCustomAnimations(DirewolfEntity animatable, long instanceId, AnimationState<DirewolfEntity> animationState) {

        CoreGeoBone head = getAnimationProcessor().getBone("Head");

        if (head != null) {
            EntityModelData entityData = animationState.getData(DataTickets.ENTITY_MODEL_DATA);

            head.setRotX(entityData.headPitch() * Mth.DEG_TO_RAD);
            head.setRotY(entityData.netHeadYaw() * Mth.DEG_TO_RAD);
        }
    }
}