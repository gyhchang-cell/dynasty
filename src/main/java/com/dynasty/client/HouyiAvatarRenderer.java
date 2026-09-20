package com.dynasty.client;

import com.dynasty.HouyiAvatarShape;
import com.dynasty.HouyiAvatarShape.P;
import com.dynasty.HouyiAvatarShape.Face;
import com.dynasty.HouyiAvatarShape.Material;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.BufferUploader;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.mojang.blaze3d.vertex.VertexBuffer;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.client.Minecraft;
import net.minecraft.core.BlockPos;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import java.util.Arrays;
import java.util.Comparator;

/** Shaded curved surfaces rendered independently from the additive magic circles. */
public final class HouyiAvatarRenderer {
    private static final BufferBuilder BUFFER = new BufferBuilder(1048576);
    private static final P LIGHT = new P(-0.45,0.8,0.6).unit();
    private static VertexBuffer guardianBuffer;

    static void invalidateGuardianBuffer() {
        if(guardianBuffer==null)return;
        if(!RenderSystem.isOnRenderThread()) {RenderSystem.recordRenderCall(HouyiAvatarRenderer::invalidateGuardianBuffer);return;}
        guardianBuffer.close();guardianBuffer=null;
    }

    public static void draw(Matrix4f matrix, Vec3 origin, float yaw, double formed) {
        Vec3 aim=HouyiAvatarShape.forward(yaw);
        Vec3 zAxis=aim.cross(new Vec3(0,1,0)), xAxis=aim.scale(-1);
        drawMesh(matrix,origin,xAxis,zAxis,formed,10,HouyiAvatarShape.MESH);
    }

    public static void drawGuanYu(Matrix4f matrix,Vec3 origin,float yaw,double formed) {
        if(formed<=0)return;
        Vec3 forward=HouyiAvatarShape.forward(yaw);
        Vec3 right=new Vec3(forward.z,0,-forward.x);
        drawSolidGuardian(matrix,origin,right,forward,Math.min(1,formed));
    }

    private static final class GuardianNormals {
        static final java.util.List<PreparedFace> FACES=prepare();
        private static java.util.List<PreparedFace> prepare() {
            var mesh=com.dynasty.GuanYuAvatarShape.MESH;
            var normals=ImperialMeshNormals.build(mesh.stream().map(f->new ImperialMeshNormals.Quad(
                    point(f.a()),point(f.b()),point(f.c()),point(f.d()),f.material().ordinal())).toList());
            var prepared=new java.util.ArrayList<PreparedFace>(mesh.size());
            for(int i=0;i<mesh.size();i++) {
                Face f=mesh.get(i);var n=normals.get(i);
                prepared.add(new PreparedFace(new LitVertex(f.a(),n.a()),new LitVertex(f.b(),n.b()),
                        new LitVertex(f.c(),n.c()),new LitVertex(f.d(),n.d()),f.material(),
                        Math.min(Math.min(f.a().y(),f.b().y()),Math.min(f.c().y(),f.d().y())),
                        Math.max(Math.max(f.a().y(),f.b().y()),Math.max(f.c().y(),f.d().y()))));
            }
            return java.util.List.copyOf(prepared);
        }
    }
    private record LitVertex(P position,ImperialMeshNormals.Point normal) {}
    private record PreparedFace(LitVertex a,LitVertex b,LitVertex c,LitVertex d,Material material,double minY,double maxY) {}
    private static ImperialMeshNormals.Point point(P p){return new ImperialMeshNormals.Point(p.x(),p.y(),p.z());}

