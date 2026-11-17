package com.dynasty.client;

import com.dynasty.cod3.*;
import com.mojang.blaze3d.platform.NativeImage;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraft.world.entity.decoration.ArmorStand;
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

/** One silent disposable world. Pairs capture production packet rendering and the same view without it. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class AuroraQa {
    private static final Path OUT=Path.of(System.getProperty("dynasty.auroraQa.output","build/aurora-unset"));
    private static final int[] SCENES=Arrays.stream(System.getProperty("dynasty.auroraQa.scenic","15").equals("0")?new String[]{"15","20","21"}:System.getProperty("dynasty.auroraQa.scenic","15").split(",")).mapToInt(Integer::parseInt).toArray();
    private static final Map<Integer,Cod3VisualPacket> PACKETS=new HashMap<>();
    private static int scenic(){return SCENES[(stage/2)%SCENES.length];}
    private static final List<String> RESULTS=new ArrayList<>();
    private static final Vec3 ANCHOR=new Vec3(0,-60,0);
    private static final String[] LABELS={"front","oblique","side","back","near","far","minimal","day","rain","late","after-reload","near-plane"};
    private static final int[] ANGLES={0,45,90,180,0,0,0,0,0,0,0,0};
    private static final double[] DISTANCES={64,64,64,64,24,128,64,64,64,64,64,64};
    private static long day(int view){return scenic()==2?(view==7?6000:view==12?17200:view==13?18800:18000):scenic()==8?(view==7?18000:6000):scenic()==7?(view==7?6000:view==12?14000:view==13?22000:view==17?42000:18000):scenic()==19?(view==7?6000:view==12?11000:view==13?13000:12000):scenic()==21?(view==7?18000:view==12?5500:view==13?6500:6000):(view==7?6000:18000);}
    private static int views(){if(Arrays.stream(SCENES).anyMatch(n->n==7))return 19;return Arrays.stream(SCENES).anyMatch(n->n==21||n==19||n==8||n==2)?17:LABELS.length;}
    private static String label(int view){if(view==8&&scenic()==7)return "dry-weather";return view==7&&(scenic()==21||scenic()==8)?"night":view>=12?new String[]{"early-window","late-window","look-away","outside-region","opaque-roof","wrong-moon","bare-rock"}[view-12]:LABELS[view];}
    // At #8 view11 the camera is inside the middle curtain looking through it; near faces must disappear.
    private static boolean suppressed(int view){return (view==7&&scenic()!=8)||view==8||(view==11&&scenic()==8)||view>=14;}
    private static int stage,settle;private static boolean started,hidden,done,configured;
    private static CompletableFuture<Void> prepare,reload,weather;
    private static Cod3VisualPacket packet;
    private static int[] baseline;
    private static final long DEADLINE=System.nanoTime()+540_000_000_000L;
    private static void require(boolean b,String label){if(!b)throw new AssertionError(label);RESULTS.add("PASS "+label);}
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
        if(!Boolean.getBoolean("dynasty.auroraQa")||done||e.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            Files.createDirectories(OUT);
            if(!hidden){GLFW.glfwHideWindow(mc.getWindow().getWindow());hidden=true;mc.options.getSoundSourceOptionInstance(net.minecraft.sounds.SoundSource.MASTER).set(0.0);}
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Aurora QA deadline");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                started=true;mc.options.pauseOnLostFocus=false;mc.options.hideGui=true;mc.options.fov().set(70);mc.options.bobView().set(false);mc.options.renderDistance().set(10);mc.options.cloudStatus().set(CloudStatus.OFF);mc.options.framerateLimit().set(40);
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);rules.getRule(GameRules.RULE_WEATHER_CYCLE).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("aurora-qa",new LevelSettings("Disposable aurora QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.PEACEFUL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(1518,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
            if(prepare==null){
                prepare=mc.getSingleplayerServer().submit(()->{
                    var l=mc.getSingleplayerServer().overworld();l.setDayTime(18000);
                    if(Arrays.stream(SCENES).anyMatch(n->n==19||n==7)){
                        for(int x=-20;x<=20;x+=10)for(int z=-20;z<=20;z+=10){
                            for(int y=-60;y<-50;y++)l.setBlock(new net.minecraft.core.BlockPos(x,y,z),net.minecraft.world.level.block.Blocks.OAK_LOG.defaultBlockState(),3);
                            for(int dx=-4;dx<=4;dx++)for(int dz=-4;dz<=4;dz++)l.setBlock(new net.minecraft.core.BlockPos(x+dx,-50,z+dz),net.minecraft.world.level.block.Blocks.OAK_LEAVES.defaultBlockState().setValue(net.minecraft.world.level.block.LeavesBlock.PERSISTENT,true),3);
                        }
                    }
                    var data=new ScenicEvents();for(int number:SCENES)require(data.start(l,number,ANCHOR),"production ScenicEvents creates sky packet "+number);
                    for(var p:data.packets(l,ANCHOR))PACKETS.put(Integer.parseInt(p.sequence().substring(7)),p);
                    var p=mc.getSingleplayerServer().getPlayerList().getPlayers().get(0);p.setGameMode(GameType.SPECTATOR);p.teleportTo(l,48,-60,48,0,0);
                });return;
            }
            if(!prepare.isDone())return;prepare.join();
            if(stage>=views()*2*SCENES.length){
                clear();ScenicArraySound.sync(mc.level,active());require(active().isEmpty(),"visual state clears without owning fog/camera/sky globals");
                Files.write(OUT.resolve("PASS.txt"),RESULTS);done=true;mc.stop();return;
            }
            int view=stage/(2*SCENES.length);packet=PACKETS.get(scenic());
            if(view==10&&reload==null){reload=mc.reloadResourcePacks();return;}
            if(reload!=null&&!reload.isDone())return;if(reload!=null)reload.join();
            if(!configured){
                clear();configured=true;settle=0;
                long day=day(view);boolean rain=scenic()==7?view!=8:view==8;
                weather=mc.getSingleplayerServer().submit(()->{var l=mc.getSingleplayerServer().overworld();l.setDayTime(day);l.setWeatherParameters(6000,6000,rain,false);});
                mc.options.particles().set(view==6?ParticleStatus.MINIMAL:ParticleStatus.ALL);
                double radius=view==15?260:view>=12?64:DISTANCES[view],angle=Math.toRadians(view>=12?0:ANGLES[view]);double elevation=view==11?85:2;
                Vec3 at=ANCHOR.add(Math.sin(angle)*radius,elevation,-Math.cos(angle)*radius),target=ANCHOR.add(0,95,0);
                if(scenic()==2){
                    target=ANCHOR.add(0,7,0);
                    if(view==11){at=ANCHOR.add(17,1,0);target=ANCHOR.add(0,7,0);}
                    if(view==12){at=ANCHOR.add(0,22,-30);target=ANCHOR.add(0,1,0);}
                    if(view==14)target=at.add(0,0,-160);
                }
                if(scenic()==8){
                    target=ANCHOR.add(0,25,0);
                    if(view==11){at=ANCHOR.add(0,25,0);target=at.add(0,0,20);}
                    if(view==14)target=at.add(0,0,-160);
                }
                if(scenic()==19||scenic()==7){
                    if(view==11)at=ANCHOR.add(5,5,5);
                    target=ANCHOR.add(0,5,0);
                    if(view==11)target=at.add(0,1,16);
                    if(scenic()==7){if(view==11)at=ANCHOR.add(5,2,5);target=view==11?at.add(0,0,16):ANCHOR.add(0,2,0);}
                    if(scenic()==7&&view==12){at=ANCHOR.add(0,8,-28);target=ANCHOR.add(0,1,0);}
                    if(view==14)target=at.add(0,0,-160);
                }
                if(view==16){at=ANCHOR.add(5,2,5);target=at.add(0,160,0);}
                if(scenic()==21){
                    mc.level.setDayTime(day);
                    var solar=ScenicSunHalo.solar(new ScenicAurora.Point(0,160,0),mc.level.getSunAngle(0));
                    target=at.add(solar.x(),solar.y(),solar.z());
                    if(view==14)target=at.add(0,0,160);
                }
                final Vec3 cameraAt=at;
                double horizontal=Math.hypot(target.x-at.x,target.z-at.z);
                float yaw=horizontal<.01?(float)Math.toDegrees(angle):(float)Math.toDegrees(Math.atan2(-(target.x-at.x),target.z-at.z));
                float pitch=(float)-Math.toDegrees(Math.atan2(target.y-at.y,horizontal));
                double eye=mc.player.getEyeHeight();
                weather=mc.getSingleplayerServer().submit(()->{
                    var l=mc.getSingleplayerServer().overworld();l.setDayTime(day);l.setWeatherParameters(6000,6000,rain,false);
                    var player=mc.getSingleplayerServer().getPlayerList().getPlayers().get(0);
                    player.teleportTo(l,cameraAt.x,cameraAt.y-eye,cameraAt.z,yaw,pitch);
                    if(view==16)for(int x=-12;x<=12;x++)for(int z=-12;z<=12;z++)
                        l.setBlock(net.minecraft.core.BlockPos.containing(cameraAt.x+x,cameraAt.y+5,cameraAt.z+z),net.minecraft.world.level.block.Blocks.STONE.defaultBlockState(),3);
                    if(scenic()==2&&view==13)for(int xx=-3;xx<=3;xx++)for(int zz=14;zz<=20;zz++)for(int yy=-60;yy<=-58;yy++)
                        l.setBlock(new net.minecraft.core.BlockPos(xx,yy,zz),(yy==-58?net.minecraft.world.level.block.Blocks.GRASS_BLOCK:net.minecraft.world.level.block.Blocks.DIRT).defaultBlockState(),3);
                    if(view==18)for(int x=-32;x<=32;x++)for(int z=-32;z<=32;z++)l.setBlock(new net.minecraft.core.BlockPos(x,-61,z),net.minecraft.world.level.block.Blocks.STONE.defaultBlockState(),3);
                });
                mc.setCameraEntity(mc.player);

            }
            if(!weather.isDone())return;weather.join();
            // Network weather interpolation is intentionally bypassed only for stable screenshot comparison.
            mc.level.setDayTime(day(view));mc.level.setRainLevel(scenic()==7?(view==8?0:1):(view==8?1:0));mc.level.setThunderLevel(0);
            if(stage%2==1&&settle==0){
                long age=scenic()==8&&view==12?25:scenic()==8&&view==13?packet.duration()-120:view==9?Math.min(1000,packet.duration()-160):Math.min(600,packet.duration()/2);
                var p=new Cod3VisualPacket(packet.dimension(),packet.template(),-1,packet.seed(),mc.level.getGameTime()-age,packet.duration(),packet.scale(),packet.origin(),packet.direction(),packet.sequence(),(int)age);
                Cod3VfxRenderer.receive(p);Cod3VfxRenderer.receive(p);
                require(active().size()==1,"duplicate sync stays a single scene "+label(view));
            }
            settle++;
        }catch(Throwable t){fail(t);}
    }
    @SuppressWarnings("unchecked") private static List<Cod3VisualPacket> active()throws Exception{var f=Cod3VfxRenderer.class.getDeclaredField("ACTIVE");f.setAccessible(true);return (List<Cod3VisualPacket>)f.get(null);}
    private static void clear()throws Exception{active().clear();}
    @SubscribeEvent public static void capture(TickEvent.RenderTickEvent e){
        if(!Boolean.getBoolean("dynasty.auroraQa")||done||e.phase!=TickEvent.Phase.END||settle<(stage/(2*SCENES.length)>=16?100:40)||stage>=views()*2*SCENES.length)return;
        try{
            int view=stage/(2*SCENES.length);packet=PACKETS.get(scenic());var mc=Minecraft.getInstance();
            if(view==16){
                require(mc.level.getBlockState(net.minecraft.core.BlockPos.containing(5,-53,5)).is(net.minecraft.world.level.block.Blocks.STONE),"roof exists in actual client world");
                if(scenic()==7)require(Double.isNaN(ScenicFireflyRenderer.ground(mc.level,4,4,ANCHOR.y)),"roof cannot emit fireflies or veins");
                if(scenic()==19){
                    var surface=ScenicLeafRenderer.column(mc.level,4,4,ANCHOR.y);
                    require(surface!=null&&surface.ground()==8&&surface.canopy()==11,"loaded roof is leaf landing surface, including refreshed chunks");
                }
            }
            if(view==18)require(Double.isNaN(ScenicFireflyRenderer.ground(mc.level,-4,-4,ANCHOR.y)),"bare stone does not emit grass light");
            if(scenic()==2){
                if(view==13)require(ScenicArrayRenderer.ground(mc.level,0,17,ANCHOR.y)==3,"array follows actual raised grass fixture");
                if(view==16)require(Double.isNaN(ScenicArrayRenderer.ground(mc.level,4,4,ANCHOR.y)),"array marks do not emit through roof");
                if(view==0||view==10){
                    require(mc.getSoundManager().getSoundEvent(new net.minecraft.resources.ResourceLocation("dynasty","scenic_ancient_array"))!=null,"original chant registered after resource load/reload");
                    try(var audio=mc.getResourceManager().open(new net.minecraft.resources.ResourceLocation("dynasty","sounds/scenic/ancient_array.ogg"))){
                        require(new String(audio.readNBytes(4),java.nio.charset.StandardCharsets.US_ASCII).equals("OggS"),"original OGG resource loads silently");
                    }
                }
            }
            require(GL11.glGetError()==GL11.GL_NO_ERROR,"actual world GL frame "+stage);
            try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){
                image.writeToFile(OUT.resolve(String.format(Locale.ROOT,"%02d-scenic%d-%s-%s.png",stage,scenic(),label(view),stage%2==0?"off":"on")));
                int[] pixels=pixels(image);
                if(stage%2==0)baseline=pixels;
                else{
                    int green=0;int tileColumns=(image.getWidth()+15)/16;int[] dense=new int[tileColumns*((image.getHeight()+15)/16)];for(int i=0;i<pixels.length;i++){
                        int a=baseline[i],b=pixels[i];int dg=(b>>8&255)-(a>>8&255),db=(b>>16&255)-(a>>16&255);
                        // Moving vanilla blue rain is not an aurora. Count its distinctive jade pixels.
                        int red=b&255,g=b>>8&255,blue=b>>16&255;
                        int dr=(b&255)-(a&255);
                        // Translucent jade cores retain a strong green excess, but little red/blue separation.
                        boolean skyColor=scenic()==2?g>red+3&&g>blue+8&&red>=blue+1:scenic()==8?blue>red+8&&g>red+15&&blue-g<55:scenic()==7?g>100&&g>red+12&&g>blue+25:scenic()==19?(view==16||red>120&&g>90)&&red>blue+25&&g>blue+15:scenic()==21?red>150&&dr-db>12:scenic()==20?red>blue+7&&g>blue+3:g>blue+4&&g>red+6;
                        // Daytime silver water darkens blue sky while moving it toward cyan; night water brightens it.
                        boolean changed=scenic()==8?(view==7?dg>8&&db>3:db< -12&&dg-db>12):dg>8&&(scenic()==21||scenic()==19?dr>10:db>3);
                        if(changed&&skyColor){green++;if(scenic()==8)dense[(i/image.getWidth()/16)*tileColumns+(i%image.getWidth()/16)]++;}
                    }
                    // A coherent water curtain fills 16x16 tiles; scattered moving vanilla rain does not.
                    if(scenic()==8){green=0;for(int pixelsInTile:dense)if(pixelsInTile>=224)green+=pixelsInTile;}
                    if(suppressed(view))require(green<300,"expected absence of production sky pixels "+label(view)+" delta="+green);
                    else require(green>(scenic()==20||scenic()==19||scenic()==7?20:200),"visible production sky pixels "+label(view)+" delta="+green);
                }
            }
            stage++;configured=false;settle=0;
        }catch(Throwable t){fail(t);}
    }
    private static int[] pixels(NativeImage image){int[] p=new int[image.getWidth()*image.getHeight()];for(int y=0;y<image.getHeight();y++)for(int x=0;x<image.getWidth();x++)p[y*image.getWidth()+x]=image.getPixelRGBA(x,y);return p;}
    private static void fail(Throwable t){done=true;t.printStackTrace();try{Files.writeString(OUT.resolve("FAIL.txt"),t.toString());Files.write(OUT.resolve("partial.txt"),RESULTS);}catch(Exception ignored){}Minecraft.getInstance().stop();}
}
