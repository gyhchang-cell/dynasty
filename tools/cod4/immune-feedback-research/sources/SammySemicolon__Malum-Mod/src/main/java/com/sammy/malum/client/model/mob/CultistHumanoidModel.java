package com.sammy.malum.client.model.mob;

import com.sammy.malum.common.entity.mob.cultist.CultistMonster;
import net.minecraft.client.model.geom.ModelPart;
import org.jetbrains.annotations.NotNull;

public abstract class CultistHumanoidModel<T extends CultistMonster> extends HierarchicalHumanoidModel<T> {

    public final ModelPart crown;

    public CultistHumanoidModel(ModelPart modelDefinition) {
        super(modelDefinition);
        this.crown = head.getChild("crown");
    }

    @Override
    public final void setupAnim(@NotNull T entity, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch) {
        var utils = MalumAnimationUtils.create(this, entity, limbSwing, limbSwingAmount);
        utils.reset();
        setupAnim(entity, utils, limbSwing, limbSwingAmount, ageInTicks, netHeadYaw, headPitch);
        if (riding) {
            utils.applyRidingRotations(this);
        }
        utils.applyGenericArmAnimations(ageInTicks);
    }

    public abstract void setupAnim(T cultist, MalumAnimationUtils<T> utils, float limbSwing, float limbSwingAmount, float ageInTicks, float netHeadYaw, float headPitch);
}