package com.dynasty.workshop;

import com.dynasty.Dynasty;
import com.dynasty.DynastyBlocks;
import com.dynasty.block.LivingWorkshopBlock;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.Connection;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.registries.*;

/** Ordered recipe: one durable counter describes every accepted ingredient exactly. */
public final class WorkshopBlockEntity extends BlockEntity {
    public static final DeferredRegister<BlockEntityType<?>> TYPES=DeferredRegister.create(ForgeRegistries.BLOCK_ENTITY_TYPES,Dynasty.MODID);
    public static final RegistryObject<BlockEntityType<WorkshopBlockEntity>> TYPE=TYPES.register("workshop",()->BlockEntityType.Builder.of(WorkshopBlockEntity::new,
        DynastyBlocks.MARROW_VAT.get(),DynastyBlocks.ESSENCE_CONDENSER.get(),DynastyBlocks.JADE_MENDING_FORGE.get(),DynastyBlocks.VITALITY_SHRINE.get(),
        DynastyBlocks.HIDE_STRETCHER.get(),DynastyBlocks.HERBAL_BASIN.get(),DynastyBlocks.LAPIDARY_BENCH.get(),DynastyBlocks.EMBER_BRAZIER.get()).build(null));
    private int deposited;
    public WorkshopBlockEntity(BlockPos p,BlockState s){super(TYPE.get(),p,s);}
    public WorkshopRecipes.Recipe recipe(){return WorkshopRecipes.get(((LivingWorkshopBlock)getBlockState().getBlock()).kind());}
    public int deposited(){return deposited;}
    public boolean ready(){return deposited==recipe().total();}
    public boolean accept(ItemStack held){
        if(level==null||level.isClientSide||ready())return false;
        var next=recipe().next(deposited);
        if(next==null||held.isEmpty()||!held.is(next.stack().getItem()))return false;
        held.shrink(1);deposited++;sync();return true;
    }
    public ItemStack collect(){
        if(level==null||level.isClientSide||!ready())return ItemStack.EMPTY;
        ItemStack result=recipe().result();deposited=0;sync();return result;
    }
    public void refund(){
        if(level==null||level.isClientSide)return;
        if(ready())net.minecraft.world.level.block.Block.popResource(level,worldPosition,recipe().result());
        else {int remaining=deposited;for(var cost:recipe().costs()){
            int n=Math.min(remaining,cost.count());if(n>0){var item=cost.stack();item.setCount(n);net.minecraft.world.level.block.Block.popResource(level,worldPosition,item);}remaining-=n;
        }}
        deposited=0;setChanged();
    }
    private void sync(){
        setChanged();if(level==null)return;
        var state=getBlockState();var next=state.setValue(net.minecraft.world.level.block.state.properties.BlockStateProperties.LIT,ready());
        if(!next.equals(state))level.setBlock(worldPosition,next,3);
        level.sendBlockUpdated(worldPosition,next,next,3);
    }
    @Override protected void saveAdditional(CompoundTag tag){super.saveAdditional(tag);tag.putInt("Deposited",deposited);tag.putString("Recipe",recipe().output());}
    @Override public void load(CompoundTag tag){super.load(tag);deposited=tag.getString("Recipe").equals(recipe().output())?Math.max(0,Math.min(recipe().total(),tag.getInt("Deposited"))):0;}
    @Override public CompoundTag getUpdateTag(){return saveWithoutMetadata();}
    @Override public ClientboundBlockEntityDataPacket getUpdatePacket(){return ClientboundBlockEntityDataPacket.create(this);}
    @Override public void onDataPacket(Connection c,ClientboundBlockEntityDataPacket p){if(p.getTag()!=null)load(p.getTag());}
    @Override public void handleUpdateTag(CompoundTag t){load(t);}
}
