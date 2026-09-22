package com.dynasty.client;

import com.mojang.blaze3d.pipeline.RenderTarget;
import com.mojang.blaze3d.pipeline.TextureTarget;
import com.mojang.blaze3d.platform.NativeImage;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.BufferBuilder;
import com.mojang.blaze3d.vertex.BufferUploader;
import com.mojang.blaze3d.vertex.DefaultVertexFormat;
import com.mojang.blaze3d.vertex.VertexFormat;
import com.mojang.blaze3d.vertex.VertexSorting;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.renderer.GameRenderer;
import net.minecraft.client.gui.screens.TitleScreen;
import net.minecraft.client.gui.screens.AccessibilityOnboardingScreen;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Matrix4f;
import org.lwjgl.opengl.GL11;

/** Opt-in developer framebuffer test. No desktop capture, no world, never included in the mod jar. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT,bus=Mod.EventBusSubscriber.Bus.FORGE)
public final class ImperialRuntimeQa {
    private static boolean completed;
    private static boolean finished;
    private static java.util.concurrent.CompletableFuture<Void> reload;
    private static long reloadStarted;
    private static int readyFrames;
    private static final Path OUT=Path.of(System.getProperty("dynasty.runtimeQa.output","build/runtime-render-qa/results"));
    private static final List<String> results=new ArrayList<>();

    @SubscribeEvent
    public static void render(TickEvent.RenderTickEvent event) {
        if(!Boolean.getBoolean("dynasty.runtimeQa")||finished||event.phase!=TickEvent.Phase.END)return;
        Minecraft mc=Minecraft.getInstance();
        if(mc.level!=null)throw new AssertionError("Runtime QA must never open a world");
        if(completed) {
            if(reload==null)return;
            if(System.nanoTime()-reloadStarted>120_000_000_000L){fail(mc,new AssertionError("resource reload timed out"));return;}
            if(!reload.isDone()||mc.getOverlay()!=null)return;
            try {
                reload.join();require(ImperialMaterialShader.bind(new Matrix4f(),1),"production material re-registered after resource reload");
                guardian("guanyu-after-reload",35,1);
                dragon("jade-dragon-after-reload",true,1);dragon("gold-dragon-after-reload",false,1);
                compareReload("guanyu-angle","guanyu-after-reload");
                compareReload("jade-dragon","jade-dragon-after-reload");
                compareReload("gold-dragon","gold-dragon-after-reload");
                require(mc.level==null,"no world was opened after resource reload");
                results.add("PASS: "+results.stream().filter(s->s.contains("non-background pixels=")).count()+" real Minecraft FBO frames; resource reload + VBO rebuild; no GL errors.");
                Files.write(OUT.resolve("PASS.txt"),results);finished=true;mc.stop();
            }catch(Throwable error){fail(mc,error);}
            return;
        }
        // This is our new, isolated test profile; skip its first-launch tutorial, not user settings.
        if(mc.getOverlay()==null&&mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
        if(!(mc.screen instanceof TitleScreen)||mc.getOverlay()!=null||++readyFrames<12)return;
        completed=true;
        try {
            Files.createDirectories(OUT);
            results.add("Actual Minecraft development-client offscreen framebuffer; NOT a world screenshot.");
            results.add("GL vendor="+GL11.glGetString(GL11.GL_VENDOR)+"; renderer="+GL11.glGetString(GL11.GL_RENDERER));
            require(mc.getResourceManager().getResource(new ResourceLocation("dynasty","textures/effect/guanyu_brocade.png")).isPresent(),"brocade texture resource loads");
            require(ImperialMaterialShader.bind(new Matrix4f(),1),"production ImperialMaterialShader is registered");
            require(ImperialMaterialShader.bindGlow(),"production glow shader is registered");
            checkGl("before test");
            guardian("guanyu-front",0,1);
            guardian("guanyu-angle",35,1);
            guardian("guanyu-side",90,1);
            guardian("guanyu-back",180,1);
            guardian("guanyu-forming",35,.65);
            guardian("guanyu-nearly-formed",35,.99);
            dragon("jade-dragon",true,1);
            dragon("gold-dragon",false,1);
            dragon("jade-dragon-forming",true,.55f);
            frame("guanyu-translucent-front",9.1,4.45,()->{
                HouyiAvatarRenderer.drawGuanYu(new Matrix4f(),Vec3.ZERO,0,1);translucentQuad(4);
            });
            frame("guanyu-translucent-behind",9.1,4.45,()->{
                HouyiAvatarRenderer.drawGuanYu(new Matrix4f(),Vec3.ZERO,0,1);translucentQuad(-4);
            });
            verifyTransparency();
            sealDescent("qinglong-cage-forming",13);
            sealDescent("qinglong-cage-dragon-descending",26);
            mobPreview("dragon_emperor",1,1.35F);
            mobPreview("nine_heaven_general",2,1.28F);
            mobPreview("jade_guard",3,1.08F);
            mobPreview("soul_soldier",4,1.05F);
            architecturePreview("main-hall",false);
            architecturePreview("academy",true);
            campusPreview("palace",64,false);
            campusPreview("palace",64,true);
            campusPreview("tomb",40,true);
            campusPreview("observatory",26,false);
            for(String id:new String[]{"exam_paper","ink_stick","bamboo_slip"})itemPreview(id);
            for(String id:new String[]{"phoenix_hairpin","jade_cicada","zen_bead_string","star_compass","auspicious_bell","yuchang_dagger","seven_star_saber","leiting_hammer","phoenix_feather_charm","jade_kylin","imperial_pearl_earring","taiyi_sword"})itemPreview(id);
            require(mc.level==null,"no world was opened");
            results.add("PASS: real ShaderInstance.apply + dynamic BufferUploader + static VertexBuffer.drawWithShader; all recorded frames nonempty; no GL errors.");
            results.add("Depth/blend checks simulate translucent draw order; they do not assert Forge world event sequencing.");
            reloadStarted=System.nanoTime();reload=mc.reloadResourcePacks();
            results.add("Requested asynchronous resource reload; render thread was not blocked.");
        } catch(Throwable error) {
            fail(mc,error);
        }
    }
    private static void guardian(String name,float yaw,double formed)throws Exception {
        frame(name,9.1,4.45,()->HouyiAvatarRenderer.drawGuanYu(new Matrix4f(),Vec3.ZERO,yaw,formed));
    }
    private static void campusPreview(String name,int size,boolean cutaway)throws Exception {
        var blocks=com.dynasty.structure.ArchitectureCapture.blocks(name);
        require(blocks.size()>1000,"production campus "+name+" placements="+blocks.size());
        frame("campus-"+name+(cutaway?"-cutaway":""),size*1.38,8,()-> {
            var mc=Minecraft.getInstance();var buffers=mc.renderBuffers().bufferSource();
            var pose=new com.mojang.blaze3d.vertex.PoseStack();pose.translate(0,8,0);
            pose.mulPose(com.mojang.math.Axis.XP.rotationDegrees(cutaway?50:30));
            pose.mulPose(com.mojang.math.Axis.YP.rotationDegrees(-30));
            pose.translate(-size/2.0,-5,-size/2.0);
            for(var e:blocks.entrySet()) {
                var s=e.getValue();var p=e.getKey();
                if(s.isAir()||s.getRenderShape()!=net.minecraft.world.level.block.RenderShape.MODEL
                        ||(cutaway&&p.getY()>(name.equals("tomb")?3:7)))continue;
                pose.pushPose();pose.translate(p.getX(),p.getY(),p.getZ());
                mc.getBlockRenderer().renderSingleBlock(s,pose,buffers,15728880,
                        net.minecraft.client.renderer.texture.OverlayTexture.NO_OVERLAY);
                pose.popPose();
            }
            buffers.endBatch();
        });
    }
    private static void itemPreview(String id)throws Exception {
        var item=net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(new ResourceLocation("dynasty",id));
        require(item!=null&&item!=net.minecraft.world.item.Items.AIR,"registered item "+id);
        frame("item-"+id,1.15,0,()-> {
            var mc=Minecraft.getInstance();var buffers=mc.renderBuffers().bufferSource();
            // Match vanilla inventory lighting for flat generated-item models.
            com.mojang.blaze3d.platform.Lighting.setupForFlatItems();
            mc.getItemRenderer().renderStatic(new net.minecraft.world.item.ItemStack(item),net.minecraft.world.item.ItemDisplayContext.GUI,
                15728880,net.minecraft.client.renderer.texture.OverlayTexture.NO_OVERLAY,new com.mojang.blaze3d.vertex.PoseStack(),buffers,null,0);
            buffers.endBatch();
            com.mojang.blaze3d.platform.Lighting.setupFor3DItems();
        });
    }
    private static void mobPreview(String name,int style,float size)throws Exception {
        for(int view=0;view<2;view++) {
        final int angle=view==0?155:205;
        frame("mob-"+name+(view==0?"":"-opposite"),style<=2?4.8:3.4,1.6,()-> {
            var model=new DynastyHumanoidModel<net.minecraft.world.entity.Mob>(DynastyHumanoidModel.decoratedLayer(style).bakeRoot());
            model.young=false;
            var pose=new com.mojang.blaze3d.vertex.PoseStack();
            pose.translate(0,1.5*size,0);pose.scale(size,-size,size);
            pose.mulPose(com.mojang.math.Axis.YP.rotationDegrees(angle));
            var buffers=Minecraft.getInstance().renderBuffers().bufferSource();
            var texture=new ResourceLocation("dynasty","textures/entity/"+name+".png");
            model.renderToBuffer(pose,buffers.getBuffer(net.minecraft.client.renderer.RenderType.entityCutoutNoCull(texture)),
                15728880,net.minecraft.client.renderer.texture.OverlayTexture.NO_OVERLAY,1,1,1,1);
            DynastyAuraLayer.drawSeal(pose,buffers,style,35);
            buffers.endBatch();
        });
        }
    }

    /** Record the production structure's local block placements, then render its real baked models.
     * No world generation, loot rolls, saves or chunk writes occur in this offscreen harness. */
    private static void architecturePreview(String name,boolean academy)throws Exception {
        var blocks=new java.util.HashMap<net.minecraft.core.BlockPos,net.minecraft.world.level.block.state.BlockState>();
        com.dynasty.structure.DynastyStructurePiece piece;
        if(academy)piece=new com.dynasty.structure.AcademyPiece(com.dynasty.structure.DynastyStructures.ACADEMY_PIECE.get(),0,net.minecraft.core.BlockPos.ZERO) {
            @Override protected void set(net.minecraft.world.level.WorldGenLevel l,net.minecraft.world.level.levelgen.structure.BoundingBox b,int x,int y,int z,net.minecraft.world.level.block.state.BlockState s){blocks.put(new net.minecraft.core.BlockPos(x,y,z),s);}
            @Override protected boolean createChest(net.minecraft.world.level.WorldGenLevel l,net.minecraft.world.level.levelgen.structure.BoundingBox b,net.minecraft.util.RandomSource r,int x,int y,int z,ResourceLocation loot){return true;}
        };else piece=new com.dynasty.structure.MainHallPiece(com.dynasty.structure.DynastyStructures.MAIN_HALL_PIECE.get(),0,net.minecraft.core.BlockPos.ZERO) {
            @Override protected void set(net.minecraft.world.level.WorldGenLevel l,net.minecraft.world.level.levelgen.structure.BoundingBox b,int x,int y,int z,net.minecraft.world.level.block.state.BlockState s){blocks.put(new net.minecraft.core.BlockPos(x,y,z),s);}
            @Override protected boolean createChest(net.minecraft.world.level.WorldGenLevel l,net.minecraft.world.level.levelgen.structure.BoundingBox b,net.minecraft.util.RandomSource r,int x,int y,int z,ResourceLocation loot){return true;}
        };
        piece.postProcess(null,null,null,net.minecraft.util.RandomSource.create(0),piece.getBoundingBox(),new net.minecraft.world.level.ChunkPos(0,0),net.minecraft.core.BlockPos.ZERO);
        require(blocks.size()>1000,"production "+name+" recorded block placements="+blocks.size());
        if(academy)require(blocks.get(new net.minecraft.core.BlockPos(16,2,19)).isAir(),"academy entrance remains open");
        frame("structure-"+name,academy?43:32,7,()-> {
            var mc=Minecraft.getInstance();var buffers=mc.renderBuffers().bufferSource();
            var pose=new com.mojang.blaze3d.vertex.PoseStack();pose.translate(0,7,0);
            pose.mulPose(com.mojang.math.Axis.XP.rotationDegrees(25));
            pose.mulPose(com.mojang.math.Axis.YP.rotationDegrees(-30));
            pose.translate(academy?-17:-11,-5,academy?-17:-10);
            for(var e:blocks.entrySet()) {
                var s=e.getValue();if(s.isAir()||s.getRenderShape()!=net.minecraft.world.level.block.RenderShape.MODEL)continue;
                var p=e.getKey();pose.pushPose();pose.translate(p.getX(),p.getY(),p.getZ());
                mc.getBlockRenderer().renderSingleBlock(s,pose,buffers,15728880,net.minecraft.client.renderer.texture.OverlayTexture.NO_OVERLAY);
                pose.popPose();
            }
            buffers.endBatch();
        });
    }
    private static void dragon(String name,boolean jade,float opacity)throws Exception {
        frame(name,3.65,.06,()->ImperialDragonRenderer.draw(new Matrix4f(),
                new ImperialDragonRenderer.Instance(new Matrix4f().rotateY((float)Math.toRadians(25)),jade,opacity)));
    }
    private static void sealDescent(String name,double age)throws Exception {
        // Exercise the production ribbon expansion and cached dragon draw without opening a world.
        // Reflection is confined to this opt-in test source set; no production API is widened.
        var geometry=ImperialWeaponRenderer.class.getDeclaredMethod("geometry",Matrix4f.class,Vec3.class,
                Vec3.class,Vec3.class,Vec3.class,double.class);geometry.setAccessible(true);
        var drawFaces=ImperialWeaponRenderer.class.getDeclaredMethod("drawFaces",Matrix4f.class);drawFaces.setAccessible(true);
        var bufferField=ImperialWeaponRenderer.class.getDeclaredField("BUFFER");bufferField.setAccessible(true);
        var facesField=ImperialWeaponRenderer.class.getDeclaredField("FACES");facesField.setAccessible(true);
        var dragonsField=ImperialWeaponRenderer.class.getDeclaredField("DRAGONS");dragonsField.setAccessible(true);
        BufferBuilder buffer=(BufferBuilder)bufferField.get(null);
        var faces=(List<?>)facesField.get(null);var dragons=(List<?>)dragonsField.get(null);
        frame(name,14,4,()-> {
            double sizeRatio=ImperialWeaponGeometry.DESCENT_DRAGON_SIZE/2.7;
            Vec3 camera=age<18?new Vec3(6,6,10):new Vec3(12,13,31).scale(sizeRatio);
            var view=RenderSystem.getModelViewStack();view.setIdentity();
            view.mulPoseMatrix(new Matrix4f().lookAt((float)camera.x,(float)camera.y,(float)camera.z,
                    0,age<18?1.3f:(float)(5*sizeRatio),0,0,1,0));RenderSystem.applyModelViewMatrix();
            // The production stroke callback expects camera-relative positions before the event
            // pose transform; translating back here lets the FBO's ordinary view matrix handle them.
            Matrix4f pose=new Matrix4f().translation((float)camera.x,(float)camera.y,(float)camera.z);
            Vec3 center=new Vec3(0,1,0).subtract(camera),right=new Vec3(1,0,0),up=new Vec3(0,1,0),forward=new Vec3(0,0,1);
            var phase=ImperialWeaponGeometry.descentPhase(age,com.dynasty.QinglongDescent.DRAGON_START_TICK,
                    com.dynasty.QinglongDescent.WINDUP_TICKS);
            BufferBuilder.RenderedBuffer glow=null;
            try(ImperialRenderState state=new ImperialRenderState()) {
                faces.clear();dragons.clear();buffer.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR);
                var cage=(ImperialWeaponGeometry)geometry.invoke(null,pose,center,right,up,forward,1d);
                cage.sealCage(age,phase.charge(),phase.connection(),-.955,2.4,ImperialWeaponGeometry.DESCENT_SEAL_RADIUS,1);
                if(phase.dragonAlpha()>0) {
                    var offset=ImperialWeaponGeometry.descentDragonOrigin(2.4,phase.travel());
                    var dragon=(ImperialWeaponGeometry)geometry.invoke(null,pose,center.add(offset.x(),offset.y(),offset.z()),right,up,forward,1d);
                    dragon.dragon(new ImperialWeaponGeometry.P(0,0,0),ImperialWeaponGeometry.DESCENT_DRAGON_SIZE,
                            Math.PI*.75,age,0x36cbbb,phase.dragonAlpha());
                    require(dragons.size()==1,"seal frame queues exactly one cached production dragon");
                }
                glow=buffer.end();drawFaces.invoke(null,pose);
                RenderSystem.enableDepthTest();RenderSystem.depthMask(false);RenderSystem.disableCull();
                RenderSystem.enableBlend();RenderSystem.blendFunc(GL11.GL_SRC_ALPHA,GL11.GL_ONE);
                require(ImperialMaterialShader.bindGlow(),"seal frame uses production glow shader");
                var packet=glow;glow=null;BufferUploader.drawWithShader(packet);
            }catch(ReflectiveOperationException error){throw new IllegalStateException(error);}
            finally {
                if(buffer.building()){var unfinished=buffer.endOrDiscardIfEmpty();if(unfinished!=null)unfinished.release();}
                if(glow!=null)glow.release();faces.clear();dragons.clear();
            }
        });
    }
    private static void frame(String name,double size,double targetY,Runnable draw)throws Exception {
        Minecraft mc=Minecraft.getInstance();
        Matrix4f oldProjection=new Matrix4f(RenderSystem.getProjectionMatrix());
        VertexSorting oldSort=RenderSystem.getVertexSorting();
        float oldFogStart=RenderSystem.getShaderFogStart(),oldFogEnd=RenderSystem.getShaderFogEnd();
        RenderTarget target=new TextureTarget(1500,1500,true,Minecraft.ON_OSX);
        var model=RenderSystem.getModelViewStack();model.pushPose();
        try {
            target.setClearColor(.055f,.075f,.105f,1);target.clear(Minecraft.ON_OSX);target.bindWrite(true);
            model.setIdentity();
            model.mulPoseMatrix(new Matrix4f().lookAt(0,(float)targetY,(float)(size*2.1),0,(float)targetY,0,0,1,0));
            RenderSystem.applyModelViewMatrix();
            RenderSystem.setProjectionMatrix(new Matrix4f().perspective(.57f,1,.05f,256),VertexSorting.DISTANCE_TO_ORIGIN);
            RenderSystem.setShaderFogStart(1000);RenderSystem.setShaderFogEnd(2000);
            RenderSystem.setShaderColor(1,1,1,1);
            RenderSystem.enableDepthTest();RenderSystem.depthMask(true);RenderSystem.disableBlend();RenderSystem.disableCull();
            draw.run();GL11.glFinish();checkGl(name+" draw");
            try(var image=Screenshot.takeScreenshot(target)) {
                int background=image.getPixelRGBA(0,0),pixels=0;
                for(int y=0;y<image.getHeight();y++)for(int x=0;x<image.getWidth();x++)if(image.getPixelRGBA(x,y)!=background)pixels++;
                require(pixels>2000,name+" non-background pixels="+pixels);
                image.writeToFile(OUT.resolve(name+".png"));
            }
            checkGl(name+" readback");
        } finally {
            model.popPose();RenderSystem.applyModelViewMatrix();
            RenderSystem.setProjectionMatrix(oldProjection,oldSort);
            RenderSystem.setShaderFogStart(oldFogStart);RenderSystem.setShaderFogEnd(oldFogEnd);
            target.destroyBuffers();mc.getMainRenderTarget().bindWrite(true);
        }
    }
    private static void require(boolean condition,String description) {
        if(!condition)throw new AssertionError(description);results.add("PASS: "+description);
    }
    private static void checkGl(String label) {
        int error=GL11.glGetError();if(error!=GL11.GL_NO_ERROR)throw new AssertionError(label+": GL error 0x"+Integer.toHexString(error));
    }
    private static void translucentQuad(float z) {
        RenderSystem.enableDepthTest();RenderSystem.depthMask(false);RenderSystem.enableBlend();RenderSystem.defaultBlendFunc();
        RenderSystem.disableCull();RenderSystem.setShader(GameRenderer::getPositionColorShader);
        BufferBuilder buffer=new BufferBuilder(256);buffer.begin(VertexFormat.Mode.QUADS,DefaultVertexFormat.POSITION_COLOR);
        buffer.vertex(-5,0,z).color(32,96,255,128).endVertex();buffer.vertex(5,0,z).color(32,96,255,128).endVertex();
        buffer.vertex(5,9.5,z).color(32,96,255,128).endVertex();buffer.vertex(-5,9.5,z).color(32,96,255,128).endVertex();
        BufferUploader.drawWithShader(buffer.end());RenderSystem.depthMask(true);RenderSystem.disableBlend();
    }
    private static void verifyTransparency()throws Exception {
        try(var baseStream=Files.newInputStream(OUT.resolve("guanyu-front.png"));
            var frontStream=Files.newInputStream(OUT.resolve("guanyu-translucent-front.png"));
            var behindStream=Files.newInputStream(OUT.resolve("guanyu-translucent-behind.png"));
            var base=NativeImage.read(baseStream);var front=NativeImage.read(frontStream);var behind=NativeImage.read(behindStream)) {
            int old=base.getPixelRGBA(750,750),ahead=front.getPixelRGBA(750,750),back=behind.getPixelRGBA(750,750);
            require(old!=base.getPixelRGBA(0,0),"translucent probe lies on the actual guardian");
            int[] tint={32,96,255};
            for(int channel=0;channel<3;channel++) {
                int oldValue=(old>>(channel*8))&255,frontValue=(ahead>>(channel*8))&255,backValue=(back>>(channel*8))&255;
                double expected=(oldValue*127+tint[channel]*128)/255.0;
                require(Math.abs(frontValue-expected)<=2,"foreground translucency blends correctly channel "+channel);
                require(Math.abs(backValue-oldValue)<=1,"guardian depth occludes rear translucency channel "+channel);
            }
        }
    }
    private static void compareReload(String original,String reloaded)throws Exception {
        try(var aStream=Files.newInputStream(OUT.resolve(original+".png"));var bStream=Files.newInputStream(OUT.resolve(reloaded+".png"));
            var a=NativeImage.read(aStream);var b=NativeImage.read(bStream)) {
            int maxDelta=0;
            for(int y=0;y<a.getHeight();y++)for(int x=0;x<a.getWidth();x++) {
                int av=a.getPixelRGBA(x,y),bv=b.getPixelRGBA(x,y);
                for(int c=0;c<3;c++)maxDelta=Math.max(maxDelta,Math.abs(((av>>(c*8))&255)-((bv>>(c*8))&255)));
            }
            require(maxDelta<=1,original+" unchanged after resource reload; maximum RGB delta="+maxDelta);
        }
    }
    private static void fail(Minecraft mc,Throwable error) {
        error.printStackTrace();results.add("FAIL: "+error);
        try {Files.createDirectories(OUT);Files.write(OUT.resolve("FAIL.txt"),results);}catch(Exception ignored){}
        // Only the isolated runClient process created for this test is stopped.
        finished=true;mc.stop();
    }
}
