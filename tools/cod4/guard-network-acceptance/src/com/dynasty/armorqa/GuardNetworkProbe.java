package com.dynasty.armorqa;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import java.util.*;

/** Observes actual AI and native hurt events while real TCP clients equip and remove gear. */
public final class GuardNetworkProbe {
    static int current=-1, ticks, illegalTargets;
    static LivingEntity enemy;
    static final List<Map<String,Object>> playerAttempts=new ArrayList<>(), enemyHits=new ArrayList<>();

    static boolean leased(net.minecraft.world.entity.Entity entity) {
        return entity instanceof Mob && entity.getPersistentData().hasUUID("cod4Summoner");
    }

    static void observe(ServerPlayer owner,int n,int age) throws Exception {
        if(current!=n) {
            if(enemy!=null)enemy.discard();
            enemy=null;current=n;ticks=0;illegalTargets=0;playerAttempts.clear();enemyHits.clear();
        }
        ticks++;
        var guards=owner.serverLevel().getEntitiesOfClass(Mob.class,owner.getBoundingBox().inflate(32),g->leased(g)&&g.getPersistentData().getUUID("cod4Summoner").equals(owner.getUUID()));
        for(var g:guards)if(g.getTarget() instanceof Player)illegalTargets++;
        // Positive control: ordinary real AI must still acquire and hurt a hostile enemy.
        // No setTarget or manual damage call is used here.
        if(n==8&&age==120&&!guards.isEmpty()) {
            var guard=guards.get(0);
            enemy=ArmorNetworkQa.mob("zombie",guard.getX()+.7,guard.getZ());
            enemy.teleportTo(guard.getX()+.7,guard.getY(),guard.getZ());
        }
        if(enemy!=null&&age==200){enemy.discard();enemy=null;}
    }

    @SubscribeEvent(priority=EventPriority.HIGHEST,receiveCanceled=true)
    public static void attack(LivingAttackEvent event) {
        if(event.getEntity().level().isClientSide||ArmorNetworkQa.active!=current||!leased(event.getSource().getEntity()))return;
        if(event.getEntity() instanceof Player)playerAttempts.add(ArmorNetworkQa.obj("victim",event.getEntity().getUUID().toString(),"source",event.getSource().getEntity().getUUID().toString(),"tick",event.getEntity().level().getGameTime(),"amount",event.getAmount(),"canceled",event.isCanceled()));
    }

    @SubscribeEvent(priority=EventPriority.LOWEST,receiveCanceled=true)
    public static void hurt(LivingHurtEvent event) {
        if(event.getEntity().level().isClientSide||ArmorNetworkQa.active!=current||!leased(event.getSource().getEntity()))return;
        if(event.getEntity()==enemy)enemyHits.add(ArmorNetworkQa.obj("victim",enemy.getUUID().toString(),"tick",enemy.level().getGameTime(),"amount",event.getAmount(),"canceled",event.isCanceled(),"source",event.getSource().getEntity().getUUID().toString()));
    }

    static void validate(int n)throws Exception {
        if(n!=7&&n!=8)return;
        ArmorNetworkQa.check("leased guard never targets a real player",illegalTargets==0,illegalTargets);
        ArmorNetworkQa.check("zero guard attack attempts against owner or bystander TCP players",playerAttempts.isEmpty(),playerAttempts);
        ArmorNetworkQa.check("native quiet observation interval",ticks>=(n==8?600:90),ticks);
        if(n==8)ArmorNetworkQa.check("native AI still damages real hostile enemy",enemyHits.stream().anyMatch(x->!Boolean.TRUE.equals(x.get("canceled"))&&((Number)x.get("amount")).floatValue()>0),enemyHits);
        ArmorNetworkQa.write("guard-safety-"+n+".json",ArmorNetworkQa.obj("case",n,"observedTicks",ticks,"illegalPlayerTargets",illegalTargets,"playerAttackAttempts",List.copyOf(playerAttempts),"positiveEnemyHits",List.copyOf(enemyHits),"forcedTargetOrDamage",false));
    }
}
