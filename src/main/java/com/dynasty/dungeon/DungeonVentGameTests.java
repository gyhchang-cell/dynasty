package com.dynasty.dungeon;

import java.util.*;
import net.minecraft.core.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod2")
@PrefixGameTestTemplate(false)
public final class DungeonVentGameTests {
    private static FakePlayer player(GameTestHelper h,Vec3 at){
        var p=new FakePlayer(h.getLevel(),new com.mojang.authlib.GameProfile(UUID.randomUUID(),"vent-test")){
            @Override public boolean isInvulnerableTo(net.minecraft.world.damagesource.DamageSource source){return false;}
        };
        try{var f=net.minecraft.server.level.ServerPlayer.class.getDeclaredField("spawnInvulnerableTime");f.setAccessible(true);f.setInt(p,0);}
        catch(ReflectiveOperationException e){throw new IllegalStateException(e);}
        p.setNoGravity(true);p.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH).setBaseValue(200);p.setHealth(200);p.setPos(at);h.getLevel().addNewPlayer(p);return p;
    }
    @GameTest(template="bow_ritual_test",batch="cod2_vent_runtime",timeoutTicks=200)
    public static void jetsRespectFacingCoverAndNeverPlaceFire(GameTestHelper h){
        var level=h.getLevel();var pos=h.absolutePos(new BlockPos(6,2,6));var target=player(h,new Vec3(pos.getX()+.5,pos.getY(),pos.getZ()+2));
        h.runAfterDelay(3,()->{try{
            for(var profile:List.of(DungeonTrapProfile.STEAM,DungeonTrapProfile.FLAME))for(var direction:Direction.Plane.HORIZONTAL){
                level.setBlockAndUpdate(pos,(profile==DungeonTrapProfile.STEAM?DungeonContent.STEAM.get():DungeonContent.FLAME.get()).defaultBlockState().setValue(DungeonMechanismBlock.FACING,direction));
                var be=(DungeonMechanismBlockEntity)level.getBlockEntity(pos);be.configure(UUID.randomUUID(),"vent_qa",profile.id+"_qa",pos,-1,List.of());
                var center=Vec3.atBottomCenterOf(pos);var front=center.add(direction.getStepX()*2,0,direction.getStepZ()*2);
                target.setPos(center.add(-direction.getStepX()*2,0,-direction.getStepZ()*2));target.setHealth(200);target.invulnerableTime=0;target.clearFire();
                DungeonTrapEffects.contact(level,be,profile);h.assertTrue(target.getHealth()==200&&!target.isOnFire(),"Rear target is outside "+profile+" jet "+direction);
                target.setPos(front);target.setDeltaMovement(Vec3.ZERO);var cover=pos.relative(direction);
                level.setBlockAndUpdate(cover,Blocks.STONE.defaultBlockState());level.setBlockAndUpdate(cover.above(),Blocks.STONE.defaultBlockState());
                DungeonTrapEffects.contact(level,be,profile);h.assertTrue(target.getHealth()==200&&!target.isOnFire(),"Solid cover blocks jet");
                level.setBlockAndUpdate(cover,Blocks.AIR.defaultBlockState());level.setBlockAndUpdate(cover.above(),Blocks.AIR.defaultBlockState());
                DungeonTrapEffects.contact(level,be,profile);h.assertTrue(target.getHealth()==197&&target.isOnFire(),"Actual native health and brief ignition follow contact");
                h.assertTrue(target.getDeltaMovement().horizontalDistance()<=.30001,"Vent impulse is bounded");
                h.assertTrue(level.getBlockState(cover).isAir()&&level.getBlockState(cover.above()).isAir(),"No real fire block or terrain destruction");
            }
            h.succeed();
        }finally{level.removePlayerImmediately(target,Entity.RemovalReason.DISCARDED);}});
    }
    @GameTest(template="bow_ritual_test",batch="cod2_vent_clocks")
    public static void ventsWarnCoolDownAndReloadWithoutReplayingBurn(GameTestHelper h){
        for(var profile:List.of(DungeonTrapProfile.STEAM,DungeonTrapProfile.FLAME)){
            var room=new DungeonRoomController();var clock=room.hazard(profile.id+"_qa",false);clock.trigger(100);
            for(int n=102;n<120;n+=2){clock.tickActive(n);h.assertTrue(clock.phase()==DungeonMechanism.Phase.WARNING&&!clock.consumeContact(),"No contact during20tick tell");}
            clock.tickActive(120);h.assertTrue(clock.phase()==DungeonMechanism.Phase.ACTIVE&&clock.consumeContact()&&!clock.consumeContact(),"Exactly one original clock contact");
            var copy=new DungeonRoomController();copy.load(room.save());var restored=copy.hazard(profile.id+"_qa",false);h.assertTrue(!restored.consumeContact(),"Saved active phase cannot replay burn");
            restored.tickActive(122);restored.tickActive(124);h.assertTrue(restored.phase()==DungeonMechanism.Phase.RECOVERY,"Four active ticks followed by cooldown");
            for(int n=126;n<=160;n+=2){restored.tickActive(n);h.assertTrue(!restored.consumeContact(),"Cooldown never emits a new contact");}
            h.assertTrue(restored.phase()==DungeonMechanism.Phase.IDLE,"Finite cooldown returns to idle");
        }h.succeed();
    }
    private DungeonVentGameTests(){}
}
