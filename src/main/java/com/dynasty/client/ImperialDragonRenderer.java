package com.dynasty.client;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.VertexBuffer;
import com.mojang.blaze3d.vertex.VertexFormat;
import org.joml.Matrix4f;
import net.minecraft.world.phys.Vec3;

/** Shared immutable dragon meshes. A moving/descending dragon uploads only an instance matrix. */
final class ImperialDragonRenderer {
    record Instance(Matrix4f worldFromLocal,boolean jade,float opacity) {}
    private static final BufferBuilder BUFFER=new BufferBuilder(1048576);
    private static VertexBuffer gold,jade;
    static void invalidate() {
        if(!RenderSystem.isOnRenderThread()) {RenderSystem.recordRenderCall(ImperialDragonRenderer::invalidate);return;}
        if(gold!=null)gold.close();if(jade!=null)jade.close();gold=null;jade=null;
    }
    static void draw(Matrix4f worldView,Instance instance) {
        if(!ImperialMaterialShader.bindDragonLocal(instance.worldFromLocal,
                HouyiAvatarRenderer.sceneLight(Vec3.ZERO),instance.opacity))return;
        VertexBuffer mesh=instance.jade?jade:gold;
        if(mesh==null||mesh.isInvalid()) {
            mesh=upload(instance.jade);
            if(instance.jade)jade=mesh;else gold=mesh;
        }
        mesh.bind();
        try {
            mesh.drawWithShader(new Matrix4f(RenderSystem.getModelViewMatrix()).mul(worldView).mul(instance.worldFromLocal),
                    RenderSystem.getProjectionMatrix(),RenderSystem.getShader());
        } finally {VertexBuffer.unbind();}
    }
    private static VertexBuffer upload(boolean jadePalette) {
        BufferBuilder buffer=BUFFER;
        buffer.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR_NORMAL);
        var normals=ImperialWeaponGeometry.dragonNormals();
        for(int i=0;i<ImperialDragonMesh.FACES.size();i++) {
            var face=ImperialDragonMesh.FACES.get(i);var normal=normals.get(i);
            int color=ImperialDragonMesh.color(face.material(),jadePalette);
            vertex(buffer,face.a(),normal.a(),color);vertex(buffer,face.b(),normal.b(),color);
            vertex(buffer,face.c(),normal.c(),color);vertex(buffer,face.d(),normal.d(),color);
        }
        VertexBuffer result=new VertexBuffer(VertexBuffer.Usage.STATIC);result.bind();
        try {result.upload(buffer.end());}finally {VertexBuffer.unbind();}
        return result;
    }
    private static void vertex(BufferBuilder buffer,ImperialWeaponGeometry.P p,ImperialMeshNormals.Point n,int color) {
        buffer.vertex(p.x(),p.y(),p.z()).color((color>>16)&255,(color>>8)&255,color&255,255)
                .normal((float)n.x(),(float)n.y(),(float)n.z()).endVertex();
    }
    private ImperialDragonRenderer() {}
}
