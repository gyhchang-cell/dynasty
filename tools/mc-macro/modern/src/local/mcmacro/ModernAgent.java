package local.mcmacro;

import com.google.gson.*;
import java.lang.instrument.Instrumentation;
import java.lang.reflect.Field;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.concurrent.atomic.AtomicBoolean;
import it.unimi.dsi.fastutil.longs.Long2ObjectMap;
import net.minecraft.client.Minecraft;
import net.minecraft.client.MouseHandler;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.*;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.*;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.decoration.ArmorStand;

/** Read-only, game-thread snapshots. No game writes, injected input or remote commands. */
public final class ModernAgent {
    private static volatile boolean running;
    public static synchronized void agentmain(String args, Instrumentation instrumentation) throws Exception {
        if(running) return;
        String[] parts=args.split(",");
        if(parts.length!=2 || !parts[1].matches("[A-Fa-f0-9-]{36}")) throw new IllegalArgumentException("session");
        int port=Integer.parseInt(parts[0]);
        Minecraft mc=Minecraft.getInstance();
        if(mc==null) throw new IllegalStateException("Minecraft not ready");
        Reader reader=new Reader(mc,port,parts[1]);running=true;
        Thread t=new Thread(reader,"mcPvPmax-read-26.1");t.setDaemon(true);t.start();
    }
    static final class Reader implements Runnable {
        final Minecraft mc; final int port; final String token;
        final DatagramSocket socket; final InetAddress loop=InetAddress.getLoopbackAddress();
        final Field prediction,verified,ignoreFirstMove;
        final AtomicBoolean queued=new AtomicBoolean();
        volatile byte[] latest; volatile long sampled;
        int seq;
        Reader(Minecraft mc,int port,String token) throws Exception {
            this.mc=mc;this.port=port;this.token=token;
            socket=new DatagramSocket(new InetSocketAddress("127.0.0.1",0));socket.setSoTimeout(12);
            prediction=ClientLevel.class.getDeclaredField("blockStatePredictionHandler");prediction.setAccessible(true);
            verified=prediction.getType().getDeclaredField("serverVerifiedStates");verified.setAccessible(true);
            ignoreFirstMove=MouseHandler.class.getDeclaredField("ignoreFirstMove");ignoreFirstMove.setAccessible(true);
        }
        public void run() {
            long heartbeat=System.nanoTime();
            try {
                while(System.nanoTime()-heartbeat<3_000_000_000L) {
                    if(queued.compareAndSet(false,true)) mc.execute(()->{
                        try { latest=snapshot().toString().getBytes(StandardCharsets.UTF_8);sampled=System.nanoTime(); }
                        catch(Throwable ex) { JsonObject error=new JsonObject();error.addProperty("active",false);error.addProperty("error",ex.getClass().getSimpleName()+": "+ex.getMessage());latest=error.toString().getBytes(StandardCharsets.UTF_8);sampled=System.nanoTime(); }
                        finally {queued.set(false);}
                    });
                    byte[] data=latest;
                    if(data!=null) {
                        JsonObject packet=JsonParser.parseString(new String(data,StandardCharsets.UTF_8)).getAsJsonObject();
                        packet.addProperty("token",token);packet.addProperty("seq",++seq);
                        packet.addProperty("age",(System.nanoTime()-sampled)/1e9);
                        byte[] bytes=packet.toString().getBytes(StandardCharsets.UTF_8);
                        if(bytes.length<64000) socket.send(new DatagramPacket(bytes,bytes.length,loop,port));
                    }
                    try {
                        byte[] b=new byte[128];DatagramPacket p=new DatagramPacket(b,b.length);socket.receive(p);
                        if(p.getAddress().isLoopbackAddress() && p.getPort()==port && token.equals(new String(b,0,p.getLength(),StandardCharsets.UTF_8))) heartbeat=System.nanoTime();
                    } catch(SocketTimeoutException ignored) {}
                    Thread.sleep(6);
                }
            } catch(Exception ignored) {} finally {socket.close();running=false;}
        }
        JsonObject snapshot() throws Exception {
            JsonObject out=new JsonObject();var p=mc.player;var world=mc.level;
            boolean active=p!=null && world!=null && p.isAlive() && !p.isSpectator() && mc.screen==null && !mc.isPaused() && mc.mouseHandler.isMouseGrabbed();
            out.addProperty("active",active);out.addProperty("version","26.1");
            if(p==null || world==null) return out;
            out.addProperty("world",System.identityHashCode(world));out.addProperty("tick",p.tickCount);
            out.addProperty("dimension",world.dimension().identifier().toString());
            out.addProperty("singleplayer",mc.getSingleplayerServer()!=null);
            out.addProperty("ground",p.onGround());out.addProperty("sneaking",p.isShiftKeyDown());
            out.addProperty("using",p.isUsingItem());out.addProperty("health",p.getHealth());
            out.add("position",vector(p.position()));out.add("eye",vector(p.getEyePosition()));out.add("velocity",vector(p.getDeltaMovement()));
            out.addProperty("yaw",p.getYRot());out.addProperty("pitch",p.getXRot());
            out.addProperty("mouseReady",!ignoreFirstMove.getBoolean(mc.mouseHandler));
            out.addProperty("sprintKey",mc.options.keySprint.saveString());
            out.addProperty("toggleSprint",mc.options.toggleSprint().get());
            out.addProperty("sprintKeyDown",mc.options.keySprint.isDown());
            out.addProperty("sprinting",p.isSprinting());
            out.addProperty("forward",p.input.hasForwardImpulse());
            out.addProperty("sensitivity",mc.options.sensitivity().get());out.addProperty("range",p.blockInteractionRange());
            out.addProperty("selected",p.getInventory().getSelectedSlot());
            out.addProperty("offhand",id(p.getOffhandItem()));
            out.addProperty("useKey",mc.options.keyUse.saveString());
            out.addProperty("leftDown",mc.mouseHandler.isLeftPressed());out.addProperty("rightDown",mc.mouseHandler.isRightPressed());
            JsonArray moveKeys=new JsonArray();boolean moveUsable=true,moveDown=false;
            for(var key:new net.minecraft.client.KeyMapping[]{mc.options.keyUp,mc.options.keyDown,mc.options.keyLeft,mc.options.keyRight}) {
                moveKeys.add(key.saveString());moveDown|=key.isDown();int bindings=0;
                for(var other:mc.options.keyMappings) if(!other.getName().startsWith("key.debug.") && other.saveString().equals(key.saveString())) bindings++;
                moveUsable&=bindings==1;
            }
            out.add("movementKeys",moveKeys);out.addProperty("movementUsable",moveUsable);out.addProperty("movementDown",moveDown);
            // Read only: native mouse/key events remain the sole action path.
            // Combat is irrelevant while placing/charging an anchor. Keep that
            // proven hot path free of collision and entity combat queries.
            String combatItem=id(p.getMainHandItem());
            if(p.getMainHandItem().isEmpty() || combatItem.endsWith("_sword") || combatItem.endsWith("_axe")) {
            JsonObject combat=new JsonObject();
            combat.addProperty("cooldown",p.getAttackStrengthScale(0.5f));
            combat.addProperty("delayTicks",p.getCurrentItemAttackStrengthDelay());
            combat.addProperty("canDisableShield",p.getSecondsToDisableBlocking()>0);
            combat.addProperty("attackKey",mc.options.keyAttack.saveString());
            combat.addProperty("jumpKey",mc.options.keyJump.saveString());
            combat.addProperty("forwardKey",mc.options.keyUp.saveString());
            JsonArray movementKeys=new JsonArray();
            for(var key:new net.minecraft.client.KeyMapping[]{mc.options.keyUp,mc.options.keyDown,mc.options.keyLeft,mc.options.keyRight,mc.options.keyJump,mc.options.keyShift,mc.options.keySprint}) movementKeys.add(key.saveString());
            combat.add("movementKeys",movementKeys);
            int jumpBindings=0,forwardBindings=0;
            for(var key:mc.options.keyMappings) if(!key.getName().startsWith("key.debug.")) {
                if(key.saveString().equals(mc.options.keyJump.saveString())) jumpBindings++;
                if(key.saveString().equals(mc.options.keyUp.saveString())) forwardBindings++;
            }
            combat.addProperty("jumpUsable",jumpBindings==1);
            combat.addProperty("forwardUsable",forwardBindings==1);
            combat.addProperty("jumpDown",mc.options.keyJump.isDown());
            combat.addProperty("forwardDown",mc.options.keyUp.isDown());
            combat.addProperty("hurtTime",p.hurtTime);
            combat.addProperty("fallDistance",p.fallDistance);
            combat.addProperty("critEnvironment",!p.onClimbable() && !p.isInWater() && !p.isMobilityRestricted() && !p.isPassenger() && !p.isFallFlying());
            int critTicks=0;double fallY=0,fallVelocity=p.getDeltaMovement().y;
            if(!p.onGround() && fallVelocity<0) for(int step=1;step<=3;step++) {
                fallY+=fallVelocity;fallVelocity=(fallVelocity-0.08)*0.98;
                if(!world.noCollision(p,p.getBoundingBox().expandTowards(p.getDeltaMovement().x*step,fallY,p.getDeltaMovement().z*step))) break;
                critTicks=step;
            }
            combat.addProperty("critTicks",critTicks);
            var damage=p.getLastDamageSource();var attacker=damage==null?null:damage.getEntity();
            combat.addProperty("attacker",attacker instanceof LivingEntity?attacker.getId():-1);
            // Only use the actual vanilla crosshair entity, never acquire/aim at nearby players.
            if(mc.hitResult instanceof EntityHitResult hit && hit.getEntity() instanceof LivingEntity target && !(target instanceof ArmorStand)) {
                JsonObject t=new JsonObject();t.addProperty("id",target.getId());
                t.addProperty("distance",p.getEyePosition().distanceTo(hit.getLocation()));
                t.addProperty("range",p.entityInteractionRange());
                t.addProperty("valid",target.isAlive() && !target.isSpectator() && target.isAttackable() && p.hasLineOfSight(target) && p.isWithinEntityInteractionRange(target,0) && p.isWithinAttackRange(p.getMainHandItem(),target.getBoundingBox(),0) && (!(target instanceof Player other) || p.canHarmPlayer(other)));
                t.addProperty("hurtTime",target.hurtTime);t.addProperty("ground",target.onGround());
                // Vanilla blocking uses horizontal head direction, not pitch.
                // Looking down/up must not turn an active shield into an opening.
                Vec3 delta=p.position().subtract(target.position());
                Vec3 towards=new Vec3(delta.x,0,delta.z).normalize();
                double yaw=Math.toRadians(target.getYHeadRot());
                double angle=Math.acos(Math.max(-1,Math.min(1,towards.dot(new Vec3(-Math.sin(yaw),0,Math.cos(yaw))))));
                var shield=target.getItemBlockingWith();
                var blocking=shield==null?null:shield.get(net.minecraft.core.component.DataComponents.BLOCKS_ATTACKS);
                t.addProperty("blocking",blocking!=null && blocking.resolveBlockedDamage(p.damageSources().playerAttack(p),1f,angle)>0);
                combat.add("target",t);
            }
            boolean safeJump=p.onGround() && !p.horizontalCollision && !p.isInWater() && !p.isInLava() && !p.onClimbable() && !p.isPassenger() && !p.isFallFlying() && !p.isCrouching() && world.noCollision(p,p.getBoundingBox().move(0,1.3,0));
            for(double dx:new double[]{-.31,.31}) for(double dz:new double[]{-.31,.31}) {
                BlockPos foot=BlockPos.containing(p.getX()+dx+p.getDeltaMovement().x*3,p.getY()-.05,p.getZ()+dz+p.getDeltaMovement().z*3);
                safeJump &= world.getBlockState(foot).isCollisionShapeFullBlock(world,foot);
            }
            combat.addProperty("safeJump",safeJump);out.add("combat",combat);
            }
            JsonArray slots=new JsonArray(),keys=new JsonArray();
            for(int i=0;i<9;i++) {
                ItemStack stack=p.getInventory().getItem(i);JsonObject slot=new JsonObject();
                slot.addProperty("slot",i);slot.addProperty("id",id(stack));slot.addProperty("count",stack.getCount());
                boolean full=stack.getItem() instanceof BlockItem bi && bi.getBlock().defaultBlockState().isCollisionShapeFullBlock(world,p.blockPosition());
                slot.addProperty("full",full);slots.add(slot);keys.add(mc.options.keyHotbarSlots[i].saveString());
            }
            out.add("slots",slots);out.add("keys",keys);
            JsonArray bound=new JsonArray();for(var key:mc.options.keyMappings) if(key.saveString().equals("key.keyboard.v") && !key.getName().startsWith("key.debug.")) bound.add(key.getName());out.add("triggerBindings",bound);
            if(mc.hitResult instanceof BlockHitResult hit && hit.getType()==HitResult.Type.BLOCK) {
                JsonObject h=new JsonObject();h.add("pos",pos(hit.getBlockPos()));h.addProperty("face",hit.getDirection().name());h.add("point",vector(hit.getLocation()));out.add("hit",h);
            }
            Long2ObjectMap<?> pending=(Long2ObjectMap<?>)verified.get(prediction.get(world));
            JsonArray cells=new JsonArray(),palette=new JsonArray(),volume=new JsonArray();
            var indices=new LinkedHashMap<String,Integer>();
            for(int value:new int[]{p.getBlockX()-5,p.getBlockX()+5,p.getBlockY()-5,p.getBlockY()+5,p.getBlockZ()-5,p.getBlockZ()+5}) volume.add(value);
            // Cover vertical interaction range too. Omit confirmed air and use
            // palette/flag encoding so even a dense volume fits one local packet.
            for(int x=p.getBlockX()-5;x<=p.getBlockX()+5;x++) for(int z=p.getBlockZ()-5;z<=p.getBlockZ()+5;z++) for(int y=p.getBlockY()-5;y<=p.getBlockY()+5;y++) {
                BlockPos at=new BlockPos(x,y,z);BlockState state=world.getBlockState(at);
                boolean predicted=pending.containsKey(at.asLong());
                if(state.isAir() && !predicted) continue;
                String blockID=BuiltInRegistries.BLOCK.getKey(state.getBlock()).toString();
                Integer index=indices.get(blockID);
                if(index==null) {index=indices.size();indices.put(blockID,index);palette.add(blockID);}
                JsonArray cell=new JsonArray();cell.add(x);cell.add(y);cell.add(z);
                cell.add(index);
                cell.add((state.isCollisionShapeFullBlock(world,at)?1:0)|(state.canBeReplaced()?2:0)|(predicted?4:0));
                cell.add(state.is(Blocks.RESPAWN_ANCHOR)?state.getValue(RespawnAnchorBlock.CHARGE):-1);
                cells.add(cell);
            }
            out.add("cells",cells);out.add("palette",palette);out.add("volume",volume);return out;
        }
        static String id(ItemStack item) {return item.isEmpty()?"minecraft:air":BuiltInRegistries.ITEM.getKey(item.getItem()).toString();}
        static JsonArray pos(BlockPos p) {JsonArray a=new JsonArray();a.add(p.getX());a.add(p.getY());a.add(p.getZ());return a;}
        static JsonArray vector(Vec3 v) {JsonArray a=new JsonArray();a.add(v.x);a.add(v.y);a.add(v.z);return a;}
    }
}
