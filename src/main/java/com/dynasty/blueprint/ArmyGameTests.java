package com.dynasty.blueprint;

import com.dynasty.blueprint.combat.AttackState;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import java.util.HashSet;
import java.util.UUID;

/** Real server entities, collisions and potion attributes. Only deterministic fixtures disable AI. */
@GameTestHolder("dynasty_army")
@PrefixGameTestTemplate(false)
public final class ArmyGameTests {
    private static void arena(GameTestHelper h){
        for(int x=0;x<16;x++)for(int z=0;z<16;z++){
            h.setBlock(x,1,z,Blocks.STONE);
            for(int y=2;y<14;y++)h.setBlock(x,y,z,y<8&&(x==0||z==0||x==15||z==15)?Blocks.STONE:Blocks.AIR);
        }
    }
    private static TemplateMob actor(GameTestHelper h,EntityType<TemplateMob> type,int x,int z){
        var mob=h.spawn(type,new BlockPos(x,2,z));mob.setNoAi(true);mob.setNoGravity(true);mob.setPersistenceRequired();return mob;
    }
    private static Cow target(GameTestHelper h,int x,int z){
        var cow=h.spawn(EntityType.COW,new BlockPos(x,2,z));cow.setNoAi(true);cow.setNoGravity(true);
        cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);cow.setHealth(200);
        cow.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);return cow;
    }
    /** Counts real explosion attempts, independently of fire/other combat events. */
    private static final class BlastWitness extends Cow {
        int explosions;
        BlastWitness(net.minecraft.world.level.Level level){super(EntityType.COW,level);}
        @Override public boolean hurt(DamageSource source,float amount){
            if(source.is(net.minecraft.tags.DamageTypeTags.IS_EXPLOSION))explosions++;
            boolean accepted=super.hurt(source,amount);
            com.mojang.logging.LogUtils.getLogger().info("ARMY_DAMAGE_WITNESS tick={} type={} amount={} accepted={} health={} explosionAttempts={}",
                level().getGameTime(),source.getMsgId(),amount,accepted,getHealth(),explosions);
            return accepted;
        }
    }
    private static void equal(GameTestHelper h,double a,double b,String message){h.assertTrue(Math.abs(a-b)<.01,message+": "+a+" / "+b);}
    private static void trace(GameTestHelper h,String label,TemplateMob mob,Cow enemy){
        var saved=new CompoundTag();mob.addAdditionalSaveData(saved);
        com.mojang.logging.LogUtils.getLogger().info("ARMY_DIAGNOSTIC {} at={} enemy={} delta={} skill={} phase={} age={} hp={}/{} sight={} data={}",
            label,mob.position(),enemy.position(),mob.getDeltaMovement(),mob.skillId(),mob.skillPhase(),mob.actionAge(0),mob.getHealth(),enemy.getHealth(),mob.hasLineOfSight(enemy),saved.getCompound("ArmyActionState"));
    }

    @GameTest(template="bow_ritual_test",timeoutTicks=40,batch="army")
    public static void spearThrustIsNarrowAndHasOneAuthoredContact(GameTestHelper h){
        arena(h);var mob=actor(h,BlueprintEntities.JUMA_CHANGQIANGBING.get(),6,5);Cow front=target(h,6,8),side=target(h,8,7),rear=target(h,6,3);
        h.assertTrue(mob.startSkill(ArmySkills.THRUST,front),"Accept 3.5-block thrust");
        h.runAfterDelay(10,()->equal(h,front.getHealth(),200,"No warning damage"));
        h.runAfterDelay(15,()->{trace(h,"thrust",mob,front);equal(h,front.getHealth(),195,"Single spear contact");equal(h,side.getHealth(),200,"Outside narrow strip");equal(h,rear.getHealth(),200,"No rear hit");});
        h.runAfterDelay(32,()->{equal(h,front.getHealth(),195,"Recovery cannot hit again");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=45,batch="army")
    public static void braceRequiresApproachAndSpendsOnlyOneCollision(GameTestHelper h){
        arena(h);var mob=actor(h,BlueprintEntities.JUMA_CHANGQIANGBING.get(),6,5);var enemy=target(h,6,8);
        h.assertTrue(!mob.startSkill(ArmySkills.BRACE,enemy),"Walking target cannot trigger brace");
        enemy.setSprinting(true);enemy.setDeltaMovement(0,0,.25);
        h.assertTrue(!ArmyBehaviors.charging(enemy,mob.position()),"Running away is not a charge");
        enemy.setDeltaMovement(0,0,-.25);h.assertTrue(mob.startSkill(ArmySkills.BRACE,enemy),"Approaching sprint triggers brace");enemy.setDeltaMovement(Vec3.ZERO);
        h.runAfterDelay(13,()->{trace(h,"brace",mob,enemy);equal(h,enemy.getHealth(),185,"Threefold counter");h.assertTrue(enemy.hasEffect(MobEffects.MOVEMENT_SLOWDOWN)&&!enemy.isSprinting(),"Counter breaks sprint and has a finite control effect");});
        h.runAfterDelay(38,()->{equal(h,enemy.getHealth(),185,"Brace collision spent once");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=55,batch="army")
    public static void crossbowFiresThreeRealNonHomingBolts(GameTestHelper h){
        arena(h);var mob=actor(h,BlueprintEntities.LIANNU_ZHENZU.get(),6,3);var enemy=target(h,6,11);var bolts=new HashSet<UUID>();
        h.onEachTick(()->h.getLevel().getEntitiesOfClass(TemplateProjectile.class,mob.getBoundingBox().inflate(14),p->p.getOwner()==mob).forEach(p->{if(p.armyMode()==1)bolts.add(p.getUUID());}));
        h.assertTrue(mob.startSkill(ArmySkills.VOLLEY,enemy),"Start actual volley");
        h.runAfterDelay(40,()->{h.assertTrue(bolts.size()==3,"Three distinct physical bolts, not one repeated visual: "+bolts.size());equal(h,enemy.getHealth(),188,"All three collision hits");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=145,batch="army")
    public static void possessedRollStillMovesAndDropsExactlyOneFiniteCaltrop(GameTestHelper h){
        arena(h);var mob=actor(h,BlueprintEntities.LIANNU_ZHENZU.get(),6,7);mob.setNoGravity(false);mob.setNoAi(false);var enemy=target(h,6,10);
        mob.addEffect(new MobEffectInstance(BlueprintEntities.BINGSHA_POSSESSION.get(),160));Vec3 initial=mob.position();
        h.assertTrue(mob.startSkill(ArmySkills.ROLL,enemy),"Possessed crossbow can roll");
        h.runAfterDelay(22,()->{
            trace(h,"roll",mob,enemy);
            h.assertTrue(mob.position().distanceTo(initial)>1.5,"Roll moves physical body; not only the model");
            var traps=h.getLevel().getEntitiesOfClass(ArmyCaltrop.class,mob.getBoundingBox().inflate(8),t->t.getOwner()==mob);
            h.assertTrue(traps.size()==1,"Scaled contact drops one real caltrop");enemy.setPos(traps.get(0).position());
        });
        h.runAfterDelay(36,()->h.assertTrue(enemy.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Caltrop slows actual overlapping enemy"));
        h.runAfterDelay(130,()->{h.assertTrue(h.getLevel().getEntitiesOfClass(ArmyCaltrop.class,mob.getBoundingBox().inflate(12),t->t.getOwner()==mob).isEmpty(),"Obstacle expires without leaving a block/item");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=80,batch="army")
    public static void hookPullsOnlyScoutAndCannotReuseStaleAction(GameTestHelper h){
        arena(h);var mob=actor(h,BlueprintEntities.TIESUO_CHIHOU.get(),6,3);mob.setNoGravity(false);mob.setNoAi(false);var enemy=target(h,6,13);Vec3 enemyStart=enemy.position(),mobStart=mob.position();
        h.assertTrue(mob.startSkill(ArmySkills.GRAPPLE,enemy),"Long-range hook accepted");long epoch=mob.skillStartTime();
        h.runAfterDelay(53,()->{
            trace(h,"hook",mob,enemy);
            h.assertTrue(mob.position().distanceTo(mobStart)>5,"A physical projectile attaches and pulls the scout");
            h.assertTrue(mob.distanceToSqr(enemy)<9,"Scout reaches knee distance");equal(h,enemy.position().distanceTo(enemyStart),0,"Player/target position is never anchored or teleported");
            h.assertTrue(enemy.getHealth()<200,"Knee collision has damage");
            mob.interruptAttack(5);mob.onArmyHookHit(enemy,epoch);
            var saved=new CompoundTag();mob.addAdditionalSaveData(saved);
            h.assertTrue(!saved.getCompound("ArmyActionState").hasUUID("Linked"),"Old projectile cannot attach after cancellation");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=90,batch="army")
    public static void powderFuseRequiresThreeSecondsAndNeverChangesTerrainOrAllies(GameTestHelper h){
        arena(h);var mob=actor(h,BlueprintEntities.KUIJUN_SISHI.get(),6,6);var enemy=target(h,6,8);var ally=actor(h,BlueprintEntities.LUDUN_JIASHI.get(),8,6);
        mob.setTarget(enemy);mob.addEffect(new MobEffectInstance(BlueprintEntities.BINGSHA_POSSESSION.get(),160));h.setBlock(5,2,6,Blocks.GOLD_BLOCK);float health=ally.getHealth();
        for(int tick:new int[]{1,20,40,50})h.runAfterDelay(tick,()->trace(h,"fuse-"+tick,mob,enemy));
        h.runAfterDelay(55,()->{trace(h,"fuse-55",mob,enemy);h.assertTrue(mob.isAlive(),"Possession does not shorten three seconds");});
        h.runAfterDelay(65,()->{trace(h,"fuse-65",mob,enemy);h.assertTrue(mob.isDeadOrDying(),"Proximity fuse detonates after sixty continuous ticks");h.assertTrue(enemy.getHealth()<190,"Blast damages enemies");equal(h,ally.getHealth(),health,"Army allies immune to blast");h.assertBlockPresent(Blocks.GOLD_BLOCK,new BlockPos(5,2,6));h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="army")
    public static void breakingProximityResetsPowderFuse(GameTestHelper h){
        arena(h);var mob=actor(h,BlueprintEntities.KUIJUN_SISHI.get(),6,6);var enemy=target(h,6,8);mob.setTarget(enemy);
        h.runAfterDelay(35,()->enemy.setPos(mob.position().add(0,0,7)));
        h.runAfterDelay(45,()->enemy.setPos(mob.position().add(0,0,2)));
        h.runAfterDelay(94,()->{h.assertTrue(mob.isAlive(),"Nonconsecutive near ticks cannot accumulate");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=130,batch="army")
    public static void breakingLitPowderFuseAllowsFreshThreeSecondFuse(GameTestHelper h){
        arena(h);var mob=actor(h,BlueprintEntities.KUIJUN_SISHI.get(),6,6);var enemy=target(h,6,8);mob.setTarget(enemy);
        h.runAfterDelay(48,()->{
            h.assertTrue(mob.skillId()==ArmySkills.DETONATE,"Fixture reaches lit fuse before retreat");
            enemy.setPos(mob.position().add(0,0,7));
        });
        h.runAfterDelay(54,()->h.assertTrue(mob.skillId()!=ArmySkills.DETONATE,"Retreat cancels the lit animation"));
        h.runAfterDelay(60,()->enemy.setPos(mob.position().add(0,0,2)));
        h.runAfterDelay(115,()->h.assertTrue(mob.isAlive(),"Returning target must earn a full new three seconds"));
        h.runAfterDelay(125,()->{
            trace(h,"relit-fuse",mob,enemy);
            h.assertTrue(mob.isDeadOrDying(),"Cancelled fuse must not retain a spent skill cooldown");
            h.assertTrue(enemy.getHealth()<190,"Fresh proximity fuse causes a real explosion");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=125,batch="army")
    public static void reloadingLitPowderFuseRequiresFreshContinuousProximity(GameTestHelper h){
        arena(h);var original=actor(h,BlueprintEntities.KUIJUN_SISHI.get(),6,6);var enemy=target(h,6,8);original.setTarget(enemy);
        TemplateMob[] restored={null};
        h.runAfterDelay(48,()->{
            h.assertTrue(original.skillId()==ArmySkills.DETONATE,"Save a genuinely lit fuse");
            var saved=new CompoundTag();original.saveWithoutId(saved);original.discard();
            var copy=BlueprintEntities.KUIJUN_SISHI.get().create(h.getLevel());copy.load(saved);copy.setTarget(enemy);
            h.getLevel().addFreshEntity(copy);restored[0]=copy;
        });
        h.runAfterDelay(103,()->h.assertTrue(restored[0].isAlive(),"Reload cannot discharge the old fuse or shorten its new clock"));
        h.runAfterDelay(118,()->{
            trace(h,"reloaded-fuse",restored[0],enemy);
            h.assertTrue(restored[0].isDeadOrDying(),"Restored live powder unit can complete a new sixty-tick fuse");
            h.assertTrue(enemy.getHealth()<190,"Reloaded fuse damages the server target");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=75,batch="army")
    public static void projectileDeathHasDelayedSmallBlastWithoutReloadReplay(GameTestHelper h){
        arena(h);var mob=actor(h,BlueprintEntities.KUIJUN_SISHI.get(),6,6);var enemy=new BlastWitness(h.getLevel());
        enemy.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(6,2,8))));enemy.setNoAi(true);enemy.setNoGravity(true);
        enemy.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);enemy.setHealth(200);enemy.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);
        h.getLevel().addFreshEntity(enemy);var arrow=new Arrow(h.getLevel(),enemy);
        mob.hurt(mob.damageSources().arrow(arrow,enemy),5000);
        h.assertTrue(mob.isDeadOrDying(),"Projectile fixture actually kills powder mob");
        h.runAfterDelay(24,()->equal(h,enemy.getHealth(),200,"No premature corpse explosion"));
        h.runAfterDelay(34,()->{
            trace(h,"corpse",mob,enemy);
            h.assertTrue(enemy.getHealth()<200&&enemy.explosions==1,"Exactly one actual thirty-tick death blast");
            enemy.clearFire();
            var saved=new CompoundTag();mob.addAdditionalSaveData(saved);h.assertTrue(saved.getCompound("ArmyActionState").getBoolean("Exploded"),"Spent blast persisted");mob.discard();
            var copy=BlueprintEntities.KUIJUN_SISHI.get().create(h.getLevel());copy.readAdditionalSaveData(saved);copy.moveTo(mob.position());h.getLevel().addFreshEntity(copy);
            h.runAfterDelay(20,()->{h.assertTrue(enemy.explosions==1,"Restored corpse cannot replay an explosion contact");
                var restored=new CompoundTag();copy.addAdditionalSaveData(restored);
                h.assertTrue(restored.getCompound("ArmyActionState").getBoolean("Exploded"),"Restored corpse retains spent state");h.succeed();});
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=100,batch="army")
    public static void bannerModifiersDoNotStackAndControlIsHalved(GameTestHelper h){
        arena(h);TemplateMob a=actor(h,BlueprintEntities.ZHENWANG_ZHANGQIGUAN.get(),5,5),b=actor(h,BlueprintEntities.ZHENWANG_ZHANGQIGUAN.get(),8,5),ally=actor(h,BlueprintEntities.ZUWU_DAOSHOU.get(),6,8);
        h.runAfterDelay(24,()->{
            equal(h,ally.getAttributeValue(Attributes.ATTACK_DAMAGE),6.25,"Two banners still grant only +25 percent");equal(h,ally.getAttributeValue(Attributes.MOVEMENT_SPEED),.2875,"One +15 percent speed modifier");
            ally.interruptAttack(40);a.discard();b.discard();
            h.runAfterDelay(21,()->h.assertTrue(ally.skillPhase()==AttackState.IDLE,"Control lasts twenty, not forty ticks"));
            h.runAfterDelay(45,()->{equal(h,ally.getAttributeValue(Attributes.ATTACK_DAMAGE),5,"Aura expires after banners leave");h.succeed();});
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30,batch="army")
    public static void bannerSlamHasOneCircleContact(GameTestHelper h){
        arena(h);var mob=actor(h,BlueprintEntities.ZHENWANG_ZHANGQIGUAN.get(),6,6);Cow front=target(h,6,8),side=target(h,8,6),outside=target(h,11,6);
        h.assertTrue(mob.startSkill(ArmySkills.SLAM,front),"Start banner slam");
        h.runAfterDelay(15,()->equal(h,front.getHealth(),200,"No warning damage"));
        h.runAfterDelay(25,()->{h.assertTrue(front.getHealth()<200&&side.getHealth()<200,"Circle hits front and side");equal(h,outside.getHealth(),200,"Bounded radius");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=45,batch="army")
    public static void armyReloadConsumesContactsAndDoesNotStackAura(GameTestHelper h){
        arena(h);var original=actor(h,BlueprintEntities.JUMA_CHANGQIANGBING.get(),6,5);var enemy=target(h,6,8);h.assertTrue(original.startSkill(ArmySkills.THRUST,enemy),"Start thrust");
        h.runAfterDelay(16,()->{var saved=new CompoundTag();original.addAdditionalSaveData(saved);original.discard();
            var copy=BlueprintEntities.JUMA_CHANGQIANGBING.get().create(h.getLevel());copy.readAdditionalSaveData(saved);copy.moveTo(original.position());h.getLevel().addFreshEntity(copy);
            h.runAfterDelay(18,()->{equal(h,enemy.getHealth(),195,"Restored consumed frame never hits again");h.succeed();});});
    }
    @GameTest(template="bow_ritual_test",batch="army")
    public static void gateSquadAndPendingBattlefieldSpawnsRemainBounded(GameTestHelper h){
        h.assertTrue(BlueprintSpawns.militaryMember(0)==BlueprintEntities.LUDUN_JIASHI.get()&&BlueprintSpawns.militaryMember(1)==BlueprintEntities.LIANNU_ZHENZU.get()
            &&BlueprintSpawns.militaryMember(2)==BlueprintEntities.LIANNU_ZHENZU.get()&&BlueprintSpawns.militaryMember(3)==BlueprintEntities.JUMA_CHANGQIANGBING.get(),"Gate uses authored four-member defensive squad");
        for(var def:TemplateContentDefinitions.ALL)if(def.id().equals("kuijun_sishi")||def.id().equals("zhenwang_zhangqiguan"))
            h.assertTrue(def.spawnWeight()==0&&def.spawnReason().contains("PENDING"),"No unsupported battlefield units scattered globally");
        h.assertTrue(ArmySkills.ALL.size()==10&&ArmySkills.ALL.stream().allMatch(s->s.impactTicks().stream().allMatch(t->s.phaseAt(t)==AttackState.ACTIVE)),"All ten server action contacts lie in ACTIVE");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=90,batch="army")
    public static void hookMissNeverPublishesOrPullsAnUnhitTarget(GameTestHelper h){
        arena(h);var mob=actor(h,BlueprintEntities.TIESUO_CHIHOU.get(),6,3);var enemy=target(h,6,13);Vec3 initial=mob.position();
        h.assertTrue(mob.startSkill(ArmySkills.GRAPPLE,enemy),"Start physical hook");
        h.runAfterDelay(14,()->enemy.setPos(enemy.position().add(5,0,0)));
        h.runAfterDelay(48,()->{h.assertTrue(mob.hookTargetId()<0&&mob.hookExpires()<0,"A missed claw never becomes a visual/physical link");
            equal(h,mob.position().distanceTo(initial),0,"Miss cannot pull the scout");equal(h,enemy.getHealth(),200,"No remote knee damage");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=90,batch="army")
    public static void wallInterceptsHookInFlightWithoutCreatingALink(GameTestHelper h){
        arena(h);var mob=actor(h,BlueprintEntities.TIESUO_CHIHOU.get(),6,3);var enemy=target(h,6,13);
        h.assertTrue(mob.startSkill(ArmySkills.GRAPPLE,enemy),"Hook begins with clear LOS");
        h.runAfterDelay(14,()->{for(int x=4;x<9;x++)for(int y=2;y<6;y++)h.setBlock(x,y,9,Blocks.STONE);});
        h.runAfterDelay(42,()->{h.assertTrue(mob.hookTargetId()<0&&mob.hookExpires()<0,"Block collision discards hook without attaching");
            h.assertTrue(h.getLevel().getEntitiesOfClass(TemplateProjectile.class,mob.getBoundingBox().inflate(14),p->p.getOwner()==mob).isEmpty(),"Intercepted hook removed");
            equal(h,enemy.getHealth(),200,"Cannot hit through wall");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=85,batch="army")
    public static void loadedHookResolvesCurrentTargetAndExpiresWithoutReplay(GameTestHelper h){
        arena(h);var mob=actor(h,BlueprintEntities.TIESUO_CHIHOU.get(),6,3);var enemy=target(h,6,13);
        h.assertTrue(mob.startSkill(ArmySkills.GRAPPLE,enemy),"Start hook before reload");
        h.runAfterDelay(27,()->{
            h.assertTrue(mob.hookTargetId()==enemy.getId()&&mob.hookExpires()>h.getLevel().getGameTime(),"Real collision published actual entity and expiry");
            var saved=new CompoundTag();mob.addAdditionalSaveData(saved);long expiry=mob.hookExpires();mob.discard();
            var copy=BlueprintEntities.TIESUO_CHIHOU.get().create(h.getLevel());copy.readAdditionalSaveData(saved);copy.moveTo(mob.position());copy.setNoAi(true);copy.setNoGravity(true);h.getLevel().addFreshEntity(copy);
            h.runAfterDelay(3,()->h.assertTrue(copy.hookTargetId()==enemy.getId()&&copy.hookExpires()==expiry,"Loaded UUID resolves current target without restarting expiry"));
            h.runAfterDelay(40,()->{h.assertTrue(copy.hookTargetId()<0&&copy.hookExpires()<0,"Restored chain always clears on expiry or action finish");equal(h,enemy.getHealth(),200,"Reload cannot manufacture a contact");h.succeed();});
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=110,batch="army")
    public static void autonomousPairedCrossbowsStaggerTheirRealVolleyStarts(GameTestHelper h){
        arena(h);var shield=actor(h,BlueprintEntities.LUDUN_JIASHI.get(),8,8);var left=actor(h,BlueprintEntities.LIANNU_ZHENZU.get(),6,5);
        var right=actor(h,BlueprintEntities.LIANNU_ZHENZU.get(),10,5);var enemy=target(h,8,13);long[] first={-1,-1};var owners=new HashSet<UUID>();
        left.setNoAi(false);right.setNoAi(false);left.setNoGravity(false);right.setNoGravity(false);left.setTarget(enemy);right.setTarget(enemy);
        h.onEachTick(()->{
            if(first[0]<0&&left.skillId()==ArmySkills.VOLLEY)first[0]=left.skillStartTime();
            if(first[1]<0&&right.skillId()==ArmySkills.VOLLEY)first[1]=right.skillStartTime();
            h.getLevel().getEntitiesOfClass(TemplateProjectile.class,shield.getBoundingBox().inflate(14),p->p.armyMode()==1&&p.getOwner()!=null)
                .forEach(p->owners.add(p.getOwner().getUUID()));
        });
        h.runAfterDelay(75,()->{
            h.assertTrue(first[0]>=0&&first[1]>=0&&Math.abs(first[0]-first[1])>=6,"Both actual CombatGoals start volleys at staggered times");
            h.assertTrue(owners.contains(left.getUUID())&&owners.contains(right.getUUID()),"Both autonomous soldiers create their own physical bolts");
            h.assertTrue(enemy.getHealth()<200,"Unscripted volleys really collide and deal damage");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=35,batch="army")
    public static void kneeUsesItsOwnArrivalClockAndHasOneContact(GameTestHelper h){
        arena(h);var mob=actor(h,BlueprintEntities.TIESUO_CHIHOU.get(),6,6);var enemy=target(h,6,8);
        h.assertTrue(mob.startSkill(ArmySkills.KNEE,enemy),"Separate arrival animation accepted");
        h.runAfterDelay(4,()->equal(h,enemy.getHealth(),200,"No instantaneous arrival damage before visible knee"));
        h.runAfterDelay(9,()->{equal(h,enemy.getHealth(),195.2,"One 1.2x knee at its sixth frame");h.assertTrue(mob.visualAnimation().equals("knee"),"Arrival selects actual independent knee clip");});
        h.runAfterDelay(25,()->{equal(h,enemy.getHealth(),195.2,"Knee recovery cannot hit again");h.succeed();});
    }

    /** Passive target only: production goal, navigation, gravity and attack clocks remain enabled. */
    private static void autonomousContact(GameTestHelper h,EntityType<TemplateMob> type,int expectedSkill,boolean detonation){
        arena(h);
        for(int x=2;x<=5;x++)for(int y=2;y<=5;y++)h.setBlock(x,y,8,Blocks.STONE);
        var mob=h.spawn(type,new BlockPos(3,2,3));mob.setPersistenceRequired();
        h.assertTrue(!mob.isNoAi()&&!mob.isNoGravity(),"Subject must retain real AI and gravity");
        var enemy=target(h,3,13);var initial=mob.position();
        boolean[] routed={false},selected={false},sprinted={false};
        mob.setTarget(enemy); // Never call startSkill or push/teleport the subject in this fixture.
        h.onEachTick(()->{
            if(Math.abs(mob.getX()-initial.x)>1.2)routed[0]=true;
            if(mob.skillId()==expectedSkill)selected[0]=true;
            if(mob.isSprinting())sprinted[0]=true;
        });
        h.startSequence().thenWaitUntil(()->h.assertTrue(enemy.getHealth()<200&&(!detonation||mob.isDeadOrDying()),
                "Waiting for autonomous contact: "+mob.blueprintId()+" position="+mob.position()+" skill="+mob.skillId()
                +" sight="+mob.hasLineOfSight(enemy)+" health="+enemy.getHealth()+" path="+mob.getNavigation().getPath()))
            .thenExecute(()->{
                h.assertTrue(routed[0]&&mob.position().distanceToSqr(initial)>16,"Physically route around a four-block obstruction");
                h.assertTrue(selected[0],"Real CombatGoal chose its own authored action: "+expectedSkill);
                h.assertTrue(!mob.isNoAi()&&!mob.isNoGravity(),"No hidden AI, gravity or speed fixture substitution");
                if(detonation)h.assertTrue(sprinted[0],"Powder unit actually sprinted before its proximity fuse");
                trace(h,"autonomous "+mob.blueprintId(),mob,enemy);
                var owners=java.util.Set.of(mob.getUUID(),enemy.getUUID());
                for(var projectile:h.getLevel().getEntitiesOfClass(TemplateProjectile.class,mob.getBoundingBox().inflate(16),
                        p->p.getOwner()!=null&&owners.contains(p.getOwner().getUUID())))projectile.discard();
                mob.discard();enemy.discard();
            }).thenSucceed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=360,batch="army_autonomy")
    public static void spearAutonomouslyRoutesAroundObstructionAndThrusts(GameTestHelper h){
        autonomousContact(h,BlueprintEntities.JUMA_CHANGQIANGBING.get(),ArmySkills.THRUST,false);
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=360,batch="army_autonomy")
    public static void scoutAutonomouslyFlanksAndCutsWithoutForcedHook(GameTestHelper h){
        autonomousContact(h,BlueprintEntities.TIESUO_CHIHOU.get(),ArmySkills.CUT,false);
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=360,batch="army_autonomy")
    public static void powderAutonomouslySprintsClosesAndCompletesFuse(GameTestHelper h){
        autonomousContact(h,BlueprintEntities.KUIJUN_SISHI.get(),ArmySkills.DETONATE,true);
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=360,batch="army_autonomy")
    public static void bannerAutonomouslyRoutesAndSlams(GameTestHelper h){
        autonomousContact(h,BlueprintEntities.ZHENWANG_ZHANGQIGUAN.get(),ArmySkills.SLAM,false);
    }
}
