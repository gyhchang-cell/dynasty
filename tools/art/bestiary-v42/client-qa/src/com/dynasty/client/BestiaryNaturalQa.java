package com.dynasty.client;

import com.google.gson.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.effect.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Disposable survival-player fixture: production target goals, navigation and melee.
 * No setTarget, scripted movement, swing or damage calls; not wild spawning or multiplayer.
 */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class BestiaryNaturalQa {
    private static final String[] IDS={"jade_guard","soul_soldier","thunder_envoy","merfolk","terracotta_warrior","minister"};
    private static final Path OUT=Path.of(System.getProperty("dynasty.bestiaryQa.output"));
    private static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
    private static final List<Map<String,Object>> RECORDS=new ArrayList<>();
    private static final long DEADLINE=System.nanoTime()+480_000_000_000L;
    private static boolean started,done;
    private static int stage,lastShot=-1,shots;
    private static CompletableFuture<Void> setup;
    private static volatile Mob mob;
    private static volatile UUID uuid;
    private static volatile int age,hits,targets,paths;
    private static volatile float damage;
    private static volatile double moved;
    private static Mob visual;
    private static double swing,walk;

    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e) {
        if(!Boolean.getBoolean("dynasty.bestiaryNaturalQa")||done||e.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try {
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Natural fixture timeout");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen) {
                if(!mc.gameDirectory.getCanonicalPath().contains("/build/bestiary-v42-client/run-"))throw new AssertionError("Ordinary game directory refused");
                started=true;Files.createDirectories(OUT);mc.options.pauseOnLostFocus=false;mc.options.hideGui=true;mc.options.fov().set(55);
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("bestiary-natural-fixture",new LevelSettings("Disposable AI combat",GameType.SURVIVAL,false,net.minecraft.world.Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(43,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;
            if(mc.screen!=null)mc.setScreen(null);
            if(stage>=IDS.length){finish(mc,null);return;}
            if(setup==null) {
                final int next=stage;visual=null;swing=walk=0;lastShot=-1;
                setup=mc.getSingleplayerServer().submit(()->prepare(mc,next));return;
            }
            if(!setup.isDone())return;setup.join();
            if(visual==null) {
                for(var entity:mc.level.entitiesForRendering())if(entity.getUUID().equals(uuid))visual=(Mob)entity;
                if(visual==null)return;
                if(!(mc.getEntityRenderDispatcher().getRenderer(visual) instanceof RealmCreatureRenderer))throw new AssertionError("Wrong renderer "+IDS[stage]);
                var camera=new ArmorStand(mc.level,8,-57.6,8);camera.setYRot(135);camera.setXRot(15);camera.setYHeadRot(135);camera.yHeadRotO=135;camera.setOldPosAndRot();
                mc.options.setCameraType(CameraType.FIRST_PERSON);mc.setCameraEntity(camera);
            }
            swing=Math.max(swing,visual.getAttackAnim(0));walk=Math.max(walk,visual.walkAnimation.speed());
            if(age>=220) {
                var r=new LinkedHashMap<String,Object>();r.put("id",IDS[stage]);r.put("ticks",age);r.put("natural_target_ticks",targets);r.put("navigation_path_ticks",paths);r.put("distance_from_spawn",moved);r.put("accepted_direct_damage_events",hits);r.put("total_direct_damage",damage);r.put("client_max_walk",walk);r.put("client_max_swing",swing);RECORDS.add(r);
                if(stage<5&&(targets==0||moved<2||hits==0||swing<.1||walk<.01))throw new AssertionError("Production melee fixture failed "+r);
                if(stage==5&&(hits>0||targets>0))throw new AssertionError("Friendly minister unexpectedly attacks");
                stage++;visual=null;setup=null;
            }
        }catch(Throwable t){finish(mc,t);}
    }

    private static void prepare(Minecraft mc,int index) {
        var server=mc.getSingleplayerServer();var level=server.overworld();level.setDayTime(6000);
        if(mob!=null)mob.discard();mob=null;
        if(index==0)for(int x=-15;x<=15;x++)for(int z=-15;z<=15;z++)level.setBlockAndUpdate(new BlockPos(x,-61,z),x<-5?Blocks.OAK_PLANKS.defaultBlockState():Blocks.STONE_BRICKS.defaultBlockState());
        var p=server.getPlayerList().getPlayers().get(0);p.setGameMode(GameType.SURVIVAL);p.getInventory().clearContent();p.removeAllEffects();p.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1024);p.setHealth(1024);
        // Player-only protection keeps an unarmoured fixture alive against existing high damage.
        p.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE,600,3,false,false));p.getFoodData().setFoodLevel(20);p.teleportTo(level,0,-60,-2,0,0);
        age=hits=targets=paths=0;damage=0;moved=0;
        mob=(Mob)ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("dynasty",IDS[index])).create(level);
        if(mob==null)throw new AssertionError("Missing existing entity");
        mob.moveTo(0,-60,5,180,0);mob.setPersistenceRequired();level.addFreshEntity(mob);uuid=mob.getUUID();
    }

    @SubscribeEvent public static void server(TickEvent.ServerTickEvent e) {
        if(!Boolean.getBoolean("dynasty.bestiaryNaturalQa")||done||mob==null||e.phase!=TickEvent.Phase.END)return;
        age++;if(mob.getTarget()!=null)targets++;
        if(!mob.getNavigation().isDone())paths++;
        moved=Math.max(moved,Math.hypot(mob.getX(),mob.getZ()-5));
        // Healing follows damage; never grants invulnerability or changes the mob's production stats.
        for(var p:e.getServer().getPlayerList().getPlayers())if(p.isAlive())p.setHealth(p.getMaxHealth());
    }

    @SubscribeEvent public static void damaged(LivingDamageEvent e) {
        if(!Boolean.getBoolean("dynasty.bestiaryNaturalQa")||done||mob==null)return;
        if(e.getEntity() instanceof net.minecraft.server.level.ServerPlayer&&e.getSource().getDirectEntity()==mob&&e.getAmount()>0){hits++;damage+=e.getAmount();}
    }

    @SubscribeEvent public static void render(TickEvent.RenderTickEvent e) {
        if(!Boolean.getBoolean("dynasty.bestiaryNaturalQa")||done||visual==null||stage>=IDS.length||e.phase!=TickEvent.Phase.END||age<20||age%10!=0||age==lastShot)return;
        try {
            var dir=OUT.resolve(IDS[stage]);Files.createDirectories(dir);
            try(var im=Screenshot.takeScreenshot(Minecraft.getInstance().getMainRenderTarget())){im.writeToFile(dir.resolve("ai-"+age+".png"));}
            lastShot=age;shots++;
        }catch(Throwable t){finish(Minecraft.getInstance(),t);}
    }

    private static void finish(Minecraft mc,Throwable error) {
        if(done)return;done=true;
        try {
            Files.createDirectories(OUT);var r=new LinkedHashMap<String,Object>();r.put("status",error==null?"PASS":"FAIL");r.put("scenarios",RECORDS);r.put("screenshots",shots);r.put("scope","Spawned disposable survival-player fixture. Production AI selects target, navigates and attacks without setTarget/move/swing/hurt calls. Player resistance/healing only; not natural spawning, death, multiplayer, aquatic encounter or load acceptance.");if(error!=null){r.put("error",error.toString());error.printStackTrace();}Files.writeString(OUT.resolve("result.json"),JSON.toJson(r));
        }catch(Exception ex){ex.printStackTrace();}
        if(mc.player!=null)mc.setCameraEntity(mc.player);mc.stop();
    }
}
