package com.dynasty.cod3;

import com.dynasty.Dynasty;
import com.dynasty.network.DynastyNetwork;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;
import java.util.*;

/** Presentation receipt from real morale reduction; never changes combat values. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class ArmorCrack {
    public static final String PREFIX="equipment_morale_crack_";
    public static final int DURATION=10,DARK=0x3C4045;
    private record Receipt(DamageSource source,UUID attacker,UUID victim,String dimension,long tick,String weapon) {}
    private static final List<Receipt> PENDING=new ArrayList<>();
    private static final String[] MASK={"........",".CCCCCC.",".CCC.DC.",".CC.DCC.",".CCD.CC.",".CC.DCC.",".CD.CCC.","........"};
    public static int color(String weapon){return "pojun_axe".equals(weapon)?0xD2A164:"xuantian_axe".equals(weapon)?0xA09ABD:-1;}
    /** Called only next to the unchanged toughness *= .5 operation. */
    public static void reduced(LivingHurtEvent event,LivingEntity attacker,String weapon,double before,double after) {
        if(color(weapon)<0||event.isCanceled()||event.getAmount()<=0||!(attacker instanceof ServerPlayer player)
                ||!(event.getEntity().level() instanceof ServerLevel level)||!Double.isFinite(before)||before<=0
                ||before!=com.dynasty.DynastyBalance.mobToughness(event.getEntity().getType())
                ||!Double.isFinite(after)||after!=before*.5||event.getSource().getDirectEntity()!=player||event.getSource().getEntity()!=player
                ||!event.getSource().is(DamageTypes.PLAYER_ATTACK))return;
        if(PENDING.size()>=32)PENDING.remove(0);
        PENDING.add(new Receipt(event.getSource(),player.getUUID(),event.getEntity().getUUID(),level.dimension().location().toString(),level.getGameTime(),weapon));
    }
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void finalDamage(LivingDamageEvent event) {
        Receipt receipt=null;
        for(int i=PENDING.size()-1;i>=0;i--) {
            var candidate=PENDING.get(i);
            if(candidate.source()==event.getSource()&&candidate.victim().equals(event.getEntity().getUUID())){receipt=PENDING.remove(i);break;}
        }
        if(receipt==null||event.isCanceled()||event.getAmount()<=0||!(event.getSource().getEntity() instanceof ServerPlayer player)
                ||!(event.getEntity().level() instanceof ServerLevel level)||receipt.tick()!=level.getGameTime()
                ||!receipt.attacker().equals(player.getUUID())||!receipt.dimension().equals(level.dimension().location().toString()))return;
        var data=player.getPersistentData();long now=level.getGameTime();
        if(data.contains("cod3_armor_crack_at")&&data.getLong("cod3_armor_crack_at")==now)return;
        data.putLong("cod3_armor_crack_at",now);
        var victim=event.getEntity();var direction=TangWind.horizontal(player.getLookAngle(),Vec3.ZERO);
        var origin=anchor(victim.position(),victim.getBbWidth(),victim.getBbHeight(),direction);
        var packet=packet(level.dimension().location().toString(),victim.getId(),receipt.weapon(),level.random.nextLong(),now,
                Math.max(.45,Math.min(1.2,victim.getBbWidth()*.8)),origin,direction);
        DynastyNetwork.CHANNEL.send(PacketDistributor.NEAR.with(()->new PacketDistributor.TargetPoint(origin.x,origin.y,origin.z,32,level.dimension())),packet);
    }
    @SubscribeEvent public static void clear(TickEvent.ServerTickEvent event){if(event.phase==TickEvent.Phase.END)PENDING.clear();}
    @SubscribeEvent public static void stopped(net.minecraftforge.event.server.ServerStoppedEvent event){PENDING.clear();}
    public static Vec3 anchor(Vec3 feet,double width,double height,Vec3 direction) {
        return feet.add(0,height*.55,0).subtract(TangWind.horizontal(direction,Vec3.ZERO).scale(width*.5+.025));
    }
    public static Cod3VisualPacket packet(String dimension,int entityId,String weapon,long seed,long start,double scale,Vec3 origin,Vec3 direction) {
        if(color(weapon)<0)return null;
        return new Cod3VisualPacket(dimension,27,entityId,seed,start,DURATION,scale,origin,direction,PREFIX+weapon,0,color(weapon));
    }
    public static boolean accepts(Cod3VisualPacket p) {
        if(p==null||!p.valid()||!p.sequence().startsWith(PREFIX))return false;
        int tint=color(p.sequence().substring(PREFIX.length()));
        return tint>=0&&p.tint()==tint&&p.template()==27&&p.entityId()>=0&&p.tick()==0&&p.duration()==DURATION&&p.scale()>=.45&&p.scale()<=1.2;
    }
    public static List<WeaponImpactVisual.Triangle> geometry(Cod3VisualPacket p,double age,Vec3 center) {
        if(!accepts(p)||!Double.isFinite(age)||age<0||age>=DURATION||center==null||!Double.isFinite(center.lengthSqr()))return List.of();
        var normal=TangWind.horizontal(p.direction(),Vec3.ZERO);var right=new Vec3(normal.z,0,-normal.x);var up=new Vec3(0,1,0);
        var out=new ArrayList<WeaponImpactVisual.Triangle>();double cell=p.scale()/8,split=Math.min(.09,age*.014)*p.scale(),alpha=(1-age/DURATION)*.9;
        for(int y=1;y<7;y++)for(int x=1;x<7;x++) {
            char pixel=MASK[y].charAt(x);if(pixel=='.')continue;
            double shift=pixel=='D'?0:(x<4?-split:split);
            rect(out,center,right,up,(x-4)*cell+shift,(3-y)*cell,cell,cell,pixel=='D'?DARK:p.tint(),alpha);
        }
        for(int i=0;i<4;i++) {
            double side=i%2==0?-1:1;
            rect(out,center,right,up,side*(.25+age*.035)*p.scale(),(.2-i*.12+age*.04-age*age*.004)*p.scale(),cell*.6,cell*.6,p.tint(),alpha);
        }
        return List.copyOf(out);
    }
    private static void rect(List<WeaponImpactVisual.Triangle> out,Vec3 c,Vec3 r,Vec3 u,double x,double y,double w,double h,int color,double alpha) {
        var a=c.add(r.scale(x)).add(u.scale(y));var b=a.add(r.scale(w));var d=a.add(u.scale(h));var e=b.add(u.scale(h));
        out.add(new WeaponImpactVisual.Triangle(a,b,e,color,alpha));out.add(new WeaponImpactVisual.Triangle(a,e,d,color,alpha));
    }
    private ArmorCrack() {}
}
