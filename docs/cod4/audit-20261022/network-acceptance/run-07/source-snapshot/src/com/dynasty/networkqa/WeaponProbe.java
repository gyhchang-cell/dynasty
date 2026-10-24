package com.dynasty.networkqa;
import com.dynasty.cod3.Cod3VisualPacket;
import com.dynasty.expansion.CombatFeedback;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;
/** Observer only; never invokes handlers or sends a visual packet. */
public final class WeaponProbe {
 public static volatile int caseId=-1;
 public static final List<Map<String,Object>> EVENTS=new CopyOnWriteArrayList<>();
 public static boolean enabled(){return System.getProperty("dynasty.networkqa.suite","states").equals("weapons");}
 public static synchronized void record(String kind,Map<String,Object> fields){if(!enabled())return;var row=new LinkedHashMap<String,Object>();row.put("case",caseId);row.put("kind",kind);row.put("wallMillis",System.currentTimeMillis());row.put("nano",System.nanoTime());row.put("thread",Thread.currentThread().getName());row.putAll(fields);row.put("kind",kind);EVENTS.add(row);try{Files.writeString(NetworkAcceptance.OUT.resolve(NetworkAcceptance.ROLE+"-wire.jsonl"),NetworkAcceptance.JSON.toJson(row).replace("\n","")+"\n",StandardOpenOption.CREATE,StandardOpenOption.APPEND);}catch(Exception ex){throw new RuntimeException(ex);}}
 public static void vfx(Cod3VisualPacket p){record("vfx-wire",Map.of("sequence",p.sequence(),"template",p.template(),"entity",p.entityId(),"seed",p.seed(),"start",p.start(),"duration",p.duration(),"layer",p.tick(),"origin",List.of(p.origin().x,p.origin().y,p.origin().z)));}
 public static void feedback(CombatFeedback p){record("feedback-client",Map.of("type",p.type(),"origin",List.of(p.x(),p.y(),p.z())));}
 public static void weapon(net.minecraft.world.entity.player.Player p,String cue){if(!p.level().isClientSide)record("weapon-server-source",Map.of("cue",cue,"owner",p.getUUID().toString(),"entity",p.getId(),"gameTick",p.level().getGameTime(),"position",List.of(p.getX(),p.getY(),p.getZ()),"players",p.level().players().stream().map(x->Map.of("uuid",x.getUUID().toString(),"distanceSqr",x.distanceToSqr(p))).toList()));}
}
