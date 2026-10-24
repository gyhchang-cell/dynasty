package com.dynasty.structure;
import com.dynasty.expansion.*;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.entity.*;
import net.minecraft.world.phys.*;
import net.minecraftforge.gametest.*;
import static com.dynasty.structure.InteractionAcceptance.*;
@GameTestHolder("dynasty_interaction_qa") @PrefixGameTestTemplate(false)
public final class InteractionEdgeAcceptance {
    @GameTest(template="bow_ritual_test",batch="interaction_packet_positive",timeoutTicks=40)
    public static void nearNativeUsePacketActuallyEntersAllNonNightGatedSiteHandlers(GameTestHelper h){
        var at=h.absolutePos(new BlockPos(3,2,3));var errors=new java.util.ArrayList<String>();
        for(String id:SmallInteractions.IDS){if(id.equals("sword_scar_wall"))continue;
            h.getLevel().setBlock(at,SmallInteractions.ENTRIES.get(id).get().defaultBlockState(),3);var p=player(h,at.north());p.setYRot(180);p.setItemInHand(InteractionHand.MAIN_HAND,offering(id));
            // Empty ground around the small template still supports native scene NPCs.
            for(var d:Direction.Plane.HORIZONTAL)h.getLevel().setBlock(at.relative(d).below(),Blocks.STONE.defaultBlockState(),3);
            var before=EquipmentBehaviors.saved(p).copy();p.connection.handleUseItemOn(new net.minecraft.network.protocol.game.ServerboundUseItemOnPacket(InteractionHand.MAIN_HAND,new BlockHitResult(Vec3.atCenterOf(at),Direction.UP,at,false),1));
            boolean entered=!before.equals(EquipmentBehaviors.saved(p));evidence("packet_near_positive","id",id,"entered",entered,"distance_squared",p.distanceToSqr(Vec3.atCenterOf(at)));if(!entered)errors.add(id);p.discard();
        }h.assertTrue(errors.isEmpty(),"Near native packets enter handlers, preventing a vacuous far-packet pass: "+errors);h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="interaction_furnace_edges",timeoutTicks=650)
    public static void productionBellowsRejectsEmptyFullOverfueledAndOutOfRangeFurnacesBeforePayment(GameTestHelper h){
        var piece=build(h,2,Direction.SOUTH,new BlockPos(3840,80,3072));var at=piece.point(17,1,28);var furnaceAt=piece.point(17,1,26);var p=player(h,piece.point(17,1,27));p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.CHARCOAL,4));use(h,p,at);
        long base=h.getTick(),start=h.getLevel().getGameTime();
        h.runAtTickTime(base+600,()->{
            var furnace=(AbstractFurnaceBlockEntity)h.getLevel().getBlockEntity(furnaceAt);
            use(h,p,at);h.assertTrue(p.getMainHandItem().getCount()==4&&!EquipmentBehaviors.saved(p).getBoolean("site_old_bellows_done"),"Empty native furnace consumes no charcoal or receipt");
            furnace.setItem(0,new ItemStack(Items.RAW_IRON));furnace.setItem(2,new ItemStack(Items.IRON_INGOT,64));use(h,p,at);h.assertTrue(p.getMainHandItem().getCount()==4&&!EquipmentBehaviors.saved(p).getBoolean("site_old_bellows_done"),"Full output does not burn payment");furnace.setItem(2,ItemStack.EMPTY);
            var data=furnace.saveWithoutMetadata();data.putInt("BurnTime",1601);furnace.load(data);use(h,p,at);h.assertTrue(p.getMainHandItem().getCount()==4&&!EquipmentBehaviors.saved(p).getBoolean("site_old_bellows_done"),"Over-fueled native furnace consumes no payment");data.putInt("BurnTime",0);furnace.load(data);
            var remote=at.offset(4,0,0);h.getLevel().setBlock(furnaceAt,Blocks.AIR.defaultBlockState(),3);h.getLevel().setBlock(remote,Blocks.FURNACE.defaultBlockState(),3);((AbstractFurnaceBlockEntity)h.getLevel().getBlockEntity(remote)).setItem(0,new ItemStack(Items.RAW_IRON));use(h,p,at);h.assertTrue(p.getMainHandItem().getCount()==4&&!EquipmentBehaviors.saved(p).getBoolean("site_old_bellows_done"),"Four-block-away furnace does not bypass +/-3 search");
            h.getLevel().setBlock(furnaceAt,Blocks.FURNACE.defaultBlockState(),3);furnace=(AbstractFurnaceBlockEntity)h.getLevel().getBlockEntity(furnaceAt);furnace.setItem(0,new ItemStack(Items.RAW_IRON));use(h,p,at);
            h.assertTrue(p.getMainHandItem().getCount()==3&&EquipmentBehaviors.saved(p).getBoolean("site_old_bellows_done")&&furnace.saveWithoutMetadata().getInt("BurnTime")==1600&&furnace.getItem(2).isEmpty(),"Exactly one actual charcoal becomes furnace burn time without fabricating smelted output");
            use(h,p,at);h.assertTrue(p.getMainHandItem().getCount()==3&&p.getInventory().countItem(Items.IRON_NUGGET)==3,"No repeated payment/reward");
            evidence("bellows_edges","elapsed_world_ticks",h.getLevel().getGameTime()-start,"empty_no_payment",true,"full_no_payment",true,"overfueled_no_payment",true,"outside_range_no_payment",true,"valid_burn_ticks",1600,"repeat_no_reward",true);h.succeed();
        });
    }
}
