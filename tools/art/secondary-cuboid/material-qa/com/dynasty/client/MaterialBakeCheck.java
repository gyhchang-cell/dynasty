package com.dynasty.client;

import com.google.gson.*;
import software.bernie.geckolib.cache.object.GeoBone;
import software.bernie.geckolib.loading.json.raw.*;
import software.bernie.geckolib.loading.object.BakedModelFactory;
import java.nio.file.*;
import java.util.*;

/** Real GeckoLib 4.8.4 face baking without GLFW; NOT a game/client acceptance. */
public final class MaterialBakeCheck {
    public static void main(String[] args)throws Exception {
        var gson=new GsonBuilder().registerTypeAdapter(Cube.class,Cube.deserializer())
            .registerTypeAdapter(ModelProperties.class,ModelProperties.deserializer())
            .registerTypeAdapter(UVUnion.class,UVUnion.deserializer())
            .registerTypeAdapter(UVFaces.class,UVFaces.deserializer())
            .registerTypeAdapter(FaceUV.class,FaceUV.deserializer()).create();
        int total=0;
        for(String id:System.getProperty("dynasty.materialBakeIds","clockwork_rat,wooden_magpie,stone_sprite").split(",")) {
            var file=Path.of(args[0],"assets/dynasty/geo/secondary/"+id+".geo.json");
            var model=JsonParser.parseString(Files.readString(file)).getAsJsonObject()
                .getAsJsonArray("minecraft:geometry").get(0).getAsJsonObject();
            var properties=gson.fromJson(model.get("description"),ModelProperties.class);
            int width=model.getAsJsonObject("description").get("texture_width").getAsInt();
            int height=model.getAsJsonObject("description").get("texture_height").getAsInt();
            var bones=new HashMap<String,GeoBone>();int faces=0,cubes=0;
            for(var element:model.getAsJsonArray("bones")) {
                var raw=element.getAsJsonObject();String name=raw.get("name").getAsString();
                var parent=raw.has("parent")?bones.get(raw.get("parent").getAsString()):null;
                var bone=new GeoBone(parent,name,false,0.0,false,false);bones.put(name,bone);
                var pivot=raw.getAsJsonArray("pivot");bone.setPivotX(-pivot.get(0).getAsFloat());
                bone.setPivotY(pivot.get(1).getAsFloat());bone.setPivotZ(pivot.get(2).getAsFloat());
                if(!raw.has("cubes"))continue;
                for(var c:raw.getAsJsonArray("cubes")) {
                    var cube=BakedModelFactory.DEFAULT_FACTORY.constructCube(gson.fromJson(c,Cube.class),properties,bone);
                    cubes++;
                    for(var quad:cube.quads()) {
                        if(quad==null||quad.vertices().length!=4)throw new AssertionError(id+" missing quad");
                        String side=quad.direction().getSerializedName();
                        var island=c.getAsJsonObject().getAsJsonObject("uv").getAsJsonObject(side);
                        var uv=island.getAsJsonArray("uv");var size=island.getAsJsonArray("uv_size");
                        double loU=uv.get(0).getAsDouble()/width,hiU=(uv.get(0).getAsDouble()+size.get(0).getAsDouble())/width;
                        double loV=uv.get(1).getAsDouble()/height,hiV=(uv.get(1).getAsDouble()+size.get(1).getAsDouble())/height;
                        for(var vertex:quad.vertices()) {
                            if(!Double.isFinite(vertex.position().x+vertex.position().y+vertex.position().z)
                                ||vertex.texU()<loU-.00001||vertex.texU()>hiU+.00001
                                ||vertex.texV()<loV-.00001||vertex.texV()>hiV+.00001)
                                throw new AssertionError(id+" bad native UV/vertex "+side+" / "+vertex);
                        }
                        faces++;
                    }
                }
            }
            if(faces!=cubes*6)throw new AssertionError("Face count "+id);
            total+=faces;System.out.println("PASS "+id+" GeckoLib4.8.4 baked "+cubes+" cubes / "+faces+" pixel-atlas faces");
        }
        System.out.println("PASS "+total+" native baked faces; no graphical or gameplay claim");
    }
}
