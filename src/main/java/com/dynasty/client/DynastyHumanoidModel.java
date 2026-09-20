package com.dynasty.client;

import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.world.entity.Mob;

/**
 * 王朝人形模型（兵马俑/士兵/Boss 共用）。
 * Shared humanoid model for Dynasty mobs.
 */
@SuppressWarnings("null")
public class DynastyHumanoidModel<T extends Mob> extends HumanoidModel<T> {

    public DynastyHumanoidModel(ModelPart root) {
        super(root);
    }

    public static LayerDefinition createBodyLayer(float inflation) {
        return LayerDefinition.create(
                HumanoidModel.createMesh(new CubeDeformation(inflation), 0.0F), 64, 64);
    }

    public static LayerDefinition createBodyLayer() {
        return createBodyLayer(0.0F);
    }

    /** Extra articulated silhouettes; unchanged vanilla UVs and equipment animation. */
    public static LayerDefinition decoratedLayer(int style) {
        var mesh=HumanoidModel.createMesh(new CubeDeformation(style<=2?.18F:.04F),0);
        var root=mesh.getRoot();
        for(int side:new int[]{-1,1}) {
            var arm=root.getChild(side<0?"right_arm":"left_arm");
            int plates=style<=2?3:2;
            for(int i=0;i<plates;i++)
                arm.addOrReplaceChild("pauldron_"+i,CubeListBuilder.create().texOffs(16,16)
                    .addBox(-3,-1,-3,6,2,6,new CubeDeformation(-i*.15F)),
                    PartPose.offsetAndRotation(side*i*.4F,-1+i*1.25F,0,0,0,side*.13F));
            var head=root.getChild("head");
            if(style==1) {
                var horn=head.addOrReplaceChild("antler_"+side,CubeListBuilder.create().texOffs(20,20)
                    .addBox(-.65F,-4,-.65F,1.3F,4,1.3F),PartPose.offsetAndRotation(side*3,-7,0,-.25F,0,side*.35F));
                horn.addOrReplaceChild("tip",CubeListBuilder.create().texOffs(20,20)
                    .addBox(-.4F,-3,-.4F,.8F,3,.8F),PartPose.offsetAndRotation(0,-3.7F,0,.4F,0,-side*.25F));
                horn.addOrReplaceChild("fork",CubeListBuilder.create().texOffs(20,20)
                    .addBox(-.35F,-2.6F,-.35F,.7F,2.6F,.7F),PartPose.offsetAndRotation(0,-2,0,0,0,side*.8F));
            } else if(style==2) {
                head.addOrReplaceChild("crown_wing_"+side,CubeListBuilder.create().texOffs(20,20)
                    .addBox(-.5F,-5,-1,1,5,2),PartPose.offsetAndRotation(side*3.8F,-6,1,-.3F,0,side*.65F));
            } else if(style==3) {
                head.addOrReplaceChild("helmet_fin_"+side,CubeListBuilder.create().texOffs(20,20)
                    .addBox(-.5F,-3,-1,1,3,2),PartPose.offsetAndRotation(side*3,-7,0,0,0,side*.24F));
            }
            var body=root.getChild("body");
            body.addOrReplaceChild("robe_panel_"+side,CubeListBuilder.create().texOffs(20,20)
                .addBox(-2,0,-.35F,4,7,.7F),PartPose.offsetAndRotation(side*2.5F,9,-2.3F,-.12F,0,-side*.13F));
            if(style<=2||style==4) {
                var banner=body.addOrReplaceChild("back_banner_"+side,CubeListBuilder.create().texOffs(20,20)
                    .addBox(-1.5F,0,0,3,10,.4F),PartPose.offsetAndRotation(side*3,-1,3.2F,.22F,0,side*(style==4?.36F:.62F)));
                banner.addOrReplaceChild("tail",CubeListBuilder.create().texOffs(20,20)
                    .addBox(-1,0,0,2,7,.3F),PartPose.offsetAndRotation(0,9.6F,0,-.32F,0,-side*.22F));
            }
        }
        return LayerDefinition.create(mesh,64,64);
    }

    /** 让模型保持默认站姿 / keep the default pose */
    public static PartPose pose() {
        return PartPose.ZERO;
    }
}
