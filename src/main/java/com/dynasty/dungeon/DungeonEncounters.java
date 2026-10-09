package com.dynasty.dungeon;

import com.dynasty.Dynasty;
import com.mojang.logging.LogUtils;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.storage.loot.LootParams;
import net.minecraft.world.level.storage.loot.LootTable;
import net.minecraft.world.level.storage.loot.parameters.LootContextParamSets;
import net.minecraft.world.level.storage.loot.parameters.LootContextParams;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingDropsEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/** Dungeon-side caller of cod1 startEncounter; no boss creation or replacement implementation. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class DungeonEncounters {
    private static final String ACTOR_TAG="dynasty_dungeon_encounter";
    private static final Map<ResourceLocation,Binding> BINDINGS=new HashMap<>();
    private static final ResourceLocation CHENSHA_BOSS=new ResourceLocation("dynasty:zhaoming_di");
    public enum Result { MISSING_DEPENDENCY, SEALED, STARTED, ACTIVE, START_RESERVED, DEFEATED, INELIGIBLE, CLAIMED, INVENTORY_FULL, ALREADY_CLAIMED }

    @FunctionalInterface public interface EncounterStarter { Mob startEncounter(ServerLevel level,Context context); }
    /** requiredItems are coffin-owned rewards: validate their existence and suppress duplicate actor drops. */
    public record Binding(ResourceLocation bossType,EncounterStarter starter,ResourceLocation worldLoot,
            ResourceLocation playerLoot,Set<ResourceLocation> requiredItems){
        public Binding {
            java.util.Objects.requireNonNull(bossType);java.util.Objects.requireNonNull(starter);
            java.util.Objects.requireNonNull(worldLoot);requiredItems=Set.copyOf(requiredItems);
        }
    }
    public record Context(UUID instance,ResourceLocation dungeon,UUID attempt,Vec3 spawn,AABB arena,List<UUID> entrants){
        public Context { entrants=List.copyOf(entrants); }
        /** Call BEFORE cod1 adds its actor, so persistent entity data carries the reservation. */
        public void bindActor(Mob actor){
            var tag=new CompoundTag();tag.putUUID("Instance",instance);tag.putUUID("Attempt",attempt);
            tag.putString("Dungeon",dungeon.toString());actor.getPersistentData().put(ACTOR_TAG,tag);
        }
    }
    public static synchronized void register(Binding binding){
        if(BINDINGS.putIfAbsent(binding.bossType(),binding)!=null)throw new IllegalStateException("Duplicate dungeon encounter "+binding.bossType());
    }
    public static Result chenshaReadiness(ServerLevel level){
        return ready(level,BINDINGS.get(CHENSHA_BOSS))?Result.ACTIVE:Result.MISSING_DEPENDENCY;
    }
    public static List<String> missingChenshaDependencies(ServerLevel level){
        var missing=new java.util.ArrayList<String>();var binding=BINDINGS.get(CHENSHA_BOSS);
        if(!ForgeRegistries.ENTITY_TYPES.containsKey(CHENSHA_BOSS))missing.add(CHENSHA_BOSS.toString());
        if(binding==null)missing.add("cod1 startEncounter + world/player reward binding");
        else{
            if(level.getServer().getLootData().getLootTable(binding.worldLoot())==LootTable.EMPTY)missing.add(binding.worldLoot().toString());
            if(binding.playerLoot()!=null&&level.getServer().getLootData().getLootTable(binding.playerLoot())==LootTable.EMPTY)missing.add(binding.playerLoot().toString());
            binding.requiredItems().stream().filter(id->!ForgeRegistries.ITEMS.containsKey(id)).sorted().forEach(id->missing.add(id.toString()));
        }
        return List.copyOf(missing);
    }
    static boolean ready(ServerLevel level,Binding binding){
        return binding!=null&&ForgeRegistries.ENTITY_TYPES.containsKey(binding.bossType())
            &&binding.requiredItems().stream().allMatch(ForgeRegistries.ITEMS::containsKey)
            &&level.getServer().getLootData().getLootTable(binding.worldLoot())!=LootTable.EMPTY
            &&(binding.playerLoot()==null||level.getServer().getLootData().getLootTable(binding.playerLoot())!=LootTable.EMPTY);
    }
    public static boolean validChenshaBinding(String room,BlockPos pos,BlockPos origin,boolean coffin){
        return room.equals("imperial_vault")&&pos.equals(origin.offset(coffin?ChenshaPiece.coffinOffset():ChenshaPiece.core(room)));
    }
    static AABB arena(BlockPos origin){return new AABB(origin.offset(8,1,2),origin.offset(56,18,30));}
    static boolean entrant(ServerPlayer p,BlockPos origin){
        if(!p.isAlive()||p.isSpectator()||p.isCreative()||!arena(origin).contains(p.position()))return false;
        double x=p.getX()-origin.getX(),z=p.getZ()-origin.getZ();
        return Math.pow((x-31.5)/23.5,2)+Math.pow((z-15.5)/13.5,2)<=1;
    }
    public static Result tickChensha(ServerLevel level,UUID instance,BlockPos origin){
        if(!level.dimension().location().equals(DungeonDefinition.CHENSHA.dimension()))return Result.SEALED;
        var players=level.players().stream().filter(p->entrant(p,origin)).limit(64).toList();
        if(players.isEmpty())return Result.INELIGIBLE;
        var store=DungeonStateStore.get(level);
        if(!store.room(instance,"entrance").completed()||!store.room(instance,"mercury").completed())return Result.SEALED;
        var state=store.encounter(instance,DungeonDefinition.CHENSHA.id().toString(),true);
        if(state.phase()==DungeonEncounterState.Phase.DEFEATED)return Result.DEFEATED;
        if(state.phase()==DungeonEncounterState.Phase.ACTIVE){
            for(var p:players)if(state.join(p.getUUID()))store.setDirty();
            return Result.ACTIVE;
        }
        if(state.phase()==DungeonEncounterState.Phase.STARTING){
            if(!recover(level,state,instance,DungeonDefinition.CHENSHA.id(),arena(origin)))return Result.START_RESERVED;
            for(var p:players)state.join(p.getUUID());store.setDirty();return Result.ACTIVE;
        }
        var context=new Context(instance,DungeonDefinition.CHENSHA.id(),null,
            Vec3.atBottomCenterOf(origin.offset(31,10,15)),arena(origin),players.stream().map(ServerPlayer::getUUID).toList());
        return start(level,store,state,context,BINDINGS.get(CHENSHA_BOSS));
    }
    static Result start(ServerLevel level,DungeonStateStore store,DungeonEncounterState state,Context context,Binding binding){
        if(!ready(level,binding))return Result.MISSING_DEPENDENCY;
        if(!state.reserve(binding.bossType()))return Result.START_RESERVED;
        store.setDirty();
        var reserved=new Context(context.instance(),context.dungeon(),state.attempt(),context.spawn(),context.arena(),context.entrants());
        try {
            var boss=binding.starter().startEncounter(level,reserved);
            if(boss==null||boss.level()!=level||!boss.isAlive()||boss.isRemoved()
                ||!binding.bossType().equals(ForgeRegistries.ENTITY_TYPES.getKey(boss.getType()))
                ||!context.arena().contains(boss.position())||level.getEntity(boss.getUUID())!=boss)return Result.START_RESERVED;
            var tag=boss.getPersistentData().getCompound(ACTOR_TAG);
            if(!tag.hasUUID("Attempt")||!state.attempt().equals(tag.getUUID("Attempt"))
                ||!tag.hasUUID("Instance")||!context.instance().equals(tag.getUUID("Instance"))
                ||!context.dungeon().toString().equals(tag.getString("Dungeon")))return Result.START_RESERVED;
            state.activate(boss.getUUID());for(var player:context.entrants())state.join(player);store.setDirty();
            return Result.STARTED;
        }catch(RuntimeException failure){
            // The starter may already have spawned an actor. Preserve its reservation, never retry blindly.
            LogUtils.getLogger().error("Dungeon encounter start reserved after failure: {} / {}",context.dungeon(),context.instance(),failure);
            return Result.START_RESERVED;
        }
    }
    /** Adopt a uniquely matching loaded actor after a partial start; never create an actor or load a chunk. */
    static boolean recover(ServerLevel level,DungeonEncounterState state,UUID instance,ResourceLocation dungeon,AABB bounds){
        if(state.phase()!=DungeonEncounterState.Phase.STARTING||state.attempt()==null||state.bossType()==null)return false;
        var candidates=level.getEntitiesOfClass(Mob.class,bounds,actor->{
            var tag=actor.getPersistentData().getCompound(ACTOR_TAG);
            return actor.isAlive()&&state.bossType().equals(ForgeRegistries.ENTITY_TYPES.getKey(actor.getType()))
                &&tag.hasUUID("Attempt")&&state.attempt().equals(tag.getUUID("Attempt"))
                &&tag.hasUUID("Instance")&&instance.equals(tag.getUUID("Instance"))&&dungeon.toString().equals(tag.getString("Dungeon"));
        });
        return candidates.size()==1&&state.activate(candidates.get(0).getUUID());
    }
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void onDeath(LivingDeathEvent event){
        if(event.isCanceled())return;
        if(!(event.getEntity() instanceof Mob actor)||!(actor.level() instanceof ServerLevel level))return;
        recordDeath(level,actor);
    }
    static boolean recordDeath(ServerLevel level,Mob actor){
        if(actor.isAlive())return false;
        var tag=actor.getPersistentData().getCompound(ACTOR_TAG);
        if(!tag.hasUUID("Instance")||!tag.hasUUID("Attempt"))return false;
        var dungeon=ResourceLocation.tryParse(tag.getString("Dungeon"));if(dungeon==null)return false;
        var store=DungeonStateStore.get(level);var state=store.encounter(tag.getUUID("Instance"),dungeon.toString(),false);
        if(state==null||!state.defeat(actor.getUUID(),ForgeRegistries.ENTITY_TYPES.getKey(actor.getType()),tag.getUUID("Attempt")))return false;
        store.setDirty();return true;
    }
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void onDrops(LivingDropsEvent event){
        if(event.isCanceled()||!(event.getEntity() instanceof Mob actor)||!(actor.level() instanceof ServerLevel level))return;
        var tag=actor.getPersistentData().getCompound(ACTOR_TAG);
        if(!tag.hasUUID("Instance")||!tag.hasUUID("Attempt"))return;
        var dungeon=ResourceLocation.tryParse(tag.getString("Dungeon"));if(dungeon==null)return;
        var state=DungeonStateStore.get(level).encounter(tag.getUUID("Instance"),dungeon.toString(),false);
        var binding=BINDINGS.get(ForgeRegistries.ENTITY_TYPES.getKey(actor.getType()));
        suppressDuplicateDrops(state,actor,event.getDrops(),binding);
    }
    static boolean suppressDuplicateDrops(DungeonEncounterState state,Mob actor,java.util.Collection<net.minecraft.world.entity.item.ItemEntity> drops,Binding binding){
        var tag=actor.getPersistentData().getCompound(ACTOR_TAG);
        if(state==null||binding==null||!actor.getUUID().equals(state.boss())||!tag.hasUUID("Attempt")
                ||!tag.getUUID("Attempt").equals(state.attempt())||!binding.bossType().equals(ForgeRegistries.ENTITY_TYPES.getKey(actor.getType())))return false;
        return drops.removeIf(drop->binding.requiredItems().contains(ForgeRegistries.ITEMS.getKey(drop.getItem().getItem())));
    }
    static String worldKey(ResourceLocation dungeon){return dungeon+"/first_kill/world";}
    static String playerKey(ResourceLocation dungeon,UUID player){return dungeon+"/first_kill/player/"+player;}
    public static Result claimChensha(ServerLevel level,UUID instance,BlockPos origin,ServerPlayer player){
        if(!level.dimension().location().equals(DungeonDefinition.CHENSHA.dimension()))return Result.INELIGIBLE;
        if(!entrant(player,origin))return Result.INELIGIBLE;
        var store=DungeonStateStore.get(level);var state=store.encounter(instance,DungeonDefinition.CHENSHA.id().toString(),false);
        return claim(level,store,state,DungeonDefinition.CHENSHA.id(),player,BINDINGS.get(CHENSHA_BOSS));
    }
    static Result claim(ServerLevel level,DungeonStateStore store,DungeonEncounterState state,ResourceLocation dungeon,ServerPlayer player,Binding binding){
        if(state==null||state.phase()!=DungeonEncounterState.Phase.DEFEATED)return Result.SEALED;
        if(!state.participant(player.getUUID()))return Result.INELIGIBLE;
        if(!ready(level,binding)||!state.bossType().equals(binding.bossType()))return Result.MISSING_DEPENDENCY;
        var worldKey=worldKey(dungeon);var playerKey=playerKey(dungeon,player.getUUID());
        var world=store.reward(worldKey);var personal=store.reward(playerKey);
        // Generate both bundles before reserving either one: missing/empty tables cannot consume a first kill.
        var worldItems=world==null?loot(level,binding.worldLoot(),player):List.<ItemStack>of();
        var playerItems=binding.playerLoot()!=null&&personal==null?loot(level,binding.playerLoot(),player):List.<ItemStack>of();
        if(world==null&&(worldItems.isEmpty()||worldItems.size()>128)
            ||binding.playerLoot()!=null&&personal==null&&(playerItems.isEmpty()||playerItems.size()>128))return Result.MISSING_DEPENDENCY;
        if(world==null)world=store.reserveReward(worldKey,player.getUUID(),worldItems);
        if(binding.playerLoot()!=null&&personal==null)personal=store.reserveReward(playerKey,player.getUUID(),playerItems);
        boolean changed=world.deliver(player);if(personal!=null)changed|=personal.deliver(player);
        if(changed)store.setDirty();
        boolean pending=player.getUUID().equals(world.owner())&&!world.empty()||personal!=null&&!personal.empty();
        return pending?Result.INVENTORY_FULL:changed?Result.CLAIMED:Result.ALREADY_CLAIMED;
    }
    private static List<ItemStack> loot(ServerLevel level,ResourceLocation table,ServerPlayer player){
        var params=new LootParams.Builder(level).withParameter(LootContextParams.ORIGIN,player.position())
            .withOptionalParameter(LootContextParams.THIS_ENTITY,player).withLuck(player.getLuck()).create(LootContextParamSets.CHEST);
        return level.getServer().getLootData().getLootTable(table).getRandomItems(params);
    }
    private DungeonEncounters(){}
}
