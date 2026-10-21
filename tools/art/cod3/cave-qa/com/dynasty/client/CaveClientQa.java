package com.dynasty.client;

import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.WorldOptions;
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

/** Native evidence from a naturally generated cave in one silent disposable NORMAL world. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class CaveClientQa {
    private static final Path OUT=Path.of(System.getProperty("dynasty.auroraQa.output","build/cave-unset"));
    private static final List<String> RESULTS=new ArrayList<>();
    private static final String[] LABELS={"front","oblique","side","back","ceiling","crystal-close","after-reload"};
    private static boolean hidden,started,done,configured;private static int stage,settle;
    private static BoundingBox bounds;private static CompletableFuture<Void> prepare,position,reload;
    private static final long DEADLINE=System.nanoTime()+540_000_000_000L;
    private static void require(boolean value,String why){if(!value)throw new AssertionError(why);RESULTS.add("PASS "+why);}
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(!Boolean.getBoolean("dynasty.caveQa")||done||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            Files.createDirectories(OUT);
            if(!hidden){GLFW.glfwHideWindow(mc.getWindow().getWindow());hidden=true;mc.options.getSoundSourceOptionInstance(net.minecraft.sounds.SoundSource.MASTER).set(0.0);}
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Cave QA deadline");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                started=true;mc.options.pauseOnLostFocus=false;mc.options.hideGui=true;mc.options.fov().set(70);mc.options.bobView().set(false);mc.options.renderDistance().set(4);mc.options.cloudStatus().set(CloudStatus.OFF);mc.options.framerateLimit().set(40);
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);rules.getRule(GameRules.RULE_WEATHER_CYCLE).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("crystal-natural-qa",new LevelSettings("Disposable natural crystal QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(1518,true,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.NORMAL).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
            if(prepare==null){
                prepare=mc.getSingleplayerServer().submit(()->{
                    var l=mc.getSingleplayerServer().overworld();l.setDayTime(6000);l.setWeatherParameters(6000,0,false,false);
                    var registry=l.registryAccess().registryOrThrow(Registries.STRUCTURE);
                    var holder=registry.getHolderOrThrow(ResourceKey.create(Registries.STRUCTURE,new ResourceLocation("dynasty","scenic_crystal_canopy")));
                    var found=l.getChunkSource().getGenerator().findNearestMapStructure(l,HolderSet.direct(holder),new BlockPos(0,-32,0),12,false);
                    require(found!=null,"native locate finds natural crystal canopy seed=1518");
                    var cp=new ChunkPos(found.getFirst());StructureStart start=null;
                    for(int dx=-1;dx<=1;dx++)for(int dz=-1;dz<=1;dz++){
                        var candidate=l.getChunk(cp.x+dx,cp.z+dz).getStartForStructure(holder.value());
                        if(candidate!=null&&candidate.isValid())start=candidate;
                    }
                    require(start!=null&&start.getPieces().size()==1,"natural world chunk contains exactly one registered jigsaw piece");bounds=start.getBoundingBox();
                    require(bounds.getXSpan()==31&&bounds.getZSpan()==31&&bounds.minY()<0&&bounds.maxY()<0,"natural cave remains bounded underground");
                    for(int x=bounds.minX()>>4;x<=bounds.maxX()>>4;x++)for(int z=bounds.minZ()>>4;z<=bounds.maxZ()>>4;z++)l.getChunk(x,z);
                    int lamps=0,visibleCalcite=0;
                    for(var p:BlockPos.betweenClosed(bounds.minX(),bounds.minY(),bounds.minZ(),bounds.maxX(),bounds.maxY(),bounds.maxZ())){
                        var state=l.getBlockState(p);
                        if(state.is(net.minecraft.world.level.block.Blocks.SEA_LANTERN)){lamps++;require(Arrays.stream(Direction.values()).anyMatch(d->l.isEmptyBlock(p.relative(d))),"natural light has an exposed face "+p.toShortString());}
                        if(p.getY()>bounds.minY()+10&&state.is(net.minecraft.world.level.block.Blocks.CALCITE)&&l.isEmptyBlock(p.below()))visibleCalcite++;
                    }
                    require(lamps==9,"all nine original crystal lights survive actual world generation");
                    require(visibleCalcite>=8,"constellation traces exposed on inside ceiling count="+visibleCalcite);
                    int cx=(bounds.minX()+bounds.maxX())/2,cz=(bounds.minZ()+bounds.maxZ())/2;
                    for(int offset=-15;offset<=15;offset++)for(var base:List.of(new BlockPos(cx+offset,bounds.minY(),cz),new BlockPos(cx,bounds.minY(),cz+offset))){
                        require(l.getBlockState(base).isSolid(),"natural crossing has solid floor");
                        for(int y=1;y<=4;y++)require(l.isEmptyBlock(base.above(y)),"natural crossing retains headroom");
                    }
                    try{Files.writeString(OUT.resolve("natural-location.json"),"{\"seed\":1518,\"locate\":\""+found.getFirst().toShortString()+"\",\"bounds\":\""+bounds+"\",\"lamps\":"+lamps+",\"exposedCeilingTrace\":"+visibleCalcite+",\"templatePlacement\":false}");}catch(Exception e){throw new RuntimeException(e);}
                    l.getChunkSource().save(true);
                    l.getServer().getPlayerList().getPlayers().get(0).setGameMode(GameType.SPECTATOR);
                });return;
            }
            if(!prepare.isDone())return;prepare.join();
            if(stage==LABELS.length){Files.write(OUT.resolve("PASS.txt"),RESULTS);done=true;mc.stop();return;}
            if(stage==6&&reload==null){reload=mc.reloadResourcePacks();return;}if(reload!=null&&!reload.isDone())return;if(reload!=null)reload.join();
            if(!configured){
                configured=true;settle=0;double angle=Math.toRadians(stage==1?45:stage==2?90:stage==3?180:0);
                var center=new Vec3((bounds.minX()+bounds.maxX()+1)/2.,bounds.minY(),(bounds.minZ()+bounds.maxZ()+1)/2.);
                Vec3 at=center.add(Math.sin(angle)*9,2.6,-Math.cos(angle)*9),target=center.add(0,9,0);
                if(stage==4){at=center.add(0,2.6,0);target=center.add(0,17,0);}
                if(stage==5){at=center.add(7,2.6,-6);target=center.add(9,4,-7);}
                var camera=at;double horizontal=Math.hypot(target.x-at.x,target.z-at.z);float yaw=(float)Math.toDegrees(Math.atan2(-(target.x-at.x),target.z-at.z));float pitch=(float)-Math.toDegrees(Math.atan2(target.y-at.y,horizontal));double eye=mc.player.getEyeHeight();
                position=mc.getSingleplayerServer().submit(()->{var l=mc.getSingleplayerServer().overworld();l.getServer().getPlayerList().getPlayers().get(0).teleportTo(l,camera.x,camera.y-eye,camera.z,yaw,pitch);});mc.setCameraEntity(mc.player);
            }
            if(!position.isDone())return;position.join();settle++;
        }catch(Throwable t){fail(t);}
    }
    @SubscribeEvent public static void capture(TickEvent.RenderTickEvent event){
        if(!Boolean.getBoolean("dynasty.caveQa")||done||event.phase!=TickEvent.Phase.END||settle<100)return;
        try{
            var mc=Minecraft.getInstance();require(GL11.glGetError()==GL11.GL_NO_ERROR,"native GL frame "+LABELS[stage]);
            try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){
                image.writeToFile(OUT.resolve(String.format(Locale.ROOT,"%02d-%s.png",stage,LABELS[stage])));
                int lit=0,purple=0;
                for(int y=0;y<image.getHeight();y++)for(int x=0;x<image.getWidth();x++){
                    int c=image.getPixelRGBA(x,y),r=c&255,g=c>>8&255,b=c>>16&255;
                    if(r+g+b>90)lit++;if(b>g+12&&r>g+8)purple++;
                }
                require(lit>image.getWidth()*image.getHeight()/12,"cave visible without night vision or added lights "+LABELS[stage]);
                require(purple>200,"native amethyst silhouette "+LABELS[stage]);
            }
            stage++;configured=false;settle=0;
        }catch(Throwable t){fail(t);}
    }
    private static void fail(Throwable t){done=true;t.printStackTrace();try{Files.writeString(OUT.resolve("FAIL.txt"),t.toString());Files.write(OUT.resolve("partial.txt"),RESULTS);}catch(Exception ignored){}Minecraft.getInstance().stop();}
}
