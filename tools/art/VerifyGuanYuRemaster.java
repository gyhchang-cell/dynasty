package com.dynasty;

import com.dynasty.HouyiAvatarShape.Face;
import com.dynasty.HouyiAvatarShape.Material;
import com.dynasty.HouyiAvatarShape.P;
import com.dynasty.client.ImperialMeshNormals;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.EnumMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.HashSet;

/** Reproducible geometric checks; does not launch Minecraft or touch a saved world. */
public final class VerifyGuanYuRemaster {
    private static final List<String> failures=new ArrayList<>();
    private static final double SHAFT_RADIUS=.059;
    private static final double CLEARANCE_MARGIN=.02;
    private static final Material[] HAND={Material.GUAN_SKIN,Material.GUAN_HIGHLIGHT,Material.GUAN_SHADOW};
    private record Triangle(P a,P b,P c,Material material) {}
    private record Near(double squared,P onShaft) {}

    public static void main(String[] args)throws Exception {
        long start=System.nanoTime();
        List<Face> mesh=GuanYuAvatarShape.MESH;
        System.out.printf("Mesh initialization: %,d quads, %.1f ms%n",mesh.size(),(System.nanoTime()-start)/1e6);
        Map<String,List<Face>> parts=new LinkedHashMap<>();
        for(String part:List.of("legs","body","cape","armor","arms","head","weapon")) {
            GuanYuSculptor builder=new GuanYuSculptor();
            Method method=GuanYuAvatarShape.class.getDeclaredMethod(part,GuanYuSculptor.class);
            method.setAccessible(true);method.invoke(null,builder);parts.put(part,List.copyOf(builder.faces));
        }
        checkBounds(mesh,"whole body",-4.1,2.7,-.02,GuanYuAvatarShape.HEIGHT+.015,-1.65,1.5);
        checkBounds(parts.get("head"),"head/beard/crown",-.85,.85,5.5,9.015,-.70,1.15);
        verifyCaps();
        double gripDistance=distanceToSegment(GuanYuAvatarShape.GRIP,GuanYuAvatarShape.SHAFT_BOTTOM,GuanYuAvatarShape.SHAFT_TOP);
        check(gripDistance<.008,"Grip axis misses shaft: "+gripDistance);
        System.out.printf("Grip-axis offset: %.6f blocks%n",gripDistance);
        shaftClearance(parts);
        wholeWeaponClearance(parts);
        verifyWeaponIdentity(parts.get("weapon"));
        verifyPhoenixEyes();
        long normalsStart=System.nanoTime();
        var quads=mesh.stream().map(f->new ImperialMeshNormals.Quad(point(f.a()),point(f.b()),point(f.c()),point(f.d()),f.material().ordinal())).toList();
        var normals=ImperialMeshNormals.build(quads);
        int invalid=0;
        for(var n:normals)for(var p:List.of(n.a(),n.b(),n.c(),n.d())) {
            double length=p.dot(p);
            if(!Double.isFinite(length)||length<.98||length>1.02)invalid++;
        }
        check(invalid==0,"Invalid/zero smoothed normals: "+invalid);
        System.out.printf("Normal cache: %,d corners, %.1f ms; invalid=%d%n",normals.size()*4,(System.nanoTime()-normalsStart)/1e6,invalid);
        check(mesh.size()<=100000,"Guardian exceeds this refinement's 100,000-face per-instance review limit");
        if(!failures.isEmpty())throw new AssertionError(String.join("\n",failures));
        System.out.println("PASS: finite geometry, bounds, outward caps, grip axis, shaft clearance, whole-weapon surface intersections and normal cache");
    }
    private static ImperialMeshNormals.Point point(P p){return new ImperialMeshNormals.Point(p.x(),p.y(),p.z());}
    private static void verifyWeaponIdentity(List<Face> faces) {
        var counts=new EnumMap<Material,Integer>(Material.class);
        for(Face f:faces)counts.merge(f.material(),1,Integer::sum);
        check(counts.getOrDefault(Material.JADE_METAL,0)>500,"Guandao must retain a dedicated green metal body/socket/shaft without cloth-shader selection");
        check(counts.getOrDefault(Material.STEEL,0)>=400&&counts.getOrDefault(Material.IVORY,0)>=200,"Guandao wide silver bevel is missing");
        check(counts.getOrDefault(Material.GOLD_PALE,0)>1000,"Guandao gold relief/guard geometry is missing");
        check(counts.getOrDefault(Material.SILK_RED,0)+counts.getOrDefault(Material.CRIMSON,0)>1800,"Guandao red silk tassel geometry is missing");
        System.out.println("Guandao material/geometry identity: "+counts);
    }
    private static void verifyPhoenixEyes()throws Exception {
        Method eye=GuanYuAvatarShape.class.getDeclaredMethod("eye",GuanYuSculptor.class,int.class);eye.setAccessible(true);
        for(int side:new int[]{-1,1}) {
            GuanYuSculptor builder=new GuanYuSculptor();eye.invoke(null,builder,side);
            double inner=Double.POSITIVE_INFINITY,outer=Double.NEGATIVE_INFINITY;
            for(Face f:builder.faces)if(f.material()==Material.EYE_DARK)for(P p:List.of(f.a(),f.b(),f.c(),f.d())) {
                if(Math.abs(p.x())<.11)inner=Math.min(inner,p.y());
                if(Math.abs(p.x())>.385)outer=Math.max(outer,p.y());
            }
            check(Double.isFinite(inner+outer)&&outer-inner>.09&&outer-inner<.18,"Phoenix-eye outer corner must rise visibly without exaggerated distortion");
            System.out.printf("Phoenix-eye side %d: outer-corner rise %.5f blocks%n",side,outer-inner);
        }
    }
    private static void check(boolean condition,String failure){if(!condition){failures.add(failure);System.out.println("FAIL: "+failure);}}
    private static void checkBounds(List<Face> faces,String label,double x0,double x1,double y0,double y1,double z0,double z1) {
        double minX=Double.POSITIVE_INFINITY,minY=minX,minZ=minX,maxX=-minX,maxY=-minX,maxZ=-minX;
        int bad=0;
        for(Face f:faces) {
            if(!Double.isFinite(f.normal().dot(f.normal())))bad++;
            for(P p:List.of(f.a(),f.b(),f.c(),f.d())) {
                if(!Double.isFinite(p.x()+p.y()+p.z()))bad++;
                minX=Math.min(minX,p.x());maxX=Math.max(maxX,p.x());minY=Math.min(minY,p.y());maxY=Math.max(maxY,p.y());minZ=Math.min(minZ,p.z());maxZ=Math.max(maxZ,p.z());
            }
        }
        System.out.printf("%s bounds: x[%.4f,%.4f] y[%.4f,%.4f] z[%.4f,%.4f], invalid=%d%n",label,minX,maxX,minY,maxY,minZ,maxZ,bad);
        check(bad==0,label+" contains non-finite geometry");
        check(minX>=x0&&maxX<=x1&&minY>=y0&&maxY<=y1&&minZ>=z0&&maxZ<=z1,label+" exceeds declared safety bounds");
    }
    private static void verifyCaps() {
        GuanYuSculptor builder=new GuanYuSculptor();
        P start=new P(0,0,0),end=new P(.5,3,.2),axis=end.sub(start).unit();
        builder.sweep(new P[]{start,end},new double[]{.2,.2},new double[]{.2,.2},8,16,Material.GOLD);
        int bad=0;
        for(int i=8*16;i<builder.faces.size();i++) {
            Face f=builder.faces.get(i);
            double outward=f.normal().dot(axis)*(i%2==0?-1:1);
            if(outward<.999)bad++;
        }
        check(bad==0,"Sweep end-cap winding wrong on "+bad+" triangles");
        System.out.println("Sweep caps: "+(bad==0?"outward":"FAILED"));
    }
    private static boolean handContact(P p,Material material) {
        boolean skin=false;for(Material m:HAND)if(material==m)skin=true;
        return skin&&p.x()>-2.48&&p.x()<-1.72&&p.y()>5.14&&p.y()<5.73&&p.z()>.55&&p.z()<1.12;
    }
    private record Cell(int x,int y,int z) {}
    private record LabeledTriangle(Triangle triangle,String part) {}
    private static void wholeWeaponClearance(Map<String,List<Face>> parts) {
        // A uniform spatial index keeps this an exhaustive test rather than a sparse vertex probe.
        // Only actual skin contact within the declared gripping hand may touch the shaft.
        Map<Cell,List<LabeledTriangle>> cells=new HashMap<>();
        for(var part:parts.entrySet()) {
            if(part.getKey().equals("weapon"))continue;
            for(Face face:part.getValue())for(Triangle tri:triangles(face)) {
                if(degenerate(tri))continue;
                LabeledTriangle item=new LabeledTriangle(tri,part.getKey());
                for(Cell cell:cells(tri))cells.computeIfAbsent(cell,key->new ArrayList<>()).add(item);
            }
        }
        int pairChecks=0,contacts=0;Map<String,Integer> byPart=new LinkedHashMap<>();
        for(Face face:parts.get("weapon"))for(Triangle weapon:triangles(face)) {
            if(degenerate(weapon))continue;
            var candidates=new HashSet<LabeledTriangle>();
            for(Cell cell:cells(weapon))candidates.addAll(cells.getOrDefault(cell,List.of()));
            for(LabeledTriangle item:candidates) {
                pairChecks++;
                P hit=surfaceCrossing(weapon,item.triangle);
                if(hit==null||handContact(hit,item.triangle.material))continue;
                contacts++;byPart.merge(item.part,1,Integer::sum);
                if(contacts<=3)System.out.printf("Unexpected weapon contact / %s at (%.6f,%.6f,%.6f), material=%s%n",item.part,hit.x(),hit.y(),hit.z(),item.triangle.material);
            }
        }
        System.out.printf("Whole weapon / body: %,d candidate triangle pairs, non-grip surface crossings=%d %s%n",pairChecks,contacts,byPart);
        check(contacts==0,"Blade/shaft/tassel cuts through non-grip body surfaces: "+byPart);
    }
    private static List<Triangle> triangles(Face face) {
        return List.of(new Triangle(face.a(),face.b(),face.c(),face.material()),new Triangle(face.a(),face.c(),face.d(),face.material()));
    }
    private static boolean degenerate(Triangle t) {
        P normal=t.b.sub(t.a).cross(t.c.sub(t.a));return normal.dot(normal)<1e-22;
    }
    private static List<Cell> cells(Triangle t) {
        double size=.30,epsilon=1e-7;
        int x0=(int)Math.floor((Math.min(t.a.x(),Math.min(t.b.x(),t.c.x()))-epsilon)/size);
        int x1=(int)Math.floor((Math.max(t.a.x(),Math.max(t.b.x(),t.c.x()))+epsilon)/size);
        int y0=(int)Math.floor((Math.min(t.a.y(),Math.min(t.b.y(),t.c.y()))-epsilon)/size);
        int y1=(int)Math.floor((Math.max(t.a.y(),Math.max(t.b.y(),t.c.y()))+epsilon)/size);
        int z0=(int)Math.floor((Math.min(t.a.z(),Math.min(t.b.z(),t.c.z()))-epsilon)/size);
        int z1=(int)Math.floor((Math.max(t.a.z(),Math.max(t.b.z(),t.c.z()))+epsilon)/size);
        var result=new ArrayList<Cell>();
        for(int x=x0;x<=x1;x++)for(int y=y0;y<=y1;y++)for(int z=z0;z<=z1;z++)result.add(new Cell(x,y,z));
        return result;
    }
    private static P surfaceCrossing(Triangle a,Triangle b) {
        P[] aa={a.a,a.b,a.c},bb={b.a,b.b,b.c};
        for(int edge=0;edge<3;edge++) {
            double u=intersection(aa[edge],aa[(edge+1)%3],b);
            if(u>=0)return aa[edge].add(aa[(edge+1)%3].sub(aa[edge]).scale(u));
            u=intersection(bb[edge],bb[(edge+1)%3],a);
            if(u>=0)return bb[edge].add(bb[(edge+1)%3].sub(bb[edge]).scale(u));
        }
        return null;
    }
    private static void shaftClearance(Map<String,List<Face>> parts) {
        P bottom=GuanYuAvatarShape.SHAFT_BOTTOM,top=GuanYuAvatarShape.SHAFT_TOP;
        for(var part:parts.entrySet()) {
            if(part.getKey().equals("weapon"))continue;
            List<Triangle> candidates=new ArrayList<>();
            for(Face f:part.getValue()) {
                double minX=Math.min(Math.min(f.a().x(),f.b().x()),Math.min(f.c().x(),f.d().x()));
                double maxX=Math.max(Math.max(f.a().x(),f.b().x()),Math.max(f.c().x(),f.d().x()));
                double minZ=Math.min(Math.min(f.a().z(),f.b().z()),Math.min(f.c().z(),f.d().z()));
                double maxZ=Math.max(Math.max(f.a().z(),f.b().z()),Math.max(f.c().z(),f.d().z()));
                if(minX>Math.max(bottom.x(),top.x())+.12||maxX<Math.min(bottom.x(),top.x())-.12||minZ>bottom.z()+.12||maxZ<bottom.z()-.12)continue;
                candidates.add(new Triangle(f.a(),f.b(),f.c(),f.material()));
                candidates.add(new Triangle(f.a(),f.c(),f.d(),f.material()));
            }
            double nearest=Double.POSITIVE_INFINITY;P location=bottom;Material nearMaterial=null;
            int intersections=0;
            Map<Material,Near> materialNearest=new EnumMap<>(Material.class);
            for(Triangle triangle:candidates) {
                double hit=intersection(bottom,top,triangle);
                if(hit>=0&&!handContact(bottom.add(top.sub(bottom).scale(hit)),triangle.material))intersections++;
                Near near=segmentTriangleDistance(bottom,top,triangle);
                if(handContact(near.onShaft,triangle.material))continue;
                Near old=materialNearest.get(triangle.material);
                if(old==null||old.squared>near.squared)materialNearest.put(triangle.material,near);
                double distance=Math.sqrt(near.squared);
                if(distance<nearest){nearest=distance;location=near.onShaft;nearMaterial=triangle.material;}
            }
            System.out.printf("Shaft / %s: candidateTriangles=%d surfaceClearance=%s at(%.3f,%.3f,%.3f) material=%s axisCrossings=%d%n",part.getKey(),candidates.size(),Double.isFinite(nearest)?String.format("%.5f",nearest-SHAFT_RADIUS):"outside swept bounds",location.x(),location.y(),location.z(),nearMaterial,intersections);
            check(intersections==0,"Weapon shaft axis crosses "+part.getKey()+" "+intersections+" times outside intended skin grip");
            check(nearest>=SHAFT_RADIUS+CLEARANCE_MARGIN,"Weapon shaft / "+part.getKey()+" misses required .02-block clearance (gap="+(nearest-SHAFT_RADIUS)+", material="+nearMaterial+")");
            for(var entry:materialNearest.entrySet())if(entry.getValue().squared<SHAFT_RADIUS*SHAFT_RADIUS) {
                P p=entry.getValue().onShaft;
                System.out.printf("  Penetrating material %s gap=%.6f at shaft(%.6f,%.6f,%.6f)%n",entry.getKey(),Math.sqrt(entry.getValue().squared)-SHAFT_RADIUS,p.x(),p.y(),p.z());
            }
        }
    }
    private static Near segmentTriangleDistance(P a,P b,Triangle triangle) {
        double hit=intersection(a,b,triangle);
        if(hit>=0)return new Near(0,a.add(b.sub(a).scale(hit)));
        Near result=new Near(pointTriangleDistanceSquared(a,triangle),a);
        Near[] candidates={new Near(pointTriangleDistanceSquared(b,triangle),b),segmentDistance(a,b,triangle.a,triangle.b),
                segmentDistance(a,b,triangle.b,triangle.c),segmentDistance(a,b,triangle.c,triangle.a)};
        for(Near near:candidates)if(near.squared<result.squared)result=near;
        return result;
    }
    private static double clamp(double x){return Math.max(0,Math.min(1,x));}
    private static Near segmentDistance(P p1,P q1,P p2,P q2) {
        P d1=q1.sub(p1),d2=q2.sub(p2),r=p1.sub(p2);
        double a=d1.dot(d1),e=d2.dot(d2),f=d2.dot(r),s,t;
        if(a<=1e-16&&e<=1e-16)return new Near(r.dot(r),p1);
        if(a<=1e-16){s=0;t=clamp(f/e);}
        else {
            double c=d1.dot(r);
            if(e<=1e-16){t=0;s=clamp(-c/a);}
            else {
                double b=d1.dot(d2),denom=a*e-b*b;
                s=Math.abs(denom)>1e-16?clamp((b*f-c*e)/denom):0;
                t=(b*s+f)/e;
                if(t<0){t=0;s=clamp(-c/a);}else if(t>1){t=1;s=clamp((b-c)/a);}
            }
        }
        P first=p1.add(d1.scale(s)),second=p2.add(d2.scale(t)),delta=first.sub(second);
        return new Near(delta.dot(delta),first);
    }
    private static double intersection(P from,P to,Triangle t) {
        P dir=to.sub(from),edge1=t.b.sub(t.a),edge2=t.c.sub(t.a),h=dir.cross(edge2);
        double det=edge1.dot(h);if(Math.abs(det)<1e-12)return -1;
        double inv=1/det;P s=from.sub(t.a);double u=inv*s.dot(h);if(u<0||u>1)return -1;
        P q=s.cross(edge1);double v=inv*dir.dot(q);if(v<0||u+v>1)return -1;
        double hit=inv*edge2.dot(q);return hit>=0&&hit<=1?hit:-1;
    }
    private static double distanceToSegment(P p,P a,P b) {
        P ab=b.sub(a);double t=Math.max(0,Math.min(1,p.sub(a).dot(ab)/Math.max(1e-16,ab.dot(ab))));
        P delta=p.sub(a.add(ab.scale(t)));return Math.sqrt(delta.dot(delta));
    }
    private static double pointTriangleDistanceSquared(P p,Triangle t) {
        P ab=t.b.sub(t.a),ac=t.c.sub(t.a),ap=p.sub(t.a);
        double d1=ab.dot(ap),d2=ac.dot(ap);if(d1<=0&&d2<=0)return ap.dot(ap);
        P bp=p.sub(t.b);double d3=ab.dot(bp),d4=ac.dot(bp);if(d3>=0&&d4<=d3)return bp.dot(bp);
        double vc=d1*d4-d3*d2;
        if(vc<=0&&d1>=0&&d3<=0){P d=ap.sub(ab.scale(d1/(d1-d3)));return d.dot(d);}
        P cp=p.sub(t.c);double d5=ab.dot(cp),d6=ac.dot(cp);if(d6>=0&&d5<=d6)return cp.dot(cp);
        double vb=d5*d2-d1*d6;
        if(vb<=0&&d2>=0&&d6<=0){P d=ap.sub(ac.scale(d2/(d2-d6)));return d.dot(d);}
        double va=d3*d6-d5*d4;
        if(va<=0&&(d4-d3)>=0&&(d5-d6)>=0){P d=bp.sub(t.c.sub(t.b).scale((d4-d3)/((d4-d3)+(d5-d6))));return d.dot(d);}
        double total=va+vb+vc;
        if(Math.abs(total)<1e-20){double d=Math.min(distanceToSegment(p,t.a,t.b),Math.min(distanceToSegment(p,t.b,t.c),distanceToSegment(p,t.c,t.a)));return d*d;}
        P delta=ap.sub(ab.scale(vb/total)).sub(ac.scale(vc/total));return Math.max(0,delta.dot(delta));
    }
}
