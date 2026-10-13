package com.dynasty.blueprint.artifact;

import com.dynasty.blueprint.combat.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.DamageTypeTags;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.event.entity.player.*;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.fml.common.Mod;
import java.util.UUID;

@Mod.EventBusSubscriber(modid="dynasty")
public final class ArtifactCombat {
    private static final UUID PARRY_SLOW=UUID.fromString("af193b8d-c1d8-4c6e-9e31-bcfcd0d8c814");
    public static long now(ServerPlayer p){return p.serverLevel().getGameTime();}
    public static boolean counterReady(ServerPlayer p,ItemStack stack){long t=p.getPersistentData().getLong("DynastyLongyinCounterUntil");return p.getPersistentData().contains("DynastyLongyinCounterUntil")&&stack.is(ArtifactContent.LONGYIN.get())&&t>=now(p)&&t<=now(p)+40;}
    public static boolean swing(ServerPlayer p){var stack=p.getMainHandItem();return ArtifactAbility.valid(p,stack)&&((ArtifactItem)stack.getItem()).ability().swing(p,stack);}
    @SubscribeEvent public static void attack(AttackEntityEvent e){if(e.getEntity() instanceof ServerPlayer p&&p.getMainHandItem().getItem() instanceof ArtifactItem){e.setCanceled(true);swing(p);}}
    @SubscribeEvent public static void logout(PlayerEvent.PlayerLoggedOutEvent e){if(e.getEntity() instanceof ServerPlayer p)ArtifactAbility.forget(p);}
    @SubscribeEvent public static void dimension(PlayerEvent.PlayerChangedDimensionEvent e){if(e.getEntity() instanceof ServerPlayer p)ArtifactAbility.forget(p);}
    @SubscribeEvent public static void tick(TickEvent.PlayerTickEvent e){if(e.phase!=TickEvent.Phase.END||!(e.player instanceof ServerPlayer p))return;var session=ArtifactAbility.USES.get(p.getUUID());if(session!=null&&(!p.isAlive()||!p.isUsingItem()||p.getUseItem()!=session.stack()||p.level().dimension()!=session.dimension()))ArtifactAbility.forget(p);}
    public static boolean surrounded(ServerPlayer p){if(!p.getMainHandItem().is(ArtifactContent.LONGYIN.get())||!ArtifactAbility.loaded(p.serverLevel(),p.getBoundingBox().inflate(4)))return false;return p.serverLevel().getEntitiesOfClass(Mob.class,p.getBoundingBox().inflate(4),m->m instanceof Enemy&&m.isAlive()&&!Combatant.allied(p,m)&&p.hasLineOfSight(m)).stream().limit(3).count()>=3;}
    private static boolean frontPhysical(ServerPlayer p,net.minecraft.world.damagesource.DamageSource source){var at=source.getSourcePosition();return source.getEntity()!=null&&at!=null&&!source.is(DamageTypeTags.BYPASSES_ARMOR)&&!source.is(DamageTypeTags.IS_FIRE)&&!source.is(DamageTypeTags.IS_EXPLOSION)&&CombatGeometry.inFront(p.position(),p.getLookAngle(),at,180);}
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void hurt(LivingHurtEvent e){if(e.getEntity() instanceof ServerPlayer p&&surrounded(p)&&frontPhysical(p,e.getSource()))e.setAmount(e.getAmount()*.75F);}
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void knock(LivingKnockBackEvent e){if(e.getEntity() instanceof ServerPlayer p&&surrounded(p))e.setStrength(e.getStrength()*.5F);}
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void stagger(MobEffectEvent.Applicable e){if(e.getEntity() instanceof ServerPlayer p&&e.getEffectInstance().getEffect()==com.dynasty.expansion.ExpansionEffects.STAGGER.get()&&surrounded(p))e.setResult(Event.Result.DENY);}
    @SubscribeEvent(priority=EventPriority.LOWEST) public static void parry(LivingAttackEvent e){
        if(e.getEntity().level().isClientSide)return;
        var source=e.getSource();var attacker=source.getEntity();
        if(attacker instanceof Mob mob&&mob.getPersistentData().getLong("DynastyArtifactParriedUntil")>mob.level().getGameTime()){e.setCanceled(true);return;}
        if(!(e.getEntity() instanceof ServerPlayer p)||!(source.getDirectEntity() instanceof Mob mob)||!frontPhysical(p,source)||Combatant.allied(p,mob))return;
        if(p.getMainHandItem().is(ArtifactContent.ZHANLU.get())){var session=ArtifactAbility.USES.get(p.getUUID());long age=session==null?-1:now(p)-session.born();if(session!=null&&session.stack()==p.getMainHandItem()&&p.isUsingItem()&&p.getUseItem()==session.stack()&&session.dimension()==p.level().dimension()&&age>=0&&age<ZhanluAbility.guardTicks(p)&&!p.getPersistentData().getBoolean("DynastyZhanluGuardSpent")){p.getPersistentData().putBoolean("DynastyZhanluGuardSpent",true);e.setCanceled(true);stun(mob,20);}return;}
        if(!p.getMainHandItem().is(ArtifactContent.LONGYIN.get()))return;
        var n=p.getPersistentData();long swing=n.contains("DynastyLongyinSwingAt")?n.getLong("DynastyLongyinSwingAt"):-1;long age=now(p)-swing;
        // Three native ticks plus one tick of receive-time tolerance; no client clock rewind.
        if(swing<0||age<0||age>4||n.contains("DynastyLongyinParrySpent")&&n.getLong("DynastyLongyinParrySpent")==swing)return;
        n.putLong("DynastyLongyinParrySpent",swing);n.putLong("DynastyLongyinCounterUntil",now(p)+40);p.getCooldowns().removeCooldown(ArtifactContent.LONGYIN.get());
        e.setCanceled(true);stun(mob,40);
    }
    public static void stun(Mob mob,int ticks){ticks=Math.max(1,Math.min(40,ticks));long now=mob.level().getGameTime(),previous=mob.getPersistentData().getLong("DynastyArtifactParriedUntil");if(previous>now&&previous<=now+40)ticks=Math.max(ticks,(int)(previous-now));mob.getPersistentData().putLong("DynastyArtifactParriedUntil",now+ticks);
        if(mob instanceof com.dynasty.blueprint.boss.BlindMarshal m)m.parried(ticks);
        else if(mob instanceof com.dynasty.blueprint.boss.TaoyanCauldron m)m.parried(ticks);
        else if(mob instanceof com.dynasty.blueprint.boss.WoodKite m)m.parried(ticks);
        var speed=mob.getAttribute(Attributes.MOVEMENT_SPEED);if(speed!=null){speed.removeModifier(PARRY_SLOW);speed.addTransientModifier(new AttributeModifier(PARRY_SLOW,"dynasty artifact parry",-1,AttributeModifier.Operation.MULTIPLY_TOTAL));}
        mob.getNavigation().stop();mob.setDeltaMovement(0,mob.getDeltaMovement().y,0);
    }
    @SubscribeEvent public static void restore(LivingEvent.LivingTickEvent e){if(!(e.getEntity() instanceof Mob mob)||mob.level().isClientSide)return;var n=mob.getPersistentData();if(!n.contains("DynastyArtifactParriedUntil"))return;long until=n.getLong("DynastyArtifactParriedUntil"),now=mob.level().getGameTime();var speed=mob.getAttribute(Attributes.MOVEMENT_SPEED);if(until<=now||until>now+40){n.remove("DynastyArtifactParriedUntil");if(speed!=null)speed.removeModifier(PARRY_SLOW);}else{if(speed!=null&&speed.getModifier(PARRY_SLOW)==null)speed.addTransientModifier(new AttributeModifier(PARRY_SLOW,"dynasty artifact parry",-1,AttributeModifier.Operation.MULTIPLY_TOTAL));mob.getNavigation().stop();mob.setDeltaMovement(0,mob.getDeltaMovement().y,0);}}
    private ArtifactCombat(){}
}
