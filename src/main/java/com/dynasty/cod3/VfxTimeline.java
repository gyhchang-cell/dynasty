package com.dynasty.cod3;

import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;

/** Canonical template timing, independent of the caller's scaled lifetime. */
public final class VfxTimeline {
    private static final int[][] TIMING={
        {2,6,10,8},{2,8,12,6},{1,4,6,6},{0,4,14,32},{3,8,26,4},
        {1,4,6,3},{2,8,10,5},{3,12,14,4},{4,12,30,2},{2,6,8,4},
        {4,10,26,3},{2,8,10,4},{2,8,14,4},{2,5,20,8},{4,12,16,3},
        {4,16,20,2},{4,12,30,1},{0,8,12,4},{2,8,12,3},{6,16,20,2},
        {2,10,14,4},{6,14,20,1},{0,4,6,4},{2,8,12,2},{3,8,14,3},
        {1,8,10,5},{1,6,8,4},{2,6,20,3},{0,6,8,6},{4,16,20,2},
        {1,3,5,3},{3,8,44,3},{4,16,20,1},{1,5,9,4},{2,6,10,3},
        {2,6,10,3},{4,16,20,1},{4,12,16,2},{3,12,14,2},{6,16,20,2}
    };
    public record Timing(double spawnEnd,double expandEnd,double sustainEnd,int limit) {
        public VfxInstance.Phase phase(double age,int lifetime){
            return age<0||age>=lifetime?VfxInstance.Phase.END:age<spawnEnd?VfxInstance.Phase.SPAWN:
                age<expandEnd?VfxInstance.Phase.EXPAND:age<sustainEnd?VfxInstance.Phase.SUSTAIN:VfxInstance.Phase.COLLAPSE;
        }
        public double expansion(double age){return Math.max(0,Math.min(1,(age-spawnEnd)/Math.max(1e-9,expandEnd-spawnEnd)));}
        public double collapse(double age,int lifetime){return Math.max(0,Math.min(1,(age-sustainEnd)/Math.max(1e-9,lifetime-sustainEnd)));}
        public double alpha(double age,int lifetime){return Math.max(0,Math.min(1,(age+1)/Math.max(1,spawnEnd)))*(1-collapse(age,lifetime));}
    }
    public static Timing timing(DynastyVfxDefinition definition,int lifetime){
        int[] t=TIMING[definition.id()-1];double ratio=lifetime/(double)definition.duration();
        return new Timing(t[0]*ratio,t[1]*ratio,t[2]*ratio,t[3]);
    }
    /** Four blocks per second outbound, then retreat during the authored collapse. */
    public static double bloodOffset(double age,int lifetime){
        var d=Cod3Catalog.vfx(37);var t=timing(d,lifetime);
        return Math.max(0,Math.min(age,t.sustainEnd()))*.2*(1-t.collapse(age,lifetime));
    }
    public static int limit(int id){return TIMING[id-1][3];}
    public static SoundEvent sound(int id){
        return switch(id){
            case 1,2,29,34->SoundEvents.PLAYER_ATTACK_SWEEP;
            case 3,30->SoundEvents.ARROW_HIT;
            case 4->SoundEvents.ARROW_SHOOT;
            case 21->SoundEvents.EXPERIENCE_ORB_PICKUP;
            case 5,39->SoundEvents.FIRECHARGE_USE;
            case 6->SoundEvents.LIGHTNING_BOLT_THUNDER;
            case 7->SoundEvents.PLAYER_SPLASH;
            case 8,24,36->SoundEvents.GLASS_BREAK;
            // 1.20.1 has no WIND or BELL field; use the existing wind and bell sounds.
            case 9,25->SoundEvents.ELYTRA_FLYING;
            case 10,27->SoundEvents.GRAVEL_BREAK;
            case 11,14->SoundEvents.AMBIENT_SOUL_SAND_VALLEY_MOOD.value();
            case 12->SoundEvents.BELL_BLOCK;
            case 13,23->SoundEvents.ENDERMAN_TELEPORT;
            case 15->SoundEvents.FIREWORK_ROCKET_LAUNCH;
            case 16,40->SoundEvents.ENDER_DRAGON_GROWL;
            case 17->SoundEvents.ENDER_DRAGON_AMBIENT;
            case 18->SoundEvents.POLAR_BEAR_WARNING;
            case 19->SoundEvents.ENDER_DRAGON_FLAP;
            case 20,33->SoundEvents.WITHER_SPAWN;
            case 22->SoundEvents.TOTEM_USE;
            case 26->SoundEvents.GENERIC_EXPLODE;
            case 28->SoundEvents.BEACON_ACTIVATE;
            case 31->SoundEvents.AMBIENT_BASALT_DELTAS_MOOD.value();
            case 32->SoundEvents.AMBIENT_CAVE.value();
            case 35->SoundEvents.SKELETON_HURT;
            case 37->SoundEvents.AMBIENT_UNDERWATER_ENTER;
            case 38->SoundEvents.WITHER_BREAK_BLOCK;
            default->throw new IllegalArgumentException("Unknown VFX template");
        };
    }
    private VfxTimeline(){}
}
