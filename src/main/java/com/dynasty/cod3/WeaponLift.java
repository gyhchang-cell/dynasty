package com.dynasty.cod3;

import com.dynasty.Dynasty;
import com.dynasty.network.DynastyNetwork;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.*;

/** Observe a real native hit and real subsequent ascent. Never pushes, moves or damages entities. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class WeaponLift {
    public static final String PREFIX="equipment_confirmed_lift_",STAMP="cod3_confirmed_lift_at";
    public static final int DURATION=8;
    private static final Set<String> LONGARMS=Set.of("mu_mao","chang_qiang","dragon_spear","bawang_spear","thunder_spear","beichen_spear","baihu_glaive");
    private static final List<Candidate> CANDIDATES=new ArrayList<>();
    private static final List<Flight> FLIGHTS=new ArrayList<>();
    public record Ground(Vec3 point,int color) {}
    /** Actual collider support, including slab top height; no dust in unsupported air or fluid. */
    public static Ground groundSupport(LivingEntity target) {
        if(!(target.level() instanceof ServerLevel level)||!target.onGround()||!Double.isFinite(target.position().lengthSqr()))return null;
        var feet=target.position();var hit=level.clip(new ClipContext(feet.add(0,.1,0),feet.add(0,-1.2,0),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,target));
        if(hit.getType()!=HitResult.Type.BLOCK||Math.abs(hit.getLocation().y-feet.y)>=.15)return null;
        int tint=level.getBlockState(hit.getBlockPos()).getMapColor(level,hit.getBlockPos()).col;
        return new Ground(hit.getLocation().add(0,.015,0),tint==0?0x9A8C78:tint);
    }
    private static final class Candidate {
        final ServerPlayer player;final LivingEntity target;final ServerLevel level;final String weapon;
        final long tick;final Vec3 feet,motion,ground,direction;final int groundColor;DamageSource source;
        Candidate(ServerPlayer p,LivingEntity t,ServerLevel l,String w) {
            player=p;target=t;level=l;weapon=w;tick=l.getGameTime();feet=t.position();motion=t.getDeltaMovement();
            direction=TangWind.horizontal(p.getLookAngle(),Vec3.ZERO);
            var support=groundSupport(t);ground=support==null?null:support.point();groundColor=support==null?0:support.color();
        }
    }
    private static final class Flight {
        final Candidate hit;boolean armed;boolean sampled;
        Flight(Candidate c){hit=c;}
    }
    public static boolean isLongarm(String id){return id!=null&&LONGARMS.contains(id);}
    public static int color(String id){return "juque_sword".equals(id)?0xC9A468:"huan_shou_dao".equals(id)?0x85A9AE:isLongarm(id)?EquipmentFeedback.tint(id):-1;}
    private static int template(String weapon){return isLongarm(weapon)?3:34;}
    private static String weapon(net.minecraft.world.item.ItemStack stack) {
        var id=ForgeRegistries.ITEMS.getKey(stack.getItem());
        return !stack.isEmpty()&&id!=null&&id.getNamespace().equals(Dynasty.MODID)?id.getPath():null;
    }
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void attack(AttackEntityEvent e) {
        if(e.isCanceled()||!(e.getEntity() instanceof ServerPlayer p)||!(e.getTarget() instanceof LivingEntity target)
                ||!(target.level() instanceof ServerLevel level)||!target.isAlive())return;
        var w=weapon(p.getMainHandItem());if(w==null)return;
        CANDIDATES.removeIf(c->c.player==p);if(CANDIDATES.size()>=32)CANDIDATES.remove(0);
        CANDIDATES.add(new Candidate(p,target,level,w));
    }
    private static boolean primary(LivingEntity target,DamageSource source,float amount) {
        return amount>0&&Float.isFinite(amount)&&source.getEntity() instanceof ServerPlayer p&&source.getDirectEntity()==p
                &&source.is(DamageTypes.PLAYER_ATTACK)&&!com.dynasty.DynastyTrinketOnHit.isSyntheticDamage()
                &&!com.dynasty.EdictSpells.isSpell(source)&&!com.dynasty.QinglongDescent.isDragonDamage(source)
                &&!com.dynasty.DynastyBowRitual.isSolarDamage(source)&&com.dynasty.DynastySchoolCombat.observedPrimary(p,target);
    }
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void hurt(LivingHurtEvent e) {
        if(e.isCanceled()||!primary(e.getEntity(),e.getSource(),e.getAmount()))return;
        for(var c:CANDIDATES)if(c.player==e.getSource().getEntity()&&c.target==e.getEntity()&&c.tick==c.level.getGameTime())c.source=e.getSource();
    }
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void damage(LivingDamageEvent e) {
        Candidate candidate=null;
        for(int i=CANDIDATES.size()-1;i>=0;i--){var c=CANDIDATES.get(i);if(c.target==e.getEntity()&&c.source==e.getSource()){candidate=CANDIDATES.remove(i);break;}}
        if(candidate==null||e.isCanceled()||!primary(e.getEntity(),e.getSource(),e.getAmount())||candidate.tick!=candidate.level.getGameTime()
                ||!candidate.weapon.equals(weapon(EquipmentFeedback.sourceWeapon(e))))return;
        if(color(candidate.weapon)<0&&com.dynasty.DynastySchoolCombat.primaryLift(candidate.player,candidate.target)<.18)return;
        var saved=candidate;FLIGHTS.removeIf(f->f.hit.target==saved.target);if(FLIGHTS.size()>=32)FLIGHTS.remove(0);FLIGHTS.add(new Flight(candidate));
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e) {
        if(e.phase!=TickEvent.Phase.END)return;
        CANDIDATES.clear();
        for(var it=FLIGHTS.iterator();it.hasNext();) {
            var flight=it.next();var c=flight.hit;long elapsed=c.level.getGameTime()-c.tick;var t=c.target;
            if(elapsed<0||elapsed>4||!t.isAlive()||t.isRemoved()||!c.player.isAlive()||c.player.isRemoved()||t.level()!=c.level||c.player.level()!=c.level
                    ||t.position().distanceToSqr(c.feet)>16){it.remove();continue;}
            if(!flight.sampled) {
                flight.sampled=true;var motion=t.getDeltaMovement();
                flight.armed=Double.isFinite(motion.lengthSqr())&&motion.y>0&&motion.y-c.motion.y>=.18
                        &&(t.noPhysics||c.level.noCollision(t,t.getBoundingBox().move(0,.18,0)));
                if(!flight.armed){it.remove();continue;}
            }
            if(t.getY()-c.feet.y<.02)continue;
            it.remove();var data=c.player.getPersistentData();long now=c.level.getGameTime();
            if(data.contains(STAMP)&&data.getLong(STAMP)==now)continue;
            data.putLong(STAMP,now);
            com.dynasty.expansion.CombatFeedback.send(t,com.dynasty.expansion.CombatFeedback.LAUNCH);
            var p=packet(c.level.dimension().location().toString(),t.getId(),c.weapon,c.level.random.nextLong(),now,
                    Math.max(.45,Math.min(1.2,t.getBbWidth())),c.ground==null?c.feet:c.ground,c.direction,c.groundColor,c.ground!=null);
            if(p==null)continue; // Other existing native lifts retain their generic cue without borrowing a weapon arc.
            var point=t.position();DynastyNetwork.CHANNEL.send(PacketDistributor.NEAR.with(()->new PacketDistributor.TargetPoint(point.x,point.y,point.z,32,c.level.dimension())),p);
        }
    }
    @SubscribeEvent public static void stopped(net.minecraftforge.event.server.ServerStoppedEvent e){CANDIDATES.clear();FLIGHTS.clear();}
    public static Cod3VisualPacket packet(String dim,int target,String weapon,long seed,long start,double scale,Vec3 ground,Vec3 direction,int groundColor,boolean supported) {
        if(color(weapon)<0)return null;
        return new Cod3VisualPacket(dim,template(weapon),target,seed,start,DURATION,scale,ground,TangWind.horizontal(direction,Vec3.ZERO),PREFIX+weapon,supported?0:1,groundColor);
    }
    public static boolean accepts(Cod3VisualPacket p) {
        return p!=null&&p.valid()&&p.sequence().startsWith(PREFIX)&&color(p.sequence().substring(PREFIX.length()))>=0&&p.template()==template(p.sequence().substring(PREFIX.length()))
                &&p.entityId()>=0&&p.duration()==DURATION&&p.tick()<=1&&p.scale()>=.45&&p.scale()<=1.2
                &&Math.abs(p.direction().y)<1e-6&&p.direction().lengthSqr()>.9&&p.direction().lengthSqr()<1.1;
    }
    /** Arc has no invented flight path; feet come from the actual interpolated target. */
    public static List<WeaponImpactVisual.Triangle> geometry(Cod3VisualPacket p,double age,Vec3 feet,boolean airborne) {
        if(!accepts(p)||!Double.isFinite(age)||age<0||age>=DURATION||feet==null||!Double.isFinite(feet.lengthSqr()))return List.of();
        var out=new ArrayList<WeaponImpactVisual.Triangle>();double scale=p.scale(),alpha=(1-age/DURATION)*.85;
        var right=new Vec3(p.direction().z,0,-p.direction().x);var up=new Vec3(0,1,0);
        if(airborne) {
            double[][] path={{-.5,.08},{-.5,.32},{-.38,.53},{-.17,.72},{.08,.85},{.34,.89}};
            int tint=color(p.sequence().substring(PREFIX.length()));
            for(int i=0;i<path.length-1;i++) {
                var a=feet.add(right.scale(path[i][0]*scale)).add(up.scale(path[i][1]*scale));
                var b=feet.add(right.scale(path[i+1][0]*scale)).add(up.scale(path[i+1][1]*scale));
                var axis=b.subtract(a).normalize();var side=p.direction().cross(axis).normalize().scale(.035*scale);
                quad(out,a.add(side),a.subtract(side),b.subtract(side),b.add(side),tint,alpha);
                var cross=p.direction().scale(.035*scale);quad(out,a.add(cross),a.subtract(cross),b.subtract(cross),b.add(cross),tint,alpha);
            }
        }
        if(p.tick()==0&&age<5)for(int i=0;i<4;i++) {
            double angle=i*Math.PI*.5+((p.seed()>>>8)&15)*.04;
            var center=p.origin().add(Math.cos(angle)*(.12+age*.045)*scale,.055*scale,Math.sin(angle)*(.12+age*.045)*scale);
            cube(out,center,.045*scale,p.tint(),(1-age/5)*.8);
        }
        return List.copyOf(out);
    }
    private static void cube(List<WeaponImpactVisual.Triangle> out,Vec3 c,double half,int color,double alpha) {
        var x=new Vec3(half,0,0);var y=new Vec3(0,half,0);var z=new Vec3(0,0,half);
        var v=new Vec3[]{c.subtract(x).subtract(y).subtract(z),c.add(x).subtract(y).subtract(z),c.add(x).add(y).subtract(z),c.subtract(x).add(y).subtract(z),
                c.subtract(x).subtract(y).add(z),c.add(x).subtract(y).add(z),c.add(x).add(y).add(z),c.subtract(x).add(y).add(z)};
        int[][] faces={{0,1,2,3},{5,4,7,6},{4,0,3,7},{1,5,6,2},{3,2,6,7},{4,5,1,0}};
        for(int i=0;i<6;i++){int[] f=faces[i];quad(out,v[f[0]],v[f[1]],v[f[2]],v[f[3]],i==4?color:shade(color,i==5?.65:.82),alpha);}
    }
    private static int shade(int c,double f){return ((int)((c>>16&255)*f)<<16)|((int)((c>>8&255)*f)<<8)|(int)((c&255)*f);}
    private static void quad(List<WeaponImpactVisual.Triangle> out,Vec3 a,Vec3 b,Vec3 c,Vec3 d,int color,double alpha) {
        out.add(new WeaponImpactVisual.Triangle(a,b,c,color,alpha));out.add(new WeaponImpactVisual.Triangle(a,c,d,color,alpha));
    }
    private WeaponLift() {}
}
