package com.dynasty.client;

import com.dynasty.expansion.*;
import com.google.gson.GsonBuilder;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.event.GeoRenderEvent;
import software.bernie.geckolib.cache.object.GeoBone;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/** Automatic native load evidence. Targets are disposable fixtures; mob AI,
 * projectiles, accepted damage and resulting client particles are production
 * code. Does not claim natural spawning, real players or gameplay duration. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class SecondaryLoadClientQa {
    static final boolean ENABLED=Boolean.getBoolean("dynasty.secondaryLoadQa");
    static final Path OUT=Path.of(System.getProperty("dynasty.secondaryArtQa.output","build/secondary-load/results"));
    static final String[] LABELS={"empty","20-locust-swarms","20-ground-path-ai","20-tree-ranged-ai","20-ghosts"};
    static final List<Entity> fixtures=new ArrayList<>();
    static final Set<Integer> serverActors=ConcurrentHashMap.newKeySet(),serverTargets=ConcurrentHashMap.newKeySet();
    static final Set<Integer> shooters=ConcurrentHashMap.newKeySet(),hitters=ConcurrentHashMap.newKeySet();
    static final Set<Integer> builtPaths=ConcurrentHashMap.newKeySet(),traversedPaths=ConcurrentHashMap.newKeySet();
    static final AtomicInteger projectiles=new AtomicInteger(),hits=new AtomicInteger();
    static final List<String> LOG=new ArrayList<>();
    static List<Integer> ids=List.of();
    static final Set<Integer> rendered=new HashSet<>();
    static final Map<Integer,Map<String,double[]>> boneRanges=new LinkedHashMap<>();
    static final Map<Integer,Set<String>> clips=new LinkedHashMap<>();
    static final Map<String,Object> baked=new LinkedHashMap<>();
    static final List<Double> frames=new ArrayList<>();
    static final List<Integer> visibleCounts=new ArrayList<>(),particles=new ArrayList<>();
    static final List<Map<String,Object>> samples=new ArrayList<>();
    static CompletableFuture<List<Integer>> pending;
    static volatile int stage=-1;
    static int settled;
    static long lastFrame,deadline=System.nanoTime()+600_000_000_000L;
    static boolean started,done,captured;
    static double baseline;

    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e){
        if(!ENABLED||done||e.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            org.lwjgl.glfw.GLFW.glfwHideWindow(mc.getWindow().getWindow());
            if(org.lwjgl.glfw.GLFW.glfwGetWindowAttrib(mc.getWindow().getWindow(),org.lwjgl.glfw.GLFW.GLFW_VISIBLE)!=0)throw new AssertionError("Window shown");
            mc.options.getSoundSourceOptionInstance(net.minecraft.sounds.SoundSource.MASTER).set(0.0);
            if(System.nanoTime()>deadline)throw new AssertionError("Load QA timeout");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                if(!mc.gameDirectory.getCanonicalPath().contains("/build/secondary-art-native/"))throw new AssertionError("Not a disposable world");
                Files.createDirectories(OUT);started=true;
                mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(3);mc.options.fov().set(50);mc.options.hideGui=true;mc.options.bobView().set(false);mc.options.framerateLimit().set(120);
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("secondary-load-"+System.currentTimeMillis(),new LevelSettings("Disposable silent 20-mob load QA",GameType.CREATIVE,false,net.minecraft.world.Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(57,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;
            if(mc.screen!=null)mc.setScreen(null);
            if(pending!=null){
                if(!pending.isDone())return;ids=pending.join();pending=null;settled=0;captured=false;frames.clear();visibleCounts.clear();particles.clear();samples.clear();boneRanges.clear();clips.clear();baked.clear();lastFrame=0;
                var cam=new ArmorStand(mc.level,0,-60,28);cam.setPos(0,-54-cam.getEyeHeight(),28);cam.setYRot(180);cam.setXRot(8);cam.setYHeadRot(180);cam.yHeadRotO=180;cam.setOldPosAndRot();mc.options.setCameraType(CameraType.FIRST_PERSON);mc.setCameraEntity(cam);return;
            }
            if(stage<0||captured){if(stage==4){finish(mc,null);return;}stage++;pending=mc.getSingleplayerServer().submit(()->prepare(mc));return;}
            settled++;
            if(settled==2||settled==20||settled==100||settled==300){
                final int t=settled;
                samples.add(mc.getSingleplayerServer().submit(()->{
                    var rows=new ArrayList<Map<String,Object>>();
                    for(var f:fixtures)if(f instanceof SecondaryMob m)rows.add(Map.of("id",m.getId(),"position",List.of(m.getX(),m.getY(),m.getZ()),"noAi",m.isNoAi(),"navigationDone",m.getNavigation().isDone(),"animation",m.animation(),"target",m.getTarget()==null?-1:m.getTarget().getId()));
                    return Map.<String,Object>of("settled",t,"actors",rows,"projectiles",projectiles.get(),"acceptedHits",hits.get(),"serverAverageTickMs",mc.getSingleplayerServer().getAverageTickTime());
                }).join());
            }
            particles.add(Integer.parseInt(mc.particleEngine.countParticles()));
            if((settled==100||settled==300)&&stage>0){
                capture(mc,String.format("%02d-%s-t%d.png",stage,LABELS[stage],settled));
                Files.writeString(OUT.resolve(String.format("%02d-live-t%d.json",stage,settled)),new GsonBuilder().setPrettyPrinting().create().toJson(Map.of("ids",ids,"clientPresent",ids.stream().filter(id->mc.level.getEntity(id)!=null).toList(),"lastRenderedIds",new ArrayList<>(rendered),"baked",baked,"observedRenderedCountMin",visibleCounts.stream().min(Integer::compareTo).orElse(0),"observedRenderedCountMax",visibleCounts.stream().max(Integer::compareTo).orElse(0))));
            }
        }catch(Throwable error){finish(mc,error);}
    }

    static List<Integer> prepare(Minecraft mc){
        var server=mc.getSingleplayerServer();var world=server.overworld();world.setDayTime(6000);
        fixtures.forEach(Entity::discard);fixtures.clear();serverActors.clear();serverTargets.clear();shooters.clear();hitters.clear();builtPaths.clear();traversedPaths.clear();projectiles.set(0);hits.set(0);
        // Remove prior-stage projectile fixtures through ordinary discard, not
        // network injection or modification of a damage/particle implementation.
        for(var f:world.getAllEntities())if(f instanceof SecondaryProjectile)f.discard();
        for(int x=-28;x<=28;x++)for(int z=-24;z<=24;z++)world.setBlockAndUpdate(new BlockPos(x,-61,z),Blocks.STONE.defaultBlockState());
        server.getPlayerList().getPlayers().get(0).teleportTo(world,-18,-60,0,0,0);
        if(stage==0)return List.of();
        String id=stage==1?"locust_swarm":stage==2?"clockwork_rat":stage==3?"tree_spirit":"wandering_spirit";
        var out=new ArrayList<Integer>();
        for(int i=0;i<20;i++){
            double x=(i%5-2)*5,z=(i/5-1.5)*4;
            var mob=SecondaryMobs.TYPES.get(id).get().create(world);mob.setUUID(new UUID(5720+stage,i+1));mob.moveTo(x,-60,z,0,0);mob.setNoAi(stage==1||stage==4);mob.setPersistenceRequired();
            world.addFreshEntity(mob);fixtures.add(mob);serverActors.add(mob.getId());out.add(mob.getId());
            if(stage==2||stage==3){
                var target=EntityType.COW.create(world);target.setUUID(new UUID(5740+stage,i+1));target.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1_000_000);target.setHealth(1_000_000);target.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);target.setNoAi(true);target.setNoGravity(stage==3);target.setPersistenceRequired();target.moveTo(x,stage==3?-55:-60,z+(stage==3?4:8),0,0);world.addFreshEntity(target);fixtures.add(target);serverTargets.add(target.getId());mob.setTarget(target);
                // Stationary elevated cows make genuine tree-spirit ranged AI
                // repeat rather than switching to melee after one shot. The
                // test targets are fixtures, not a natural combat encounter.
            }
        }
        return out;
    }

    @SubscribeEvent public static void joined(EntityJoinLevelEvent e){
        if(ENABLED&&!e.getLevel().isClientSide()&&e.getEntity() instanceof SecondaryProjectile p&&p.getOwner()!=null&&serverActors.contains(p.getOwner().getId())){projectiles.incrementAndGet();shooters.add(p.getOwner().getId());}
    }
    @SubscribeEvent public static void damaged(LivingDamageEvent e){
        if(ENABLED&&!e.getEntity().level().isClientSide&&serverTargets.contains(e.getEntity().getId())&&e.getSource().getEntity()!=null&&serverActors.contains(e.getSource().getEntity().getId())&&e.getAmount()>0){hits.incrementAndGet();hitters.add(e.getSource().getEntity().getId());}
    }
    @SubscribeEvent public static void serverTick(TickEvent.ServerTickEvent e){
        if(!ENABLED||done||stage!=2||e.phase!=TickEvent.Phase.END)return;
        // Observe every server tick: a single fixed-time sample can miss short
        // valid paths that the melee goal has already completed. No moveTo or
        // goal/position mutation is performed by this observer.
        for(var f:fixtures)if(f instanceof SecondaryMob m&&!m.isNoAi()){
            var path=m.getNavigation().getPath();
            if(path!=null&&path.getNodeCount()>0)builtPaths.add(m.getId());
            if(path!=null&&path.getNextNodeIndex()>0)traversedPaths.add(m.getId());
        }
    }
    @SubscribeEvent public static void geo(GeoRenderEvent.Entity.Post e){
        if(!ENABLED||pending!=null||!ids.contains(e.getEntity().getId()))return;
        int id=e.getEntity().getId();rendered.add(id);
        if(e.getEntity() instanceof SecondaryMob mob){
            var ctrl=mob.getAnimatableInstanceCache().getManagerForId(id).getAnimationControllers().get("body");
            if(ctrl!=null&&ctrl.getCurrentAnimation()!=null)clips.computeIfAbsent(id,k->new LinkedHashSet<>()).add(ctrl.getCurrentAnimation().animation().name());
            var ranges=boneRanges.computeIfAbsent(id,k->new LinkedHashMap<>());
            int[] counts={0,0,0};for(var b:e.getModel().topLevelBones())observe(b,ranges,counts);
            baked.put(mob.spec.id(),Map.of("bones",counts[0],"cuboids",counts[1],"nonNullQuads",counts[2]));
        }
    }
    static void observe(GeoBone b,Map<String,double[]> ranges,int[] counts){
        counts[0]++;counts[1]+=b.getCubes().size();for(var c:b.getCubes())if(c.quads()!=null)for(var q:c.quads())if(q!=null)counts[2]++;
        double[] values={b.getRotX(),b.getRotY(),b.getRotZ(),b.getPosX(),b.getPosY(),b.getPosZ()};
        var r=ranges.computeIfAbsent(b.getName(),k->new double[]{1e9,-1e9,1e9,-1e9,1e9,-1e9,1e9,-1e9,1e9,-1e9,1e9,-1e9});
        for(int i=0;i<6;i++){r[i*2]=Math.min(r[i*2],values[i]);r[i*2+1]=Math.max(r[i*2+1],values[i]);}
        for(var child:b.getChildBones())observe(child,ranges,counts);
    }
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent e){
        if(!ENABLED||done)return;
        if(e.phase==TickEvent.Phase.START){rendered.clear();return;}
        if(pending!=null||stage<0||captured||settled<60)return;
        var mc=Minecraft.getInstance();
        try{
            long now=System.nanoTime();if(lastFrame!=0){frames.add((now-lastFrame)/1e6);visibleCounts.add(rendered.size());}lastFrame=now;
            if(settled<400)return;
            if(frames.size()<120)throw new AssertionError("Insufficient measured frames");
            var r=new LinkedHashMap<String,Object>();r.put("stage",LABELS[stage]);r.put("count",ids.size());r.put("viewport",List.of(mc.getWindow().getWidth(),mc.getWindow().getHeight()));r.put("frames",frames.size());r.put("frameIntervalsMs",frames);r.put("renderedCounts",visibleCounts);r.put("medianFrameMs",GuardArtClientQa.percentile(frames,.5));r.put("p95FrameMs",GuardArtClientQa.percentile(frames,.95));r.put("serverAverageTickMs",mc.getSingleplayerServer().getAverageTickTime());r.put("baked",baked);r.put("serverSamples",samples);r.put("nativeClips",clips);r.put("particleCountsPerClientTick",particles);r.put("particlePeak",particles.stream().max(Integer::compareTo).orElse(0));r.put("projectiles",projectiles.get());r.put("shooters",shooters);r.put("acceptedHits",hits.get());r.put("hitters",hitters);
            r.put("scope","Automatic native client: 20 actual mob renders, production AI and genuine replicated feedback with disposable fixture targets. No natural ecosystem, human, or basic-mob face-budget acceptance.");
            // Preserve the complete failing measurement too; never label this
            // diagnostic record accepted unless every subsequent assertion passes.
            Files.writeString(OUT.resolve(String.format("%02d-diagnostic.json",stage)),new GsonBuilder().setPrettyPrinting().create().toJson(r));
            if(stage==0)baseline=GuardArtClientQa.percentile(frames,.5);
            else{
                double fraction=(double)visibleCounts.stream().filter(n->n==20).count()/visibleCounts.size();r.put("all20RenderedFraction",fraction);r.put("emptyMedianMs",baseline);r.put("medianRatioToEmpty",GuardArtClientQa.percentile(frames,.5)/baseline);
                if(fraction<.9)throw new AssertionError("Not all 20 rendered together: "+fraction);
                if(GuardArtClientQa.percentile(frames,.5)>50||GuardArtClientQa.percentile(frames,.95)>100)throw new AssertionError("Severe native load stutter");
                long movingBones=boneRanges.values().stream().filter(m->m.values().stream().anyMatch(a->{for(int i=0;i<6;i++)if(a[2*i+1]-a[2*i]>.02)return true;return false;})).count();r.put("entitiesWithActualBoneMotion",movingBones);
                if(movingBones<18)throw new AssertionError("Rendered bones did not animate: "+movingBones);
                if(stage==2){
                    var a=(List<Map<String,Object>>)samples.get(0).get("actors");var b=(List<Map<String,Object>>)samples.get(2).get("actors");int moved=0,navigating=0;
                    for(int i=0;i<a.size();i++){var p=(List<Double>)a.get(i).get("position");var q=(List<Double>)b.get(i).get("position");if(Math.hypot(p.get(0)-q.get(0),p.get(2)-q.get(2))>1)moved++;if(Boolean.TRUE.equals(a.get(i).get("noAi"))||Boolean.TRUE.equals(b.get(i).get("noAi")))throw new AssertionError("Path actor had NoAI");if(Boolean.FALSE.equals(a.get(i).get("navigationDone")))navigating++;}
                    r.put("movedOver1Block",moved);r.put("navigatingFirstSample",navigating);r.put("actorsBuiltNonemptyPaths",builtPaths);r.put("actorsTraversedPathNodes",traversedPaths);
                    if(moved<18||builtPaths.size()<18||traversedPaths.size()<18)throw new AssertionError("Real group pathfinding not observed: moved="+moved+" built="+builtPaths.size()+" traversed="+traversedPaths.size());
                }
                if(stage==3){
                    long cast=clips.values().stream().filter(s->s.contains("special")).count();r.put("actorsRenderedNaturalSpecial",cast);
                    if(shooters.size()<18||hitters.size()<18||projectiles.get()<40||hits.get()<40||cast<18||particles.stream().max(Integer::compareTo).orElse(0)<60)throw new AssertionError("Actual ranged AI / accepted hits / client particles insufficient: "+shooters.size()+" / "+hitters.size()+" / "+projectiles+" / "+hits+" / "+r.get("particlePeak"));
                }
            }
            Files.writeString(OUT.resolve(String.format("%02d-state.json",stage)),new GsonBuilder().setPrettyPrinting().create().toJson(r));capture(mc,String.format("%02d-%s.png",stage,LABELS[stage]));LOG.add(LABELS[stage]+" median="+r.get("medianFrameMs")+" p95="+r.get("p95FrameMs")+" particles="+r.get("particlePeak"));captured=true;
        }catch(Throwable error){finish(mc,error);}
    }
    static void capture(Minecraft mc,String name)throws Exception{try(var shot=Screenshot.takeScreenshot(mc.getMainRenderTarget())){shot.writeToFile(OUT.resolve(name));}}
    static void finish(Minecraft mc,Throwable error){if(done)return;done=true;try{Files.createDirectories(OUT);Files.writeString(OUT.resolve(error==null?"PASS.txt":"FAIL.txt"),String.join("\n",LOG)+"\n"+(error==null?"PASS: five native load windows; 20 actual rendered mobs, production ground/ranged AI and replicated particles. Fixture targets, no humans or natural ecological acceptance.":"FAIL: "+error)+"\n");if(error!=null)error.printStackTrace();}catch(Exception e){e.printStackTrace();}mc.stop();}
}
