package com.dynasty.client;
import com.dynasty.cod3.*;
import net.minecraft.client.multiplayer.ClientLevel;
import java.util.*;
/** Shared actual-ground validity for this scene's model and local cue. */
final class ScenicStoneGodGround {
 private record Check(long tick,boolean valid){}
 private static final Map<Cod3VisualPacket,Check> CHECKS=new HashMap<>();private static ClientLevel world;
 static void clear(){CHECKS.clear();world=null;}
 static void retain(List<Cod3VisualPacket> active){CHECKS.keySet().retainAll(active);}
 static boolean valid(ClientLevel level,Cod3VisualPacket p){
  if(world!=level){clear();world=level;}if(ScenicStoneGodSite.visibility(level)<=0)return false;
  var old=CHECKS.get(p);long now=level.getGameTime();if(old==null||now<old.tick()||now-old.tick()>=10){old=new Check(now,ScenicStoneGodSite.valid(level,new ScenicStoneGodSite.Site(p.origin(),p.direction())));CHECKS.put(p,old);}return old.valid();
 }
 private ScenicStoneGodGround(){}
}
