package com.dynasty.cod3;

import com.dynasty.Dynasty;
import com.dynasty.DynastyWeapons;
import net.minecraft.core.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.*;
import net.minecraft.world.*;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.entity.*;
import net.minecraft.world.level.block.state.*;
import net.minecraft.world.level.block.state.properties.*;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.*;
import net.minecraftforge.registries.*;
import java.util.*;

/** Permanent, two-block bronze memorial. Its sword is an existing captured drop, never a new reward. */
public final class RebelStatueBlock extends LootableRemains {
    public static final DirectionProperty FACING=BlockStateProperties.HORIZONTAL_FACING;
    public static final EnumProperty<DoubleBlockHalf> HALF=BlockStateProperties.DOUBLE_BLOCK_HALF;
    public static final BooleanProperty WEAPON=BooleanProperty.create("weapon");
    public static final DeferredRegister<Block> BLOCKS=DeferredRegister.create(ForgeRegistries.BLOCKS,Dynasty.MODID);
    public static final DeferredRegister<Item> ITEMS=DeferredRegister.create(ForgeRegistries.ITEMS,Dynasty.MODID);
    public static final DeferredRegister<BlockEntityType<?>> TYPES=DeferredRegister.create(ForgeRegistries.BLOCK_ENTITY_TYPES,Dynasty.MODID);
    public static final RegistryObject<Block> BLOCK=BLOCKS.register("rebel_general_statue",RebelStatueBlock::new);
    public static final RegistryObject<Item> ITEM=ITEMS.register("rebel_general_statue",()->new BlockItem(BLOCK.get(),new Item.Properties()));
    public static final RegistryObject<BlockEntityType<Statue>> TYPE=TYPES.register("rebel_general_statue",()->BlockEntityType.Builder.of(Statue::new,BLOCK.get()).build(null));
    private RebelStatueBlock(){super(Properties.copy(Blocks.COPPER_BLOCK).noOcclusion());registerDefaultState(defaultBlockState().setValue(FACING,Direction.NORTH).setValue(HALF,DoubleBlockHalf.LOWER).setValue(WEAPON,false));}
    @Override protected void createBlockStateDefinition(StateDefinition.Builder<Block,BlockState> b){b.add(FACING,HALF,WEAPON);}
    @Override public BlockEntity newBlockEntity(BlockPos pos,BlockState state){return state.getValue(HALF)==DoubleBlockHalf.LOWER?new Statue(pos,state):null;}
    @Override public VoxelShape getShape(BlockState s,BlockGetter level,BlockPos pos,CollisionContext context){
        return s.getValue(HALF)==DoubleBlockHalf.LOWER?Block.box(1,0,1,15,16,15):Block.box(2,0,2,14,8,14);
    }
    @Override public VoxelShape getCollisionShape(BlockState s,BlockGetter l,BlockPos p,CollisionContext c){return getShape(s,l,p,c);}
    @Override public BlockState rotate(BlockState s,Rotation r){return s.setValue(FACING,r.rotate(s.getValue(FACING)));}
    @Override public BlockState mirror(BlockState s,Mirror m){return rotate(s,m.getRotation(s.getValue(FACING)));}
    @Override public BlockState getStateForPlacement(BlockPlaceContext c){
        var pos=c.getClickedPos();var level=c.getLevel();
        if(pos.getY()+1>=level.getMaxBuildHeight()||!level.getBlockState(pos.above()).canBeReplaced(c))return null;
        return defaultBlockState().setValue(FACING,c.getHorizontalDirection().getOpposite());
    }
    @Override public void setPlacedBy(Level l,BlockPos p,BlockState s,LivingEntity who,ItemStack stack){l.setBlock(p.above(),s.setValue(HALF,DoubleBlockHalf.UPPER),3);}
    @Override public BlockState updateShape(BlockState s,Direction d,BlockState neighbor,LevelAccessor l,BlockPos p,BlockPos np){
        Direction other=s.getValue(HALF)==DoubleBlockHalf.LOWER?Direction.UP:Direction.DOWN;
        if(d==other&&(!neighbor.is(this)||neighbor.getValue(HALF)==s.getValue(HALF)||neighbor.getValue(FACING)!=s.getValue(FACING)))return Blocks.AIR.defaultBlockState();
        return super.updateShape(s,d,neighbor,l,p,np);
    }
    @Override public InteractionResult use(BlockState s,Level l,BlockPos p,Player who,InteractionHand hand,BlockHitResult hit){
        if(hand!=InteractionHand.MAIN_HAND)return InteractionResult.PASS;
        BlockPos base=s.getValue(HALF)==DoubleBlockHalf.LOWER?p:p.below();
        if(!(l.getBlockEntity(base) instanceof Statue statue))return InteractionResult.PASS;
        if(!l.isClientSide){
            if(!who.isShiftKeyDown()&&statue.swordSlot()>=0)statue.pullSword(who);
            else who.openMenu(statue);
        }
        return InteractionResult.sidedSuccess(l.isClientSide);
    }
    /** Bounded reward placement: refuse occupied upper blocks, and leave no partial memorial. */
    static boolean place(ServerLevel l,BlockPos p,Direction facing,List<ItemStack> drops,UUID boss){
        if(p.getY()+1>=l.getMaxBuildHeight()||!l.getBlockState(p).isAir()||!l.getBlockState(p.above()).isAir())return false;
        var state=BLOCK.get().defaultBlockState().setValue(FACING,facing);
        if(!l.setBlock(p,state,3))return false;
        if(!l.setBlock(p.above(),state.setValue(HALF,DoubleBlockHalf.UPPER),3)||!(l.getBlockEntity(p) instanceof Statue statue)){
            l.removeBlock(p,false);return false;
        }
        statue.boss=boss;
        int slot=0;for(var drop:drops){if(slot<54)statue.setItem(slot++,drop.copy());else Block.popResource(l,p,drop.copy());}
        statue.setChanged();return true;
    }
    public static final class Statue extends Remains {
        private UUID boss;
        public Statue(BlockPos p,BlockState s){super(TYPE.get(),p,s);}
        @Override protected Component getDefaultName(){return Component.translatable("block.dynasty.rebel_general_statue");}
        int swordSlot(){for(int i=0;i<getContainerSize();i++)if(getItem(i).is(DynastyWeapons.YITIAN_SWORD.get()))return i;return -1;}
        boolean pullSword(Player player){
            int slot=swordSlot();if(slot<0)return false;
            var original=getItem(slot).copy();var sword=removeItem(slot,1);
            if(!player.getInventory().add(sword)){setItem(slot,original);player.displayClientMessage(Component.translatable("cod3.dynasty.statue.inventory_full"),true);return false;}
            setChanged();player.getInventory().setChanged();
            level.playSound(null,worldPosition,SoundEvents.ARMOR_EQUIP_IRON,SoundSource.BLOCKS,1,.8f);
            player.displayClientMessage(Component.translatable("cod3.dynasty.statue.sword_pulled"),true);return true;
        }
        @Override public ItemStack removeItem(int slot,int count){var result=super.removeItem(slot,count);setChanged();return result;}
        @Override public ItemStack removeItemNoUpdate(int slot){var result=super.removeItemNoUpdate(slot);setChanged();return result;}
        @Override public void clearContent(){super.clearContent();setChanged();}
        @Override public void setChanged(){
            super.setChanged();
            if(level==null||level.isClientSide||isRemoved()||level.getBlockEntity(worldPosition)!=this)return;
            var state=level.getBlockState(worldPosition);boolean present=swordSlot()>=0;
            if(state.is(BLOCK.get())&&state.getValue(WEAPON)!=present){
                level.setBlock(worldPosition,state.setValue(WEAPON,present),3);
                var upper=level.getBlockState(worldPosition.above());
                if(upper.is(BLOCK.get())&&upper.getValue(HALF)==DoubleBlockHalf.UPPER)level.setBlock(worldPosition.above(),upper.setValue(WEAPON,present),3);
            }
        }
        @Override public void onLoad(){super.onLoad();setChanged();}
        @Override protected void saveAdditional(CompoundTag n){super.saveAdditional(n);if(boss!=null)n.putUUID("Boss",boss);}
        @Override public void load(CompoundTag n){super.load(n);boss=n.hasUUID("Boss")?n.getUUID("Boss"):null;}
    }
}
