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
        STEEL(.58F,.69F,.67F), EYE_DARK(.012F,.016F,.015F), JADE_METAL(.035F,.25F,.20F);
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
    private static final List<Face> BUILD = new ArrayList<>();
    private static final List<Volume> VOLUMES = new ArrayList<>();
    public static final List<Face> MESH = create();

    private static List<Face> create() {
        // Anatomical silhouette: taper at waist, wider chest, neck, separate articulated limbs.
        loft(0,0,new double[][]{{4.05,.70,.40},{4.55,.68,.40},{5.2,.76,.46},
                {5.9,1.02,.53},{6.6,1.16,.56},{7.05,.93,.43},{7.3,.45,.29}},Material.ARMOR,24);
        ellipsoid(p(0,7.43,0),p(.31,.38,.30),Material.SKIN,16,10);
        for(int side:new int[]{-1,1}) {
            double x=side*.47;
            tube(p(x,4.2,0),p(side*.56,2.3,.08),.43,.30,Material.CLOTH,14);
            ellipsoid(p(side*.56,2.3,.14),p(.34,.34,.33),Material.GOLD,14,8);
            tube(p(side*.56,2.25,.06),p(side*.66,.53,.10),.29,.20,Material.ARMOR,14);
            ellipsoid(p(side*.67,.28,.35),p(.37,.25,.64),Material.IVORY,16,8);
            ring(p(side*.65,.65,.1),.24,.24,.045,Material.GOLD,0);
            ellipsoid(p(side*.64,1.5,.30),p(.23,.65,.10),Material.GOLD,14,8);
        }
        // Layered open ceremonial skirt: gaps show thighs, knees, and greaves.
        for(int panel=0;panel<7;panel++) {
            double a=panel*Math.PI*2/7;
            for(int row=0;row<9;row++) {
                double t=row/9.0,u=(row+1)/9.0;
                double y=4.45-2.6*t, yy=4.45-2.6*u;
                double r=.8+.55*t, rr=.8+.55*u;
                for(int col=0;col<4;col++) {
                    double b=a-.31+.62*col/4,c=a-.31+.62*(col+1)/4;
                    quad(p(Math.cos(b)*r,y,Math.sin(b)*r*.62),p(Math.cos(c)*r,y,Math.sin(c)*r*.62),
                            p(Math.cos(c)*rr,yy,Math.sin(c)*rr*.62),p(Math.cos(b)*rr,yy,Math.sin(b)*rr*.62),
                            panel%2==0?Material.IVORY:Material.CLOTH);
                }
            }
            curve(new P[]{p(Math.cos(a-.31)*.8,4.45,Math.sin(a-.31)*.50),
                    p(Math.cos(a-.31)*1.1,3.2,Math.sin(a-.31)*.68),
                    p(Math.cos(a-.31)*1.35,1.85,Math.sin(a-.31)*.84)},.025,Material.GOLD);
        }
        ring(p(0,4.5,0),.78,.46,.10,Material.GOLD,0);
        ellipsoid(p(0,4.5,.48),p(.22,.22,.11),Material.LIGHT,16,8);
        // Sculpted breastplate with raised sun, ribs, and overlapping scales.
        for(int side:new int[]{-1,1}) {
            ellipsoid(p(side*.50,6.47,.52),p(.55,.35,.13),Material.IVORY,20,10);
            for(int i=0;i<4;i++) {
                curve(new P[]{p(side*.12,6.05-i*.31,.57),p(side*.52,5.94-i*.28,.60),
                        p(side*(.88-i*.045),5.92-i*.28,.35)},.035,Material.GOLD);
            }
            for(int layer=0;layer<3;layer++) {
                ellipsoid(p(side*(1.06+layer*.15),7.04-layer*.20,-.02),
                        p(.58,.25,.59-layer*.06),layer%2==0?Material.GOLD:Material.ARMOR,18,8);
            }
        }
        ring(p(0,6.48,.69),.27,.27,.04,Material.GOLD,1);
        ellipsoid(p(0,6.48,.72),p(.13,.13,.08),Material.LIGHT,16,8);
        for(int i=0;i<12;i++) {
            double a=i*Math.PI/6;
            tube(p(Math.cos(a)*.30,6.48+Math.sin(a)*.30,.70),
                    p(Math.cos(a)*.40,6.48+Math.sin(a)*.40,.70),.025,.006,Material.GOLD,6);
        }
        P leftShoulder=p(-1.17,6.96,0),leftElbow=p(-2.40,6.86,.28),leftWrist=p(-3.58,6.99,.83);
        limb(leftShoulder,leftElbow,leftWrist);
        P rightShoulder=p(1.17,6.96,0),rightElbow=p(2.25,6.68,.35),rightWrist=p(.43,7.05,1.0);
        limb(rightShoulder,rightElbow,rightWrist);
        hand(p(-3.75,7.00,.87),-1);
        hand(p(.25,7.07,1.00),1);
        // A shaped jaw, ears, nose bridge, cheekbones, luminous eyes and flowing dark hair.
        ellipsoid(p(0,8.38,-.08),p(.60,.83,.51),Material.HAIR,24,14);
        loft(0,.10,new double[][]{{7.63,.24,.23},{7.82,.36,.34},{8.13,.49,.43},
                {8.50,.52,.46},{8.83,.45,.38},{9.02,.25,.22}},Material.SKIN,24);
        for(int side:new int[]{-1,1}) {
            ellipsoid(p(side*.52,8.27,.08),p(.12,.24,.14),Material.SKIN,14,10);
            ellipsoid(p(side*.215,8.46,.546),p(.153,.044,.026),Material.LIGHT,16,8);
            curve(new P[]{p(side*.075,8.58,.56),p(side*.23,8.63,.55),p(side*.41,8.61,.49)},.032,Material.HAIR);
            curve(new P[]{p(side*.50,8.92,-.08),p(side*.66,8.34,-.16),
                    p(side*.57,7.77,-.18),p(side*.71,7.33,-.36)},.07,Material.HAIR);
        }
        tube(p(0,8.52,.53),p(0,8.22,.63),.035,.065,Material.SKIN,10);
        ellipsoid(p(0,8.19,.60),p(.065,.035,.045),Material.SKIN,14,8);
        curve(new P[]{p(-.16,8.00,.48),p(0,7.985,.52),p(.16,8.00,.48)},.017,Material.GOLD);
        ellipsoid(p(0,9.27,-.12),p(.26,.39,.25),Material.HAIR,18,10);
        // Solar coronet: a curved band, tapered rays, and a floating central jewel.
        ring(p(0,8.91,.02),.53,.45,.055,Material.GOLD,0);
        for(int i=-3;i<=3;i++) {
            double x=i*.16;
            double peak=9.82-Math.abs(i)*.15;
            curve(new P[]{p(x,8.93,.35),p(x*1.16,9.28,.23),p(x*1.28,peak,.08)},.048,Material.GOLD);
        }
        ellipsoid(p(0,9.53,.25),p(.10,.17,.07),Material.LIGHT,14,8);
        // Hair and silk ribbons are curved surfaces, not rectangular cape slabs.
        for(int i=-3;i<=3;i++) {
            double x=i*.12;
            ribbon(new P[]{p(x,8.65,-.45),p(x*1.6,7.1,-.77),p(x*2.2+.25,5.6,-1.06),
                    p(x*1.8+.38,4.6,-.65)},.16,Material.HAIR);
        }
        for(int side:new int[]{-1,1}) {
            ribbon(new P[]{p(side*.9,7.20,-.37),p(side*2.1,6.6,-1.15),
                    p(side*2.65,4.65,-1.7),p(side*1.85,2.75,-1.15)},.36,Material.IVORY);
            ribbon(new P[]{p(side*.8,4.55,-.25),p(side*1.85,4.2,-.95),
                    p(side*2.4,3.0,-1.3),p(side*2.15,2.2,-.65)},.18,Material.CLOTH);
        }
        // Smooth recurved bow, tapered string and arrowhead.
        List<P> bow=new ArrayList<>();
        for(int i=0;i<=32;i++) {
            double t=i/32.0;
            bow.add(p(-3.0-.84*Math.sin(Math.PI*t),4.65+4.7*t,.88));
        }
        curve(bow.toArray(P[]::new),.075,Material.GOLD);
        curve(new P[]{p(-3.0,4.65,.88),p(.32,7.05,1.0),p(-3.0,9.35,.88)},.018,Material.LIGHT);
        tube(p(-4.52,7.05,.98),p(.36,7.05,.98),.028,.028,Material.GOLD,8);
        tube(p(-4.85,7.05,.98),p(-4.45,7.05,.98),.001,.13,Material.LIGHT,8);
        // Thin celestial nimbus behind the crown, separate from the rotating head sigil.
        ring(p(0,8.45,-.76),1.14,1.14,.018,Material.GOLD,1);
        ring(p(0,8.45,-.78),1.24,1.24,.013,Material.LIGHT,1);
        List<Face> result=List.copyOf(BUILD);
        BUILD.clear();
        return result;
    }

    private static P p(double x,double y,double z) {return new P(x,y,z);}
    private static void quad(P a,P b,P c,P d,Material material) {
        P normal=d.sub(a).cross(b.sub(a)).unit();
        BUILD.add(new Face(a,b,c,d,material,normal,a.add(b).add(c).add(d).scale(.25)));
    }
    private static void ellipsoid(P center,P r,Material m,int sides,int rows) {
        VOLUMES.add(new Volume(center,r));
        for(int j=0;j<rows;j++) for(int i=0;i<sides;i++) {
            double a=-Math.PI/2+Math.PI*j/rows,b=-Math.PI/2+Math.PI*(j+1)/rows;
            double c=Math.PI*2*i/sides,d=Math.PI*2*(i+1)/sides;
            quad(sphere(center,r,a,c),sphere(center,r,a,d),sphere(center,r,b,d),sphere(center,r,b,c),m);
        }
    }
    private static P sphere(P c,P r,double lat,double angle) {
        return c.add(p(r.x*Math.cos(lat)*Math.cos(angle),r.y*Math.sin(lat),r.z*Math.cos(lat)*Math.sin(angle)));
    }
    private static void loft(double x,double z,double[][] rings,Material material,int sides) {
        for(int row=0;row<rings.length-1;row++) {
            double[] a=rings[row],b=rings[row+1];
            VOLUMES.add(new Volume(p(x,(a[0]+b[0])/2,z),p(Math.max(a[1],b[1]),(b[0]-a[0])/2,Math.max(a[2],b[2]))));
            for(int i=0;i<sides;i++) {
                double c=Math.PI*2*i/sides,d=Math.PI*2*(i+1)/sides;
                quad(p(x+a[1]*Math.cos(c),a[0],z+a[2]*Math.sin(c)),p(x+a[1]*Math.cos(d),a[0],z+a[2]*Math.sin(d)),
                        p(x+b[1]*Math.cos(d),b[0],z+b[2]*Math.sin(d)),p(x+b[1]*Math.cos(c),b[0],z+b[2]*Math.sin(c)),material);
            }
        }
    }
    private static void tube(P from,P to,double r0,double r1,Material material,int sides) {
        P axis=to.sub(from).unit(),u=axis.cross(p(0,1,0));
        if(u.dot(u)<.001)u=p(1,0,0);
        u=u.unit(); P v=u.cross(axis).unit();
        P center=from.add(to).scale(.5),delta=to.sub(from);
        VOLUMES.add(new Volume(center,p(Math.abs(delta.x)/2+Math.max(r0,r1),
                Math.abs(delta.y)/2+Math.max(r0,r1),Math.abs(delta.z)/2+Math.max(r0,r1))));
        for(int i=0;i<sides;i++) {
            double a=Math.PI*2*i/sides,b=Math.PI*2*(i+1)/sides;
            P da=u.scale(Math.cos(a)).add(v.scale(Math.sin(a)));
            P db=u.scale(Math.cos(b)).add(v.scale(Math.sin(b)));
            quad(from.add(da.scale(r0)),from.add(db.scale(r0)),to.add(db.scale(r1)),to.add(da.scale(r1)),material);
        }
    }
    private static void curve(P[] points,double radius,Material material) {
        for(int i=0;i<points.length-1;i++)tube(points[i],points[i+1],radius,radius,material,8);
    }
    private static void ring(P center,double rx,double ry,double width,Material material,int plane) {
        P[] points=new P[65];
        for(int i=0;i<=64;i++) {
            double a=Math.PI*2*i/64;
            points[i]=center.add(plane==0?p(rx*Math.cos(a),0,ry*Math.sin(a)):p(rx*Math.cos(a),ry*Math.sin(a),0));
        }
        curve(points,width,material);
    }
    private static void limb(P shoulder,P elbow,P wrist) {
        tube(shoulder,elbow,.36,.27,Material.ARMOR,18);
        ellipsoid(elbow,p(.29,.29,.29),Material.IVORY,16,10);
        tube(elbow,wrist,.29,.17,Material.IVORY,18);
        P mid=elbow.scale(.55).add(wrist.scale(.45));
        tube(mid,wrist,.31,.22,Material.GOLD,18);
    }
    private static void hand(P center,int sign) {
        ellipsoid(center,p(.23,.29,.17),Material.SKIN,16,10);
        for(int i=0;i<4;i++) {
            double y=center.y+.20-i*.12;
            curve(new P[]{p(center.x-.10*sign,y,center.z+.1),p(center.x-.30*sign,y-.02,center.z+.15),
                    p(center.x-.34*sign,y-.10,center.z+.02)},.045,Material.SKIN);
        }
        curve(new P[]{p(center.x+.12*sign,center.y-.20,center.z),
                p(center.x-.10*sign,center.y-.32,center.z+.16),p(center.x-.25*sign,center.y-.20,center.z+.20)},.06,Material.SKIN);
    }
    private static void ribbon(P[] control,double width,Material material) {
        P previous=null,left=null,right=null;
        for(int i=0;i<=24;i++) {
            double t=i/24.0,u=1-t;
            P center=control[0].scale(u*u*u).add(control[1].scale(3*u*u*t))
                    .add(control[2].scale(3*u*t*t)).add(control[3].scale(t*t*t));
            P half=p(width*(1-t*.55),.04*Math.sin(t*Math.PI*3),0);
            P l=center.sub(half),r=center.add(half);
            if(previous!=null) {
                quad(left,right,r,l,material);
                tube(left,l,.012,.012,material==Material.HAIR?Material.HAIR:Material.GOLD,6);
                tube(right,r,.012,.012,material==Material.HAIR?Material.HAIR:Material.GOLD,6);
            }
            previous=center;left=l;right=r;
        }
    }

    public static Vec3 forward(float yaw) {
        double angle=Math.toRadians(yaw);
        return new Vec3(-Math.sin(angle),0,Math.cos(angle));
    }
    public static Vec3 origin(Vec3 player,float yaw) {return player.subtract(forward(yaw).scale(4));}
    public static boolean contains(double x,double y,double z,double formedHeight) {
        if(y>formedHeight)return false;
        P p=p(x,y,z);
        for(Volume volume:VOLUMES)if(volume.contains(p))return true;
        return false;
    }
    private HouyiAvatarShape() {}
}
