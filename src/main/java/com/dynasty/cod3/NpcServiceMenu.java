package com.dynasty.cod3;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.*;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.ItemStack;

/** Three real slots. Payment precedes output; closing or switching returns every remaining item. */
public final class NpcServiceMenu extends AbstractContainerMenu {
    private final DynastyNpcEntity npc;
    private final Player owner;
    private final SimpleContainer items=new SimpleContainer(3);
    private final ContainerData data=new SimpleContainerData(2);
    public NpcServiceMenu(int id,Inventory inv,FriendlyByteBuf buf){this(id,inv,find(inv,buf.readInt()),buf.readUnsignedByte());}
    private static DynastyNpcEntity find(Inventory inv,int id){return inv.player.level().getEntity(id) instanceof DynastyNpcEntity npc?npc:null;}
    public NpcServiceMenu(int id,Inventory inv,DynastyNpcEntity npc,int page){
        super(NpcTrading.SERVICE.get(),id);this.npc=npc;owner=inv.player;data.set(0,page==2?2:1);
        addSlot(new Slot(items,0,65,43){@Override public boolean mayPlace(ItemStack s){return s.isDamageableItem();}@Override public int getMaxStackSize(){return 1;}});
        addSlot(new Slot(items,1,119,43){@Override public boolean mayPlace(ItemStack s){return s.is(com.dynasty.expansion.ExpansionContent.item("copper_coin"));}});
        addSlot(new Slot(items,2,195,43){@Override public boolean mayPlace(ItemStack s){return false;}});
        for(int row=0;row<3;row++)for(int col=0;col<9;col++)addSlot(new Slot(inv,9+row*9+col,57+col*18,111+row*18));
        for(int col=0;col<9;col++)addSlot(new Slot(inv,col,57+col*18,169));
        addDataSlots(data);
    }
    public int page(){return data.get(0);}
    public int cost(){return page()==1?NpcEquipmentService.REPAIR_COST:NpcEquipmentService.ENCHANT_COST;}
    public int status(){return data.get(1);}
    private int check(){
        var gear=items.getItem(0);var coins=items.getItem(1);
        if(!items.getItem(2).isEmpty())return 4;
        if(gear.getCount()!=1||!gear.isDamageableItem())return 1;
        if(page()==1?!gear.isDamaged():NpcEquipmentService.candidates(gear).isEmpty())return page()==1?2:3;
        if(!coins.is(com.dynasty.expansion.ExpansionContent.item("copper_coin"))||coins.getCount()<cost())return 5;
        return 0;
    }
    @Override public void broadcastChanges(){if(!owner.level().isClientSide)data.set(1,check());super.broadcastChanges();}
    @Override public boolean stillValid(Player p){return p==owner&&(p.level().isClientSide||npc!=null&&npc.getTradingPlayer()==p&&npc.canTrade(p));}
    @Override public boolean clickMenuButton(Player p,int button){
        if(!(p instanceof ServerPlayer server)||p.containerMenu!=this||!stillValid(p))return false;
        if(button==0)return NpcTrading.open(server,npc,0);
        if(button==3)return NpcTrading.dialogue(server,npc);
        if(button==1||button==2){data.set(0,button);broadcastChanges();return true;}
        if(button!=20||check()!=0)return false;
        ItemStack output=page()==1?NpcEquipmentService.repair(items.getItem(0)):NpcEquipmentService.enchant(items.getItem(0),p.getRandom());
        if(output.isEmpty())return false;
        items.removeItem(0,1);items.removeItem(1,cost());items.setItem(2,output);items.setChanged();
        npc.beginConversation(p);broadcastChanges();return true;
    }
    @Override public void removed(Player p){
        super.removed(p);if(!p.level().isClientSide){clearContainer(p,items);if(npc!=null&&npc.getTradingPlayer()==p)npc.setTradingPlayer(null);}
    }
    @Override public ItemStack quickMoveStack(Player p,int index){
        if(index<0||index>=slots.size())return ItemStack.EMPTY;
        var slot=slots.get(index);if(!slot.hasItem())return ItemStack.EMPTY;
        var stack=slot.getItem();var original=stack.copy();
        if(index<3){if(!moveItemStackTo(stack,3,39,true))return ItemStack.EMPTY;}
        else if(stack.is(com.dynasty.expansion.ExpansionContent.item("copper_coin"))){if(!moveItemStackTo(stack,1,2,false))return ItemStack.EMPTY;}
        else if(stack.isDamageableItem()){if(!moveItemStackTo(stack,0,1,false))return ItemStack.EMPTY;}
        else if(index<30){if(!moveItemStackTo(stack,30,39,false))return ItemStack.EMPTY;}
        else if(!moveItemStackTo(stack,3,30,false))return ItemStack.EMPTY;
        if(stack.isEmpty())slot.set(ItemStack.EMPTY);else slot.setChanged();slot.onTake(p,stack);broadcastChanges();return original;
    }
}
