import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Font;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.awt.image.DataBufferInt;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import javax.imageio.ImageIO;

/** Offline exact-mesh rasterizer. Real triangle Z-buffer; not SVG painter sorting or generated art. */
public final class RenderImperialMeshes {
    private record P(double x,double y,double z) {
        P add(P p){return new P(x+p.x,y+p.y,z+p.z);} P sub(P p){return new P(x-p.x,y-p.y,z-p.z);}
        P scale(double s){return new P(x*s,y*s,z*s);} double dot(P p){return x*p.x+y*p.y+z*p.z;}
        P cross(P p){return new P(y*p.z-z*p.y,z*p.x-x*p.z,x*p.y-y*p.x);} P unit(){return scale(1/Math.max(1e-12,Math.sqrt(dot(this))));}
    }
    private record Vertex(double x,double y,double z,P world,P normal) {}
    private record Paint(double r,double g,double b) {}
    private record Mesh(String id,String name,double[] vertices,double[] normals,int[] materials,Paint[] palette,P min,P max) {}
    private static final P KEY=new P(-.45,.8,.6).unit(), FILL=new P(.7,.35,-.45).unit();
    private static int[] pixels;private static double[] depths;private static int width,height;
    public static void main(String[] args)throws Exception {
        if(args.length<2)throw new IllegalArgumentException("RenderImperialMeshes meshes.json output.png [guanyu|jade_dragon|gold_dragon] [four|threequarter|front|side|back|portrait]");
        String id=args.length>2?args[2]:"guanyu",mode=args.length>3?args[3]:"four";
        JsonObject data;try(var reader=Files.newBufferedReader(Path.of(args[0]))){data=JsonParser.parseReader(reader).getAsJsonObject();}
        Mesh mesh=null;
        for(var e:data.getAsJsonArray("models")) {
            JsonObject o=e.getAsJsonObject();if(!o.get("id").getAsString().equals(id))continue;
            var ps=o.getAsJsonArray("materials");Paint[] paints=new Paint[ps.size()];
            for(int i=0;i<paints.length;i++){var a=ps.get(i).getAsJsonObject().getAsJsonArray("rgb");paints[i]=new Paint(a.get(0).getAsDouble(),a.get(1).getAsDouble(),a.get(2).getAsDouble());}
            var ids=o.getAsJsonArray("materialIndices");int[] materials=new int[ids.size()];for(int i=0;i<materials.length;i++)materials[i]=ids.get(i).getAsInt();
            var b=o.getAsJsonObject("bounds");mesh=new Mesh(id,o.get("name").getAsString(),array(o.getAsJsonArray("positions")),array(o.getAsJsonArray("normals")),materials,paints,point(array(b.getAsJsonArray("min")),0),point(array(b.getAsJsonArray("max")),0));
        }
        if(mesh==null)throw new IllegalArgumentException("Unknown model: "+id);
        width=1800;height=mode.equals("four")?1400:1600;
        BufferedImage image=new BufferedImage(width,height,BufferedImage.TYPE_INT_RGB);pixels=((DataBufferInt)image.getRaster().getDataBuffer()).getData();depths=new double[pixels.length];Arrays.fill(depths,Double.POSITIVE_INFINITY);
        for(int y=0;y<height;y++){double t=(double)y/height;int r=(int)(16+4*t),g=(int)(24+6*t),b=(int)(34+9*t);Arrays.fill(pixels,y*width,(y+1)*width,(r<<16)|(g<<8)|b);}
        long start=System.nanoTime();
        if(mode.equals("four")) {
            render(mesh,0,120,900,600,0,.015,false);render(mesh,900,120,900,600,Math.PI/2,.015,false);
            render(mesh,0,720,900,600,Math.PI,.015,false);render(mesh,900,720,900,600,.43,.11,false);
        } else {double yaw=switch(mode){case "front"->0;case "side"->Math.PI/2;case "back"->Math.PI;case "portrait"->.09;default->.43;};render(mesh,0,120,width,height-190,yaw,mode.equals("portrait")?.035:.08,mode.equals("portrait"));}
        Graphics2D g=image.createGraphics();g.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING,RenderingHints.VALUE_TEXT_ANTIALIAS_ON);g.setColor(new Color(217,191,131));g.setFont(new Font("SansSerif",Font.BOLD,29));g.drawString("DYNASTY  /  "+mesh.name,38,50);g.setColor(new Color(149,168,187));g.setFont(new Font("SansSerif",Font.PLAIN,18));g.drawString("ACTUAL RUNTIME MESH · Z-BUFFERED MATERIAL PREVIEW · NOT AN IN-GAME SCREENSHOT",38,86);
        if(mode.equals("four")){g.setColor(new Color(66,79,91));g.setStroke(new BasicStroke(1));g.drawLine(900,120,900,1320);g.drawLine(0,720,1800,720);g.setFont(new Font("SansSerif",Font.PLAIN,18));g.setColor(new Color(167,184,201));g.drawString("FRONT / 正面",28,152);g.drawString("SIDE / 侧面",928,152);g.drawString("BACK / 背面",28,752);g.drawString("THREE-QUARTER / 立体视角",928,752);}
        g.setColor(new Color(144,160,177));g.setFont(new Font("SansSerif",Font.PLAIN,18));g.drawString(String.format("%,d QUADS  ·  shared runtime smooth normals  ·  opaque depth-tested surfaces",mesh.materials.length),38,height-38);g.dispose();
        Path output=Path.of(args[1]);if(output.getParent()!=null)Files.createDirectories(output.getParent());ImageIO.write(image,"png",output.toFile());
        System.out.printf("Rendered %s %s · %,d quads · %.2fs · %s%n",id,mode,mesh.materials.length,(System.nanoTime()-start)/1e9,output.toAbsolutePath());
    }
    private static void render(Mesh m,int x,int y,int w,int h,double yaw,double pitch,boolean portrait) {
        boolean dragon=m.id.endsWith("_dragon");
        // A dragon's horns, lower jaw and beard span more height than a human portrait.
        double size=m.max.y-m.min.y;P center=m.min.add(m.max).scale(.5);if(portrait)center=new P(center.x,m.min.y+size*(dragon?.73:.83),center.z);
        double aspect=(double)w/h;double distance=Math.max(size,(m.max.x-m.min.x)/aspect)*(portrait?(dragon?.95:.66):1.98);
        P eye=center.add(new P(Math.sin(yaw)*Math.cos(pitch),Math.sin(pitch),Math.cos(yaw)*Math.cos(pitch)).scale(distance));
        P forward=center.sub(eye).unit(),right=forward.cross(new P(0,1,0)).unit(),up=right.cross(forward).unit();double focal=h/(2*Math.tan(.57*.5));
        Vertex[] q=new Vertex[4];
        for(int f=0;f<m.materials.length;f++) {
            boolean visible=true;
            for(int i=0;i<4;i++){int index=f*12+i*3;P world=point(m.vertices,index),normal=point(m.normals,index),v=world.sub(eye);double z=v.dot(forward);if(z<size*.003){visible=false;break;}q[i]=new Vertex(x+w*.5+v.dot(right)/z*focal,y+h*.50-v.dot(up)/z*focal,z,world,normal);}
            if(!visible)continue;Paint p=m.palette[m.materials[f]];triangle(q[0],q[1],q[2],p,eye,x,y,w,h);triangle(q[0],q[2],q[3],p,eye,x,y,w,h);
        }
    }
    private static double edge(Vertex a,Vertex b,double x,double y){return (x-a.x)*(b.y-a.y)-(y-a.y)*(b.x-a.x);}
    private static void triangle(Vertex a,Vertex b,Vertex c,Paint p,P eye,int ox,int oy,int w,int h) {
        double area=edge(a,b,c.x,c.y);if(Math.abs(area)<1e-10)return;
        int minX=Math.max(ox,(int)Math.floor(Math.min(a.x,Math.min(b.x,c.x)))),maxX=Math.min(ox+w-1,(int)Math.ceil(Math.max(a.x,Math.max(b.x,c.x))));
        int minY=Math.max(oy,(int)Math.floor(Math.min(a.y,Math.min(b.y,c.y)))),maxY=Math.min(oy+h-1,(int)Math.ceil(Math.max(a.y,Math.max(b.y,c.y))));
        for(int y=minY;y<=maxY;y++)for(int x=minX;x<=maxX;x++) {
            double wa=edge(b,c,x+.5,y+.5)/area,wb=edge(c,a,x+.5,y+.5)/area,wc=1-wa-wb;if(wa<-.0000001||wb<-.0000001||wc<-.0000001)continue;
            wa/=a.z;wb/=b.z;wc/=c.z;double z=1/(wa+wb+wc);int index=y*width+x;if(z>=depths[index])continue;wa*=z;wb*=z;wc*=z;
            P n=a.normal.scale(wa).add(b.normal.scale(wb)).add(c.normal.scale(wc)).unit(),world=a.world.scale(wa).add(b.world.scale(wb)).add(c.world.scale(wc)),view=eye.sub(world).unit();if(n.dot(view)<0)n=n.scale(-1);
            double metal=Math.max(smooth(.09,.27,p.r-p.b)*smooth(.23,.55,p.g),smooth(.66,.86,Math.min(p.r,Math.min(p.g,p.b)))*.55);
            double diffuse=.28+.64*Math.max(0,n.dot(KEY))+.16*Math.max(0,n.dot(FILL));
            double highlight=Math.pow(Math.max(0,n.dot(KEY.add(view).unit())),26+54*metal),rim=Math.pow(1-Math.max(0,n.dot(view)),3),spec=highlight*(.055+.365*metal);
            double r=p.r*diffuse+(.8+.2*metal)*spec+p.r*.13*rim,g=p.g*diffuse+(.88-.01*metal)*spec+p.g*.17*rim,bv=p.b*diffuse+(1-.36*metal)*spec+p.b*.20*rim;
            pixels[index]=(channel(r)<<16)|(channel(g)<<8)|channel(bv);depths[index]=z;
        }
    }
    private static int channel(double v){return (int)Math.round(Math.max(0,Math.min(1,v))*255);}
    private static double smooth(double a,double b,double x){double t=Math.max(0,Math.min(1,(x-a)/(b-a)));return t*t*(3-2*t);}
    private static P point(double[] a,int offset){return new P(a[offset],a[offset+1],a[offset+2]);}
    private static double[] array(JsonArray a){double[] result=new double[a.size()];for(int i=0;i<result.length;i++)result[i]=a.get(i).getAsDouble();return result;}
}
