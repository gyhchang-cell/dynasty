package com.dynasty.blueprint.client;

import com.dynasty.blueprint.TemplateMob;
import net.minecraft.client.Minecraft;
import net.minecraft.core.Direction;
import net.minecraft.util.Mth;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import org.joml.Quaternionf;
import software.bernie.geckolib.cache.object.GeoBone;
import java.util.LinkedHashMap;
import java.util.IdentityHashMap;
import java.util.Map;
import java.util.UUID;

/** Bounded cosmetic state. Dedicated identity bones isolate inertia/IK from authored actions. */
@Mod.EventBusSubscriber(modid="dynasty", value=Dist.CLIENT)
public final class TemplateSecondaryMotion {
    private static final String[] SIDES={"right", "left"};
    private static final String[] IK_PARTS={"shoulder", "elbow", "wrist", "thigh", "knee", "ankle"};
    private static final LinkedHashMap<UUID, Motion> STATES=new LinkedHashMap<>(64,.75F,true);
    private static Object world;
    private static final class Motion {
        long tick=Long.MIN_VALUE, seen;
        Vec3 velocity=Vec3.ZERO;
        float yaw, rightArm, leftArm;
        final float[] angle=new float[14], speed=new float[14], roll=new float[14], rollSpeed=new float[14];
        final float[] rail=new float[2], ik=new float[12], ikY=new float[12], ikZ=new float[12];
        final double[] plantedY=new double[4];
        final boolean[] stance=new boolean[4];
        Direction face;
    }
    private TemplateSecondaryMotion() {}
    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut event) { STATES.clear();world=null; }
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event) {
        if(event.phase!=TickEvent.Phase.END)return;
        var level=Minecraft.getInstance().level;
        if(level!=world){STATES.clear();world=level;}
        if(level!=null&&level.getGameTime()%40==0)STATES.values().removeIf(s->level.getGameTime()-s.seen>80);
    }
    public static int activeStates(){return STATES.size();}
    public static void apply(TemplateMobModel model, TemplateMob mob, float partial) {
        // These bones have no authored animation. Reset on every draw, including far/dead entities,
        // because baked GeoBone objects may be reused when rendering another entity of this kind.
        resetProcedural(model,mob.kind());
        var mc=Minecraft.getInstance();
        if(mc.level!=world){STATES.clear();world=mc.level;}
        if(!mob.isAlive()||mc.level==null||mc.gameRenderer.getMainCamera().getPosition().distanceToSqr(mob.position())>32*32){STATES.remove(mob.getUUID());return;}
        if(mob.kind()==TemplateMob.Kind.SWORD||mob.kind()==TemplateMob.Kind.POWDER)return;
        Motion s=STATES.computeIfAbsent(mob.getUUID(),id->new Motion());
        while(STATES.size()>64)STATES.remove(STATES.keySet().iterator().next());
        long now=mc.level.getGameTime();s.seen=now;
        boolean advance=!mc.isPaused()&&s.tick!=now;
        if(advance){
            boolean fresh=s.tick==Long.MIN_VALUE||now-s.tick>4;
            int steps=fresh?1:(int)Math.max(1,Math.min(4,now-s.tick));
            Vec3 v=mob.getDeltaMovement();float yaw=mob.yBodyRot;
            float armR=rotation(model,"right_shoulder"),armL=rotation(model,"left_shoulder");
            Vec3 accel=fresh?Vec3.ZERO:v.subtract(s.velocity);
            double rad=Math.toRadians(yaw);
            float forward=(float)(accel.x*Math.sin(rad)-accel.z*Math.cos(rad));
            float sideways=(float)(accel.x*Math.cos(rad)+accel.z*Math.sin(rad));
            float turn=fresh?0:Mth.wrapDegrees(yaw-s.yaw)*Mth.DEG_TO_RAD;
            if(mob.kind()==TemplateMob.Kind.PRIEST)for(int j=0;j<14;j++){
                int side=j<8?j/4:j%2;
                float armDelta=fresh?0:(side==0?armR-s.rightArm:armL-s.leftArm);
                boolean distal=j<8?j%2==1:j>=11;
                float limit=(j<8?(distal?18:10):25)*Mth.DEG_TO_RAD;
                float target=Mth.clamp(-forward*2.4F-armDelta*.35F, -limit,limit);
                float targetRoll=Mth.clamp(-sideways*2-turn*.55F,-limit,limit);
                // Distal sections react to the parent's prior displacement and retain momentum.
                if(distal){int parent=j<8?j-1:j-3;target=Mth.clamp(target+s.angle[parent]*.35F,-limit,limit);targetRoll=Mth.clamp(targetRoll+s.roll[parent]*.35F,-limit,limit);}
                for(int n=0;n<steps;n++){
                    float k=distal?55:80,d=distal?11:14;
                    s.speed[j]+=(k*(target-s.angle[j])-d*s.speed[j])*.05F;
                    s.rollSpeed[j]+=(k*(targetRoll-s.roll[j])-d*s.rollSpeed[j])*.05F;
                    s.angle[j]=Mth.clamp(s.angle[j]+s.speed[j]*.05F,-limit,limit);
                    s.roll[j]=Mth.clamp(s.roll[j]+s.rollSpeed[j]*.05F,-limit,limit);
                }
            }
            if(mob.kind()==TemplateMob.Kind.SHIELD)for(int i=0;i<2;i++){
                float arm=i==0?armR:armL;
                float pulse=v.horizontalDistanceSqr()>.0001?Math.max(0,Mth.sin((mob.tickCount+i*10)*.32F))*.35F:0;
                float target=Mth.clamp(Math.abs(Mth.sin(arm))*.85F+pulse,0,1.2F);
                for(int n=0;n<steps;n++)s.rail[i]+=(target-s.rail[i])*.62F;
            }
            String[] gear=gearBones(mob.kind());
            for(int j=0;j<gear.length;j++){
                float limit=(mob.kind()==TemplateMob.Kind.FLAG?8:mob.kind()==TemplateMob.Kind.SCOUT?12:7)*Mth.DEG_TO_RAD;
                // Acceleration/yaw/body-action response only. Authored idle waves remain on
                // child bones; these identity wrappers never accumulate their transforms.
                float bodyDelta=fresh?0:armR-s.rightArm;
                float target=Mth.clamp(-forward*1.8F-bodyDelta*.14F,-limit,limit);
                float targetRoll=Mth.clamp(-sideways*1.5F-turn*.38F,-limit,limit);
                if(mob.kind()==TemplateMob.Kind.FLAG&&j>0){target+=s.angle[j-1]*.25F;targetRoll+=s.roll[j-1]*.25F;}
                target=Mth.clamp(target,-limit,limit);targetRoll=Mth.clamp(targetRoll,-limit,limit);
                for(int n=0;n<steps;n++){
                    s.speed[j]+=(58*(target-s.angle[j])-12*s.speed[j])*.05F;
                    s.rollSpeed[j]+=(58*(targetRoll-s.roll[j])-12*s.rollSpeed[j])*.05F;
                    s.angle[j]=Mth.clamp(s.angle[j]+s.speed[j]*.05F,-limit,limit);
                    s.roll[j]=Mth.clamp(s.roll[j]+s.rollSpeed[j]*.05F,-limit,limit);
                }
            }
            s.velocity=v;s.yaw=yaw;s.rightArm=armR;s.leftArm=armL;s.tick=now;
        }
        if(mob.kind()==TemplateMob.Kind.PRIEST){
            int j=0;for(String side:SIDES)for(String part:new String[]{"sleeve_inner_spring","sleeve_inner_tip","sleeve_outer_spring","sleeve_outer_tip"})set(model,side+"_"+part,s.angle[j],s.roll[j++]);
            float cast=mob.skillId()==0?1:.35F;
            for(int i=0;i<3;i++){set(model,"talisman_spring_"+i,s.angle[8+i]*cast,s.roll[8+i]*cast);set(model,"talisman_tip_"+i,s.angle[11+i]*cast,s.roll[11+i]*cast);}
        }else if(mob.kind()==TemplateMob.Kind.SHIELD){
            for(int i=0;i<2;i++){final float y=s.rail[i];model.getBone(SIDES[i]+"_shoulder_rail").ifPresent(b->b.setPosY(y));set(model,SIDES[i]+"_hip_plate_lower",Mth.clamp(rotation(model,SIDES[i]+"_knee")*.2F,-.14F,.14F),0);}
        }else if(mob.kind()==TemplateMob.Kind.BEAST&&mob.onClimbable()&&mob.climbFace()!=null&&mob.skillId()==0){
            if(advance)solveClimb(model,mob,s,now);
            for(int i=0;i<2;i++)for(int j=0;j<6;j++){
                int index=i*6+j;
                set(model,SIDES[i]+"_climb_"+IK_PARTS[j],s.ik[index],s.ikZ[index]);
                model.getBone(SIDES[i]+"_climb_"+IK_PARTS[j]).ifPresent(b->b.setRotY(s.ikY[index]));
            }
        }else if(mob.kind()==TemplateMob.Kind.BEAST){s.face=null;java.util.Arrays.fill(s.stance,false);java.util.Arrays.fill(s.ik,0);}
        String[] gear=gearBones(mob.kind());
        for(int j=0;j<gear.length;j++)set(model,gear[j],s.angle[j],s.roll[j]);
    }
    private static String[] gearBones(TemplateMob.Kind kind){return switch(kind){
        case SPEAR->SPEAR_GEAR;case CROSSBOW->CROSSBOW_GEAR;case SCOUT->SCOUT_GEAR;case FLAG->FLAG_GEAR;default->NO_GEAR;};}
    private static final String[] NO_GEAR={},SPEAR_GEAR={"skirt_spring_front","skirt_spring_back","skirt_spring_left","skirt_spring_right"},
        CROSSBOW_GEAR={"gear_pouch_0","gear_pouch_1","gear_pouch_2"},SCOUT_GEAR={"right_chain_spring","left_chain_spring"},
        FLAG_GEAR={"flag_spring_0","flag_spring_1","flag_spring_2","flag_spring_3"};
    private static void resetProcedural(TemplateMobModel model,TemplateMob.Kind kind){
        if(kind==TemplateMob.Kind.PRIEST){for(String side:SIDES)for(String n:new String[]{"sleeve_inner_spring","sleeve_inner_tip","sleeve_outer_spring","sleeve_outer_tip"})reset(model,side+"_"+n);for(int i=0;i<3;i++){reset(model,"talisman_spring_"+i);reset(model,"talisman_tip_"+i);}}
        if(kind==TemplateMob.Kind.SHIELD)for(String side:SIDES){reset(model,side+"_shoulder_rail");reset(model,side+"_hip_plate_lower");}
        if(kind==TemplateMob.Kind.BEAST)for(String side:SIDES)for(String part:IK_PARTS)reset(model,side+"_climb_"+part);
        for(String gear:gearBones(kind))reset(model,gear);
    }
    private static void reset(TemplateMobModel model,String name){model.getBone(name).ifPresent(b->{b.setRotX(0);b.setRotY(0);b.setRotZ(0);b.setPosX(0);b.setPosY(0);b.setPosZ(0);});}
    private static void set(TemplateMobModel model,String name,float x,float z){model.getBone(name).ifPresent(b->{b.setRotX(x);b.setRotZ(z);});}
    private static float rotation(TemplateMobModel model,String name){return model.getBone(name).map(GeoBone::getRotX).orElse(0F);}

    private static void solveClimb(TemplateMobModel model,TemplateMob mob,Motion s,long now){
        if(s.face!=mob.climbFace()){s.face=mob.climbFace();java.util.Arrays.fill(s.stance,false);}
        // Contact phase is keyed to the server epoch. The six-tick stepping cycle bounds limb
        // reach at the server's rapid climb speed; the slower authored clip supplies body motion.
        double phase=Math.floorMod(now-mob.climbStartTime(),6)/6.0;
        for(int side=0;side<2;side++)for(int rear=0;rear<2;rear++){
            int limb=side*2+rear;double p=(phase+(side==rear?0:.5))%1;boolean stance=p<.5;
            double centre=rear==0?-10.45:4.85,front=centre-3.5;
            if(stance&&!s.stance[limb])s.plantedY[limb]=mob.getY()-p*6*mob.getDeltaMovement().y;
            double z,y=.16;
            if(stance)z=front+16*(mob.getY()-s.plantedY[limb]);
            else{double swing=(p-.5)*2;z=Mth.lerp((float)swing,centre+3.5,front);y+=Math.sin(Math.PI*swing)*1.28;}
            // A lost/too-distant plant is released rather than stretching the animal's bones.
            z=Mth.clamp(z,centre-3.6,centre+3.6);s.stance[limb]=stance;
            String prefix=SIDES[side],contact=prefix+(rear==0?"_claw_contact":"_foot_contact");
            GeoBone end=model.getBone(contact).orElse(null);if(end==null)continue;
            Vector3f target=new Vector3f((side==0?1:-1)*(rear==0?5.4F:2.8F),(float)y,(float)z);
            String[] parts=rear==0?new String[]{"shoulder","elbow","wrist"}:new String[]{"thigh","knee","ankle"};
            GeoBone a=model.getBone(prefix+"_climb_"+parts[0]).orElse(null),b=model.getBone(prefix+"_climb_"+parts[1]).orElse(null),d=model.getBone(prefix+"_climb_"+parts[2]).orElse(null);
            if(a==null||b==null||d==null)continue;
            Vector3f wristTarget=new Vector3f(target).add(0,rear==0?1.95F:1.72F,rear==0?4.85F:1.95F);
            for(int iteration=0;iteration<6;iteration++){
                Map<GeoBone,Matrix4f> cache=new IdentityHashMap<>();
                Vector3f pa=point(a,cache),pb=point(b,cache),pd=point(d,cache);
                float l1=pa.distance(pb),l2=pb.distance(pd);
                Vector3f direction=new Vector3f(wristTarget).sub(pa);
                float length=Math.max(.001F,Math.min(l1+l2-.002F,direction.length()));
                if(direction.lengthSquared()<1e-8)continue;
                direction.normalize();
                Vector3f bend=new Vector3f(0,0,rear==0?-1:1);
                bend.sub(new Vector3f(direction).mul(bend.dot(direction)));
                if(bend.lengthSquared()<1e-8)continue;
                bend.normalize();
                float along=(length*length+l1*l1-l2*l2)/(2*length);
                Vector3f elbowTarget=new Vector3f(pa).add(new Vector3f(direction).mul(along)).add(bend.mul((float)Math.sqrt(Math.max(0,l1*l1-along*along))));
                for(int repeat=0;repeat<3;repeat++){aim(a,b,elbowTarget,false);aim(a,b,elbowTarget,true);}
                aim(b,d,wristTarget,false);
                // Cancel accumulated parent orientation at the wrist/ankle so the actual
                // palm/sole lies parallel to the wall, rather than merely touching it.
                Quaternionf inverse=matrix(d.getParent(),new IdentityHashMap<>()).getUnnormalizedRotation(new Quaternionf()).invert();
                Vector3f angles=inverse.getEulerAnglesZYX(new Vector3f());
                d.setRotX(angles.x);d.setRotY(angles.y);d.setRotZ(angles.z);
            }
        }
        for(int i=0;i<2;i++)for(int j=0;j<6;j++){s.ik[i*6+j]=rotation(model,SIDES[i]+"_climb_"+IK_PARTS[j]);s.ikY[i*6+j]=model.getBone(SIDES[i]+"_climb_"+IK_PARTS[j]).map(GeoBone::getRotY).orElse(0F);s.ikZ[i*6+j]=model.getBone(SIDES[i]+"_climb_"+IK_PARTS[j]).map(GeoBone::getRotZ).orElse(0F);}
    }
    private static void aim(GeoBone joint,GeoBone end,Vector3f target,boolean roll){
        Map<GeoBone,Matrix4f> cache=new IdentityHashMap<>();Matrix4f m=matrix(joint,cache);
        Vector3f pivot=point(joint,cache),current=point(end,cache).sub(pivot),wanted=new Vector3f(target).sub(pivot);
        Vector3f axis=roll?new Vector3f(0,0,1).mulDirection(matrix(joint.getParent(),cache)).normalize():new Vector3f(1,0,0).mulDirection(m).normalize();
        current.sub(new Vector3f(axis).mul(current.dot(axis)));wanted.sub(new Vector3f(axis).mul(wanted.dot(axis)));
        if(current.lengthSquared()<1e-8||wanted.lengthSquared()<1e-8)return;
        float angle=(float)Math.atan2(axis.dot(new Vector3f(current).cross(wanted)),current.dot(wanted));
        if(roll)joint.setRotZ(joint.getRotZ()+angle);else joint.setRotX(joint.getRotX()+angle);
    }
    private static Vector3f point(GeoBone bone,Map<GeoBone,Matrix4f> cache){return new Vector3f(bone.getPivotX(),bone.getPivotY(),bone.getPivotZ()).mulPosition(matrix(bone,cache));}
    private static Matrix4f matrix(GeoBone bone,Map<GeoBone,Matrix4f> cache){
        Matrix4f old=cache.get(bone);if(old!=null)return old;
        Matrix4f m=bone.getParent()==null?new Matrix4f():new Matrix4f(matrix(bone.getParent(),cache));
        m.translate(-bone.getPosX(),bone.getPosY(),bone.getPosZ()).translate(bone.getPivotX(),bone.getPivotY(),bone.getPivotZ())
            .rotateZ(bone.getRotZ()).rotateY(bone.getRotY()).rotateX(bone.getRotX()).scale(bone.getScaleX(),bone.getScaleY(),bone.getScaleZ())
            .translate(-bone.getPivotX(),-bone.getPivotY(),-bone.getPivotZ());
        cache.put(bone,m);return m;
    }
}
