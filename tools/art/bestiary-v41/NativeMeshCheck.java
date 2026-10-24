package com.dynasty.client;

import com.google.gson.*;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.world.entity.Mob;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.zip.GZIPOutputStream;

/** Bakes the real MC model and captures its actual UV vertices, without a window/world/audio. */
public final class NativeMeshCheck {
    private static final class Capture implements VertexConsumer {
        final JsonArray vertices = new JsonArray();
        double x,y,z; float u,v;
        public VertexConsumer vertex(double x,double y,double z) {this.x=x;this.y=y;this.z=z;return this;}
        public VertexConsumer color(int r,int g,int b,int a) {return this;}
        public VertexConsumer uv(float u,float v) {this.u=u;this.v=v;return this;}
        public VertexConsumer overlayCoords(int u,int v) {return this;}
        public VertexConsumer uv2(int u,int v) {return this;}
        public VertexConsumer normal(float x,float y,float z) {return this;}
        public void endVertex() {
            JsonArray a=new JsonArray();a.add(x*16);a.add(24-y*16);a.add(z*16);a.add(u*128);a.add(v*128);vertices.add(a);
        }
        public void defaultColor(int r,int g,int b,int a) {}
        public void unsetDefaultColor() {}
    }
    public static void main(String[] args) throws Exception {
        JsonObject output=new JsonObject();
        for(boolean bird:new boolean[]{false,true}) {
            String id=bird?"phoenix":"nine_tailed_fox";
            ModelPart root=(bird?BestiarySpiritLayers.phoenix():BestiarySpiritLayers.fox()).bakeRoot();
            BestiarySpiritModel<Mob> model=new BestiarySpiritModel<>(root,bird);
            JsonObject poses=new JsonObject();
            for(String state:bird?new String[]{"idle","walk","fly"}:new String[]{"idle","walk","attack"}) {
                for(int tick=0;tick<80;tick+=2) {
                    float attack=state.equals("attack")?(tick%20)/20F:0;
                    float yaw=(float)(Math.sin(tick*.035)*.13*180/Math.PI);
                    model.applyPose(state.equals("fly"),attack,tick*.62F,state.equals("walk")?.8F:0,tick,yaw,0);
                    Capture capture=new Capture();
                    model.renderToBuffer(new PoseStack(),capture,0xF000F0,0,1,1,1,1);
                    int expected=(bird?34:45)*24;
                    if(capture.vertices.size()!=expected)throw new AssertionError(id+" missing faces: "+capture.vertices.size());
                    poses.add(state+"@"+tick,capture.vertices);
                }
            }
            output.add(id,poses);
        }
        Path file=Path.of(args[0]);Files.createDirectories(file.getParent());
        try(Writer writer=new OutputStreamWriter(new GZIPOutputStream(Files.newOutputStream(file)),StandardCharsets.UTF_8)) {
            new Gson().toJson(output,writer);
        }
        System.out.println("PASS: native layers baked; 240 poses rendered to UV vertices, no window/world/audio.");
    }
}
