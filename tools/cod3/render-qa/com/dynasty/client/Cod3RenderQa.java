package com.dynasty.client;

import com.dynasty.cod3.*;
import com.mojang.blaze3d.pipeline.*;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.renderer.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import org.lwjgl.opengl.GL11;
import software.bernie.geckolib.core.animatable.GeoAnimatable;
import software.bernie.geckolib.core.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.core.animation.AnimatableManager;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoObjectRenderer;
import software.bernie.geckolib.util.GeckoLibUtil;
import java.nio.file.*;
import java.util.*;

/** Production VFX geometry and baked GeckoLib resources in a real Minecraft GL context. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class Cod3RenderQa {
    private static boolean done;
    private static int frames;
    private static final Path OUT=Path.of(System.getProperty("dynasty.cod3RenderQa.output","build/cod3-render-qa/results"));
    private static final List<String> RESULTS=new ArrayList<>();
    @SubscribeEvent public static void tick(TickEvent.RenderTickEvent e){
        var mc=Minecraft.getInstance();
        if(!Boolean.getBoolean("dynasty.cod3RenderQa")||done||e.phase!=TickEvent.Phase.END)return;
        if(mc.getOverlay()==null&&mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
        if(!(mc.screen instanceof TitleScreen)||mc.getOverlay()!=null||++frames<12)return;
        done=true;
        try{
            Files.createDirectories(OUT);Files.deleteIfExists(OUT.resolve("FAIL.txt"));Files.deleteIfExists(OUT.resolve("PASS.txt"));
            RESULTS.add("Minecraft Forge framebuffer QA; no world opened. GL="+GL11.glGetString(GL11.GL_RENDERER));
            for(int i=1;i<=40;i++){final int id=i;vfx(id,32,"near");vfx(id,12,"low");}
            for(int i=1;i<=25;i++){final int id=i;scenic(id);}
            for(var row:Cod3Catalog.entries("npcs")){var role=row.getAsJsonObject().get("id").getAsString();npc(role,180);npc(role,90);}
            for(var recipe:com.dynasty.workshop.WorkshopRecipes.ALL)workshop(recipe);
            for(int i=0;i<30;i++){final int kind=i;frame("landmark-"+kind,2, .6,()->{
                var buffers=mc.renderBuffers().bufferSource();var pose=new PoseStack();pose.translate(-.5,0,-.5);
                mc.getBlockRenderer().renderSingleBlock(StoryAnchor.BLOCK.get().defaultBlockState().setValue(StoryAnchor.KIND,kind),pose,buffers,15728880,net.minecraft.client.renderer.texture.OverlayTexture.NO_OVERLAY);buffers.endBatch();
            });}
            if(mc.level!=null)throw new AssertionError("QA opened a world");
            Files.write(OUT.resolve("PASS.txt"),RESULTS);
        }catch(Throwable t){t.printStackTrace();RESULTS.add("FAIL: "+t);try{Files.createDirectories(OUT);Files.write(OUT.resolve("FAIL.txt"),RESULTS);}catch(Exception ignored){}}
        mc.stop();
    }
    private static void vfx(int id,int segments,String lod)throws Exception{
        var d=Cod3Catalog.vfx(id);double size=Math.max(4,Math.max(d.radius()*2,d.length()));
        var geometry=Class.forName("com.dynasty.client.Cod3VfxRenderer$Geometry");
        var ctor=geometry.getDeclaredConstructor(Matrix4f.class,Vec3.class,Vec3.class,Vec3.class,double.class,int.class,double.class,int.class,long.class);ctor.setAccessible(true);
        var draw=geometry.getDeclaredMethod("draw",int.class,DynastyVfxDefinition.class,double.class,double.class,double.class);draw.setAccessible(true);
        var field=Cod3VfxRenderer.class.getDeclaredField("BUFFER");field.setAccessible(true);var buffer=(BufferBuilder)field.get(null);
        frame(String.format(Locale.ROOT,"vfx-%02d-%s",id,lod),size,3,()->{
            int depth=GL11.glGetInteger(GL11.GL_DEPTH_WRITEMASK);boolean blend=GL11.glIsEnabled(GL11.GL_BLEND),test=GL11.glIsEnabled(GL11.GL_DEPTH_TEST);
            try(ImperialRenderState state=new ImperialRenderState()){
                RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();RenderSystem.enableDepthTest();RenderSystem.depthMask(false);RenderSystem.disableCull();RenderSystem.setShader(GameRenderer::getPositionColorShader);
                var matrix=new Matrix4f().rotateY(.65f).rotateX(.2f).translate(0,0,-(float)d.length()/3);
                buffer.begin(VertexFormat.Mode.TRIANGLES,DefaultVertexFormat.POSITION_COLOR);
                try{draw.invoke(ctor.newInstance(matrix,new Vec3(0,3,size*2.1),Vec3.ZERO,new Vec3(0,0,1),1d,d.color(),.8d,segments,1234L),id,d,1d,.5d,20d);BufferUploader.drawWithShader(buffer.end());}catch(Exception error){buffer.discard();throw new RuntimeException(error);}
            }
            if(GL11.glGetInteger(GL11.GL_DEPTH_WRITEMASK)!=depth||GL11.glIsEnabled(GL11.GL_BLEND)!=blend||GL11.glIsEnabled(GL11.GL_DEPTH_TEST)!=test)throw new AssertionError("VFX leaked GL state");
        });
    }
    private static final class Preview implements GeoAnimatable {
        final String role;final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);
        Preview(String role){this.role=role;}
        public void registerControllers(AnimatableManager.ControllerRegistrar r){}
        public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}
        public double getTick(Object object){return 0;}
    }
    private static void npc(String role,int angle)throws Exception{
        var model=new GeoModel<Preview>(){
            public ResourceLocation getModelResource(Preview p){return new ResourceLocation("dynasty","geo/npc/"+p.role+".geo.json");}
            public ResourceLocation getTextureResource(Preview p){return new ResourceLocation("dynasty","textures/entity/npc/"+p.role+".png");}
            public ResourceLocation getAnimationResource(Preview p){return new ResourceLocation("dynasty","animations/npc/"+p.role+".animation.json");}
            // This resource/baked-model test runs without a level. World Molang queries
            // belong to in-world animation QA, not the isolated resource framebuffer.
            public void applyMolangQueries(Preview p,double tick){}
        };
        var renderer=new GeoObjectRenderer<>(model);var p=new Preview(role);
        frame("npc-"+role+"-"+angle,3.5,1,()->{
            var pose=new PoseStack();pose.mulPose(com.mojang.math.Axis.YP.rotationDegrees(angle));var buffers=Minecraft.getInstance().renderBuffers().bufferSource();
            com.mojang.blaze3d.platform.Lighting.setupFor3DItems();renderer.render(pose,p,buffers,RenderType.entityCutoutNoCull(model.getTextureResource(p)),null,15728880);buffers.endBatch();
        });
    }
    private static void workshop(com.dynasty.workshop.WorkshopRecipes.Recipe recipe)throws Exception{
        var item=new com.dynasty.workshop.WorkshopRecipes.Cost("dynasty:"+recipe.station(),1).stack();
        var state=((net.minecraft.world.item.BlockItem)item.getItem()).getBlock().defaultBlockState();var be=new com.dynasty.workshop.WorkshopBlockEntity(net.minecraft.core.BlockPos.ZERO,state);
        var inventory=new net.minecraft.world.entity.player.Inventory(null);var data=new net.minecraft.world.inventory.SimpleContainerData(4);data.set(1,recipe.total());
        for(int stage=0;stage<2;stage++){
            data.set(0,stage==0?0:recipe.total());var menu=new com.dynasty.workshop.WorkshopMenu(1,inventory,be,data);var screen=new WorkshopScreen(menu,inventory,net.minecraft.network.chat.Component.literal(recipe.station()));
            var mc=Minecraft.getInstance();screen.init(mc,240,200);int n=stage;
            frame("workshop-"+recipe.station()+"-"+n,1,0,()->{
                RenderSystem.setProjectionMatrix(new Matrix4f().setOrtho(0,240,200,0,1000,3000),VertexSorting.ORTHOGRAPHIC_Z);var view=RenderSystem.getModelViewStack();view.setIdentity();view.translate(0,0,-2000);RenderSystem.applyModelViewMatrix();
                var graphics=new net.minecraft.client.gui.GuiGraphics(mc,mc.renderBuffers().bufferSource());screen.renderBg(graphics,0,0,0);graphics.flush();
            });
        }
    }
    private static void scenic(int id)throws Exception{
        var geometry=Class.forName("com.dynasty.client.Cod3VfxRenderer$Geometry");
        var ctor=geometry.getDeclaredConstructor(Matrix4f.class,Vec3.class,Vec3.class,Vec3.class,double.class,int.class,double.class,int.class,long.class);ctor.setAccessible(true);
        var draw=geometry.getDeclaredMethod("scenic",int.class,double.class);draw.setAccessible(true);
        var field=Cod3VfxRenderer.class.getDeclaredField("BUFFER");field.setAccessible(true);var buffer=(BufferBuilder)field.get(null);
        frame(String.format(Locale.ROOT,"scenic-%02d",id),36,8,()->{
            try(ImperialRenderState state=new ImperialRenderState()){
                RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();RenderSystem.enableDepthTest();RenderSystem.depthMask(false);RenderSystem.disableCull();RenderSystem.setShader(GameRenderer::getPositionColorShader);
                buffer.begin(VertexFormat.Mode.TRIANGLES,DefaultVertexFormat.POSITION_COLOR);
                try{draw.invoke(ctor.newInstance(new Matrix4f().rotateY(.3f),new Vec3(0,8,75.6),Vec3.ZERO,new Vec3(0,0,1),1d,0xB5E0C9,.8d,32,1234L),id,.5d);BufferUploader.drawWithShader(buffer.end());}catch(Exception error){buffer.discard();throw new RuntimeException(error);}
            }
        });
    }
    private static void frame(String name,double size,double height,Runnable draw)throws Exception{
        var mc=Minecraft.getInstance();var oldProjection=new Matrix4f(RenderSystem.getProjectionMatrix());var sort=RenderSystem.getVertexSorting();
        float fogStart=RenderSystem.getShaderFogStart(),fogEnd=RenderSystem.getShaderFogEnd();var target=new TextureTarget(600,600,true,Minecraft.ON_OSX);var view=RenderSystem.getModelViewStack();view.pushPose();
        try(ImperialRenderState state=new ImperialRenderState()){
            target.setClearColor(.055f,.075f,.105f,1);target.clear(Minecraft.ON_OSX);target.bindWrite(true);view.setIdentity();
            view.mulPoseMatrix(new Matrix4f().lookAt(0,(float)height,(float)(size*2.1),0,(float)height,0,0,1,0));RenderSystem.applyModelViewMatrix();
            RenderSystem.setProjectionMatrix(new Matrix4f().perspective(.57f,1,.05f,256),VertexSorting.DISTANCE_TO_ORIGIN);RenderSystem.setShaderFogStart(1000);RenderSystem.setShaderFogEnd(2000);RenderSystem.setShaderColor(1,1,1,1);
            RenderSystem.enableDepthTest();RenderSystem.depthMask(true);RenderSystem.disableBlend();RenderSystem.disableCull();draw.run();GL11.glFinish();
            int error=GL11.glGetError();if(error!=GL11.GL_NO_ERROR)throw new AssertionError(name+" GL error "+error);
            try(var image=Screenshot.takeScreenshot(target)){
                int background=image.getPixelRGBA(0,0),pixels=0;for(int y=0;y<600;y++)for(int x=0;x<600;x++)if(image.getPixelRGBA(x,y)!=background)pixels++;
                if(pixels<10)throw new AssertionError(name+" is empty ("+pixels+")");image.writeToFile(OUT.resolve(name+".png"));RESULTS.add("PASS "+name+" pixels="+pixels);
            }
        }finally{view.popPose();RenderSystem.applyModelViewMatrix();RenderSystem.setProjectionMatrix(oldProjection,sort);RenderSystem.setShaderFogStart(fogStart);RenderSystem.setShaderFogEnd(fogEnd);target.destroyBuffers();mc.getMainRenderTarget().bindWrite(true);}
    }
}
