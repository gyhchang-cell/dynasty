package com.dynasty.ecologyqa;

import com.google.gson.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.EntityLeaveLevelEvent;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.registries.ForgeRegistries;
import java.nio.file.*;
import java.util.*;

/** Private bounded fixture actions. Never creates actors/items, calls spawn predicates or changes time/caps. */
public final class NativeSceneDriver {
    public static final boolean ENABLED=Boolean.getBoolean("ecology.nativeqa.driveScenes");
    static final UUID PLAYER=UUID.fromString("817f74c6-1403-3509-b336-db7c734bf8f6");
    static final String[] SCENES={"post_house","battlefield","forest","cold_ocean"};
    // Known existing QA terrain anchors; observer flight is an explicit pre-existing saved-player fixture.
    static final double[][] ANCHORS={{728,118,-664},{-2696,63,-1360},{-88,103,-104},{488,50,488}};
    static final Set<String> JUNK=Set.of("minecraft:prismarine_crystals","minecraft:porkchop","minecraft:phantom_membrane","minecraft:ender_pearl","minecraft:leather","minecraft:prismarine_shard","minecraft:bone","minecraft:gunpowder","minecraft:arrow","minecraft:rotten_flesh","minecraft:string","minecraft:spider_eye","minecraft:feather","minecraft:kelp","dynasty:copper_coin","dynasty:silver_coin");
    static final Set<UUID> pendingNatural=new HashSet<>(),freshNatural=new HashSet<>(),skipTargets=new HashSet<>(),selectedCullTargets=new HashSet<>();
    record DeathCandidate(Mob mob,DamageSource source,int tick,long epoch){}
    record JoinCandidate(Entity entity,ServerLevel level,long gameTime){}
    static final Map<UUID,DeathCandidate> pendingCullDeaths=new HashMap<>();
    static final Map<UUID,JoinCandidate> pendingWorldJoins=new HashMap<>();
    static long targetEpoch;
    static volatile UUID attackTarget;
    static volatile boolean clearInventory=true;
    static int ticks,stage=-1,stageStart,preparationStart,confirmedCullDeaths,targetStart,lootStart;
    static boolean initialized,inventoryConfirmed,actualClosedSeen,qaFlightRestored;
    static volatile boolean clientFlightAcknowledged;
    static boolean creatureSampling=true,oilWindowVisited,oilAcquired;
    static final Set<Long> overworldGateScopes=new HashSet<>();
    static int oilCountBefore,oilPickedAmount,pickupConfirmStarted=-1;
    static UUID pickedOilUuid;
    static volatile boolean finished;
    static long gateOffset,latestCategoryTick=-1;
    static boolean latestCategoryWindowOpen;
    static long actualOpenGameTime=-1;
    static UUID oil;
    static String phase="initial";
    static void log(String kind,Object... pairs)throws Exception {
        var row=new LinkedHashMap<String,Object>();row.put("kind",kind);row.put("driver_tick",ticks);row.put("phase",phase);row.put("stage",stage);
        if(EcologyNativeQa.server!=null)row.put("game_time",EcologyNativeQa.server.overworld().getGameTime());
        for(int i=0;i<pairs.length;i+=2)row.put(pairs[i].toString(),pairs[i+1]);
        Files.writeString(EcologyNativeQa.output.resolve("native-driver.jsonl"),new Gson().toJson(row)+"\n",StandardOpenOption.CREATE,StandardOpenOption.APPEND);
    }
    static void stop(String reason)throws Exception {
        if(finished)return;finished=true;attackTarget=null;clearInventory=false;
        log("bounded_driver_stop","reason",reason,"natural_birth_or_pickup_not_inferred",true);
        try{Files.writeString(EcologyNativeQa.output.resolve("external-stop-request.txt"),reason+"\n",StandardOpenOption.CREATE_NEW);}catch(FileAlreadyExistsException ignored){}
    }
    static int empty(ServerPlayer p){return (int)p.getInventory().items.stream().filter(net.minecraft.world.item.ItemStack::isEmpty).count();}
    static int oilCount(ServerPlayer p){return p.getInventory().items.stream().filter(st->"dynasty:lantern_oil".equals(String.valueOf(ForgeRegistries.ITEMS.getKey(st.getItem())))).mapToInt(net.minecraft.world.item.ItemStack::getCount).sum();}
    static boolean countedAnimal(Entity e){
        if(!(e instanceof Animal m))return false;
        String type=String.valueOf(ForgeRegistries.ENTITY_TYPES.getKey(m.getType()));
        return Set.of("minecraft:cow","minecraft:pig","minecraft:chicken","minecraft:sheep").contains(type)
            &&m.getClassification(true)==MobCategory.CREATURE&&!m.isPersistenceRequired()&&!m.requiresCustomPersistence()
            &&!m.hasCustomName()&&!m.isBaby()&&m.getAge()==0&&!m.isInLove()&&m.getLoveCause()==null&&!m.isLeashed()&&!m.isPassenger()&&!m.isVehicle()
            &&!(m instanceof OwnableEntity owner&&owner.getOwnerUUID()!=null)&&m.getPersistentData().isEmpty();
    }
    static boolean safeNativeStrike(ServerPlayer p,Entity target){
        if(target==null||!target.isAlive()||p.serverLevel()!=EcologyNativeQa.server.overworld()||p.onGround()||!p.getAbilities().flying||!p.getAbilities().mayfly||p.isPassenger()||p.isSpectator()||target.distanceToSqr(p)>=16)return false;
        if(!"dynasty:yuchang_dagger".equals(String.valueOf(ForgeRegistries.ITEMS.getKey(p.getMainHandItem().getItem()))))return false;
        if(phase.equals("cull_counted_creature")&&!countedAnimal(target))return false;
        if(!phase.equals("cull_counted_creature")&&(!freshNatural.contains(target.getUUID())||!"dynasty:lantern_ghost".equals(String.valueOf(ForgeRegistries.ENTITY_TYPES.getKey(target.getType())))))return false;
        return p.serverLevel().getEntitiesOfClass(LivingEntity.class,target.getBoundingBox().inflate(3),n->n!=p&&n!=target&&!countedAnimal(n)).isEmpty();
    }
    @SubscribeEvent(priority=EventPriority.HIGHEST) public static void guardNativeAttack(AttackEntityEvent e)throws Exception {
        if(!ENABLED||!(e.getEntity() instanceof ServerPlayer p)||!p.getUUID().equals(PLAYER))return;
        boolean safe=!finished&&!EcologyNativeQa.stopRequested&&e.getTarget().getUUID().equals(attackTarget)&&safeNativeStrike(p,e.getTarget());
        log("actual_native_attack_guard","target",e.getTarget().getUUID().toString(),"allowed",safe,"server_on_ground",p.onGround(),"server_flying",p.getAbilities().flying,"held_item",String.valueOf(ForgeRegistries.ITEMS.getKey(p.getMainHandItem().getItem())),"unsafe_fixture_input_canceled",!safe);
        if(!safe)e.setCanceled(true); // Private fixture input boundary; allowed native damage/AI is unchanged.
    }
    static void teleport(ServerPlayer p,double x,double y,double z,String reason)throws Exception {
        if(p.serverLevel()!=EcologyNativeQa.server.overworld())throw new IllegalStateException("Only Overworld fixture scenes permitted");
        p.teleportTo(EcologyNativeQa.server.overworld(),x,y,z,p.getYRot(),p.getXRot());
        log("private_observer_teleport","reason",reason,"player",p.getUUID().toString(),"position",p.position().toString(),"dimension",p.level().dimension().location().toString(),"fixture_not_survival_travel",true);
    }
    static void scene(ServerPlayer p,int next)throws Exception {
        attackTarget=null;stage=next;stageStart=ticks;phase="observe";
        latestCategoryTick=-1;latestCategoryWindowOpen=false;
        if(stage>=SCENES.length){stop("FOUR_BOUNDED_WINDOWS_ENDED_REVIEW_RAW_NATIVE_EVIDENCE");return;}
        if(stage==1)oilWindowVisited=true;
        double[] a=ANCHORS[stage];teleport(p,a[0]+40.5,a[1]+60,a[2]+.5,"scene_"+SCENES[stage]);
        log("scene_window_started","scene",SCENES[stage],"anchor",a,"window_ticks",800,"actual_night",p.serverLevel().isNight(),"day_time",p.serverLevel().getDayTime(),"target_chunks_not_preclaimed_loaded",true);
    }
    static void creaturePendingAndOil(ServerPlayer p,String reason)throws Exception {
        creatureSampling=false;attackTarget=null;
        log("creature_sampling_stays_pending","reason",reason,"monster_oil_denominator_independent",true);
        if(stage==1)return;
        if(!oilWindowVisited)scene(p,1);else stop("CREATURE_GATE_CLOSED_AND_OIL_WINDOW_ALREADY_VISITED");
    }
    // Read only actual hook rows as a preparation hint. The separate audit rejects anomalous scopes;
    // this hint is never an accepted attempt/birth count and never invokes native predicates.
    static void gateHints()throws Exception {
        Path file=Path.of(EcologyNativeQa.required("ecology.nativegate.output")).resolve("native-gates.jsonl");
        if(!Files.exists(file))return;
        try(var input=new java.io.RandomAccessFile(file.toFile(),"r")){
          input.seek(gateOffset);
          String line;
          while((line=input.readLine())!=null){
            gateOffset=input.getFilePointer();
            var r=JsonParser.parseString(line).getAsJsonObject();
            String kind=r.get("kind").getAsString();
            if(kind.equals("native_persistent_chunk_opportunity")){
                if("minecraft:overworld".equals(r.get("dimension").getAsString())&&r.get("native_spawn_friendlies").getAsBoolean()&&r.get("native_persistent_phase").getAsBoolean())overworldGateScopes.add(r.get("scope_id").getAsLong());
                continue;
            }
            if(kind.equals("native_chunk_loop_return")){overworldGateScopes.remove(r.get("scope_id").getAsLong());continue;}
            if(!kind.equals("actual_native_creature_category_return")||!overworldGateScopes.contains(r.get("scope_id").getAsLong()))continue;
            long when=r.get("overworld_game_time").getAsLong();
            if(when>latestCategoryTick){latestCategoryTick=when;latestCategoryWindowOpen=false;}
            if(r.get("actual_category_return").getAsBoolean()){
                actualOpenGameTime=Math.max(actualOpenGameTime,when);
                if(when==latestCategoryTick)latestCategoryWindowOpen=true;
            }else actualClosedSeen=true;
          }
        }
    }
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void tick(TickEvent.ServerTickEvent e)throws Exception {
        if(!ENABLED||finished||EcologyNativeQa.stopRequested||EcologyNativeQa.server==null||e.phase!=TickEvent.Phase.END)return;
        ticks++;var server=EcologyNativeQa.server;var p=server.getPlayerList().getPlayer(PLAYER);
        for(var it=pendingWorldJoins.entrySet().iterator();it.hasNext();){
            var entry=it.next();var j=entry.getValue();if(j.level().getGameTime()<=j.gameTime())continue;
            boolean present=j.level().getEntity(entry.getKey())==j.entity()&&!j.entity().isRemoved();
            if(present)freshNatural.add(entry.getKey());
            log("post_join_native_world_presence","uuid",entry.getKey().toString(),"species",String.valueOf(ForgeRegistries.ENTITY_TYPES.getKey(j.entity().getType())),"actual_entity_present_after_later_world_tick",present,"observed_join_game_time",j.gameTime(),"presence_game_time",j.level().getGameTime(),"dimension",j.level().dimension().location().toString());it.remove();
        }
        for(var it=pendingCullDeaths.entrySet().iterator();it.hasNext();){
            var entry=it.next();var d=entry.getValue();
            if(d.mob().getHealth()>0||ticks-d.tick()>40||d.mob().getLastDamageSource()!=d.source()){
                log("death_candidate_invalidated","uuid",entry.getKey().toString(),"reason","revived_expired_or_source_changed");it.remove();
            }
        }
        if(p==null){if(ticks>=100)stop("EXPECTED_SAVED_REAL_PLAYER_NOT_CONNECTED");return;}
        if(p.serverLevel()!=server.overworld()){stop("WRONG_DIMENSION_NO_SCENES_OR_ATTACKS");return;}
        if(pickupConfirmStarted>=0){
            int count=oilCount(p);boolean increased=count>=oilCountBefore+oilPickedAmount;
            if(increased){log("same_uuid_pickup_server_inventory_delta_confirmed","uuid",pickedOilUuid.toString(),"before",oilCountBefore,"after",count,"actual_event_count",oilPickedAmount,"saved_persistence_not_yet_verified",true);pickupConfirmStarted=-1;}
            else if(ticks-pickupConfirmStarted>=5){stop("PICKUP_EVENT_WITHOUT_SERVER_OIL_COUNT_DELTA");return;}
        }
        if(!initialized){
            initialized=true;preparationStart=ticks;
            // Explicit PRIVATE fixture intervention: vanilla survival login resets saved flight.
            // Default off; never a production grant or proof of ordinary survival acquisition.
            if(Boolean.getBoolean("ecology.nativeqa.restoreSavedQaFlight")){
                if(p.gameMode.getGameModeForPlayer()!=net.minecraft.world.level.GameType.SURVIVAL||!p.getUUID().equals(PLAYER)||!server.getWorldPath(net.minecraft.world.level.storage.LevelResource.ROOT).toRealPath().equals(EcologyNativeQa.expectedWorld))throw new IllegalStateException("Private survival-flight fixture identity mismatch");
                boolean beforeMayfly=p.getAbilities().mayfly,beforeFlying=p.getAbilities().flying;
                p.getAbilities().mayfly=true;p.getAbilities().flying=true;p.onUpdateAbilities();qaFlightRestored=true;
                log("explicit_private_qa_flight_restoration","player",p.getUUID().toString(),"before_mayfly",beforeMayfly,"before_flying",beforeFlying,"after_mayfly",true,"after_flying",true,"observed_health",p.getHealth(),"observed_invulnerable",p.getAbilities().invulnerable,"ordinary_survival_acquisition_credit",false);
            }
            if(p.isSpectator()||!p.getAbilities().mayfly||!p.getAbilities().flying){stop("PRESERVED_FLIGHT_FIXTURE_NOT_PRESENT_NO_ABILITIES_GRANTED");return;}
            if(!"dynasty:yuchang_dagger".equals(String.valueOf(ForgeRegistries.ITEMS.getKey(p.getInventory().getItem(8).getItem())))){stop("SAVED_DAGGER_NOT_PRESENT_NO_WEAPON_GRANTED");return;}
            log("preserved_fixture","player",p.getUUID().toString(),"mayfly",p.getAbilities().mayfly,"flying",p.getAbilities().flying,"invulnerable",p.getAbilities().invulnerable,"health",p.getHealth(),"game_mode",p.gameMode.getGameModeForPlayer().getName(),"inventory_empty",empty(p),"qa_flight_restored",qaFlightRestored,"no_grants",!qaFlightRestored);
        }
        if(qaFlightRestored&&!clientFlightAcknowledged){
            if(ticks-preparationStart>=100)stop("RESTORED_FLIGHT_NO_NATIVE_CLIENT_READBACK");
            return;
        }
        if(ticks%20==0){
            gateHints();int n=empty(p);clearInventory=n<8;
            log("server_inventory_and_cap_readback","empty_main_slots",n,"capacity_for_one_oil_stack",n>=8,"actual_category_hint_only",true,"latest_actual_open_game_time",actualOpenGameTime,"actual_closed_seen",actualClosedSeen);
            if(n>=8&&!inventoryConfirmed){inventoryConfirmed=true;log("server_inventory_preparation_confirmed","empty_main_slots",n);}
        }
        if(oil!=null){
            attackTarget=null;phase="same_uuid_pickup";
            Entity entity=p.serverLevel().getEntity(oil);
            if(ticks-lootStart>=200||stage>=0&&ticks-stageStart>=800){stop("SAME_UUID_OIL_NOT_PICKED_WITHIN_PICKUP_OR_SCENE_BOUND");return;}
            if(entity instanceof ItemEntity item&&item.isAlive()&&ticks%5==0){
                log("same_uuid_pickup_window","uuid",oil.toString(),"position",item.position().toString(),"age",item.getAge(),"empty_main_slots",empty(p),"stack",item.getItem().save(new CompoundTag()).toString());
                if(empty(p)>=8)teleport(p,item.getX(),item.getY(),item.getZ(),"same_original_natural_oil_UUID_pickup");
            }
            return;
        }
        if(phase.equals("initial")){
            if(ticks-preparationStart<200)return;
            if(!inventoryConfirmed||empty(p)<8){stop("INVENTORY_CAPACITY_NOT_CONFIRMED_IN_INITIAL_200_TICKS");return;}
            if(latestCategoryWindowOpen){scene(p,0);return;}
            if(!actualClosedSeen){creaturePendingAndOil(p,"NO_ACTUAL_NATIVE_CREATURE_GATE_OBSERVED_IN_INITIAL_BOUND");return;}
            phase="cull_counted_creature";preparationStart=ticks;
            log("counted_creature_preparation_started","max_deaths",64,"max_ticks",1200,"monster_clear_forbidden",true);
        }
        if(phase.equals("cull_counted_creature")){
            if(latestCategoryWindowOpen){scene(p,0);return;}
            if(ticks-preparationStart>=1200||confirmedCullDeaths>=64){creaturePendingAndOil(p,"NATIVE_CREATURE_GATE_STILL_CLOSED_AFTER_CULL_BOUND");return;}
            if(ticks%20!=0)return;
            if(attackTarget!=null){
                Entity target=p.serverLevel().getEntity(attackTarget);
                if(target!=null&&target.isAlive()&&ticks-targetStart<80)return;
                skipTargets.add(attackTarget);attackTarget=null;
            }
            if(selectedCullTargets.size()>=64){creaturePendingAndOil(p,"64_DISTINCT_CULL_RESERVATIONS_USED_NO_MORE_TARGETS");return;}
            var candidates=new ArrayList<Animal>();
            for(Entity candidate:p.serverLevel().getAllEntities())if(candidate.isAlive()&&countedAnimal(candidate)&&!skipTargets.contains(candidate.getUUID())&&!selectedCullTargets.contains(candidate.getUUID())&&candidate.distanceToSqr(p)<128*128&&p.serverLevel().getChunkSource().getChunkNow(candidate.blockPosition().getX()>>4,candidate.blockPosition().getZ()>>4)!=null)candidates.add((Animal)candidate);
            candidates.sort(Comparator.comparingDouble(m->m.distanceToSqr(p)));
            if(candidates.isEmpty()){creaturePendingAndOil(p,"NO_LOADED_COUNTED_CREATURE_ANIMAL_FOR_NATIVE_PREPARATION");return;}
            Animal target=candidates.get(0);attackTarget=target.getUUID();targetStart=ticks;selectedCullTargets.add(attackTarget);targetEpoch++;
            log("counted_creature_target","uuid",attackTarget.toString(),"species",ForgeRegistries.ENTITY_TYPES.getKey(target.getType()).toString(),"native_classification",target.getClassification(true).getName(),"persistent",target.isPersistenceRequired(),"custom_persistent",target.requiresCustomPersistence(),"scene_or_birth_credit",false);
            teleport(p,target.getX()+1.5,target.getY()+1,target.getZ(),"real_native_client_attack_counted_vanilla_animal");return;
        }
        if(phase.equals("observe")){
            if(ticks-stageStart>=800){
                log("scene_window_ended","scene",SCENES[stage],"elapsed_ticks",ticks-stageStart,"births_must_be_verified_from_native_observers",true);
                if(!creatureSampling){stop("BOUNDED_OIL_ONLY_WINDOW_DONE_CREATURE_SAMPLING_PENDING");return;}
                scene(p,stage+1);return;
            }
            if(creatureSampling&&ticks%20==0&&latestCategoryTick>=0&&!latestCategoryWindowOpen&&p.serverLevel().getGameTime()-latestCategoryTick<=400){
                creaturePendingAndOil(p,"ALL_OBSERVED_NATIVE_CATEGORY_RETURNS_CLOSED_IN_LATEST_PERIOD_NO_EXTENSION");return;
            }
            if(stage==1&&!oilAcquired&&attackTarget==null&&ticks%20==0&&empty(p)>=8){
                for(UUID id:freshNatural){Entity mob=p.serverLevel().getEntity(id);if(mob instanceof Mob m&&m.isAlive()&&!skipTargets.contains(id)&&"dynasty:lantern_ghost".equals(String.valueOf(ForgeRegistries.ENTITY_TYPES.getKey(m.getType())))&&m.distanceToSqr(p)<128*128){attackTarget=id;targetStart=ticks;teleport(p,m.getX()+1.5,m.getY()+1,m.getZ(),"fresh_native_lantern_real_client_attack");break;}}
            }
            if(attackTarget!=null&&ticks-targetStart>100){skipTargets.add(attackTarget);attackTarget=null;}
        }
    }
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void finalized(MobSpawnEvent.FinalizeSpawn e){
        if(!ENABLED||e.getSpawnType()!=MobSpawnType.NATURAL)return;
        if(Arrays.stream(Thread.currentThread().getStackTrace()).anyMatch(s->s.getClassName().equals("net.minecraft.world.level.NaturalSpawner")))pendingNatural.add(e.getEntity().getUUID());
    }
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void joined(EntityJoinLevelEvent e)throws Exception {
        if(!ENABLED||e.getLevel().isClientSide()||e.isCanceled()||e.loadedFromDisk()||!pendingNatural.remove(e.getEntity().getUUID()))return;
        if(!(e.getLevel() instanceof ServerLevel level)||EcologyNativeQa.server==null||level!=EcologyNativeQa.server.overworld())return;
        Entity entity=e.getEntity();var pos=entity.blockPosition();var box=entity.getBoundingBox();
        int margin="dynasty:snail_maiden".equals(String.valueOf(ForgeRegistries.ENTITY_TYPES.getKey(entity.getType())))?4:1;
        boolean full=true;
        for(int cx=Math.floorDiv((int)Math.floor(box.minX)-margin,16);cx<=Math.floorDiv((int)Math.floor(box.maxX)+margin,16);cx++)
            for(int cz=Math.floorDiv((int)Math.floor(box.minZ)-margin,16);cz<=Math.floorDiv((int)Math.floor(box.maxZ)+margin,16);cz++)full&=level.getChunkSource().getChunkNow(cx,cz)!=null;
        boolean center=level.getChunkSource().getChunkNow(pos.getX()>>4,pos.getZ()>>4)!=null;
        pendingWorldJoins.put(entity.getUUID(),new JoinCandidate(entity,level,level.getGameTime()));
        log("driver_fresh_native_join_candidate","uuid",entity.getUUID().toString(),"species",String.valueOf(ForgeRegistries.ENTITY_TYPES.getKey(entity.getType())),"position",entity.position().toString(),"dimension",level.dimension().location().toString(),"biome",center?level.getBiome(pos).unwrapKey().map(k->k.location().toString()).orElse("unkeyed"):"CENTER_NOT_FULL", "support",center?level.getBlockState(pos.below()).toString():"NOT_READ_UNLOADED","fluid",center?level.getFluidState(pos).toString():"NOT_READ_UNLOADED","body_margin",margin,"entire_body_margin_full_chunks",full,"nearest_player_distance_squared",level.players().stream().filter(pl->!pl.isSpectator()).mapToDouble(pl->pl.distanceToSqr(entity)).min().orElse(-1),"shared_spawn_distance_squared",pos.distSqr(level.getSharedSpawnPos()),"day_time",level.getDayTime(),"night",level.isNight(),"loaded_from_disk",false,"post_join_world_presence_still_required",true);
    }
    @SubscribeEvent public static void died(LivingDeathEvent e)throws Exception {
        if(!ENABLED)return;
        pendingCullDeaths.remove(e.getEntity().getUUID()); // Any later death invalidates an older canceled attempt.
        if(!e.getEntity().getUUID().equals(attackTarget))return;
        boolean player=e.getSource().getEntity() instanceof ServerPlayer p&&p.getUUID().equals(PLAYER);
        if(phase.equals("cull_counted_creature")&&player&&countedAnimal(e.getEntity()))pendingCullDeaths.put(e.getEntity().getUUID(),new DeathCandidate((Mob)e.getEntity(),e.getSource(),ticks,targetEpoch));
        log("target_death_event_candidate","uuid",attackTarget.toString(),"actual_saved_player_source",player,"confirmed_cull_deaths",confirmedCullDeaths);attackTarget=null;
    }
    @SubscribeEvent public static void left(EntityLeaveLevelEvent e)throws Exception {
        if(!ENABLED||e.getLevel().isClientSide())return;
        var candidate=pendingCullDeaths.remove(e.getEntity().getUUID());if(candidate==null)return;
        boolean killed=e.getEntity()==candidate.mob()&&e.getEntity().getRemovalReason()==Entity.RemovalReason.KILLED&&candidate.mob().getHealth()<=0&&candidate.mob().deathTime>=20&&candidate.mob().getLastDamageSource()==candidate.source()&&ticks-candidate.tick()<=40;
        if(killed)confirmedCullDeaths++;
        log("counted_creature_actual_removal","uuid",e.getEntity().getUUID().toString(),"removal_reason",String.valueOf(e.getEntity().getRemovalReason()),"confirmed_cull_deaths",confirmedCullDeaths,"killed_after_saved_player_death_source",killed,"candidate_epoch",candidate.epoch(),"death_animation_ticks",candidate.mob().deathTime);
    }
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void drops(LivingDropsEvent e)throws Exception {
        if(!ENABLED||finished||stage<0||!phase.equals("observe")||e.isCanceled()||oil!=null||!freshNatural.contains(e.getEntity().getUUID())||!(e.getSource().getEntity() instanceof ServerPlayer p)||!p.getUUID().equals(PLAYER))return;
        for(ItemEntity item:e.getDrops())if("dynasty:lantern_oil".equals(String.valueOf(ForgeRegistries.ITEMS.getKey(item.getItem().getItem())))){
            oil=item.getUUID();lootStart=ticks;attackTarget=null;oilCountBefore=oilCount(p);
            log("fresh_natural_player_oil_drop","source_mob",e.getEntity().getUUID().toString(),"source_player",p.getUUID().toString(),"original_item_uuid",oil.toString(),"stack",item.getItem().save(new CompoundTag()).toString());break;
        }
    }
    @SubscribeEvent public static void picked(PlayerEvent.ItemPickupEvent e)throws Exception {
        if(!ENABLED||finished||oil==null||!oil.equals(e.getOriginalEntity().getUUID())||!e.getEntity().getUUID().equals(PLAYER))return;
        if(e.getStack().isEmpty()||!"dynasty:lantern_oil".equals(String.valueOf(ForgeRegistries.ITEMS.getKey(e.getStack().getItem())))){stop("ORIGINAL_UUID_PICKUP_HAS_DIFFERENT_OR_EMPTY_STACK");return;}
        pickedOilUuid=oil;oilPickedAmount=e.getStack().getCount();pickupConfirmStarted=ticks;oilAcquired=true;
        log("exact_original_oil_pickup_event","uuid",oil.toString(),"player",e.getEntity().getUUID().toString(),"stack",e.getStack().save(new CompoundTag()).toString());
        oil=null;phase="observe"; // Preserve the original scene deadline; pickup never extends it.
    }
    public static final class ClientActions {
        static int age;
        @SubscribeEvent public static void tick(TickEvent.ClientTickEvent e)throws Exception {
            if(!ENABLED||finished||EcologyNativeQa.stopRequested||e.phase!=TickEvent.Phase.END)return;
            var mc=net.minecraft.client.Minecraft.getInstance();if(mc.player==null||mc.level==null||mc.gameMode==null||!mc.player.getUUID().equals(PLAYER))return;
            age++;
            if(Boolean.getBoolean("ecology.nativeqa.restoreSavedQaFlight")&&!clientFlightAcknowledged){
                if(mc.level.dimension()!=net.minecraft.world.level.Level.OVERWORLD||!mc.player.getAbilities().mayfly||!mc.player.getAbilities().flying)return;
                Files.writeString(EcologyNativeQa.output.resolve("native-client-inputs.jsonl"),new Gson().toJson(Map.of("kind","actual_native_client_flight_readback","player",mc.player.getUUID().toString(),"dimension",mc.level.dimension().location().toString(),"client_game_time",mc.level.getGameTime(),"mayfly",mc.player.getAbilities().mayfly,"flying",mc.player.getAbilities().flying,"client_fields_written",false))+"\n",StandardOpenOption.CREATE,StandardOpenOption.APPEND);
                clientFlightAcknowledged=true;
            }
            if(clearInventory&&age%5==0&&mc.player.containerMenu==mc.player.inventoryMenu){
                for(int slot=9;slot<=44;slot++){
                    var stack=mc.player.inventoryMenu.getSlot(slot).getItem();
                    if(!JUNK.contains(String.valueOf(ForgeRegistries.ITEMS.getKey(stack.getItem()))))continue;
                    Files.writeString(EcologyNativeQa.output.resolve("native-client-inputs.jsonl"),new Gson().toJson(Map.of("kind","native_inventory_throw","client_game_time",mc.level.getGameTime(),"slot",slot,"item",String.valueOf(ForgeRegistries.ITEMS.getKey(stack.getItem())),"count",stack.getCount(),"server_capacity_ack_separate",true))+"\n",StandardOpenOption.CREATE,StandardOpenOption.APPEND);
                    mc.gameMode.handleInventoryMouseClick(mc.player.inventoryMenu.containerId,slot,1,net.minecraft.world.inventory.ClickType.THROW,mc.player);break;
                }
            }
            UUID target=attackTarget;if(target==null||age%14!=0||mc.player.onGround()||!mc.player.getAbilities().flying||!mc.player.getAbilities().mayfly)return;
            for(Entity entity:mc.level.entitiesForRendering())if(entity.getUUID().equals(target)&&entity.isAlive()&&entity.distanceToSqr(mc.player)<16){
                mc.player.getInventory().selected=8; // Saved dagger; per-strike airborne server guard prevents vanilla sweep. No item grant.
                var delta=entity.getEyePosition().subtract(mc.player.getEyePosition());mc.player.setYRot((float)(Math.atan2(delta.z,delta.x)*180/Math.PI)-90);mc.player.setXRot((float)(-Math.atan2(delta.y,Math.sqrt(delta.x*delta.x+delta.z*delta.z))*180/Math.PI));
                Files.writeString(EcologyNativeQa.output.resolve("native-client-inputs.jsonl"),new Gson().toJson(Map.of("kind","native_client_attack","client_game_time",mc.level.getGameTime(),"target",target.toString(),"distance_squared",entity.distanceToSqr(mc.player),"selected_slot",8,"damage_and_death_ack_separate",true))+"\n",StandardOpenOption.CREATE,StandardOpenOption.APPEND);
                mc.gameMode.attack(mc.player,entity);mc.player.swing(net.minecraft.world.InteractionHand.MAIN_HAND);break;
            }
        }
    }
}
