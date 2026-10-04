package com.dynasty;

import com.dynasty.HouyiAvatarShape.*;
import java.util.*;

/** Exact production-mesh checks; no display-only proxy and no gameplay changes. */
public final class VerifyHouyiRemaster {
    private static void require(boolean ok,String message){if(!ok)throw new AssertionError(message);}
    public static void main(String[] args)throws Exception {
        var mesh=HouyiAvatarShape.MESH;
        require(mesh.size()>8000&&mesh.size()<22000,"Face budget: "+mesh.size());
        double minY=100,maxY=-100;
        for(Face f:mesh) {
            double area=f.b().sub(f.a()).cross(f.c().sub(f.a())).dot(f.b().sub(f.a()).cross(f.c().sub(f.a())))
                    +f.c().sub(f.a()).cross(f.d().sub(f.a())).dot(f.c().sub(f.a()).cross(f.d().sub(f.a())));
            require(area>1e-16,"Degenerate face");
            require(Math.abs(f.normal().dot(f.normal())-1)<1e-8,"Normal length");
            for(P p:new P[]{f.a(),f.b(),f.c(),f.d()}){
                require(Double.isFinite(p.x()+p.y()+p.z()),"Non-finite geometry");
                require(Math.abs(p.x())<6&&Math.abs(p.z())<2,"Outlier vertex");minY=Math.min(minY,p.y());maxY=Math.max(maxY,p.y());
            }
        }
        require(minY>=0&&maxY>9.7&&maxY<10,"Original giant scale/reveal height: "+maxY);
        var torso=part("proportions");
        require(depth(torso,6.55)>.95,"Chest too thin");
        require(depth(torso,4.4)>.8,"Pelvis too thin");
        require(width(torso,6.7)>width(torso,5.2)*1.35,"Chest/waist taper");
        require(HouyiArcherSculpture.DRAW_ELBOW.x()>1.8,"Draw elbow silhouette");
        require(HouyiArcherSculpture.NOCK.sub(HouyiArcherSculpture.HEAD).dot(HouyiArcherSculpture.NOCK.sub(HouyiArcherSculpture.HEAD))<.75,"Nock too far from cheek");
        P aim=HouyiArcherSculpture.GRIP.sub(HouyiArcherSculpture.NOCK).unit();
        require(aim.dot(new P(-1,0,0))>.999,"Eye/arrow aim");
        require(Math.abs(HouyiArcherSculpture.BOW_TOP.y()+HouyiArcherSculpture.BOW_BOTTOM.y()-2*HouyiArcherSculpture.GRIP.y())<.01,"Unbalanced bow limbs");
        // Sample the anatomical hand at the bow's actual gripping axis.
        var hands=part("hands");double bore=100;
        for(double y=-.15;y<=.15;y+=.025){
            P at=HouyiArcherSculpture.GRIP.add(new P(0,y,0));
            for(Face f:hands) {
                bore=Math.min(bore,distance(at,f.a(),f.b(),f.c()));
                bore=Math.min(bore,distance(at,f.a(),f.c(),f.d()));
            }
        }
        require(bore>.088,"Palm/fingers intersect wrapped grip: "+bore);
        double hook=100;for(Face f:hands){hook=Math.min(hook,distance(HouyiArcherSculpture.NOCK,f.a(),f.b(),f.c()));hook=Math.min(hook,distance(HouyiArcherSculpture.NOCK,f.a(),f.c(),f.d()));}
        require(hook>.023&&hook<.18,"Nock hand clearance: "+hook);
        // Formation sampling remains server-safe and is gated by revealed height.
        require(HouyiAvatarShape.contains(0,6,0,10),"Missing torso formation volume");
        require(!HouyiAvatarShape.contains(0,8,0,5),"Formation height gate");
        require(!HouyiAvatarShape.contains(30,6,30,10),"Unbounded formation volume");
        System.out.printf(Locale.ROOT,"PASS: %,d faces, height %.3f, chest depth %.3f, pelvis depth %.3f, bow grip bore %.4f, nock clearance %.4f; geometry/aim/formation valid.%n",mesh.size(),maxY,depth(torso,6.55),depth(torso,4.4),bore,hook);
    }
    private static List<Face> part(String name)throws Exception{var m=new GuanYuSculptor();var method=HouyiArcherSculpture.class.getDeclaredMethod(name,GuanYuSculptor.class);method.setAccessible(true);method.invoke(null,m);return m.faces;}
    private static double depth(List<Face> fs,double y){return extent(fs,y,false);}
    private static double width(List<Face> fs,double y){return extent(fs,y,true);}
    private static double extent(List<Face> fs,double y,boolean x){double lo=100,hi=-100;for(Face f:fs)for(P p:new P[]{f.a(),f.b(),f.c(),f.d()})if(Math.abs(p.y()-y)<.15){lo=Math.min(lo,x?p.x():p.z());hi=Math.max(hi,x?p.x():p.z());}return hi-lo;}
    private static double distance(P p,P a,P b,P c) {
        // Closest point on a triangle, with degenerate cap edges handled explicitly.
        P ab=b.sub(a),ac=c.sub(a),ap=p.sub(a);double d1=ab.dot(ap),d2=ac.dot(ap);
        if(d1<=0&&d2<=0)return length(ap);
        P bp=p.sub(b);double d3=ab.dot(bp),d4=ac.dot(bp);if(d3>=0&&d4<=d3)return length(bp);
        double vc=d1*d4-d3*d2;if(vc<=0&&d1>=0&&d3<=0&&d1-d3>1e-15)return length(p.sub(a.add(ab.scale(d1/(d1-d3)))));
        P cp=p.sub(c);double d5=ab.dot(cp),d6=ac.dot(cp);if(d6>=0&&d5<=d6)return length(cp);
        double vb=d5*d2-d1*d6;if(vb<=0&&d2>=0&&d6<=0&&d2-d6>1e-15)return length(p.sub(a.add(ac.scale(d2/(d2-d6)))));
        double va=d3*d6-d5*d4;if(va<=0&&d4-d3>=0&&d5-d6>=0&&d4-d3+d5-d6>1e-15)return length(p.sub(b.add(c.sub(b).scale((d4-d3)/(d4-d3+d5-d6)))));
        double sum=va+vb+vc;if(Math.abs(sum)<1e-20)return Math.min(length(ap),Math.min(length(bp),length(cp)));
        return length(p.sub(a.add(ab.scale(vb/sum)).add(ac.scale(vc/sum))));
    }
    private static double length(P p){return Math.sqrt(p.dot(p));}
}
