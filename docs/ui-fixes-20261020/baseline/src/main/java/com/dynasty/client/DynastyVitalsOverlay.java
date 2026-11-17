package com.dynasty.client;

import net.minecraft.client.Minecraft;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterGuiOverlaysEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Independent of vanilla HOTBAR/HEALTH events, which HUD mods may cancel. */
@Mod.EventBusSubscriber(modid="dynasty", value=Dist.CLIENT, bus=Mod.EventBusSubscriber.Bus.MOD)
public final class DynastyVitalsOverlay {
    @SubscribeEvent public static void register(RegisterGuiOverlaysEvent event) {
        event.registerAboveAll("vitals", (gui,g,partial,w,h)->{
            var mc=Minecraft.getInstance();var p=mc.player;
            if(p==null || mc.options.hideGui || p.isSpectator())return;
            var compass=p.getMainHandItem().is(com.dynasty.navigation.CreatureCompass.ITEM.get())?p.getMainHandItem():p.getOffhandItem();
            if(compass.is(com.dynasty.navigation.CreatureCompass.ITEM.get())&&compass.hasTag()&&compass.getTag().contains("TargetPos")){
                var tag=compass.getTag();var pos=net.minecraft.core.BlockPos.of(tag.getLong("TargetPos"));
                if(p.level().dimension().location().toString().equals(tag.getString("TargetDimension"))){
                    String id=tag.getString("TargetName");var type=net.minecraftforge.registries.ForgeRegistries.ENTITY_TYPES.getValue(new net.minecraft.resources.ResourceLocation(id));
                    String name=type==null?id:net.minecraft.network.chat.Component.translatable(type.getDescriptionId()).getString();
                    int x=w-180,y=18;g.fill(x-4,y-3,w-4,y+34,0xB0000000);
                    g.drawString(mc.font,name,x,y,0xFFFFFF);g.drawString(mc.font,"X "+pos.getX()+"  Y "+pos.getY()+"  Z "+pos.getZ(),x,y+11,0xFFFFFF);
                    g.drawString(mc.font,"距离 "+(int)Math.sqrt(p.distanceToSqr(pos.getX(),pos.getY(),pos.getZ()))+" 格",x,y+22,0xFFFFFF);
                }
            }
            String text=(DynastyItemInfo.chinese()?"生命 ":"HP ")+number(p.getHealth())+" / "+number(p.getMaxHealth());
            if(p.getAbsorptionAmount()>0)text+="  +"+number(p.getAbsorptionAmount());
            // Fixed, compact row above the stacked hearts; not proportional to max-health rows.
            int x=w/2-91,y=h-65;
            g.fill(x-2,y-2,x+mc.font.width(text)+3,y+10,0xB0000000);
            g.drawString(mc.font,text,x,y,0xFFFFFFFF,true);
        });
    }
    static String number(float v){return v==Math.rint(v)?Long.toString(Math.round(v)):String.format(java.util.Locale.ROOT,"%.1f",v);}
}
