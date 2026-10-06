package com.dynasty.infusion;

import net.minecraft.core.BlockPos;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.*;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.ItemStack;
import net.minecraft.sounds.*;
import com.dynasty.DynastyAdvancements;

/** Container-owned input; closing/breaking/out-of-range returns stacks. Ghost preview is never a slot. */
public final class InfusionMenu extends AbstractContainerMenu {
    private final SimpleContainer input=new SimpleContainer(2);
    private final ContainerLevelAccess access;
    private final Player owner;
    private final ContainerData data=new SimpleContainerData(2);
    public InfusionMenu(int id,Inventory inv,BlockPos pos){
        super(InfusionContent.MENU.get(),id);owner=inv.player;
        access=ContainerLevelAccess.create(owner.level(),pos);
        addSlot(new Slot(input,0,20,40){@Override public boolean mayPlace(ItemStack s){return InfusionTraits.eligible(s);}@Override public int getMaxStackSize(){return 1;}});
        addSlot(new Slot(input,1,70,40){@Override public boolean mayPlace(ItemStack s){return InfusionTraits.material(s)!=null;}});
        for(int row=0;row<3;row++)for(int col=0;col<9;col++)addSlot(new Slot(inv,col+row*9+9,8+col*18,154+row*18));
        for(int col=0;col<9;col++)addSlot(new Slot(inv,col,8+col*18,212));
        addDataSlots(data);
    }
    public int selected(){return data.get(0);}
    public int status(){return data.get(1);}
    public ItemStack gear(){return input.getItem(0);}
    public ItemStack material(){return input.getItem(1);}
    public ItemStack preview(boolean remove){return InfusionTraits.preview(gear(),InfusionTraits.material(material()),selected(),remove);}
    // 0 ready; 1 base progression; 2 material progression; 3 invalid/conflict; 4 material; 5 XP.
    public int check(boolean remove){
        if(!InfusionTraits.unlocked(owner,"get_jade"))return 1;
        var trait=InfusionTraits.material(material());
        if(!remove&&trait!=null&&!InfusionTraits.unlocked(owner,trait.gate()))return 2;
        if(preview(remove).isEmpty())return 3;
        if(!remove&&material().getCount()<InfusionTraits.MATERIAL_COST)return 4;
        if(!owner.isCreative()&&owner.experienceLevel<(remove?1:InfusionTraits.XP_COST))return 5;
        return 0;
    }
    @Override public void broadcastChanges(){if(!owner.level().isClientSide)data.set(1,check(false));super.broadcastChanges();}
    @Override public boolean clickMenuButton(Player p,int button){
        if(p!=owner||p.level().isClientSide||!stillValid(p))return false;
        if(button>=0&&button<3){data.set(0,button);broadcastChanges();return true;}
        if(button!=3&&button!=4)return false;
        boolean remove=button==4;int status=check(remove);data.set(1,status);if(status!=0){broadcastChanges();return false;}
        ItemStack result=preview(remove); // Server recomputes; no client-supplied stack/NBT.
        if(!p.isCreative()){p.giveExperienceLevels(-(remove?1:InfusionTraits.XP_COST));if(!remove)material().shrink(InfusionTraits.MATERIAL_COST);}
        input.setItem(0,result);input.setChanged();
        if(!remove&&p instanceof net.minecraft.server.level.ServerPlayer sp)DynastyAdvancements.award(sp,"first_infusion");
        access.execute((world,pos)->world.playSound(null,pos,SoundEvents.ENCHANTMENT_TABLE_USE,SoundSource.BLOCKS,.7f,1f));
        broadcastChanges();return true;
    }
    @Override public boolean stillValid(Player p){return stillValid(access,p,InfusionContent.TABLE.get());}
    @Override public void removed(Player p){super.removed(p);if(!p.level().isClientSide)clearContainer(p,input);}
    @Override public ItemStack quickMoveStack(Player p,int index){
        if(index<0||index>=slots.size())return ItemStack.EMPTY;
        var slot=slots.get(index);if(!slot.hasItem())return ItemStack.EMPTY;
        var stack=slot.getItem();var copy=stack.copy();
        if(index<2){if(!moveItemStackTo(stack,2,38,true))return ItemStack.EMPTY;}
        else if(InfusionTraits.eligible(stack)){if(!moveItemStackTo(stack,0,1,false))return ItemStack.EMPTY;}
        else if(InfusionTraits.material(stack)!=null){if(!moveItemStackTo(stack,1,2,false))return ItemStack.EMPTY;}
        else return ItemStack.EMPTY;
        if(stack.isEmpty())slot.set(ItemStack.EMPTY);else slot.setChanged();slot.onTake(p,stack);return copy;
    }
}
