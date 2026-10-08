package com.dynasty.infusion;

import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.*;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BaseContainerBlockEntity;
import net.minecraft.world.level.block.state.BlockState;

/** Persistent inventory shared by viewers. Revision invalidates obsolete previews. */
public final class InfusionBlockEntity extends BaseContainerBlockEntity {
    private NonNullList<ItemStack> items=NonNullList.withSize(2,ItemStack.EMPTY);
    private int revision;
    private ItemStack lastGear=ItemStack.EMPTY,lastMaterial=ItemStack.EMPTY;
    public InfusionBlockEntity(BlockPos p,BlockState s){super(InfusionContent.ENTITY.get(),p,s);}
    public int revision(){
        if(!ItemStack.matches(lastGear,items.get(0))||!ItemStack.matches(lastMaterial,items.get(1))){
            revision=revision==Integer.MAX_VALUE?0:revision+1;lastGear=items.get(0).copy();lastMaterial=items.get(1).copy();super.setChanged();
        }return revision;
    }
    @Override public void setChanged(){super.setChanged();revision();}
    @Override public int getContainerSize(){return 2;}
    @Override public boolean isEmpty(){return items.stream().allMatch(ItemStack::isEmpty);}
    @Override public ItemStack getItem(int i){return items.get(i);}
    @Override public ItemStack removeItem(int i,int n){var s=ContainerHelper.removeItem(items,i,n);if(!s.isEmpty())setChanged();return s;}
    @Override public ItemStack removeItemNoUpdate(int i){var s=ContainerHelper.takeItem(items,i);setChanged();return s;}
    @Override public void setItem(int i,ItemStack s){items.set(i,s);s.setCount(Math.min(s.getCount(),i==0?1:getMaxStackSize()));setChanged();}
    @Override public boolean stillValid(Player p){return level!=null&&level.getBlockEntity(worldPosition)==this&&p.distanceToSqr(worldPosition.getX()+.5,worldPosition.getY()+.5,worldPosition.getZ()+.5)<=64;}
    @Override public void clearContent(){items.clear();setChanged();}
    @Override protected Component getDefaultName(){return Component.translatable("block.dynasty.infusion_table");}
    @Override protected AbstractContainerMenu createMenu(int id,Inventory inv){return new InfusionMenu(id,inv,worldPosition);}
    @Override public void load(CompoundTag t){super.load(t);items=NonNullList.withSize(2,ItemStack.EMPTY);ContainerHelper.loadAllItems(t,items);revision=Math.max(0,t.getInt("Revision"));lastGear=items.get(0).copy();lastMaterial=items.get(1).copy();}
    @Override protected void saveAdditional(CompoundTag t){super.saveAdditional(t);ContainerHelper.saveAllItems(t,items);t.putInt("Revision",revision());}
}
