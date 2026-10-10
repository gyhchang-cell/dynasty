package com.dynasty.cod3;

import net.minecraft.world.phys.Vec3;

public record VfxInstance(DynastyVfxDefinition definition,Vec3 origin,Vec3 direction,long seed,long start,
                          int lifetime,double scale,int windupTicks,int activeTicks,int spawnTicks) {
    public VfxInstance(DynastyVfxDefinition d,Vec3 origin,Vec3 direction,long seed,long start,int lifetime,double scale){
        this(d,origin,direction,seed,start,lifetime,scale,windup(d,lifetime),
            Math.max(1,Math.min(lifetime-windup(d,lifetime),(int)Math.ceil(VfxTimeline.timing(d,lifetime).sustainEnd())-windup(d,lifetime))),
            Math.min(windup(d,lifetime),(int)Math.ceil(VfxTimeline.timing(d,lifetime).spawnEnd())));
    }
    public VfxInstance(DynastyVfxDefinition d,Vec3 origin,Vec3 direction,long seed,long start,int lifetime,double scale,int windup,int active){
        this(d,origin,direction,seed,start,lifetime,scale,windup,active,Math.min(2,windup));
    }
    private static int windup(DynastyVfxDefinition d,int lifetime){return Math.max(0,Math.min(lifetime-1,(int)Math.ceil(VfxTimeline.timing(d,lifetime).expandEnd())));}
    public VfxInstance {
        if(definition==null||origin==null||direction==null||!Double.isFinite(origin.lengthSqr())||!Double.isFinite(direction.lengthSqr())
                ||lifetime<1||lifetime>2400||!Double.isFinite(scale)||scale<=0||scale>32||windupTicks<0||activeTicks<1||windupTicks+activeTicks>lifetime||spawnTicks<0||spawnTicks>windupTicks)
            throw new IllegalArgumentException("Invalid VFX instance");
    }
    public enum Phase {SPAWN,EXPAND,SUSTAIN,COLLAPSE,END}
    public Phase phase(double age){return age<0||age>=lifetime?Phase.END:age<spawnTicks?Phase.SPAWN:age<windupTicks?Phase.EXPAND:age<windupTicks+activeTicks?Phase.SUSTAIN:Phase.COLLAPSE;}
    public double expansion(double age){return windupTicks==spawnTicks?1:Math.max(0,Math.min(1,(age-spawnTicks)/(windupTicks-spawnTicks)));}
    public VfxVolume volume(double age){return VfxVolume.of(definition,origin,direction,scale,expansion(age),age,lifetime);}
    public boolean contains(Vec3 point,double age){return phase(age)==Phase.SUSTAIN&&volume(age).contains(point);}
    public static VfxInstance combat(Cod3VisualPacket packet){
        String[] parts=packet.sequence().split("_");
        if(parts.length!=3&&parts.length!=4||!parts[0].equals("combat")||parts.length==4&&(!parts[3].equals("disk")||packet.template()!=12))throw new IllegalArgumentException("Invalid combat timing");
        var definition=Cod3Catalog.vfx(packet.template());if(parts.length==4)definition=definition.withShape(DynastyVfxDefinition.Shape.CIRCLE);
        return new VfxInstance(definition,packet.origin(),packet.direction(),packet.seed(),packet.start(),packet.duration(),packet.scale(),Integer.parseInt(parts[1]),Integer.parseInt(parts[2]));
    }
}
