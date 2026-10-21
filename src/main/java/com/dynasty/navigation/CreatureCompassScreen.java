package com.dynasty.navigation;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.*;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.*;

/** Same search/list/action arrangement as the installed explorer compass. */
public final class CreatureCompassScreen extends Screen {
    private EditBox search;private int offset;private ResourceLocation selected;
    private List<ResourceLocation> visible=List.of();private final List<Button> rows=new ArrayList<>();
    private CreatureCompassScreen(){super(Component.literal("选择生物"));}
    public static void open(){net.minecraft.client.Minecraft.getInstance().setScreen(new CreatureCompassScreen());}
    @Override protected void init(){
        rows.clear();
        int sidebar=Math.max(100,width/3),right=width-sidebar-20;
        search=new EditBox(font,sidebar,18,right,20,Component.literal("搜索生物"));search.setHint(Component.literal("搜索名称或注册名"));search.setResponder(s->{offset=0;refresh();});addRenderableWidget(search);
        addRenderableWidget(Button.builder(Component.literal("搜索"),b->{if(selected!=null){CreatureCompass.request(selected);onClose();}}).bounds(10,52,sidebar-22,20).build());
        addRenderableWidget(Button.builder(Component.literal("上一页"),b->{offset=Math.max(0,offset-rows.size());refresh();}).bounds(10,82,sidebar-22,20).build());
        addRenderableWidget(Button.builder(Component.literal("下一页"),b->{if(offset+rows.size()<visible.size())offset+=rows.size();refresh();}).bounds(10,112,sidebar-22,20).build());
        addRenderableWidget(Button.builder(Component.literal("取消"),b->onClose()).bounds(10,height-32,sidebar-22,20).build());
        for(int y=50;y<height-30;y+=32){final int index=rows.size();Button row=Button.builder(Component.empty(),b->{int i=offset+index;if(i<visible.size()){selected=visible.get(i);refresh();}}).bounds(sidebar,y,right,28).build();rows.add(row);addRenderableWidget(row);}
        refresh();
    }
    private void refresh(){
        String needle=search.getValue().toLowerCase(Locale.ROOT);
        visible=ForgeRegistries.ENTITY_TYPES.getKeys().stream().filter(id->{var t=ForgeRegistries.ENTITY_TYPES.getValue(id);return t.getCategory()!=net.minecraft.world.entity.MobCategory.MISC || net.minecraft.world.item.SpawnEggItem.byId(t)!=null;})
            .filter(id->id.toString().contains(needle)||Component.translatable(ForgeRegistries.ENTITY_TYPES.getValue(id).getDescriptionId()).getString().toLowerCase(Locale.ROOT).contains(needle))
            .sorted(Comparator.comparing(id->Component.translatable(ForgeRegistries.ENTITY_TYPES.getValue(id).getDescriptionId()).getString())).toList();
        for(int n=0;n<rows.size();n++){var b=rows.get(n);int i=offset+n;b.visible=i<visible.size();if(b.visible){var id=visible.get(i);b.setMessage(Component.literal(id.equals(selected)?"▶ ":"").append(Component.translatable(ForgeRegistries.ENTITY_TYPES.getValue(id).getDescriptionId())).append(" · "+id.getNamespace()));}}
    }
    @Override public void render(GuiGraphics g,int x,int y,float partial){renderBackground(g);super.render(g,x,y,partial);g.drawString(font,title,14,24,0xFFFFFF);g.drawString(font,"范围：附近256格",14,145,0xCCCCCC);}
    @Override public boolean isPauseScreen(){return false;}
}
