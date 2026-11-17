package com.dynasty.cod3;

import com.dynasty.*;
import com.dynasty.network.DynastyNetwork;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.damagesource.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;
import java.util.*;

/** Cosmetic receipt for the existing 360-degree sweep. Never damages or moves an entity. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class FangtianSweep {
    public static final String CUE="equipment_confirmed_fangtian_sweep",STAMP="cod3_confirmed_sweep_at";
    public static final int DURATION=6;
    private static final ThreadLocal<Receipt> ACTIVE=new ThreadLocal<>();
    private static final List<Receipt> PENDING=new ArrayList<>();
    private record Start(ServerPlayer player,LivingEntity main,long tick) {}
    private static final List<Start> STARTS=new ArrayList<>();
    private record Contact(LivingEntity target,float health) {}
    public static final class Receipt {
        final ServerPlayer player;final LivingEntity main;final ServerLevel level;final long tick;final Vec3 origin,direction;
        final float health;final List<Contact> contacts=new ArrayList<>();
        final DamageSource primary;boolean secondary,primaryDamage;
        Receipt(ServerPlayer p,LivingEntity t,DamageSource source) {
            player=p;main=t;primary=source;level=p.serverLevel();tick=level.getGameTime();health=t.getHealth();
            origin=t.position().add(0,Math.min(1.1,t.getBbHeight()*.5),0);
            double yaw=Math.toRadians(p.getYRot());direction=new Vec3(-Math.sin(yaw),0,Math.cos(yaw));
        }
    }
    public static Receipt begin(LivingEntity attacker,LivingEntity main,DamageSource source) {
        if(!(attacker instanceof ServerPlayer p)||main.level()!=p.level()||!main.isAlive()
                ||!source.is(DamageTypes.PLAYER_ATTACK)||!real(source,1,p)
                ||DynastyTrinketOnHit.isSyntheticDamage()||!DynastySchoolCombat.observedPrimary(p,main)
                ||!"halberd_fangtian".equals(DynastyTrinkets.idOf(DynastySchoolCombat.primaryStack(p,main))))return null;
        boolean nativeAttack=STARTS.removeIf(s->s.player==p&&s.main==main&&s.tick==p.serverLevel().getGameTime());
        if(!nativeAttack)return null;
        var r=new Receipt(p,main,source);ACTIVE.set(r);return r;
    }
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void attack(net.minecraftforge.event.entity.player.AttackEntityEvent e) {
        if(e.isCanceled()||!(e.getEntity() instanceof ServerPlayer p)||!(e.getTarget() instanceof LivingEntity main)
                ||!"halberd_fangtian".equals(DynastyTrinkets.idOf(p.getMainHandItem())))return;
        STARTS.removeIf(s->s.player==p);if(STARTS.size()>=32)STARTS.remove(0);
        STARTS.add(new Start(p,main,p.serverLevel().getGameTime()));
    }
    public static void finish(Receipt r) {
        if(r==null)return;
        ACTIVE.remove();
        // The original hurt calls have returned: a canceled/zero final event cannot fake contact.
        r.secondary=r.contacts.stream().anyMatch(c->c.target.getHealth()<c.health);
        if(PENDING.size()>=32)PENDING.remove(0);PENDING.add(r);
    }
    private static boolean real(DamageSource s,float amount,ServerPlayer p) {
        return amount>0&&Float.isFinite(amount)&&s.getEntity()==p&&s.getDirectEntity()==p
                &&!DynastyTrinketOnHit.isSyntheticDamage()&&!EdictSpells.isSpell(s)
                &&!QinglongDescent.isDragonDamage(s)&&!DynastyBowRitual.isSolarDamage(s);
    }
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void damage(LivingDamageEvent e) {
        if(e.isCanceled())return;
        var active=ACTIVE.get();
        if(active!=null&&e.getEntity()!=active.main&&e.getEntity()!=active.player&&e.getSource().is(DamageTypes.MOB_ATTACK)
                &&real(e.getSource(),e.getAmount(),active.player)&&active.contacts.size()<64)
            active.contacts.add(new Contact(e.getEntity(),e.getEntity().getHealth()));
        for(var r:PENDING)if(r.main==e.getEntity()&&r.primary==e.getSource()&&real(e.getSource(),e.getAmount(),r.player)
                &&e.getSource().is(DamageTypes.PLAYER_ATTACK))r.primaryDamage=true;
    }
    @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e) {
        if(e.phase!=TickEvent.Phase.END)return;
        STARTS.clear();
        for(var it=PENDING.iterator();it.hasNext();) {
            var r=it.next();it.remove();var p=r.player;long now=p.serverLevel().getGameTime();
            // Native C2S damage may precede the next END by one world tick.
            long age=now-r.tick;
            if(age<0||age>1||!p.isAlive()||p.isRemoved()||p.serverLevel()!=r.level||r.main.level()!=r.level
                    ||!(r.secondary||r.primaryDamage&&r.main.getHealth()<r.health))continue;
            var n=p.getPersistentData();if(n.contains(STAMP)&&n.getLong(STAMP)==now)continue;n.putLong(STAMP,now);
            var packet=packet(p.serverLevel().dimension().location().toString(),p.getId(),now,r.origin,r.direction);
            DynastyNetwork.CHANNEL.send(PacketDistributor.NEAR.with(()->new PacketDistributor.TargetPoint(r.origin.x,r.origin.y,r.origin.z,32,p.serverLevel().dimension())),packet);
        }
    }
    @SubscribeEvent public static void stopped(net.minecraftforge.event.server.ServerStoppedEvent e){ACTIVE.remove();PENDING.clear();STARTS.clear();}
    public static Cod3VisualPacket packet(String dim,int actor,long start,Vec3 origin,Vec3 direction) {
        return new Cod3VisualPacket(dim,2,actor,0,start,DURATION,1,origin,TangWind.horizontal(direction,Vec3.ZERO),CUE,0,0x91B6B7);
    }
    public static boolean accepts(Cod3VisualPacket p) {
        return p!=null&&p.valid()&&CUE.equals(p.sequence())&&p.template()==2&&p.entityId()>=0
                &&p.duration()==DURATION&&p.scale()==1&&p.tick()==0&&p.tint()==0x91B6B7
                &&Math.abs(p.direction().y)<1e-6&&Math.abs(p.direction().lengthSqr()-1)<1e-6;
    }
    /** Faceted contact ornament, not a depiction of the original box's exact damage boundary. */
    public static List<WeaponImpactVisual.Triangle> geometry(Cod3VisualPacket p,double age) {
        if(!accepts(p)||!Double.isFinite(age)||age<0||age>=DURATION)return List.of();
        var out=new ArrayList<WeaponImpactVisual.Triangle>();double alpha=.8*(1-age/DURATION);
        double heading=Math.atan2(p.direction().x,p.direction().z),step=Math.PI/6,phase=heading+age/DURATION*Math.PI*2;
        for(int i=0;i<12;i++) {
            double a=heading+i*step,b=a+step;
            quad(out,at(p,a,1.27,-.035),at(p,a,1.31,.035),at(p,b,1.31,.035),at(p,b,1.27,-.035),0x647F83,alpha*.65);
        }
        for(int i=0;i<6;i++) {
            double a=phase+(i-3)*step,b=a+step,width=.025+.105*(1-Math.abs((i-2.5)/3));
            quad(out,at(p,a,1.15-width,0),at(p,a,1.15+width,0),at(p,b,1.15+width,0),at(p,b,1.15-width,0),p.tint(),alpha);
            quad(out,at(p,a,1.15,-width*.55),at(p,a,1.15,width*.55),at(p,b,1.15,width*.55),at(p,b,1.15,-width*.55),p.tint(),alpha);
        }
        return List.copyOf(out);
    }
    private static Vec3 at(Cod3VisualPacket p,double angle,double radius,double y){return p.origin().add(Math.sin(angle)*radius,y,Math.cos(angle)*radius);}
    private static void quad(List<WeaponImpactVisual.Triangle> out,Vec3 a,Vec3 b,Vec3 c,Vec3 d,int color,double alpha) {
        out.add(new WeaponImpactVisual.Triangle(a,b,c,color,alpha));out.add(new WeaponImpactVisual.Triangle(a,c,d,color,alpha));
    }
    private FangtianSweep() {}
}
