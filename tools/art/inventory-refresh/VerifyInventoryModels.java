import java.nio.file.*;
import java.util.*;
import java.util.zip.*;
import net.minecraft.client.renderer.block.model.BlockModel;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemDisplayContext;
public class VerifyInventoryModels {
 public static void main(String[] args)throws Exception{
  Path root=Path.of("src/main/resources/assets/dynasty/models");
  var models=new HashMap<ResourceLocation,BlockModel>();
  try(var zip=new ZipFile(args[0])){
   var entry=zip.getEntry("assets/minecraft/models/block/block.json");
   models.put(new ResourceLocation("minecraft","block/block"),BlockModel.fromString(new String(zip.getInputStream(entry).readAllBytes(),java.nio.charset.StandardCharsets.UTF_8)));
  }
  String[] ids={"old_bellows","broken_waterwheel","broken_waterwheel_repaired","old_weapon_rack","abandoned_armory","puzzle_box","wayside_shrine","nameless_tomb","sword_scar_wall","broken_stele","battlefield_remnant","herb_spot","mortuary_room","ghost_market_boat","wayside_tea_stall","wayside_tea_stall_overturned","ancient_well"};
  int cubes=0;
  for(String id:ids){var m=BlockModel.fromString(Files.readString(root.resolve("block/"+id+".json")));m.name=id;models.put(new ResourceLocation("dynasty","block/"+id),m);cubes+=m.getElements().size();}
  for(String id:ids){var m=models.get(new ResourceLocation("dynasty","block/"+id));m.resolveParents(models::get);if(m.getTransforms().getTransform(ItemDisplayContext.GUI).rotation.lengthSquared()==0)throw new AssertionError("flat GUI: "+id);}
  for(String id:ids){if(id.endsWith("_repaired")||id.endsWith("_overturned"))continue;var m=BlockModel.fromString(Files.readString(root.resolve("item/"+id+".json")));m.resolveParents(models::get);if(m.getElements().isEmpty())throw new AssertionError("Empty item: "+id);}
  System.out.println("PASS actual Minecraft BlockModel parser/parent resolver: 17 site variants, 15 item parents, "+cubes+" cuboids, inherited 3D GUI transforms. No graphical client launched.");
 }
}
