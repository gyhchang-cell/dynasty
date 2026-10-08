package com.dynasty.workshop;

import com.dynasty.Dynasty;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.player.*;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.common.extensions.IForgeMenuType;
import net.minecraftforge.registries.*;

public final class WorkshopMenu extends AbstractContainerMenu {
    public static final DeferredRegister<MenuType<?>> MENUS=DeferredRegister.create(ForgeRegistries.MENU_TYPES,Dynasty.MODID);
    public static final RegistryObject<MenuType<WorkshopMenu>> TYPE=MENUS.register("workshop",()->IForgeMenuType.create(WorkshopMenu::new));
    public final WorkshopBlockEntity station;
    private final ContainerData data;
    public WorkshopMenu(int id,Inventory inv,net.minecraft.network.FriendlyByteBuf buf){this(id,inv,require(inv,buf.readBlockPos()),new SimpleContainerData(4));}
    private static WorkshopBlockEntity require(Inventory inv,BlockPos p){
        if(inv.player.level().getBlockEntity(p) instanceof WorkshopBlockEntity be)return be;
        throw new IllegalArgumentException("Missing workshop at "+p);
    }
    public WorkshopMenu(int id,Inventory inv,WorkshopBlockEntity station,ContainerData data){
        super(TYPE.get(),id);this.station=station;this.data=data;
        for(int i=0;i<3;i++)addSlot(new Slot(station,i,30+i*22,22){@Override public boolean mayPlace(ItemStack s){return station.canPlaceItem(getContainerSlot(),s);}});
        addSlot(new Slot(station,3,124,22){@Override public boolean mayPlace(ItemStack s){return false;}});
        for(int row=0;row<3;row++)for(int col=0;col<9;col++)addSlot(new Slot(inv,9+row*9+col,8+col*18,84+row*18));
        for(int col=0;col<9;col++)addSlot(new Slot(inv,col,8+col*18,142));
        addDataSlots(data);
    }
    public int deposited(){return data.get(0);}
    public int total(){return Math.max(1,data.get(1));}
    @Override public boolean stillValid(Player p){return station.stillValid(p);}
    @Override public ItemStack quickMoveStack(Player p,int index){
        if(index<0||index>=slots.size())return ItemStack.EMPTY;
        Slot slot=slots.get(index);if(!slot.hasItem())return ItemStack.EMPTY;
        ItemStack stack=slot.getItem(),copy=stack.copy();
        if(index<4){if(!moveItemStackTo(stack,4,40,true))return ItemStack.EMPTY;}
        else if(!moveItemStackTo(stack,0,3,false))return ItemStack.EMPTY;
        if(stack.isEmpty())slot.set(ItemStack.EMPTY);else slot.setChanged();
        // Output extraction through vanilla Slot mutates the stack before setItem.
        if(index==3&&stack.isEmpty())station.outputTaken();
        slot.onTake(p,stack);return copy;
    }
}
