package com.dynasty.client;

import com.dynasty.Dynasty;
import com.dynasty.cod3.*;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderLevelStageEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import org.joml.Vector3f;
import java.util.*;

/** Bounded world-space library. Six composable renderers, with no full-screen geometry. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID,value=Dist.CLIENT)
public final class Cod3VfxRenderer {
    private static final List<Cod3VisualPacket> ACTIVE=new ArrayList<>();
    private static ClientLevel world;
    private static final BufferBuilder BUFFER=new BufferBuilder(262144);
    private static void clean(){
        var mc=Minecraft.getInstance();var current=mc.level;
        if(current!=world){ACTIVE.clear();world=current;}
        if(world==null)return;
        ACTIVE.removeIf(p->{
            if(world.getGameTime()-p.start()>=p.duration()||p.start()-world.getGameTime()>40)return true;
            if(p.sequence().startsWith("equipment_")){
                var owner=world.getEntity(p.entityId());
                return owner==null||!owner.isAlive()||owner.getUUID().getLeastSignificantBits()!=p.seed();
            }
            if(!p.sequence().startsWith("intro_")&&!p.sequence().startsWith("death_"))return false;
            var entity=world.getEntity(p.entityId());
            return mc.player==null||entity==null||mc.player.distanceToSqr(entity)>32*32;
        });
    }
    public static void receive(Cod3VisualPacket packet){
        clean();if(!packet.valid()||world==null||!packet.dimension().equals(world.dimension().location().toString()))return;
        if(packet.sequence().startsWith("status_clear_")){
            String status="status_"+packet.sequence().substring("status_clear_".length());
            ACTIVE.removeIf(old->old.entityId()==packet.entityId()&&old.sequence().equals(status));return;
        }
        if(packet.sequence().matches("status_[1-8]")||packet.sequence().startsWith("secondary_"))ACTIVE.removeIf(old->old.entityId()==packet.entityId()&&old.sequence().equals(packet.sequence()));
        if(packet.template()==0){
            // Typed selection excludes sound, WAIT and SET_* steps from the visual queue.
            Cod3Vfx.resume(packet, Cod3Catalog.sequenceById(packet.sequence())).forEach(Cod3VfxRenderer::add);
        }else add(packet);
    }
    private static void add(Cod3VisualPacket p){
        if(!p.valid()||p.template()==0)return;
        if(ACTIVE.stream().anyMatch(old->old.entityId()==p.entityId()&&old.start()==p.start()&&old.template()==p.template()&&old.seed()==p.seed()&&old.sequence().equals(p.sequence())))return;
        if(p.scale()>2&&ACTIVE.stream().filter(x->x.scale()>2).count()>=3)return;
        if(ACTIVE.size()>=48)ACTIVE.remove(0);ACTIVE.add(p);
    }
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
        if(e.phase!=TickEvent.Phase.END)return;clean();if(world==null||Minecraft.getInstance().isPaused()||world.getGameTime()%4!=0)return;
        var mc=Minecraft.getInstance();boolean low=mc.options.particles().get()==net.minecraft.client.ParticleStatus.MINIMAL;
        int remaining=128;
        for(var p:ACTIVE){
            if(remaining<=0)break;
            var d=Cod3Catalog.vfx(p.template());double age=world.getGameTime()-p.start();if(age<0||age>Math.min(p.duration(),40)||p.scale()>3)continue;
            Vec3 origin=p.origin();if(p.entityId()>=0){var entity=world.getEntity(p.entityId());if(entity==null||p.template()==4&&entity.getDeltaMovement().lengthSqr()<.0025)continue;origin=entity.position();}
            double distance=mc.gameRenderer.getMainCamera().getPosition().distanceTo(origin);if(distance>64)continue;
            int count=Math.min(remaining,p.sequence().startsWith("status_")?low?1:3:Math.max(1,d.budget(distance,low)/10));remaining-=count;Random r=new Random(p.seed()+world.getGameTime());
            int tint=p.tint()==0?d.color():p.tint();var color=new Vector3f((tint>>16&255)/255f,(tint>>8&255)/255f,(tint&255)/255f);
            for(int i=0;i<count;i++){double a=r.nextDouble()*Math.PI*2,rad=p.sequence().startsWith("status_")?.45:d.radius()*p.scale();
                var particle=p.sequence().equals("status_5")?net.minecraft.core.particles.ParticleTypes.SOUL_FIRE_FLAME:new DustParticleOptions(color,.6f);
                world.addParticle(particle,origin.x+Math.cos(a)*rad,origin.y+(p.sequence().startsWith("status_")?.6:.2),origin.z+Math.sin(a)*rad,0,.01,0);}
        }
    }
    @SubscribeEvent public static void render(RenderLevelStageEvent e){
        if(e.getStage()!=RenderLevelStageEvent.Stage.AFTER_PARTICLES)return;clean();if(world==null||ACTIVE.isEmpty())return;
        var camera=e.getCamera().getPosition();var pose=e.getPoseStack();pose.pushPose();boolean drawing=false;
        try(ImperialRenderState state=new ImperialRenderState()){
            RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();RenderSystem.enableDepthTest();RenderSystem.depthMask(false);RenderSystem.disableCull();RenderSystem.setShader(GameRenderer::getPositionColorShader);
            pose.translate(-camera.x,-camera.y,-camera.z);BUFFER.begin(VertexFormat.Mode.TRIANGLES,DefaultVertexFormat.POSITION_COLOR);drawing=true;
            int nearLarge=0,mediumLarge=0,farLarge=0;
            for(var p:ACTIVE){
                double age=world.getGameTime()-p.start()+e.getPartialTick();if(age<0||age>=p.duration())continue;
                Vec3 origin=p.origin(),direction=p.direction();
                if(p.entityId()>=0){var entity=world.getEntity(p.entityId());
                    if((entity==null||!entity.isAlive())&&(p.template()==4||p.sequence().startsWith("status_")||p.sequence().startsWith("secondary_")||p.sequence().startsWith("equipment_")))continue;
                    if(p.sequence().equals("equipment_beidou_stride")&&entity instanceof net.minecraft.world.entity.player.Player wearer&&com.dynasty.expansion.EquipmentBehaviors.pieces(wearer,"beidou")<4)continue;
                    if(p.sequence().equals("secondary_roots")&&entity instanceof net.minecraft.world.entity.LivingEntity living&&!living.hasEffect(com.dynasty.expansion.ExpansionEffects.STAGGER.get()))continue;
                    if(p.sequence().equals("secondary_coil")&&entity instanceof net.minecraft.world.entity.LivingEntity living&&!living.hasEffect(net.minecraft.world.effect.MobEffects.MOVEMENT_SLOWDOWN))continue;
                    if(entity!=null){if(p.template()==4){if(!entity.isAlive()||entity.getDeltaMovement().lengthSqr()<.0025)continue;direction=entity.getDeltaMovement().normalize();}origin=entity.getPosition(e.getPartialTick());}}
                double distance=origin.distanceTo(camera);if(distance>256||distance<.8)continue;
                if(p.scale()>2){if(distance>96&&farLarge++>=1||distance>32&&distance<=96&&mediumLarge++>=2||distance<=32&&nearLarge++>=3)continue;}
                var d=Cod3Catalog.vfx(p.template());double life=age/p.duration(),expansion=Math.min(1,life/.35),alpha=Math.min(1,age/2)*Math.min(1,(1-life)/.2)*.6;
                int segments=distance>96?12:distance>32?20:32;
                if(Minecraft.getInstance().options.particles().get()==net.minecraft.client.ParticleStatus.MINIMAL)segments=Math.min(12,segments);
                var geometry=new Geometry(pose.last().pose(),camera,origin,direction,p.scale(),p.tint()==0?d.color():p.tint(),alpha,segments,p.seed());
                if(p.sequence().matches("status_[1-8]"))geometry.status(Integer.parseInt(p.sequence().substring(7)),p.tick()+1,age);
                else if(p.sequence().equals("secondary_roots"))geometry.roots(age);
                else if(p.sequence().equals("secondary_coil"))geometry.coil(age);
                else if(p.sequence().equals("secondary_possession"))geometry.possession(age);
                else if(p.sequence().equals("secondary_echo"))geometry.echo(life);
                else if(p.sequence().equals("secondary_alarm"))geometry.alarm(life);
                else if(p.sequence().equals("equipment_beidou_stride"))geometry.starStride(age);
                else if(p.sequence().equals("equipment_phoenix_embers"))geometry.phoenixEmbers(age,life);
                else if(p.sequence().equals("equipment_mortuary_breath"))geometry.patientBreath(age,false);
                else if(p.sequence().equals("equipment_mortuary_rescued"))geometry.patientBreath(age,true);
                else if(p.sequence().equals("site_bellows"))geometry.bellows(life);
                else if(p.sequence().equals("site_waterwheel"))geometry.waterwheel(age);
                else if(p.sequence().equals("site_puzzle_press"))geometry.puzzle(life,false);
                else if(p.sequence().equals("site_puzzle_open"))geometry.puzzle(life,true);
                else if(p.sequence().equals("qinglong_combo_wave"))geometry.dragonWave(life,age);
                else if(p.sequence().matches("scenic_(0[1-9]|1[0-9]|2[0-5])"))geometry.scenic(Integer.parseInt(p.sequence().substring(7)),life);else geometry.draw(p.template(),d,expansion,life,age);
            }
            BufferUploader.drawWithShader(BUFFER.end());drawing=false;
        }finally{if(drawing)BUFFER.discard();pose.popPose();}
    }
    private static final class Geometry {
        final Matrix4f matrix;final Vec3 camera,o,f,r,u=new Vec3(0,1,0);final double scale,alpha;final int color,segments;final long seed;
        Geometry(Matrix4f matrix,Vec3 camera,Vec3 o,Vec3 forward,double scale,int color,double alpha,int segments,long seed){this.matrix=matrix;this.camera=camera;this.o=o;Vec3 horizontal=new Vec3(forward.x,0,forward.z);this.f=horizontal.lengthSqr()<1e-9?new Vec3(0,0,1):horizontal.normalize();this.r=new Vec3(f.z,0,-f.x);this.scale=scale;this.color=color;this.alpha=alpha;this.segments=segments;this.seed=seed;}
        Vec3 p(double x,double y,double z){return o.add(r.scale(x*scale)).add(u.scale(y*scale)).add(f.scale(z*scale));}
        void vertex(Vec3 p){BUFFER.vertex(matrix,(float)p.x,(float)p.y,(float)p.z).color(color>>16&255,color>>8&255,color&255,(int)(255*alpha)).endVertex();}
        void triangle(Vec3 a,Vec3 b,Vec3 c,double shade){
            if(a.distanceToSqr(camera)<.64||b.distanceToSqr(camera)<.64||c.distanceToSqr(camera)<.64)return;
            for(Vec3 point:new Vec3[]{a,b,c})BUFFER.vertex(matrix,(float)point.x,(float)point.y,(float)point.z).color((int)((color>>16&255)*shade),(int)((color>>8&255)*shade),(int)((color&255)*shade),(int)(255*alpha)).endVertex();
        }
        // BeamRenderer: camera-facing ribbon, culled before it can cross the camera near plane.
        void beam(Vec3 a,Vec3 b,double width){
            Vec3 delta=b.subtract(a);double t=delta.lengthSqr()<1e-12?0:Math.max(0,Math.min(1,camera.subtract(a).dot(delta)/delta.lengthSqr()));
            if(a.add(delta.scale(t)).distanceToSqr(camera)<.64)return;
            Vec3 side=b.subtract(a).cross(camera.subtract(a)).normalize().scale(width*scale/2);if(side.lengthSqr()<1e-12)return;
            Vec3 a1=a.add(side),a2=a.subtract(side),b1=b.add(side),b2=b.subtract(side);
            vertex(a1);vertex(a2);vertex(b1);vertex(b1);vertex(a2);vertex(b2);
        }
        // RingRenderer / GroundDecalRenderer share the exact radius from the definition.
        void ring(double radius,double y,double arc){for(int i=0;i<segments;i++){double a=(i/(double)segments-.5)*arc,b=((i+1)/(double)segments-.5)*arc;beam(p(Math.sin(a)*radius,y,Math.cos(a)*radius),p(Math.sin(b)*radius,y,Math.cos(b)*radius),.06);}}
        void decal(double radius,int points,double rotation){ring(radius,.04,Math.PI*2);for(int i=0;i<points;i++){double a=i*Math.PI*2/points+rotation,b=a+Math.PI*4/points;beam(p(Math.sin(a)*radius,.06,Math.cos(a)*radius),p(Math.sin(b)*radius,.06,Math.cos(b)*radius),.045);}}
        // SplineRenderer samples a deterministic curve instead of creating visual entities.
        void spline(double length,double height,double time){Vec3 last=p(0,0,0);for(int i=1;i<=segments;i++){double t=i/(double)segments;Vec3 next=p(Math.sin(t*Math.PI*4+time)*height,t*height,t*length);beam(last,next,.1);last=next;}}
        // InstancedMeshRenderer: shared diamond primitive for bones, crystals, swords and feathers.
        void mesh(double x,double y,double z,double size){Vec3 tip=p(x,y+size,z),bottom=p(x,y-size,z);if(p(x,y,z).distanceTo(camera)<size*scale+.8)return;for(int i=0;i<4;i++){double a=i*Math.PI/2,b=(i+1)*Math.PI/2;Vec3 edge=p(x+Math.cos(a)*size*.4,y,z+Math.sin(a)*size*.4),next=p(x+Math.cos(b)*size*.4,y,z+Math.sin(b)*size*.4);triangle(tip,edge,next,.75+i*.06);triangle(bottom,next,edge,.55+i*.07);}}
        void blade(double x,double y,double z,double size){triangle(p(x,y-size,z),p(x-.16*size,y+.7*size,z),p(x,y+size,z),.95);triangle(p(x,y-size,z),p(x,y+size,z),p(x+.16*size,y+.7*size,z),.7);beam(p(x-.3*size,y-.6*size,z),p(x+.3*size,y-.6*size,z),.08);beam(p(x,y-size,z),p(x,y-1.3*size,z),.1);}
        void box(double x,double y,double z,double width,double height,double depth){
            Vec3[] v={p(x-width,y,z-depth),p(x+width,y,z-depth),p(x+width,y+height,z-depth),p(x-width,y+height,z-depth),p(x-width,y,z+depth),p(x+width,y,z+depth),p(x+width,y+height,z+depth),p(x-width,y+height,z+depth)};
            int[][] faces={{0,1,2,3},{5,4,7,6},{1,5,6,2},{4,0,3,7},{3,2,6,7},{4,5,1,0}};
            for(int i=0;i<6;i++){var f=faces[i];triangle(v[f[0]],v[f[1]],v[f[2]],.6+i*.06);triangle(v[f[0]],v[f[2]],v[f[3]],.6+i*.06);}
        }
        void orb(double radius,double y){
            if(p(0,y,0).distanceTo(camera)<radius*scale+.8)return;
            int rings=segments<=12?4:8;
            for(int j=0;j<rings;j++)for(int i=0;i<segments;i++){double a=i*Math.PI*2/segments,b=(i+1)*Math.PI*2/segments,lat=j*Math.PI/rings,lat2=(j+1)*Math.PI/rings;
                Vec3 a1=p(Math.sin(lat)*Math.cos(a)*radius,y+Math.cos(lat)*radius,Math.sin(lat)*Math.sin(a)*radius),a2=p(Math.sin(lat)*Math.cos(b)*radius,y+Math.cos(lat)*radius,Math.sin(lat)*Math.sin(b)*radius),b1=p(Math.sin(lat2)*Math.cos(a)*radius,y+Math.cos(lat2)*radius,Math.sin(lat2)*Math.sin(a)*radius),b2=p(Math.sin(lat2)*Math.cos(b)*radius,y+Math.cos(lat2)*radius,Math.sin(lat2)*Math.sin(b)*radius);
                triangle(a1,a2,b1,.65+.25*Math.sin(lat));triangle(b1,a2,b2,.65+.25*Math.sin(lat2));
            }
        }
        // AfterImageRenderer keeps time-separated arcs in weapon space.
        void after(double radius,double life,int count){for(int i=0;i<count;i++)ring(radius*(1-i*.08),.3+i*.12,Math.PI*(.2+life));}
        void mountain(double x,double y,double z,double size){
            for(int side=0;side<4;side++){double a=side*Math.PI/2,b=(side+1)*Math.PI/2;Vec3 base=p(x+Math.cos(a)*size,y,z+Math.sin(a)*size),next=p(x+Math.cos(b)*size,y,z+Math.sin(b)*size);triangle(base,next,p(x,y+size*1.7,z),.5+side*.12);beam(base,p(x,y+size*1.7,z),.08);}
        }
        void soldier(double x,double z,double time){
            mesh(x,2.4,z,.45);box(x,1,z,.32,1,.2);beam(p(x,.8,z),p(x-.35,0,z+.3*Math.sin(time)),.15);beam(p(x,.8,z),p(x+.35,0,z-.3*Math.sin(time)),.15);beam(p(x-.7,.2,z),p(x-.7,4,z),.05);beam(p(x,1.7,z),p(x-.7,1.3,z),.1);
        }
        void coil(double age){
            Vec3 last=p(.5,.04,0);
            for(int i=1;i<=32;i++){double t=i/32.,a=t*Math.PI*5;Vec3 next=p(Math.cos(a)*.5,t*1.15,Math.sin(a)*.5);beam(last,next,.10+.015*Math.sin(age*.2));last=next;}
            mesh(last.subtract(o).dot(r),1.2,last.subtract(o).dot(f),.12);
        }
        void possession(double age){
            double turn=age*.09;
            for(int side=-1;side<=1;side+=2){
                Vec3 a=p(side*.28,.45,-.32),b=p(side*.48,.9,-.3),c=p(side*(.28+Math.sin(turn)*.05),1.45,-.32);
                triangle(a,b,c,.65);beam(a,c,.035);
            }
            mesh(0,1.65,-.32,.17);beam(p(-.22,.8,-.32),p(.22,.8,-.32),.02);
        }
        void echo(double life){for(int band=0;band<3;band++)ring(.25+life*(1.1+band*.35),.8+band*.15,Math.PI*1.5);}
        void alarm(double life){for(int i=0;i<3;i++){double y=1.8+i*.2+life*.2;beam(p(-.18,y,0),p(0,y+.12,0),.035);beam(p(0,y+.12,0),p(.18,y,0),.035);}}
        void dragonWave(double life,double age){
            // One tapered, travelling body with a horned head, rather than another water ring.
            double head=.35+life*1.6;
            Vec3 last=p(0,.75,head);
            for(int i=1;i<=16;i++){
                double t=i/16.,a=t*Math.PI*3-age*.12;
                Vec3 next=p(Math.sin(a)*(.15+t*.3),.75+Math.cos(a)*.22,head-t*2.3);
                beam(last,next,.16*(1-t)+.02);
                if(i%3==0)triangle(next,next.add(u.scale(.14)),next.subtract(f.scale(.12)),.85);
                last=next;
            }
            triangle(p(-.22,.68,head),p(.22,.68,head),p(0,.9,head+.45),.95);
            beam(p(-.12,.85,head+.08),p(-.28,1.15,head-.12),.05);
            beam(p(.12,.85,head+.08),p(.28,1.15,head-.12),.05);
            beam(p(-.12,.7,head+.25),p(-.45,.58,head+.35),.025);
            beam(p(.12,.7,head+.25),p(.45,.58,head+.35),.025);
        }
        void starStride(double age){
            double[][] stars={{-.45,-.65},{-.15,-.45},{.10,-.20},{.20,.15},{.45,.30},{.55,.58},{.28,.72}};
            int visible=Math.min(7,1+(int)age/2);
            for(int i=0;i<visible;i++){
                double x=stars[i][0],z=stars[i][1];mesh(x,.08,z,.065);
                if(i>0)beam(p(stars[i-1][0],.045,stars[i-1][1]),p(x,.045,z),.028);
            }
            double step=Math.sin(age*Math.PI/7)*.22;
            for(int side=-1;side<=1;side+=2){beam(p(side*.18,.03,side*step-.18),p(side*.18,.035,side*step+.12),.045);}
        }
        void phoenixEmbers(double age,double life){
            for(int i=0;i<5;i++){
                double a=i*Math.PI*2/5+age*.12,x=Math.cos(a)*(.35+life*.3),z=Math.sin(a)*(.35+life*.3),y=.7+life*.5;
                triangle(p(x-.06,y-.10,z),p(x+.06,y-.10,z),p(x,y+.18,z),.95);mesh(x,y+.18,z,.035);
            }
        }
        void patientBreath(double age,boolean rescued){
            double breath=Math.sin(age*Math.PI/15)*.045;
            // Small paired chest strokes breathe; rescue raises the pulse.
            for(int side=-1;side<=1;side+=2){
                Vec3 last=p(side*.06,.85,0);
                for(int step=1;step<=8;step++){
                    double t=step/8.,y=.85+Math.sin(t*Math.PI)*(.09+breath)+(rescued?t*.2:0);
                    Vec3 next=p(side*(.06+t*.2),y,0);beam(last,next,.025);last=next;
                }
            }
            if(rescued)mesh(0,1.05+age*.006,0,.055);
        }
        void puzzle(double life,boolean open){
            double slide=open?Math.min(1,life/.55)*.7:Math.sin(Math.PI*life)*.12;
            // Three perpendicular interlocking pins slide apart, with a finite
            // raised centre latch; no ring, visual entity or gameplay collision.
            box(-slide,.05,0,.32,.12,.09);
            box(0,.18,slide,.09,.12,.32);
            box(slide,.31,0,.25,.12,.08);
            box(0,.42+(open?slide*.4:0),0,.08,.08,.08);
        }
        void bellows(double life){
            double stroke=Math.sin(life*Math.PI*2)*.12;
            box(0,0,0,.35,.2+stroke,.25);
            for(int i=0;i<4;i++)beam(p(-.32,i*.05,0),p(.32,i*.05+stroke,0),.025);
            beam(p(0,.12,0),p(0,.12,.75+life*.4),.07);
            for(int i=0;i<3;i++)mesh((i-1)*.13,.15+life*.3,.7+life*.4,.06);
        }
        void waterwheel(double age){
            double angle=age*.12;
            for(int i=0;i<12;i++){
                double a=angle+i*Math.PI/6,b=a+Math.PI/6;
                beam(p(Math.cos(a)*.7,.4+Math.sin(a)*.7,0),p(Math.cos(b)*.7,.4+Math.sin(b)*.7,0),.065);
                if(i%2==0)beam(p(0,.4,0),p(Math.cos(a)*.7,.4+Math.sin(a)*.7,0),.055);
            }
            beam(p(0,.4,-.3),p(0,.4,.3),.11);
        }
        void roots(double age){
            double growth=Math.min(1,age/5);
            for(int root=0;root<4;root++){
                double a=root*Math.PI/2;Vec3 last=p(Math.cos(a)*.9,.02,Math.sin(a)*.9);
                for(int step=1;step<=10;step++){
                    double t=step/10.,turn=a+t*Math.PI*2,r=.9-(.9-.38)*t;
                    Vec3 next=p(Math.cos(turn)*r,t*.65*growth,Math.sin(turn)*r);beam(last,next,.045);last=next;
                }
            }
        }
        void status(int code,int layers,double age){
            double phase=age*.15;
            switch(code){
                case 1,3->{for(int strand=0;strand<(code==3?3:layers);strand++){
                    Vec3 last=p(.5,0,0);for(int i=1;i<=12;i++){double a=i*.65+phase+strand*2.1;Vec3 next=p(Math.cos(a)*.5,i*.12,Math.sin(a)*.5);beam(last,next,code==3?.07:.11);last=next;}}}
                case 2->{for(int i=0;i<layers;i++)ring(.5+i*.07,.35+i*.4,Math.PI*2);for(int i=0;i<6;i++){double a=i*Math.PI/3+phase;beam(p(Math.sin(a)*.45,.3,Math.cos(a)*.45),p(Math.sin(a)*.55,1.5,Math.cos(a)*.55),.025);}}
                case 4->{Random random=new Random(seed+(long)age/3);for(int mark=0;mark<layers;mark++){
                    double a=mark*Math.PI*2/layers+phase;Vec3 last=p(Math.cos(a)*.45,.2,Math.sin(a)*.45);
                    for(int i=1;i<=5;i++){Vec3 next=p(Math.cos(a)*(.4+random.nextDouble()*.12),.2+i*.25,Math.sin(a)*(.4+random.nextDouble()*.12));beam(last,next,.045);last=next;}}
                    for(int i=0;i<layers;i++)mesh((i-(layers-1)*.5)*.18,1.7,0,.10);}
                case 5->{for(int i=0;i<4;i++){double a=i*Math.PI/2+phase;double x=Math.sin(a)*.4,z=Math.cos(a)*.4;triangle(p(x-.08,.5,z),p(x+.08,.5,z),p(x+Math.sin(phase+i)*.08,1.2,z),.9);}}
                case 6->{for(int i=0;i<5;i++){double a=i*Math.PI*2/5;double x=Math.cos(a)*.4,z=Math.sin(a)*.4;beam(p(x,.3,z),p(x+.15,.65,z),.035);beam(p(x+.15,.65,z),p(x-.12,1.1,z),.035);mesh(x,1.25,z,.14);}}
                case 7->{for(int side=-1;side<=1;side+=2){Vec3 a=p(side*.2,.3,.32),b=p(side*.06,.7,.32),c=p(side*.28,1,.32);beam(a,b,.045);beam(b,c,.045);beam(b,p(side*.38,.78,.32),.035);}}
                case 8->{for(int i=0;i<3;i++){double shift=Math.sin(phase+i)*.12;beam(p(-.4+shift,.02,i*.14),p(.4+shift,.02,i*.14),.09);}ring(.5+Math.sin(phase)*.08,.03,Math.PI*1.7);}
            }
        }
        void ship(double x,double y,double z){
            beam(p(x-4,y,z),p(x+4,y,z),.5);beam(p(x-4,y,z),p(x-3,y-1,z),.12);beam(p(x-3,y-1,z),p(x+3,y-1,z),.2);beam(p(x+3,y-1,z),p(x+4,y,z),.12);beam(p(x,y,z),p(x,y+6,z),.12);beam(p(x-2,y+2,z),p(x+2,y+2,z),.12);beam(p(x-2,y+2,z),p(x,y+5,z),.12);beam(p(x,y+5,z),p(x+2,y+2,z),.12);
        }
        // DistantVisual scenes reuse the primitive library, never gameplay entities or terrain.
        void scenic(int id,double life){
            Random random=new Random(seed);double time=life*Math.PI*2;int count=segments<=12?4:segments<=20?16:40;
            switch(id){
                case 1->{spline(28,4,time);beam(p(0,4,28),p(-1.5,5,30),.3);beam(p(0,4,28),p(1.5,5,30),.3);for(int i=1;i<6&&segments>12;i++){beam(p(Math.sin(i)*4,i*.65,i*4),p(Math.sin(i)*4+2,i*.65-1,i*4+1),.15);}}
                case 2->{decal(14,8,time*.1);for(int i=0;i<8;i++){double a=i*Math.PI/4;beam(p(Math.cos(a)*14,0,Math.sin(a)*14),p(Math.cos(a)*14,12,Math.sin(a)*14),.2);}}
                case 3,16->{ship((life-.5)*20,6,0);if(id==16&&segments>12)for(int i=-2;i<=2;i++)mountain(i*2,5,2,1);}
                case 4,11,18->{for(int i=0;i<count;i++){double x=(i%8-3.5)*2,z=(i/8)*3+life*12;soldier(x,z,time+i);if(i%8==0){beam(p(x,0,z),p(x,6,z),.08);beam(p(x,6,z),p(x+2,5,z),.25);}}}
                case 5,23->{int islands=segments<=12?3:7;for(int i=0;i<islands;i++){double x=(i-islands/2)*5,y=4+Math.sin(i)*2,z=Math.cos(i)*4;mountain(x,y,z,3);if(id==23&&i>0)beam(p(x-5,5,z),p(x,5,z),.07);if(segments>12){beam(p(x-1,y+5,z),p(x+1,y+5,z),.18);beam(p(x,y+5,z),p(x,y+6,z),.12);}}}
                case 6->{beam(p(-3,0,0),p(-3,16,0),.35);beam(p(3,0,0),p(3,16,0),.35);mesh(0,12,0,2);beam(p(0,10,0),p(-7,7,0),.5);beam(p(0,10,0),p(7,7,0),.5);}
                case 7,19,20->{for(int i=0;i<count;i++){double x=(random.nextDouble()-.5)*30,z=(random.nextDouble()-.5)*24,y=id==20?20-life*18:3+Math.sin(time+i)*2;mesh(x,y,z,.15);if(id==20)beam(p(x,y,z),p(x-2,y+4,z+1),.06);}}
                case 8->{for(int i=0;i<5;i++)spline(3,18,time+i);ring(5,0,Math.PI*2);}
                case 9,24->{for(int i=0;i<Math.min(count,16);i++){double a=i*Math.PI*2/Math.min(count,16);mesh(Math.sin(a)*10,5+Math.cos(a)*3,Math.cos(a)*10,id==24?1.5:.3);if(id==9&&i>0)beam(p(Math.sin(a)*10,5+Math.cos(a)*3,Math.cos(a)*10),p(Math.sin(a+.3)*10,5+Math.cos(a+.3)*3,Math.cos(a+.3)*10),.06);}}
                case 10->{ring(10,0,Math.PI*2);for(int i=0;i<5;i++)ring(8-i,i*.8,Math.PI*2);mesh(0,2,11,2);mountain(0,4,0,3);}
                case 12->{decal(8,12,0);for(int i=0;i<3;i++){beam(p(-4+i*4,0,0),p(-4+i*4,8,0),.8);mesh(-4+i*4,9,0,1.2);}}
                case 13->{beam(p(0,0,0),p(0,10,0),.5);for(int i=0;i<8;i++){double a=i*Math.PI/4;beam(p(0,5,0),p(Math.sin(a)*6,8+Math.cos(a),Math.cos(a)*6),.25);mesh(Math.sin(a)*6,8+Math.cos(a),Math.cos(a)*6,.8);}}
                case 14,17,22->{for(int i=0;i<(segments<=12?3:9);i++){double x=(i%3-1)*6,z=i/3*6;beam(p(x-2,0,z),p(x-2,4,z),.12);beam(p(x+2,0,z),p(x+2,4,z),.12);beam(p(x-3,4,z),p(x+3,4,z),.25);beam(p(x-3,4,z),p(x,6,z),.1);beam(p(x,6,z),p(x+3,4,z),.1);if(id==22)mesh(x,2,z,.3);}}
                case 15->{for(int i=0;i<4;i++){Vec3 last=p(-16,14+i,0);for(int j=1;j<=segments;j++){double x=j*32./segments-16;Vec3 next=p(x,14+i+Math.sin(x*.25+time)*2,j*.1);beam(last,next,.3);last=next;}}}
                case 21->{for(int i=0;i<3;i++){Vec3 last=p(-18,8+i*.5,0);for(int j=1;j<=segments;j++){double x=j*36./segments-18;Vec3 next=p(x,8+i*.5+Math.sin(j*Math.PI/segments)*8,0);beam(last,next,.2);last=next;}}}
                case 25->{mesh(0,12,0,2);for(int i=0;i<6;i++)beam(p(0,12,0),p((i-2.5)*2,10-Math.abs(i-2.5),0),.3);beam(p(0,0,0),p(0,8,0),.1);}
                default->throw new IllegalArgumentException("Unknown scenic event "+id);
            }
        }
        void draw(int id,DynastyVfxDefinition d,double expand,double life,double age){
            double radius=d.radius()*expand,angle=age*.06;Random random=new Random(seed);
            switch(id){
                case 1,3,34 -> {beam(p(0,.5,0),p(0,.5,d.length()*expand),id==3?.12:.3);if(id==34)beam(p(-.2,0,0),p(.2,0,d.length()*expand),.04);}
                case 2 -> {ring(radius,.6,Math.toRadians(70));ring(radius*.88,.65,Math.toRadians(70));}
                case 4 -> {beam(p(0,0,-Math.min(4,age*.2)),p(0,0,0),.08);mesh(0,0,0,.18);}
                case 5 -> {ring(radius,.1,Math.PI*2);for(int i=0;i<8;i++){double a=i*Math.PI/4+angle;beam(p(Math.cos(a)*radius,0,Math.sin(a)*radius),p(Math.cos(a+.4)*radius*.5,6*expand,Math.sin(a+.4)*radius*.5),.16);}}
                case 6,31 -> {Vec3 last=p(0,id==31?3:20,0);for(int i=0;i<6;i++){Vec3 next=p((random.nextDouble()-.5)*.8,(5-i)*(id==31?.5:4), (random.nextDouble()-.5)*.8);beam(last,next,id==31?.04:.15);last=next;}}
                case 7 -> {ring(radius,.2,Math.PI*2);ring(radius*.9,.6*Math.sin(life*Math.PI),Math.PI*2);}
                case 8 -> {ring(radius,.04,Math.PI*2);for(int i=0;i<12;i++){double a=i*Math.PI/6;mesh(Math.cos(a)*radius,expand,Math.sin(a)*radius,expand);}}
                case 9 -> {for(int j=0;j<3;j++){Vec3 last=p(radius,0,0);for(int i=1;i<=segments;i++){double t=i/(double)segments,a=t*Math.PI*6+angle+j*2.1;Vec3 n=p(Math.cos(a)*radius,t*12,Math.sin(a)*radius);beam(last,n,.08);last=n;}}}
                case 10,27 -> {for(int i=0;i<8;i++){double z=i*1.2;beam(p((i%2-.5)*.8,.06,z),p(((i+1)%2-.5)*.8,.06,z+1.2),.06);if(id==27)mesh((random.nextDouble()-.5)*4,Math.sin(life*Math.PI)*2,z,.3);}}
                case 11 -> {for(int i=0;i<5;i++)ring(radius*(.4+i*.12),.2+i*.25+Math.sin(angle+i)*.1,Math.PI*2);spline(radius*1.5,.5,angle);}
                case 32 -> {orb(radius*.75,radius*.75);for(int i=0;i<Math.min(segments,16);i++){double a=angle+i*2.4;mesh(Math.cos(a)*radius*.8,1+Math.sin(a*2),Math.sin(a)*radius*.8,.1);}}
                case 12 -> {ring(radius,.08,Math.PI*2);for(int i=0;i<8;i++){double a=i*Math.PI/4;beam(p(Math.cos(a)*radius*.85,.08,Math.sin(a)*radius*.85),p(Math.cos(a)*radius,.08,Math.sin(a)*radius),.09);}}
                case 25 -> {ring(radius,.08,Math.PI*2);ring(radius*.8,-.15,Math.PI*2);for(int i=0;i<8;i++){double a=i*Math.PI/4+angle;beam(p(Math.sin(a)*radius,.1,Math.cos(a)*radius),p(0,-.4,0),.05);}}
                case 26 -> {double shock=6+(d.radius()-6)*expand;ring(shock,.08,Math.PI*2);ring(shock*.92,.35*Math.sin(life*Math.PI),Math.PI*2);}
                case 13,17 -> {for(int i=0;i<(id==13?3:1);i++)spline(d.length()*expand,id==17?2:.8,angle+i*2);if(id==17)for(int i=0;i<6;i++)mesh(Math.sin(angle+i)*1.5,i*.3,i*2,.3);}
                case 24 -> {Vec3 last=p(0,1,0);for(int i=1;i<=8;i++){Vec3 next=p((random.nextDouble()-.5)*2,1+(random.nextDouble()-.5)*2,i*d.length()*expand/8);beam(last,next,.2+life*.4);mesh((random.nextDouble()-.5)*2,1,i*d.length()*expand/8,.12);last=next;}}
                case 14,33 -> {for(int i=0;i<3;i++)ring(radius*(1-i*.15),.5+i*.5,Math.PI*2);orb(radius*.6,radius);}
                case 15,16,20,40 -> {decal(radius,id==15?8:id==40?4:6,angle*.2);if(id==16){ring(radius,8,Math.PI*2);for(int i=0;i<8;i++){double a=i*Math.PI/4;beam(p(Math.sin(a)*radius,0,Math.cos(a)*radius),p(Math.sin(a)*radius,8,Math.cos(a)*radius),.04);}}if(id==40)for(int i=0;i<4;i++){
                    double a=i*Math.PI/2;Vec3 center=p(Math.cos(a)*radius*.6,.08,Math.sin(a)*radius*.6);int tint=new int[]{0x6BE0C0,0x1A2A3A,0xE8E0C8,0xFF8A30}[i];
                    var beast=new Geometry(matrix,camera,center,new Vec3(0,0,1),scale*.35,tint,alpha,Math.min(segments,12),seed+i);
                    switch(i){case 0->beast.spline(5,.6,angle);case 1->{beast.ring(1.6,.1,Math.PI*2);beast.decal(1.2,6,0);}case 2->{beast.box(0,.1,0,.8,.45,1.2);beast.mesh(0,.5,1.3,.4);for(int leg=0;leg<4;leg++)beast.beam(beast.p(leg%2==0?-.8:.8,.1,leg<2?-.8:.8),beast.p(leg%2==0?-1.1:1.1,.04,leg<2?-.9:.9),.12);}case 3->{for(int feather=0;feather<8;feather++){double t=(feather/7.-.5)*Math.PI;beast.beam(beast.p(0,.1,0),beast.p(Math.sin(t)*2.4,.1,Math.cos(t)*2.4),.15);}}}
                }}
                case 18 -> {for(int i=0;i<6;i++){box(0,.3,-i*.65,.4,.65,.8);mesh(0,.9,1-i*.65,.4);}after(radius,life,2);}
                case 23 -> {for(int i=0;i<5;i++){box((i-2)*.5,.1,-i*.65,.2,1.1,.15);mesh((i-2)*.5,1.5,-i*.65,.3);}}
                case 29 -> after(2,life,6);
                case 19 -> {for(int i=0;i<12;i++){double a=(i/11.-.5)*Math.PI;beam(p(0,1,0),p(Math.sin(a)*radius,1+Math.cos(a)*2,Math.cos(a)*radius),.12);}}
                case 21,30 -> {for(int i=0;i<Math.min(segments,40);i++){double a=random.nextDouble()*Math.PI*2,r=Math.sqrt(random.nextDouble())*radius;if(id==30)blade(Math.cos(a)*r,(1-life)*12,Math.sin(a)*r,.8);else mesh(Math.cos(a)*r,(1-life)*12,Math.sin(a)*r,.2);}if(id==30)ring(radius,12,Math.PI*2);}
                case 22 -> {box(0,2,0,1.1,3,.6);mesh(0,6.5,0,1);box(-.7,0,0,.5,2,.45);box(.7,0,0,.5,2,.45);beam(p(-1,4.8,0),p(-2.7,3.5,0),.55);beam(p(1,4.8,0),p(2.7,3.5,0),.55);ring(1.8,6.8,Math.PI*2);decal(radius,6,0);}
                case 28 -> {beam(p(0,0,0),p(0,24*expand,0),1.5);ring(1.5,.1,Math.PI*2);}
                case 35 -> {ring(radius,.04,Math.PI*2);for(int i=0;i<12;i++){double a=i*Math.PI/6;beam(p(Math.cos(a)*radius,0,Math.sin(a)*radius),p(Math.cos(a)*radius*.7,2,Math.sin(a)*radius*.7),.18);}}
                case 36 -> {ring(radius,1,Math.PI/3);for(int i=0;i<4;i++)beam(p(i-2,0,radius),p(i-2,3,radius),.06);}
                case 37 -> {for(int i=0;i<5;i++)beam(p(-radius,i*.5,life*8),p(radius,i*.5,life*8),.16);}
                case 38 -> {for(int i=0;i<5;i++)beam(p(i-.5*4,.08,0),p(i-.5*4,.08,4+i%2),.25);ring(2,.05,Math.PI*2);}
                case 39 -> {mesh(0,(1-life)*12,0,2*expand);for(int i=0;i<6;i++)beam(p(0,(1-life)*12,0),p(Math.sin(i)*.4,(1-life)*12+4,Math.cos(i)*.4),.1);}
                default -> {}
            }
        }
    }
    private Cod3VfxRenderer(){}
}
