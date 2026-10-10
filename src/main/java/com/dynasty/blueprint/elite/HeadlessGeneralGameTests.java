package com.dynasty.blueprint.elite;

import com.dynasty.blueprint.BlueprintSpawnState;
import com.dynasty.blueprint.SkullBloodPool;
import com.dynasty.blueprint.combat.AttackState;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class HeadlessGeneralGameTests {
    private static HeadlessGeneral mob(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++){
            h.setBlock(x,1,z,Blocks.STONE);for(int y=2;y<=9;y++)h.setBlock(x,y,z,Blocks.AIR);
            if(x==0||x==15||z==0||z==15)for(int y=2;y<=7;y++)h.setBlock(x,y,z,Blocks.STONE);
        }
        var m=h.spawn(EliteContent.HEADLESS.get(),new BlockPos(7,2,7));m.setNoAi(true);m.setNoGravity(true);return m;
    }
    private static Cow cow(GameTestHelper h,int x,int z){var c=h.spawn(EntityType.COW,new BlockPos(x,2,z));c.setNoAi(true);c.setNoGravity(true);c.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);c.setHealth(1000);return c;}
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="headless_elite")
    public static void roarHasFullTellAndConeSideEscape(GameTestHelper h){
        var m=mob(h);var front=cow(h,7,13);var side=cow(h,12,7);
        h.assertTrue(m.startSkill(301,front),"Real server roar starts");
        h.runAfterDelay(22,()->h.assertTrue(front.getHealth()==1000&&side.getHealth()==1000,"No damage before 1.2-second tell"));
        h.runAfterDelay(27,()->h.assertTrue(front.getHealth()<1000&&side.getHealth()==1000&&front.hasEffect(net.minecraft.world.effect.MobEffects.WEAKNESS),"Cone contact hits front but permits lateral evasion"));
        h.runAfterDelay(92,()->{h.assertTrue(!front.hasEffect(net.minecraft.world.effect.MobEffects.WEAKNESS)&&m.skillId()==0,"Finite weakness and action cleanup");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=85,batch="headless_elite")
    public static void spinHasThreeContactsAndThirtyTickRecovery(GameTestHelper h){
        var m=mob(h);var target=cow(h,7,9);float[] hp={1000,1000,1000};
        h.onEachTick(()->{if(target.isAlive()){target.setPos(m.position().add(0,0,1));target.setDeltaMovement(Vec3.ZERO);}});
        h.assertTrue(m.startSkill(302,target),"Spin starts");
        h.runAfterDelay(14,()->h.assertTrue(target.getHealth()==1000,"Full 0.8-second twist warning"));
        h.runAfterDelay(18,()->{hp[0]=target.getHealth();h.assertTrue(hp[0]<1000,"First circle contact");});
        h.runAfterDelay(28,()->{hp[1]=target.getHealth();h.assertTrue(hp[1]<hp[0],"Second circle contact");});
        h.runAfterDelay(38,()->{hp[2]=target.getHealth();h.assertTrue(hp[2]<hp[1],"Third circle contact");});
        h.runAfterDelay(55,()->h.assertTrue(m.phase()==AttackState.RECOVERY&&target.getHealth()==hp[2],"Recovery leaves a real punish window with no damage"));
        h.runAfterDelay(80,()->{h.assertTrue(target.getHealth()==hp[2]&&m.skillId()==0&&!m.startSkill(302,target),"Exactly three contacts; cooldown remains");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=60,batch="headless_elite")
    public static void thrownHeadLocksLandingAndReloadDoesNotReplay(GameTestHelper h){
        var m=mob(h);var target=cow(h,7,12);var landing=target.position();
        h.assertTrue(m.startSkill(303,target),"Head throw starts");
        h.runAfterDelay(10,()->target.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(12,2,12)))));
        h.runAfterDelay(23,()->{
            h.assertTrue(target.getHealth()==1000,"Sidestep escapes locked landing");
            var pools=h.getLevel().getEntitiesOfClass(SkullBloodPool.class,m.getBoundingBox().inflate(12));
            h.assertTrue(pools.size()==1&&pools.get(0).position().distanceToSqr(landing)<.01,"One pool uses the warned point");
            var saved=new CompoundTag();m.save(saved);var id=m.getUUID();m.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            var restored=EliteContent.HEADLESS.get().create(h.getLevel());restored.load(saved);h.getLevel().addFreshEntity(restored);
            h.runAtTickTime(50,()->{h.assertTrue(restored.getUUID().equals(id)&&h.getLevel().getEntitiesOfClass(SkullBloodPool.class,restored.getBoundingBox().inflate(12)).size()==1,"Consumed impact remains consumed after real entity NBT reload");h.succeed();});
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=50,batch="headless_elite")
    public static void rearCounterBreaksThrowButNotSpin(GameTestHelper h){
        var m=mob(h);var target=cow(h,7,10);var rear=cow(h,7,5);
        h.assertTrue(m.startSkill(303,target),"Throw tell begins");m.hurt(m.damageSources().mobAttack(rear),4);
        h.assertTrue(m.attack().current()==null&&m.phase()==AttackState.STUN,"Actual accepted back hit interrupts throw");
        h.runAfterDelay(32,()->{
            h.assertTrue(h.getLevel().getEntitiesOfClass(SkullBloodPool.class,m.getBoundingBox().inflate(12)).isEmpty(),"Cancelled throw never leaks delayed damage");
            h.assertTrue(m.startSkill(302,target),"Independent spin remains usable");m.invulnerableTime=0;m.hurt(m.damageSources().mobAttack(rear),4);
            h.assertTrue(m.attack().current()==HeadlessGeneral.SPIN,"Spin retains authored unstoppable windup");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=35,batch="headless_elite")
    public static void structureMembershipSurvivesUnloadAndBlocksSecondEntrant(GameTestHelper h){
        var dummy=mob(h);dummy.discard();var level=h.getLevel();var feet=h.absolutePos(new BlockPos(7,2,7));var entrant=h.absolutePos(new BlockPos(1,2,1));
        var rule=level.getGameRules().getRule(GameRules.RULE_DOMOBSPAWNING);boolean previous=rule.get();rule.set(true,level.getServer());
        String key="headless-gametest@"+feet.asLong();
        try{
            h.assertTrue(EliteEncounters.spawn(level,key,feet,entrant),"One native authored encounter spawns");
            var marker=BlueprintSpawnState.get(level).markers.get(key);var id=marker.members.iterator().next();
            h.assertTrue(!EliteEncounters.spawn(level,key,feet,entrant.offset(1,0,0)),"Second entrant cannot duplicate member");
            var actor=level.getEntity(id);h.assertTrue(actor instanceof HeadlessGeneral,"Actual registered elite identity");actor.remove(Entity.RemovalReason.UNLOADED_TO_CHUNK);
            h.assertTrue(!EliteEncounters.spawn(level,key,feet,entrant)&&marker.members.contains(id),"Null UUID lookup is not death");
            var snapshot=BlueprintSpawnState.load(BlueprintSpawnState.get(level).save(new CompoundTag()));
            h.assertTrue(snapshot.markers.get(key).members.contains(id),"Native SavedData retains membership");h.succeed();
        }finally{rule.set(previous,level.getServer());}
    }
}
