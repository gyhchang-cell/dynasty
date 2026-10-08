package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.*;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.*;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;
import java.util.ArrayList;

/** Three finite, persisted whirl centres; pulls use velocity and ordinary collision, never teleport/input locks. */
final class BlindFishBehavior implements ArmyBehaviors.Behavior {
    private final TemplateMob mob;
    private final ArrayList<Vec3> whirls=new ArrayList<>(3);
    private long frightenedUntil,expires;
    BlindFishBehavior(TemplateMob mob){this.mob=mob;}
    public boolean allows(int id){return id==ArmySkills.FISH_TAIL||id==ArmySkills.FISH_RESONANCE;}
    public String animation(int id){return id==ArmySkills.FISH_RESONANCE?"resonance":"attack";}
    public int choose(LivingEntity target,long now){return (now<frightenedUntil||mob.distanceToSqr(target)<9)&&mob.attack().ready(ArmySkills.FISH_RESONANCE,now)?ArmySkills.FISH_RESONANCE:ArmySkills.FISH_TAIL;}
    public void hurtAccepted(DamageSource source,boolean frontal){frightenedUntil=mob.level().getGameTime()+100;}
    public void move(LivingEntity target,long now){
        double a=now*.018;Vec3 p=target.position().add(Math.cos(a)*2,1.5,Math.sin(a)*2);
        var box=mob.getType().getDimensions().makeBoundingBox(p.x,p.y,p.z);
        if(!mob.level().hasChunkAt(BlockPos.containing(box.minX,box.minY,box.minZ))||!mob.level().hasChunkAt(BlockPos.containing(box.maxX,box.maxY,box.maxZ))||!mob.level().noCollision(mob,box))return;
        var path=mob.getNavigation().createPath(p.x,p.y,p.z,0);if(path!=null&&path.canReach())mob.getNavigation().moveTo(path,.8);
    }
    public void impact(SkillDefinition skill,int frame){
        var level=(ServerLevel)mob.level();
        if(skill.id()==ArmySkills.FISH_TAIL){
            for(var target:CombatGeometry.query(level,mob.position(),mob.attack().direction(),CombatGeometry.Shape.SECTOR,3.5,1,150,1.8,e->mob.validEnemy(e)&&mob.hasLineOfSight(e)))
                {if(target.hurt(mob.damageSources().mobAttack(mob),6))target.knockback(.4,mob.getX()-target.getX(),mob.getZ()-target.getZ());if(!mob.isAlive())break;}
            return;
        }
        var target=mob.resolve(mob.attack().target());if(!mob.validEnemy(target)||mob.distanceToSqr(target)>100||!mob.hasLineOfSight(target))return;
        whirls.clear();expires=level.getGameTime()+60;
        // Fixed triangle around the victim's feet; dodgeable after the wave, maximum three total per caster.
        for(int i=0;i<3;i++){
            double a=i*Math.PI*2/3;var p=target.position().add(Math.cos(a)*1.3,.1,Math.sin(a)*1.3);
            var bp=BlockPos.containing(p);if(level.hasChunkAt(bp)&&level.getBlockState(bp).getCollisionShape(level,bp).isEmpty())whirls.add(p);
        }
        mob.playSound(net.minecraft.sounds.SoundEvents.AMETHYST_BLOCK_CHIME,.35F,.7F);
    }
    public void tick(long now){
        if(now>=expires){whirls.clear();return;}if(whirls.isEmpty()||now%5!=0)return;
        var level=(ServerLevel)mob.level();
        // One nearby query, then nearest centre: overlap does not multiply pull strength.
        for(var target:level.getEntitiesOfClass(LivingEntity.class,mob.getBoundingBox().inflate(14),e->mob.validEnemy(e)&&mob.hasLineOfSight(e))){
            Vec3 nearest=null;double best=4;
            for(var centre:whirls){double d=target.position().distanceToSqr(centre);if(d<best){best=d;nearest=centre;}}
            if(nearest==null)continue;
            Vec3 toward=nearest.subtract(target.position()).multiply(1,0,1);if(toward.lengthSqr()<.04)continue;
            Vec3 push=toward.normalize().scale(.055);target.push(push.x,0,push.z);target.hurtMarked=true;
        }
        for(var centre:whirls){
            if(!level.hasChunkAt(BlockPos.containing(centre)))continue;
            for(int i=0;i<6;i++){double a=i*Math.PI/3+now*.12;level.sendParticles(ParticleTypes.END_ROD,centre.x+Math.cos(a)*1.2,centre.y,centre.z+Math.sin(a)*1.2,1,0,0,0,0);}
        }
    }
    public void died(DamageSource source){whirls.clear();expires=0;}
    public void tickDead(long now){if(now%4==0)((ServerLevel)mob.level()).sendParticles(ParticleTypes.END_ROD,mob.getX(),mob.getY()+.5,mob.getZ(),3,.6,.3,.6,.015);}
    public CompoundTag save(){var t=new CompoundTag();t.putLong("Expires",expires);t.putLong("Frightened",frightenedUntil);var list=new ListTag();
        for(var p:whirls){var n=new CompoundTag();n.putDouble("X",p.x);n.putDouble("Y",p.y);n.putDouble("Z",p.z);list.add(n);}t.put("Whirls",list);return t;}
    public void load(CompoundTag t){long now=mob.level().getGameTime();expires=Math.min(t.getLong("Expires"),now+60);frightenedUntil=Math.min(t.getLong("Frightened"),now+100);whirls.clear();
        if(expires<=now)return;var list=t.getList("Whirls",Tag.TAG_COMPOUND);for(int i=0;i<Math.min(3,list.size());i++){var n=list.getCompound(i);Vec3 p=new Vec3(n.getDouble("X"),n.getDouble("Y"),n.getDouble("Z"));if(p.distanceToSqr(mob.position())<400)whirls.add(p);}}
}
