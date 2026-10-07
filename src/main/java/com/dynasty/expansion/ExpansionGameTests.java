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
        int count=p.getInventory().countItem(ExpansionContent.MATERIALS.get("qimen_gear").get());
        block.defaultBlockState().use(h.getLevel(),p,InteractionHand.MAIN_HAND,hit);
        h.assertTrue(count==1&&p.getInventory().countItem(ExpansionContent.MATERIALS.get("qimen_gear").get())==1,"Only one reward despite repeated clicks");h.succeed();
    }
}
