import java.nio.file.*;import com.google.gson.*;import com.mojang.serialization.JsonOps;import net.minecraft.client.renderer.texture.atlas.SpriteSources;import net.minecraft.client.renderer.block.model.BlockModel;
public class VerifyTiledOriginals {
 public static void main(String[] args)throws Exception {
  var atlas=JsonParser.parseString(Files.readString(Path.of("src/main/resources/assets/minecraft/atlases/blocks.json")));
  var sources=SpriteSources.FILE_CODEC.parse(JsonOps.INSTANCE,atlas).getOrThrow(false,s->{throw new AssertionError(s);});int elements=0,models=0;
  for(var entry:atlas.getAsJsonObject().getAsJsonArray("sources")){var obj=entry.getAsJsonObject();if(!obj.has("resource"))continue;String id=obj.get("resource").getAsString().replace("dynasty:item/","");var m=BlockModel.fromString(Files.readString(Path.of("src/main/resources/assets/dynasty/models/item/"+id+".json")));if(m.getElements().isEmpty())throw new AssertionError(id);elements+=m.getElements().size();models++;for(var e:m.getElements())for(var f:e.faces.values())for(float uv:f.uv.uvs)if(uv<0||uv>16.001f)throw new AssertionError(id+" invalid UV "+uv);}
  System.out.println("PASS Minecraft atlas codec: "+sources.size()+" sources; BlockModel parser: "+models+" models, "+elements+" elements, all UVs bounded. No graphical client.");
 }
}
