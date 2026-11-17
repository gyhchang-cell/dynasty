import java.nio.file.*;
import com.google.gson.*;
import com.mojang.serialization.JsonOps;
import com.mojang.blaze3d.platform.NativeImage;
import net.minecraft.client.renderer.texture.SpriteContents;
import net.minecraft.client.resources.metadata.animation.*;
import net.minecraft.client.renderer.block.model.ItemModelGenerator;
import net.minecraft.client.resources.model.BlockModelRotation;
import net.minecraft.client.renderer.texture.atlas.SpriteSources;
import net.minecraft.resources.ResourceLocation;

/** Exercises Minecraft's PNG decoder, item extrusion, source UVs and atlas codec without a window. */
public class VerifyV28Originals {
    public static void main(String[] args) throws Exception {
        var doc=Path.of("docs/art/armor-foundations-v28");
        var rows=JsonParser.parseString(Files.readString(doc.resolve("selection.json"))).getAsJsonArray();
        var atlas=JsonParser.parseString(Files.readString(Path.of("src/main/resources/assets/minecraft/atlases/blocks.json")));
        var sources=SpriteSources.FILE_CODEC.parse(JsonOps.INSTANCE,atlas).getOrThrow(false,s->{throw new AssertionError(s);});
        if(sources.isEmpty()) throw new AssertionError("Missing atlas sources");
        int count=0,faces=0;
        long start=System.nanoTime();
        for(var entry:rows) {
            String id=entry.getAsJsonObject().get("id").getAsString();
            var texture=new ResourceLocation("dynasty","textures/item/"+id+".png");
            try(var input=Files.newInputStream(Path.of("src/main/resources/assets/dynasty/textures/item/"+id+".png"))) {
                NativeImage image=NativeImage.read(input);
                try(var contents=new SpriteContents(texture,new FrameSize(image.getWidth(),image.getHeight()),image,AnimationMetadataSection.EMPTY,null)) {
                    var model=JsonParser.parseString(Files.readString(Path.of("src/main/resources/assets/dynasty/models/item/"+id+".json"))).getAsJsonObject();
                    if(!model.get("loader").getAsString().equals("dynasty:original_item"))throw new AssertionError("wrong loader");
                    for(String hand:java.util.List.of("firstperson_righthand","thirdperson_righthand"))if(!model.getAsJsonObject("display").has(hand))throw new AssertionError("Missing hand transform "+hand);
                    int tint=model.has("tint_index")?model.get("tint_index").getAsInt():-1;
                    boolean potion=java.util.Set.of("dynasty_potion","dynasty_splash_potion","dynasty_lingering_potion").contains(id);
                    if(tint!=(potion?0:-1))throw new AssertionError(id+": wrong tint index");
                    var elements=new ItemModelGenerator().processFrames(tint,"layer0",contents);
                    if(elements.size()<5) throw new AssertionError(id+": missing extrusion");
                    for(var element:elements)for(var face:element.faces.values()) {
                        if(face.tintIndex!=tint)throw new AssertionError(id+": lost face tint");
                        for(float uv:face.uv.uvs)if(!Float.isFinite(uv)||uv<0||uv>16)throw new AssertionError(id+": UV "+uv);
                        faces++;
                    }
                }
                count++;
                if(count%25==0)System.out.println("Baked "+count+" originals");
            }
        }
        System.out.println("PASS "+count+" original PNGs, "+faces+" native extruded faces, bounded source UVs; atlas codec accepted; seconds="+((System.nanoTime()-start)/1e9));
        System.out.println("Headless native resource/model test only; no graphical or live-world acceptance.");
    }
}
