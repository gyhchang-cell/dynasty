package com.dynasty.expansion;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.phys.Vec3;
import java.util.*;

/** Finite phases of the existing mob AI. Damage is owned by one actual contact, never the animation. */
final class SecondaryCombatActions {
    private final SecondaryMob mob;
    private String action="";
    private UUID targetId;
    private int age,holdTicks,evadeTicks;
    private boolean hit,pinch;
    private Vec3 launch=Vec3.ZERO,holdAnchor;
    private BlockPos water;
    private UUID heldId;
    private long holdReady;
    SecondaryCombatActions(SecondaryMob mob){this.mob=mob;}
    boolean active(){return !action.isEmpty()||evadeTicks>0;}
    String phase(){return action;}
    boolean begin(LivingEntity target){
        if(active()||target==null||!target.isAlive()||mob.isAlliedTo(target)||!mob.hasLineOfSight(target)||mob.distanceToSqr(target)>100)return false;
        if(mob.spec.id().equals("venom_scorpion")&&mob.distanceToSqr(target)>4)return false;
        action=switch(mob.spec.id()){
            case "red_fox"->"pounce";case "golden_leopard"->"stalk";
            case "gray_falcon","bat_demon","wooden_magpie"->"circle";
            case "carp_spirit"->mob.isInWater()?"return_water":"";
            case "crab_soldier"->"side_charge";
            case "venom_scorpion"->pinch?"sting":"pinch";
            case "corpse_beetle","stone_worm"->mob.level().getBlockState(mob.blockPosition().below()).isSolid()?"burrow":"";
            default->"";
        };
        if(action.isEmpty())return false;
        targetId=target.getUUID();age=0;hit=false;launch=Vec3.ZERO;mob.getNavigation().stop();
        if(mob.spec.id().equals("carp_spirit"))water=mob.blockPosition();
        mob.skillAnimation(action);
        if(mob.spec.id().equals("wooden_magpie")){
            mob.playSound(SoundEvents.NOTE_BLOCK_BIT.get(),.6F,1.3F);
            for(var other:mob.level().getEntitiesOfClass(SecondaryMob.class,mob.getBoundingBox().inflate(12),m->m.spec.id().equals("wooden_magpie")&&m!=mob))other.setTarget(target);
            visual(target,"secondary_alarm",21,0xBD965B,16);
        }
        return true;
    }
    void tick(){
        tickHold();
        if(evadeTicks>0){evadeTicks--;mob.getNavigation().stop();mob.skillAnimation("evade");return;}
        if(action.isEmpty()||!(mob.level() instanceof ServerLevel level))return;
        var entity=level.getEntity(targetId);
        if(!(entity instanceof LivingEntity target)||!target.isAlive()||mob.isAlliedTo(target)||mob.distanceToSqr(target)>196||!mob.hasLineOfSight(target)){cancel();return;}
        mob.getNavigation().stop();mob.getLookControl().setLookAt(target,30,30);age++;
        String id=mob.spec.id();
        if(Set.of("gray_falcon","bat_demon","wooden_magpie").contains(id)){
            if(age<=20){
                action="circle";double a=age*.22;
                steer(target.position().add(Math.cos(a)*2.5,3.5,Math.sin(a)*2.5),.22);
            }else if(age<=30){
                action="dive";steer(target.getBoundingBox().getCenter(),.7);contact(target);
            }else{
                action="circle";steer(target.position().add(0,4,0),.24);
                if(age>=46)cancel();
            }
        }else if(id.equals("carp_spirit")){
            if(age<5)action="return_water";
            else if(age==5){action="pounce";launch=horizontal(target).scale(.48);mob.setDeltaMovement(launch.x,.52,launch.z);mob.hurtMarked=true;}
            else if(age<=18){action="pounce";contact(target);}
            else{
                action="return_water";
                if(water==null||!level.hasChunkAt(water)||!level.getFluidState(water).is(net.minecraft.tags.FluidTags.WATER)){cancel();return;}
                steer(Vec3.atCenterOf(water),.28);
                if(mob.isInWater()||age>=44)cancel();
            }
        }else if(id.equals("crab_soldier")){
            action="side_charge";
            if(age==1){var f=horizontal(target);launch=new Vec3(f.z,0,-f.x).scale(.28);}
            if(age<=6)mob.setDeltaMovement(launch.x,mob.getDeltaMovement().y,launch.z);
            else if(age<=18){if(age==7)launch=horizontal(target).scale(.42);mob.setDeltaMovement(launch.x,mob.getDeltaMovement().y,launch.z);contact(target);}
            else cancel();
        }else if(id.equals("corpse_beetle")||id.equals("stone_worm")){
            if(age<=18){
                action="burrow";
                if(age==7)launch=horizontal(target).scale(.32);
                if(age>=7){if(mob.horizontalCollision){cancel();return;}mob.setDeltaMovement(launch.x,mob.getDeltaMovement().y,launch.z);}
            }else{
                action="eruption";
                if(age==19){launch=horizontal(target).scale(.38);mob.setDeltaMovement(launch.x,.28,launch.z);mob.hurtMarked=true;CombatFeedback.send(mob,CombatFeedback.LAUNCH);}
                contact(target);if(age>=30)cancel();
            }
        }else if(id.equals("venom_scorpion")){
            if(age<6)mob.setDeltaMovement(0,mob.getDeltaMovement().y,0);
            else if(age<=12){var f=horizontal(target).scale(.18);mob.setDeltaMovement(f.x,mob.getDeltaMovement().y,f.z);contact(target);}
            else if(age>=18)cancel();
        }else{
            int release=id.equals("golden_leopard")?12:6;
            if(age<release){action=id.equals("golden_leopard")?"stalk":"pounce";mob.setDeltaMovement(0,mob.getDeltaMovement().y,0);}
            else{
                action="pounce";
                if(age==release){launch=horizontal(target).scale(id.equals("golden_leopard")?.62:.48);mob.setDeltaMovement(launch.x,.23,launch.z);mob.hurtMarked=true;}
                else if(age<release+8)mob.setDeltaMovement(launch.x,mob.getDeltaMovement().y,launch.z);
                contact(target);if(age>=release+16||mob.horizontalCollision)cancel();
            }
        }
        if(!action.isEmpty())mob.skillAnimation(action);
    }
    private Vec3 horizontal(LivingEntity target){return target.position().subtract(mob.position()).multiply(1,0,1).normalize();}
    private void steer(Vec3 point,double speed){
        var delta=point.subtract(mob.position());
        mob.setDeltaMovement(delta.lengthSqr()<speed*speed?delta:delta.normalize().scale(speed));mob.hurtMarked=true;
    }
    private void contact(LivingEntity target){
        if(hit||!mob.getBoundingBox().inflate(.15).intersects(target.getBoundingBox())||!mob.hasLineOfSight(target))return;
        // Re-entry through doHurtTarget adds the mob's original poison, theft, leech, etc. once.
        if(mob.doHurtTarget(target)){
            hit=true;
            if(mob.spec.id().equals("bat_demon"))visual(target,"secondary_echo",26,0xB899D6,16);
            if(mob.spec.id().equals("golden_leopard"))CombatFeedback.send(target,CombatFeedback.ARMOR);
        }
    }
    void successfulMelee(LivingEntity target){
        switch(mob.spec.id()){
            case "giant_python"->{if(bind(target,32)){mob.skillAnimation("coil");visual(target,"secondary_coil",13,0x719852,32);}}
            case "crab_soldier"->{bind(target,18);mob.skillAnimation("pinch");}
            case "venom_scorpion"->{
                pinch=!pinch;
                if(pinch){bind(target,18);mob.skillAnimation("pinch");}else mob.skillAnimation("sting");
            }
            case "wandering_spirit"->{mob.skillAnimation("possession");visual(target,"secondary_possession",15,0x6F92A5,30);}
            default->{}
        }
    }
    private boolean bind(LivingEntity target,int duration){
        if(ExpansionEffects.boss(target)||mob.isAlliedTo(target)||mob.level().getGameTime()<holdReady)return false;
        heldId=target.getUUID();holdAnchor=target.position();holdTicks=duration;
        holdReady=mob.level().getGameTime()+80;
        // This is the existing vanilla movement effect plus bounded impulses, not input/camera control.
        target.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,duration,4));
        return true;
    }
    private void tickHold(){
        if(holdTicks<=0||!(mob.level() instanceof ServerLevel level))return;
        var entity=level.getEntity(heldId);
        if(!(entity instanceof LivingEntity target)||!target.isAlive()||ExpansionEffects.boss(target)||mob.isAlliedTo(target)
                ||mob.distanceToSqr(target)>9||!mob.hasLineOfSight(target)||!target.hasEffect(MobEffects.MOVEMENT_SLOWDOWN)){holdTicks=0;return;}
        holdTicks--;
        var old=target.getDeltaMovement();var returnForce=holdAnchor.subtract(target.position()).multiply(1,0,1).scale(.18);
        if(returnForce.lengthSqr()>.01)returnForce=returnForce.normalize().scale(.1);
        target.setDeltaMovement(old.x*.1+returnForce.x,old.y,old.z*.1+returnForce.z);target.hurtMarked=true;
        if(mob.spec.id().equals("giant_python")){
            mob.skillAnimation("coil");
            if(holdTicks%5==0)target.setAirSupply(Math.max(0,target.getAirSupply()-8));
            if(holdTicks==12)target.hurt(target.damageSources().drown(),2);
        }
    }
    void evade(LivingEntity attacker){
        if(!mob.spec.id().equals("red_fox")||attacker==null||evadeTicks>0)return;
        var away=mob.position().subtract(attacker.position()).multiply(1,0,1).normalize();
        var side=new Vec3(away.z,0,-away.x).scale(.4);
        if(!mob.level().noCollision(mob,mob.getBoundingBox().move(side.scale(2))))side=side.scale(-1);
        if(!mob.level().noCollision(mob,mob.getBoundingBox().move(side.scale(2))))return;
        cancel();evadeTicks=6;mob.setDeltaMovement(side.x,.12,side.z);mob.hurtMarked=true;mob.skillAnimation("evade");
    }
    private static void visual(LivingEntity target,String sequence,int template,int tint,int duration){
        if(!(target.level() instanceof ServerLevel level))return;
        var packet=new com.dynasty.cod3.Cod3VisualPacket(level.dimension().location().toString(),template,target.getId(),
                level.random.nextLong(),level.getGameTime(),duration,1,target.position(),target.getLookAngle(),sequence,0,tint);
        com.dynasty.network.DynastyNetwork.CHANNEL.send(net.minecraftforge.network.PacketDistributor.NEAR.with(()->
                new net.minecraftforge.network.PacketDistributor.TargetPoint(target.getX(),target.getY(),target.getZ(),32,level.dimension())),packet);
    }
    void cancel(){action="";targetId=null;age=0;launch=Vec3.ZERO;mob.getNavigation().stop();}
    void reset(){cancel();holdTicks=0;evadeTicks=0;heldId=null;holdAnchor=null;water=null;}
}
