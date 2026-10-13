package com.dynasty.blueprint.artifact;

import com.dynasty.blueprint.combat.CombatGeometry;
import net.minecraft.core.*;
import net.minecraft.core.particles.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.*;
import org.joml.Vector3f;

/** The first catalog artifact. No arbitrary crafting or client-supplied geometry. */
public final class LongyinAbility implements ArtifactAbility {
    @Override public double gripOffsetMetres(){return 1.1875;}
    public static final AttackProfile MELEE=new AttackProfile(CombatGeometry.Shape.SECTOR,3.2,0,180,1.2);
    public static final AttackProfile WAVE=new AttackProfile(CombatGeometry.Shape.CIRCLE,.8,0,360,.75);
    private static boolean ready(ServerPlayer p){long until=p.getPersistentData().getLong("DynastyLongyinUntil");return until<=ArtifactCombat.now(p)||until>ArtifactCombat.now(p)+240;}
    @Override public boolean swing(ServerPlayer p,ItemStack stack){
        long now=ArtifactCombat.now(p);var n=p.getPersistentData();
        if(!ArtifactAbility.valid(p,stack)||!ready(p)||p.isUsingItem()||p.getAttackStrengthScale(0)<.9F||n.getLong("DynastyLongyinRecoveryUntil")>now)return false;
        double attack=p.getAttributeValue(Attributes.ATTACK_DAMAGE);if(!Double.isFinite(attack)||attack<=0)return false;attack=Math.min(512,attack);
        com.dynasty.blueprint.boss.BlindMarshalNoise.action(p);n.putLong("DynastyLongyinSwingAt",now);n.putLong("DynastyLongyinRecoveryUntil",now+4);p.resetAttackStrengthTicker();p.swing(InteractionHand.MAIN_HAND,true);
        var origin=p.position().add(0,1,0);var f=p.getLookAngle().multiply(1,0,1).normalize();boolean hit=false;
        for(var target:MELEE.targets(p,origin,f))if(p.hasLineOfSight(target)&&target.hurt(p.damageSources().playerAttack(p),(float)attack)){target.knockback(.65,p.getX()-target.getX(),p.getZ()-target.getZ());com.dynasty.expansion.ExpansionEffects.apply(target,com.dynasty.expansion.ExpansionEffects.STAGGER,8);hit=true;}
        if(hit)stack.hurtAndBreak(1,p,e->e.broadcastBreakEvent(InteractionHand.MAIN_HAND));
        p.getCooldowns().addCooldown(stack.getItem(),4);
        for(int i=0;i<9;i++){double angle=Math.toRadians(-90+180D*i/8);var side=new Vec3(-f.z,0,f.x);var at=origin.add(f.scale(Math.cos(angle)*MELEE.range())).add(side.scale(Math.sin(angle)*MELEE.range()));p.serverLevel().sendParticles(new DustParticleOptions(new Vector3f(.3F,.5F,.58F),1),at.x,at.y,at.z,1,0,0,0,0);}
        return true;
    }
    @Override public boolean release(ServerPlayer p,ItemStack stack,int elapsed){
        boolean counter=ArtifactCombat.counterReady(p,stack);
        if(!ArtifactAbility.valid(p,stack)||!ready(p)||!counter&&elapsed<40)return false;
        var world=p.serverLevel();double attack=p.getAttributeValue(Attributes.ATTACK_DAMAGE);if(!Double.isFinite(attack)||attack<=0)return false;var f=p.getLookAngle().multiply(1,0,1).normalize();if(f.lengthSqr()<.001||!p.onGround())return false;
        var floor=ArtifactWave.floor(world,p.position().add(f));if(floor==null||Math.abs(floor.getY()-p.getY())>1)return false;
        var type=ArtifactContent.WAVE.get();var wave=type.create(world);if(wave==null)return false;
        wave.begin(p,f,floor);if(!world.addFreshEntity(wave))return false;
        var n=p.getPersistentData();n.remove("DynastyLongyinCounterUntil");n.putLong("DynastyLongyinUntil",ArtifactCombat.now(p)+200);n.putLong("DynastyLongyinRecoveryUntil",ArtifactCombat.now(p)+4);
        p.getCooldowns().addCooldown(stack.getItem(),200);stack.hurtAndBreak(2,p,e->e.broadcastBreakEvent(InteractionHand.MAIN_HAND));
        p.move(MoverType.SELF,f.scale(.35));p.hurtMarked=true;p.swing(InteractionHand.MAIN_HAND,true);return true;
    }
}
