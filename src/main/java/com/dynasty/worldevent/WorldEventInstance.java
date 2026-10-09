package com.dynasty.worldevent;

import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import java.util.*;

/** Absolute server clock and actor reservations survive unloads. Missing UUID is never a death. */
public final class WorldEventInstance {
    public enum Phase { WARNING, ASSEMBLING, ACTIVE, SUCCESS, FAILED }
    public record Actor(UUID uuid,ResourceLocation type,String team,boolean dead){}
    public record TemporaryBlock(BlockState original,BlockState placed){}
    public final UUID uuid;
    public final ResourceLocation definition;
    public final BlockPos center;
    public final long started,expires,seed;
    public final ResourceLocation rewardTable;
    public Phase phase=Phase.WARNING;
    public int spawned;
    public boolean provoked,rewardGranted,effectGranted;
    public final Set<UUID> participants=new LinkedHashSet<>();
    public final Map<UUID,Actor> actors=new LinkedHashMap<>();
    public final Map<BlockPos,TemporaryBlock> blocks=new LinkedHashMap<>();
    public final Map<UUID,List<ItemStack>> pendingRewards=new LinkedHashMap<>();
    WorldEventInstance(WorldEventDefinition definition,BlockPos center,long time,long seed,ResourceLocation rewardTable){
        this(UUID.randomUUID(),definition.id(),center,time,time+definition.duration(),seed,rewardTable);
    }
    private WorldEventInstance(UUID uuid,ResourceLocation definition,BlockPos center,long started,long expires,long seed,ResourceLocation rewardTable){
        this.uuid=uuid;this.definition=definition;this.center=center.immutable();this.started=started;this.expires=expires;this.seed=seed;this.rewardTable=rewardTable;
    }
    public boolean active(){return phase==Phase.WARNING||phase==Phase.ASSEMBLING||phase==Phase.ACTIVE;}
    public boolean participate(UUID player){return participants.contains(player)||participants.size()<64&&participants.add(player);}
    public CompoundTag save(){
        var t=new CompoundTag();t.putUUID("UUID",uuid);t.putString("Definition",definition.toString());t.putLong("Center",center.asLong());t.putLong("Started",started);t.putLong("Expires",expires);t.putLong("Seed",seed);
        if(rewardTable!=null)t.putString("RewardTable",rewardTable.toString());t.putString("Phase",phase.name());t.putInt("Spawned",spawned);t.putBoolean("Provoked",provoked);t.putBoolean("RewardGranted",rewardGranted);t.putBoolean("EffectGranted",effectGranted);
        var people=new net.minecraft.nbt.ListTag();participants.forEach(p->people.add(net.minecraft.nbt.NbtUtils.createUUID(p)));t.put("Participants",people);
        var entities=new net.minecraft.nbt.ListTag();actors.values().forEach(a->{var x=new CompoundTag();x.putUUID("UUID",a.uuid());x.putString("Type",a.type().toString());x.putString("Team",a.team());x.putBoolean("Dead",a.dead());entities.add(x);});t.put("Actors",entities);
        var terrain=new net.minecraft.nbt.ListTag();blocks.forEach((p,b)->{var x=new CompoundTag();x.putLong("Pos",p.asLong());x.put("Original",net.minecraft.nbt.NbtUtils.writeBlockState(b.original()));x.put("Placed",net.minecraft.nbt.NbtUtils.writeBlockState(b.placed()));terrain.add(x);});t.put("Blocks",terrain);
        var rewards=new net.minecraft.nbt.ListTag();pendingRewards.forEach((p,items)->{var x=new CompoundTag();x.putUUID("Player",p);var stacks=new net.minecraft.nbt.ListTag();items.forEach(s->stacks.add(s.save(new CompoundTag())));x.put("Items",stacks);rewards.add(x);});t.put("PendingRewards",rewards);return t;
    }
    public static WorldEventInstance load(CompoundTag t){
        if(!t.hasUUID("UUID"))return null;
        var definition=ResourceLocation.tryParse(t.getString("Definition"));if(definition==null)return null;
        var out=new WorldEventInstance(t.getUUID("UUID"),definition,BlockPos.of(t.getLong("Center")),t.getLong("Started"),t.getLong("Expires"),t.getLong("Seed"),ResourceLocation.tryParse(t.getString("RewardTable")));
        try{out.phase=Phase.valueOf(t.getString("Phase"));}catch(IllegalArgumentException e){out.phase=Phase.FAILED;}
        out.spawned=Math.max(0,Math.min(24,t.getInt("Spawned")));out.provoked=t.getBoolean("Provoked");out.rewardGranted=t.getBoolean("RewardGranted");out.effectGranted=t.getBoolean("EffectGranted");
        for(var p:t.getList("Participants",11))if(out.participants.size()<64)try{out.participants.add(net.minecraft.nbt.NbtUtils.loadUUID(p));}catch(IllegalArgumentException ignored){}
        for(var a:t.getList("Actors",10))if(out.actors.size()<24){var x=(CompoundTag)a;var type=ResourceLocation.tryParse(x.getString("Type"));if(x.hasUUID("UUID")&&type!=null&&Set.of("ARMY","REBELS","SPIRITS").contains(x.getString("Team"))){var u=x.getUUID("UUID");out.actors.put(u,new Actor(u,type,x.getString("Team"),x.getBoolean("Dead")));}}
        var registry=net.minecraft.core.registries.BuiltInRegistries.BLOCK.asLookup();
        for(var b:t.getList("Blocks",10))if(out.blocks.size()<64){var x=(CompoundTag)b;out.blocks.put(BlockPos.of(x.getLong("Pos")),new TemporaryBlock(net.minecraft.nbt.NbtUtils.readBlockState(registry,x.getCompound("Original")),net.minecraft.nbt.NbtUtils.readBlockState(registry,x.getCompound("Placed"))));}
        for(var r:t.getList("PendingRewards",10))if(out.pendingRewards.size()<64){var x=(CompoundTag)r;if(!x.hasUUID("Player"))continue;var stacks=new ArrayList<ItemStack>();for(var s:x.getList("Items",10))if(stacks.size()<128){var stack=ItemStack.of((CompoundTag)s);if(!stack.isEmpty())stacks.add(stack);}out.pendingRewards.put(x.getUUID("Player"),stacks);}
        if(!out.pendingRewards.isEmpty())out.rewardGranted=true;
        return out;
    }
}
