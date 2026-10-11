package com.dynasty.client;

import com.dynasty.client.character.*;
import com.google.gson.GsonBuilder;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.world.entity.Mob;
import org.joml.Vector3f;
import java.nio.file.*;
import java.util.*;

/** Actual Java transforms, using the exact accepted guard-v2 source as the control. */
final class GuardProportionProof {
    static List<GuardStyleProof.Cube> cubes(LegacyGuardStyleModel<?> model){var out=new ArrayList<GuardStyleProof.Cube>();collect(model.root,out);return out;}
    static void collect(LegacyGuardStyleModel.Joint j,List<GuardStyleProof.Cube> out){
        if(!j.visible)return;var p=new PoseStack();j.path(p);int index=0;
        for(var b:j.boxes){double[][] vertices=new double[8][3];int k=0;for(int x=0;x<2;x++)for(int y=0;y<2;y++)for(int z=0;z<2;z++){
            var v=p.last().pose().transformPosition(new Vector3f((b.x()+x*b.w())/16,(b.y()+y*b.h())/16,(b.z()+z*b.d())/16));vertices[k++]=new double[]{v.x,v.y,v.z};}
            out.add(new GuardStyleProof.Cube(j.name,index++,b.color(),vertices));}
        for(var child:j.children)collect(child,out);
    }
    static LegacyGuardStyleModel.Joint joint(LegacyGuardStyleModel.Joint j,String name){if(j.name.equals(name))return j;for(var c:j.children){var result=joint(c,name);if(result!=null)return result;}return null;}
    static void subtree(DynastyCharacterModel.Joint j,Set<String> names){names.add(j.name);for(var child:j.children)subtree(child,names);}
    static void equal(List<GuardStyleProof.Cube> a,List<GuardStyleProof.Cube> b,Set<String> allowed){
        if(a.size()!=b.size())throw new AssertionError("Cubes removed");
        for(int i=0;i<a.size();i++){
            var x=a.get(i);var y=b.get(i);
            if(!x.joint().equals(y.joint())||x.index()!=y.index()||x.color()!=y.color())throw new AssertionError("Cube identity/color changed");
            if(!allowed.contains(x.joint())&&!(x.joint().equals("waist")&&x.index()==0)&&!Arrays.deepEquals(x.vertices(),y.vertices()))throw new AssertionError("Unintended geometry change: "+x.joint());
        }
    }
    static double distance(double[] a,double[] b){double value=0;for(int i=0;i<3;i++)value+=(a[i]-b[i])*(a[i]-b[i]);return Math.sqrt(value);}
    static double neckContact(List<GuardStyleProof.Cube> cubes){
        var neck=cubes.stream().filter(c->c.joint().equals("neck")&&c.index()==0).findFirst().orElseThrow();
        var jaw=cubes.stream().filter(c->c.joint().equals("head")&&c.index()==1).findFirst().orElseThrow();
        double depth=GuardStyleProof.overlap(GuardStyleProof.obb(neck),GuardStyleProof.obb(jaw));
        if(depth<=0)throw new AssertionError("Visible neck/jaw gap in actual rig");return depth;
    }
    static void verifyOrReuse(Path out)throws Exception{
        var cached=out.getParent().getParent().resolve("headless/rig-clearance-proof.json");
        if(Files.exists(cached)){
            var d=com.google.gson.JsonParser.parseString(Files.readString(cached)).getAsJsonObject();
            if(d.get("modelDevClassSha256").getAsString().equals(GuardStyleProof.classSha())&&d.get("actualJavaPoseSamples").getAsInt()==13545&&d.get("finalOverlappingPairs").getAsInt()==0){Files.copy(cached,out.resolve("rig-clearance-proof.json"),StandardCopyOption.REPLACE_EXISTING);return;}
        }
        verify(out);
    }
    static void verify(Path out)throws Exception{
        var a=new DynastyCharacterModel<Mob>(DynastyCharacterModel.Role.GUARD);var b=new LegacyGuardStyleModel<Mob>(LegacyGuardStyleModel.Role.GUARD);
        Set<String> allowed=new HashSet<>();for(String n:List.of("head","right_shoulder","left_shoulder"))subtree(GuardStyleClientQa.joint(a.root,n),allowed);
        if(a.boxCount()!=166||b.boxCount()!=166||!a.jointNames().equals(b.jointNames())||a.jointNames().size()!=72)throw new AssertionError("Rig budget/identity changed");
        int poses=0;long pairs=0;
        for(int death=0;death<=20;death++)for(int amount=0;amount<=4;amount++)for(int phase=0;phase<=128;phase++){
            float limb=(float)(phase*Math.PI*2/128/.64),stride=amount*.25f;
            a.pose(limb,stride,phase,0,0,0,0,death,0,phase%3,false);b.pose(limb,stride,phase,0,0,0,0,death,0,phase%3,false);
            var x=GuardStyleProof.cubes(a);var y=cubes(b);equal(x,y,allowed);
            var check=GuardStyleProof.check(x);if(check.overlapping()!=0)throw new AssertionError("Skirt penetration: "+check);poses++;pairs+=check.pairs();
            if(a.root.x!=b.root.x||a.root.y!=b.root.y||a.root.z!=b.root.z||a.root.dx!=b.root.dx||a.root.dy!=b.root.dy||a.root.dz!=b.root.dz)throw new AssertionError("Root displacement");
        }
        int other=0;double headRatio=0,minNeckContact=Double.MAX_VALUE;
        for(int i=0;i<32;i++){
            a.pose(i*.4f,i%5*.25f,i, i%9*8-30,i%7*9-27,i%11*.1f,i%3==0?7:0,i%9==0?10:0,0,i%3,true);
            b.pose(i*.4f,i%5*.25f,i, i%9*8-30,i%7*9-27,i%11*.1f,i%3==0?7:0,i%9==0?10:0,0,i%3,true);
            var x=GuardStyleProof.cubes(a);var y=cubes(b);equal(x,y,allowed);
            minNeckContact=Math.min(minNeckContact,neckContact(x));
            var hx=x.stream().filter(c->c.joint().equals("head")&&c.index()==0).findFirst().orElseThrow();
            var hy=y.stream().filter(c->c.joint().equals("head")&&c.index()==0).findFirst().orElseThrow();
            for(int end:List.of(4,2,1)){headRatio=distance(hx.vertices()[end],hx.vertices()[0])/distance(hy.vertices()[end],hy.vertices()[0]);if(Math.abs(headRatio-.94)>0.00001)throw new AssertionError("Head proportions not uniformly preserved: "+headRatio);}
            if(Math.abs(GuardStyleClientQa.joint(a.root,"right_shoulder").x/joint(b.root,"right_shoulder").x-1.05)>.00001)throw new AssertionError("Shoulder ratio");
        }
        for(String role:List.of("ARCHER","REBEL","GENERAL")){
            var m=new DynastyCharacterModel<Mob>(DynastyCharacterModel.Role.valueOf(role));var old=new LegacyGuardStyleModel<Mob>(LegacyGuardStyleModel.Role.valueOf(role));
            for(int i=0;i<32;i++){
                m.pose(i*.37f,i%5*.25f,i*2,i%9*8-30,i%7*9-27,i%11*.1f,i%3==0?7:0,i%9==0?10:0,i%5*.25f,i%3,true);
                old.pose(i*.37f,i%5*.25f,i*2,i%9*8-30,i%7*9-27,i%11*.1f,i%3==0?7:0,i%9==0?10:0,i%5*.25f,i%3,true);
                var x=GuardStyleProof.cubes(m);var y=cubes(old);if(x.size()!=y.size())throw new AssertionError("Other role changed");
                for(int j=0;j<x.size();j++)if(!x.get(j).joint().equals(y.get(j).joint())||x.get(j).color()!=y.get(j).color()||!Arrays.deepEquals(x.get(j).vertices(),y.get(j).vertices()))throw new AssertionError("Other role changed: "+role);other++;
            }
        }
        var waist=GuardStyleClientQa.joint(a.root,"waist").boxes.get(0);var before=joint(b.root,"waist").boxes.get(0);
        if(Math.abs(waist.w()-4.95)>.00001||Math.abs(before.w()-5.05)>.00001)throw new AssertionError("Waist ratio");
        var d=new LinkedHashMap<String,Object>();d.put("modelDevClassSha256",GuardStyleProof.classSha());d.put("actualJavaPoseSamples",poses);d.put("obbPairs",pairs);d.put("finalOverlappingPairs",0);d.put("beforeCuboids",166);d.put("afterCuboids",166);d.put("joints",72);d.put("addedJoints",0);d.put("headScale",.94);d.put("headScaledAxesVerifiedPoseSamples",32);d.put("neckJawContactVerifiedPoseSamples",32);d.put("minNeckJawContactBlocks",minNeckContact);d.put("shoulderWidthBefore",10);d.put("shoulderWidthAfter",10.5);d.put("waistWidthBefore",5.05);d.put("waistWidthAfter",4.95);d.put("rootOffsetsUnchanged",true);d.put("skirtLegFootVerticesUnchanged",true);d.put("otherRolesExactPoseSamples",other);d.put("scope","Actual Java transforms; only intentional head-subtree/shoulder-subtrees and waist0 differ; no human gameplay or server formation claim");
        Files.createDirectories(out);Files.writeString(out.resolve("rig-clearance-proof.json"),new GsonBuilder().setPrettyPrinting().create().toJson(d));
    }
}
