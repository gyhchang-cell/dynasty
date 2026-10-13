package com.dynasty.cod3;

import com.dynasty.network.DynastyNetwork;
import com.dynasty.Dynasty;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.*;

/** Small material-specific hit geometry. Never applies damage, effects or impulses. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class WeaponImpactVisual {
    public static final String PREFIX="equipment_impact_";
    public enum Shape { CHIP, SPARK }
    public record Burst(int onset,int count,double rotation,double speed,double length,double width,int life) {}
    public record Style(String weapon,int code,int duration,int color,Shape shape,List<Burst> bursts) {}
    public record Triangle(Vec3 a,Vec3 b,Vec3 c,int color,double alpha) {}
    private static final Map<String,Style> STYLES=Map.of(
        "mu_mao",new Style("mu_mao",0,8,0xB48C59,Shape.CHIP,List.of(new Burst(0,4,.2,.08,.14,.035,8))),
        "shi_ge",new Style("shi_ge",1,10,0x909794,Shape.CHIP,List.of(new Burst(0,3,.9,.065,.085,.05,10))),
        "tong_dao",new Style("tong_dao",2,8,0xD5A46D,Shape.SPARK,List.of(new Burst(0,5,.2,.10,.16,.02,8))),
        "tie_jian",new Style("tie_jian",3,7,0xA9B8BD,Shape.SPARK,List.of(new Burst(0,4,.7,.13,.21,.018,7))),
        "qinggang_sword",new Style("qinggang_sword",4,9,0x86DFC8,Shape.SPARK,List.of(
            new Burst(0,3,.25,.12,.22,.02,5),new Burst(3,3,1.25,.15,.27,.02,6))),
        "gilded_mace",new Style("gilded_mace",5,12,0xE5BE72,Shape.SPARK,List.of(
            new Burst(0,2,0,.035,.08,.035,3),new Burst(2,4,.45,.085,.15,.035,5),new Burst(6,3,1.2,.07,.14,.025,6))),
        "yitian_sword",new Style("yitian_sword",6,10,0xC6D9E0,Shape.SPARK,List.of(
            new Burst(0,2,.65,.11,.25,.018,4),new Burst(2,2,2.2,.11,.25,.018,4),new Burst(4,2,.1,.14,.3,.018,6))));

    public static Set<String> weapons(){return STYLES.keySet();}
    public static Style style(String id){return STYLES.get(id);}
    public static boolean stamp(net.minecraft.nbt.CompoundTag data,long now) {
        if(data.contains("cod3_material_impact_at")&&data.getLong("cod3_material_impact_at")==now)return false;
        data.putLong("cod3_material_impact_at",now);return true;
    }
    public static Cod3VisualPacket packet(String dimension,String weapon,long seed,long start,Vec3 origin,Vec3 direction) {
        var s=style(weapon);return s==null?null:new Cod3VisualPacket(dimension,29,-1,seed,start,s.duration(),1,origin,direction,PREFIX+weapon,s.code(),s.color());
    }
    public static boolean accepts(Cod3VisualPacket p) {
        if(p==null||!p.valid()||!p.sequence().startsWith(PREFIX))return false;
        var s=style(p.sequence().substring(PREFIX.length()));
        return s!=null&&p.template()==29&&p.entityId()==-1&&p.duration()==s.duration()&&p.scale()==1&&p.tick()==s.code()&&p.tint()==s.color();
    }
    public static void sendIfSupported(ServerLevel level,String weapon,Vec3 origin,Vec3 direction) {
        if(style(weapon)==null)return;
        var p=packet(level.dimension().location().toString(),weapon,level.random.nextLong(),level.getGameTime(),origin,direction);
        if(!accepts(p))return;
        DynastyNetwork.CHANNEL.send(PacketDistributor.NEAR.with(()->new PacketDistributor.TargetPoint(origin.x,origin.y,origin.z,32,level.dimension())),p);
    }
    /** Observe final primary damage, with an independent bounded cosmetic stamp. */
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void hit(LivingDamageEvent event) {
        if(event.isCanceled()||event.getAmount()<=0||!(event.getSource().getEntity() instanceof ServerPlayer player)
                ||!(event.getEntity().level() instanceof ServerLevel level))return;
        var weapon=EquipmentFeedback.sourceWeapon(event);var id=ForgeRegistries.ITEMS.getKey(weapon.getItem());
        if(weapon.isEmpty()||id==null||!id.getNamespace().equals(Dynasty.MODID)||style(id.getPath())==null)return;
        // sourceWeapon excludes spells, proc damage and held-item substitution;
        // these cues additionally reject every projectile/indirect hit.
        if(event.getSource().getDirectEntity()!=player||!event.getSource().is(net.minecraft.world.damagesource.DamageTypes.PLAYER_ATTACK))return;
        var data=player.getPersistentData();long now=level.getGameTime();
        if(!stamp(data,now))return;
        sendIfSupported(level,id.getPath(),event.getEntity().position().add(0,event.getEntity().getBbHeight()*.55,0),player.getLookAngle());
    }

    /** Exactly the triangles consumed by the client, also inspectable without GLFW. */
    public static List<Triangle> geometry(Cod3VisualPacket p,double age) {
        if(!accepts(p)||!Double.isFinite(age)||age<0||age>=p.duration())return List.of();
        var s=style(p.sequence().substring(PREFIX.length()));var result=new ArrayList<Triangle>();
        var right=SevenStarFlash.right(p.direction());var forward=new Vec3(-right.z,0,right.x);var up=new Vec3(0,1,0);
        double spin=((p.seed()>>>8)&255)/255.*.32;
        for(var burst:s.bursts()) {
            double local=age-burst.onset();if(local<0||local>=burst.life())continue;
            double alpha=1-local/burst.life();
            for(int i=0;i<burst.count();i++) {
                double angle=burst.rotation()+spin+i*Math.PI*2/burst.count();
                Vec3 radial=right.scale(Math.cos(angle)).add(up.scale(Math.sin(angle)));
                Vec3 center=p.origin().add(radial.scale(.06+local*burst.speed())).add(forward.scale(.045*local));
                if(s.shape()==Shape.CHIP)center=center.add(0,-.008*local*local,0);
                double length=burst.length()*(.7+.3*alpha);
                Vec3 axis=s.shape()==Shape.CHIP?radial.add(forward.scale(.5)).normalize():radial;
                Vec3 a=center.subtract(axis.scale(length*.5)),b=center.add(axis.scale(length*.5));
                if(s.shape()==Shape.CHIP)box(result,a,b,burst.width(),s.color(),alpha);
                else spark(result,a,b,burst.width(),s.color(),alpha);
            }
        }
        return List.copyOf(result);
    }
    private static Vec3 side(Vec3 axis) {
        var s=axis.cross(new Vec3(0,1,0));
        return s.lengthSqr()<.000001?new Vec3(1,0,0):s.normalize();
    }
    private static void spark(List<Triangle> out,Vec3 a,Vec3 b,double width,int color,double alpha) {
        var axis=b.subtract(a).normalize();var s=side(axis).scale(width);var u=axis.cross(s).normalize().scale(width);
        quad(out,a.add(s),b.add(s),b.subtract(s),a.subtract(s),color,alpha);
        quad(out,a.add(u),b.add(u),b.subtract(u),a.subtract(u),color,alpha);
    }
    private static void box(List<Triangle> out,Vec3 a,Vec3 b,double width,int color,double alpha) {
        var axis=b.subtract(a).normalize();var s=side(axis).scale(width);var u=axis.cross(s).normalize().scale(width);
        Vec3 a0=a.add(s).add(u),a1=a.subtract(s).add(u),a2=a.subtract(s).subtract(u),a3=a.add(s).subtract(u);
        Vec3 b0=b.add(s).add(u),b1=b.subtract(s).add(u),b2=b.subtract(s).subtract(u),b3=b.add(s).subtract(u);
        quad(out,a0,a1,a2,a3,shade(color,.68),alpha);quad(out,b3,b2,b1,b0,color,alpha);
        quad(out,a0,b0,b1,a1,color,alpha);quad(out,a1,b1,b2,a2,shade(color,.82),alpha);
        quad(out,a2,b2,b3,a3,shade(color,.68),alpha);quad(out,a3,b3,b0,a0,shade(color,.82),alpha);
    }
    private static int shade(int color,double factor) {
        return ((int)((color>>16&255)*factor)<<16)|((int)((color>>8&255)*factor)<<8)|(int)((color&255)*factor);
    }
    private static void quad(List<Triangle> out,Vec3 a,Vec3 b,Vec3 c,Vec3 d,int color,double alpha) {
        out.add(new Triangle(a,b,c,color,alpha));out.add(new Triangle(a,c,d,color,alpha));
    }
    private WeaponImpactVisual() {}
}
