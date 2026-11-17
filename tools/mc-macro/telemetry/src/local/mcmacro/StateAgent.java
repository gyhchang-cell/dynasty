package local.mcmacro;

import java.lang.instrument.Instrumentation;
import java.lang.reflect.*;
import java.io.DataOutput;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.Set;
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
        final Field player,world,screen,focus,hit,dead,ground,ticks,flying,capabilities,itemCount,hitType,hitFace,timer,partial,clickDelay,headYaw,ticksDue;
        final Field[] vectors=new Field[11];
        final Constructor<?> blockPos, collisionBox;
        final Method collisions;
        final Field[] boxCoordinates=new Field[6];
        final Class<?> itemBlock;
        final AtomicBoolean pending=new AtomicBoolean();
        final InventoryTelemetry inventory=new InventoryTelemetry();
        volatile boolean closed;
        volatile boolean geometry=true;
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
            ticksDue=field(timer.getType(),"b");headYaw=field(living,"aK");clickDelay=field(mc,"ap");rayTrace=entity.getMethod("a",double.class,float.class);eyeHeight=entity.getMethod("aS");
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
                    else if(message.equals(token+" LIGHT")) {geometry=false;heartbeat=System.nanoTime();}
                    else if(message.equals(token+" FULL")) {geometry=true;heartbeat=System.nanoTime();}
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
            boolean includeGeometry=geometry;
            Object p=player.get(minecraft),w=world.get(minecraft);
            StringBuilder out=new StringBuilder(4096).append("{\"token\":\"").append(token).append("\",\"seq\":").append(++sequence);
            boolean active=p!=null&&w!=null&&screen.get(minecraft)==null&&focus.getBoolean(minecraft)&&!dead.getBoolean(p);
            out.append(",\"active\":").append(active);
            out.append(",\"geometry\":").append(includeGeometry);
            if(active) {
                out.append(",\"world\":").append(System.identityHashCode(w));
                out.append(",\"tick\":").append(ticks.getInt(p));
                out.append(",\"partial\":").append(partial.getFloat(timer.get(minecraft)));
                out.append(",\"ticksDue\":").append(ticksDue.getInt(timer.get(minecraft)));
                out.append(",\"clickDelay\":").append(clickDelay.getInt(minecraft));
                out.append(",\"useDown\":").append(mouseButton.invoke(null,1));
                out.append(",\"eyeHeight\":").append(eyeHeight.invoke(p));
                out.append(",\"headYaw\":").append(headYaw.getFloat(p));
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
                if(includeGeometry) {
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
                } else out.append(",\"solid\":[],\"collisions\":[]");
                inventory.append(out,minecraft,p,w);
            } else {
                inventory.clear();
                if(!includeGeometry) out.append(",\"solid\":[],\"collisions\":[]");
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

    /** Optional, independently fail-closed: never append a partial inventory object. */
    private static final class InventoryTelemetry {
        InventoryReader reader;
        boolean unavailable;
        long retryAfter;
        void clear() {if(reader!=null) reader.clear();}
        void append(StringBuilder packet,Object mc,Object p,Object w) {
            if(unavailable || System.nanoTime()<retryAfter) return;
            if(reader==null) try {reader=new InventoryReader(mc.getClass());}
            catch(Exception | LinkageError error) {unavailable=true;return;}
            try {
                String observation=reader.snapshot(mc,p,w);
                // Both builders contain ASCII only. Leave room for the packet age
                // so this optional field cannot push a valid bridge packet over its UDP limit.
                if(packet.length()+observation.length()<59000) packet.append(",\"inventory\":").append(observation);
            } catch(Exception | LinkageError error) {
                clear();retryAfter=System.nanoTime()+50_000_000L;
            }
        }
    }

    /** Mappings verified with /usr/bin/javap on the local vanilla 1.8.9 jar.
     * See research/experiments-195/telemetry-mappings.txt. All game access is read-only.
     */
    private static final class InventoryReader {
        final Field inventory,stacks,selected,settings,hotbar,keyBindings,hit,hitType,count;
        final Method mainThread,keyCode,getItem,metadata,damageable,maxDamage,itemID;
        final Method hitPos,posX,posY,posZ,getState,getBlock,blockID,hardness,material,handHarvest;
        final Method strength,harvest,enchantment,blockFromItem,fullCube,tag,tagType,tagWrite;
        final Method compoundKeys,compoundGet,listSize,listType,listGet;
        final Class<?> sword,tool,shears,hoe,itemBlock;
        final Class<?>[] nbtTypes=new Class<?>[12];
        final Identity[] identities=new Identity[9];
        Object previousPlayer,previousWorld;

        InventoryReader(Class<?> mc) throws Exception {
            ClassLoader loader=mc.getClassLoader();
            Class<?> player=Class.forName("wn",false,loader), inv=Class.forName("wm",false,loader);
            Class<?> stack=Class.forName("zx",false,loader), item=Class.forName("zw",false,loader);
            Class<?> gameSettings=Class.forName("avh",false,loader), key=Class.forName("avb",false,loader);
            Class<?> target=Class.forName("auh",false,loader), hitEnum=Class.forName("auh$a",false,loader);
            Class<?> position=Class.forName("cj",false,loader), vec=Class.forName("df",false,loader);
            Class<?> world=Class.forName("adm",false,loader), state=Class.forName("alz",false,loader);
            Class<?> block=Class.forName("afh",false,loader), mat=Class.forName("arm",false,loader);
            Class<?> nbt=Class.forName("eb",false,loader), compound=Class.forName("dn",false,loader);
            Class<?> list=Class.forName("du",false,loader);
            sword=Class.forName("aay",false,loader);tool=Class.forName("za",false,loader);
            shears=Class.forName("aap",false,loader);hoe=Class.forName("zv",false,loader);
            itemBlock=Class.forName("yo",false,loader);
            mainThread=readMethod(mc,"aJ",boolean.class);
            inventory=readField(player,"bi",inv);stacks=readField(inv,"a",Array.newInstance(stack,0).getClass());
            selected=readField(inv,"c",int.class);count=readField(stack,"b",int.class);
            settings=readField(mc,"t",gameSettings);hotbar=readField(gameSettings,"aw",Array.newInstance(key,0).getClass());
            keyBindings=readField(gameSettings,"ax",Array.newInstance(key,0).getClass());
            keyCode=readMethod(key,"i",int.class);
            hit=readField(mc,"s",target);hitType=readField(target,"a",hitEnum);
            hitPos=readMethod(target,"a",position);
            posX=readMethod(vec,"n",int.class);posY=readMethod(vec,"o",int.class);posZ=readMethod(vec,"p",int.class);
            getState=readMethod(world,"p",state,position);getBlock=readMethod(state,"c",block);
            blockID=readMethod(block,"a",int.class,block);hardness=readMethod(block,"g",float.class,world,position);
            material=readMethod(block,"t",mat);handHarvest=readMethod(mat,"l",boolean.class);
            getItem=readMethod(stack,"b",item);metadata=readMethod(stack,"i",int.class);
            damageable=readMethod(stack,"e",boolean.class);maxDamage=readMethod(stack,"j",int.class);
            itemID=readMethod(item,"b",int.class,item);
            strength=readMethod(stack,"a",float.class,block);harvest=readMethod(stack,"b",boolean.class,block);
            enchantment=readMethod(Class.forName("ack",false,loader),"a",int.class,int.class,stack);
            blockFromItem=readMethod(itemBlock,"d",block);fullCube=readMethod(block,"u",boolean.class);
            tag=readMethod(stack,"o",compound);tagType=readMethod(nbt,"a",byte.class);
            tagWrite=nbt.getDeclaredMethod("a",DataOutput.class);tagWrite.setAccessible(true);
            require(tagWrite.getReturnType()==void.class && !Modifier.isStatic(tagWrite.getModifiers()));
            compoundKeys=readMethod(compound,"c",Set.class);compoundGet=readMethod(compound,"a",nbt,String.class);
            listSize=readMethod(list,"c",int.class);listType=readMethod(list,"f",int.class);listGet=readMethod(list,"g",nbt,int.class);
            String[] types={"dq","dm","dz","dt","dv","dr","dp","dl","ea","du","dn","ds"};
            for(int i=0;i<types.length;i++) nbtTypes[i]=Class.forName(types[i],false,loader);
        }
        private static Field readField(Class<?> type,String name,Class<?> expected) throws Exception {
            Field result=field(type,name);
            require(result.getType()==expected && !Modifier.isStatic(result.getModifiers()));return result;
        }
        private static Method readMethod(Class<?> type,String name,Class<?> result,Class<?>... args) throws Exception {
            Method method=type.getMethod(name,args);require(method.getReturnType()==result);return method;
        }
        private static void require(boolean valid) {
            if(!valid) throw new IllegalStateException("Invalid optional inventory observation");
        }
        void clear() {Arrays.fill(identities,null);previousPlayer=null;previousWorld=null;}

        String snapshot(Object mc,Object p,Object w) throws Exception {
            // No game objects are read before this check; this runs only in the scheduled callback.
            require((Boolean)mainThread.invoke(mc));
            long oldest=System.nanoTime();
            if(p!=previousPlayer || w!=previousWorld) {clear();previousPlayer=p;previousWorld=w;}
            Object inv=inventory.get(p);
            int current=selected.getInt(inv);require(current>=0 && current<9);
            Object[] contents=(Object[])stacks.get(inv);require(contents!=null && contents.length>=9);
            Object gameSettings=settings.get(mc);
            Object[] bindings=(Object[])hotbar.get(gameSettings);require(bindings!=null && bindings.length==9);
            Object[] allBindings=(Object[])keyBindings.get(gameSettings);
            require(allBindings!=null && allBindings.length>bindings.length);
            StringBuilder out=new StringBuilder(2048).append("{\"selected\":").append(current).append(",\"keys\":[");
            for(int i=0;i<9;i++) {
                require(bindings[i]!=null);
                for(int j=0;j<i;j++) require(bindings[i]!=bindings[j]);
                if(i>0) out.append(',');out.append(keyCode.invoke(bindings[i]));
            }
            out.append("],\"blockedKeys\":[");boolean blockedComma=false;int seenHotbar=0;
            // avh.ax combines all action bindings with aw. Exclude by binding
            // identity, never by keycode: an action sharing a hotbar key must block it.
            for(Object binding:allBindings) {
                require(binding!=null);boolean isHotbar=false;
                for(int i=0;i<9;i++) if(binding==bindings[i]) {isHotbar=true;seenHotbar|=1<<i;}
                if(!isHotbar) {
                    if(blockedComma) out.append(',');blockedComma=true;out.append(keyCode.invoke(binding));
                }
            }
            require(seenHotbar==511 && blockedComma);out.append(']');
            // Always fresh objectMouseOver, including renderer entity occlusion. Never use Entity.rayTrace.
            Object actualHit=hit.get(mc), block=null;
            String hitKind="unknown";
            if(actualHit!=null) {
                Object type=hitType.get(actualHit);
                String name=type instanceof Enum<?> ? ((Enum<?>)type).name() : "";
                if(name.equals("BLOCK")) hitKind="block";
                else if(name.equals("ENTITY")) hitKind="entity";
                else if(name.equals("MISS")) hitKind="miss";
            }
            out.append(",\"hitKind\":\"").append(hitKind).append('"');
            boolean emptyHarvest=false;
            double targetHardness=0;
            if(hitKind.equals("block")) {
                Object at=hitPos.invoke(actualHit);require(at!=null);
                block=getBlock.invoke(getState.invoke(w,at));require(block!=null);
                int id=(Integer)blockID.invoke(null,block);require(id>0);
                targetHardness=((Number)hardness.invoke(block,w,at)).doubleValue();require(Double.isFinite(targetHardness));
                emptyHarvest=(Boolean)handHarvest.invoke(material.invoke(block));
                // Includes bed ID 26 unchanged; bed preference belongs to Swift, not telemetry.
                out.append(",\"blockID\":").append(id).append(",\"hardness\":").append(targetHardness);
                out.append(",\"target\":[").append(posX.invoke(at)).append(',').append(posY.invoke(at)).append(',').append(posZ.invoke(at)).append(']');
            } else out.append(",\"blockID\":null,\"hardness\":null,\"target\":null");
            out.append(",\"slots\":[");boolean comma=false;
            NbtBudget budget=new NbtBudget();
            for(int slot=0;slot<9;slot++) {
                Object stack=contents[slot];
                if(stack==null || count.getInt(stack)<=0) {identities[slot]=null;continue;}
                int size=count.getInt(stack), meta=(Integer)metadata.invoke(stack);
                Object item=getItem.invoke(stack);require(item!=null && size<=64 && meta>=0);
                int id=(Integer)itemID.invoke(null,item);require(id>0);
                if((Boolean)damageable.invoke(stack)) {
                    int limit=(Integer)maxDamage.invoke(stack);require(limit>0 && meta<=limit);
                }
                Object nbt=tag.invoke(stack);
                Identity identity=identities[slot];
                long now=System.nanoTime();
                if(identity==null || identity.stack!=stack || identity.item!=item || identity.nbt!=nbt ||
                        identity.itemID!=id || identity.metadata!=meta || now-identity.sampled>=50_000_000L) {
                    String value=id+":"+meta+":sha256:"+digest(nbt,budget);
                    identity=new Identity(stack,item,nbt,id,meta,now,value);identities[slot]=identity;
                }
                oldest=Math.min(oldest,identity.sampled);
                String kind=sword.isInstance(item)?"sword":
                    (tool.isInstance(item)||shears.isInstance(item)||hoe.isInstance(item))?"tool":
                    itemBlock.isInstance(item)?"block":"other";
                boolean full=kind.equals("block") && (Boolean)fullCube.invoke(blockFromItem.invoke(item));
                double score=1;
                if(block!=null && targetHardness>0) {
                    double base=((Number)strength.invoke(stack,block)).doubleValue();
                    require(Double.isFinite(base) && base>=0);
                    int efficiency=base>1 ? (Integer)enchantment.invoke(null,32,stack) : 0;
                    boolean canHarvest=emptyHarvest || (Boolean)harvest.invoke(stack,block);
                    score=relativeScore(base,efficiency,emptyHarvest,canHarvest);
                }
                require(Double.isFinite(score) && score>=0);
                if(comma) out.append(',');comma=true;
                out.append("{\"slot\":").append(slot).append(",\"itemID\":").append(id).append(",\"metadata\":").append(meta);
                out.append(",\"count\":").append(size).append(",\"identity\":\"").append(identity.value);
                out.append("\",\"kind\":\"").append(kind).append("\",\"fullBlock\":").append(full).append(",\"score\":").append(score).append('}');
            }
            return out.append("],\"age\":").append((System.nanoTime()-oldest)/1e9).append('}').toString();
        }
        private static double relativeScore(double base,int efficiency,boolean emptyHarvest,boolean canHarvest) {
            // wn.a: efficiency only when base > 1. Common potion/water/ground factors
            // and hardness cancel. afh.a uses /30 if harvestable, otherwise /100.
            // Thus an empty selected slot has exactly score 1, with no handScore needed.
            if(base>1 && efficiency>0) base+=(double)efficiency*efficiency+1;
            return base*(emptyHarvest?30.0:100.0)/(canHarvest?30.0:100.0);
        }
        private String digest(Object nbt,NbtBudget budget) throws Exception {
            MessageDigest hash=MessageDigest.getInstance("SHA-256");
            DataOutputStream out=new DataOutputStream(new OutputStream() {
                @Override public void write(int value) throws IOException {budget.bytes(1);hash.update((byte)value);}
                @Override public void write(byte[] bytes,int offset,int length) throws IOException {
                    budget.bytes(length);hash.update(bytes,offset,length);
                }
            });
            if(nbt==null) out.writeByte(0);else writeTag(nbt,out,budget,0);
            char[] hex="0123456789abcdef".toCharArray();StringBuilder result=new StringBuilder(64);
            for(byte b:hash.digest()) result.append(hex[(b&255)>>>4]).append(hex[b&15]);
            return result.toString();
        }
        private void writeTag(Object nbt,DataOutputStream out,NbtBudget budget,int depth) throws Exception {
            require(nbt!=null && depth<=64 && --budget.nodes>=0);
            int type=((Number)tagType.invoke(nbt)).intValue();
            require(type>0 && type<nbtTypes.length && nbt.getClass()==nbtTypes[type]);
            out.writeByte(type);
            if(type==10) {
                Set<?> keys=(Set<?>)compoundKeys.invoke(nbt);require(keys.size()<=budget.nodes);
                String[] names=keys.toArray(new String[0]);Arrays.sort(names);out.writeInt(names.length);
                for(String name:names) {out.writeUTF(name);writeTag(compoundGet.invoke(nbt,name),out,budget,depth+1);}
            } else if(type==9) {
                int size=(Integer)listSize.invoke(nbt), elementType=(Integer)listType.invoke(nbt);
                require(size>=0 && size<=budget.nodes && elementType>=0 && elementType<nbtTypes.length && (size==0 || elementType>0));
                out.writeByte(elementType);out.writeInt(size);
                for(int i=0;i<size;i++) {
                    Object child=listGet.invoke(nbt,i);require(child!=null && ((Number)tagType.invoke(child)).intValue()==elementType);
                    writeTag(child,out,budget,depth+1);
                }
            } else {
                // Only verified primitive writers. du.a(DataOutput) mutates list type!
                tagWrite.invoke(nbt,out);
            }
        }
    }
    private static final class Identity {
        final Object stack,item,nbt;
        final int itemID,metadata;
        final long sampled;
        final String value;
        Identity(Object stack,Object item,Object nbt,int itemID,int metadata,long sampled,String value) {
            this.stack=stack;this.item=item;this.nbt=nbt;this.itemID=itemID;this.metadata=metadata;this.sampled=sampled;this.value=value;
        }
    }
    private static final class NbtBudget {
        int remaining=65536,nodes=4096;
        void bytes(int count) throws IOException {
            if(count<0 || count>remaining) throw new IOException("Optional inventory NBT budget exceeded");
            remaining-=count;
        }
    }
}
