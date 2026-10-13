package com.dynasty.cod3;

import com.dynasty.network.DynastyNetwork;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.PacketDistributor;
import java.util.ArrayList;
import java.util.List;

/** Cosmetic receipt of the original successful Tang speed application. */
public final class TangWind {
    public static final String CUE="equipment_tang_speed_applied";
    public static final int DURATION=12,COLOR=0x54B79A;
    /** Effect.update can return true for cosmetic flag changes, not just speed. */
    public static boolean willRefresh(LivingEntity entity) {
        var effect=entity.getEffect(MobEffects.MOVEMENT_SPEED);
        return effect==null||effect.getAmplifier()<0
                ||effect.getAmplifier()==0&&effect.getDuration()>=0&&effect.getDuration()<60;
    }
    public static void applied(LivingEntity entity) {
        if(!(entity instanceof ServerPlayer player)||!(player.level() instanceof ServerLevel level)
                ||!player.hasEffect(MobEffects.MOVEMENT_SPEED))return;
        var effect=player.getEffect(MobEffects.MOVEMENT_SPEED);
        if(effect.getAmplifier()!=0||effect.getDuration()!=60)return;
        var data=player.getPersistentData();long now=level.getGameTime();
        if(data.contains("cod3_tang_wind_at")&&data.getLong("cod3_tang_wind_at")==now)return;
        data.putLong("cod3_tang_wind_at",now);
        Vec3 travel=horizontal(player.getDeltaMovement(),player.getLookAngle());
        var packet=packet(level.dimension().location().toString(),player.getId(),level.random.nextLong(),now,player.position(),travel);
        var origin=player.position();
        DynastyNetwork.CHANNEL.send(PacketDistributor.NEAR.with(()->new PacketDistributor.TargetPoint(origin.x,origin.y,origin.z,32,level.dimension())),packet);
    }
    public static Cod3VisualPacket packet(String dimension,int entityId,long seed,long start,Vec3 origin,Vec3 direction) {
        return new Cod3VisualPacket(dimension,1,entityId,seed,start,DURATION,1,origin,direction,CUE,0,COLOR);
    }
    public static boolean accepts(Cod3VisualPacket p) {
        return p!=null&&p.valid()&&CUE.equals(p.sequence())&&p.template()==1&&p.entityId()>=0
                &&p.duration()==DURATION&&p.scale()==1&&p.tick()==0&&p.tint()==COLOR;
    }
    /** Prefer actual horizontal movement; standing/vertical-only falls back to look. */
    public static Vec3 horizontal(Vec3 movement,Vec3 fallback) {
        if(movement!=null&&Double.isFinite(movement.lengthSqr())) {
            var flat=new Vec3(movement.x,0,movement.z);if(flat.lengthSqr()>.0025)return flat.normalize();
        }
        if(fallback!=null&&Double.isFinite(fallback.lengthSqr())) {
            var flat=new Vec3(fallback.x,0,fallback.z);if(flat.lengthSqr()>1e-8)return flat.normalize();
        }
        return new Vec3(0,0,1);
    }
    public static List<WeaponImpactVisual.Triangle> geometry(Cod3VisualPacket p,double age,Vec3 feet,Vec3 movement,boolean ownFirstPerson) {
        if(!accepts(p)||!Double.isFinite(age)||age<0||age>=DURATION||feet==null||!Double.isFinite(feet.lengthSqr()))return List.of();
        var forward=horizontal(movement,p.direction());var right=new Vec3(forward.z,0,-forward.x);
        var up=new Vec3(0,1,0);var out=new ArrayList<WeaponImpactVisual.Triangle>();
        double alpha=(1-age/DURATION)*.8,extension=.65+.35*Math.min(1,age/3);
        for(int band=0;band<(ownFirstPerson?1:2);band++)for(int i=0;i<5;i++) {
            double height=(band==0?.2:.85)+((i+band)%2)*.04;
            double side=band==0?-.22:.22;
            var a=feet.add(0,height,0).add(right.scale(side)).subtract(forward.scale((.25+i*.24)*extension));
            var b=a.subtract(forward.scale(.18*extension));double width=band==0?.025:.03;
            // Separated hard rectangles, never a smooth tube or blurred sprite.
            quad(out,a,b,right.scale(width),alpha);quad(out,a,b,up.scale(width),alpha);
        }
        return List.copyOf(out);
    }
    private static void quad(List<WeaponImpactVisual.Triangle> out,Vec3 a,Vec3 b,Vec3 s,double alpha) {
        out.add(new WeaponImpactVisual.Triangle(a.add(s),b.add(s),b.subtract(s),COLOR,alpha));
        out.add(new WeaponImpactVisual.Triangle(a.add(s),b.subtract(s),a.subtract(s),COLOR,alpha));
    }
    private TangWind() {}
}
