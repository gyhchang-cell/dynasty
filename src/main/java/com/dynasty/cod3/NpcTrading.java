package com.dynasty.cod3;

import com.dynasty.Dynasty;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.inventory.MenuType;
import net.minecraft.world.inventory.MerchantMenu;
import net.minecraftforge.common.extensions.IForgeMenuType;
import net.minecraftforge.network.NetworkHooks;
import net.minecraftforge.registries.*;

/** Native merchant offers and paid services share one NPC and the same server authority. */
public final class NpcTrading {
    public static final DeferredRegister<MenuType<?>> MENUS=DeferredRegister.create(ForgeRegistries.MENU_TYPES,Dynasty.MODID);
    public static final RegistryObject<MenuType<MerchantMenu>> TRADE=MENUS.register("npc_trade",()->IForgeMenuType.create(NpcTradeMenu::new));
    public static final RegistryObject<MenuType<NpcServiceMenu>> SERVICE=MENUS.register("npc_service",()->IForgeMenuType.create(NpcServiceMenu::new));
    public static boolean open(ServerPlayer player,DynastyNpcEntity npc,int page){
        if(page<0||page>2||!npc.canTrade(player))return false;
        npc.ensureContentTrades();
        if(page==0){
            NetworkHooks.openScreen(player,new SimpleMenuProvider((id,inv,p)->new NpcTradeMenu(id,inv,npc),npc.getDisplayName()),buf->buf.writeInt(npc.getId()));
            npc.setTradingPlayer(player);
            player.sendMerchantOffers(player.containerMenu.containerId,npc.getOffers(),1,npc.getVillagerXp(),false,false);
        }else{
            NetworkHooks.openScreen(player,new SimpleMenuProvider((id,inv,p)->new NpcServiceMenu(id,inv,npc,page),npc.getDisplayName()),buf->{buf.writeInt(npc.getId());buf.writeByte(page);});
            npc.setTradingPlayer(player);
        }
        npc.beginConversation(player);return true;
    }
    public static boolean dialogue(ServerPlayer player,DynastyNpcEntity npc){
        if(!npc.canTrade(player))return false;
        player.closeContainer();NpcDialogue.open(player,npc);return true;
    }
    private NpcTrading(){}
}
