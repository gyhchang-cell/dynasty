import com.mojang.blaze3d.platform.NativeImage;
import net.minecraft.client.renderer.texture.Stitcher;
import net.minecraft.resources.ResourceLocation;
import java.nio.file.*;
public class VerifyStatusIcons {
 record Sprite(int width,int height,ResourceLocation name) implements Stitcher.Entry {}
 public static void main(String[] args)throws Exception {
  Stitcher<Sprite> s=new Stitcher<>(16384,16384,0);int count=0,pngs=0;
  for(String line:Files.readAllLines(Path.of(args[0]))) {
   String[] p=line.split("\t");int w=Integer.parseInt(p[1]),h=Integer.parseInt(p[2]);
   if(p.length==4){try(var in=Files.newInputStream(Path.of(p[3]));NativeImage im=NativeImage.read(in)){
    if(im.getWidth()!=w||im.getHeight()!=h)throw new AssertionError(p[0]);pngs++;
   }}
   s.registerSprite(new Sprite(w,h,new ResourceLocation(p[0])));count++;
  }
  s.stitch();System.out.println("PASS NativeImage decoded "+pngs+" original PNGs; native Stitcher packed "+count+" vanilla+Dynasty effects at "+s.getWidth()+"x"+s.getHeight()+" mip0. CPU only, not a graphical game test.");
 }
}
