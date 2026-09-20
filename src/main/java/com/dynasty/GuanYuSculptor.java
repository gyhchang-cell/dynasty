package com.dynasty;

import com.dynasty.HouyiAvatarShape.Face;
import com.dynasty.HouyiAvatarShape.Material;
import com.dynasty.HouyiAvatarShape.P;
import java.util.ArrayList;
import java.util.List;
import java.util.function.BiFunction;

/** Curved control surfaces for the guardian. All geometry is real, closed or double-sided mesh. */
final class GuanYuSculptor {
    final List<Face> faces = new ArrayList<>();
    static P p(double x,double y,double z) {return new P(x,y,z);}
    void quad(P a,P b,P c,P d,Material m) {
        P cross=b.sub(a).cross(c.sub(a));
        if(cross.dot(cross)<1e-16)cross=c.sub(a).cross(d.sub(a));
        if(cross.dot(cross)<1e-16)return;
        faces.add(new Face(a,b,c,d,m,cross.unit(),a.add(b).add(c).add(d).scale(.25)));
    }
    void surface(int us,int vs,BiFunction<Double,Double,P> sample,Material m) {
        for(int v=0;v<vs;v++)for(int u=0;u<us;u++)
            quad(sample.apply(u/(double)us,v/(double)vs),sample.apply((u+1.)/us,v/(double)vs),
                    sample.apply((u+1.)/us,(v+1.)/vs),sample.apply(u/(double)us,(v+1.)/vs),m);
    }
    /** A cross-section profile contains y, half-width, front depth, back depth, and center x/z. */
    void profile(double[][] rings,int sides,int rows,Material m) {
        surface(sides,rows,(u,v)->profilePoint(rings,u,v),m);
    }
    static P profilePoint(double[][] q,double u,double v) {
        double f=v*(q.length-1);int i=Math.min(q.length-2,(int)f);double t=f-i;
        double[] row=new double[6];
        for(int k=0;k<6;k++)row[k]=spline(q[Math.max(0,i-1)][k],q[i][k],q[i+1][k],q[Math.min(q.length-1,i+2)][k],t);
        double a=u*Math.PI*2,cos=Math.cos(a);
        return p(row[4]+Math.max(0,row[1])*Math.sin(a),row[0],row[5]+Math.max(0,cos>=0?row[2]:row[3])*cos);
    }
    void ellipsoid(P c,P r,Material m,int sides,int rows) {
        surface(sides,rows,(u,v)->{
            double a=u*Math.PI*2,b=(v-.5)*Math.PI;
            return c.add(p(r.x()*Math.sin(a)*Math.cos(b),r.y()*Math.sin(b),r.z()*Math.cos(a)*Math.cos(b)));
        },m);
    }
    /** Smooth tapered extrusion, oval cross-sections, capped ends. */
    void sweep(P[] points,double[] widths,double[] depths,int steps,int sides,Material m) {
        P[][] rings=new P[steps+1][sides];
        P previousU=null;
        for(int j=0;j<=steps;j++) {
            double t=j/(double)steps;P c=path(points,t);
            P tangent=path(points,Math.min(1,t+.002)).sub(path(points,Math.max(0,t-.002))).unit();
            P u=previousU==null?tangent.cross(p(0,0,1)):previousU.sub(tangent.scale(previousU.dot(tangent)));
            if(u.dot(u)<1e-8)u=tangent.cross(p(0,1,0));u=u.unit();previousU=u;
            P v=tangent.cross(u).unit();
            double w=Math.max(.001,scalar(widths,t)),d=Math.max(.001,scalar(depths,t));
            for(int k=0;k<sides;k++) {double a=k*Math.PI*2/sides;rings[j][k]=c.add(u.scale(Math.cos(a)*w)).add(v.scale(Math.sin(a)*d));}
        }
        for(int j=0;j<steps;j++)for(int k=0;k<sides;k++)quad(rings[j][k],rings[j][(k+1)%sides],rings[j+1][(k+1)%sides],rings[j+1][k],m);
        for(int k=0;k<sides;k++) {
            quad(points[0],rings[0][(k+1)%sides],rings[0][k],points[0],m);
            quad(points[points.length-1],rings[steps][k],rings[steps][(k+1)%sides],points[points.length-1],m);
        }
    }
    void strand(P[] points,double width,Material m,int steps) {
        sweep(points,new double[]{width,width*.92,width*.65,.0015},new double[]{width,width*.92,width*.65,.0015},steps,6,m);
    }
    void wire(P[] points,double width,Material m,int steps) {
        sweep(points,new double[]{width,width},new double[]{width,width},steps,6,m);
    }
    void band(P center,double rx,double ry,double thickness,Material m) {
        P[] path=new P[33];for(int k=0;k<=32;k++){double a=k*Math.PI/16;path[k]=center.add(p(rx*Math.cos(a),ry*Math.sin(a),0));}
        wire(path,thickness,m,48);
    }
    /** Domed embossed petal/plate, a smooth pointed shield, never a sphere glued to armor. */
    void plate(P center,P across,P down,double width,double height,double lift,Material m) {
        P normal=across.cross(down).unit();
        if(normal.z()<0)normal=normal.scale(-1);
        final P n=normal;
        surface(4,4,(u,v)->{
            double w=width*(.86+.14*Math.sin(v*Math.PI))*(v>.72?1-.74*(v-.72)/.28:1);
            return center.add(across.scale((u-.5)*w)).add(down.scale(v*height))
                    .add(n.scale(lift*Math.sin(u*Math.PI)*Math.sin(v*Math.PI)));
        },m);
    }
    static double spline(double a,double b,double c,double d,double t) {
        return .5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t);
    }
    static P path(P[] q,double t) {
        double f=Math.max(0,Math.min(1,t))*(q.length-1);int i=Math.min(q.length-2,(int)f);double a=f-i;
        P p=q[Math.max(0,i-1)],b=q[i],c=q[i+1],d=q[Math.min(q.length-1,i+2)];
        return p(spline(p.x(),b.x(),c.x(),d.x(),a),spline(p.y(),b.y(),c.y(),d.y(),a),spline(p.z(),b.z(),c.z(),d.z(),a));
    }
    static double scalar(double[] q,double t) {
        double f=Math.max(0,Math.min(1,t))*(q.length-1);int i=Math.min(q.length-2,(int)f);return q[i]+(q[i+1]-q[i])*(f-i);
    }
}
