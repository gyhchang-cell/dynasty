package com.dynasty.dungeon;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.*;

/** Contacts use finite loaded-room geometry. No explosion, terrain edit or camera/input mutation. */
final class DungeonTrapEffects {
    static void contact(ServerLevel level,DungeonMechanismBlockEntity be,DungeonTrapProfile profile){
        if(profile.damage<=0)return;var pos=be.getBlockPos();var facing=be.getBlockState().getValue(DungeonMechanismBlock.FACING);
        var box=switch(profile){
            case CRUSHER->DungeonTrapGeometry.hammerContact(pos);
            case STEAM->new AABB(pos.above()).move(facing.getStepX()*1.5,0,facing.getStepZ()*1.5).inflate(1.5,.5,1.5);
            case MINE->new AABB(pos.above()).inflate(3,1,3);
            case ARROW_RAIN->new AABB(pos.above()).inflate(6,3,6);
            default->new AABB(pos.above());
        };
        var source=Vec3.atBottomCenterOf(pos.above()).add(0,.1,0);
        for(var player:level.getEntitiesOfClass(Player.class,box,p->p.isAlive()&&!p.isCreative()&&!p.isSpectator())){
            Vec3 from=profile==DungeonTrapProfile.ARROW_RAIN?player.getEyePosition().add(0,10,0):source;
            if(!level.hasChunkAt(BlockPos.containing(from))||level.clip(new ClipContext(from,player.getEyePosition(),ClipContext.Block.COLLIDER,ClipContext.Fluid.NONE,player)).getType()!=HitResult.Type.MISS)continue;
            if(player.hurt(level.damageSources().generic(),profile.damage)&&profile==DungeonTrapProfile.STEAM){
                player.setSecondsOnFire(2);push(player,facing,.12);player.hurtMarked=true;
            }
        }
        level.sendParticles(profile==DungeonTrapProfile.STEAM?ParticleTypes.CLOUD:profile==DungeonTrapProfile.MINE?ParticleTypes.EXPLOSION:ParticleTypes.CRIT,
                source.x,source.y,source.z,profile==DungeonTrapProfile.ARROW_RAIN?12:6,1,.3,1,.02);
    }
    static void continuous(ServerLevel level,DungeonMechanismBlockEntity be,DungeonTrapProfile profile){
        if(profile!=DungeonTrapProfile.CONVEYOR&&profile!=DungeonTrapProfile.WIND_FIELD&&profile!=DungeonTrapProfile.UPDRAFT)return;
        var pos=be.getBlockPos();
        if(profile==DungeonTrapProfile.CONVEYOR){
            var surface=new AABB(pos.getX(),pos.getY()+.98,pos.getZ(),pos.getX()+1,pos.getY()+1.1,pos.getZ()+1);
            for(var entity:level.getEntities((Entity)null,surface,e->e.isAlive()&&!e.isSpectator()&&!e.noPhysics
                &&!e.isPassenger()&&e.onGround()&&Math.abs(e.getBoundingBox().minY-(pos.getY()+1))<=.08)){
                push(entity,be.getBlockState().getValue(DungeonMechanismBlock.FACING),.055);entity.hurtMarked=true;
            }
            return;
        }
        if(profile==DungeonTrapProfile.UPDRAFT){
            for(var entity:level.getEntities((Entity)null,DungeonTrapGeometry.updraft(pos),e->e.isAlive()&&!e.isSpectator()&&!e.noPhysics&&!e.isPassenger())){
                var velocity=entity.getDeltaMovement();
                // Cores run every two ticks; overcome native gravity without an unbounded launch.
                if(velocity.y<.33)entity.setDeltaMovement(velocity.x,Math.min(.33,velocity.y+.24),velocity.z);
                entity.fallDistance=0;entity.hurtMarked=true;
            }
            if(level.getGameTime()%4==0)level.sendParticles(ParticleTypes.CLOUD,pos.getX()+.5,pos.getY()+1.1,pos.getZ()+.5,2,.25,.05,.25,.02);
            return;
        }
        var box=new AABB(pos.above()).inflate(4,2,4);
        var facing=be.getBlockState().getValue(DungeonMechanismBlock.FACING);
        for(var player:level.getEntitiesOfClass(Player.class,box,p->p.isAlive()&&!p.isSpectator()&&!p.isCreative())){
            push(player,facing,profile==DungeonTrapProfile.CONVEYOR?.055:.04);player.hurtMarked=true;
        }
    }
    private static void push(Entity player,Direction facing,double strength){
        var old=player.getDeltaMovement();var horizontal=new Vec3(old.x+facing.getStepX()*strength,0,old.z+facing.getStepZ()*strength);
        // A fast player keeps their existing movement. Environmental acceleration itself is capped.
        if(horizontal.horizontalDistanceSqr()>.09){if(old.horizontalDistanceSqr()>.09)return;horizontal=horizontal.normalize().scale(.3);}
        player.setDeltaMovement(horizontal.x,old.y,horizontal.z);
    }
    private DungeonTrapEffects(){}
}
