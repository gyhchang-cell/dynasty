package com.dynasty.blueprint.boss;

import net.minecraft.server.level.*;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import java.util.*;

/** Server-observed sprint/jump/attack cues. Never reads or modifies the user's controls or audio. */
@Mod.EventBusSubscriber(modid="dynasty")
public final class BlindMarshalNoise {
    private static final Map<ServerLevel,Map<UUID,Long>> NOISE=new WeakHashMap<>();
    private static void record(ServerPlayer p){
        if(p.isSpectator()||p.isCreative()||!p.isAlive())return;
        var world=p.serverLevel();long now=world.getGameTime();
        var rows=NOISE.computeIfAbsent(world,k->new LinkedHashMap<>());
        rows.entrySet().removeIf(e->e.getValue()>now||now-e.getValue()>10);
        if(rows.size()>=32&&!rows.containsKey(p.getUUID()))rows.remove(rows.keySet().iterator().next());
        rows.put(p.getUUID(),now);
    }
    public static void action(ServerPlayer p){record(p);}
    public static long heard(ServerPlayer p){return NOISE.getOrDefault(p.serverLevel(),Map.of()).getOrDefault(p.getUUID(),-1L);}
    @SubscribeEvent public static void sprint(TickEvent.PlayerTickEvent e){
        if(e.phase==TickEvent.Phase.END&&e.player instanceof ServerPlayer p&&p.isSprinting()
                &&p.getDeltaMovement().horizontalDistanceSqr()>.008&&p.tickCount%2==0)record(p);
    }
    @SubscribeEvent public static void jump(LivingEvent.LivingJumpEvent e){if(e.getEntity() instanceof ServerPlayer p)record(p);}
    @SubscribeEvent public static void attack(AttackEntityEvent e){if(e.getEntity() instanceof ServerPlayer p)record(p);}
    private BlindMarshalNoise(){}
}
