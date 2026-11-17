package com.dynasty.navigation;

import net.minecraft.gametest.framework.*;
import net.minecraftforge.gametest.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.*;
import net.minecraft.world.inventory.*;
import net.minecraft.world.entity.player.Player;
import net.minecraft.core.registries.Registries;

@GameTestHolder("dynasty_bugfix") @PrefixGameTestTemplate(false)
public final class NavigationGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void allPlanksCraftSameSpear(GameTestHelper h){
        var recipe=h.getLevel().getRecipeManager().byKey(new ResourceLocation("dynasty","mu_mao")).orElseThrow();
        var menu=new AbstractContainerMenu(null,0){public ItemStack quickMoveStack(Player p,int i){return ItemStack.EMPTY;}public boolean stillValid(Player p){return true;}};
        var grid=new TransientCraftingContainer(menu,3,3);int checked=0;
        for(var holder:net.minecraftforge.registries.ForgeRegistries.ITEMS.tags().getTag(net.minecraft.tags.ItemTags.PLANKS)){
            grid.clearContent();grid.setItem(0,new ItemStack(Items.STICK));grid.setItem(1,new ItemStack(Items.STICK));grid.setItem(2,new ItemStack(holder));
            @SuppressWarnings("unchecked") var craft=(net.minecraft.world.item.crafting.Recipe<net.minecraft.world.inventory.CraftingContainer>)recipe;
            h.assertTrue(craft.matches(grid,h.getLevel()),"Spear must accept "+holder);
            h.assertTrue(craft.assemble(grid,h.getLevel().registryAccess()).is(com.dynasty.DynastyWeapons.MU_MAO.get()),"All plank types must yield same spear");checked++;
        }
        h.assertTrue(checked>=11,"Must include nether and overworld plank tags");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void legacyBuildingsHaveLocatableStarts(GameTestHelper h){
        var registry=h.getLevel().registryAccess().registryOrThrow(Registries.STRUCTURE);int n=0;
        for(var id:registry.keySet())if(id.getNamespace().equals("dynasty")&&id.getPath().startsWith("legacy_")){
            h.assertTrue(registry.get(id) instanceof com.dynasty.structure.LegacyBuildingStructure,"Real structure entry required");n++;
        }
        h.assertTrue(n==21,"All 21 active legacy building types registered");
        var origin=h.absolutePos(new net.minecraft.core.BlockPos(24,0,24)).atY(100);
        var piece=new com.dynasty.structure.LegacyBuildingPiece(origin,new ResourceLocation("dynasty","ritual_circle"),123);
        var cp=new net.minecraft.world.level.ChunkPos(origin);var l=h.getLevel();
        for(int x=-1;x<=1;x++)for(int z=-1;z<=1;z++){
            var c=new net.minecraft.world.level.ChunkPos(cp.x+x,cp.z+z);l.getChunk(c.x,c.z);
            var clip=new net.minecraft.world.level.levelgen.structure.BoundingBox(c.getMinBlockX(),l.getMinBuildHeight(),c.getMinBlockZ(),c.getMaxBlockX(),l.getMaxBuildHeight()-1,c.getMaxBlockZ());
            piece.postProcess(l,l.structureManager(),l.getChunkSource().getGenerator(),net.minecraft.util.RandomSource.create(1),clip,c,origin);
        }
        h.assertTrue(l.getBlockState(origin.above()).is(com.dynasty.DynastyBlocks.RITUAL_ALTAR.get()),"Located structure contains actual altar blocks");
        h.assertTrue(l.getBlockEntity(origin.offset(2,1,2)) instanceof net.minecraft.world.level.block.entity.ChestBlockEntity,"Structure preserves real chest at "+origin+" state="+l.getBlockState(origin.offset(2,1,2)));h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100)
    public static void compassSelectsNearestAndClearsMissing(GameTestHelper h){
        var p=net.minecraftforge.common.util.FakePlayerFactory.getMinecraft(h.getLevel());
        var origin=h.absolutePos(new net.minecraft.core.BlockPos(2,3,2));p.moveTo(origin.getX(),origin.getY(),origin.getZ());
        var stack=new ItemStack(CreatureCompass.ITEM.get());p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,stack);
        var near=h.spawn(net.minecraft.world.entity.EntityType.PIG,3,3,2);
        var far=h.spawn(net.minecraft.world.entity.EntityType.PIG,8,3,2);
        CreatureCompass.search(p,new ResourceLocation("minecraft","pig"));
        h.assertTrue(stack.hasTag()&&stack.getTag().getUUID("TargetUuid").equals(near.getUUID()),"Compass selects nearest living mob");
        near.kill();far.kill();p.getCooldowns().removeCooldown(CreatureCompass.ITEM.get());
        CreatureCompass.search(p,new ResourceLocation("minecraft","ender_dragon"));
        h.assertTrue(!stack.getTag().contains("TargetPos")&&!stack.getTag().hasUUID("TargetUuid"),"Failed search clears old target");
        p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,ItemStack.EMPTY);h.succeed();
    }
}
