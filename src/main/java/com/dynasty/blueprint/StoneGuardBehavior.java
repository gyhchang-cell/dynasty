package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.CombatGeometry;
import com.dynasty.blueprint.combat.SkillDefinition;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;

/** A single contact after a 1.5-second tell, using the same strip width as the client warning. */
public final class StoneGuardBehavior implements ArmyBehaviors.Behavior {
    public static final double SLAM_WIDTH=1.25;
    private final TemplateMob mob;
    StoneGuardBehavior(TemplateMob mob){this.mob=mob;}
    public boolean allows(int id){return id==ArmySkills.STONE_UPPERCUT||id==ArmySkills.STONE_SLAM;}
    public String animation(int id){return id==ArmySkills.STONE_SLAM?"slam":"attack";}
    public int choose(LivingEntity target,long now){return mob.attack().ready(ArmySkills.STONE_SLAM,now)?ArmySkills.STONE_SLAM:ArmySkills.STONE_UPPERCUT;}
    public void move(LivingEntity target,long now){mob.getNavigation().moveTo(target,.9);}
    public void impact(SkillDefinition skill,int frame){
        boolean slam=skill.id()==ArmySkills.STONE_SLAM;
        var shape=slam?CombatGeometry.Shape.STRIP:CombatGeometry.Shape.SECTOR;
        var direction=mob.attack().direction();
        for(var target:CombatGeometry.query((ServerLevel)mob.level(),mob.attack().origin(),direction,shape,skill.maxRange(),SLAM_WIDTH,skill.angleDegrees(),1.6,
                e->mob.validEnemy(e)&&mob.hasLineOfSight(e))){
            if(slam&&target.isBlocking()){
                if(target instanceof ServerPlayer player)player.disableShield(true);
                else target.stopUsingItem();
            }
            if(target.hurt(mob.damageSources().mobAttack(mob),(float)mob.getAttributeValue(Attributes.ATTACK_DAMAGE)*skill.damageMultiplier())){
                target.knockback(skill.knockback(),-direction.x,-direction.z);
                if(!slam){var v=target.getDeltaMovement();target.setDeltaMovement(v.x,Math.max(v.y,.38),v.z);target.hurtMarked=true;}
            }
            if(!mob.isAlive()||mob.attack().current()!=skill)break;
        }
        mob.playSound(net.minecraft.sounds.SoundEvents.IRON_GOLEM_ATTACK,1,slam?.6F:.85F);
    }
}
