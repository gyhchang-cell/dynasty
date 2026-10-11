package com.dynasty.cod3;

import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;

/** One local frame and volume for both authoritative hit tests and visible danger outlines. */
public record VfxVolume(DynastyVfxDefinition.Shape shape,Vec3 origin,Vec3 forward,Vec3 right,
                        double radius,double length,double halfWidth,double height,double innerRadius,
                        double halfAngle,boolean cylinder,boolean damaging,int template,double age) {
    public static VfxVolume of(DynastyVfxDefinition d,Vec3 at,Vec3 direction,double scale,double expansion,double age){
        return of(d,at,direction,scale,expansion,age,d.duration());
    }
    public static VfxVolume of(DynastyVfxDefinition d,Vec3 at,Vec3 direction,double scale,double expansion,double age,int lifetime){
        boolean pitched=(d.shape()==DynastyVfxDefinition.Shape.LINE&&d.id()!=10&&d.id()!=34)||d.shape()==DynastyVfxDefinition.Shape.CHAIN;
        Vec3 forward=pitched?direction:new Vec3(direction.x,0,direction.z);
        forward=forward.lengthSqr()<1e-10?new Vec3(0,0,1):forward.normalize();
        Vec3 right=new Vec3(0,1,0).cross(forward);if(right.lengthSqr()<1e-10)right=new Vec3(1,0,0);else right=right.normalize();
        double radius=d.radius()*scale*expansion,length=d.length()*scale*expansion,halfWidth=d.width()*scale/2;
        double height=Math.max(1,d.width())*scale;
        var shape=d.shape();boolean cylinder=d.id()==5||d.id()==9;
        if(d.id()==24)shape=DynastyVfxDefinition.Shape.LINE;
        if(d.id()==20)shape=DynastyVfxDefinition.Shape.ANNULUS;
        if(cylinder||shape==DynastyVfxDefinition.Shape.BOX||shape==DynastyVfxDefinition.Shape.RECT||shape==DynastyVfxDefinition.Shape.ANNULUS)height=d.length()*scale;
        if(d.id()==26)radius=(6+(d.radius()-6)*expansion)*scale;
        if(d.id()==31){shape=DynastyVfxDefinition.Shape.TARGET_LOCK;radius=d.radius()*scale;}
        if(d.id()==39){shape=DynastyVfxDefinition.Shape.CIRCLE;height=scale;}
        if(d.id()==37)at=at.add(forward.scale(VfxTimeline.bloodOffset(age,lifetime)*scale));
        if(shape==DynastyVfxDefinition.Shape.SPHERE)at=at.add(0,radius,0);
        return new VfxVolume(shape,at,forward,right,radius,length,halfWidth,height,Math.max(0,radius-d.width()*scale),Math.toRadians(d.id()==36?30:d.id()==19?45:35),cylinder,d.damaging(),d.id(),age);
    }
    public Vec3 point(double x,double y,double z){
        Vec3 up=forward.cross(right);return origin.add(right.scale(x)).add(up.scale(y)).add(forward.scale(z));
    }
    public double halfLength(){return template==37?halfWidth:radius;}
    public int branches(){return template==13?3:1;}
    public Vec3 centerline(int branch,double t){
        double phase=age*.06+branch*Math.PI*2/branches();
        return point(Math.sin(t*Math.PI*4+phase)*radius*.65,Math.sin(t*Math.PI*2+phase)*radius*.3,t*length);
    }
    public boolean contains(Vec3 point){
        if(!damaging||point==null||!Double.isFinite(point.lengthSqr()))return false;
        Vec3 p=point.subtract(origin);double x=p.dot(right),z=p.dot(forward),y=p.dot(forward.cross(right));
        double radial=p.horizontalDistance(),epsilon=1e-7;
        return switch(shape){
            case SPHERE->p.lengthSqr()<=radius*radius+epsilon;
            case LINE->z>=-epsilon&&z<=length+epsilon&&x*x+y*y<=halfWidth*halfWidth+epsilon;
            case CHAIN->{
                boolean hit=false;
                for(int branch=0;branch<branches()&&!hit;branch++){
                    Vec3 last=centerline(branch,0);
                    for(int segment=1;segment<=32&&!hit;segment++){
                        Vec3 next=centerline(branch,segment/32.0),delta=next.subtract(last);
                        double along=delta.lengthSqr()<epsilon?0:Math.max(0,Math.min(1,point.subtract(last).dot(delta)/delta.lengthSqr()));
                        hit=last.add(delta.scale(along)).distanceToSqr(point)<=halfWidth*halfWidth+epsilon;last=next;
                    }
                }
                yield hit;
            }
            case CIRCLE,TARGET_LOCK->radial<=radius+epsilon&&p.y>=-epsilon&&p.y<=height+epsilon;
            case ANNULUS->radial>=innerRadius-epsilon&&radial<=radius+epsilon&&p.y>=-epsilon&&p.y<=height+epsilon;
            case CONE->radial<=radius+epsilon&&p.y>=-epsilon&&p.y<=height+epsilon&&(radial<epsilon||z/radial>=Math.cos(halfAngle)-epsilon);
            case RECT,BOX->p.y>=-epsilon&&p.y<=height+epsilon&&(cylinder?radial<=radius+epsilon:Math.abs(x)<=radius+epsilon&&Math.abs(z)<=halfLength()+epsilon);
        };
    }
    public AABB bounds(){
        if(shape==DynastyVfxDefinition.Shape.LINE||shape==DynastyVfxDefinition.Shape.CHAIN)return new AABB(origin,origin.add(forward.scale(length))).inflate(halfWidth+(shape==DynastyVfxDefinition.Shape.CHAIN?radius:0));
        if(shape==DynastyVfxDefinition.Shape.SPHERE)return new AABB(origin,origin).inflate(radius);
        if(template==37){double x=Math.abs(right.x)*radius+Math.abs(forward.x)*halfLength(),z=Math.abs(right.z)*radius+Math.abs(forward.z)*halfLength();return new AABB(origin.x-x,origin.y,origin.z-z,origin.x+x,origin.y+height,origin.z+z);}
        double horizontal=(shape==DynastyVfxDefinition.Shape.BOX||shape==DynastyVfxDefinition.Shape.RECT)&&!cylinder?radius*Math.sqrt(2):radius;
        return new AABB(origin.x-horizontal,origin.y,origin.z-horizontal,origin.x+horizontal,origin.y+height,origin.z+horizontal);
    }
}
