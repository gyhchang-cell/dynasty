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
    private static long soundTick=Long.MIN_VALUE;
    private static int sounds;
    private static final BufferBuilder BUFFER=new BufferBuilder(262144);
    private static void clean(){
        var mc=Minecraft.getInstance();var current=mc.level;
        if(current!=world){ACTIVE.clear();Cod3AfterImages.clear();soundTick=Long.MIN_VALUE;world=current;}
        if(world==null)return;
        ACTIVE.removeIf(p->{
            if(world.getGameTime()-p.start()>=p.duration()||p.start()-world.getGameTime()>40)return true;
            if(p.template()==4&&!p.sequence().equals("arrow_collapse")&&p.entityId()>=0){var arrow=world.getEntity(p.entityId());if(arrow==null||!arrow.isAlive())return true;}
            if(p.sequence().startsWith("equipment_")||p.sequence().equals("vfx_follow")||Cod3AfterImages.supports(p)||p.sequence().matches("accessory_proc_[13456]")){
                var owner=world.getEntity(p.entityId());
                if(owner==null||!owner.isAlive()||owner.getUUID().getLeastSignificantBits()!=p.seed())return true;
                return p.sequence().equals("equipment_weapon_meteor_charge")&&(!(owner instanceof net.minecraft.world.entity.LivingEntity living)||!living.isUsingItem()||!living.getUseItem().is(com.dynasty.expansion.ExpansionContent.HAMMER.get()));
            }
            if(p.sequence().startsWith("scenic_"))return mc.player==null||mc.player.distanceToSqr(p.origin())>256*256;
            if(!p.sequence().startsWith("intro_")&&!p.sequence().startsWith("death_"))return false;
            var entity=world.getEntity(p.entityId());
            return mc.player==null||entity==null||mc.player.distanceToSqr(entity)>32*32;
        });
        Cod3AfterImages.retain(ACTIVE);
    }
    public static void receive(Cod3VisualPacket packet){
        clean();if(!packet.valid()||world==null||!packet.dimension().equals(world.dimension().location().toString()))return;
        if(packet.sequence().startsWith("status_clear_")){
            String status="status_"+packet.sequence().substring("status_clear_".length());
            ACTIVE.removeIf(old->old.entityId()==packet.entityId()&&old.sequence().equals(status));return;
        }
        if(packet.sequence().matches("status_[1-8]")||packet.sequence().startsWith("secondary_"))ACTIVE.removeIf(old->old.entityId()==packet.entityId()&&old.sequence().equals(packet.sequence()));
        if(packet.sequence().equals("equipment_weapon_meteor_charge"))ACTIVE.removeIf(old->old.entityId()==packet.entityId()&&old.sequence().equals(packet.sequence()));
        if(packet.sequence().equals("arrow_collapse"))ACTIVE.removeIf(old->old.template()==4&&old.entityId()==packet.entityId()&&old.seed()==packet.seed());
        if(packet.template()==0){
            // Typed selection excludes sound, WAIT and SET_* steps from the visual queue.
            Cod3Vfx.resume(packet, Cod3Catalog.sequenceById(packet.sequence())).forEach(Cod3VfxRenderer::add);
        }else add(packet);
    }
    private static void add(Cod3VisualPacket p){
        if(!p.valid()||p.template()==0)return;
        if(p.sequence().startsWith("combat_")){try{VfxInstance.combat(p);}catch(RuntimeException invalid){return;}}
        if(ACTIVE.stream().anyMatch(old->old.entityId()==p.entityId()&&old.start()==p.start()&&old.template()==p.template()&&old.seed()==p.seed()&&old.sequence().equals(p.sequence())))return;
        boolean templateCue=p.sequence().isBlank()||p.sequence().equals("vfx_follow")||p.sequence().startsWith("combat_")||Cod3AfterImages.supports(p);
        if(templateCue&&ACTIVE.stream().filter(x->x.template()==p.template()&&(p.template()!=29||x.entityId()==p.entityId())).count()>=VfxTimeline.limit(p.template()))return;
        if(p.scale()>2&&ACTIVE.stream().filter(x->x.scale()>2).count()>=3)return;
        if(ACTIVE.size()>=48)ACTIVE.remove(0);ACTIVE.add(p);Cod3AfterImages.sample(p);
        if(templateCue&&p.template()!=4&&world.getGameTime()-p.start()>=0&&world.getGameTime()-p.start()<=2){
            long now=world.getGameTime();if(soundTick!=now){soundTick=now;sounds=0;}
            if(sounds++<3)world.playLocalSound(p.origin().x,p.origin().y,p.origin().z,VfxTimeline.sound(p.template()),net.minecraft.sounds.SoundSource.PLAYERS,.4f,1,false);
        }
    }
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
        if(e.phase!=TickEvent.Phase.END)return;clean();if(world==null||Minecraft.getInstance().isPaused())return;
        Cod3AfterImages.history();ACTIVE.forEach(Cod3AfterImages::sample);if(world.getGameTime()%4!=0)return;
        var mc=Minecraft.getInstance();boolean low=mc.options.particles().get()==net.minecraft.client.ParticleStatus.MINIMAL;
        int remaining=128;
        for(var p:ACTIVE){
            if(p.sequence().startsWith("equipment_weapon_")||Cod3AfterImages.supports(p))continue;
            if(remaining<=0)break;
            var d=Cod3Catalog.vfx(p.template());double age=world.getGameTime()-p.start();if(age<0||age>=p.duration()||p.sequence().startsWith("scenic_")&&age>40||p.scale()>3)continue;
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
                if(p.entityId()>=0&&!p.sequence().equals("arrow_collapse")){var entity=world.getEntity(p.entityId());
                    if((entity==null||!entity.isAlive())&&(p.template()==4||p.sequence().startsWith("status_")||p.sequence().startsWith("secondary_")||p.sequence().startsWith("equipment_")||p.sequence().equals("vfx_follow")||p.sequence().matches("accessory_proc_[13456]")))continue;
                    if(p.sequence().equals("equipment_beidou_stride")&&entity instanceof net.minecraft.world.entity.player.Player wearer&&com.dynasty.expansion.EquipmentBehaviors.pieces(wearer,"beidou")<4)continue;
                    if(p.sequence().equals("secondary_roots")&&entity instanceof net.minecraft.world.entity.LivingEntity living&&!living.hasEffect(com.dynasty.expansion.ExpansionEffects.STAGGER.get()))continue;
                    if(p.sequence().equals("secondary_coil")&&entity instanceof net.minecraft.world.entity.LivingEntity living&&!living.hasEffect(net.minecraft.world.effect.MobEffects.MOVEMENT_SLOWDOWN))continue;
                    if(entity!=null){if(p.template()==4){if(!entity.isAlive()||entity.getDeltaMovement().lengthSqr()<.0025)continue;direction=entity.getDeltaMovement().normalize();}origin=entity.getPosition(e.getPartialTick());}}
                double distance=origin.distanceTo(camera);if(distance>256||distance<.8)continue;
                if(p.scale()>2){if(distance>96&&farLarge++>=1||distance>32&&distance<=96&&mediumLarge++>=2||distance<=32&&nearLarge++>=3)continue;}
                var d=Cod3Catalog.vfx(p.template());var combat=p.sequence().startsWith("combat_")?VfxInstance.combat(p):null;var timeline=VfxTimeline.timing(d,p.duration());double life=age/p.duration(),expansion=combat==null?timeline.expansion(age):combat.expansion(age),alpha=timeline.alpha(age,p.duration())*.6;
                if(p.template()==4){expansion=1;alpha=.6*(p.sequence().equals("arrow_collapse")?1-life:1);}
                if(Cod3AfterImages.supports(p)&&p.template()!=36)continue; // Registered models are drawn after the primitive buffer is flushed.
                int segments=distance>96?12:distance>32?20:32;
                if(Minecraft.getInstance().options.particles().get()==net.minecraft.client.ParticleStatus.MINIMAL)segments=Math.min(12,segments);
                var geometry=new Geometry(pose.last().pose(),camera,origin,direction,p.scale(),p.tint()==0?(p.template()==27?terrainColor(origin):d.color()):p.tint(),alpha,segments,p.seed(),(d.shape()==DynastyVfxDefinition.Shape.LINE&&d.id()!=10&&d.id()!=34&&d.id()!=28)||d.shape()==DynastyVfxDefinition.Shape.CHAIN);
                if(combat!=null){geometry.draw(p.template(),d,expansion,life,age);geometry.volume(combat.volume(age));continue;}
                if(p.sequence().matches("status_[1-8]"))geometry.status(Integer.parseInt(p.sequence().substring(7)),p.tick()+1,age);
                else if(p.sequence().equals("secondary_roots"))geometry.roots(age);
                else if(p.sequence().equals("secondary_coil"))geometry.coil(age);
                else if(p.sequence().equals("secondary_possession"))geometry.possession(age);
                else if(p.sequence().equals("secondary_echo"))geometry.echo(life);
                else if(p.sequence().equals("secondary_alarm"))geometry.alarm(life);
                else if(p.sequence().matches("accessory_proc_[1-6]"))geometry.proc(Integer.parseInt(p.sequence().substring("accessory_proc_".length())),direction,age,life);
                else if(p.sequence().equals("equipment_weapon_rope_dart")||p.sequence().equals("equipment_weapon_flying_claw"))geometry.weaponTether(p.origin().add(p.direction()),p.sequence().endsWith("flying_claw"),age,life);
                else if(p.sequence().startsWith("equipment_weapon_"))geometry.weapon(p.sequence().substring("equipment_weapon_".length()),age,life,p.tick());
                else if(p.sequence().startsWith("equipment_accessory_"))geometry.accessory(p.sequence().substring("equipment_accessory_".length()),age,life);
                else if(p.sequence().equals("equipment_beidou_stride"))geometry.starStride(age);
                else if(p.sequence().equals("equipment_phoenix_embers"))geometry.phoenixEmbers(age,life);
                else if(p.sequence().equals("equipment_mortuary_breath"))geometry.patientBreath(age,false);
                else if(p.sequence().equals("equipment_mortuary_rescued"))geometry.patientBreath(age,true);
                else if(p.sequence().equals("site_bellows"))geometry.bellows(life);
                else if(p.sequence().equals("site_waterwheel"))geometry.waterwheel(age);
                else if(p.sequence().equals("site_puzzle_press"))geometry.puzzle(life,false);
                else if(p.sequence().equals("site_puzzle_open"))geometry.puzzle(life,true);
                else if(p.sequence().equals("site_tea_flip"))geometry.teaFlip(life);
                else if(p.sequence().equals("site_sword_shadow"))geometry.swordShadow(p.tick(),life);
                else if(p.sequence().equals("qinglong_combo_wave"))geometry.dragonWave(life,age);
                else if(p.sequence().matches("scenic_(0[1-9]|1[0-9]|2[0-5])"))geometry.scenic(Integer.parseInt(p.sequence().substring(7)),life);else{
                    geometry.draw(p.template(),d,expansion,life,p.sequence().equals("arrow_collapse")?20:age);
                    if(p.sequence().isBlank())geometry.volume(VfxVolume.of(d,origin,direction,p.scale(),expansion,age,p.duration()));
                }
            }
            BufferUploader.drawWithShader(BUFFER.end());drawing=false;
            for(var p:ACTIVE)if(Cod3AfterImages.supports(p)){
                double age=world.getGameTime()-p.start()+e.getPartialTick();if(age<0||age>=p.duration())continue;
                double distance=p.origin().distanceTo(camera);boolean low=Minecraft.getInstance().options.particles().get()==net.minecraft.client.ParticleStatus.MINIMAL;
                Cod3AfterImages.render(p,pose,camera,e.getPartialTick(),VfxTimeline.timing(Cod3Catalog.vfx(p.template()),p.duration()).alpha(age,p.duration()),distance>32?1:low?2:6);
            }
        }finally{if(drawing)BUFFER.discard();pose.popPose();}
    }
    /** Average the actual block sprite and biome tint, without terrain mutations or falling entities. */
    private static int terrainColor(Vec3 origin){
        var mc=Minecraft.getInstance();if(mc.level==null)return 0x888888;
        var pos=net.minecraft.core.BlockPos.containing(origin).below();var block=mc.level.getBlockState(pos);
        var sprite=mc.getBlockRenderer().getBlockModelShaper().getParticleIcon(block).contents().getOriginalImage();
        long red=0,green=0,blue=0;int count=0;
        for(int x=0;x<sprite.getWidth();x+=Math.max(1,sprite.getWidth()/4))for(int y=0;y<sprite.getHeight();y+=Math.max(1,sprite.getHeight()/4)){
            int rgba=sprite.getPixelRGBA(x,y);if((rgba>>>24)<128)continue;red+=rgba&255;green+=rgba>>8&255;blue+=rgba>>16&255;count++;
        }
        if(count==0)return 0x888888;int biome=mc.getBlockColors().getColor(block,mc.level,pos,0);if(biome==-1)biome=0xffffff;
        return (int)(red/count*(biome>>16&255)/255)<<16|(int)(green/count*(biome>>8&255)/255)<<8|(int)(blue/count*(biome&255)/255);
    }
    private static final class Geometry {
        final Matrix4f matrix;final Vec3 camera,o,f,r,u;final double scale,alpha;final int color,segments;final long seed;
        Geometry(Matrix4f matrix,Vec3 camera,Vec3 o,Vec3 forward,double scale,int color,double alpha,int segments,long seed){this(matrix,camera,o,forward,scale,color,alpha,segments,seed,false);}
        Geometry(Matrix4f matrix,Vec3 camera,Vec3 o,Vec3 forward,double scale,int color,double alpha,int segments,long seed,boolean pitched){
            this.matrix=matrix;this.camera=camera;this.o=o;Vec3 basis=pitched?forward:new Vec3(forward.x,0,forward.z);
            this.f=basis.lengthSqr()<1e-9?new Vec3(0,0,1):basis.normalize();Vec3 right=new Vec3(0,1,0).cross(f);this.r=right.lengthSqr()<1e-9?new Vec3(1,0,0):right.normalize();this.u=f.cross(r);
            this.scale=scale;this.color=color;this.alpha=alpha;this.segments=segments;this.seed=seed;
        }
        void volume(VfxVolume v){
            if(!v.damaging())return;double stroke=.055/scale;
            switch(v.shape()){
                case LINE->{for(int i=0;i<4;i++){double a=i*Math.PI/2;beam(v.point(Math.cos(a)*v.halfWidth(),Math.sin(a)*v.halfWidth(),0),v.point(Math.cos(a)*v.halfWidth(),Math.sin(a)*v.halfWidth(),v.length()),stroke);}}
                case CHAIN->{for(int branch=0;branch<v.branches();branch++)for(int side:new int[]{-1,1}){
                    Vec3 shift=v.right().scale(side*v.halfWidth()),last=v.centerline(branch,0).add(shift);
                    for(int i=1;i<=32;i++){Vec3 next=v.centerline(branch,i/32.0).add(shift);beam(last,next,stroke);last=next;}
                }}
                case CIRCLE,TARGET_LOCK,ANNULUS,SPHERE,CONE->{
                    double arc=v.shape()==DynastyVfxDefinition.Shape.CONE?v.halfAngle()*2:Math.PI*2;
                    for(int i=0;i<segments;i++){double a=(i/(double)segments-.5)*arc,b=((i+1)/(double)segments-.5)*arc;
                        beam(v.point(Math.sin(a)*v.radius(),.04,Math.cos(a)*v.radius()),v.point(Math.sin(b)*v.radius(),.04,Math.cos(b)*v.radius()),stroke);
                        if(v.shape()==DynastyVfxDefinition.Shape.ANNULUS)beam(v.point(Math.sin(a)*v.innerRadius(),.04,Math.cos(a)*v.innerRadius()),v.point(Math.sin(b)*v.innerRadius(),.04,Math.cos(b)*v.innerRadius()),stroke);
                        if(v.shape()==DynastyVfxDefinition.Shape.SPHERE)beam(v.point(Math.sin(a)*v.radius(),Math.cos(a)*v.radius(),0),v.point(Math.sin(b)*v.radius(),Math.cos(b)*v.radius(),0),stroke);
                    }
                    if(v.shape()==DynastyVfxDefinition.Shape.CONE)for(int side:new int[]{-1,1})beam(v.point(0,.04,0),v.point(Math.sin(side*v.halfAngle())*v.radius(),.04,Math.cos(v.halfAngle())*v.radius()),stroke);
                }
                case BOX,RECT->{
                    if(v.cylinder()){
                        for(int i=0;i<segments;i++){double a=i*Math.PI*2/segments,b=(i+1)*Math.PI*2/segments;
                            for(double y:new double[]{.04,v.height()})beam(v.point(Math.sin(a)*v.radius(),y,Math.cos(a)*v.radius()),v.point(Math.sin(b)*v.radius(),y,Math.cos(b)*v.radius()),stroke);
                        }
                    }else for(int side:new int[]{-1,1})for(double y:new double[]{.04,v.height()}){
                        beam(v.point(-v.radius(),y,side*v.halfLength()),v.point(v.radius(),y,side*v.halfLength()),stroke);
                        beam(v.point(side*v.radius(),y,-v.halfLength()),v.point(side*v.radius(),y,v.halfLength()),stroke);
                    }
                }
            }
        }

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
        // Finite geometric weapons; original server ray, movement, damage and actor ownership remain authoritative.
        void weaponTether(Vec3 endpoint,boolean claw,double age,double life){
            Vec3 hand=p(.18,1.15,.32);double travel=Math.min(1,age/4),retract=Math.max(0,(age-16)/8);
            Vec3 head=hand.lerp(endpoint,travel*(1-retract));int links=Math.min(24,Math.max(6,segments));
            Vec3 last=hand;for(int i=1;i<=links;i++){double t=i/(double)links;Vec3 next=hand.lerp(head,t).add(0,-Math.sin(t*Math.PI)*.22*(1-retract),0);beam(last,next,claw?.025:.017);last=next;}
            Vec3 axis=endpoint.subtract(hand).normalize();if(axis.lengthSqr()<1e-8)return;
            Vec3 side=axis.cross(u).normalize();if(side.lengthSqr()<1e-8)side=r;Vec3 up=side.cross(axis).normalize();
            Vec3 base=head.subtract(axis.scale(claw?.24:.34));double width=claw?.13:.07;
            Vec3 a=base.add(side.scale(width)),b=base.add(up.scale(width)),c=base.subtract(side.scale(width)),d=base.subtract(up.scale(width));
            triangle(head,a,b,.95);triangle(head,b,c,.8);triangle(head,c,d,.65);triangle(head,d,a,.9);
            if(claw)for(int k=0;k<3;k++){double angle=k*Math.PI*2/3;Vec3 finger=side.scale(Math.cos(angle)).add(up.scale(Math.sin(angle)));Vec3 root=base.add(finger.scale(.07)),bend=head.add(finger.scale(.24)).subtract(axis.scale(.09));beam(root,bend,.045);beam(bend,head.add(finger.scale(.12)),.035);}
        }
        void weapon(String id,double age,double life,int charge){
            if(id.equals("meteor_hammer")||id.equals("meteor_charge")){
                boolean charging=id.equals("meteor_charge");double angle=charging?(age+charge)*.22:life*Math.PI*2,radius=charging?.65+Math.min(20,charge)/40.0:1.5+Math.sin(life*Math.PI)*.7;Vec3 hand=p(.2,1.05,.2),head=p(Math.sin(angle)*radius,.85,Math.cos(angle)*radius);int links=Math.min(16,segments);Vec3 last=hand;
                for(int i=1;i<=links;i++){double t=i/(double)links;Vec3 next=hand.lerp(head,t).add(0,-Math.sin(t*Math.PI)*.16,0);beam(last,next,.045);last=next;}
                mesh(Math.sin(angle)*radius,.85,Math.cos(angle)*radius,.24);return;
            }
            if(id.equals("duck_guard")||id.equals("duck_counter")){
                boolean counter=id.equals("duck_counter");for(int k=0;k<(counter?3:1);k++)for(int side:new int[]{-1,1}){
                    double lag=k*.12,a=(counter?life*Math.PI*1.2:Math.PI*.15)+side*.65-lag;Vec3 center=p(side*(.34+.1*Math.cos(a)),1.15,.65+Math.sin(a)*.22);
                    beam(center.add(r.scale(-.18)),center.add(r.scale(.18)),.055);beam(center.add(u.scale(-.24)),center.add(u.scale(.24)),.07);
                    beam(center.add(r.scale(side*.17)),center.add(r.scale(side*.25)).add(f.scale(-.14)),.04);
                }return;
            }
            if(id.equals("repeating_crossbow")||id.equals("siege_crossbow")){
                double recoil=Math.sin(life*Math.PI)*.12;box(.15,1.08,.35-recoil,.22,.10,.18);beam(p(-.22,1.12,.50-recoil),p(.52,1.12,.50-recoil),.035);beam(p(.15,1.12,.32-recoil),p(.15,1.12,.78-recoil),.03);
            }
        }
        void proc(int code,Vec3 direction,double age,double life){
            switch(code){
                case 1->{double length=Math.min(6,direction.length())/scale;for(int strand=0;strand<2;strand++){Vec3 last=p(0,1.1,0);for(int i=1;i<=10;i++){double t=i/10.;Vec3 next=p(Math.sin(t*Math.PI*2+age*.45+strand*Math.PI)*.08,1.1+.10*Math.sin(t*Math.PI),length*t);beam(last,next,.025);last=next;}}}
                case 2->{for(int branch=0;branch<3;branch++){double x=(branch-1)*.28;Vec3 last=p(x,.5,0);for(int i=1;i<=4;i++){Vec3 next=p(x+(i%2==0?-.08:.08),.5+i*.18,0);beam(last,next,.035);if(i==2)beam(next,next.add(r.scale(.12*scale)),.025);last=next;}}}
                case 3,4->{for(int star=0;star<(code==3?5:3);star++){double a=star*Math.PI*2/(code==3?5:3)+life*.8,x=Math.cos(a)*.45,y=1.25+Math.sin(a)*.30;beam(p(x-.10,y,0),p(x+.10,y,0),.025);beam(p(x,y-.14,0),p(x,y+.14,0),.035);}}
                case 5->{for(int strip=0;strip<3;strip++)beam(p(-.38,1+strip*.16,-.08),p(.38,1.15+strip*.16,.08),.035*(1-life)+.01);}
                case 6->{for(int branch=0;branch<2;branch++){Vec3 last=p((branch-.5)*.35,1.8,0);for(int i=1;i<=6;i++){Vec3 next=p((branch-.5)*.35+Math.sin(i*2.1+seed)*.12,1.8-i*.22,0);beam(last,next,.035);if(i==3)beam(next,next.add(r.scale((branch==0?-.2:.2)*scale)).add(0,-.16,0),.018);last=next;}}}
                default->{}
            }
        }
        /** Small item-specific silhouettes, drawn by the same bounded world-space primitives. */
        void accessory(String id,double age,double life){
            double pulse=Math.sin(life*Math.PI),y=1.35+.04*Math.sin(age*.3);
            switch(id){
                case "jade_pendant"->{mesh(0,y,.4,.17);for(int s:new int[]{-1,1}){beam(p(s*.08,y-.18,.4),p(s*.28,y,.4),.025);beam(p(s*.28,y,.4),p(s*.08,y+.18,.4),.025);}}
                case "jade_bi_disc","moon_pendant"->{
                    boolean moon=id.equals("moon_pendant");int count=Math.min(segments,16);double arc=moon?Math.PI*1.6:Math.PI*2;
                    for(int i=0;i<count;i++){double a=(i/(double)count-.5)*arc,b=((i+1)/(double)count-.5)*arc;
                        beam(p(.44+Math.sin(a)*.17,y+.30+Math.cos(a)*.17,-.18),p(.44+Math.sin(b)*.17,y+.30+Math.cos(b)*.17,-.18),moon?.045:.025);}
                    if(moon){mesh(.62,y+.52,-.18,.035);mesh(.30,y+.60,-.18,.025);}else mesh(.44,y+.30,-.18,.045);
                }
                case "gold_seal_charm"->{double z=.42;for(int s:new int[]{-1,1}){beam(p(s*.18,y-.16,z),p(s*.18,y+.16,z),.04);beam(p(-.18,y+s*.16,z),p(.18,y+s*.16,z),.04);}beam(p(-.10,y+.07,z),p(.10,y+.07,z),.025);beam(p(0,y+.12,z),p(0,y-.12,z),.025);beam(p(-.10,y-.04,z),p(.10,y-.04,z),.025);}
                case "dragon_scale_charm"->{for(int i=0;i<3;i++){double x=(i-1)*.18,h=y+.10*Math.abs(i-1);triangle(p(x-.11,h,.40),p(x+.11,h,.40),p(x,h-.20,.43),.72+.08*i);beam(p(x-.11,h,.40),p(x,h-.20,.43),.025);}beam(p(-.24,y+.12,.40),p(0,y+.25,.40),.035);beam(p(0,y+.25,.40),p(.24,y+.12,.40),.035);}
                case "phoenix_feather_charm"->{for(int i=0;i<5;i++){double x=(i-2)*.16,h=y+.12+life*.35;triangle(p(x-.035,h,-.25),p(x+.035,h,-.25),p(x+.08*Math.sin(age*.25+i),h+.28,-.25),.8);beam(p(x,h,-.25),p(x,h+.22,-.25),.025);}}
                case "qilin_horn_charm"->{for(int s:new int[]{-1,1}){beam(p(s*.14,1.95,-.22),p(s*.30,2.12,-.22),.04);beam(p(s*.30,2.12,-.22),p(s*.24,2.34,-.22),.03);beam(p(s*.30,2.12,-.22),p(s*.43,2.22,-.22),.025);}mesh(0,2.01,-.22,.06);}
                case "fox_tail_charm"->{for(int tail=0;tail<3;tail++){Vec3 last=p(0,.85,-.35);for(int i=1;i<=6;i++){double t=i/6.;Vec3 next=p((tail-1)*t*.35+.07*Math.sin(age*.4+i+tail),.85+t*.45,-.35-t*.18);beam(last,next,.065*(1-t)+.02);last=next;}mesh((tail-1)*.35,1.33,-.53,.045*pulse);}}
                case "silk_pouch"->{for(int i=-1;i<=1;i++){beam(p(-.20,.78+i*.08,.4),p(.20,1.02+i*.08,.4),.018);beam(p(-.20,1.02+i*.08,.4),p(.20,.78+i*.08,.4),.018);}beam(p(-.23,.65,.4),p(.23,.65,.4),.022);beam(p(-.23,1.15,.4),p(.23,1.15,.4),.022);}
                case "jade_cicada"->{mesh(0,y,-.35,.08);double flap=.15+.12*Math.sin(age*1.2);for(int s:new int[]{-1,1}){triangle(p(s*.04,y,-.35),p(s*.40,y+flap,-.35),p(s*.32,y-.15,-.35),.85);triangle(p(s*.04,y-.06,-.35),p(s*.30,y-.18-flap*.3,-.35),p(s*.16,y-.30,-.35),.65);beam(p(0,y-.1,-.35),p(s*.32,y+flap*.7,-.35),.018);}}
                default->{} // Unknown sequences never fall back to a large generic healing field.
            }
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
        void swordShadow(int step,double life){
            blade(0,1.2,0,.48);beam(p(-.22,.04,-.18),p(.22,.04,.18),.035);beam(p(-.22,.04,.18),p(.22,.04,-.18),.035);
            if(step==2){beam(p(0,1.1,-.35),p(0,1.1,.65),.035);beam(p(0,1.1,.65),p(-.12,1.1,.4),.035);beam(p(0,1.1,.65),p(.12,1.1,.4),.035);}
            else for(int i=0;i<10;i++){double a=(i/10.0-.5)*Math.PI,b=((i+1)/10.0-.5)*Math.PI;double tilt=step==0?0:.35;beam(p(Math.sin(a)*.5,1.1+Math.sin(a)*tilt,Math.cos(a)*.35),p(Math.sin(b)*.5,1.1+Math.sin(b)*tilt,Math.cos(b)*.35),.025+.012*Math.sin(life*Math.PI));}
        }
        void teaFlip(double life){
            double angle=Math.min(1,life/.65)*Math.PI*.7,cs=Math.cos(angle),sn=Math.sin(angle);
            Vec3 a=p(-.44,.12-.44*sn,-.44*cs),b=p(.44,.12-.44*sn,-.44*cs),c=p(.44,.12+.44*sn,.44*cs),d=p(-.44,.12+.44*sn,.44*cs);
            triangle(a,b,c,.9);triangle(a,c,d,.72);
            for(int x:new int[]{-1,1})for(int z:new int[]{-1,1})beam(p(x*.35,.12+z*.35*sn,z*.35*cs),p(x*.35,.12+z*.35*sn-.45*cs,z*.35*cs+.45*sn),.045);
            for(int i=0;i<5;i++)mesh((i-2)*.11,.35+life*(.3+i*.03),life*.25,.025);
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
        int details(int count){return Math.max(1,Math.min(o.distanceTo(camera)>96?4:count,segments>=32?count:segments>=20?count*2/5:count/4));}
        Geometry colored(int tint,double opacity){return new Geometry(matrix,camera,o,f,scale,tint,alpha*opacity,segments,seed,true);}
        void paper(double x,double y,double z,double width,double height){
            triangle(p(x-width,y-height,z),p(x+width,y-height,z),p(x+width,y+height,z),.8);
            triangle(p(x-width,y-height,z),p(x+width,y+height,z),p(x-width,y+height,z),.95);
            beam(p(x,y-height*.6,z-.005),p(x,y+height*.6,z-.005),.025);
        }
        void fog(double radius,boolean poison,double age){
            if(o.distanceTo(camera)<=32&&segments>12){
                colored(color,.24).orb(radius,radius);
                colored(poison?0x754585:0x40344E,.14).orb(radius*.8,radius);
            }else ring(radius,radius,Math.PI*2);
            int count=details(poison?40:30);
            for(int i=0;i<count;i++){
                double a=i*Math.PI*2/count+age*.03,x=Math.cos(a)*radius*.7,z=Math.sin(a)*radius*.7,y=radius+Math.sin(a*2)*radius*.6;
                if(poison){mesh(x,y,z,.07);beam(p(x-.13,y,z),p(x+.13,y,z),.025);}
                else beam(p(x,y,z),p(x+Math.cos(a)*.3,y+.18,z+Math.sin(a)*.3),.035);
            }
        }
        void sparks(int count,double radius,double y,double age,boolean inward){
            var random=new Random(seed+311);int n=details(count);
            for(int i=0;i<n;i++){double a=random.nextDouble()*Math.PI*2+age*.04,r=radius*(inward?1-(age*.055+i*.11)%1:.3+.7*random.nextDouble());
                double h=y+Math.sin(age*.13+i)*.25;mesh(Math.cos(a)*r,h,Math.sin(a)*r,.035+random.nextDouble()*.025);}
        }
        void rune(double radius,double y,double rotation){
            ring(radius,y,Math.PI*2);ring(radius*.75,y,Math.PI*2);
            for(int i=0;i<8;i++){double a=i*Math.PI/4+rotation,x=Math.sin(a)*radius*.86,z=Math.cos(a)*radius*.86;
                for(int j=-1;j<=1;j++){double along=j*.1;beam(p(x+Math.cos(a)*.22+Math.sin(a)*along,y,z-Math.sin(a)*.22+Math.cos(a)*along),p(x-Math.cos(a)*.22+Math.sin(a)*along,y,z+Math.sin(a)*.22+Math.cos(a)*along),.035);}
            }
            for(int i=0;i<8;i++){double a=i*Math.PI/4+rotation,b=a+3*Math.PI/4;beam(p(Math.sin(a)*radius*.7,y,Math.cos(a)*radius*.7),p(Math.sin(b)*radius*.7,y,Math.cos(b)*radius*.7),.035);}
        }
        void hemisphere(double radius,double y){
            int rings=segments<=12?3:6;
            for(int j=0;j<rings;j++)for(int i=0;i<segments;i++){
                double a=i*Math.PI*2/segments,b=(i+1)*Math.PI*2/segments,t=j*Math.PI/(2*rings),v=(j+1)*Math.PI/(2*rings);
                Vec3 aa=p(Math.cos(t)*Math.cos(a)*radius,y+Math.sin(t)*radius,Math.cos(t)*Math.sin(a)*radius),ab=p(Math.cos(t)*Math.cos(b)*radius,y+Math.sin(t)*radius,Math.cos(t)*Math.sin(b)*radius),ba=p(Math.cos(v)*Math.cos(a)*radius,y+Math.sin(v)*radius,Math.cos(v)*Math.sin(a)*radius),bb=p(Math.cos(v)*Math.cos(b)*radius,y+Math.sin(v)*radius,Math.cos(v)*Math.sin(b)*radius);
                triangle(aa,ab,ba,.8);triangle(ba,ab,bb,.9);
            }
        }
        void draw(int id,DynastyVfxDefinition d,double expand,double life,double age){
            double radius=d.radius()*expand,angle=age*.06;
            double collapse=VfxTimeline.timing(d,d.duration()).collapse(life*d.duration(),d.duration());Random random=new Random(seed);
            switch(id){
                case 1,3,34 -> {
                    beam(p(0,id==34?.04:0,0),p(0,id==34?.04:0,d.length()*expand),d.width());
                    if(id==3)mesh(0,0,d.length()*expand,.14);
                    if(id==1||id==34)for(int side:new int[]{-1,1})for(int i=0;i<details(12);i++){
                        double z=(i+.5)*d.length()*expand/details(12);beam(p(side*d.width()*.5,.05,z),p(side*(d.width()*.5+.25),.2,z-.35),.035);
                    }
                }
                case 2 -> {ring(radius,.06,Math.toRadians(70));ring(radius*.88,.12,Math.toRadians(70));}
                case 4 -> {beam(p(0,0,-Math.min(4,age*.2)),p(0,0,0),.08);mesh(0,0,0,.18);}
                case 5 -> {
                    ring(radius,.1,Math.PI*2);
                    var flame=colored(color,.2);for(int i=0;i<segments;i++){double a=i*Math.PI*2/segments,b=(i+1)*Math.PI*2/segments;flame.triangle(p(Math.cos(a)*radius,0,Math.sin(a)*radius),p(Math.cos(b)*radius,0,Math.sin(b)*radius),p(Math.cos(a)*radius,d.length()*expand,Math.sin(a)*radius),.8);flame.triangle(p(Math.cos(b)*radius,0,Math.sin(b)*radius),p(Math.cos(b)*radius,d.length()*expand,Math.sin(b)*radius),p(Math.cos(a)*radius,d.length()*expand,Math.sin(a)*radius),.9);}
                    for(int i=0;i<details(12);i++){double a=i*Math.PI*2/details(12)+angle;Vec3 last=p(Math.cos(a)*radius*.85,0,Math.sin(a)*radius*.85);
                        for(int j=1;j<=6;j++){double t=j/6.;Vec3 next=p(Math.cos(a+t)*radius*(1-t*.2),d.length()*expand*t,Math.sin(a+t)*radius*(1-t*.2));beam(last,next,.18*(1-t*.4));last=next;}}
                }
                case 6 -> {for(int branch=0;branch<(segments>12?3:1);branch++){
                    Vec3 last=p(0,d.length()*expand,0);for(int i=1;i<=8;i++){double t=i/8.,x=(random.nextDouble()-.5)*radius,z=(random.nextDouble()-.5)*radius;Vec3 next=p(x,d.length()*expand*(1-t),z);beam(last,next,.12);last=next;}
                    ring(radius,.04,Math.PI*2);
                }}
                case 31 -> {beam(p(0,d.length()*expand,0),p(0,0,0),.1);ring(radius,.04,Math.PI*2);for(int i=0;i<details(8);i++){double a=i*Math.PI/4;beam(p(Math.sin(a)*radius*.6,.05,Math.cos(a)*radius*.6),p(Math.sin(a+.25)*radius,.1,Math.cos(a+.25)*radius),.04);}}
                case 7 -> {ring(radius,.06,Math.PI*2);for(int i=0;i<3;i++)ring(Math.max(0,radius-d.width()*i/3),d.length()*expand*i/3,Math.PI*2);}
                case 8 -> {ring(radius,.04,Math.PI*2);for(int i=0;i<details(24);i++){double a=i*Math.PI*2/details(24);mesh(Math.cos(a)*radius,d.length()*expand*.5,Math.sin(a)*radius,d.length()*expand*.5);}}
                case 9 -> {for(int j=0;j<(segments<=12?1:3);j++){Vec3 last=p(radius,0,0);for(int i=1;i<=segments;i++){double t=i/(double)segments,a=t*Math.PI*6+angle+j*2.1;Vec3 next=p(Math.cos(a)*radius,t*d.length()*expand,Math.sin(a)*radius);beam(last,next,.08);last=next;}}}
                case 10 -> {for(int i=0;i<10;i++){double z=i*d.length()*expand/10;beam(p((i%2-.5)*d.width(),.04,z),p(((i+1)%2-.5)*d.width(),.04,z+d.length()*expand/10),.06);}for(int i=0;i<details(20);i++)mesh((random.nextDouble()-.5)*d.width(),Math.sin(life*Math.PI)*.6,random.nextDouble()*d.length()*expand,.15);}
                case 27 -> {for(int i=0;i<details(30);i++){double a=random.nextDouble()*Math.PI*2,r=random.nextDouble()*d.radius()*Math.min(1,age/6);double height=Math.max(0,age*.15-age*age*.011)*(.3+.7*random.nextDouble());box(Math.cos(a)*r,height,Math.sin(a)*r,.07+random.nextDouble()*.1,.12,.09);}colored(color,.4).sparks(20,d.radius(),.15,age,false);}
                case 11,32 -> fog(radius,id==32,age);
                case 12 -> {ring(radius,.04,Math.PI*2);for(int i=0;i<details(30);i++){double a=i*Math.PI*2/details(30);mesh(Math.cos(a)*radius,.06+Math.sin(a+age*.1)*.1,Math.sin(a)*radius,.045);}}
                case 25 -> {ring(radius,.04,Math.PI*2);for(int j=1;j<=4;j++)ring(radius*(1-j*.17),-.5*j/4,Math.PI*2);for(int i=0;i<details(30);i++){double a=i*Math.PI*2/details(30)+angle,r=radius*(1-life);beam(p(Math.sin(a)*r,.1,Math.cos(a)*r),p(Math.sin(a+.25)*r*.8,.06,Math.cos(a+.25)*r*.8),.035);}}
                case 26 -> {double shock=6+(d.radius()-6)*expand;ring(shock,.04,Math.PI*2);ring(Math.max(0,shock-d.width()),.06,Math.PI*2);colored(0xD7C7A4,.55).sparks(30,shock,.2,age,false);}
                case 13,17 -> {
                    var volume=VfxVolume.of(d,o,f,scale,expand,age);
                    for(int branch=0;branch<volume.branches();branch++){Vec3 last=volume.centerline(branch,0);for(int i=1;i<=32;i++){Vec3 next=volume.centerline(branch,i/32.);beam(last,next,d.width());last=next;}}
                    if(id==17){int n=details(60);for(int i=0;i<n;i++){double t=i/(double)n,x=Math.sin(t*Math.PI*4+angle)*d.radius()*.65,y=Math.sin(t*Math.PI*2+angle)*d.radius()*.3;mesh(x,y,t*d.length()*expand,.08);}Vec3 head=volume.centerline(0,1);beam(head,head.add(u.scale(.5*scale)),.07);beam(head,head.add(r.scale(.4*scale)).add(f.scale(.4*scale)),.08);}
                }
                case 24 -> {
                    // The jagged core plus its ribbon always fits inside the advertised two-block corridor.
                    double width=(.5+expand*1.5)*(1-collapse),jag=.12;Vec3 last=p(0,0,0);
                    for(int i=1;i<=12;i++){double x=(random.nextDouble()-.5)*jag,y=(random.nextDouble()-.5)*jag;Vec3 next=p(x,y,i*d.length()*expand/12);beam(last,next,Math.max(.02,width-2*jag));last=next;}
                    var stars=colored(0xEEF2FF,.9);for(int i=0;i<details(20);i++)stars.mesh((random.nextDouble()-.5)*Math.max(0,width-2*jag),0,random.nextDouble()*d.length()*expand,.045);
                    if(collapse>0)for(int i=0;i<details(20);i++)mesh((random.nextDouble()-.5)*width,random.nextDouble()*.6*collapse,random.nextDouble()*d.length(),.08);
                }
                case 14 -> {colored(color,.65).orb(radius,radius);var flame=colored(0xBDEAFF,.9);for(int i=0;i<details(16);i++){double a=i*Math.PI*2/details(16)+angle,x=Math.cos(a)*radius*.55,z=Math.sin(a)*radius*.55,y=radius+Math.sin(a*2+age*.15)*radius*.35;flame.triangle(p(x-.06,y,z),p(x+.06,y,z),p(x+.035*Math.sin(age*.3+i),y+.3,z),.9);}}
                case 33 -> {double core=radius*.3*(1-collapse);colored(0x000000,.9).orb(core,radius);var horizon=colored(0x8A2AFF,.85);double wave=collapse>0?d.radius()*(.3+.7*collapse):radius;horizon.ring(wave,radius,Math.PI*2);horizon.ring(wave*.85,radius+.15,Math.PI*2);horizon.sparks(60,radius,radius,age,true);if(collapse==0)for(int i=0;i<3;i++)horizon.ring(core*(1.3+i*.3),radius+i*.12,Math.PI*2);}
                case 15 -> {double shrink=life>=.5&&collapse==0?1-(life-.5)*.5:1;radius*=shrink;ring(radius,.04,Math.PI*2);int n=details(32);for(int i=0;i<n;i++){double a=i*Math.PI*2/n;paper(Math.sin(a)*radius,.6+.15*Math.sin(angle+i),Math.cos(a)*radius,.14*(1-collapse),.28*(1-collapse));}for(int i=0;i<details(36);i++){double a=i*Math.PI*2/36,b=a+Math.PI*5/6;beam(p(Math.sin(a)*radius,.05,Math.cos(a)*radius),p(Math.sin(b)*radius,.05,Math.cos(b)*radius),.025);}if(collapse>0)colored(0x302018,.7).sparks(20,radius+collapse*2,.2+collapse,age,false);}
                case 16 -> {double height=d.length()*expand,lower=height*.5*collapse,upper=height*(1-.5*collapse),spin=angle*(life>16./28?2:1);var ink=colored(0x101018,.8);ink.rune(radius,lower+.04,spin);var gold=colored(0xC0A020,.95);gold.rune(radius,upper+.04,-spin);for(int i=0;i<8;i++){double a=i*Math.PI/4,x=Math.sin(a)*radius,z=Math.cos(a)*radius;gold.beam(p(x,lower,z),p(x,upper,z),.05);}gold.sparks(40,radius,height*.5,age,false);if(collapse>.6)for(int i=0;i<details(16);i++)mesh(Math.sin(i)*radius,lower+(collapse-.6)*2,Math.cos(i)*radius,.09);}
                case 20 -> {double sink=-.4*collapse;decal(radius,6,0);for(int side:new int[]{-1,1})for(int i=0;i<3;i++){double z=(i-1)*radius*.45;beam(p(-radius*.6,.04+sink,z),p(radius*.6,.04+sink,z),.055);beam(p(side*radius*.3,.04+sink,-radius*.7),p(side*radius*.3,.04+sink,radius*.7),.055);}mesh(0,.12+sink,radius*.85,.3);for(int i=0;i<4;i++){double a=i*Math.PI/2+Math.PI/4;beam(p(Math.cos(a)*radius*.65,.04+sink,Math.sin(a)*radius*.65),p(Math.cos(a)*radius*.9,.04+sink,Math.sin(a)*radius*.9),.14);}Vec3 last=p(radius,0,0);for(int i=1;i<=segments;i++){double a=i*Math.PI*2/segments,r=radius*(.75+.12*Math.sin(a*3+angle));Vec3 next=p(Math.cos(a)*r,.08+sink,Math.sin(a)*r);beam(last,next,.12);last=next;}var water=colored(0x668FA0,.65);for(int i=0;i<details(40);i++){double a=i*Math.PI*2/details(40)+angle,r=radius*(.65+.35*((age*.07+i*.13)%1));Vec3 middle=p(Math.cos(a)*r,.06+sink,Math.sin(a)*r);water.beam(middle.add(this.r.scale(.13*scale)),middle.add(f.scale(.08*scale)),.035);water.beam(middle.add(f.scale(.08*scale)),middle.subtract(this.r.scale(.13*scale)),.035);}}
                case 40 -> {decal(radius,4,0);for(int i=0;i<4;i++){
                    double a=i*Math.PI/2;Vec3 center=o.add(Math.cos(a)*radius*.6*scale,.08,Math.sin(a)*radius*.6*scale);int tint=new int[]{0x6BE0C0,0xFF8A30,0xE8E0C8,0x1A2A3A}[i];
                    var beast=new Geometry(matrix,camera,center,new Vec3(0,0,1),scale*.35,tint,alpha,Math.min(segments,12),seed+i);
                    beast.sparks(10,1.5,.08,age,false);
                    switch(i){case 0->beast.spline(5,.6,angle);case 3->{beast.ring(1.6,.04,Math.PI*2);beast.decal(1.2,6,0);}case 2->{beast.box(0,.1,0,.8,.45,1.2);beast.mesh(0,.5,1.3,.4);for(int leg=0;leg<4;leg++)beast.beam(beast.p(leg%2==0?-.8:.8,.1,leg<2?-.8:.8),beast.p(leg%2==0?-1.1:1.1,.04,leg<2?-.9:.9),.12);}case 1->{for(int feather=0;feather<8;feather++){double t=(feather/7.-.5)*Math.PI/2;beast.beam(beast.p(0,.1,0),beast.p(Math.sin(t)*2.4,.1,Math.cos(t)*2.4),.15);}}}
                }}
                // World-anchored sequence previews have no equipment snapshot. Actor cues use Cod3AfterImages.
                case 18 -> {for(int i=0;i<details(6);i++){box(0,.3,-i*.65,.4,.65,.8);mesh(0,.9,1-i*.65,.4);}}
                case 23 -> {for(int i=0;i<details(5);i++){box((i-2)*.5,.1,-i*.65,.2,1.1,.15);mesh((i-2)*.5,1.5,-i*.65,.3);}}
                case 29 -> {for(int i=0;i<details(6);i++){double a=life*Math.PI-i*.2;blade(Math.sin(a)*1.3,.8,Math.cos(a)*1.3,.8);}}
                case 19 -> {int n=details(12);for(int i=0;i<n;i++){double a=(i/(double)Math.max(1,n-1)-.5)*Math.PI/2;Vec3 tip=p(Math.sin(a)*radius,.4,Math.cos(a)*radius);triangle(p(0,.1,0),tip.add(r.scale(.12*scale)),tip.subtract(r.scale(.12*scale)),.9);beam(p(0,.1,0),tip,.055);}var fire=colored(0xFFDA66,.85);for(int i=0;i<details(40);i++){double a=(random.nextDouble()-.5)*Math.PI/2,r=radius*Math.sqrt(random.nextDouble());fire.mesh(Math.sin(a)*r,.35+random.nextDouble()*.2,Math.cos(a)*r,.04);}}
                case 21,30 -> {int n=details(id==30?72:40);for(int i=0;i<n;i++){double a=id==30?i*Math.PI*2/n+angle:random.nextDouble()*Math.PI*2,r=id==30?radius*(.3+.7*(i%3)/2.):Math.sqrt(random.nextDouble())*radius,y=id==30?12*(1-collapse):12*(1-Math.min(1,(Math.max(0,age-2)+i*.2)%12/8));if(id==30)blade(Math.cos(a)*r,y,Math.sin(a)*r,.8);else{mesh(Math.cos(a)*r,y,Math.sin(a)*r,.15);if(i<details(8))beam(p(Math.cos(a)*r,y,Math.sin(a)*r),p(Math.cos(a)*r,y+2,Math.sin(a)*r),.04);}}if(id==30)ring(radius,12*(1-collapse),Math.PI*2);}
                case 22 -> {double growth=Math.max(.1,expand);var spirit=new Geometry(matrix,camera,o,f,scale*growth,color,alpha*.65,segments,seed);spirit.box(0,2,0,1.1,3,.6);spirit.mesh(0,7,0,1);spirit.box(-.7,0,0,.5,2,.45);spirit.box(.7,0,0,.5,2,.45);spirit.beam(spirit.p(-1,4.8,0),spirit.p(-2.7,3.5,0),.55);spirit.beam(spirit.p(1,4.8,0),spirit.p(2.7,3.5,0),.55);spirit.ring(1.8,7,Math.PI*2);}
                case 28 -> {beam(p(0,0,0),p(0,24*expand,0),1.5*(1-collapse));ring(.75,.04,Math.PI*2);for(int i=0;i<details(40);i++){double a=random.nextDouble()*Math.PI*2,y=((age*.5+i*.6)%24)*expand;mesh(Math.cos(a)*.6,y,Math.sin(a)*.6,.055);}}
                case 35 -> {ring(radius,.04,Math.PI*2);int n=details(24);for(int i=0;i<n;i++){double a=i*Math.PI*2/n,lean=d.width()/2+(collapse==0&&life>1./3?(life-1./3)*.4:0),height=d.length()*expand*(1-collapse);beam(p(Math.cos(a)*radius,0,Math.sin(a)*radius),p(Math.cos(a)*(radius-lean),height,Math.sin(a)*(radius-lean)),.12);mesh(Math.cos(a)*(radius-lean),height,Math.sin(a)*(radius-lean),.15);}if(collapse>0)colored(0xD3C9B5,.8).sparks(16,radius,.1+Math.sin(collapse*Math.PI),age,false);}
                case 36 -> {
                    double z=.6;ring(radius,.04,Math.PI/3);var shine=colored(0xD5E5CE,.45);for(int i=0;i<segments;i++){double a=(i/(double)segments-.5)*Math.PI/3,b=((i+1)/(double)segments-.5)*Math.PI/3;shine.triangle(p(0,.045,0),p(Math.sin(a)*radius,.045,Math.cos(a)*radius),p(Math.sin(b)*radius,.045,Math.cos(b)*radius),.7);}
                    if(collapse==0){for(int i=0;i<segments;i++){double a=i*Math.PI*2/segments,b=(i+1)*Math.PI*2/segments;triangle(p(0,1.5,z),p(Math.sin(a),1.5+Math.cos(a)*1.4,z),p(Math.sin(b),1.5+Math.cos(b)*1.4,z),.8);}}
                    else for(int i=0;i<details(12);i++){double a=i*Math.PI*2/details(12),x=Math.sin(a)*collapse*2,y=1.5+Math.cos(a)*collapse*2;triangle(p(x-.1,y-.1,z+collapse*.3),p(x+.12,y-.06,z+collapse*.3),p(x,y+.17,z+collapse*.3),.8);}
                }
                case 37 -> {double z=VfxTimeline.bloodOffset(life*d.duration(),d.duration());triangle(p(-radius,0,z-d.width()/2),p(radius,0,z-d.width()/2),p(radius,d.length()*expand,z),.8);triangle(p(-radius,0,z-d.width()/2),p(radius,d.length()*expand,z),p(-radius,d.length()*expand,z),.8);for(int i=0;i<details(60);i++)mesh((random.nextDouble()-.5)*radius*2,d.length()*expand+Math.sin(angle+i)*.15,z,.045);}
                case 38 -> {double y=6*(1-expand);box(0,y+.04,0,1.5,.1,1.2);for(int i=0;i<5;i++){double x=(i-2)*.6;beam(p(x,y+.05,1),p(x,y+.05,2.5-(i%4==0?.6:0)),.38);}colored(0x655426,.45).box(0,.045,0,1.5,.01,1.2);ring(radius,.04,Math.PI*2);sparks(40,radius,.12+collapse,age,false);}
                case 39 -> {double y=12*(1-expand*expand),mix=Math.min(1,age/14);int tint=((int)(255)<<16)|((int)(176*(1-mix)+74*mix)<<8)|(int)(32*(1-mix)+26*mix);var fire=colored(tint,.85);if(collapse==0){fire.orb(radius,y+radius);for(int i=0;i<details(40);i++)fire.beam(p(Math.sin(i)*radius*.6,y+radius,Math.cos(i)*radius*.6),p(Math.sin(i)*radius*.6,y+radius+3,Math.cos(i)*radius*.6),.04);}else{fire.hemisphere(d.radius()*(.5+.5*collapse),.03);fire.sparks(40,d.radius(),.15+collapse,age,false);ring(d.radius(),.04,Math.PI*2);}}
                default -> {}
            }
        }
    }
    private Cod3VfxRenderer(){}
}
