import com.dynasty.GuanYuAvatarShape;
import com.dynasty.HouyiAvatarShape.P;
import java.awt.*;
import java.awt.geom.*;
import java.awt.image.BufferedImage;
import java.nio.file.*;
import java.util.List;
import javax.imageio.ImageIO;

/** Original photograph beside the actual sampled extrusion boundary, without generative repainting. */
public final class GuandaoPhotoComparison {
    public static void main(String[] args)throws Exception {
        Path dir=Path.of(args[0]);
        var method=GuanYuAvatarShape.class.getDeclaredMethod("photoOutline");method.setAccessible(true);
        @SuppressWarnings("unchecked") List<P> outline=(List<P>)method.invoke(null);
        Path2D path=new Path2D.Double();boolean first=true;
        for(P q:outline) {
            double x=280+(.4061384661*q.x()-.9138115486*q.y())/.014;
            double y=165+(.9138115486*q.x()+.4061384661*q.y())/.014;
            if(first){path.moveTo(x,y);first=false;}else path.lineTo(x,y);
        }
        path.closePath();
        BufferedImage photo=ImageIO.read(dir.resolve("reference.png").toFile());
        BufferedImage out=new BufferedImage(1680,790,BufferedImage.TYPE_INT_RGB);
        Graphics2D g=out.createGraphics();g.setColor(new Color(238,238,234));g.fillRect(0,0,1680,790);
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON);
        g.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING,RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
        g.setColor(new Color(26,30,33));g.setFont(new Font("SansSerif",Font.BOLD,30));g.drawString("PHOTO TRACE / SAME SCALE / NO OUTLINE REDESIGN",42,60);
        String[] labels={"01  YOUR PHOTO + TRACE OVERLAY","02  NEW MESH OUTLINE / PURE BLACK"};
        for(int i=0;i<2;i++) {
            int ox=42+i*824;
            g.setFont(new Font("SansSerif",Font.BOLD,22));g.setColor(new Color(30,34,39));g.drawString(labels[i],ox,125);
            Graphics2D card=(Graphics2D)g.create();card.translate(ox,167);card.clipRect(0,0,776,435);
            card.setColor(Color.WHITE);card.fillRect(0,0,776,435);card.scale(3.1,3.1);card.translate(-44,-131);
            if(i==0){card.drawImage(photo,0,0,null);card.setColor(new Color(78,255,207));card.setStroke(new BasicStroke(.36f));card.draw(path);}
            else {card.setColor(Color.BLACK);card.fill(path);}
            card.dispose();
        }
        g.setFont(new Font("SansSerif",Font.PLAIN,21));g.setColor(new Color(66,72,76));
        g.drawString("Primary reference: supplied image 3, 474 x 316. Both panels use the identical 3.1x scale.",42,655);
        g.drawString("Visible steel boundary traced manually; hidden heel under the gold socket reconstructed only for fitting.",42,692);
        g.drawString("No dragon relief, gold decoration or final texture is included in the new blade head.",42,729);
        g.dispose();ImageIO.write(out,"png",dir.resolve("comparison.png").toFile());
        BufferedImage black=new BufferedImage(1000,1300,BufferedImage.TYPE_INT_RGB);g=black.createGraphics();
        g.setColor(Color.WHITE);g.fillRect(0,0,1000,1300);g.setColor(Color.BLACK);
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON);
        path=new Path2D.Double();first=true;
        for(P q:outline){double x=500+q.x()*330,y=1160-q.y()*330;if(first){path.moveTo(x,y);first=false;}else path.lineTo(x,y);}path.closePath();g.fill(path);g.dispose();
        ImageIO.write(black,"png",dir.resolve("silhouette.png").toFile());
        System.out.println("Photo and mesh outline comparison exported: "+dir);
    }
}
