package com.dynasty.client;

import com.dynasty.blueprint.*;
import com.dynasty.blueprint.client.TemplateMobRenderer;
import com.google.gson.*;
import com.mojang.blaze3d.platform.NativeImage;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.server.MinecraftServer;
import net.minecraft.world.Difficulty;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Actual client rendering and server-started actions in a disposable world. Art QA only. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class Cod2VoxelClientQa {
    private static final boolean ENABLED=Boolean.getBoolean("dynasty.cod2VoxelQa")&&!Set.of("elites","art-load").contains(System.getProperty("dynasty.cod2VoxelQa.batch","first"));
    private static final Path OUT=Path.of(System.getProperty("dynasty.cod2VoxelQa.output","build/voxel-qa"));
    private static final Gson JSON=new GsonBuilder().setPrettyPrinting().create();
    private static final int ONLY_INDEX=Integer.getInteger("dynasty.cod2VoxelQa.onlyIndex",-1);
    private static final boolean NINTH="child-paper".equals(System.getProperty("dynasty.cod2VoxelQa.batch"));
    private static final boolean EIGHTH_WALL="ape-wall".equals(System.getProperty("dynasty.cod2VoxelQa.batch"));
    private static final boolean EIGHTH=EIGHTH_WALL||"ape-dao".equals(System.getProperty("dynasty.cod2VoxelQa.batch"));
    private static final boolean SEVENTH="corpse-ghost-palanquin-flag".equals(System.getProperty("dynasty.cod2VoxelQa.batch"));
    private static final boolean SIXTH_DETAILS="shield-skull-details".equals(System.getProperty("dynasty.cod2VoxelQa.batch"));
    private static final boolean SIXTH=SIXTH_DETAILS||"shield-skull-guard-scout".equals(System.getProperty("dynasty.cod2VoxelQa.batch"));
    private static final boolean ARMY_DETAILS="army-details".equals(System.getProperty("dynasty.cod2VoxelQa.batch"));
    private static final boolean ARMIES=ARMY_DETAILS||"armies-tree".equals(System.getProperty("dynasty.cod2VoxelQa.batch"));
    private static final boolean BEAST_DETAILS="beast-details".equals(System.getProperty("dynasty.cod2VoxelQa.batch"));
    private static final boolean BEASTS=BEAST_DETAILS||"beasts-priest".equals(System.getProperty("dynasty.cod2VoxelQa.batch"));
    private static final boolean DETAILS="mechanical-details".equals(System.getProperty("dynasty.cod2VoxelQa.batch"));
    private static final boolean MECHANICALS=System.getProperty("dynasty.cod2VoxelQa.batch", "first").startsWith("mechanical");
    private static final boolean FLOATERS="floaters".equals(System.getProperty("dynasty.cod2VoxelQa.batch","first"));
    private static final String[] IDS=NINTH?new String[]{"fuhun_baibu_tongzi","zhiren_jianke"}:EIGHTH_WALL?new String[]{"shanjing_shanxiao"}:EIGHTH?new String[]{"shanjing_shanxiao","zuwu_daoshou"}:SEVENTH?new String[]{"shibian_lishi","yinbing_guizu","yinyang_zhijiao_youhun","zhenwang_zhangqiguan"}:SIXTH?new String[]{"ludun_jiashi","muxue_feilu","pijia_panjiang_huwei","tiesuo_chihou"}:ARMIES?new String[]{"juma_changqiangbing","kuijun_sishi","kumu_shujing","liannu_zhenzu"}:BEAST_DETAILS?new String[]{"baimu_mowu","chimu_zhuha"}:BEASTS?new String[]{"baimu_mowu","bishui_xuanjiao_youzi","chimu_zhuha","fufa_jijiu"}:DETAILS?new String[]{"qingtong_shuangtoushekui","mingsha_shixie","bazu_digongzhu"}:MECHANICALS?new String[]{"qingtong_shuangtoushekui","xunshan_mujiaquan","bazu_digongzhu","mingsha_shixie"}:FLOATERS?new String[]{"youdeng_guimianfu","xueju_mangguyu","shashui_funigui"}:new String[]{"jubi_shigandang","juli_bixi_kuilei","tongbi_feitian_yecha"};
    private static final String[] POSES={"front","45","side","back","walk","run","attack-tell","attack-contact","special-tell","special-contact","hurt","death"};
    private static final int[] BASIC=NINTH?new int[]{ArmySkills.CHILD_LAUGH,ArmySkills.PAPER_SLASH}:EIGHTH?new int[]{5,1}:SEVENTH?new int[]{24,22,64,18}:SIXTH?new int[]{2,29,20,14}:ARMIES?new int[]{10,16,35,12}:BEAST_DETAILS?new int[]{60,31}:BEASTS?new int[]{60,40,31,3}:DETAILS?new int[]{47,38,50}:MECHANICALS?new int[]{46,44,50,38}:FLOATERS?new int[]{52,54,56}:new int[]{42,58,62},SPECIAL=NINTH?new int[]{ArmySkills.CHILD_CURSE,ArmySkills.PAPER_SHED}:EIGHTH?new int[]{6,1}:SEVENTH?new int[]{24,23,65,18}:SIXTH?new int[]{2,30,21,SIXTH_DETAILS?19:15}:ARMIES?(ARMY_DETAILS?new int[]{11,17,34,13}:new int[]{11,17,36,13}):BEAST_DETAILS?new int[]{61,33}:BEASTS?new int[]{61,41,32,4}:DETAILS?new int[]{49,37,51}:MECHANICALS?new int[]{48,45,51,39}:FLOATERS?new int[]{53,55,57}:new int[]{43,59,63},CONTACT=NINTH?new int[]{12,6}:EIGHTH?new int[]{EIGHTH_WALL?24:14,12}:SEVENTH?new int[]{20,14,16,18}:SIXTH?(SIXTH_DETAILS?new int[]{24,14,22,15}:new int[]{16,14,16,9}):ARMIES?(ARMY_DETAILS?new int[]{12,17,18,22}:new int[]{12,8,18,14}):BEAST_DETAILS?new int[]{12,10}:BEASTS?new int[]{12,12,10,24}:DETAILS?new int[]{10,20,12}:MECHANICALS?new int[]{10,8,12,12}:FLOATERS?new int[]{18,16,14}:new int[]{16,18,16},SPECIAL_CONTACT=NINTH?new int[]{40,6}:EIGHTH?new int[]{18,22}:SEVENTH?new int[]{20,5,24,18}:SIXTH?new int[]{24,20,10,SIXTH_DETAILS?6:12}:ARMIES?(ARMY_DETAILS?new int[]{8,18,20,20}:new int[]{8,18,28,12}):BEAST_DETAILS?new int[]{26,12}:BEASTS?new int[]{26,18,10,20}:DETAILS?new int[]{18,22,32}:MECHANICALS?new int[]{18,20,20,20}:FLOATERS?new int[]{24,30,24}:new int[]{30,32,20};
    private static int beastSpecies(int index){return BEAST_DETAILS&&index/12==1?2:index/12;}
    private static boolean beastCeiling(int index){return BEAST_DETAILS&&index/12==0&&(index%12<4||index%12==8||index%12==9);}
    private static boolean beastDeferred(int index){return BEASTS&&(beastCeiling(index)||beastSpecies(index)==1&&index%12>=6&&index%12<=9||beastSpecies(index)==2&&index%12>=6&&index%12<=9);}
    private static boolean armyTreeWake(int index){return ARMY_DETAILS&&index/12==2&&(index%12==8||index%12==9);}
    private static boolean armyDeferred(int index){return ARMIES&&(index/12==1&&(index%12==8||index%12==9)||index/12==2&&index%12!=11&&!(ARMY_DETAILS&&index%12<4)&&!armyTreeWake(index));}
    private static boolean ninthDeferred(int index){return NINTH&&index/12==0&&(index%12==8||index%12==9);}
    private static boolean eighthDeferred(int index){return EIGHTH&&index/12==0&&(index%12==8||index%12==9||EIGHTH_WALL&&index%12<6);}
    private static boolean scorpionSettles(int index){return DETAILS&&index/12==1&&(index%12<4||index%12==8||index%12==9);}
    private static final int RELOAD_STAGE=ONLY_INDEX>=0?2:IDS.length*12;
    private record Snapshot(int index,int entityId,String uuid,long start,int skill,long published){}
    private static final List<Object> REPORT=new ArrayList<>();
    private static boolean started,done,captured,reloaded,jumpContactCaptured,powderPreblastCaptured,skullFlightCaptured,scoutHookCaptured,ghostReturnCaptured,flagAuraCaptured,apeFlightCaptured,paperRecoveryCaptured;
    private static int stage=-1,settled,frames;
    private static CompletableFuture<Void> setup,reload;
    private static CompletableFuture<Snapshot> pending;
    private static Snapshot current;
    private static CompletableFuture<Snapshot> wetAction;
    private static int wetIndex,wetSkill;
    private static long wetAt;
    private static volatile int landedEntity=-1;
    private static volatile String serverDropState="";
    private static volatile String serverBlastState="";
    private static volatile int detonatedEntity=-1,actualBloodPools;
    private static volatile String guardHitEvidence="";
    private static volatile int actualProjectiles;
    private static volatile String wallEvidence="";
    private static volatile String highGroundEvidence="";
    private static volatile int actualMiasma;
    private static volatile boolean actualAura;
    private static volatile String ghostEvadeEvidence="";
    private static volatile String paperShedEvidence="";
    private static volatile boolean actualSoulBind;
    private static volatile int actualFood=-1;
    private static TemplateMob auraAlly;
    private static TemplateMob fixture;
    private static volatile int serverPose=-1;
    private static LivingEntity target;
    private static ArmorStand camera;
    private static final long DEADLINE=System.nanoTime()+600_000_000_000L;

    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent event){
        if(!ENABLED||done||event.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try {
            if(System.nanoTime()>DEADLINE)throw new AssertionError("Native art QA timed out");
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                if(!mc.gameDirectory.getCanonicalPath().contains("/build/cod2-voxel-client/"))throw new AssertionError("Refusing user game directory");
                if(Files.exists(OUT.resolve("PASS.txt")))throw new AssertionError("Use a fresh evidence directory");
                Files.createDirectories(OUT);started=true;mc.options.pauseOnLostFocus=false;
                mc.options.renderDistance().set(4);mc.options.fov().set(50);mc.options.hideGui=true;
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("cod2-voxel-qa",new LevelSettings("Disposable Cod2 art QA",GameType.CREATIVE,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),
                    new WorldOptions(57,false,false),r->r.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;
            if(mc.screen!=null)mc.setScreen(null);
            var server=mc.getSingleplayerServer();if(server==null)return;
            if(setup==null){setup=server.submit(()->{
                var world=server.overworld();world.setDayTime(6000);
                for(int x=-24;x<=24;x++)for(int z=-24;z<=24;z++)world.setBlockAndUpdate(new BlockPos(x,-61,z),Blocks.SMOOTH_STONE.defaultBlockState());
                // Keep the actual player outside the changing pond: first-person block overlays
                // use the player even when an independent camera entity renders the model.
                for(var p:server.getPlayerList().getPlayers())p.teleportTo(world,12,-60,12,135,0);
            });return;}
            if(!setup.isDone())return;setup.join();
            if(stage==RELOAD_STAGE){
                if(!reloaded){reloaded=true;reload=mc.reloadResourcePacks();return;}
                if(!reload.isDone())return;reload.join();
                if(!REPORT.stream().anyMatch(x->x.toString().contains("reload"))){
                    REPORT.add(Map.of("reload","actual Minecraft resource reload complete"));stage=RELOAD_STAGE+1;
                    pending=prepareAsync(server,0);return;
                }
            }
            if(stage==RELOAD_STAGE+1&&captured){finish(mc,null);return;}
            if(stage<0||captured){
                current=null;captured=false;jumpContactCaptured=false;powderPreblastCaptured=false;skullFlightCaptured=false;scoutHookCaptured=false;ghostReturnCaptured=false;flagAuraCaptured=false;apeFlightCaptured=false;paperRecoveryCaptured=false;settled=0;frames=0;camera=null;
                stage++;
                if(stage==RELOAD_STAGE)return;
                final int next=stage;pending=prepareAsync(server,next);return;
            }
            if(current==null){if(!pending.isDone())return;current=pending.join();}
            if(!(mc.level.getEntity(current.entityId) instanceof TemplateMob entity)||!entity.getUUID().toString().equals(current.uuid))return;
            int pose=current.index%12;
            // The real powder blast is photographed with all its fire in pose 9.
            // Hide only the fixture corpse's client fire overlay in pose 11 so
            // its actual server-selected death animation can also be inspected.
            if(ARMIES&&current.index/12==1&&pose==11){
                entity.clearFire();entity.setSharedFlagOnFire(false);
                // Invisible vanilla targets still draw their fire in front of the corpse.
                var clientTarget=target==null?null:mc.level.getEntity(target.getId());
                if(clientTarget!=null){clientTarget.clearFire();clientTarget.setSharedFlagOnFire(false);}
            }
            if(camera==null){
                double angle=pose==1?45:pose==2?90:pose==3?180:(BEASTS||ARMIES||SIXTH||SEVENTH||EIGHTH||NINTH)&&pose>=6&&pose<=9?45:MECHANICALS&&pose>=6&&pose<=9?(DETAILS&&current.index/12==0?135:45):0;
                double rad=Math.toRadians(angle),distance=6.6;
                double actorY=EIGHTH&&current.index/12==0&&(pose==8||pose==9)?-58:SIXTH&&current.index/12==1?-56.5:beastCeiling(current.index)?-55.875:MECHANICALS&&current.index/12==2&&(pose==8||pose==9)?-56.4:FLOATERS&&current.index/12==0?-58.2:-60;
                camera=new ArmorStand(mc.level,Math.sin(rad)*distance,actorY-.15,Math.cos(rad)*distance);
                camera.setNoGravity(true);camera.setYRot((float)(180-angle));camera.setXRot(3);
                if(beastCeiling(current.index)){
                    // View the physically inverted rig from beneath its support, not above it.
                    // ArmorStand eye height otherwise puts the lens above the ceiling plane.
                    camera.setPos(camera.getX(),actorY-.8-camera.getEyeHeight(),camera.getZ());
                    camera.setXRot(-10);
                }
                camera.setYHeadRot(camera.getYRot());camera.yHeadRotO=camera.getYRot();camera.setOldPosAndRot();
                mc.options.setCameraType(CameraType.FIRST_PERSON);mc.setCameraEntity(camera);
            }
            if(SIXTH&&(current.index/12==1&&(pose==6||pose==7||pose==11)||current.index/12==3&&!SIXTH_DETAILS&&(pose==8||pose==9))||ARMIES&&current.index/12==3&&(pose==8||pose==9)||BEASTS&&!BEAST_DETAILS&&current.index/12==2&&(pose==8||pose==9)||FLOATERS&&(pose==11||current.index/12==2&&pose==9)||MECHANICALS&&current.index/12==2&&(pose==8||pose==9)){
                // Follow a genuinely falling corpse; view the melted pool under the water surface.
                double eyeAbove=SIXTH?1.05:ARMIES?1.2:BEASTS?1:MECHANICALS?.8:current.index/12==2?.22:.7;
                camera.setPos(camera.getX(),entity.getY()+eyeAbove-camera.getEyeHeight(),camera.getZ());
                if(SIXTH&&(current.index/12==1&&(pose==6||pose==7||pose==11)||current.index/12==3&&!SIXTH_DETAILS&&(pose==8||pose==9))||ARMIES&&current.index/12==3&&(pose==8||pose==9)||BEASTS&&!BEAST_DETAILS&&current.index/12==2&&(pose==8||pose==9)){
                    double rad=Math.toRadians(180-camera.getYRot()),distance=6.6;
                    camera.setPos(entity.getX()+Math.sin(rad)*distance,entity.getY()+eyeAbove-camera.getEyeHeight(),entity.getZ()+Math.cos(rad)*distance);
                }
                camera.setOldPosAndRot();
            }
            if(SEVENTH&&current.index/12==1&&(pose==8||pose==9)){
                double rad=Math.toRadians(180-camera.getYRot()),distance=6.6;
                camera.setPos(entity.getX()+Math.sin(rad)*distance,entity.getY()+1.05-camera.getEyeHeight(),entity.getZ()+Math.cos(rad)*distance);
                camera.setOldPosAndRot();
            }
            if(EIGHTH&&current.index/12==0&&((pose==6||pose==7)||EIGHTH_WALL&&pose<6)){
                double distance=6.6;
                if(EIGHTH_WALL&&pose<6){
                    double angle=pose==1?45:pose==2?80:pose==3?-45:0,rad=Math.toRadians(angle);
                    camera.setPos(entity.getX()+Math.sin(rad)*distance,entity.getY()+1.3-camera.getEyeHeight(),entity.getZ()-Math.cos(rad)*distance);
                    camera.setYRot((float)angle);camera.setYHeadRot(camera.getYRot());camera.yHeadRotO=camera.getYRot();camera.setXRot(3);
                }else{
                    double rad=Math.toRadians(180-camera.getYRot());camera.setPos(entity.getX()+Math.sin(rad)*distance,entity.getY()+1-camera.getEyeHeight(),entity.getZ()+Math.cos(rad)*distance);
                }
                camera.setOldPosAndRot();
            }
            if(NINTH&&current.index/12==1&&(pose==8||pose==9)){
                double rad=Math.toRadians(180-camera.getYRot()),distance=6.6;
                camera.setPos(entity.getX()+Math.sin(rad)*distance,entity.getY()+1.05-camera.getEyeHeight(),entity.getZ()+Math.cos(rad)*distance);camera.setOldPosAndRot();
            }
            settled++;
        }catch(Throwable failure){finish(mc,failure);}
    }

    private static CompletableFuture<Snapshot> prepareAsync(MinecraftServer server,int requestedIndex){
        // A focused action needs the same actual renderer warmup as the full
        // cohort. Its first stage is a neutral pose of that actual species.
        final int index=ONLY_INDEX<0?requestedIndex:requestedIndex==0?ONLY_INDEX/12*12:ONLY_INDEX;
        var result=new CompletableFuture<Snapshot>();
        server.execute(()->{try{
            var snapshot=prepare(server,index);
            if(ninthDeferred(index)||eighthDeferred(index)||armyDeferred(index)||beastDeferred(index)||FLOATERS&&index/12==2&&index%12>=6&&index%12<=9||MECHANICALS&&index/12==2&&(index%12==8||index%12==9)||scorpionSettles(index)){wetAction=result;wetIndex=index;wetSkill=snapshot.skill;wetAt=server.overworld().getGameTime()+(eighthDeferred(index)?8:armyDeferred(index)?index/12==1?41:35:scorpionSettles(index)?14:4);}
            else result.complete(snapshot);
        }catch(Throwable e){result.completeExceptionally(e);}});
        return result;
    }

    private static Snapshot prepare(MinecraftServer server,int index){
        var world=server.overworld();if(auraAlly!=null){auraAlly.discard();auraAlly=null;}if(fixture!=null)fixture.discard();if(target!=null&&!(target instanceof net.minecraft.server.level.ServerPlayer))target.discard();
        world.getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,new net.minecraft.world.phys.AABB(-24,-64,-24,24,-40,24)).forEach(Entity::discard);
        int entity=index/12,pose=index%12;
        landedEntity=-1;serverDropState="";serverPose=pose;detonatedEntity=-1;serverBlastState="";actualBloodPools=0;guardHitEvidence="";actualMiasma=0;actualAura=false;ghostEvadeEvidence="";actualProjectiles=0;wallEvidence="";highGroundEvidence="";paperShedEvidence="";actualSoulBind=false;actualFood=-1;
        if(NINTH)for(var player:server.getPlayerList().getPlayers()){
            player.setGameMode(GameType.CREATIVE);player.removeAllEffects();player.setHealth(20);player.getFoodData().setFoodLevel(20);player.teleportTo(world,12,-60,12,135,0);
        }
        world.getEntitiesOfClass(RootSnare.class,new net.minecraft.world.phys.AABB(-24,-64,-24,24,-40,24)).forEach(Entity::discard);
        if(FLOATERS){
            // A real three-block pond, restored to dry ground for the other species.
            for(int x=-8;x<=8;x++)for(int z=-8;z<=8;z++){
                world.setBlockAndUpdate(new BlockPos(x,-63,z),Blocks.SMOOTH_STONE.defaultBlockState());
                for(int y=-62;y<=-60;y++)world.setBlockAndUpdate(new BlockPos(x,y,z),entity==2?Blocks.WATER.defaultBlockState():y<=-61?Blocks.SMOOTH_STONE.defaultBlockState():Blocks.AIR.defaultBlockState());
            }
        }
        if(MECHANICALS){
            for(int x=-2;x<=2;x++)for(int z=-2;z<=2;z++){
                world.setBlockAndUpdate(new BlockPos(x,-55,z),entity==2&&(pose==8||pose==9)?Blocks.SMOOTH_STONE.defaultBlockState():Blocks.AIR.defaultBlockState());
                world.setBlockAndUpdate(new BlockPos(x,-61,z),(DETAILS?entity==1:entity==3)?Blocks.SAND.defaultBlockState():Blocks.SMOOTH_STONE.defaultBlockState());
            }
        }
        if(BEASTS){
            for(int x=-8;x<=8;x++)for(int z=-8;z<=8;z++){
                world.setBlockAndUpdate(new BlockPos(x,-63,z),Blocks.SMOOTH_STONE.defaultBlockState());
                for(int y=-62;y<=-60;y++)world.setBlockAndUpdate(new BlockPos(x,y,z),beastSpecies(index)==1?Blocks.WATER.defaultBlockState():y<=-61?Blocks.SMOOTH_STONE.defaultBlockState():Blocks.AIR.defaultBlockState());
            }
            for(int x=-2;x<=2;x++)for(int z=-3;z<=3;z++)world.setBlockAndUpdate(new BlockPos(x,-55,z),beastCeiling(index)?Blocks.SMOOTH_STONE.defaultBlockState():Blocks.AIR.defaultBlockState());
        }
        var type=NINTH?(entity==0?BlueprintEntities.FUHUN_BAIBU_TONGZI.get():BlueprintEntities.ZHIREN_JIANKE.get()):EIGHTH?(entity==0?BlueprintEntities.SHANJING_SHANXIAO.get():BlueprintEntities.ZUWU_DAOSHOU.get()):SEVENTH?switch(entity){case 0->BlueprintEntities.SHIBIAN_LISHI.get();case 1->BlueprintEntities.YINBING_GUIZU.get();case 2->BlueprintEntities.YINYANG_ZHIJIAO_YOUHUN.get();default->BlueprintEntities.ZHENWANG_ZHANGQIGUAN.get();}:SIXTH?switch(entity){case 0->BlueprintEntities.LUDUN_JIASHI.get();case 1->BlueprintEntities.MUXUE_FEILU.get();case 2->BlueprintEntities.PIJIA_PANJIANG_HUWEI.get();default->BlueprintEntities.TIESUO_CHIHOU.get();}:ARMIES?switch(entity){case 0->BlueprintEntities.JUMA_CHANGQIANGBING.get();case 1->BlueprintEntities.KUIJUN_SISHI.get();case 2->BlueprintEntities.KUMU_SHUJING.get();default->BlueprintEntities.LIANNU_ZHENZU.get();}:BEASTS?switch(beastSpecies(index)){case 0->BlueprintEntities.BAIMU_MOWU.get();case 1->BlueprintEntities.BISHUI_XUANJIAO_YOUZI.get();case 2->BlueprintEntities.CHIMU_ZHUHA.get();default->BlueprintEntities.FUFA_JIJIU.get();}:DETAILS?switch(entity){case 0->BlueprintEntities.QINGTONG_SHUANGTOUSHEKUI.get();case 1->BlueprintEntities.MINGSHA_SHIXIE.get();default->BlueprintEntities.BAZU_DIGONGZHU.get();}:MECHANICALS?switch(entity){case 0->BlueprintEntities.QINGTONG_SHUANGTOUSHEKUI.get();case 1->BlueprintEntities.XUNSHAN_MUJIAQUAN.get();case 2->BlueprintEntities.BAZU_DIGONGZHU.get();default->BlueprintEntities.MINGSHA_SHIXIE.get();}:FLOATERS?switch(entity){case 0->BlueprintEntities.YOUDENG_GUIMIANFU.get();case 1->BlueprintEntities.XUEJU_MANGGUYU.get();default->BlueprintEntities.SHASHUI_FUNIGUI.get();}:switch(entity){case 0->BlueprintEntities.JUBI_SHIGANDANG.get();case 1->BlueprintEntities.JULI_BIXI_KUILEI.get();default->BlueprintEntities.TONGBI_FEITIAN_YECHA.get();};
        double actorY=EIGHTH&&entity==0&&(pose==8||pose==9)?-58:SIXTH&&entity==1?-56.5:beastCeiling(index)?-55.875:MECHANICALS&&entity==2&&(pose==8||pose==9)?-56.4:FLOATERS&&entity==0?-58.2:-60;
        fixture=type.create(world);fixture.moveTo(0,actorY,0,0,0);fixture.setNoAi(true);fixture.setNoGravity(true);fixture.setPersistenceRequired();world.addFreshEntity(fixture);
        var cow=EntityType.COW.create(world);cow.moveTo(0,-60,scorpionSettles(index)?40:MECHANICALS&&entity==0&&(pose==8||pose==9)?(DETAILS?-4.5:4.5):DETAILS&&entity==0?-2:FLOATERS&&entity==2?1.4:2,180,0);cow.setNoAi(true);cow.setNoGravity(true);
        cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);cow.setHealth(1000);
        cow.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.INVISIBILITY,12000,0,false,false,false));
        // Hurt is a fresh two-tick fixture; the vanilla target's initial effect
        // packets can arrive after that frame. Keep it outside the camera ray.
        if(pose==10)cow.moveTo(12,-60,8,180,0);
        world.addFreshEntity(cow);target=cow;
        if(NINTH){
            if(entity==1&&(pose==4||pose==5))fixture.setTarget(cow);
            if(entity==0&&(pose==8||pose==9)){
                cow.discard();var player=server.getPlayerList().getPlayers().get(0);
                player.setGameMode(GameType.SURVIVAL);player.teleportTo(world,0,-60,5,0,0);player.getFoodData().setFoodLevel(20);
                player.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.INVISIBILITY,1200,0,false,false,false));target=player;
                return new Snapshot(index,fixture.getId(),fixture.getUUID().toString(),-1,ArmySkills.CHILD_CURSE,world.getGameTime());
            }
            if(entity==1&&(pose==8||pose==9)){
                var before=fixture.position();float health=fixture.getHealth();
                fixture.hurt(fixture.damageSources().mobAttack(cow),health+100);
                double distance=fixture.position().distanceTo(cow.position());
                if(!fixture.isAlive()||fixture.skillId()!=ArmySkills.PAPER_SHED||Math.abs(distance-5)>.05||fixture.position().distanceToSqr(before)<1)throw new AssertionError("Real lethal melee did not substitute five blocks behind target");
                paperShedEvidence="actualLethalMelee health="+health+"->"+fixture.getHealth()+" position="+before+"->"+fixture.position()+" target="+cow.position()+" distance="+distance+" epoch="+fixture.skillStartTime();
                return new Snapshot(index,fixture.getId(),fixture.getUUID().toString(),fixture.skillStartTime(),ArmySkills.PAPER_SHED,fixture.skillStartTime());
            }
        }
        if(EIGHTH){
            world.getEntitiesOfClass(TemplateProjectile.class,new net.minecraft.world.phys.AABB(-30,-64,-30,30,-35,30)).forEach(Entity::discard);
            for(int x=-5;x<=5;x++)for(int y=-60;y<=-40;y++)world.setBlockAndUpdate(new BlockPos(x,y,1),EIGHTH_WALL&&entity==0&&pose<6?Blocks.SMOOTH_STONE.defaultBlockState():Blocks.AIR.defaultBlockState());
            for(int x=-1;x<=1;x++)for(int z=-1;z<=1;z++)for(int y=-60;y<=-59;y++)world.setBlockAndUpdate(new BlockPos(x,y,z),entity==0&&((pose==8||pose==9)||EIGHTH_WALL&&pose<6&&z==1)?Blocks.SMOOTH_STONE.defaultBlockState():Blocks.AIR.defaultBlockState());
            if(entity==0&&(pose==6||pose==7)){cow.moveTo(0,-60,6,180,0);fixture.setNoAi(false);fixture.setNoGravity(false);}
            if(entity==0&&(pose==8||pose==9)){
                cow.moveTo(0,-60,10,180,0);fixture.setNoAi(false);fixture.setNoGravity(false);fixture.setTarget(null);
                return new Snapshot(index,fixture.getId(),fixture.getUUID().toString(),-1,TemplateSkills.ROCK_THROW,world.getGameTime());
            }
            if(EIGHTH_WALL&&entity==0&&pose<6){
                // Actual collision and ordinary travel produce CLIMBING/contact metadata.
                cow.moveTo(0,-48,3,180,0);fixture.moveTo(0,-60,.5,0,0);fixture.setTarget(cow);fixture.setNoAi(false);fixture.setNoGravity(false);fixture.setDeltaMovement(0,0,.12);
                return new Snapshot(index,fixture.getId(),fixture.getUUID().toString(),-1,0,world.getGameTime());
            }
        }
        if(SEVENTH){
            world.getEntitiesOfClass(CorpseMiasma.class,new net.minecraft.world.phys.AABB(-24,-64,-24,24,-40,24)).forEach(Entity::discard);
            if(entity==0&&(pose==4||pose==5))fixture.setTarget(cow);
            if(entity==3&&(pose==8||pose==9)){
                auraAlly=BlueprintEntities.JUMA_CHANGQIANGBING.get().create(world);auraAlly.moveTo(3,-60,-2,0,0);auraAlly.setNoAi(true);auraAlly.setNoGravity(true);
                auraAlly.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.INVISIBILITY,12000,0,false,false,false));world.addFreshEntity(auraAlly);
            }
            if(entity==1&&(pose==8||pose==9)){
                var before=fixture.position();float health=fixture.getHealth();int attempts=0;
                while(fixture.skillId()!=ArmySkills.GHOST_PHASE&&attempts++<20){fixture.invulnerableTime=0;fixture.hurt(fixture.damageSources().mobAttack(cow),.2F);}
                if(fixture.skillId()!=ArmySkills.GHOST_PHASE||fixture.position().distanceToSqr(before)<1)throw new AssertionError("Real melee attacks did not trigger side phase");
                ghostEvadeEvidence="actualMeleeAttempts="+attempts+" health="+health+"->"+fixture.getHealth()+" position="+before+"->"+fixture.position();
                return new Snapshot(index,fixture.getId(),fixture.getUUID().toString(),fixture.skillStartTime(),ArmySkills.GHOST_PHASE,fixture.skillStartTime());
            }
        }
        if(SIXTH){
            world.getEntitiesOfClass(com.dynasty.blueprint.SkullBloodPool.class,new net.minecraft.world.phys.AABB(-24,-64,-24,24,-40,24)).forEach(Entity::discard);
            if(pose!=10)cow.moveTo(0,-60,entity==3&&!SIXTH_DETAILS&&(pose==8||pose==9)?10:2,180,0);
            if(entity==1&&(pose==6||pose==7)||entity==3&&!SIXTH_DETAILS&&(pose==8||pose==9))fixture.setNoAi(false);
            if(entity==3&&!SIXTH_DETAILS&&(pose==8||pose==9))fixture.setNoGravity(false);
            if(entity==2&&(pose==8||pose==9)){
                float before=fixture.getHealth();
                for(int hit=0;hit<3;hit++){
                    fixture.invulnerableTime=0;
                    if(!fixture.hurt(fixture.damageSources().mobAttack(cow),2))throw new AssertionError("Real frontal guard hit was rejected");
                }
                if(fixture.skillId()!=ArmySkills.AXE_COUNTER||before-fixture.getHealth()<=0)throw new AssertionError("Three real frontal hits did not trigger counter");
                guardHitEvidence="actualFrontalHits=3 health="+before+"->"+fixture.getHealth()+" skill="+fixture.skillId()+" epoch="+fixture.skillStartTime();
                return new Snapshot(index,fixture.getId(),fixture.getUUID().toString(),fixture.skillStartTime(),ArmySkills.AXE_COUNTER,fixture.skillStartTime());
            }
        }
        if(ARMIES){
            cow.moveTo(0,-60,entity==3&&pose>=6&&pose<=7||entity==2&&pose>=8&&pose<=9&&!ARMY_DETAILS?6:2,180,0);
            if(entity==0&&(pose==8||pose==9)){
                cow.moveTo(0,-60,5.5,180,0);cow.setNoAi(false);cow.setNoGravity(false);
                cow.setSprinting(true);cow.setDeltaMovement(0,0,-.3);
                if(!ArmyBehaviors.charging(cow,fixture.position()))throw new AssertionError("Actual approaching target did not gate brace");
            }
            if(entity==1&&pose>=6&&pose<=9)fixture.setTarget(cow);
            if(entity==3&&(pose==8||pose==9)){fixture.setNoAi(false);fixture.setNoGravity(false);}
            if(entity==2&&pose!=11&&!(ARMY_DETAILS&&pose<4)){
                if(!fixture.hurt(fixture.damageSources().mobAttack(cow),1)||!fixture.treeAwake()||fixture.skillId()!=ArmySkills.TREE_WAKE)throw new AssertionError("Real damage did not awaken tree");
                if(armyTreeWake(index))return new Snapshot(index,fixture.getId(),fixture.getUUID().toString(),fixture.skillStartTime(),ArmySkills.TREE_WAKE,fixture.skillStartTime());
            }
            if(armyDeferred(index))return new Snapshot(index,fixture.getId(),fixture.getUUID().toString(),-1,(pose==8||pose==9)?SPECIAL[entity]:pose>=6&&pose<=7?BASIC[entity]:0,world.getGameTime());
        }
        if(BEASTS){
            double distance=beastCeiling(index)?4.5:beastSpecies(index)==3?6:beastSpecies(index)==2&&pose>=8&&pose<=9&&!BEAST_DETAILS?6:2;
            cow.moveTo(0,beastCeiling(index)?actorY-1.2:-60,distance,180,0);
            if(beastSpecies(index)==3&&(pose==8||pose==9)){
                cow.discard();var ally=BlueprintEntities.ZUWU_DAOSHOU.get().create(world);ally.moveTo(0,-60,6,180,0);ally.setNoAi(true);ally.setNoGravity(true);
                ally.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.INVISIBILITY,12000,0,false,false,false));world.addFreshEntity(ally);target=ally;
            }
            if(beastDeferred(index)){
                if(beastSpecies(index)==2){fixture.setNoAi(false);fixture.setNoGravity(false);}
                return new Snapshot(index,fixture.getId(),fixture.getUUID().toString(),-1,pose>=8?SPECIAL[entity]:pose>=6?BASIC[entity]:0,world.getGameTime());
            }
        }
        if(scorpionSettles(index)){
            // Ordinary AI on real sand enters burrow; freeze only after observing that state.
            fixture.setNoAi(false);fixture.setNoGravity(false);
            return new Snapshot(index,fixture.getId(),fixture.getUUID().toString(),-1,pose>=8?SPECIAL[entity]:0,world.getGameTime());
        }
        if(pose==4||pose==5){fixture.setSprinting(pose==5);fixture.setDeltaMovement(0,0,.075);}
        if(pose==6||pose==7||pose==8||pose==9){int skill=pose<8?BASIC[entity]:SPECIAL[entity];
            // Fluid flags are set by actual entity ticks, never fabricated for canStart.
            if(FLOATERS&&entity==2||MECHANICALS&&entity==2&&(pose==8||pose==9))return new Snapshot(index,fixture.getId(),fixture.getUUID().toString(),-1,skill,world.getGameTime());
            if(!fixture.startSkill(skill,target))throw new AssertionError("Production startSkill rejected "+skill);}
        if(pose==10)fixture.hurt(fixture.damageSources().generic(),1);
        if(pose==11)fixture.hurt(fixture.damageSources().generic(),10000);
        return new Snapshot(index,fixture.getId(),fixture.getUUID().toString(),fixture.skillStartTime(),fixture.skillId(),world.getGameTime());
    }

    @SubscribeEvent public static void serverTick(TickEvent.ServerTickEvent event){
        if(!ENABLED||done||event.phase!=TickEvent.Phase.START||fixture==null||fixture.isRemoved())return;
        if(ARMIES&&fixture.kind()==TemplateMob.Kind.POWDER&&serverPose==11&&fixture.isDeadOrDying()){
            // Keep the pose-9 real explosion intact. Only the separate corpse
            // inspection fixture clears its environmental fire after real death.
            fixture.clearFire();fixture.setSharedFlagOnFire(false);
            if(target!=null){target.clearFire();target.setSharedFlagOnFire(false);}
            for(int x=-8;x<=8;x++)for(int y=-60;y<=-56;y++)for(int z=-8;z<=8;z++){
                var p=new BlockPos(x,y,z);var state=fixture.level().getBlockState(p);
                if(state.is(Blocks.FIRE)||state.is(Blocks.SOUL_FIRE))fixture.level().setBlockAndUpdate(p,Blocks.AIR.defaultBlockState());
            }
        }
        if(NINTH&&target instanceof net.minecraft.server.level.ServerPlayer player){actualSoulBind=player.hasEffect(BlueprintEntities.SOUL_BIND.get());actualFood=player.getFoodData().getFoodLevel();}
        if(EIGHTH){
            actualProjectiles=fixture.level().getEntitiesOfClass(TemplateProjectile.class,new net.minecraft.world.phys.AABB(-30,-64,-30,30,-35,30)).size();
            if(EIGHTH_WALL&&serverPose<6){
                var v=fixture.getDeltaMovement();fixture.setDeltaMovement(0,v.y,.12);fixture.hasImpulse=true;fixture.hurtMarked=true;
                wallEvidence="actualCollision="+fixture.horizontalCollision+" face="+fixture.climbFace()+" contact="+fixture.climbContactDistance()+" position="+fixture.position();
            }
        }
        if(SEVENTH){
            actualMiasma=fixture.level().getEntitiesOfClass(CorpseMiasma.class,new net.minecraft.world.phys.AABB(-8,-64,-8,8,-50,8)).size();
            actualAura=auraAlly!=null&&auraAlly.hasEffect(BlueprintEntities.JUNHUN_AURA.get());
        }
        if(SIXTH&&fixture.kind()==TemplateMob.Kind.SKULL)actualBloodPools=fixture.level().getEntitiesOfClass(com.dynasty.blueprint.SkullBloodPool.class,new net.minecraft.world.phys.AABB(-8,-64,-8,8,-50,8)).size();
        if(wetAction!=null&&fixture.level().getGameTime()>=wetAt){
            var ready=wetAction;wetAction=null;
            try{
                if(eighthDeferred(wetIndex)){
                    if(EIGHTH_WALL&&wetIndex%12<6){
                        if(!fixture.onClimbable()||fixture.climbFace()==null||!fixture.horizontalCollision)throw new AssertionError("Actual wall collision did not produce climb contact: "+wallEvidence);
                        ready.complete(new Snapshot(wetIndex,fixture.getId(),fixture.getUUID().toString(),fixture.skillStartTime(),0,fixture.level().getGameTime()));return;
                    }
                    if(!fixture.onGround()||fixture.getY()<=target.getY()+1.5||fixture.level().getBlockState(fixture.blockPosition().below()).isAir())throw new AssertionError("Actual high-ground landing missing");
                    highGroundEvidence="actualOnGround="+fixture.onGround()+" height="+fixture.getY()+" targetY="+target.getY()+" floor="+fixture.level().getBlockState(fixture.blockPosition().below());
                    fixture.setNoAi(true);
                }
                if(ARMIES&&wetIndex/12==1){
                    if(fixture.skillId()!=ArmySkills.DETONATE||fixture.skillStartTime()<0)throw new AssertionError("Actual forty near ticks did not light powder fuse");
                    ready.complete(new Snapshot(wetIndex,fixture.getId(),fixture.getUUID().toString(),fixture.skillStartTime(),fixture.skillId(),fixture.skillStartTime()));
                    return;
                }
                if(ARMIES&&wetIndex/12==2){
                    if(!fixture.treeAwake()||fixture.skillId()!=0)throw new AssertionError("Real tree awakening did not finish");
                    int pose=wetIndex%12;
                    if(pose==4||pose==5){fixture.setSprinting(pose==5);fixture.setDeltaMovement(0,0,.075);}
                    if(pose==10)fixture.hurt(fixture.damageSources().generic(),1);
                }
                if(FLOATERS&&(!fixture.isInWater()||!target.isInWater()))throw new AssertionError("Pond fixture did not become wet by normal entity ticks");
                if(BEASTS){
                    if(beastCeiling(wetIndex)&&!fixture.hanging())throw new AssertionError("Real centipede ceiling support missing");
                    if(beastSpecies(wetIndex)==1&&(!fixture.isInWater()||!target.isInWater()))throw new AssertionError("Deep pond fixture did not become wet");
                    if(beastSpecies(wetIndex)==2){
                        if(!fixture.onGround())throw new AssertionError("Toad did not settle on real ground");
                        if(wetSkill!=ArmySkills.TOAD_LEAP){fixture.setNoAi(true);fixture.setNoGravity(true);}
                        if(wetSkill==ArmySkills.TOAD_BURST){
                            // Trigger the production damage gate only after settling and freezing AI,
                            // so ordinary AI cannot consume the burst before the operator's start.
                            float before=fixture.getHealth();
                            if(!fixture.hurt(fixture.damageSources().generic(),10)||before-fixture.getHealth()<6)throw new AssertionError("Actual burst trigger did not lose six health");
                        }
                    }
                }
                if(scorpionSettles(wetIndex)){
                    if(!fixture.burrowed()||!fixture.onGround())throw new AssertionError("Real sand/AI did not produce burrow state");
                    fixture.setNoAi(true);target.moveTo(0,-60,2,180,0);
                }else if(MECHANICALS){
                    if(!fixture.hanging())throw new AssertionError("Physical ceiling did not produce hanging state");
                    // Vanilla living travel/gravity requires effective AI; hold actions suppress travel on the ceiling.
                    fixture.setNoAi(false);
                }
                if(wetSkill!=0&&!fixture.startSkill(wetSkill,target))throw new AssertionError("Production deferred startSkill rejected "+wetSkill);
                ready.complete(new Snapshot(wetIndex,fixture.getId(),fixture.getUUID().toString(),fixture.skillStartTime(),fixture.skillId(),fixture.level().getGameTime()));
            }catch(Throwable e){ready.completeExceptionally(e);}
        }
        if(DETAILS&&fixture.kind()==TemplateMob.Kind.MINING_SPIDER&&serverPose==9){
            serverDropState="tick="+fixture.level().getGameTime()+" pos="+fixture.position()+" ground="+fixture.onGround()+" gravity="+!fixture.isNoGravity()+" hanging="+fixture.hanging()+" skill="+fixture.skillId()+" targetHealth="+target.getHealth();
            if(fixture.onGround()&&fixture.skillId()==0)landedEntity=fixture.getId();
        }
        if(ARMIES&&fixture.kind()==TemplateMob.Kind.POWDER&&serverPose==9&&fixture.isDeadOrDying()&&target.getHealth()<1000){
            detonatedEntity=fixture.getId();serverBlastState="tick="+fixture.level().getGameTime()+" actualDead=true targetHealth="+target.getHealth()+" position="+fixture.position();
        }
        if(ARMIES&&fixture.kind()==TemplateMob.Kind.SPEAR&&(serverPose==8||serverPose==9)&&target.isAlive()){
            target.setSprinting(true);target.setDeltaMovement(0,target.getDeltaMovement().y,-.3);target.hasImpulse=true;target.hurtMarked=true;
        }
        if((serverPose==4||serverPose==5)&&!(EIGHTH_WALL&&fixture.kind()==TemplateMob.Kind.BEAST)){
            fixture.setSprinting(serverPose==5);fixture.setDeltaMovement(0,0,.075);
            fixture.hasImpulse=true;fixture.hurtMarked=true;
        }
    }

    @SubscribeEvent public static void render(TickEvent.RenderTickEvent event){
        if(!ENABLED||done||event.phase!=TickEvent.Phase.END||captured||current==null)return;
        var mc=Minecraft.getInstance();if(mc.level==null||mc.getOverlay()!=null||!(mc.level.getEntity(current.entityId) instanceof TemplateMob mob))return;
        try {
            int entity=current.index/12,pose=current.index%12;long age=mc.level.getGameTime()-current.published;
            int desired=pose==4||pose==5?4:pose==6?(DETAILS&&entity==1?8:MECHANICALS||BEASTS||ARMIES||SIXTH||SEVENTH||EIGHTH||NINTH?CONTACT[entity]-4:12):pose==7?CONTACT[entity]:pose==8?(DETAILS&&entity==2?14:SPECIAL_CONTACT[entity]-6):pose==9?SPECIAL_CONTACT[entity]:pose==10?2:pose==11?30:30;
            // Knee contact is only six ticks: its fresh client entity must
            // receive the real skill epoch before photographing the windup.
            if(NINTH&&entity==1&&(pose==6||pose==8))desired=2;
            if(NINTH&&entity==1&&pose==8)desired=paperRecoveryCaptured?12:3;
            if(NINTH&&entity==1&&pose==11)desired=7;
            if(SIXTH_DETAILS&&entity==3&&pose==8)desired=3;
            if(SEVENTH&&entity==1&&pose==8)desired=3;
            boolean ghostReturn=SEVENTH&&entity==1&&pose==9&&ghostReturnCaptured;
            boolean aura=SEVENTH&&entity==3&&pose==9&&flagAuraCaptured;
            if(ghostReturn)desired=10;
            if(aura)desired=22;
            boolean apeFlight=EIGHTH&&!EIGHTH_WALL&&entity==0&&pose==7&&apeFlightCaptured;
            if(apeFlight)desired=18;
            boolean jump=BEASTS&&!BEAST_DETAILS&&entity==2&&pose==9;
            if(jump&&jumpContactCaptured)desired=16;
            boolean blast=ARMIES&&entity==1&&pose==9&&powderPreblastCaptured;
            if(blast)desired=22;
            boolean skullFlight=SIXTH&&entity==1&&pose==7&&skullFlightCaptured;
            boolean hookCatch=SIXTH&&!SIXTH_DETAILS&&entity==3&&pose==9&&scoutHookCaptured;
            if(skullFlight)desired=20;
            if(hookCatch)desired=22;
            if(age<desired)return;
            if(NINTH&&entity==1&&(pose==8||pose==9)&&mob.position().distanceTo(target.position())<4.9){
                if(age>desired+7)throw new AssertionError("Real paper landing not received by client");return;
            }
            // Server START precedes the production impact in that same tick.
            if(NINTH&&entity==0&&pose==9&&(!actualSoulBind||actualFood!=18)){
                if(age>desired+7)throw new AssertionError("Actual player curse contact absent: food="+actualFood);
                return;
            }
            if(EIGHTH&&entity==0&&pose==9&&actualProjectiles==0){if(age>desired+7)throw new AssertionError("Actual rock release did not create projectile");return;}
            if(SEVENTH&&entity==2&&pose==9&&mob.hookTargetId()<0){if(age>desired+7)throw new AssertionError("Actual palanquin contact did not hold its target");return;}
            if(SIXTH&&entity==1&&pose==9&&actualBloodPools==0){if(age>desired+7)throw new AssertionError("Actual blood contact did not create its pool");return;}
            if(hookCatch&&mob.hookTargetId()<0){if(age>35)throw new AssertionError("Real projectile never linked the target");return;}
            boolean landed=DETAILS&&entity==2&&pose==9;
            if(landed&&(landedEntity!=mob.getId()||Math.abs(mob.getY()+60)>.08)){if(age>50)throw new AssertionError("Actual landing not observed: "+serverDropState);return;}
            if((pose>=6&&pose<=10)&&age>desired+(hookCatch?13:7))throw new AssertionError("Missed action frame "+POSES[pose]+" age="+age);
            if(pose<4&&settled<25)return;
            if(++frames<2)return;
            if(!(mc.getEntityRenderDispatcher().getRenderer(mob) instanceof TemplateMobRenderer renderer))throw new AssertionError("Wrong renderer");
            var model=renderer.getGeoModel();String id=IDS[entity];
            String poseLabel=NINTH&&entity==1&&pose==8&&paperRecoveryCaptured?"actual-paper-reformed":EIGHTH_WALL&&pose<6?(pose==3?"mounted-opposite45":"mounted-"+POSES[pose]):apeFlight?"actual-pounce-flight":ghostReturn?"actual-phase-return":aura?"actual-ally-aura":skullFlight?"actual-dive-flight":hookCatch?"actual-hook-catch":blast?"actual-detonation":ARMIES&&entity==1&&pose==9?"fuse-preblast":ARMY_DETAILS&&entity==2&&pose<4?"camouflage-"+POSES[pose]:armyTreeWake(current.index)?"wake-"+POSES[pose]:jump&&jumpContactCaptured?"actual-jump-flight":beastCeiling(current.index)&&pose<4?"hanging-"+POSES[pose]:DETAILS&&entity==1&&pose<4?"burrow-"+POSES[pose]:landed?"actual-landing":POSES[pose];
            if(!model.getTextureResource(mob).getPath().equals("textures/entity/blueprint/"+(NINTH?"cod2_voxel/":"")+id+".png"))throw new AssertionError("Dedicated texture not bound");
            try(var stream=mc.getResourceManager().open(model.getTextureResource(mob));var image=NativeImage.read(stream)){
                if(image.getWidth()!=16||image.getHeight()!=16)throw new AssertionError("Runtime texture resolution differs");
            }
            String[] required=NINTH?(entity==0?new String[]{"mourning_collar","robe_front","lantern_flame","lamp_inertia","ribbon_spring_2","right_grip"}:new String[]{"waist_upper","paper_crown","right_folded_sleeve","left_paper_skirt","paper_sword","right_grip"}):EIGHTH?(entity==0?new String[]{"right_climb_wrist","left_foot_contact","ape_brow","right_ape_cheek","held_rock","tail_hook"}:new String[]{"waist_upper","helmet","right_grip","dao","scabbard","left_rag"}):SEVENTH?switch(entity){case 0->new String[]{"belly","vein_chest","right_finger_4_2","corpse_jaw","left_broken_lock"};case 1->new String[]{"ghost_pelvis","ghost_waist","ghost_ge","right_grip","smoke_tail_2"};case 2->new String[]{"cabin","curtain_2","right_ghost_hand","bearer_3_chest","bearer_3_smoke"};default->new String[]{"waist_upper","flag_spring_3","flag_cloth_3","right_grip","left_grip","ghost_shadow_hood"};}:SIXTH?switch(entity){case 0->new String[]{"waist_upper","helmet","left_grip","shield_grip","mace","left_shoulder_rail"};case 1->new String[]{"jaw","helmet","viscera_spring_3","viscera_3_3","neck_stump"};case 2->new String[]{"right_grip","right_axe","left_axe","left_beast_shoulder","cape_lower"};default->new String[]{"waist_upper","headwrap","right_chain_spring","left_chain_7","right_claw","rope_pack"};}:ARMIES?switch(entity){case 0->new String[]{"waist_upper","iron_crown","spear_2","left_grip","skirt_spring_front"};case 1->new String[]{"waist_upper","blindfold","right_powder_jar","left_broken_dao","right_fuse_tip"};case 2->new String[]{"lower_log","tree_heart","root_spring_5","root_tip_5","crown_branch_3"};default->new String[]{"waist_upper","headband","arrow_box","crossbow_lever","crossbow_tongue","left_grip"};}:BEASTS?switch(beastSpecies(current.index)){case 0->new String[]{"segment_15","eye_15","left_jaw","right_leg_15_foot"};case 1->new String[]{"spine_13","jaw","fin_spring_13","horn_1","pectoral_-1"};case 2->new String[]{"tongue_reach","tongue_4","mouth_jaw","venom_gland_7","left_hind_foot"};default->new String[]{"pelvis","waist_upper","chest","right_grip","staff","talisman_tip_2","right_sleeve_inner_spring"};}:DETAILS&&entity==1?new String[]{"shell_plate_3","leg_ik_knee_5","right_pincer_tip","tail_6","tail_stinger"}:MECHANICALS?switch(entity){case 0->new String[]{"joint_9","front_nozzle","rear_head","rear_nozzle"};case 1->new String[]{"waist","haunch","winding_key","tail_tip","foot_3"};case 2->new String[]{"head","abdomen","left_mandible","hip_7","drill_7"};default->new String[]{"shell_plate_3","leg_ik_knee_5","right_pincer_tip","tail_6","tail_stinger"};}:FLOATERS?switch(entity){case 0->new String[]{"face","left_finger_3","right_claw","lantern","flame"};case 1->new String[]{"jaw","spine_7","tail_tip","left_fin_tip","dorsal_6"};default->new String[]{"pelvis","waist","neck","wave_2","right_whip_2","hair_6"};}:switch(entity){case 0->new String[]{"waist","chest","right_fist","inscription"};case 1->new String[]{"plastron","stele","front_left_foot","tail_tip"};default->new String[]{"waist","chest","left_wing_2","giant_arm_4","palm","finger_2"};};
            for(String bone:required)
                if(model.getBone(bone).isEmpty())throw new AssertionError("Missing baked bone "+bone);
            var controller=mob.getAnimatableInstanceCache().getManagerForId(mob.getId()).getAnimationControllers().get("body");
            String actual=controller==null||controller.getCurrentAnimation()==null?"none":controller.getCurrentAnimation().animation().name();
            String wanted="animation."+id+"."+mob.visualAnimation();
            if(EIGHTH_WALL&&pose<6&&!wanted.endsWith(".climb"))throw new AssertionError("Actual wall did not select climb clip");
            if(!(EIGHTH_WALL&&pose<6)&&(pose==4&&!wanted.endsWith(".walk")||pose==5&&!wanted.endsWith(".run")))throw new AssertionError("Locomotion fixture did not move: "+wanted);
            if(!actual.equals(wanted)||controller.getAnimationState().name().equals("STOPPED"))throw new AssertionError("Gecko clip differs "+actual+" expected "+wanted);
            if(pose>=6&&pose<=9&&!landed&&!blast&&(mob.skillId()!=current.skill||mob.skillStartTime()!=current.start))throw new AssertionError("Action epoch not synchronized");
            if(blast&&(!mob.isDeadOrDying()||detonatedEntity!=mob.getId()||mob.skillStartTime()==current.start))throw new AssertionError("Actual timed powder detonation missing: "+serverBlastState);
            if(ARMIES&&entity==2&&!mob.isDeadOrDying()&&mob.treeAwake()==(ARMY_DETAILS&&pose<4))throw new AssertionError("Actual tree camouflage/wake state differs");
            if(FLOATERS&&entity==2&&pose==9&&!mob.waterPool())throw new AssertionError("Real pool contact did not flatten body");
            if(beastCeiling(current.index)&&!mob.hanging())throw new AssertionError("Centipede hanging state not synchronized");
            if(BEASTS&&beastSpecies(current.index)==1&&pose==9&&!mob.isInWater())throw new AssertionError("Actual coil did not render in water");
            if(BEASTS&&beastSpecies(current.index)==2&&pose==7){
                float visualReach=model.getBone("tongue_reach").orElseThrow().getScaleZ();
                if(Math.abs(visualReach-mob.tongueReach()/5)>.001||visualReach<=0)throw new AssertionError("Tongue procedural reach differs");
            }
            if(BEASTS&&beastSpecies(current.index)==3&&pose==9&&mob.buffTargetId()<0)throw new AssertionError("Actual priest support target absent");
            if(jump&&jumpContactCaptured&&(mob.onGround()||mob.getY()<=-59.8))throw new AssertionError("Actual toad impulse did not produce flight");
            if(DETAILS&&entity==1&&pose<4&&!mob.burrowed())throw new AssertionError("Burrow pose lost real sand state");
            if(landed&&(mob.skillId()!=0||mob.skillStartTime()==current.start))throw new AssertionError("Landing did not cancel the production drop action");
            if(skullFlight&&mob.position().distanceToSqr(new net.minecraft.world.phys.Vec3(0,-56.5,0))<.25)throw new AssertionError("Real skull impulse did not move the entity");
            if(hookCatch&&mob.hookTargetId()!=target.getId())throw new AssertionError("Grapple linked a different real target");
            if(SEVENTH&&entity==1&&(pose==8||pose==9)){
                if(ghostEvadeEvidence.isEmpty()||mob.position().distanceToSqr(new net.minecraft.world.phys.Vec3(0,-60,0))<1)throw new AssertionError("Real ghost teleport missing");
                if(mob.isPhased()==ghostReturn)throw new AssertionError("Actual six-tick phase visibility differs");
            }
            if(SEVENTH&&entity==2&&pose==9&&mob.hookTargetId()!=target.getId())throw new AssertionError("Palanquin held the wrong real target");
            if(aura&&!actualAura)throw new AssertionError("Actual standard bearer aura missing on its real ally");
            if(SEVENTH&&entity==0&&pose==10&&actualMiasma<1)throw new AssertionError("Actual damage did not create corpse miasma");
            if(EIGHTH_WALL&&pose<6&&(!mob.onClimbable()||mob.climbFace()==null||wallEvidence.isEmpty()))throw new AssertionError("Actual climb metadata disappeared");
            if(apeFlight&&(mob.onGround()||mob.getY()<=-59.5||mob.position().distanceToSqr(new net.minecraft.world.phys.Vec3(0,-60,0))<.25))throw new AssertionError("Actual pounce impulse did not move beast");
            if(EIGHTH&&entity==0&&pose==9&&highGroundEvidence.isEmpty())throw new AssertionError("Real rock high-ground evidence missing");
            if(NINTH&&entity==0&&pose==9&&(!actualSoulBind||actualFood!=18))throw new AssertionError("Actual player curse contact did not bind soul and consume ten percent food: food="+actualFood);
            if(NINTH&&entity==1&&(pose==8||pose==9)&&paperShedEvidence.isEmpty())throw new AssertionError("Real lethal melee evidence missing");
            if(NINTH&&(!model.getModelResource(mob).getPath().equals("geo/blueprint/cod2_voxel/"+id+".geo.json")||!model.getAnimationResource(mob).getPath().equals("animations/blueprint/cod2_voxel/"+id+".animation.json")))throw new AssertionError("Isolated authored rig path not bound");
            if(pose==11&&!mob.isDeadOrDying())throw new AssertionError("Death clip not server synchronized");
            try(var frame=Screenshot.takeScreenshot(mc.getMainRenderTarget())){
                int low=765,high=0;
                for(int x=1;x<8;x++)for(int y=1;y<8;y++){
                    int pixel=frame.getPixelRGBA(frame.getWidth()*x/8,frame.getHeight()*y/8);
                    int light=(pixel&255)+(pixel>>8&255)+(pixel>>16&255);low=Math.min(low,light);high=Math.max(high,light);
                }
                if(high-low<80)throw new AssertionError("Blank/occluded framebuffer: "+id+" "+poseLabel);
                frame.writeToFile(OUT.resolve(String.format("%02d-%s-%s.png",stage,id,poseLabel)));
            }
            var sample=Map.ofEntries(Map.entry("stage",stage),Map.entry("id",id),Map.entry("view",poseLabel),Map.entry("uuid",mob.getUUID().toString()),Map.entry("clip",actual),Map.entry("age",age),Map.entry("actionAge",mob.actionAge(0)),Map.entry("skill",mob.skillId()),Map.entry("start",mob.skillStartTime()),Map.entry("position",mob.position().toString()),Map.entry("width",mob.getBbWidth()),Map.entry("height",mob.getBbHeight()),Map.entry("fps",mc.getFps()),Map.entry("hanging",mob.hanging()),Map.entry("inWater",mob.isInWater()),Map.entry("onGround",mob.onGround()),Map.entry("tongueReach",mob.tongueReach()),Map.entry("buffTargetId",mob.buffTargetId()),Map.entry("treeAwake",mob.treeAwake()),Map.entry("health",mob.getHealth()),Map.entry("hookTargetId",mob.hookTargetId()),Map.entry("actualBloodPools",actualBloodPools),Map.entry("actualGuardHits",guardHitEvidence),Map.entry("actualCorpseMiasma",actualMiasma),Map.entry("actualAllyAura",actualAura),Map.entry("actualGhostEvade",ghostEvadeEvidence),Map.entry("isPhased",mob.isPhased()),Map.entry("actualProjectiles",actualProjectiles),Map.entry("actualWall",wallEvidence),Map.entry("actualHighGround",highGroundEvidence),Map.entry("actualPaperShed",paperShedEvidence),Map.entry("actualSoulBind",actualSoulBind),Map.entry("actualPlayerFood",actualFood),Map.entry("climbFace",String.valueOf(mob.climbFace())),Map.entry("climbDistance",mob.climbContactDistance()));
            REPORT.add(sample);if(landed)REPORT.add(Map.of("actualServerLanding",serverDropState));Files.writeString(OUT.resolve("samples.json"),JSON.toJson(REPORT)+"\n");captured=true;
            if(blast){REPORT.add(Map.of("actualServerDetonation",serverBlastState));Files.writeString(OUT.resolve("samples.json"),JSON.toJson(REPORT)+"\n");}
            if(NINTH&&entity==1&&pose==8&&!paperRecoveryCaptured){paperRecoveryCaptured=true;frames=0;captured=false;}
            if(EIGHTH&&!EIGHTH_WALL&&entity==0&&pose==7&&!apeFlightCaptured){apeFlightCaptured=true;frames=0;captured=false;}
            if(SEVENTH&&entity==1&&pose==9&&!ghostReturnCaptured){ghostReturnCaptured=true;frames=0;captured=false;}
            if(SEVENTH&&entity==3&&pose==9&&!flagAuraCaptured){flagAuraCaptured=true;frames=0;captured=false;}
            if(SIXTH&&entity==1&&pose==7&&!skullFlightCaptured){skullFlightCaptured=true;frames=0;captured=false;}
            if(SIXTH&&!SIXTH_DETAILS&&entity==3&&pose==9&&!scoutHookCaptured){scoutHookCaptured=true;frames=0;captured=false;}
            if(jump&&!jumpContactCaptured){jumpContactCaptured=true;frames=0;captured=false;}
            if(ARMIES&&entity==1&&pose==9&&!powderPreblastCaptured){powderPreblastCaptured=true;frames=0;captured=false;}
        }catch(Throwable failure){finish(mc,failure);}
    }

    private static void finish(Minecraft mc,Throwable error){
        if(done)return;done=true;
        try {
            Files.createDirectories(OUT);
            if(error!=null){error.printStackTrace();try(var f=Screenshot.takeScreenshot(mc.getMainRenderTarget())){f.writeToFile(OUT.resolve("FAILED.png"));}}
            Files.writeString(OUT.resolve(error==null?"PASS.txt":"FAIL.txt"),error==null?
                (ONLY_INDEX>=0?"PASS focused actual pose index "+ONLY_INDEX+" and real resource reload/re-render. Actual server state and active Gecko clip asserted; the isolated fixture visual adjustments are documented with its evidence.\n":(DETAILS?"PASS additional real rear stab/poison, sand-triggered burrow/emerge, claw tick 20 and server landing with settled client pose. ":"PASS: ")+IDS.length+" actual entities rendered front/45/side/back, locomotion, production attacks, special contact, hurt and death; dedicated 16x16 PNGs and baked bones; server action epochs and active Gecko clips; actual resource reload and re-render. Disposable single client fixture, not full dungeon/combat acceptance.\n"):"FAIL: "+error+"\n");
        }catch(Exception e){e.printStackTrace();}mc.stop();
    }
}
