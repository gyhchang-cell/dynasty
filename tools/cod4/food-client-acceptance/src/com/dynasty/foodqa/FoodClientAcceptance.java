package com.dynasty.foodqa;

import com.google.gson.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingEntityUseItemEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

/** Drives only its own real LocalPlayer and integrated-server counterpart through native inputs. */
@Mod("dynastyfoodqa")
public final class FoodClientAcceptance {
    static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
    static final Path OUT=Path.of(System.getProperty("dynasty.foodqa.output"));
    static volatile UUID playerId;
    static volatile String currentCase="";
    static volatile Map<String,Object> serverState=Map.of();
    static final Queue<Object> EVENTS=new ConcurrentLinkedQueue<>();
    static void write(String name,Object data) throws Exception {Files.writeString(OUT.resolve(name),JSON.toJson(data)+"\n");}
    static String id(ItemStack stack) {return ForgeRegistries.ITEMS.getKey(stack.getItem()).toString();}
    static void require(boolean condition,String why) {if(!condition)throw new AssertionError(why);}
    static ItemStack item(String id,int count) {return new ItemStack(Objects.requireNonNull(ForgeRegistries.ITEMS.getValue(new ResourceLocation(id))),count);}
    static List<Object> effects(net.minecraft.world.entity.LivingEntity p) {
        return p.getActiveEffects().stream().map(e->(Object)Map.of("id",ForgeRegistries.MOB_EFFECTS.getKey(e.getEffect()).toString(),"duration",e.getDuration(),"amplifier",e.getAmplifier())).toList();
    }
    static Map<String,Object> state(net.minecraft.world.entity.player.Player p) {
        var s=new LinkedHashMap<String,Object>();s.put("case",currentCase);s.put("uuid",p.getUUID().toString());s.put("class",p.getClass().getName());
        s.put("worldTime",p.level().getGameTime());s.put("using",p.isUsingItem());s.put("useTicks",p.getTicksUsingItem());s.put("remainingUseTicks",p.getUseItemRemainingTicks());
        s.put("main",id(p.getMainHandItem()));s.put("mainCount",p.getMainHandItem().getCount());s.put("off",id(p.getOffhandItem()));s.put("offCount",p.getOffhandItem().getCount());
        s.put("usedHand",p.getUsedItemHand().toString());s.put("health",p.getHealth());s.put("food",p.getFoodData().getFoodLevel());s.put("saturation",p.getFoodData().getSaturationLevel());s.put("effects",effects(p));
        s.put("position",List.of(p.getX(),p.getY(),p.getZ()));s.put("dimension",p.level().dimension().location().toString());s.put("yaw",p.getYRot());s.put("pitch",p.getXRot());
        s.put("cooldownMain",p.getCooldowns().isOnCooldown(p.getMainHandItem().getItem()));s.put("cooldownOff",p.getCooldowns().isOnCooldown(p.getOffhandItem().getItem()));
        if(p instanceof ServerPlayer sp) {
            s.put("guide",sp.getPersistentData().getCompound("cod4Guide").toString());s.put("qiUntil",sp.getPersistentData().getLong("cod4QiUntil"));s.put("rage",sp.getPersistentData().getInt("cod4Rage"));
            s.put("examWineUntil",sp.getPersistentData().getLong("cod4ExamWine"));s.put("antidoteUntil",sp.getPersistentData().getLong("cod4Antidote"));s.put("warmUntil",sp.getPersistentData().getLong("cod4WarmUntil"));
            try{s.put("examAnswerMillis",Class.forName("com.dynasty.DynastyKeju").getMethod("answerDurationMillis",net.minecraft.world.entity.player.Player.class).invoke(null,p));}catch(Exception e){s.put("examProbeError",e.toString());}
            var targets=sp.serverLevel().getEntitiesOfClass(Zombie.class,sp.getBoundingBox().inflate(40),z->z.getTags().contains("foodqa"));
            s.put("targets",targets.stream().map(z->Map.of("uuid",z.getUUID().toString(),"health",z.getHealth(),"fireTicks",z.getRemainingFireTicks(),"effects",effects(z),"targetIsPlayer",z.getTarget()==p)).toList());
        }
        return s;
    }
    @Mod.EventBusSubscriber(modid="dynastyfoodqa")
    public static final class NativeEvidence {
        static boolean owned(net.minecraft.world.entity.LivingEntity p){return p instanceof ServerPlayer&&p.getUUID().equals(playerId)&&!currentCase.isEmpty();}
        static void record(String kind,net.minecraft.world.entity.LivingEntity e,ItemStack stack,int remaining) {
            if(!owned(e))return;
            EVENTS.add(Map.of("case",currentCase,"kind",kind,"item",id(stack),"count",stack.getCount(),"durationRemaining",remaining,"state",state((ServerPlayer)e)));
        }
        @SubscribeEvent public static void start(LivingEntityUseItemEvent.Start e){record("native_use_start",e.getEntity(),e.getItem(),e.getDuration());}
        @SubscribeEvent public static void stop(LivingEntityUseItemEvent.Stop e){record("native_use_stop",e.getEntity(),e.getItem(),e.getDuration());}
        @SubscribeEvent public static void finish(LivingEntityUseItemEvent.Finish e){record("native_use_finish",e.getEntity(),e.getResultStack(),e.getDuration());}
        @SubscribeEvent public static void click(PlayerInteractEvent.RightClickItem e){if(e.getEntity() instanceof ServerPlayer p)record("native_server_right_click",p,e.getItemStack(),0);}
        @SubscribeEvent public static void tick(TickEvent.ServerTickEvent e) {
            if(e.phase!=TickEvent.Phase.END||playerId==null)return;
            var server=net.minecraftforge.server.ServerLifecycleHooks.getCurrentServer();if(server==null)return;
            var p=server.getPlayerList().getPlayer(playerId);if(p!=null)serverState=state(p);
        }
    }