    /** Unlike the archer apparition, Guan Yu has solid armor: nearer surfaces hide internal geometry. */
    private static void drawSolidGuardian(Matrix4f matrix,Vec3 origin,Vec3 xAxis,Vec3 zAxis,double formed) {
        try(ImperialRenderState state=new ImperialRenderState()) {
            RenderSystem.enableDepthTest();
            RenderSystem.depthMask(true);
            RenderSystem.disableBlend();
            RenderSystem.disableCull();
            if(formed>=1) {
                Matrix4f worldFromLocal=new Matrix4f().m00((float)xAxis.x).m02((float)xAxis.z)
                        .m20((float)zAxis.x).m22((float)zAxis.z)
                        .m30((float)origin.x).m31((float)origin.y).m32((float)origin.z);
                if(ImperialMaterialShader.bindGuardianLocal(worldFromLocal,sceneLight(origin))) {
                    if(guardianBuffer==null||guardianBuffer.isInvalid())uploadGuardian();
                    guardianBuffer.bind();
                    try {
                        guardianBuffer.drawWithShader(new Matrix4f(RenderSystem.getModelViewMatrix()).mul(matrix).mul(worldFromLocal),
                                RenderSystem.getProjectionMatrix(),RenderSystem.getShader());
                    } finally {VertexBuffer.unbind();}
                    return;
                }
            }
            boolean shader=ImperialMaterialShader.bindGuardian(matrix,origin,xAxis,zAxis,sceneLight(origin));
            if(!shader)RenderSystem.setShader(GameRenderer::getPositionColorShader);
            BUFFER.begin(VertexFormat.Mode.TRIANGLES,shader?DefaultVertexFormat.POSITION_COLOR_NORMAL:DefaultVertexFormat.POSITION_COLOR);
            LitVertex[] input=new LitVertex[4],output=new LitVertex[8];
            double formationHeight=com.dynasty.GuanYuAvatarShape.HEIGHT*formed;
            for(PreparedFace face:GuardianNormals.FACES) {
                if(face.minY>formationHeight)continue;
                // Stable fully formed vertices are cached. Only the tiny set straddling the reveal
                // plane allocates interpolated vertices; no 260,000 temporary packets every frame.
                if(face.maxY<=formationHeight) {
                    solidVertex(matrix,origin,xAxis,zAxis,face.a,face.material,formed,shader);
                    solidVertex(matrix,origin,xAxis,zAxis,face.b,face.material,formed,shader);
                    solidVertex(matrix,origin,xAxis,zAxis,face.c,face.material,formed,shader);
                    solidVertex(matrix,origin,xAxis,zAxis,face.a,face.material,formed,shader);
                    solidVertex(matrix,origin,xAxis,zAxis,face.c,face.material,formed,shader);
                    solidVertex(matrix,origin,xAxis,zAxis,face.d,face.material,formed,shader);
                    continue;
                }
                input[0]=face.a;input[1]=face.b;input[2]=face.c;input[3]=face.d;
                int count=clipLit(input,output,formationHeight);
                if(count<3)continue;
                for(int i=1;i<count-1;i++) {
                    solidVertex(matrix,origin,xAxis,zAxis,output[0],face.material,formed,shader);
                    solidVertex(matrix,origin,xAxis,zAxis,output[i],face.material,formed,shader);
                    solidVertex(matrix,origin,xAxis,zAxis,output[i+1],face.material,formed,shader);
                }
            }
            BufferUploader.drawWithShader(BUFFER.end());
        }
    }
    private static void uploadGuardian() {
        BUFFER.begin(VertexFormat.Mode.TRIANGLES,DefaultVertexFormat.POSITION_COLOR_NORMAL);
        for(PreparedFace face:GuardianNormals.FACES) {
            localVertex(face.a,face.material);localVertex(face.b,face.material);localVertex(face.c,face.material);
            localVertex(face.a,face.material);localVertex(face.c,face.material);localVertex(face.d,face.material);
        }
        guardianBuffer=new VertexBuffer(VertexBuffer.Usage.STATIC);
        guardianBuffer.bind();
        try {guardianBuffer.upload(BUFFER.end());}finally {VertexBuffer.unbind();}
    }
    private static void localVertex(LitVertex vertex,Material material) {
        var p=vertex.position;var n=vertex.normal;
        BUFFER.vertex(p.x(),p.y(),p.z()).color(material.r,material.g,material.b,1)
                .normal((float)n.x(),(float)n.y(),(float)n.z()).endVertex();
    }
    static float sceneLight(Vec3 cameraRelativeOrigin) {
        Minecraft mc=Minecraft.getInstance();
        if(mc.level==null)return 1;
        Vec3 world=cameraRelativeOrigin.add(mc.gameRenderer.getMainCamera().getPosition());
        return .38f+.62f*mc.level.getMaxLocalRawBrightness(BlockPos.containing(world))/15f;
    }
    private static int clipLit(LitVertex[] in,LitVertex[] out,double height) {
        int count=0;
        for(int i=0;i<4;i++) {
            LitVertex a=in[i],b=in[(i+1)%4];
            boolean inside=a.position.y()<=height,next=b.position.y()<=height;
            if(inside)out[count++]=a;
            if(inside!=next) {
                double t=(height-a.position.y())/(b.position.y()-a.position.y());
                out[count++]=new LitVertex(a.position.add(b.position.sub(a.position).scale(t)),
                        a.normal.scale(1-t).add(b.normal.scale(t)).unit());
            }
        }
        return count;
    }
    private static void solidVertex(Matrix4f matrix,Vec3 origin,Vec3 xAxis,Vec3 zAxis,LitVertex vertex,
                                    Material material,double formed,boolean shader) {
        P p=vertex.position;
        var normal=vertex.normal;
        float nx=(float)(xAxis.x*normal.x()+zAxis.x*normal.z());
        float ny=(float)normal.y();
        float nz=(float)(xAxis.z*normal.x()+zAxis.z*normal.z());
        float shade=shader?1:(float)(.35+.65*Math.max(0,nx*LIGHT.x()+ny*LIGHT.y()+nz*LIGHT.z()));
        BUFFER.vertex(matrix,(float)(origin.x+xAxis.x*p.x()+zAxis.x*p.z()),(float)(origin.y+p.y()),
                        (float)(origin.z+xAxis.z*p.x()+zAxis.z*p.z()))
                .color(material.r*shade,material.g*shade,material.b*shade,(float)Math.min(1,formed*8));
        if(shader)BUFFER.normal(nx,ny,nz);
        BUFFER.endVertex();
    }

