package com.dynasty.blueprint;
import com.dynasty.blueprint.combat.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.phys.AABB;
/** Heavy single-body construct; one shockwave contact and a non-ticking structure-only death remnant. */
public final class BixiBehavior implements ArmyBehaviors.Behavior {
    public static final double STOMP_RADIUS=5;
    private final TemplateMob mob;
    private boolean remnantAttempted;
    BixiBehavior(TemplateMob mob){this.mob=mob;}
    public boolean allows(int id){return id==ArmySkills.BIXI_BITE||id==ArmySkills.BIXI_STOMP;}
    public String animation(int id){return id==ArmySkills.BIXI_STOMP?"stomp":"attack";}
    public int choose(LivingEntity target,long now){return mob.distanceToSqr(target)<9&&mob.attack().ready(ArmySkills.BIXI_STOMP,now)?ArmySkills.BIXI_STOMP:ArmySkills.BIXI_BITE;}
    public void move(LivingEntity target,long now){mob.getNavigation().moveTo(target,.8);}
    public void impact(SkillDefinition skill,int frame){
        boolean stomp=skill.id()==ArmySkills.BIXI_STOMP;
        for(var target:CombatGeometry.query((ServerLevel)mob.level(),mob.attack().origin(),mob.attack().direction(),stomp?CombatGeometry.Shape.CIRCLE:CombatGeometry.Shape.SECTOR,
                stomp?STOMP_RADIUS:3.6,1,stomp?360:65,1.5,e->mob.validEnemy(e)&&mob.hasLineOfSight(e))){
            if(target.hurt(mob.damageSources().mobAttack(mob),stomp?12:8)){
                if(stomp)target.addEffect(new MobEffectInstance(BlueprintEntities.HEAVY_STAGGER.get(),16),mob);
                target.knockback(stomp?.3:.2,mob.getX()-target.getX(),mob.getZ()-target.getZ());
            }if(!mob.isAlive()||mob.attack().current()!=skill)break;
        }
        mob.playSound(net.minecraft.sounds.SoundEvents.IRON_GOLEM_ATTACK,1,.5F);
    }
    public void tickDead(long now){
        if(now%4==0)((ServerLevel)mob.level()).sendParticles(ParticleTypes.CLOUD,mob.getX(),mob.getY()+.6,mob.getZ(),4,.8,.2,.8,.03);
        if(remnantAttempted||mob.actionAge(0)<32)return;remnantAttempted=true;
        placeRemnant((ServerLevel)mob.level(),mob.blockPosition(),mob.encounterSite());
    }
    static boolean placeRemnant(ServerLevel level,BlockPos p,String site){
        if(!site.startsWith("dynasty:imperial_tomb@")||!level.getGameRules().getBoolean(GameRules.RULE_MOBGRIEFING)||!level.hasChunkAt(p)
                ||!level.getWorldBorder().isWithinBounds(p)||!level.getBlockState(p.below()).isFaceSturdy(level,p.below(),Direction.UP))return false;
        for(int y=0;y<2;y++)if(!level.isInWorldBounds(p.above(y))||!level.isEmptyBlock(p.above(y))||level.getBlockEntity(p.above(y))!=null)return false;
        if(!level.getEntitiesOfClass(LivingEntity.class,new AABB(p).expandTowards(0,1,0),LivingEntity::isAlive).isEmpty())return false;
        for(int y=0;y<2;y++)level.setBlock(p.above(y),com.dynasty.DynastyBlocks.BIXI_STELE.get().defaultBlockState(),3);
        return true;
    }
    public CompoundTag save(){var t=new CompoundTag();t.putBoolean("RemnantAttempted",remnantAttempted);return t;}
    public void load(CompoundTag t){remnantAttempted=t.getBoolean("RemnantAttempted");}
}