    @Mod.EventBusSubscriber(modid="dynastyfoodqa",value=net.minecraftforge.api.distmarker.Dist.CLIENT)
    public static final class Client {
        static boolean started,ready,done;static int ticks,readyTicks,age,phase,phaseAge;
        static String lastCommand="";static JsonObject active;static CompletableFuture<?> preparation;
        static final List<Object> TICKS=new ArrayList<>(),SHOTS=new ArrayList<>();static final Queue<String> shots=new ConcurrentLinkedQueue<>();
        static final Set<String> requested=new HashSet<>();static BlockPos base;
        static Map<String,Object> before,afterCancel;
        static Map<String,Object> entityState(Entity entity) {
            if(entity==null)return Map.of("present",false);
            return Map.of("present",true,"uuid",entity.getUUID().toString(),"entityId",entity.getId(),"type",EntityType.getKey(entity.getType()).toString(),"class",entity.getClass().getName(),"position",List.of(entity.getX(),entity.getY(),entity.getZ()));
        }
        static Map<String,Object> clientState(Minecraft m) {
            var s=new LinkedHashMap<String,Object>();s.put("case",currentCase);s.put("clientTick",ticks);s.put("age",age);s.put("phase",phase);s.put("screen",m.screen==null?"none":m.screen.getClass().getName());
            s.put("instance",m.gameDirectory.getAbsolutePath());s.put("camera",m.options.getCameraType().name());s.put("keyUseDown",m.options.keyUse.isDown());s.put("language",m.getLanguageManager().getSelected());
            s.put("cameraEntity",entityState(m.getCameraEntity()));s.put("playerEntity",entityState(m.player));
            var camera=m.gameRenderer.getMainCamera();var pos=camera.getPosition();
            s.put("renderCameraEntity",entityState(camera.getEntity()));s.put("renderCameraPosition",List.of(pos.x,pos.y,pos.z));s.put("renderCameraDetached",camera.isDetached());
            if(m.player!=null){s.put("client",state(m.player));s.put("nativeAnimation",held(m).getUseAnimation().name());s.put("nativeDuration",held(m).getUseDuration());s.put("displayName",held(m).getHoverName().getString());}
            s.put("server",serverState);return s;
        }
        static InteractionHand hand(){return active!=null&&active.has("offhand")&&active.get("offhand").getAsBoolean()?InteractionHand.OFF_HAND:InteractionHand.MAIN_HAND;}
        static ItemStack held(Minecraft m){return m.player.getItemInHand(hand());}
        static boolean food(){return active.get("kind").getAsString().equals("food");}
        static void shot(String label){if(requested.add(label))shots.add(label);}
        static void press(Minecraft m){m.options.keyUse.setDown(true);KeyMapping.click(m.options.keyUse.getKey());}
        static void release(Minecraft m){m.options.keyUse.setDown(false);if(m.player.isUsingItem())m.gameMode.releaseUsingItem(m.player);}
        static void fail(Throwable e){
            e.printStackTrace();try{write((currentCase.isEmpty()?"startup":currentCase)+"-FAIL.json",Map.of("error",e.toString(),"trace",Arrays.toString(e.getStackTrace()),"state",clientState(Minecraft.getInstance()),"events",new ArrayList<>(EVENTS)));}catch(Exception ignored){}
            release(Minecraft.getInstance());active=null;preparation=null;
        }
        static void prepare(Minecraft m,JsonObject c) {
            require(m.gameDirectory.getAbsolutePath().equals(System.getProperty("dynasty.foodqa.instance")),"Only own private profile may receive QA input");
            release(m);m.setScreen(null);m.options.hideGui=false;m.options.setCameraType(CameraType.valueOf(c.get("camera").getAsString()));
            m.player.getInventory().selected=0;currentCase=c.get("id").getAsString();active=c;age=0;phase=0;phaseAge=0;before=null;afterCancel=null;
            EVENTS.clear();TICKS.clear();SHOTS.clear();shots.clear();requested.clear();
            preparation=m.getSingleplayerServer().submit(()->{
                var p=m.getSingleplayerServer().getPlayerList().getPlayer(playerId);require(p!=null,"Real integrated player is connected");
                p.stopUsingItem();p.getInventory().clearContent();p.getInventory().selected=0;p.removeAllEffects();p.setGameMode(GameType.SURVIVAL);
                for(var i:ForgeRegistries.ITEMS.getValues())if(p.getCooldowns().isOnCooldown(i))p.getCooldowns().removeCooldown(i);
                for(String key:List.of("cod4Guide","cod4QiUntil","cod4Rage","cod4ExamWine","cod4Antidote","cod4WarmUntil","cod4WarmDimension"))p.getPersistentData().remove(key);
                p.getAttribute(Attributes.MAX_HEALTH).setBaseValue(100);p.setHealth(40);p.getFoodData().setFoodLevel(10);p.getFoodData().setSaturation(0);p.setNoGravity(true);p.setOnGround(true);
                if(base==null)base=p.blockPosition().offset(32,8,32);
                p.teleportTo(p.serverLevel(),base.getX()+.5,base.getY(),base.getZ()+.5,0,0);
                var stack=item(c.get("item").getAsString(),food()?3:16);if(c.has("warm")&&c.get("warm").getAsBoolean())stack.getOrCreateTag().putBoolean("cod4WarmWine",true);
                p.setItemInHand(hand(),stack);
                String name=c.get("item").getAsString();
                if(name.endsWith("antidote_pill")||name.endsWith("return_talisman"))p.addEffect(new MobEffectInstance(MobEffects.POISON,2000,0));
                if(name.endsWith("soul_incense")){apply(p,"yin_qi");apply(p,"soul_burn");}
                if(c.has("warm"))apply(p,"frost_vein");
                for(var z:p.serverLevel().getEntitiesOfClass(Zombie.class,p.getBoundingBox().inflate(64),z->z.getTags().contains("foodqa")))z.discard();
                var z=new Zombie(p.serverLevel());z.addTag("foodqa");z.setNoAi(true);z.setNoGravity(true);z.setSilent(true);z.setItemSlot(EquipmentSlot.HEAD,new ItemStack(Items.CARVED_PUMPKIN));
                z.getAttribute(Attributes.MAX_HEALTH).setBaseValue(5000);z.setHealth(5000);z.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);
                int distance=name.endsWith("fire_talisman")?26:name.endsWith("thunder_talisman")?28:name.endsWith("soul_talisman")?22:3;
                // A lateral food fixture stays within incense range without occluding the front camera.
                z.setPos(p.getX()+(food()?4:0),p.getY(),p.getZ()+(food()?1:distance));z.setTarget(p);p.serverLevel().addFreshEntity(z);
                p.containerMenu.broadcastChanges();serverState=state(p);
            });
        }
        static void apply(ServerPlayer p,String name){var effect=ForgeRegistries.MOB_EFFECTS.getValue(new ResourceLocation("dynasty",name));require(effect!=null,"Existing status "+name);p.addEffect(new MobEffectInstance(effect,2000,0));}
        @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e) {
            if(done||e.phase!=TickEvent.Phase.END)return;var m=Minecraft.getInstance();ticks++;
            try {
                if(!ready||m.player==null)return;
                if(active==null){Path command=OUT.resolve("command.json");if(!Files.exists(command))return;var c=JsonParser.parseString(Files.readString(command)).getAsJsonObject();String cid=c.get("id").getAsString();if(cid.equals(lastCommand))return;lastCommand=cid;Files.copy(command,OUT.resolve(cid+"-command.json"));
                    if(c.get("op").getAsString().equals("finish")){release(m);write("FINISHED.json",clientState(m));done=true;m.stop();return;}prepare(m,c);return;
                }
                if(preparation!=null){if(!preparation.isDone())return;preparation.join();preparation=null;}
                age++;phaseAge++;TICKS.add(clientState(m));
                require(age<700,"Native client case deadline (no manufactured completion)");
                if(phase==0) {
                    if(age<16||!id(held(m)).equals(active.get("item").getAsString()))return;
                    m.setScreen(null);m.mouseHandler.grabMouse();m.player.setYRot(0);m.player.setXRot(0);
                    before=clientState(m);shot("before");phase=1;phaseAge=0;return;
                }
                if(phase==1&&phaseAge==3){press(m);shot(food()?"use-start":"cast-start");}
                if(phase==1&&food()&&m.player.isUsingItem()&&m.player.getTicksUsingItem()>=8) {
                    shot("cancel-mid");release(m);phase=2;phaseAge=0;return;
                }
                if(phase==1&&!food()&&phaseAge>=5){release(m);phase=2;phaseAge=0;return;}
                if(phase==2&&phaseAge>=18){
                    afterCancel=clientState(m);shot(food()?"cancelled":"cast-result");
                    if(food()){require(held(m).getCount()==3,"Cancelled client use retains3 QA items");require(EVENTS.stream().noneMatch(v->v.toString().contains("native_use_finish")),"Cancelled use did not finish on real server");}
                    phase=3;phaseAge=0;return;
                }
                if(phase==3&&phaseAge==3){press(m);}
                if(phase==3&&food()) {
                    if(m.player.isUsingItem()&&m.player.getTicksUsingItem()>=16)shot("held-mid");
                    if(m.player.isUsingItem()&&m.player.getTicksUsingItem()>=24)shot("held-late");
                    if(held(m).getCount()==2&&serverCount()==2){release(m);phase=4;phaseAge=0;shot("completed");return;}
                }
                if(phase==3&&!food()) {
                    if(phaseAge>=8)shot("held-cast");
                    if(phaseAge>=18){release(m);phase=4;phaseAge=0;shot("released");return;}
                }
                if(phase==4&&phaseAge>=15)shot("settled");
                if(phase==4&&phaseAge>=20&&shots.isEmpty()) {
                    require(food()?held(m).getCount()==2:held(m).getCount()<16,"Real server charged original item");
                    if(food())require(EVENTS.stream().anyMatch(v->v.toString().contains("native_use_finish")),"Native connected ServerPlayer finished food use");
                    var result=new LinkedHashMap<String,Object>();result.put("case",currentCase);result.put("item",active.get("item").getAsString());result.put("kind",active.get("kind").getAsString());result.put("input",active);result.put("before",before);result.put("afterCancelOrTap",afterCancel);result.put("after",clientState(m));result.put("serverEvents",new ArrayList<>(EVENTS));result.put("captures",new ArrayList<>(SHOTS));result.put("qa_items_supplied",true);result.put("native_input_executed",true);
                    write(currentCase+"-ticks.json",TICKS);write(currentCase+"-result.json",result);active=null;
                }
            }catch(Throwable error){fail(error);}
        }
        static int serverCount(){Object v=serverState.get(hand()==InteractionHand.MAIN_HAND?"mainCount":"offCount");return v instanceof Number n?n.intValue():-1;}
        @SubscribeEvent public static void render(TickEvent.RenderTickEvent e) {
            if(done||e.phase!=TickEvent.Phase.END)return;var m=Minecraft.getInstance();
            try {
                if(m.getOverlay()!=null)return;
                if(m.screen instanceof AccessibilityOnboardingScreen)m.setScreen(new TitleScreen());
                if(m.screen!=null&&m.screen.getClass().getName().contains("LoadingErrorScreen")){write("STARTUP-FAIL.json",clientState(m));done=true;m.stop();return;}
                if(!started&&m.screen instanceof TitleScreen){
                    require(m.gameDirectory.getCanonicalPath().equals(System.getProperty("dynasty.foodqa.instance")),"Independent private profile");started=true;m.getWindow().setTitle("COD4 Food QA - independent private profile");
                    write("loaded-mods.json",net.minecraftforge.fml.ModList.get().getMods().stream().map(x->Map.of("id",x.getModId(),"version",x.getVersion().toString())).toList());
                    var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);rules.getRule(GameRules.RULE_NATURAL_REGENERATION).set(false,null);rules.getRule(GameRules.RULE_DOFIRETICK).set(false,null);
                    m.createWorldOpenFlows().createFreshLevel("food-client-qa-"+System.currentTimeMillis(),new LevelSettings("COD4 Food Client QA",GameType.SURVIVAL,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(43,true,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.NORMAL).createWorldDimensions());return;
                }
                if(m.player==null||m.level==null)return;
                if(!ready){if(++readyTicks<120)return;playerId=m.player.getUUID();m.setScreen(null);ready=true;write("READY.json",clientState(m));}
                if(active!=null&&!shots.isEmpty()) {
                    String label=shots.remove();String name=currentCase+"-"+label+".png";
                    try(var pixels=Screenshot.takeScreenshot(m.getMainRenderTarget())){pixels.writeToFile(OUT.resolve(name));}
                    var info=new LinkedHashMap<String,Object>();info.put("label",label);info.put("file",name);info.put("state",clientState(m));SHOTS.add(info);write(currentCase+"-captures.json",SHOTS);
                }
            }catch(Throwable error){fail(error);}
        }
    }
}