    private static void drawMesh(Matrix4f matrix,Vec3 origin,Vec3 xAxis,Vec3 zAxis,double formed,double height,java.util.List<Face> mesh) {
        P view=new P(-origin.dot(xAxis),-origin.y,-origin.dot(zAxis)).unit();
        Face[] faces=mesh.toArray(Face[]::new);
        Arrays.sort(faces,Comparator.comparingDouble(face -> face.center().dot(view)));
        RenderSystem.enableBlend();
        RenderSystem.defaultBlendFunc();
        RenderSystem.enableDepthTest();
        RenderSystem.depthMask(false);
        RenderSystem.disableCull();
        RenderSystem.setShader(GameRenderer::getPositionColorShader);
        BUFFER.begin(VertexFormat.Mode.TRIANGLES,DefaultVertexFormat.POSITION_COLOR);
        try {
            P[] input=new P[4],output=new P[8];
            for(Face face:faces) {
                input[0]=face.a();input[1]=face.b();input[2]=face.c();input[3]=face.d();
                int count=clip(input,output,height*formed);
                if(count<3)continue;
                double rim=Math.pow(1-Math.abs(face.normal().dot(view)),3);
                double shade=.38+.62*Math.max(0,face.normal().dot(LIGHT));
                Material material=face.material();
                if(material==Material.LIGHT)shade=1;
                float red=(float)Math.min(1,material.r*shade+rim*.13);
                float green=(float)Math.min(1,material.g*shade+rim*.15);
                float blue=(float)Math.min(1,material.b*shade+rim*.18);
                float alpha=(float)((material==Material.LIGHT?.95:material==Material.GOLD?.82:.68)*(.25+.75*formed));
                for(int i=1;i<count-1;i++) {
                    vertex(matrix,origin,xAxis,zAxis,output[0],red,green,blue,alpha);
                    vertex(matrix,origin,xAxis,zAxis,output[i],red,green,blue,alpha);
                    vertex(matrix,origin,xAxis,zAxis,output[i+1],red,green,blue,alpha);
                }
            }
            BufferUploader.drawWithShader(BUFFER.end());
        } finally {
            RenderSystem.depthMask(true);
            RenderSystem.enableCull();
            RenderSystem.defaultBlendFunc();
            RenderSystem.disableBlend();
        }
    }

    /** Clip polygons at the rising formation plane instead of exposing square part boundaries. */
    private static int clip(P[] in,P[] out,double height) {
        int count=0;
        for(int i=0;i<4;i++) {
            P a=in[i],b=in[(i+1)%4];
            boolean inside=a.y()<=height,next=b.y()<=height;
            if(inside)out[count++]=a;
            if(inside!=next) {
                double t=(height-a.y())/(b.y()-a.y());
                out[count++]=a.add(b.sub(a).scale(t));
            }
        }
        return count;
    }
    private static void vertex(Matrix4f matrix,Vec3 origin,Vec3 xAxis,Vec3 zAxis,P p,
                               float red,float green,float blue,float alpha) {
        BUFFER.vertex(matrix,(float)(origin.x+xAxis.x*p.x()+zAxis.x*p.z()),
                (float)(origin.y+p.y()),(float)(origin.z+xAxis.z*p.x()+zAxis.z*p.z()))
                .color(red,green,blue,alpha).endVertex();
    }
    private HouyiAvatarRenderer() {}
}
