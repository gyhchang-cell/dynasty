package com.dynasty.client;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Pure, cached-at-load smoothing shared by the in-game renderer and model inspection tools. */
public final class ImperialMeshNormals {
    public record Point(double x,double y,double z) {
        public Point add(Point p){return new Point(x+p.x,y+p.y,z+p.z);}
        public Point sub(Point p){return new Point(x-p.x,y-p.y,z-p.z);}
        public Point scale(double s){return new Point(x*s,y*s,z*s);}
        public double dot(Point p){return x*p.x+y*p.y+z*p.z;}
        public Point cross(Point p){return new Point(y*p.z-z*p.y,z*p.x-x*p.z,x*p.y-y*p.x);}
        public Point unit(){double l=Math.sqrt(dot(this));return l<1e-12?new Point(0,0,0):scale(1/l);}
    }
    public record Quad(Point a,Point b,Point c,Point d,int material) {}
    public record Normals(Point a,Point b,Point c,Point d) {}
    private record Key(long x,long y,long z,int material) {}
    private static final double CREASE=.55;
    private static Key key(Point p,int material) {
        return new Key(Math.round(p.x*1e6),Math.round(p.y*1e6),Math.round(p.z*1e6),material);
    }

    public static List<Normals> build(List<Quad> quads) {
        Map<Key,List<Point>> adjacent=new HashMap<>();
        List<Point> weighted=new ArrayList<>(quads.size());
        for(Quad q:quads) {
            Point n=q.b.sub(q.a).cross(q.c.sub(q.a)).add(q.c.sub(q.a).cross(q.d.sub(q.a)));
            weighted.add(n);
            // A collapsed pole must not add the same face multiple times to its shared vertex.
            Key[] keys={key(q.a,q.material),key(q.b,q.material),key(q.c,q.material),key(q.d,q.material)};
            for(int i=0;i<4;i++) {
                boolean duplicate=false;
                for(int j=0;j<i;j++)if(keys[i].equals(keys[j])){duplicate=true;break;}
                if(!duplicate)adjacent.computeIfAbsent(keys[i],k->new ArrayList<>()).add(n);
            }
        }
        List<Normals> result=new ArrayList<>(quads.size());
        for(int i=0;i<quads.size();i++) {
            Quad q=quads.get(i);Point face=weighted.get(i).unit();
            result.add(new Normals(smooth(adjacent,key(q.a,q.material),face),smooth(adjacent,key(q.b,q.material),face),
                    smooth(adjacent,key(q.c,q.material),face),smooth(adjacent,key(q.d,q.material),face)));
        }
        return List.copyOf(result);
    }
    private static Point smooth(Map<Key,List<Point>> adjacent,Key key,Point face) {
        Point sum=new Point(0,0,0);
        for(Point n:adjacent.get(key))if(face.dot(n.unit())>=CREASE)sum=sum.add(n);
        Point result=sum.unit();
        return result.dot(result)<.5?face:result;
    }
    private ImperialMeshNormals() {}
}
