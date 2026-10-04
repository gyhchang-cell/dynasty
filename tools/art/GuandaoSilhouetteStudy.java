import java.awt.*;
import java.awt.geom.*;
import java.awt.image.BufferedImage;
import java.nio.file.*;
import javax.imageio.ImageIO;

/** 2D design first: cubic boundaries, no materials or 3D mesh involved. */
public class GuandaoSilhouetteStudy {
    public static final double[][] BACK={{.14,0},{.14,.55},{.14,1.10},{.14,1.65},{.14,2.20},{-.80,2.85},{-1.68,3.30}};
    public static final double[][] EDGE={{-.14,0},{-.14,.45},{-.16,.62},{-.46,.78},{-1.22,1.05},{-1.83,1.25},{-1.78,1.80},{-1.75,2.30},{-1.36,2.77},{-1.68,3.30}};
    public static void main(String[] args)throws Exception {
        BufferedImage image=new BufferedImage(1100,1500,BufferedImage.TYPE_INT_RGB);
        Graphics2D g=image.createGraphics();g.setColor(Color.WHITE);g.fillRect(0,0,1100,1500);
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON);
        Path2D shape=new Path2D.Double();shape.moveTo(BACK[0][0],BACK[0][1]);
        for(int i=1;i<BACK.length;i+=3)shape.curveTo(BACK[i][0],BACK[i][1],BACK[i+1][0],BACK[i+1][1],BACK[i+2][0],BACK[i+2][1]);
        for(int i=EDGE.length-2;i>=2;i-=3)shape.curveTo(EDGE[i][0],EDGE[i][1],EDGE[i-1][0],EDGE[i-1][1],EDGE[i-2][0],EDGE[i-2][1]);
        shape.closePath();g.translate(875,1365);g.scale(365,-365);g.setColor(Color.BLACK);g.fill(shape);g.dispose();
        Path out=Path.of(args[0]);Files.createDirectories(out.getParent());ImageIO.write(image,"png",out.toFile());
    }
}
