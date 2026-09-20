import com.dynasty.client.ImperialDragonMesh;
import com.dynasty.client.ImperialWeaponGeometry.P;
import java.util.List;

/** Diagnostic for the underlying body sweep, using the actual runtime triangles. */
public final class VerifyDragonSurfaceClearance {
    private static final int ROWS=ImperialDragonMesh.BODY_ROWS,SIDES=ImperialDragonMesh.BODY_SIDES,SKIN_FACES=ROWS*SIDES;
    private static final List<ImperialDragonMesh.Face> FACES=ImperialDragonMesh.FACES;
    private static final P[] CENTERS=new P[ROWS+1];
    private record Triangle(P a,P b,P c){}
    private record Tile(java.util.List<Triangle> triangles,double[] min,double[] max){}
    private static P add(P a,P b){return new P(a.x()+b.x(),a.y()+b.y(),a.z()+b.z());}
    private static P sub(P a,P b){return new P(a.x()-b.x(),a.y()-b.y(),a.z()-b.z());}
    private static P scale(P a,double k){return new P(a.x()*k,a.y()*k,a.z()*k);}
    private static double dot(P a,P b){return a.x()*b.x()+a.y()*b.y()+a.z()*b.z();}
    private static P cross(P a,P b){return new P(a.y()*b.z()-a.z()*b.y(),a.z()*b.x()-a.x()*b.z(),a.x()*b.y()-a.y()*b.x());}
    private static double length(P a){return Math.sqrt(dot(a,a));}
    private static double ray(P origin,P direction,P a,P b,P c){
        P e1=sub(b,a),e2=sub(c,a),h=cross(direction,e2);double det=dot(e1,h);
        if(Math.abs(det)<1e-12)return Double.POSITIVE_INFINITY;
        double inverse=1/det;P s=sub(origin,a);double u=inverse*dot(s,h);
        if(u<-.000001||u>1.000001)return Double.POSITIVE_INFINITY;
        P q=cross(s,e1);double v=inverse*dot(direction,q);
        if(v<-.000001||u+v>1.000001)return Double.POSITIVE_INFINITY;
        double t=inverse*dot(e2,q);return t>1e-8?t:Double.POSITIVE_INFINITY;
    }
    private static void centers(){
        for(int row=0;row<=ROWS;row++){
            P sum=new P(0,0,0);for(int j=0;j<SIDES;j++){
                var f=FACES.get(Math.min(row,ROWS-1)*SIDES+j);sum=add(sum,row==ROWS?f.d():f.a());
            }
            CENTERS[row]=scale(sum,1.0/SIDES);
        }
    }
    private static double clearance(P sample){
        double min=Double.POSITIVE_INFINITY;P center=null;int nearest=0;
        for(int i=0;i<ROWS;i++){
            P edge=sub(CENTERS[i+1],CENTERS[i]);double u=Math.max(0,Math.min(1,dot(sub(sample,CENTERS[i]),edge)/dot(edge,edge)));
            P projection=add(CENTERS[i],scale(edge,u));double d=dot(sub(sample,projection),sub(sample,projection));
            if(d<min){min=d;center=projection;nearest=i;}
        }
        P radial=sub(sample,center);double distance=length(radial);P direction=scale(radial,1/distance);
        double skin=Double.POSITIVE_INFINITY;
        for(int row=Math.max(0,nearest-4);row<=Math.min(ROWS-1,nearest+4);row++)for(int j=0;j<SIDES;j++){
            var f=FACES.get(row*SIDES+j);skin=Math.min(skin,ray(center,direction,f.a(),f.b(),f.c()));
            skin=Math.min(skin,ray(center,direction,f.a(),f.c(),f.d()));
        }
        if(!Double.isFinite(skin))throw new AssertionError("No body shell intersection");
        return distance-skin;
    }
    private static boolean cuts(P a,P b,Triangle t){
        P n=cross(sub(t.b,t.a),sub(t.c,t.a));double ln=length(n);if(ln<1e-12)return false;
        double da=dot(sub(a,t.a),n)/ln,db=dot(sub(b,t.a),n)/ln;
        if(da*db>=0||Math.abs(da)<1e-7||Math.abs(db)<1e-7)return false;
        P edge=sub(b,a);double distance=length(edge),hit=ray(a,scale(edge,1/distance),t.a,t.b,t.c);
        return hit>1e-7&&hit<distance-1e-7;
    }
    private static boolean crosses(Triangle a,Triangle b){
        return cuts(a.a,a.b,b)||cuts(a.b,a.c,b)||cuts(a.c,a.a,b)||cuts(b.a,b.b,a)||cuts(b.b,b.c,a)||cuts(b.c,b.a,a);
    }
    private static boolean boxes(Tile a,Tile b){
        for(int k=0;k<3;k++)if(a.max[k]<b.min[k]||b.max[k]<a.min[k])return false;return true;
    }
    private static int neighboringTiles(int scales){
        var tiles=new java.util.ArrayList<Tile>();
        for(int tile=0;tile<scales;tile++){
            var triangles=new java.util.ArrayList<Triangle>();double[] min={Double.POSITIVE_INFINITY,Double.POSITIVE_INFINITY,Double.POSITIVE_INFINITY};
            double[] max={Double.NEGATIVE_INFINITY,Double.NEGATIVE_INFINITY,Double.NEGATIVE_INFINITY};
            for(int k=0;k<11;k++){
                var f=FACES.get(SKIN_FACES+tile*11+k);triangles.add(new Triangle(f.a(),f.b(),f.c()));triangles.add(new Triangle(f.a(),f.c(),f.d()));
                for(P p:new P[]{f.a(),f.b(),f.c(),f.d()}){double[] v={p.x(),p.y(),p.z()};for(int j=0;j<3;j++){min[j]=Math.min(min[j],v[j]);max[j]=Math.max(max[j],v[j]);}}
            }
            tiles.add(new Tile(triangles,min,max));
        }
        int candidate=0,crossings=0;
        var examples=new java.util.ArrayList<String>();
        for(int a=0;a<tiles.size();a++)for(int b=a+1;b<tiles.size();b++){
            if(!boxes(tiles.get(a),tiles.get(b)))continue;candidate++;boolean crossed=false;
            for(Triangle x:tiles.get(a).triangles){for(Triangle y:tiles.get(b).triangles)if(crosses(x,y)){crossed=true;break;}if(crossed)break;}
            if(crossed){crossings++;if(examples.size()<8)examples.add(a+"/"+b);}
        }
        System.out.printf("Neighbor scale strict surface intersection: candidatePairs=%d, crossingPairs=%d, examples=%s%n",candidate,crossings,examples);
        return crossings;
    }
    @SuppressWarnings("unchecked")
    private static java.util.List<ImperialDragonMesh.Face> isolated(String method,Class<?>[] types,Object...args)throws Exception{
        var field=ImperialDragonMesh.class.getDeclaredField("BUILD");field.setAccessible(true);
        var build=(java.util.List<ImperialDragonMesh.Face>)field.get(null);
        if(!build.isEmpty())throw new AssertionError("Shared construction buffer unexpectedly in use");
        var generate=ImperialDragonMesh.class.getDeclaredMethod(method,types);generate.setAccessible(true);
        try{generate.invoke(null,args);return List.copyOf(build);}finally{build.clear();}
    }
    private static boolean inside(P point,List<ImperialDragonMesh.Face> shell){
        P direction=new P(.930979,.247183,.268648);direction=scale(direction,1/length(direction));
        var intersections=new java.util.ArrayList<Double>();
        for(var f:shell){double a=ray(point,direction,f.a(),f.b(),f.c()),b=ray(point,direction,f.a(),f.c(),f.d());
            if(Double.isFinite(a))intersections.add(a);if(Double.isFinite(b))intersections.add(b);}
        intersections.sort(Double::compare);int distinct=0;double previous=-1;
        for(double distance:intersections)if(Math.abs(distance-previous)>1e-6){distinct++;previous=distance;}
        return distinct%2!=0;
    }
    private static int hairTips()throws Exception{
        var field=ImperialDragonMesh.class.getDeclaredField("CRANIUM");field.setAccessible(true);
        var skull=isolated("loft",new Class<?>[]{double[][].class,int.class,int.class},field.get(null),48,0);
        int samples=0,inside=0;
        for(int side:new int[]{-1,1}){
            var mane=isolated("mane",new Class<?>[]{int.class},side);
            final int ear=128,main=128,fine=48,bundle=main+3*fine;
            int locks=3*ImperialDragonMesh.MANE_LOCKS_PER_GROUP;
            if(mane.size()!=ear+locks*bundle)throw new AssertionError("Mane structure changed; update diagnostic sampling map");
            for(int lock=0;lock<locks;lock++){
                int start=ear+lock*bundle;
                for(int i=10*8;i<14*8;i++){
                    var f=mane.get(start+i);P q=scale(add(add(f.a(),f.b()),add(f.c(),f.d())),.25);
                    samples++;if(inside(q,skull))inside++;
                }
                for(int strand=0;strand<3;strand++)for(int i=7*4;i<10*4;i++){
                    var f=mane.get(start+main+strand*fine+i);P q=scale(add(add(f.a(),f.b()),add(f.c(),f.d())),.25);
                    samples++;if(inside(q,skull))inside++;
                }
            }
        }
        System.out.printf("Free mane tips against closed skull: samples=%d, insideSkull=%d (attached roots deliberately excluded)%n",samples,inside);
        return inside;
    }
    public static void main(String[] args)throws Exception{
        centers();int scales=(int)FACES.stream().filter(f->f.material()==10).count()/2;
        int below=0,near=0,samples=0,flipped=0;double min=Double.POSITIVE_INFINITY,max=-Double.POSITIVE_INFINITY,minFold=1;
        double[][] bary={{1.0/3,1.0/3,1.0/3},{.6,.2,.2},{.2,.6,.2},{.2,.2,.6}};
        for(int i=SKIN_FACES;i<SKIN_FACES+scales*11;i++){
            var f=FACES.get(i);P n1=cross(sub(f.b(),f.a()),sub(f.c(),f.a())),n2=cross(sub(f.c(),f.a()),sub(f.d(),f.a()));
            if(length(n1)>1e-10&&length(n2)>1e-10){double cosine=dot(n1,n2)/(length(n1)*length(n2));minFold=Math.min(minFold,cosine);if(cosine<0)flipped++;}
            for(P[] triangle:new P[][]{{f.a(),f.b(),f.c()},{f.a(),f.c(),f.d()}})for(double[] w:bary){
                P p=add(add(scale(triangle[0],w[0]),scale(triangle[1],w[1])),scale(triangle[2],w[2]));
                double c=clearance(p);samples++;min=Math.min(min,c);max=Math.max(max,c);
                if(c<-.00005)below++;if(Math.abs(c)<=.00005)near++;
            }
        }
        System.out.printf("Actual scale/body ray test: scales=%d, samples=%d, minGap=%.9f, maxGap=%.9f, penetrating=%d, nearCoplanar=%d%n",scales,samples,min,max,below,near);
        System.out.printf("Scale quad fold test: negative triangle-normal pairs=%d; minimum cosine=%.6f%n",flipped,minFold);
        int crossings=neighboringTiles(scales),buriedTips=hairTips();
        if(args.length>0&&args[0].equals("--strict")&&(below>0||near>0||flipped>0||crossings>0||buriedTips>0))
            throw new AssertionError("Scale clearance/fold or free hair-tip diagnostic failed");
    }
}
