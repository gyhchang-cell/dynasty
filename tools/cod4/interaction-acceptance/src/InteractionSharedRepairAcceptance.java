package com.dynasty.structure;
import com.dynasty.expansion.*;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraftforge.gametest.*;
import static com.dynasty.structure.InteractionAcceptance.*;
@GameTestHolder("dynasty_interaction_extra_qa") @PrefixGameTestTemplate(false)
public final class InteractionSharedRepairAcceptance {
    @GameTest(template="bow_ritual_test",batch="interaction_shared_physical_repair",timeoutTicks=1300)
    public static void realPhysicalWaterwheelRepairSharedButPaymentAndCoinsRemainPersonal(GameTestHelper h){
        var piece=build(h,1,Direction.WEST,new BlockPos(4352,80,3072));var at=piece.point(21,1,28);var approach=piece.point(21,1,27);
        var p=player(h,approach);var q=player(h,approach);p.setItemInHand(InteractionHand.MAIN_HAND,offering("broken_waterwheel"));q.setItemInHand(InteractionHand.MAIN_HAND,offering("broken_waterwheel"));use(h,p,at);long start=h.getLevel().getGameTime(),base=h.getTick();
        h.runAtTickTime(base+1200,()->{
            use(h,p,at);h.assertTrue(h.getLevel().getBlockState(at).getValue(BlockStateProperties.LIT)&&EquipmentBehaviors.saved(p).getBoolean("site_broken_waterwheel_done")&&p.getMainHandItem().getCount()==1&&p.getInventory().countItem(ExpansionContent.item("copper_coin"))==2,"Actual repair consumes one owner's cable once");
            h.assertTrue(!EquipmentBehaviors.saved(q).getBoolean("site_broken_waterwheel_done"),"World block change does not itself write another player's receipt");use(h,q,at);
            h.assertTrue(EquipmentBehaviors.saved(q).getBoolean("site_broken_waterwheel_done")&&q.getMainHandItem().getCount()==2&&q.getInventory().countItem(ExpansionContent.item("copper_coin"))==0,"Second player may acknowledge shared repair without payment or another owner's coins");
            use(h,p,at);use(h,q,at);h.assertTrue(p.getInventory().countItem(ExpansionContent.item("copper_coin"))==2&&q.getInventory().countItem(ExpansionContent.item("copper_coin"))==0,"Repeats never duplicate either reward");
            evidence("shared_waterwheel","elapsed_world_ticks",h.getLevel().getGameTime()-start,"physical_repair_shared",true,"owner_cables_consumed",1,"second_cables_consumed",0,"owner_coins",2,"second_coins",0,"second_receipt_requires_own_use",true);h.succeed();
        });
    }
}
