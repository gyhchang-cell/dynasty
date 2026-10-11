package com.dynasty.client;

import com.dynasty.blueprint.elite.*;
import com.dynasty.blueprint.client.Cod2EliteVoxelRenderer;
import com.google.gson.*;
import com.mojang.blaze3d.platform.NativeImage;
import net.minecraft.client.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.WorldOptions;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Frozen, silent native art fixture. Only optional QA invokes real existing elite skills. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class Cod2EliteVoxelClientQa {
    private static final boolean ENABLED=Boolean.getBoolean("dynasty.cod2VoxelQa")&&"elites".equals(System.getProperty("dynasty.cod2VoxelQa.batch"));
    private static final Path OUT=Path.of(System.getProperty("dynasty.cod2VoxelQa.output","build/elite-art-qa"));
    private static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
    private static final int TOTAL=39;
    private static final List<Object> REPORT=new ArrayList<>();
    private static final long DEADLINE=System.nanoTime()+600_000_000_000L;
    private record Snapshot(int index,int entityId,String uuid,long published,long start,int skill){}
    private static int stage=-1,frames;
    private static boolean started,done,captured,reloaded;
    private static CompletableFuture<Void> setup,reload;
    private static CompletableFuture<Snapshot> pending;
    private static Snapshot current;
    private static LivingEntity fixture,target;
    private static Mechanist owner;
    private static ArmorStand camera;
    private static volatile int wheels,spiders,pools;
    private static volatile boolean actualNet;
    private static int species(int index){return index<16?0:index<32?1:2;}
    private static int pose(int index){return index<32?index%16:index-32;}
    private static String id(int index){return species(index)==0?HeadlessGeneral.ID:species(index)==1?Mechanist.ID:ClockworkSpider.ID;}
    private static int skill(LivingEntity m){return m instanceof HeadlessGeneral h?h.skillId():m instanceof Mechanist a?a.skillId():0;}
    private static long start(LivingEntity m){return m instanceof HeadlessGeneral h?h.skillStart():m instanceof Mechanist a?a.skillStart():m instanceof ClockworkSpider s?s.fuseStart():-1;}
    private static String clip(LivingEntity m){return m instanceof HeadlessGeneral h?h.visualAnimation():m instanceof Mechanist a?a.visualAnimation():((ClockworkSpider)m).fuseStart()>=0?"fuse":"walk";}
    private static int desired(int index){
        int p=pose(index),s=species(index);
        if(s==2)return p<4?30:p==4?4:p==5?3:8;
        if(p<4)return 30;if(p==4)return 4;if(p==5)return 2;if(p==6)return 48;
        if(s==0)return switch(p){case 7->18;case 8->24;case 9->12;case 10->26;case 11->36;case 12->46;case 13->14;case 14->20;default->24;};
        return switch(p){case 7->10;case 8->14;case 9->6;case 10->10;case 11->20;case 12->16;case 13->20;default->24;};
    }
    private static String label(int index){int p=pose(index);if(p<7)return new String[]{"front","45","side","back","walk","hurt","death"}[p];return species(index)==0?new String[]{"roar-tell","roar-contact","spin-tell","spin-26","spin-36","spin-46","throw-tell","throw-contact","actual-blood-pool"}[p-7]:new String[]{"net-tell","net-contact","wheels-tell","wheels-contact","actual-two-wheels","spiders-tell","spiders-contact","actual-four-spiders","spiders-recovery"}[p-7];}
    private static String view(int index){return species(index)==2&&pose(index)>=5?(pose(index)==5?"actual-fuse-tell":"actual-fuse-8"):label(index);}

    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(!ENABLED||done||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Native elite QA deadline");
            if(!started){
                if(!(mc.screen instanceof net.minecraft.client.gui.screens.TitleScreen))return;
                Files.createDirectories(OUT);started=true;mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(4);mc.options.fov().set(50);mc.options.hideGui=true;
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("cod2-elite-voxel-qa",new LevelSettings("Disposable Cod2 elite art",GameType.CREATIVE,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(73,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
            var server=mc.getSingleplayerServer();if(server==null)return;
            if(setup==null){setup=server.submit(()->{
                var world=server.overworld();world.setDayTime(6000);
                for(int x=-24;x<=24;x++)for(int z=-24;z<=24;z++)world.setBlockAndUpdate(new BlockPos(x,-61,z),Blocks.SMOOTH_STONE.defaultBlockState());
                server.getPlayerList().getPlayers().forEach(p->p.teleportTo(world,12,-60,12,135,0));
            });return;}
            if(!setup.isDone())return;setup.join();
            if(stage==TOTAL){
                if(!reloaded){reloaded=true;reload=mc.reloadResourcePacks();return;}
                if(!reload.isDone())return;reload.join();REPORT.add(Map.of("reload","actual Minecraft resource reload"));stage=TOTAL+1;pending=server.submit(()->prepare(server,0));return;
            }
            if(stage==TOTAL+1&&captured){finish(mc,null);return;}
            if(stage<0||captured){current=null;captured=false;frames=0;camera=null;stage++;if(stage==TOTAL)return;int next=stage;pending=server.submit(()->prepare(server,next));return;}
            if(current==null){if(!pending.isDone())return;current=pending.join();}
            if(!(mc.level.getEntity(current.entityId) instanceof LivingEntity mob)||!mob.getUUID().toString().equals(current.uuid))return;
            int s=species(current.index),p=pose(current.index);double angle=p==1?45:p==2?90:p==3?180:p>=7||s==2&&p>=5?45:0,rad=Math.toRadians(angle),distance=s==2?3:8;
            if(camera==null){camera=new ArmorStand(mc.level,0,0,0);camera.setNoGravity(true);camera.setYRot((float)(180-angle));camera.setXRot(3);camera.setYHeadRot(camera.getYRot());camera.yHeadRotO=camera.getYRot();mc.options.setCameraType(CameraType.FIRST_PERSON);mc.setCameraEntity(camera);}
            if(s==1&&p>=12){angle=135;rad=Math.toRadians(angle);camera.setYRot((float)(180-angle));camera.setYHeadRot(camera.getYRot());}
            camera.setPos(mob.getX()+Math.sin(rad)*distance,mob.getY()+(s==0?1.3:s==1?1:.32)-camera.getEyeHeight(),mob.getZ()+Math.cos(rad)*distance);camera.setOldPosAndRot();
        }catch(Throwable e){finish(mc,e);}
    }
    private static Snapshot prepare(MinecraftServer server,int index){
        var world=server.overworld();if(fixture!=null)fixture.discard();if(target!=null)target.discard();if(owner!=null){owner.discard();owner=null;}
        world.getEntitiesOfClass(ClockworkSpider.class,new net.minecraft.world.phys.AABB(-24,-64,-24,24,-40,24)).forEach(Entity::discard);
        world.getEntitiesOfClass(MechanistWheel.class,new net.minecraft.world.phys.AABB(-24,-64,-24,24,-40,24)).forEach(Entity::discard);
        world.getEntitiesOfClass(com.dynasty.blueprint.SkullBloodPool.class,new net.minecraft.world.phys.AABB(-24,-64,-24,24,-40,24)).forEach(Entity::discard);
        world.getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,new net.minecraft.world.phys.AABB(-24,-64,-24,24,-40,24)).forEach(Entity::discard);
        int s=species(index),p=pose(index);wheels=spiders=pools=0;actualNet=false;
        var cow=EntityType.COW.create(world);cow.moveTo(p==5&&s<2?12:0,-60,p==5&&s<2?8:s==2?(p>=5?1:8):2,180,0);cow.setNoAi(true);cow.setNoGravity(true);cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);cow.setHealth(1000);cow.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.INVISIBILITY,12000,0,false,false,false));world.addFreshEntity(cow);target=cow;
        if(s==0)fixture=EliteContent.HEADLESS.get().create(world);else if(s==1)fixture=EliteContent.MECHANIST.get().create(world);else{
            owner=EliteContent.MECHANIST.get().create(world);owner.moveTo(-8,-60,-8,0,0);owner.setNoAi(true);owner.setNoGravity(true);owner.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.INVISIBILITY,12000,0,false,false,false));world.addFreshEntity(owner);
            var spider=EliteContent.SPIDER.get().create(world);spider.launch(owner,cow.getUUID(),0);fixture=spider;
        }
        fixture.moveTo(0,-60,0,0,0);((net.minecraft.world.entity.Mob)fixture).setNoAi(true);fixture.setNoGravity(true);fixture.setDeltaMovement(0,0,0);world.addFreshEntity(fixture);
        if(p==4&&s<2)fixture.setDeltaMovement(0,0,.075);
        if(s<2&&p==5)fixture.hurt(fixture.damageSources().generic(),1);
        if(s<2&&p==6)fixture.hurt(fixture.damageSources().generic(),10000);
        if(s==0&&p>=7){
            int action=p<=8?301:p<=12?302:303;
            if(action==302)cow.moveTo(0,-60,5,180,0);
            if(!((HeadlessGeneral)fixture).startSkill(action,cow))throw new AssertionError("Actual headless startSkill rejected "+action);
            if(action==302)cow.moveTo(0,-60,8,180,0);
        }
        if(s==1&&p>=7){int action=p<=8?321:p<=11?322:323;if(!((Mechanist)fixture).startSkill(action,cow))throw new AssertionError("Actual mechanist startSkill rejected "+action);}
        return new Snapshot(index,fixture.getId(),fixture.getUUID().toString(),world.getGameTime(),start(fixture),skill(fixture));
    }
    @SubscribeEvent public static void server(TickEvent.ServerTickEvent event){
        if(!ENABLED||done||event.phase!=TickEvent.Phase.END||fixture==null||fixture.isRemoved())return;
        var box=new net.minecraft.world.phys.AABB(-24,-64,-24,24,-40,24);wheels=fixture.level().getEntitiesOfClass(MechanistWheel.class,box).size();spiders=fixture.level().getEntitiesOfClass(ClockworkSpider.class,box).size();pools=fixture.level().getEntitiesOfClass(com.dynasty.blueprint.SkullBloodPool.class,box).size();actualNet=target.hasEffect(EliteContent.THREAD_NET.get());
        if(current!=null&&pose(current.index)==4&&species(current.index)<2){fixture.setDeltaMovement(0,0,.075);fixture.hasImpulse=true;fixture.hurtMarked=true;}
    }
    @SuppressWarnings({"rawtypes","unchecked"})
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent event){
        if(!ENABLED||done||captured||current==null||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();if(mc.level==null||mc.getOverlay()!=null||!(mc.level.getEntity(current.entityId) instanceof LivingEntity mob))return;
        try{
            int s=species(current.index),p=pose(current.index);long age=mc.level.getGameTime()-current.published;
            if(age<desired(current.index))return;if((p==5||p>=7)&&s<2&&age>desired(current.index)+8)throw new AssertionError("Missed actual elite action frame");
            if(!(mc.getEntityRenderDispatcher().getRenderer(mob) instanceof Cod2EliteVoxelRenderer))throw new AssertionError("Separate authored art renderer not selected");
            var renderer=(GeoEntityRenderer)mc.getEntityRenderDispatcher().getRenderer(mob);var model=renderer.getGeoModel();var animatable=(GeoEntity)mob;
            String name=id(current.index);if(!model.getTextureResource(animatable).getPath().equals("textures/entity/blueprint/cod2_voxel/"+name+".png"))throw new AssertionError("New pixel atlas not bound");
            try(var stream=mc.getResourceManager().open(model.getTextureResource(animatable));var im=NativeImage.read(stream)){if(im.getWidth()!=16||im.getHeight()!=16)throw new AssertionError("Actual texture not 16px");}
            String[] bones=s==0?new String[]{"waist_upper","chest_mirror","right_grip","greatblade","held_head","seal_flame"}:s==1?new String[]{"waist_upper","neck","backpack","box_lid","aux_3_claw","left_thread_4","left_forearm","left_wrist","left_shin","left_ankle","left_foot"}:new String[]{"boiler","mandibles","leg_7_tip"};
            var actualBones=new LinkedHashMap<String,Object>();
            for(String bone:bones){
                if(model.getBone(bone).isEmpty())throw new AssertionError("Missing baked bone "+bone);
                var baked=(software.bernie.geckolib.cache.object.GeoBone)model.getBone(bone).orElseThrow();
                actualBones.put(bone,List.of(baked.getRotX(),baked.getRotY(),baked.getRotZ(),baked.getPosX(),baked.getPosY(),baked.getPosZ(),baked.getScaleX(),baked.getScaleY(),baked.getScaleZ()));
            }
            var controller=animatable.getAnimatableInstanceCache().getManagerForId(mob.getId()).getAnimationControllers().get("body");
            String actual=controller.getCurrentAnimation()==null?"none":controller.getCurrentAnimation().animation().name(),wanted="animation."+name+"."+clip(mob);
            if(!actual.equals(wanted)||controller.getAnimationState().name().equals("STOPPED"))throw new AssertionError("Native clip differs "+actual+" expected "+wanted);
            if(s<2&&p>=7&&(skill(mob)!=current.skill||start(mob)!=current.start))throw new AssertionError("Actual skill epoch differs");
            if(s<2&&p==4&&!wanted.endsWith(".walk"))throw new AssertionError("Actual movement not walk");
            if(s<2&&p==5&&mob.hurtTime<=0||s<2&&p==6&&!mob.isDeadOrDying())throw new AssertionError("Real hurt/death state absent");
            if(s<2){
                var chest=(software.bernie.geckolib.cache.object.GeoBone)model.getBone("chest").orElseThrow();
                var knee=(software.bernie.geckolib.cache.object.GeoBone)model.getBone("right_knee").orElseThrow();
                actualBones.put("chest",List.of(chest.getRotX(),chest.getRotY(),chest.getRotZ()));actualBones.put("right_knee",List.of(knee.getRotX(),knee.getRotY(),knee.getRotZ()));
                if(p==5&&Math.abs(chest.getRotX())<.0087F){if(age>6)throw new AssertionError("Actual hurt chest pose has not appeared");return;}
                if(p==6&&Math.abs(knee.getRotX())<.2F)throw new AssertionError("Actual death knee pose absent");
            }
            if(s==0&&p>=10&&p<=12&&mob.getZ()<(p-9)*2-.01){if(age>desired(current.index)+6)throw new AssertionError("Actual spin step position not received");return;}
            if(s==0&&(p==8||p==12)&&target.getHealth()>=1000){if(age>desired(current.index)+6)throw new AssertionError("Actual roar/spin contact absent");return;}
            if(s==0&&p==15&&pools<1||s==1&&p==8&&!actualNet||s==1&&p==11&&wheels!=2||s==1&&p==14&&spiders!=4){if(age>desired(current.index)+6)throw new AssertionError("Actual contact result absent");return;}
            if(s==2&&p>=5&&(!wanted.endsWith(".fuse")||((ClockworkSpider)mob).fuseStart()<0)){if(age>7)throw new AssertionError("Actual near-target fuse absent");return;}
            if(s==2&&!((ClockworkSpider)fixture).ownedBy(owner))throw new AssertionError("Actual launch owner absent");
            if(++frames<2)return;
            try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){image.writeToFile(OUT.resolve(String.format("%02d-%s-%s.png",stage,name,view(current.index))));}
            REPORT.add(Map.ofEntries(Map.entry("stage",stage),Map.entry("id",name),Map.entry("view",view(current.index)),Map.entry("uuid",mob.getUUID().toString()),Map.entry("clip",actual),Map.entry("age",age),Map.entry("skill",skill(mob)),Map.entry("start",start(mob)),Map.entry("position",mob.position().toString()),Map.entry("health",mob.getHealth()),Map.entry("hurtTime",mob.hurtTime),Map.entry("deathTime",mob.deathTime),Map.entry("actualNet",actualNet),Map.entry("actualWheels",wheels),Map.entry("actualSpiders",spiders),Map.entry("actualBloodPools",pools),Map.entry("actualTargetHealth",target.getHealth()),Map.entry("actualOwnerLaunch",s==2&&((ClockworkSpider)fixture).ownedBy(owner)),Map.entry("boilerScaleY",s==2?((software.bernie.geckolib.cache.object.GeoBone)model.getBone("boiler").orElseThrow()).getScaleY():1F),Map.entry("actualBakedBones",actualBones),Map.entry("fps",mc.getFps())));Files.writeString(OUT.resolve("samples.json"),JSON.toJson(REPORT)+"\n");captured=true;
        }catch(Throwable e){finish(mc,e);}
    }
    private static void finish(Minecraft mc,Throwable error){
        if(done)return;done=true;
        try{Files.writeString(OUT.resolve(error==null?"PASS.txt":"FAIL.txt"),error==null?"PASS two actual elites, three skills each, real walk/hurt/death, original server contact outcomes and owned summoned spider walk/fuse; separate authored resources, actual reload. Auxiliary has only production walk/fuse and immediately discards on death; no false hurt/death coverage.\n":"FAIL: "+error+"\n");if(error!=null)try(var image=Screenshot.takeScreenshot(mc.getMainRenderTarget())){image.writeToFile(OUT.resolve("FAILED.png"));}}catch(Exception ignored){}
        mc.stop();
    }
}
