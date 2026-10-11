package com.dynasty.cod3;

import com.dynasty.Dynasty;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

/** Loaded entity UUID + actual travel, sampled once per second. No offline or anchor-only credit. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class WhiteDeerTrail {
    public static final String PROGRESS="cod3_white_deer_trail";
    public static final String RECEIPT="minecraft:overworld:secret_12";
    public static final int REQUIRED_TICKS=6000;
    public static boolean claimed(ServerPlayer p){return p.getPersistentData().getCompound(Player.PERSISTED_NBT_TAG).contains(RECEIPT);}
    public static CompoundTag state(ServerPlayer p){if(!p.getPersistentData().contains(PROGRESS))p.getPersistentData().put(PROGRESS,new CompoundTag());return p.getPersistentData().getCompound(PROGRESS);}
    public static void reset(ServerPlayer p){p.getPersistentData().remove(PROGRESS);}
    private static boolean context(ServerPlayer p,WhiteDeerEntity d){return p.isAlive()&&!p.isSpectator()&&p.level().dimension()==Level.OVERWORLD&&p.isShiftKeyDown()&&p.onGround()&&!p.isPassenger()&&!p.isSprinting()&&!p.getAbilities().flying
            &&d!=null&&d.isAlive()&&d.level()==p.level()&&!d.isPassenger()&&!d.isVehicle()&&!d.frightened()&&p.distanceToSqr(d)>=2.25&&p.distanceToSqr(d)<=100&&p.hasLineOfSight(d);}
    private static Vec3 previous(CompoundTag n,String key){return new Vec3(n.getDouble(key+"X"),n.getDouble(key+"Y"),n.getDouble(key+"Z"));}
    private static void position(CompoundTag n,String key,Vec3 v){n.putDouble(key+"X",v.x);n.putDouble(key+"Y",v.y);n.putDouble(key+"Z",v.z);}
    public static void sample(ServerPlayer p){
        if(claimed(p)){reset(p);return;}
        var n=state(p);var level=p.serverLevel();WhiteDeerEntity d=null;
        if(n.hasUUID("Deer")){var entity=level.getEntity(n.getUUID("Deer"));if(entity instanceof WhiteDeerEntity deer)d=deer;}
        else if(WhiteDeerEntity.morning(level))d=level.getEntitiesOfClass(WhiteDeerEntity.class,p.getBoundingBox().inflate(10),Entity->Entity.isAlive()).stream().min(java.util.Comparator.comparingDouble(p::distanceToSqr)).orElse(null);
        if(!context(p,d)){reset(p);return;}
        long now=level.getGameTime();
        if(!n.hasUUID("Deer")){
            n.putUUID("Deer",d.getUUID());n.putInt("Disturbance",d.disturbance());n.putLong("Last",now);position(n,"Player",p.position());position(n,"Deer",d.position());p.displayClientMessage(Component.translatable("cod3.dynasty.deer.begin"),true);return;
        }
        long elapsed=now-n.getLong("Last");
        if(elapsed==0)return;
        double playerMove=p.position().distanceTo(previous(n,"Player")),deerMove=d.position().distanceTo(previous(n,"Deer"));
        if(elapsed<0||elapsed>25||n.getInt("Disturbance")!=d.disturbance()||playerMove>2||deerMove>2){reset(p);return;}
        // A motionless player cannot complete this by camping beside a static entity.
        if(playerMove<.02){n.putInt("Still",n.getInt("Still")+(int)elapsed);if(n.getInt("Still")>100){reset(p);return;}}
        else n.putInt("Still",0);
        if(deerMove<.02){n.putInt("DeerStill",n.getInt("DeerStill")+(int)elapsed);if(n.getInt("DeerStill")>100){reset(p);return;}}
        else n.putInt("DeerStill",0);
        n.putDouble("Travel",n.getDouble("Travel")+playerMove);n.putDouble("DeerTravel",n.getDouble("DeerTravel")+deerMove);
        n.putInt("Ticks",Math.min(REQUIRED_TICKS,n.getInt("Ticks")+(int)elapsed));n.putLong("Last",now);position(n,"Player",p.position());position(n,"Deer",d.position());
        if(n.getInt("Ticks")>=REQUIRED_TICKS&&n.getDouble("Travel")>=30&&n.getDouble("DeerTravel")>=30){
            n.putLong("ReadyAt",now);n.putLong("At",d.blockPosition().asLong());
            if(SecretTracker.get(level).claim(p,12,d.blockPosition()))reset(p);
        }else if(n.getInt("Ticks")%1200==0)p.displayClientMessage(Component.translatable("cod3.dynasty.deer.progress",n.getInt("Ticks")/20,300),true);
    }
    public static boolean ready(ServerPlayer p,BlockPos at){
        var n=state(p);if(!n.hasUUID("Deer")||!n.contains("ReadyAt")||n.getLong("ReadyAt")!=p.level().getGameTime()||n.getLong("At")!=at.asLong()||n.getInt("Ticks")<REQUIRED_TICKS||n.getDouble("Travel")<30||n.getDouble("DeerTravel")<30)return false;
        var e=p.serverLevel().getEntity(n.getUUID("Deer"));return e instanceof WhiteDeerEntity d&&context(p,d)&&n.getInt("Disturbance")==d.disturbance()&&d.blockPosition().equals(at);
    }
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){if(e.phase==TickEvent.Phase.END&&e.player instanceof ServerPlayer p&&p.tickCount%20==0)sample(p);}
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){if(e.getEntity() instanceof ServerPlayer p)reset(p);}
    @SubscribeEvent public static void login(PlayerEvent.PlayerLoggedInEvent e){if(e.getEntity() instanceof ServerPlayer p)reset(p);}
    @SubscribeEvent public static void changedDimension(PlayerEvent.PlayerChangedDimensionEvent e){if(e.getEntity() instanceof ServerPlayer p)reset(p);}
    private WhiteDeerTrail(){}
}
