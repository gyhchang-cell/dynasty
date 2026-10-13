package com.dynasty.client;

import com.google.gson.GsonBuilder;
import net.minecraft.client.model.geom.ModelPart;
import java.nio.file.*;
import java.util.*;

/** QA-only rest-pose export of our existing dragon; no copied third-party art. */
final class LegacyCuboidExport {
    static void dragon(Path output)throws Exception{
        Path path=output.resolve("dragon-emperor-rest-parts.json");
        if(Files.exists(path))return;
        var model=new DragonEmperorModel();
        var rootField=DragonEmperorModel.class.getDeclaredField("root");rootField.setAccessible(true);
        var nodes=new ArrayList<Map<String,Object>>();walk((ModelPart)rootField.get(model),"root",null,nodes);
        Files.writeString(path,new GsonBuilder().setPrettyPrinting().create().toJson(Map.of("coordinateSystem","vanilla Y-down, root ground at Y=24; radians","parts",nodes)));
    }
    private static void walk(ModelPart part,String name,String parent,List<Map<String,Object>> nodes)throws Exception{
        var pose=part.getInitialPose();var node=new LinkedHashMap<String,Object>();node.put("name",name);if(parent!=null)node.put("parent",parent);
        node.put("translation",List.of(pose.x,pose.y,pose.z));node.put("rotation",List.of(pose.xRot,pose.yRot,pose.zRot));
        var cubesField=ModelPart.class.getDeclaredField("cubes");cubesField.setAccessible(true);
        @SuppressWarnings("unchecked") var cubes=(List<ModelPart.Cube>)cubesField.get(part);var boxes=new ArrayList<Map<String,Object>>();
        for(var c:cubes)boxes.add(Map.of("min",List.of(c.minX,c.minY,c.minZ),"max",List.of(c.maxX,c.maxY,c.maxZ)));
        node.put("cubes",boxes);nodes.add(node);
        var field=ModelPart.class.getDeclaredField("children");field.setAccessible(true);
        @SuppressWarnings("unchecked") var children=(Map<String,ModelPart>)field.get(part);
        for(String key:new TreeSet<>(children.keySet()))walk(children.get(key),name+"__"+key,name,nodes);
    }
}
