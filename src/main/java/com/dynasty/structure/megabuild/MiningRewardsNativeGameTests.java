package com.dynasty.structure.megabuild;

import com.dynasty.DynastyItems;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod6") @PrefixGameTestTemplate(false)
public final class MiningRewardsNativeGameTests {
    private static ChestBlockEntity fresh(GameTestHelper h,BlockPos pos){
        if(h.getLevel().getBlockEntity(pos) instanceof ChestBlockEntity old)old.clearContent();
        h.getLevel().setBlock(pos,Blocks.AIR.defaultBlockState(),3);h.getLevel().setBlock(pos,Blocks.CHEST.defaultBlockState(),3);return (ChestBlockEntity)h.getLevel().getBlockEntity(pos);
    }
    @GameTest(template="bow_ritual_test",batch="cod6_quarry_rewards_native",setupTicks=20,timeoutTicks=100)
    public static void hundredActualNativeChestInventoriesKeepOriginalJadeCoreBoundedRareResourcesAndSavedContents(GameTestHelper h){
        var pos=h.absolutePos(new BlockPos(6,52,6));int slots=0,units=0,mineralSlots=0;var rare=new TreeMap<String,Integer>();
        Set<Item> minerals=Set.of(DynastyItems.JADE.get(),Items.RAW_IRON,Items.RAW_COPPER,Items.RAW_GOLD,Items.COAL,Items.IRON_ORE,Items.COPPER_ORE,Items.REDSTONE,Items.LAPIS_LAZULI);
        ChestBlockEntity chest=null;
        try{for(int seed=0;seed<100;seed++){
            chest=fresh(h,pos);MiningRewards.fillNew(chest,seed);int occupied=0,core=0;
            for(int i=0;i<chest.getContainerSize();i++){
                var stack=chest.getItem(i);if(stack.isEmpty())continue;occupied++;units+=stack.getCount();
                if(stack.is(DynastyItems.JADE.get())){core+=stack.getCount();h.assertTrue(stack.getCount()==1,"Original fixed jade core is neither multiplied nor removed");}
                else h.assertTrue(stack.getCount()>=10&&stack.getCount()<=12,"Native new resource stacks account for single-unit core while keeping total mean near10");
                h.assertTrue(!stack.is(Items.IRON_INGOT)&&!stack.is(Items.COPPER_INGOT)&&!stack.is(Items.GOLD_INGOT),"Native actual mine reward has no smelted metal");
                if(minerals.contains(stack.getItem()))mineralSlots++;
                if(stack.is(Items.RAW_GOLD)||stack.is(Items.AMETHYST_SHARD)||stack.is(DynastyItems.JADE.get()))rare.merge(net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(stack.getItem()).toString(),stack.getCount(),Integer::sum);
            }
            h.assertTrue(occupied==9&&core==1,"Native27-slot inventory has exactly nine distinct occupied slots including original jade core");slots+=occupied;
            var saved=chest.saveWithFullMetadata();MiningRewards.fillNew(chest,999);h.assertTrue(saved.equals(chest.saveWithFullMetadata()),"A second native fill cannot refill an already generated container");
            chest=fresh(h,pos);chest.load(saved);h.assertTrue(saved.equals(chest.saveWithFullMetadata()),"Native block-entity NBT reload preserves exact slots/core/stacks");
        }
        double mean=(double)units/slots,ratio=(double)mineralSlots/slots;
        h.assertTrue(mean>9.8&&mean<10.2&&slots==900&&mineralSlots==700&&rare.getOrDefault("dynasty:jade",0)==100,"Actual100 native containers prove fixed occupancy, mineral ratio and total stack mean");
        h.assertTrue(rare.getOrDefault("minecraft:raw_gold",0)>0&&rare.getOrDefault("minecraft:amethyst_shard",0)>0,"Actual seeded rare mineral value remains reachable and measured by retained real-item quantities");
        System.out.println("COD6_NATIVE_CHEST100 occupied="+slots+"/2700, units="+units+", allStackMean="+mean+", mineralSlotRatio="+ratio+", rareRealItemTotals="+rare);h.succeed();
        }finally{if(chest!=null)chest.clearContent();h.getLevel().setBlock(pos,Blocks.AIR.defaultBlockState(),3);}
    }
    private static void place(GameTestHelper h,MegabuildPiece piece,BlockPos at){
        h.getLevel().getChunkAt(at);piece.postProcess(h.getLevel(),h.getLevel().structureManager(),h.getLevel().getChunkSource().getGenerator(),h.getLevel().random,new net.minecraft.world.level.levelgen.structure.BoundingBox(at),new net.minecraft.world.level.ChunkPos(at),at);
    }
    @GameTest(template="bow_ritual_test",batch="cod6_quarry_rewards_preservation",setupTicks=20,timeoutTicks=100)
    public static void actualStructureNewChestHasOriginalCoreWhilePlayerAndUnopenedOldNativeNbtNeverRefill(GameTestHelper h){
        var origin=h.absolutePos(new BlockPos(0,52,0));var piece=new MegabuildPiece(MegabuildStructures.MINING_PIECE.get(),0,origin,MegabuildStructures::mining,28,0,96,36);
        var at=origin.offset(39,1,29);h.getLevel().getChunkAt(at);h.getLevel().setBlock(at,Blocks.AIR.defaultBlockState(),3);place(h,piece,at);
        var chest=(ChestBlockEntity)h.getLevel().getBlockEntity(at);h.assertTrue(chest!=null,"Actual native structure postProcess creates new mine chest");int occupied=0,core=0;
        for(int i=0;i<27;i++){var s=chest.getItem(i);if(!s.isEmpty())occupied++;if(s.is(DynastyItems.JADE.get()))core+=s.getCount();}
        h.assertTrue(occupied==9&&core==1,"Original placement hook—not a standalone reward simulation—keeps core within nine slots");
        chest.clearContent();var own=new ItemStack(Items.DIAMOND,17);own.getOrCreateTag().putString("ForeignPlayerData","do-not-overwrite");chest.setItem(2,own);var saved=chest.saveWithFullMetadata();
        chest=fresh(h,at);chest.load(saved);place(h,piece,at);h.assertTrue(saved.equals(chest.saveWithFullMetadata()),"Native saved player inventory, count, slots and foreign NBT survive new-code structure repeat");
        chest.clearContent();chest.setLootTable(new ResourceLocation("dynasty","chests/tiangong_common"),73);var unopened=chest.saveWithFullMetadata();
        h.assertTrue(unopened.contains("LootTable")&&!unopened.contains("Items"),"Old unopened native chest persists original loot reference, not generated inventory");
        chest=fresh(h,at);chest.load(unopened);place(h,piece,at);
        h.assertTrue(unopened.equals(chest.saveWithFullMetadata()),"Native unopened old chest retains original loot table and seed without forcing new fill or unpacking");
        // Only now open the original table through vanilla's native unpack path.
        int oldCore=0;for(int i=0;i<27;i++)if(chest.getItem(i).is(DynastyItems.JADE.get()))oldCore+=chest.getItem(i).getCount();
        h.assertTrue(oldCore==1,"An actual opened old loot-reference chest still uses original fixed jade pool, not new nine-stack fill");
        chest.clearContent();h.getLevel().setBlock(at,Blocks.AIR.defaultBlockState(),3);h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod6_quarry_manual_native",setupTicks=20,timeoutTicks=100)
    public static void actualNativeResourceTemplateAndPlacementKeepCoreAndExistingNaturalGalleryLayout(GameTestHelper h){
        var template=h.getLevel().getStructureManager().get(new ResourceLocation("dynasty","tiangong_mining_estate")).orElseThrow();
        h.assertTrue(template.getSize().equals(new net.minecraft.core.Vec3i(96,36,96)),"Native resource manager loads original manual mine template size");
        var saved=template.save(new CompoundTag());int chests=0;boolean gallery=false;
        for(var value:saved.getList("blocks",10)){
            var block=(CompoundTag)value;var pos=block.getList("pos",3);
            if(pos.getInt(0)==17&&pos.getInt(1)==6&&pos.getInt(2)==66)gallery=true;
            var nbt=block.getCompound("nbt");if(!nbt.getString("id").equals("minecraft:chest"))continue;chests++;int occupied=0,core=0;
            for(var item:nbt.getList("Items",10)){var stack=ItemStack.of((CompoundTag)item);if(!stack.isEmpty())occupied++;if(stack.is(DynastyItems.JADE.get()))core+=stack.getCount();}
            h.assertTrue(occupied==9&&core==1,"Each actual native loaded manual-template chest includes retained core within original occupancy");
        }
        h.assertTrue(chests==4&&gallery,"Native manual template has all four mines and existing v6 mechanical-spider gallery roof");
        var at=h.absolutePos(new BlockPos(6,52,6));var origin=at.offset(-39,-1,-29);fresh(h,at).clearContent();
        var settings=new net.minecraft.world.level.levelgen.structure.templatesystem.StructurePlaceSettings().setBoundingBox(new net.minecraft.world.level.levelgen.structure.BoundingBox(at)).setIgnoreEntities(true);
        h.assertTrue(template.placeInWorld(h.getLevel(),origin,origin,settings,h.getLevel().random,3),"Actual native template placement pipeline succeeds at bounded chest clip");
        var chest=(ChestBlockEntity)h.getLevel().getBlockEntity(at);int core=0,occupied=0;
        for(int i=0;i<27;i++){var stack=chest.getItem(i);if(!stack.isEmpty())occupied++;if(stack.is(DynastyItems.JADE.get()))core+=stack.getCount();}
        h.assertTrue(core==1&&occupied==9,"Actual placed native resource-template container has same core/count contract as natural structure code");
        chest.clearContent();h.getLevel().setBlock(at,Blocks.AIR.defaultBlockState(),3);h.succeed();
    }
}
