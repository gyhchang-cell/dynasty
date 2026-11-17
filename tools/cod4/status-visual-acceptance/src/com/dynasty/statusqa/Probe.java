package com.dynasty.statusqa;
import com.dynasty.cod3.Cod3VisualPacket;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.item.*;
import net.minecraftforge.registries.ForgeRegistries;
import org.joml.Matrix4f;
import org.lwjgl.opengl.GL11;
import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;

/** Observational only: never emits, cancels or edits a production packet/renderer. */
public final class Probe {
 public static volatile String current="";
 public static final List<Object> events=new CopyOnWriteArrayList<>();
 static Map<String,List<Object>> geometry=new LinkedHashMap<>();
 static Map<String,Object> renderState=new LinkedHashMap<>();
 static List<Object> ghosts=new ArrayList<>();
 static long serial; public static java.util.List<Object> activeVisuals=java.util.List.of();
 public static void active(java.util.List<Cod3VisualPacket> list){activeVisuals=list.stream().map(Probe::packet).toList();}
 static boolean pixelProbe;
 static Map<String,com.mojang.blaze3d.platform.NativeImage> before=new HashMap<>();
 static Map<String,Long> pixelTicks=new HashMap<>();
 static Map<String,Integer> savedPairs=new HashMap<>();
 static Map<String,Object> pixels=new LinkedHashMap<>();
 public static List<Double> v(Vec3 p){return List.of(p.x,p.y,p.z);}
 public static void event(String kind,Object data){if(!current.isEmpty())events.add(Map.of("case",current,"kind",kind,"nano",System.nanoTime(),"thread",Thread.currentThread().getName(),"data",data));}
 public static void wire(Cod3VisualPacket p){event("actual-s2c-handle",packet(p));}
 static Object packet(Cod3VisualPacket p){var m=new LinkedHashMap<String,Object>();m.put("sequence",p.sequence());m.put("template",p.template());m.put("entity",p.entityId());m.put("start",p.start());m.put("duration",p.duration());m.put("origin",v(p.origin()));m.put("direction",v(p.direction()));m.put("tint",p.tint());m.put("tick",p.tick());m.put("seed",p.seed());return m;}
 static void begin(){serial++;geometry=new LinkedHashMap<>();renderState=new LinkedHashMap<>();ghosts=new ArrayList<>();pixels=new LinkedHashMap<>();}
 public static void pixelBefore(String kind,net.minecraftforge.client.event.RenderLevelStageEvent event,boolean active){
  var m=net.minecraft.client.Minecraft.getInstance();
  if(!pixelProbe||current.isEmpty()||!active||event.getStage()!=net.minecraftforge.client.event.RenderLevelStageEvent.Stage.AFTER_PARTICLES||m.level==null)return;
  long tick=m.level.getGameTime();if(Objects.equals(pixelTicks.get(kind),tick))return;pixelTicks.put(kind,tick);
  before.put(kind,net.minecraft.client.Screenshot.takeScreenshot(m.getMainRenderTarget()));
 }
 public static void pixelAfter(String kind){
  var pre=before.remove(kind);if(pre==null)return;var m=net.minecraft.client.Minecraft.getInstance();
  try(pre;var post=net.minecraft.client.Screenshot.takeScreenshot(m.getMainRenderTarget())){
   int changed=0,substantial=0;int x0=post.getWidth(),y0=post.getHeight(),x1=-1,y1=-1;long magnitude=0;
   for(int y=0;y<post.getHeight();y++)for(int x=0;x<post.getWidth();x++){int a=pre.getPixelRGBA(x,y),b=post.getPixelRGBA(x,y);int d=Math.abs((a&255)-(b&255))+Math.abs((a>>8&255)-(b>>8&255))+Math.abs((a>>16&255)-(b>>16&255));if(d>0){changed++;magnitude+=d;x0=Math.min(x0,x);x1=Math.max(x1,x);y0=Math.min(y0,y);y1=Math.max(y1,y);if(d>=12)substantial++;}}
   var report=new LinkedHashMap<String,Object>();report.put("changedPixels",changed);report.put("rgbDifferenceAtLeast12",substantial);report.put("summedRgbDifference",magnitude);report.put("bounds",List.of(x0,y0,x1,y1));
   int count=savedPairs.getOrDefault(kind,0);if(count<2){String prefix=current+"-native-"+kind+"-f"+serial;for(var entry:Map.of("before",pre,"after",post).entrySet()){var copy=new com.mojang.blaze3d.platform.NativeImage(post.getWidth(),post.getHeight(),false);copy.copyFrom(entry.getValue());StatusVisualAcceptance.Client.images.put(prefix+"-"+entry.getKey()+".png",copy);}report.put("nativeBefore",prefix+"-before.png");report.put("nativeAfter",prefix+"-after.png");savedPairs.put(kind,count+1);}
   pixels.put(kind,report);
  }
 }
 static void gl(String kind,Matrix4f m){if(renderState.containsKey(kind))return;renderState.put(kind,Map.of("modelView",m.get(new float[16]),"depthTest",GL11.glIsEnabled(GL11.GL_DEPTH_TEST),"depthWrite",GL11.glGetBoolean(GL11.GL_DEPTH_WRITEMASK),"depthFunc",GL11.glGetInteger(GL11.GL_DEPTH_FUNC),"blend",GL11.glIsEnabled(GL11.GL_BLEND),"cull",GL11.glIsEnabled(GL11.GL_CULL_FACE),"blendSrc",GL11.glGetInteger(GL11.GL_BLEND_SRC),"blendDst",GL11.glGetInteger(GL11.GL_BLEND_DST)));}
 public static void triangle(String kind,Matrix4f m,Vec3 a,Vec3 b,Vec3 c,int color,double alpha){if(current.isEmpty())return;gl(kind,m);geometry.computeIfAbsent(kind,k->new ArrayList<>()).add(List.of(v(a),v(b),v(c),color,alpha));}
 public static void vertex(String kind,Matrix4f m,Vec3 a,int color,double alpha){if(current.isEmpty())return;gl(kind,m);geometry.computeIfAbsent(kind,k->new ArrayList<>()).add(List.of(v(a),color,alpha));}
 public static void ghost(ItemStack s,Matrix4f m,int color,float alpha,ItemDisplayContext c){if(current.isEmpty()||s.isEmpty())return;ghosts.add(Map.of("item",ForgeRegistries.ITEMS.getKey(s.getItem()).toString(),"matrix",m.get(new float[16]),"alpha",alpha,"color",color,"context",c.toString()));}
}
