package com.dynasty;
import com.dynasty.expansion.ContentProgress;
import com.mojang.authlib.GameProfile;
import java.util.*;
import net.minecraft.advancements.CriteriaTriggers;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.inventory.*;
import net.minecraft.world.item.*;
import net.minecraftforge.gametest.*;
@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class TalismanDiscoveryNativeGameTests {
    private static ServerPlayer player(GameTestHelper h){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"talisman-native"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.setPos(h.absolutePos(new BlockPos(4,2,4)).getX()+.5,h.absolutePos(new BlockPos(4,2,4)).getY(),h.absolutePos(new BlockPos(4,2,4)).getZ()+.5);p.setItemInHand(net.minecraft.world.InteractionHand.MAIN_HAND,new ItemStack(Items.STICK));return p;
    }
    @GameTest(template="bow_ritual_test",batch="cod4_talisman_native_discovery",setupTicks=20)
    public static void nativePaperInventoryTriggerDiscoversAllOriginalRecipesAndCraftingConsumesEachRealIngredientOnce(GameTestHelper h){
        var p=player(h);try{
            for(String id:TalismanDiscovery.IDS)h.assertTrue(!p.getRecipeBook().contains(new ResourceLocation("dynasty",id)),"Fresh native player has not yet discovered optional talisman: "+id);
            var paper=new ItemStack(net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(new ResourceLocation("dynasty","talisman_paper")));p.getInventory().setItem(10,paper);
            CriteriaTriggers.INVENTORY_CHANGED.trigger(p,p.getInventory(),paper);
            for(String id:TalismanDiscovery.IDS){
                var recipe=h.getLevel().getRecipeManager().byKey(new ResourceLocation("dynasty",id)).orElseThrow();
                h.assertTrue(p.getRecipeBook().contains(recipe)&&p.getAdvancements().getOrStartProgress(p.server.getAdvancements().getAdvancement(new ResourceLocation("dynasty","recipes/talismans/"+id))).isDone(),"Actual native inventory trigger/advancement reward discovers exact original recipe, no custom quest unlock engine");
                var menu=new CraftingMenu(9,p.getInventory(),ContainerLevelAccess.create(h.getLevel(),p.blockPosition()));p.containerMenu=menu;int n=0;
                for(var ingredient:recipe.getIngredients()){var stack=ingredient.getItems()[0].copy();stack.setCount(1);menu.getSlot(++n).set(stack);}
                var output=menu.getSlot(0).remove(1);h.assertTrue(output.getItem() instanceof TalismanCharmItem&&net.minecraftforge.registries.ForgeRegistries.ITEMS.getKey(output.getItem()).equals(new ResourceLocation("dynasty",id))&&output.getCount()==1,"Actual native original crafting result, no substitute or new item");
                menu.getSlot(0).onTake(p,output);for(int slot=1;slot<=n;slot++)h.assertTrue(menu.getSlot(slot).getItem().isEmpty(),"Native ResultSlot consumes each actual ingredient once, including duplicated ingredient slots");h.assertTrue(menu.getSlot(0).getItem().isEmpty(),"Empty crafting grid cannot replay result");
                h.assertTrue(TalismanDiscovery.details(id).length==3&&DynastyCodex.find(id)!=null,"Shared JEI source/use/single-use information exists; actual client display pending");p.closeContainer();
            }
            int xp=p.totalExperience;ContentProgress.reconcile(p);ContentProgress.reconcile(p);h.assertTrue(p.totalExperience==xp&&p.getInventory().getItem(10).getCount()==1,"Repeated discovery pays no item/XP and consumes no source paper");h.succeed();
        }finally{p.closeContainer();p.discard();}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_talisman_native_old_owned",setupTicks=20)
    public static void originalOwnedTalismanNativePlayerReloadReconcilesOnlyExistingRecipeWithoutNewGateOrReward(GameTestHelper h){
        var p=player(h);var q=player(h);try{
            var charm=new ItemStack(DynastyFineItems.VAJRA_TALISMAN.get(),3);charm.getOrCreateTag().putString("ForeignTalismanData","kept");p.getInventory().setItem(10,charm);
            var saved=new CompoundTag();p.saveWithoutId(saved);q.load(saved);ContentProgress.login(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedInEvent(q));
            h.assertTrue(q.getRecipeBook().contains(new ResourceLocation("dynasty","vajra_talisman"))&&!q.getRecipeBook().contains(new ResourceLocation("dynasty","fire_talisman")),"Actual old owned stack/native NBT load backfills only its existing recipe; no unrelated blanket unlock");
            h.assertTrue(ItemStack.isSameItemSameTags(q.getInventory().getItem(10),charm)&&q.getInventory().getItem(10).getCount()==3,"Original item count and foreign NBT unchanged on login reconciliation");h.succeed();
        }finally{p.discard();q.discard();}
    }
}
