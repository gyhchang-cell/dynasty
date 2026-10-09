package com.dynasty.expansion;

import com.dynasty.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraft.world.item.trading.*;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.*;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Existing minister gains an optional vanilla merchant screen; unlocks remain player advancements. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class ProgressionMerchant implements Merchant {
    private static final net.minecraft.world.entity.npc.VillagerTrades.ItemListing KAPPA_TRADE=(trader,random)->
            new MerchantOffer(new ItemStack(ExpansionContent.MATERIALS.get("kappa_scale").get(),2),new ItemStack(Items.EMERALD),12,5,.05F);
    @SubscribeEvent public static void fishermanTrades(net.minecraftforge.event.village.VillagerTradesEvent e){
        if(e.getType()==net.minecraft.world.entity.npc.VillagerProfession.FISHERMAN&&!e.getTrades().get(2).contains(KAPPA_TRADE))e.getTrades().get(2).add(KAPPA_TRADE);
    }
    /** Existing native villagers keep all saved prices/stock; only the missing offer is appended. */
    public static void ensureFishermanTrade(net.minecraft.world.entity.npc.Villager villager){
        if(villager.level().isClientSide||villager.getVillagerData().getProfession()!=net.minecraft.world.entity.npc.VillagerProfession.FISHERMAN||villager.getVillagerData().getLevel()<2)return;
        var offers=villager.getOffers();
        if(offers.stream().noneMatch(o->o.getBaseCostA().is(ExpansionContent.MATERIALS.get("kappa_scale").get())&&o.getResult().is(Items.EMERALD)))offers.add(KAPPA_TRADE.getOffer(villager,villager.getRandom()));
    }
    @SubscribeEvent public static void fishermanLoaded(net.minecraftforge.event.entity.EntityJoinLevelEvent e){
        if(e.getEntity() instanceof net.minecraft.world.entity.npc.Villager villager)ensureFishermanTrade(villager);
    }
    private Player customer;
    private MerchantOffers offers=new MerchantOffers();
    private final ServerPlayer owner;
    ProgressionMerchant(ServerPlayer player) {
        owner=player;customer=player;
        if(done("cod4_obtain_heart_mirror"))offer("heart_mirror",32);
        if(done("entered_dragon_palace"))offer("sea_pearl",48);
        if(DynastyStats.getRank(player)>=3 || DynastySchoolProgression.rank(player,"guard")>=3) {
            offer("qimen_cable",8);offer("qimen_gear",8);offer("rope_dart",48);offer("flying_claw",48);offer("meteor_hammer",64);offer("mandarin_duck_axe",64);
        }
    }
    private boolean done(String id) {var a=owner.server.getAdvancements().getAdvancement(new ResourceLocation("dynasty",id));return a!=null && owner.getAdvancements().getOrStartProgress(a).isDone();}
    private String stockKey(ItemStack result) {return "stock_"+EquipmentBehaviors.id(result);}
    private void offer(String item,int coins) {
        ItemStack output=new ItemStack(ExpansionContent.item(item));
        var n=EquipmentBehaviors.saved(owner);long day=owner.level().getGameTime()/24000;
        if(n.getLong("stockDay")!=day){n.putLong("stockDay",day);for(String id:java.util.List.of("heart_mirror","sea_pearl","qimen_cable","qimen_gear","rope_dart","flying_claw","meteor_hammer","mandarin_duck_axe"))n.remove("stock_"+id);}
        var offer=new MerchantOffer(new ItemStack(ExpansionContent.item("copper_coin"),coins),ItemStack.EMPTY,output,n.getInt(stockKey(output)),8,0,0);offers.add(offer);
    }
    @SubscribeEvent public static void interact(PlayerInteractEvent.EntityInteract e) {
        if(e.getTarget() instanceof net.minecraft.world.entity.npc.Villager villager)ensureFishermanTrade(villager);
        if(e.getHand()!=net.minecraft.world.InteractionHand.MAIN_HAND || !(e.getEntity() instanceof ServerPlayer p) || !p.isShiftKeyDown() || !(e.getTarget() instanceof com.dynasty.entity.DynastyMobs.Minister))return;
        var merchant=new ProgressionMerchant(p);if(merchant.offers.isEmpty())return;
        merchant.openTradingScreen(p,Component.translatable("merchant.dynasty.cod4"),1);e.setCanceled(true);e.setCancellationResult(net.minecraft.world.InteractionResult.SUCCESS);
    }
    @Override public void setTradingPlayer(Player p){customer=p;}
    @Override public Player getTradingPlayer(){return customer;}
    @Override public MerchantOffers getOffers(){return offers;}
    @Override public void overrideOffers(MerchantOffers offers){this.offers=offers;}
    @Override public void notifyTrade(MerchantOffer offer){offer.increaseUses();EquipmentBehaviors.saved(owner).putInt(stockKey(offer.getResult()),offer.getUses());}
    @Override public void notifyTradeUpdated(ItemStack s){}
    @Override public int getVillagerXp(){return 0;}
    @Override public void overrideXp(int xp){}
    @Override public boolean showProgressBar(){return false;}
    @Override public SoundEvent getNotifyTradeSound(){return SoundEvents.VILLAGER_YES;}
    @Override public boolean isClientSide(){return false;}
}
