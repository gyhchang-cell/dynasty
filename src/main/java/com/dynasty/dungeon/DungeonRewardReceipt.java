package com.dynasty.dungeon;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.world.item.ItemStack;
import net.minecraft.server.level.ServerPlayer;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/** Persistent reward escrow: full inventories leave stacks here, never on the floor. */
public final class DungeonRewardReceipt {
    private final UUID owner;
    private final List<ItemStack> pending;
    DungeonRewardReceipt(UUID owner,List<ItemStack> items){
        this.owner=owner;pending=new ArrayList<>(items.stream().filter(s->!s.isEmpty()).map(ItemStack::copy).toList());
    }
    public UUID owner(){return owner;}
    public boolean empty(){return pending.isEmpty();}
    public boolean deliver(ServerPlayer player){
        if(!player.getUUID().equals(owner))return false;
        boolean changed=false;
        for(var stack:pending){int before=stack.getCount();player.getInventory().add(stack);changed|=stack.getCount()!=before;}
        pending.removeIf(ItemStack::isEmpty);
        if(changed)player.containerMenu.broadcastChanges();
        return changed;
    }
    public CompoundTag save(){
        var tag=new CompoundTag();if(owner!=null)tag.putUUID("Owner",owner);
        var stacks=new ListTag();pending.forEach(s->stacks.add(s.save(new CompoundTag())));tag.put("Pending",stacks);return tag;
    }
    public static DungeonRewardReceipt load(CompoundTag tag){
        var items=new ArrayList<ItemStack>();
        for(var item:tag.getList("Pending",10))if(items.size()<128)items.add(ItemStack.of((CompoundTag)item));
        // A malformed receipt retains its key with no claimant; it cannot reroll loot.
        return new DungeonRewardReceipt(tag.hasUUID("Owner")?tag.getUUID("Owner"):null,items);
    }
}
