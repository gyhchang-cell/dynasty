package com.dynasty.cod3;

import com.dynasty.Dynasty;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.*;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.entity.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.registries.*;

/** Permanent loot container. No dead entity or immortal ItemEntity remains in the world. */
public final class LootableRemains extends BaseEntityBlock {
    public static final DeferredRegister<Block> BLOCKS=DeferredRegister.create(ForgeRegistries.BLOCKS,Dynasty.MODID);
    public static final DeferredRegister<Item> ITEMS=DeferredRegister.create(ForgeRegistries.ITEMS,Dynasty.MODID);
    public static final DeferredRegister<BlockEntityType<?>> TYPES=DeferredRegister.create(ForgeRegistries.BLOCK_ENTITY_TYPES,Dynasty.MODID);
    public static final RegistryObject<Block> BLOCK=BLOCKS.register("lootable_remains",LootableRemains::new);
    public static final RegistryObject<Item> ITEM=ITEMS.register("lootable_remains",()->new BlockItem(BLOCK.get(),new Item.Properties()));
    public static final RegistryObject<BlockEntityType<Remains>> TYPE=TYPES.register("lootable_remains",()->BlockEntityType.Builder.of(Remains::new,BLOCK.get()).build(null));
    public LootableRemains(){super(Properties.copy(Blocks.BARREL).noOcclusion());}
    @Override public RenderShape getRenderShape(BlockState s){return RenderShape.MODEL;}
    @Override public BlockEntity newBlockEntity(BlockPos p,BlockState s){return new Remains(p,s);}
    @Override public InteractionResult use(BlockState s,Level l,BlockPos p,Player who,InteractionHand hand,BlockHitResult hit){
        if(l.getBlockEntity(p) instanceof Remains remains){if(!l.isClientSide)who.openMenu(remains);return InteractionResult.sidedSuccess(l.isClientSide);}
        return InteractionResult.PASS;
    }
    @Override public void onRemove(BlockState s,Level l,BlockPos p,BlockState next,boolean moving){if(!s.is(next.getBlock())&&l.getBlockEntity(p) instanceof Remains r)Containers.dropContents(l,p,r);super.onRemove(s,l,p,next,moving);}
    public static final class Remains extends RandomizableContainerBlockEntity {
        private NonNullList<ItemStack> items=NonNullList.withSize(54,ItemStack.EMPTY);
        public Remains(BlockPos p,BlockState s){super(TYPE.get(),p,s);}
        @Override public int getContainerSize(){return 54;}
        @Override protected Component getDefaultName(){return Component.translatable("block.dynasty.lootable_remains");}
        @Override protected AbstractContainerMenu createMenu(int id,Inventory inv){return ChestMenu.sixRows(id,inv,this);}
        @Override protected NonNullList<ItemStack> getItems(){return items;}
        @Override protected void setItems(NonNullList<ItemStack> list){items=list;}
        @Override protected void saveAdditional(CompoundTag tag){super.saveAdditional(tag);ContainerHelper.saveAllItems(tag,items);}
        @Override public void load(CompoundTag tag){super.load(tag);items=NonNullList.withSize(54,ItemStack.EMPTY);ContainerHelper.loadAllItems(tag,items);}
        @Override public boolean canPlaceItem(int slot,ItemStack s){return false;}
    }
}
