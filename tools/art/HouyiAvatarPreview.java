import com.dynasty.HouyiAvatarShape;
import com.dynasty.HouyiAvatarShape.P;
import com.dynasty.HouyiAvatarShape.Material;
import com.dynasty.client.BowSigilGeometry;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Locale;

/** Exports the actual curved mesh and head sigil, rather than a concept painting. */
public final class HouyiAvatarPreview {
    record Face(double depth,String xml) {}
    public static void main(String[] args) throws Exception {
        StringBuilder svg=new StringBuilder("<svg xmlns='http://www.w3.org/2000/svg' width='1440' height='900' viewBox='0 0 1440 900'><rect width='1440' height='900' fill='#0b1323'/>");
        svg.append("<rect x='930' y='120' width='475' height='665' rx='24' fill='#101f32'/>");
        svg.append("<text x='45' y='54' fill='#efcea0' font-family='sans-serif' font-size='28'>HOUYI / DIVINE ASPECT</text>");
        svg.append("<text x='45' y='85' fill='#95abc1' font-family='sans-serif' font-size='16'>Sculpted anatomy · layered ceremonial armor · solar crown · luminous head sigil</text>");
        render(svg,470,763,59,0.28,0,false);
        drawSigil(svg,470,139,115,0.26,40);
        drawSigil(svg,1167,196,132,0.24,40);
        render(svg,1167,590,130,-0.04,7.4,true);
        svg.append("<text x='1167' y='744' text-anchor='middle' fill='#d4dfed' font-family='sans-serif' font-size='18'>Crown, face and luminous eyes</text>");
        svg.append("<text x='470' y='834' text-anchor='middle' fill='#d4dfed' font-family='sans-serif' font-size='18'>Curved body, separate hands, layered armor and floating silk</text>");
        svg.append("<text x='720' y='880' text-anchor='middle' fill='#7f96b0' font-family='sans-serif' font-size='14'>Exported from the in-game mesh and seal geometry — not an in-game screenshot</text></svg>");
        Files.writeString(Path.of(args[0]),svg);
        System.out.println("Mesh quads: "+HouyiAvatarShape.MESH.size());
    }
    static void render(StringBuilder svg,double cx,double base,double scale,double angle,double offset,boolean portrait) {
        var faces=new ArrayList<Face>();
        double c=Math.cos(angle),s=Math.sin(angle);
        P view=new P(-s,.12,c).unit(),light=new P(-.45,.8,.6).unit();
        for(var face:HouyiAvatarShape.MESH) {
            if(portrait&&(face.center().y()<7.45||Math.abs(face.center().x())>1.35))continue;
            if(portrait && (Math.abs(face.a().x())>1.35 || Math.abs(face.b().x())>1.35
                    || Math.abs(face.c().x())>1.35 || Math.abs(face.d().x())>1.35))continue;
            StringBuilder points=new StringBuilder();
            for(P p:new P[]{face.a(),face.b(),face.c(),face.d()}) {
                double x=p.x()*c+p.z()*s, depth=-p.x()*s+p.z()*c;
                points.append(String.format(Locale.ROOT,"%.3f,%.3f ",cx+x*scale,base-(p.y()-offset)*scale-depth*scale*.12));
            }
            double rim=Math.pow(1-Math.abs(face.normal().dot(view)),3);
            double shade=.38+.62*Math.max(0,face.normal().dot(light));
            Material m=face.material();
            if(m==Material.LIGHT)shade=1;
            int r=(int)(255*Math.min(1,m.r*shade+rim*.13));
            int g=(int)(255*Math.min(1,m.g*shade+rim*.15));
            int b=(int)(255*Math.min(1,m.b*shade+rim*.18));
            double alpha=m==Material.LIGHT?.95:m==Material.GOLD?.82:.68;
            String color=String.format("#%02x%02x%02x",r,g,b);
            faces.add(new Face(face.center().dot(view),String.format(Locale.ROOT,
                    "<polygon points='%s' fill='%s' fill-opacity='%.2f' stroke='none'/>",
                    points,color,alpha)));
        }
        faces.sort(Comparator.comparingDouble(Face::depth));
        for(var face:faces)svg.append(face.xml());
    }
    static void drawSigil(StringBuilder svg,double cx,double cy,double radius,double squash,double time) {
        svg.append("<g stroke='#f6b656' fill='none'>");
        new BowSigilGeometry(1,(x1,y1,x2,y2,w)->svg.append(String.format(Locale.ROOT,
                "<line stroke='#f6b656' stroke-opacity='1' x1='%.3f' y1='%.3f' x2='%.3f' y2='%.3f' stroke-width='%.3f'/>",
                cx+x1*radius,cy-y1*radius*squash,cx+x2*radius,cy-y2*radius*squash,Math.max(.6,w*radius*2)))).drawBagua(time);
        svg.append("</g>");
    }
}
