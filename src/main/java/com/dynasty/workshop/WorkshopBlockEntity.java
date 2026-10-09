package com.dynasty.workshop;

import com.dynasty.Dynasty;
import com.dynasty.DynastyBlocks;
import com.dynasty.block.LivingWorkshopBlock;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.Connection;
import net.minecraft.network.chat.Component;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.*;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.registries.*;
import net.minecraftforge.common.capabilities.*;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.items.*;
import net.minecraftforge.items.wrapper.SidedInvWrapper;

/** One persisted transaction counter for hand, GUI and sided automation. No ticking required. */
public final class WorkshopBlockEntity extends BlockEntity implements WorldlyContainer, MenuProvider {
    public static final DeferredRegister<BlockEntityType<?>> TYPES=DeferredRegister.create(ForgeRegistries.BLOCK_ENTITY_TYPES,Dynasty.MODID);
    public static final RegistryObject<BlockEntityType<WorkshopBlockEntity>> TYPE=TYPES.register("workshop",()->BlockEntityType.Builder.of(WorkshopBlockEntity::new,
        DynastyBlocks.MARROW_VAT.get(),DynastyBlocks.ESSENCE_CONDENSER.get(),DynastyBlocks.JADE_MENDING_FORGE.get(),DynastyBlocks.VITALITY_SHRINE.get(),
        DynastyBlocks.HIDE_STRETCHER.get(),DynastyBlocks.HERBAL_BASIN.get(),DynastyBlocks.LAPIDARY_BENCH.get(),DynastyBlocks.EMBER_BRAZIER.get()).build(null));
    private int deposited;
    // The original counter remains authoritative; this bounded receipt records
    // the actual one-item payments so alternate ingredients refund correctly.
    private final java.util.List<ItemStack> paid=new java.util.ArrayList<>();
    private void completeLegacyReceipt(){while(paid.size()<deposited){var stack=recipe().next(paid.size()).stack();stack.setCount(1);paid.add(stack);}}
    private void resetPayment(){deposited=0;paid.clear();}
    private boolean processing;
    private final NonNullList<ItemStack> inventory=NonNullList.withSize(4,ItemStack.EMPTY);
    private LazyOptional<IItemHandler> input=LazyOptional.of(()->new SidedInvWrapper(this,Direction.UP));
    private LazyOptional<IItemHandler> output=LazyOptional.of(()->new SidedInvWrapper(this,Direction.DOWN));
    public final ContainerData data=new ContainerData(){
        public int get(int i){return switch(i){case 0->deposited;case 1->recipe().total();case 2->ready()?1:0;case 3->Math.min(3,deposited*3/recipe().total());default->0;};}
        public void set(int i,int v){if(i==0)deposited=v;}
        public int getCount(){return 4;}
    };
    public WorkshopBlockEntity(BlockPos p,BlockState s){super(TYPE.get(),p,s);}
    public WorkshopRecipes.Recipe recipe(){return WorkshopRecipes.get(((LivingWorkshopBlock)getBlockState().getBlock()).kind());}
    public int deposited(){return deposited;}
    public boolean ready(){return deposited==recipe().total();}
    private boolean accepts(ItemStack held){return !ready()&&recipe().accepts(deposited,held);}
    public boolean accept(ItemStack held){
        if(level==null||level.isClientSide||!accepts(held))return false;
        completeLegacyReceipt();var receipt=held.copy();receipt.setCount(1);paid.add(receipt);held.shrink(1);deposited++;
        if(ready())inventory.set(3,recipe().result());
        sync();return true;
    }
    public ItemStack collect(){
        if(level==null||level.isClientSide||!ready())return ItemStack.EMPTY;
        ItemStack result=inventory.get(3).copy();inventory.set(3,ItemStack.EMPTY);resetPayment();processInputs();sync();return result;
    }
    private void processInputs(){
        if(processing||level==null||level.isClientSide)return;
        processing=true;
        try {
            boolean advanced;
            do {advanced=false;for(int i=0;i<3&&!ready();i++)if(accepts(inventory.get(i))){accept(inventory.get(i));advanced=true;}}
            while(advanced&&!ready());
        } finally {processing=false;}
    }
    public void refund(){
        if(level==null||level.isClientSide)return;
        if(ready())net.minecraft.world.level.block.Block.popResource(level,worldPosition,inventory.get(3).copy());
        else {completeLegacyReceipt();for(var receipt:paid)net.minecraft.world.level.block.Block.popResource(level,worldPosition,receipt.copy());}
        for(int i=0;i<3;i++)net.minecraft.world.level.block.Block.popResource(level,worldPosition,inventory.get(i));
        inventory.clear();resetPayment();super.setChanged();
    }
    private void sync(){
        super.setChanged();if(level==null||level.isClientSide)return;
        var state=getBlockState();var next=state.setValue(net.minecraft.world.level.block.state.properties.BlockStateProperties.LIT,ready());
        if(!next.equals(state))level.setBlock(worldPosition,next,3);
        level.sendBlockUpdated(worldPosition,next,next,3);
    }
    @Override public void setChanged(){processInputs();sync();}
    @Override public int getContainerSize(){return 4;}
    @Override public boolean isEmpty(){return inventory.stream().allMatch(ItemStack::isEmpty);}
    @Override public ItemStack getItem(int slot){return inventory.get(slot);}
    @Override public void setItem(int slot,ItemStack stack){inventory.set(slot,stack);if(slot==3)outputTaken();setChanged();}
    public void outputTaken(){if(ready()&&inventory.get(3).isEmpty()){resetPayment();processInputs();sync();}}
    @Override public ItemStack removeItem(int slot,int amount){
        var result=ContainerHelper.removeItem(inventory,slot,amount);
        if(slot==3&&inventory.get(3).isEmpty()&&!result.isEmpty())resetPayment();
        setChanged();return result;
    }
    @Override public ItemStack removeItemNoUpdate(int slot){return removeItem(slot,getItem(slot).getCount());}
    @Override public void clearContent(){inventory.clear();resetPayment();sync();}
    @Override public boolean stillValid(Player p){return level!=null&&level.getBlockEntity(worldPosition)==this&&p.distanceToSqr(worldPosition.getX()+.5,worldPosition.getY()+.5,worldPosition.getZ()+.5)<=64;}
    @Override public boolean canPlaceItem(int slot,ItemStack stack){return slot<3&&accepts(stack);}
    @Override public int[] getSlotsForFace(Direction side){return side==Direction.DOWN?new int[]{3}:new int[]{0,1,2};}
    @Override public boolean canPlaceItemThroughFace(int slot,ItemStack stack,Direction side){return side!=Direction.DOWN&&canPlaceItem(slot,stack);}
    @Override public boolean canTakeItemThroughFace(int slot,ItemStack stack,Direction side){return side==Direction.DOWN&&slot==3;}
    @Override public Component getDisplayName(){return getBlockState().getBlock().getName();}
    @Override public AbstractContainerMenu createMenu(int id,Inventory inv,Player p){return new WorkshopMenu(id,inv,this,data);}
    @Override public <T> LazyOptional<T> getCapability(Capability<T> cap,Direction side){
        if(cap==ForgeCapabilities.ITEM_HANDLER&&side!=null&&!isRemoved())return (side==Direction.DOWN?output:input).cast();
        return super.getCapability(cap,side);
    }
    @Override public void invalidateCaps(){super.invalidateCaps();input.invalidate();output.invalidate();}
    @Override public void reviveCaps(){super.reviveCaps();input=LazyOptional.of(()->new SidedInvWrapper(this,Direction.UP));output=LazyOptional.of(()->new SidedInvWrapper(this,Direction.DOWN));}
    @Override protected void saveAdditional(CompoundTag tag){super.saveAdditional(tag);tag.putInt("Deposited",deposited);tag.putString("Recipe",recipe().output());ContainerHelper.saveAllItems(tag,inventory);
        completeLegacyReceipt();var receipts=new net.minecraft.nbt.ListTag();for(var stack:paid)receipts.add(stack.save(new CompoundTag()));tag.put("Paid",receipts);}
    @Override public void load(CompoundTag tag){
        super.load(tag);deposited=tag.getString("Recipe").equals(recipe().output())?Math.max(0,Math.min(recipe().total(),tag.getInt("Deposited"))):0;
        paid.clear();var receipts=tag.getList("Paid",net.minecraft.nbt.Tag.TAG_COMPOUND);
        for(int i=0;i<Math.min(deposited,receipts.size());i++){
            var receipt=ItemStack.of(receipts.getCompound(i));
            if(receipt.getCount()!=1||!recipe().accepts(i,receipt)){paid.clear();break;}
            paid.add(receipt);
        }
        completeLegacyReceipt();
        inventory.clear();ContainerHelper.loadAllItems(tag,inventory);
        // Old saves have only Deposited. New saves may have a partially extracted output.
        if(ready()&&!tag.contains("Items"))inventory.set(3,recipe().result());
    }
    @Override public CompoundTag getUpdateTag(){return saveWithoutMetadata();}
    @Override public ClientboundBlockEntityDataPacket getUpdatePacket(){return ClientboundBlockEntityDataPacket.create(this);}
    @Override public void onDataPacket(Connection c,ClientboundBlockEntityDataPacket p){if(p.getTag()!=null)load(p.getTag());}
    @Override public void handleUpdateTag(CompoundTag t){load(t);}
}
