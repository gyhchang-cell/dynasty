import com.dynasty.GuanYuAvatarShape;
import com.dynasty.HouyiAvatarShape;
import com.dynasty.client.ImperialDragonMesh;
import com.dynasty.client.ImperialMeshNormals;
import java.io.BufferedWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;

/** Exports the exact runtime quad meshes, never an AI image or a separately built display model. */
public final class ExportImperialMeshes {
    private record Point(double x, double y, double z) {
        Point sub(Point p) { return new Point(x-p.x,y-p.y,z-p.z); }
        Point add(Point p) { return new Point(x+p.x,y+p.y,z+p.z); }
        Point scale(double k) { return new Point(x*k,y*k,z*k); }
        double dot(Point p) { return x*p.x+y*p.y+z*p.z; }
        Point cross(Point p) { return new Point(y*p.z-z*p.y,z*p.x-x*p.z,x*p.y-y*p.x); }
        double length() { return Math.sqrt(dot(this)); }
        Point unit() { double n=length(); return n<1e-12?new Point(0,1,0):scale(1/n); }
    }
    private record Quad(Point[] vertices, int material, Point normal, double area) {}
    private record Paint(String name, float r, float g, float b, double metal, double rough, double emission) {}
    private record Model(String id, String name, List<Quad> faces, List<Paint> materials) {}
    private static final Locale L=Locale.ROOT;

    public static void main(String[] args) throws Exception {
        if(args.length!=1) throw new IllegalArgumentException("Usage: ExportImperialMeshes output.json");
        List<Model> models=new ArrayList<>();
        List<Paint> guanPaints=new ArrayList<>();
        for(var m:HouyiAvatarShape.Material.values()) {
            String name=m.name();
            boolean metal=name.equals("GOLD")||name.equals("BRONZE")||name.equals("IVORY")||name.equals("ARMOR");
            guanPaints.add(new Paint(name,m.r,m.g,m.b,metal?.70:.03,metal?.32:.72,name.equals("LIGHT")?.8:0));
        }
        List<Quad> guanFaces=new ArrayList<>();
        for(var f:GuanYuAvatarShape.MESH) {
            Point[] v={point(f.a()),point(f.b()),point(f.c()),point(f.d())};
            guanFaces.add(quad(v,f.material().ordinal()));
        }
        models.add(new Model("guanyu","关羽 · 实际游戏网格",guanFaces,guanPaints));
        List<Quad> dragonFaces=new ArrayList<>();
        for(var f:ImperialDragonMesh.FACES) {
            dragonFaces.add(quad(new Point[]{point(f.a()),point(f.b()),point(f.c()),point(f.d())},f.material()));
        }
        for(boolean jade:new boolean[]{true,false}) {
            List<Paint> paints=new ArrayList<>();
            int maxMaterial=dragonFaces.stream().mapToInt(Quad::material).max().orElseThrow();
            for(int i=0;i<=maxMaterial;i++) {
                int c=ImperialDragonMesh.color(i,jade);
                paints.add(new Paint("DRAGON_"+i,((c>>16)&255)/255f,((c>>8)&255)/255f,(c&255)/255f,
                        i==1||(!jade&&i==0)?.72:.10,i==1?.32:.58,i==4?.9:0));
            }
            models.add(new Model(jade?"jade_dragon":"gold_dragon",jade?"青龙 · 实际游戏网格":"金龙 · 实际游戏网格",dragonFaces,paints));
        }
        Path path=Path.of(args[0]);
        if(path.getParent()!=null) Files.createDirectories(path.getParent());
        try(BufferedWriter out=Files.newBufferedWriter(path)) {
            out.write("{\"schema\":1,\"disclaimer\":\"Actual runtime mesh; studio preview, not an in-game screenshot\",\"smoothingCreaseDot\":0.55,\"models\":[");
            for(int i=0;i<models.size();i++) { if(i!=0) out.write(','); writeModel(out,models.get(i)); }
            out.write("]}");
        }
        System.out.println("Exported exact mesh JSON: "+path.toAbsolutePath());
    }

    private static Quad quad(Point[] vertices,int material) {
        Point a=vertices[1].sub(vertices[0]).cross(vertices[2].sub(vertices[0]));
        Point b=vertices[2].sub(vertices[0]).cross(vertices[3].sub(vertices[0]));
        Point sum=a.add(b);
        return new Quad(vertices,material,sum.unit(),(a.length()+b.length())*.5);
    }
    private static Point point(HouyiAvatarShape.P p) { return new Point(p.x(),p.y(),p.z()); }
    private static Point point(com.dynasty.client.ImperialWeaponGeometry.P p) { return new Point(p.x(),p.y(),p.z()); }

