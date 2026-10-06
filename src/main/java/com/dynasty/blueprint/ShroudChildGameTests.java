package com.dynasty.blueprint;

import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class ShroudChildGameTests {
    private static TemplateMob child(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++)for(int y=1;y<=8;y++)h.setBlock(x,y,z,y==1||y==8?Blocks.STONE:Blocks.AIR);
        var mob=h.spawn(BlueprintEntities.FUHUN_BAIBU_TONGZI.get(),new BlockPos(7,2,7));mob.setNoAi(true);return mob;
    }
    private static final class Victim extends net.minecraft.server.level.ServerPlayer {
        Victim(net.minecraft.server.level.ServerLevel level){
            super(level.getServer(),level,new com.mojang.authlib.GameProfile(UUID.randomUUID(),"shroud-test"));
            connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(level.getServer(),
                new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),this);
        }
        public void attemptJump(){super.jumpFromGround();}
    }
    private static Victim player(GameTestHelper h,int x,int z,float yaw){
        var p=new Victim(h.getLevel());p.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(x,2,z))));p.setYRot(yaw);p.setXRot(0);
        p.getFoodData().setFoodLevel(10);p.getFoodData().setSaturation(0);h.getLevel().addNewPlayer(p);
        h.onEachTick(()->{if(!p.isRemoved())p.doTick();});return p;
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="shroud")
    public static void curseHasFortyTickWarningAndOnlyBindsSelectedPlayer(GameTestHelper h){
        var mob=child(h);var a=player(h,7,10,0);var b=player(h,9,10,0);double original=a.getAttributeValue(Attributes.MOVEMENT_SPEED);
        h.assertTrue(mob.startSkill(ArmySkills.CHILD_CURSE,a),"Child starts behind selected server player");
        h.runAfterDelay(38,()->h.assertTrue(!a.hasEffect(BlueprintEntities.SOUL_BIND.get())&&a.getFoodData().getFoodLevel()==10,"No early bind or food drain"));
        h.runAfterDelay(43,()->{
            h.assertTrue(a.hasEffect(BlueprintEntities.SOUL_BIND.get())&&a.getFoodData().getFoodLevel()==9,"Contact binds and drains10% of current food once");
            h.assertTrue(!b.hasEffect(BlueprintEntities.SOUL_BIND.get())&&b.getFoodData().getFoodLevel()==10,"Nearby second player is not substituted or hit");
            h.assertTrue(Math.abs(a.getAttributeValue(Attributes.MOVEMENT_SPEED)-original*.05)<.001,"Finite server movement attribute applies");
            a.attemptJump();h.assertTrue(a.getDeltaMovement().y<=0,"Actual jump event blocks upward impulse while bound");
        });
        h.runAfterDelay(77,()->{
            h.assertTrue(!a.hasEffect(BlueprintEntities.SOUL_BIND.get())&&Math.abs(a.getAttributeValue(Attributes.MOVEMENT_SPEED)-original)<.001,"Thirty-tick bind expires and restores movement");
            a.attemptJump();h.assertTrue(a.getDeltaMovement().y>0,"Jump resumes after expiry");
            h.assertTrue(a.getFoodData().getFoodLevel()==9,"Recovery cannot replay food drain");a.discard();b.discard();h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=75,batch="shroud")
    public static void turningBackInterruptsAndReloadCannotBypassCooldown(GameTestHelper h){
        var mob=child(h);var p=player(h,7,10,0);h.assertTrue(mob.startSkill(ArmySkills.CHILD_CURSE,p),"Curse starts");
        h.runAfterDelay(20,()->p.setYRot(180));
        h.runAfterDelay(23,()->{
            h.assertTrue(mob.skillId()==0,"Looking at caster cancels authoritative action and tracked clip");p.setYRot(0);
            var nbt=new CompoundTag();mob.save(nbt);mob.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            var copy=BlueprintEntities.FUHUN_BAIBU_TONGZI.get().create(h.getLevel());copy.load(nbt);h.getLevel().addFreshEntity(copy);
            h.assertTrue(!copy.startSkill(ArmySkills.CHILD_CURSE,p),"Saved cooldown survives cancelled cast and reload");
        });
        h.runAfterDelay(60,()->{h.assertTrue(!p.hasEffect(BlueprintEntities.SOUL_BIND.get())&&p.getFoodData().getFoodLevel()==10,"Turning away later never resumes cancelled curse");p.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=95,batch="shroud")
    public static void reloadResumesWarningOnceAndPostContactReloadNeverReplays(GameTestHelper h){
        TemplateMob[] mob={child(h)};var p=player(h,7,10,0);h.assertTrue(mob[0].startSkill(ArmySkills.CHILD_CURSE,p),"Curse starts");
        Runnable reload=()->{var nbt=new CompoundTag();mob[0].save(nbt);mob[0].remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            mob[0]=BlueprintEntities.FUHUN_BAIBU_TONGZI.get().create(h.getLevel());mob[0].load(nbt);h.getLevel().addFreshEntity(mob[0]);};
        h.runAfterDelay(20,reload);
        h.runAfterDelay(37,()->h.assertTrue(p.getFoodData().getFoodLevel()==10&&!p.hasEffect(BlueprintEntities.SOUL_BIND.get()),"Mid-warning reload retains original server epoch"));
        h.runAfterDelay(43,()->{h.assertTrue(p.getFoodData().getFoodLevel()==9&&p.hasEffect(BlueprintEntities.SOUL_BIND.get()),"Reloaded cast contacts exactly once");reload.run();});
        h.runAfterDelay(78,()->{h.assertTrue(p.getFoodData().getFoodLevel()==9&&!p.hasEffect(BlueprintEntities.SOUL_BIND.get())&&mob[0].skillId()==0,"Consumed contact stays consumed across second reload");p.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=65,batch="shroud")
    public static void losingSightCancelsWithoutRetargetingAnotherPlayer(GameTestHelper h){
        var mob=child(h);var a=player(h,7,10,0);var b=player(h,10,10,0);h.assertTrue(mob.startSkill(ArmySkills.CHILD_CURSE,a),"Curse starts");
        h.runAfterDelay(15,()->{for(int x=6;x<=8;x++)for(int y=2;y<=5;y++)h.setBlock(x,y,9,Blocks.STONE);});
        h.runAfterDelay(18,()->h.assertTrue(mob.skillId()==0,"Solid cover breaks real server line of sight"));
        h.runAfterDelay(53,()->{h.assertTrue(a.getFoodData().getFoodLevel()==10&&b.getFoodData().getFoodLevel()==10&&!a.hasEffect(BlueprintEntities.SOUL_BIND.get())&&!b.hasEffect(BlueprintEntities.SOUL_BIND.get()),"No through-wall damage or target handoff");a.discard();b.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=125,batch="shroud")
    public static void laughOnlyGlaresAtPlayersFacingLanternAndExpires(GameTestHelper h){
        var mob=child(h);var facing=player(h,7,10,180);var away=player(h,10,7,-90);
        h.assertTrue(!mob.startSkill(ArmySkills.CHILD_CURSE,facing),"Cannot curse a player already watching");
        // Let the native sixty-tick login invulnerability expire; no damage override in this player.
        h.runAfterDelay(65,()->h.assertTrue(mob.startSkill(ArmySkills.CHILD_LAUGH,facing),"Lantern attack starts"));
        h.runAfterDelay(75,()->h.assertTrue(facing.getHealth()==20&&away.getHealth()==20,"Laugh warning has no early contact"));
        h.runAfterDelay(80,()->{
            h.assertTrue(facing.getHealth()<20&&away.getHealth()<20,"Real bounded ring damages both nearby enemies");
            h.assertTrue(facing.hasEffect(BlueprintEntities.LANTERN_GLARE.get())&&!away.hasEffect(BlueprintEntities.LANTERN_GLARE.get()),"Only server-confirmed forward gaze receives finite glare");
        });
        h.runAfterDelay(101,()->{h.assertTrue(!facing.hasEffect(BlueprintEntities.LANTERN_GLARE.get()),"Glare expires natively without a persistent camera flag");facing.discard();away.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=130,batch="shroud")
    public static void autonomousRetreatKeepsFacingEnemyWithNormalCollision(GameTestHelper h){
        var mob=child(h);var p=player(h,7,10,180);mob.setNoAi(false);mob.setTarget(p);var initial=mob.position();boolean[] retreated={false},faced={false};
        h.onEachTick(()->{
            if(mob.position().distanceTo(initial)>.5&&mob.distanceTo(p)>3.5){retreated[0]=true;
                var toward=p.position().subtract(mob.position()).multiply(1,0,1).normalize();
                if(mob.getLookAngle().dot(toward)>.8)faced[0]=true;}
        });
        h.runAfterDelay(110,()->{h.assertTrue(retreated[0]&&faced[0]&&!mob.noPhysics&&!mob.isNoGravity(),"AI physically retreats while facing player; no noclip/teleport; retreat="+retreated[0]+" face="+faced[0]);p.discard();h.succeed();});
    }
}
