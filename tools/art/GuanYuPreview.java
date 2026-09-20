import com.dynasty.GuanYuAvatarShape;
import com.dynasty.HouyiAvatarShape.P;
import com.dynasty.HouyiAvatarShape.Material;
import java.nio.file.*;
import java.util.*;

/** Legacy SVG geometry diagnostic; use RenderImperialMeshes for depth/material visual review. */
public final class GuanYuPreview {
    // The remaster adds articulated anatomy, closed swept surfaces and layered armor.
    // Match VerifyGuanYuRemaster's per-instance review ceiling; never disable the budget check.
    private static final int GUARDIAN_QUAD_LIMIT=120_000;
    record Fragment(double depth,String xml){}
    public static void main(String[] args)throws Exception {
        StringBuilder svg=new StringBuilder("<svg xmlns='http://www.w3.org/2000/svg' width='1440' height='1000'><rect width='1440' height='1000' fill='#0a1420'/>");
        svg.append("<text x='44' y='52' fill='#edd59e' font-family='sans-serif' font-size='30'>GUAN YU / GUARDIAN OF THE GUANDAO</text><text x='44' y='84' fill='#9aafbd' font-family='sans-serif' font-size='17'>Red face · flowing beard · jade robes · gilded armor · crescent blade</text>");
        svg.append("<rect x='945' y='120' width='450' height='735' rx='20' fill='#112235'/>");
        draw(svg,530,893,85,.15,false);
        draw(svg,1165,1430,130,0,true);
        svg.append("<text x='1165' y='820' text-anchor='middle' fill='#dacbaa' font-family='sans-serif' font-size='18'>Face, long beard and crown</text><text x='720' y='963' text-anchor='middle' fill='#8da6b9' font-family='sans-serif' font-size='16'>Legacy SVG geometry diagnostic: not depth-correct, not the current game material, not a screenshot.</text></svg>");
        Files.createDirectories(Path.of(args[0]).getParent());Files.writeString(Path.of(args[0]),svg);
        if(GuanYuAvatarShape.MESH.isEmpty()||GuanYuAvatarShape.MESH.size()>=GUARDIAN_QUAD_LIMIT)
            throw new AssertionError("Guardian mesh budget exceeded: "+GuanYuAvatarShape.MESH.size()+" (limit < "+GUARDIAN_QUAD_LIMIT+")");
        System.out.println("Guardian quads: "+GuanYuAvatarShape.MESH.size());
    }
    static void draw(StringBuilder svg,double cx,double base,double scale,double angle,boolean portrait) {
        List<Fragment> fragments=new ArrayList<>();
        P view=new P(-Math.sin(angle),.10,Math.cos(angle)).unit(),light=new P(-.45,.8,.6).unit();
        for(var f:GuanYuAvatarShape.MESH) {
            if(portrait&&(f.center().y()<5.5||Math.abs(f.center().x())>.85))continue;
            StringBuilder points=new StringBuilder();
            for(P p:new P[]{f.a(),f.b(),f.c(),f.d()}) {
                if(!Double.isFinite(p.x()+p.y()+p.z()))throw new AssertionError("Nonfinite mesh");
                double x=p.x()*Math.cos(angle)+p.z()*Math.sin(angle),depth=-p.x()*Math.sin(angle)+p.z()*Math.cos(angle);
                points.append(String.format(Locale.ROOT,"%.2f,%.2f ",cx+x*scale,base-p.y()*scale-depth*scale*.10));
            }
            double rim=Math.pow(1-Math.abs(f.normal().dot(view)),3),shade=.38+.62*Math.max(0,f.normal().dot(light));
            Material m=f.material();if(m==Material.LIGHT)shade=1;
            int r=(int)(255*Math.min(1,m.r*shade+rim*.13)),g=(int)(255*Math.min(1,m.g*shade+rim*.15)),b=(int)(255*Math.min(1,m.b*shade+rim*.18));
            fragments.add(new Fragment(f.center().dot(view),String.format(Locale.ROOT,"<polygon points='%s' fill='#%02x%02x%02x' fill-opacity='%.2f'/>",points,r,g,b,m==Material.GOLD?.82:.68)));
        }
        fragments.sort(Comparator.comparingDouble(Fragment::depth));for(var f:fragments)svg.append(f.xml);
    }
}
