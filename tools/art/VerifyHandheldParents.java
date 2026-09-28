import java.nio.file.*;
import java.util.*;
import net.minecraft.client.renderer.block.model.BlockModel;
import net.minecraft.resources.ResourceLocation;

/** Exercise Minecraft's actual BlockModel parent resolver, not just a JSON viewer. */
public final class VerifyHandheldParents {
    public static void main(String[] args) throws Exception {
        Path directory=Path.of("src/main/resources/assets/dynasty/models/item");
        var models=new HashMap<ResourceLocation,BlockModel>();
        try(var files=Files.list(directory)) {
            for(Path p:files.filter(p->p.toString().endsWith(".json")).toList()) {
                String json=Files.readString(p);
                if(!json.contains("dynasty_solid_edges")&&!json.contains("dynasty:item/solid_bow")&&!p.getFileName().toString().startsWith("solid_"))continue;
                String name=p.getFileName().toString().replace(".json","");
                BlockModel model=BlockModel.fromString(json);model.name=name;
                models.put(new ResourceLocation("dynasty","item/"+name),model);
            }
        }
        BlockModel root=models.get(new ResourceLocation("dynasty","item/solid_handheld"));
        if(root==null)throw new AssertionError("Concrete root missing");
        for(var entry:models.entrySet()) {
            BlockModel model=entry.getValue();
            model.resolveParents(id->{
                var parent=models.get(id);
                if(parent==null)throw new AssertionError("Unexpected parent/override: "+id);
                return parent;
            });
            if(model.getRootModel()!=root)throw new AssertionError("Wrong bake root "+entry.getKey());
            if(model!=root&&!model.name.equals("solid_bow")&&model.getElements().size()<2)throw new AssertionError("Missing explicit mesh");
        }
        System.out.println("PASS: Minecraft BlockModel resolved "+(models.size()-2)+" weapon models to concrete mesh root; no generated-item ancestor.");
    }
}
