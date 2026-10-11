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
public final class GuardProportionClientQa {
    static final boolean ENABLED=Boolean.getBoolean("dynasty.guardProportionQa");
    static final int START_STAGE=Integer.getInteger("dynasty.guardStyleStartStage",0);
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
    static boolean liveClose(){return stage>=19&&stage<=22;}
    static int probeCounter,clearanceSamples;
    static double worstClearance;
    static DynastyCharacterModel<?> lastModel;
    static Entity cinematicCamera;
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
                checkCrossbowGrips();GuardProportionProof.verifyOrReuse(OUT);
                mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(3);mc.options.fov().set(50);mc.options.hideGui=true;mc.options.bobView().set(false);mc.options.framerateLimit().set(120);
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("guard-art-"+System.currentTimeMillis(),new LevelSettings("Disposable silent guard art QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(57,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;
            if(mc.screen!=null)mc.setScreen(null);
            if(pending!=null){if(!pending.isDone())return;ids=pending.join();pending=null;settled=0;captured=false;frames.clear();visibleCounts.clear();groupSamples.clear();kneeRanges.clear();nativeGripError=0;nativeGripSamples=0;lastFrame=0;clearanceSamples=0;worstClearance=0;lastModel=null;camera(mc);return;}
            if(stage<0||captured){if(stage==28){finish(mc,null);return;}mc.options.keyUp.setDown(false);stage=stage<0?START_STAGE:stage+1;pending=mc.getSingleplayerServer().submit(()->prepare(mc));return;}
            // The server future can finish before its entity-spawn packet arrives on the client.
            if(ids.stream().anyMatch(id->mc.level.getEntity(id)==null))return;
            settled++;
            if(stage==18||liveClose()){
                // Real client forward input makes the owner's existing FollowOwnerGoal navigate.
                mc.options.keyUp.setDown(stage==18?settled>=80&&settled<145:settled>=20&&settled<100);
                if(liveClose())camera(mc);
                if(settled==80||settled==150||settled==300){
                    var sample=mc.getSingleplayerServer().submit(()->{
                        var rows=new ArrayList<Map<String,Object>>();
                        for(var mob:fixtures)rows.add(Map.of("id",mob.getId(),"position",List.of(mob.getX(),mob.getY(),mob.getZ()),"noAi",mob.isNoAi(),"navigationDone",mob.getNavigation().isDone()));
                        return Map.<String,Object>of("settled",settled,"entities",rows,"owner",mc.getSingleplayerServer().getPlayerList().getPlayers().get(0).position().toString());
                    }).join();groupSamples.add(sample);
                    Files.writeString(OUT.resolve(String.format("%02d-server-t%d.json",stage,settled)),new GsonBuilder().setPrettyPrinting().create().toJson(sample));
                }
            }
        }catch(Throwable e){finish(mc,e);}
    }
    static List<Integer> prepare(Minecraft mc){
        var world=mc.getSingleplayerServer().overworld();world.setDayTime(6000);fixtures.forEach(Entity::discard);fixtures.clear();
        for(int x=-22;x<=22;x++)for(int z=-22;z<=22;z++)world.setBlockAndUpdate(new BlockPos(x,-61,z),Blocks.STONE.defaultBlockState());
        var owner=mc.getSingleplayerServer().getPlayerList().getPlayers().get(0);owner.teleportTo(world,stage==18||liveClose()?0:-18,-60,stage==18||liveClose()?-8:-18,180,0);owner.setInvisible(true);
        int count=stage<16||liveClose()||stage>=23?1:stage==16?0:18;
        for(int i=0;i<count;i++){
            Mob mob=stage>=23?DynastyEntities.REBEL_GENERAL.get().create(world):stage<16?DynastyEntities.ROYAL_GUARD.get().create(world):DynastyEntities.IMPERIAL_SOLDIER.get().create(world);
            int role=stage<16?stage/4:liveClose()?1:i%3;
            mob.setUUID(new UUID(5714,i+1));mob.moveTo(count==1?0:(i%6-2.5)*2.1,-60,count==1?0:(i/6-1)*2.3,0,0);mob.setYHeadRot(0);mob.setPersistenceRequired();mob.setNoAi(stage!=18&&!liveClose());
            if(stage<23)mob.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(role==1?Items.CROSSBOW:role==3?net.minecraft.core.registries.BuiltInRegistries.ITEM.get(new net.minecraft.resources.ResourceLocation("dynasty","chang_qiang")):Items.IRON_SWORD));
            if(role==2)mob.setItemSlot(EquipmentSlot.OFFHAND,new ItemStack(Items.SHIELD));
            if(stage==18||liveClose())((ImperialSoldier)mob).setOwner(owner);
            if(stage<23&&mob.getMainHandItem().isEmpty())throw new AssertionError("Missing registered weapon for role "+role);
            world.addFreshEntity(mob);fixtures.add(mob);
        }
        return fixtures.stream().map(Entity::getId).toList();
    }
    static void camera(Minecraft mc){
        boolean single=stage<16||liveClose()||stage>=23;
        double angle=stage>=23?Math.toRadians(new double[]{0,45,-90,90,180,135}[stage-23]):single?Math.toRadians(new double[]{0,45,90,180}[(stage<16?stage:stage-19)%4]):0,r=single?5.0:20,x=0,z=0,y=-60;
        if(liveClose()){var mob=(Mob)mc.level.getEntity(ids.get(0));if(mob==null)return;x=mob.getX();z=mob.getZ();y=mob.getY();angle+=Math.toRadians(-mob.yBodyRot);}
        var cam=new ArmorStand(mc.level,x+Math.sin(angle)*r,y,z+Math.cos(angle)*r);
        cam.setPos(cam.getX(),y+(single?1.05:2.8)-cam.getEyeHeight(),cam.getZ());cam.setYRot((float)(180-Math.toDegrees(angle)));cam.setXRot(single?0:4);cam.setYHeadRot(cam.getYRot());cam.yHeadRotO=cam.getYRot();cam.setOldPosAndRot();
        mc.options.setCameraType(CameraType.FIRST_PERSON);cinematicCamera=cam;
    }
    @SubscribeEvent public static void living(RenderLivingEvent.Post<?,?> e){
        if(!ENABLED||pending!=null||!ids.contains(e.getEntity().getId()))return;
        rendered.add(e.getEntity().getId());
        if(e.getRenderer().getModel() instanceof DynastyCharacterModel<?> model){
            lastModel=model;
            if(model.role!=DynastyCharacterModel.Role.GUARD)return;
            boolean crossbow=e.getEntity().getMainHandItem().is(Items.CROSSBOW);
            boolean spear="dynasty:chang_qiang".equals(net.minecraft.core.registries.BuiltInRegistries.ITEM.getKey(e.getEntity().getMainHandItem().getItem()).toString());
            if(model.rendersGuardSpear()!=spear)throw new AssertionError("Spear presentation mismatch");
            if(spear&&model.point("guard_spear",0,0,0).distance(model.point("right_hand",0,.8f,-.12f))>.00001)throw new AssertionError("Spear detached from hand");
            if(joint(model.root,"guard_bolt_case").visible!=crossbow)throw new AssertionError("Bolt case mismatch with actual equipment");
            if(++probeCounter%16==0){
                var cubes=GuardStyleProof.cubes(model);var proof=GuardStyleProof.check(cubes);GuardProportionProof.neckContact(cubes);clearanceSamples++;worstClearance=Math.max(worstClearance,proof.maxDepthBlocks());
                if(proof.overlapping()>0)throw new AssertionError("Actual rendered skirt penetration: "+proof);
            }
            if(e.getEntity().getMainHandItem().is(Items.CROSSBOW)){
                nativeGripError=Math.max(nativeGripError,Math.abs(model.point("right_hand",0,.8f,-.12f).distance(model.point("left_hand",0,.8f,-.12f))-2.8/16));nativeGripSamples++;
            }
            if((stage==18||liveClose())&&settled>=20&&settled<=180){
                var knee=joint(model.root,"right_knee");
                var range=kneeRanges.computeIfAbsent(e.getEntity().getId(),id->new double[]{Double.POSITIVE_INFINITY,Double.NEGATIVE_INFINITY});range[0]=Math.min(range[0],knee.rx);range[1]=Math.max(range[1],knee.rx);
            }
        }
    }
    static DynastyCharacterModel.Joint joint(DynastyCharacterModel.Joint parent,String name){if(parent.name.equals(name))return parent;for(var child:parent.children){var found=joint(child,name);if(found!=null)return found;}return null;}
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent e){
        if(!ENABLED||done)return;var mc=Minecraft.getInstance();
        if(e.phase==TickEvent.Phase.START){rendered.clear();if(cinematicCamera!=null)mc.setCameraEntity(cinematicCamera);return;}
        try{renderEnd(e);}finally{if(mc.player!=null)mc.setCameraEntity(mc.player);}
    }
    static void renderEnd(TickEvent.RenderTickEvent e){
        if(!ENABLED||done)return;
        if(e.phase==TickEvent.Phase.START){rendered.clear();return;}
        if(pending!=null||stage<0||captured||settled<60)return;
        var mc=Minecraft.getInstance();
        try{
            long now=System.nanoTime();if(lastFrame!=0){frames.add((now-lastFrame)/1e6);visibleCounts.add(rendered.size());}lastFrame=now;
            if(settled<(stage<16||stage>=23?64:liveClose()?85:340))return;
            if(stage>=16&&stage<=18&&frames.size()<120)throw new AssertionError("Too few load frames: "+frames.size());
            var record=new LinkedHashMap<String,Object>();record.put("stage",stage);record.put("entities",ids.size());record.put("frames",frames.size());record.put("medianFrameMs",percentile(frames,.5));record.put("p95FrameMs",percentile(frames,.95));record.put("fpsCounter",mc.getFps());record.put("serverAverageTickMs",mc.getSingleplayerServer().getAverageTickTime());record.put("viewport",List.of(mc.getWindow().getWidth(),mc.getWindow().getHeight()));
            record.put("renderedCountMin",visibleCounts.stream().min(Integer::compareTo).orElse(0));record.put("renderedCountMax",visibleCounts.stream().max(Integer::compareTo).orElse(0));record.put("frameIntervalsMs",frames);record.put("renderedCounts",visibleCounts);
            record.put("scope",stage>=23?"Automatic native preserved RebelGeneral art views; no combat or skill timing claim":stage<16?"Automatic native equipped art views; not natural combat":stage==17?"18 actual guards rendered together, NoAI standing load":stage==18?"18 real ImperialSoldiers with FollowOwnerGoal and real automated client forward input; not roster slots, formation, or human gameplay":"Same warmed native scene without guards");
            if(stage<16||liveClose()||stage>=23){
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
            if(stage==16)baselineMs=percentile(frames,.5);
            if(stage>=17&&stage<=18){
                long full=visibleCounts.stream().filter(n->n==18).count();double ratio=(double)full/visibleCounts.size();record.put("all18RenderedFraction",ratio);record.put("emptySceneMedianMs",baselineMs);record.put("medianRatioToEmpty",percentile(frames,.5)/baselineMs);record.put("movementSamples",groupSamples);
                if(ratio<.8)throw new AssertionError("Not all 18 guards visible in load window: "+ratio);
                if(percentile(frames,.5)>50||percentile(frames,.95)>100)throw new AssertionError("Severe load stutter: "+record);
                if(stage==18){
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
            String label=stage>=23?"general-"+new String[]{"front","45","left","right","back","rear45"}[stage-23]:stage<16?new String[]{"sword","crossbow","shield","spear"}[stage/4]+"-"+VIEWS[stage%4]:liveClose()?"live-walk-"+VIEWS[stage-19]:new String[]{"empty-load","18-standing-load","18-follow-ai-load"}[stage-16];
            record.put("nativeClearanceSamples",clearanceSamples);record.put("nativeWorstOverlapBlocks",worstClearance);
            record.put("spearVisible",lastModel!=null&&lastModel.rendersGuardSpear());
            record.put("boltCaseVisible",lastModel!=null&&lastModel.role==DynastyCharacterModel.Role.GUARD&&joint(lastModel.root,"guard_bolt_case").visible);
            if(liveClose()){var mob=(Mob)mc.level.getEntity(ids.get(0));record.put("actualKneeRange",kneeRanges);record.put("serverMovement",groupSamples);record.put("noAi",mob.isNoAi());record.put("bodyYaw",mob.yBodyRot);record.put("scope","Automatic native close view of real FollowOwnerGoal movement; no forced limb pose, no humans or paid roster claim");
                long knees=kneeRanges.values().stream().filter(v->v[1]-v[0]>.02).count();if(knees!=1||mob.isNoAi())throw new AssertionError("Single follow animation absent");}
            if(lastModel!=null)GuardStyleProof.snapshot(OUT,String.format("%02d",stage),lastModel);
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
    static void finish(Minecraft mc,Throwable error){if(done)return;done=true;mc.options.keyUp.setDown(false);try{Files.createDirectories(OUT);Files.writeString(OUT.resolve(error==null?"PASS.txt":"FAIL.txt"),String.join("\n",LOG)+"\n"+(error==null?"PASS: native stages "+START_STAGE+" through "+stage+"; automatic client, no human or roster formation claim.":"FAIL at stage "+stage+", tick "+settled+": "+error)+"\n");if(error!=null)error.printStackTrace();}catch(Exception e){e.printStackTrace();}mc.stop();}
}
