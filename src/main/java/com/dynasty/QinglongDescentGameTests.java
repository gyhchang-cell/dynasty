package com.dynasty;

import com.dynasty.network.DragonDescentPacket;
import io.netty.buffer.Unpooled;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.damagesource.CombatRules;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;

@GameTestHolder(Dynasty.MODID)
@PrefixGameTestTemplate(false)
public final class QinglongDescentGameTests {
    private static LivingEntity attacker(GameTestHelper h) {
        var mob=h.spawn(EntityType.ZOMBIE,3,2,3);mob.setNoAi(true);mob.setNoGravity(true);
        mob.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyWeapons.QINGLONG_DAO.get()));return mob;
    }
    private static LivingEntity target(GameTestHelper h) {
        var mob=h.spawn(EntityType.SHEEP,5,2,3);mob.setNoAi(true);mob.setNoGravity(true);
        mob.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);mob.setHealth(1000);return mob;
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=65)
    public static void delayDamageExactlyOnceAndKeepDefenses(GameTestHelper h) {
        var attacker=attacker(h);var target=target(h);
        target.getAttribute(Attributes.ARMOR).setBaseValue(20);
        target.addEffect(new MobEffectInstance(MobEffects.DAMAGE_RESISTANCE,200,0));
        target.setAbsorptionAmount(40);
        target.hurt(h.getLevel().damageSources().mobAttack(attacker),2);
        h.assertTrue(target.getHealth()==1000 && target.getAbsorptionAmount()==40,"Mark must not consume health or absorption");
        // Switching to a different weapon must not change the captured attack or add its bonuses.
        attacker.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyWeapons.TIANZI_SWORD.get()));
        float damage=CombatRules.getDamageAfterAbsorb(2+(float)DynastyBalance.weaponBonus("qinglong_dao"),20,0)*.8f-40;
        h.runAfterDelay(15,()->h.assertTrue(target.getHealth()==1000,"Damage must wait for the descending dragon"));
        h.runAfterDelay(QinglongDescent.DELAY+5,()-> {
            h.assertTrue(Math.abs(target.getHealth()-(1000-damage))<.05,"Armor/resistance/absorption must apply once; actual "+target.getHealth());
            h.assertTrue(target.getLastHurtByMob()==attacker,"Landing must retain attacker attribution");
        });
        h.runAfterDelay(48,()-> {
            h.assertTrue(Math.abs(target.getHealth()-(1000-damage))<.05,"Landing must not recurse or deal damage twice");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=45)
    public static void independentHitsIgnoreOnlyTheHurtCooldown(GameTestHelper h) {
        var attacker=attacker(h);var target=target(h);
        target.hurt(h.getLevel().damageSources().mobAttack(attacker),1);
        target.invulnerableTime=0;
        target.hurt(h.getLevel().damageSources().mobAttack(attacker),1);
        h.runAfterDelay(QinglongDescent.DELAY+6,()-> {
            h.assertTrue(Math.abs(target.getHealth()-298)<.05,"Two accepted attacks must each land once, not be lost to hurt cooldown: "+target.getHealth());h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=45)
    public static void removedAttackerCancelsPendingStrike(GameTestHelper h) {
        var attacker=attacker(h);var target=target(h);
        target.hurt(h.getLevel().damageSources().mobAttack(attacker),1);attacker.discard();
        h.runAfterDelay(QinglongDescent.DELAY+6,()->{h.assertTrue(target.getHealth()==1000,"Disconnected/removed attacker must not leave a ghost hit");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=45)
    public static void canceledMarkDoesNotScheduleDamage(GameTestHelper h) {
        var attacker=attacker(h);var target=target(h);
        var event=new LivingHurtEvent(target,h.getLevel().damageSources().mobAttack(attacker),10);
        event.setCanceled(true);QinglongDescent.mark(event);
        h.runAfterDelay(QinglongDescent.DELAY+6,()->{h.assertTrue(target.getHealth()==1000,"Canceled hit must not summon a damaging dragon");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30)
    public static void descentPacketKeepsTargetAndTiming(GameTestHelper h) {
        var b=new FriendlyByteBuf(Unpooled.buffer());
        try {
            for(int phase=0;phase<3;phase++) {
                b.clear();var p=new DragonDescentPacket(73,phase,44,java.util.UUID.randomUUID(),300,-40.25,82.3,20,135f);
                DragonDescentPacket.encode(p,b);
                h.assertTrue(p.equals(DragonDescentPacket.decode(b)) && b.readableBytes()==0,"Keep target identity, timing and authoritative phase");
            }
        }finally{b.release();}h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=45)
    public static void lethalLandingCreditsPlayer(GameTestHelper h) {
        var player=new net.minecraftforge.common.util.FakePlayer(h.getLevel(),
                new com.mojang.authlib.GameProfile(java.util.UUID.randomUUID(),"dragon-test"));
        h.getLevel().addNewPlayer(player);
        player.setPos(net.minecraft.world.phys.Vec3.atCenterOf(h.absolutePos(new net.minecraft.core.BlockPos(3,2,3))));
        player.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyWeapons.QINGLONG_DAO.get()));
        var sheep=h.spawn(EntityType.SHEEP,5,2,3);sheep.setNoAi(true);sheep.setNoGravity(true);
        sheep.hurt(h.getLevel().damageSources().playerAttack(player),1);
        h.assertTrue(sheep.isAlive() && sheep.getHealth()==sheep.getMaxHealth(),"Mark must not kill the target early");
        h.runAfterDelay(QinglongDescent.DELAY+4,()-> {
            h.assertTrue(!sheep.isAlive(),"Lethal weapon damage must kill on landing");
            h.assertTrue(sheep.getKillCredit()==player,"Kill rewards must belong to the player");
            player.discard();h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=65)
    public static void cageHoldsThenReleasesWithoutPersistentAiChanges(GameTestHelper h) {
        var caster=attacker(h);var mob=target(h);var anchor=mob.position();
        mob.hurt(h.getLevel().damageSources().mobAttack(caster),1);
        h.runAfterDelay(7,()-> {
            mob.setPos(anchor.add(1,.3,0));mob.setDeltaMovement(.8,.4,.1);
            var tick=new net.minecraftforge.event.entity.living.LivingEvent.LivingTickEvent(mob);
            QinglongDescent.holdBoundTarget(tick);
            h.assertTrue(tick.isCanceled()&&mob.position().distanceToSqr(anchor)<1e-8,"Active cage must hold the original position");
            h.assertTrue(mob.getDeltaMovement().lengthSqr()==0,"Cage must stop velocity");
        });
        h.runAfterDelay(QinglongDescent.DELAY+5,()-> {
            var tick=new net.minecraftforge.event.entity.living.LivingEvent.LivingTickEvent(mob);
            QinglongDescent.holdBoundTarget(tick);
            h.assertTrue(!tick.isCanceled(),"Cage must release on landing");
            h.assertTrue(((net.minecraft.world.entity.Mob)mob).isNoAi()&&mob.isNoGravity(),"Preexisting entity flags must be unchanged");
            h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=30)
    public static void casterRemovalReleasesCageEarly(GameTestHelper h) {
        var caster=attacker(h);var mob=target(h);
        mob.hurt(h.getLevel().damageSources().mobAttack(caster),1);caster.discard();
        h.runAfterDelay(3,()-> {
            var tick=new net.minecraftforge.event.entity.living.LivingEvent.LivingTickEvent(mob);
            QinglongDescent.holdBoundTarget(tick);
            h.assertTrue(!tick.isCanceled(),"Removed caster must not leave the target frozen");
            h.assertTrue(mob.getHealth()==1000,"Canceled cage must not damage target");h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=65)
    public static void overlappingCagesReleaseOrdinaryAiAfterLastStrike(GameTestHelper h) {
        var caster=attacker(h);var mob=(net.minecraft.world.entity.Mob)target(h);
        mob.setNoAi(false);mob.setNoGravity(false);var anchor=mob.position();
        mob.hurt(h.getLevel().damageSources().mobAttack(caster),1);
        h.runAfterDelay(12,()-> {
            h.assertTrue(mob.position().distanceToSqr(anchor)<1e-8,"Real entity ticks must keep the victim at the seal anchor");
            h.assertTrue(mob.invulnerableTime<=10,"Damage cooldown must continue during binding");
            mob.hurt(h.getLevel().damageSources().mobAttack(caster),1);
        });
        h.runAfterDelay(QinglongDescent.DELAY+3,()-> {
            var tick=new net.minecraftforge.event.entity.living.LivingEvent.LivingTickEvent(mob);
            QinglongDescent.holdBoundTarget(tick);
            h.assertTrue(tick.isCanceled(),"Second accepted strike must retain the binding after the first lands");
            h.assertTrue(mob.position().distanceToSqr(anchor)<1e-8,"Overlapping cages must retain the same anchor");
            h.assertTrue(!mob.isNoAi()&&!mob.isNoGravity(),"Binding must not alter ordinary persisted entity flags");
        });
        h.runAfterDelay(QinglongDescent.DELAY+15,()-> {
            var tick=new net.minecraftforge.event.entity.living.LivingEvent.LivingTickEvent(mob);
            QinglongDescent.holdBoundTarget(tick);
            h.assertTrue(!tick.isCanceled()&&!mob.isNoAi()&&!mob.isNoGravity(),"Ordinary mob must resume after the final landing");
            h.assertTrue(Math.abs(mob.getHealth()-298)<.05,"Overlapping accepted strikes must each resolve once");
            h.succeed();
        });
    }
}
