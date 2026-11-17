package com.dynasty.client;

import com.dynasty.cod3.*;
import com.dynasty.structure.ScenicFireTreeStructure;
import com.google.gson.GsonBuilder;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.level.levelgen.structure.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;
import org.lwjgl.opengl.GL11;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** One silent NORMAL world, production generation and production site packets. No manual /place. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class FireTreeQa {
    private static final Path OUT=Path.of(System.getProperty("dynasty.auroraQa.output"));
    private static final List<String> RESULTS=new ArrayList<>();
    private static final String[] LABELS={"front","45","side","back","west-walk","east-walk","root-bank","night-near","night-far","minimal","day","rain","after-reload","late-observer"};
    private static boolean hidden,started,done,configured;private static int stage,settle;
    private static BlockPos origin;private static BoundingBox bounds;private static CompletableFuture<Void> prepare,position,reload,finish;
    private static final long DEADLINE=System.nanoTime()+540_000_000_000L;
    private static void require(boolean value,String why){if(!value)throw new AssertionError(why);RESULTS.add("PASS "+why);}
    @SuppressWarnings("unchecked") private static List<Cod3VisualPacket> active()throws Exception{var f=Cod3VfxRenderer.class.getDeclaredField("ACTIVE");f.setAccessible(true);return (List<Cod3VisualPacket>)f.get(null);}
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(!Boolean.getBoolean("dynasty.fireTreeQa")||done||event.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();
        try{
            Files.createDirectories(OUT);
            if(!hidden){GLFW.glfwHideWindow(mc.getWindow().getWindow());hidden=true;mc.options.getSoundSourceOptionInstance(net.minecraft.sounds.SoundSource.MASTER).set(0.0);}
            if(System.nanoTime()>DEADLINE)throw new AssertionError("fire-tree QA deadline");if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                started=true;mc.options.pauseOnLostFocus=false;mc.options.hideGui=true;mc.options.fov().set(70);mc.options.bobView().set(false);mc.options.renderDistance().set(6);mc.options.cloudStatus().set(CloudStatus.OFF);mc.options.framerateLimit().set(40);
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);rules.getRule(GameRules.RULE_WEATHER_CYCLE).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("fire-tree-natural-qa",new LevelSettings("Disposable natural fire-tree QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(1518,true,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.NORMAL).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
            if(prepare==null){prepare=mc.getSingleplayerServer().submit(()->{
                var l=mc.getSingleplayerServer().overworld();l.setDayTime(18000);l.setWeatherParameters(6000,0,false,false);
                var holder=l.registryAccess().registryOrThrow(Registries.STRUCTURE).getHolderOrThrow(ResourceKey.create(Registries.STRUCTURE,ScenicFireTreeStructure.ID));
                var found=l.getChunkSource().getGenerator().findNearestMapStructure(l,HolderSet.direct(holder),new BlockPos(0,70,0),12,false);
                require(found!=null,"native locate finds natural fire-tree ravine seed1518");
                var cp=new ChunkPos(found.getFirst());StructureStart start=null;
                for(int dx=-2;dx<=2;dx++)for(int dz=-2;dz<=2;dz++){var candidate=l.getChunk(cp.x+dx,cp.z+dz).getStartForStructure(holder.value());if(candidate!=null&&candidate.isValid())start=candidate;}
                require(start!=null&&start.getPieces().size()==1,"natural one-piece structure registered");bounds=start.getBoundingBox();origin=new BlockPos(bounds.minX(),bounds.minY(),bounds.minZ());
                require(bounds.getXSpan()==47&&bounds.getYSpan()==43&&bounds.getZSpan()==47,"natural footprint bounded47x43x47");
                for(int x=bounds.minX()>>4;x<=bounds.maxX()>>4;x++)for(int z=bounds.minZ()>>4;z<=bounds.maxZ()>>4;z++)l.getChunk(x,z);
                int lava=0,lights=0;
                for(var p:BlockPos.betweenClosed(bounds.minX(),bounds.minY(),bounds.minZ(),bounds.maxX(),bounds.maxY(),bounds.maxZ())){
                    var s=l.getBlockState(p);if((s.is(Blocks.OCHRE_FROGLIGHT)||s.is(Blocks.SHROOMLIGHT)))lights++;
                    if(s.is(Blocks.LAVA)){lava++;for(var dir:List.of(Direction.NORTH,Direction.SOUTH,Direction.WEST,Direction.EAST,Direction.DOWN)){var neighbor=l.getBlockState(p.relative(dir));require(neighbor.is(Blocks.LAVA)||neighbor.isSolid(),"natural lava sealed at "+p.toShortString());}}
                }
                require(lava==424&&lights==20,"natural chunks keep424 lava and20 lamps actual="+lava+"/"+lights);
                for(int x:new int[]{7,39}){
                    var entry=origin.offset(x,7,0);require(l.isEmptyBlock(entry)&&l.isEmptyBlock(entry.above())&&l.getBlockState(entry.below()).isSolid(),"natural entry clear and supported "+x);
                    int outer=l.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,entry.getX(),entry.getZ()-1);
                    require(Math.abs(outer-entry.getY())<=1,"natural entry meets outside terrain "+x+" delta="+(outer-entry.getY()));
                }
                var center=origin.offset(24,20,24);require(ScenicFireTreeSite.originNear(l,center).orElseThrow().equals(origin),"loaded native start supplies exact effect frame");
                var site=ScenicFireTreeSite.packet(l,origin);require(site.valid()&&site.scale()==1&&site.entityId()==-1,"native site packet valid no entity");
                require(!new ScenicEvents().start(l,13,site.origin()),"old timed tree disabled");
                try{Files.writeString(OUT.resolve("natural-location.json"),new GsonBuilder().setPrettyPrinting().create().toJson(Map.of("seed",1518,"locate",found.getFirst().toShortString(),"bounds",bounds.toString(),"origin",origin.toShortString(),"lava",lava,"lights",lights,"manuallyPlaced",false)));}catch(Exception e){throw new RuntimeException(e);}
                l.getChunkSource().save(true);l.getServer().getPlayerList().getPlayers().get(0).setGameMode(GameType.SPECTATOR);
            });return;}
            if(!prepare.isDone())return;prepare.join();
            if(stage==LABELS.length){
                if(finish==null){finish=mc.getSingleplayerServer().submit(()->{
                    var level=mc.getSingleplayerServer().overworld();int lava=0,lights=0;
                    for(var p:BlockPos.betweenClosed(bounds.minX()-1,bounds.minY()-1,bounds.minZ()-1,bounds.maxX()+1,bounds.maxY()+1,bounds.maxZ()+1)){
                        var state=level.getBlockState(p);if(bounds.isInside(p)&&(state.is(Blocks.OCHRE_FROGLIGHT)||state.is(Blocks.SHROOMLIGHT)))lights++;
                        if(state.is(Blocks.LAVA)){require(bounds.isInside(p),"lava remains inside sealed ravine after world ticks");lava++;}
                    }
                    require(lava==424&&lights==20,"lava/lighting survive weather changes and fluid updates");level.getChunkSource().save(true);
                });return;}if(!finish.isDone())return;finish.join();
                active().clear();ScenicFireTreeSound.clear();Files.write(OUT.resolve("PASS.txt"),RESULTS);done=true;mc.stop();return;
            }
            if(stage==12&&reload==null){active().clear();reload=mc.reloadResourcePacks();return;}if(reload!=null&&!reload.isDone())return;if(reload!=null)reload.join();
            if(!configured){
                configured=true;settle=0;active().clear();mc.options.particles().set(stage==9?ParticleStatus.MINIMAL:ParticleStatus.ALL);
                double angle=Math.toRadians(stage==1?45:stage==2?90:stage==3?180:0),radius=stage==8?125:52;
                var center=Vec3.atLowerCornerOf(origin).add(23.5,22,23.5);Vec3 target=center,at=center.add(Math.sin(angle)*radius,8,-Math.cos(angle)*radius);
                if(stage==4){at=Vec3.atLowerCornerOf(origin).add(7.5,10.0+mc.player.getEyeHeight(),3);target=center;}
                if(stage==5){at=Vec3.atLowerCornerOf(origin).add(39.5,10.0+mc.player.getEyeHeight(),3);target=center;}
                if(stage==6){at=Vec3.atLowerCornerOf(origin).add(12.5,11.0+mc.player.getEyeHeight(),18.5);target=Vec3.atLowerCornerOf(origin).add(24.5,22,25.5);}
                if(stage==7){at=Vec3.atLowerCornerOf(origin).add(34.5,11.0+mc.player.getEyeHeight(),21.5);target=Vec3.atLowerCornerOf(origin).add(37.5,33.5,25.5);}
                var camera=at;double horizontal=Math.hypot(target.x-at.x,target.z-at.z);float yaw=(float)Math.toDegrees(Math.atan2(-(target.x-at.x),target.z-at.z));float pitch=(float)-Math.toDegrees(Math.atan2(target.y-at.y,horizontal));double eye=mc.player.getEyeHeight();
                position=mc.getSingleplayerServer().submit(()->{var l=mc.getSingleplayerServer().overworld();l.setDayTime(stage==10?6000:18000);l.setWeatherParameters(6000,6000,stage==11,false);
                    if(stage>=4&&stage<=7){var foot=BlockPos.containing(camera.x,camera.y-eye,camera.z);require(l.isEmptyBlock(foot)&&l.isEmptyBlock(foot.above())&&l.getBlockState(foot.below()).isSolid(),"actual walking camera has floor and two blocks headroom "+LABELS[stage]+" foot="+foot+" states="+l.getBlockState(foot)+"/"+l.getBlockState(foot.above())+"/"+l.getBlockState(foot.below()));}
                    l.getServer().getPlayerList().getPlayers().get(0).teleportTo(l,camera.x,camera.y-eye,camera.z,yaw,pitch);});mc.setCameraEntity(mc.player);
            }
            if(!position.isDone())return;position.join();mc.level.setDayTime(stage==10?6000:18000);mc.level.setRainLevel(stage==11?1:0);mc.level.setThunderLevel(0);
            if(settle==0){var packet=ScenicFireTreeSite.packet(mc.getSingleplayerServer().overworld(),origin);
                if(stage==13){var old=new Cod3VisualPacket(packet.dimension(),packet.template(),-1,packet.seed(),packet.start()-80,packet.duration(),packet.scale(),packet.origin(),packet.direction(),packet.sequence(),packet.tick()+80);Cod3VfxRenderer.receive(old);}
                Cod3VfxRenderer.receive(packet);Cod3VfxRenderer.receive(packet);require(active().stream().filter(p->p.sequence().equals("scenic_13")).count()==1,"duplicate site sync single packet "+LABELS[stage]);}
            settle++;
        }catch(Throwable t){fail(t);}
    }
    @SubscribeEvent public static void capture(TickEvent.RenderTickEvent event){
        if(!Boolean.getBoolean("dynasty.fireTreeQa")||done||event.phase!=TickEvent.Phase.END||settle<100)return;
        try{
            var mc=Minecraft.getInstance();require(GL11.glGetError()==GL11.GL_NO_ERROR,"native GL "+LABELS[stage]);
            try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){image.writeToFile(OUT.resolve(String.format(Locale.ROOT,"%02d-%s.png",stage,LABELS[stage])));}
            double visibility=ScenicFireTreeLight.visibility(mc.level.getDayTime(),mc.level.getRainLevel(1));
            require(stage==10||stage==11?visibility==0:visibility==1,"native weather visibility "+LABELS[stage]);
            var f=ScenicFireTreeRenderer.class.getDeclaredField("layout");f.setAccessible(true);var layout=f.get(null);var buds=layout.getClass().getDeclaredMethod("buds");buds.setAccessible(true);
            @SuppressWarnings("unchecked")var points=(List<ScenicAurora.Point>)buds.invoke(layout);require(points.size()==16,"native exported16 bud anchors loaded "+LABELS[stage]);
            double distance=ScenicFireTreeRenderer.soundPosition(active().stream().filter(p->p.sequence().equals("scenic_13")).findFirst().orElseThrow()).distanceTo(mc.gameRenderer.getMainCamera().getPosition());
            var mesh=ScenicFireTreeLight.mesh(1518,mc.level.getGameTime(),distance,stage==9,visibility,points);
            require(stage==10||stage==11?mesh.isEmpty():!mesh.isEmpty()&&mesh.size()<=160,"native night mesh budget/gate "+LABELS[stage]);
            stage++;configured=false;settle=0;
        }catch(Throwable t){fail(t);}
    }
    private static void fail(Throwable t){done=true;t.printStackTrace();try{Files.writeString(OUT.resolve("FAIL.txt"),t.toString());Files.write(OUT.resolve("partial.txt"),RESULTS);}catch(Exception ignored){}Minecraft.getInstance().stop();}
}
