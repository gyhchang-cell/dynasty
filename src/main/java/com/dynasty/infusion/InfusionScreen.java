package com.dynasty.infusion;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.MenuScreens;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class InfusionScreen extends AbstractContainerScreen<InfusionMenu> {
    private Button apply;
    public InfusionScreen(InfusionMenu menu,Inventory inv,Component title){super(menu,inv,title);imageWidth=320;imageHeight=238;inventoryLabelY=142;}
    @SubscribeEvent public static void setup(FMLClientSetupEvent e){e.enqueueWork(()->MenuScreens.register(InfusionContent.MENU.get(),InfusionScreen::new));}
    private void send(int id){if(minecraft!=null&&minecraft.gameMode!=null)minecraft.gameMode.handleInventoryButtonClick(menu.containerId,id);}
    @Override protected void init(){
        super.init();
        for(int i=0;i<3;i++){final int slot=i;addRenderableWidget(Button.builder(Component.literal("炼入位 "+(i+1)),b->send(slot)).bounds(leftPos+8+i*56,topPos+75,53,18).build());}
        apply=addRenderableWidget(Button.builder(Component.literal("炼入 / 替换"),b->send(3)).bounds(leftPos+8,topPos+112,100,20).build());
        addRenderableWidget(Button.builder(Component.literal("移除"),b->send(4)).bounds(leftPos+113,topPos+112,55,20).build());
    }
    @Override public void render(GuiGraphics g,int mx,int my,float partial){renderBackground(g);apply.active=menu.status()==0;super.render(g,mx,my,partial);renderTooltip(g,mx,my);}
    @Override protected void renderBg(GuiGraphics g,float partial,int mx,int my){
        g.fill(leftPos,topPos,leftPos+imageWidth,topPos+imageHeight,0xff233633);
        g.fill(leftPos+3,topPos+3,leftPos+imageWidth-3,topPos+imageHeight-3,0xffe2d9bb);
        g.fill(leftPos+176,topPos+25,leftPos+312,topPos+229,0xffc9c4aa);
        for(var s:menu.slots){int x=leftPos+s.x,y=topPos+s.y;g.fill(x-1,y-1,x+17,y+17,0xff666b60);g.fill(x,y,x+16,y+16,0xffadaf9d);}
        g.fill(leftPos+124,topPos+39,leftPos+142,topPos+57,0xff7b947f);
        var preview=menu.preview(false);if(!preview.isEmpty())g.renderItem(preview,leftPos+125,topPos+40);
    }
    private int wrap(GuiGraphics g,String text,int x,int y,int width,int color){for(var line:font.split(Component.literal(text),width)){g.drawString(font,line,x,y,color,false);y+=10;}return y;}
    @Override protected void renderLabels(GuiGraphics g,int mx,int my){
        g.drawString(font,title,8,8,0xff233633,false);
        g.drawString(font,"装备",17,27,0xff333333,false);g.drawString(font,"材料",67,27,0xff333333,false);g.drawString(font,"预览",121,27,0xff333333,false);
        var ids=InfusionTraits.slots(menu.gear());g.drawString(font,"选中 "+(menu.selected()+1)+" · 容量 "+InfusionTraits.capacity(ids)+" / 4",8,98,0xff333333,false);
        g.drawString(font,"2材料 + 3级；移除1级，不返材料",8,135,0xff333333,false);
        int y=31;g.drawString(font,"当前特性",182,y,0xff233633,false);y+=13;
        for(int i=0;i<3;i++){var t=InfusionTraits.get(ids.get(i));y=wrap(g,(i+1)+". "+(t==null?"空":t.name()),182,y,126,0xff333333);}
        var t=InfusionTraits.material(menu.material());y+=9;
        if(t!=null){y=wrap(g,t.name()+" · 容量"+t.cost(),182,y,126,0xff24584c);y=wrap(g,t.description(),182,y+3,126,0xff333333);y=wrap(g,"适用："+switch(t.kind()){case WEAPON->t.material().equals("shanxiao_claw")||t.material().equals("baihu_fang")?"近战武器":"武器";case ARMOR->"防具 / 盾";default->"全部装备";},182,y+3,126,0xff333333);}
        String status=switch(menu.status()){case 1->"需完成已有进度：获得玉";case 2->t!=null&&t.gate().equals("entered_underworld")?"需完成已有进度：下探地府":"需完成已有进度：踏入天朝";case 3->"请检查装备、炼入位、容量；同类特性冲突";case 4->"需要2个相同材料";case 5->"经验等级不足";default->"可以炼入；同位原特性被替换";};
        wrap(g,status,182,Math.max(185,y+5),126,menu.status()==0?0xff24584c:0xff9b362e);
    }
}
