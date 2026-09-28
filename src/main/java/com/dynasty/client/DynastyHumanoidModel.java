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
        if(style<=2) {
            // Layered breastplate and flared greaves change the body silhouette as well as the halo.
            var chest=root.getChild("body");
            chest.addOrReplaceChild("breast_keel",CubeListBuilder.create().texOffs(20,20)
                .addBox(-2.5F,0,-.5F,5,7,1),PartPose.offsetAndRotation(0,1,-2.6F,-.13F,0,0));
            for(int side:new int[]{-1,1}) {
                chest.addOrReplaceChild("waist_flare_"+side,CubeListBuilder.create().texOffs(16,16)
                    .addBox(-1.5F,0,-2.5F,3,5,5),PartPose.offsetAndRotation(side*4.3F,8,0,0,0,-side*.32F));
                var leg=root.getChild(side<0?"right_leg":"left_leg");
                leg.addOrReplaceChild("knee_guard",CubeListBuilder.create().texOffs(20,20)
                    .addBox(-2.4F,-1,-1,4.8F,4,1.5F),PartPose.offsetAndRotation(0,5,-2,.12F,0,0));
            }
        }
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
        var torso=root.getChild("body");
        // Distinct articulated silhouettes, not a uniformly inflated player skin.
        if(style==1 || style==5) {
            for(int side:new int[]{-1,1}) {
                var arm=root.getChild(side<0?"right_arm":"left_arm");
                for(int i=0;i<4;i++)arm.addOrReplaceChild("fortress_plate_"+i,
                    CubeListBuilder.create().texOffs(16,16).addBox(-3.5F,-1,-3.4F,7,2.4F,6.8F),
                    PartPose.offsetAndRotation(side*1.3F,2+i*2,0,0,0,side*.1F));
            }
            var shield=root.getChild("left_arm").addOrReplaceChild("tower_shield",
                CubeListBuilder.create().texOffs(16,16).addBox(-4,-7,-1,8,14,2),
                PartPose.offsetAndRotation(3,6,-3,0,-.28F,-.1F));
            shield.addOrReplaceChild("shield_spine",CubeListBuilder.create().texOffs(20,20)
                .addBox(-.7F,-8,-1,1.4F,16,2),PartPose.offset(0,0,-1));
        }
        if(style==2 || style==8) {
            for(int side:new int[]{-1,1}) {
                var wing=torso.addOrReplaceChild("storm_wing_"+side,CubeListBuilder.create().texOffs(20,20)
                    .addBox(-1,-1,-1,2,8,2),PartPose.offsetAndRotation(side*5,1,3,.2F,side*.3F,side*1.1F));
                for(int i=0;i<6;i++)wing.addOrReplaceChild("blade_"+i,CubeListBuilder.create().texOffs(20,20)
                    .addBox(-.7F,0,-.5F,1.4F,9-i*.8F,1),
                    PartPose.offsetAndRotation(side*i*1.5F,3+i*.7F,0,.1F,0,side*.25F));
            }
            for(int i=0;i<5;i++)torso.addOrReplaceChild("floating_blade_"+i,CubeListBuilder.create().texOffs(20,20)
                .addBox(-.65F,-5,-.65F,1.3F,10,1.3F),
                PartPose.offsetAndRotation((i-2)*5,-7-Math.abs(i-2)*2,5,0,0,(i-2)*.3F));
        }
        if(style==4 || style==6 || style==10) {
            // Wraith-like lower body: overlapping tapered robe, no walking square legs.
            root.addOrReplaceChild("right_leg",CubeListBuilder.create(),PartPose.offset(-1.9F,12,0));
            root.addOrReplaceChild("left_leg",CubeListBuilder.create(),PartPose.offset(1.9F,12,0));
            for(int i=0;i<5;i++)torso.addOrReplaceChild("spirit_robe_"+i,CubeListBuilder.create().texOffs(16,16)
                .addBox(-4+i*.5F,0,-2.5F+i*.25F,8-i,3,5-i*.5F),
                PartPose.offsetAndRotation(0,10+i*2,0,.04F*i,0,0));
            for(int side:new int[]{-1,1})torso.addOrReplaceChild("floating_mask_"+side,
                CubeListBuilder.create().texOffs(6,6).addBox(-2.5F,-3,-1,5,6,2),
                PartPose.offsetAndRotation(side*10,-4,2,0,side*.45F,side*.2F));
        }
        if(style==7 || style==9) {
            root.addOrReplaceChild("right_leg",CubeListBuilder.create(),PartPose.offset(-1.9F,12,0));
            root.addOrReplaceChild("left_leg",CubeListBuilder.create(),PartPose.offset(1.9F,12,0));
            PartDefinition segment=torso;
            for(int i=0;i<9;i++) {
                float radius=3.7F-i*.3F;
                segment=segment.addOrReplaceChild("tidal_tail_"+i,CubeListBuilder.create().texOffs(16,16)
                    .addBox(-radius,0,-radius,radius*2,4.5F,radius*2),
                    PartPose.offsetAndRotation(0,i==0?10:4,0,i==0?.12F:.25F,i>4?.17F:0,0));
                if(i%2==0)segment.addOrReplaceChild("fin",CubeListBuilder.create().texOffs(20,20)
                    .addBox(-.4F,0,0,.8F,4,4),PartPose.offset(0,0,radius));
            }
            for(int side:new int[]{-1,1})root.getChild("head").addOrReplaceChild("crown_fin_"+side,
                CubeListBuilder.create().texOffs(20,20).addBox(-.5F,-6,-1,1,7,3),
                PartPose.offsetAndRotation(side*4,-5,0,0,0,side*.7F));
            if(style==7) {
                var head=root.getChild("head");
                head.addOrReplaceChild("dragon_muzzle",CubeListBuilder.create().texOffs(16,16)
                    .addBox(-3.2F,-2,-8,6.4F,3.5F,5),PartPose.offset(0,-1,0));
                head.addOrReplaceChild("lower_jaw",CubeListBuilder.create().texOffs(20,20)
                    .addBox(-2.8F,-.4F,-7.8F,5.6F,1,4.5F),PartPose.offsetAndRotation(0,0,0,.12F,0,0));
                for(int side:new int[]{-1,1}) {
                    head.addOrReplaceChild("brow_"+side,CubeListBuilder.create().texOffs(40,20)
                        .addBox(-1.5F,-.5F,-1,3,1,2),PartPose.offsetAndRotation(side*2.3F,-4,-4,0,0,-side*.22F));
                    var horn=head.addOrReplaceChild("royal_antler_"+side,CubeListBuilder.create().texOffs(20,20)
                        .addBox(-.5F,-7,-.5F,1,7,1),PartPose.offsetAndRotation(side*2.7F,-7,1,-.4F,0,side*.25F));
                    horn.addOrReplaceChild("fork",CubeListBuilder.create().texOffs(20,20)
                        .addBox(-.35F,-3,-.35F,.7F,3,.7F),PartPose.offsetAndRotation(0,-3,0,0,0,side*.8F));
                    head.addOrReplaceChild("whisker_"+side,CubeListBuilder.create().texOffs(20,20)
                        .addBox(0,-.2F,-.2F,6,.4F,.4F),PartPose.offsetAndRotation(side*2.7F,-1,-7,0,0,side<0?2.8F:.35F));
                }
            }
        }
        if(style==10) {
            var head=root.getChild("head");
            head.addOrReplaceChild("imperial_canopy",CubeListBuilder.create().texOffs(16,16)
                .addBox(-6,-1,-5,12,1.5F,10),PartPose.offset(0,-8,0));
            for(int i=0;i<7;i++)head.addOrReplaceChild("crown_beads_"+i,
                CubeListBuilder.create().texOffs(20,20).addBox(-.25F,0,-.25F,.5F,4+(i%2),.5F),
                PartPose.offset((i-3)*1.6F,-8,-4.8F));
            for(int side:new int[]{-1,1})for(int i=0;i<3;i++)torso.addOrReplaceChild("spirit_tablet_"+side+"_"+i,
                CubeListBuilder.create().texOffs(16,16).addBox(-1.3F,-3,-.5F,2.6F,6,1),
                PartPose.offsetAndRotation(side*(8+i*2),i*4-4,4+i,0,side*.45F,side*.2F));
        }
        return LayerDefinition.create(mesh,64,64);
    }

    @Override public void setupAnim(T entity,float limb,float amount,float age,float yaw,float pitch) {
        super.setupAnim(entity,limb,amount,age,yaw,pitch);
        for(int side:new int[]{-1,1}) {
            String wing="storm_wing_"+side;
            if(body.hasChild(wing)) body.getChild(wing).yRot=side*(.3F+(float)Math.sin(age*.07F)*.13F);
            String mask="floating_mask_"+side;
            if(body.hasChild(mask)) body.getChild(mask).y=-4+(float)Math.sin(age*.07F+side)*1.2F;
        }
        if(body.hasChild("tidal_tail_0"))body.getChild("tidal_tail_0").yRot=(float)Math.sin(age*.05F)*.15F;
        for(int i=0;i<5;i++)if(body.hasChild("floating_blade_"+i))
            body.getChild("floating_blade_"+i).y=-7-Math.abs(i-2)*2+(float)Math.sin(age*.08F+i)*.7F;
    }

    /** 让模型保持默认站姿 / keep the default pose */
    public static PartPose pose() {
        return PartPose.ZERO;
    }
}
