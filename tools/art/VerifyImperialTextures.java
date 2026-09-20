import javax.imageio.ImageIO;
import java.nio.file.*;
public class VerifyImperialTextures {
    public static void main(String[] args)throws Exception {
        for(String id:new String[]{"tianzi_sword","qinglong_dao"}) {
            var image=ImageIO.read(Path.of(args[0],id+".png").toFile());
            if(image.getWidth()!=128||image.getHeight()!=128||!image.getColorModel().hasAlpha())throw new AssertionError("Invalid PNG format");
            int minX=128,minY=128,maxX=-1,maxY=-1,count=0;
            for(int y=0;y<128;y++)for(int x=0;x<128;x++)if((image.getRGB(x,y)>>>24)>16) {
                minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);count++;
            }
            if(minX<1||minY<1||maxX>126||maxY>126||maxX-minX+1<116||maxY-minY+1<116)throw new AssertionError("Poor slot fit: "+id);
            if(count>128*128*.6)throw new AssertionError("Background may be opaque");
            System.out.println(id+": 128x128 RGBA, silhouette "+(maxX-minX+1)+"x"+(maxY-minY+1)+", border "+minX+","+minY);
        }
    }
}
