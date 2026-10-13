package com.dynasty.client;

import com.google.gson.*;
import net.minecraft.core.Direction;
import software.bernie.geckolib.cache.object.*;
import software.bernie.geckolib.loading.json.raw.*;
import software.bernie.geckolib.loading.object.BakedModelFactory;
import java.nio.file.*;
import java.util.*;

/** Check every omitted face with actual GeckoLib 4.8.4 baked vertices. QA only. */
final class NativeCuboidFaces {
    static final Gson GSON=new GsonBuilder().registerTypeAdapter(Cube.class,Cube.deserializer())
        .registerTypeAdapter(ModelProperties.class,ModelProperties.deserializer())
        .registerTypeAdapter(UVUnion.class,UVUnion.deserializer()).registerTypeAdapter(UVFaces.class,UVFaces.deserializer())
        .registerTypeAdapter(FaceUV.class,FaceUV.deserializer()).create();
    static Map<String,Object> check(String id,BakedGeoModel model,Path out)throws Exception{
        var dir=out.getParent().getParent().resolve("face-cull-v1");
        var file=dir.resolve("before/"+id+".geo.json");
        if(!Files.exists(file))return Map.of("scope","No culling change for this entity");
        var source=JsonParser.parseString(Files.readString(file)).getAsJsonObject().getAsJsonArray("minecraft:geometry").get(0).getAsJsonObject();
        var properties=GSON.fromJson(source.get("description"),ModelProperties.class);
        var full=new HashMap<String,List<GeoCube>>();
        for(var element:source.getAsJsonArray("bones")){
            var bone=element.getAsJsonObject();String name=bone.get("name").getAsString();var cubes=new ArrayList<GeoCube>();
            if(bone.has("cubes"))for(var c:bone.getAsJsonArray("cubes"))cubes.add(BakedModelFactory.DEFAULT_FACTORY.constructCube(GSON.fromJson(c,Cube.class),properties,model.getBone(name).orElseThrow()));
            full.put(name,cubes);
        }
        var proof=JsonParser.parseString(Files.readString(dir.resolve("occlusion-proof.json"))).getAsJsonObject().getAsJsonObject(id);
        int checked=0,surviving=0;
        for(var element:proof.getAsJsonArray("removed")){
            var p=element.getAsJsonObject();String name=p.get("bone").getAsString();int index=p.get("cube").getAsInt(),other=p.get("occluderCube").getAsInt();
            String face=p.get("face").getAsString();var cube=full.get(name).get(index);var occluder=full.get(name).get(other);
            GeoQuad covered=null;int slot=-1;for(int i=0;i<cube.quads().length;i++)if(cube.quads()[i].direction().getSerializedName().equals(face)){covered=cube.quads()[i];slot=i;break;}
            if(covered==null||model.getBone(name).orElseThrow().getCubes().get(index).quads()[slot]!=null)throw new AssertionError("Face not omitted in actual native bake: "+id+" / "+p);
            double[] lo={1e9,1e9,1e9},hi={-1e9,-1e9,-1e9};
            for(var q:occluder.quads())for(var v:q.vertices())for(int k=0;k<3;k++){lo[k]=Math.min(lo[k],v.position().get(k));hi[k]=Math.max(hi[k],v.position().get(k));}
            var normal=covered.direction().step();int axis=covered.direction().getAxis()==Direction.Axis.X?0:covered.direction().getAxis()==Direction.Axis.Y?1:2;
            for(var v:covered.vertices())for(int k=0;k<3;k++){
                double probe=v.position().get(k)+normal.get(k)*.0001;
                if(probe<lo[k]-.000001||probe>hi[k]+.000001||(k==axis&&(probe<=lo[k]||probe>=hi[k])))throw new AssertionError("Omitted native face is externally exposed: "+id+" / "+p+" vertex="+v.position());
            }
            checked++;
        }
        for(var entry:full.entrySet()){
            var actual=model.getBone(entry.getKey()).orElseThrow().getCubes();if(actual.size()!=entry.getValue().size())throw new AssertionError("Cuboid count changed");
            for(int i=0;i<actual.size();i++)for(int slot=0;slot<6;slot++){
                var q=actual.get(i).quads()[slot];if(q==null)continue;var original=entry.getValue().get(i).quads()[slot];
                for(int v=0;v<4;v++)if(!q.vertices()[v].position().equals(original.vertices()[v].position())||q.vertices()[v].texU()!=original.vertices()[v].texU()||q.vertices()[v].texV()!=original.vertices()[v].texV())throw new AssertionError("Surviving baked vertex or UV changed");
                surviving++;
            }
        }
        if(checked!=proof.get("facesBefore").getAsInt()-proof.get("facesAfter").getAsInt()||surviving!=proof.get("facesAfter").getAsInt())throw new AssertionError("Native face proof mismatch");
        return Map.of("omittedFacesChecked",checked,"survivingFacesUnchanged",surviving,"method","Actual GeckoLib4.8.4 native baked vertices, outward probe inside same-bone occluder, all surviving positions/UV exact");
    }
}
