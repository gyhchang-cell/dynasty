package com.dynasty.client;

import com.dynasty.Dynasty;
import com.dynasty.HouyiAvatarShape.Material;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import net.minecraft.client.renderer.ShaderInstance;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterShadersEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.io.IOException;
import org.joml.Matrix4f;
import net.minecraft.world.phys.Vec3;

/** One reload-safe program for opaque, depth-correct sculpted guardian/dragon surfaces. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID,value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.MOD)
public final class ImperialMaterialShader {
    private static ShaderInstance material;
    private static ShaderInstance glow;
    private static final ResourceLocation BROCADE=new ResourceLocation(Dynasty.MODID,"textures/effect/guanyu_brocade.png");
    private static boolean brocadeAvailable;
    @SubscribeEvent
    public static void register(RegisterShadersEvent event) throws IOException {
        HouyiAvatarRenderer.invalidateGuardianBuffer();
        ImperialDragonRenderer.invalidate();
        ImperialWeaponRenderer.invalidateTransientBuffers();
        brocadeAvailable=event.getResourceProvider().getResource(BROCADE).isPresent();
        event.registerShader(new ShaderInstance(event.getResourceProvider(),
                new ResourceLocation(Dynasty.MODID,"imperial_material"),DefaultVertexFormat.POSITION_COLOR_NORMAL),
                shader->material=shader);
        event.registerShader(new ShaderInstance(event.getResourceProvider(),
                new ResourceLocation(Dynasty.MODID,"imperial_glow"),DefaultVertexFormat.POSITION_COLOR),shader->glow=shader);
    }
    public static boolean bind(Matrix4f worldView,float sceneLight) {
        if(material==null)return false;
        RenderSystem.setShader(()->material);
        var light=material.getUniform("SceneLight");
        if(light!=null)light.set(Math.max(.35f,Math.min(1f,sceneLight)));
        var orientation=material.getUniform("WorldViewMat");
        if(orientation!=null)orientation.set(worldView);
        var lighting=material.getUniform("LightViewMat");
        if(lighting!=null)lighting.set(worldView);
        var mode=material.getUniform("MaterialMode");
        if(mode!=null)mode.set(0f);
        var opacity=material.getUniform("MeshOpacity");if(opacity!=null)opacity.set(1f);
        return true;
    }
    public static boolean available(){return material!=null;}
    public static boolean bindGuardian(Matrix4f worldView,Vec3 origin,Vec3 right,Vec3 forward,float sceneLight) {
        if(!bind(worldView,sceneLight))return false;
        Matrix4f worldFromLocal=new Matrix4f().m00((float)right.x).m02((float)right.z)
                .m20((float)forward.x).m22((float)forward.z)
                .m30((float)origin.x).m31((float)origin.y).m32((float)origin.z);
        var local=material.getUniform("LocalFromPosition");
        if(local!=null)local.set(new Matrix4f(worldView).mul(worldFromLocal).invert());
        enableBrocade();
        return true;
    }
    /** Cached VBO stores local positions/normals; remove instance yaw from light directions only. */
    public static boolean bindGuardianLocal(Matrix4f worldFromLocal,float sceneLight) {
        if(!bind(new Matrix4f(),sceneLight))return false;
        var lighting=material.getUniform("LightViewMat");
        if(lighting!=null)lighting.set(new Matrix4f(worldFromLocal).invert());
        var local=material.getUniform("LocalFromPosition");
        if(local!=null)local.set(new Matrix4f());
        enableBrocade();
        return true;
    }
    public static boolean bindDragonLocal(Matrix4f worldFromLocal,float sceneLight,float opacity) {
        if(!bind(new Matrix4f(),sceneLight))return false;
        var lighting=material.getUniform("LightViewMat");
        if(lighting!=null)lighting.set(new Matrix4f(worldFromLocal).invert());
        var local=material.getUniform("LocalFromPosition");if(local!=null)local.set(new Matrix4f());
        var visibility=material.getUniform("MeshOpacity");if(visibility!=null)visibility.set(opacity);
        return true;
    }
    private static void enableBrocade() {
        if(!brocadeAvailable)return;
        var colorA=material.getUniform("RobeColorA");
        var colorB=material.getUniform("RobeColorB");
        if(colorA!=null)colorA.set(Material.CLOTH_GREEN.r,Material.CLOTH_GREEN.g,Material.CLOTH_GREEN.b);
        if(colorB!=null)colorB.set(Material.EMERALD.r,Material.EMERALD.g,Material.EMERALD.b);
        var mode=material.getUniform("MaterialMode");if(mode!=null)mode.set(1f);
        RenderSystem.setShaderTexture(0,BROCADE);
    }
    public static boolean bindGlow() {
        if(glow==null)return false;
        RenderSystem.setShader(()->glow);
        return true;
    }
    private ImperialMaterialShader() {}
}
