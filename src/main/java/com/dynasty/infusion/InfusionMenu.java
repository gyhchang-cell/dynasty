package com.dynasty.infusion;

import net.minecraft.core.BlockPos;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.*;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.ItemStack;
import net.minecraft.sounds.*;
import net.minecraft.core.particles.ParticleTypes;
import com.dynasty.DynastyAdvancements;

/** Server-authoritative transaction over shared persistent inputs and an untakeable ghost preview. */
public final class InfusionMenu extends AbstractContainerMenu {
    private final Container input;
    private final InfusionBlockEntity entity;
    private final ContainerLevelAccess access;
    private final Player owner;
    private final ContainerData data=new SimpleContainerData(5);
    public InfusionMenu(int id,Inventory inv,BlockPos pos){
        super(InfusionContent.MENU.get(),id);owner=inv.player;access=ContainerLevelAccess.create(owner.level(),pos);
        entity=owner.level().getBlockEntity(pos) instanceof InfusionBlockEntity be?be:null;
        input=entity==null?new SimpleContainer(2):entity;data.set(0,-1);
        addSlot(new Slot(input,0,26,31){@Override public boolean mayPlace(ItemStack s){return InfusionTraits.eligible(s);}@Override public int getMaxStackSize(){return 1;}});
        addSlot(new Slot(input,1,80,31){@Override public boolean mayPlace(ItemStack s){return InfusionTraits.material(s)!=null;}});
        for(int row=0;row<3;row++)for(int col=0;col<9;col++)addSlot(new Slot(inv,col+row*9+9,8+col*18,120+row*18));
        for(int col=0;col<9;col++)addSlot(new Slot(inv,col,8+col*18,178));addDataSlots(data);
    }
    public int selected(){return data.get(0);}
    public int targetSlot(){return selected()<0?InfusionTraits.automaticSlot(gear()):selected();}
    public int status(){return data.get(1);}
    public int removeStatus(){return data.get(4);}
    public int revision(){return(data.get(2)&65535)|((data.get(3)&32767)<<16);}
    public ItemStack gear(){return input.getItem(0);}
    public ItemStack material(){return input.getItem(1);}
    public ItemStack preview(boolean remove){return InfusionTraits.preview(gear(),InfusionTraits.material(material()),remove?selected():targetSlot(),remove);}
    public int check(boolean remove){
        var trait=InfusionTraits.material(material());int problem=InfusionTraits.problem(gear(),trait,remove?selected():targetSlot(),remove);if(problem!=0)return problem;
        if(!InfusionTraits.unlocked(owner,"get_jade"))return 1;if(!remove&&!InfusionTraits.unlocked(owner,trait.gate()))return 2;
        if(!remove&&material().getCount()<trait.count())return 4;
        if(!owner.isCreative()&&owner.experienceLevel<(remove?1:InfusionTraits.XP_COST))return 5;return 0;
    }
    @Override public void broadcastChanges(){
        if(!owner.level().isClientSide){data.set(1,check(false));data.set(4,check(true));int rev=entity==null?0:entity.revision();data.set(2,rev&65535);data.set(3,rev>>>16);}super.broadcastChanges();
    }
    /** action 0 apply, 1 remove, 2 select; negative slot means automatic placement. */
    public boolean request(Player p,int action,int slot,int expectedRevision){
        if(p!=owner||p.containerMenu!=this||p.level().isClientSide||entity==null||!stillValid(p)||entity.isRemoved())return false;
        if(slot< -1||slot>=3||action<0||action>2)return false;
        if(entity.revision()!=expectedRevision){p.displayClientMessage(net.minecraft.network.chat.Component.translatable("infusion.dynasty.error.13"),true);broadcastChanges();return false;}
        data.set(0,slot);if(action==2){broadcastChanges();return true;}
        boolean remove=action==1;int status=check(remove);if(status!=0){broadcastChanges();return false;}
        var trait=InfusionTraits.material(material());var result=preview(remove);if(result.isEmpty())return false;
        if(!p.isCreative()){p.giveExperienceLevels(-(remove?1:InfusionTraits.XP_COST));if(!remove)material().shrink(trait.count());}
        input.setItem(0,result);input.setChanged();data.set(0,-1);
        if(!remove&&p instanceof net.minecraft.server.level.ServerPlayer sp)DynastyAdvancements.award(sp,"first_infusion");
        access.execute((world,pos)->{world.playSound(null,pos,SoundEvents.AMETHYST_BLOCK_CHIME,SoundSource.BLOCKS,.6f,1.1f);if(world instanceof net.minecraft.server.level.ServerLevel server)server.sendParticles(ParticleTypes.ENCHANT,pos.getX()+.5,pos.getY()+1,pos.getZ()+.5,8,.18,.08,.18,.01);});
        broadcastChanges();return true;
    }
    @Override public boolean clickMenuButton(Player p,int button){return false;}
    @Override public boolean stillValid(Player p){return entity!=null&&!entity.isRemoved()&&entity.stillValid(p)&&stillValid(access,p,InfusionContent.TABLE.get());}
    @Override public ItemStack quickMoveStack(Player p,int index){
        if(index<0||index>=slots.size())return ItemStack.EMPTY;var slot=slots.get(index);if(!slot.hasItem())return ItemStack.EMPTY;
        var stack=slot.getItem();var copy=stack.copy();
        if(index<2){if(!moveItemStackTo(stack,2,38,true))return ItemStack.EMPTY;}
        else if(InfusionTraits.eligible(stack)){if(!moveItemStackTo(stack,0,1,false))return ItemStack.EMPTY;}
        else if(InfusionTraits.material(stack)!=null){if(!moveItemStackTo(stack,1,2,false))return ItemStack.EMPTY;}
        else if(index<29){if(!moveItemStackTo(stack,29,38,false))return ItemStack.EMPTY;}
        else if(!moveItemStackTo(stack,2,29,false))return ItemStack.EMPTY;
        if(stack.isEmpty())slot.set(ItemStack.EMPTY);else slot.setChanged();slot.onTake(p,stack);return copy;
    }
}
