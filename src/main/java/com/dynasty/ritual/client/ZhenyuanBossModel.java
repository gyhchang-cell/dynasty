package com.dynasty.ritual.client;
import com.dynasty.ritual.ZhenyuanSovereign;
import net.minecraft.resources.ResourceLocation;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.core.animation.AnimationState;

/** Server-clocked arrival: observers and reconnects seek the same pose, never replay a local intro. */
public final class ZhenyuanBossModel extends GeoModel<ZhenyuanSovereign> {
    @Override public ResourceLocation getModelResource(ZhenyuanSovereign e) { return new ResourceLocation("dynasty","geo/zhenyuan_sovereign.geo.json"); }
    @Override public ResourceLocation getTextureResource(ZhenyuanSovereign e) { return new ResourceLocation("dynasty","textures/entity/zhenyuan_sovereign.png"); }
    @Override public ResourceLocation getAnimationResource(ZhenyuanSovereign e) { return new ResourceLocation("dynasty","animations/zhenyuan_sovereign.animation.json"); }
    private static float smooth(double x) { float a=(float)Math.max(0,Math.min(1,x));return a*a*(3-2*a); }
    private void rotate(String name,float x,float y,float z) { getBone(name).ifPresent(b->{b.setRotX(x);b.setRotY(y);b.setRotZ(z);}); }
    private void scale(String name,float s) {getBone(name).ifPresent(b->{b.setScaleX(s);b.setScaleY(s);b.setScaleZ(s);});}
    @Override public void setCustomAnimations(ZhenyuanSovereign e,long id,AnimationState<ZhenyuanSovereign> state) {
        super.setCustomAnimations(e,id,state);
        float t=e.introTick()+(e.introRunning()?state.getPartialTick():0);
        poseArrival(t,e,state.getPartialTick());
    }
    public void poseArrival(float t,ZhenyuanSovereign e,float partial) {
        float rise=smooth((t-60)/80),roar=smooth((t-202)/25)*(1-smooth((t-252)/28));
        for(var bone:getAnimationProcessor().getRegisteredBones()) {
            String n=bone.getName();
            if(n.equals("seal_core")) {bone.setHidden(t>=140);continue;}
            int reveal=n.contains("claw")||n.contains("hand")||n.contains("wrist")?60:
                    n.contains("arm")||n.contains("elbow")?76:n.contains("shoulder")?90:
                    n.contains("head")||n.contains("face")||n.contains("horn")||n.contains("jaw")||n.contains("neck")?118:
                    n.contains("thigh")||n.contains("knee")||n.contains("shin")||n.contains("ankle")||n.contains("foot")||n.contains("toe")?128:102;
            if(n.equals("root"))reveal=0;
            bone.setHidden(t<reveal || n.contains("eye")&&t<190);
            // Hidden torso cubes must not hide the already-emerging hands in their child hierarchy.
            bone.setChildrenHidden(false);
        }
        getBone("root").ifPresent(b->b.setPosY(-24*(1-rise)));
        getBone("seal_core").ifPresent(b->{ b.setPosY(24*(1-rise)); b.setRotY(t*.025F); });
        float pulse=0;for(int key:new int[]{12,32,54})pulse+=Math.max(0,1-Math.abs(t-key)/8F)*.18F;
        scale("seal_core",1+pulse);
        if(t<280) {
            rotate("spine_01",.4F*(1-rise)-roar*.12F,0,0);
            rotate("spine_02",.22F*(1-smooth((t-160)/35))-roar*.15F,0,0);
            rotate("main_head",.62F*(1-smooth((t-165)/25))-roar*.65F,e==null?0:smooth((t-170)/20)*Math.max(-.65F,Math.min(.65F,(e.yHeadRot-e.yBodyRot)*(float)Math.PI/180)),0);
            rotate("jaw",roar*.8F,0,0);
            for(String side:new String[]{"left","right"}) {
                int sign=side.equals("left")?1:-1;
                rotate(side+"_shoulder",-.65F*(1-rise),0,-sign*(.18F+roar*.65F));
                rotate(side+"_elbow",-.55F*(1-rise)-roar*.2F,0,0);
                rotate(side+"_wrist",roar*.25F,0,sign*roar*.2F);
                rotate(side+"_back_blade",0,sign*roar*.8F,sign*roar*.25F);
                for(int i=1;i<=3;i++)rotate(side+"_claw_0"+i,-.25F-roar*.3F+(t>160&&t<190?(float)Math.sin((t-160)*.22+i)*.14F:0),0,0);
            }
            scale("chest",1+(t>160?(float)Math.sin((t-160)*.07)*.015F:0));
        } else {
            scale("chest",1);
            getBone("spine_01").ifPresent(b->b.setRotX(0));rotate("spine_02",0,0,0);
            rotate("main_head",e==null?0:e.getXRot()*(float)Math.PI/180,e==null?0:Math.max(-.6F,Math.min(.6F,(e.yHeadRot-e.yBodyRot)*(float)Math.PI/180)),0);
            rotate("jaw",.08F,0,0);
            float attack=e==null?0:e.getAttackAnim(partial);
            for(String side:new String[]{"left","right"}) {
                int sign=side.equals("left")?1:-1;
                rotate(side+"_back_blade",0,sign*.15F,sign*.1F);
                float walk=e==null?0:(float)Math.sin(e.walkAnimation.position(partial)*.6F)*Math.min(.3F,e.walkAnimation.speed(partial));
                rotate(side+"_shoulder",-sign*walk,0,-sign*.16F);
                rotate(side+"_upper_arm",0,0,0);rotate(side+"_elbow",-.2F,0,0);
                rotate(side+"_forearm",0,0,0);rotate(side+"_wrist",0,0,0);
                for(int i=1;i<=3;i++)rotate(side+"_claw_0"+i,-.2F,0,0);
                if(attack>0) {
                    // Existing melee swing propagates down actual joints; this is not a new combat skill.
                    String[] joints={"shoulder","upper_arm","elbow","forearm","wrist"};
                    for(int i=0;i<joints.length;i++)rotate(side+"_"+joints[i],-(float)Math.sin(Math.max(0,attack-i*.07)*Math.PI)*(1.1F-i*.18F),0,i==0?sign*.2F:0);
                }
            }
        }
    }
}
