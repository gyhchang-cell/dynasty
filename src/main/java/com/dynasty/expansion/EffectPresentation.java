package com.dynasty.expansion;

import com.dynasty.cod3.Cod3VisualPacket;
import com.dynasty.cod3.Cod3Vfx;
import com.dynasty.network.DynastyNetwork;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.MobType;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.PacketDistributor;
import java.util.List;

/** Uses COD3's bounded entity-bound renderer; effects and damage remain owned by the server. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class EffectPresentation {
    public static List<MobEffect> effects(){return List.of(ExpansionEffects.YIN.get(),ExpansionEffects.YANG.get(),ExpansionEffects.SHA.get(),ExpansionEffects.THUNDER.get(),ExpansionEffects.SOUL.get(),ExpansionEffects.FROST.get(),ExpansionEffects.BREAK.get(),ExpansionEffects.STAGGER.get());}
    public static Cod3VisualPacket packet(LivingEntity target,int code,boolean clear){
        var effect=target.getEffect(effects().get(code-1));
        int duration=clear?1:effect==null?1:effect.isInfiniteDuration()?20:Math.max(1,Math.min(20,effect.getDuration()));
        return new Cod3VisualPacket(target.level().dimension().location().toString(),14,target.getId(),target.getUUID().getLeastSignificantBits()+code,
                target.level().getGameTime(),duration,1,target.position(),target.getLookAngle(),"status_"+(clear?"clear_":"")+code,
                effect==null?0:Math.min(2,effect.getAmplifier()),effects().get(code-1).getColor());
    }
    private static void send(LivingEntity target,int code,boolean clear){
        if(!(target.level() instanceof ServerLevel level))return;
        DynastyNetwork.CHANNEL.send(PacketDistributor.NEAR.with(()->new PacketDistributor.TargetPoint(target.getX(),target.getY(),target.getZ(),32,level.dimension())),packet(target,code,clear));
    }
    @SubscribeEvent public static void tick(LivingEvent.LivingTickEvent e){
        var target=e.getEntity();if(target.level().isClientSide)return;
        var data=target.getPersistentData();if(target.tickCount%20!=0&&!data.getBoolean("cod4StatusDirty"))return;
        data.remove("cod4StatusDirty");
        var effects=effects();for(int i=0;i<effects.size();i++)if(target.hasEffect(effects.get(i)))send(target,i+1,false);
    }
    @SubscribeEvent public static void added(MobEffectEvent.Added e){
        if(!e.getEntity().level().isClientSide&&effects().contains(e.getEffectInstance().getEffect()))e.getEntity().getPersistentData().putBoolean("cod4StatusDirty",true);
    }
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void removed(MobEffectEvent.Remove e){
        if(e.isCanceled()||e.getEffectInstance()==null)return;clear(e.getEntity(),e.getEffect());
    }
    @SubscribeEvent public static void expired(MobEffectEvent.Expired e){if(e.getEffectInstance()!=null)clear(e.getEntity(),e.getEffectInstance().getEffect());}
    private static void clear(LivingEntity target,MobEffect effect){
        if(target.level().isClientSide)return;int index=effects().indexOf(effect);if(index<0)return;
        send(target,index+1,true);
        if(effect==ExpansionEffects.SHA.get())Cod3Vfx.send((ServerLevel)target.level(),14,target.position(),target.getLookAngle(),8,.08,0xE7C866);
    }
    @SubscribeEvent public static void tracking(PlayerEvent.StartTracking e){
        if(!(e.getEntity() instanceof net.minecraft.server.level.ServerPlayer player)||!(e.getTarget() instanceof LivingEntity target))return;
        var effects=effects();for(int i=0;i<effects.size();i++)if(target.hasEffect(effects.get(i)))
            DynastyNetwork.CHANNEL.send(PacketDistributor.PLAYER.with(()->player),packet(target,i+1,false));
    }
    @SubscribeEvent(priority=EventPriority.LOW) public static void yangDamage(LivingHurtEvent e){
        if(e.isCanceled()||e.getAmount()<=0||e.getEntity().level().isClientSide||e.getEntity().getMobType()!=MobType.UNDEAD
                ||!(e.getSource().getEntity() instanceof LivingEntity attacker)||com.dynasty.DynastyTrinketOnHit.isSyntheticDamage())return;
        var yang=attacker.getEffect(ExpansionEffects.YANG.get());if(yang==null)return;
        e.setAmount(e.getAmount()*(1+.08F*(Math.min(2,yang.getAmplifier())+1)));
    }
    private EffectPresentation(){}
}
