package com.dynasty;

import net.minecraft.world.phys.Vec3;
import java.util.ArrayList;
import java.util.List;

/** Sculpted celestial archer mesh. No cuboid body parts or wireframe box outlines. */
public final class HouyiAvatarShape {
    public record P(double x, double y, double z) {
        public P add(P b) { return new P(x+b.x,y+b.y,z+b.z); }
        public P sub(P b) { return new P(x-b.x,y-b.y,z-b.z); }
        public P scale(double s) { return new P(x*s,y*s,z*s); }
        public double dot(P b) { return x*b.x+y*b.y+z*b.z; }
        public P cross(P b) { return new P(y*b.z-z*b.y,z*b.x-x*b.z,x*b.y-y*b.x); }
        public P unit() { double n=Math.sqrt(dot(this)); return n<1e-9?new P(0,1,0):scale(1/n); }
    }
    public enum Material {
        ARMOR(0.17F,0.36F,0.64F), GOLD(1F,0.70F,0.28F), IVORY(0.76F,0.88F,0.98F),
        SKIN(0.95F,0.81F,0.63F), HAIR(0.07F,0.13F,0.24F), CLOTH(0.18F,0.32F,0.58F),
        LIGHT(0.32F,0.95F,1F), EMERALD(.035F,.34F,.22F), GUAN_SKIN(.66F,.075F,.075F),
        BEARD(.045F,.055F,.06F), CRIMSON(.40F,.035F,.045F), BRONZE(.55F,.34F,.12F),
        GUAN_HIGHLIGHT(.70F,.115F,.075F), GUAN_SHADOW(.31F,.028F,.023F),
        JADE_DARK(.022F,.115F,.085F), GOLD_OLD(.57F,.39F,.16F),
        GOLD_PALE(.91F,.73F,.40F), CLOTH_GREEN(.045F,.235F,.17F),
        SILK_RED(.43F,.042F,.035F), BEARD_GLEAM(.11F,.14F,.135F),
        STEEL(.58F,.69F,.67F), EYE_DARK(.012F,.016F,.015F), JADE_METAL(.035F,.25F,.20F),
        GUAN_BLADE(.045F,.155F,.145F), GUAN_BEVEL(.49F,.65F,.70F), GUAN_EDGE(.79F,.87F,.91F),
        GUAN_RELIEF(.22F,.36F,.29F), GUAN_SOCKET(.46F,.32F,.13F), GUAN_SHAFT(.055F,.070F,.058F);
        public final float r,g,b;
        Material(float r,float g,float b) {this.r=r;this.g=g;this.b=b;}
    }
    public record Face(P a,P b,P c,P d,Material material,P normal,P center) {}
    private record Volume(P center,P radius) {
        boolean contains(P p) {
            double dx=p.x-center.x,dy=p.y-center.y,dz=p.z-center.z;
            if(Math.abs(dx)>radius.x+0.5 || Math.abs(dy)>radius.y+0.5 || Math.abs(dz)>radius.z+0.5)return false;
            double x=dx/(radius.x+0.5), y=dy/(radius.y+0.5), z=dz/(radius.z+0.5);
            return x*x+y*y+z*z<=1;
        }
    }
    private static final List<Volume> VOLUMES = new ArrayList<>();
    public static final List<Face> MESH = create();

    private static List<Face> create() {
        // Retain the existing formation-volume API for server ritual particles.
        VOLUMES.add(new Volume(new P(0,5.80,0),new P(1.12,1.52,.76)));
        VOLUMES.add(new Volume(new P(0,8.14,.08),new P(.72,.87,.55)));
        for(int side:new int[]{-1,1}) {
            VOLUMES.add(new Volume(new P(side*.62,2.40,.10),new P(.46,2.30,.50)));
        }
        volume(HouyiArcherSculpture.HOLD_SHOULDER,HouyiArcherSculpture.HOLD_ELBOW,.39);
        volume(HouyiArcherSculpture.HOLD_ELBOW,HouyiArcherSculpture.GRIP,.31);
        volume(HouyiArcherSculpture.DRAW_SHOULDER,HouyiArcherSculpture.DRAW_ELBOW,.37);
        volume(HouyiArcherSculpture.DRAW_ELBOW,HouyiArcherSculpture.NOCK,.30);
        volume(HouyiArcherSculpture.BOW_TOP,HouyiArcherSculpture.GRIP,.15);
        volume(HouyiArcherSculpture.BOW_BOTTOM,HouyiArcherSculpture.GRIP,.15);
        return HouyiArcherSculpture.create();
    }
    private static void volume(P a,P b,double radius) {
        P d=b.sub(a);
        VOLUMES.add(new Volume(a.add(b).scale(.5),new P(Math.abs(d.x)/2+radius,
                Math.abs(d.y)/2+radius,Math.abs(d.z)/2+radius)));
    }

    public static Vec3 forward(float yaw) {
        double angle=Math.toRadians(yaw);
        return new Vec3(-Math.sin(angle),0,Math.cos(angle));
    }
    public static Vec3 origin(Vec3 player,float yaw) {return player.subtract(forward(yaw).scale(4));}
    public static boolean contains(double x,double y,double z,double formedHeight) {
        if(y>formedHeight)return false;
        P p=new P(x,y,z);
        for(Volume volume:VOLUMES)if(volume.contains(p))return true;
        return false;
    }
    private HouyiAvatarShape() {}
}
