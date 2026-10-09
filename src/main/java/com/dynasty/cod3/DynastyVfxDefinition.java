package com.dynasty.cod3;

import net.minecraft.world.phys.Vec3;

/** Shared spatial parameters; existing attacks keep their damage pipeline. */
public record DynastyVfxDefinition(int id,String name,Shape shape,int duration,double radius,double length,double width,int color,int near,int medium,int far) {
    public enum Shape {CIRCLE,ANNULUS,CONE,LINE,RECT,BOX,SPHERE,CHAIN,TARGET_LOCK}
    public boolean contains(Vec3 point,Vec3 origin,Vec3 direction){
        Vec3 p=point.subtract(origin),forward=direction.normalize();double along=p.dot(forward),radial=p.horizontalDistance();
        return switch(shape){
            case SPHERE->p.lengthSqr()<=radius*radius;
            case CIRCLE,TARGET_LOCK->radial<=radius&&Math.abs(p.y)<=width;
            case ANNULUS->Math.abs(radial-radius)<=width&&Math.abs(p.y)<=Math.max(1,width);
            case LINE,CHAIN->along>=0&&along<=length&&p.subtract(forward.scale(along)).lengthSqr()<=width*width;
            case CONE->p.length()<=radius&&p.normalize().dot(forward)>=Math.cos(Math.toRadians(35));
            case RECT,BOX->Math.abs(p.x)<=radius&&Math.abs(p.z)<=radius&&p.y>=0&&p.y<=length;
        };
    }
    public int budget(double distance,boolean low){return Math.max(1,(distance<32?near:distance<96?medium:far)/(low?4:1));}
}
