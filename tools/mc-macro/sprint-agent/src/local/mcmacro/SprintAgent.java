package local.mcmacro;
import java.lang.instrument.Instrumentation;
import java.lang.reflect.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.Executor;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.BooleanSupplier;
/** Version independent, read-only logical sprint key observation. No game writes. */
public final class SprintAgent {
 static volatile Session current;
 public static synchronized void agentmain(String args, Instrumentation inst) throws Exception {
  String[] p=args.split(",",2);
  if(p.length!=2 || !p[1].matches("[a-zA-Z0-9-]{32,64}")) throw new IllegalArgumentException();
  int port=Integer.parseInt(p[0]);if(port<1024||port>65535)throw new IllegalArgumentException();
  if(current!=null)current.close();current=new Session(inst,port,p[1]);current.start();
 }
 static Object find(Instrumentation inst)throws Exception {
  for(Class<?> type:inst.getAllLoadedClasses()) {
   // Match a key-binding registry by structure and exact translation key,
   // independently of official, obfuscated, MCP or intermediary class names.
   if(type.isArray()||type.isInterface()||type.getName().startsWith("java."))continue;
   Field[] fields;
   try{fields=type.getDeclaredFields();}catch(Throwable e){continue;}
   boolean text=false,flag=false;
   for(Field f:fields)if(!Modifier.isStatic(f.getModifiers())){text|=f.getType()==String.class;flag|=f.getType()==boolean.class;}
   if(!text||!flag)continue;
   for(Field f:fields)if(Modifier.isStatic(f.getModifiers())&&Map.class.isAssignableFrom(f.getType())) {
    try{f.setAccessible(true);Object map=f.get(null);if(!(map instanceof Map))continue;
     Object value=((Map<?,?>)map).get("key.sprint");if(value!=null&&type.isInstance(value))return value;
    }catch(Throwable e){}
   }
  }
  throw new IllegalStateException("sprint registry unavailable");
 }
 static Field downField(Object key)throws Exception {
  List<Field> flags=new ArrayList<>();
  for(Class<?> t=key.getClass();t!=null&&t!=Object.class;t=t.getSuperclass())
   for(Field f:t.getDeclaredFields())if(!Modifier.isStatic(f.getModifiers())&&f.getType()==boolean.class)flags.add(f);
  // Ambiguous modded bindings are rejected rather than guessed.
  if(flags.size()!=1)throw new IllegalStateException("ambiguous sprint state");
  Field f=flags.get(0);f.setAccessible(true);return f;
 }
 static Executor executor(Instrumentation inst,Object key)throws Exception {
  Class<?> base=downField(key).getDeclaringClass();
  for(Class<?> t:inst.getAllLoadedClasses())try{
   if(!Executor.class.isAssignableFrom(t)||Modifier.isAbstract(t.getModifiers()))continue;
   boolean options=false;
   for(Field f:t.getDeclaredFields())if(!Modifier.isStatic(f.getModifiers())&&!f.getType().isPrimitive()&&!f.getType().getName().startsWith("java."))
    for(Field k:f.getType().getDeclaredFields())if(base.isAssignableFrom(k.getType()))options=true;
   if(!options)continue;
   for(Field f:t.getDeclaredFields())if(Modifier.isStatic(f.getModifiers())&&f.getType()==t){f.setAccessible(true);Object v=f.get(null);if(v instanceof Executor)return (Executor)v;}
  }catch(Throwable ignored){}
  throw new IllegalStateException("game executor unavailable");
 }
 static boolean toggle(Object key)throws Exception {
  BooleanSupplier option=null;
  for(Class<?> t=key.getClass();t!=null&&t!=Object.class;t=t.getSuperclass())for(Field f:t.getDeclaredFields())
   if(!Modifier.isStatic(f.getModifiers())&&BooleanSupplier.class.isAssignableFrom(f.getType())){
    if(option!=null)throw new IllegalStateException("ambiguous toggle option");f.setAccessible(true);option=(BooleanSupplier)f.get(key);
   }
  return option!=null&&option.getAsBoolean();
 }
 static final class Session implements Runnable {
  final Instrumentation inst;final DatagramSocket socket;final String token;volatile boolean closed;long seq;
  Session(Instrumentation i,int port,String t)throws Exception{inst=i;token=t;socket=new DatagramSocket(new InetSocketAddress("127.0.0.1",0));socket.connect(InetAddress.getByName("127.0.0.1"),port);socket.setSoTimeout(500);}
  void start(){Thread t=new Thread(this,"mc-sprint-readonly");t.setDaemon(true);t.start();}
  void close(){closed=true;socket.close();}
  public void run(){
   Object key=null;Field down=null;Executor executor=null;Method grabbed=null;long last=System.nanoTime(),retry=0;
   final AtomicBoolean pending=new AtomicBoolean();final String[] sampled={"unknown\t0\t0"};final long[] sampledAt={0};
   while(!closed&&System.nanoTime()-last<3000000000L)try{
    if(key==null&&System.nanoTime()>retry){retry=System.nanoTime()+1000000000L;try{key=find(inst);down=downField(key);
      try{grabbed=Class.forName("org.lwjgl.input.Mouse",false,key.getClass().getClassLoader()).getMethod("isGrabbed");}catch(Exception modern){executor=executor(inst,key);}}catch(Throwable e){key=null;down=null;}}
    if(key!=null&&pending.compareAndSet(false,true)){
     final Object observed=key;final Field field=down;final Method mouse=grabbed;
     Runnable sample=()->{try{
      boolean capture;
      if(mouse!=null)capture=(Boolean)mouse.invoke(null);
      else{Class<?> glfw=Class.forName("org.lwjgl.glfw.GLFW",false,observed.getClass().getClassLoader());long window=(Long)glfw.getMethod("glfwGetCurrentContext").invoke(null);
       capture=window!=0&&((Integer)glfw.getMethod("glfwGetInputMode",long.class,int.class).invoke(null,window,0x33001))==0x34003;}
      synchronized(sampled){sampled[0]=(field.getBoolean(observed)?"1":"0")+"\t"+(capture?"1":"0")+"\t"+(toggle(observed)?"1":"0");sampledAt[0]=System.nanoTime();}
     }catch(Throwable e){synchronized(sampled){sampledAt[0]=0;}}finally{pending.set(false);}};
     try{if(executor!=null)executor.execute(sample);else sample.run();}
     catch(Throwable rejected){pending.set(false);synchronized(sampled){sampledAt[0]=0;}key=null;executor=null;grabbed=null;}
    }
    String value;synchronized(sampled){value=System.nanoTime()-sampledAt[0]<150000000L?sampled[0]:"unknown\t0\t0";}
    byte[] data=(token+"\t"+(++seq)+"\t"+value).getBytes(StandardCharsets.US_ASCII);socket.send(new DatagramPacket(data,data.length));
    DatagramPacket ack=new DatagramPacket(new byte[128],128);socket.receive(ack);
    String msg=new String(ack.getData(),0,ack.getLength(),StandardCharsets.US_ASCII);if(msg.equals(token))last=System.nanoTime();else if(msg.equals("STOP "+token))break;
    Thread.sleep(25);
   }catch(SocketTimeoutException e){}catch(Throwable e){if(!closed)try{Thread.sleep(100);}catch(InterruptedException ignored){break;}}
   close();
  }
 }
}
