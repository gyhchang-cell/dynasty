package com.dynasty.dungeon;

import com.dynasty.expansion.ExpansionContent;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.inventory.CraftingMenu;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.levelgen.structure.BoundingBox;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import java.util.UUID;

@GameTestHolder("dynasty_cod2")
@PrefixGameTestTemplate(false)
public final class ChenshaArtisanGameTests {
    private static FakePlayer artisan(GameTestHelper h){
        var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"artisan-test"));
        p.setGameMode(GameType.SURVIVAL);p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(Items.IRON_PICKAXE));
        return p;
    }
    private static CraftingMenu workbench(GameTestHelper h,FakePlayer player){
        var pos=h.absolutePos(new BlockPos(4,1,4));h.getLevel().setBlockAndUpdate(pos,Blocks.CRAFTING_TABLE.defaultBlockState());
        return new CraftingMenu(1,player.getInventory(),ContainerLevelAccess.create(h.getLevel(),pos));
    }
    private static void mine(FakePlayer player,BlockPos pos,int sequence){
        player.gameMode.handleBlockBreakAction(pos,net.minecraft.network.protocol.game.ServerboundPlayerActionPacket.Action.START_DESTROY_BLOCK,
            net.minecraft.core.Direction.NORTH,player.level().getMaxBuildHeight(),sequence);
        for(int tick=0;tick<30;tick++)player.gameMode.tick();
        player.gameMode.handleBlockBreakAction(pos,net.minecraft.network.protocol.game.ServerboundPlayerActionPacket.Action.STOP_DESTROY_BLOCK,
            net.minecraft.core.Direction.NORTH,player.level().getMaxBuildHeight(),sequence+1);
    }
    private static void inputs(CraftingMenu menu,net.minecraft.world.item.Item plan){
        menu.getSlot(1).set(new ItemStack(plan));
        for(int slot=2;slot<=5;slot++)menu.getSlot(slot).set(new ItemStack(Items.IRON_INGOT));
        for(int slot=6;slot<=7;slot++)menu.getSlot(slot).set(new ItemStack(Items.COPPER_INGOT));
        menu.getSlot(8).set(new ItemStack(Items.REDSTONE));
    }
    @GameTest(template="bow_ritual_test",batch="cod2_artisan_generation")
    public static void actualAuthoredColumnHasMineableSecretEntryPlanAndNativeWorkbench(GameTestHelper h){
        var level=h.getLevel();var origin=h.absolutePos(new BlockPos(-48,-24,-80));
        var piece=new ChenshaPiece(origin,3,5,UUID.randomUUID());
        var clip=new BoundingBox(origin.getX()+48,level.getMinBuildHeight(),origin.getZ()+80,
            origin.getX()+63,level.getMaxBuildHeight()-1,origin.getZ()+95);
        piece.postProcess(level,level.structureManager(),level.getChunkSource().getGenerator(),RandomSource.create(67),clip,
            new ChunkPos(origin.offset(48,0,80)),origin);
        var player=artisan(h);var foot=origin.offset(52,25,87);var head=foot.above();
        player.setPos(foot.getX()+.5,foot.getY(),foot.getZ()-2.5);
        h.assertTrue(level.getBlockState(foot).is(Blocks.CRACKED_STONE_BRICKS)&&level.getBlockState(head).is(Blocks.CRACKED_STONE_BRICKS),"Production column places the secret breakable wall");
        mine(player,foot,1);mine(player,head,3);
        h.assertTrue(level.getBlockState(foot).isAir()&&level.getBlockState(head).isAir(),"Passage is physically open after mining");
        var wall=origin.offset(49,25,91);player.setPos(wall.getX()+1.5,wall.getY(),wall.getZ()+.5);mine(player,wall,5);
        h.assertTrue(level.getBlockState(wall).is(DungeonContent.MASONRY.get()),"Normal survival break actions cannot bypass the protected outer shell");
        h.assertTrue(level.getBlockState(origin.offset(55,25,91)).is(Blocks.CRAFTING_TABLE),"Generated artisans' room contains a real crafting table");
        var chest=(ChestBlockEntity)level.getBlockEntity(origin.offset(52,25,91));chest.unpackLootTable(player);
        int plans=0,oldBlueprints=0;
        for(int slot=0;slot<chest.getContainerSize();slot++){
            var stack=chest.getItem(slot);if(stack.is(DungeonContent.HIGH_GRADE_PLAN.get()))plans+=stack.getCount();
            if(stack.is(ExpansionContent.item("blueprint")))oldBlueprints+=stack.getCount();
        }
        h.assertTrue(plans==1&&oldBlueprints==1,"Real generated chest guarantees one functional advanced plan and preserves the ordinary blueprint");
        chest.clearContent();var saved=chest.saveWithFullMetadata();
        level.removeBlock(chest.getBlockPos(),false);level.setBlockAndUpdate(chest.getBlockPos(),Blocks.CHEST.defaultBlockState());
        var restored=(ChestBlockEntity)level.getBlockEntity(chest.getBlockPos());restored.load(saved);restored.unpackLootTable(player);
        h.assertTrue(restored.isEmpty(),"Fresh chest block entity restored from native NBT cannot refill the advanced plan");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod2_artisan_recipe")
    public static void nativeWorkbenchConsumesAdvancedPlanAndCannotCraftFromOrdinaryBlueprint(GameTestHelper h){
        var player=artisan(h);player.getInventory().clearContent();var menu=workbench(h,player);
        inputs(menu,ExpansionContent.item("blueprint"));
        var recipe=h.getLevel().getRecipeManager().byKey(new ResourceLocation("dynasty:high_grade_mechanism_gears")).orElseThrow();
        h.assertTrue(menu.getSlot(0).getItem().isEmpty(),"Existing general blueprint cannot substitute for this specific high-grade recipe");
        inputs(menu,DungeonContent.HIGH_GRADE_PLAN.get());
        h.assertTrue(menu.getSlot(0).getItem().is(ExpansionContent.item("qimen_gear"))&&menu.getSlot(0).getItem().getCount()==8,"Native recipe manager computes the actual eight-gear result");
        menu.quickMoveStack(player,0);
        h.assertTrue(player.getInventory().countItem(ExpansionContent.item("qimen_gear"))==8&&player.getInventory().countItem(DungeonContent.HIGH_GRADE_PLAN.get())==0,"Native result transfer awards eight usable gears without copying the plan");
        for(int slot=1;slot<=9;slot++)h.assertTrue(menu.getSlot(slot).getItem().isEmpty(),"Vanilla result slot consumes every ingredient exactly once");
        h.assertTrue(menu.quickMoveStack(player,0).isEmpty()&&player.getInventory().countItem(ExpansionContent.item("qimen_gear"))==8,"Repeated result click cannot duplicate gears");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod2_artisan_recipe")
    public static void fullInventoryPreservesPlanUntilNativeResultCanBeTaken(GameTestHelper h){
        var player=artisan(h);for(int slot=0;slot<player.getInventory().getContainerSize();slot++)player.getInventory().setItem(slot,new ItemStack(Items.COBBLESTONE,64));
        var menu=workbench(h,player);inputs(menu,DungeonContent.HIGH_GRADE_PLAN.get());
        h.assertTrue(menu.quickMoveStack(player,0).isEmpty()&&menu.getSlot(1).getItem().is(DungeonContent.HIGH_GRADE_PLAN.get()),"No output space leaves the unique plan intact");
        player.getInventory().setItem(0,ItemStack.EMPTY);menu.quickMoveStack(player,0);
        h.assertTrue(player.getInventory().countItem(ExpansionContent.item("qimen_gear"))==8&&menu.getSlot(1).getItem().isEmpty(),"Opening one real inventory slot permits exactly one native craft");h.succeed();
    }
    private ChenshaArtisanGameTests(){}
}
