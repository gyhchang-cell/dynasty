package com.dynasty.client;

import com.dynasty.Dynasty;
import com.dynasty.workshop.*;
import net.minecraft.client.gui.*;
import net.minecraft.client.gui.screens.MenuScreens;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

/** Dark lacquer/bronze with eight different process diagrams; no fake tanks or temperatures. */
public final class WorkshopScreen extends AbstractContainerScreen<WorkshopMenu> {
    public WorkshopScreen(WorkshopMenu menu,Inventory inv,Component title){super(menu,inv,title);imageWidth=176;imageHeight=166;inventoryLabelY=73;}
    @Mod.EventBusSubscriber(modid=Dynasty.MODID,bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
    public static final class Registration {
        @SubscribeEvent public static void setup(FMLClientSetupEvent e){e.enqueueWork(()->MenuScreens.register(WorkshopMenu.TYPE.get(),WorkshopScreen::new));}
    }
    @Override protected void renderBg(GuiGraphics g,float partial,int mx,int my){
        int x=leftPos,y=topPos,n=menu.deposited(),total=menu.total();double progress=(double)n/total;
        g.fill(x,y,x+176,y+166,0xff403a2b);g.fill(x+2,y+2,x+174,y+164,0xff181e20);
        g.fill(x+5,y+70,x+171,y+71,0xff56635b);
        for(var s:menu.slots){int sx=x+s.x,sy=y+s.y;g.fill(sx-1,sy-1,sx+17,sy+17,0xff81704b);g.fill(sx,sy,sx+16,sy+16,0xff293033);}
        int cx=x+92,cy=y+54,color=n==total?0xffd8bc70:0xff76b9a5;
        switch(menu.station.recipe().kind()) {
            case MARROW -> {g.fill(cx-21,cy-11,cx+21,cy+9,0xff4a595c);for(int i=0;i<3;i++)if(progress>i/3.)g.fill(cx-18,cy+5-i*5,cx+18,cy+9-i*5,color);}
            case ESSENCE -> {g.fill(cx-8,cy-14,cx+8,cy+10,0xff405966);g.fill(cx-5,cy+8-(int)(22*progress),cx+5,cy+8,color);for(int i=0;i<n;i++)g.fill(cx-20+i*4,cy-12,cx-18+i*4,cy-10,color);}
            case REPAIR -> {for(int i=0;i<12;i++){int sx=cx-18+i%6*6,sy=cy-9+i/6*10;g.fill(sx,sy,sx+4,sy+7,i<progress*12?color:0xff3e4948);}}
            case VITALITY -> {g.fill(cx-14,cy-7,cx+14,cy+9,0xff556253);g.fill(cx-18,cy-10,cx+18,cy-7,color);g.fill(cx-2,cy-14-(int)(4*progress),cx+2,cy-11,color);}
            case HIDE -> {g.fill(cx-22,cy-11,cx+22,cy+11,0xff605447);int w=8+(int)(12*progress);g.fill(cx-w,cy-8,cx+w,cy+8,0xffaf9372);}
            case HERBAL -> {g.fill(cx-22,cy-3,cx+22,cy+10,0xff47544d);g.fill(cx-19,cy+8-(int)(10*progress),cx+19,cy+8,0xff7ea36b);}
            case LAPIDARY -> {g.fill(cx-20,cy+6,cx+20,cy+10,0xff60594c);g.fill(cx-11,cy-9,cx+11,cy+5,0xff548777);for(int i=0;i<progress*5;i++)g.fill(cx-9+i*4,cy-6,cx-7+i*4,cy+2,color);}
            case EMBER -> {for(int i=0;i<5;i++){int height=3+(int)(progress*(10-i));g.fill(cx-12+i*5,cy+8-height,cx-9+i*5,cy+8,0xffaa5b3b+i*0x050500);}}
        }
        g.fill(x+30,y+66,x+142,y+68,0xff3c4445);g.fill(x+30,y+66,x+30+(int)(112*progress),y+68,color);
    }
    @Override protected void renderLabels(GuiGraphics g,int mx,int my){g.drawString(font,title,8,6,0xd8d0b6,false);g.drawString(font,playerInventoryTitle,8,73,0xb9c3bc,false);g.drawString(font,menu.deposited()+" / "+menu.total(),8,52,0xc5d1c6,false);}
    @Override public void render(GuiGraphics g,int mx,int my,float partial){
        renderBackground(g);super.render(g,mx,my,partial);renderTooltip(g,mx,my);
        if(mx>=leftPos+60&&mx<leftPos+120&&my>=topPos+42&&my<topPos+65){
            var next=menu.station.recipe().next(menu.deposited());
            if(next!=null)g.renderTooltip(font,Component.translatable("workshop.dynasty.next",next.stack().getHoverName(),menu.deposited(),menu.total()),mx,my);
        }
    }
}
