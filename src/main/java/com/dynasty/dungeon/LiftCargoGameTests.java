package com.dynasty.dungeon;

import com.dynasty.expansion.ExpansionContent;
import com.mojang.authlib.GameProfile;
import java.util.*;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class LiftCargoGameTests {
    private record Fixture(BlockPos core,BlockPos stele,BlockPos lift,BlockPos exit,UUID instance,DungeonMechanismBlockEntity elevator,ServerPlayer player){}
    private static Fixture fixture(GameTestHelper h){
        for(int x=0;x<=14;x++)for(int z=0;z<=14;z++)for(int y=1;y<=5;y++)h.setBlock(x,y,z,y==1?Blocks.STONE:Blocks.AIR);
        var core=h.absolutePos(new BlockPos(2,2,2));var stele=core.east();var lift=h.absolutePos(new BlockPos(5,2,3));var exit=h.absolutePos(new BlockPos(11,2,10));var id=UUID.randomUUID();
        BlockPos[] pos={core,stele,lift};net.minecraft.world.level.block.Block[] block={DungeonContent.CORE.get(),DungeonContent.SHORTCUT_STELE.get(),DungeonContent.ELEVATOR.get()};
        for(int i=0;i<3;i++){h.getLevel().setBlock(pos[i],block[i].defaultBlockState(),3);((DungeonMechanismBlockEntity)h.getLevel().getBlockEntity(pos[i])).configure(id,"cargo_qa",i==0?"core":"return_lift",core,-1,List.of());}
        var elevator=(DungeonMechanismBlockEntity)h.getLevel().getBlockEntity(lift);elevator.setDestination(exit);
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"lift-native"));p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.setPos(Vec3.atBottomCenterOf(lift.south(2)));return new Fixture(core,stele,lift,exit,id,elevator,p);
    }
    private static void use(GameTestHelper h,ServerPlayer p,BlockPos at){var state=h.getLevel().getBlockState(at);state.getBlock().use(state,h.getLevel(),at,p,InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(at),Direction.UP,at,false));}
    private static void unlock(GameTestHelper h,Fixture f){var p=f.player();p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.IRON_PICKAXE));p.setPos(Vec3.atBottomCenterOf(f.stele().south()));use(h,p,f.stele());h.assertTrue(DungeonStateStore.get(h.getLevel()).room(f.instance(),"cargo_qa").shortcutOpen("return_lift"),"Actual original stele/pickaxe unlocks native shared lift");p.setPos(Vec3.atBottomCenterOf(f.lift().south(2)));p.setShiftKeyDown(true);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.item("qimen_cable"),3));}
    private static ItemEntity cargo(GameTestHelper h,Fixture f,UUID owner){var stack=new ItemStack(Items.IRON_INGOT,17);stack.getOrCreateTag().putString("NativeCargoReceipt","keep-original");var at=Vec3.atBottomCenterOf(f.lift().east());var e=new ItemEntity(h.getLevel(),at.x,at.y,at.z,stack);e.setDeltaMovement(Vec3.ZERO);e.setTarget(owner);e.setThrower(f.player().getUUID());h.getLevel().addFreshEntity(e);return e;}
    @GameTest(template="bow_ritual_test",batch="cod4_lift_cargo",setupTicks=20,timeoutTicks=80)
    public static void nativeUnlockedLiftMovesActualOwnedStackChargesOneAndRetainsFreePassengerInput(GameTestHelper h){
        var f=fixture(h);var p=f.player();var cargo=cargo(h,f,p.getUUID());p.setShiftKeyDown(true);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.item("qimen_cable"),3));
        h.startSequence().thenWaitUntil(()->h.assertTrue(h.getLevel().getEntity(cargo.getUUID())==cargo&&cargo.tickCount>0,"Actual loaded cargo is entity-visible and ticking"))
        .thenExecute(()->{try{
            var origin=cargo.position();use(h,p,f.lift());h.assertTrue(p.getMainHandItem().getCount()==3&&cargo.position().equals(origin),"Locked original shortcut cannot send cargo or charge cable");
            unlock(h,f);var passenger=p.position();var original=cargo.getItem().copy();var saved=cargo.saveWithoutId(new CompoundTag());var uuid=cargo.getUUID();
            use(h,p,f.lift());h.assertTrue(cargo.distanceToSqr(Vec3.atBottomCenterOf(f.exit()))<.01&&p.getMainHandItem().getCount()==2&&p.position().equals(passenger),"Real native entity moves to original safe destination and one actual cable pays cargo only");
            h.assertTrue(cargo.getUUID().equals(uuid)&&ItemStack.isSameItemSameTags(original,cargo.getItem())&&cargo.getItem().getCount()==17,"No replacement/duplicate entity or item stack, foreign cargo NBT and original count retained");
            var moved=cargo.saveWithoutId(new CompoundTag());h.assertTrue(saved.getUUID("Owner").equals(moved.getUUID("Owner"))&&saved.getUUID("Thrower").equals(moved.getUUID("Thrower")),"Native pickup ownership and thrower survive actual transport");
            use(h,p,f.lift());h.assertTrue(p.getMainHandItem().getCount()==2,"Empty origin cannot replay payment or cargo");
            var be=f.elevator().saveWithoutMetadata();f.elevator().load(be);p.setShiftKeyDown(false);use(h,p,f.lift());
            h.assertTrue(p.distanceToSqr(Vec3.atBottomCenterOf(f.exit()))<.01&&p.getMainHandItem().getCount()==2,"Original normal-click passenger input remains free with cable held, also after native BE reload");h.succeed();
        }finally{cargo.discard();p.discard();}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_lift_cargo",setupTicks=20,timeoutTicks=80)
    public static void foreignPickupOwnershipBlockedFluidAndMalformedDestinationDoNotChargeOrCopyCargo(GameTestHelper h){
        var f=fixture(h);var p=f.player();unlock(h,f);var owner=UUID.randomUUID();var cargo=cargo(h,f,owner);
        h.startSequence().thenWaitUntil(()->h.assertTrue(h.getLevel().getEntity(cargo.getUUID())==cargo&&cargo.tickCount>0,"Actual protected cargo is entity-visible and ticking"))
        .thenExecute(()->{try{
            var origin=cargo.position();use(h,p,f.lift());h.assertTrue(cargo.position().equals(origin)&&p.getMainHandItem().getCount()==3,"Native foreign pickup owner prevents moving another player's protected stack");cargo.setTarget(p.getUUID());
            h.getLevel().setBlock(f.exit(),Blocks.STONE.defaultBlockState(),3);use(h,p,f.lift());h.assertTrue(p.getMainHandItem().getCount()==3&&cargo.position().equals(origin),"Actual solid destination rejects cargo without payment");
            h.getLevel().setBlock(f.exit(),Blocks.WATER.defaultBlockState(),3);use(h,p,f.lift());h.assertTrue(p.getMainHandItem().getCount()==3&&cargo.position().equals(origin),"Actual fluid landing rejects cargo without payment");h.getLevel().setBlock(f.exit(),Blocks.AIR.defaultBlockState(),3);
            var tag=f.elevator().saveWithoutMetadata();tag.putLong("Destination",f.exit().offset(200000,0,0).asLong());f.elevator().load(tag);int tickets=h.getLevel().getForcedChunks().size();use(h,p,f.lift());
            h.assertTrue(cargo.position().equals(origin)&&p.getMainHandItem().getCount()==3&&h.getLevel().getForcedChunks().size()==tickets,"Original malformed/out-of-range destination migration rejects without forced tickets, cargo or costs");
            h.assertTrue(h.getLevel().getEntitiesOfClass(ItemEntity.class,cargo.getBoundingBox().inflate(2),e->e.getItem().hasTag()&&e.getItem().getTag().getString("NativeCargoReceipt").equals("keep-original")).size()==1,"Rejected requests never copy the original dropped stack");h.succeed();
        }finally{cargo.discard();p.discard();}});
    }
}
