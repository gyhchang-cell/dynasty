package com.dynasty.expansion;

import com.mojang.authlib.GameProfile;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.npc.*;
import net.minecraft.world.inventory.MerchantMenu;
import net.minecraft.world.item.*;
import net.minecraft.world.item.trading.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class FishermanMaterialGameTests {
    private static Villager villager(GameTestHelper h,VillagerProfession job,int level){var v=new Villager(net.minecraft.world.entity.EntityType.VILLAGER,h.getLevel());v.setVillagerData(v.getVillagerData().setProfession(job).setLevel(level));v.setNoAi(true);v.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(3,2,3))));return v;}
    private static MerchantOffer scale(Villager v){return v.getOffers().stream().filter(o->o.getBaseCostA().is(ExpansionContent.MATERIALS.get("kappa_scale").get())&&o.getResult().is(Items.EMERALD)).findFirst().orElseThrow();}
    private static ServerPlayer player(GameTestHelper h,Villager v){var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"fisher-paid"));p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);p.setPos(v.position());return p;}
    @GameTest(template="bow_ritual_test",batch="cod4_fisher_native",setupTicks=20)
    public static void nativeProfessionLevelPoolRetainsAllExistingListings(GameTestHelper h){
        var nativePool=VillagerTrades.TRADES.get(VillagerProfession.FISHERMAN).get(2);var v=villager(h,VillagerProfession.FISHERMAN,2);
        h.assertTrue(java.util.Arrays.stream(nativePool).anyMatch(listing->{var offer=listing.getOffer(v,v.getRandom());return offer!=null&&offer.getBaseCostA().is(ExpansionContent.MATERIALS.get("kappa_scale").get());}),"Actual server-start native fisherman level-two trade pool contains the registered material trade");
        var lists=new it.unimi.dsi.fastutil.ints.Int2ObjectOpenHashMap<java.util.List<VillagerTrades.ItemListing>>();for(int i=1;i<=5;i++)lists.put(i,new ArrayList<>(java.util.Arrays.asList(VillagerTrades.TRADES.get(VillagerProfession.FARMER).get(i))));
        int original=lists.get(2).size();ProgressionMerchant.fishermanTrades(new net.minecraftforge.event.village.VillagerTradesEvent(lists,VillagerProfession.FARMER));h.assertTrue(lists.get(2).size()==original,"Other native professions retain all exact existing listings");
        ProgressionMerchant.fishermanTrades(new net.minecraftforge.event.village.VillagerTradesEvent(lists,VillagerProfession.FISHERMAN));h.assertTrue(lists.get(2).size()==original+1,"Append exactly one listing without replacing the original pool");ProgressionMerchant.fishermanTrades(new net.minecraftforge.event.village.VillagerTradesEvent(lists,VillagerProfession.FISHERMAN));h.assertTrue(lists.get(2).size()==original+1,"Repeated setup cannot duplicate the registered listing");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_fisher_native",setupTicks=20)
    public static void oldNativeOffersRetainExactStockPricesAndMigrationIsLimitedToFishermen(GameTestHelper h){
        var v=villager(h,VillagerProfession.FISHERMAN,2);var old=new MerchantOffer(new ItemStack(Items.COAL,16),ItemStack.EMPTY,new ItemStack(Items.EMERALD),7,16,10,.05F,3);old.addToSpecialPriceDiff(-2);var offers=new MerchantOffers();offers.add(old);v.setOffers(offers);
        var original=old.createTag();ProgressionMerchant.ensureFishermanTrade(v);int size=v.getOffers().size();for(int i=0;i<20;i++)ProgressionMerchant.ensureFishermanTrade(v);
        h.assertTrue(v.getOffers().size()==size&&size==2&&old.createTag().equals(original),"Old finite stock, demand and special price remain byte-identical while exactly one missing offer is appended");
        var paid=scale(v);paid.increaseUses();paid.addToSpecialPriceDiff(1);var data=v.saveWithoutId(new CompoundTag());var restored=villager(h,VillagerProfession.FISHERMAN,2);restored.load(data);ProgressionMerchant.ensureFishermanTrade(restored);
        h.assertTrue(restored.getOffers().size()==2&&restored.getOffers().get(0).createTag().equals(original)&&scale(restored).getUses()==1&&scale(restored).getSpecialPriceDiff()==1,"Native villager NBT reload retains all old and new stock/price state without resetting a saved material offer");
        for(var job:new VillagerProfession[]{VillagerProfession.FARMER,VillagerProfession.NONE}){var other=villager(h,job,2);other.setOffers(new MerchantOffers());ProgressionMerchant.ensureFishermanTrade(other);h.assertTrue(other.getOffers().isEmpty(),"No material trade is injected into unrelated native profession");}
        var novice=villager(h,VillagerProfession.FISHERMAN,1);novice.setOffers(new MerchantOffers());ProgressionMerchant.ensureFishermanTrade(novice);h.assertTrue(novice.getOffers().isEmpty(),"Original profession level remains a real prerequisite");h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_fisher_paid",setupTicks=20)
    public static void actualNativeMenuChargesScalesAndKeepsFiniteStock(GameTestHelper h){
        var v=villager(h,VillagerProfession.FISHERMAN,2);v.setOffers(new MerchantOffers());h.getLevel().addFreshEntity(v);var p=player(h,v);v.setTradingPlayer(p);v.openTradingScreen(p,v.getDisplayName(),2);
        h.assertTrue(p.containerMenu instanceof MerchantMenu,"Actual vanilla merchant menu opens for the native fisherman");var menu=(MerchantMenu)p.containerMenu;var offer=scale(v);menu.setSelectionHint(v.getOffers().indexOf(offer));
        menu.getSlot(0).set(new ItemStack(ExpansionContent.MATERIALS.get("kappa_scale").get()));h.assertTrue(menu.getSlot(2).getItem().isEmpty()&&menu.quickMoveStack(p,2).isEmpty()&&offer.getUses()==0,"One scale cannot buy output or consume stock");
        menu.getSlot(0).set(new ItemStack(Items.COD,2));h.assertTrue(menu.quickMoveStack(p,2).isEmpty()&&offer.getUses()==0,"Existing fish cannot be mistaken for the new material payment");
        for(int i=0;i<12;i++){menu.getSlot(0).set(new ItemStack(ExpansionContent.MATERIALS.get("kappa_scale").get(),2));h.assertTrue(!menu.quickMoveStack(p,2).isEmpty()&&menu.getSlot(0).getItem().isEmpty()&&offer.getUses()==i+1,"Native paid trade takes two actual scales and increments only its own finite stock");h.assertTrue(menu.quickMoveStack(p,2).isEmpty(),"An empty input cannot replay a native trade");}
        menu.getSlot(0).set(new ItemStack(ExpansionContent.MATERIALS.get("kappa_scale").get(),2));h.assertTrue(menu.quickMoveStack(p,2).isEmpty()&&menu.getSlot(0).getItem().getCount()==2&&p.getInventory().countItem(Items.EMERALD)==12,"Exhausted native stock rejects thirteenth trade without charging");
        p.closeContainer();v.discard();h.succeed();
    }
}
