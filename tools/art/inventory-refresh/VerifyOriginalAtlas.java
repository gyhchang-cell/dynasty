import net.minecraft.client.renderer.texture.Stitcher;
import net.minecraft.resources.ResourceLocation;
import java.nio.file.*;
public class VerifyOriginalAtlas {
 record Sprite(int width,int height,ResourceLocation name) implements Stitcher.Entry {}
 public static void main(String[] args)throws Exception {
  Stitcher<Sprite> s=new Stitcher<>(16384,16384,0);int count=0;
  for(String line:Files.readAllLines(Path.of(args[0]))) {
   String[] p=line.split("\\t");s.registerSprite(new Sprite(Integer.parseInt(p[1]),Integer.parseInt(p[2]),new ResourceLocation(p[0])));count++;
  }
  s.stitch();System.out.println("PASS "+count+" sprites: "+s.getWidth()+" x "+s.getHeight()+" at mip0; CPU packing only, not a GPU/client test");
 }
}
