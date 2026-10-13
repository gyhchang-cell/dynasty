package com.dynasty.cod3;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.*;
import net.minecraft.world.inventory.*;

/** Remains a MerchantMenu so vanilla stock, trade selection and result accounting are retained. */
public final class NpcTradeMenu extends MerchantMenu {
    private final DynastyNpcEntity npc;
    public NpcTradeMenu(int id,Inventory inventory,FriendlyByteBuf buf){
        super(id,inventory);var entity=inventory.player.level().getEntity(buf.readInt());npc=entity instanceof DynastyNpcEntity n?n:null;
    }
    public NpcTradeMenu(int id,Inventory inventory,DynastyNpcEntity npc){super(id,inventory,npc);this.npc=npc;}
    @Override public MenuType<?> getType(){return NpcTrading.TRADE.get();}
    @Override public boolean stillValid(Player player){return player.level().isClientSide||npc!=null&&npc.getTradingPlayer()==player&&npc.canTrade(player);}
    @Override public boolean clickMenuButton(Player player,int button){
        if(!(player instanceof ServerPlayer server)||player.containerMenu!=this||!stillValid(player))return false;
        if(button==3)return NpcTrading.dialogue(server,npc);
        return button>=1&&button<=2&&NpcTrading.open(server,npc,button);
    }
}
