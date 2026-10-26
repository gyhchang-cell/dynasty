package local.mcmacro;

import java.lang.instrument.Instrumentation;
import java.lang.reflect.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.atomic.AtomicBoolean;

/** Vanilla 1.8.9, read-only telemetry. No transformers, field writes, or input calls. */
public final class StateAgent {
    private static volatile Session current;
    public static synchronized void agentmain(String arguments, Instrumentation instrumentation) throws Exception {
        String[] parts=arguments.split(",",2);
        if(parts.length!=2 || !parts[1].matches("[a-zA-Z0-9-]{32,64}")) throw new IllegalArgumentException("Invalid session");
        int port=Integer.parseInt(parts[0]);
        if(port<1024 || port>65535) throw new IllegalArgumentException("Invalid loopback port");
        Class<?> minecraft=null;
        for(Class<?> type:instrumentation.getAllLoadedClasses()) if(type.getName().equals("ave")) { minecraft=type;break; }
        if(minecraft==null) throw new IllegalStateException("Vanilla 1.8.9 is not loaded");
        if(current!=null) current.close();
        current=new Session(minecraft,port,parts[1]);
        current.start();
    }
    private static Field field(Class<?> type,String name) throws Exception {
        Field field=type.getDeclaredField(name);field.setAccessible(true);return field;
    }
    private static final class Session {
        final DatagramSocket socket;
        final String token;
        final Object minecraft;
        final Method schedule, getState, getBlock, fullCube, getHeld, getItem, heldBlock, getHitPos, posX,posY,posZ,rayTrace,mouseButton,eyeHeight,sprinting,keyboardDown;
        final Field player,world,screen,focus,hit,dead,ground,ticks,flying,capabilities,itemCount,hitType,hitFace,timer,partial,clickDelay;
        final Field[] vectors=new Field[11];
        final Constructor<?> blockPos, collisionBox;
        final Method collisions;
        final Field[] boxCoordinates=new Field[6];
        final Class<?> itemBlock;
        final AtomicBoolean pending=new AtomicBoolean();
        volatile boolean closed;
        volatile long heartbeat=System.nanoTime();
        long sequence;
        Session(Class<?> mc,int port,String token) throws Exception {
            this.token=token;
            ClassLoader loader=mc.getClassLoader();
            Class<?> entity=Class.forName("pk",false,loader), living=Class.forName("pr",false,loader);
            Class<?> position=Class.forName("cj",false,loader), vec=Class.forName("df",false,loader);
            Class<?> block=Class.forName("afh",false,loader), state=Class.forName("alz",false,loader);
            Class<?> box=Class.forName("aug",false,loader);
            collisionBox=box.getConstructor(double.class,double.class,double.class,double.class,double.class,double.class);
            collisions=Class.forName("adm",false,loader).getMethod("a",entity,box);
            for(int i=0;i<6;i++) boxCoordinates[i]=field(box,String.valueOf((char)('a'+i)));
            Class<?> stack=Class.forName("zx",false,loader), target=Class.forName("auh",false,loader);
            itemBlock=Class.forName("yo",false,loader);heldBlock=itemBlock.getMethod("d");
            minecraft=mc.getMethod("A").invoke(null);schedule=mc.getMethod("a",Runnable.class);
            player=field(mc,"h");world=field(mc,"f");screen=field(mc,"m");focus=field(mc,"w");hit=field(mc,"s");
            timer=field(mc,"Y");partial=field(Class.forName("avl",false,loader),"c");
            clickDelay=field(mc,"ap");rayTrace=entity.getMethod("a",double.class,float.class);eyeHeight=entity.getMethod("aS");
            mouseButton=Class.forName("org.lwjgl.input.Mouse",false,loader).getMethod("isButtonDown",int.class);
            sprinting=entity.getMethod("aw");
            keyboardDown=Class.forName("org.lwjgl.input.Keyboard",false,loader).getMethod("isKeyDown",int.class);
            String[] names={"s","t","u","v","w","x","y","z","p","q","r"};
            for(int i=0;i<names.length;i++) vectors[i]=field(entity,names[i]);
            dead=field(entity,"I");ground=field(entity,"C");ticks=field(entity,"W");
            capabilities=field(Class.forName("wn",false,loader),"bA");flying=field(Class.forName("wl",false,loader),"b");
            getState=Class.forName("adm",false,loader).getMethod("p",position);getBlock=state.getMethod("c");fullCube=block.getMethod("u");
            getHeld=living.getMethod("bA");getItem=stack.getMethod("b");itemCount=field(stack,"b");
            getHitPos=target.getMethod("a");hitType=field(target,"a");hitFace=field(target,"b");
            posX=vec.getMethod("n");posY=vec.getMethod("o");posZ=vec.getMethod("p");blockPos=position.getConstructor(int.class,int.class,int.class);
            socket=new DatagramSocket(new InetSocketAddress(InetAddress.getByName("127.0.0.1"),0));
            socket.connect(InetAddress.getByName("127.0.0.1"),port);socket.setSoTimeout(250);
        }
        void start() {
            Thread receiver=new Thread(()->{
                byte[] bytes=new byte[128];
                while(!closed) try {
                    DatagramPacket packet=new DatagramPacket(bytes,bytes.length);socket.receive(packet);
                    String message=new String(bytes,0,packet.getLength(),StandardCharsets.US_ASCII);
                    if(message.equals(token)) heartbeat=System.nanoTime();
                    else if(message.equals("STOP "+token)) close();
                } catch(SocketTimeoutException ignored) {} catch(Exception error) {close();}
            },"MC assistant telemetry heartbeat");receiver.setDaemon(true);receiver.start();
            Thread poller=new Thread(()->{
                while(!closed) {
                    if(System.nanoTime()-heartbeat>3_000_000_000L) {close();break;}
                    if(pending.compareAndSet(false,true)) try {
                        schedule.invoke(minecraft,(Runnable)()->{
                            try {if(!closed) send(snapshot());}
                            catch(Exception error) {close();}
                            finally {pending.set(false);}
                        });
                    } catch(Exception error) {close();}
                    try {Thread.sleep(8);} catch(InterruptedException ignored) {close();}
                }
            },"MC assistant telemetry scheduler");poller.setDaemon(true);poller.start();
        }
        String snapshot() throws Exception {
            long began=System.nanoTime();
            Object p=player.get(minecraft),w=world.get(minecraft);
            StringBuilder out=new StringBuilder(4096).append("{\"token\":\"").append(token).append("\",\"seq\":").append(++sequence);
            boolean active=p!=null&&w!=null&&screen.get(minecraft)==null&&focus.getBoolean(minecraft)&&!dead.getBoolean(p);
            out.append(",\"active\":").append(active);
            if(active) {
                out.append(",\"world\":").append(System.identityHashCode(w));
                out.append(",\"tick\":").append(ticks.getInt(p));
                out.append(",\"partial\":").append(partial.getFloat(timer.get(minecraft)));
                out.append(",\"clickDelay\":").append(clickDelay.getInt(minecraft));
                out.append(",\"useDown\":").append(mouseButton.invoke(null,1));
                out.append(",\"eyeHeight\":").append(eyeHeight.invoke(p));
                out.append(",\"ground\":").append(ground.getBoolean(p));
                out.append(",\"sprinting\":").append(sprinting.invoke(p));
                out.append(",\"controlDown\":").append(keyboardDown.invoke(null,29));
                out.append(",\"flying\":").append(flying.getBoolean(capabilities.get(p)));
                double[] values=new double[vectors.length];out.append(",\"v\":[");
                for(int i=0;i<values.length;i++) {values[i]=((Number)vectors[i].get(p)).doubleValue();if(i>0)out.append(',');out.append(values[i]);}out.append(']');
                Object held=getHeld.invoke(p);boolean blocks=held!=null&&itemCount.getInt(held)>0&&itemBlock.isInstance(getItem.invoke(held))&&(Boolean)fullCube.invoke(heldBlock.invoke(getItem.invoke(held)));
                out.append(",\"blocks\":").append(blocks);
                Object target=hit.get(minecraft);
                if(target!=null&&String.valueOf(hitType.get(target)).equals("BLOCK")) {
                    Object at=getHitPos.invoke(target);
                    out.append(",\"hit\":[").append(posX.invoke(at)).append(',').append(posY.invoke(at)).append(',').append(posZ.invoke(at)).append(']');
                    out.append(",\"face\":\"").append(hitFace.get(target)).append('"');
                }
                // Supplemental logical-position ray. Vanilla rightClickMouse
                // consumes its cached objectMouseOver above; these two rays
                // can disagree. Does not invoke use/place APIs.
                Object useTarget=rayTrace.invoke(p,4.5,1.0f);
                if(useTarget!=null&&String.valueOf(hitType.get(useTarget)).equals("BLOCK")) {
                    Object at=getHitPos.invoke(useTarget);
                    out.append(",\"useHit\":[").append(posX.invoke(at)).append(',').append(posY.invoke(at)).append(',').append(posZ.invoke(at)).append(']');
                    out.append(",\"useFace\":\"").append(hitFace.get(useTarget)).append('"');
                }
                int bx=(int)Math.floor(values[0]),by=(int)Math.floor(values[1]),bz=(int)Math.floor(values[2]);
                out.append(",\"solid\":[");boolean comma=false;
                for(int x=bx-4;x<=bx+4;x++) for(int z=bz-4;z<=bz+4;z++) for(int y=by-3;y<=by+4;y++) {
                    Object b=getBlock.invoke(getState.invoke(w,blockPos.newInstance(x,y,z)));
                    if((Boolean)fullCube.invoke(b)) {if(comma)out.append(',');comma=true;out.append('[').append(x).append(',').append(y).append(',').append(z).append(']');}
                }out.append(']');
                // Query vanilla's actual collision geometry, including slabs,
                // fences and other non-full cubes. No input or world writes.
                Object region=collisionBox.newInstance(values[0]-4.5,values[1]-0.1,values[2]-4.5,values[0]+4.5,values[1]+4.1,values[2]+4.5);
                java.util.List<?> boxes=(java.util.List<?>)collisions.invoke(w,p,region);
                out.append(",\"collisions\":[");comma=false;
                for(Object box:boxes) {
                    if(comma)out.append(',');comma=true;out.append('[');
                    for(int i=0;i<6;i++) {if(i>0)out.append(',');out.append(boxCoordinates[i].getDouble(box));}
                    out.append(']');
                }out.append(']');
            }
            out.append(",\"age\":").append((System.nanoTime()-began)/1e9).append('}');
            return out.toString();
        }
        void send(String message) throws Exception {
            byte[] bytes=message.getBytes(StandardCharsets.UTF_8);
            if(bytes.length<60000)socket.send(new DatagramPacket(bytes,bytes.length));
        }
        void close() {closed=true;socket.close();}
    }
}
