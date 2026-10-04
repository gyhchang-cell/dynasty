package com.dynasty.client.character;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.Items;
import org.joml.Vector3f;
import java.util.*;

/** Original Dynasty articulated humans. Geometry, poses and the QA export share this one rig.
 * Model units are 1/16 block, +Y down, -Z forward. No client state is written to entities.
 */
public final class DynastyCharacterModel<T extends Mob> extends EntityModel<T> {
    public enum Role { ARCHER, REBEL, GUARD, GENERAL }
    public static final int SKIN=0xB88B69, SKIN_LIGHT=0xC99C78, SKIN_SHADE=0x95664F,
            INK=0x292623, EYE=0x191B1A, LINEN=0xAAA28B, TEAL=0x354F50,
            RED=0x653531, LEATHER=0x514030, STEEL=0x58646A, EDGE=0x9AA8AA,
            BRONZE=0xA0844F, DARK=0x303A3E, CLOTH=0x555444;

    public record Box(float x,float y,float z,float w,float h,float d,int color,ModelPart mesh) {}
    public static final class Joint {
        public final String name;
        public final Joint parent;
        public final List<Joint> children=new ArrayList<>();
        public final List<Box> boxes=new ArrayList<>();
        public final float x,y,z,restX,restY,restZ;
        public float rx,ry,rz,dx,dy,dz,sx=1,sy=1,sz=1;
        public boolean visible=true;
        public org.joml.Quaternionf orientation;
        Joint(String name,Joint parent,float x,float y,float z,float rx,float ry,float rz) {
            this.name=name;this.parent=parent;this.x=x;this.y=y;this.z=z;
            restX=rx;restY=ry;restZ=rz;reset();if(parent!=null)parent.children.add(this);
        }
        void reset(){rx=restX;ry=restY;rz=restZ;dx=dy=dz=0;sx=sy=sz=1;visible=true;orientation=null;children.forEach(Joint::reset);}
        public void transform(PoseStack p){p.translate((x+dx)/16,(y+dy)/16,(z+dz)/16);if(orientation!=null)p.mulPose(orientation);else{p.mulPose(Axis.ZP.rotation(rz));p.mulPose(Axis.YP.rotation(ry));p.mulPose(Axis.XP.rotation(rx));}p.scale(sx,sy,sz);}
        public void path(PoseStack p){if(parent!=null)parent.path(p);transform(p);}
    }
    public final Role role;
    public final Joint root;
    private final Map<String,Joint> joints=new LinkedHashMap<>();
    private int variant;
    private float draw;
    public DynastyCharacterModel(Role role) {
        this.role=role;root=j(null,"root",0,24,0);
        build();pose(0,0,0,0,0,0,0,0,0,0,false);
    }
    private Joint j(Joint parent,String name,float x,float y,float z){return j(parent,name,x,y,z,0,0,0);}
    private Joint j(Joint parent,String name,float x,float y,float z,float rx,float ry,float rz) {
        Joint p=new Joint(name,parent,x,y,z,rx,ry,rz);
        if(joints.put(name,p)!=null)throw new IllegalStateException("Duplicate joint "+name);return p;
    }
    private Joint n(String name){return Objects.requireNonNull(joints.get(name),name);}
    private void box(Joint p,float x,float y,float z,float w,float h,float d,int color) {
        var mesh=new MeshDefinition();mesh.getRoot().addOrReplaceChild("surface",CubeListBuilder.create().texOffs(0,0).addBox(x,y,z,w,h,d),PartPose.ZERO);
        p.boxes.add(new Box(x,y,z,w,h,d,color,LayerDefinition.create(mesh,16,16).bakeRoot()));
    }
    private void centered(Joint p,float w,float h,float d,int color){box(p,-w/2,0,-d/2,w,h,d,color);}
    private Joint detail(Joint p,String name,float x,float y,float z,float w,float h,float d,int color,float rx,float ry,float rz) {
        Joint q=j(p,name,x,y,z,rx,ry,rz);centered(q,w,h,d,color);return q;
    }
    private void build() {
        boolean general=role==Role.GENERAL,guard=role==Role.GUARD,archer=role==Role.ARCHER;
        boolean heavy=general||guard;
        float leg=general?15.6f:archer?14.2f:12.6f, shoulder=general?6.1f:guard?4.8f:archer?3.6f:3.8f;
        int coat=general?RED:guard?TEAL:archer?CLOTH:0x746449;
        Joint pelvis=j(root,"pelvis",0,-leg,0);centered(pelvis,heavy?6.8f:5.5f,2.3f,heavy?4.4f:3.6f,coat);
        Joint waist=j(pelvis,"waist",0,-1,0);centered(waist,heavy?5.3f:archer?4.0f:4.6f,1.2f,3.5f,LEATHER);
        box(waist,-1,-.15f,-2.05f,2,1.5f,.55f,BRONZE);
        Joint abdomen=j(waist,"abdomen",0,-2.4f,0);centered(abdomen,heavy?5.4f:4.6f,2.5f,heavy?3.7f:3.2f,coat);
        Joint chest=j(abdomen,"chest",0,-4.6f,0);
        centered(chest,general?9.6f:guard?8.3f:archer?5.9f:6.4f,general?5.2f:4.6f,general?5.6f:guard?4.8f:archer?3.4f:3.9f,coat);
        // Crossed lapels have independent volume; the outer cuirass sits in front of the inner tunic.
        detail(chest,"lapel_left",-1,-.1f,-2.35f,.72f,4.8f,.42f,LINEN,0,0,-.4f);
        detail(chest,"lapel_right",1.6f,-.1f,-2.38f,.65f,3.9f,.42f,LINEN,0,0,.4f);
        if(heavy) {
            centered(detail(chest,"breastplate",0,.7f,-.3f,7.5f,3.3f,5.1f,DARK,0,0,0),6,2.6f,5.4f,STEEL);
            for(int row=0;row<3;row++)for(int col=0;col<7;col++)
                box(chest,-3.5f+col,1+row*1.12f,-3f,.86f,.95f,.45f,(row+col)%3==0?STEEL:DARK);
            detail(chest,"heart_mirror",0,1.1f,-3.35f,2.7f,2.7f,.38f,BRONZE,0,0,0);
            detail(chest,"mirror_inset",0,1.55f,-3.62f,1.8f,1.8f,.2f,DARK,0,0,0);
        } else if(archer) {
            detail(chest,"leather_front",.1f,1.3f,-2.1f,5.8f,2.6f,.5f,LEATHER,0,0,0);
            for(int k=0;k<4;k++)detail(chest,"strap_stud"+k,-2.6f+k*1.3f,2,-2.42f,.3f,.3f,.18f,BRONZE,0,0,0);
            detail(chest,"quiver_sling",-.8f,-.1f,-2.5f,.65f,6.7f,.4f,LEATHER,0,0,-.43f);
            Joint quiver=j(chest,"quiver",2.5f,-1,3.1f,.1f,0,-.28f);
            centered(quiver,3.2f,9.4f,2.7f,LEATHER);
            for(int k=0;k<3;k++) {
                box(quiver,-.8f+k*.7f,-3,-.3f,.22f,4,.22f,LINEN);
                box(quiver,-1+k*.7f,-3.1f,-.4f,.6f,1.6f,.45f,INK);
            }
            box(quiver,-1.75f,0,-1.48f,3.5f,.65f,2.96f,BRONZE);
        } else {
            detail(chest,"patched_armor",-1.65f,.8f,-2.32f,3.3f,3.6f,.7f,DARK,0,0,-.12f);
            for(int k=0;k<3;k++)detail(chest,"repair_tie"+k,-1.7f,1.3f+k,-2.8f,2.6f,.2f,.18f,LEATHER,0,0,.15f);
        }
        Joint neck=j(chest,"neck",0,-1.4f,0);centered(neck,2,1.6f,2.2f,SKIN_SHADE);
        Joint head=j(neck,"head",0,-4.1f,-.05f);float hw=general?4.7f:4.35f;
        box(head,-hw/2,0,-1.85f,hw,3.65f,3.7f,SKIN);
        box(head,-1.65f,3,-1.7f,3.3f,1.15f,3.1f,SKIN_SHADE);
        box(head,-.43f,1,-2.23f,.86f,1.6f,.62f,SKIN_LIGHT);
        box(head,-.54f,2.15f,-2.57f,1.08f,.55f,.7f,SKIN_LIGHT);
        for(int sign:new int[]{-1,1}) {
            detail(head,"brow"+sign,sign*1.13f,.85f,-2.03f,1.5f,.35f,.5f,INK,0,0,sign*.12f);
            box(head,sign<0?-1.7f:.55f,1.28f,-2.01f,1.15f,.32f,.2f,LINEN);
            box(head,sign<0?-1.1f:.75f,1.28f,-2.16f,.4f,.32f,.1f,EYE);
            detail(head,"cheek"+sign,sign*1.65f,2,-1.88f,.62f,.8f,.22f,SKIN,0,sign*.32f,0);
            detail(head,"ear"+sign,sign*(hw/2+.1f),1.3f,0,.4f,1.25f,.8f,SKIN_SHADE,0,0,0);
        }
        box(head,-.7f,3,-1.98f,1.4f,.18f,.12f,INK);
        box(head,-hw/2-.12f,-.35f,-1.87f,hw+.24f,.85f,3.96f,INK);
        Joint knot=j(head,"topknot",0,-1.55f,.65f);centered(knot,1.6f,1.4f,1.5f,INK);
        box(knot,-1,-.1f,-.84f,2,.4f,1.7f,LEATHER);
        if(heavy) {
            box(head,-2.5f,-.6f,-2,5,1.1f,4.3f,DARK);
            box(head,-2.05f,-1.55f,-1.6f,4.1f,1,3.6f,STEEL);
            box(head,-1.1f,-2.3f,-.8f,2.2f,.85f,2.2f,DARK);
            box(head,-2.6f,.35f,-2.2f,5.2f,.42f,.65f,BRONZE);
            for(int sign:new int[]{-1,1})detail(head,"helmet_cheek"+sign,sign*2.35f,.7f,.65f,.6f,3.8f,2.3f,DARK,0,0,-sign*.06f);
            if(general) {
                detail(head,"crest",0,-4.7f,.7f,.85f,3.4f,1.4f,BRONZE,-.14f,0,0);
                detail(head,"crest_tail",0,-4.5f,1.3f,1.25f,5.8f,.65f,RED,-.52f,0,0);
                for(int sign:new int[]{-1,1})detail(head,"crown_fin"+sign,sign*1.55f,-3.6f,.5f,.7f,3,2,BRONZE,0,0,sign*.18f);
                box(head,-1.9f,3.1f,-1.9f,3.8f,1.3f,3.4f,SKIN_SHADE);
                box(head,-.4f,.8f,-2.4f,.8f,1.7f,.8f,SKIN_LIGHT);
            } else {
                // The guard's winged official cap cannot be mistaken for the general's crown.
                box(head,-2,-2.7f,-1.8f,4,2.1f,3.9f,INK);
                for(int sign:new int[]{-1,1})detail(head,"official_cap_wing"+sign,sign*3.5f,-.7f,.7f,3,.5f,1.1f,INK,0,0,sign*.12f);
            }
        } else {
            box(head,-2.3f,.25f,-2.02f,4.6f,.65f,4.05f,archer?TEAL:RED);
            detail(head,"headwrap_tail",2.05f,.6f,1.6f,.7f,4, .45f,archer?TEAL:RED,.25f,0,-.18f);
        }
        // Authored ensembles, not independent dice rolls. UUID chooses one of three coherent sets.
        Joint beard=j(head,"variant_beard",0,3,-1.75f);
        for(int k=0;k<3;k++)detail(beard,"beard_lobe"+k,(k-1)*.7f,0,0,.85f,k==1?2.8f:1.7f,.65f,INK,.12f,0,(k-1)*.08f);
        Joint moustache=j(head,"variant_moustache",0,2.8f,-2.02f);
        box(moustache,-1,0,-.22f,2,.4f,.45f,INK);
        detail(head,"variant_scar",1.6f,1.65f,-2.17f,.17f,1.3f,.16f,0x784B42,0,0,.3f);
        detail(pelvis,"variant_pouch",3,1.3f,.5f,1.9f,2.3f,2.2f,LEATHER,0,0,-.09f);
        Joint mantle=j(chest,"variant_mantle",-2.4f,.3f,2.5f,.13f,0,-.12f);
        centered(mantle,3.6f,7,.55f,TEAL);
        Joint extraWrap=j(head,"variant_wrap",-1.8f,.6f,1.8f,.16f,0,.18f);centered(extraWrap,.8f,5.2f,.5f,archer?TEAL:RED);
        Joint helmetRidge=j(head,"variant_ridge",0,-1.6f,-1.8f);centered(helmetRidge,.7f,2.3f,.6f,BRONZE);
        Joint sash=j(pelvis,"sash",-.8f,1.5f,-2.2f,.12f,0,.12f);
        centered(sash,1.3f,heavy?6:4.5f,.4f,RED);
        // A closed outer skirt first, overlapping plates second. Hips remain wider than waist.
        for(int i=0;i<5;i++) {
            float angle=(float)(i*Math.PI*2/5);
            Joint skirt=j(pelvis,"skirt"+i,(float)Math.sin(angle)*2.1f,1,(float)-Math.cos(angle)*1.8f,
                    -(float)Math.cos(angle)*.16f,angle,(float)-Math.sin(angle)*.17f);
            centered(skirt,heavy?3.7f:2.6f,heavy?(i==0?5.3f:6):archer?3.4f:4.1f,.55f,coat);
            if(heavy)for(int row=0;row<4;row++)box(skirt,-1.68f,.3f+row*1.2f,-.6f,3.36f,1,.38f,row%2==0?STEEL:DARK);
        }
        if(general) {
            Joint cape=j(chest,"cape",0,0,2.9f,.10f,0,0);
            centered(cape,10.6f,8,.7f,RED);
            Joint hem=j(cape,"cape_hem",0,8,.15f,.10f,0,0);centered(hem,12,9,.75f,RED);
            box(hem,-6,8.1f,-.47f,12,.7f,.95f,BRONZE);
            for(int sign:new int[]{-1,1})detail(chest,"cape_clasp"+sign,sign*3.35f,.4f,-2.9f,1.1f,.9f,.6f,BRONZE,0,0,0);
            for(int sign:new int[]{-1,1})detail(chest,"cape_shoulder_bridge"+sign,sign*4.2f,-.25f,0,1.4f,.7f,6.8f,BRONZE,0,0,0);
        }
        for(int sign:new int[]{-1,1}) {
            String side=sign<0?"right":"left";
            Joint shoulderJoint=j(chest,side+"_shoulder",sign*shoulder,.65f,0);
            Joint upper=j(shoulderJoint,side+"_upper_arm",0,0,0);
            float arm=archer?4.9f:general?5.1f:4.5f;
            centered(upper,heavy?2.9f:2.15f,arm,heavy?3.25f:2.55f,coat);
            if(heavy||(!archer&&sign<0)) {
                for(int k=0;k<(general?3:2);k++)
                    detail(upper,side+"_pauldron"+k,sign*k*.32f,-.6f+k*.8f,0,heavy?4.1f:3.2f,1.15f,heavy?4.5f:3.6f,k==0?BRONZE:DARK,0,0,-sign*.12f);
            } else box(upper,-1.3f,0,-1.5f,2.6f,1.4f,3,TEAL);
            Joint elbow=j(upper,side+"_elbow",0,arm,0);centered(elbow,heavy?2.5f:1.8f,.65f,heavy?2.7f:2.1f,LEATHER);
            Joint forearm=j(elbow,side+"_forearm",0,.15f,0);centered(forearm,heavy?2.4f:1.9f,4.1f,heavy?2.65f:2.1f,SKIN);
            box(forearm,-1.15f,.4f,-1.3f,2.3f,role==Role.REBEL&&sign>0?1.4f:2.8f,.65f,heavy?STEEL:role==Role.REBEL&&sign<0?DARK:LEATHER);
            for(int k=0;k<2;k++)box(forearm,-1.27f,.65f+k*1.75f,-1.47f,2.54f,.38f,2.95f,LEATHER);
            Joint wrist=j(forearm,side+"_wrist",0,3.9f,0);
            Joint hand=j(wrist,side+"_hand",0,.3f,0);
            // Hollow grip: palm at back, four curled fingers at front, thumb on one side.
            box(hand,-.9f,0,.38f,1.8f,1.6f,.55f,SKIN);
            for(int finger=0;finger<4;finger++) {
                box(hand,-.85f+finger*.44f,.25f,-.8f,.37f,.48f,1.2f,SKIN_LIGHT);
                box(hand,-.85f+finger*.44f,.65f,-.8f,.37f,.8f,.4f,SKIN);
            }
            detail(hand,side+"_thumb",sign*.83f,.1f,-.17f,.48f,1.25f,.55f,SKIN_LIGHT,0,0,sign*.35f);
            Joint thigh=j(pelvis,side+"_thigh",sign*(heavy?1.85f:1.5f),2,0);
            centered(thigh,heavy?3.35f:2.6f,4.8f,heavy?3.8f:3.1f,coat);
            Joint knee=j(thigh,side+"_knee",0,4.8f,0);
            box(knee,-1.4f,-.3f,-2,2.8f,1.6f,.8f,heavy?STEEL:LEATHER);
            Joint shin=j(knee,side+"_shin",0,.25f,0);float sh=leg-9.3f;
            centered(shin,heavy?2.65f:2.05f,sh,heavy?3:2.4f,LEATHER);
            if(heavy)box(shin,-1.05f,.9f,-1.8f,2.1f,sh-1,.65f,STEEL);
            else for(int k=0;k<3;k++)box(shin,-1.08f,k*.85f+.4f,-1.25f,2.16f,.25f,2.5f,LINEN);
            Joint ankle=j(shin,side+"_ankle",0,sh,0);
            Joint foot=j(ankle,side+"_foot",0,0,-.6f);box(foot,-1.4f,0,-2.55f,2.8f,1.8f,4.5f,INK);
            box(foot,-1.43f,1.55f,-2.6f,2.86f,.4f,4.6f,LEATHER);
            box(foot,-1.3f,.35f,-2.7f,2.6f,.8f,.5f,heavy?STEEL:LEATHER);
        }
        if(archer)buildBow();else buildSabre(general);
        if(!archer) {
            Joint scabbard=j(pelvis,"scabbard",3.4f,.8f,1.2f,.05f,0,-.23f);
            centered(scabbard,.95f,11,1.3f,LEATHER);
            box(scabbard,-.6f,9.9f,-.78f,1.2f,1.15f,1.55f,BRONZE);
        }
    }
    private void buildSabre(boolean general) {
        Joint blade=j(n("right_hand"),"weapon",0,.8f,-.12f,(float)-Math.PI/2,0,0);
        centered(blade,.55f,3.4f,.6f,LEATHER);
        box(blade,-1.35f,3.3f,-.6f,2.7f,.6f,1.2f,BRONZE);
        float length=general?14:10.5f,width=general?1.7f:1.2f;
        box(blade,-width/2,3.9f,-.23f,width,length,.46f,STEEL);
        box(blade,-width/2-.2f,3.9f,-.12f,.25f,length,.24f,EDGE);
        detail(blade,"blade_tip",-.25f,length+3.5f,0,width*.65f,1.4f,.3f,EDGE,0,0,.32f);
        box(blade,-.5f,-.6f,-.45f,1,.65f,.9f,BRONZE);
        if(general){
            box(blade,-2.4f,3,-.7f,4.8f,.9f,1.4f,BRONZE);
            for(int sign:new int[]{-1,1})detail(blade,"general_guard_hook"+sign,sign*2.1f,2.2f,0,.65f,2,.9f,BRONZE,0,0,-sign*.3f);
            box(blade,-.3f,-1.3f,-.3f,.6f,1,.6f,RED);
        }
    }
    private void buildBow() {
        Joint bow=j(n("left_hand"),"weapon",0,.85f,-.15f,0,0,0);
        centered(bow,.5f,1.5f,.65f,LEATHER);
        for(int sign:new int[]{-1,1}) {
            Joint inner=j(bow,"bow_inner"+sign,0,sign*.7f,0,sign*.28f,0,0);
            box(inner,-.3f,sign<0?-4.8f:0,-.3f,.6f,4.8f,.6f,LEATHER);
            Joint tip=j(inner,"bow_tip"+sign,0,sign*4.8f,0,-sign*.65f,0,0);
            box(tip,-.23f,sign<0?-3:0,-.25f,.46f,3,.5f,BRONZE);
        }
        for(String name:List.of("bow_string_top","bow_string_bottom","nocked_arrow")) {
            Joint line=j(root,name,0,0,0);box(line,-.5f,0,-.5f,1,1,1,name.equals("nocked_arrow")?LEATHER:LINEN);
        }
    }
    @Override public void setupAnim(T e,float limb,float amount,float age,float yaw,float pitch) {
        variant=Math.floorMod(e.getUUID().hashCode(),3);
        float partial=Mth.clamp(age-e.tickCount,0,1);
        float drawing=e.isUsingItem()&&e.getUseItem().is(Items.BOW)?Mth.clamp((e.getTicksUsingItem()+partial)/20,0,1):0;
        float attack=e instanceof com.dynasty.entity.DynastyHumanoidMob humanoid&&role!=Role.ARCHER?humanoid.characterAttackProgress(partial):e.getAttackAnim(partial);
        pose(limb,amount,age,yaw,pitch,attack,e.hurtTime,e.deathTime,drawing,variant,e.isAggressive());
        n("weapon").visible=role==Role.ARCHER?e.getMainHandItem().is(Items.BOW):e.getMainHandItem().isEmpty();
        if(role==Role.ARCHER&&!n("weapon").visible){n("bow_string_top").visible=false;n("bow_string_bottom").visible=false;n("nocked_arrow").visible=false;}
    }
    /** Also used by deterministic studio QA, with exactly the same animation paths as the renderer. */
    public void pose(float limb,float amount,float age,float yaw,float pitch,float attack,float hurt,float death,float drawing,int ensemble,boolean aggressive) {
        root.reset();variant=ensemble;draw=drawing;
        boolean archer=role==Role.ARCHER,general=role==Role.GENERAL,guard=role==Role.GUARD;
        float mass=general?.65f:guard?.8f:1, stride=Math.min(1,amount)*mass,cycle=limb*.64f;
        n("pelvis").dy=(float)Math.abs(Math.sin(cycle))*stride*.45f;
        n("waist").ry=(float)Math.sin(cycle)*stride*.10f;
        n("abdomen").rx=role==Role.REBEL?.12f:guard?.055f:.025f;
        n("chest").rx+=(float)Math.sin(age*(general?.045f:.065f))*.018f;
        n("chest").ry=archer?-.30f:general?-.08f:0;
        n("head").ry=yaw*Mth.DEG_TO_RAD-n("chest").ry*.6f;
        n("neck").rx=pitch*Mth.DEG_TO_RAD*.35f;n("head").rx=pitch*Mth.DEG_TO_RAD*.65f;
        n("variant_beard").visible=general||ensemble==2;
        n("variant_moustache").visible=general||ensemble==1;
        n("variant_scar").visible=ensemble==2;
        n("variant_pouch").visible=ensemble!=1;
        n("variant_mantle").visible=ensemble==1&&!general&&!guard;
        n("variant_wrap").visible=ensemble==0&&!general&&!guard;
        n("variant_ridge").visible=(guard||general)&&ensemble==2;
        // Bone-local facial variation, stable across reconnects because entity UUID is saved/synced.
        n("head").rz=(ensemble-1)*.015f;
        n("head").sx=ensemble==2?1.06f:ensemble==1?.95f:1;
        n("topknot").visible=ensemble!=1;
        for(int sign:new int[]{-1,1}) {
            String side=sign<0?"right":"left";
            float phase=cycle+(sign<0?(float)Math.PI:0),s=(float)Math.sin(phase);
            n(side+"_thigh").rx=s*stride*.72f-(guard?.07f:0);
            n(side+"_knee").rx=-Math.max(0,-s)*stride*.90f-(guard?.11f:.045f);
            n(side+"_ankle").rx=Math.max(0,s)*stride*.18f;
            n(side+"_foot").rx=-n(side+"_thigh").rx*.14f;
            n(side+"_shoulder").rz=-sign*(general?.16f:guard?.12f:.08f);
            n(side+"_upper_arm").rx=-s*stride*.5f;
            n(side+"_elbow").rx=-.25f-Math.max(0,s)*stride*.35f;
            n(side+"_wrist").rz=sign*.05f+(float)Math.sin(age*.08f)*.012f;
        }
        if(archer) {
            n("chest").ry-=drawing*.42f;
            n("left_shoulder").ry=-drawing*.12f;
            // Two-bone solves place bow grip forward and string hand at the right cheek.
            armTarget("left",new Vector3f(3.4f,3.4f-6.2f*drawing,-3.1f-5.6f*drawing));
            armTarget("right",new Vector3f(-2.7f,4.1f-8.0f*drawing,-3+1.0f*drawing));
        } else {
            n("right_upper_arm").rx-=guard?.42f:general?.28f:.15f;
            n("right_elbow").rx-=general?.45f:guard?.65f:.25f;
            n("right_wrist").rx=-.12f;
            // Sequential windup -> waist/chest rotation -> shoulder -> elbow -> wrist, then recovery.
            float wind=attack<.3f?attack/.3f:Math.max(0,1-(attack-.3f)/.7f);
            float strike=(float)Math.sin(Math.PI*Mth.clamp((attack-.25f)/.5f,0,1));
            n("waist").ry+=wind*-.24f+strike*.45f;
            n("chest").ry+=wind*-.35f+strike*.65f;
            n("right_shoulder").rx-=wind*.25f;
            n("right_upper_arm").rx-=wind*1.7f-strike*.8f;
            n("right_elbow").rx-=wind*.65f-strike*.5f;
            n("right_wrist").rx+=strike*.5f;
            n("left_upper_arm").rx-=strike*.4f;
        }
        for(int i=0;i<5;i++)n("skirt"+i).rx+=(float)Math.sin(cycle+i*.5)*stride*.10f;
        n("sash").rx+=(float)Math.sin(age*.09f)*.05f+stride*.15f;
        if(general){n("cape").rx+=stride*.16f;n("cape_hem").rx+=(float)Math.sin(age*.075f)*.045f+stride*.12f;}
        if(hurt>0){float f=(float)Math.sin(hurt*.32f);n("abdomen").rx-=f*.18f;n("chest").rz=f*.11f;n("head").rx-=f*.12f;}
        if(death>0){float f=Mth.clamp(death/20,0,1);n("pelvis").dy+=f*3;n("waist").rx+=f*.35f;n("neck").rx+=f*.35f;for(String side:List.of("left","right")){n(side+"_knee").rx-=f*.65f;n(side+"_elbow").rx-=f*.4f;}}
        if(archer)updateBowLines();
    }
    private void armTarget(String side,Vector3f target) {
        Joint sh=n(side+"_shoulder");sh.rz=0;
        var shoulderQ=new org.joml.Quaternionf().rotationZYX(sh.rz,sh.ry,sh.rx);
        Vector3f d=new org.joml.Quaternionf(shoulderQ).invert().transform(new Vector3f(target).sub(sh.x,sh.y,sh.z));
        float upper=4.9f,lower=4.05f,length=Mth.clamp(d.length(),1,upper+lower-.06f);
        d.normalize().mul(length);Vector3f axis=new Vector3f(d).normalize();
        Vector3f pole=new Vector3f(side.equals("left")?1:-1,.15f,.65f);
        pole.sub(new Vector3f(axis).mul(pole.dot(axis))).normalize();
        float along=(upper*upper+length*length-lower*lower)/(2*length);
        Vector3f elbow=new Vector3f(axis).mul(along).add(pole.mul((float)Math.sqrt(Math.max(0,upper*upper-along*along))));
        var upperQ=new org.joml.Quaternionf().rotationTo(new Vector3f(0,1,0),new Vector3f(elbow).normalize());
        Vector3f lowerDir=new org.joml.Quaternionf(upperQ).invert().transform(new Vector3f(d).sub(elbow).normalize());
        var lowerQ=new org.joml.Quaternionf().rotationTo(new Vector3f(0,1,0),lowerDir);
        n(side+"_upper_arm").orientation=upperQ;n(side+"_elbow").orientation=lowerQ;
        n(side+"_wrist").orientation=new org.joml.Quaternionf(shoulderQ).mul(upperQ).mul(lowerQ).invert();
    }
    @Override public void renderToBuffer(PoseStack p,VertexConsumer out,int light,int overlay,float r,float g,float b,float a) {
        render(root,p,out,light,overlay,r,g,b,a);
    }
    private void render(Joint j,PoseStack p,VertexConsumer out,int light,int overlay,float r,float g,float b,float a) {
        if(!j.visible)return;p.pushPose();j.transform(p);
        for(Box box:j.boxes){int c=box.color;box.mesh.render(p,out,light,overlay,r*((c>>16)&255)/255f,g*((c>>8)&255)/255f,b*(c&255)/255f,a);}
        for(Joint child:j.children)render(child,p,out,light,overlay,r,g,b,a);p.popPose();
    }
    public Vector3f point(String name,float x,float y,float z) {
        var p=new PoseStack();n(name).path(p);return p.last().pose().transformPosition(new Vector3f(x/16,y/16,z/16));
    }
    private void updateBowLines() {
        if(draw>.05f) {
            var p=new PoseStack();n("weapon").path(p);
            Vector3f local=new org.joml.Matrix4f(p.last().pose()).invert().transformPosition(point("right_hand",0,.7f,-.1f));
            n("weapon").ry=(float)Math.atan2(local.x,local.z);
        }
        Vector3f top=point("bow_tip-1",0,-3,0),bottom=point("bow_tip1",0,3,0);
        Vector3f grip=point("weapon",0,0,0);
        Vector3f pull=draw>.05f?point("right_hand",0,.7f,-.1f):new Vector3f(top).lerp(bottom,.5f);
        line("bow_string_top",top,pull,.012f);line("bow_string_bottom",bottom,pull,.012f);
        n("nocked_arrow").visible=draw>.05f;
        if(draw>.05f){Vector3f tip=new Vector3f(grip).sub(pull).normalize().mul(.32f).add(grip);line("nocked_arrow",pull,tip,.022f);}
    }
    private void line(String name,Vector3f from,Vector3f to,float width) {
        Joint j=n(name);Vector3f d=new Vector3f(to).sub(from);
        j.dx=from.x*16;j.dy=from.y*16-24;j.dz=from.z*16;
        j.orientation=new org.joml.Quaternionf().rotationTo(new Vector3f(0,1,0),new Vector3f(d).normalize());
        j.sx=j.sz=width*16;j.sy=d.length()*16;
    }
    public void handTransform(PoseStack p,boolean left){n(left?"left_hand":"right_hand").path(p);p.translate(0,.8/16,-.12/16);}
    public int boxCount(){return joints.values().stream().mapToInt(j->j.boxes.size()).sum();}
    public Set<String> jointNames(){return Collections.unmodifiableSet(joints.keySet());}
}
