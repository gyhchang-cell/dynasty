package com.dynasty.expansion;

import com.mojang.authlib.GameProfile;
import com.dynasty.*;
import net.minecraft.gametest.framework.*;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.item.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.nbt.CompoundTag;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.gametest.*;
import net.minecraftforge.event.entity.living.*;
import java.util.*;

@GameTestHolder("dynasty_cod4")
@PrefixGameTestTemplate(false)
public final class ExpansionGameTests {
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void sharedComboCountsOncePerTickAndAdvancesNextTick(GameTestHelper h) {
        var p=player(h);var target=new Zombie(h.getLevel());
        h.assertTrue(DynastyTrinketOnHit.advanceCombo(p,target)==1,"First strike starts combo");
        h.assertTrue(DynastyTrinketOnHit.advanceCombo(p,target)==1,"Armor and accessory hooks share one strike");
        h.runAfterDelay(2,()->{h.assertTrue(DynastyTrinketOnHit.advanceCombo(p,target)==2,"Next strike advances shared combo");h.succeed();});
    }
    private static FakePlayer player(GameTestHelper h) {
        var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"cod4-qa"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(net.minecraft.world.phys.Vec3.atCenterOf(h.absolutePos(new BlockPos(2,2,2))));return p;
    }
    private static void suit(FakePlayer p,String id,int count) {
        var slots=new EquipmentSlot[]{EquipmentSlot.HEAD,EquipmentSlot.CHEST,EquipmentSlot.LEGS,EquipmentSlot.FEET};String[] suffix={"helmet","chestplate","leggings","boots"};
        for(int i=0;i<4;i++)p.setItemSlot(slots[i],i<count?new ItemStack(ExpansionContent.item(id+"_"+suffix[i])):ItemStack.EMPTY);
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void allThirtySecondaryTypesInstantiateAndHaveNoBossBar(GameTestHelper h) {
        h.assertTrue(SecondaryMobs.TYPES.size()==30,"Exactly 30 additional IDs");
        for(var spec:SecondaryMobs.SPECS) {
            var mob=SecondaryMobs.TYPES.get(spec.id()).get().create(h.getLevel());
            h.assertTrue(mob!=null && Math.abs(mob.getMaxHealth()-spec.health())<.01,"Attributes exist for "+spec.id());
            h.assertTrue(!((Object)mob instanceof DynastyBossCombat.BarHolder),"Secondary is not a boss");
            h.assertTrue(mob instanceof net.minecraft.world.entity.monster.Enemy != spec.neutral(),"Hostile classification: "+spec.id());
            CompoundTag saved=new CompoundTag();mob.addAdditionalSaveData(saved);mob.readAdditionalSaveData(saved);
        }h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void oppositeQiCancelsAndStacksAreCapped(GameTestHelper h) {
        var z=new Zombie(h.getLevel());ExpansionEffects.apply(z,ExpansionEffects.YIN,100);ExpansionEffects.apply(z,ExpansionEffects.YIN,100);ExpansionEffects.apply(z,ExpansionEffects.YIN,100);ExpansionEffects.apply(z,ExpansionEffects.YIN,100);
        h.assertTrue(z.getEffect(ExpansionEffects.YIN.get()).getAmplifier()==2,"Three layers maximum");ExpansionEffects.apply(z,ExpansionEffects.YANG,100);
        h.assertTrue(!z.hasEffect(ExpansionEffects.YIN.get())&&!z.hasEffect(ExpansionEffects.YANG.get()),"Opposite Qi cleanses instead of stacking");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void thunderThirdMarkDetonatesAndClears(GameTestHelper h) {
        var z=new Zombie(h.getLevel());float hp=z.getHealth();for(int i=0;i<3;i++)ExpansionEffects.apply(z,ExpansionEffects.THUNDER,60);
        h.assertTrue(!z.hasEffect(ExpansionEffects.THUNDER.get())&&z.getHealth()<hp,"Third mark deals damage and consumes marks");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void armorModifiersAreIdempotentAndImmediatelyRemoved(GameTestHelper h) {
        var p=player(h);suit(p,"beidou",2);double base=p.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.MOVEMENT_SPEED);
        EquipmentBehaviors.refresh(p);double once=p.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.MOVEMENT_SPEED);EquipmentBehaviors.refresh(p);
        h.assertTrue(Math.abs(once-p.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.MOVEMENT_SPEED))<.00001,"Repeated refresh must not stack");
        suit(p,"beidou",0);EquipmentBehaviors.refresh(p);h.assertTrue(p.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.MOVEMENT_SPEED)<once,"Unequip removes bonus immediately");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void armorStateDoesNotLeakBetweenPlayers(GameTestHelper h) {
        var a=player(h);var b=player(h);suit(a,"general",4);a.getPersistentData().putInt("cod4Still",40);EquipmentBehaviors.refresh(a);EquipmentBehaviors.refresh(b);
        h.assertTrue(b.getAttributeValue(net.minecraft.world.entity.ai.attributes.Attributes.ARMOR)==0,"Unarmored player remains unmodified");
        h.assertTrue(EquipmentBehaviors.ready(a,"test",6000)&&EquipmentBehaviors.ready(b,"test",6000)&&!EquipmentBehaviors.ready(a,"test",6000),"Cooldowns belong to each player");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void crossbowConsumesThreeRoundsOnceAndMagazinePersists(GameTestHelper h) {
        var p=player(h);var stack=new ItemStack(ExpansionContent.REPEATING.get());p.setItemInHand(InteractionHand.MAIN_HAND,stack);p.getInventory().add(new ItemStack(Items.ARROW,5));
        var bow=(ExpansionWeapons.BurstCrossbow)stack.getItem();bow.releaseUsing(stack,h.getLevel(),p,71960);
        h.assertTrue(p.getInventory().countItem(Items.ARROW)==2 && CrossbowItem.isCharged(stack),"Exactly three arrows consumed when loading");
        var restored=ItemStack.of(stack.save(new CompoundTag()));h.assertTrue(restored.getTag().getList("cod4Magazine",10).size()==3,"Magazine survives save/reload");
        for(int i=0;i<3;i++)bow.onUseTick(h.getLevel(),p,restored,72000-i*6);
        h.assertTrue(!CrossbowItem.isCharged(restored)&&p.getInventory().countItem(Items.ARROW)==2,"Firing does not consume ammo twice");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void crossbowCannotLoadWrongBoltsOrFireBeforeCharge(GameTestHelper h) {
        var p=player(h);var stack=new ItemStack(ExpansionContent.SIEGE.get());var bow=(ExpansionWeapons.BurstCrossbow)stack.getItem();
        h.assertTrue(!bow.getAllSupportedProjectiles().test(new ItemStack(ExpansionContent.AMMO.get("repeating_bolt").get())),"Wrong bolt rejected");
        p.setItemInHand(InteractionHand.MAIN_HAND,stack);p.getInventory().add(new ItemStack(Items.ARROW,1));bow.releaseUsing(stack,h.getLevel(),p,71999);
        h.assertTrue(!CrossbowItem.isCharged(stack)&&p.getInventory().countItem(Items.ARROW)==1,"Early release leaves ammunition untouched");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void trinketBoxDoesNotRepeatBeforePoolExhaustion(GameTestHelper h) {
        var p=player(h);Set<Item> seen=new HashSet<>();for(int i=0;i<20;i++)h.assertTrue(seen.add(ContentProgress.gift(p).getItem()),"No repeat among first 20 rolls");
        var data=EquipmentBehaviors.saved(p).copy();var q=player(h);var persisted=new CompoundTag();persisted.put("dynastyCod4",data);q.getPersistentData().put(net.minecraft.world.entity.player.Player.PERSISTED_NBT_TAG,persisted);
        h.assertTrue(!seen.contains(ContentProgress.gift(q).getItem()),"History survives reconstructed player data");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void lastStandCooldownPersistsAndDoesNotBlockKillCommand(GameTestHelper h) {
        var p=player(h);suit(p,"zhuque",4);var z=new Zombie(h.getLevel());var e=new LivingDamageEvent(p,p.damageSources().mobAttack(z),p.getHealth()+100);EquipmentBehaviors.damage(e);
        h.assertTrue(e.getAmount()==0,"First lethal hit prevented");var again=new LivingDamageEvent(p,p.damageSources().mobAttack(z),p.getHealth()+100);EquipmentBehaviors.damage(again);h.assertTrue(again.getAmount()>0,"Second hit is not immortal");
        var bypass=new LivingDamageEvent(p,p.damageSources().genericKill(),99999);EquipmentBehaviors.damage(bypass);h.assertTrue(bypass.getAmount()==99999,"Administrative kill is never intercepted");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void refugeeFeedingIsServerOwnedAndSurvivesSave(GameTestHelper h) {
        var p=player(h);var mob=SecondaryMobs.TYPES.get("famished_refugee").get().create(h.getLevel());p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.BREAD,2));mob.mobInteract(p,InteractionHand.MAIN_HAND);
        h.assertTrue(p.getMainHandItem().getCount()==1,"Consumes one food");var n=new CompoundTag();mob.addAdditionalSaveData(n);h.assertTrue(n.getBoolean("Cod4Friendly"),"Redemption persisted");mob.mobInteract(p,InteractionHand.MAIN_HAND);h.assertTrue(p.getMainHandItem().getCount()==1,"No repeated charge");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void syntheticDamageGuardAlwaysRestoresAfterException(GameTestHelper h) {
        try{DynastyTrinketOnHit.syntheticDamage(()->{throw new IllegalStateException("test");});}catch(IllegalStateException expected){}
        h.assertTrue(!DynastyTrinketOnHit.isSyntheticDamage(),"Exception cannot poison later combat");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void projectileGrowthKeepsOriginalCrossbowIdentity(GameTestHelper h) {
        var p=player(h);var bow=new ItemStack(ExpansionContent.SIEGE.get());p.setItemInHand(InteractionHand.MAIN_HAND,bow);
        var arrow=new net.minecraft.world.entity.projectile.Arrow(h.getLevel(),p);
        DynastyWeaponProgression.onArrow(new net.minecraftforge.event.entity.EntityJoinLevelEvent(arrow,h.getLevel()));
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.STICK));
        var saved=DynastyWeaponProgression.attackWeapon(p,p.damageSources().arrow(arrow,p));
        h.assertTrue(saved.is(ExpansionContent.SIEGE.get()) && saved.getTagElement(DynastyWeaponProgression.KEY).hasUUID("identity"),"Arrows keep the firing crossbow identity after swapping");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void immunityCannotBeBypassedByRepeatedMarks(GameTestHelper h) {
        var boss=com.dynasty.ritual.ZhenyuanBosses.FINAL_BOSS.get().create(h.getLevel());
        ExpansionEffects.apply(boss,ExpansionEffects.STAGGER,40);ExpansionEffects.apply(boss,ExpansionEffects.SHA,80);
        h.assertTrue(!boss.hasEffect(ExpansionEffects.STAGGER.get())&&!boss.hasEffect(ExpansionEffects.SHA.get()),"Boss does not accept hard control");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void oneShotWorldInteractionCannotBeClaimedTwice(GameTestHelper h) {
        var p=player(h);var pos=h.absolutePos(new BlockPos(3,2,3));var block=SmallInteractions.ENTRIES.get("old_weapon_rack").get();h.getLevel().setBlockAndUpdate(pos,block.defaultBlockState());
        var hit=new net.minecraft.world.phys.BlockHitResult(net.minecraft.world.phys.Vec3.atCenterOf(pos),net.minecraft.core.Direction.UP,pos,false);
        block.defaultBlockState().use(h.getLevel(),p,InteractionHand.MAIN_HAND,hit);
        var n=EquipmentBehaviors.saved(p);n.putLong("site_old_weapon_rack_next",0);
        block.defaultBlockState().use(h.getLevel(),p,InteractionHand.MAIN_HAND,hit);
        int count=p.getInventory().countItem(ExpansionContent.item("tie_jian"));
        block.defaultBlockState().use(h.getLevel(),p,InteractionHand.MAIN_HAND,hit);
        h.assertTrue(count==1&&p.getInventory().countItem(ExpansionContent.item("tie_jian"))==1,"Only one reward despite repeated clicks");h.succeed();
    }

    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void examRobeAndWineShareOneDeadlineBonus(GameTestHelper h) {
        var p=player(h);
        h.assertTrue(DynastyKeju.answerDurationMillis(p)==30000,"Base exam is 30 seconds");
        suit(p,"brocade",4);h.assertTrue(DynastyKeju.answerDurationMillis(p)==36000,"Four robe pieces add 20% answer time");
        p.getPersistentData().putLong("cod4ExamWine",p.level().getGameTime()+1200);
        h.assertTrue(DynastyKeju.answerDurationMillis(p)==42000,"Robe and wine add to the same base");
        suit(p,"brocade",0);h.assertTrue(DynastyKeju.answerDurationMillis(p)==36000,"Wine alone adds 20%");
        p.getPersistentData().putLong("cod4ExamWine",p.level().getGameTime());
        h.assertTrue(DynastyKeju.answerDurationMillis(p)==30000,"Expired wine has no effect");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void skyJumpTwoIsOwnedAndStrongerPotionsSurvive(GameTestHelper h) {
        var p=player(h);suit(p,"sky",4);EquipmentBehaviors.refresh(p);
        h.assertTrue(p.hasEffect(MobEffects.JUMP)&&p.getEffect(MobEffects.JUMP).getAmplifier()==1,"Actual Jump Boost II");
        suit(p,"sky",3);EquipmentBehaviors.refresh(p);h.assertTrue(!p.hasEffect(MobEffects.JUMP),"Unequip removes owned jump immediately");
        p.addEffect(new MobEffectInstance(MobEffects.JUMP,600,0));suit(p,"sky",4);EquipmentBehaviors.refresh(p);
        h.assertTrue(p.getEffect(MobEffects.JUMP).getAmplifier()==1,"Weaker potion cannot suppress set Jump II");
        suit(p,"sky",3);EquipmentBehaviors.refresh(p);
        h.assertTrue(p.getEffect(MobEffects.JUMP).getAmplifier()==0&&p.getEffect(MobEffects.JUMP).getDuration()>500,"Unequip restores weaker external potion");
        p.removeEffect(MobEffects.JUMP);
        p.addEffect(new MobEffectInstance(MobEffects.JUMP,1200,3));suit(p,"sky",4);EquipmentBehaviors.refresh(p);suit(p,"sky",0);EquipmentBehaviors.refresh(p);
        h.assertTrue(p.getEffect(MobEffects.JUMP).getAmplifier()==3,"External stronger potion remains");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void qilinProcPreventsWholeHitAndNeverAdministrativeKill(GameTestHelper h) {
        var p=player(h);suit(p,"qilin",3);var mob=new Zombie(h.getLevel());boolean proc=false,miss=false;
        p.getRandom().setSeed(17);
        for(int i=0;i<80;i++) {
            var event=new LivingHurtEvent(p,p.damageSources().mobAttack(mob),10);EquipmentBehaviors.hurt(event);
            h.assertTrue(event.getAmount()==0||event.getAmount()==10,"Proc cannot be half damage");proc|=event.getAmount()==0;miss|=event.getAmount()==10;
        }
        h.assertTrue(proc&&miss,"15% roll can both proc and miss");
        var kill=new LivingHurtEvent(p,p.damageSources().genericKill(),99999);EquipmentBehaviors.hurt(kill);
        h.assertTrue(kill.getAmount()==99999,"Administrative damage bypasses proc");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void starStepRequiresContinuityAndUnequipRevokesWindow(GameTestHelper h) {
        var p=player(h);suit(p,"beidou",4);p.setSprinting(true);
        EquipmentBehaviors.advanceStarStep(p,.25);
        h.assertTrue(!p.getPersistentData().contains("cod4StarIFrame"),"Single movement cannot proc");
        for(int i=0;i<8;i++)EquipmentBehaviors.advanceStarStep(p,.25);
        EquipmentBehaviors.advanceStarStep(p,0);
        h.assertTrue(p.getPersistentData().getInt("cod4ContinuousSteps")==0,"Stopping breaks sequence");
        for(int i=0;i<10;i++)EquipmentBehaviors.advanceStarStep(p,.25);
        h.assertTrue(p.getPersistentData().getLong("cod4StarIFrame")==p.level().getGameTime()+4,"Consecutive movement opens four-tick window");
        suit(p,"beidou",3);EquipmentBehaviors.refresh(p);
        h.assertTrue(!p.getPersistentData().contains("cod4StarIFrame"),"Unequip revokes invulnerability");
        suit(p,"beidou",4);EquipmentBehaviors.advanceStarStep(p,100);
        h.assertTrue(p.getPersistentData().getInt("cod4ContinuousSteps")==0,"Teleport cannot count as a stride");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void phoenixWindowSurvivesExtinguishingAndExpires(GameTestHelper h) {
        var p=player(h);p.setSecondsOnFire(2);EquipmentBehaviors.phoenixIgnited(p);p.clearFire();
        h.assertTrue(EquipmentBehaviors.phoenixAttackActive(p),"Extinguishing cannot erase offensive proc");
        p.getPersistentData().putLong("cod4PhoenixAttack",p.level().getGameTime());
        h.assertTrue(!EquipmentBehaviors.phoenixAttackActive(p),"Expired fire window ends");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void qiPillUsesSharedComboAndRestoresNormalAdvance(GameTestHelper h) {
        var p=player(h);var target=new Zombie(h.getLevel());
        DynastyTrinketOnHit.advanceCombo(p,target);
        var pill=new ItemStack(ExpansionContent.SUPPLIES.get("qi_pill").get());pill.finishUsingItem(h.getLevel(),p);
        h.assertTrue(p.getPersistentData().getInt("cod4Rage")==2,"Pill fills two points of existing rage");
        h.runAfterDelay(2,()->{
            h.assertTrue(DynastyTrinketOnHit.advanceCombo(p,target)==3,"Pill advances existing combo by two");
            h.assertTrue(DynastyTrinketOnHit.advanceCombo(p,target)==3,"Same tick still counts only once");
            p.getPersistentData().putLong("cod4QiUntil",p.level().getGameTime());
        });
        h.runAfterDelay(4,()->{h.assertTrue(DynastyTrinketOnHit.advanceCombo(p,target)==4,"Expired pill restores single advance");h.succeed();});
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void supplyObjectiveRequiresCraftAndKeepsLegacyCompletion(GameTestHelper h) {
        // Forge rejects advancement grants to FakePlayer; exercise the normal server-player path.
        var p=new net.minecraft.server.level.ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"cod4-craft"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        var item=new ItemStack(ExpansionContent.SUPPLIES.get("regen_pill").get());p.getInventory().add(item.copy());
        var adv=p.server.getAdvancements().getAdvancement(new net.minecraft.resources.ResourceLocation("dynasty","cod4_obtain_regen_pill"));
        ContentProgress.reconcile(p);h.assertTrue(!p.getAdvancements().getOrStartProgress(adv).isDone(),"Inventory is not craft evidence");
        ContentProgress.crafted(new net.minecraftforge.event.entity.player.PlayerEvent.ItemCraftedEvent(p,item,new net.minecraft.world.SimpleContainer(9)));
        h.assertTrue(p.getAdvancements().getOrStartProgress(adv).isDone(),"Real craft hook advances original node");
        ContentProgress.reconcile(p);h.assertTrue(p.getAdvancements().getOrStartProgress(adv).isDone(),"Previously completed objective survives login reconciliation");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void qimenMerchantUnlocksBothMissingWeaponsWithPersistentStock(GameTestHelper h) {
        var p=player(h);h.assertTrue(new ProgressionMerchant(p).getOffers().isEmpty(),"No early shop unlock");
        p.getPersistentData().putInt("dynasty_rank",3);var merchant=new ProgressionMerchant(p);
        for(String id:List.of("meteor_hammer","mandarin_duck_axe")) {
            var offer=merchant.getOffers().stream().filter(o->o.getResult().is(ExpansionContent.item(id))).findFirst().orElseThrow();
            merchant.notifyTrade(offer);
            var restored=new ProgressionMerchant(p).getOffers().stream().filter(o->o.getResult().is(ExpansionContent.item(id))).findFirst().orElseThrow();
            h.assertTrue(restored.getUses()==1&&restored.getMaxUses()==8,"Stock persists across reopening "+id);
        }h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void feedbackPriorityKeepsImmunityAndArmorAboveOrdinaryHits(GameTestHelper h) {
        var n=new CompoundTag();n.putLong("cod4FeedbackTick",10);n.putInt("cod4FeedbackType",CombatFeedback.NORMAL);
        h.assertTrue(CombatFeedback.allowsFeedback(n,10,CombatFeedback.ARMOR),"Armor break can supersede ordinary hit");
        n.putInt("cod4FeedbackType",CombatFeedback.IMMUNE);
        h.assertTrue(!CombatFeedback.allowsFeedback(n,11,CombatFeedback.NORMAL)&&!CombatFeedback.allowsFeedback(n,11,CombatFeedback.IMMUNE),"Normal or duplicate immunity cannot spam/replace immunity");
        h.assertTrue(CombatFeedback.allowsFeedback(n,13,CombatFeedback.NORMAL),"Throttle eventually releases");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void herbTradeReturnsUsableMedicineIngredientOnce(GameTestHelper h) {
        var p=player(h);var mob=SecondaryMobs.TYPES.get("herb_picker").get().create(h.getLevel());
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.item("copper_coin"),2));
        mob.mobInteract(p,InteractionHand.MAIN_HAND);mob.mobInteract(p,InteractionHand.MAIN_HAND);
        h.assertTrue(p.getMainHandItem().getCount()==1&&p.getInventory().countItem(DynastyItems.TEA.get())==2,"One purchase returns two real tea herbs; cooldown prevents double charge");
        h.assertTrue(com.dynasty.workshop.WorkshopRecipes.ALL.stream().anyMatch(r->r.costs().stream().anyMatch(c->c.id().equals("dynasty:tea"))&&r.output().equals("dynasty:healing_salve")),"Harvested ingredient has existing medicinal use");h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void jadeForgeCleansesWithoutMutatingDepositedRecipe(GameTestHelper h) {
        var p=player(h);var pos=h.absolutePos(new BlockPos(3,2,3));var block=DynastyBlocks.JADE_MENDING_FORGE.get();
        h.getLevel().setBlockAndUpdate(pos,block.defaultBlockState());
        var vat=(com.dynasty.workshop.WorkshopBlockEntity)h.getLevel().getBlockEntity(pos);
        vat.accept(new ItemStack(DynastyItems.JADE.get()));int before=vat.deposited();
        p.addEffect(new MobEffectInstance(ExpansionEffects.BREAK.get(),100));p.setShiftKeyDown(true);
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.MATERIALS.get("sprite_jade").get(),2));
        var hit=new net.minecraft.world.phys.BlockHitResult(net.minecraft.world.phys.Vec3.atCenterOf(pos),net.minecraft.core.Direction.UP,pos,false);
        block.defaultBlockState().use(h.getLevel(),p,InteractionHand.MAIN_HAND,hit);
        h.assertTrue(!p.hasEffect(ExpansionEffects.BREAK.get())&&p.getMainHandItem().getCount()==1,"One jade cleanses once");
        h.assertTrue(vat.deposited()==before,"Cleansing cannot consume or reset deposited recipe");
        block.defaultBlockState().use(h.getLevel(),p,InteractionHand.MAIN_HAND,hit);
        h.assertTrue(p.getMainHandItem().getCount()==1,"No condition means no jade consumed");h.succeed();
    }

    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void cinnabarPurifiesOnlyNearbyAllies(GameTestHelper h) {
        var p=player(h);suit(p,"cinnabar",3);
        var ally=new Zombie(h.getLevel());ally.setNoAi(true);ally.setPos(p.position().add(1,0,0));h.getLevel().addFreshEntity(ally);
        var outsider=new Zombie(h.getLevel());outsider.setNoAi(true);outsider.setPos(p.position().add(1,0,1));h.getLevel().addFreshEntity(outsider);
        var far=new Zombie(h.getLevel());far.setNoAi(true);far.setPos(p.position().add(4,0,0));h.getLevel().addFreshEntity(far);
        var scoreboard=h.getLevel().getScoreboard();var team=scoreboard.addPlayerTeam("cod4-"+p.getId());
        scoreboard.addPlayerToTeam(p.getScoreboardName(),team);scoreboard.addPlayerToTeam(ally.getScoreboardName(),team);scoreboard.addPlayerToTeam(far.getScoreboardName(),team);
        for(var entity:List.of(p,ally,outsider,far))entity.addEffect(new MobEffectInstance(ExpansionEffects.SHA.get(),100));
        EquipmentBehaviors.purifyCinnabar(p);
        h.assertTrue(!p.hasEffect(ExpansionEffects.SHA.get())&&!ally.hasEffect(ExpansionEffects.SHA.get()),"Wearer and nearby ally are purified");
        h.assertTrue(outsider.hasEffect(ExpansionEffects.SHA.get())&&far.hasEffect(ExpansionEffects.SHA.get()),"Not an enemy cleanse and not infinite range");
        h.assertTrue(p.getPersistentData().getInt("cod4FeedbackType")==CombatFeedback.CINNABAR,"Dedicated cinnabar feedback dispatched");
        scoreboard.removePlayerTeam(team);ally.discard();outsider.discard();far.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void phoenixArmorExtinguishesAndReflectsOnlyInRange(GameTestHelper h) {
        var p=player(h);suit(p,"phoenix",4);p.setSecondsOnFire(5);
        var enemy=new Zombie(h.getLevel());enemy.setNoAi(true);enemy.setPos(p.position().add(1,0,0));h.getLevel().addFreshEntity(enemy);
        var event=new LivingAttackEvent(p,p.damageSources().onFire(),2);EquipmentBehaviors.attack(event);EquipmentBehaviors.refresh(p);
        h.assertTrue(event.isCanceled()&&!p.isOnFire()&&enemy.isOnFire(),"Extinguish, immunity and reflected fire stay connected");
        h.assertTrue(p.getPersistentData().getLong("cod4PhoenixSpeed")>p.level().getGameTime(),"Speed window is opened");
        h.assertTrue(p.getPersistentData().getInt("cod4FeedbackType")==CombatFeedback.FIRE_RING,"Visible fire ring packet uses dedicated pattern");
        enemy.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",timeoutTicks=20,batch="cod4")
    public static void stormCharmStrikesOnFirstProcWithoutBuildingMarks(GameTestHelper h) {
        var p=player(h);p.getInventory().add(new ItemStack(DynastyTrinkets.STORM_CHARM.get()));p.tickCount++;
        var target=new Zombie(h.getLevel());target.setPos(p.position().add(1,0,0));
        float rain=h.getLevel().getRainLevel(1),thunder=h.getLevel().getThunderLevel(1);
        try {
            h.getLevel().setRainLevel(1);h.getLevel().setThunderLevel(1);p.getRandom().setSeed(37);
            boolean sawProc=false;
            for(int i=0;i<80;i++) {
                var event=new LivingHurtEvent(target,p.damageSources().playerAttack(p),10);EquipmentBehaviors.hurt(event);
                h.assertTrue(event.getAmount()==10||event.getAmount()==14,"Small thunder is added exactly once to the current hit");
                if(event.getAmount()==14)sawProc=true;
            }
            h.assertTrue(sawProc&&!target.hasEffect(ExpansionEffects.THUNDER.get()),"First proc strikes without requiring three marks");
        } finally {h.getLevel().setRainLevel(rain);h.getLevel().setThunderLevel(thunder);}
        h.succeed();
    }
}
