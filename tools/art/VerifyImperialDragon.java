import com.dynasty.client.ImperialDragonMesh;
import com.dynasty.client.ImperialMeshNormals;
import com.dynasty.client.ImperialWeaponGeometry;
import com.dynasty.client.ImperialWeaponGeometry.P;
import java.util.ArrayList;
import java.util.Arrays;

/** Bounded geometry checks for the real runtime mesh. These do not replace visual/gameplay QA. */
public final class VerifyImperialDragon {
    private static P subtract(P a,P b){return new P(a.x()-b.x(),a.y()-b.y(),a.z()-b.z());}
    private static P cross(P a,P b){return new P(a.y()*b.z()-a.z()*b.y(),a.z()*b.x()-a.x()*b.z(),a.x()*b.y()-a.y()*b.x());}
    private static double length(P p){return Math.sqrt(p.x()*p.x()+p.y()*p.y()+p.z()*p.z());}
    private static ImperialMeshNormals.Point point(P p){return new ImperialMeshNormals.Point(p.x(),p.y(),p.z());}
    private static void check(boolean valid,String message){if(!valid)throw new AssertionError(message);}
    private static P rotate(P p,double scale,double angle){
        return new P((p.x()*Math.cos(angle)-p.y()*Math.sin(angle))*scale,
                (p.x()*Math.sin(angle)+p.y()*Math.cos(angle))*scale,p.z()*scale);
    }
    public static void main(String[] args){
        var faces=ImperialDragonMesh.FACES;
        check(faces.size()>=30000&&faces.size()<=56000&&faces.size()*2<120000,"Single and paired dragon face budgets");
        int[] counts=new int[19];double maxEdge=0;
        var normalInput=new ArrayList<ImperialMeshNormals.Quad>();
        for(var f:faces){
            check(f.material()>=0&&f.material()<counts.length,"Unexpected material index");counts[f.material()]++;
            P[] vertices={f.a(),f.b(),f.c(),f.d()};
            for(int i=0;i<4;i++){
                P v=vertices[i];check(Double.isFinite(v.x()+v.y()+v.z()),"Non-finite vertex");
                check(Math.abs(v.x())<1.5&&v.y()>-1.9&&v.y()<2.0&&Math.abs(v.z())<1.2,"Outlier or disconnected vertex");
                maxEdge=Math.max(maxEdge,length(subtract(v,vertices[(i+1)%4])));
            }
            double area=length(cross(subtract(f.b(),f.a()),subtract(f.c(),f.a())))
                    +length(cross(subtract(f.c(),f.a()),subtract(f.d(),f.a())));
            check(area>1e-12,"Fully collapsed face");
            normalInput.add(new ImperialMeshNormals.Quad(point(f.a()),point(f.b()),point(f.c()),point(f.d()),f.material()));
        }
        check(maxEdge<.35,"Long spanning surface suggests a wrongly connected limb/face");
        double muzzleDistance=faces.stream().flatMap(f->java.util.stream.Stream.of(f.a(),f.b(),f.c(),f.d()))
                .mapToDouble(p->length(subtract(p,ImperialDragonMesh.MUZZLE))).min().orElseThrow();
        check(muzzleDistance<1e-10,"Muzzle landmark is not on the actual nose cap");
        double size=ImperialWeaponGeometry.DESCENT_DRAGON_SIZE;
        check(Math.abs(size/2.7-1.5)<1e-10,"Attack dragon must be 1.5 times the original scale");
        check(ImperialWeaponGeometry.DRAGON_ENLARGEMENT==3.0,"Decorative guardians must retain their scale");
        check(ImperialWeaponGeometry.DESCENT_START_HEIGHT==12.0,"Raised descent height must be preserved");
        P impact=ImperialDragonMesh.impactOffset(size,Math.PI*.75);
        check(length(subtract(impact,rotate(ImperialDragonMesh.MUZZLE,size,Math.PI*.75)))<1e-10,"Impact landmark transform drifted");
        // The renderer subtracts this local offset in the yaw-dependent right/up/forward basis.
        for(double yaw:new double[]{0,Math.PI/2,Math.PI*.79})for(double age:new double[]{18,19,26,31,32,44}){
            P target=new P(11.2,68.7,-4.5),right=new P(Math.cos(yaw),0,Math.sin(yaw)),forward=new P(-Math.sin(yaw),0,Math.cos(yaw));
            var phase=ImperialWeaponGeometry.descentPhase(age,18,32);
            double lift=(2.4+12.0)*(1-phase.travel()*phase.travel());
            P offset=ImperialWeaponGeometry.descentDragonOrigin(2.4,phase.travel());
            P origin=target.add(right.scale(offset.x())).add(new P(0,offset.y(),0)).add(forward.scale(offset.z()));
            P nose=origin.add(right.scale(impact.x())).add(new P(0,impact.y(),0)).add(forward.scale(impact.z()));
            check(length(subtract(nose,target.add(new P(0,lift,0))))<1e-9,"Descent muzzle drifts off the target axis");
            if(age>=32)check(length(subtract(nose,target))<1e-9,"Nose does not land on target at damage tick");
        }
        // Verify the complete golden aura sway range, including the mirrored left guardian.
        for(double angle:new double[]{-.22,-.18,-.14}){
            P nose=rotate(ImperialDragonMesh.MUZZLE,3.54,angle).add(new P(3.15,0,.24));
            P skull=rotate(ImperialDragonMesh.HEAD_CENTER,3.54,angle).add(new P(3.15,0,.24));
            check(nose.x()>0&&nose.x()<skull.x(),"Right guardian no longer faces inward");
            check(-nose.x()<0&&-nose.x()>-skull.x(),"Mirrored left guardian no longer faces inward");
        }
        check(counts[0]>8000&&counts[8]>2000&&counts[6]>600,"Missing scales/skin/ventral plates");
        check(counts[2]>300&&counts[3]>2000&&counts[7]>300,"Missing mouth/teeth/gums");
        check(counts[4]>100&&counts[12]>100&&counts[13]>1000,"Missing iris/catchlights/volumetric mane");
        var normals=ImperialMeshNormals.build(normalInput);
        check(normals.size()==faces.size(),"Normal count does not match mesh");
        for(var n:normals)for(var p:new ImperialMeshNormals.Point[]{n.a(),n.b(),n.c(),n.d()}){
            double len=Math.sqrt(p.x()*p.x()+p.y()*p.y()+p.z()*p.z());
            check(Double.isFinite(len)&&Math.abs(len-1)<1e-6,"Invalid or non-unit smoothed normal");
        }
        int[] emitted={0};
        var geometry=new ImperialWeaponGeometry((a,b,w,c,alpha)->{},(a,b,c,d,color,alpha)->{
            emitted[0]++;for(P p:new P[]{a,b,c,d})check(Double.isFinite(p.x()+p.y()+p.z()+alpha),"Invalid transformed dragon");
        });
        for(double t:new double[]{0,8,40,80}){
            emitted[0]=0;geometry.aura(1,t,Math.min(1,t/40));
            check(emitted[0]==faces.size()*2,"Dual golden guardians lost a body part");
            emitted[0]=0;geometry.dragon(new P(0,2,0),1.8,Math.PI*.75,t,0x36cbbb,1);
            check(emitted[0]==faces.size(),"Descending dragon count changed");
        }
        System.out.println("Dragon geometry PASS: "+faces.size()+" quads; max edge "+maxEdge+"; material counts "+Arrays.toString(counts));
        System.out.println("Actual muzzle "+ImperialDragonMesh.MUZZLE+"; descent impact offset "+impact+"; exact age-32 landing / enlarged inward golden heads PASS");
        System.out.println("Finite/area/bounds/smooth-normal/dual-guardian/descent transforms PASS; visual reference fidelity is not automatically certified.");
    }
}
