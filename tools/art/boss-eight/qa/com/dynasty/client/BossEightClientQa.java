package com.dynasty.client;

import com.dynasty.blueprint.elite.*;
import com.google.gson.GsonBuilder;
import net.minecraft.client.*;
import net.minecraft.client.gui.screens.*;
import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.item.*;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.*;
import net.minecraft.world.level.levelgen.presets.WorldPresets;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.core.animatable.GeoAnimatable;
import software.bernie.geckolib.model.GeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CompletableFuture;

/** Disposable native art acceptance. Calls production startSkill/swing/hurt/death, not animation triggers. */
@Mod.EventBusSubscriber(modid="dynasty",value=Dist.CLIENT)
public final class BossEightClientQa {
    private static final boolean CHECKLIST=Boolean.getBoolean("dynasty.bossChecklistQa");
    private static final boolean HUMAN_PRESENCE=Boolean.getBoolean("dynasty.bossHumanPresenceQa");
    private static final boolean HUMAN=Boolean.getBoolean("dynasty.bossHumanQa");
    private static final boolean MATERIALS=Boolean.getBoolean("dynasty.bossMaterialQa");
    private static final boolean SPIRITS=MATERIALS||Boolean.getBoolean("dynasty.bossSpiritQa");
    private static final boolean PRESENCE=CHECKLIST||SPIRITS||Boolean.getBoolean("dynasty.bossPresenceQa");
    private static final boolean ENABLED=Boolean.getBoolean("dynasty.bossEightQa");
    private static final Path OUT=Path.of(System.getProperty("dynasty.bossEightQa.output","build/boss-eight-native/results"));
    private static final String[] IDS={"undead_first_emperor","eunuch_mastermind","rebel_general","xianzhen_duantoujiang","qianji_bailian_yanshi","pilin_zhijinwu","baimian_huxiangu","juchui_jinjia_lishi"};
    private record Stage(String id,String label,int skill,int age){}
    private static final List<Stage> STAGES=new ArrayList<>();
    private static final List<String> LOG=new ArrayList<>();
    static {
        String[][] clips={{"roar","spin","throw"},{"net","wheels","spiders"},{"sweep","charge","order"},{"mirror","fire","split"},{"slam","wheel","throw"}};
        int[][] skill={{301,302,303},{321,322,323},{341,342,343},{351,352,353},{361,362,363}};
        int[][] age={{24,26,20},{14,10,20},{20,20,24},{20,20,8},{28,26,36}};
        for(int i=0;i<IDS.length;i++){
            for(String v:new String[]{"front","45","side","back","walk"})STAGES.add(new Stage(IDS[i],v,0,0));
            if(i<3)STAGES.add(new Stage(IDS[i],"attack",-1,2));
            else for(int j=0;j<3;j++)STAGES.add(new Stage(IDS[i],clips[i-3][j],skill[i-3][j],age[i-3][j]));
            STAGES.add(new Stage(IDS[i],"hurt",-2,2));STAGES.add(new Stage(IDS[i],"death",-3,i<3?17:55));
        }
        if(PRESENCE){
            STAGES.clear();
            for(String id:new String[]{IDS[0],IDS[5],IDS[7]}){
                for(String v:new String[]{"front","45","side","back","walk"})STAGES.add(new Stage(id,v,0,0));
                if(id.equals(IDS[0])){
                    STAGES.add(new Stage(id,"attack-contact",-1,1));STAGES.add(new Stage(id,"attack-recovery",-1,16));
                } else if(id.equals(IDS[5])){
                    STAGES.add(new Stage(id,"sweep-tell",341,15));STAGES.add(new Stage(id,"sweep-contact",341,20));STAGES.add(new Stage(id,"sweep-recovery",341,45));
                } else {
                    STAGES.add(new Stage(id,"slam-tell",361,24));STAGES.add(new Stage(id,"slam-contact",361,28));STAGES.add(new Stage(id,"slam-pulse2",361,44));STAGES.add(new Stage(id,"slam-pulse3",361,60));STAGES.add(new Stage(id,"slam-recovery",361,75));
                }
            }
        }
        if(SPIRITS){
            STAGES.clear();
            for(String id:new String[]{IDS[1],IDS[2],IDS[3]}){
                for(String v:new String[]{"front","45","side","back","walk"})STAGES.add(new Stage(id,v,0,0));
                if(id.equals(IDS[1])){
                    STAGES.add(new Stage(id,"attack-contact",-1,1));STAGES.add(new Stage(id,"attack-recovery",-1,19));
                }else if(id.equals(IDS[2])){
                    STAGES.add(new Stage(id,"attack-tell",-1,9));STAGES.add(new Stage(id,"attack-contact",-1,12));STAGES.add(new Stage(id,"attack-recovery",-1,22));
                }else{
                    STAGES.add(new Stage(id,"roar-tell",301,18));STAGES.add(new Stage(id,"roar-contact",301,24));STAGES.add(new Stage(id,"roar-recovery",301,44));
                    STAGES.add(new Stage(id,"spin-contact",302,26));STAGES.add(new Stage(id,"throw-contact",303,20));
                }
            }
        }
        if(MATERIALS)STAGES.removeIf(s -> s.id.equals(IDS[1]));
        if(CHECKLIST){
            STAGES.clear();
            for(String id:new String[]{"nine_heaven_general","dragon_king","dragon_emperor"}){
                for(String v:new String[]{"front","45","side","back","walk"})STAGES.add(new Stage(id,v,0,0));
                STAGES.add(new Stage(id,"attack-tell",-1,1));
                STAGES.add(new Stage(id,"attack-contact",-1,3));
                STAGES.add(new Stage(id,"attack-recovery",-1,5));
                STAGES.add(new Stage(id,"hurt",-2,2));
                STAGES.add(new Stage(id,"death",-3,15));
            }
        }
        if(HUMAN_PRESENCE){
            STAGES.clear();
            for(String id:new String[]{"nine_heaven_general","dragon_king","dragon_emperor"}){
                for(String v:new String[]{"front","45","side","back"})for(String fx:new String[]{"off","on"})STAGES.add(new Stage(id,v+"-"+fx,0,0));
                STAGES.add(new Stage(id,"walk",0,0));
                STAGES.add(new Stage(id,"attack-tell",-1,1));STAGES.add(new Stage(id,"attack-contact",-1,3));STAGES.add(new Stage(id,"attack-recovery",-1,5));
                STAGES.add(new Stage(id,"hurt",-2,2));STAGES.add(new Stage(id,"death",-3,15));
            }
        }
        if(HUMAN_PRESENCE&&Boolean.getBoolean("dynasty.tianjiangAuraEnvironments")){
            STAGES.removeIf(s->!s.id.equals("nine_heaven_general"));
            for(String label:new String[]{"night-off","night-on","far-on","minimal-on","decreased-on"})STAGES.add(new Stage("nine_heaven_general",label,0,0));
        }
        int limit=Integer.getInteger("dynasty.bossEightQa.limit",STAGES.size());
        if(limit<STAGES.size())STAGES.subList(limit,STAGES.size()).clear();
    }
    private static boolean started,done,captured,activated;
    private static final int START=Integer.getInteger("dynasty.bossEightQa.start",0);
    private static int stage=START-1,entityId,settled,rendered;
    private static long actionAt=-1,deadline=System.nanoTime()+850_000_000_000L;
    private static CompletableFuture<Integer> pending;
    private static CompletableFuture<Long> action;
    private static Mob fixture,victim;
    private static String diagnostic="no render";
    private static int auraFrames,lastAuraTick=-1;
    private static net.minecraft.world.phys.Vec3 walkStart;
    @SubscribeEvent public static void tick(TickEvent.ClientTickEvent ev){
        if(!ENABLED||done||ev.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();
        try{
            org.lwjgl.glfw.GLFW.glfwHideWindow(mc.getWindow().getWindow());
            if(System.nanoTime()>deadline)throw new AssertionError("Eight boss native timeout stage="+stage);
            if(mc.getOverlay()!=null)return;
            if(mc.screen instanceof AccessibilityOnboardingScreen)mc.setScreen(new TitleScreen());
            if(!started&&mc.screen instanceof TitleScreen){
                if(!mc.gameDirectory.getCanonicalPath().contains("/build/boss-eight-native/"))throw new AssertionError("Refusing normal save");
                Files.createDirectories(OUT);started=true;mc.options.pauseOnLostFocus=false;mc.options.renderDistance().set(3);mc.options.fov().set(HUMAN_PRESENCE?70:48);mc.options.hideGui=true;mc.options.bobView().set(false);
                mc.options.getSoundSourceOptionInstance(net.minecraft.sounds.SoundSource.MASTER).set(0.0);
                var rules=new GameRules();rules.getRule(GameRules.RULE_DOMOBSPAWNING).set(false,null);rules.getRule(GameRules.RULE_DAYLIGHT).set(false,null);
                mc.createWorldOpenFlows().createFreshLevel("boss-eight-"+System.currentTimeMillis(),new LevelSettings("Disposable eight boss art",GameType.CREATIVE,false,Difficulty.NORMAL,true,rules,WorldDataConfiguration.DEFAULT),new WorldOptions(57,false,false),reg->reg.registryOrThrow(Registries.WORLD_PRESET).getOrThrow(WorldPresets.FLAT).createWorldDimensions());return;
            }
            if(mc.level==null||mc.player==null)return;if(mc.screen!=null)mc.setScreen(null);
            if(pending!=null){if(!pending.isDone())return;entityId=pending.join();pending=null;settled=0;rendered=0;captured=false;activated=false;action=null;actionAt=-1;camera(mc);return;}
            if(stage<START||captured){if(stage==STAGES.size()-1){finish(mc,null);return;}stage++;pending=mc.getSingleplayerServer().submit(()->prepare(mc));return;}
            if(!(mc.level.getEntity(entityId) instanceof Mob mob))return;
            settled++;
            if(HUMAN_PRESENCE&&settled==40)mc.getSingleplayerServer().submit(()->{
                var w=mc.getSingleplayerServer().overworld();
                for(int x=-4;x<=4;x++)for(int z=-4;z<=4;z++)for(int y=-60;y<=-55;y++){
                    var p=new BlockPos(x,y,z);var old=w.getBlockState(p);w.setBlockAndUpdate(p,Blocks.AIR.defaultBlockState());
                    w.sendBlockUpdated(p,old,Blocks.AIR.defaultBlockState(),3);
                }
                return 0;
            });
            if(action!=null&&action.isDone())actionAt=action.join();
            Stage s=STAGES.get(stage);
            if(settled>300)throw new AssertionError("Pose not reached "+s+" actionAt="+actionAt+" "+diagnostic);
            if(s.skill!=0&&!activated&&rendered>=6&&settled>=32){activated=true;action=mc.getSingleplayerServer().submit(()->{try{return activate(mc,s);}catch(Exception e){throw new RuntimeException(e);}});}
            if(s.label.equals("walk")&&rendered>=6&&!activated){activated=true;walkStart=mob.position();action=mc.getSingleplayerServer().submit(()->{fixture.setNoAi(CHECKLIST);fixture.setTarget(null);fixture.getNavigation().moveTo(6,-60,0,1);return mc.getSingleplayerServer().overworld().getGameTime();});}
        }catch(Throwable e){finish(mc,e);}
    }
    @SubscribeEvent public static void serverTick(TickEvent.ServerTickEvent ev){
        if(ENABLED&&HUMAN_PRESENCE&&!done&&ev.phase==TickEvent.Phase.END&&fixture!=null){
            // The real delayed death service may place a lootable corpse after the next
            // fixture begins. Remove only this test world's remains, never disable that service.
            var world=fixture.level();
            for(var item:world.getEntitiesOfClass(net.minecraft.world.entity.item.ItemEntity.class,fixture.getBoundingBox().inflate(12)))item.discard();
            for(int x=-4;x<=4;x++)for(int z=-4;z<=4;z++)for(int y=-60;y<=-55;y++){
                var pos=new BlockPos(x,y,z);var key=net.minecraftforge.registries.ForgeRegistries.BLOCKS.getKey(world.getBlockState(pos).getBlock());
                if(key!=null&&key.getNamespace().equals("dynasty")&&(key.getPath().contains("remains")||key.getPath().contains("statue")))world.removeBlock(pos,false);
            }
        }
        if(!ENABLED||done||ev.phase!=TickEvent.Phase.END||fixture==null||stage<0||!activated||captured)return;
        if(STAGES.get(stage).label.equals("walk")){fixture.move(MoverType.SELF,new net.minecraft.world.phys.Vec3(.065,0,0));fixture.setDeltaMovement(.065,0,0);fixture.hurtMarked=true;}
    }
    private static int prepare(Minecraft mc){
        var server=mc.getSingleplayerServer();var world=server.overworld();world.setDayTime(STAGES.get(stage).label.startsWith("night")?18000:6000);if(HUMAN_PRESENCE)try{BossPowerReferenceQa.suppressAmbientWorld(mc,world);}catch(Exception e){throw new RuntimeException(e);}
        if(fixture!=null)fixture.discard();if(victim!=null)victim.discard();
        var cleanup=new ArrayList<Entity>();for(var e:world.getAllEntities())if(e!=null&&!(e instanceof net.minecraft.server.level.ServerPlayer))cleanup.add(e);cleanup.forEach(Entity::discard);
        for(int x=-12;x<=12;x++)for(int z=-12;z<=12;z++)world.setBlockAndUpdate(new BlockPos(x,-61,z),((x+z)%7==0?Blocks.STONE_BRICKS:Blocks.GRASS_BLOCK).defaultBlockState());
        // Clear only this disposable fixture's air volume; no user save can enter this harness.
        if(HUMAN)for(int x=-12;x<=12;x++)for(int z=-12;z<=12;z++)for(int y=-60;y<=-51;y++)world.setBlockAndUpdate(new BlockPos(x,y,z),Blocks.AIR.defaultBlockState());
        Stage s=STAGES.get(stage);var type=net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("dynasty",s.id));
        if(type==null)throw new AssertionError("Unregistered "+s.id);
        fixture=(Mob)type.create(world);fixture.moveTo(0,-60,0,0,0);fixture.setNoAi(true);fixture.setNoGravity(true);fixture.setPersistenceRequired();if(CHECKLIST)fixture.setSilent(true);world.addFreshEntity(fixture);
        if(!PRESENCE&&!(fixture instanceof GeoEntity)){fixture.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(Items.STONE_SWORD));fixture.setItemSlot(EquipmentSlot.OFFHAND,new ItemStack(Items.SHIELD));}
        victim=EntityType.COW.create(world);victim.setNoAi(true);victim.setNoGravity(true);victim.setSilent(true);victim.moveTo(0,-60,PRESENCE?8:s.skill==342||s.skill==363?6:2,180,0);victim.getAttribute(Attributes.MAX_HEALTH).setBaseValue(10000);victim.setHealth(10000);victim.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.INVISIBILITY,12000,0,false,false,false));world.addFreshEntity(victim);
        for(var p:server.getPlayerList().getPlayers())p.teleportTo(world,HUMAN_PRESENCE?-2.65:PRESENCE?-4:0,-60,HUMAN_PRESENCE?0:PRESENCE?1:20,180,0);
        return fixture.getId();
    }
    private static long activate(Minecraft mc,Stage s)throws Exception{
        if(PRESENCE)victim.moveTo(0,-60,2,180,0);
        if(s.skill>0){boolean ok=(Boolean)fixture.getClass().getMethod("startSkill",int.class,LivingEntity.class).invoke(fixture,s.skill,victim);if(!ok)throw new AssertionError("Production skill rejected "+s);}
        else if(s.skill==-1){
            if(SPIRITS&&fixture instanceof com.dynasty.entity.DynastyBosses.RebelGeneral rebel)rebel.beginCharacterAttack();
            fixture.swing(InteractionHand.MAIN_HAND);
        }
        else if(!fixture.hurt(fixture.damageSources().generic(),s.skill==-3?1000000:8))throw new AssertionError("Damage rejected "+s);
        return mc.getSingleplayerServer().overworld().getGameTime();
    }
    private static void camera(Minecraft mc){
        Stage s=STAGES.get(stage);String view=s.label.replace("-off","").replace("-on","");
        if(HUMAN_PRESENCE){BossHumanAura.setReviewSuppressed(s.label.endsWith("-off"));mc.particleEngine.setLevel(mc.level);}
        if(Boolean.getBoolean("dynasty.tianjiangAuraEnvironments"))mc.options.particles().set(s.label.startsWith("minimal")?ParticleStatus.MINIMAL:s.label.startsWith("decreased")?ParticleStatus.DECREASED:ParticleStatus.ALL);
        double yaw=view.equals("45")?45:view.equals("side")?90:view.equals("back")?180:0;
        if(s.skill!=0||s.label.equals("walk"))yaw=35;
        double a=Math.toRadians(yaw),distance=s.id.equals("pilin_zhijinwu")?7.5:s.id.equals("juchui_jinjia_lishi")||s.id.equals("xianzhen_duantoujiang")?6.5:5.5;
        if(PRESENCE)distance=s.id.equals("pilin_zhijinwu")?11:10;
        if(CHECKLIST)distance=s.id.equals("dragon_emperor")?18:11;
        if(HUMAN)distance=HUMAN_PRESENCE?6:8.5;
        if(HUMAN&&s.label.startsWith("attack"))distance=HUMAN_PRESENCE?8:11;
        // Optional art-only camera match to existing reference captures.
        // Default fixture distances and production rendering stay unchanged.
        distance=Double.parseDouble(System.getProperty("dynasty.bossEightQa.cameraDistance",Double.toString(distance)));
        if(s.label.equals("far-on"))distance=12;
        var cam=new ArmorStand(mc.level,Math.sin(a)*distance,-60,Math.cos(a)*distance);
        cam.setPos(cam.getX(),-60+(HUMAN?1.62:PRESENCE?2.5:s.id.equals("pilin_zhijinwu")?1.9:1.5)-cam.getEyeHeight(),cam.getZ());cam.setNoGravity(true);cam.setYRot((float)(180-yaw));cam.setXRot(PRESENCE?3:5);cam.setYHeadRot(cam.getYRot());cam.yHeadRotO=cam.getYRot();cam.setOldPosAndRot();mc.options.setCameraType(CameraType.FIRST_PERSON);mc.setCameraEntity(cam);
        if(System.getProperty("dynasty.bossEightQa.cameraPitch")!=null){cam.setXRot(Float.parseFloat(System.getProperty("dynasty.bossEightQa.cameraPitch")));cam.setOldPosAndRot();}
    }
    @SuppressWarnings({"rawtypes","unchecked"})
    @SubscribeEvent public static void render(TickEvent.RenderTickEvent ev){
        if(ENABLED&&PRESENCE&&!HUMAN_PRESENCE&&ev.phase==TickEvent.Phase.START)Minecraft.getInstance().particleEngine.setLevel(Minecraft.getInstance().level);
        if(!ENABLED||done||captured||pending!=null||stage<0||ev.phase!=TickEvent.Phase.END)return;
        var mc=Minecraft.getInstance();if(mc.level==null||!(mc.level.getEntity(entityId) instanceof Mob mob))return;
        try{
            if(HUMAN_PRESENCE)BossPowerReferenceQa.clearScenicVisuals(mc);Object renderer=mc.getEntityRenderDispatcher().getRenderer(mob);GeoModel model;GeoAnimatable visual;
            if(renderer instanceof BossFormsRenderer.Core<?> r){model=r.getGeoModel();visual=r.getAnimatable();}
            else if(renderer instanceof BossCuboidRenderer<?> r){model=r.getGeoModel();visual=r.getAnimatable();}
            else if(renderer instanceof GeoEntityRenderer<?> r){model=r.getGeoModel();visual=(GeoEntity)mob;}
            else throw new AssertionError("Wrong renderer "+renderer);
            diagnostic="renderer="+renderer.getClass().getName()+" bones="+model.getAnimationProcessor().getRegisteredBones().size();
            if(model.getBone(PRESENCE?"root":"chest").isEmpty())return;rendered++;
            var manager=visual.getAnimatableInstanceCache().getManagerForId(mob.getId());var ctrl=manager.getAnimationControllers().get("body");
            if(ctrl==null||ctrl.getCurrentAnimation()==null)return;
            String clip=ctrl.getCurrentAnimation().animation().name();diagnostic+=" clip="+clip+" velocity="+mob.getDeltaMovement();Stage s=STAGES.get(stage);
            String expected=s.skill!=0?s.label.split("-")[0]:s.label.equals("walk")?"walk":"idle";
            if(mob instanceof GeoEntity)expected="animation."+s.id+"."+expected;
            long age=actionAt<0?-1:mc.level.getGameTime()-actionAt;
            // The first fixture needs chunk meshes ready, not merely entity replication.
            boolean ready=s.skill!=0?age>=s.age:s.label.equals("walk")?age>=10:settled>=(stage==START?160:HUMAN_PRESENCE?80:26)&&rendered>=8;
            if(!ready)return;
            if(!clip.equals(expected)){
                if(age<60)return;
                throw new AssertionError("Wrong pose "+s+" expected="+expected+" actual="+clip);
            }
            if(HUMAN&&s.label.equals("attack-contact")){
                // Packet age is not animation time: capture the actual forward strike,
                // never an idle-looking frame labelled "contact" merely because age==3.
                float extension=((software.bernie.geckolib.cache.object.GeoBone)model.getBone("right_arm").orElseThrow()).getRotX();
                if(extension<1.05f){if(age>14)throw new AssertionError("Human strike peak not observed "+s);return;}
            }
            if(s.skill==-3&&!mob.isDeadOrDying())throw new AssertionError("Death not replicated");
            if(s.skill>0&&(Integer)mob.getClass().getMethod("skillId").invoke(mob)!=s.skill)throw new AssertionError("Skill not replicated");
            if(s.label.equals("walk")&&walkStart!=null&&walkStart.distanceTo(mob.position())<.1)throw new AssertionError("No actual movement");
            var tex=model.getTextureResource(visual);String folder=s.id.equals("xianzhen_duantoujiang")||s.id.equals("qianji_bailian_yanshi")?"blueprint/cod2_voxel":mob instanceof GeoEntity?"blueprint/elite":"boss_cuboid";
            if(PRESENCE)folder=CHECKLIST?"boss_cuboid":"boss_forms";
            if(!tex.getPath().equals("textures/entity/"+folder+"/"+s.id+".png"))throw new AssertionError("Texture binding "+tex);
            try(var stream=mc.getResourceManager().open(tex);var image=com.mojang.blaze3d.platform.NativeImage.read(stream)){
                if(PRESENCE){
                    var geo=model.getModelResource(visual);
                    int expectedSize;
                    try(var gs=mc.getResourceManager().open(geo)){
                        expectedSize=com.google.gson.JsonParser.parseString(new String(gs.readAllBytes(),java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject().getAsJsonArray("minecraft:geometry").get(0).getAsJsonObject().getAsJsonObject("description").get("texture_width").getAsInt();
                    }
                    if(image.getWidth()!=expectedSize||image.getHeight()!=expectedSize)throw new AssertionError("Atlas size");
                } else {
                if(image.getWidth()!=16||image.getHeight()!=16)throw new AssertionError("Not 16px");Set<Integer> colors=new HashSet<>();
                for(int y=0;y<16;y++)for(int x=0;x<16;x++){int pixel=image.getPixelRGBA(x,y);colors.add(pixel);if((x==0||x==15||y==0||y==15)&&pixel!=-1)throw new AssertionError("White margin");if(pixel!=image.getPixelRGBA(x-x%2,y-y%2))throw new AssertionError("Sub2px island");}
                if(colors.size()!=4)throw new AssertionError("Palette count "+colors.size());
                }
            }
            var record=new LinkedHashMap<String,Object>();record.put("entity",s.id);record.put("stage",s.label);record.put("dimensions",Map.of("width",mob.getBbWidth(),"height",mob.getBbHeight()));record.put("equipment",Map.of("main",mob.getMainHandItem().toString(),"off",mob.getOffhandItem().toString()));record.put("clip",clip);record.put("age",age);record.put("renderer",renderer.getClass().getName());record.put("texture",tex.toString());record.put("scope","Actual registered entity, production startSkill/swing/hurt/death, controlled disposable world; not natural combat balance acceptance");
            if(PRESENCE){
                var expectedHashes=com.google.gson.JsonParser.parseString(Files.readString(OUT.resolve("runtime-manifest.json"))).getAsJsonObject().getAsJsonObject("resources");
                Map<String,String> loadedHashes=new LinkedHashMap<>();
                var resources=new ArrayList<Object>(List.of(tex,model.getModelResource(visual),model.getAnimationResource(visual)));
                if(HUMAN_PRESENCE&&s.id.equals("nine_heaven_general")){resources.add(TianjiangAura.GLOW);resources.add(TianjiangAura.STREAM);}
                for(Object resource:resources){
                    var location=(ResourceLocation)resource;
                    try(var stream=mc.getResourceManager().open(location)){
                        String hash=HexFormat.of().formatHex(java.security.MessageDigest.getInstance("SHA-256").digest(stream.readAllBytes()));
                        String path="assets/"+location.getNamespace()+"/"+location.getPath();
                        if(!hash.equals(expectedHashes.get(path).getAsString()))throw new AssertionError("Stale resource "+location);
                        loadedHashes.put(path,hash);
                    }
                }
                record.put("loadedResourceSha256",loadedHashes);record.put("particles",HUMAN_PRESENCE?(s.label.endsWith("-off")?"independent aura and particles disabled":"production aura and particles enabled"):"cleared in QA only before frame");
                if(HUMAN_PRESENCE&&s.id.equals("nine_heaven_general")){
                    float glow=TianjiangAura.glowAlpha(mob,mc.getFrameTime(),false);
                    record.put("environment",Map.of("time",mc.level.getDayTime(),"particleSetting",mc.options.particles().get().name(),"distance",s.label.equals("far-on")?12:Double.parseDouble(System.getProperty("dynasty.bossEightQa.cameraDistance","8"))));
                    record.put("materialGlowAlpha",glow);record.put("replicatedSwing",mob.getAttackAnim(mc.getFrameTime()));
                    if((s.label.endsWith("-off")||s.skill==-3)&&glow!=0)throw new AssertionError("Aura failed to stop");
                    if(glow<0||glow>1)throw new AssertionError("Glow out of range");
                }
                if(HUMAN_PRESENCE){record.put("auraParticleEmissionRequests",BossHumanAura.reviewEmissions());
                    int obstructions=0;for(int x=-3;x<=3;x++)for(int z=-3;z<=3;z++)for(int y=-60;y<=-56;y++)if(!mc.level.getBlockState(new BlockPos(x,y,z)).isAir())obstructions++;
                    record.put("fixtureAirObstructions",obstructions);if(obstructions!=0){if(settled>240)throw new AssertionError("Fixture obstruction "+s+" count="+obstructions);return;}
                    if(s.label.startsWith("minimal")&&BossHumanAura.reviewEmissions()!=0)throw new AssertionError("Minimal still emits particles");if(s.label.endsWith("-on")&&!s.label.startsWith("minimal")&&BossHumanAura.reviewEmissions()<10)throw new AssertionError("No production aura emissions "+s);if(s.label.endsWith("-off")&&BossHumanAura.reviewEmissions()!=0)throw new AssertionError("Particles not disabled "+s);}
            }
            Map<String,Object> bones=new LinkedHashMap<>();for(Object o:model.getAnimationProcessor().getRegisteredBones()){var b=(software.bernie.geckolib.cache.object.GeoBone)o;bones.put(b.getName(),Map.of("rotation",List.of(b.getRotX(),b.getRotY(),b.getRotZ()),"position",List.of(b.getPosX(),b.getPosY(),b.getPosZ())));}record.put("bones",bones);
            if(Boolean.getBoolean("dynasty.tianjiangAuraSequence")&&s.id.equals("nine_heaven_general")&&s.label.equals("45-on")&&auraFrames<24){
                if(lastAuraTick<0||mob.tickCount-lastAuraTick>=4){
                    lastAuraTick=mob.tickCount;var dir=OUT.resolve("sequence");Files.createDirectories(dir);
                    try(var shot=Screenshot.takeScreenshot(mc.getMainRenderTarget())){shot.writeToFile(dir.resolve(String.format("%02d.png",auraFrames++)));}
                }
                if(auraFrames<24)return;
            }
            Files.writeString(OUT.resolve(String.format("%02d-state.json",stage)),new GsonBuilder().setPrettyPrinting().create().toJson(record));
            try(var shot=Screenshot.takeScreenshot(mc.getMainRenderTarget())){shot.writeToFile(OUT.resolve(String.format("%02d-%s-%s.png",stage,s.id,s.label)));}
            LOG.add(s.id+" "+s.label+" "+clip+" age="+age);Files.writeString(OUT.resolve("progress.txt"),String.join("\n",LOG));captured=true;
        }catch(Throwable e){finish(mc,e);}
    }
    private static void finish(Minecraft mc,Throwable error){
        if(done)return;done=true;try{Files.createDirectories(OUT);Files.writeString(OUT.resolve(error==null?"PASS.txt":"FAIL.txt"),String.join("\n",LOG)+"\n"+(error==null?"PASS: "+(STAGES.size()-START)+" native art stages for selected existing bosses; no animation triggers. Natural encounter/multiplayer acceptance is separate.\n":"FAIL: "+error+"\n"));}catch(Exception e){e.printStackTrace();}if(error!=null){error.printStackTrace();try(var shot=Screenshot.takeScreenshot(mc.getMainRenderTarget())){shot.writeToFile(OUT.resolve("failure-frame.png"));}catch(Exception ignored){}}mc.stop();
    }
}
