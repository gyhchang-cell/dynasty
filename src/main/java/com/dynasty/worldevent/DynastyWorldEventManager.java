package com.dynasty.worldevent;

import com.dynasty.blueprint.*;
import com.dynasty.blueprint.combat.Faction;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.storage.loot.*;
import net.minecraft.world.level.storage.loot.parameters.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.*;

/** Bounded per-level lifecycle. No structure generation, explosions, global entity scans or refill waves. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class DynastyWorldEventManager {
    public static final String ACTOR_TAG="DynastyWorldEvent";
    private static final String PROVOKED="DynastyEventProvokedBy";
    private static final String KILLS="DynastyEventMonsterKills";
    private static final String BLESSING="DynastyXuanniaoBlessing";
    private static final Map<ServerLevel,PeaceCache> PEACE=new WeakHashMap<>();
    private record PeaceCache(long time,List<WorldEventInstance> events){}
    public static boolean pacified(Mob mob){
        if(!(mob.level() instanceof ServerLevel level)||mob.getType().getCategory()!=MobCategory.MONSTER
                ||mob instanceof com.dynasty.DynastyBossCombat.BarHolder||!mob.canChangeDimensions())return false;
        long now=level.getGameTime();var cached=PEACE.get(level);
        if(cached==null||cached.time()!=now){cached=new PeaceCache(now,WorldEventStore.get(level).instances.values().stream()
            .filter(i->i.active()&&i.definition.getPath().equals("xuanniao_zhige")).limit(3).toList());PEACE.put(level,cached);}
        return cached.events().stream().anyMatch(i->i.phase==WorldEventInstance.Phase.ACTIVE&&now<i.expires&&mob.blockPosition().distSqr(i.center)<48*48);
    }
    public record StartResult(UUID instance,List<String> missing){public boolean started(){return instance!=null;}}
    public static List<String> missing(ServerLevel level,WorldEventDefinition d){
        var out=new ArrayList<String>();
        if(d.controller()==WorldEventDefinition.Controller.UNIMPLEMENTED)out.add("controller:"+d.id());
        for(var id:d.dependencies())if(!ForgeRegistries.ENTITY_TYPES.containsKey(id)&&!ForgeRegistries.ITEMS.containsKey(id))out.add(id.toString());
        for(var actor:d.actors())if(!ForgeRegistries.ENTITY_TYPES.containsKey(actor.type()))out.add(actor.type().toString());
        if(d.rewardTable()!=null&&level.getServer().getLootData().getLootTable(d.rewardTable())==LootTable.EMPTY)out.add("loot:"+d.rewardTable());
        return List.copyOf(new LinkedHashSet<>(out));
    }
    public static boolean eligible(ServerLevel level,ServerPlayer player,WorldEventDefinition d){
        var pos=player.blockPosition();var store=WorldEventStore.get(level);long time=Math.floorMod(level.getDayTime(),24000L);
        boolean clock=d.startTime()<=d.endTime()?time>=d.startTime()&&time<=d.endTime():time>=d.startTime()||time<=d.endTime();
        return !(player instanceof net.minecraftforge.common.util.FakePlayer)&&!player.isSpectator()&&!player.isCreative()&&level.hasChunkAt(pos)
            &&level.dimensionTypeRegistration().is(TagKey.create(Registries.DIMENSION_TYPE,d.dimensionTag()))
            &&pos.getY()>=d.minY()&&pos.getY()<=d.maxY()&&clock
            &&(d.biomeTag()==null||level.getBiome(pos).is(TagKey.create(Registries.BIOME,d.biomeTag())))
            &&LoadedStructureRegions.contains(level,pos,d.structureTag(),16)
            &&switch(d.weather()){case "ANY"->true;case "CLEAR"->!level.isRaining();case "RAIN"->level.isRaining();case "THUNDER"->level.isThundering();case "FOG"->WorldEventWeather.fogAt(level,pos)||store.worldStates.contains("dynasty:fog");case "SANDSTORM"->store.worldStates.contains("dynasty:sandstorm");case "NO_MOON"->level.getMoonPhase()==4;default->false;}
            &&pos.distSqr(level.getSharedSpawnPos())>=(double)d.minDistanceFromSpawn()*d.minDistanceFromSpawn()
            &&store.worldStates.containsAll(d.requiredWorldStates())&&Collections.disjoint(store.worldStates,d.forbiddenWorldStates())
            &&(!d.id().getPath().equals("xuanniao_zhige")||player.getPersistentData().getInt(KILLS)>=100)
            &&(!d.id().getPath().equals("luoshui_yuansuo")||EcologyManager.connectedWater(level,pos)&&level.getFluidState(pos.below()).is(net.minecraft.tags.FluidTags.WATER));
    }
    public static StartResult start(ServerLevel level,WorldEventDefinition d,BlockPos center,ServerPlayer initiator,boolean manual){
        var dependencies=missing(level,d);if(!dependencies.isEmpty())return new StartResult(null,dependencies);
        if(!level.hasChunkAt(center)||!level.dimensionTypeRegistration().is(TagKey.create(Registries.DIMENSION_TYPE,d.dimensionTag())))return new StartResult(null,List.of("loaded valid dimension"));
        if(!manual&&(initiator==null||!eligible(level,initiator,d)))return new StartResult(null,List.of("trigger conditions"));
        var store=WorldEventStore.get(level);long now=level.getGameTime();
        long active=store.instances.values().stream().filter(WorldEventInstance::active).count();
        long same=store.instances.values().stream().filter(i->i.active()&&i.definition.equals(d.id())).count();
        if(store.instances.size()>=256||active>=3||same>=d.maxConcurrent()
            ||store.instances.values().stream().anyMatch(i->i.active()&&i.center.distSqr(center)<(double)(d.radius()*2)*(d.radius()*2)))return new StartResult(null,List.of("concurrency/distance/storage cap"));
        String playerKey=initiator==null?null:d.id()+"/"+initiator.getUUID();
        var global=WorldEventStore.get(level.getServer().overworld());long globalNow=level.getServer().overworld().getGameTime();
        if(!manual&&(global.cooldowns.getOrDefault("group/"+d.globalCooldownGroup(),0L)>globalNow||playerKey!=null&&store.cooldowns.getOrDefault(playerKey,0L)>now))return new StartResult(null,List.of("cooldown"));
        var instance=new WorldEventInstance(d,center,now,level.random.nextLong(),d.rewardTable());
        if(initiator!=null)instance.participate(initiator.getUUID());store.instances.put(instance.uuid,instance);
        PEACE.remove(level);
        global.cooldowns.put("group/"+d.globalCooldownGroup(),globalNow+d.cooldown());global.setDirty();if(playerKey!=null)store.cooldowns.put(playerKey,now+d.cooldown());store.setDirty();
        return new StartResult(instance.uuid,List.of());
    }
    public static boolean stop(ServerLevel level,UUID uuid){
        var store=WorldEventStore.get(level);var instance=store.instances.get(uuid);if(instance==null||!instance.active())return false;
        finish(level,store,instance,false);return true;
    }
    @SubscribeEvent public static void tick(TickEvent.LevelTickEvent e){
        if(e.phase!=TickEvent.Phase.END||!(e.level instanceof ServerLevel level))return;
        long now=level.getGameTime();var store=WorldEventStore.get(level);
        if(now%20==0){
            int budget=2;
            for(var instance:new ArrayList<>(store.instances.values())){
                if(instance.active())budget=tickInstance(level,store,instance,budget);
                else {cleanup(level,instance);deliverPending(level,instance);}
            }
            // A completed instance may be pruned only after every escrow stack and owned block is gone.
            store.instances.entrySet().removeIf(entry->!entry.getValue().active()&&entry.getValue().rewardGranted
                &&entry.getValue().pendingRewards.isEmpty()&&entry.getValue().blocks.isEmpty()&&now-entry.getValue().expires>24000);
            store.cooldowns.entrySet().removeIf(entry->entry.getValue()<now-24000);store.setDirty();
        }
        if(WorldEventConfig.enabled()&&now%WorldEventConfig.interval()==0&&level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING))evaluateOne(level,store,now);
    }
    private static void evaluateOne(ServerLevel level,WorldEventStore store,long now){
        var players=level.players().stream().filter(p->!(p instanceof net.minecraftforge.common.util.FakePlayer)).toList();
        if(players.isEmpty())return;long batch=now/WorldEventConfig.interval();var player=players.get(Math.floorMod(batch,players.size()));
        var definitions=new ArrayList<>(WorldEventDefinitions.ALL.values());
        // Six candidates per batch; rotate through all 30 across five batches.
        int offset=Math.floorMod(batch*6,definitions.size());
        for(int n=0;n<6;n++){var d=definitions.get((offset+n)%definitions.size());
            if(d.controller()==WorldEventDefinition.Controller.UNIMPLEMENTED||level.random.nextDouble()>=WorldEventConfig.chance(d.rarity())||!eligible(level,player,d))continue;
            if(start(level,d,player.blockPosition(),player,false).started())break;
        }
    }
    static int tickInstance(ServerLevel level,WorldEventStore store,WorldEventInstance instance,int budget){
        var d=WorldEventDefinitions.ALL.get(instance.definition);
        if(d==null||d.controller()==WorldEventDefinition.Controller.UNIMPLEMENTED){finish(level,store,instance,false);return budget;}
        if(level.getGameTime()>=instance.expires){finish(level,store,instance,false);return budget;}
        boolean nearby=false;
        for(var player:level.players())if(!player.isSpectator()&&(!player.isCreative()||instance.participants.contains(player.getUUID()))&&player.blockPosition().distSqr(instance.center)<(double)d.radius()*d.radius()){
            nearby=true;instance.participate(player.getUUID());
            if(level.getGameTime()%100==0)sendState(player,instance);
        }
        if(!nearby)return budget; // Absolute expiry still advances; actor actions never catch up after unload.
        if(instance.phase==WorldEventInstance.Phase.WARNING){
            if(level.getGameTime()<instance.started+40)return budget;
            instance.phase=WorldEventInstance.Phase.ASSEMBLING;store.setDirty();
        }
        var requests=new ArrayList<WorldEventDefinition.Actor>();for(var request:d.actors())for(int n=0;n<request.count();n++)requests.add(request);
        while(instance.phase==WorldEventInstance.Phase.ASSEMBLING&&instance.spawned<requests.size()&&budget>0){
            budget--;if(!spawnActor(level,instance,requests.get(instance.spawned),instance.spawned))break;instance.spawned++;store.setDirty();
        }
        if(instance.phase==WorldEventInstance.Phase.ASSEMBLING&&instance.spawned>=requests.size()){instance.phase=WorldEventInstance.Phase.ACTIVE;store.setDirty();}
        if(instance.phase!=WorldEventInstance.Phase.ACTIVE)return budget;
        switch(d.controller()){
            case PROCESSION->{
                if(instance.provoked){if(instance.actors.values().stream().allMatch(WorldEventInstance.Actor::dead))finish(level,store,instance,true);}
                else if(level.getGameTime()-instance.started>=1200
                    &&instance.actors.values().stream().allMatch(a->level.getEntity(a.uuid()) instanceof Mob m&&m.blockPosition().distSqr(marchDestination(instance))<64))finish(level,store,instance,true);
            }
            case BATTLE->{
                var guards=instance.actors.values().stream().filter(a->a.team().equals("ARMY")).toList();
                var rebels=instance.actors.values().stream().filter(a->a.team().equals("REBELS")).toList();
                if(!guards.isEmpty()&&guards.stream().allMatch(WorldEventInstance.Actor::dead))finish(level,store,instance,false);
                else if(!rebels.isEmpty()&&rebels.stream().allMatch(WorldEventInstance.Actor::dead))finish(level,store,instance,true);
                else targetOpponents(level,instance);
            }
            case CELESTIAL->{
                blessParticipants(level,instance);pacifyNearby(level,instance);
                if(level.getGameTime()-instance.started>=400){instance.effectGranted=true;finish(level,store,instance,true);}
            }
            default->{}
        }
        return budget;
    }
    private static boolean spawnActor(ServerLevel level,WorldEventInstance instance,WorldEventDefinition.Actor request,int index){
        var type=ForgeRegistries.ENTITY_TYPES.getValue(request.type());if(type==null)return false;
        // Runtime templates consume only real cod1 combatants, never old bosses or disguised replacements.
        var entity=type.create(level);if(!(entity instanceof TemplateMob mob))return false;
        var random=net.minecraft.util.RandomSource.create(instance.seed+index*7919L+level.getGameTime()/20);BlockPos found=null;
        for(int n=0;n<8;n++){
            int dx=(request.team().equals("REBELS")?10:-10)+random.nextInt(9)-4,dz=random.nextInt(17)-8;
            var candidate=instance.center.offset(dx,0,dz);if(!level.hasChunkAt(candidate))continue;
            for(int dy=3;dy>=-4;dy--){var p=candidate.above(dy);
                if(p.getY()<=level.getMinBuildHeight()||p.getY()>=level.getMaxBuildHeight()-3||!level.hasChunkAt(p)
                    ||!com.dynasty.entity.DynastySpawnPlacement.hasStandingSpace(level,p,type.getDimensions().makeBoundingBox(p.getX()+.5,p.getY(),p.getZ()+.5)))continue;
                if(level.players().stream().anyMatch(player->!player.isSpectator()&&player.blockPosition().distSqr(p)<16))continue;
                found=p;break;
            }
            if(found!=null)break;
        }
        if(found==null)return false;
        mob.moveTo(found.getX()+.5,found.getY(),found.getZ()+.5,0,0);mob.setPersistenceRequired();
        mob.getPersistentData().putUUID(ACTOR_TAG,instance.uuid);mob.getPersistentData().putString("DynastyWorldEventTeam",request.team());
        EcologyManager.assignFaction(mob,request.team().equals("REBELS")?Faction.REBELS:request.team().equals("SPIRITS")?Faction.SPIRITS:Faction.DYNASTY_ARMY);
        mob.finalizeSpawn(level,level.getCurrentDifficultyAt(found),MobSpawnType.EVENT,null,null);
        if(request.team().equals("ARMY")&&WorldEventDefinitions.ALL.get(instance.definition).controller()==WorldEventDefinition.Controller.BATTLE)mob.setHealth(Math.max(8,mob.getMaxHealth()*.4F));
        instance.actors.put(mob.getUUID(),new WorldEventInstance.Actor(mob.getUUID(),request.type(),request.team(),false));
        if(!level.addFreshEntity(mob)){instance.actors.remove(mob.getUUID());return false;}return true;
    }
    private static void targetOpponents(ServerLevel level,WorldEventInstance instance){
        for(var actor:instance.actors.values())if(!actor.dead()&&level.getEntity(actor.uuid()) instanceof TemplateMob mob){
            if(mob.getTarget() instanceof net.minecraft.world.entity.player.Player||mob.attack().current()!=null)continue;
            instance.actors.values().stream().filter(a->!a.dead()&&!a.team().equals(actor.team())).map(a->level.getEntity(a.uuid()))
                .filter(e->e instanceof LivingEntity&&e.isAlive()&&mob.distanceToSqr(e)<=24*24&&mob.hasLineOfSight(e))
                .min(Comparator.comparingDouble(mob::distanceToSqr)).ifPresent(e->mob.setTarget((LivingEntity)e));
        }
    }
    private static WorldEventInstance instance(Entity entity){
        if(!(entity.level() instanceof ServerLevel level)||!entity.getPersistentData().hasUUID(ACTOR_TAG))return null;
        var i=WorldEventStore.get(level).instances.get(entity.getPersistentData().getUUID(ACTOR_TAG));
        return i!=null&&i.active()&&i.actors.containsKey(entity.getUUID())?i:null;
    }
    public static boolean peacefulToPlayer(TemplateMob mob){
        var i=instance(mob);if(i==null)return false;var d=WorldEventDefinitions.ALL.get(i.definition);if(d==null)return false;
        return d.controller()==WorldEventDefinition.Controller.PROCESSION&&!i.provoked
            ||d.controller()==WorldEventDefinition.Controller.BATTLE&&!mob.getPersistentData().hasUUID(PROVOKED);
    }
    public static boolean marching(TemplateMob mob){
        var i=instance(mob);var d=i==null?null:WorldEventDefinitions.ALL.get(i.definition);
        return d!=null&&d.controller()==WorldEventDefinition.Controller.PROCESSION&&i.phase==WorldEventInstance.Phase.ACTIVE&&!i.provoked;
    }
    public static BlockPos marchDestination(WorldEventInstance instance){return instance.center.offset((instance.seed&1)==0?50:-50,0,0);}
    public static void march(TemplateMob mob){
        var i=instance(mob);if(i==null)return;var end=marchDestination(i);var delta=Vec3.atBottomCenterOf(end).subtract(mob.position());
        if(delta.horizontalDistanceSqr()<9){mob.getNavigation().stop();return;}
        var step=BlockPos.containing(mob.position().add(delta.normalize().scale(8)));
        if(mob.level().hasChunkAt(step))mob.getNavigation().moveTo(step.getX()+.5,step.getY(),step.getZ()+.5,.6);
    }
    @SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.LOWEST) public static void hurt(LivingHurtEvent event){
        if(event.isCanceled()||event.getAmount()<=0)return;
        if(event.getSource().getEntity() instanceof Mob mob&&pacified(mob)){event.setCanceled(true);return;}
        if(!(event.getSource().getEntity() instanceof ServerPlayer player))return;
        if(event.getEntity() instanceof TemplateMob mob&&mob.faction()==Faction.DYNASTY_ARMY)player.getPersistentData().remove(WorldEventItems.PERMIT);
        var i=instance(event.getEntity());if(i==null)return;
        i.provoked=true;i.participate(player.getUUID());event.getEntity().getPersistentData().putUUID(PROVOKED,player.getUUID());WorldEventStore.get((ServerLevel)event.getEntity().level()).setDirty();
    }
    @SubscribeEvent(priority=net.minecraftforge.eventbus.api.EventPriority.LOWEST) public static void died(LivingDeathEvent event){
        if(event.getSource().getEntity() instanceof ServerPlayer player&&event.getEntity().getType().getCategory()==MobCategory.MONSTER){
            var data=player.getPersistentData();data.putInt(KILLS,Math.min(10000,data.getInt(KILLS)+1));
        }
        var i=instance(event.getEntity());if(i==null)return;var actor=i.actors.get(event.getEntity().getUUID());
        i.actors.put(actor.uuid(),new WorldEventInstance.Actor(actor.uuid(),actor.type(),actor.team(),true));WorldEventStore.get((ServerLevel)event.getEntity().level()).setDirty();
    }
    @SubscribeEvent public static void joined(EntityJoinLevelEvent event){
        if(!(event.getLevel() instanceof ServerLevel level)||!event.getEntity().getPersistentData().hasUUID(ACTOR_TAG))return;
        var entity=event.getEntity();var i=WorldEventStore.get(level).instances.get(entity.getPersistentData().getUUID(ACTOR_TAG));
        if(i==null||!i.active()||level.getGameTime()>=i.expires||!i.actors.containsKey(entity.getUUID())||i.actors.get(entity.getUUID()).dead()||!i.actors.get(entity.getUUID()).type().equals(ForgeRegistries.ENTITY_TYPES.getKey(entity.getType()))){
            event.setCanceled(true);entity.discard();
        }
    }
    private static void blessParticipants(ServerLevel level,WorldEventInstance instance){
        for(var player:level.players())if(instance.participants.contains(player.getUUID())){
            var data=player.getPersistentData();if(data.hasUUID(BLESSING)&&data.getUUID(BLESSING).equals(instance.uuid))continue;
            for(var stack:player.getInventory().items)if(stack.isDamageableItem()&&stack.getAttributeModifiers(EquipmentSlot.MAINHAND).containsKey(Attributes.ATTACK_DAMAGE))
                stack.setDamageValue(Math.max(0,stack.getDamageValue()-(int)Math.ceil(stack.getMaxDamage()*.3)));
            player.addEffect(new MobEffectInstance(MobEffects.LUCK,36000,0));player.addEffect(new MobEffectInstance(MobEffects.DAMAGE_BOOST,36000,0));
            data.putUUID(BLESSING,instance.uuid);player.containerMenu.broadcastChanges();
        }
    }
    private static void pacifyNearby(ServerLevel level,WorldEventInstance instance){
        var nearby=level.getEntitiesOfClass(Mob.class,new net.minecraft.world.phys.AABB(instance.center).inflate(48),e->e.isAlive()&&pacified(e));
        for(int n=0;n<Math.min(16,nearby.size());n++){
            var mob=nearby.get(Math.floorMod(level.getGameTime()/20*16+n,nearby.size()));mob.setTarget(null);var away=mob.position().subtract(Vec3.atCenterOf(instance.center));
            if(away.horizontalDistanceSqr()<.1)away=new Vec3(1,0,0);var p=BlockPos.containing(mob.position().add(away.normalize().scale(6)));
            if(level.hasChunkAt(p))mob.getNavigation().moveTo(p.getX(),p.getY(),p.getZ(),1.1);
        }
    }
    static void finish(ServerLevel level,WorldEventStore store,WorldEventInstance instance,boolean success){
        if(!instance.active())return;instance.phase=success?WorldEventInstance.Phase.SUCCESS:WorldEventInstance.Phase.FAILED;
        if(success)reserveRewards(level,instance);else instance.rewardGranted=true;
        cleanup(level,instance);deliverPending(level,instance);store.setDirty();for(var player:level.players())sendState(player,instance);
    }
    private static void reserveRewards(ServerLevel level,WorldEventInstance i){
        if(i.rewardGranted)return;
        if(i.rewardTable==null){i.rewardGranted=true;return;}
        var table=level.getServer().getLootData().getLootTable(i.rewardTable);if(table==LootTable.EMPTY)return;
        var d=WorldEventDefinitions.ALL.get(i.definition);if(d==null)return;
        var owners=new ArrayList<>(i.participants);if(d.rewardMode()==WorldEventDefinition.RewardMode.WORLD_ONCE&&owners.size()>1)owners=new ArrayList<>(owners.subList(0,1));
        var bundles=new LinkedHashMap<UUID,List<ItemStack>>();
        for(var owner:owners){var player=level.getServer().getPlayerList().getPlayer(owner);
            var builder=new LootParams.Builder(level).withParameter(LootContextParams.ORIGIN,Vec3.atCenterOf(i.center)).withOptionalParameter(LootContextParams.THIS_ENTITY,player);
            if(player!=null)builder.withLuck(player.getLuck());var loot=table.getRandomItems(builder.create(LootContextParamSets.CHEST),i.seed^owner.getLeastSignificantBits());
            if(loot.size()>128)return;bundles.put(owner,new ArrayList<>(loot.stream().map(ItemStack::copy).toList()));
        }
        i.pendingRewards.putAll(bundles);i.rewardGranted=true;
    }
    static void deliverPending(ServerLevel level,WorldEventInstance i){
        if(i.phase==WorldEventInstance.Phase.SUCCESS&&!i.rewardGranted)reserveRewards(level,i);
        var iterator=i.pendingRewards.entrySet().iterator();
        while(iterator.hasNext()){var entry=iterator.next();var player=level.players().stream().filter(p->p.getUUID().equals(entry.getKey())).findFirst().orElse(null);if(player==null)continue;
            for(var stack:entry.getValue())player.getInventory().add(stack);entry.getValue().removeIf(ItemStack::isEmpty);
            player.containerMenu.broadcastChanges();if(entry.getValue().isEmpty())iterator.remove();
        }
    }
    static void cleanup(ServerLevel level,WorldEventInstance instance){
        for(var actor:instance.actors.values()){var entity=level.getEntity(actor.uuid());if(entity!=null)entity.discard();}
        var iterator=instance.blocks.entrySet().iterator();while(iterator.hasNext()){
            var entry=iterator.next();if(!level.hasChunkAt(entry.getKey()))continue;
            // Restore only our exact placed state; preserve subsequent player edits.
            if(level.getBlockState(entry.getKey()).equals(entry.getValue().placed()))level.setBlock(entry.getKey(),entry.getValue().original(),3);iterator.remove();
        }
    }
    private static void sendState(ServerPlayer player,WorldEventInstance i){
        if(player instanceof net.minecraftforge.common.util.FakePlayer)return;
        com.dynasty.network.DynastyNetwork.CHANNEL.send(net.minecraftforge.network.PacketDistributor.PLAYER.with(()->player),
            new WorldEventStatePacket(i.uuid,i.definition,player.level().dimension().location(),i.center,i.started,i.expires,i.phase.ordinal(),i.seed));
    }
    private DynastyWorldEventManager(){}
}
