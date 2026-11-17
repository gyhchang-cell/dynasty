package com.dynasty.client;
import com.google.gson.*;
import com.mojang.blaze3d.vertex.*;
import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import java.util.*;

/** Bounded original ghost flames, anchored to actual supported froglight blocks; no world light writes. */
final class ScenicGhostMarketLights {
    private static final BufferBuilder BUFFER=new BufferBuilder(32768);
    private static List<Vec3> centers;private static Object marker;
    static void clear(){centers=null;marker=null;}
    private static List<Vec3> centers(){
        var mc=Minecraft.getInstance();var current=mc.getModelManager().getMissingModel();if(centers!=null&&marker==current)return centers;
        var result=new ArrayList<Vec3>();
        try(var reader=mc.getResourceManager().openAsReader(ResourceLocation.fromNamespaceAndPath("dynasty","scenic/ghost_market.json"))){
            var root=JsonParser.parseReader(reader).getAsJsonObject();var pivot=root.getAsJsonArray("centerPivot");var palette=root.getAsJsonArray("palette");
            for(var e:root.getAsJsonArray("blocks")){var b=e.getAsJsonArray();if(palette.get(b.get(3).getAsInt()).getAsJsonObject().get("Name").getAsString().equals("minecraft:verdant_froglight"))result.add(new Vec3(b.get(0).getAsDouble()+.5-pivot.get(0).getAsDouble(),b.get(1).getAsDouble()+.5-pivot.get(1).getAsDouble(),b.get(2).getAsDouble()+.5-pivot.get(2).getAsDouble()));}
            if(result.size()!=12)throw new IllegalStateException("Expected twelve actual lamp anchors");
        }catch(Exception e){throw new IllegalStateException("Cannot load ghost market lamp anchors",e);}
        centers=List.copyOf(result);marker=current;return centers;
    }
    private static void quad(Matrix4f matrix,Vec3 at,Vec3 right,double w,double h,int color,float alpha){
        var r=right.scale(w);var u=new Vec3(0,h,0);var a=at.subtract(r).subtract(u);var b=at.add(r).subtract(u);var c=at.add(r).add(u);var d=at.subtract(r).add(u);
        for(var p:List.of(a,b,c,a,c,d))BUFFER.vertex(matrix,(float)p.x,(float)p.y,(float)p.z).color(color>>16&255,color>>8&255,color&255,Math.round(alpha*255)).endVertex();
    }
    static int render(PoseStack pose,Vec3 camera,double age,float alpha,boolean minimal,double distance){
        var points=centers();boolean drawing=false;int count=0;
        try{
            RenderSystem.setShader(GameRenderer::getPositionColorShader);RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();RenderSystem.enableDepthTest();RenderSystem.depthMask(false);RenderSystem.disableCull();
            BUFFER.begin(VertexFormat.Mode.TRIANGLES,DefaultVertexFormat.POSITION_COLOR);drawing=true;var matrix=pose.last().pose();
            for(int i=0;i<points.size();i++){
                var at=points.get(i).add(0,.32+.08*Math.sin(age*.055+i*1.7),0);var right=camera.subtract(at).cross(new Vec3(0,1,0)).normalize();if(right.lengthSqr()<1e-8)right=new Vec3(1,0,0);
                quad(matrix,at,right,.20,.34,0x62C8B9,alpha*.65f);quad(matrix,at.add(0,.04,0),right,.08,.20,0xCBE6CE,alpha);count+=2;
                if(!minimal){quad(matrix,at.add(0,-.30,0),right,.34,.08,0x62C8B9,alpha*.22f);count++;}
                // Thin, local mist belongs only to the near market; it never changes the global fog.
                if(!minimal&&distance<96){quad(matrix,at.add(0,-1,0),right,1.1,.16,0xA8B9B0,alpha*.04f);count++;}
            }
            BufferUploader.drawWithShader(BUFFER.end());drawing=false;return count;
        }finally{if(drawing)BUFFER.discard();}
    }
    private ScenicGhostMarketLights(){}
}
