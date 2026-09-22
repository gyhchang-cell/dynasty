package com.dynasty;

import com.dynasty.network.DragonDescentPacket;
import com.dynasty.network.DynastyNetwork;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.living.LivingKnockBackEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;
import java.util.*;

/** Defers an accepted Qinglong melee hit, preserving its already-computed weapon damage. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class QinglongDescent {
    public static final int WINDUP_TICKS=32;
    public static final int DRAGON_START_TICK=18;
    public static final int DELAY=WINDUP_TICKS;
    private static final ResourceKey<DamageType> DAMAGE=ResourceKey.create(Registries.DAMAGE_TYPE,
            new ResourceLocation(Dynasty.MODID,"qinglong_descent"));
    private record Strike(long id,ResourceKey<Level> dimension,UUID attacker,UUID target,float damage,long due,float yaw,
                          int targetEntityId,Vec3 initialCenter) {}
    private static final List<Strike> PENDING=new ArrayList<>();
    private record BoundTarget(ResourceKey<Level> dimension,UUID target) {}
    private static final class Binding {
        final Vec3 feet;
        long until,lastCooldownTick=Long.MIN_VALUE;
        Binding(Vec3 feet,long until){this.feet=feet;this.until=until;}
    }
    private static final Map<BoundTarget,Binding> BINDINGS=new HashMap<>();
    private static long nextId;
    // Prevent trinket-generated secondary hits during the landing from creating another dragon.
    private static boolean resolving;
    public static boolean isDragonDamage(DamageSource source){return source.is(DAMAGE);}
    public static boolean shouldDefer(DamageSource source) {
        return !resolving && !isDragonDamage(source) && source.getEntity() instanceof LivingEntity attacker
                && source.getDirectEntity()==attacker && attacker.getMainHandItem().is(DynastyWeapons.QINGLONG_DAO.get());
    }
    @SubscribeEvent(priority=EventPriority.LOWEST)
    public static void mark(LivingHurtEvent event) {
        if(event.isCanceled() || event.getAmount()<=0 || !Float.isFinite(event.getAmount())
                || !(event.getEntity().level() instanceof ServerLevel level) || !shouldDefer(event.getSource()))return;
        var attacker=(LivingEntity)event.getSource().getEntity();
        var target=event.getEntity();
        if(!target.isAlive() || !attacker.isAlive() || PENDING.size()>=2048)return;
        Strike strike=new Strike(++nextId,level.dimension(),attacker.getUUID(),target.getUUID(),event.getAmount(),
                level.getGameTime()+DELAY,attacker.getYRot(),target.getId(),target.getBoundingBox().getCenter());
        PENDING.add(strike);
        if(!(target instanceof Player)) {
            var key=new BoundTarget(level.dimension(),target.getUUID());
            var previous=BINDINGS.get(key);
            var binding=previous==null?new Binding(target.position(),strike.due):previous;
            binding.until=strike.due;
            BINDINGS.put(key,binding);
            target.stopRiding();
            hold(target,binding);
        }
        // No health/armor/absorption is consumed by the marking contact.
        event.setAmount(0);
        send(level,target,strike,0);
    }
    /** A short-lived server-side seal: no persistent NoAI/NoGravity flags can strand a saved mob. */
    @SubscribeEvent(priority=EventPriority.HIGHEST)
    public static void holdBoundTarget(LivingEvent.LivingTickEvent event) {
        LivingEntity target=event.getEntity();
        Binding binding=activeBinding(target);
        if(binding==null)return;
        hold(target,binding);
        // LivingTick cancellation also skips baseTick. Preserve vanilla damage cooldowns so a
        // movement seal does not accidentally make the target immune to ordinary follow-up hits.
        long tick=target.level().getGameTime();
        if(binding.lastCooldownTick!=tick) {
            if(target.hurtTime>0)--target.hurtTime;
            if(target.invulnerableTime>0)--target.invulnerableTime;
            binding.lastCooldownTick=tick;
        }
        // Pause locomotion and AI while the cage is assembling, without altering persisted AI state.
        event.setCanceled(true);
    }
    @SubscribeEvent(priority=EventPriority.HIGHEST)
    public static void stopBoundKnockback(LivingKnockBackEvent event) {
        if(activeBinding(event.getEntity())!=null)event.setCanceled(true);
    }
    private static Binding activeBinding(LivingEntity target) {
        if(target instanceof Player||!target.isAlive()||!(target.level() instanceof ServerLevel level))return null;
        Binding binding=BINDINGS.get(new BoundTarget(level.dimension(),target.getUUID()));
        // The landing resolves at ServerTick.END: keep the victim fixed during that tick's movement.
        return binding!=null&&level.getGameTime()<=binding.until?binding:null;
    }
    private static void hold(LivingEntity target,Binding binding) {
        if(target instanceof Mob mob)mob.getNavigation().stop();
        if(target.position().distanceToSqr(binding.feet)>1e-10)target.setPos(binding.feet);
        target.setDeltaMovement(Vec3.ZERO);
        target.fallDistance=0;
        target.hasImpulse=true;
    }
    @SubscribeEvent
    public static void tick(TickEvent.ServerTickEvent event) {
        if(event.phase!=TickEvent.Phase.END)return;
        // Remove before applying damage: a landing can itself dispatch further combat events.
        var ready=new ArrayList<Strike>();
        PENDING.removeIf(strike->{
            var level=event.getServer().getLevel(strike.dimension);
            if(level==null)return true;
            var entity=level.getEntity(strike.target);
            if(!(entity instanceof LivingEntity target)||!target.isAlive()) {
                send(level,strike,strike.initialCenter,2);return true;
            }
            if(!(level.getEntity(strike.attacker) instanceof LivingEntity attacker)||!attacker.isAlive()) {
                send(level,target,strike,2);return true;
            }
            if(level.getGameTime()>=strike.due){ready.add(strike);return true;}
            return false;
        });
        Set<BoundTarget> active=new HashSet<>();
        for(Strike strike:PENDING)active.add(new BoundTarget(strike.dimension,strike.target));
        BINDINGS.keySet().retainAll(active);
        for(Strike strike:ready) {
            var level=event.getServer().getLevel(strike.dimension);
            if(level==null)continue;
            if(!(level.getEntity(strike.target) instanceof LivingEntity target) || !target.isAlive()) {
                send(level,strike,strike.initialCenter,2);continue;
            }
            if(!(level.getEntity(strike.attacker) instanceof LivingEntity attacker) || !attacker.isAlive()) {
                send(level,target,strike,2);continue;
            }
            DamageSource source=new DamageSource(level.registryAccess().registryOrThrow(Registries.DAMAGE_TYPE)
                    .getHolderOrThrow(DAMAGE),attacker,attacker);
            resolving=true;
            try {
                // Normal armor, resistance, absorption, PvP and protection hooks still apply.
                // Capture where damage is applied, before death/retaliation hooks can move or
                // resize the target. The visual landing must not jump to its post-hit position.
                Vec3 impactCenter=target.getBoundingBox().getCenter();
                boolean landed=target.hurt(source,strike.damage);
                send(level,strike,impactCenter,landed?1:2);
            } finally {resolving=false;}
        }
    }
    private static void send(ServerLevel level,LivingEntity target,Strike strike,int phase) {
        send(level,strike,target.getBoundingBox().getCenter(),phase);
    }
    private static void send(ServerLevel level,Strike strike,Vec3 p,int phase) {
        DynastyNetwork.CHANNEL.send(PacketDistributor.NEAR.with(()->new PacketDistributor.TargetPoint(
                p.x,p.y,p.z,64,level.dimension())),new DragonDescentPacket(strike.id,phase,strike.targetEntityId,
                strike.target,strike.due-DELAY,p.x,p.y,p.z,strike.yaw));
    }
    @SubscribeEvent
    public static void stop(ServerStoppedEvent event){PENDING.clear();BINDINGS.clear();resolving=false;nextId=0;}
    private QinglongDescent(){}
}
