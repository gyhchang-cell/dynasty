package com.dynasty.client;

import com.dynasty.*;
import com.dynasty.network.*;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.*;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import java.util.*;

/** Six bounded, depth-tested meshes. No client damage and no particle clouds covering the target. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID,value=Dist.CLIENT)
public final class EdictRenderer {
    private static final BufferBuilder BUFFER=new BufferBuilder(65536);
    private static final Map<UUID,EdictVisualPacket> CASTS=new LinkedHashMap<>();
    private static net.minecraft.client.multiplayer.ClientLevel world;
    static void reset(){CASTS.clear();world=null;}
    private static void clean(){var current=Minecraft.getInstance().level;if(world!=current){CASTS.clear();world=current;}if(world!=null)CASTS.values().removeIf(p->world.getGameTime()-p.born()>100);}
    public static void receive(EdictVisualPacket p) {
        clean();if(world==null||!p.valid()||!world.dimension().location().toString().equals(p.dimension()))return;
        if(p.kind()==-1){CASTS.remove(p.id());return;}
        if(p.kind()<0||p.kind()>5||!Double.isFinite(p.origin().lengthSqr()+p.end().lengthSqr())||p.origin().distanceToSqr(p.end())>1024)return;
        CASTS.put(p.id(),p);while(CASTS.size()>24)CASTS.remove(CASTS.keySet().iterator().next());
    }
    /** Resolve the actual holder, never the nearest player or the local viewer. */
    static EdictVisualPacket heldCast(net.minecraft.world.item.ItemStack stack){
        clean();if(world==null)return null;
        EdictVisualPacket newest=null;
        for(var cast:CASTS.values()){
            var holder=world.getEntity(cast.ownerId());
            if(!(holder instanceof net.minecraft.world.entity.player.Player p)||!p.getUUID().equals(cast.ownerUuid())||!p.isAlive()
                    ||p.isSpectator()||p.getMainHandItem()!=stack||world.getGameTime()-cast.born()>EdictSpells.WINDUP[cast.kind()]+16)continue;
            if(newest==null||newest.born()<cast.born())newest=cast;
        }
        return newest;
    }
    @SubscribeEvent public static void input(InputEvent.InteractionKeyMappingTriggered e) {
        var p=Minecraft.getInstance().player;
        if(e.isAttack()&&p!=null&&EdictSpells.weapon(p.getMainHandItem())&&Minecraft.getInstance().screen==null) {
            e.setCanceled(true);e.setSwingHand(true);DynastyNetwork.CHANNEL.sendToServer(new EdictCastPacket());
        }
    }
    @SubscribeEvent public static void render(RenderLevelStageEvent e) {
        if(e.getStage()!=RenderLevelStageEvent.Stage.AFTER_PARTICLES)return;clean();
        if(world==null)return;
        var camera=e.getCamera().getPosition();var matrix=e.getPoseStack().last().pose();
        try(var state=new ImperialRenderState()) {
            RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();RenderSystem.enableDepthTest();RenderSystem.depthMask(false);RenderSystem.disableCull();
            RenderSystem.setShader(GameRenderer::getPositionColorShader);BUFFER.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR);
            for(var p:CASTS.values()) {
                if(p.ownerId()>=0){var owner=world.getEntity(p.ownerId());if(owner==null||!owner.isAlive()||!owner.getUUID().equals(p.ownerUuid()))continue;}
                double age=world.getGameTime()+e.getPartialTick()-p.born(),windup=EdictSpells.WINDUP[p.kind()];
                if(age<0||age>windup+12||p.end().distanceToSqr(camera)>64*64)continue;
                double phase=Math.min(1,age/windup),alpha=.8*Math.min(1,age/3)*Math.min(1,(windup+12-age)/12);
                Vec3 origin=p.kind()==0?p.origin().lerp(p.end(),phase):p.end();
                Vec3 forward=p.end().subtract(p.origin()).normalize(),right=forward.cross(new Vec3(0,1,0)).normalize();
                if(right.lengthSqr()<.1)right=new Vec3(1,0,0);
                var mesh=new Mesh(matrix,camera,origin,right,forward,alpha);
                draw(mesh,p.kind(),phase,age);
            }
            armorAuras(matrix,camera,e.getPartialTick());
            BufferUploader.drawWithShader(BUFFER.end());
        } finally {if(BUFFER.building())BUFFER.end().release();}
    }
    private record Mesh(Matrix4f matrix,Vec3 camera,Vec3 center,Vec3 right,Vec3 forward,double alpha) {
        Vec3 point(double x,double y,double z){return center.add(right.scale(x)).add(0,y,0).add(forward.scale(z));}
        void line(double x,double y,double z,double a,double b,double c,double width,int color) {
            Vec3 from=point(x,y,z),to=point(a,b,c),normal=to.subtract(from).cross(camera.subtract(from)).normalize().scale(width*.5);
            face(from.add(normal),to.add(normal),to.subtract(normal),from.subtract(normal),color,alpha);
        }
        void face(Vec3 a,Vec3 b,Vec3 c,Vec3 d,int col,double opacity){for(var v:new Vec3[]{a,b,c,d}){var p=v.subtract(camera);BUFFER.vertex(matrix,(float)p.x,(float)p.y,(float)p.z).color((col>>16)&255,(col>>8)&255,col&255,(int)(255*Math.max(0,Math.min(1,opacity)))).endVertex();}}
        void panel(double x,double y,double z,double w,double h,int color){face(point(x-w,y-h,z),point(x+w,y-h,z),point(x+w,y+h,z),point(x-w,y+h,z),color,alpha*.35);}
    }
    private static void armorAuras(Matrix4f matrix,Vec3 camera,float partial) {
        var mc=Minecraft.getInstance();
        if(mc.player==null)return;
        int budget=8;
        for(var p:world.players().stream().sorted(java.util.Comparator.comparingDouble(v->v.distanceToSqr(camera))).toList()) {
            if(budget<=0)break;
            if(!p.isAlive()||p.isInvisibleTo(mc.player)||p.isSpectator()||p.distanceToSqr(camera)>28*28
                    ||p==mc.player&&mc.options.getCameraType().isFirstPerson())continue;
            String chest=DynastyTrinkets.idOf(p.getItemBySlot(net.minecraft.world.entity.EquipmentSlot.CHEST));
            if(chest==null)continue;
            int theme=chest.startsWith("taiyi_")||chest.startsWith("cinnabar_")?1:
                    chest.startsWith("ziwei_")||chest.startsWith("hongmeng_")?2:
                    chest.startsWith("disha_")||chest.startsWith("dark_iron_")?3:
                    chest.startsWith("sea_silk_")||chest.startsWith("draco_king_")?4:
                    chest.startsWith("tiangang_")||chest.startsWith("beidou_")?5:0;
            if(theme==0)continue;budget--;
            String family=chest.substring(0,chest.lastIndexOf('_'));
            int count=0;for(var piece:p.getArmorSlots()){String id=DynastyTrinkets.idOf(piece);if(id!=null&&id.startsWith(family+"_"))count++;}
            double yaw=Math.toRadians(p.yBodyRot),time=p.tickCount+partial;
            Vec3 forward=new Vec3(-Math.sin(yaw),0,Math.cos(yaw)),right=new Vec3(Math.cos(yaw),0,Math.sin(yaw));
            double alpha=count==4&&(p.hurtTime>0||p.isUsingItem()||p.tickCount%180<40)?.38:.16;
            var m=new Mesh(matrix,camera,p.getPosition(partial).add(0,1.1,0).subtract(forward.scale(.33)),right,forward,alpha);
            switch(theme) {
                case 1 -> {m.panel(0,0,0,.11,.32,0xffdd8b);m.line(0,-.24,-.01,0,.24,-.01,.013,0xffaa53);for(int side:new int[]{-1,1})m.line(side*.2,-.3,0,side*(.23+Math.sin(time*.015)*.025),.32,0,.01,0xffdb8b);}
                case 2 -> {for(int side:new int[]{-1,1}){m.line(side*.25,.25,0,side*.52,.55,0,.015,0xffcc72);m.line(side*.52,.55,0,side*.5,.1,0,.015,0xffcc72);m.line(side*.5,.1,0,side*.25,.25,0,.015,0xffcc72);}}
                case 3 -> {for(int i=0;i<4;i++){double y=-.35+i*.2;m.line(-.1,y,0,0,y+.1,0,.018,0x70a6b4);m.line(0,y+.1,0,.1,y,0,.018,0x70a6b4);}}
                case 4 -> {for(int side:new int[]{-1,1})for(int i=0;i<3;i++){double x=side*(.25+i*.13),y=.18+i*.06;m.line(x,y,0,x+side*.1,y+.13,0,.018,0x81e6ec);m.line(x+side*.1,y+.13,0,x+side*.18,y+.02,0,.012,0x81e6ec);}}
                case 5 -> {for(int side:new int[]{-1,1}){m.line(side*.28,.25,0,side*.4,.4,0,.014,0xbacfff);m.line(side*.4,.4,0,side*.34,.5,0,.014,0xbacfff);m.line(side*.34,.5,0,side*.57,.6,0,.014,0xbacfff);}}
            }
        }
    }

    private static void draw(Mesh m,int kind,double p,double age) {
        double scale=.3+.7*p;
        switch(kind) {
            case 0 -> { // Paper talisman with central split stroke; travels along the server's clipped ray.
                m.panel(0,0,0,.18,.42,0xffd884);
                m.line(-.15,.39,0,.15,.39,0,.025,0xff802c);m.line(0,.3,.005,0,-.28,.005,.03,0xe86125);
                for(int i=0;i<3;i++){double y=.17-i*.16;m.line(-.11,y,0,.11,y-.06,0,.022,0xe86125);}
                m.line(0,-.38,-.2,0,-.38,-.9,.022,0xffe9ab);
            }
            case 1 -> { // Three offset crescent ribbons, open at both ends.
                for(int k=0;k<3;k++)for(int i=0;i<24;i++) {
                    double a=-1.4+i*.11,b=a+.11,r=(1.1+k*.4)*scale;
                    m.line(Math.cos(a)*r,Math.sin(a)*r,k*.3,Math.cos(b)*r,Math.sin(b)*r,k*.3,.06*Math.sin(Math.PI*(i+1)/25),0x8af9de);
                }
            }
            case 2 -> { // Forked lightning grows downward; a narrow ground chevron marks the strike.
                for(int branch=-1;branch<=1;branch++)for(int i=0;i<7;i++) {
                    double x=(i%2==0?-.23:.23)+branch*i*.1,z=branch*.25;
                    m.line(x,4-i*.56,z,-x+branch*i*.18,4-(i+1)*.56,z,.045*scale,0xb2cfff);
                }
                m.line(-.6,.03,0,0,.03,-.5,.04,0x8aacff);m.line(0,.03,-.5,0.6,.03,0,.04,0x8aacff);
            }
            case 3 -> { // Four vertical binding slips linked by angular cords, leaving the middle open.
                for(int i=0;i<4;i++){double a=i*Math.PI/2,x=Math.cos(a)*1.7,z=Math.sin(a)*1.7;
                    m.panel(x,.4+scale,z,.16,.7*scale,0xc394ff);
                    double b=a+Math.PI/2;m.line(x,.12,z,Math.cos(b)*1.7,.12,Math.sin(b)*1.7,.025,0xa8b1ff);
                }
            }
            case 4 -> { // Folded shield, solid edge and faint surface instead of an opaque sphere.
                for(int side:new int[]{-1,1}) {
                    m.face(m.point(0,-.7,-.7),m.point(side*.9,.1,-.4),m.point(side*.75,1.1,-.4),m.point(0,1.45,-.7),0x91ffe0,m.alpha*.14);
                    m.line(0,-.7,-.7,side*.9,.1,-.4,.05,0x91ffe0);m.line(side*.9,.1,-.4,side*.75,1.1,-.4,.05,0x91ffe0);m.line(side*.75,1.1,-.4,0,1.45,-.7,.05,0x91ffe0);
                }
            }
            case 5 -> { // Cubic seal descends onto a square footprint; four corner teeth, no circular ring.
                double y=3*(1-p)+.4,r=scale*.8;
                for(int side:new int[]{-1,1}) {
                    m.line(-r,y,side*r,r,y,side*r,.08,0xffce69);m.line(side*r,y,-r,side*r,y,r,.08,0xffce69);
                    for(int other:new int[]{-1,1})m.line(side*r,y,other*r,side*r,y+.5,other*r,.065,0xffedb6);
                    m.line(-r,y+.5,side*r,r,y+.5,side*r,.06,0xffedb6);m.line(side*r,y+.5,-r,side*r,y+.5,r,.06,0xffedb6);
                    m.line(side*1.8,.04,-1.8,side*1.8,.04,-.8,.04,0xffce69);m.line(side*1.8,.04,1.8,side*.8,.04,1.8,.04,0xffce69);
                }
            }
        }
    }
}
