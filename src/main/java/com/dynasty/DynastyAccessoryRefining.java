package com.dynasty;

import java.util.*;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageTypes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.AnvilUpdateEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.registries.ForgeRegistries;

/** Stack-owned refinement; vanilla anvil consumes material and XP on taking output. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class DynastyAccessoryRefining {
    public static final String KEY="DynastyAccessoryRefinement";
    public static int level(ItemStack stack) {
        return stack.hasTag() ? Math.max(0,stack.getTag().getInt(KEY)) : 0;
    }
    public static boolean eligible(ItemStack stack) {
        String id=DynastyTrinkets.idOf(stack);
        return id!=null && DynastyAccessoryData.get(id)!=null;
    }
    public static String material(int level) {
        return level<10 ? "jade" : level<25 ? "dragon_crystal" : level<50 ? "xuantian_jade" : "sky_token";
    }
    public static int materialCost(int level) { return 1+(int)Math.min(63,(long)level/4); }
    public static int xpCost(int level) { return 2+(int)Math.min(37,(long)level); }
    public static double bonus(int level) { return .04*Math.sqrt(Math.max(0,level)); }

    @SubscribeEvent
    public static void anvil(AnvilUpdateEvent event) {
        ItemStack base=event.getLeft();
        if(!eligible(base) || base.getCount()!=1 || event.getRight().isEmpty()) return;
        int rank=level(base);
        var key=ForgeRegistries.ITEMS.getKey(event.getRight().getItem());
        if(!new ResourceLocation(Dynasty.MODID,material(rank)).equals(key)) return;
        if(rank==Integer.MAX_VALUE || event.getRight().getCount()<materialCost(rank)) {
            event.setCanceled(true); return;
        }
        ItemStack out=base.copy();
        out.getOrCreateTag().putInt(KEY,rank+1);
        if(event.getName()!=null) {
            if(event.getName().isBlank()) out.resetHoverName();
            else if(!event.getName().equals(base.getHoverName().getString())) out.setHoverName(Component.literal(event.getName()));
        }
        event.setOutput(out); event.setCost(xpCost(rank)); event.setMaterialCost(materialCost(rank));
    }

    static List<ItemStack> equipped(Player player) {
        List<ItemStack> stacks=new ArrayList<>();
        if(DynastyCuriosSetup.isLoaded()) DynastyCuriosSetup.collectStacks(player,stacks);
        else { stacks.addAll(player.getInventory().items); stacks.add(player.getOffhandItem()); }
        return stacks;
    }
    static double damageBonus(Player player, DamageSource source) {
        boolean melee=source.is(DamageTypes.PLAYER_ATTACK) && source.getDirectEntity()==player;
        boolean arrow=source.getDirectEntity() instanceof AbstractArrow a && a.getOwner()==player;
        String weapon=DynastySchoolCombat.weapon(player);
        boolean edict=Set.of("chiling_brush","leifu_staff","taiyi_sword","taiyi_whisk","hunyuan_staff","zhuque_fan").contains(weapon);
        Map<String,Integer> best=new HashMap<>();
        for(ItemStack stack:equipped(player)) if(eligible(stack))
            best.merge(DynastyTrinkets.idOf(stack),level(stack),Math::max);
        double result=0;
        for(var entry:best.entrySet()) {
            String school=DynastyAccessoryData.get(entry.getKey()).school();
            if(switch(school) {case "archer" -> arrow; case "talisman" -> (melee || EdictSpells.isSpell(source)) && edict; default -> melee;})
                result+=bonus(entry.getValue());
        }
        return result;
    }
    public static void tooltip(ItemStack stack, List<Component> brief, List<Component> details) {
        if(!eligible(stack)) return;
        int rank=level(stack);
        brief.add(Component.literal("淬炼 +"+rank).withStyle(ChatFormatting.BLUE));
    }
    @SubscribeEvent
    public static void milestones(TickEvent.PlayerTickEvent event) {
        if(event.phase!=TickEvent.Phase.END || !(event.player instanceof ServerPlayer player) || player.tickCount%20!=0) return;
        List<ItemStack> held=new ArrayList<>(player.getInventory().items);
        held.add(player.getOffhandItem()); held.addAll(equipped(player));
        for(ItemStack stack:held) if(eligible(stack)) {
            String school=DynastyAccessoryData.get(DynastyTrinkets.idOf(stack)).school();
            for(int target:new int[]{1,5,15,30}) if(level(stack)>=target) {
                var adv=player.server.getAdvancements().getAdvancement(new ResourceLocation(Dynasty.MODID,"refine_"+school+"_"+target));
                if(adv!=null && !player.getAdvancements().getOrStartProgress(adv).isDone()) player.getAdvancements().award(adv,"refined");
            }
        }
    }
}
