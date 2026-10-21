package com.dynasty.client;

import com.dynasty.cod3.*;
import com.google.gson.JsonParser;
import com.mojang.blaze3d.vertex.BufferBuilder;
import net.minecraft.client.Minecraft;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.*;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterClientReloadListenersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import java.io.InputStreamReader;
import java.util.*;

/** The static tree is actual blocks. This only draws sparks at its exported bud coordinates. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public final class ScenicFireTreeRenderer {
    private record Layout(List<ScenicAurora.Point> buds,Vec3 sound){}
    private static volatile Layout layout=new Layout(List.of(),new Vec3(24.5,26,24.5));
    @SubscribeEvent public static void register(RegisterClientReloadListenersEvent event){
        event.registerReloadListener(new SimplePreparableReloadListener<Layout>(){
            @Override protected Layout prepare(ResourceManager manager,ProfilerFiller profiler){
                try(var stream=manager.open(new ResourceLocation("dynasty","scenic/fire_tree.json"));var reader=new InputStreamReader(stream,java.nio.charset.StandardCharsets.UTF_8)){
                    var json=JsonParser.parseReader(reader).getAsJsonObject();var list=new ArrayList<ScenicAurora.Point>();
                    for(var value:json.getAsJsonArray("bud_centers")){var p=value.getAsJsonArray();double x=p.get(0).getAsDouble(),y=p.get(1).getAsDouble(),z=p.get(2).getAsDouble();
                        if(!Double.isFinite(x+y+z)||x<0||x>=47||y<0||y>=43||z<0||z>=47)throw new IllegalArgumentException("Invalid fire-tree bud");list.add(new ScenicAurora.Point(x,y,z));}
                    if(list.isEmpty()||list.size()>64)throw new IllegalArgumentException("Invalid fire-tree bud count");
                    var p=json.getAsJsonArray("effect_anchor");return new Layout(List.copyOf(list),new Vec3(p.get(0).getAsDouble(),p.get(1).getAsDouble(),p.get(2).getAsDouble()));
                }catch(Exception e){throw new IllegalStateException("Invalid fire-tree visual layout",e);}
            }
            @Override protected void apply(Layout loaded,ResourceManager manager,ProfilerFiller profiler){layout=loaded;}
        });
    }
    static Vec3 soundPosition(Cod3VisualPacket packet){return packet.origin().add(layout.sound);}
    static boolean hasBody(Cod3VisualPacket packet){
        var level=Minecraft.getInstance().level;var at=net.minecraft.core.BlockPos.containing(packet.origin().add(24,8,22));
        return level!=null&&level.hasChunkAt(at)&&level.getBlockState(at).is(net.minecraft.world.level.block.Blocks.SHROOMLIGHT);
    }
    static void draw(BufferBuilder buffer,Matrix4f matrix,Cod3VisualPacket packet,Vec3 camera,boolean low,double partial){
        var level=Minecraft.getInstance().level;if(level==null)return;
        double distance=soundPosition(packet).distanceTo(camera),visibility=ScenicFireTreeLight.visibility(level.getDayTime(),level.getRainLevel((float)partial));
        var candidates=ScenicFireTreeLight.mesh(packet.seed(),level.getGameTime()+partial,distance,low,visibility,layout.buds);
        var mesh=new ArrayList<ScenicAurora.Quad>();
        for(int i=0;i<candidates.size();i++){
            var bud=layout.buds.get((i/2)%layout.buds.size());var at=net.minecraft.core.BlockPos.containing(packet.origin().add(bud.x(),bud.y(),bud.z()));
            if(!level.hasChunkAt(at))continue;var state=level.getBlockState(at);
            if(state.is(net.minecraft.world.level.block.Blocks.OCHRE_FROGLIGHT)||state.is(net.minecraft.world.level.block.Blocks.SHROOMLIGHT))mesh.add(candidates.get(i));
        }
        mesh.sort(Comparator.comparingDouble((ScenicAurora.Quad q)->point(q.a(),packet.origin()).distanceToSqr(camera)).reversed());
        for(var quad:mesh){
            // Tiny sparks remain visible at walking distance; large sky-surface near fades do not apply.
            double alpha=quad.alpha()*Math.max(0,Math.min(1,(point(quad.a(),packet.origin()).distanceTo(camera)-.5)));
            if(alpha<=0)continue;
            for(var local:List.of(quad.a(),quad.b(),quad.c(),quad.a(),quad.c(),quad.d())){
                var world=point(local,packet.origin());buffer.vertex(matrix,(float)world.x,(float)world.y,(float)world.z)
                    .color(quad.color()>>16&255,quad.color()>>8&255,quad.color()&255,(int)(alpha*255)).endVertex();
            }
        }
    }
    private static Vec3 point(ScenicAurora.Point point,Vec3 origin){return origin.add(point.x(),point.y(),point.z());}
    private ScenicFireTreeRenderer(){}
}
