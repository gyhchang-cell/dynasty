import java.awt.*;
import java.awt.image.BufferedImage;
import java.nio.file.*;
import javax.imageio.ImageIO;

/** Mechanical asset integration only: crops AI-created artwork into existing Minecraft UV islands. */
public final class PackRemasterAssets {
    private static BufferedImage source,target;
    private static Graphics2D graphics;
    private static void region(int u,int v,int w,int h,int x,int y,int sw,int sh) {
        int sx=(int)Math.round(x*source.getWidth()/1280.0),sy=(int)Math.round(y*source.getHeight()/1280.0);
        int ex=(int)Math.round((x+sw)*source.getWidth()/1280.0),ey=(int)Math.round((y+sh)*source.getHeight()/1280.0);
        graphics.drawImage(source,u*4,v*4,(u+w)*4,(v+h)*4,sx,sy,ex,ey,null);
    }
    private static void box(int u,int v,int w,int h,int d,int[] front,int[] side,int[] top) {
        region(u+d,v,w,d,top[0],top[1],top[2],top[3]);
        region(u+d+w,v,w,d,top[0],top[1],top[2],top[3]);
        region(u,v+d,d,h,side[0],side[1],side[2],side[3]);
        region(u+d,v+d,w,h,front[0],front[1],front[2],front[3]);
        region(u+d+w,v+d,d,h,side[0],side[1],side[2],side[3]);
        region(u+d+w+d,v+d,w,h,side[0],side[1],side[2],side[3]);
    }
    public static void main(String[] args)throws Exception {
        source=ImageIO.read(Path.of(args[1]).toFile());
        if(source==null)throw new IllegalArgumentException("Invalid PNG");
        if(args[0].equals("skin")) {
            target=new BufferedImage(256,256,BufferedImage.TYPE_INT_ARGB);graphics=target.createGraphics();
            graphics.setRenderingHint(RenderingHints.KEY_INTERPOLATION,RenderingHints.VALUE_INTERPOLATION_NEAREST_NEIGHBOR);
            box(0,0,8,8,8,new int[]{120,155,217,182},new int[]{344,165,173,168},new int[]{540,8,170,135});
            // WEST walks back -> front in Minecraft's cube UVs; EAST walks front -> back.
            // Mirror the side artwork only for WEST, keeping both ears toward the face.
            int sx=(int)Math.round(344*source.getWidth()/1280.0),ex=(int)Math.round(517*source.getWidth()/1280.0);
            int sy=(int)Math.round(165*source.getHeight()/1280.0),ey=(int)Math.round(333*source.getHeight()/1280.0);
            graphics.drawImage(source,0,32,32,64,ex,sy,sx,ey,null);
            // The back is hair/helmet, not a third copy of an ear.
            region(24,8,8,8,540,165,173,168);
            box(16,16,8,12,4,new int[]{368,463,259,379},new int[]{639,468,112,373},new int[]{371,354,248,88});
            box(40,16,4,12,4,new int[]{780,465,182,367},new int[]{985,465,103,367},new int[]{780,350,183,91});
            box(0,16,4,12,4,new int[]{368,881,116,312},new int[]{532,881,103,312},new int[]{371,758,112,72});
            // Modern left limb islands are supplied as well for future model variants.
            box(32,48,4,12,4,new int[]{780,465,182,367},new int[]{985,465,103,367},new int[]{780,350,183,91});
            box(16,48,4,12,4,new int[]{532,881,103,312},new int[]{368,881,116,312},new int[]{371,758,112,72});
        } else if(args[0].equals("block")) {
            // These registered solid cube faces use opaque RGB; transparent mortar gaps
            // in generated source art resolve to black recesses, not holes in terrain.
            target=new BufferedImage(128,128,BufferedImage.TYPE_INT_RGB);graphics=target.createGraphics();
            // Pale marble's generated translucent grain needs its intended white substrate.
            if(Path.of(args[1]).getFileName().toString().equals("marble_block.png")) {
                graphics.setColor(Color.WHITE);graphics.fillRect(0,0,128,128);
            }
            graphics.setRenderingHint(RenderingHints.KEY_INTERPOLATION,RenderingHints.VALUE_INTERPOLATION_NEAREST_NEIGHBOR);
            graphics.drawImage(source,0,0,128,128,null);
            for(int y=0;y<128;y++)for(int x=0;x<128;x++)
                if((target.getRGB(x,y)>>>24)<250)throw new IllegalStateException("Block face must be opaque: "+args[1]);
        } else if(args[0].equals("item")) {
            int minX=source.getWidth(),minY=source.getHeight(),maxX=-1,maxY=-1;
            int clear=0;
            for(int y=0;y<source.getHeight();y++)for(int x=0;x<source.getWidth();x++) {
                int alpha=source.getRGB(x,y)>>>24;
                if(alpha>24){minX=Math.min(minX,x);minY=Math.min(minY,y);maxX=Math.max(maxX,x);maxY=Math.max(maxY,y);}else clear++;
            }
            if(clear<source.getWidth()*source.getHeight()/20||maxX<0)throw new IllegalStateException("Real transparent background required");
            int w=maxX-minX+1,h=maxY-minY+1;double fit=120.0/Math.max(w,h);
            int dw=(int)Math.round(w*fit),dh=(int)Math.round(h*fit),x=(128-dw)/2,y=(128-dh)/2;
            target=new BufferedImage(128,128,BufferedImage.TYPE_INT_ARGB);graphics=target.createGraphics();
            graphics.setRenderingHint(RenderingHints.KEY_INTERPOLATION,RenderingHints.VALUE_INTERPOLATION_NEAREST_NEIGHBOR);
            graphics.drawImage(source,x,y,x+dw,y+dh,minX,minY,maxX+1,maxY+1,null);
            System.out.printf("Item extent: %dx%d /128, source clear pixels %d%n",dw,dh,clear);
        } else throw new IllegalArgumentException("skin, block or item");
        graphics.dispose();Path out=Path.of(args[2]);Files.createDirectories(out.getParent());ImageIO.write(target,"png",out.toFile());
        System.out.println(out.toAbsolutePath());
    }
}
