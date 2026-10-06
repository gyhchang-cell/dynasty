package com.dynasty.blueprint;

import com.dynasty.Dynasty;
import com.dynasty.blueprint.combat.Combatant;
import com.dynasty.blueprint.combat.Faction;
import com.dynasty.blueprint.combat.MobRole;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.world.Difficulty;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

import java.util.ArrayList;
import java.util.List;

/** Real production goals choose paths, support targets and skills; no authored action is forced.
 * Only passive cow fixtures have NoAI. Each tested TemplateMob retains AI, gravity and base speed.
 * Seeding one enemy tests combat autonomy, not player-discovery/NearestAttackableTargetGoal.
 */
@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public final class BlueprintAutonomyGameTests {
    private BlueprintAutonomyGameTests() { }

    private static void arena(GameTestHelper h) {
        h.assertTrue(h.getLevel().getDifficulty() != Difficulty.PEACEFUL,
                "Autonomy fixtures require non-peaceful difficulty; do not change the shared server difficulty");
        // bow_ritual_test is exactly 16 x 14 x 16. Never edit neighbouring test footprints.
        // Six-block perimeter walls hide neighbouring factions and cannot be selected by the
        // shanxiao's initial 2..5-block high-ground scan; its intended platform is only 3 high.
        for (int x = 0; x < 16; x++) for (int z = 0; z < 16; z++) {
            h.setBlock(x, 1, z, Blocks.STONE);
            for (int y = 2; y < 14; y++)
                // Keep natural falling overburden outside the arena, without changing mob physics.
                h.setBlock(x, y, z, y == 13 || y <= 7 && (x == 0 || x == 15 || z == 0 || z == 15)
                        ? Blocks.STONE : Blocks.AIR);
        }
    }

    private static TemplateMob actor(GameTestHelper h, EntityType<TemplateMob> type, int x, int z) {
        TemplateMob mob = h.spawn(type, new BlockPos(x, 2, z));
        h.assertTrue(!mob.isNoAi() && !mob.isNoGravity(), "Subject must retain production AI and gravity");
        return mob;
    }

    private static <T extends Cow> T passive(GameTestHelper h, T cow, int x, int z) {
        cow.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(x, 2, z))));
        cow.setNoAi(true); // The subject is never disabled; stationary fixtures make geometry repeatable.
        cow.setPersistenceRequired();
        cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);
        cow.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);
        cow.setHealth(200);
        h.assertTrue(h.getLevel().addFreshEntity(cow), "Passive fixture must be added to the level");
        return cow;
    }

    private static Cow enemy(GameTestHelper h, int x, int z) {
        return passive(h, new Cow(EntityType.COW, h.getLevel()), x, z);
    }

    private static void climbingPlatform(GameTestHelper h) {
        // Three-block vertical face, no steps/vines/ladder. The top cannot be reached by a normal step.
        for (int x = 2; x <= 6; x++) for (int z = 5; z <= 7; z++)
            for (int y = 2; y <= 4; y++) h.setBlock(x, y, z, Blocks.STONE);
    }

    private static void assertRealClimbContact(GameTestHelper h, TemplateMob beast) {
        h.assertTrue(beast.climbFace() != null, "Actual wall climbing must publish a horizontal contact face");
        h.assertTrue(beast.climbContactDistance() > 0
                        && beast.climbContactDistance() <= beast.getBbWidth() / 2 + .18,
                "Published claw contact must be on the nearby actual wall; distance=" + beast.climbContactDistance());
        h.assertTrue(beast.climbStartTime() > 0, "Climbing publishes a real server start clock");
    }

    private static Arrow movingArrow(GameTestHelper h, TemplateMob shield, Cow owner, boolean frontal) {
        Vec3 towardEnemy = owner.position().subtract(shield.position()).multiply(1, 0, 1).normalize();
        Vec3 side = towardEnemy.scale(frontal ? 1 : -1);
        Arrow arrow = new Arrow(h.getLevel(), owner);
        arrow.setPos(shield.position().add(side.scale(1.2)).add(0, 1, 0));
        arrow.setDeltaMovement(side.scale(-1.8));
        arrow.setBaseDamage(8);
        arrow.setNoGravity(true);
        h.assertTrue(h.getLevel().addFreshEntity(arrow), "Add an actual moving directional arrow");
        return arrow;
    }

    private static void cleanup(GameTestHelper h, Entity... fixtures) {
        // Touch only this test's entities/projectiles, not a global kill selector or neighbouring mobs.
        var owners = java.util.Arrays.stream(fixtures).map(Entity::getUUID).collect(java.util.stream.Collectors.toSet());
        AABB bounds = new AABB(h.absolutePos(BlockPos.ZERO), h.absolutePos(new BlockPos(16, 14, 16)));
        for (var projectile : h.getLevel().getEntitiesOfClass(TemplateProjectile.class, bounds,
                p -> p.getOwner() != null && owners.contains(p.getOwner().getUUID()))) projectile.discard();
        for (Entity fixture : fixtures) fixture.discard();
    }

    private record Contact(long time, long actionStart, int skill, float healthLost) { }
    private static final class RecordingCow extends Cow {
        final List<Contact> contacts = new ArrayList<>();
        TemplateMob watched;
        RecordingCow(GameTestHelper h) { super(EntityType.COW, h.getLevel()); }
        @Override public boolean hurt(DamageSource source, float amount) {
            float before = getHealth();
            boolean accepted = super.hurt(source, amount);
            if (accepted && source.getEntity() == watched)
                contacts.add(new Contact(level().getGameTime(), watched.skillStartTime(), watched.skillId(), before - getHealth()));
            return accepted;
        }
    }

    private static final class BacklineCow extends Cow implements Combatant {
        BacklineCow(GameTestHelper h) { super(EntityType.COW, h.getLevel()); }
        @Override public Faction faction() { return Faction.DYNASTY_ARMY; }
        @Override public MobRole role() { return MobRole.SUPPORT; }
    }

    @GameTest(template="bow_ritual_test", batch="blueprint_autonomy", timeoutTicks=120)
    public static void priestPrioritizesTheAssaultFrontPowderUnit(GameTestHelper h) {
        arena(h);
        var priest = actor(h, BlueprintEntities.FUFA_JIJIU.get(), 8, 5);
        var strongest = actor(h, BlueprintEntities.ZUWU_DAOSHOU.get(), 6, 7);
        var front = actor(h, BlueprintEntities.KUIJUN_SISHI.get(), 8, 9);
        var rear = actor(h, BlueprintEntities.KUIJUN_SISHI.get(), 11, 6);
        var target = enemy(h, 8, 13);
        strongest.getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(18);
        priest.setTarget(target); front.setTarget(target); rear.setTarget(target);
        h.startSequence().thenWaitUntil(() -> h.assertTrue(front.isPossessed(),
                "The assault formation must strengthen its foremost powder unit"))
            .thenExecute(() -> {
                h.assertTrue(priest.buffTargetId() == front.getId(), "Actual cast links the front unit");
                h.assertTrue(!strongest.isPossessed() && !rear.isPossessed(), "One front unit, not the strongest generic ally");
                h.assertTrue(!priest.isNoAi() && !front.isNoAi(), "Production AI selected and cast the skill");
                cleanup(h, priest, strongest, front, rear, target);
            }).thenSucceed();
    }

    @GameTest(template="bow_ritual_test", batch="blueprint_autonomy", timeoutTicks=300)
    public static void swordAutonomouslyRoutesAroundWallAndLandsBothContacts(GameTestHelper h) {
        arena(h);
        // A two-block-high, three-block-wide obstruction cannot be stepped over.
        for (int x = 2; x <= 4; x++) for (int y = 2; y <= 3; y++) h.setBlock(x, y, 8, Blocks.STONE);
        TemplateMob sword = actor(h, BlueprintEntities.ZUWU_DAOSHOU.get(), 3, 4);
        RecordingCow target = passive(h, new RecordingCow(h), 3, 12);
        target.watched = sword;
        Vec3 initial = sword.position();
        boolean[] routed = {false};
        sword.setTarget(target); // Only seed an enemy; CombatGoal must choose and begin its own combo.
        h.onEachTick(() -> {
            h.assertTrue(sword.isAlive() && !sword.isNoAi(), "Autonomous swordsman must stay active");
            if (Math.abs(sword.getX() - initial.x) > 1.2) routed[0] = true;
        });
        h.startSequence().thenWaitUntil(() -> h.assertTrue(target.contacts.size() >= 2,
                "Waiting for two real AI-selected sword contacts; target=" + sword.getTarget()
                        + ", position=" + sword.position() + ", skill=" + sword.skillId()))
            .thenExecute(() -> {
                h.assertTrue(routed[0] && sword.position().distanceToSqr(initial) > 16,
                        "Sword must actually route around the wall and close distance");
                h.assertTrue(target.contacts.size() == 2, "Exactly two contacts in the first observed combo");
                Contact first = target.contacts.get(0), second = target.contacts.get(1);
                h.assertTrue(first.skill == TemplateSkills.SWORD_COMBO && second.skill == first.skill
                                && first.actionStart == second.actionStart,
                        "Both contacts belong to one naturally selected combo, not two later attempts");
                h.assertTrue(first.time - first.actionStart == 12 && second.time - second.actionStart == 22,
                        "Autonomous contact times are the authored 12/22 ticks");
                h.assertTrue(first.healthLost > 0 && second.healthLost > 0, "Both contacts must cause actual health loss");
                cleanup(h, sword, target);
            }).thenSucceed();
    }

    @GameTest(template="bow_ritual_test", batch="blueprint_autonomy", timeoutTicks=350)
    public static void shieldAutonomouslyProtectsNearestReachableBacklineBeyondEightBlocks(GameTestHelper h) {
        arena(h);
        TemplateMob shield = actor(h, BlueprintEntities.LUDUN_JIASHI.get(), 3, 7);
        Cow target = enemy(h, 3, 14);
        BacklineCow nearest = passive(h, new BacklineCow(h), 12, 2);
        BacklineCow farther = passive(h, new BacklineCow(h), 14, 5);
        h.assertTrue(shield.distanceToSqr(nearest) > 64 && shield.distanceToSqr(nearest) <= 144
                        && shield.distanceToSqr(farther) > shield.distanceToSqr(nearest)
                        && shield.distanceToSqr(farther) <= 144,
                "Both allies must begin outside the old 8-block radius but inside 12; nearest is unambiguous");
        Vec3 initial = shield.position();
        Vec3 intercept = nearest.position().add(target.position().subtract(nearest.position()).normalize().scale(1.8));
        Vec3 wrongIntercept = farther.position().add(target.position().subtract(farther.position()).normalize().scale(1.8));
        boolean[] usedReachableCoverPath = {false};
        shield.setTarget(target);
        for(int diagnosticTick:new int[]{1,2,5,10,20,40})h.runAfterDelay(diagnosticTick,()->{
            Vec3 forward=target.position().subtract(shield.position()).multiply(1,0,1).normalize();
            for(var ally:List.of(nearest,farther))Dynasty.LOGGER.info("[blueprint-cover-candidate] tick={} shield={} ally={} alive={} distance={} rearDot={} sight={} contained={} role={} cover={} pathTarget={}",
                diagnosticTick,shield.position(),ally.position(),ally.isAlive(),shield.distanceToSqr(ally),
                ally.position().subtract(shield.position()).dot(forward),shield.hasLineOfSight(ally),
                shield.getBoundingBox().inflate(12).intersects(ally.getBoundingBox()),ally.role(),shield.isCoveringBackline(),
                shield.getNavigation().getPath()==null?"none":shield.getNavigation().getPath().getTarget());
        });
        h.onEachTick(() -> {
            var path = shield.getNavigation().getPath();
            if (path != null && path.canReach()
                    && Vec3.atBottomCenterOf(path.getTarget()).distanceToSqr(intercept) < 1.3)
                usedReachableCoverPath[0] = true;
        });
        // Bounded evidence for Forge's fractional-width waypoint boundary; do not offset the spawn
        // or relax the movement assertion, since production structure spawns also use block centers.
        for (int diagnosticTick : new int[]{20, 180}) h.runAfterDelay(diagnosticTick, () -> {
            var path = shield.getNavigation().getPath();
            var move = shield.getMoveControl();
            float width = shield.getBbWidth();
            float waypointLimit = width > .75F ? width / 2F : .75F - width / 2F;
            double forgeCenterOffset = (width + 1) / 2D;
            double halfBlockDelta = forgeCenterOffset - .5D;
            double pathCenterOffset = (int) (width + 1F) * .5D;
            String node = path == null || path.isDone() ? "none/done"
                    : path.getNextNodePos() + ", entityPos=" + path.getNextEntityPos(shield)
                    + ", forgeDeltaX=" + Math.abs(shield.getX() - (path.getNextNodePos().getX() + forgeCenterOffset))
                    + ", forgeDeltaZ=" + Math.abs(shield.getZ() - (path.getNextNodePos().getZ() + forgeCenterOffset));
            Dynasty.LOGGER.info("[blueprint-autonomy-cover] tick={} width={} position={} nextIndex={} node={} "
                            + "speed={} zza={} wanted={} hasWanted={} phase={} skill={} onGround={} "
                            + "waypointLimit={} forgeHalfBlockDelta={} boundaryExcess={} pathCenterOffset={}",
                    diagnosticTick, width, shield.position(), path == null ? -1 : path.getNextNodeIndex(), node,
                    shield.getSpeed(), shield.zza, new Vec3(move.getWantedX(), move.getWantedY(), move.getWantedZ()),
                    move.hasWanted(), shield.skillPhase(), shield.skillId(), shield.onGround(), waypointLimit,
                    halfBlockDelta, halfBlockDelta - waypointLimit, pathCenterOffset);
        });
        h.startSequence().thenWaitUntil(() -> h.assertTrue(shield.position().distanceToSqr(intercept) < 1.44,
                "Waiting for real cover movement to nearest ally's intercept; shield=" + shield.position()
                        + ", desired=" + intercept + ", path=" + shield.getNavigation().getPath()))
            .thenExecute(() -> {
                h.assertTrue(!shield.isNoAi() && usedReachableCoverPath[0], "Production AI must choose a reachable cover path");
                h.assertTrue(shield.position().distanceToSqr(initial) > 16, "Shield must physically move, not merely name an ally");
                h.assertTrue(shield.position().distanceToSqr(wrongIntercept) > 4,
                        "Shield must protect the nearest ally, not the farther valid ally");
            }).thenIdle(90).thenExecute(()->{
                h.assertTrue(shield.isAlive()&&!shield.isNoAi(),"Guard retains active production AI");
                h.assertTrue(shield.position().distanceToSqr(intercept)<2.25,
                    "Guard must hold its reached cover point, not chase away during a scan boundary; at="+shield.position());
                // Moving the passive enemy is the input to this second case; never
                // force the shield's skill/path/velocity. The guard must decide to counter.
                target.setPos(shield.position().add(0,0,2));
            }).thenWaitUntil(()->h.assertTrue(target.getHealth()<200,
                "A close enemy must trigger the real shield contact despite an active cover plan"))
            .thenExecute(()->cleanup(h,shield,target,nearest,farther)).thenSucceed();
    }

    @GameTest(template="bow_ritual_test", batch="blueprint_autonomy", timeoutTicks=260)
    public static void priestAutonomouslyChoosesHighestAttackLegalAlly(GameTestHelper h) {
        arena(h);
        TemplateMob priest = actor(h, BlueprintEntities.FUFA_JIJIU.get(), 8, 9);
        TemplateMob weaker = actor(h, BlueprintEntities.ZUWU_DAOSHOU.get(), 6, 7);
        TemplateMob strongest = actor(h, BlueprintEntities.LUDUN_JIASHI.get(), 10, 7);
        TemplateMob enemyBeast = actor(h, BlueprintEntities.SHANJING_SHANXIAO.get(), 12, 10);
        weaker.getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(6);
        strongest.getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(18);
        enemyBeast.getAttribute(Attributes.ATTACK_DAMAGE).setBaseValue(99);
        Cow target = enemy(h, 8, 13);
        boolean[] choseBuff = {false};
        priest.setTarget(target);
        h.onEachTick(() -> {
            if (priest.skillId() == TemplateSkills.POSSESSION) choseBuff[0] = true;
        });
        h.startSequence().thenWaitUntil(() -> h.assertTrue(strongest.hasEffect(BlueprintEntities.BINGSHA_POSSESSION.get()),
                "Waiting for automatic highest-attack ally possession; skill=" + priest.skillId()
                        + ", linked=" + priest.buffTargetId()))
            .thenExecute(() -> {
                h.assertTrue(choseBuff[0] && !priest.isNoAi(), "Priest must autonomously select and cast its buff");
                h.assertTrue(priest.buffTargetId() == strongest.getId() && strongest.isPossessed(),
                        "Authoritative visual link and possession metadata identify the strongest legal ally");
                h.assertTrue(!weaker.hasEffect(BlueprintEntities.BINGSHA_POSSESSION.get())
                                && !enemyBeast.hasEffect(BlueprintEntities.BINGSHA_POSSESSION.get()),
                        "Do not strengthen weaker allies or the higher-attack enemy faction");
                cleanup(h, priest, weaker, strongest, enemyBeast, target);
            }).thenSucceed();
    }

    @GameTest(template="bow_ritual_test", batch="blueprint_autonomy", timeoutTicks=300)
    public static void shieldMaintainsFrontalArrowGuardWhileReallySidesteppingToCover(GameTestHelper h) {
        arena(h);
        TemplateMob shield = actor(h, BlueprintEntities.LUDUN_JIASHI.get(), 3, 7);
        Cow target = enemy(h, 3, 14);
        BacklineCow backline = passive(h, new BacklineCow(h), 12, 2);
        Vec3 initial = shield.position();
        Vec3[] probePosition = {Vec3.ZERO};
        Arrow[] arrows = new Arrow[2];
        float[] healthBefore = {0};
        boolean[] probing = {false};
        shield.setTarget(target);
        h.onEachTick(() -> {
            if (!probing[0]) return;
            Vec3 towardEnemy = target.position().subtract(shield.position()).multiply(1, 0, 1).normalize();
            h.assertTrue(shield.isCoveringBackline() && !shield.isNoAi() && !shield.isNoGravity(),
                    "The directional probes must happen during actual autonomous cover movement; pos="
                            + shield.position() + ", probe=" + probePosition[0] + ", target=" + shield.getTarget()
                            + ", skill=" + shield.skillId() + ", phase=" + shield.skillPhase()
                            + ", pathDone=" + shield.getNavigation().isDone() + ", age=" + shield.tickCount);
            h.assertTrue(shield.getLookAngle().multiply(1, 0, 1).normalize().dot(towardEnemy) > .95,
                    "The real defensive yaw, not just head/body rendering, must remain enemy-facing");
        });
        h.startSequence().thenWaitUntil(() -> h.assertTrue(shield.isCoveringBackline()
                        && shield.position().distanceToSqr(initial) > 1
                        && Math.abs(shield.xxa) > .04 && Math.abs(shield.xxa) > Math.abs(shield.zza)
                        && shield.getDeltaMovement().horizontalDistanceSqr() > .0001,
                "Waiting for real lateral input and displacement along the reachable cover path; position="
                        + shield.position() + ", input=" + shield.xxa + "/" + shield.zza))
            .thenExecute(() -> {
                probing[0] = true;
                probePosition[0] = shield.position();
                healthBefore[0] = shield.getHealth();
                arrows[0] = movingArrow(h, shield, target, true);
            })
            .thenExecuteAfter(3, () -> {
                h.assertTrue(arrows[0].isRemoved(), "A real arrow approaching from the enemy side must hit and be consumed");
                h.assertTrue(shield.getHealth() == healthBefore[0], "Front arrow cannot deal damage during the sidestep");
                shield.invulnerableTime = 0;
                arrows[1] = movingArrow(h, shield, target, false);
            })
            .thenExecuteAfter(3, () -> {
                h.assertTrue(shield.getHealth() < healthBefore[0], "Real rear arrow must still damage the moving shield");
                h.assertTrue(shield.position().distanceToSqr(probePosition[0]) > .01,
                        "Do not pass by freezing the subject while checking directional damage");
                probing[0] = false;
                cleanup(h, shield, target, backline, arrows[0], arrows[1]);
            }).thenSucceed();
    }

    @GameTest(template="bow_ritual_test", batch="blueprint_autonomy", timeoutTicks=400)
    public static void shanxiaoAutonomouslyClimbsPlatformThenThrowsRock(GameTestHelper h) {
        arena(h);
        climbingPlatform(h);
        TemplateMob beast = actor(h, BlueprintEntities.SHANJING_SHANXIAO.get(), 4, 3);
        Cow target = enemy(h, 13, 13);
        double initialY = beast.getY();
        double[] peakY = {initialY};
        boolean[] climbed = {false}, threwFromHighGround = {false};
        beast.setTarget(target);
        AABB bounds = new AABB(h.absolutePos(BlockPos.ZERO), h.absolutePos(new BlockPos(16, 14, 16)));
        h.onEachTick(() -> {
            peakY[0] = Math.max(peakY[0], beast.getY());
            if (beast.onClimbable() && beast.getY() > initialY + .4) {
                assertRealClimbContact(h, beast);
                climbed[0] = true;
            }
            for (TemplateProjectile rock : h.getLevel().getEntitiesOfClass(TemplateProjectile.class, bounds,
                    p -> p.isRock() && p.getOwner() == beast)) {
                if (beast.skillId() == TemplateSkills.ROCK_THROW && beast.getY() >= initialY + 2
                        && beast.distanceTo(target) > 8 && beast.hasLineOfSight(target)) threwFromHighGround[0] = true;
            }
        });
        h.startSequence().thenWaitUntil(() -> h.assertTrue(threwFromHighGround[0],
                "Waiting for autonomous climb -> high-ground rock projectile; climbed=" + climbed[0]
                        + ", peakY=" + peakY[0] + ", position=" + beast.position() + ", skill=" + beast.skillId()))
            .thenExecute(() -> {
                h.assertTrue(!beast.isNoAi() && !beast.isNoGravity(), "No disabled AI, levitation fixture or direct skill start");
                h.assertTrue(climbed[0] && peakY[0] >= initialY + 2,
                        "Rock throw alone is insufficient: subject must first climb the actual vertical face");
                cleanup(h, beast, target);
            }).thenSucceed();
    }

    @GameTest(template="bow_ritual_test", batch="blueprint_autonomy", timeoutTicks=440)
    public static void shanxiaoFindsOnlyEvenOffsetSinglePillarThenClimbsAndThrows(GameTestHelper h) {
        arena(h);
        // Only one eligible elevated standing block: even offset (+2,0), off the direct enemy
        // route. The old odd-X/odd-Z scan never sees it while chasing straight along +Z.
        for (int y = 2; y <= 4; y++) h.setBlock(6, y, 3, Blocks.STONE);
        TemplateMob beast = actor(h, BlueprintEntities.SHANJING_SHANXIAO.get(), 4, 3);
        Cow target = enemy(h, 4, 14);
        double initialY = beast.getY();
        BlockPos summit = h.absolutePos(new BlockPos(6, 5, 3));
        boolean[] climbed = {false}, stoodOnOnlySummit = {false}, threw = {false};
        double[] peakY = {initialY};
        AABB bounds = new AABB(h.absolutePos(BlockPos.ZERO), h.absolutePos(new BlockPos(16, 14, 16)));
        beast.setTarget(target);
        h.onEachTick(() -> {
            peakY[0] = Math.max(peakY[0], beast.getY());
            if (beast.onClimbable() && beast.getY() > initialY + .4) {
                assertRealClimbContact(h, beast);
                climbed[0] = true;
            }
            boolean overPillar = beast.getX() >= summit.getX() && beast.getX() < summit.getX() + 1
                    && beast.getZ() >= summit.getZ() && beast.getZ() < summit.getZ() + 1;
            if (climbed[0] && overPillar && beast.onGround() && beast.getY() >= initialY + 2.9)
                stoodOnOnlySummit[0] = true;
            if (stoodOnOnlySummit[0] && overPillar && beast.getY() >= initialY + 2.9
                    && beast.skillId() == TemplateSkills.ROCK_THROW && beast.distanceTo(target) > 8) {
                threw[0] |= !h.getLevel().getEntitiesOfClass(TemplateProjectile.class, bounds,
                        p -> p.isRock() && p.getOwner() == beast).isEmpty();
            }
        });
        // Bounded diagnostics distinguish losing the summit goal mid-climb from a blocked
        // waypoint or WallClimberNavigation's integer-corner fallback. No fixture changes.
        for (int tick : new int[]{10, 20, 30, 40, 60, 100, 200}) h.runAfterDelay(tick, () -> {
            var path = beast.getNavigation().getPath();
            var move = beast.getMoveControl();
            String node = path == null || path.isDone() ? "none/done" : path.getNextEntityPos(beast).toString();
            Dynasty.LOGGER.info("[blueprint-autonomy-pillar] tick={} position={} peakY={} summit={} stood={} "
                            + "ground={} climbing={} face={} contact={} skill={} pathTarget={} nextIndex={} next={} "
                            + "wanted={} velocity={}",
                    tick, beast.position(), peakY[0], summit, stoodOnOnlySummit[0], beast.onGround(), beast.onClimbable(),
                    beast.climbFace(), beast.climbContactDistance(), beast.skillId(), path == null ? "none" : path.getTarget(),
                    path == null ? -1 : path.getNextNodeIndex(), node,
                    new Vec3(move.getWantedX(), move.getWantedY(), move.getWantedZ()), beast.getDeltaMovement());
        });
        h.startSequence().thenWaitUntil(() -> h.assertTrue(threw[0],
                "Waiting for autonomous even-offset single-pillar climb, real summit support, then rock; climbed="
                        + climbed[0] + ", summit=" + stoodOnOnlySummit[0] + ", peakY=" + peakY[0] + ", position=" + beast.position()
                        + ", skill=" + beast.skillId()))
            .thenExecute(() -> {
                h.assertTrue(climbed[0] && stoodOnOnlySummit[0] && !beast.isNoAi() && !beast.isNoGravity(),
                        "Finding a coordinate or casting from the ground cannot substitute for real pillar traversal");
                cleanup(h, beast, target);
            }).thenSucceed();
    }

    @GameTest(template="bow_ritual_test", batch="blueprint_autonomy", timeoutTicks=300)
    public static void shanxiaoKilledDuringRealClimbReleasesWallAndFalls(GameTestHelper h) {
        arena(h);
        climbingPlatform(h);
        TemplateMob beast = actor(h, BlueprintEntities.SHANJING_SHANXIAO.get(), 4, 3);
        Cow target = enemy(h, 13, 13);
        double initialY = beast.getY();
        double[] deathY = {Double.NaN};
        beast.setTarget(target);
        h.startSequence().thenWaitUntil(() -> h.assertTrue(beast.onClimbable() && !beast.onGround()
                        && beast.getY() > initialY + 1.5,
                "Waiting for real airborne wall climb before lethal damage; position=" + beast.position()
                        + ", onClimbable=" + beast.onClimbable()))
            .thenExecute(() -> {
                assertRealClimbContact(h, beast);
                deathY[0] = beast.getY();
                beast.hurt(beast.damageSources().genericKill(), 10000);
                h.assertTrue(beast.isDeadOrDying(), "Lethal damage must enter the real death lifecycle");
                h.assertTrue(!beast.onClimbable(), "Death must release wall attachment immediately");
                h.assertTrue(beast.climbFace() == null && beast.climbStartTime() == -1,
                        "Death must clear synchronized wall face and climb animation clock");
                h.assertTrue(!beast.isNoGravity(), "Falling corpse retains normal gravity");
            })
            .thenExecuteAfter(10, () -> {
                h.assertTrue(!beast.isRemoved() && beast.isDeadOrDying(), "Observe the corpse before its 44-tick removal");
                h.assertTrue(!beast.onClimbable(), "Wall attachment must not return during death physics");
                h.assertTrue(beast.climbFace() == null && beast.climbStartTime() == -1,
                        "Death physics must not republish the wall-contact synchronization state");
                h.assertTrue(beast.getY() < deathY[0] - .5,
                        "Corpse must fall under normal physics; deathY=" + deathY[0] + ", currentY=" + beast.getY());
                cleanup(h, beast, target);
            }).thenSucceed();
    }
}
