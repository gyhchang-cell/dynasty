import com.dynasty.structure.megabuild.*;
import java.awt.*;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.File;
/** Direct voxel projection for geometry QA, not a Minecraft screenshot. */
public class RenderPlan {
    public static void main(String[] args)throws Exception{
        render(new TiangongCitadel(0).blueprint(),args[0]+"/citadel.png");
        render(new MiningEstate(0).blueprint(),args[0]+"/estate.png");
    }
    static Color color(Blueprint.Kind k){
        return switch(k){
            case AIR,LIGHT->new Color(0,0,0,0);
            case PLATFORM->new Color(75,82,86);
            case WALL->new Color(156,153,140);
            case FLOOR->new Color(181,169,147);
            case ROOF->new Color(32,99,94);
            case RED_WOOD->new Color(132,50,44);
            case WATER->new Color(56,115,160);
            case CROP->new Color(56,107,63);
            case DARK_WOOD,WOOD->new Color(98,55,37);
            case LANTERN,COPPER->new Color(231,161,62);
            case CHEST,RICH_CHEST,BARREL->new Color(165,110,47);
            default->new Color(83,102,114);
        };
    }
    static void render(Blueprint b,String file)throws Exception{
        int s=4,cx=b.sizeX*s+20;
        var img=new BufferedImage(b.sizeX*s*2+40,b.sizeZ*s+b.sizeY*s+60,BufferedImage.TYPE_INT_RGB);
        var g=img.createGraphics();g.setColor(new Color(28,38,46));g.fillRect(0,0,img.getWidth(),img.getHeight());
        for(int sum=0;sum<b.sizeX+b.sizeZ;sum++)for(int x=0;x<b.sizeX;x++){
            int z=sum-x;if(z<0||z>=b.sizeZ)continue;
            for(int y=0;y<b.sizeY;y++){
                var k=b.at(x,y,z);if(Blueprint.empty(k))continue;
                int px=cx+(x-z)*s,py=30+b.sizeY*s+(x+z)*s/2-y*s;
                Color c=color(k);
                if(Blueprint.empty(b.at(x+1,y,z))){g.setColor(c.darker());g.fillPolygon(new int[]{px,px+s,px+s,px},new int[]{py,py+s/2,py+s/2+s,py+s},4);}
                if(Blueprint.empty(b.at(x,y,z+1))){g.setColor(c.darker().darker());g.fillPolygon(new int[]{px,px-s,px-s,px},new int[]{py,py+s/2,py+s/2+s,py+s},4);}
                if(Blueprint.empty(b.at(x,y+1,z))){g.setColor(c);g.fillPolygon(new int[]{px,px+s,px,px-s},new int[]{py-s/2,py,py+s/2,py},4);}
            }
        }
        g.dispose();ImageIO.write(img,"png",new File(file));
    }
}
