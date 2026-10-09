package com.dynasty.expansion;

import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class SecondaryActionGameTests {
    private static void room(GameTestHelper h){
        for(int x=1;x<=12;x++)for(int z=1;z<=7;z++)for(int y=1;y<=9;y++)h.setBlock(x,y,z,y==1||y==9?Blocks.STONE:Blocks.AIR);
    }
    private static SecondaryMob source(GameTestHelper h,String id,int x,int y){
        var m=SecondaryMobs.TYPES.get(id).get().create(h.getLevel());m.goalSelector.removeAllGoals(g->true);m.targetSelector.removeAllGoals(g->true);
        m.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(x,y,4))));h.getLevel().addFreshEntity(m);return m;
    }
    private static Zombie target(GameTestHelper h,int x){
        var z=new Zombie(h.getLevel());z.setNoAi(true);z.setNoGravity(true);z.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);z.setHealth(1000);
        z.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(x,2,4))));h.getLevel().addFreshEntity(z);return z;
    }
    @GameTest(template="bow_ritual_test",batch="cod4_pounce_physics",timeoutTicks=100)
    public static void actualFoxPounceHasWindupAndOnlyOneContact(GameTestHelper h){
        room(h);var fox=source(h,"red_fox",3,2);var z=target(h,6);h.assertTrue(fox.combatActions.begin(z),"Fox starts its real pounce");float[] hitHealth={1000};
        h.startSequence().thenIdle(4).thenExecute(()->h.assertTrue(z.getHealth()==1000,"Windup cannot hurt a remote target"))
            .thenWaitUntil(()->h.assertTrue(z.getHealth()<1000,"Actual vanilla movement reaches one body contact"))
            .thenExecute(()->hitHealth[0]=z.getHealth()).thenIdle(20).thenExecute(()->{try{
                h.assertTrue(z.getHealth()==hitHealth[0],"Remaining phase ticks do not repeat the hit");h.assertTrue(!fox.combatActions.active(),"Pounce ends within its finite action window");h.succeed();
            }finally{fox.discard();z.discard();}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_action_occlusion")
    public static void wallsCancelAmbushBurrowAndDiveWithoutDamage(GameTestHelper h){
        room(h);var z=target(h,9);
        for(String id:new String[]{"golden_leopard","corpse_beetle","stone_worm","gray_falcon"}){
            var m=source(h,id,3,2);try{
                h.assertTrue(m.combatActions.begin(z),"Visible target starts authored phase: "+id);
                for(int y=2;y<9;y++)for(int dz=1;dz<=7;dz++)h.setBlock(6,y,dz,Blocks.STONE);
                m.combatActions.tick();h.assertTrue(!m.combatActions.active()&&z.getHealth()==1000,"Solid wall cancels action without animation damage: "+id);
                for(int y=2;y<9;y++)for(int dz=1;dz<=7;dz++)h.setBlock(6,y,dz,Blocks.AIR);
            }finally{m.discard();}
        }
        z.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_python_control")
    public static void coilDrainsAirForFiniteWindowAndCannotBePermanentlyRefreshed(GameTestHelper h){
        room(h);var python=source(h,"giant_python",3,2);python.setNoAi(true);var z=target(h,4);int air=z.getAirSupply();
        try{
            python.combatActions.successfulMelee(z);h.assertTrue(z.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Coil owns a real finite movement constraint");
            z.setDeltaMovement(.4,0,.4);python.combatActions.tick();h.assertTrue(z.getDeltaMovement().horizontalDistance()<.1,"Coil bounds horizontal escape while preserving vertical motion");
            for(int i=0;i<15;i++)python.combatActions.tick();python.combatActions.successfulMelee(z);
            for(int i=0;i<16;i++)python.combatActions.tick();h.assertTrue(z.getAirSupply()<air,"Finite coil actually drains breath");
            z.setDeltaMovement(.4,0,0);python.combatActions.tick();h.assertTrue(z.getDeltaMovement().x==.4,"Second contact cannot refresh the hold during its control cooldown");
            var boss=com.dynasty.entity.DynastyEntities.DRAGON_KING.get().create(h.getLevel());python.combatActions.successfulMelee(boss);
            h.assertTrue(!boss.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Boss rejects coil movement control");h.succeed();
        }finally{python.discard();z.discard();}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_falcon_dive",timeoutTicks=100)
    public static void falconCirclesAboveThenDamagesThroughActualDive(GameTestHelper h){
        room(h);var falcon=source(h,"gray_falcon",3,6);var z=target(h,6);h.assertTrue(falcon.combatActions.begin(z),"Flight action starts from a real high position");
        h.startSequence().thenIdle(16).thenExecute(()->h.assertTrue(falcon.getY()>z.getY()+2&&z.getHealth()==1000,"High circling telegraphs before the contact phase"))
            .thenWaitUntil(()->h.assertTrue(z.getHealth()<1000,"Actual dive movement reaches and hurts the target"))
            .thenIdle(25).thenExecute(()->{try{h.assertTrue(!falcon.combatActions.active()&&falcon.getY()>z.getY()+1,"Dive ends in bounded climb rather than permanent contact");h.succeed();}finally{falcon.discard();z.discard();}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_fox_evade")
    public static void foxEvadeHasActualSafeDisplacementAndReloadDropsAction(GameTestHelper h){
        room(h);var fox=source(h,"red_fox",4,2);var attacker=target(h,6);
        try{
            fox.combatActions.evade(attacker);h.assertTrue(fox.getDeltaMovement().horizontalDistance()>.3,"Evasion has a real sideways impulse");
            h.assertTrue(fox.animation().equals("evade"),"Impulse and authored evasion pose share the same state");
            var n=new net.minecraft.nbt.CompoundTag();fox.addAdditionalSaveData(n);fox.readAdditionalSaveData(n);
            h.assertTrue(!fox.combatActions.active(),"Reload cannot replay a half-finished contact action");h.succeed();
        }finally{fox.discard();attacker.discard();}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_crab_charge",timeoutTicks=100)
    public static void sidewaysCrabChargeEndsInActualPinch(GameTestHelper h){
        room(h);var crab=source(h,"crab_soldier",3,2);var z=target(h,6);double startZ=crab.getZ();
        h.assertTrue(crab.combatActions.begin(z),"Crab starts sideways rather than generic jump");
        h.startSequence().thenIdle(5).thenExecute(()->h.assertTrue(Math.abs(crab.getZ()-startZ)>.5&&z.getHealth()==1000,"Side movement precedes the real forward contact"))
            .thenWaitUntil(()->h.assertTrue(z.getHealth()<1000,"Claw contact really damages"))
            .thenExecute(()->{try{h.assertTrue(z.hasEffect(MobEffects.MOVEMENT_SLOWDOWN)&&z.getEffect(MobEffects.MOVEMENT_SLOWDOWN).getAmplifier()==4,"Successful claw contact owns finite pinch");h.succeed();}finally{crab.discard();z.discard();}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_scorpion_modes")
    public static void scorpionClawsAndTailKeepDistinctPosesAndBossImmunity(GameTestHelper h){
        room(h);var scorpion=source(h,"venom_scorpion",3,2);var z=target(h,4);
        try{
            scorpion.combatActions.successfulMelee(z);h.assertTrue(scorpion.animation().equals("pinch")&&z.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Claws own an authored grip plus finite hold");
            scorpion.combatActions.successfulMelee(z);h.assertTrue(scorpion.animation().equals("sting"),"The following contact uses the segmented tail-sting clip");
            var boss=com.dynasty.entity.DynastyEntities.DRAGON_KING.get().create(h.getLevel());scorpion.combatActions.successfulMelee(boss);
            h.assertTrue(!boss.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Boss cannot be pinned by claws");h.succeed();
        }finally{scorpion.discard();z.discard();}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_water_down",timeoutTicks=100)
    public static void underwaterDragOwnsDownwardForceAndPurificationStopsCoil(GameTestHelper h){
        room(h);for(int x=2;x<=5;x++)for(int z=3;z<=5;z++)for(int y=2;y<=4;y++)h.setBlock(x,y,z,Blocks.WATER);
        var ghost=source(h,"drowning_ghost",3,2);ghost.setNoAi(true);var z=target(h,4);z.baseTick();
        try{
            h.assertTrue(z.isInWater()&&ghost.beginWaterDrag(z),"Underwater fixture binds to actual nearby water");z.setDeltaMovement(Vec3.ZERO);ghost.tickWaterDrag();
            h.assertTrue(z.getDeltaMovement().y<0&&z.getDeltaMovement().y>=-.0251,"Submerged drag uses a small finite downward force");
            var python=source(h,"giant_python",3,2);python.setNoAi(true);python.combatActions.successfulMelee(z);z.removeEffect(MobEffects.MOVEMENT_SLOWDOWN);
            z.setDeltaMovement(.4,0,0);python.combatActions.tick();h.assertTrue(z.getDeltaMovement().x==.4,"Purification stops control rather than leaving an invisible constraint");python.discard();h.succeed();
        }finally{ghost.discard();z.discard();}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_carp_cycle",timeoutTicks=120)
    public static void carpActuallyLeavesWaterHitsAndReturnsToWater(GameTestHelper h){
        room(h);for(int x=2;x<=4;x++)for(int z=3;z<=5;z++)h.setBlock(x,2,z,Blocks.WATER);
        var carp=source(h,"carp_spirit",3,2);var z=target(h,6);carp.baseTick();boolean[] left={false};
        h.assertTrue(carp.isInWater()&&carp.combatActions.begin(z),"Carp begins the cycle from real water");
        h.onEachTick(()->{if(!carp.isRemoved()&&!carp.isInWater())left[0]=true;});
        h.startSequence().thenWaitUntil(()->h.assertTrue(z.getHealth()<1000,"Actual jump meets target body"))
            .thenWaitUntil(()->h.assertTrue(!carp.combatActions.active()&&carp.isInWater(),"Finite return phase reaches real water"))
            .thenExecute(()->{try{h.assertTrue(left[0],"This was an exit/jump/contact/return cycle, not a hit while remaining submerged");h.succeed();}finally{carp.discard();z.discard();}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_burrow_contact",timeoutTicks=100)
    public static void wormBurrowsBeforeEruptionAndRealContactLaunch(GameTestHelper h){
        room(h);var worm=source(h,"stone_worm",3,2);var z=target(h,9);
        h.assertTrue(worm.combatActions.begin(z),"Solid ground permits real burrow approach");
        h.startSequence().thenIdle(12).thenExecute(()->h.assertTrue(worm.animation().equals("burrow")&&z.getHealth()==1000,"Burrow pose and underground approach cannot pre-hit a remote body"))
            .thenWaitUntil(()->h.assertTrue(z.getHealth()<1000,"Eruption movement must actually meet target body"))
            .thenExecute(()->{try{h.assertTrue(z.getDeltaMovement().y>0,"Real eruption contact owns the existing upward impulse");h.succeed();}finally{worm.discard();z.discard();}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_scorpion_contact",timeoutTicks=100)
    public static void scorpionClawWindupPrecedesOneRealPoisonContact(GameTestHelper h){
        room(h);var scorpion=source(h,"venom_scorpion",3,2);
        // Undead are immune to vanilla poison; use an actually susceptible live body.
        var z=net.minecraft.world.entity.EntityType.COW.create(h.getLevel());z.setNoAi(true);z.setNoGravity(true);
        z.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);z.setHealth(1000);
        z.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(4,2,4))));h.getLevel().addFreshEntity(z);
        h.assertTrue(scorpion.combatActions.begin(z)&&scorpion.animation().equals("pinch"),"Claw windup starts before the logical attack");
        h.startSequence().thenIdle(4).thenExecute(()->h.assertTrue(z.getHealth()==1000&&!z.hasEffect(MobEffects.POISON),"Windup has no remote poison/damage"))
            .thenWaitUntil(()->h.assertTrue(z.hasEffect(MobEffects.POISON),"Actual post-windup body contact adds the original poison once"))
            .thenExecute(()->{try{h.assertTrue(z.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"That same successful claw hit also owns its finite grip");h.succeed();}finally{scorpion.discard();z.discard();}});
    }
    private SecondaryActionGameTests(){}
}
