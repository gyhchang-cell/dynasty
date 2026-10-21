package com.dynasty.army;

import com.dynasty.Dynasty;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.client.gui.screens.MenuScreens;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

/** Presentation only: every operation retains the existing server action and revision protocol. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID,bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class ArmyRosterScreen extends AbstractContainerScreen<ArmyMenu> {
    private static final int ROWS=6;
    private int recruitRole;
    private int observedWindow=-1,pendingPage=-1,pendingRevision=-1;
    private int page,tab,selected=-1,lastSignature=Integer.MIN_VALUE;
    private int sidebar,listWidth,bodyY=53,rowHeight;
    @SubscribeEvent public static void setup(FMLClientSetupEvent e){e.enqueueWork(()->MenuScreens.register(ArmyContent.MENU.get(),ArmyRosterScreen::new));}
    public ArmyRosterScreen(ArmyMenu menu,Inventory inv,Component title){super(menu,inv,title);imageWidth=360;imageHeight=236;if(menu.desk!=null)tab=3;}
    private void send(int action){if(pendingRevision>=0&&action!=80&&action!=81)return;if(minecraft!=null&&minecraft.gameMode!=null)minecraft.gameMode.handleInventoryButtonClick(menu.containerId,(menu.view.get(2)<<8)|action);}
    private Button local(int x,int y,int w,int h,String text,Runnable click){return addRenderableWidget(Button.builder(Component.literal(text),b->click.run()).bounds(leftPos+x,topPos+y,w,h).build());}
    private Button action(int x,int y,int w,int h,String text,int code){return local(x,y,w,h,text,()->send(code));}
    private int count(){return Math.max(0,menu.total());}
    private int flags(int n){return menu.view.get(8+n*3);}
    private int role(int n){return Math.max(0,Math.min(2,menu.view.get(6+n*3)));}
    private String state(int n){int f=flags(n);return f>=128?"收阵中":f>=64?"重伤":f>=32?"出战":f%32>0?"已编入":"预备";}
    private boolean deployed(){return menu.view.get(118)==1;}
    private void availability(Button b,boolean active,String reason){b.active=active;if(!active)b.setTooltip(Tooltip.create(Component.literal(reason)));}
    @Override protected void init(){
        imageWidth=Math.max(280,Math.min(360,width-20));imageHeight=Math.max(212,Math.min(236,height-16));super.init();
        sidebar=imageWidth-126;listWidth=sidebar-16;rowHeight=Math.max(17,(imageHeight-104)/ROWS);page=Math.min(page,Math.max(0,(Math.min(36,count()-menu.window()*36)-1)/ROWS));
        for(int i=0;i<(menu.desk!=null?4:3);i++){final int next=i;local(10+i*58,28,54,18,new String[]{"兵册","军阵","关卡","募兵"}[i],()->{tab=next;rebuildWidgets();});}
        local(imageWidth-29,7,20,16,"×",this::onClose);
        if(tab==3){
            for(int i=0;i<3;i++){final int role=i;local(12,58+i*39,listWidth-4,33,ArmyRoster.ROLES[i]+"   "+ArmyRoster.PRICE[i]+"银",()->{recruitRole=role;rebuildWidgets();});}
            int price=ArmyRoster.PRICE[recruitRole];
            availability(action(sidebar+6,imageHeight-48,104,28,"确认购买 · "+price+"银",recruitRole),menu.view.get(4)==1&&menu.view.get(5)!=2&&menu.balance()>=price,menu.balance()<price?"银两不足":"战斗中不能募兵");
            return;
        }
        if(tab==2){
            for(int i=0;i<6;i++){int y=56+(i/2)*26,x=10+(i%2)*(imageWidth/2);action(x,y,imageWidth/2-20,24,ArmyEncounters.NAMES[i],130+i);}
            action(10,imageHeight-58,(imageWidth-26)/2,22,"部署后开战",200);
            action(16+(imageWidth-26)/2,imageHeight-58,(imageWidth-26)/2,22,menu.view.get(115)==1?"确认认输":"撤离战区",201);return;
        }
        boolean locked=deployed()||menu.view.get(5)==2;
        for(int i=0;i<ROWS;i++){
            int n=page*ROWS+i;if(menu.window()*36+n>=count())break;
            String label="#"+(menu.window()*36+n+1)+" "+ArmyRoster.ROLES[role(n)]+"  "+menu.view.get(7+n*3)+"血  "+state(n);
            local(10,bodyY+i*rowHeight,listWidth,rowHeight-2,label,()->{selected=n;if(tab==1)send(150+n);rebuildWidgets();});
        }
        int pagerY=imageHeight-47;
        local(10,pagerY,24,16,"‹",()->{if(page>0)page--;else{pendingPage=5;pendingRevision=menu.view.get(2);send(80);}rebuildWidgets();}).active=page>0||menu.window()>0;
        local(sidebar-30,pagerY,24,16,"›",()->{if(page<5)page++;else{pendingPage=0;pendingRevision=menu.view.get(2);send(81);}rebuildWidgets();}).active=menu.window()*36+(page+1)*ROWS<count();
        if(tab==0){
            if(selected>=0&&menu.window()*36+selected<count()){
                String operation=menu.view.get(4)==1&&flags(selected)>=64&&flags(selected)<128?"修整兵员":flags(selected)%32>0?"移出编队":"编入军阵";
                availability(action(sidebar+6,98,104,22,operation,40+selected),!locked,"先收阵，战斗中不能调整兵册");
            }
            if(menu.desk!=null)local(sidebar+6,143,104,24,"前往募兵",()->{tab=3;rebuildWidgets();});
        }else{
            int form=0;
            // One live formation; slots are assigned directly, with no preset save/load UI.
            var points=new java.util.ArrayList<net.minecraft.world.phys.Vec3>();for(int i=0;i<9;i++)points.add(ArmyRoster.slot(net.minecraft.world.phys.Vec3.ZERO,0,menu.slotPage()*9+i,form));
            double minX=points.stream().mapToDouble(p->p.x).min().orElse(0),maxX=points.stream().mapToDouble(p->p.x).max().orElse(1),minZ=points.stream().mapToDouble(p->p.z).min().orElse(0),maxZ=points.stream().mapToDouble(p->p.z).max().orElse(1);
            for(int i=0;i<9;i++){var p=points.get(i);int bw=form==3?10:20;int x=sidebar+12+(int)((p.x-minX)/Math.max(1,maxX-minX)*86);int y=maxZ-minZ<.01?110:imageHeight-89-(int)((p.z-minZ)/Math.max(1,maxZ-minZ)*(imageHeight-183));
                availability(action(x-bw/2,y,bw,14,Integer.toString(menu.slotPage()*9+i+1),186+i),!locked&&menu.selectedIndex()>=0&&menu.slotPage()*9+i<count(),"先在左侧选择兵员，再选择阵位");}
            availability(action(sidebar+6,72,18,16,"‹",82),!locked&&menu.slotPage()>0,"第一组阵位");
            availability(action(sidebar+92,72,18,16,"›",83),!locked&&(menu.slotPage()+1)*9<count(),"暂无更多阵位");

        }
        int bw=(imageWidth-32)/4,y=imageHeight-25;
        availability(action(10,y,bw,19,"快速编队",13),!locked,"先收阵再编队");
        action(14+bw,y,bw,19,"出阵",10);action(18+bw*2,y,bw,19,"收阵",11);action(22+bw*3,y,bw,19,"转向",12);
    }
    @Override protected void renderBg(GuiGraphics g,float partial,int x,int y){
        g.fill(leftPos-1,topPos-1,leftPos+imageWidth+1,topPos+imageHeight+1,0xFF373737);
        g.fill(leftPos,topPos,leftPos+imageWidth,topPos+imageHeight,0xFFC6C6C6);
        g.fill(leftPos,topPos,leftPos+imageWidth-2,topPos+2,0xFFFFFFFF);
        g.fill(leftPos,topPos,leftPos+2,topPos+imageHeight-2,0xFFFFFFFF);
        g.fill(leftPos+2,topPos+imageHeight-2,leftPos+imageWidth,topPos+imageHeight,0xFF555555);
        g.fill(leftPos+imageWidth-2,topPos+2,leftPos+imageWidth,topPos+imageHeight,0xFF555555);
        g.fill(leftPos+10,topPos+23,leftPos+imageWidth-10,topPos+24,0xFF8B8B8B);
        if(tab!=2){g.fill(leftPos+sidebar,topPos+51,leftPos+sidebar+1,topPos+imageHeight-31,0xFF8B8B8B);int row=selected-page*ROWS;if(tab!=3&&row>=0&&row<ROWS&&selected<count())g.fill(leftPos+7,topPos+bodyY+row*rowHeight,leftPos+9,topPos+bodyY+row*rowHeight+rowHeight-2,0xFFFFFFFF);}
    }
    @Override protected void renderLabels(GuiGraphics g,int x,int y){
        g.drawString(font,tab==3?"募兵台":"虎符",10,9,0x303030,false);g.drawString(font,"银 "+menu.balance()+"   兵员 "+count()+"名",53,9,0x404040,false);
        g.fill(10+tab*58,46,64+tab*58,47,0xFFFFFFFF);
        if(tab==3){
            int detailX=sidebar+6,price=ArmyRoster.PRICE[recruitRole];
            var icon=recruitRole==1?net.minecraft.world.item.Items.CROSSBOW:recruitRole==2?net.minecraft.world.item.Items.SHIELD:net.minecraft.world.item.Items.IRON_SWORD;
            g.renderItem(new net.minecraft.world.item.ItemStack(icon),detailX,54);
            g.drawString(font,ArmyRoster.ROLES[recruitRole],detailX+22,59,0x303030,false);
            g.drawString(font,"生命 "+(int)ArmyRoster.HEALTH[recruitRole],detailX,80,0x404040,false);
            g.drawString(font,new String[]{"近战 · 持刀守位","远程 · 弩箭支援","防御 · 正面持盾"}[recruitRole],detailX,99,0x505050,false);
            g.drawString(font,"购买 1名 / "+price+"银",detailX,123,0x303030,false);
            g.drawString(font,"购后余额 "+Math.max(0,menu.balance()-price),detailX,140,0x505050,false);
            g.drawString(font,"兵册 "+count()+"名",12,imageHeight-40,0x505050,false);
            return;
        }
        if(tab==2){g.drawString(font,"科举中第解锁 · 部署后开战",10,imageHeight-86,0x505050,false);g.drawString(font,"战斗中兵册锁定；全军覆没判败",10,imageHeight-72,0x505050,false);return;}
        if(count()==0){g.drawString(font,"兵册尚无兵员",18,82,0x303030,false);g.drawString(font,"前往募兵台招募兵员",18,100,0x505050,false);}
        g.drawCenteredString(font,(menu.window()*6+page+1)+" / "+Math.max(1,(count()+ROWS-1)/ROWS)+" 页",sidebar/2,imageHeight-43,0x505050);
        if(tab==0){
            if(selected>=0&&menu.window()*36+selected<count()){g.drawString(font,ArmyRoster.ROLES[role(selected)]+" #"+(menu.window()*36+selected+1),sidebar+6,58,0x303030,false);g.drawString(font,"生命 "+menu.view.get(7+selected*3)+" · "+state(selected),sidebar+6,76,0x505050,false);}
            else{g.drawString(font,"选择左侧兵员",sidebar+6,61,0x303030,false);g.drawString(font,"查看状态与编队操作",sidebar+6,78,0x505050,false);}
            g.drawString(font,menu.desk!=null?"募兵台 · 花银购买":"士兵需在募兵台购买",sidebar+6,131,0x505050,false);
            g.drawString(font,"选兵员，再选阵位",sidebar+6,160,0x505050,false);
        }else g.drawCenteredString(font,"↑ 前方",sidebar+58,54,0x505050);
    }
    @Override protected void containerTick(){super.containerTick();if(observedWindow!=menu.window()){observedWindow=menu.window();selected=-1;page=pendingPage>=0?pendingPage:0;pendingPage=-1;}
        if(pendingRevision>=0&&menu.view.get(2)!=pendingRevision){pendingRevision=-1;pendingPage=-1;}
        if(tab==1&&!deployed()&&menu.view.get(5)!=2&&menu.view.get(3)!=0&&pendingRevision<0){send(20);pendingRevision=menu.view.get(2);}
        int signature=tab*31+page;for(int i=0;i<menu.view.getCount();i++)signature=31*signature+menu.view.get(i);if(signature!=lastSignature){lastSignature=signature;if(menu.window()*36+selected>=count())selected=-1;rebuildWidgets();}}
    @Override public void render(GuiGraphics g,int x,int y,float partial){renderBackground(g);super.render(g,x,y,partial);renderTooltip(g,x,y);}
}
