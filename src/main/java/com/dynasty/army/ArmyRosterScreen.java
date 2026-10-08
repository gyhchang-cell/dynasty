package com.dynasty.army;
import com.dynasty.Dynasty;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.MenuScreens;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
@Mod.EventBusSubscriber(modid=Dynasty.MODID,bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class ArmyRosterScreen extends AbstractContainerScreen<ArmyMenu> {
    private int page;
    private boolean encounters,formation;
    private int lastFormation=-1;
    @SubscribeEvent public static void setup(FMLClientSetupEvent e){e.enqueueWork(()->MenuScreens.register(ArmyContent.MENU.get(),ArmyRosterScreen::new));}
    public ArmyRosterScreen(ArmyMenu menu,Inventory inv,Component title){super(menu,inv,title);imageWidth=312;imageHeight=244;}
    private void send(int action){if(minecraft!=null&&minecraft.gameMode!=null)minecraft.gameMode.handleInventoryButtonClick(menu.containerId,(menu.view.get(2)<<8)|action);}
    private void button(int x,int y,int w,String label,int action){addRenderableWidget(Button.builder(Component.literal(label),b->send(action)).bounds(leftPos+x,topPos+y,w,18).build());}
    @Override protected void init(){super.init();
        addRenderableWidget(Button.builder(Component.literal(encounters?"兵册":"关卡"),b->{encounters=!encounters;rebuildWidgets();}).bounds(leftPos+258,topPos+5,45,16).build());
        addRenderableWidget(Button.builder(Component.literal(formation?"兵册":"阵图"),b->{formation=!formation;encounters=false;rebuildWidgets();}).bounds(leftPos+210,topPos+5,45,16).build());
        if(encounters) {
            for(int i=0;i<6;i++)button(12,45+i*23,288,ArmyEncounters.NAMES[i],130+i);
            button(12,200,140,"部署后开战",200);button(160,200,140,"撤离战区",201);return;
        }
        for(int i=0;i<3;i++)button(8+i*99,27,96,ArmyRoster.ROLES[i]+" "+ArmyRoster.PRICE[i]+"银",i);
        for(int i=0;i<9;i++){final int row=i;addRenderableWidget(Button.builder(Component.literal(formation?"选":"编入/移出/修整"),b->send((formation?150:40)+page*9+row)).bounds(leftPos+(formation?174:200),topPos+50+i*15,formation?22:104,14).build());}
        if(formation) {
            var points=new java.util.ArrayList<net.minecraft.world.phys.Vec3>();
            for(int i=0;i<9;i++)points.add(ArmyRoster.slot(net.minecraft.world.phys.Vec3.ZERO,0,i,menu.view.get(3)));
            double minX=points.stream().mapToDouble(p->p.x).min().orElse(0),maxX=points.stream().mapToDouble(p->p.x).max().orElse(1);
            double minZ=points.stream().mapToDouble(p->p.z).min().orElse(0),maxZ=points.stream().mapToDouble(p->p.z).max().orElse(1);
            int width=menu.view.get(3)==3?9:20;
            for(int i=0;i<9;i++){var p=points.get(i);int x=210+(int)((p.x-minX)/Math.max(1,maxX-minX)*82);
                int y=maxZ-minZ<.01?110:150-(int)((p.z-minZ)/(maxZ-minZ)*82);
                button(x-width/2,y,width,Integer.toString(i+1),186+i);}
        }
        button(8,188,55,"快速编队",13);button(67,188,55,"出阵",10);button(126,188,55,"收阵",11);button(185,188,55,"转向",12);
        addRenderableWidget(Button.builder(Component.literal("翻页"),b->{page=(page+1)%4;}).bounds(leftPos+244,topPos+188,60,18).build());
        for(int i=0;i<5;i++)button(8+i*59,208,56,new String[]{"方阵","锋矢阵","分散阵","横阵","环阵"}[i],20+i);
        for(int i=0;i<3;i++){button(8+i*98,226,45,"存"+(i+1),100+i);button(54+i*98,226,45,"读"+(i+1),110+i);}
    }
    @Override protected void renderBg(GuiGraphics g,float partial,int x,int y){g.fill(leftPos,topPos,leftPos+imageWidth,topPos+imageHeight,0xff172127);g.fill(leftPos+4,topPos+4,leftPos+imageWidth-4,topPos+23,0xff514634);}
    @Override protected void renderLabels(GuiGraphics g,int x,int y){
        g.drawString(font,title,8,8,0xffe6cf98,false);g.drawString(font,"银 "+menu.view.get(1)+" · "+menu.view.get(0)+"/36",118,8,0xffffff,false);
        if(encounters){g.drawString(font,"科举中第解锁 · 全军覆没判败 · 开战后锁定兵册",10,28,0xe6cf98,false);return;}
        for(int i=0;i<9;i++){int n=page*9+i;if(n>=menu.view.get(0))continue;int flags=menu.view.get(8+n*3),slot=flags%32;
            String state=flags>=128?"收阵中":flags>=64?"重伤":flags>=32?"出战":"预备";
            int role=Math.max(0,Math.min(2,menu.view.get(6+n*3)));
            g.drawString(font,"#"+(n+1)+" "+ArmyRoster.ROLES[role]+" "+menu.view.get(7+n*3)+"血 "+state+(slot>0?" 位"+slot:""),8,53+i*15,menu.view.get(114)==n?0xffd27b:0xd9e5eb,false);
        }
        if(formation){g.drawString(font,"↑ 敌方",220,48,0xe6cf98,false);g.drawString(font,"↓ 主将",220,165,0xe6cf98,false);}
        g.drawString(font,"阵型 "+(menu.view.get(3)+1)+" · "+(page+1)+"/4页 · 在募兵台支付/修整",8,181,0xb9c8d0,false);
    }
    @Override protected void containerTick(){super.containerTick();if(formation&&lastFormation!=menu.view.get(3)){lastFormation=menu.view.get(3);rebuildWidgets();}}
    @Override public void render(GuiGraphics g,int x,int y,float partial){renderBackground(g);super.render(g,x,y,partial);renderTooltip(g,x,y);}
}
