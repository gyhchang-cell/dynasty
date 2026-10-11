package com.dynasty.cod3;

import com.dynasty.Dynasty;
import com.dynasty.network.DynastyNetwork;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.server.ServerStoppedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;
import java.util.*;
import java.util.function.Consumer;
import java.util.function.Predicate;

/** Bounded server casts. Visual-only sends never create damage; a cast has one explicit owner. */
@Mod.EventBusSubscriber(modid=Dynasty.MODID)
public final class Cod3CombatVfx {
    private record Cast(LivingEntity owner,VfxInstance visual,float damage,Predicate<LivingEntity> filter,Consumer<LivingEntity> onHit,Set<UUID> hit) {}
    private static final Map<ServerLevel,List<Cast>> ACTIVE=new IdentityHashMap<>();
    public static boolean cast(LivingEntity owner,int template,Vec3 origin,Vec3 direction,double scale,int windup,int active,float damage,Predicate<LivingEntity> filter,Consumer<LivingEntity> onHit){
        return cast(owner,template,origin,direction,scale,windup,active,damage,filter,onHit,false);
    }
    /** Existing boss areas cover the whole disk; the default gold template is a hollow ring. */
    public static boolean castDisk(LivingEntity owner,Vec3 origin,Vec3 direction,double scale,int windup,int active,float damage,Predicate<LivingEntity> filter,Consumer<LivingEntity> onHit){
        return cast(owner,12,origin,direction,scale,windup,active,damage,filter,onHit,true);
    }
    private static boolean cast(LivingEntity owner,int template,Vec3 origin,Vec3 direction,double scale,int windup,int active,float damage,Predicate<LivingEntity> filter,Consumer<LivingEntity> onHit,boolean disk){
        if(owner==null||template<1||template>40||filter==null||onHit==null||origin==null||direction==null||!Double.isFinite(origin.lengthSqr())||!Double.isFinite(direction.lengthSqr())||!(owner.level() instanceof ServerLevel level)||!owner.isAlive()||owner.isRemoved()||!Float.isFinite(damage)||damage<=0||!Double.isFinite(scale)||scale<=0||scale>4||windup<0||windup>2380||active<1||active>2380||windup+active>2380)return false;
        var definition=Cod3Catalog.vfx(template);if(disk)definition=definition.withShape(DynastyVfxDefinition.Shape.CIRCLE);if(!definition.damaging())return false;
        var casts=ACTIVE.computeIfAbsent(level,ignored->new ArrayList<>());
        if(casts.size()>=32||casts.stream().filter(c->c.visual.definition().id()==template).count()>=VfxTimeline.limit(template))return false;
        var visual=new VfxInstance(definition,origin,direction,level.random.nextLong(),level.getGameTime(),windup+active+12,scale,windup,active);
        casts.add(new Cast(owner,visual,damage,Objects.requireNonNull(filter),Objects.requireNonNull(onHit),new HashSet<>()));
        var packet=new Cod3VisualPacket(level.dimension().location().toString(),template,-1,visual.seed(),visual.start(),visual.lifetime(),scale,origin,direction,"combat_"+windup+"_"+active+(disk?"_disk":""),0);
        DynastyNetwork.CHANNEL.send(PacketDistributor.NEAR.with(()->new PacketDistributor.TargetPoint(origin.x,origin.y,origin.z,32,level.dimension())),packet);return true;
    }
    static List<LivingEntity> targets(ServerLevel level,VfxInstance visual,double age,Predicate<LivingEntity> filter){
        if(visual.phase(age)!=VfxInstance.Phase.SUSTAIN)return List.of();
        return level.getEntitiesOfClass(LivingEntity.class,visual.volume(age).bounds(),entity->entity.isAlive()&&!entity.isSpectator()&&filter.test(entity)&&visual.contains(entity.position(),age));
    }
    @SubscribeEvent public static void tick(TickEvent.LevelTickEvent event){
        if(event.phase!=TickEvent.Phase.END||!(event.level instanceof ServerLevel level))return;
        var casts=ACTIVE.get(level);if(casts==null)return;
        casts.removeIf(cast->!cast.owner.isAlive()||cast.owner.isRemoved()||cast.owner.level()!=level||cast.visual.phase(level.getGameTime()-cast.visual.start())==VfxInstance.Phase.END);
        for(var cast:List.copyOf(casts)){
            double age=level.getGameTime()-cast.visual.start();
            for(var target:targets(level,cast.visual,age,entity->entity!=cast.owner&&cast.filter.test(entity))){
                if(!cast.hit.add(target.getUUID()))continue;
                if(target.hurt(cast.owner.damageSources().mobAttack(cast.owner),cast.damage))cast.onHit.accept(target);
            }
        }
        if(casts.isEmpty())ACTIVE.remove(level);
    }
    @SubscribeEvent public static void stop(ServerStoppedEvent event){ACTIVE.clear();}
    private Cod3CombatVfx(){}
}
