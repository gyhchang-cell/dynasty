package com.dynasty.client;

import com.dynasty.cod3.*;
import com.google.gson.*;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.renderer.texture.TextureAtlas;
import net.minecraft.core.*;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.Property;
import net.minecraft.world.phys.Vec3;
import org.joml.Vector3f;
import java.util.*;

/** Shared version-1 NBT-derived mesh; cached real vanilla atlas quads, no copied textures. */
final class ScenicBlockMirageMesh {
    private record Vertex(float x,float y,float z,float u,float v){}
    private record Face(Vertex[] vertices,Vector3f normal,float shade,Vec3 center){}
    private final ResourceLocation resource;
    private final MultiBufferSource.BufferSource buffers=MultiBufferSource.immediate(new BufferBuilder(1048576));
    private List<Face> faces,sorted;
    private Vec3 sortedCamera;
    private Object resources;
    ScenicBlockMirageMesh(String path){resource=ResourceLocation.fromNamespaceAndPath("dynasty",path);}
    @SuppressWarnings({"unchecked","rawtypes"}) private static BlockState state(JsonObject entry){
        String name=entry.has("Name")?entry.get("Name").getAsString():entry.get("name").getAsString();
        var block=BuiltInRegistries.BLOCK.getOptional(ResourceLocation.parse(name)).orElseThrow();var state=block.defaultBlockState();
        if(entry.has("Properties"))for(var p:entry.getAsJsonObject("Properties").entrySet()){
            Property property=block.getStateDefinition().getProperty(p.getKey());if(property==null)throw new IllegalArgumentException(p.getKey());
            state=state.setValue(property,(Comparable)property.getValue(p.getValue().getAsString()).orElseThrow());
        }
        return state;
    }
    private void bake(){
        var mc=Minecraft.getInstance();var manager=mc.getResourceManager();
        // Model instances change on reload even if the resource manager object is retained.
        Object marker=mc.getModelManager().getMissingModel();
        if(faces!=null&&resources==marker)return;
        var baked=new ArrayList<Face>();
        try(var reader=manager.openAsReader(resource)){
            var root=JsonParser.parseReader(reader).getAsJsonObject();if(root.get("version").getAsInt()!=1)throw new IllegalArgumentException("version");
            var palette=new ArrayList<BlockState>();for(var e:root.getAsJsonArray("palette"))palette.add(state(e.getAsJsonObject()));
            var pivot=root.getAsJsonArray("centerPivot");float px=pivot.get(0).getAsFloat(),py=pivot.get(1).getAsFloat(),pz=pivot.get(2).getAsFloat();
            var source=root.getAsJsonArray("exposedFaces");if(source.size()>12000)throw new IllegalArgumentException("face budget");
            for(var entry:source){
                var a=entry.getAsJsonArray();int index=a.get(3).getAsInt();var s=palette.get(index);
                var direction=Direction.byName(a.get(4).getAsString());if(direction==null)throw new IllegalArgumentException("face");
                var model=mc.getBlockRenderer().getBlockModel(s);float x=a.get(0).getAsFloat()-px,y=a.get(1).getAsFloat()-py,z=a.get(2).getAsFloat()-pz;
                for(var quad:model.getQuads(s,direction,RandomSource.create(0),net.minecraftforge.client.model.data.ModelData.EMPTY,null)){
                    int[] data=quad.getVertices();int stride=data.length/4;if(stride<6)throw new IllegalArgumentException("quad format");
                    var vertices=new Vertex[4];Vec3 center=Vec3.ZERO;
                    for(int i=0;i<4;i++){int j=i*stride;var v=new Vertex(x+Float.intBitsToFloat(data[j]),y+Float.intBitsToFloat(data[j+1]),z+Float.intBitsToFloat(data[j+2]),Float.intBitsToFloat(data[j+4]),Float.intBitsToFloat(data[j+5]));vertices[i]=v;center=center.add(v.x,v.y,v.z);}
                    var n=quad.getDirection().step();float shade=switch(direction){case UP->1;case DOWN->.55f;case NORTH,SOUTH->.78f;case WEST,EAST->.88f;};
                    baked.add(new Face(vertices,n,shade,center.scale(.25)));
                }
            }
            if(baked.size()!=source.size())throw new IllegalArgumentException("Full-cube face contract mismatch "+baked.size()+"/"+source.size());
        }catch(Exception failure){throw new IllegalStateException("Cannot bake scenic block mesh",failure);}
        faces=List.copyOf(baked);sorted=new ArrayList<>(faces);sortedCamera=null;resources=marker;
    }

    int render(PoseStack pose,Vec3 localCamera,float alpha,float red,float green,float blue){
        bake();
        if(sortedCamera==null||localCamera.distanceToSqr(sortedCamera)>4){sorted.sort(Comparator.comparingDouble((Face f)->f.center.distanceToSqr(localCamera)).reversed());sortedCamera=localCamera;}
        try{
            var consumer=buffers.getBuffer(ScenicMirageRenderType.TYPE);var matrix=pose.last().pose();var normals=pose.last().normal();
            for(var face:sorted)for(var v:face.vertices)consumer.vertex(matrix,v.x,v.y,v.z).color(face.shade*red,face.shade*green,face.shade*blue,alpha).uv(v.u,v.v).overlayCoords(OverlayTexture.NO_OVERLAY).uv2(15728880).normal(normals,face.normal.x,face.normal.y,face.normal.z).endVertex();
            return sorted.size();
        }finally{buffers.endBatch();}
    }
}
