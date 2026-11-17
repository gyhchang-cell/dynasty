package com.dynasty.client;

import com.google.gson.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Opt-in disposable client evidence. Not production code, not a natural-combat test. */
@Mod.EventBusSubscriber(modid="dynasty", value=Dist.CLIENT)
public final class BestiaryClientQa {
    private static final String[] IDS={"jade_guard","soul_soldier","thunder_envoy","merfolk","terracotta_warrior","minister"};
    private static final String[] VIEWS={"front","45","side","back","walk","swing"};
    private static final double[] ANGLES={0,45,90,180,35,35};
    private static final Path OUT=Path.of(System.getProperty("dynasty.bestiaryQa.output","build/bestiary-v42/client-results"));
    private static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
    private static final List<Map<String,Object>> EVIDENCE=new ArrayList<>();
    private static final long DEADLINE=System.nanoTime()+480_000_000_000L;
    private static boolean started,done,reloaded;
    private static int stage,ticks,lastShot=-1;
    private static CompletableFuture<Void> setup,reload;
    private static volatile Mob serverMob;
    private static volatile int mode,serverTicks;
    private static volatile UUID entityId;
    private static Mob clientMob;
    private static double maxWalk,maxSwing;
    private static int screenshots;

    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event) {
        if(!Boolean.getBoolean("dynasty.bestiaryQa")||done||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try {
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Isolated bestiary QA timed out");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen) {
                if(!mc.gameDirectory.getCanonicalPath().contains("/build/bestiary-v42-client/run-"))throw new AssertionError("Refusing ordinary game directory");
                started=true;Files.createDirectories(OUT);
                mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(3);mc.options.fov().set(48);mc.options.hideGui=true;
                GameRules rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("bestiary-only",new LevelSettings("Disposable bestiary checks",GameType.CREATIVE,false,net.minecraft.world.Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(42,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;
            if(mc.screen!=null)mc.setScreen(null);
            if(stage>=36) {
                if(reload==null){reload=mc.reloadResourcePacks();return;}
                if(!reload.isDone())return;reload.join();
                if(!reloaded){for(String id:IDS)checkTexture(mc,id);reloaded=true;ticks=0;}
                if(++ticks>30)finish(mc,null);return;
            }
            if(stage==35){stage++;setup=null;return;} // Civilian has no attack AI.
            if(setup==null) {
                final int current=stage;clientMob=null;maxWalk=maxSwing=0;ticks=0;lastShot=-1;
                setup=mc.getSingleplayerServer().submit(()->prepare(mc,current));return;
            }
            if(!setup.isDone())return;setup.join();
            if(clientMob==null) {
                for(var entity:mc.level.entitiesForRendering())if(entity.getUUID().equals(entityId))clientMob=(Mob)entity;
                if(clientMob==null)return;
                var renderer=mc.getEntityRenderDispatcher().getRenderer(clientMob);
                if(!(renderer instanceof RealmCreatureRenderer))throw new AssertionError("Wrong runtime renderer: "+renderer.getClass());
                String texture=renderer.getTextureLocation(clientMob).toString();
                if(!texture.equals("dynasty:textures/entity/bestiary/"+IDS[stage/6]+".png"))throw new AssertionError("Wrong texture "+texture);
                checkTexture(mc,IDS[stage/6]);
                double a=Math.toRadians(ANGLES[stage%6]);
                var camera=new ArmorStand(mc.level,Math.sin(a)*6,-61.05,Math.cos(a)*6);
                camera.setYRot((float)(180-ANGLES[stage%6]));camera.setXRot(0);camera.setYHeadRot(camera.getYRot());camera.yHeadRotO=camera.getYRot();camera.setOldPosAndRot();
                mc.options.setCameraType(CameraType.FIRST_PERSON);mc.setCameraEntity(camera);
            }
            maxWalk=Math.max(maxWalk,clientMob.walkAnimation.speed());maxSwing=Math.max(maxSwing,clientMob.getAttackAnim(0));
            if(++ticks>=65) {
                if(stage%6==4&&maxWalk<.01)throw new AssertionError("No actual client walking animation "+IDS[stage/6]);
                if(stage%6==5&&maxSwing<.1)throw new AssertionError("No server swing packet observed "+IDS[stage/6]);
                EVIDENCE.add(Map.of("id",IDS[stage/6],"view",VIEWS[stage%6],"renderer",mc.getEntityRenderDispatcher().getRenderer(clientMob).getClass().getName(),"max_walk_speed",maxWalk,"max_swing_progress",maxSwing));
                stage++;setup=null;
            }
            if(ticks%20==0)Files.writeString(OUT.resolve("state.txt"),"stage="+stage+" tick="+ticks+" screenshots="+screenshots);
        }catch(Throwable t){finish(mc,t);}
    }

    private static void prepare(Minecraft mc,int current) {
        var server=mc.getSingleplayerServer();var level=server.overworld();level.setDayTime(6000);
        if(serverMob!=null)serverMob.discard();mode=0;serverTicks=0;
        if(current==0)for(int x=-12;x<=12;x++)for(int z=-12;z<=12;z++)level.setBlockAndUpdate(new BlockPos(x,-61,z),x<-4?Blocks.OAK_PLANKS.defaultBlockState():Blocks.STONE_BRICKS.defaultBlockState());
        serverMob=(Mob)ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("dynasty",IDS[current/6])).create(level);
        if(serverMob==null)throw new AssertionError("Entity missing");
        serverMob.moveTo(0,-60,0,0,0);serverMob.setYHeadRot(0);serverMob.setNoAi(true);serverMob.setNoGravity(true);serverMob.setInvulnerable(true);serverMob.setPersistenceRequired();
        level.addFreshEntity(serverMob);entityId=serverMob.getUUID();
        double a=Math.toRadians(ANGLES[current%6]);
        var player=server.getPlayerList().getPlayers().get(0);player.teleportTo(level,-Math.cos(a)*2,-60,Math.sin(a)*2,0,0);player.getInventory().clearContent();
        mode=current%6;
    }

    @SubscribeEvent public static void serverTick(TickEvent.ServerTickEvent event) {
        if(!Boolean.getBoolean("dynasty.bestiaryQa")||done||event.phase!=TickEvent.Phase.END||serverMob==null)return;
        int age=++serverTicks;
        // Controlled fixture movement and vanilla swing broadcasts, no production AI changes.
        if(mode==4)serverMob.move(MoverType.SELF,new net.minecraft.world.phys.Vec3(age%40<20?.045:-.045,0,0));
        if(mode==5&&age%12==0)serverMob.swing(InteractionHand.MAIN_HAND);
    }

    private static void checkTexture(Minecraft mc,String id)throws Exception {
        var path=new ResourceLocation("dynasty","textures/entity/bestiary/"+id+".png");
        String actual;
        try(var in=mc.getResourceManager().getResourceOrThrow(path).open()){actual=HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(in.readAllBytes()));}
        var expected=JSON.fromJson(Files.readString(OUT.resolve("expected-textures.json")),JsonObject.class).get(id).getAsString();
        if(!actual.equals(expected))throw new AssertionError("Stale resource PNG "+id);
    }

    @SubscribeEvent public static void render(TickEvent.RenderTickEvent event) {
        if(!Boolean.getBoolean("dynasty.bestiaryQa")||done||stage>=36||event.phase!=TickEvent.Phase.END||clientMob==null||ticks<24||ticks==lastShot)return;
        var mc=Minecraft.getInstance();if(mc.getOverlay()!=null)return;
        int view=stage%6;if(view<4&&(ticks<30||lastShot>=0))return;if(view>=4&&(ticks<28||ticks>60||ticks%4!=0))return;
        try {
            var dir=OUT.resolve(IDS[stage/6]);Files.createDirectories(dir);
            try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){image.writeToFile(dir.resolve(VIEWS[view]+(view<4?"":"-"+ticks)+".png"));}
            lastShot=ticks;screenshots++;
        }catch(Throwable t){finish(mc,t);}
    }

    private static void finish(Minecraft mc,Throwable error) {
        if(done)return;done=true;
        try {
            Files.createDirectories(OUT);
            var result=new LinkedHashMap<String,Object>();result.put("status",error==null?"PASS":"FAIL");result.put("screenshots",screenshots);result.put("resource_reload",reloaded);result.put("stages",EVIDENCE);result.put("scope","Real isolated Forge client: registered renderers, resource PNG hashes, standard daylight, controlled walking and vanilla server swing broadcasts. Not natural AI combat, multiplayer or load acceptance.");
            if(error!=null){error.printStackTrace();result.put("error",error.toString());}
            Files.writeString(OUT.resolve("result.json"),JSON.toJson(result));
        }catch(Exception e){e.printStackTrace();}
        if(mc.player!=null)mc.setCameraEntity(mc.player);mc.stop();
    }
}
