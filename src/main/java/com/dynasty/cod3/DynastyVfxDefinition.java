package com.dynasty.cod3;

import net.minecraft.world.phys.Vec3;

/** Shared spatial parameters; existing attacks keep their damage pipeline. */
public record DynastyVfxDefinition(int id,String name,Shape shape,int duration,double radius,double length,double width,int color,int near,int medium,int far) {
    public DynastyVfxDefinition {
        if(id<1||id>40||name==null||shape==null||duration<1||duration>2400||!Double.isFinite(radius)||radius<=0||!Double.isFinite(length)||length<=0||!Double.isFinite(width)||width<=0||color<0||color>0xffffff||far<1||medium<=far||near<=medium)
            throw new IllegalArgumentException("Invalid VFX definition");
    }
    public enum Shape {CIRCLE,ANNULUS,CONE,LINE,RECT,BOX,SPHERE,CHAIN,TARGET_LOCK}
    public DynastyVfxDefinition withShape(Shape value){return new DynastyVfxDefinition(id,name,value,duration,radius,length,width,color,near,medium,far);}
    public boolean damaging(){return switch(id){case 4,18,22,23,27,28,29->false;default->true;};}
    public boolean contains(Vec3 point,Vec3 origin,Vec3 direction){return VfxVolume.of(this,origin,direction,1,1,0).contains(point);}
    public int budget(double distance,boolean low){return Math.max(1,(distance<32?near:distance<96?medium:far)/(low?4:1));}
}
