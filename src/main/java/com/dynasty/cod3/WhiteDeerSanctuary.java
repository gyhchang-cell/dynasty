package com.dynasty.cod3;

import net.minecraft.core.*;
import net.minecraft.core.registries.Registries;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.*;
import net.minecraft.server.level.*;
import net.minecraft.world.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.saveddata.SavedData;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** A real, separately saved bamboo grotto. Access and the return point are personal. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class WhiteDeerSanctuary {
    private static final String RETURN="cod3_white_deer_return";
    public static ItemStack reward(ServerPlayer p){var item=new ItemStack(WhiteDeerContent.TOKEN.get());item.getOrCreateTag().putUUID("Owner",p.getUUID());return item;}
    public static boolean available(ServerPlayer p){return p.server.getLevel(WhiteDeerContent.SANCTUARY)!=null;}
    public static boolean enter(ServerPlayer p){
        if(!WhiteDeerTrail.claimed(p)||!available(p)||!p.isAlive()||p.isPassenger())return false;
        if(p.level().dimension()==WhiteDeerContent.SANCTUARY)return leave(p);
        var target=p.server.getLevel(WhiteDeerContent.SANCTUARY);build(target);
        var at=safe(target,new BlockPos(8,64,8));if(at==null)return false;
        var n=new CompoundTag();n.putString("Dimension",p.level().dimension().location().toString());n.putDouble("X",p.getX());n.putDouble("Y",p.getY());n.putDouble("Z",p.getZ());n.putFloat("Yaw",p.getYRot());n.putFloat("Pitch",p.getXRot());
        p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).put(RETURN,n);
        WhiteDeerTrail.reset(p);p.teleportTo(target,at.x,at.y,at.z,180,0);p.setDeltaMovement(Vec3.ZERO);p.fallDistance=0;
        p.displayClientMessage(Component.translatable("cod3.dynasty.deer.enter"),false);return true;
    }
    public static boolean leave(ServerPlayer p){
        var n=p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).getCompound(RETURN);
        var id=ResourceLocation.tryParse(n.getString("Dimension"));var target=id==null?null:p.server.getLevel(ResourceKey.create(Registries.DIMENSION,id));
        if(target==null||target.dimension()==WhiteDeerContent.SANCTUARY)target=p.server.overworld();
        var origin=n.contains("X")?BlockPos.containing(n.getDouble("X"),n.getDouble("Y"),n.getDouble("Z")):target.getSharedSpawnPos();
        target.getChunkAt(origin);var at=safe(target,origin);
        if(at==null){var spawn=target.getSharedSpawnPos();target.getChunkAt(spawn);at=safe(target,target.getHeightmapPos(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES,spawn));}
        if(at==null){p.displayClientMessage(Component.translatable("cod3.dynasty.deer.return_blocked"),true);return false;}
        p.teleportTo(target,at.x,at.y,at.z,n.getFloat("Yaw"),n.getFloat("Pitch"));p.setDeltaMovement(Vec3.ZERO);p.fallDistance=0;
        p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).remove(RETURN);return true;
    }
    private static Vec3 safe(ServerLevel l,BlockPos origin){
        for(int radius=0;radius<=4;radius++)for(int dx=-radius;dx<=radius;dx++)for(int dz=-radius;dz<=radius;dz++){
            if(Math.max(Math.abs(dx),Math.abs(dz))!=radius)continue;
            for(int dy=0;dy<=4;dy++){
                var at=origin.offset(dx,dy,dz);if(!l.hasChunkAt(at)||!l.getWorldBorder().isWithinBounds(at))continue;
                if(l.getBlockState(at.below()).isFaceSturdy(l,at.below(),Direction.UP)&&l.getBlockState(at).getCollisionShape(l,at).isEmpty()&&l.getBlockState(at.above()).getCollisionShape(l,at.above()).isEmpty()
                        &&l.getFluidState(at).isEmpty()&&l.getFluidState(at.above()).isEmpty()&&!l.getBlockState(at).is(Blocks.FIRE)&&!l.getBlockState(at.below()).is(Blocks.MAGMA_BLOCK))return new Vec3(at.getX()+.5,at.getY(),at.getZ()+.5);
            }
        }return null;
    }
    public static final class Garden extends SavedData {
        private boolean built;
        public static Garden get(ServerLevel l){return l.getDataStorage().computeIfAbsent(n->{var d=new Garden();d.built=n.getBoolean("Built");return d;},Garden::new,"dynasty_white_deer_garden");}
        public CompoundTag save(CompoundTag n){n.putBoolean("Built",built);return n;}
    }
    public static void build(ServerLevel l){
        if(l.dimension()!=WhiteDeerContent.SANCTUARY)throw new IllegalArgumentException("Garden belongs to its own dimension");
        var data=Garden.get(l);if(data.built)return;l.getChunk(0,0);
        for(int x=0;x<16;x++)for(int z=0;z<16;z++){
            l.setBlock(new BlockPos(x,62,z),Blocks.STONE.defaultBlockState(),2);l.setBlock(new BlockPos(x,63,z),Blocks.MOSS_BLOCK.defaultBlockState(),2);
            if(x==0||z==0||x==15||z==15)for(int y=64;y<70+((x+z)%3);y++)l.setBlock(new BlockPos(x,y,z),Blocks.MOSSY_COBBLESTONE.defaultBlockState(),2);
            if(x<3||x>12||z<3||z>12)l.setBlock(new BlockPos(x,71,z),Blocks.AZALEA_LEAVES.defaultBlockState().setValue(LeavesBlock.PERSISTENT,true),2);
        }
        for(int x:new int[]{3,12})for(int z:new int[]{3,7,12}){
            l.setBlock(new BlockPos(x,63,z),Blocks.GRASS_BLOCK.defaultBlockState(),2);
            for(int y=64;y<=68;y++)l.setBlock(new BlockPos(x,y,z),Blocks.BAMBOO.defaultBlockState().setValue(BambooStalkBlock.AGE,1).setValue(BambooStalkBlock.LEAVES,y==68?net.minecraft.world.level.block.state.properties.BambooLeaves.LARGE:net.minecraft.world.level.block.state.properties.BambooLeaves.SMALL),2);
        }
        for(int x=5;x<=7;x++)for(int z=10;z<=12;z++){l.setBlock(new BlockPos(x,63,z),Blocks.WATER.defaultBlockState(),2);l.setBlock(new BlockPos(x,62,z),Blocks.CLAY.defaultBlockState(),2);}
        for(int x:new int[]{5,10})l.setBlock(new BlockPos(x,64,5),Blocks.LANTERN.defaultBlockState(),2);
        l.setBlock(new BlockPos(10,64,10),Blocks.FLOWERING_AZALEA.defaultBlockState(),2);
        l.setBlock(new BlockPos(8,64,12),Blocks.CHISELED_STONE_BRICKS.defaultBlockState(),2);
        l.setBlock(new BlockPos(8,65,12),Blocks.BELL.defaultBlockState().setValue(BlockStateProperties.HORIZONTAL_FACING,Direction.NORTH),2);
        data.built=true;data.setDirty();
    }
    public static final class Pass extends Item {
        public Pass(Properties p){super(p);}
        @Override public InteractionResultHolder<ItemStack> use(Level l,Player p,InteractionHand hand){
            var stack=p.getItemInHand(hand);if(!l.isClientSide&&p instanceof ServerPlayer sp){
                if(!stack.hasTag()||!stack.getTag().hasUUID("Owner")||!stack.getTag().getUUID("Owner").equals(p.getUUID())||!enter(sp)){p.displayClientMessage(Component.translatable("cod3.dynasty.deer.locked"),true);return InteractionResultHolder.fail(stack);}
            }return InteractionResultHolder.sidedSuccess(stack,l.isClientSide);
        }
    }
    @SubscribeEvent public static void returnBell(PlayerInteractEvent.RightClickBlock e){
        if(e.getEntity() instanceof ServerPlayer p&&p.level().dimension()==WhiteDeerContent.SANCTUARY&&e.getPos().equals(new BlockPos(8,65,12))&&p.level().getBlockState(e.getPos()).is(Blocks.BELL)&&WhiteDeerTrail.claimed(p)){
            e.setCanceled(true);e.setCancellationResult(leave(p)?InteractionResult.SUCCESS:InteractionResult.FAIL);
        }
    }
    private WhiteDeerSanctuary(){}
}
