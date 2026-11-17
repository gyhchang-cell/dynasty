import com.google.gson.*;
import software.bernie.geckolib.cache.object.*;
import software.bernie.geckolib.loading.json.raw.Model;
import software.bernie.geckolib.loading.object.*;
import software.bernie.geckolib.util.JsonUtil;
import java.nio.file.*;
import javax.imageio.ImageIO;

/** Actual installed GeckoLib4.8.4 parser and mesh factory. No window or world. */
public final class NativeKiteCheck {
    private static int bones, cubes, quads;
    private static void inspect(GeoBone bone, JsonArray meshes) {
        bones++;
        for (GeoCube cube : bone.getCubes()) {
            cubes++;
            for (GeoQuad quad : cube.quads()) {
                if (quad == null) continue;
                quads++;
                JsonObject face = new JsonObject();
                face.addProperty("bone", bone.getName());
                face.addProperty("direction", quad.direction().toString());
                JsonArray vertices = new JsonArray();
                for (GeoVertex vertex : quad.vertices()) {
                    if (!Float.isFinite(vertex.position().x()+vertex.position().y()+vertex.position().z()) ||
                            !Float.isFinite(vertex.texU() + vertex.texV()) ||
                            vertex.texU() < 0 || vertex.texU() > 1 ||
                            vertex.texV() < 0 || vertex.texV() > 1)
                        throw new AssertionError("Invalid native UV");
                    JsonArray v = new JsonArray();
                    v.add(vertex.position().x()); v.add(vertex.position().y());
                    v.add(vertex.position().z()); v.add(vertex.texU()*512);
                    v.add(vertex.texV()*512); vertices.add(v);
                }
                face.add("vertices", vertices); meshes.add(face);
            }
        }
        for (GeoBone child : bone.getChildBones()) inspect(child, meshes);
    }
    public static void main(String[] args) throws Exception {
        Path root = Path.of(args[0]);
        Path assets = root.resolve("src/main/resources/assets/dynasty");
        JsonObject report = new JsonObject();
        for (String id : new String[]{"luban_yisha", "luban_yisha_metal"}) {
            Model raw;
            try (var reader = Files.newBufferedReader(assets.resolve("geo/blueprint/boss/"+id+".geo.json"))) {
                raw = JsonUtil.GEO_GSON.fromJson(reader, Model.class);
            }
            BakedGeoModel model = new BakedModelFactory.Builtin().constructGeoModel(GeometryTree.fromModel(raw));
            BakedAnimations animations;
            try (var reader = Files.newBufferedReader(assets.resolve("animations/blueprint/boss/"+id+".animation.json"))) {
                // FileLoader passes the inner animations object to this adapter.
                JsonObject channels=JsonParser.parseReader(reader).getAsJsonObject().getAsJsonObject("animations");
                animations = JsonUtil.GEO_GSON.fromJson(channels, BakedAnimations.class);
            }
            if (animations.animations().size()!=12) throw new AssertionError("Missing existing clips: "+animations.animations().size());
            var image = ImageIO.read(assets.resolve("textures/entity/blueprint/boss/"+id+".png").toFile());
            if (image.getWidth()!=512 || image.getHeight()!=512) throw new AssertionError("PNG mismatch");
            JsonArray mesh = new JsonArray(); bones=cubes=quads=0;
            for (GeoBone bone : model.topLevelBones()) inspect(bone, mesh);
            int expected = id.endsWith("_metal") ? 136 : 172;
            if (bones!=73 || cubes!=expected || quads!=expected*6) throw new AssertionError("Mesh count mismatch");
            JsonObject row = new JsonObject();
            row.addProperty("bones",bones); row.addProperty("cubes",cubes);
            row.addProperty("quads",quads); row.addProperty("actualGeckoLibVersion","4.8.4");
            row.addProperty("parsedAnimationClips",animations.animations().size());
            row.addProperty("nativeGameOrRenderTest",false); row.add("bakedFaces",mesh);
            report.add(id,row);
            System.out.println("PASS actual GeckoLib bake: "+id+" / "+bones+" bones / "+cubes+" cubes / "+quads+" quads");
        }
        Path out=Path.of(args[1]); Files.createDirectories(out.getParent());
        Files.writeString(out,new GsonBuilder().setPrettyPrinting().create().toJson(report)+"\n");
    }
}
