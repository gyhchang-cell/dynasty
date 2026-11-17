package com.dynasty.armorqa;

import com.dynasty.expansion.EquipmentBehaviors;
import com.google.gson.JsonParser;
import net.minecraft.client.Minecraft;
import net.minecraft.world.InteractionHand;
import net.minecraft.network.protocol.game.ServerboundMovePlayerPacket;
import java.nio.file.Files;
import static com.dynasty.armorqa.ArmorNetworkQa.*;

/** Reads server observations, then uses actual client movement keys and native air-swing packets. */
final class NativeSwordDanceDriver {
    static int sequence=-1,cut=-1;
    static boolean swung;
    static void release(Minecraft m){m.options.keyLeft.setDown(false);m.options.keyRight.setDown(false);m.options.keyUp.setDown(false);m.options.keyDown.setDown(false);}
    static void observe()throws Exception{
        var p=players(server).get(1);var n=p.getPersistentData().getCompound("cod3_progress_28");var root=EquipmentBehaviors.saved(p);
        write("dance-live.json",obj("sequence",InteractionNetworkQa.sequence,"count",n.getInt("Count"),"focused",n.getBoolean("DanceFocused"),"done",root.getBoolean("site_sword_scar_wall_done"),"next",root.getLong("site_sword_scar_wall_next"),"tick",server.overworld().getGameTime(),"baseX",n.getDouble("DanceBaseX"),"baseY",n.getDouble("DanceBaseY"),"baseZ",n.getDouble("DanceBaseZ"),"actorX",p.getX(),"actorY",p.getY(),"actorZ",p.getZ(),"onGround",p.onGround()));
    }
    static boolean drive(Minecraft m,int command)throws Exception{
        if(sequence!=command){sequence=command;cut=-1;swung=false;release(m);}
        if(!has("dance-live.json"))return false;
        var n=JsonParser.parseString(Files.readString(OUT.resolve("dance-live.json"))).getAsJsonObject();
        if(n.get("sequence").getAsInt()!=sequence)return false;
        if(n.get("done").getAsBoolean()){release(m);return true;}
        if(!n.get("focused").getAsBoolean())return false;
        int next=n.get("count").getAsInt();
        require(next>=cut,"Native sword dance unexpectedly reset after a client cut");
        if(next!=cut){cut=next;swung=false;release(m);}
        require(cut>=0&&cut<3,"Sword dance step in range");
        m.setScreen(null);m.options.keyShift.setDown(false);m.player.setShiftKeyDown(false);
        float yaw=cut==2?-90:180;m.player.setYRot(yaw);m.player.setXRot(0);
        double dx=m.player.getX()-n.get("baseX").getAsDouble(),dz=m.player.getZ()-n.get("baseZ").getAsDouble();
        double along=cut==0?dx:cut==1?-dx:-dz,across=cut<2?Math.abs(dz):Math.abs(dx);
        require(across<.35,"Native dance input drifted away from required step axis");
        if(!swung&&along<.55){m.options.keyRight.setDown(cut==0);m.options.keyLeft.setDown(cut!=0);return false;}
        release(m);
        if(swung||n.get("tick").getAsLong()<n.get("next").getAsLong()||!m.player.onGround())return false;
        require(along>=.35&&along<=1.5,"Native step displacement in actual rule bounds");
        // Rotation and swing use normal client packet paths; never call SwordDance.tick/open from QA.
        m.player.connection.send(new ServerboundMovePlayerPacket.Rot(yaw,0,m.player.onGround()));
        m.player.swing(InteractionHand.MAIN_HAND);
        write("peer-native-dance-"+sequence+"-"+cut+".json",obj("step",cut,"client",m.player.getUUID().toString(),"along",along,"across",across,"onGround",m.player.onGround(),"worldTickObserved",n.get("tick").getAsLong(),"deadlineObserved",n.get("next").getAsLong(),"inputPath","Native keyboard strafe then LocalPlayer.swing and native rotation packet"));
        swung=true;return false;
    }
}
