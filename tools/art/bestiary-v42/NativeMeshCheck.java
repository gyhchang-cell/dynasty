package com.dynasty.client;

import com.google.gson.*;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.world.entity.Mob;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.zip.GZIPOutputStream;

/** Real native LayerDefinition, ModelPart and animation replay. No window or world. */
public final class NativeMeshCheck {
    private static final class Capture implements VertexConsumer {
        final JsonArray vertices = new JsonArray();
        double x,y,z; float u,v; final float tex,scale;
        Capture(float tex,float scale) {this.tex=tex;this.scale=scale;}
        public VertexConsumer vertex(double x,double y,double z) {this.x=x;this.y=y;this.z=z;return this;}
        public VertexConsumer color(int r,int g,int b,int a) {return this;}
        public VertexConsumer uv(float u,float v) {this.u=u;this.v=v;return this;}
        public VertexConsumer overlayCoords(int u,int v) {return this;}
        public VertexConsumer uv2(int u,int v) {return this;}
        public VertexConsumer normal(float x,float y,float z) {return this;}
        public void endVertex() {
            if (!Double.isFinite(x+y+z+u+v)) throw new AssertionError("non-finite geometry");
            JsonArray a=new JsonArray();a.add(x*16*scale);a.add((24-y*16)*scale);a.add(z*16*scale);a.add(u*tex);a.add(v*tex);vertices.add(a);
        }
        public void defaultColor(int r,int g,int b,int a) {}
        public void unsetDefaultColor() {}
    }
    public static void main(String[] args) throws Exception {
        String[] ids={"jade_guard","soul_soldier","thunder_envoy","merfolk","terracotta_warrior","minister"};
        float[] scales={1.08F,1.05F,1,1,1,1};int[] styles={3,4,8,9,-1,-1};
        LayerDefinition[] layers={RealmCreatureLayers.jade_guard(),RealmCreatureLayers.soul_soldier(),RealmCreatureLayers.thunder_envoy(),RealmCreatureLayers.merfolk(),RealmCreatureLayers.terracotta_warrior(),RealmCreatureLayers.minister()};
        JsonObject output=new JsonObject();
        for(int i=0;i<ids.length;i++) {
            ModelPart root=layers[i].bakeRoot();
            RealmCreatureModel<Mob> model=new RealmCreatureModel<>(root,ids[i]);
            JsonObject poses=new JsonObject();
            for(String state:new String[]{"idle","walk","attack"}) {
                if(ids[i].equals("minister") && state.equals("attack")) continue;
                for(int tick=0;tick<80;tick+=2) {
                    float attack=state.equals("attack")?(tick%20)/20F:0;
                    model.applyPose(attack,tick*.62F,state.equals("walk")?.8F:0,tick,
                            (float)Math.sin(tick*.035)*12,0);
                    Capture capture=new Capture(128,scales[i]);
                    model.renderToBuffer(new PoseStack(),capture,0xF000F0,0,1,1,1,1);
                    if(capture.vertices.size()==0||capture.vertices.size()%24!=0)throw new AssertionError("missing faces");
                    poses.add(state+"@"+tick,capture.vertices);
                }
            }
            // Old layer + actual old atlas; static baseline is labelled static, not fake motion.
            ModelPart old=(styles[i]<0?DynastyHumanoidModel.createBodyLayer():DynastyHumanoidModel.decoratedLayer(styles[i])).bakeRoot();
            int oldTextureSize=javax.imageio.ImageIO.read(Path.of("src/main/resources/assets/dynasty/textures/entity/"+ids[i]+".png").toFile()).getWidth();
            Capture before=new Capture(oldTextureSize,scales[i]);
            old.render(new PoseStack(),before,0xF000F0,0,1,1,1,1);
            poses.add("before",before.vertices);output.add(ids[i],poses);
        }
        Path path=Path.of(args[0]);Files.createDirectories(path.getParent());
        try(Writer w=new OutputStreamWriter(new GZIPOutputStream(Files.newOutputStream(path)),StandardCharsets.UTF_8)) {new Gson().toJson(output,w);}
        System.out.println("PASS: six actual native layers, 680 animated poses and six old-layer baselines; minister has no fabricated attack clip; no window/world/audio");
    }
}
