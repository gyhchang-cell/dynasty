package com.dynasty.blueprint;

import com.dynasty.Dynasty;
import com.dynasty.blueprint.combat.AttackState;
import com.dynasty.blueprint.combat.Combatant;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

/** Server integration tests exercise real entity ticks, damage events, reload data and projectile collision. */
@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public final class BlueprintTemplateGameTests {
    private BlueprintTemplateGameTests() { }

    private static TemplateMob mob(GameTestHelper h, EntityType<TemplateMob> type, int x, int z) {
        TemplateMob mob = h.spawn(type, new BlockPos(x, 2, z));
        mob.setNoAi(true); mob.setNoGravity(true); mob.setPersistenceRequired();
        return mob;
    }
    private static Cow victim(GameTestHelper h, int x, int z) {
        Cow cow = h.spawn(EntityType.COW, new BlockPos(x, 2, z));
        cow.setNoAi(true); cow.setNoGravity(true);
        cow.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);
        cow.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);
        cow.setHealth(200);
        return cow;
    }
    private static void equal(GameTestHelper h, double actual, double expected, String label) {
        h.assertTrue(Math.abs(actual - expected) < .001, label + ": expected=" + expected + ", actual=" + actual);
    }

    @GameTest(template="bow_ritual_test", timeoutTicks=50)
    public static void swordHitsOnlyOnTwoAuthoredFramesAndIgnoresAlly(GameTestHelper h) {
        TemplateMob sword = mob(h, BlueprintEntities.ZUWU_DAOSHOU.get(), 5, 5);
        Cow enemy = victim(h, 5, 7);
        TemplateMob ally = mob(h, BlueprintEntities.FUFA_JIJIU.get(), 6, 7);
        float allyHealth = ally.getHealth();
        h.assertTrue(Combatant.allied(sword, ally), "The army faction must recognize its priest");
        h.assertTrue(sword.startSkill(TemplateSkills.SWORD_COMBO, enemy), "Sword must accept valid target");
        h.runAfterDelay(10, () -> equal(h, enemy.getHealth(), 200, "No windup damage"));
        h.runAfterDelay(14, () -> equal(h, enemy.getHealth(), 195, "First contact at tick 12"));
        h.runAfterDelay(20, () -> equal(h, enemy.getHealth(), 195, "No per-tick repeated contact"));
        h.runAfterDelay(25, () -> equal(h, enemy.getHealth(), 190, "Second contact at tick 22"));
        h.runAfterDelay(39, () -> {
            equal(h, enemy.getHealth(), 190, "No damage in recovery");
            equal(h, ally.getHealth(), allyHealth, "Area attacks never damage the priest");
            h.assertTrue(sword.skillPhase() == AttackState.IDLE, "Action returns to idle"); h.succeed();
        });
    }

    @GameTest(template="bow_ritual_test", timeoutTicks=30)
    public static void shieldProtectsFrontButExposesBack(GameTestHelper h) {
        TemplateMob shield = mob(h, BlueprintEntities.LUDUN_JIASHI.get(), 6, 6);
        shield.getAttribute(Attributes.ARMOR).setBaseValue(0); shield.setYRot(0); shield.setXRot(0);
        Cow attacker = victim(h, 6, 9);
        float initial = shield.getHealth();
        shield.hurt(shield.damageSources().mobAttack(attacker), 10);
        double baseMitigation = 1-com.dynasty.DynastyBalance.mobToughness(shield.getType());
        equal(h, initial - shield.getHealth(), 2*baseMitigation, "Front defense preserves existing Dynasty toughness pipeline");
        shield.invulnerableTime = 0;
        attacker.setPos(shield.position().add(0, 0, -3));
        initial = shield.getHealth();
        shield.hurt(shield.damageSources().mobAttack(attacker), 10);
        equal(h, initial - shield.getHealth(), 10*baseMitigation, "Rear melee bypasses the shield");
        shield.invulnerableTime = 0;
        Arrow front = new Arrow(h.getLevel(), attacker); front.setPos(shield.position().add(0, 1, 2));
        h.getLevel().addFreshEntity(front); initial = shield.getHealth();
        h.assertTrue(!shield.hurt(shield.damageSources().arrow(front, attacker), 12), "Front projectile damage is rejected");
        equal(h, shield.getHealth(), initial, "Front arrow cannot hurt");
        h.assertTrue(front.isRemoved(), "Blocked projectile is consumed");
        Arrow rear = new Arrow(h.getLevel(), attacker); rear.setPos(shield.position().add(0, 1, -2));
        h.getLevel().addFreshEntity(rear); shield.invulnerableTime = 0;
        h.assertTrue(shield.hurt(shield.damageSources().arrow(rear, attacker), 12), "Rear projectile can hurt");
        equal(h, initial - shield.getHealth(), 12*baseMitigation, "Rear arrow has no frontal reduction");
        rear.discard(); h.succeed();
    }

    @GameTest(template="bow_ritual_test", timeoutTicks=50)
    public static void interruptingWindupCancelsAllPendingContacts(GameTestHelper h) {
        TemplateMob sword = mob(h, BlueprintEntities.ZUWU_DAOSHOU.get(), 5, 5);
        Cow enemy = victim(h, 5, 7);
        h.assertTrue(sword.startSkill(TemplateSkills.SWORD_COMBO, enemy), "Start combo");
        h.runAfterDelay(5, () -> sword.hurt(sword.damageSources().mobAttack(enemy), 6));
        h.runAfterDelay(8, () -> h.assertTrue(sword.skillPhase() == AttackState.STUN, "A substantial windup hit causes stun"));
        h.runAfterDelay(30, () -> {
            equal(h, enemy.getHealth(), 200, "Interrupted animation cannot deal delayed hits");
            h.assertTrue(!sword.startSkill(TemplateSkills.SWORD_COMBO, enemy), "Interruption does not clear cooldown");
            h.succeed();
        });
    }

    @GameTest(template="bow_ritual_test", timeoutTicks=60)
    public static void reloadBetweenContactsDoesNotReplayDamage(GameTestHelper h) {
        TemplateMob sword = mob(h, BlueprintEntities.ZUWU_DAOSHOU.get(), 5, 5);
        Cow enemy = victim(h, 5, 7);
        h.assertTrue(sword.startSkill(TemplateSkills.SWORD_COMBO, enemy), "Start combo");
        CompoundTag saved = new CompoundTag();
        h.runAfterDelay(15, () -> {
            equal(h, enemy.getHealth(), 195, "First contact was committed before save");
            sword.addAdditionalSaveData(saved); sword.readAdditionalSaveData(saved);
        });
        h.runAfterDelay(26, () -> equal(h, enemy.getHealth(), 190, "Reload resumes only the second contact"));
        h.runAfterDelay(40, () -> sword.readAdditionalSaveData(saved));
        h.runAfterDelay(44, () -> {
            equal(h, enemy.getHealth(), 190, "Expired snapshot does not dump catch-up damage");
            h.assertTrue(!sword.attack().ready(TemplateSkills.SWORD_COMBO, h.getLevel().getGameTime()), "Cooldown survives reload");
            h.succeed();
        });
    }

    @GameTest(template="bow_ritual_test", timeoutTicks=195)
    public static void priestPossessionExpiresWithoutStackingOrPermanentAttributes(GameTestHelper h) {
        TemplateMob priest = mob(h, BlueprintEntities.FUFA_JIJIU.get(), 5, 5);
        TemplateMob ally = mob(h, BlueprintEntities.ZUWU_DAOSHOU.get(), 7, 5);
        double speed = ally.getAttributeValue(Attributes.MOVEMENT_SPEED);
        double attackSpeed = ally.getAttributeValue(Attributes.ATTACK_SPEED);
        double resistance = ally.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE);
        h.assertTrue(priest.startSkill(TemplateSkills.POSSESSION, ally), "Priest can buff a same-faction humanoid");
        h.runAfterDelay(18, () -> h.assertTrue(!ally.hasEffect(BlueprintEntities.BINGSHA_POSSESSION.get()), "No buff during windup"));
        h.runAfterDelay(23, () -> {
            equal(h, ally.getAttributeValue(Attributes.MOVEMENT_SPEED), speed * 1.3, "Possession movement bonus");
            equal(h, ally.getAttributeValue(Attributes.ATTACK_SPEED), attackSpeed * 1.3, "Possession attack speed bonus");
            equal(h, ally.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE), 1, "Possession knockback immunity");
            h.assertTrue(priest.buffTargetId() == ally.getId(), "Client beam follows the authoritative ally id");
            h.assertTrue(ally.isPossessed(), "Explicit client-scale metadata must mirror the effect");
            CompoundTag saved = new CompoundTag(); ally.addAdditionalSaveData(saved); ally.readAdditionalSaveData(saved);
            equal(h, ally.getAttributeValue(Attributes.MOVEMENT_SPEED), speed * 1.3, "Reload does not stack stable modifier UUIDs");
        });
        h.runAfterDelay(186, () -> {
            h.assertTrue(!ally.hasEffect(BlueprintEntities.BINGSHA_POSSESSION.get()), "Buff eventually expires");
            h.assertTrue(!ally.isPossessed(), "Client-scale metadata must clear on expiry");
            equal(h, ally.getAttributeValue(Attributes.MOVEMENT_SPEED), speed, "Movement modifier removed");
            equal(h, ally.getAttributeValue(Attributes.ATTACK_SPEED), attackSpeed, "Attack modifier removed");
            equal(h, ally.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE), resistance, "Knockback modifier removed");
            h.assertTrue(priest.buffTargetId() == -1, "Expired beam is cleared"); h.succeed();
        });
    }

    @GameTest(template="bow_ritual_test", timeoutTicks=40)
    public static void priestDeathRemovesPossessionAndBeam(GameTestHelper h) {
        TemplateMob priest = mob(h, BlueprintEntities.FUFA_JIJIU.get(), 5, 5);
        TemplateMob ally = mob(h, BlueprintEntities.ZUWU_DAOSHOU.get(), 7, 5);
        h.assertTrue(priest.startSkill(TemplateSkills.POSSESSION, ally), "Begin possession");
        h.runAfterDelay(24, () -> {
            h.assertTrue(ally.hasEffect(BlueprintEntities.BINGSHA_POSSESSION.get()), "Possession landed");
            priest.hurt(priest.damageSources().genericKill(), 10000);
            h.assertTrue(!ally.hasEffect(BlueprintEntities.BINGSHA_POSSESSION.get()), "Dead caster releases buff");
            h.assertTrue(priest.buffTargetId() == -1, "Dead caster releases visual link"); h.succeed();
        });
    }

    @GameTest(template="bow_ritual_test", timeoutTicks=50)
    public static void restoredAllyReconcilesPriestDeathWhileItWasUnloaded(GameTestHelper h) {
        var priest = mob(h, BlueprintEntities.FUFA_JIJIU.get(), 5, 5);
        var ally = mob(h, BlueprintEntities.ZUWU_DAOSHOU.get(), 7, 5);
        double speed = ally.getAttributeValue(Attributes.MOVEMENT_SPEED);
        var saved = new CompoundTag();
        TemplateMob[] restored = {null};
        h.assertTrue(priest.startSkill(TemplateSkills.POSSESSION, ally), "Begin actual possession");
        h.runAfterDelay(24, () -> {
            h.assertTrue(ally.isPossessed(), "Save an active buff, not an idle fixture");
            ally.saveWithoutId(saved);
            ally.remove(net.minecraft.world.entity.Entity.RemovalReason.UNLOADED_TO_CHUNK);
        });
        h.runAfterDelay(27, () -> priest.hurt(priest.damageSources().genericKill(), 10000));
        h.runAfterDelay(29, () -> {
            var copy = BlueprintEntities.ZUWU_DAOSHOU.get().create(h.getLevel());
            copy.load(saved);
            h.assertTrue(copy.getUUID().equals(ally.getUUID()), "Restore full entity identity");
            h.assertTrue(h.getLevel().addFreshEntity(copy), "Restore after the old entity has unloaded");
            restored[0] = copy;
        });
        h.runAfterDelay(33, () -> {
            h.assertTrue(!restored[0].isPossessed()
                    && !restored[0].hasEffect(BlueprintEntities.BINGSHA_POSSESSION.get()),
                    "Loading an ally after caster death must not resurrect the buff");
            equal(h, restored[0].getAttributeValue(Attributes.MOVEMENT_SPEED), speed, "No orphaned speed modifier");
            h.succeed();
        });
    }

    @GameTest(template="bow_ritual_test", timeoutTicks=55)
    public static void activeComboRetainsIdentityAndEncounterMembershipAcrossEntityUnload(GameTestHelper h) {
        var sword = mob(h, BlueprintEntities.ZUWU_DAOSHOU.get(), 5, 5);
        var enemy = victim(h, 5, 7);
        var state = BlueprintSpawnState.get(h.getLevel());
        String key = "test@active@" + sword.getUUID();
        var marker = new BlueprintSpawnState.Marker(key, sword.blockPosition());
        marker.members.add(sword.getUUID()); marker.produced = 1; state.markers.put(key, marker);
        var saved = new CompoundTag();
        TemplateMob[] restored = {null};
        h.assertTrue(sword.startSkill(TemplateSkills.SWORD_COMBO, enemy), "Start real two-contact attack");
        long start = sword.skillStartTime();
        h.runAfterDelay(15, () -> {
            equal(h, enemy.getHealth(), 195, "First contact already consumed");
            sword.saveWithoutId(saved);
            sword.remove(net.minecraft.world.entity.Entity.RemovalReason.UNLOADED_TO_CHUNK);
        });
        h.runAfterDelay(18, () -> {
            var copy = BlueprintEntities.ZUWU_DAOSHOU.get().create(h.getLevel()); copy.load(saved);
            h.assertTrue(h.getLevel().addFreshEntity(copy), "Reinsert persisted entity"); restored[0] = copy;
            h.assertTrue(copy.getUUID().equals(sword.getUUID()) && copy.skillStartTime() == start,
                    "UUID and attack epoch survive full NBT loading");
            var persisted = BlueprintSpawnState.load(state.save(new CompoundTag())).markers.get(key);
            h.assertTrue(persisted.members.equals(marker.members) && persisted.members.contains(copy.getUUID())
                    && persisted.produced == 1 && persisted.nextSpawn == 0, "Unload never releases or refills the encounter slot");
        });
        h.runAfterDelay(39, () -> {
            equal(h, enemy.getHealth(), 190, "Only the remaining contact executes after reload");
            h.assertTrue(!restored[0].attack().ready(TemplateSkills.SWORD_COMBO, h.getLevel().getGameTime()),
                    "Restart does not reset the attack cooldown");
            restored[0].hurt(restored[0].damageSources().genericKill(), 10000);
            h.assertTrue(marker.members.isEmpty(), "Actual death releases the retained encounter membership");
            state.markers.remove(key); state.setDirty(); h.succeed();
        });
    }

    @GameTest(template="bow_ritual_test", timeoutTicks=115)
    public static void projectilesHaveFiniteLifetimeEvenWithoutCollision(GameTestHelper h) {
        TemplateMob priest = mob(h, BlueprintEntities.FUFA_JIJIU.get(), 5, 5);
        TemplateProjectile projectile = new TemplateProjectile(BlueprintEntities.TEMPLATE_PROJECTILE.get(), h.getLevel());
        projectile.setOwner(priest); projectile.setPos(priest.position().add(0, 5, 0)); projectile.setDeltaMovement(Vec3.ZERO);
        h.getLevel().addFreshEntity(projectile);
        h.runAfterDelay(80, () -> h.assertTrue(!projectile.isRemoved(), "An unobstructed projectile remains within its lifetime"));
        h.runAfterDelay(104, () -> { h.assertTrue(projectile.isRemoved(), "Projectile must expire after 100 ticks"); h.succeed(); });
    }

    @GameTest(template="bow_ritual_test", timeoutTicks=215)
    public static void shieldCorpseRemainsActualCoverForTenSeconds(GameTestHelper h) {
        TemplateMob shield = mob(h, BlueprintEntities.LUDUN_JIASHI.get(), 6, 6);
        shield.setYRot(0); shield.hurt(shield.damageSources().genericKill(), 10000);
        h.assertTrue(shield.isDeadOrDying(), "Shield is dead");
        h.assertTrue(shield.canBeCollidedWith() && shield.canBeHitByProjectile(), "Corpse retains real collision and projectile bounds");
        Vec3 deathPosition = shield.position();
        h.runAfterDelay(25, () -> {
            Arrow arrow = new Arrow(h.getLevel(), shield.getX(), shield.getY() + 1, shield.getZ() + 3);
            arrow.setDeltaMovement(0, 0, -.8); arrow.setNoGravity(true); h.getLevel().addFreshEntity(arrow);
            h.runAfterDelay(10, () -> h.assertTrue(arrow.isRemoved(), "An actual moving arrow hits and is stopped by dead shield cover"));
        });
        h.runAfterDelay(190, () -> {
            h.assertTrue(!shield.isRemoved(), "Cover remains for 200 ticks");
            equal(h, shield.position().distanceToSqr(deathPosition), 0, "Remnant does not drift");
            CompoundTag saved = new CompoundTag(); shield.addAdditionalSaveData(saved); shield.readAdditionalSaveData(saved);
        });
        h.runAfterDelay(204, () -> { h.assertTrue(shield.isRemoved(), "Cover expires, including after reload"); h.succeed(); });
    }

    @GameTest(template="bow_ritual_test", timeoutTicks=45)
    public static void deathLootCannotBeRepeatedOrReplayedAfterReload(GameTestHelper h) {
        TemplateMob sword = mob(h, BlueprintEntities.ZUWU_DAOSHOU.get(), 6, 6);
        sword.hurt(sword.damageSources().genericKill(), 10000);
        int drops = droppedStacks(h, sword);
        h.assertTrue(drops > 0, "Registered copper-coin loot table must yield a drop");
        sword.die(sword.damageSources().genericKill());
        h.assertTrue(droppedStacks(h, sword) == drops, "Repeated death call cannot duplicate loot");
        CompoundTag saved = new CompoundTag(); sword.addAdditionalSaveData(saved); sword.readAdditionalSaveData(saved);
        sword.die(sword.damageSources().genericKill());
        h.assertTrue(droppedStacks(h, sword) == drops, "Reloaded death guard cannot duplicate loot");
        h.succeed();
    }
    private static int droppedStacks(GameTestHelper h, LivingEntity origin) {
        return h.getLevel().getEntitiesOfClass(ItemEntity.class, origin.getBoundingBox().inflate(3)).stream()
                .mapToInt(e -> e.getItem().getCount()).sum();
    }
    @GameTest(template="bow_ritual_test", timeoutTicks=32)
    public static void reflectedDamageDeathPreservesDeathAnimationClock(GameTestHelper h) {
        TemplateMob sword=mob(h,BlueprintEntities.ZUWU_DAOSHOU.get(),5,5);
        Cow thorns=new Cow(EntityType.COW,h.getLevel()) {
            @Override public boolean hurt(net.minecraft.world.damagesource.DamageSource source,float amount) {
                boolean hit=super.hurt(source,amount);
                if(hit && source.getEntity()==sword)sword.hurt(sword.damageSources().genericKill(),10000);
                return hit;
            }
        };
        thorns.moveTo(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(5,2,7))));
        thorns.setNoAi(true);thorns.setNoGravity(true);
        thorns.getAttribute(Attributes.MAX_HEALTH).setBaseValue(200);thorns.setHealth(200);
        h.assertTrue(h.getLevel().addFreshEntity(thorns),"Add retaliating target");
        h.assertTrue(sword.startSkill(TemplateSkills.SWORD_COMBO,thorns),"Start real entity attack");
        long attackStart=sword.skillStartTime();
        h.runAfterDelay(16,()-> {
            h.assertTrue(sword.isDeadOrDying(),"Damage callback killed attacker");
            h.assertTrue(sword.skillStartTime()==attackStart+12,"Death clock survives attack.advance return");
            h.assertTrue(sword.skillId()==0&&sword.attack().current()==null,"Dead attacker cannot continue combo");
            CompoundTag saved=new CompoundTag();sword.addAdditionalSaveData(saved);sword.readAdditionalSaveData(saved);
            h.assertTrue(sword.skillStartTime()==attackStart+12,"Death clock survives reload/late tracking");
            thorns.discard();h.succeed();
        });
    }
}
