package com.dynasty.armorqa;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.ChatScreen;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.Style;
import java.util.*;
import static com.dynasty.armorqa.ArmorNetworkQa.*;

/** Chooses only nonce-bearing RUN_COMMAND choices actually received by this real client. */
final class NativeDialogueClientDriver {
    static final Map<String,Style> offered=new HashMap<>();
    static int sequence=-1,step,age;
    static String site="";
    static void reset(int command,String id){sequence=command;site=id;step=0;age=0;offered.clear();}
    static void received(Component component){
        var click=component.getStyle().getClickEvent();
        if(click!=null&&click.getAction()==ClickEvent.Action.RUN_COMMAND){
            String value=click.getValue();
            if(value.matches("/dynasty_dialogue [0-9a-fA-F-]{36} [a-z_]+")) {
                String action=value.substring(value.lastIndexOf(' ')+1);
                offered.put(action,component.getStyle());
            }
        }
        for(var sibling:component.getSiblings())received(sibling);
    }
    static String[] plan(boolean completion){
        if(site.equals("ghost_market_boat"))return completion?new String[]{"deliver"}:new String[]{"talk"};
        if(site.equals("wayside_tea_stall"))return completion?new String[]{"flip"}:new String[]{"inspect","drink"};
        return new String[0];
    }
    static boolean drive(Minecraft minecraft,boolean completion)throws Exception {
        String[] plan=plan(completion);age++;
        if(step>=plan.length)return true;
        if(age<8||!offered.containsKey(plan[step]))return false;
        String action=plan[step];Style style=offered.get(action);
        // Run through the actual chat component click handler. The client issues its
        // normal command packet; no server choose() call or reconstructed nonce.
        var screen=new ChatScreen("");minecraft.setScreen(screen);
        require(screen.handleComponentClicked(style),"Native chat choice must be handled: "+action);
        write("peer-native-dialogue-"+sequence+"-"+step+".json",obj("site",site,"action",action,"client",minecraft.player.getUUID().toString(),"path","ChatScreen.handleComponentClicked on received RUN_COMMAND style","completionPhase",completion));
        offered.clear();step++;age=0;
        return false;
    }
}
