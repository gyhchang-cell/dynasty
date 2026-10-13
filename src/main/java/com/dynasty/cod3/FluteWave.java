package com.dynasty.cod3;

import com.dynasty.*;
import com.dynasty.network.DynastyNetwork;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.network.PacketDistributor;
import java.util.*;

/** Observe original flute effect applications. Never applies effects, damage, sound or cooldowns. */
public final class FluteWave {
    public static final String CUE="equipment_flute_debuff_applied",STAMP="cod3_flute_wave_at";
    public static final int DURATION=10,COLOR=0x65B99B;
    private record Effect(boolean present,int amplifier,int duration) {
        static Effect of(LivingEntity t,MobEffect type) {
            var e=t.getEffect(type);return e==null?new Effect(false,0,0):new Effect(true,e.getAmplifier(),e.getDuration());
        }
    }
    public record Before(Effect weakness,Effect slow) {}
    public record Cast(ServerPlayer player,ServerLevel level,long tick,Vec3 anchor,Vec3 direction,InteractionHand hand) {}
    public static Cast capture(net.minecraft.world.level.Level level,net.minecraft.world.entity.player.Player caster,ItemStack original,InteractionHand hand) {
        if(!(caster instanceof ServerPlayer p)||!(level instanceof ServerLevel server)||p.level()!=level
                ||!original.is(DynastyWeapons.YU_DI.get()))return null;
        return new Cast(p,server,server.getGameTime(),p.position().add(0,p.getEyeHeight()*.7,0),TangWind.horizontal(p.getLookAngle(),Vec3.ZERO),hand);
    }
    public static Before snapshot(LivingEntity t){return new Before(Effect.of(t,MobEffects.WEAKNESS),Effect.of(t,MobEffects.MOVEMENT_SLOWDOWN));}
    private static boolean refreshed(Effect old,Effect now) {
        return now.present&&now.amplifier==1&&now.duration==120&&(!old.present||old.amplifier<1
                ||old.amplifier==1&&old.duration>=0&&old.duration<120);
    }
    public static boolean changed(LivingEntity t,Before before) {
        return before!=null&&t.isAlive()&&(refreshed(before.weakness,Effect.of(t,MobEffects.WEAKNESS))
                ||refreshed(before.slow,Effect.of(t,MobEffects.MOVEMENT_SLOWDOWN)));
    }
    public static void applied(Cast cast,int confirmed) {
        if(cast==null||confirmed<=0)return;
        var p=cast.player;var level=cast.level;
        if(!p.isAlive()||p.isRemoved()||p.level()!=level||level.getGameTime()!=cast.tick
                ||p.position().add(0,p.getEyeHeight()*.7,0).distanceToSqr(cast.anchor)>64)return;
        var n=p.getPersistentData();long now=level.getGameTime();
        if(n.contains(STAMP)&&n.getLong(STAMP)==now)return;n.putLong(STAMP,now);
        var anchor=cast.anchor;
        var packet=packet(level.dimension().location().toString(),p.getId(),now,anchor,cast.direction,cast.hand);
        DynastyNetwork.CHANNEL.send(PacketDistributor.NEAR.with(()->new PacketDistributor.TargetPoint(anchor.x,anchor.y,anchor.z,32,level.dimension())),packet);
    }
    public static Cod3VisualPacket packet(String dim,int caster,long start,Vec3 anchor,Vec3 look,InteractionHand hand) {
        return new Cod3VisualPacket(dim,26,caster,0,start,DURATION,1,anchor,TangWind.horizontal(look,Vec3.ZERO),CUE,hand==InteractionHand.OFF_HAND?1:0,COLOR);
    }
    public static boolean accepts(Cod3VisualPacket p) {
        return p!=null&&p.valid()&&CUE.equals(p.sequence())&&p.template()==26&&p.entityId()>=0&&p.duration()==DURATION
                &&p.scale()==1&&p.tick()<=1&&p.tint()==COLOR&&Math.abs(p.direction().y)<1e-6&&Math.abs(p.direction().lengthSqr()-1)<1e-6;
    }
    /** Contact ornament: original eight-block inflated box is instantaneous, not this expanding pulse. */
    public static List<WeaponImpactVisual.Triangle> geometry(Cod3VisualPacket p,double age) {
        if(!accepts(p)||!Double.isFinite(age)||age<0||age>=DURATION)return List.of();
        var out=new ArrayList<WeaponImpactVisual.Triangle>();double heading=Math.atan2(p.direction().x,p.direction().z),step=Math.PI/6;
        for(int pulse=0;pulse<3;pulse++) {
            double life=age-pulse*3;if(life<0||life>=4)continue;
            double radius=.35+life*.5,width=.04-life*.003,alpha=.72*(1-life/4);
            int tint=pulse==1?0xA0CCAE:COLOR;
            for(int i=0;i<12;i++) {
                double a=heading+i*step,b=a+step;
                quad(out,at(p,a,radius-width,0),at(p,a,radius+width,0),at(p,b,radius+width,0),at(p,b,radius-width,0),tint,alpha);
                quad(out,at(p,a,radius,-width),at(p,a,radius,width),at(p,b,radius,width),at(p,b,radius,-width),tint,alpha);
            }
        }
        return List.copyOf(out);
    }
    private static Vec3 at(Cod3VisualPacket p,double angle,double r,double y){return p.origin().add(Math.sin(angle)*r,y,Math.cos(angle)*r);}
    private static void quad(List<WeaponImpactVisual.Triangle> out,Vec3 a,Vec3 b,Vec3 c,Vec3 d,int color,double alpha) {
        out.add(new WeaponImpactVisual.Triangle(a,b,c,color,alpha));out.add(new WeaponImpactVisual.Triangle(a,c,d,color,alpha));
    }
    private FluteWave() {}
}
