package com.dynasty.client;

import com.google.gson.GsonBuilder;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Screenshot-only comparative study in a separate muted world. Never exports external assets. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class BossPowerReferenceQa {
    private static final boolean ENABLED=Boolean.getBoolean("dynasty.bossPowerReferenceQa");
    private static final Path OUT=Path.of(System.getProperty("dynasty.bossPowerReferenceQa.output","build/boss-power-reference"));
    private static final String[] IDS=System.getProperty("dynasty.bossPowerReferenceQa.entity")!=null?new String[]{System.getProperty("dynasty.bossPowerReferenceQa.entity")}:Boolean.getBoolean("dynasty.bossPowerReferenceQa.ownOnly")?new String[]{"dynasty:nine_heaven_general","dynasty:dragon_king","dynasty:dragon_emperor"}:new String[]{"cataclysm:ender_guardian","cataclysm:netherite_monstrosity","cataclysm:ignis","cataclysm:the_harbinger","cataclysm:the_leviathan","cataclysm:ancient_remnant","cataclysm:maledictus","cataclysm:scylla","dynasty:nine_heaven_general","dynasty:dragon_king","dynasty:dragon_emperor"};
    private static final double DISTANCE=Double.parseDouble(System.getProperty("dynasty.bossPowerReferenceQa.distance","12"));
    private static final boolean BOTH=Boolean.getBoolean("dynasty.bossPowerReferenceQa.both");
    private static final int VIEWS=BOTH?4:2;
    private static final List<String> LOG=new ArrayList<>();
    private static boolean started,done,captured;private static int stage=-1,entityId,settled;
    private static Mob fixture;private static CompletableFuture<Integer> pending;
    private static long deadline=System.nanoTime()+800_000_000_000L;
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent ev){
        if(!ENABLED||done||ev.phase!=TickEvent.Phase.END)return;var mc=Minecraft.getInstance();
        try{
            org.lwjgl.glfw.GLFW.glfwHideWindow(mc.getWindow().getWindow());
            if(System.nanoTime()>deadline)throw new AssertionError("Reference timeout "+stage);
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                if(!mc.gameDirectory.getCanonicalPath().contains("/build/boss-eight-native/"))throw new AssertionError("Normal save refused");
                started=true;Files.createDirectories(OUT);mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(4);mc.options.fov().set(70);mc.options.hideGui=true;mc.options.bobView().set(false);mc.options.getSoundSourceOptionInstance(net.minecraft.sounds.SoundSource.MASTER).set(0.0);
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("reference-"+System.currentTimeMillis(),new LevelSettings("Disposable Cataclysm reference",GameType.CREATIVE,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(57,false,false),reg->reg.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
            if(pending!=null){if(!pending.isDone())return;entityId=pending.join();pending=null;settled=0;captured=false;return;}
            if(stage<0||captured){if(stage==IDS.length*VIEWS-1){finish(mc,null);return;}stage++;pending=mc.getSingleplayerServer().submit(()->{try{return prepare(mc);}catch(Exception e){throw new RuntimeException(e);}});return;}
            if(!(mc.level.getEntity(entityId) instanceof Mob mob))return;
            if(++settled==25)camera(mc,mob);
        }catch(Throwable e){finish(mc,e);}
    }
    private static int prepare(Minecraft mc)throws Exception{
        var server=mc.getSingleplayerServer();var world=server.overworld();world.setDayTime(6000);suppressAmbientWorld(mc,world);
        var clean=new ArrayList<Entity>();for(var e:world.getAllEntities())if(!(e instanceof net.minecraft.server.level.ServerPlayer))clean.add(e);clean.forEach(Entity::discard);
        for(int x=-24;x<=24;x++)for(int z=-24;z<=24;z++)world.setBlockAndUpdate(new BlockPos(x,-61,z),((x+z)%7==0?Blocks.STONE_BRICKS:Blocks.GRASS_BLOCK).defaultBlockState());
        var key=new ResourceLocation(IDS[stage/VIEWS]);var type=ForgeRegistries.ENTITY_TYPES.getValue(key);if(type==null)throw new AssertionError(key);
        fixture=(Mob)type.create(world);fixture.moveTo(0,-60,0,0,0);fixture.setNoAi(true);fixture.setNoGravity(true);fixture.setSilent(true);fixture.setPersistenceRequired();
        if(key.getPath().equals("netherite_monstrosity"))fixture.getClass().getMethod("setIsAwaken",boolean.class).invoke(fixture,true);
        if(key.getPath().equals("ancient_remnant"))fixture.getClass().getMethod("setNecklace",boolean.class).invoke(fixture,true);
        if(key.getPath().equals("ignis"))fixture.getClass().getMethod("setIsShield",boolean.class).invoke(fixture,true);
        world.addFreshEntity(fixture);
        double playerX=-Math.max(2.65,fixture.getBbWidth()/2+1.3);
        for(var p:server.getPlayerList().getPlayers())p.teleportTo(world,playerX,-60,0,180,0);
        return fixture.getId();
    }
    private static void camera(Minecraft mc,Mob mob){
        double yaw=(BOTH?stage%4/2:stage%2)==0?0:45,a=Math.toRadians(yaw),d=DISTANCE;
        var cam=new ArmorStand(mc.level,Math.sin(a)*d,-60,Math.cos(a)*d);cam.setPos(cam.getX(),-60+1.62-cam.getEyeHeight(),cam.getZ());cam.setNoGravity(true);cam.setYRot((float)(180-yaw));cam.setXRot(-7);cam.setYHeadRot(cam.getYRot());cam.yHeadRotO=cam.getYRot();cam.setOldPosAndRot();mc.options.setCameraType(CameraType.FIRST_PERSON);mc.setCameraEntity(cam);
        BossHumanAura.setReviewSuppressed(!(BOTH?stage%2==1:Boolean.getBoolean("dynasty.bossPowerReferenceQa.ownEffects")));mc.particleEngine.setLevel(mc.level);
    }
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent ev){
        if(!ENABLED||done||captured||pending!=null||stage<0||ev.phase!=TickEvent.Phase.END||settled<120)return;
        var mc=Minecraft.getInstance();if(mc.level==null||!(mc.level.getEntity(entityId) instanceof Mob mob))return;
        try{
            clearScenicVisuals(mc);var renderer=mc.getEntityRenderDispatcher().getRenderer(mob);var id=IDS[stage/VIEWS];boolean fx=BOTH?stage%2==1:Boolean.getBoolean("dynasty.bossPowerReferenceQa.ownEffects");var name=id.replace(':','_')+((BOTH?stage%4/2:stage%2)==0?"-front":"-45")+(BOTH?(fx?"-on":"-off"):"");
            var record=new LinkedHashMap<String,Object>();record.put("id",id);record.put("renderer",renderer.getClass().getName());record.put("dynastyAuraEnabled",fx);record.put("auraEmissionRequests",BossHumanAura.reviewEmissions());var scene=new ArrayList<Object>();for(var e:mc.level.entitiesForRendering()){var info=new LinkedHashMap<String,Object>();info.put("type",String.valueOf(ForgeRegistries.ENTITY_TYPES.getKey(e.getType())));info.put("position",e.position().toString());info.put("id",e.getId());if(e instanceof Mob m){info.put("noAI",m.isNoAi());info.put("target",m.getTarget()==null?null:m.getTarget().getId());}scene.add(info);}record.put("sceneEntities",scene);
            var fxCounts=new LinkedHashMap<String,Integer>();for(String[] entry:new String[][]{{"com.dynasty.client.Cod3VfxRenderer","ACTIVE"},{"com.dynasty.client.ClientBowEffects","ARROWS"},{"com.dynasty.client.ClientBowEffects","IMPACTS"},{"com.dynasty.worldevent.client.WorldEventVisuals","STATES"},{"com.dynasty.client.ImperialWeaponRenderer","IMPACTS"}}){var field=Class.forName(entry[0]).getDeclaredField(entry[1]);field.setAccessible(true);var value=field.get(null);fxCounts.put(entry[0]+"."+entry[1],value instanceof Collection<?> c?c.size():value instanceof Map<?,?> m?m.size():-1);}record.put("separateVisualCounts",fxCounts);var field=Class.forName("com.dynasty.client.Cod3VfxRenderer").getDeclaredField("ACTIVE");field.setAccessible(true);record.put("separateVisualPackets",field.get(null).toString());record.put("width",mob.getBbWidth());record.put("height",mob.getBbHeight());record.put("cameraDistance",DISTANCE);record.put("fov",70);record.put("eyeHeight",1.62);record.put("pitch",-7);record.put("yaw",(BOTH?stage%4/2:stage%2)==0?0:45);record.put("light","vanilla day 6000; no shader/resource pack");record.put("state","NoAI idle; production models. Monstrosity awakened, Remnant necklace active, Ignis shield raised. Not a natural fight capture.");
            Files.writeString(OUT.resolve(name+".json"),new GsonBuilder().setPrettyPrinting().create().toJson(record));
            try(var shot=Screenshot.takeScreenshot(mc.getMainRenderTarget())){shot.writeToFile(OUT.resolve(name+".png"));}
            LOG.add(name);Files.writeString(OUT.resolve("progress.txt"),String.join("\n",LOG));captured=true;
        }catch(Throwable e){finish(mc,e);}
    }
    static void suppressAmbientWorld(Minecraft mc,net.minecraft.server.level.ServerLevel world)throws Exception{
        if(!mc.gameDirectory.getCanonicalPath().contains("/build/boss-eight-native/"))throw new AssertionError("Ambient QA refuses normal save");
        var scenic=com.dynasty.cod3.ScenicEvents.get(world);
        var active=scenic.getClass().getDeclaredField("active");active.setAccessible(true);((Collection<?>)active.get(scenic)).clear();
        var cooldown=scenic.getClass().getDeclaredField("cooldown");cooldown.setAccessible(true);
        @SuppressWarnings("unchecked") var regions=(Map<Long,Long>)cooldown.get(scenic);
        for(int x=-2;x<=2;x++)for(int z=-2;z<=2;z++)regions.put(net.minecraft.world.level.ChunkPos.asLong(x,z),world.getGameTime());
        scenic.setDirty();
    }
    static void clearScenicVisuals(Minecraft mc)throws Exception{
        if(!mc.gameDirectory.getCanonicalPath().contains("/build/boss-eight-native/"))throw new AssertionError("Ambient QA refuses normal save");
        var field=Class.forName("com.dynasty.client.Cod3VfxRenderer").getDeclaredField("ACTIVE");field.setAccessible(true);
        ((Collection<?>)field.get(null)).removeIf(p->p instanceof com.dynasty.cod3.Cod3VisualPacket packet&&packet.sequence().startsWith("scenic_"));
    }
    private static void finish(Minecraft mc,Throwable e){if(done)return;done=true;try{Files.createDirectories(OUT);Files.writeString(OUT.resolve(e==null?"PASS.txt":"FAIL.txt"),String.join("\n",LOG)+"\n"+(e==null?"PASS "+LOG.size()+" reference/own screenshot states":"FAIL "+e));}catch(Exception ignored){}if(e!=null)e.printStackTrace();mc.stop();}
}
