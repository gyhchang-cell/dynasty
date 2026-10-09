package com.dynasty.expansion;

import com.dynasty.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.*;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/** Existing advancements and recipe book own progress. Reconcile old saves from inventory and ranks. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class ContentProgress {
    public static void reconcile(ServerPlayer p) {
        DynastySchoolProgression.reconcile(p);
        Set<String> obtained=new HashSet<>();
        for(ItemStack stack:p.getInventory().items)obtained.add(EquipmentBehaviors.id(stack));
        for(ItemStack stack:p.getArmorSlots())obtained.add(EquipmentBehaviors.id(stack));
        obtained.addAll(DynastyTrinkets.activeIds(p));
        for(String id:obtained) {
            if(id.isEmpty() || ExpansionContent.SUPPLIES.containsKey(id))continue;
            DynastyAdvancements.award(p,"cod4_obtain_"+id);
        }
        if(DynastyStats.getRank(p)>=3 && !EquipmentBehaviors.saved(p).getBoolean("crownGranted")) {
            EquipmentBehaviors.saved(p).putBoolean("crownGranted",true);
            if(!obtained.contains("jade_crown")) {var gift=new ItemStack(ExpansionContent.item("jade_crown"));if(!p.getInventory().add(gift))p.drop(gift,false);}
            obtained.add("jade_crown");
        }
        if(obtained.contains("silk_pouch"))DynastySlotProgression.unlock(p,"cod4_silk");
        if(obtained.contains("jade_crown") && DynastyStats.getRank(p)>=3)DynastySlotProgression.unlock(p,"cod4_crown");
        if(done(p,"slay_dragon_emperor"))unlockExisting(p,"dragon_scale_charm");
        if(obtained.contains("jade_pendant")){unlockExisting(p,"jade_bi_disc");unlockExisting(p,"jade_ring");}
        for(String element:List.of("qinglong","baihu","zhuque","xuanwu"))if(done(p,"ritual_"+element)) {
            String weapon=switch(element){case "qinglong"->"qinglong_dao";case "baihu"->"baihu_glaive";case "zhuque"->"zhuque_fan";default->"xuanwu_blade";};unlockExisting(p,weapon);
        }
        if(DynastySchoolProgression.rank(p,"archer")>=6)unlock(p,"repeating_crossbow");
        if(DynastySchoolProgression.rank(p,"archer")>=10)unlock(p,"siege_crossbow");
        if(DynastyStats.getRank(p)>=3 || DynastySchoolProgression.rank(p,"guard")>=3) {
            for(String id:List.of("rope_dart","meteor_hammer","mandarin_duck_axe","flying_claw"))unlock(p,id);
        }
        for(String id:ExpansionContent.SUPPLIES.keySet())unlock(p,id);
        for(String id:ExpansionContent.AMMO.keySet())unlock(p,id);
        unlock(p,"qimen_cable");unlock(p,"qimen_gear");
    }
    private static boolean done(ServerPlayer p,String id){var a=p.server.getAdvancements().getAdvancement(new ResourceLocation("dynasty",id));return a!=null&&p.getAdvancements().getOrStartProgress(a).isDone();}
    private static void unlockExisting(ServerPlayer p,String id) {var key=new ResourceLocation("dynasty",id);if(p.server.getRecipeManager().byKey(key).isPresent())p.awardRecipesByKey(new ResourceLocation[]{key});}
    private static void unlock(ServerPlayer p,String id) {p.awardRecipesByKey(new ResourceLocation[]{new ResourceLocation("dynasty","cod4/"+id)});}
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e) {if(e.phase==TickEvent.Phase.END && e.player instanceof ServerPlayer p && p.tickCount%100==0)reconcile(p);}
    /** Keep legacy advancement IDs and completed rewards; new progress requires actual crafting. */
    @SubscribeEvent public static void crafted(PlayerEvent.ItemCraftedEvent e) {
        if(e.getEntity() instanceof ServerPlayer p && !e.getCrafting().isEmpty()) {
            String id=EquipmentBehaviors.id(e.getCrafting());
            if(ExpansionContent.SUPPLIES.containsKey(id))DynastyAdvancements.award(p,"cod4_obtain_"+id);
        }
    }
    @SubscribeEvent public static void login(PlayerEvent.PlayerLoggedInEvent e) {if(e.getEntity() instanceof ServerPlayer p)reconcile(p);}
    @SubscribeEvent public static void clone(PlayerEvent.Clone e) {
        if(e.getOriginal().getPersistentData().contains(Player.PERSISTED_NBT_TAG))e.getEntity().getPersistentData().put(Player.PERSISTED_NBT_TAG,e.getOriginal().getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).copy());
    }
    /** Unseen outcomes until every accessory has appeared; only then return to the legacy weighted pool. */
    public static ItemStack gift(Player p) {
        var saved=EquipmentBehaviors.saved(p);var opened=saved.getCompound("openedTrinkets");
        List<Item> pool=new ArrayList<>();
        for(String id:DynastyTrinkets.IDS)if(!opened.getBoolean(id)) {
            Item item=ExpansionContent.item(id);if(item!=null && item!=Items.AIR)pool.add(item);
        }
        ItemStack gift=pool.isEmpty()?DynastyTrinkets.randomGift(p.getRandom()):new ItemStack(pool.get(p.getRandom().nextInt(pool.size())));
        opened.putBoolean(EquipmentBehaviors.id(gift),true);saved.put("openedTrinkets",opened);return gift;
    }
    private ContentProgress() { }
}