    private static void writeModel(BufferedWriter out,Model m) throws Exception {
        // Match the dedicated geometry verifiers, rather than a permissive generic 200k export cap.
        int maximum=m.id.equals("guanyu")?119_999:45_000;
        if(m.faces.isEmpty()||m.faces.size()>maximum) throw new AssertionError("Invalid face budget for "+m.id+": "+m.faces.size()+" > "+maximum);
        double[] min={Double.POSITIVE_INFINITY,Double.POSITIVE_INFINITY,Double.POSITIVE_INFINITY};
        double[] max={Double.NEGATIVE_INFINITY,Double.NEGATIVE_INFINITY,Double.NEGATIVE_INFINITY};
        int[] counts=new int[m.materials.size()];
        int degenerate=0;
        for(Quad f:m.faces) {
            if(f.material<0||f.material>=m.materials.size())throw new AssertionError("Unknown material");
            counts[f.material]++;
            if(f.area<1e-12)degenerate++;
            for(Point p:f.vertices) {
                double[] xyz={p.x,p.y,p.z};
                for(int a=0;a<3;a++) {
                    if(!Double.isFinite(xyz[a]))throw new AssertionError("Non-finite vertex "+m.id);
                    if(Math.abs(xyz[a])>64)throw new AssertionError("Outlier vertex "+m.id+" "+p);
                    min[a]=Math.min(min[a],xyz[a]);max[a]=Math.max(max[a],xyz[a]);
                }
            }
        }
        if(degenerate>m.faces.size()/20)throw new AssertionError("More than 5% degenerate faces: "+m.id);
        out.write("{\"id\":\""+m.id+"\",\"name\":\""+m.name+"\",\"bounds\":{\"min\":");
        numbers(out,min);out.write(",\"max\":");numbers(out,max);
        out.write("},\"qa\":{\"quads\":"+m.faces.size()+",\"vertices\":"+m.faces.size()*4+",\"degenerateQuads\":"+degenerate+",\"finite\":true,\"materialCounts\":");
        out.write(Arrays.toString(counts));out.write("},\"materials\":[");
        for(int i=0;i<m.materials.size();i++) {
            if(i!=0)out.write(',');Paint p=m.materials.get(i);
            out.write(String.format(L,"{\"name\":\"%s\",\"rgb\":[%.5f,%.5f,%.5f],\"metalness\":%.3f,\"roughness\":%.3f,\"emission\":%.3f}",p.name,p.r,p.g,p.b,p.metal,p.rough,p.emission));
        }
        out.write("],\"positions\":[");
        boolean first=true;
        for(Quad f:m.faces)for(Point p:f.vertices) {
            if(!first)out.write(',');first=false;pointValues(out,p);
        }
        List<ImperialMeshNormals.Quad> runtimeQuads=new ArrayList<>();
        for(Quad f:m.faces)runtimeQuads.add(new ImperialMeshNormals.Quad(runtimePoint(f.vertices[0]),runtimePoint(f.vertices[1]),runtimePoint(f.vertices[2]),runtimePoint(f.vertices[3]),f.material));
        List<ImperialMeshNormals.Normals> sharedNormals=ImperialMeshNormals.build(runtimeQuads);
        out.write("],\"normals\":[");first=true;
        for(var n:sharedNormals)for(var p:new ImperialMeshNormals.Point[]{n.a(),n.b(),n.c(),n.d()}) {
            if(!Double.isFinite(p.x()+p.y()+p.z()))throw new AssertionError("Non-finite shared normal "+m.id);
            if(!first)out.write(',');first=false;pointValues(out,new Point(p.x(),p.y(),p.z()));
        }
        out.write("],\"faceNormals\":[");first=true;
        for(Quad f:m.faces) { if(!first)out.write(',');first=false;pointValues(out,f.normal); }
        out.write("],\"materialIndices\":[");
        for(int i=0;i<m.faces.size();i++){if(i!=0)out.write(',');out.write(Integer.toString(m.faces.get(i).material));}
        out.write("]}");
        System.out.printf(L,"%-12s %6d quads · bounds %s → %s · degenerate %d · finite PASS%n",m.id,m.faces.size(),Arrays.toString(min),Arrays.toString(max),degenerate);
    }
    private static void numbers(BufferedWriter out,double[] numbers)throws Exception {
        out.write('[');for(int i=0;i<numbers.length;i++){if(i!=0)out.write(',');out.write(String.format(L,"%.6f",numbers[i]));}out.write(']');
    }
    private static void pointValues(BufferedWriter out,Point p)throws Exception {out.write(String.format(L,"%.6f,%.6f,%.6f",p.x,p.y,p.z));}
    private static ImperialMeshNormals.Point runtimePoint(Point p){return new ImperialMeshNormals.Point(p.x,p.y,p.z);}
}
