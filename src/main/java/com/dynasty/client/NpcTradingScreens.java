package com.dynasty.client;

import com.dynasty.Dynasty;
import com.dynasty.cod3.*;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.client.gui.screens.MenuScreens;
import net.minecraft.client.gui.screens.inventory.*;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.inventory.MerchantMenu;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

@Mod.EventBusSubscriber(modid=Dynasty.MODID,bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class NpcTradingScreens {
    @SubscribeEvent public static void setup(FMLClientSetupEvent event){event.enqueueWork(()->{
        MenuScreens.register(NpcTrading.TRADE.get(),Trades::new);MenuScreens.register(NpcTrading.SERVICE.get(),Services::new);
    });}
    private static Component text(String key){return Component.translatable("npc.dynasty.shop."+key);}
    /** Full vanilla villager screen: all existing offers, native input/result slots and scrolling. */
    public static final class Trades extends MerchantScreen {
        public Trades(MerchantMenu menu,Inventory inventory,Component title){super(menu,inventory,title);}
        @Override protected void init(){
            super.init();String[] labels={"trade","repair","enchant","dialogue"};
            for(int i=0;i<4;i++){final int page=i;var button=Button.builder(text(labels[i]),b->minecraft.gameMode.handleInventoryButtonClick(menu.containerId,page))
                    .bounds(leftPos+i*69,topPos-24,67,20).build();button.active=i!=0;addRenderableWidget(button);}
        }
    }
    public static final class Services extends AbstractContainerScreen<NpcServiceMenu> {
        private Button submit;
        private final Button[] tabs=new Button[4];
        public Services(NpcServiceMenu menu,Inventory inventory,Component title){super(menu,inventory,title);imageWidth=276;imageHeight=193;inventoryLabelX=56;inventoryLabelY=100;}
        @Override protected void init(){
            super.init();topPos=Math.max(24,topPos);String[] labels={"trade","repair","enchant","dialogue"};
            for(int i=0;i<4;i++){final int page=i;tabs[i]=addRenderableWidget(Button.builder(text(labels[i]),b->send(page)).bounds(leftPos+i*69,topPos-24,67,20).build());}
            submit=addRenderableWidget(Button.builder(text("submit"),b->send(20)).bounds(leftPos+94,topPos+77,88,20)
                    .tooltip(Tooltip.create(text("submit_tip"))).build());
        }
        private void send(int button){minecraft.gameMode.handleInventoryButtonClick(menu.containerId,button);}
        @Override protected void containerTick(){super.containerTick();submit.active=menu.status()==0;for(int i=0;i<4;i++)tabs[i].active=i!=menu.page();}
        private void panel(GuiGraphics g,int x,int y,int w,int h){
            g.fill(x,y,x+w,y+h,0xff373737);g.fill(x+1,y+1,x+w-1,y+h-1,0xffeeeeee);g.fill(x+2,y+2,x+w-2,y+h-2,0xffc6c6c6);
            g.fill(x+2,y+h-3,x+w-2,y+h-1,0xff555555);g.fill(x+w-3,y+2,x+w-1,y+h-2,0xff555555);
        }
        @Override protected void renderBg(GuiGraphics g,float partial,int mx,int my){
            panel(g,leftPos,topPos,imageWidth,imageHeight);
            for(var slot:menu.slots){int x=leftPos+slot.x,y=topPos+slot.y;g.fill(x-1,y-1,x+17,y+17,0xff373737);g.fill(x,y,x+17,y+17,0xffeeeeee);g.fill(x,y,x+16,y+16,0xff8b8b8b);}
            int x=leftPos+161,y=topPos+48;g.fill(x,y,x+18,y+4,0xff555555);g.fill(x+14,y-3,x+18,y+7,0xff555555);g.fill(x+18,y-1,x+21,y+5,0xff555555);
        }
        @Override protected void renderLabels(GuiGraphics g,int mx,int my){
            g.drawString(font,font.plainSubstrByWidth(title.getString(),260),8,6,0x404040,false);
            g.drawCenteredString(font,text(menu.page()==1?"repair_desc":"enchant_desc"),138,22,0x404040);
            g.drawCenteredString(font,text("gear"),73,32,0x404040);g.drawCenteredString(font,Component.translatable("npc.dynasty.shop.coins",menu.cost()),127,32,0x404040);
            g.drawCenteredString(font,text("result"),203,32,0x404040);
            g.drawCenteredString(font,text("status."+menu.status()),138,65,menu.status()==0?0x355b35:0x7a3434);
            g.drawString(font,playerInventoryTitle,56,100,0x404040,false);
        }
        @Override public void render(GuiGraphics g,int mx,int my,float partial){renderBackground(g);super.render(g,mx,my,partial);renderTooltip(g,mx,my);}
    }
    private NpcTradingScreens(){}
}
