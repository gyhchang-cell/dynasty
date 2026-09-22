import com.dynasty.client.ImperialDragonMesh;
import com.dynasty.client.ImperialWeaponGeometry;
import com.dynasty.client.ImperialWeaponGeometry.P;
import java.awt.*;
import java.awt.geom.Line2D;
import java.awt.image.BufferedImage;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import javax.imageio.ImageIO;

/** Exact production stroke geometry/timing diagnostic, not a Minecraft world screenshot. */
public final class QinglongSealPreview {
    private static final double BOTTOM=-.955,TOP=2.4,RADIUS=ImperialWeaponGeometry.DESCENT_SEAL_RADIUS;
    private static final int START=18,LAND=32;
    private record Stroke(P a,P b,double width,int color,double alpha) {}
    private static List<Stroke> geometry(double age,double fade) {
        List<Stroke> lines=new ArrayList<>();
        var phase=ImperialWeaponGeometry.descentPhase(age,START,LAND);
        new ImperialWeaponGeometry((a,b,w,c,alpha)->lines.add(new Stroke(a,b,w,c,alpha)))
                .sealCage(age,phase.charge(),phase.connection(),BOTTOM,TOP,RADIUS,fade);
        return lines;
    }
    private static void check(boolean condition,String description){if(!condition)throw new AssertionError(description);}
    private static boolean close(double a,double b){return Math.abs(a-b)<1e-9;}
    private static void verify() {
        int maximum=0,frames=0;double previousTip=BOTTOM;
        for(int step=0;step<=176;step++) {
            double age=step*.25;var phase=ImperialWeaponGeometry.descentPhase(age,START,LAND);
            check(phase.charge()>=0&&phase.charge()<=1&&phase.connection()>=0&&phase.connection()<=1,"Phase bounds");
            check(age>START||phase.dragonAlpha()==0,"Dragon appears before cage completes");
            check(age<LAND||phase.travel()==1,"Dragon has not landed at damage tick");
            List<Stroke> full=geometry(age,1),half=geometry(age,.5);
            check(full.size()==half.size(),"Fade changed formation topology");
            List<Stroke> seals=full.stream().filter(s->s.color==0x79ffe2).toList();
            check(seals.size()%2==0,"Unequal seal stroke counts");int n=seals.size()/2;
            for(int i=0;i<n;i++) {
                Stroke a=seals.get(i),b=seals.get(i+n);
                check(close(a.a.x(),b.a.x())&&close(a.a.z(),b.a.z())&&close(a.b.x(),b.b.x())&&close(a.b.z(),b.b.z())
                        &&close(a.a.y(),BOTTOM)&&close(b.a.y(),TOP)&&close(a.width,b.width),"Upper/lower array pattern or radius differs");
            }
            double tip=BOTTOM;
            for(int i=0;i<full.size();i++) {
                Stroke s=full.get(i),f=half.get(i);
                check(Double.isFinite(s.a.x()+s.a.y()+s.a.z()+s.b.x()+s.b.y()+s.b.z()+s.width+s.alpha),"Nonfinite vertex");
                check(s.width>0&&s.alpha>0&&s.alpha<=1,"Invalid stroke width/opacity");
                check(s.a.y()>=BOTTOM-1e-9&&s.b.y()<=TOP+1e-9&&s.a.y()<=TOP+1e-9&&s.b.y()>=BOTTOM-1e-9,"Cage escaped height bounds");
                check(s.a.equals(f.a)&&s.b.equals(f.b)&&close(s.alpha*.5,f.alpha),"Fading moved a line");
                if(s.color==0x8cffe6) {
                    check(close(s.a.y(),BOTTOM),"Pillar did not start at feet");
                    check(close(s.a.x(),s.b.x())&&close(s.a.z(),s.b.z()),"Pillar is not vertical");
                    check(close(Math.hypot(s.a.x(),s.a.z()),RADIUS*.955),"Pillar did not attach to seal ring");
                    tip=Math.max(tip,s.b.y());
                }
            }
            if(age<=8)check(full.stream().noneMatch(s->s.color!=0x79ffe2),"Cage connected before arrays formed");
            check(tip>=previousTip-1e-9,"Pillar reveal moved downwards");previousTip=tip;
            if(age>=START)check(close(tip,TOP),"Cage not closed before descent");
            var muzzle=ImperialWeaponGeometry.descentDragonPose(TOP,phase.travel()).point(ImperialDragonMesh.MUZZLE);
            check(close(muzzle.x(),0)&&close(muzzle.z(),0),"Dragon misses target horizontally");
            if(age>=LAND)check(close(muzzle.y(),0),"Dragon misses target vertically at impact");
            maximum=Math.max(maximum,full.size());frames++;
        }
        check(maximum<5000,"Excessive seal stroke budget: "+maximum);
        check(geometry(0,1).isEmpty()&&geometry(18,0).isEmpty(),"Zero-visibility frame allocates geometry");
        System.out.printf("PASS: %d fractional-tick frames; identical upper/lower arrays; monotonic upward cage; independent fade; exact %.2f-scale muzzle landing; max %,d strokes.%n",frames,ImperialWeaponGeometry.DESCENT_DRAGON_SIZE,maximum);
    }
    private static double sx(P p,double cx){return cx+(p.x()*.8660254-p.z()*.5)*76;}
    private static double sy(P p){return 532-(p.y()-BOTTOM)*76+(p.x()*.5+p.z()*.8660254)*.38*76;}
    private static void segment(Graphics2D g,P a,P b,double cx,double width,Color color) {
        g.setColor(color);g.setStroke(new BasicStroke((float)width,BasicStroke.CAP_ROUND,BasicStroke.JOIN_ROUND));
        g.draw(new Line2D.Double(sx(a,cx),sy(a),sx(b,cx),sy(b)));
    }
    private static void panel(Graphics2D g,int index,double age,String heading) {
        int left=20+index*455;double cx=left+217;
        g.setColor(new Color(13,26,38));g.fillRoundRect(left,112,435,536,18,18);
        Shape clip=g.getClip();g.clipRect(left+5,190,425,418);
        for(int j=-3;j<=3;j++) {
            segment(g,new P(-3,BOTTOM,j),new P(3,BOTTOM,j),cx,.6,new Color(29,47,59));
            segment(g,new P(j,BOTTOM,-3),new P(j,BOTTOM,3),cx,.6,new Color(29,47,59));
        }
        // A labelled two-block target volume is a scale guide, never a stand-in for a game model.
        Color guide=new Color(64,80,92);
        for(double x:new double[]{-.32,.32})for(double z:new double[]{-.32,.32})
            segment(g,new P(x,BOTTOM,z),new P(x,BOTTOM+2,z),cx,1,guide);
        for(double y:new double[]{BOTTOM,BOTTOM+2}) {
            segment(g,new P(-.32,y,-.32),new P(.32,y,-.32),cx,1,guide);
            segment(g,new P(.32,y,-.32),new P(.32,y,.32),cx,1,guide);
            segment(g,new P(.32,y,.32),new P(-.32,y,.32),cx,1,guide);
            segment(g,new P(-.32,y,.32),new P(-.32,y,-.32),cx,1,guide);
        }
        for(Stroke s:geometry(age,1))for(int pass=0;pass<2;pass++) {
            int rgb=s.color;Color c=new Color((rgb>>16)&255,(rgb>>8)&255,rgb&255,(int)(255*s.alpha*(pass==0?.12:.72)));
            segment(g,s.a,s.b,cx,Math.max(.35,s.width*76*2*(pass==0?2.6:1)),c);
        }
        g.setClip(clip);
        g.setFont(new Font("SansSerif",Font.BOLD,20));g.setColor(new Color(205,232,222));g.drawString(heading,left+18,146);
        g.setFont(new Font("SansSerif",Font.PLAIN,15));g.setColor(new Color(139,168,182));
        g.drawString(String.format("tick %.0f / %d  ·  %.2f-block radius",age,LAND,RADIUS),left+18,172);
        g.drawString("同纹上阵 / 底阵 · 中央框为 2 格参照",left+18,624);
    }
    public static void main(String[] args)throws Exception {
        verify();Path file=Path.of(args.length>0?args[0]:"build/qinglong-seal-preview/stages.png");
        BufferedImage img=new BufferedImage(1840,735,BufferedImage.TYPE_INT_RGB);Graphics2D g=img.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON);
        g.setColor(new Color(7,15,25));g.fillRect(0,0,img.getWidth(),img.getHeight());
        g.setColor(new Color(235,221,170));g.setFont(new Font("SansSerif",Font.BOLD,27));g.drawString("青龙封印 / 上下双阵与连接笼形成",30,45);
        g.setColor(new Color(153,174,190));g.setFont(new Font("SansSerif",Font.PLAIN,17));
        g.drawString("PRODUCTION STROKE GEOMETRY · DIAGNOSTIC PROJECTION · NOT A GAMEPLAY SCREENSHOT",30,80);
        panel(g,0,3,"01  双阵逐渐绘成");panel(g,1,8,"02  上下阵完全展开");
        panel(g,2,13,"03  连线由脚下升起");panel(g,3,18,"04  封印闭合，青龙将落");
        g.setFont(new Font("SansSerif",Font.PLAIN,17));g.setColor(new Color(153,174,190));
        g.drawString("0–8 tick：双阵  |  8–18 tick：封印笼  |  18–32 tick：放大青龙下落，鼻尖对准目标中心",30,688);
        g.drawString("Actual runtime line coordinates and phase math. Shading / transparency / world-camera integration are not tested by this image.",30,717);
        g.dispose();if(file.getParent()!=null)Files.createDirectories(file.getParent());ImageIO.write(img,"png",file.toFile());
        System.out.println(file.toAbsolutePath());
    }
}
