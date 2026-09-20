import com.dynasty.client.ImperialWeaponGeometry;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;
import java.util.ArrayList;
import java.util.Comparator;

/** Legacy SVG effect-layout diagnostic. Geometry checks are real; painter shading is not the game material. */
public final class ImperialWeaponPreview {
    // Two remastered dragons may be visible together; VerifyImperialDragon caps each at 45k quads.
    // The final layered mane, facial anatomy and individually shaped scales use ~43k per dragon.
    // The original 30k whole-panel ceiling predates the anatomical/closed-surface remaster.
    private static final int SURFACE_BUDGET=2*56_000; // Still below the production 120k face cap.
    record Surface(double depth,String xml) {}
    public static void main(String[] args) throws Exception {
        StringBuilder svg=new StringBuilder("<svg xmlns='http://www.w3.org/2000/svg' width='1560' height='1040' viewBox='0 0 1560 1040'><rect width='1560' height='1040' fill='#070f1b'/>");
        svg.append("<text x='40' y='48' fill='#f5dfaa' font-family='sans-serif' font-size='28'>DYNASTY / IMPERIAL WEAPONS</text>");
        svg.append("<text x='40' y='80' fill='#99aec3' font-family='sans-serif' font-size='17'>Actual effect geometry · held aura / attack sweep / impact mark</text>");
        for(int style=1;style<=2;style++) for(int phase=0;phase<3;phase++) {
            final double cx=270+phase*510, cy=330+(style-1)*445, scale=89;
            String color=style==1?"#ffd27d":"#77eed0";
            svg.append(String.format(Locale.ROOT,"<rect x='%.0f' y='%.0f' width='490' height='410' rx='20' fill='#0e1b2c'/>",cx-245,cy-200));
            int[] count={0};
            var surfaces=new ArrayList<Surface>();
            var geometry=new ImperialWeaponGeometry((a,b,width,c,alpha)-> {
                if(!Double.isFinite(a.x()+a.y()+a.z()+b.x()+b.y()+b.z()+width+alpha)||width<0||alpha<0)
                    throw new AssertionError("Invalid geometry");
                count[0]++;
                String hex=String.format("#%06x",c);
                for(int pass=0;pass<2;pass++)svg.append(String.format(Locale.ROOT,
                        "<line x1='%.2f' y1='%.2f' x2='%.2f' y2='%.2f' stroke='%s' stroke-width='%.2f' stroke-opacity='%.3f' stroke-linecap='round'/>",
                        cx+(a.x()+a.z()*.18)*scale,cy-a.y()*scale,
                        cx+(b.x()+b.z()*.18)*scale,cy-b.y()*scale,hex,
                        Math.max(.3,width*scale*2*(pass==0?2.6:1)),alpha*(pass==0?.12:.72)));
            },(a,b,c,d,col,alpha)-> {
                var points=new ImperialWeaponGeometry.P[]{a,b,c,d};
                StringBuilder coords=new StringBuilder();
                if(!Double.isFinite(alpha)||alpha<0)throw new AssertionError("Invalid surface alpha");
                for(var p:points) {
                    if(!Double.isFinite(p.x()+p.y()+p.z()))throw new AssertionError("Invalid surface");
                    coords.append(String.format(Locale.ROOT,"%.2f,%.2f ",cx+(p.x()+p.z()*.18)*scale,cy-p.y()*scale));
                }
                double ux=b.x()-a.x(),uy=b.y()-a.y(),uz=b.z()-a.z();
                double vx=c.x()-a.x(),vy=c.y()-a.y(),vz=c.z()-a.z();
                double nx=uy*vz-uz*vy,ny=uz*vx-ux*vz,nz=ux*vy-uy*vx;
                double len=Math.sqrt(nx*nx+ny*ny+nz*nz);
                double shade=len<1e-9?.44:.44+.56*Math.abs((nx*-.35+ny*.65+nz*.68)/len);
                if(col==0xd4ffff)shade=1;
                String hex=String.format("#%02x%02x%02x",(int)(((col>>16)&255)*shade),(int)(((col>>8)&255)*shade),(int)((col&255)*shade));
                surfaces.add(new Surface((a.z()+b.z()+c.z()+d.z())/4,String.format(Locale.ROOT,
                        "<polygon points='%s' fill='%s' fill-opacity='%.3f'/>",coords,hex,Math.min(.96,alpha*1.35))));
            });
            if(phase==0)geometry.aura(style,70,1);
            if(phase==1 && style==1)geometry.slash(style,.45,1);
            if(phase==2 && style==1)geometry.impact(style,.35,1);
            if(style==2 && phase>0) {
                if(phase==1)geometry.dragon(new ImperialWeaponGeometry.P(0,.1,0),1.15,Math.PI*.75,16,0x36cbbb,1);
                double sealY=phase==1?1.35:-.9;
                new com.dynasty.client.BowSigilGeometry(1,(x1,y1,x2,y2,w)->svg.append(String.format(Locale.ROOT,
                        "<line x1='%.2f' y1='%.2f' x2='%.2f' y2='%.2f' stroke='#79ffe2' stroke-opacity='.75' stroke-width='%.2f'/>",
                        cx+x1*135,cy-sealY*scale-y1*40,cx+x2*135,cy-sealY*scale-y2*40,Math.max(.5,w*150)))).draw(3,16);
                if(phase==2)geometry.dragon(new ImperialWeaponGeometry.P(0,.25,0),.95,Math.PI*.75,20,0x36cbbb,.6);
            }
            surfaces.sort(Comparator.comparingDouble(Surface::depth));
            for(var surface:surfaces)svg.append(surface.xml());
            if(surfaces.size()>SURFACE_BUDGET)throw new AssertionError("Surface budget exceeded: "+surfaces.size()+" > "+SURFACE_BUDGET);
            if(count[0]>1200)throw new AssertionError("Geometry budget exceeded: "+count[0]);
            System.out.println("Style "+style+", phase "+phase+": "+count[0]+" strokes, "+surfaces.size()+" faces");
            String name=style==1?"TIANZI / DUAL GOLDEN DRAGONS":"QINGLONG / JADE DRAGON";
            String phaseName=(style==1?new String[]{"HELD AURA","ATTACK SWEEP","HIT CONFIRM"}
                    :new String[]{"THIRD-PERSON AURA","DESCENDING STRIKE","LANDING / DAMAGE"})[phase];
            svg.append(String.format(Locale.ROOT,"<text x='%.0f' y='%.0f' text-anchor='middle' fill='%s' font-family='sans-serif' font-size='15'>%s · %s</text>",cx,cy+185,color,name,phaseName));
        }
        // Check the complete animation, including formation and fade endpoints.
        int[] maximum={0};
        for(int style=1;style<=2;style++)for(int frame=0;frame<=120;frame++) {
            int[] n={0},surfaceCount={0};
            var g=new ImperialWeaponGeometry((a,b,w,c,alpha)-> {
                if(!Double.isFinite(a.x()+a.y()+a.z()+b.x()+b.y()+b.z()+w+alpha)||w<0||alpha<0)
                    throw new AssertionError("Invalid animation frame");
                n[0]++;
            },(a,b,c,d,col,alpha)-> {
                surfaceCount[0]++;
                if(alpha<0)throw new AssertionError("Negative animated surface alpha");
                for(var p:new ImperialWeaponGeometry.P[]{a,b,c,d})
                    if(!Double.isFinite(p.x()+p.y()+p.z()+alpha))throw new AssertionError("Invalid animated surface");
            });
            g.aura(style,frame,Math.min(1,frame/18.0));
            g.slash(style,frame/120.0,Math.sin(frame/120.0*Math.PI));
            g.impact(style,frame/120.0,1-frame/120.0);
            if(surfaceCount[0]>SURFACE_BUDGET)throw new AssertionError("Animated surface budget exceeded at "+frame);
            maximum[0]=Math.max(maximum[0],n[0]);
        }
        System.out.println("Animation frames checked: 242; maximum combined strokes: "+maximum[0]);
        svg.append("<text x='780' y='1013' text-anchor='middle' fill='#92a6bf' font-family='sans-serif' font-size='16'>Legacy SVG layout diagnostic: painter shading is not the current game material; not an in-game screenshot.</text></svg>");
        Files.createDirectories(Path.of(args[0]).getParent());
        Files.writeString(Path.of(args[0]),svg);
    }
}
