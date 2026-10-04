package com.dynasty.client;

import com.dynasty.client.character.DynastyCharacterModel;
import com.dynasty.client.character.DynastyCharacterModel.Role;
import com.dynasty.entity.DynastyEntities;
import com.google.gson.*;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.joml.Vector3f;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Disposable integrated-server QA. Exports the same posed rig, then records real world framebuffers. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class CharacterWorldQa {
    private static boolean started,done;
    private static CompletableFuture<Void> setup;
    private static CompletableFuture<Void> arenaSetup;
    private static int movementTicks;
    private static net.minecraft.world.phys.Vec3 segmentStart;
    private static boolean jumped,sprinted,crouched,used;
    private static int ticks,stage,wait;
    private static final Path OUT=Path.of(System.getProperty("dynasty.characterQa.output","build/character-world-qa/results"));
    private static final long DEADLINE=System.nanoTime()+360_000_000_000L;
    private static final String[] VIEWS={"front","left","right","back","45","rear45"};
    private static final List<String> LOG=new ArrayList<>();
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e) {
        if(!Boolean.getBoolean("dynasty.characterQa")||done||e.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try {
            if(System.nanoTime()>DEADLINE)throw new AssertionError("QA timed out");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen) {
                if(!mc.gameDirectory.getCanonicalPath().endsWith("/build/character-world-qa/client"))throw new AssertionError("Not a disposable QA directory");
                started=true;Files.createDirectories(OUT);exportModels();
                mc.options.renderDistance().set(4);mc.options.fov().set(36);mc.options.pauseOnLostFocus=false;
                GameRules rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);
                var settings=new LevelSettings("Dynasty character QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT);
                mc.createWorldOpenFlows().createFreshLevel("characters-"+System.currentTimeMillis(),settings,new WorldOptions(42,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null||++ticks<40)return;
            if(setup==null) {
                setup=mc.getSingleplayerServer().submit(()->{
                    var server=mc.getSingleplayerServer();var world=server.overworld();world.setDayTime(6000);world.getGameRules().getRule(GameRules.RULE_DAYLIGHT).set(false,server);
                    var player=server.getPlayerList().getPlayers().get(0);player.teleportTo(world,0,-60,-5,0,0);
                    var types=List.of(DynastyEntities.ARCHER.get(),DynastyEntities.REBEL_SOLDIER.get(),DynastyEntities.ROYAL_GUARD.get(),DynastyEntities.REBEL_GENERAL.get());
                    for(int i=0;i<types.size();i++) {
                        Mob mob=(Mob)types.get(i).create(world);mob.setUUID(new UUID(1234,i+18));mob.moveTo(i*8,-60,0,0,0);mob.setYHeadRot(0);mob.setNoAi(true);mob.setPersistenceRequired();world.addFreshEntity(mob);
                    }
                });return;
            }
            if(!setup.isDone())return;setup.join();if(mc.screen!=null)mc.setScreen(null);
            if(stage>=24){movement(mc);return;}
            if(wait==0) {
                int role=stage/6,view=stage%6;double angle=Math.toRadians(new double[]{0,-90,90,180,45,135}[view]),r=5.1;
                var camera=new ArmorStand(mc.level,role*8+Math.sin(angle)*r,-61.05,Math.cos(angle)*r);
                camera.setYRot((float)(180-Math.toDegrees(angle)));camera.setXRot(0);camera.setYHeadRot(camera.getYRot());camera.yHeadRotO=camera.getYRot();camera.setOldPosAndRot();
                mc.options.hideGui=true;mc.options.setCameraType(CameraType.FIRST_PERSON);mc.setCameraEntity(camera);
            }
            wait++;
        }catch(Throwable err){finish(mc,err);}
    }
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent e) {
        if(!Boolean.getBoolean("dynasty.characterQa")||done||stage>=24||e.phase!=TickEvent.Phase.END||wait<25)return;
        var mc=Minecraft.getInstance();if(mc.getOverlay()!=null||mc.level==null)return;
        try {
            String name=Role.values()[stage/6].name().toLowerCase()+"-world-"+VIEWS[stage%6];
            try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){image.writeToFile(OUT.resolve(name+".png"));}
            LOG.add("Captured "+name+" FPS="+mc.getFps());
            ++stage;wait=0;
        }catch(Throwable err){finish(mc,err);}
    }
    private static void movement(Minecraft mc)throws Exception {
        if(arenaSetup==null) {
            mc.setCameraEntity(mc.player);mc.options.hideGui=false;
            arenaSetup=mc.getSingleplayerServer().submit(()->com.dynasty.ritual.MovementClientFixture.enter(mc.getSingleplayerServer().getPlayerList().getPlayers().get(0)));return;
        }
        if(!arenaSetup.isDone())return;arenaSetup.join();
        if(!mc.level.dimension().equals(com.dynasty.ritual.ZhenyuanArena.DIMENSION))return;
        int t=movementTicks++;
        if(t==0){mc.player.setYRot(180);mc.player.setXRot(0);segmentStart=mc.player.position();}
        mc.options.keyUp.setDown(t<40||t>=160&&t<240||t>=280&&t<320);
        mc.options.keyDown.setDown(t>=40&&t<80||t>=240&&t<280);
        mc.options.keyLeft.setDown(t>=80&&t<120);mc.options.keyRight.setDown(t>=120&&t<160);
        mc.options.keyJump.setDown(t>=160&&t<180);mc.options.keySprint.setDown(t>=200&&t<240);mc.options.keyShift.setDown(t>=240&&t<280);
        if(t>=160&&t<200&&mc.player.getY()>65.4)jumped=true;
        if(t>=200&&t<240&&mc.player.isSprinting())sprinted=true;
        if(t>=240&&t<280&&mc.player.isShiftKeyDown())crouched=true;
        if(t>0&&t<=320&&t%40==0) {
            double distance=mc.player.position().distanceTo(segmentStart);
            if(distance<.6)throw new AssertionError("Client movement blocked, segment "+(t/40)+" distance="+distance);
            LOG.add("Real client input segment "+(t/40)+" moved "+distance+" blocks; y="+mc.player.getY());segmentStart=mc.player.position();
        }
        if(t==325)mc.gameMode.useItem(mc.player,net.minecraft.world.InteractionHand.MAIN_HAND);
        mc.options.keyUse.setDown(t>=325&&t<345);
        if(t>=326&&mc.player.isUsingItem())used=true;
        if(t==350){mc.player.setYRot(217);mc.player.setXRot(-18);}
        if(t==355) {
            if(!jumped||!sprinted||!crouched||!used)throw new AssertionError("Controls: jump="+jumped+" sprint="+sprinted+" crouch="+crouched+" use="+used);
            if(Math.abs(mc.player.getYRot()-217)>1||Math.abs(mc.player.getXRot()+18)>1)throw new AssertionError("Look was re-anchored");
            LOG.add("PASS: real WASD/jump/sprint/sneak/bow/look input through INTRO and COMBAT on an integrated server.");
            try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){image.writeToFile(OUT.resolve("arena-free-movement-world.png"));}
            finish(mc,null);
        }
    }
    private static void exportModels()throws Exception {
        var models=new JsonArray();
        for(Role role:Role.values()) {
            var m=new DynastyCharacterModel<Mob>(role);
            for(String side:List.of("left","right"))for(String joint:List.of("shoulder","upper_arm","elbow","forearm","wrist","hand","thigh","knee","shin","ankle","foot"))
                if(!m.jointNames().contains(side+"_"+joint))throw new AssertionError("Missing joint "+side+joint);
            if(m.boxCount()>320)throw new AssertionError("Over cube budget "+role+":"+m.boxCount());
            LOG.add(role+" boxes="+m.boxCount()+" joints="+m.jointNames().size());
            for(int variant=0;variant<3;variant++) {
                m.pose(0,0,0,0,0,0,0,0,role==Role.ARCHER?1:0,variant,true);
                models.add(export(m,role.name().toLowerCase()+(variant==0?"":"-variant"+variant)));
            }
            for(int frame=0;frame<5;frame++) {
                m.pose(frame*2,.8f,frame*5,0,0,frame*.2f,0,0,role==Role.ARCHER?frame*.25f:0,0,true);
                models.add(export(m,role.name().toLowerCase()+"-action"+frame));
            }
        }
        JsonObject json=new JsonObject();json.add("models",models);Files.writeString(OUT.resolve("meshes.json"),new Gson().toJson(json));
    }
    private static JsonObject export(DynastyCharacterModel<?> m,String name) {
        List<Integer> palette=new ArrayList<>();JsonArray positions=new JsonArray(),normals=new JsonArray(),materials=new JsonArray();
        float[] min={Float.MAX_VALUE,Float.MAX_VALUE,Float.MAX_VALUE},max={-Float.MAX_VALUE,-Float.MAX_VALUE,-Float.MAX_VALUE};
        collect(m.root,new PoseStack(),palette,positions,normals,materials,min,max);
        JsonObject out=new JsonObject();out.addProperty("id",name);out.addProperty("name",name);out.add("positions",positions);out.add("normals",normals);out.add("materialIndices",materials);
        JsonArray paints=new JsonArray();for(int c:palette){JsonObject p=new JsonObject();JsonArray rgb=new JsonArray();rgb.add(((c>>16)&255)/255f);rgb.add(((c>>8)&255)/255f);rgb.add((c&255)/255f);p.add("rgb",rgb);paints.add(p);}out.add("materials",paints);
        JsonObject bounds=new JsonObject();bounds.add("min",new Gson().toJsonTree(min));bounds.add("max",new Gson().toJsonTree(max));out.add("bounds",bounds);return out;
    }
    private static void collect(DynastyCharacterModel.Joint j,PoseStack pose,List<Integer> palette,JsonArray pos,JsonArray normals,JsonArray materials,float[] min,float[] max) {
        if(!j.visible)return;pose.pushPose();j.transform(pose);
        for(var b:j.boxes) {
            if(!palette.contains(b.color()))palette.add(b.color());int color=palette.indexOf(b.color());
            Vector3f[] vs=new Vector3f[8];
            for(int i=0;i<8;i++) {
                var v=pose.last().pose().transformPosition(new Vector3f((b.x()+((i&1)>0?b.w():0))/16,(b.y()+((i&2)>0?b.h():0))/16,(b.z()+((i&4)>0?b.d():0))/16));
                v.y=-v.y;v.z=-v.z;vs[i]=v;
                for(int k=0;k<3;k++){min[k]=Math.min(min[k],v.get(k));max[k]=Math.max(max[k],v.get(k));}
            }
            for(int[] face:new int[][]{{0,4,6,2},{1,3,7,5},{0,1,5,4},{2,6,7,3},{0,2,3,1},{4,5,7,6}}) {
                var normal=new Vector3f(vs[face[1]]).sub(vs[face[0]]).cross(new Vector3f(vs[face[2]]).sub(vs[face[0]])).normalize();
                materials.add(color);for(int index:face){var v=vs[index];pos.add(v.x);pos.add(v.y);pos.add(v.z);normals.add(normal.x);normals.add(normal.y);normals.add(normal.z);}
            }
        }
        for(var child:j.children)collect(child,pose,palette,pos,normals,materials,min,max);pose.popPose();
    }
    private static void finish(Minecraft mc,Throwable e) {
        if(done)return;done=true;if(e!=null){e.printStackTrace();LOG.add("FAIL "+e);}else LOG.add("PASS: runtime rigs and 24 in-world views loaded in an isolated save; no launcher world touched.");
        try{Files.createDirectories(OUT);Files.write(OUT.resolve(e==null?"runtime-PASS.txt":"runtime-FAIL.txt"),LOG);}catch(Exception ignored){}
        mc.options.keyUp.setDown(false);mc.options.keyDown.setDown(false);mc.options.keyLeft.setDown(false);mc.options.keyRight.setDown(false);mc.options.keyJump.setDown(false);mc.options.keySprint.setDown(false);mc.options.keyShift.setDown(false);mc.options.keyUse.setDown(false);
        mc.setCameraEntity(mc.player);mc.stop();
    }
}
