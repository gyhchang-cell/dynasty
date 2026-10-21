package com.dynasty.client;

import com.dynasty.Dynasty;
import com.dynasty.cod3.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/** Actual waterline inversion, drawn before translucent water so its real surface occludes naturally. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID,value=Dist.CLIENT)
final class ScenicDragonPalaceRenderer {
    private record Check(long tick,boolean valid){}
    private static final Map<Cod3VisualPacket,Check> CHECKS=new HashMap<>();
    private static final ScenicBlockMirageMesh MESH=new ScenicBlockMirageMesh("scenic/dragon_palace_mirage.json");
    private static ClientLevel world;
    static int lastDrawnFaces;
    static void clear(){CHECKS.clear();world=null;lastDrawnFaces=0;}
    static boolean valid(ClientLevel l,Cod3VisualPacket p){
        if(world!=l){clear();world=l;}
        if(!ScenicDragonPalaceSite.dimension(l))return false;
        var old=CHECKS.get(p);long now=l.getGameTime();
        if(old==null||now<old.tick()||now-old.tick()>=20){old=new Check(now,ScenicDragonPalaceSite.valid(l,p.origin()));CHECKS.put(p,old);}
        return old.valid();
    }
    @SubscribeEvent public static void render(RenderLevelStageEvent e){
        if(e.getStage()!=RenderLevelStageEvent.Stage.AFTER_BLOCK_ENTITIES)return;
        lastDrawnFaces=0;var active=Cod3VfxRenderer.scenicPackets();CHECKS.keySet().retainAll(active);var l=Minecraft.getInstance().level;if(l==null)return;
        Vec3 camera=e.getCamera().getPosition();
        var p=active.stream().filter(v->v.sequence().equals("scenic_17")&&valid(l,v)).min(Comparator.comparingDouble(v->v.origin().distanceToSqr(camera))).orElse(null);if(p==null)return;
        double age=l.getGameTime()-p.start()+e.getPartialTick();if(age<0||age>=p.duration())return;
        float alpha=(float)ScenicDragonPalaceSite.alpha(age,p.duration(),p.origin().distanceTo(camera));if(alpha<=0)return;
        var local=camera.subtract(p.origin());var pose=e.getPoseStack();pose.pushPose();
        try(ImperialRenderState state=new ImperialRenderState()){
            pose.translate(p.origin().x-camera.x,p.origin().y-camera.y,p.origin().z-camera.z);
            // Data remains upright. Mirror position AND normal matrix exactly once about the source-water plane.
            // NO_CULL handles the reversed winding; depth remains LEQUAL, without global fog changes.
            // PoseStack.scale uses a signed inverse-cube-root normalization for negative determinant.
            // Apply the reflection matrices directly: the inverse transpose of diag(1,-1,1) is itself.
            pose.last().pose().scale(1,-1,1);
            pose.last().normal().scale(1,-1,1);
            lastDrawnFaces=MESH.render(pose,new Vec3(local.x,-local.y,local.z),alpha,.76f,.92f,1);
        }finally{pose.popPose();}
    }
    private ScenicDragonPalaceRenderer(){}
}
