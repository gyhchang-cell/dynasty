package com.dynasty.mobnetworkqa;
import com.dynasty.cod3.Cod3VisualPacket;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import java.util.*;
/** Read-only native renderer and packet observations; never emits/cancels feedback. */
public final class NativeStatusProbe {
 public static String current="";public static Map<String,Integer> geometry=new LinkedHashMap<>();public static List<Object> activeVisuals=List.of();public static List<Object> events=new ArrayList<>();
 public static void begin(){geometry=new LinkedHashMap<>();}
 public static void active(List<Cod3VisualPacket> list){activeVisuals=list.stream().map(NativeStatusProbe::packet).toList();}
 static Object packet(Cod3VisualPacket p){return Map.of("sequence",p.sequence(),"entity",p.entityId(),"start",p.start(),"duration",p.duration(),"tint",p.tint());}
 public static void wire(Cod3VisualPacket p){event("actual-s2c-vfx",packet(p));}
 public static void event(String kind,Object value){if(!current.isEmpty())events.add(Map.of("case",current,"kind",kind,"data",value,"clientWorldTick",net.minecraft.client.Minecraft.getInstance().level==null?-1:net.minecraft.client.Minecraft.getInstance().level.getGameTime()));}
 public static void vertex(String kind,Matrix4f matrix,Vec3 a,int color,double alpha){if(!current.isEmpty())geometry.merge(kind,1,Integer::sum);}
 public static void triangle(String kind,Matrix4f matrix,Vec3 a,Vec3 b,Vec3 c,int color,double alpha){if(!current.isEmpty())geometry.merge(kind,3,Integer::sum);}
}
