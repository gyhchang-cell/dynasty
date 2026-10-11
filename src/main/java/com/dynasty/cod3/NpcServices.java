package com.dynasty.cod3;

import com.dynasty.DynastyStats;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraftforge.registries.ForgeRegistries;

/** Transactions are executed only by a live, revalidated per-player dialogue choice. */
public final class NpcServices {
    public static boolean repair(ServerPlayer player,DynastyNpcEntity npc){
        if(!context(player,npc,"lao_chen"))return false;
        var tool=player.getMainHandItem();
        var coin=ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty:copper_coin"));
        if(!tool.isDamageableItem()||tool.getDamageValue()==0||coin==null||coin==Items.AIR||player.getInventory().items.stream().filter(stack->stack.is(coin)).mapToInt(ItemStack::getCount).sum()<4){
            player.displayClientMessage(Component.translatable("cod3.dynasty.service.repair.failure"),true);return false;
        }
        int left=4;
        for(var stack:player.getInventory().items)if(stack.is(coin)){
            int take=Math.min(left,stack.getCount());stack.shrink(take);left-=take;if(left==0)break;
        }
        tool.setDamageValue(Math.max(0,tool.getDamageValue()-Math.max(1,tool.getMaxDamage()/4)));
        player.getInventory().setChanged();player.displayClientMessage(Component.translatable("cod3.dynasty.service.repair.success"),true);
        npc.beginConversation(player);Cod3Vfx.send(player.serverLevel(),27,npc.position().add(0,1,0),npc.getLookAngle(),12,.15,0xEBC370);return true;
    }
    public static boolean commemorate(ServerPlayer player,DynastyNpcEntity npc){
        if(!context(player,npc,"han_chong"))return false;
        var roster=ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty:bamboo_slip"));
        var reward=ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation("dynasty:refined_steel"));
        var saved=player.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG);
        if(saved.getBoolean("cod3_roster_memorial")||!player.getMainHandItem().is(roster)||reward==null||reward==Items.AIR){
            player.displayClientMessage(Component.translatable("cod3.dynasty.service.memorial.failure"),true);return false;
        }
        player.getMainHandItem().shrink(1);saved.putBoolean("cod3_roster_memorial",true);player.getPersistentData().put(Player.PERSISTED_NBT_TAG,saved);
        var steel=new ItemStack(reward);if(!player.getInventory().add(steel))player.drop(steel,false);
        DynastyStats.addMerit(player,10);player.getInventory().setChanged();npc.beginConversation(player);
        player.displayClientMessage(Component.translatable("cod3.dynasty.service.memorial.success"),false);return true;
    }
    private static boolean context(ServerPlayer p,DynastyNpcEntity npc,String role){return npc.role.equals(role)&&npc.isAlive()&&p.isAlive()&&!p.isSpectator()&&p.level()==npc.level()&&p.distanceToSqr(npc)<=36&&(!npc.isTrading()||npc.getTradingPlayer()==p);}
    private NpcServices(){}
}
