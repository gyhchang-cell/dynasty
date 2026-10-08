package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;

/** Alert selects only loaded members of the same real encounter site. No global faction broadcast. */
final class ClockworkDogBehavior implements ArmyBehaviors.Behavior {
    private final TemplateMob mob;
    private long nextPatrol;
    private int patrol;
    ClockworkDogBehavior(TemplateMob mob){this.mob=mob;}
    public boolean allows(int id){return id==ArmySkills.DOG_BITE||id==ArmySkills.DOG_ALARM;}
    public String animation(int id){return id==ArmySkills.DOG_ALARM?"alarm":"attack";}
    public int choose(LivingEntity target,long now){return mob.attack().ready(ArmySkills.DOG_ALARM,now)?ArmySkills.DOG_ALARM:ArmySkills.DOG_BITE;}
    public void move(LivingEntity target,long now){mob.getNavigation().moveTo(target,1.1);}
    public void tick(long now){
        if(mob.isNoAi()||mob.validEnemy(mob.getTarget())||mob.skillId()!=0||now<nextPatrol||!mob.hasRestriction())return;
        nextPatrol=now+60;
        int[][] offsets={{-4,0},{0,-4},{4,0},{0,4}};var step=offsets[Math.floorMod(patrol++,4)];
        BlockPos point=mob.getRestrictCenter().offset(step[0],0,step[1]);
        if(!mob.level().hasChunkAt(point))return;
        var path=mob.getNavigation().createPath(point,0);
        if(path!=null&&path.canReach())mob.getNavigation().moveTo(path,.8);
    }
    public void impact(SkillDefinition skill,int frame){
        var target=mob.resolve(mob.attack().target());
        if(!mob.validEnemy(target)||!mob.hasLineOfSight(target)||mob.distanceToSqr(target)>skill.maxRange()*skill.maxRange())return;
        if(skill.id()==ArmySkills.DOG_BITE){
            if(CombatGeometry.contains(mob.position(),mob.attack().direction(),CombatGeometry.Shape.SECTOR,skill.maxRange(),.8,skill.angleDegrees(),1.3,target.getBoundingBox()))
                target.hurt(mob.damageSources().mobAttack(mob),(float)mob.getAttributeValue(Attributes.ATTACK_DAMAGE));
            mob.playSound(net.minecraft.sounds.SoundEvents.IRON_TRAPDOOR_CLOSE,.7F,1.4F);return;
        }
        mob.playSound(net.minecraft.sounds.SoundEvents.NOTE_BLOCK_BIT.value(),1.4F,1.8F);
        mob.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED,100,0),mob);
        if(mob.encounterSite().isBlank())return;
        ((ServerLevel)mob.level()).getEntitiesOfClass(TemplateMob.class,mob.getBoundingBox().inflate(20),
            other->other!=mob&&other.isAlive()&&!other.isNoAi()&&mob.distanceToSqr(other)<=400
                &&other.encounterSite().equals(mob.encounterSite())
                &&(other.faction()==Faction.CONSTRUCT||other.faction()==Faction.DYNASTY_ARMY)&&other.validEnemy(target))
            .stream().sorted(java.util.Comparator.comparingDouble(mob::distanceToSqr)).limit(16)
            .forEach(other->{if(!other.validEnemy(other.getTarget()))other.setTarget(target);});
    }
    public CompoundTag save(){var tag=new CompoundTag();tag.putInt("Patrol",Math.floorMod(patrol,4));tag.putLong("NextPatrol",nextPatrol);return tag;}
    public void load(CompoundTag tag){patrol=Math.floorMod(tag.getInt("Patrol"),4);nextPatrol=Math.min(tag.getLong("NextPatrol"),mob.level().getGameTime()+60);}
}
