package com.dynasty.client;

import com.dynasty.client.character.DynastyCharacterModel;
import com.dynasty.client.character.LegacyGuardModel;
import com.google.gson.GsonBuilder;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.world.entity.Mob;
import org.joml.Vector3f;
import java.nio.file.*;
import java.util.*;

/** Independent OBB separation-axis acceptance using actual rendered Java cube transforms. */
final class GuardStyleProof {
    record Cube(String joint,int index,int color,double[][] vertices) {}
    record Obb(double[] center,double[][] axis,double[] half) {}
    static List<Cube> cubes(DynastyCharacterModel<?> model) {var out=new ArrayList<Cube>();collect(model.root,out);return out;}
    static void collect(DynastyCharacterModel.Joint j,List<Cube> out) {
        if(!j.visible)return;var stack=new PoseStack();j.path(stack);int index=0;
        for(var b:j.boxes){double[][] v=new double[8][3];int k=0;for(int x=0;x<2;x++)for(int y=0;y<2;y++)for(int z=0;z<2;z++){
            var p=stack.last().pose().transformPosition(new Vector3f((b.x()+x*b.w())/16,(b.y()+y*b.h())/16,(b.z()+z*b.d())/16));v[k++]=new double[]{p.x,p.y,p.z};}
            out.add(new Cube(j.name,index++,b.color(),v));}
        for(var child:j.children)collect(child,out);
    }
    static List<Cube> cubes(LegacyGuardModel<?> model) {var out=new ArrayList<Cube>();collect(model.root,out);return out;}
    static void collect(LegacyGuardModel.Joint j,List<Cube> out) {
        if(!j.visible)return;var stack=new PoseStack();j.path(stack);int index=0;
        for(var b:j.boxes){double[][] v=new double[8][3];int k=0;for(int x=0;x<2;x++)for(int y=0;y<2;y++)for(int z=0;z<2;z++){
            var p=stack.last().pose().transformPosition(new Vector3f((b.x()+x*b.w())/16,(b.y()+y*b.h())/16,(b.z()+z*b.d())/16));v[k++]=new double[]{p.x,p.y,p.z};}
            out.add(new Cube(j.name,index++,b.color(),v));}
        for(var child:j.children)collect(child,out);
    }
    static Obb obb(Cube c){var center=new double[3];for(var v:c.vertices)for(int i=0;i<3;i++)center[i]+=v[i]/8;double[][] axis=new double[3][3];double[] half=new double[3];int[] end={4,2,1};
        for(int i=0;i<3;i++){axis[i]=sub(c.vertices[end[i]],c.vertices[0]);double length=Math.sqrt(dot(axis[i],axis[i]));half[i]=length/2;for(int k=0;k<3;k++)axis[i][k]/=length;}return new Obb(center,axis,half);}
    static double[] sub(double[] a,double[] b){return new double[]{a[0]-b[0],a[1]-b[1],a[2]-b[2]};}
    static double dot(double[] a,double[] b){return a[0]*b[0]+a[1]*b[1]+a[2]*b[2];}
    static double[] cross(double[] a,double[] b){return new double[]{a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]};}
    static double overlap(Obb a,Obb b){
        var d=sub(b.center,a.center);var axes=new ArrayList<double[]>(15);axes.addAll(Arrays.asList(a.axis));axes.addAll(Arrays.asList(b.axis));for(var x:a.axis)for(var y:b.axis)axes.add(cross(x,y));double smallest=Double.MAX_VALUE;
        for(var axis:axes){double length=Math.sqrt(dot(axis,axis));if(length<1e-7)continue;double ra=0,rb=0;for(int i=0;i<3;i++){ra+=Math.abs(dot(a.axis[i],axis))*a.half[i];rb+=Math.abs(dot(b.axis[i],axis))*b.half[i];}
            double depth=(ra+rb-Math.abs(dot(d,axis)))/length;if(depth<=.000001)return 0;smallest=Math.min(smallest,depth);}
        return smallest;
    }
    record Check(int pairs,int overlapping,double maxDepthBlocks,String worst) {}
    static Check check(List<Cube> cubes){var skirts=new ArrayList<Cube>();var legs=new ArrayList<Cube>();for(var c:cubes){if(c.joint.startsWith("skirt"))skirts.add(c);if(c.joint.matches("(left|right)_(thigh|knee|shin|foot)"))legs.add(c);}
        int pairs=0,hits=0;double max=0;String worst="";var boxes=new IdentityHashMap<Cube,Obb>();for(var c:skirts)boxes.put(c,obb(c));for(var c:legs)boxes.put(c,obb(c));
        for(var a:skirts)for(var b:legs){pairs++;double depth=overlap(boxes.get(a),boxes.get(b));if(depth>0){hits++;if(depth>max){max=depth;worst=a.joint+":"+a.index+" / "+b.joint+":"+b.index;}}}return new Check(pairs,hits,max,worst);
    }
    static String classSha()throws Exception{try(var in=DynastyCharacterModel.class.getResourceAsStream("DynastyCharacterModel.class")){return java.util.HexFormat.of().formatHex(java.security.MessageDigest.getInstance("SHA-256").digest(in.readAllBytes()));}}
    static void verifyOrReuse(Path out)throws Exception{
        var cached=out.getParent().getParent().resolve("headless/rig-clearance-proof.json");
        if(Files.exists(cached)){
            var report=com.google.gson.JsonParser.parseString(Files.readString(cached)).getAsJsonObject();
            if(report.get("modelDevClassSha256").getAsString().equals(classSha())&&report.get("actualJavaPoseSamples").getAsInt()==13545&&report.get("finalOverlappingPairs").getAsInt()==0){
                Files.copy(cached,out.resolve("rig-clearance-proof.json"),StandardCopyOption.REPLACE_EXISTING);return;
            }
        }
        verify(out);
    }
    static void verify(Path out)throws Exception {
        var model=new DynastyCharacterModel<Mob>(DynastyCharacterModel.Role.GUARD);var old=new LegacyGuardModel<Mob>(LegacyGuardModel.Role.GUARD);
        int poses=0,beforeHits=0;long pairs=0;double beforeWorst=0;int nonGuardPoses=0;
        // Dense phase samples at five actual stride amplitudes, including folded death knees.
        for(int death=0;death<=20;death++)for(int amount=0;amount<=4;amount++)for(int phase=0;phase<=128;phase++){
            float limb=(float)(phase*Math.PI*2/128/.64),stride=amount*.25f;model.pose(limb,stride,phase,0,0,0,0,death,0,phase%3,false);old.pose(limb,stride,phase,0,0,0,0,death,0,phase%3,false);
            var actual=check(cubes(model));var original=check(cubes(old));poses++;pairs+=actual.pairs;beforeHits+=original.overlapping;beforeWorst=Math.max(beforeWorst,original.maxDepthBlocks);
            if(actual.overlapping>0)throw new AssertionError("Guard skirt penetrates leg: phase="+phase+" amount="+amount+" death="+death+" "+actual);
            if(model.root.x!=old.root.x||model.root.y!=old.root.y||model.root.z!=old.root.z||model.root.dx!=old.root.dx||model.root.dy!=old.root.dy||model.root.dz!=old.root.dz)throw new AssertionError("Root displacement changed");
        }
        if(beforeHits==0)throw new AssertionError("Baseline penetration not reproduced");
        for(String role:List.of("ARCHER","REBEL","GENERAL")){
            var a=new DynastyCharacterModel<Mob>(DynastyCharacterModel.Role.valueOf(role));var b=new LegacyGuardModel<Mob>(LegacyGuardModel.Role.valueOf(role));
            for(int i=0;i<32;i++){
                a.pose(i*.37f,i%5*.25f,i*2,i%9*8-30,i%7*9-27,i%11*.1f,i%3==0?7:0,i%9==0?10:0,i%5*.25f,i%3,true);
                b.pose(i*.37f,i%5*.25f,i*2,i%9*8-30,i%7*9-27,i%11*.1f,i%3==0?7:0,i%9==0?10:0,i%5*.25f,i%3,true);
                var x=cubes(a);var y=cubes(b);if(x.size()!=y.size())throw new AssertionError("Other role geometry changed: "+role);
                for(int j=0;j<x.size();j++)if(!x.get(j).joint.equals(y.get(j).joint)||x.get(j).color!=y.get(j).color||!Arrays.deepEquals(x.get(j).vertices,y.get(j).vertices))throw new AssertionError("Other role changed: "+role+" "+i+" "+j);nonGuardPoses++;
            }
        }
        // Guard cubes outside the skirt remain byte-for-byte coordinate/color matches while alive.
        for(int sample=0;sample<32;sample++){
            model.pose(sample*.4f,sample%5*.25f,sample,0,0,sample%11*.1f,sample%7==0?7:0,0,0,sample%3,true);
            old.pose(sample*.4f,sample%5*.25f,sample,0,0,sample%11*.1f,sample%7==0?7:0,0,0,sample%3,true);
            var original=cubes(old).stream().filter(c->!c.joint.startsWith("skirt")).toList();var current=cubes(model).stream().filter(c->!c.joint.startsWith("skirt")&&!c.joint.equals("guard_bolt_case")&&!c.joint.equals("guard_spear")).toList();
            if(original.size()!=current.size())throw new AssertionError("Guard non-skirt cube removed");
            for(int i=0;i<original.size();i++)if(!original.get(i).joint.equals(current.get(i).joint)||original.get(i).color!=current.get(i).color||!Arrays.deepEquals(original.get(i).vertices,current.get(i).vertices))throw new AssertionError("Guard torso/limbs changed while alive");
        }
        int beforeBoxes=old.boxCount();if(model.boxCount()!=beforeBoxes+13||model.jointNames().size()!=old.jointNames().size()+2)throw new AssertionError("Guard light-modification budget");
        for(String name:old.jointNames())if(!model.jointNames().contains(name))throw new AssertionError("Original bone removed: "+name);
        for(int i=0;i<32;i++){
            model.pose(i,1,i,0,0,0,0,0,0,i%3,false);
            if(GuardStyleClientQa.joint(model.root,"guard_bolt_case").visible)throw new AssertionError("Bolt case retained after reset");model.poseHeldCrossbow();
            if(!GuardStyleClientQa.joint(model.root,"guard_bolt_case").visible)throw new AssertionError("Bolt case missing for crossbow");
        }
        var report=new LinkedHashMap<String,Object>();report.put("modelDevClassSha256",classSha());report.put("actualJavaPoseSamples",poses);report.put("obbPairs",pairs);report.put("finalOverlappingPairs",0);report.put("baselineOverlappingPairs",beforeHits);report.put("baselineWorstOverlapBlocks",beforeWorst);report.put("otherRolesExactPoseSamples",nonGuardPoses);report.put("beforeCuboids",beforeBoxes);report.put("afterCuboids",model.boxCount());report.put("addedJoints",2);report.put("allOldJointsRetained",true);report.put("rootOffsetsUnchanged",true);report.put("scope","Actual Java cube OBBs, all skirt fabric/armor against both thighs/knees/shins/feet; deterministic geometry acceptance, separate native movement required.");
        Files.writeString(out.resolve("rig-clearance-proof.json"),new GsonBuilder().setPrettyPrinting().create().toJson(report));
    }
    static void snapshot(Path out,String label,DynastyCharacterModel<?> model)throws Exception{Files.writeString(out.resolve(label+"-mesh.json"),new GsonBuilder().setPrettyPrinting().create().toJson(Map.of("source","Actual rendered Java rig; body cubes only, held item renderer checked in native frames separately","cubes",cubes(model))));}
}
