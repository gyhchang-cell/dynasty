package com.dynasty.client;

import com.dynasty.cod3.*;
import com.google.gson.*;
import com.mojang.authlib.GameProfile;
import com.mojang.blaze3d.pipeline.*;
import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.client.renderer.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.*;
import net.minecraft.world.*;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.level.storage.ServerLevelData;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.common.util.FakePlayer;
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
import java.util.concurrent.CompletableFuture;

/** One disposable client: accelerated server clock tests, real AI, native poses and dimension roundtrip. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class WhiteDeerQa {
    private static final Path OUT=Path.of(System.getProperty("dynasty.cod3WhiteDeerQa.output","build/white-deer-unset"));
    private static final List<String> RESULTS=Collections.synchronizedList(new ArrayList<>());
    private static final List<Map<String,Object>> POSES=new ArrayList<>();
    private static CompletableFuture<Void> checks,change,reload;
    private static WhiteDeerEntity deer;
    private static FakePlayer nativeFollower;
    private static ArmorStand camera;
    private static boolean started,done,views,entered;
    private static int phase=-1,settle,shot,wait;
    private static long stageStart;
    private static Vec3 aiStart;
    private static volatile int aiTicks;
    private static List<Double> lastPose;
    private static EntityDataAccessor<Integer> poseKey;
    private static final long DEADLINE=System.nanoTime()+300_000_000_000L;
    private static void require(boolean ok,String text){if(!ok)throw new AssertionError(text);RESULTS.add("PASS "+text);}
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
        if(!Boolean.getBoolean("dynasty.cod3WhiteDeerQa")||done||e.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            Files.createDirectories(OUT);if(System.nanoTime()>DEADLINE)throw new AssertionError("White deer client timeout");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                started=true;mc.options.pauseOnLostFocus=false;mc.options.hideGui=true;mc.options.fov().set(45);mc.options.renderDistance().set(4);mc.options.framerateLimit().set(40);
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);rules.getRule(GameRules.RULE_WEATHER_CYCLE).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("cod3-white-deer",new LevelSettings("Disposable white deer QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(312,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
            if(checks==null){checks=mc.getSingleplayerServer().submit(()->server(mc.getSingleplayerServer().overworld()));return;}
            if(!checks.isDone())return;checks.join();
            if(!views){views=true;for(int angle:new int[]{180,135,90,0})model(angle,false);model(180,true);return;}
            if(phase==-1){
                mc.options.keyShift.setDown(true);
                if(aiTicks<160)return;
                change=mc.getSingleplayerServer().submit(()->{require(deer.position().distanceTo(aiStart)>.5,"real navigation walks toward broad loaded waypoint with quiet follower; shift="+deer.level().getServer().getPlayerList().getPlayers().get(0).isShiftKeyDown()+" navDone="+deer.getNavigation().isDone()+" position="+deer.position()+" ticks="+deer.tickCount+" speed="+deer.getSpeed()+" ground="+deer.onGround()+" path="+(deer.getNavigation().getPath()==null?"null":deer.getNavigation().getPath().getNextNodeIndex()+"/"+deer.getNavigation().getPath().getNodeCount())+" detail");if(nativeFollower!=null){nativeFollower.discard();nativeFollower=null;}deer.setNoAi(true);deer.setNoGravity(true);deer.setPos(0,-60,0);deer.setYRot(0);deer.yBodyRot=0;deer.yBodyRotO=0;var p=mc.getSingleplayerServer().getPlayerList().getPlayers().get(0);p.setShiftKeyDown(false);p.teleportTo(p.serverLevel(),-8,-60,8,180,0);});phase=0;mc.options.keyShift.setDown(false);settle=0;shot=0;return;
            }
            if(change!=null){if(!change.isDone())return;change.join();change=null;stageStart=mc.level.getGameTime();}
            if(phase<5){
                if(mc.level.getEntity(deer.getId()) instanceof WhiteDeerEntity d){
                    if(camera==null){camera=new ArmorStand(mc.level,2,-60.5,4);camera.setYRot(153.435f);camera.setYHeadRot(153.435f);camera.setXRot(5);camera.setOldPosAndRot();mc.setCameraEntity(camera);}
                    if(mc.getEntityRenderDispatcher().getRenderer(d) instanceof WhiteDeerRenderer r)for(var core:r.getGeoModel().getAnimationProcessor().getRegisteredBones())((software.bernie.geckolib.cache.object.GeoBone)core).setTrackingMatrices(true);
                    settle++;
                }return;
            }
            if(phase==5){if(reload==null){reload=mc.reloadResourcePacks();return;}if(!reload.isDone())return;reload.join();model(180,false);require(true,"actual resources reloaded without missing model or animation");
                mc.setCameraEntity(mc.player);camera=null;change=mc.getSingleplayerServer().submit(()->{
                    var p=mc.getSingleplayerServer().getPlayerList().getPlayers().get(0);var personal=new CompoundTag();personal.putLong(WhiteDeerTrail.RECEIPT,p.level().getGameTime());p.getPersistentData().put(Player.PERSISTED_NBT_TAG,personal);p.setItemInHand(InteractionHand.MAIN_HAND,WhiteDeerSanctuary.reward(p));
                    require(WhiteDeerContent.TOKEN.get().use(p.level(),p,InteractionHand.MAIN_HAND).getResult().consumesAction(),"native token use enters real registered dimension");require(p.level().dimension()==WhiteDeerContent.SANCTUARY,"server dimension is white deer grotto");
                });phase=6;wait=0;return;
            }
            if(phase==6){if(mc.level.dimension()!=WhiteDeerContent.SANCTUARY)return;
                if(camera==null){camera=new ArmorStand(mc.level,8.5,65,3.5);camera.setYRot(0);camera.setYHeadRot(0);camera.setXRot(14);camera.setOldPosAndRot();mc.setCameraEntity(camera);wait=0;}
                if(++wait<60)return;image("grotto-world");mc.setCameraEntity(mc.player);camera=null;
                change=mc.getSingleplayerServer().submit(()->{
                    var p=mc.getSingleplayerServer().getPlayerList().getPlayers().get(0);var l=p.serverLevel();l.setBlock(new BlockPos(9,64,9),Blocks.DIAMOND_BLOCK.defaultBlockState(),2);WhiteDeerSanctuary.build(l);require(l.getBlockState(new BlockPos(9,64,9)).is(Blocks.DIAMOND_BLOCK),"garden builds once and preserves later player edits");
                    p.setItemInHand(InteractionHand.MAIN_HAND,ItemStack.EMPTY);var bell=new BlockPos(8,65,12);
                    require(p.gameMode.useItemOn(p,l,ItemStack.EMPTY,InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(bell),Direction.UP,bell,false)).consumesAction(),"native empty-hand return bell succeeds without token");require(p.level().dimension()==Level.OVERWORLD&&p.getY()==-60,"return restores overworld floor and player position");require(!p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).contains("cod3_white_deer_return"),"return point cleared only after successful arrival");p.server.getPlayerList().saveAll();p.server.saveAllChunks(false,true,true);
                });phase=7;wait=0;return;
            }
            if(phase==7&&mc.level.dimension()==Level.OVERWORLD&&++wait>30){image("returned-world");Files.write(OUT.resolve("PASS.txt"),RESULTS);Files.writeString(OUT.resolve("poses.json"),new GsonBuilder().setPrettyPrinting().create().toJson(POSES));done=true;mc.stop();}
        }catch(Throwable t){t.printStackTrace();try{Files.writeString(OUT.resolve("FAIL.txt"),t.toString());Files.write(OUT.resolve("partial-checks.txt"),RESULTS);}catch(Exception ignored){}done=true;mc.stop();}
    }
    private static FakePlayer fake(ServerLevel l,String name){var p=new FakePlayer(l,new GameProfile(UUID.randomUUID(),name));p.setPos(0,-60,4);p.setShiftKeyDown(true);p.setOnGround(true);return p;}
    private static void advance(ServerLevel l){((ServerLevelData)l.getLevelData()).setGameTime(l.getGameTime()+20);}
    private static int tokens(FakePlayer p){return p.getInventory().items.stream().filter(s->s.is(WhiteDeerContent.TOKEN.get())).mapToInt(ItemStack::getCount).sum();}
    private static void step(ServerLevel l,FakePlayer p,WhiteDeerEntity d,int i){advance(l);double x=Math.sin(i*.1)*3,z=Math.cos(i*.1)*3;d.setPos(x,-60,z);p.setPos(x,-60,z+4);p.setOnGround(true);WhiteDeerTrail.sample(p);}
    private static void server(ServerLevel l){
        for(var pos:BlockPos.betweenClosed(new BlockPos(-16,-61,-16),new BlockPos(16,-61,16)))l.setBlock(pos,Blocks.STONE.defaultBlockState(),2);l.setDayTime(1000);
        deer=WhiteDeerContent.DEER.get().create(l);deer.setPos(0,-60,0);deer.setNoAi(true);deer.setNoGravity(true);l.addFreshEntity(deer);
        var a=fake(l,"DeerA");var b=fake(l,"DeerB");
        require(SecretDefinition.of(12).enabled()&&WhiteDeerSanctuary.available(a),"secret 12 and real grotto registry available");
        require(!SecretTracker.get(l).claim(a,12,deer.blockPosition()),"bare anchor or unverified live entity cannot award pact");
        WhiteDeerTrail.sample(a);require(WhiteDeerTrail.state(a).hasUUID("Deer"),"dawn begins tracking exact live deer UUID");
        for(int i=0;i<10;i++){advance(l);WhiteDeerTrail.sample(a);}require(!WhiteDeerTrail.claimed(a)&&WhiteDeerTrail.state(a).getDouble("Travel")==0,"stationary crouching earns no completion");
        a.setShiftKeyDown(false);advance(l);WhiteDeerTrail.sample(a);require(!a.getPersistentData().contains(WhiteDeerTrail.PROGRESS),"standing breaks continuous quiet trail");a.setShiftKeyDown(true);WhiteDeerTrail.sample(a);
        advance(l);deer.startle();WhiteDeerTrail.sample(a);require(!a.getPersistentData().contains(WhiteDeerTrail.PROGRESS),"disturbing deer clears progress");
        ((ServerLevelData)l.getLevelData()).setGameTime(l.getGameTime()+201);WhiteDeerTrail.sample(a);((ServerLevelData)l.getLevelData()).setGameTime(l.getGameTime()+100);WhiteDeerTrail.sample(a);require(!a.getPersistentData().contains(WhiteDeerTrail.PROGRESS),"unload/offline-sized clock gap grants no time");
        WhiteDeerTrail.sample(a);a.setPos(20,-60,20);advance(l);WhiteDeerTrail.sample(a);require(!a.getPersistentData().contains(WhiteDeerTrail.PROGRESS),"leaving local range resets");
        deer.setPos(0,-60,0);a.setPos(0,-60,4);WhiteDeerTrail.sample(a);advance(l);a.setPos(4,-60,4);WhiteDeerTrail.sample(a);require(!a.getPersistentData().contains(WhiteDeerTrail.PROGRESS),"teleport-sized movement resets");
        l.setDayTime(6000);a.setPos(0,-60,4);WhiteDeerTrail.sample(a);require(!a.getPersistentData().contains(WhiteDeerTrail.PROGRESS),"afternoon cannot begin new dawn encounter");l.setDayTime(1000);
        deer.setPos(0,-60,3);a.setPos(0,-60,7);WhiteDeerTrail.sample(a);
        // 300 actual 20-tick samples and entity/player displacements; only the disposable clock is accelerated.
        for(int i=1;i<300;i++)step(l,a,deer,i);
        require(!WhiteDeerTrail.claimed(a)&&WhiteDeerTrail.state(a).getInt("Ticks")==5980,"299 seconds cannot complete five-minute trail");step(l,a,deer,300);
        require(WhiteDeerTrail.claimed(a)&&tokens(a)==1,"6000 verified server ticks award one personal owned pact");
        var pact=a.getInventory().items.stream().filter(s->s.is(WhiteDeerContent.TOKEN.get())).findFirst().orElseThrow();require(pact.getTag().getUUID("Owner").equals(a.getUUID()),"reward binds correct player UUID");
        require(!SecretTracker.get(l).claim(a,12,deer.blockPosition())&&tokens(a)==1,"duplicate completion cannot pay twice");
        require(!WhiteDeerTrail.claimed(b),"other player does not inherit receipt");b.setItemInHand(InteractionHand.MAIN_HAND,pact.copy());require(WhiteDeerContent.TOKEN.get().use(l,b,InteractionHand.MAIN_HAND).getResult()==InteractionResult.FAIL,"another player cannot use owner pact");
        var restored=fake(l,"Restore");restored.getPersistentData().put(Player.PERSISTED_NBT_TAG,a.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).copy());require(WhiteDeerTrail.claimed(restored),"persistent receipt survives NBT restore");
        deer.setPos(0,-60,3);b.setPos(0,-60,7);WhiteDeerTrail.sample(b);for(int i=1;i<=300;i++)step(l,b,deer,i);require(WhiteDeerTrail.claimed(b)&&tokens(b)==2,"second player completes independent trail; carried A token plus own B token");
        var saved=new CompoundTag();deer.addAdditionalSaveData(saved);var replacement=WhiteDeerContent.DEER.get().create(l);replacement.readAdditionalSaveData(saved);require(replacement.disturbance()==deer.disturbance()&&saved.contains("TrailHome")==false,"entity persistence restores disturbance before first native home tick");
        deer.setPos(0,-60,0);deer.setNoGravity(false);deer.setNoAi(false);aiStart=deer.position();var real=l.getServer().getPlayerList().getPlayers().get(0);real.teleportTo(l,-12,-60,12,180,0);nativeFollower=fake(l,"NativeFollow");l.addNewPlayer(nativeFollower);
    }
    @SuppressWarnings("unchecked") private static void forcePose(){
        try{if(poseKey==null){var f=WhiteDeerEntity.class.getDeclaredField("POSE");f.setAccessible(true);poseKey=(EntityDataAccessor<Integer>)f.get(null);}deer.getEntityData().set(poseKey,phase);}catch(Exception e){throw new RuntimeException(e);}
    }
    @SubscribeEvent public static void serverTick(TickEvent.ServerTickEvent e){
        if(!Boolean.getBoolean("dynasty.cod3WhiteDeerQa")||done||e.phase!=TickEvent.Phase.END||deer==null)return;
        if(phase>=0&&phase<5)forcePose();
        else if(phase==-1&&checks!=null&&checks.isDone()){aiTicks++;var p=nativeFollower;if(p!=null){p.setPos(deer.getX(),-60,deer.getZ()+4);p.setShiftKeyDown(true);p.setOnGround(true);}}
    }
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent e){
        if(Boolean.getBoolean("dynasty.cod3WhiteDeerQa")&&!done&&e.phase==TickEvent.Phase.START&&Minecraft.getInstance().level!=null){
            var client=Minecraft.getInstance();for(var entity:client.level.entitiesForRendering())if(client.getEntityRenderDispatcher().getRenderer(entity)==null){
                String missing="No native renderer for "+net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getKey(entity.getType())+" class="+entity.getClass().getName();
                try{Files.writeString(OUT.resolve("FAIL.txt"),missing);}catch(Exception ignored){}System.err.println(missing);done=true;client.stop();return;
            }
        }
        if(!Boolean.getBoolean("dynasty.cod3WhiteDeerQa")||done||e.phase!=TickEvent.Phase.END||phase<0||phase>=5||change!=null||settle<(shot==0?20:36))return;
        var mc=Minecraft.getInstance();if(mc.getOverlay()!=null||mc.level==null||!(mc.level.getEntity(deer.getId()) instanceof WhiteDeerEntity d)||!(mc.getEntityRenderDispatcher().getRenderer(d) instanceof WhiteDeerRenderer r))return;
        try{
            var controller=d.getAnimatableInstanceCache().<WhiteDeerEntity>getManagerForId(d.getId()).getAnimationControllers().get("deer");var state=WhiteDeerEntity.Pose.values()[phase].name().toLowerCase(Locale.ROOT);
            require(controller!=null&&controller.getCurrentAnimation()!=null&&controller.getCurrentAnimation().animation().name().equals("animation.white_deer."+state),"native animation controller plays "+state+" / sample "+shot);
            var model=r.getGeoModel();List<Double> values=new ArrayList<>();for(String name:List.of("head","neck","front_left_upper","front_right_upper","hind_left_upper","hind_right_upper","tail")){var bone=model.getBone(name).orElseThrow();values.add((double)bone.getRotX());values.add((double)bone.getRotY());values.add((double)bone.getRotZ());}
            var herb=model.getBone("herb").orElseThrow();require(herb.getParent().getName().equals("head"),"herb remains child of head "+state+" / sample "+shot);
            double gap=herb.getWorldPosition().distance(herb.getParent().getWorldPosition());require(Double.isFinite(gap)&&Math.abs(gap-Math.sqrt(25.25)/16)<.001,"mouth herb transforms with head "+state+" / sample "+shot);
            String file="world-"+state+"-"+shot;image(file);double delta=lastPose==null?0:java.util.stream.IntStream.range(0,values.size()).mapToDouble(i->Math.abs(values.get(i)-lastPose.get(i))).sum();
            if(shot==1)require(delta>.00001,"two native keyframe poses differ "+state);
            POSES.add(Map.of("state",state,"shot",shot,"rotations",values,"poseDelta",delta,"herbDistance",gap,"screenshot",file+".png","bbHeight",d.getBbHeight()));lastPose=values;shot++;
            if(shot==2){phase++;settle=0;shot=0;lastPose=null;}
        }catch(Throwable t){t.printStackTrace();try{Files.writeString(OUT.resolve("FAIL.txt"),t.toString());Files.write(OUT.resolve("partial-checks.txt"),RESULTS);}catch(Exception ignored){}done=true;mc.stop();}
    }
    private static void image(String name)throws Exception{try(var im=Screenshot.takeScreenshot(Minecraft.getInstance().getMainRenderTarget())){im.writeToFile(OUT.resolve(name+".png"));}}
    private static final class Preview implements GeoAnimatable {
        final AnimatableInstanceCache cache=GeckoLibUtil.createInstanceCache(this);public void registerControllers(AnimatableManager.ControllerRegistrar r){}public AnimatableInstanceCache getAnimatableInstanceCache(){return cache;}public double getTick(Object o){return 0;}
    }
    private static void model(int angle,boolean black)throws Exception{
        var model=new GeoModel<Preview>(){
            public ResourceLocation getModelResource(Preview p){return new ResourceLocation("dynasty","geo/cod3/white_deer.geo.json");}
            public ResourceLocation getTextureResource(Preview p){return new ResourceLocation("dynasty","textures/entity/cod3/white_deer.png");}
            public ResourceLocation getAnimationResource(Preview p){return new ResourceLocation("dynasty","animations/cod3/white_deer.animation.json");}
            public void applyMolangQueries(Preview p,double t){}
        };
        var renderer=new GeoObjectRenderer<Preview>(model){public software.bernie.geckolib.core.object.Color getRenderColor(Preview p,float tick,int light){return software.bernie.geckolib.core.object.Color.ofRGBA(black?0:255,black?0:255,black?0:255,255);}};
        var p=new Preview();model.getBakedModel(model.getModelResource(p));for(var pose:WhiteDeerEntity.Pose.values())require(model.getAnimation(p,"animation.white_deer."+pose.name().toLowerCase(Locale.ROOT))!=null,"baked animation "+pose+" / view "+angle+" black="+black);
        frame("deer-"+(black?"silhouette":angle),2.7,1.4,()->{var stack=new PoseStack();stack.mulPose(com.mojang.math.Axis.YP.rotationDegrees(angle));var buffers=Minecraft.getInstance().renderBuffers().bufferSource();com.mojang.blaze3d.platform.Lighting.setupFor3DItems();renderer.render(stack,p,buffers,RenderType.entityCutoutNoCull(model.getTextureResource(p)),null,15728880);buffers.endBatch();});
    }
    private static void frame(String name,double size,double height,Runnable draw)throws Exception{
        var mc=Minecraft.getInstance();var oldProjection=new Matrix4f(RenderSystem.getProjectionMatrix());var sort=RenderSystem.getVertexSorting();
        float fogStart=RenderSystem.getShaderFogStart(),fogEnd=RenderSystem.getShaderFogEnd();var target=new TextureTarget(600,600,true,Minecraft.ON_OSX);var view=RenderSystem.getModelViewStack();view.pushPose();
        try(ImperialRenderState state=new ImperialRenderState()){
            target.setClearColor(.72f,.76f,.8f,1);target.clear(Minecraft.ON_OSX);target.bindWrite(true);view.setIdentity();
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
