package com.dynasty.client;

import com.dynasty.client.character.*;
import com.dynasty.entity.*;
import com.google.gson.GsonBuilder;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RenderLivingEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Real silent renderer/load QA. Automatic art fixtures and live follow AI are not human acceptance. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class GuardArtClientQa {
    static final boolean ENABLED=Boolean.getBoolean("dynasty.guardArtQa");
    static final Path OUT=Path.of(System.getProperty("dynasty.secondaryArtQa.output"));
    static final String[] VIEWS={"front","45","side","back"};
    static final List<String> LOG=new ArrayList<>();
    static final List<Mob> fixtures=new ArrayList<>();
    static final Set<Integer> rendered=new HashSet<>();
    static final List<Double> frames=new ArrayList<>();
    static final List<Integer> visibleCounts=new ArrayList<>();
    static final List<Map<String,Object>> groupSamples=new ArrayList<>();
    static final Map<Integer,double[]> kneeRanges=new LinkedHashMap<>();
    static double nativeGripError;
    static int nativeGripSamples;
    static CompletableFuture<List<Integer>> pending;
    static List<Integer> ids=List.of();
    static boolean started,done,captured;
    static int stage=-1,settled;
    static long lastFrame,deadline=System.nanoTime()+600_000_000_000L;
    static double baselineMs;
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(!ENABLED||done||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            org.lwjgl.glfw.GLFW.glfwHideWindow(mc.getWindow().getWindow());
            if(org.lwjgl.glfw.GLFW.glfwGetWindowAttrib(mc.getWindow().getWindow(),org.lwjgl.glfw.GLFW.GLFW_VISIBLE)!=0)throw new AssertionError("Window shown");
            if(System.nanoTime()>deadline)throw new AssertionError("QA timeout");
            mc.options.getSoundSourceOptionInstance(net.minecraft.sounds.SoundSource.MASTER).set(0.0);
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                if(!mc.gameDirectory.getCanonicalPath().contains("/build/secondary-art-native/"))throw new AssertionError("Not disposable directory");
                Files.createDirectories(OUT);started=true;
                checkCrossbowGrips();
                mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(3);mc.options.fov().set(50);mc.options.hideGui=true;mc.options.bobView().set(false);mc.options.framerateLimit().set(120);
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("guard-art-"+System.currentTimeMillis(),new LevelSettings("Disposable silent guard art QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(57,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;
            if(mc.screen!=null)mc.setScreen(null);
            if(pending!=null){if(!pending.isDone())return;ids=pending.join();pending=null;settled=0;captured=false;frames.clear();visibleCounts.clear();groupSamples.clear();kneeRanges.clear();nativeGripError=0;nativeGripSamples=0;lastFrame=0;camera(mc);return;}
            if(stage<0||captured){if(stage==14){finish(mc,null);return;}stage++;pending=mc.getSingleplayerServer().submit(()->prepare(mc));return;}
            settled++;
            if(stage==14){
                // Real client forward input makes the owner's existing FollowOwnerGoal navigate.
                mc.options.keyUp.setDown(settled>=80&&settled<145);
                if(settled==80||settled==150||settled==300){
                    var sample=mc.getSingleplayerServer().submit(()->{
                        var rows=new ArrayList<Map<String,Object>>();
                        for(var mob:fixtures)rows.add(Map.of("id",mob.getId(),"position",List.of(mob.getX(),mob.getY(),mob.getZ()),"noAi",mob.isNoAi(),"navigationDone",mob.getNavigation().isDone()));
                        return Map.<String,Object>of("settled",settled,"entities",rows,"owner",mc.getSingleplayerServer().getPlayerList().getPlayers().get(0).position().toString());
                    }).join();groupSamples.add(sample);
                }
            }
        }catch(Throwable e){finish(mc,e);}
    }
    static List<Integer> prepare(Minecraft mc){
        var world=mc.getSingleplayerServer().overworld();world.setDayTime(6000);fixtures.forEach(Entity::discard);fixtures.clear();
        for(int x=-22;x<=22;x++)for(int z=-22;z<=22;z++)world.setBlockAndUpdate(new BlockPos(x,-61,z),Blocks.STONE.defaultBlockState());
        var owner=mc.getSingleplayerServer().getPlayerList().getPlayers().get(0);owner.teleportTo(world,stage==14?0:-18,-60,stage==14?-8:-18,180,0);
        int count=stage<12?1:stage==12?0:18;
        for(int i=0;i<count;i++){
            Mob mob=stage<12?DynastyEntities.ROYAL_GUARD.get().create(world):DynastyEntities.IMPERIAL_SOLDIER.get().create(world);
            int role=stage<12?stage/4:i%3;
            mob.setUUID(new UUID(5714,i+1));mob.moveTo(count==1?0:(i%6-2.5)*2.1,-60,count==1?0:(i/6-1)*2.3,0,0);mob.setYHeadRot(0);mob.setPersistenceRequired();mob.setNoAi(stage!=14);
            mob.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(role==1?Items.CROSSBOW:Items.IRON_SWORD));
            if(role==2)mob.setItemSlot(EquipmentSlot.OFFHAND,new ItemStack(Items.SHIELD));
            if(stage==14)((ImperialSoldier)mob).setOwner(owner);
            world.addFreshEntity(mob);fixtures.add(mob);
        }
        return fixtures.stream().map(Entity::getId).toList();
    }
    static void camera(Minecraft mc){
        double angle=stage<12?Math.toRadians(new double[]{0,45,90,180}[stage%4]):0,r=stage<12?5.0:20;
        var cam=new ArmorStand(mc.level,Math.sin(angle)*r,-60,Math.cos(angle)*r);
        cam.setPos(cam.getX(),-60+(stage<12?1.05:2.8)-cam.getEyeHeight(),cam.getZ());cam.setYRot((float)(180-Math.toDegrees(angle)));cam.setXRot(stage<12?0:4);cam.setYHeadRot(cam.getYRot());cam.yHeadRotO=cam.getYRot();cam.setOldPosAndRot();
        mc.options.setCameraType(CameraType.FIRST_PERSON);mc.setCameraEntity(cam);
    }
    @SubscribeEvent public static void living(RenderLivingEvent.Post<?,?> e){
        if(!ENABLED||pending!=null||!ids.contains(e.getEntity().getId()))return;
        rendered.add(e.getEntity().getId());
        if(e.getRenderer().getModel() instanceof DynastyCharacterModel<?> model){
            if(e.getEntity().getMainHandItem().is(Items.CROSSBOW)){
                nativeGripError=Math.max(nativeGripError,Math.abs(model.point("right_hand",0,.8f,-.12f).distance(model.point("left_hand",0,.8f,-.12f))-2.8/16));nativeGripSamples++;
            }
            if(stage==14&&settled>=80&&settled<=180){
                var knee=joint(model.root,"right_knee");
                var range=kneeRanges.computeIfAbsent(e.getEntity().getId(),id->new double[]{Double.POSITIVE_INFINITY,Double.NEGATIVE_INFINITY});range[0]=Math.min(range[0],knee.rx);range[1]=Math.max(range[1],knee.rx);
            }
        }
    }
    static DynastyCharacterModel.Joint joint(DynastyCharacterModel.Joint parent,String name){if(parent.name.equals(name))return parent;for(var child:parent.children){var found=joint(child,name);if(found!=null)return found;}return null;}
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent e){
        if(!ENABLED||done)return;
        if(e.phase==TickEvent.Phase.START){rendered.clear();return;}
        if(pending!=null||stage<0||captured||settled<60)return;
        var mc=Minecraft.getInstance();
        try{
            long now=System.nanoTime();if(lastFrame!=0){frames.add((now-lastFrame)/1e6);visibleCounts.add(rendered.size());}lastFrame=now;
            if(settled<(stage<12?64:340))return;
            if(stage>=12&&frames.size()<120)throw new AssertionError("Too few load frames: "+frames.size());
            var record=new LinkedHashMap<String,Object>();record.put("stage",stage);record.put("entities",ids.size());record.put("frames",frames.size());record.put("medianFrameMs",percentile(frames,.5));record.put("p95FrameMs",percentile(frames,.95));record.put("fpsCounter",mc.getFps());record.put("serverAverageTickMs",mc.getSingleplayerServer().getAverageTickTime());record.put("viewport",List.of(mc.getWindow().getWidth(),mc.getWindow().getHeight()));
            record.put("renderedCountMin",visibleCounts.stream().min(Integer::compareTo).orElse(0));record.put("renderedCountMax",visibleCounts.stream().max(Integer::compareTo).orElse(0));record.put("frameIntervalsMs",frames);record.put("renderedCounts",visibleCounts);
            record.put("scope",stage<12?"Automatic native equipped art views; not natural combat":stage==13?"18 actual guards rendered together, NoAI standing load":stage==14?"18 real ImperialSoldiers with FollowOwnerGoal and real automated client forward input; not roster slots, formation, or human gameplay":"Same warmed native scene without guards");
            if(stage<12){
                var mob=(Mob)mc.level.getEntity(ids.get(0));
                if(!(mc.getEntityRenderDispatcher().getRenderer(mob) instanceof DynastyCharacterRenderer<?> renderer))throw new AssertionError("Wrong guard renderer");
                var model=renderer.getModel();record.put("boxes",model.boxCount());record.put("joints",model.jointNames());record.put("mainHand",mob.getMainHandItem().toString());record.put("offHand",mob.getOffhandItem().toString());
                var points=new LinkedHashMap<String,Object>();for(String side:List.of("right","left")){var p=model.point(side+"_hand",0,.8f,-.12f);points.put(side+"GripModelBlocks",List.of(p.x,p.y,p.z));}record.put("grips",points);
                if(mob.getMainHandItem().is(Items.CROSSBOW)){
                    double gap=model.point("right_hand",0,.8f,-.12f).distance(model.point("left_hand",0,.8f,-.12f));record.put("supportGripSeparationBlocks",gap);
                    if(Math.abs(gap-2.8/16)>.0001)throw new AssertionError("Crossbow hands detached: "+gap);
                }
            }
            record.put("nativeGripSamples",nativeGripSamples);record.put("nativeGripMaxSeparationErrorBlocks",nativeGripError);
            if(nativeGripError>.0001)throw new AssertionError("Native walking crossbow grip drift: "+nativeGripError);
            if(stage==12)baselineMs=percentile(frames,.5);
            if(stage>=13){
                long full=visibleCounts.stream().filter(n->n==18).count();double ratio=(double)full/visibleCounts.size();record.put("all18RenderedFraction",ratio);record.put("emptySceneMedianMs",baselineMs);record.put("medianRatioToEmpty",percentile(frames,.5)/baselineMs);record.put("movementSamples",groupSamples);
                if(ratio<.8)throw new AssertionError("Not all 18 guards visible in load window: "+ratio);
                if(percentile(frames,.5)>50||percentile(frames,.95)>100)throw new AssertionError("Severe load stutter: "+record);
                if(stage==14){
                    var first=groupSamples.get(0);var last=groupSamples.get(groupSamples.size()-1);record.put("movementEvidence",List.of(first,last));
                    var a=(List<Map<String,Object>>)first.get("entities");var b=(List<Map<String,Object>>)last.get("entities");int moved=0,navigating=0;
                    for(int i=0;i<a.size();i++){
                        var p=(List<Double>)a.get(i).get("position");var q=(List<Double>)b.get(i).get("position");double dx=p.get(0)-q.get(0),dz=p.get(2)-q.get(2);if(Math.hypot(dx,dz)>1)moved++;
                        if(Boolean.TRUE.equals(a.get(i).get("noAi"))||Boolean.TRUE.equals(b.get(i).get("noAi")))throw new AssertionError("Moving guard had NoAI");
                        if(Boolean.FALSE.equals(a.get(i).get("navigationDone")))navigating++;
                    }
                    record.put("guardsMovedOver1Block",moved);record.put("guardsNavigatingAtFirstSample",navigating);
                    if(moved<12||navigating<1)throw new AssertionError("Follow AI motion not observed: "+moved+" / "+navigating);
                    long knees=kneeRanges.values().stream().filter(r->r[1]-r[0]>.02).count();record.put("actualRenderedRightKneeRadians",kneeRanges);record.put("guardsWithKneeMotion",knees);
                    if(knees<12)throw new AssertionError("Native knee motion not observed in walking group: "+knees);
                }
            }
            String label=stage<12?(stage/4==0?"sword":stage/4==1?"crossbow":"shield")+"-"+VIEWS[stage%4]:new String[]{"empty-load","18-standing-load","18-follow-ai-load"}[stage-12];
            try(var shot=Screenshot.takeScreenshot(mc.getMainRenderTarget())){shot.writeToFile(OUT.resolve(String.format("%02d-%s.png",stage,label)));}
            Files.writeString(OUT.resolve(String.format("%02d-state.json",stage)),new GsonBuilder().setPrettyPrinting().create().toJson(record));LOG.add(label+" medianMs="+percentile(frames,.5)+" p95Ms="+percentile(frames,.95));captured=true;
        }catch(Throwable error){finish(mc,error);}
    }
    static double percentile(List<Double> values,double p){var sorted=new ArrayList<>(values);Collections.sort(sorted);return sorted.isEmpty()?0:sorted.get(Math.min(sorted.size()-1,(int)(p*(sorted.size()-1))));}
    static void checkCrossbowGrips()throws Exception{
        var model=new DynastyCharacterModel<Mob>(DynastyCharacterModel.Role.GUARD);double worst=0;
        for(int i=0;i<128;i++){
            model.pose(i*.31f,i%5*.2f,i*.5f,(i%9-4)*11,(i%7-3)*8,i%11/10f,i%8==0?7:0,0,0,i%3,true);model.poseHeldCrossbow();
            double gap=model.point("right_hand",0,.8f,-.12f).distance(model.point("left_hand",0,.8f,-.12f));worst=Math.max(worst,Math.abs(gap-2.8/16));
        }
        if(worst>.0001)throw new AssertionError("Two-hand grip drift: "+worst);
        Files.writeString(OUT.resolve("grip-sweep.json"),new GsonBuilder().setPrettyPrinting().create().toJson(Map.of("samples",128,"worstSeparationErrorBlocks",worst,"authoredSeparationBlocks",2.8/16,"scope","Actual Java rig, varied walking/look/attack/hurt/ensemble poses. Numerical grip stability; visual contact separately checked in native views.")));
    }
    static void finish(Minecraft mc,Throwable error){if(done)return;done=true;mc.options.keyUp.setDown(false);try{Files.createDirectories(OUT);Files.writeString(OUT.resolve(error==null?"PASS.txt":"FAIL.txt"),String.join("\n",LOG)+"\n"+(error==null?"PASS: 12 native equipment views and empty/18-standing/18-real-follow-AI load windows. Automatic client, no human or roster formation claim.":"FAIL: "+error)+"\n");if(error!=null)error.printStackTrace();}catch(Exception e){e.printStackTrace();}mc.stop();}
}
