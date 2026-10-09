package com.dynasty.expansion;

import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.FurnaceBlockEntity;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;
import java.util.UUID;

@GameTestHolder("dynasty_cod4")
@PrefixGameTestTemplate(false)
public final class SiteIntegrationGameTests {
    private static ServerPlayer player(GameTestHelper h){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"site-test"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(Vec3.atCenterOf(h.absolutePos(new BlockPos(2,2,2))));return p;
    }
    private static void use(GameTestHelper h,ServerPlayer p,BlockPos pos){
        var state=h.getLevel().getBlockState(pos);state.use(h.getLevel(),p,InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(pos),Direction.UP,pos,false));
    }
    private static void ready(ServerPlayer p,String id){
        var root=EquipmentBehaviors.saved(p);root.putLong("site_"+id+"_start",p.level().getGameTime()-3600);root.putLong("site_"+id+"_next",p.level().getGameTime());
    }
    @GameTest(template="bow_ritual_test",batch="cod4_bellows",timeoutTicks=220)
    public static void bellowsConsumesCharcoalAndActuallySmeltsWithoutCreatingOutput(GameTestHelper h){
        var p=player(h);var pos=h.absolutePos(new BlockPos(2,2,2));var furnacePos=pos.offset(2,0,0);
        h.getLevel().setBlockAndUpdate(pos,SmallInteractions.ENTRIES.get("old_bellows").get().defaultBlockState());
        h.getLevel().setBlockAndUpdate(furnacePos,Blocks.FURNACE.defaultBlockState());
        var furnace=(FurnaceBlockEntity)h.getLevel().getBlockEntity(furnacePos);furnace.setItem(0,new ItemStack(Items.RAW_IRON,8));furnace.setItem(1,new ItemStack(Items.BAMBOO,3));
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.CHARCOAL,2));use(h,p,pos);
        h.assertTrue(EquipmentBehaviors.saved(p).getLong("site_old_bellows_next")==h.getLevel().getGameTime()+600,"Existing thirty-second wind-up retained");
        use(h,p,pos);h.assertTrue(p.getMainHandItem().getCount()==2&&furnace.getItem(2).isEmpty(),"No fuel, reward or smelting before deadline");
        ready(p,"old_bellows");use(h,p,pos);
        var save=furnace.saveWithoutMetadata();
        h.assertTrue(p.getMainHandItem().getCount()==1&&save.getInt("BurnTime")==1600&&save.getInt("CookTime")==20,"One charcoal becomes real finite furnace fuel and one bellows stroke");
        h.assertTrue(furnace.getItem(0).getCount()==8&&furnace.getItem(1).getCount()==3&&furnace.getItem(2).isEmpty(),"Bellows preserves input, existing fuel and empty output");
        h.assertTrue(p.getInventory().countItem(Items.IRON_NUGGET)==3,"Original completion reward preserved");
        furnace.load(save);use(h,p,pos);h.assertTrue(p.getMainHandItem().getCount()==1&&p.getInventory().countItem(Items.IRON_NUGGET)==3,"Reload and repeated interaction never pay twice");
        h.runAfterDelay(190,()->{
            h.assertTrue(furnace.getItem(2).is(Items.IRON_INGOT)&&furnace.getItem(2).getCount()==1&&furnace.getItem(0).getCount()==7,"Vanilla furnace ticker performs exactly one actual smelt from the assisted fire");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void bellowsRejectsMissingRecipeBlockedOutputAndFullFireWithoutPayment(GameTestHelper h){
        var p=player(h);var pos=h.absolutePos(new BlockPos(2,2,2));var furnacePos=pos.offset(2,0,0);
        h.getLevel().setBlockAndUpdate(pos,SmallInteractions.ENTRIES.get("old_bellows").get().defaultBlockState());
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.CHARCOAL,2));ready(p,"old_bellows");use(h,p,pos);
        h.assertTrue(p.getMainHandItem().getCount()==2&&!EquipmentBehaviors.saved(p).getBoolean("site_old_bellows_done"),"Missing furnace does not complete or charge");
        h.getLevel().setBlockAndUpdate(furnacePos,Blocks.FURNACE.defaultBlockState());var furnace=(FurnaceBlockEntity)h.getLevel().getBlockEntity(furnacePos);
        furnace.setItem(0,new ItemStack(Items.STICK));use(h,p,pos);h.assertTrue(p.getMainHandItem().getCount()==2,"Uns meltable input never consumes fuel");
        furnace.setItem(0,new ItemStack(Items.RAW_IRON));furnace.setItem(2,new ItemStack(Items.IRON_INGOT,64));use(h,p,pos);h.assertTrue(p.getMainHandItem().getCount()==2,"Full output never consumes fuel");
        furnace.setItem(2,ItemStack.EMPTY);var data=furnace.saveWithoutMetadata();data.putInt("BurnTime",1601);furnace.load(data);use(h,p,pos);
        h.assertTrue(p.getMainHandItem().getCount()==2&&!EquipmentBehaviors.saved(p).getBoolean("site_old_bellows_done"),"Existing full fire cannot waste charcoal or duplicate completion");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void waterwheelUpdatesExistingWorldStateAndPersistsOneSharedRepair(GameTestHelper h){
        var p=player(h);var q=player(h);var pos=h.absolutePos(new BlockPos(2,2,2));var block=SmallInteractions.ENTRIES.get("broken_waterwheel").get();
        h.getLevel().setBlockAndUpdate(pos,block.defaultBlockState());p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.item("qimen_cable"),2));use(h,p,pos);
        h.assertTrue(EquipmentBehaviors.saved(p).getLong("site_broken_waterwheel_next")==h.getLevel().getGameTime()+1200,"One-minute repair retained");
        ready(p,"broken_waterwheel");use(h,p,pos);var state=h.getLevel().getBlockState(pos);
        h.assertTrue(state.getValue(BlockStateProperties.LIT)&&com.dynasty.cod3.Cod3WorldState.get(h.getLevel()).unlocked("world_02"),"Physical wheel and existing mechanism-city world flag both change");
        h.assertTrue(p.getMainHandItem().getCount()==1&&p.getInventory().countItem(ExpansionContent.item("copper_coin"))==2,"Original cost and reward retained once");
        var saved=net.minecraft.nbt.NbtUtils.writeBlockState(state);h.getLevel().setBlockAndUpdate(pos,net.minecraft.nbt.NbtUtils.readBlockState(h.getLevel().holderLookup(net.minecraft.core.registries.Registries.BLOCK),saved));
        q.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.item("qimen_cable"),2));use(h,q,pos);use(h,p,pos);
        h.assertTrue(q.getMainHandItem().getCount()==2&&q.getInventory().countItem(ExpansionContent.item("copper_coin"))==0&&EquipmentBehaviors.saved(q).getBoolean("site_broken_waterwheel_done"),"Second player recognizes persisted shared repair without second charge or reward");
        h.assertTrue(p.getMainHandItem().getCount()==1,"Repeated repair remains idempotent");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4")
    public static void completedLegacySitesReceiveMissingBehaviorWithoutRepayingRewards(GameTestHelper h){
        var p=player(h);var pos=h.absolutePos(new BlockPos(2,2,2));var furnacePos=pos.offset(2,0,0);
        var root=EquipmentBehaviors.saved(p);root.putBoolean("site_old_bellows_done",true);root.putBoolean("site_broken_waterwheel_done",true);
        h.getLevel().setBlockAndUpdate(pos,SmallInteractions.ENTRIES.get("old_bellows").get().defaultBlockState());
        p.setItemInHand(InteractionHand.MAIN_HAND,ItemStack.EMPTY);use(h,p,pos);h.assertTrue(!root.getBoolean("site_old_bellows_assisted"),"Missing furnace does not lose the legacy paid bellows stroke");
        h.getLevel().setBlockAndUpdate(furnacePos,Blocks.FURNACE.defaultBlockState());var furnace=(FurnaceBlockEntity)h.getLevel().getBlockEntity(furnacePos);furnace.setItem(0,new ItemStack(Items.RAW_IRON));use(h,p,pos);
        h.assertTrue(root.getBoolean("site_old_bellows_assisted")&&furnace.saveWithoutMetadata().getInt("BurnTime")==1600&&p.getInventory().countItem(Items.IRON_NUGGET)==0,"Legacy payment gains missing real furnace assistance without replaying old rewards");
        use(h,p,pos);h.assertTrue(furnace.saveWithoutMetadata().getInt("BurnTime")==1600,"Legacy migration is one-time");
        h.getLevel().setBlockAndUpdate(pos,SmallInteractions.ENTRIES.get("broken_waterwheel").get().defaultBlockState());use(h,p,pos);
        h.assertTrue(h.getLevel().getBlockState(pos).getValue(BlockStateProperties.LIT)&&com.dynasty.cod3.Cod3WorldState.get(h.getLevel()).unlocked("world_02"),"Previously completed repair migrates into actual shared wheel/world state");
        h.assertTrue(p.getInventory().countItem(ExpansionContent.item("copper_coin"))==0&&p.getMainHandItem().isEmpty(),"No legacy completion reward or charge replays");h.succeed();
    }
}
