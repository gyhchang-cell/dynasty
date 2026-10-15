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
    private static final String[] FORMS={"方阵","锋矢阵","分散阵","横阵","环阵"};
    private static final int ROWS=6;
    private int page,tab,selected=-1,preset,lastSignature=Integer.MIN_VALUE;
    private int sidebar,listWidth,bodyY=53,rowHeight;
    @SubscribeEvent public static void setup(FMLClientSetupEvent e){e.enqueueWork(()->MenuScreens.register(ArmyContent.MENU.get(),ArmyRosterScreen::new));}
    public ArmyRosterScreen(ArmyMenu menu,Inventory inv,Component title){super(menu,inv,title);imageWidth=400;imageHeight=248;}
    private void send(int action){if(minecraft!=null&&minecraft.gameMode!=null)minecraft.gameMode.handleInventoryButtonClick(menu.containerId,(menu.view.get(2)<<8)|action);}
    private Button local(int x,int y,int w,int h,String text,Runnable click){return addRenderableWidget(new QuietButton(leftPos+x,topPos+y,w,h,text,click));}
    private Button action(int x,int y,int w,int h,String text,int code){return local(x,y,w,h,text,()->send(code));}
    private int count(){return Math.max(0,Math.min(36,menu.view.get(0)));}
    private int flags(int n){return menu.view.get(8+n*3);}
    private int role(int n){return Math.max(0,Math.min(2,menu.view.get(6+n*3)));}
    private String state(int n){int f=flags(n);return f>=128?"收阵中":f>=64?"重伤":f>=32?"出战":f%32>0?"已编入":"预备";}
    private boolean deployed(){for(int n=0;n<count();n++)if(flags(n)>=128||(flags(n)>=32&&flags(n)<64))return true;return false;}
    private void availability(Button b,boolean active,String reason){b.active=active;if(!active)b.setTooltip(Tooltip.create(Component.literal(reason)));}
    @Override protected void init(){
        imageWidth=Math.max(280,Math.min(420,width-20));imageHeight=Math.max(212,Math.min(250,height-16));super.init();
        sidebar=imageWidth-126;listWidth=sidebar-16;rowHeight=Math.max(17,(imageHeight-104)/ROWS);page=Math.min(page,Math.max(0,(count()-1)/ROWS));
        for(int i=0;i<3;i++){final int next=i;local(10+i*62,28,58,18,new String[]{"兵册","军阵","关卡"}[i],()->{tab=next;rebuildWidgets();});}
        local(imageWidth-29,7,20,16,"×",this::onClose);
        if(tab==2){
            for(int i=0;i<6;i++){int y=56+(i/2)*26,x=10+(i%2)*(imageWidth/2);action(x,y,imageWidth/2-20,24,ArmyEncounters.NAMES[i],130+i);}
            action(10,imageHeight-58,(imageWidth-26)/2,22,"部署后开战",200);
            action(16+(imageWidth-26)/2,imageHeight-58,(imageWidth-26)/2,22,menu.view.get(115)==1?"确认认输":"撤离战区",201);return;
        }
        boolean locked=deployed()||menu.view.get(5)==2;
        for(int i=0;i<ROWS;i++){
            int n=page*ROWS+i;if(n>=count())break;
            String label="#"+(n+1)+" "+ArmyRoster.ROLES[role(n)]+"  "+menu.view.get(7+n*3)+"血  "+state(n);
            local(10,bodyY+i*rowHeight,listWidth,rowHeight-2,label,()->{selected=n;if(tab==1)send(150+n);rebuildWidgets();});
        }
        int pagerY=imageHeight-47;
        local(10,pagerY,24,16,"‹",()->{page=Math.max(0,page-1);rebuildWidgets();}).active=page>0;
        local(sidebar-30,pagerY,24,16,"›",()->{page=Math.min(Math.max(0,(count()-1)/ROWS),page+1);rebuildWidgets();}).active=(page+1)*ROWS<count();
        if(tab==0){
            if(selected>=0&&selected<count()){
                String operation=menu.view.get(4)==1&&flags(selected)>=64&&flags(selected)<128?"修整兵员":flags(selected)%32>0?"移出编队":"编入军阵";
                availability(action(sidebar+6,98,104,22,operation,40+selected),!locked,"先收阵，战斗中不能调整兵册");
            }
            for(int i=0;i<3;i++)availability(action(sidebar+6,132+i*21,104,19,ArmyRoster.ROLES[i]+" · "+ArmyRoster.PRICE[i]+"银",i),menu.view.get(4)==1&&menu.view.get(5)!=2,"到募兵台招募兵员");
        }else{
            int form=Math.max(0,Math.min(4,menu.view.get(3)));
            availability(action(sidebar+6,51,104,19,"阵型 · "+FORMS[form]+" ›",20+(form+1)%5),!locked,"先收阵再调整阵型");
            var points=new java.util.ArrayList<net.minecraft.world.phys.Vec3>();for(int i=0;i<9;i++)points.add(ArmyRoster.slot(net.minecraft.world.phys.Vec3.ZERO,0,i,form));
            double minX=points.stream().mapToDouble(p->p.x).min().orElse(0),maxX=points.stream().mapToDouble(p->p.x).max().orElse(1),minZ=points.stream().mapToDouble(p->p.z).min().orElse(0),maxZ=points.stream().mapToDouble(p->p.z).max().orElse(1);
            for(int i=0;i<9;i++){var p=points.get(i);int bw=form==3?10:20;int x=sidebar+12+(int)((p.x-minX)/Math.max(1,maxX-minX)*86);int y=maxZ-minZ<.01?110:141-(int)((p.z-minZ)/Math.max(1,maxZ-minZ)*58);
                availability(action(x-bw/2,y,bw,16,Integer.toString(i+1),186+i),!locked&&menu.view.get(114)>=0,"先在左侧选择兵员，再选择阵位");}
            local(sidebar+6,imageHeight-67,104,18,"预设 "+(preset+1)+" ›",()->{preset=(preset+1)%3;rebuildWidgets();});
            availability(action(sidebar+6,imageHeight-46,50,18,"保存",100+preset),!locked,"先收阵再保存");availability(action(sidebar+60,imageHeight-46,50,18,"载入",110+preset),!locked,"先收阵再载入");
        }
        int bw=(imageWidth-32)/4,y=imageHeight-25;
        availability(action(10,y,bw,19,"快速编队",13),!locked,"先收阵再编队");
        action(14+bw,y,bw,19,"出阵",10);action(18+bw*2,y,bw,19,"收阵",11);action(22+bw*3,y,bw,19,"转向",12);
    }
    @Override protected void renderBg(GuiGraphics g,float partial,int x,int y){
        g.fill(leftPos,topPos,leftPos+imageWidth,topPos+imageHeight,0xF214252B);g.fill(leftPos+1,topPos+1,leftPos+imageWidth-1,topPos+2,0xFFB99B65);
        g.fill(leftPos+10,topPos+23,leftPos+imageWidth-10,topPos+24,0xFF344B50);
        if(tab!=2){g.fill(leftPos+sidebar,topPos+51,leftPos+sidebar+1,topPos+imageHeight-31,0xFF344B50);int row=selected-page*ROWS;if(row>=0&&row<ROWS&&selected<count())g.fill(leftPos+7,topPos+bodyY+row*rowHeight,leftPos+9,topPos+bodyY+row*rowHeight+rowHeight-2,0xFFE1C18C);}
    }
    @Override protected void renderLabels(GuiGraphics g,int x,int y){
        g.drawString(font,"虎符",10,9,0xE6CF98,false);g.drawString(font,"银 "+menu.view.get(1)+"   兵员 "+count()+"/36",53,9,0xD2DED8,false);
        g.fill(10+tab*62,46,68+tab*62,47,0xFFE1C18C);
        if(tab==2){g.drawString(font,"科举中第解锁 · 部署后开战",10,imageHeight-86,0xB2C5C2,false);g.drawString(font,"战斗中兵册锁定；全军覆没判败",10,imageHeight-72,0xB2C5C2,false);return;}
        if(count()==0){g.drawString(font,"兵册尚无兵员",18,82,0xE6CF98,false);g.drawString(font,"前往募兵台招募兵员",18,100,0xA2B8B7,false);}
        g.drawCenteredString(font,(page+1)+" / "+Math.max(1,(count()+ROWS-1)/ROWS)+" 页",sidebar/2,imageHeight-43,0xA2B8B7);
        if(tab==0){
            if(selected>=0&&selected<count()){g.drawString(font,ArmyRoster.ROLES[role(selected)]+" #"+(selected+1),sidebar+6,58,0xE6CF98,false);g.drawString(font,"生命 "+menu.view.get(7+selected*3)+" · "+state(selected),sidebar+6,76,0xB2C5C2,false);}
            else{g.drawString(font,"选择左侧兵员",sidebar+6,61,0xE6CF98,false);g.drawString(font,"查看状态与编队操作",sidebar+6,78,0xA2B8B7,false);}
            g.drawString(font,menu.view.get(4)==1?"募兵台 · 招募":"招募需前往募兵台",sidebar+6,119,0xA2B8B7,false);
        }else g.drawCenteredString(font,"↑ 敌方",sidebar+58,73,0xA2B8B7);
    }
    @Override protected void containerTick(){super.containerTick();int signature=tab*31+page;for(int i=0;i<menu.view.getCount();i++)signature=31*signature+menu.view.get(i);if(signature!=lastSignature){lastSignature=signature;if(selected>=count())selected=-1;rebuildWidgets();}}
    @Override public void render(GuiGraphics g,int x,int y,float partial){renderBackground(g);super.render(g,x,y,partial);renderTooltip(g,x,y);}
    private static final class QuietButton extends Button{
        QuietButton(int x,int y,int w,int h,String text,Runnable click){super(x,y,w,h,Component.literal(text),b->click.run(),DEFAULT_NARRATION);}
        @Override protected void renderWidget(GuiGraphics g,int mx,int my,float partial){var f=net.minecraft.client.Minecraft.getInstance().font;boolean hover=isHoveredOrFocused()&&active;g.fill(getX(),getY(),getX()+width,getY()+height,hover?0xFF365356:active?0xFF223A40:0xFF1C2D32);g.fill(getX(),getY()+height-1,getX()+width,getY()+height,hover?0xFFD4B67D:0xFF3C5356);float scale=Math.min(1,(width-8F)/Math.max(1,f.width(getMessage())));g.pose().pushPose();g.pose().translate(getX()+width/2F,getY()+(height-9*scale)/2F,0);g.pose().scale(scale,scale,1);g.drawString(f,getMessage(),-f.width(getMessage())/2,0,active?0xE3E9DF:0x758C8D,false);g.pose().popPose();}
    }
}
