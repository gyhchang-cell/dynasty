package com.dynasty.client;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.util.Mth;
import com.dynasty.entity.DynastyBosses;
import java.util.*;
/** Original quadruped imperial dragon; nine visual tail joints, no extra server mobs. */
public final class DragonEmperorModel extends EntityModel<DynastyBosses.DragonEmperor> {
    private final ModelPart root,neck,head,jaw;
    private final List<ModelPart> legs=new ArrayList<>(),tails=new ArrayList<>();
    public DragonEmperorModel() {
        var mesh=new MeshDefinition();var r=mesh.getRoot();
        var body=r.addOrReplaceChild("chest",CubeListBuilder.create().texOffs(0,0).addBox(-13,-10,-16,26,20,32),PartPose.offset(0,-5,0));
        for(int i=0;i<4;i++)body.addOrReplaceChild("neck"+i,CubeListBuilder.create().texOffs(0,0).addBox(-8+i,-7+i,-7,16-i*2,14-i*2,12),PartPose.offsetAndRotation(0,-4-i*4,-12-i*6,-.12f,0,0));
        var h=body.addOrReplaceChild("head",CubeListBuilder.create().texOffs(0,0).addBox(-8,-6,-9,16,12,17),PartPose.offset(0,-17,-34));
        h.addOrReplaceChild("snout",CubeListBuilder.create().texOffs(0,0).addBox(-5,-2,-18,10,5,12),PartPose.ZERO);
        h.addOrReplaceChild("jaw",CubeListBuilder.create().texOffs(0,0).addBox(-4,-.5f,-17,8,2,16),PartPose.offset(0,4,0));
        for(int side:new int[]{-1,1}) {
            h.addOrReplaceChild("brow"+side,CubeListBuilder.create().texOffs(0,0).addBox(-3,-1,-2,6,2,4),PartPose.offsetAndRotation(side*5,-5,-7,0,0,side*.18f));
            h.addOrReplaceChild("eye"+side,CubeListBuilder.create().texOffs(0,0).addBox(-.6f,-.7f,-2,1.2f,1.4f,3),PartPose.offset(side*7.5f,-2,-7));
            var horn=h.addOrReplaceChild("horn"+side,CubeListBuilder.create().texOffs(0,0).addBox(-1,-8,-1,2,8,2),PartPose.offsetAndRotation(side*6,-5,4,-.35f,0,side*.25f));
            horn.addOrReplaceChild("fork",CubeListBuilder.create().texOffs(0,0).addBox(-.6f,-5,-.6f,1.2f,5,1.2f),PartPose.offsetAndRotation(0,-5,0,.6f,0,side*.5f));
            h.addOrReplaceChild("whisker"+side,CubeListBuilder.create().texOffs(0,0).addBox(-.4f,0,-.4f,.8f,10,.8f),PartPose.offsetAndRotation(side*4,1,-15,.3f,0,side*.7f));
            for(int front=0;front<2;front++) {
                var leg=r.addOrReplaceChild("leg"+side+"_"+front,CubeListBuilder.create().texOffs(0,0).addBox(-4,-2,-4,8,13,8),PartPose.offset(side*11,front==0?-5:1,front==0?-9:16));
                var shin=leg.addOrReplaceChild("shin",CubeListBuilder.create().texOffs(0,0).addBox(-2.7f,0,-3,5.4f,12,6),PartPose.offsetAndRotation(0,10,0,-.15f,0,0));
                for(int toe=-1;toe<=1;toe++)shin.addOrReplaceChild("claw"+toe,CubeListBuilder.create().texOffs(0,0).addBox(-.7f,-1,-6,1.4f,2,7),PartPose.offset(toe*2,11,-1));
            }
            for(int i=0;i<3;i++)body.addOrReplaceChild("pauldron"+side+"_"+i,CubeListBuilder.create().texOffs(0,0).addBox(-4,-1,-7,8,3,14),PartPose.offsetAndRotation(side*(10+i*1.2f),-9+i*2,-6,0,0,side*.25f));
        }
        r.addOrReplaceChild("hind",CubeListBuilder.create().texOffs(0,0).addBox(-10,-7,-9,20,15,20),PartPose.offset(0,1,19));
        var tail=r;for(int i=0;i<9;i++){float w=10-i*.9f;tail=tail.addOrReplaceChild("tail"+i,CubeListBuilder.create().texOffs(0,0).addBox(-w/2,-w/2,0,w,w,6),i==0?PartPose.offset(0,0,27):PartPose.offsetAndRotation(0,0,5,-.035f,0,0));
            if(i%2==0)tail.addOrReplaceChild("spine",CubeListBuilder.create().texOffs(0,0).addBox(-.7f,-3,0,1.4f,4,3),PartPose.offset(0,-w/2,1));}
        for(int i=0;i<5;i++)body.addOrReplaceChild("backplate"+i,CubeListBuilder.create().texOffs(0,0).addBox(-6,-1,-3,12,2,6),PartPose.offset(0,-11,-11+i*6));
        root=LayerDefinition.create(mesh,16,16).bakeRoot();neck=root.getChild("chest");head=neck.getChild("head");jaw=head.getChild("jaw");
        for(int side:new int[]{-1,1})for(int front=0;front<2;front++)legs.add(root.getChild("leg"+side+"_"+front));
        ModelPart t=root;for(int i=0;i<9;i++){t=t.getChild("tail"+i);tails.add(t);}
    }
    @Override public void setupAnim(DynastyBosses.DragonEmperor e,float limb,float amount,float age,float yaw,float pitch) {
        root.getAllParts().forEach(ModelPart::resetPose);
        neck.y+=Mth.sin(age*.06f)*.25f;head.yRot=Mth.clamp(yaw*.01745f,-.55f,.55f);head.xRot=pitch*.012f;
        float attack=e.characterAttackProgress(Mth.clamp(age-e.tickCount,0,1));
        jaw.xRot=.08f+Mth.sin(age*.035f)*.025f+Mth.sin(attack*Mth.PI)*.3f;
        for(int i=0;i<legs.size();i++)legs.get(i).xRot=Mth.cos(limb*.6f+(i%3==0?0:Mth.PI))*amount*.5f;
        for(int i=0;i<tails.size();i++){tails.get(i).yRot=Mth.sin(age*.04f-i*.5f)*(.035f+i*.008f);}
        if(e.deathTime>0)neck.zRot=Mth.clamp(e.deathTime/20f,0,1)*.7f;
    }
    @Override public void renderToBuffer(PoseStack pose,VertexConsumer out,int light,int overlay,float r,float g,float b,float alpha) {
        root.render(pose,out,light,overlay,r*.55f,g*.74f,b*.61f,alpha);
    }
}
