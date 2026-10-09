package com.dynasty.infusion;

import java.util.*;
import com.dynasty.network.DynastyNetwork;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.MenuScreens;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;

@Mod.EventBusSubscriber(modid="dynasty",bus=Mod.EventBusSubscriber.Bus.MOD,value=Dist.CLIENT)
public final class InfusionScreen extends AbstractContainerScreen<InfusionMenu> {
    private static final ResourceLocation BACKGROUND=new ResourceLocation("dynasty","textures/gui/infusion.png");
    private static final ResourceLocation CRESTS=new ResourceLocation("dynasty","textures/gui/infusion_crests.png");
    private static final List<String> EFFECTS=InfusionTraits.ALL.stream().map(InfusionTraits.Trait::effect).distinct().sorted().toList();
    private Button apply,remove;
    public InfusionScreen(InfusionMenu menu,Inventory inv,Component title){super(menu,inv,title);imageWidth=176;imageHeight=202;inventoryLabelY=108;}
    @SubscribeEvent public static void setup(FMLClientSetupEvent e){e.enqueueWork(()->MenuScreens.register(InfusionContent.MENU.get(),InfusionScreen::new));}
    private void send(int action,int slot){DynastyNetwork.CHANNEL.sendToServer(new InfusionRequest(menu.containerId,action,slot,menu.revision()));}
    @Override protected void init(){
        super.init();
        apply=addRenderableWidget(Button.builder(Component.translatable("infusion.dynasty.apply"),b->send(0,menu.selected())).bounds(leftPos+8,topPos+85,98,18).build());
        remove=addRenderableWidget(Button.builder(Component.translatable("infusion.dynasty.remove"),b->send(1,menu.selected())).bounds(leftPos+110,topPos+85,58,18).build());
    }
    @Override public boolean mouseClicked(double x,double y,int button){
        if(button==0&&y>=topPos+57&&y<topPos+77){for(int i=0;i<3;i++)if(x>=leftPos+23+i*24&&x<leftPos+43+i*24){send(2,menu.selected()==i?-1:i);return true;}}
        return super.mouseClicked(x,y,button);
    }
    @Override public void render(GuiGraphics g,int mx,int my,float partial){
        renderBackground(g);apply.active=menu.status()==0;remove.active=menu.removeStatus()==0;
        super.render(g,mx,my,partial);renderTooltip(g,mx,my);
        int x=mx-leftPos,y=my-topPos;
        for(int i=0;i<3;i++)if(x>=23+i*24&&x<43+i*24&&y>=57&&y<77){
            var t=InfusionTraits.get(InfusionTraits.slots(menu.gear()).get(i));var lines=new ArrayList<Component>();
            lines.add(t==null?Component.translatable("infusion.dynasty.empty"):t.name());
            if(t!=null){lines.add(t.description());lines.add(Component.translatable("infusion.dynasty.trait_cost",t.cost()));}
            lines.add(Component.translatable("infusion.dynasty.select_hint"));tip(g,lines,mx,my);
        }
        if(x>=130&&x<151&&y>=29&&y<50){var preview=menu.preview(false);if(!preview.isEmpty())g.renderTooltip(font,preview,mx,my);}
        if(y>=85&&y<103&&x>=8&&x<168){boolean r=x>=110;int code=r?menu.removeStatus():menu.status();var lines=new ArrayList<Component>();lines.add(Component.translatable("infusion.dynasty."+(r?"remove_cost":"apply_cost")));lines.add(Component.translatable("infusion.dynasty.error."+code));tip(g,lines,mx,my);}
        if(x>=104&&x<168&&y>=55&&y<79){var lines=new ArrayList<Component>();lines.add(Component.translatable("infusion.dynasty.capacity",InfusionTraits.capacity(InfusionTraits.slots(menu.gear())),InfusionTraits.maxCapacity(menu.gear())));lines.add(Component.translatable("infusion.dynasty.error."+menu.status()));tip(g,lines,mx,my);}
    }
    private void tip(GuiGraphics g,List<Component> lines,int x,int y){var wrapped=new ArrayList<net.minecraft.util.FormattedCharSequence>();for(var line:lines)wrapped.addAll(font.split(line,Math.min(220,width-16)));g.renderTooltip(font,wrapped,x,y);}
    @Override protected void renderBg(GuiGraphics g,float partial,int mx,int my){
        g.blit(BACKGROUND,leftPos,topPos,0,0,imageWidth,imageHeight,imageWidth,imageHeight);
        for(var s:menu.slots){int x=leftPos+s.x,y=topPos+s.y;g.fill(x-1,y-1,x+17,y+17,0xff161816);g.fill(x,y,x+17,y+17,0xff877b64);g.fill(x,y,x+16,y+16,0xff49473e);}
        var preview=menu.preview(false);if(!preview.isEmpty()){g.renderItem(preview,leftPos+134,topPos+31);g.renderItemDecorations(font,preview,leftPos+134,topPos+31);}
        var ids=InfusionTraits.slots(menu.gear());
        for(int i=0;i<3;i++){int x=leftPos+23+i*24,y=topPos+57;g.fill(x,y,x+20,y+20,menu.targetSlot()==i?0xffc8aa68:0xff67573c);g.fill(x+1,y+1,x+19,y+19,0xff292d26);var t=InfusionTraits.get(ids.get(i));if(t!=null){int n=EFFECTS.indexOf(t.effect());g.blit(CRESTS,x+2,y+2,(n%10)*16,(n/10)*16,16,16,160,64);}else g.drawString(font,"·",x+8,y+5,0xff719b83,false);}
    }
    @Override protected void renderLabels(GuiGraphics g,int mx,int my){
        g.drawString(font,title,8,6,0xffeadbbb,false);
        g.drawString(font,Component.translatable("infusion.dynasty.gear"),18,19,0xffc4b797,false);
        g.drawString(font,Component.translatable("infusion.dynasty.material"),69,19,0xffc4b797,false);
        g.drawString(font,Component.translatable("infusion.dynasty.preview"),125,19,0xffc4b797,false);
        g.drawString(font,"+",58,35,0xffb5c6a0,false);g.drawString(font,"→",111,35,0xffb5c6a0,false);
        int used=InfusionTraits.capacity(InfusionTraits.slots(menu.gear())),cap=InfusionTraits.maxCapacity(menu.gear());
        for(int i=0;i<cap;i++)g.fill(107+i*11,59,115+i*11,64,i<used?0xff79b397:0xff414638);
        g.drawString(font,menu.status()==0?"✓":"!",109,69,menu.status()==0?0xff8ac7a1:0xffd7a46b,false);
        g.drawString(font,used+" / "+cap,126,69,0xffc4b797,false);
        g.drawString(font,playerInventoryTitle,8,108,0xffc4b797,false);
    }
}
