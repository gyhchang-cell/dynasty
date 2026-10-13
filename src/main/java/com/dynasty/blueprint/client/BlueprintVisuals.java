package com.dynasty.blueprint.client;

import com.dynasty.blueprint.BlueprintVisualEvent;
import com.dynasty.blueprint.BlueprintEntities;
import com.dynasty.blueprint.TemplateMob;
import net.minecraft.client.Minecraft;
import net.minecraft.client.ParticleStatus;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.ClientPlayerNetworkEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Vector3f;
import java.util.LinkedHashMap;
import java.util.UUID;
import java.util.ArrayList;

/** Bounded world-space hints and finite translucent glare; no camera or input mutation. */
@Mod.EventBusSubscriber(modid="dynasty", value=Dist.CLIENT)
public final class BlueprintVisuals {
    private record Key(UUID caster, long started) {}
    private static final LinkedHashMap<Key, BlueprintVisualEvent> ACTIVE = new LinkedHashMap<>();
    private static ResourceLocation world;
    private static final ArrayList<Integer> SUPPORTS = new ArrayList<>();
    private static final ArrayList<Integer> SHIELDS = new ArrayList<>();
    @SubscribeEvent public static void glare(net.minecraftforge.client.event.RenderGuiOverlayEvent.Post event) {
        if(!event.getOverlay().id().equals(net.minecraftforge.client.gui.overlay.VanillaGuiOverlay.HOTBAR.id()))return;
        var mc=Minecraft.getInstance();if(mc.player==null||!mc.player.isAlive()||mc.options.hideGui)return;
        var haze=mc.player.getEffect(com.dynasty.blueprint.elite.EliteContent.FOX_HAZE.get());
        if(haze!=null){
            int w=mc.getWindow().getGuiScaledWidth(),h=mc.getWindow().getGuiScaledHeight(),a=Math.min(42,haze.getDuration()*3),pink=0xDE92BB;
            var g=event.getGuiGraphics();g.fillGradient(0,0,w,h/5,(a<<24)|pink,pink);g.fillGradient(0,h*4/5,w,h,pink,(a<<24)|pink);
            g.fill(0,h/5,w/16,h*4/5,((a/2)<<24)|pink);g.fill(w*15/16,h/5,w,h*4/5,((a/2)<<24)|pink);
        }
        var effect=mc.player.getEffect(BlueprintEntities.LANTERN_GLARE.get());if(effect==null)return;
        int width=mc.getWindow().getGuiScaledWidth(),height=mc.getWindow().getGuiScaledHeight();
        int color=effect.getAmplifier()>=2?0xE6C54A:effect.getAmplifier()>0?0x62D994:0xFFF9E6;
        int alpha=Math.min(48,Math.max(0,effect.getDuration())*3);var gui=event.getGuiGraphics();
        // Under25% combined opacity around the edges, under5% over the centre; expires with native effect sync.
        gui.fill(0,0,width,height,((alpha/4)<<24)|color);
        gui.fillGradient(0,0,width,height/4,(alpha<<24)|color,color);
        gui.fillGradient(0,height*3/4,width,height,color,(alpha<<24)|color);
    }
    private BlueprintVisuals() {}
    public static void accept(BlueprintVisualEvent p) {
        var mc=Minecraft.getInstance();
        if(mc.level==null || !mc.level.dimension().location().equals(p.dimension())) return;
        if(p.cancelled()) {ACTIVE.entrySet().removeIf(e->e.getKey().caster.equals(p.entityUuid()) && e.getKey().started<=p.started());return;}
        if(mc.level.getGameTime()-p.started()>p.duration()) return;
        var key=new Key(p.entityUuid(),p.started());
        if(ACTIVE.containsKey(key)) return;
        ACTIVE.entrySet().removeIf(e->e.getKey().caster.equals(p.entityUuid()));
        while(ACTIVE.size()>=64) ACTIVE.remove(ACTIVE.keySet().iterator().next());
        ACTIVE.put(key,p);
    }
    @SubscribeEvent public static void logout(ClientPlayerNetworkEvent.LoggingOut e) { ACTIVE.clear();SUPPORTS.clear();SHIELDS.clear();world=null; }
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event) {
        if(event.phase!=TickEvent.Phase.END) return;
        var mc=Minecraft.getInstance();
        if(mc.level==null) {ACTIVE.clear();SUPPORTS.clear();SHIELDS.clear();world=null;return;}
        var dim=mc.level.dimension().location();
        if(world!=null && !world.equals(dim)) {ACTIVE.clear();SUPPORTS.clear();SHIELDS.clear();} world=dim;
        if(mc.isPaused()) return;
        long now=mc.level.getGameTime();
        int budget=mc.options.particles().get()==ParticleStatus.MINIMAL?8:mc.options.particles().get()==ParticleStatus.DECREASED?24:48;
        if(now%5==0){int shells=0;for(var entity:mc.level.entitiesForRendering()){
            if(budget<=0||shells>=8)break;
            if(!(entity instanceof com.dynasty.blueprint.elite.Alchemist caster)||!caster.shellActive()||mc.gameRenderer.getMainCamera().getPosition().distanceToSqr(caster.position())>48*48)continue;
            int count=Math.min(3,budget);budget-=count;shells++;for(int i=0;i<count;i++){double angle=now*.12+i*Math.PI*2/3;mc.level.addParticle(new DustParticleOptions(new Vector3f(.9F,.65F,.25F),.8F),caster.getX()+Math.cos(angle)*.8,caster.getY()+.5+i*.4,caster.getZ()+Math.sin(angle)*.8,0,.01,0);}
        }}
        // At most eight nearby live birds contribute one central-stump drip every six ticks.
        if(now%6==0){int birds=0;for(var entity:mc.level.entitiesForRendering()){
            if(budget<=0||birds>=8)break;
            if(!(entity instanceof com.dynasty.blueprint.elite.GhostCarriageBird bird)||!bird.isAlive()
                ||mc.gameRenderer.getMainCamera().getPosition().distanceToSqr(bird.position())>48*48)continue;
            var at=bird.position().add(bird.getLookAngle().multiply(.3,0,.3)).add(0,1.4,0);
            mc.level.addParticle(new DustParticleOptions(new Vector3f(.28F,.025F,.045F),.55F),at.x,at.y,at.z,0,-.08,0);birds++;budget--;
        }}
        // Entity metadata survives tracking/rejoin; the possession beam outlives the brief casting event.
        if(now%10==0) {
            SUPPORTS.clear();SHIELDS.clear();
            for(var entity:mc.level.entitiesForRendering()) {
                if(entity instanceof TemplateMob mob && mob.kind()==TemplateMob.Kind.PRIEST && mob.isAlive()
                        && mob.buffTargetId()>=0 && mc.gameRenderer.getMainCamera().getPosition().distanceToSqr(mob.position())<=48*48)
                    if(SUPPORTS.size()<32) SUPPORTS.add(mob.getId());
                if(entity instanceof TemplateMob mob && mob.kind()==TemplateMob.Kind.SHIELD && mob.isAlive()
                        && SHIELDS.size()<24 && mc.gameRenderer.getMainCamera().getPosition().distanceToSqr(mob.position())<=24*24)
                    SHIELDS.add(mob.getId());
                if(SUPPORTS.size()>=32 && SHIELDS.size()>=24) break;
            }
        }
        for(int id:SUPPORTS) {
            if(budget<=0 || (now+id)%3!=0 || !(mc.level.getEntity(id) instanceof TemplateMob caster) || !caster.isAlive()) continue;
            if(!(mc.level.getEntity(caster.buffTargetId()) instanceof net.minecraft.world.entity.LivingEntity target)
                    || !target.isAlive() || !(target instanceof TemplateMob linked && linked.isPossessed())
                    || caster.distanceToSqr(target)>16*16) continue;
            int count=Math.min(6,budget);budget-=count;
            var dust=new DustParticleOptions(new Vector3f(.78F,.12F,.19F),.7F);
            for(int i=0;i<count;i++) {
                double u=(i+(now*.06)%1)/count;
                var at=caster.position().add(0,caster.getBbHeight()*.7,0).lerp(target.position().add(0,target.getBbHeight()*.6,0),u);
                mc.level.addParticle(dust,at.x,at.y,at.z,0,.005,0);
            }
        }
        for(int id:SHIELDS) {
            if(budget<=0 || (now+id)%10!=0 || !(mc.level.getEntity(id) instanceof TemplateMob mob)
                    || !mob.isAlive() || !mob.onGround() || mob.getDeltaMovement().horizontalDistanceSqr()<.0005) continue;
            var state=mc.level.getBlockState(mob.blockPosition().below());
            if(state.isAir())continue;
            var chips=new BlockParticleOption(ParticleTypes.BLOCK,state);
            for(int i=0;i<2 && budget>0;i++,budget--) {
                double side=i==0?-.24:.24;
                mc.level.addParticle(chips,mob.getX()+side,mob.getY()+.05,mob.getZ(),side*.05,.03,0);
            }
        }
        var iterator=ACTIVE.entrySet().iterator();
        while(iterator.hasNext()) {
            var p=iterator.next().getValue(); var caster=mc.level.getEntity(p.entityId()); long age=now-p.started();
            boolean death=p.key().startsWith("death_");
            if(!p.dimension().equals(dim) || age>p.duration()+4 || age< -20
                    || caster!=null && (!caster.getUUID().equals(p.entityUuid()) || !death && !caster.isAlive())) {iterator.remove();continue;}
            if(caster==null || age<0 || budget<=0 || (now+p.entityId())%3!=0 || mc.gameRenderer.getMainCamera().getPosition().distanceToSqr(caster.position())>48*48)continue;
            if(death) {
                budget-=deathParticles(mc,p,age,budget);
                continue;
            }
            if(p.key().startsWith("kite_")){
                if(!(caster instanceof com.dynasty.blueprint.boss.WoodKite kite))continue;
                if(p.key().equals("kite_bombs"))continue;
                if(p.key().equals("kite_wing_cut")&&age>=56||p.key().equals("kite_claws")&&age>=36||p.key().equals("kite_wind")&&age>=104||p.key().equals("kite_lightning")&&age>=81||p.key().equals("kite_meteor")&&age>=81)continue;
                int count=Math.min(8,budget);budget-=count;var f=p.direction().multiply(1,0,1).normalize();var side=new Vec3(-f.z,0,f.x);var color=new Vector3f(.58F,.36F,.67F);
                for(int i=0;i<count;i++){Vec3 at;double a=i*Math.PI*2/count;
                    if(p.key().equals("kite_claws"))at=kite.lockedPoint().add(Math.cos(a)*2.2,.08,Math.sin(a)*2.2);
                    else if(p.key().equals("kite_lightning")){int mark=i/2;long impact=32+mark*16;if(age>=impact)continue;at=kite.lightningPoint(mark).add(Math.cos(a)*4,.08,Math.sin(a)*4);}
                    else if(p.key().equals("kite_meteor")){double radius=age<68?20:1+(age-68)/12D*19;at=kite.centre().add(Math.cos(a)*radius,.08,Math.sin(a)*radius);color=age>=58?new Vector3f(.93F,.55F,.12F):color;}
                    else if(p.key().equals("kite_wind")){double angle=Math.toRadians(-45+90D*i/Math.max(1,count-1));at=caster.position().add(f.scale(Math.cos(angle)*24)).add(side.scale(Math.sin(angle)*24));at=new Vec3(at.x,kite.centre().y+.08,at.z);}
                    else if(age<24){double u=i/2D/Math.max(1,(count-2)/2D)*32;at=kite.centre().add(f.scale(-16+u)).add(side.scale(9*Math.sin(Math.PI*u/32)+(i%2==0?2.8:4.5))).add(0,.08,0);}
                    else {at=kite.wingOrigin(side).add(side.scale(1.7*i/Math.max(1,count-1)));}
                    mc.level.addParticle(new DustParticleOptions(color,.8F),at.x,at.y,at.z,0,.008,0);
                }continue;
            }
            if(p.key().startsWith("wuwang_")){
                if(!(caster instanceof com.dynasty.blueprint.boss.BlindMarshal marshal))continue;
                if(p.key().equals("wuwang_trample")&&age>=68||p.key().equals("wuwang_slash")&&age>=p.windup()+1||p.key().equals("wuwang_listen")&&age>=80||p.key().equals("wuwang_arrows")&&age>=25||p.key().equals("wuwang_onslaught")&&age>=72||p.key().equals("wuwang_storm")&&age>=128)continue;
                int count=Math.min(8,budget);budget-=count;var f=p.direction().multiply(1,0,1).normalize();var colour=new Vector3f(.55F,.38F,.32F);
                for(int i=0;i<count;i++){double a=i*Math.PI*2/count;Vec3 at;
                    if(p.key().equals("wuwang_trample"))at=marshal.lockedPoint().add(Math.cos(a)*3,.1,Math.sin(a)*3);
                    else if(p.key().equals("wuwang_listen"))at=caster.position().add(Math.cos(a)*2,.4,Math.sin(a)*2);
                    else if(p.key().equals("wuwang_arrows"))at=marshal.lockedPoint().add(Math.cos(a)*3,.1,Math.sin(a)*3);
                    else if(p.key().equals("wuwang_storm")){at=caster.position().add(Math.cos(a)*4,1+(i%3)*.5,Math.sin(a)*4);colour=new Vector3f(.45F,.27F,.29F);}
                    else if(i%2==0){double angle=Math.toRadians(-marshal.meleeAngle()/2+marshal.meleeAngle()*i/Math.max(1,count-2));var side=new Vec3(-f.z,0,f.x);at=marshal.meleeOrigin().add(f.scale(Math.cos(angle)*marshal.meleeRadius())).add(side.scale(Math.sin(angle)*marshal.meleeRadius()));}
                    else at=marshal.bladeTip().add(f.scale(5D*(i-1)/Math.max(1,count-2)));
                    mc.level.addParticle(new DustParticleOptions(colour,.8F),at.x,at.y,at.z,0,.01,0);
                }continue;
            }
            if(p.key().startsWith("taoyan_")){
                if(!(caster instanceof com.dynasty.blueprint.boss.TaoyanCauldron pot))continue;
                if(p.key().equals("taoyan_ram")&&age>=32||p.key().equals("taoyan_whip")&&age>=48||p.key().equals("taoyan_oil")&&age>=36||p.key().equals("taoyan_bells")&&age>=40||p.key().equals("taoyan_slam")&&age>=36||p.key().equals("taoyan_drink")&&age>=88)continue;
                int count=Math.min(8,budget);budget-=count;var f=p.direction().multiply(1,0,1).normalize();var side=new Vec3(-f.z,0,f.x);var color=new Vector3f(.5F,.4F,.26F);
                for(int i=0;i<count;i++){double a=i*Math.PI*2/count;Vec3 at;
                    if(p.key().equals("taoyan_ram"))at=p.origin().add(f.scale(12D*i/Math.max(1,count-1))).add(side.scale(i%2==0?-2:2)).add(0,.1,0);
                    else if(p.key().equals("taoyan_whip")){double angle=Math.toRadians(-135+270D*i/Math.max(1,count-1));at=pot.whipOrigin().add(f.scale(Math.cos(angle)*4.5)).add(side.scale(Math.sin(angle)*4.5));}
                    else if(p.key().equals("taoyan_oil"))at=p.origin().add(f.scale(4)).add(Math.cos(a)*6,.08,Math.sin(a)*6);
                    else if(p.key().equals("taoyan_slam"))at=pot.landing().add(Math.cos(a)*4,.08,Math.sin(a)*4);
                    else if(p.key().equals("taoyan_bells"))at=(pot.arenaCentre()==null?caster.position():Vec3.atBottomCenterOf(pot.arenaCentre())).add(Math.cos(a)*20,.15,Math.sin(a)*20);
                    else {double radius=age<p.windup()?20:2+(age%20)*.9;at=caster.position().add(Math.cos(a)*radius,1.1,Math.sin(a)*radius);}
                    mc.level.addParticle(new DustParticleOptions(color,.95F),at.x,at.y,at.z,0,.008,0);
                }continue;
            }
            if(p.key().startsWith("suanni_")){
                if(!(caster instanceof com.dynasty.blueprint.elite.BronzeSuanni lion))continue;
                if(p.key().equals("suanni_fire")&&age>=84||p.key().equals("suanni_stomp")&&age>=30||p.key().equals("suanni_roar")&&age>=16)continue;
                int count=Math.min(8,budget);budget-=count;var forward=p.direction().multiply(1,0,1).normalize();var side=new Vec3(-forward.z,0,forward.x);
                for(int i=0;i<count;i++){Vec3 at;var color=new Vector3f(.7F,.32F,.1F);
                    if(p.key().equals("suanni_fire")){
                        if(age<24){double a=Math.toRadians(-45+90D*i/Math.max(1,count-1));at=caster.position().add(forward.scale(.75)).add(forward.scale(Math.cos(a)*9.25)).add(side.scale(Math.sin(a)*9.25)).add(0,.08,0);}
                        else {double u=(i/2D)/Math.max(1,(count-1)/2D);var d=lion.headDirection(age);var flank=new Vec3(-d.z,0,d.x);at=lion.fireMuzzle(age).add(d.scale(lion.flameLength(age)*u)).add(flank.scale(i%2==0?-2:2));at=new Vec3(at.x,caster.getY()+.08,at.z);}
                    }else if(p.key().equals("suanni_stomp"))at=lion.stompOrigin().add(forward.scale(5D*i/Math.max(1,count-1))).add(side.scale(i%2==0?-.45:.45)).add(0,.08,0);
                    else {double a=i*Math.PI*2/count;at=caster.position().add(Math.cos(a)*4,.08,Math.sin(a)*4);}
                    mc.level.addParticle(new DustParticleOptions(color,.85F),at.x,at.y,at.z,0,.006,0);
                }continue;
            }
            if(p.key().startsWith("eagle_")){
                if(!(caster instanceof com.dynasty.blueprint.elite.GoldenEagle eagle))continue;
                if(p.key().equals("eagle_rain")&&age>=80||p.key().equals("eagle_fan")&&age>=20||p.key().equals("eagle_dive")&&age>32)continue;
                int count=Math.min(8,budget);budget-=count;var color=new Vector3f(.85F,.6F,.22F);var forward=p.direction().multiply(1,0,1).normalize();var side=new Vec3(-forward.z,0,forward.x);
                for(int i=0;i<count;i++){Vec3 at;
                    if(p.key().equals("eagle_rain")){int index=(int)((now+p.seed()+i)%24+24)%24;double angle=index%6*Math.PI/3+(index/6%2)*Math.PI/6;double radius=.7+(index/6)*1.05;at=eagle.landing().add(Math.cos(angle)*radius,.08,Math.sin(angle)*radius);}
                    else if(p.key().equals("eagle_dive")){double a=i/(double)count*Math.PI*2;at=eagle.landing().add(Math.cos(a)*2,.08,Math.sin(a)*2);if(age>=13)color=new Vector3f(.8F,.15F,.1F);}
                    else {double a=Math.toRadians(-90+i*180D/Math.max(1,count-1));at=new Vec3(eagle.getX(),eagle.landing().y+.08,eagle.getZ()).add(forward.scale(Math.cos(a)*16)).add(side.scale(Math.sin(a)*16));}
                    mc.level.addParticle(new DustParticleOptions(color,.85F),at.x,at.y,at.z,0,.01,0);
                }continue;
            }
            if(p.key().startsWith("judge_")){
                if(!(caster instanceof com.dynasty.blueprint.elite.LampJudge judge))continue;
                if(p.key().equals("judge_name")&&age>=45||p.key().equals("judge_cage")&&age>=176||p.key().equals("judge_strokes")&&age>=50)continue;
                int count=Math.min(8,budget);budget-=count;
                for(int i=0;i<count;i++){
                    double a=i/(double)count*Math.PI*2;Vec3 at;Vector3f color=new Vector3f(.48F,.65F,.6F);
                    if(p.key().equals("judge_name")){at=judge.mark().add(Math.cos(a)*.45,.08,Math.sin(a)*.45);if(age>=36)color=new Vector3f(.85F,.12F,.1F);}
                    else if(p.key().equals("judge_cage"))at=judge.mark().add(Math.cos(a)*3,.08,Math.sin(a)*3);
                    else at=caster.position().add(p.direction().scale(1.5+i*.5)).add(0,1.125,0);
                    mc.level.addParticle(new DustParticleOptions(color,.8F),at.x,at.y,at.z,0,.005,0);
                }continue;
            }
            if(p.key().startsWith("gorilla_")){
                if(!(caster instanceof com.dynasty.blueprint.elite.BronzeGorilla ape))continue;
                if(p.key().equals("gorilla_leap")&&age>38||p.key().equals("gorilla_smash")&&age>=88||p.key().equals("gorilla_throw")&&age>=18)continue;
                int count=Math.min(8,budget);budget-=count;var forward=p.direction().multiply(1,0,1).normalize();var side=new Vec3(-forward.z,0,forward.x);
                for(int i=0;i<count;i++){Vec3 at;Vector3f color=new Vector3f(.6F,.45F,.28F);
                    if(p.key().equals("gorilla_leap")){double a=i/(double)count*Math.PI*2;at=ape.landing().add(Math.cos(a)*4,.08,Math.sin(a)*4);if(age>=30&&age<=35)color=new Vector3f(.8F,.12F,.1F);}
                    else if(p.key().equals("gorilla_smash")){double distance=.7+8*i/(double)Math.max(1,count-1);at=p.origin().add(forward.scale(distance)).add(side.scale(i%2==0?-1:1)).add(0,.08,0);}
                    else at=caster.position().add(side.scale((i%2==0?-1:1)*.55)).add(forward.scale(1.4)).add(0,.7+i*.1,0);
                    mc.level.addParticle(new DustParticleOptions(color,age>=30&&p.key().equals("gorilla_leap")?1.25F:.9F),at.x,at.y,at.z,0,.015,0);
                }continue;
            }
            if(p.key().startsWith("ink_")){
                if(!(caster instanceof com.dynasty.blueprint.elite.InkAssassin ink))continue;
                if(p.key().equals("ink_stealth")&&age>=81||p.key().equals("ink_field")&&age>=56||p.key().equals("ink_mist")&&age>=29)continue;
                int count=Math.min(4,budget);budget-=count;
                for(int i=0;i<count;i++){Vec3 at;
                    if(p.key().equals("ink_stealth")){at=age<70?caster.position().add((i%2==0?-.15:.15),.05,(i/2)*.2):ink.mark().add(Math.cos(i*Math.PI*.5)*.9,.06,Math.sin(i*Math.PI*.5)*.9);}
                    else if(p.key().equals("ink_field")){var a=ink.fieldCorner(i);var b=ink.fieldCorner((i+1)%4);at=a.lerp(b,(age%12)/12D).add(0,.06,0);}
                    else at=caster.position().add(p.direction().scale(.4+i*.25)).add(0,.12,0);
                    mc.level.addParticle(new DustParticleOptions(i%2==0?new Vector3f(.12F,.14F,.16F):new Vector3f(.75F,.77F,.75F),.7F),at.x,at.y,at.z,0,.005,0);
                }continue;
            }
            if(p.key().startsWith("corpse_")){
                if(!(caster instanceof com.dynasty.blueprint.elite.RageCorpse corpse))continue;
                if(p.key().equals("corpse_leap")&&age>36||p.key().equals("corpse_spin")&&age>102||p.key().equals("corpse_blood")&&age>41)continue;
                int count=Math.min(8,budget);budget-=count;var forward=p.direction().multiply(1,0,1).normalize();var side=new Vec3(-forward.z,0,forward.x);
                for(int i=0;i<count;i++){double angle=(i/(double)count+age*.03)*Math.PI*2;Vec3 at;
                    if(p.key().equals("corpse_leap"))at=corpse.landing().add(Math.cos(angle)*3,.1,Math.sin(angle)*3);
                    else if(p.key().equals("corpse_spin"))at=caster.position().add(Math.cos(angle)*3,.13,Math.sin(angle)*3);
                    else{double distance=1.2+8*i/(double)Math.max(1,count-1);at=caster.position().add(forward.scale(distance)).add(side.scale((i%2==0?-1:1)*Math.tan(Math.toRadians(15))*(distance-1.2))).add(0,1.5,0);}
                    mc.level.addParticle(new DustParticleOptions(age<p.windup()?new Vector3f(.58F,.44F,.32F):new Vector3f(.48F,.15F,.2F),.95F),at.x,at.y,at.z,0,.015,0);
                }continue;
            }
            if(p.key().startsWith("tide_")){
                if(!(caster instanceof com.dynasty.blueprint.elite.TideYasha yasha))continue;
                int count=Math.min(8,budget);var forward=p.direction().multiply(1,0,1).normalize();var side=new Vec3(-forward.z,0,forward.x);
                if(p.key().equals("tide_wave")&&age>=p.windup()||p.key().equals("tide_dive")&&age>36||p.key().equals("tide_combo")&&age>44)continue;
                budget-=count;
                for(int i=0;i<count;i++){double angle=(i/(double)count+age*.03)*Math.PI*2;Vec3 at;
                    if(p.key().equals("tide_dive"))at=yasha.poolPoint().add(Math.cos(angle)*2,age<30?.07:.1+(age-30)*.25,Math.sin(angle)*2);
                    else if(p.key().equals("tide_wave"))at=caster.position().add(side.scale(i%2==0?-.8:.8)).add(Math.cos(angle)*.3,.15+i%4*.7,Math.sin(angle)*.3);
                    else at=caster.position().add(forward.scale(2.8*i/(double)count)).add(side.scale(.9)).add(0,.1,0);
                    var dust=new DustParticleOptions(p.key().equals("tide_dive")&&age<30?new Vector3f(.06F,.1F,.14F):new Vector3f(.4F,.75F,.8F),.9F);mc.level.addParticle(dust,at.x,at.y,at.z,0,age<30?0:.05,0);
                }
                if(p.key().equals("tide_dive")&&age<30&&budget>0){budget--;mc.level.addParticle(ParticleTypes.SQUID_INK,caster.getX(),caster.getY()+.1,caster.getZ(),0,.01,0);}continue;
            }
            if(p.key().startsWith("alchemist_")){
                if(age>=p.windup())continue;int count=Math.min(8,budget);budget-=count;
                for(int i=0;i<count;i++){double angle=(i/(double)count+age*.025)*Math.PI*2;Vec3 at;
                    if(p.key().equals("alchemist_fire_sea")){double radius=i%3==0?2:5;at=p.origin().add(Math.cos(angle)*radius,.1,Math.sin(angle)*radius);}
                    else if(p.key().equals("alchemist_helix"))at=caster.position().add(Math.cos(angle)*.9,1.1+Math.sin(angle)*.35,Math.sin(angle)*.9);
                    else at=caster.position().add(Math.cos(angle)*.7,1.5,Math.sin(angle)*.7);
                    var dust=new DustParticleOptions(i%2==0?new Vector3f(.95F,.85F,.68F):new Vector3f(.2F,.18F,.22F),.85F);mc.level.addParticle(dust,at.x,at.y,at.z,0,0,0);
                }continue;
            }
            if(p.key().startsWith("spider_")){
                int count=Math.min(8,budget);budget-=count;var dust=new DustParticleOptions(new Vector3f(.46F,.71F,.29F),.85F);
                Vec3 floor=p.origin();for(int y=0;y<=12;y++){var block=net.minecraft.core.BlockPos.containing(p.origin()).below(y);if(!mc.level.hasChunkAt(block))break;if(mc.level.getBlockState(block.below()).isFaceSturdy(mc.level,block.below(),net.minecraft.core.Direction.UP)){floor=new Vec3(p.origin().x,block.getY()+.08,p.origin().z);break;}}
                for(int i=0;i<count;i++){
                    double angle=(i/(double)count+age*.015)*Math.PI*2;Vec3 at;
                    if(p.key().equals("spider_drop")){at=floor.add(Math.cos(angle)*2,0,Math.sin(angle)*2);if(i<2&&age<p.windup())at=floor.lerp(caster.position(),i/2.0);}
                    else if(p.key().equals("spider_acid")){at=age<p.windup()?caster.position().add(Math.cos(angle)*.7,.4,Math.sin(angle)*.7):floor.add(p.direction().scale(2+i%3*2)).add(new Vec3(-p.direction().z,0,p.direction().x).scale(i%2==0?-1.5:1.5));}
                    else at=caster.position().add(Math.cos(angle)*1.2,.15,Math.sin(angle)*1.2);
                    mc.level.addParticle(dust,at.x,at.y,at.z,0,p.key().equals("spider_acid")&&age>=p.windup()?-.025:0,0);
                }continue;
            }
            if(p.key().startsWith("hammer_")){
                int count=Math.min(8,budget);budget-=count;var forward=p.direction().multiply(1,0,1).normalize();var side=new Vec3(-forward.z,0,forward.x);
                var dust=new DustParticleOptions(new Vector3f(.77F,.60F,.29F),.9F);
                for(int i=0;i<count;i++){
                    Vec3 at;
                    if(p.key().equals("hammer_slam")){
                        double radius=age<28?2:age<44?2:age<60?4:6;double angle=(i/(double)count+age*.012)*Math.PI*2;
                        at=p.origin().add(Math.cos(angle)*radius,.12,Math.sin(angle)*radius);
                    }else if(p.key().equals("hammer_wheel"))at=(age<p.windup()?p.origin():caster.position()).add(forward.scale(2.1*(i/2)/3.0)).add(side.scale(i%2==0?-com.dynasty.blueprint.elite.HammerGuardian.WHEEL_WIDTH*.5:com.dynasty.blueprint.elite.HammerGuardian.WHEEL_WIDTH*.5)).add(0,.12,0);
                    else at=p.origin().add(forward.scale(com.dynasty.blueprint.elite.HammerChain.RANGE*i/(double)count)).add(0,.12,0);
                    mc.level.addParticle(age<p.windup()?dust:new BlockParticleOption(ParticleTypes.BLOCK,Blocks.STONE.defaultBlockState()),at.x,at.y,at.z,0,age<p.windup()?0:.035,0);
                }continue;
            }
            if(p.key().startsWith("fox_")){
                var dust=new DustParticleOptions(new Vector3f(.86F,.52F,.67F),.9F);
                if(p.key().equals("fox_fire")){
                    for(int cell=0;cell<5&&budget>0;cell++){
                        int impact=20+cell*12;if(age<impact-16||age>impact+4)continue;
                        var at=p.origin().add(p.direction().multiply(1,0,1).normalize().scale(cell*1.5));int count=Math.min(4,budget);budget-=count;
                        for(int j=0;j<count;j++){double angle=(j/(double)count+age*.04)*Math.PI*2,r=com.dynasty.blueprint.elite.FoxMatron.FIRE_RADIUS;var pos=at.add(Math.cos(angle)*r,age>=impact?(j+1)*.55:.08,Math.sin(angle)*r);mc.level.addParticle(age<impact?dust:ParticleTypes.SOUL_FIRE_FLAME,pos.x,pos.y,pos.z,0,.02,0);}
                    }
                }else{
                    int count=Math.min(age<p.windup()?3:4,budget);budget-=count;
                    for(int i=0;i<count;i++){var at=p.key().equals("fox_mirror")&&age>=20?p.origin().add(p.direction().scale((age-20)*com.dynasty.blueprint.elite.FoxMatron.BEAM_SPEED)).add(0,i*.04,0):caster.position().add(Math.cos(age*.1+i*Math.PI*2/3)*1.2,1.2,Math.sin(age*.1+i*Math.PI*2/3)*1.2);mc.level.addParticle(dust,at.x,at.y,at.z,0,.01,0);}
                }continue;
            }
            if(p.key().startsWith("jinwu_")){
                int count=Math.min(8,budget);budget-=count;var forward=p.direction().multiply(1,0,1).normalize();var side=new Vec3(-forward.z,0,forward.x);
                var dust=new DustParticleOptions(new Vector3f(.92F,.89F,.74F),.9F);
                for(int i=0;i<count;i++){
                    double u=(i+.5)/count;Vec3 at;
                    if(p.key().equals("jinwu_charge"))at=p.origin().add(forward.scale(p.range()*u)).add(side.scale(i%2==0?-.75:.75));
                    else{double angle=Math.atan2(forward.z,forward.x)+Math.toRadians(p.angle())*(u-.5);double radius=p.range();
                        if(p.key().equals("jinwu_sweep")&&i==count-1){angle=Math.atan2(forward.z,forward.x)+Math.PI;radius=com.dynasty.blueprint.elite.Jinwu.REAR_SWEEP;}
                        at=p.origin().add(Math.cos(angle)*radius,0,Math.sin(angle)*radius);}
                    mc.level.addParticle(age<p.windup()?dust:ParticleTypes.CLOUD,at.x,at.y+.13,at.z,0,.015,0);
                }continue;
            }
            if(p.key().startsWith("mechanist_")){
                int count=Math.min(8,budget);budget-=count;
                var dust=new DustParticleOptions(new Vector3f(.48F,.84F,.87F),.7F);
                var forward=p.direction().multiply(1,0,1).normalize();var side=new Vec3(-forward.z,0,forward.x);
                for(int i=0;i<count;i++){
                    double u=(i+(age/3)%count)/(double)count;Vec3 at;
                    if(p.key().equals("mechanist_net")){
                        double theta=Math.atan2(forward.z,forward.x)+Math.toRadians(p.angle())*(u-.5);
                        at=p.origin().add(Math.cos(theta)*p.range(),.13,Math.sin(theta)*p.range());
                    }else if(p.key().equals("mechanist_wheels")){
                        double wave=Math.sin(Math.PI*(i/2+.5)/(count/2.0));
                        at=p.origin().add(forward.scale(com.dynasty.blueprint.elite.MechanistWheel.RANGE*wave)).add(side.scale((i%2==0?1:-1)*(com.dynasty.blueprint.elite.MechanistWheel.INNER_GAP+com.dynasty.blueprint.elite.MechanistWheel.CURVE_WIDTH*wave))).add(0,.15,0);
                    }else at=caster.position().add(Math.cos(u*Math.PI*2)*1.5,1.2,Math.sin(u*Math.PI*2)*1.5);
                    mc.level.addParticle(dust,at.x,at.y,at.z,0,.005,0);
                }continue;
            }
            if(p.key().startsWith("headless_")){
                int count=Math.min(8,budget);budget-=count;
                var centre=p.key().equals("headless_spin")?caster.position():p.origin();
                var dust=new DustParticleOptions(new Vector3f(.55F,.12F,.2F),.8F);
                for(int i=0;i<count;i++){
                    double u=(i+(age/3)%count)/(double)count;
                    double theta=Math.atan2(p.direction().z,p.direction().x)+Math.toRadians(p.angle())*(u-.5);
                    double radius=p.key().equals("headless_roar")?p.range()*(.3+.7*(i%3)/2.0):p.range();
                    var at=centre.add(Math.cos(theta)*radius,.12,Math.sin(theta)*radius);
                    mc.level.addParticle(age<p.windup()?dust:ParticleTypes.SOUL_FIRE_FLAME,at.x,at.y,at.z,0,.015,0);
                }continue;
            }
            if(p.key().startsWith("bird_")){
                int count=Math.min(8,budget);budget-=count;
                var forward=p.direction().multiply(1,0,1).normalize();var side=new Vec3(forward.z,0,-forward.x);
                var dust=new DustParticleOptions(new Vector3f(.65F,.1F,.2F),.85F);
                for(int i=0;i<count;i++){
                    Vec3 at;
                    if(p.key().equals("bird_bomb")){
                        var centre=com.dynasty.blueprint.elite.GhostCarriageBird.bloodLanding(p.origin(),forward,i);
                        double theta=age*.45;at=centre.add(Math.cos(theta)*1.2,0,Math.sin(theta)*1.2);
                    }
                    else if(p.key().equals("bird_dive"))at=p.origin().add(forward.scale(p.range()*(i/2)/3.0)).add(side.scale(i%2==0?.75:-.75));
                    else{double theta=(i/(double)count)*Math.PI*2;at=p.origin().add(Math.cos(theta)*p.range(),0,Math.sin(theta)*p.range());}
                    mc.level.addParticle(age<p.windup()?dust:ParticleTypes.SMOKE,at.x,at.y+.08,at.z,0,.015,0);
                }continue;
            }
            if(p.key().equals("stone_slam")){
                var d=p.direction().multiply(1,0,1).normalize();
                var side=new Vec3(-d.z,0,d.x).scale(com.dynasty.blueprint.StoneGuardBehavior.SLAM_WIDTH*.5);
                int count=Math.min(6,budget);budget-=count;
                for(int i=0;i<count;i++){
                    double u=((age/3+i/2)%6)/5.0;
                    var at=p.origin().add(d.scale(p.range()*u)).add(side.scale(i%2==0?1:-1)).add(0,.08,0);
                    if(age<p.windup())mc.level.addParticle(new DustParticleOptions(new Vector3f(.85F,.65F,.25F),.7F),at.x,at.y,at.z,0,0,0);
                    else if(age<p.windup()+6)mc.level.addParticle(new BlockParticleOption(ParticleTypes.BLOCK,Blocks.STONE.defaultBlockState()),at.x,at.y,at.z,0,.1,0);
                }continue;
            }
            if((p.key().equals("bronze_fire")||p.key().equals("bronze_poison"))&&age>=p.windup()){
                if(age>=p.windup()+60)continue;
                int count=Math.min(6,budget);budget-=count;
                for(int i=0;i<count;i++){
                    double u=((age+i*11)%30)/30.0;
                    double angle=Math.atan2(p.direction().z,p.direction().x)+Math.toRadians(p.angle())*(i/(double)Math.max(1,count-1)-.5);
                    var at=p.origin().add(Math.cos(angle)*p.range()*u,.4,Math.sin(angle)*p.range()*u);
                    var effect=p.key().equals("bronze_fire")?ParticleTypes.FLAME:new DustParticleOptions(new Vector3f(.35F,.65F,.18F),.8F);
                    mc.level.addParticle(effect,at.x,at.y,at.z,0,.005,0);
                }continue;
            }
            if(p.key().equals("spider_drop")&&age<p.windup()){
                var floor=mc.level.clip(new net.minecraft.world.level.ClipContext(p.origin(),p.origin().add(0,-12,0),net.minecraft.world.level.ClipContext.Block.COLLIDER,net.minecraft.world.level.ClipContext.Fluid.NONE,caster)).getLocation();
                int count=Math.min(6,budget);budget-=count;
                for(int i=0;i<count;i++){
                    double angle=(i/(double)count+age*.015)*Math.PI*2,r=com.dynasty.blueprint.MiningSpiderBehavior.IMPACT_RADIUS;
                    mc.level.addParticle(new DustParticleOptions(new Vector3f(.9F,.55F,.2F),.8F),floor.x+Math.cos(angle)*r,floor.y+.08,floor.z+Math.sin(angle)*r,0,0,0);
                }continue;
            }
            boolean buff=p.key().contains("buff")||p.key().contains("possession");
            if(p.key().equals("powder_detonate")){
                for(int i=0;i<2&&budget>0;i++,budget--)mc.level.addParticle(age<p.windup()?ParticleTypes.SMOKE:ParticleTypes.FLAME,
                        caster.getX()+(i==0?-.35:.35),caster.getY()+.85,caster.getZ(),0,.012,0);
                continue;
            }
            if(p.key().equals("scout_grapple")&&caster instanceof TemplateMob scout){
                // A thrown hook that misses must never appear attached to the intended victim.
                if(scout.hookTargetId()<0||now>=scout.hookExpires())continue;
                var hooked=mc.level.getEntity(scout.hookTargetId());
                if(hooked==null||scout.distanceToSqr(hooked)>400)continue;
                int count=Math.min(8,budget);budget-=count;
                var iron=new DustParticleOptions(new Vector3f(.38F,.42F,.43F),.4F);
                for(int i=0;i<count;i++){var at=caster.position().add(0,.8,0).lerp(hooked.position().add(0,.2,0),(i+1D)/(count+1));
                    mc.level.addParticle(iron,at.x,at.y,at.z,0,0,0);}continue;
            }
            var color=buff?new Vector3f(.78F,.12F,.19F):p.key().contains("talisman")?new Vector3f(.12F,.65F,.85F):new Vector3f(.70F,.50F,.24F);
            var dust=new DustParticleOptions(color,.7F);
            var target=mc.level.getEntity(p.targetId());
            int count=Math.min(budget,6); budget-=count;
            double offset=((p.seed()&1023)/1024.0 + age*.08)%1;
            for(int i=0;i<count;i++) {
                Vec3 at;
                if(buff && target!=null) {
                    double u=(i+offset)/count;
                    at=caster.position().add(0,caster.getBbHeight()*.7,0).lerp(target.position().add(0,target.getBbHeight()*.6,0),u);
                } else if(age<p.windup()) {
                    double a=Math.atan2(p.direction().z,p.direction().x)+Math.toRadians(p.angle())*((i+offset)/count-.5);
                    at=p.origin().add(Math.cos(a)*p.range(),.10,Math.sin(a)*p.range());
                } else {
                    double a=(i+offset)/count*Math.PI*2;
                    at=caster.position().add(Math.cos(a)*.55,.6+age*.007,Math.sin(a)*.55);
                }
                mc.level.addParticle(dust,at.x,at.y,at.z,0,.005,0);
            }
        }
    }
    private static int deathParticles(Minecraft mc,BlueprintVisualEvent p,long age,int budget) {
        if(p.key().equals("death_luban_yisha")){
            var caster=mc.level.getEntity(p.entityId());if(caster==null||!caster.getUUID().equals(p.entityUuid())||age>=218)return 0;
            int count=Math.min(6,budget);for(int i=0;i<count;i++){double a=i*Math.PI/3+age*.04;var at=caster.position().add(Math.cos(a)*2.5,1.4,Math.sin(a)*2.5);mc.level.addParticle(new BlockParticleOption(ParticleTypes.BLOCK,(i%2==0?Blocks.COPPER_BLOCK:Blocks.DARK_OAK_PLANKS).defaultBlockState()),at.x,at.y,at.z,Math.cos(a)*.04,-.04,Math.sin(a)*.04);}return count;
        }
        if(p.key().equals("death_taoyan_zhishi")){
            var caster=mc.level.getEntity(p.entityId());if(caster==null||!caster.getUUID().equals(p.entityUuid())||age>=194)return 0;
            int count=Math.min(8,budget);for(int i=0;i<count;i++){double a=i*Math.PI/4+age*.03;var at=caster.position().add(Math.cos(a)*2,Math.max(.1,3-age*.02),Math.sin(a)*2);mc.level.addParticle(new BlockParticleOption(ParticleTypes.BLOCK,(i%2==0?Blocks.COPPER_BLOCK:Blocks.BONE_BLOCK).defaultBlockState()),at.x,at.y,at.z,Math.cos(a)*.035,-.04,Math.sin(a)*.035);}return count;
        }
        if(p.key().equals("death_zhenmu_suanni_tonghou")){
            var caster=mc.level.getEntity(p.entityId());if(caster==null||!caster.getUUID().equals(p.entityUuid())||age>=88)return 0;
            int count=Math.min(6,budget);for(int i=0;i<count;i++){double a=i*Math.PI/3;var at=caster.position().add(Math.cos(a)*1.1,age<16?1:.2,Math.sin(a)*1.1);mc.level.addParticle(age<16?new DustParticleOptions(new Vector3f(.86F,.36F,.12F),1):new BlockParticleOption(ParticleTypes.BLOCK,Blocks.COPPER_BLOCK.defaultBlockState()),at.x,at.y,at.z,Math.cos(a)*.025,age<16?.03:-.02,Math.sin(a)*.025);}return count;
        }
        if(p.key().equals("death_liefeng_jindiao_yushi")){
            var caster=mc.level.getEntity(p.entityId());if(caster==null||!caster.getUUID().equals(p.entityUuid())||age>=88)return 0;
            int count=Math.min(6,budget);for(int i=0;i<count;i++){double a=i*Math.PI/3+age*.045;var at=caster.position().add(Math.cos(a)*1.4,.15+age%12*.07,Math.sin(a)*1.4);mc.level.addParticle(age<40?new DustParticleOptions(new Vector3f(.46F,.45F,.41F),.75F):new BlockParticleOption(ParticleTypes.BLOCK,Blocks.SAND.defaultBlockState()),at.x,at.y,at.z,Math.cos(a)*.025,age<40?-.04:.015,Math.sin(a)*.025);}return count;
        }
        if(p.key().equals("death_mojia_jueying_cike")){
            var caster=mc.level.getEntity(p.entityId());if(caster==null||!caster.getUUID().equals(p.entityUuid())||age>=58)return 0;
            int count=Math.min(4,budget);for(int i=0;i<count;i++){double angle=i*Math.PI*.5+age*.035;var at=caster.position().add(Math.cos(angle)*age*.02,.05,Math.sin(angle)*age*.02);mc.level.addParticle(new DustParticleOptions(i%2==0?new Vector3f(.12F,.14F,.16F):new Vector3f(.8F,.82F,.8F),.8F),at.x,at.y,at.z,Math.cos(angle)*.012,0,Math.sin(angle)*.012);}return count;
        }
        if(p.key().equals("death_banshan_jiazhou_shikuang")){
            var caster=mc.level.getEntity(p.entityId());if(caster==null||!caster.getUUID().equals(p.entityUuid())||age>=76)return 0;
            int count=Math.min(4,budget);for(int i=0;i<count;i++){double angle=i*Math.PI*.5+age*.08;var at=caster.position().add(Math.cos(angle)*1.2,.15+age%14*.03,Math.sin(angle)*1.2);mc.level.addParticle(age<25?new DustParticleOptions(new Vector3f(.48F,.15F,.2F),1):new BlockParticleOption(ParticleTypes.BLOCK,Blocks.MUD.defaultBlockState()),at.x,at.y,at.z,Math.cos(angle)*.02,age<25?.07:.01,Math.sin(angle)*.02);}return count;
        }
        if(p.key().equals("death_fubo_xunhai_yecha")){
            var caster=mc.level.getEntity(p.entityId());if(caster==null||!caster.getUUID().equals(p.entityUuid())||age>=76)return 0;
            int count=Math.min(4,budget);for(int i=0;i<count;i++){double angle=i*Math.PI*.5+age*.11;var at=caster.position().add(Math.cos(angle)*1,.15+age%16*.03,Math.sin(angle)*1);mc.level.addParticle(age<32?ParticleTypes.FALLING_WATER:new BlockParticleOption(ParticleTypes.BLOCK,Blocks.PRISMARINE.defaultBlockState()),at.x,at.y,at.z,Math.cos(angle)*.025,.015,Math.sin(angle)*.025);}return count;
        }
        if(p.key().equals("death_yinyang_liandan_fangshi")){
            var caster=mc.level.getEntity(p.entityId());if(caster==null||!caster.getUUID().equals(p.entityUuid())||age>=76)return 0;
            int count=Math.min(4,budget);for(int i=0;i<count;i++){double angle=i*Math.PI*.5+age*.12;var at=caster.position().add(Math.cos(angle)*.7,.3+(age%24)*.045,Math.sin(angle)*.7);mc.level.addParticle(age<18?new ItemParticleOption(ParticleTypes.ITEM,new ItemStack(Items.RAW_COPPER)):i%2==0?ParticleTypes.FLAME:ParticleTypes.SOUL_FIRE_FLAME,at.x,at.y,at.z,Math.cos(angle)*.02,.04,Math.sin(angle)*.02);}return count;
        }
        if(p.key().equals("death_gudu_tianzhunv")){
            if(!(mc.level.getEntity(p.entityId()) instanceof com.dynasty.blueprint.elite.SpiderWoman spider)||!spider.onGround())return 0;
            int count=Math.min(4,budget);for(int i=0;i<count;i++){double angle=(i/(double)count+age*.02)*Math.PI*2;mc.level.addParticle(new DustParticleOptions(new Vector3f(.46F,.71F,.29F),.9F),spider.getX()+Math.cos(angle)*1.2,spider.getY()+.08,spider.getZ()+Math.sin(angle)*1.2,0,.02,0);}return count;
        }
        if(p.key().equals("death_guiche_jiushouniao")){
            var bird=mc.level.getEntity(p.entityId());if(bird==null||!bird.getUUID().equals(p.entityUuid())||!bird.onGround()||age>=96)return 0;
            int count=Math.min(4,budget);var random=net.minecraft.util.RandomSource.create(p.seed()^age);
            for(int i=0;i<count;i++){
                var at=bird.position().add((random.nextDouble()-.5)*3,.12+random.nextDouble()*.3,(random.nextDouble()-.5)*2);
                if(age<55)mc.level.addParticle(new ItemParticleOption(ParticleTypes.ITEM,new ItemStack(Items.FEATHER)),at.x,at.y,at.z,(at.x-bird.getX())*.05,.025,(at.z-bird.getZ())*.05);
                else mc.level.addParticle(ParticleTypes.SQUID_INK,at.x,at.y,at.z,0,.025,0);
            }return count;
        }
        boolean priest=p.key().endsWith("fufa_jijiu"),shield=p.key().endsWith("ludun_jiashi"),sword=p.key().endsWith("zuwu_daoshou"),
            cross=p.key().endsWith("liannu_zhenzu"),powder=p.key().endsWith("kuijun_sishi"),flag=p.key().endsWith("zhenwang_zhangqiguan");
        boolean child=p.key().endsWith("fuhun_baibu_tongzi"),paper=p.key().endsWith("zhiren_jianke"),skull=p.key().endsWith("muxue_feilu"),toad=p.key().endsWith("chimu_zhuha"),tree=p.key().endsWith("kumu_shujing"),scorpion=p.key().endsWith("mingsha_shixie");
        if(!(scorpion&&age<36||tree&&age>=8&&age<32||toad&&age>=12&&age<28||skull&&age<28||paper&&age<10||child&&age<30||priest&&age<18||shield&&age>=188||sword&&age>=40||cross&&age>=8&&age<20||powder&&age<30||flag&&age>=8&&age<28))return 0;
        int count=Math.min(budget,priest?8:4);
        // No visual entities, frame packets or random state to replicate: seed + absolute age is deterministic.
        var random=net.minecraft.util.RandomSource.create(p.seed()^age*0x9e3779b97f4a7c15L);
        for(int i=0;i<count;i++) {
            double x=p.origin().x+(random.nextDouble()-.5)*.8,z=p.origin().z+(random.nextDouble()-.5)*.8;
            double y=p.origin().y+(priest?.6:shield?.4:.15)+random.nextDouble()*(priest?.6:shield?1.2:.25);
            if(scorpion){
                mc.level.addParticle(age<8?ParticleTypes.END_ROD:new BlockParticleOption(ParticleTypes.BLOCK,Blocks.SANDSTONE.defaultBlockState()),x,y+.2,z,(x-p.origin().x)*.18,.015,(z-p.origin().z)*.18);
            } else if(tree){
                mc.level.addParticle(new BlockParticleOption(ParticleTypes.BLOCK,Blocks.DARK_OAK_LOG.defaultBlockState()),x,y+1,z,(x-p.origin().x)*.3,.03,(z-p.origin().z)*.3);
            } else if(toad){
                mc.level.addParticle(new ItemParticleOption(ParticleTypes.ITEM,new ItemStack(Items.WHITE_DYE)),x,y+.4,z,(x-p.origin().x)*.04,.005,(z-p.origin().z)*.04);
            } else if(skull){
                mc.level.addParticle(age<8?new ItemParticleOption(ParticleTypes.ITEM,new ItemStack(Items.IRON_NUGGET)):age<18?ParticleTypes.SMOKE:new ItemParticleOption(ParticleTypes.ITEM,new ItemStack(Items.BONE_MEAL)),x,y,z,(x-p.origin().x)*.1,.025,(z-p.origin().z)*.1);
            } else if(paper){
                mc.level.addParticle(age<6?ParticleTypes.END_ROD:ParticleTypes.SQUID_INK,x,y,z,0,age<6?.02:0,0);
            } else if(child){
                mc.level.addParticle(new ItemParticleOption(ParticleTypes.ITEM,new ItemStack(age<18?Items.PAPER:Items.BONE_MEAL)),x,y+.6,z,(x-p.origin().x)*.14,.025,(z-p.origin().z)*.14);
            } else if(priest) {
                if(i%3==0)mc.level.addParticle(ParticleTypes.SOUL_FIRE_FLAME,x,y,z,(x-p.origin().x)*.05,.025,(z-p.origin().z)*.05);
                else mc.level.addParticle(new ItemParticleOption(ParticleTypes.ITEM,new ItemStack(Items.PAPER)),x,y,z,(x-p.origin().x)*.2,.06,(z-p.origin().z)*.2);
            } else if(cross){
                mc.level.addParticle(new BlockParticleOption(ParticleTypes.BLOCK,Blocks.OAK_PLANKS.defaultBlockState()),x,y+.8,z,(x-p.origin().x)*.12,.03,(z-p.origin().z)*.12);
            } else if(powder){mc.level.addParticle(ParticleTypes.SMOKE,x,y+.3,z,0,.018,0);
            } else if(flag){mc.level.addParticle(ParticleTypes.SOUL,x,y+.7,z,0,.025,0);
            } else if(shield) {
                mc.level.addParticle(new BlockParticleOption(ParticleTypes.BLOCK,(i%2==0?Blocks.IRON_BLOCK:Blocks.DARK_OAK_PLANKS).defaultBlockState()),x,y,z,(x-p.origin().x)*.05,.02,(z-p.origin().z)*.05);
            } else mc.level.addParticle(ParticleTypes.SMOKE,x,y,z,0,.012,0);
        }
        return count;
    }
    public static int activeCount() {return ACTIVE.size();}
}
