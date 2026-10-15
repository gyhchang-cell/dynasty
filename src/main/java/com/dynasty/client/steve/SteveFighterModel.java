package com.dynasty.client.steve;

import com.google.gson.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.AnimationUtils;
import net.minecraft.client.model.geom.*;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Mob;
import java.util.*;
import com.dynasty.blueprint.TemplateMob;
import com.dynasty.blueprint.TemplateSkills;
import com.dynasty.entity.DynastyHumanoidMob;

/** Standard Steve pivots and six body cuboids, with small independently textured equipment. */
public final class SteveFighterModel<T extends Mob> extends HumanoidModel<T> {
    public final String id,role;
    public final float visualScale;
    private final ModelPart root;
    private final Map<String,ModelPart> pieces=new HashMap<>();
    private record Baked(ModelPart root,JsonObject definition){}
    public SteveFighterModel(String id){this(id,load(id));}
    private SteveFighterModel(String id,Baked data){
        super(data.root);this.root=data.root;this.id=id;role=data.definition.get("role").getAsString();visualScale=data.definition.get("scale").getAsFloat();
        pieces.put("root",root);
        for(var entry:data.definition.getAsJsonArray("parts")){
            var q=entry.getAsJsonObject();pieces.put(q.get("name").getAsString(),pieces.get(q.get("parent").getAsString()).getChild(q.get("name").getAsString()));
        }
    }
    public static ResourceLocation definition(String id){return new ResourceLocation("dynasty","models/entity/steve_fighters/"+id+".json");}
    public static ResourceLocation texture(String id){return new ResourceLocation("dynasty","textures/entity/steve_fighters/"+id+".png");}
    private static float v(JsonObject o,String key,int i){return o.getAsJsonArray(key).get(i).getAsFloat();}
    private static Baked load(String id){
        try(var reader=Minecraft.getInstance().getResourceManager().getResourceOrThrow(definition(id)).openAsReader()){
            var data=JsonParser.parseReader(reader).getAsJsonObject();var mesh=new MeshDefinition();var parts=new HashMap<String,PartDefinition>();parts.put("root",mesh.getRoot());
            for(var entry:data.getAsJsonArray("parts")){
                var q=entry.getAsJsonObject();String name=q.get("name").getAsString();
                var bone=parts.get(q.get("parent").getAsString()).addOrReplaceChild(name,CubeListBuilder.create(),PartPose.offsetAndRotation(v(q,"pivot",0),v(q,"pivot",1),v(q,"pivot",2),v(q,"rotation",0)*Mth.DEG_TO_RAD,v(q,"rotation",1)*Mth.DEG_TO_RAD,v(q,"rotation",2)*Mth.DEG_TO_RAD));
                // Only the surface is doubled and scaled back: vanilla pivots/animation stay exact.
                bone.addOrReplaceChild("surface",CubeListBuilder.create().texOffs((int)v(q,"uv",0),(int)v(q,"uv",1)).addBox(v(q,"origin",0)*2,v(q,"origin",1)*2,v(q,"origin",2)*2,v(q,"size",0)*2,v(q,"size",1)*2,v(q,"size",2)*2),PartPose.ZERO);parts.put(name,bone);
            }
            mesh.getRoot().addOrReplaceChild("hat",CubeListBuilder.create(),PartPose.ZERO);
            var root=LayerDefinition.create(mesh,256,256).bakeRoot();root.getAllParts().forEach(p->{if(p.hasChild("surface")){var s=p.getChild("surface");s.xScale=s.yScale=s.zScale=.5f;}});
            return new Baked(root,data);
        }catch(Exception e){throw new IllegalStateException("Invalid Steve fighter resource: "+id,e);}
    }
    @Override public void setupAnim(T mob,float limb,float amount,float age,float yaw,float pitch){
        root.getAllParts().forEach(p->{p.resetPose();p.visible=true;});
        root.getAllParts().forEach(p->{if(p.hasChild("surface")){var s=p.getChild("surface");s.xScale=s.yScale=s.zScale=.5f;}});
        leftArmPose=rightArmPose=ArmPose.EMPTY;
        if(mob.isUsingItem()&&mob.getUseItem().is(net.minecraft.world.item.Items.BOW)){
            if(mob.getMainArm()==net.minecraft.world.entity.HumanoidArm.RIGHT)rightArmPose=ArmPose.BOW_AND_ARROW;else leftArmPose=ArmPose.BOW_AND_ARROW;
        }
        super.setupAnim(mob,limb,amount,age,yaw,pitch);
        if(role.equals("crossbow"))AnimationUtils.animateCrossbowHold(rightArm,leftArm,head,true);
        else if(!mob.isUsingItem()&&attackTime==0){rightArm.zRot=-.05f;leftArm.zRot=.05f;}
        float partial=age-mob.tickCount;
        if(mob instanceof DynastyHumanoidMob fighter){float p=fighter.characterAttackProgress(partial);if(p>0)strike(p,.5f);}
        if(mob instanceof TemplateMob t){
            var def=TemplateSkills.byId(t.skillId());
            if(def!=null){float tick=t.actionAge(partial);float contact=def.impactTicks().isEmpty()?def.windupTicks():def.impactTicks().get(0);
                float p=Mth.clamp(tick/def.totalTicks(),0,1);float peak=contact/def.totalTicks();
                float pulse=0;
                for(int hit:def.impactTicks())pulse=Math.max(pulse,Math.max(0,1-Math.abs(tick-hit)/3));
                if(role.equals("crossbow")){AnimationUtils.animateCrossbowHold(rightArm,leftArm,head,true);rightArm.xRot-=pulse*.16f;}
                else if(role.equals("spear")||role.equals("powder")){
                    float ready=Mth.clamp(tick/Math.max(1,contact-3),0,1);
                    float recover=Mth.clamp((def.totalTicks()-tick)/Math.max(1,def.recoveryTicks()),0,1);
                    rightArm.xRot=-1.15f*ready*recover-.3f*pulse;rightArm.z=-2*pulse;
                    if(role.equals("spear")){leftArm.xRot=-.9f*ready*recover;leftArm.yRot=.35f;}
                }else{
                    // Each server contact owns a separate swing, including multi-hit combos.
                    float previous=0;boolean posed=false;
                    for(int hit:def.impactTicks()){
                        float end=hit+Math.min(4,def.recoveryTicks());
                        if(tick<=end){strike(Mth.clamp((tick-previous)/Math.max(1,end-previous),0,1),(hit-previous)/Math.max(1,end-previous));posed=true;break;}
                        previous=end;
                    }
                    if(!posed)rightArm.xRot=0;
                    if(role.equals("shield")&&tick<contact+4){leftArm.xRot=-.6f*pulse;leftArm.z=-2*pulse;}
                }
            }
        }
        // Real inventory takes precedence over authored visual weapons. Never alter inventory/drop state.
        if(pieces.containsKey("weapon_shaft"))pieces.get("weapon_shaft").visible=mob.getMainHandItem().isEmpty();
        if(pieces.containsKey("shield"))pieces.get("shield").visible=mob.getOffhandItem().isEmpty();
        if(role.equals("shield")&&mob.isDeadOrDying()){
            // Existing ten-second server cover remains upright; do not roll the shield into the ground.
            body.y=5;head.y=5;rightArm.y=7;leftArm.y=7;rightLeg.xRot=-.9f;leftLeg.xRot=-.9f;leftArm.xRot=0;leftArm.zRot=0;
            pieces.get("shield").y=0;
        }
    }
    private void strike(float p,float impact){
        float peak=Math.max(.01f,impact*.7f);
        if(p<peak)rightArm.xRot=Mth.lerp(p/peak,-.25f,-2.1f);
        else if(p<impact)rightArm.xRot=Mth.lerp((p-peak)/Math.max(.01f,impact-peak),-2.1f,-.65f);
        else rightArm.xRot=Mth.lerp(Mth.clamp((p-impact)/Math.max(.01f,1-impact),0,1),-.65f,0);
        rightArm.yRot=-.15f;body.yRot=-.08f*(float)Math.sin(p*Math.PI);
    }
}
