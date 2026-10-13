package com.dynasty.blueprint.artifact;

import com.dynasty.blueprint.combat.CombatGeometry;
import com.dynasty.blueprint.combat.Combatant;
import net.minecraft.core.particles.DustParticleOptions;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.damagesource.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.*;
import org.joml.Vector3f;
import java.util.*;

/** Four different precise sword cuts; all geometry, clocks and damage come from the server. */
public final class ZhanluAbility implements ArtifactAbility {
    public static final List<AttackProfile> CHAIN=List.of(
        new AttackProfile(CombatGeometry.Shape.STRIP,2.4,.45,0,.65),
        new AttackProfile(CombatGeometry.Shape.SECTOR,2.1,0,100,.85),
        new AttackProfile(CombatGeometry.Shape.STRIP,2.2,.75,0,1.5),
        new AttackProfile(CombatGeometry.Shape.STRIP,2.3,.65,0,1.15)
    );
    public static final ResourceKey<DamageType> VOID=ResourceKey.create(Registries.DAMAGE_TYPE,new ResourceLocation("dynasty","zhanlu_void_submission"));
    private record Combo(ItemStack stack,int next,long last,ResourceKey<net.minecraft.world.level.Level> dimension){}
    private static final Map<ServerPlayer,Combo> COMBOS=new WeakHashMap<>();
    @Override public UseAnim useAnimation(){return UseAnim.BLOCK;}
    @Override public void startUse(ServerPlayer p,ItemStack stack){stack.getOrCreateTag().putLong("DynastyZhanluStanceAt",ArtifactCombat.now(p));}
    @Override public void stopUse(ServerPlayer p,ItemStack stack){if(stack.getTag()!=null)stack.getTag().remove("DynastyZhanluStanceAt");cancelField(p);}
    public static int guardTicks(ServerPlayer p){double health=p.getHealth()/Math.max(1,p.getMaxHealth());return 3+(int)Math.round(9*Math.max(0,Math.min(1,1-health)));}
    public static boolean susceptible(LivingEntity target){
        if(target.hasEffect(com.dynasty.expansion.ExpansionEffects.STAGGER.get())||target.getPersistentData().getLong("DynastyArtifactParriedUntil")>target.level().getGameTime())return true;
        if(target instanceof Mob m&&ZhanluField.disarmed(m))return true;
        // A cauldron, glaive-bearing reliquary or animal's built-in attack is not an empty native hand.
        return !(target instanceof Combatant)&&!weapon(target.getMainHandItem())&&!weapon(target.getOffhandItem());
    }
    private static boolean weapon(ItemStack stack){return !stack.isEmpty()&&(stack.getItem() instanceof SwordItem||stack.getItem() instanceof BowItem||stack.getItem() instanceof CrossbowItem||stack.getItem() instanceof TridentItem||stack.getAttributeModifiers(EquipmentSlot.MAINHAND).containsKey(Attributes.ATTACK_DAMAGE));}
    @Override public boolean swing(ServerPlayer p,ItemStack stack){
        long now=ArtifactCombat.now(p);if(!ArtifactAbility.valid(p,stack)||p.isUsingItem()||p.getAttackStrengthScale(0)<.9F)return false;
        var previous=COMBOS.get(p);int cut=previous!=null&&previous.stack()==stack&&previous.dimension()==p.level().dimension()&&now>=previous.last()+4&&now<=previous.last()+40?previous.next():0;
        if(previous!=null&&now>=previous.last()&&now<previous.last()+4)return false;
        double attack=p.getAttributeValue(Attributes.ATTACK_DAMAGE);if(!Double.isFinite(attack)||attack<=0)return false;attack=Math.min(512,attack);
        var origin=p.position().add(0,1,0);var facing=p.getLookAngle().multiply(1,0,1).normalize();if(facing.lengthSqr()<.001)return false;
        COMBOS.put(p,new Combo(stack,(cut+1)%4,now,p.level().dimension()));stack.getOrCreateTag().putInt("DynastyZhanluCut",cut);stack.getOrCreateTag().putLong("DynastyZhanluCutAt",now);
        com.dynasty.blueprint.boss.BlindMarshalNoise.action(p);p.resetAttackStrengthTicker();p.swing(InteractionHand.MAIN_HAND,true);boolean hit=false;
        for(var target:CHAIN.get(cut).targets(p,origin,facing))if(p.hasLineOfSight(target)){
            boolean submit=susceptible(target);var source=submit?new DamageSource(p.serverLevel().registryAccess().registryOrThrow(Registries.DAMAGE_TYPE).getHolderOrThrow(VOID),p):p.damageSources().playerAttack(p);
            if(target.hurt(source,(float)Math.min(1536,attack*(submit?3:1)))){hit=true;if(submit){if(target instanceof Mob mob)ArtifactCombat.stun(mob,20);else com.dynasty.expansion.ExpansionEffects.apply(target,com.dynasty.expansion.ExpansionEffects.STAGGER,20);}}
        }
        if(hit&&p.getHealth()<=p.getMaxHealth()*.8F)stack.hurtAndBreak(1,p,e->e.broadcastBreakEvent(InteractionHand.MAIN_HAND));
        p.getCooldowns().addCooldown(stack.getItem(),4);var side=new Vec3(-facing.z,0,facing.x);
        for(int i=0;i<7;i++){double u=i/6D;var at=switch(cut){case 0->origin.add(facing.scale(.4+2*u));case 1->origin.add(facing.scale(Math.cos(Math.toRadians(-50+100*u))*2.1)).add(side.scale(Math.sin(Math.toRadians(-50+100*u))*2.1));case 2->origin.add(facing.scale(1+u)).add(0,-.7+1.6*u,0);default->origin.add(facing.scale(1+u)).add(0,.8-1.5*u,0);};p.serverLevel().sendParticles(new DustParticleOptions(new Vector3f(.87F,.93F,.88F),.65F),at.x,at.y,at.z,1,0,0,0,0);}
        return true;
    }
    @Override public void tickUse(ServerPlayer p,ItemStack stack,int elapsed){
        if(elapsed<20||elapsed>100||!ArtifactAbility.valid(p,stack)||!p.onGround())return;
        var n=p.getPersistentData();var session=USES.get(p.getUUID());if(session==null||n.contains("DynastyZhanluCastAt")&&n.getLong("DynastyZhanluCastAt")==session.born())return;
        var ground=ArtifactWave.floor(p.serverLevel(),p.position());if(ground==null||Math.abs(ground.getY()-p.getY())>.25)return;
        var area=new AABB(p.position().add(-5,-.5,-5),p.position().add(5,3,5));if(!ArtifactAbility.loaded(p.serverLevel(),area))return;
        var field=ArtifactContent.ZHANLU_FIELD.get().create(p.serverLevel());if(field==null)return;field.begin(p,ground);if(!p.serverLevel().addFreshEntity(field))return;
        n.putLong("DynastyZhanluCastAt",session.born());n.putUUID("DynastyZhanluField",field.getUUID());p.getCooldowns().addCooldown(stack.getItem(),200);
    }
    @Override public boolean release(ServerPlayer p,ItemStack stack,int elapsed){cancelField(p);return false;}
    public static void cancelField(ServerPlayer p){var n=p.getPersistentData();if(n.hasUUID("DynastyZhanluField")){var e=p.serverLevel().getEntity(n.getUUID("DynastyZhanluField"));if(e instanceof ZhanluField field&&field.ownedBy(p))field.cancel();n.remove("DynastyZhanluField");}}
}
