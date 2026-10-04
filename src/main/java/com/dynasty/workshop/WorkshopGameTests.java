package com.dynasty.workshop;

import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.item.*;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty")
@PrefixGameTestTemplate(false)
public final class WorkshopGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void allStationsPersistAndNeverDuplicate(GameTestHelper h){
        int index=0;
        for(var recipe:WorkshopRecipes.ALL){
            var item=new WorkshopRecipes.Cost("dynasty:"+recipe.station(),1).stack();
            h.assertTrue(item.getItem() instanceof BlockItem,"Station missing: "+recipe.station());
            h.assertTrue(!recipe.result().isEmpty(),"Output missing: "+recipe.output());
            BlockPos p=new BlockPos(1+index%4,2,1+index/4);index++;
            h.setBlock(p,((BlockItem)item.getItem()).getBlock());
            var vat=(WorkshopBlockEntity)h.getBlockEntity(p);
            h.assertTrue(!vat.accept(new ItemStack(Items.DIRT,16)),"Accepted invalid material");
            for(var cost:recipe.costs()){
                h.assertTrue(!cost.stack().isEmpty(),"Input missing "+cost.id());
                var held=cost.stack();int expected=held.getCount();
                for(int i=0;i<cost.count();i++){
                    h.assertTrue(vat.accept(held),"Rejected valid ingredient");
                    h.assertTrue(held.getCount()==--expected,"Consumed more than one");
                    var saved=vat.saveWithoutMetadata();int before=vat.deposited();
                    vat.load(saved);h.assertTrue(vat.deposited()==before,"Lost persisted progress");
                    var client=new WorkshopBlockEntity(vat.getBlockPos(),vat.getBlockState());client.handleUpdateTag(vat.getUpdateTag());
                    h.assertTrue(client.deposited()==before,"Client mask differs");
                }
            }
            h.assertTrue(vat.ready(),"Completion state missing");
            h.assertTrue(!vat.accept(recipe.costs().get(0).stack()),"Second player overfilled ready station");
            var output=vat.collect();h.assertTrue(ItemStack.isSameItemSameTags(output,recipe.result())&&output.getCount()==recipe.count(),"Wrong output");
            h.assertTrue(vat.collect().isEmpty(),"Duplicate collection");
            h.assertTrue(vat.deposited()==0,"Progress not reset");
        }
        h.succeed();
    }
}
