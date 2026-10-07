package com.dynasty.entity;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;

import java.util.EnumSet;
import java.util.UUID;

/**
 * 帝国士兵：用虎符召唤的友方部队，会跟随主人并攻击怪物。
 * Imperial Soldier: friendly troops summoned by the Tiger Tally; they follow their owner and hunt monsters.
 */
@SuppressWarnings("null")
public class ImperialSoldier extends PathfinderMob {

    static final int NATURAL_LOCAL_LIMIT = 4;
    static final double NATURAL_LOCAL_RADIUS = 48.0D;
    private UUID ownerId;
    private boolean savedLeashProtection;

    public ImperialSoldier(EntityType<? extends ImperialSoldier> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, 1024.0D)
                .add(Attributes.ATTACK_DAMAGE, 300.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.28D)
                .add(Attributes.ARMOR, 20.0D)
                .add(Attributes.FOLLOW_RANGE, 24.0D);
    }

    public void setOwner(Player owner) {
        this.ownerId = owner == null ? null : owner.getUUID();
    }

    public Player getOwner() {
        return this.ownerId == null ? null : this.level().getPlayerByUUID(this.ownerId);
    }

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        if (ownerId != null) tag.putUUID("DynastyOwner", ownerId);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        ownerId = tag.hasUUID("DynastyOwner") ? tag.getUUID("DynastyOwner") : null;
        // Leash holders resolve only on a later mob tick; isLeashed() is false during join.
        // Conservatively keep this protection for the session, even if later unhitched.
        savedLeashProtection = tag.contains("Leash", 10);
    }

    private static boolean natural(MobSpawnType reason) {
        return reason == MobSpawnType.NATURAL || reason == MobSpawnType.CHUNK_GENERATION;
    }

    @Override
    public boolean checkSpawnRules(LevelAccessor level, MobSpawnType reason) {
        if (!super.checkSpawnRules(level, reason)) return false;
        if (!natural(reason)) return true; // Commands, eggs and the player's army are not wild patrols.
        // WorldGenRegion cannot see live entities, so its animal population pass bypasses
        // density checks. Patrols enter only through the live, capped natural-spawn pass.
        if (reason == MobSpawnType.CHUNK_GENERATION) return false;
        if (!Mob.checkMobSpawnRules(DynastyEntities.IMPERIAL_SOLDIER.get(), level, reason, blockPosition(), level.getRandom())) return false;
        return level.getEntitiesOfClass(ImperialSoldier.class,
                getBoundingBox().inflate(NATURAL_LOCAL_RADIUS),
                soldier -> soldier != this && soldier.isAlive() && natural(soldier.getSpawnType()))
                .size() < NATURAL_LOCAL_LIMIT;
    }

    @Override
    public int getMaxSpawnClusterSize() {
        return 1;
    }

    @Override
    public boolean requiresCustomPersistence() {
        return ownerId != null || hasCustomName() || savedLeashProtection || super.requiresCustomPersistence();
    }

    @Override
    public boolean removeWhenFarAway(double distance) {
        // Forge saves forge:spawn_type even for old worlds. Unknown/command origins are
        // deliberately preserved: the old army did not save its owner's UUID.
        return natural(getSpawnType()) && ownerId == null && !hasCustomName()
                && !isPersistenceRequired() && !savedLeashProtection && !isLeashed() && !isPassenger() && !isVehicle();
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(1, new FormationGoal());
        this.goalSelector.addGoal(2, new MeleeAttackGoal(this, 1.2D, true));
        this.goalSelector.addGoal(6, new FollowOwnerGoal());
        this.goalSelector.addGoal(7, new RandomStrollGoal(this, 0.9D));
        this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 8.0F));
        this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
        this.targetSelector.addGoal(1, new NearestAttackableTargetGoal<>(this, Monster.class, true));
    }

    public boolean isRosterSoldier(){return getPersistentData().hasUUID("ArmySoldier");}
    @Override public boolean isAlliedTo(net.minecraft.world.entity.Entity other) {
        if(ownerId!=null&&(ownerId.equals(other.getUUID())||other instanceof ImperialSoldier s&&ownerId.equals(s.ownerId)))return true;
        return super.isAlliedTo(other);
    }
    @Override public void push(net.minecraft.world.entity.Entity other) {
        if(isRosterSoldier()&&other instanceof ImperialSoldier s&&s.isRosterSoldier()&&ownerId!=null&&ownerId.equals(s.ownerId))return;
        super.push(other);
    }
    @Override protected boolean shouldDropLoot(){return !isRosterSoldier()&&super.shouldDropLoot();}
    @Override public int getExperienceReward(){return isRosterSoldier()?0:super.getExperienceReward();}
    private class FormationGoal extends Goal {
        FormationGoal(){setFlags(EnumSet.of(Flag.MOVE,Flag.LOOK));}
        @Override public boolean canUse(){return isRosterSoldier();}
        @Override public boolean requiresUpdateEveryTick(){return true;}
        @Override public void tick() {
            var self=ImperialSoldier.this;
            if(!(getOwner() instanceof net.minecraft.server.level.ServerPlayer owner)||!owner.isAlive()) {getNavigation().stop();setTarget(null);return;}
            if(!com.dynasty.army.ArmyRoster.valid(self,owner)){discard();return;}
            var tag=getPersistentData();
            var record=com.dynasty.army.ArmyRoster.find(owner,tag.getUUID("ArmySoldier"));
            if(record.getBoolean("RecallRequested")&&!com.dynasty.army.ArmyEncounters.active(owner)
                    &&(getLastHurtByMob()==null||tickCount-getLastHurtByMobTimestamp()>=40)) {
                com.dynasty.army.ArmyRoster.snapshot(record,self);record.putString("State","RESERVE");record.remove("Entity");record.remove("RecallRequested");discard();return;
            }
            var target=com.dynasty.army.ArmyRoster.slot(owner.position(),tag.getFloat("ArmyYaw"),tag.getInt("ArmySlot"),tag.getInt("ArmyFormation"));
            if(distanceToSqr(owner)>96*96){getNavigation().stop();setTarget(null);return;}
            var p=net.minecraft.core.BlockPos.containing(target);
            boolean ground=false;
            for(int dy=1;dy>=-2;dy--) {
                var feet=p.offset(0,dy,0);var floor=feet.below();
                if(!level().hasChunkAt(feet))continue;
                if(level().getBlockState(floor).isFaceSturdy(level(),floor,net.minecraft.core.Direction.UP)
                        &&level().getBlockState(feet).getCollisionShape(level(),feet).isEmpty()
                        &&level().getBlockState(feet.above()).getCollisionShape(level(),feet.above()).isEmpty()
                        &&level().getFluidState(feet).isEmpty()){target=new net.minecraft.world.phys.Vec3(target.x,feet.getY(),target.z);ground=true;break;}
            }
            double error=position().distanceToSqr(target);
            if(!ground||error<.12*.12)getNavigation().stop();
            else if(tickCount%5==0)getNavigation().moveTo(target.x,target.y,target.z,tag.getBoolean("ArmyBanner")?1.28:1.15);
            var enemy=getTarget();
            int ready=Math.max(0,tag.getInt("ArmyAttackCooldown")-1);tag.putInt("ArmyAttackCooldown",ready);
            if(enemy!=null&&enemy.isAlive()&&!isAlliedTo(enemy)&&error<.75*.75&&hasLineOfSight(enemy)) {
                getLookControl().setLookAt(enemy,20,getMaxHeadXRot());
                if(ready==0) {
                    if(tag.getInt("ArmyRole")==1&&distanceToSqr(enemy)<18*18) {
                        var line=new net.minecraft.world.phys.AABB(getEyePosition(),enemy.getEyePosition()).inflate(.2);
                        boolean blocked=level().getEntitiesOfClass(ImperialSoldier.class,line,e->e!=self&&isAlliedTo(e))
                            .stream().anyMatch(e->e.getBoundingBox().inflate(.1).clip(getEyePosition(),enemy.getEyePosition()).isPresent());
                        if(!blocked) {
                            var arrow=new net.minecraft.world.entity.projectile.Arrow(level(),self);
                            var direction=enemy.getEyePosition().subtract(arrow.position());
                            arrow.shoot(direction.x,direction.y+Math.sqrt(direction.x*direction.x+direction.z*direction.z)*.12,direction.z,1.8f,2);
                            arrow.getPersistentData().putUUID("ArmyShotOwner",owner.getUUID());
                            arrow.getPersistentData().putUUID("ArmyShotSoldier",tag.getUUID("ArmySoldier"));
                            arrow.setBaseDamage(90);arrow.pickup=net.minecraft.world.entity.projectile.AbstractArrow.Pickup.DISALLOWED;
                            level().addFreshEntity(arrow);tag.putInt("ArmyAttackCooldown",tag.getBoolean("ArmyVolley")?34:40);
                        }
                    } else if(tag.getInt("ArmyRole")!=1&&distanceToSqr(enemy)<5.3) {
                        swing(net.minecraft.world.InteractionHand.MAIN_HAND);doHurtTarget(enemy);tag.putInt("ArmyAttackCooldown",24);
                    }
                }
            }
            if(tickCount%40==0&&!com.dynasty.army.ArmyEncounters.active(owner))com.dynasty.army.ArmySupport.snapshot(owner,java.util.List.of(self));
            if(tickCount%40==0)com.dynasty.army.ArmyRoster.snapshot(com.dynasty.army.ArmyRoster.find(owner,tag.getUUID("ArmySoldier")),self);
        }
    }

    /** 跟随召唤者；离得太远直接传送过去。 / Follows the summoner, teleporting when far away. */
    private class FollowOwnerGoal extends Goal {
        private int nextPathTick;

        FollowOwnerGoal() {
            this.setFlags(EnumSet.of(Goal.Flag.MOVE, Goal.Flag.LOOK));
        }

        @Override
        public boolean canUse() {
            Player owner = ImperialSoldier.this.getOwner();
            return owner != null && owner.isAlive()
                    && ImperialSoldier.this.distanceToSqr(owner) > 16.0D;
        }

        @Override
        public boolean canContinueToUse() {
            return canUse();
        }

        @Override
        public void tick() {
            Player owner = ImperialSoldier.this.getOwner();
            if (owner == null) {
                return;
            }
            double dist = ImperialSoldier.this.distanceToSqr(owner);
            if (dist > 256.0D && !ImperialSoldier.this.level().isClientSide) {
                ImperialSoldier.this.teleportTo(owner.getX(), owner.getY(), owner.getZ());
            } else if (ImperialSoldier.this.tickCount >= nextPathTick) {
                ImperialSoldier.this.getNavigation().moveTo(owner, 1.1D);
                nextPathTick = ImperialSoldier.this.tickCount + 10;
            }
            ImperialSoldier.this.getLookControl().setLookAt(owner, 10.0F, ImperialSoldier.this.getMaxHeadXRot());
        }
    }
}
