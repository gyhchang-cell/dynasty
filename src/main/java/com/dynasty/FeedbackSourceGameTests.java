package com.dynasty;

import com.dynasty.cod3.EquipmentFeedback;
import com.dynasty.expansion.CombatFeedback;
import com.dynasty.expansion.ExpansionContent;
import com.mojang.authlib.GameProfile;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.event.entity.player.*;
import net.minecraftforge.gametest.*;

/** Feedback observes native source/crit/velocity; it never repeats the gameplay hit. */
@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class FeedbackSourceGameTests {
    private static ServerPlayer player(GameTestHelper h){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"feedback-source"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);return p;
    }
    private static Cow target(GameTestHelper h){var t=h.spawn(EntityType.COW,new BlockPos(4,2,4));t.setNoAi(true);t.setNoGravity(true);t.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);t.setHealth(1000);return t;}
    private static void clear(Cow t){t.getPersistentData().remove("cod4FeedbackTick");t.getPersistentData().remove("cod4FeedbackType");}
    @GameTest(template="bow_ritual_test",batch="cod4_feedback_sources",setupTicks=20)
    public static void arrowSnapshotKeepsOriginalFiringGrowthAcrossSwapAndNbtReload(GameTestHelper h){
        var p=player(h);var bow=new ItemStack(ExpansionContent.item("zhuxing_bow"));bow.setDamageValue(9);bow.getOrCreateTagElement(DynastyWeaponProgression.KEY).putUUID("identity",UUID.randomUUID());bow.getOrCreateTag().putString("ForeignData","original");p.setItemSlot(EquipmentSlot.MAINHAND,bow.copy());
        var arrow=new Arrow(h.getLevel(),p);arrow.setNoGravity(true);arrow.setDeltaMovement(0,0,1);h.getLevel().addFreshEntity(arrow);
        h.assertTrue(arrow.getPersistentData().contains("cod3_firing_weapon"),"Actual join listener stores the immutable firing item");
        long start=arrow.getPersistentData().getLong("cod3_trail_start"),seed=arrow.getPersistentData().getLong("cod3_trail_seed");
        p.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(ExpansionContent.item("juling_axe")));var saved=new CompoundTag();arrow.save(saved);arrow.discard();var restored=new Arrow(EntityType.ARROW,h.getLevel());restored.load(saved);restored.setOwner(p);
        EquipmentFeedback.arrow(new net.minecraftforge.event.entity.EntityJoinLevelEvent(restored,h.getLevel()));
        h.assertTrue(ItemStack.isSameItemSameTags(bow,EquipmentFeedback.firingWeapon(restored,p)),"Swap and actual arrow NBT reload retain exact source dye/damage/growth/foreign fields");
        h.assertTrue(restored.getPersistentData().getLong("cod3_trail_start")==start&&restored.getPersistentData().getLong("cod3_trail_seed")==seed,"Reload does not restart or reroll an existing bounded arrow trail");
        var t=target(h);var hit=new LivingDamageEvent(t,p.damageSources().arrow(restored,p),10);float before=t.getHealth();EquipmentFeedback.damage(hit);CombatFeedback.hit(hit);
        h.assertTrue(t.getPersistentData().getInt("cod4FeedbackType")==CombatFeedback.NORMAL&&t.getPersistentData().contains("cod3_arrow_impact_at"),"Arrow hit gets its own impact and is not classified as the newly held axe");
        h.assertTrue(p.getPersistentData().getInt("cod3_combo")==0&&t.getHealth()==before&&hit.getAmount()==10,"Presentation does not advance a melee combo or reapply damage");
        t.discard();restored.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_feedback_sources",setupTicks=20)
    public static void legacyTrailIdentityAndForeignArrowCannotBorrowHeldDynastyWeapon(GameTestHelper h){
        var p=player(h);p.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(ExpansionContent.item("seven_star_saber")));var old=new Arrow(h.getLevel(),p);old.getPersistentData().putString("cod3_trail_weapon","dynasty:fengling_bow");
        h.assertTrue(EquipmentFeedback.firingWeapon(old,p).is(ExpansionContent.item("fengling_bow")),"Old already-flying arrows retain original registered trail identity");
        var foreign=new Arrow(h.getLevel(),p);foreign.getPersistentData().put("cod3_firing_weapon",new ItemStack(Items.BOW).save(new CompoundTag()));var t=target(h);var hit=new LivingDamageEvent(t,p.damageSources().arrow(foreign,p),10);
        EquipmentFeedback.damage(hit);CombatFeedback.hit(hit);h.assertTrue(!t.getPersistentData().contains("cod4FeedbackTick")&&!t.getPersistentData().contains("cod3_arrow_impact_at")&&p.getPersistentData().getInt("cod3_combo")==0,"Vanilla shot cannot fabricate Dynasty saber stars or melee combo after swapping");
        var spell=new LivingDamageEvent(t,p.damageSources().indirectMagic(p,p),10);EquipmentFeedback.damage(spell);CombatFeedback.hit(spell);h.assertTrue(EquipmentFeedback.sourceWeapon(spell).isEmpty()&&!t.getPersistentData().contains("cod4FeedbackTick"),"Indirect magic does not masquerade as the held blade");t.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_feedback_sources",setupTicks=20)
    public static void actualCritResultAndAddedImpulseOwnFeedbackInsteadOfNamesOrFalling(GameTestHelper h){
        var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"feedback-crit")){@Override public float getAttackStrengthScale(float partial){return 1;}};
        p.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(ExpansionContent.item("dragon_spear")));p.fallDistance=2;p.setOnGround(false);var t=target(h);t.setDeltaMovement(0,.4,0);
        DynastySchoolCombat.attack(new AttackEntityEvent(p,t));var hit=new LivingDamageEvent(t,p.damageSources().playerAttack(p),1);CombatFeedback.hit(hit);
        h.assertTrue(t.getPersistentData().getInt("cod4FeedbackType")==CombatFeedback.NORMAL,"Spear name, falling attacker and pre-existing upward velocity cannot fake launch/crit");
        var denied=new CriticalHitEvent(p,t,1.5f,true);denied.setResult(net.minecraftforge.eventbus.api.Event.Result.DENY);DynastySchoolCombat.critical(denied);clear(t);CombatFeedback.hit(hit);h.assertTrue(t.getPersistentData().getInt("cod4FeedbackType")==CombatFeedback.NORMAL,"Native denied critical result is respected");
        var forced=new CriticalHitEvent(p,t,1.5f,false);forced.setResult(net.minecraftforge.eventbus.api.Event.Result.ALLOW);DynastySchoolCombat.critical(forced);clear(t);CombatFeedback.hit(hit);h.assertTrue(t.getPersistentData().getInt("cod4FeedbackType")==CombatFeedback.CRITICAL,"Actual Forge-forced critical result is respected");
        t.setDeltaMovement(0,.8,0);clear(t);CombatFeedback.hit(hit);h.assertTrue(t.getPersistentData().getInt("cod4FeedbackType")==CombatFeedback.LAUNCH,"Only new captured-hit vertical impulse qualifies as launch");
        var roof=h.absolutePos(new BlockPos(4,4,4));h.getLevel().setBlockAndUpdate(roof,net.minecraft.world.level.block.Blocks.STONE.defaultBlockState());
        t.setPos(t.getX(),roof.getY()-t.getBbHeight(),t.getZ());t.setDeltaMovement(Vec3.ZERO);DynastySchoolCombat.attack(new AttackEntityEvent(p,t));t.setDeltaMovement(0,.4,0);clear(t);CombatFeedback.hit(hit);
        h.assertTrue(t.getPersistentData().getInt("cod4FeedbackType")==CombatFeedback.NORMAL,"A solid roof blocks a false launch even when this hit added upward speed");h.getLevel().setBlockAndUpdate(roof,net.minecraft.world.level.block.Blocks.AIR.defaultBlockState());
        h.assertTrue(hit.getAmount()==1&&t.getHealth()==1000,"Every classification remains presentation-only");t.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",batch="cod4_feedback_native_lift",setupTicks=20,timeoutTicks=40)
    public static void realPlayerAttackJuqueLiftProducesLaunchAndZeroDamageProducesNothing(GameTestHelper h){
        var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"feedback-native")){@Override public float getAttackStrengthScale(float partial){return 1;}};
        var t=target(h);p.setPos(t.getX()-1,t.getY(),t.getZ());p.setOnGround(true);p.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(ExpansionContent.item("juque_sword")));t.setDeltaMovement(Vec3.ZERO);
        p.attack(t);h.assertTrue(t.getHealth()<1000&&t.getDeltaMovement().y>=.39&&t.getPersistentData().getInt("cod4FeedbackType")==CombatFeedback.LAUNCH,"Real vanilla Player.attack uses native juque hurt impulse and captured primary context");
        clear(t);var zero=new LivingDamageEvent(t,p.damageSources().playerAttack(p),0);EquipmentFeedback.damage(zero);CombatFeedback.hit(zero);h.assertTrue(!t.getPersistentData().contains("cod4FeedbackTick"),"Zero/cancelled gameplay has no fabricated feedback");t.discard();h.succeed();
    }
}
