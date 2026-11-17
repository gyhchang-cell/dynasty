package com.dynasty.expansion;

import com.dynasty.*;
import com.mojang.authlib.GameProfile;
import java.util.*;
import java.util.function.Consumer;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.effect.*;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.gametest.*;

/** Headless native ServerPlayer fixtures and explicit event-unit regressions; no human/GUI claim. */
@GameTestHolder("dynasty_armor_qa") @PrefixGameTestTemplate(false)
public final class ArmorAcceptanceGameTests {
    static final List<String> SETS=List.of("cloth","bamboo","leather","brocade","bronze","general","silver","jade","cinnabar","dragon_scale","phoenix","qilin","sea_silk","xuantian","sky","dark_iron","draco_king","xuanwu","zhuque","qinglong","baihu","beidou","tiangang","disha","taiyi","ziwei","hunyuan","hongmeng");
    private static ServerPlayer player(GameTestHelper h){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"armor-qa"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(6,52,6))));p.setNoGravity(true);p.getFoodData().setFoodLevel(17);
        // Let the original ServerPlayer spawn protection expire before testing real hurt/block input.
        for(int i=0;i<61;i++)p.tick();
        return p;
    }
    private static void suit(ServerPlayer p,String set,int count){
        var slots=new EquipmentSlot[]{EquipmentSlot.HEAD,EquipmentSlot.CHEST,EquipmentSlot.LEGS,EquipmentSlot.FEET};
        var names=new String[]{"helmet","chestplate","leggings","boots"};
        for(int i=0;i<4;i++)p.setItemSlot(slots[i],i<count?new ItemStack(ExpansionContent.item(set+"_"+names[i])):ItemStack.EMPTY);
    }
    private static void equipmentTick(ServerPlayer p){p.tick();p.doTick();}
    private static void cleanup(ServerPlayer p){p.stopUsingItem();net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent(p));DynastyTrinkets.forget(p);p.discard();}
    private static double[] attributes(ServerPlayer p){return new double[]{p.getAttributeValue(Attributes.MAX_HEALTH),p.getAttributeValue(Attributes.MOVEMENT_SPEED),p.getAttributeValue(Attributes.ARMOR),p.getAttributeValue(Attributes.ATTACK_DAMAGE),p.getAttributeValue(Attributes.LUCK),p.getAttributeValue(Attributes.KNOCKBACK_RESISTANCE),p.getAttributeValue(net.minecraftforge.common.ForgeMod.SWIM_SPEED.get())};}
    private static void same(GameTestHelper h,double[] a,double[] b,String message){for(int i=0;i<a.length;i++)h.assertTrue(Math.abs(a[i]-b[i])<.001,message+" attribute="+i+" "+a[i]+" vs "+b[i]);}
    private static TestFunction test(String name,Consumer<GameTestHelper> body){return new TestFunction("armor_"+name,"dynasty_armor_qa."+name,"dynasty_armor_qa:bow_ritual_test",160,20,true,body);}
    @GameTestGenerator public static Collection<TestFunction> matrix(){
        var result=new ArrayList<TestFunction>();
        for(String set:SETS)result.add(test("matrix_"+set,h->{
            var p=player(h);var other=player(h);h.getLevel().setDayTime(6000);h.getLevel().updateSkyBrightness();equipmentTick(p);equipmentTick(other);var baseline=attributes(p);var otherBase=attributes(other);
            try{
                // Foreign potion must survive every 2/3/4-piece equipment transition.
                p.addEffect(new MobEffectInstance(MobEffects.NIGHT_VISION,1200,2));
                for(int count:new int[]{2,3,4,3,2,0}){
                    suit(p,set,count);equipmentTick(p);p.setHealth(p.getMaxHealth());EquipmentBehaviors.refresh(p);
                    h.assertTrue(EquipmentBehaviors.pieces(p,set)==count,"Exact worn count for "+set+"/"+count);
                    var once=attributes(p);for(int i=0;i<3;i++)EquipmentBehaviors.refresh(p);
                    same(h,once,attributes(p),"Repeated refresh cannot stack "+set+"/"+count);
                    same(h,otherBase,attributes(other),"Second disconnected server actor unaffected "+set);
                    h.assertTrue(p.hasEffect(MobEffects.NIGHT_VISION)&&p.getEffect(MobEffects.NIGHT_VISION).getAmplifier()==2,"Foreign potion preserved "+set+"/"+count);
                }
                same(h,baseline,attributes(p),"Native equipment removal rolls back every armor attribute "+set);
                h.assertTrue(!p.hasEffect(MobEffects.JUMP)&&!p.hasEffect(MobEffects.DOLPHINS_GRACE),"No owned movement potion survives "+set);
                System.out.println("ARMOR_MATRIX_PASS set="+set+" counts=2,3,4,3,2,0 nativeEquipment=true repeatedRefresh=3 foreignPotion=preserved actorIsolation=disconnected-fixtures");h.succeed();
            }finally{cleanup(p);cleanup(other);}
        }));
        return result;
    }
    @GameTestGenerator public static Collection<TestFunction> inherited(){
        var r=new ArrayList<TestFunction>();
        // Invoke the existing test bodies without rewriting their mechanics or pretending FakePlayer is networking.
        r.add(test("existing_modifiers",ExpansionGameTests::armorModifiersAreIdempotentAndImmediatelyRemoved));
        r.add(test("existing_owner_cooldowns",ExpansionGameTests::armorStateDoesNotLeakBetweenPlayers));
        r.add(test("existing_last_stand",ExpansionGameTests::lastStandCooldownPersistsAndDoesNotBlockKillCommand));
        r.add(test("existing_sky_potions",ExpansionGameTests::skyJumpTwoIsOwnedAndStrongerPotionsSurvive));
        r.add(test("existing_qilin",ExpansionGameTests::qilinProcPreventsWholeHitAndNeverAdministrativeKill));
        r.add(test("existing_star_steps",ExpansionGameTests::starStepRequiresContinuityAndUnequipRevokesWindow));
        r.add(test("existing_phoenix_ring",ExpansionGameTests::phoenixWindowSurvivesExtinguishingAndExpires));
        r.add(test("existing_cinnabar",ExpansionGameTests::cinnabarPurifiesOnlyNearbyAllies));
        r.add(test("existing_phoenix_armor",ExpansionGameTests::phoenixArmorExtinguishesAndReflectsOnlyInRange));
        r.add(test("existing_brocade",ExpansionGameTests::examRobeAndWineShareOneDeadlineBonus));
        r.add(test("existing_qi_pill",ExpansionGameTests::qiPillUsesSharedComboAndRestoresNormalAdvance));
        r.add(test("existing_taiyi",Cod4ContinuationGameTests::taiyiReducesExistingFluteSkillAndGlowHasRealRequirements));
        r.add(test("existing_perfect_guard",EquipmentGuardGameTests::perfectGuardUsesSixActualBlockingTicksAfterSchoolReduction));
        r.add(test("existing_guard_lease",EquipmentGuardGameTests::dragonArmorLeasesShrimpThenCrabAndNeverDuplicates));
        r.add(test("existing_hunyuan",EquipmentGuardGameTests::hunyuanNeutralisationAndRageFeedExistingQiWithUnequipCleanup));
        r.add(test("existing_qinglong",EquipmentGuardGameTests::fifthComboWaveReturnsExistingQiOnceAndResetsOnUnequip));
        r.add(test("existing_blocked_guard",EquipmentGuardGameTests::blockedWaterSpawnDoesNotConsumeLeaseAndCanRetry));
        r.add(test("existing_guard_pair",EquipmentGuardGameTests::partlyBlockedPairDoesNotLeaseOneGuardOrOverlapAndCanRetry));
        r.add(test("existing_native_guard",PerfectBlockNativeGameTests::actualFrontBlockedDamageClearsStaggerOnShieldGuardBladeAndPairedAxesWithoutSuitGate));
        r.add(test("existing_native_guard_controls",PerfectBlockNativeGameTests::actualRearLateAndCanceledBlocksLeaveLiveStaggerWhileFirstValidFrontBlockClearsIt));
        return r;
    }
    @GameTestGenerator public static Collection<TestFunction> regressions(){
        var r=new ArrayList<TestFunction>();
        for(String set:List.of("cloth","bronze","phoenix","ziwei"))r.add(test("window_"+set,h->window(h,set)));
        r.add(test("duck_offhand_revokes_counter",h->counter(h,false)));
        r.add(test("xuanwu_counter_cannot_transfer_to_duck",h->counter(h,true)));
        r.add(test("star_immunity_reads_live_gear",ArmorAcceptanceGameTests::star));
        r.add(test("native_last_stand_save_swap_owner",ArmorAcceptanceGameTests::lastStand));
        r.add(test("owned_counter_original_damage_once",ArmorAcceptanceGameTests::ownedCounter));
        r.add(test("unworn_bronze_cannot_prestore_window",ArmorAcceptanceGameTests::unwornBronze));
        r.add(test("other_fire_set_cannot_prestore_phoenix_window",ArmorAcceptanceGameTests::unwornPhoenix));
        return r;
    }
    private static void window(GameTestHelper h,String set){
        var p=player(h);var target=new Zombie(h.getLevel());suit(p,set,4);equipmentTick(p);
        String key=switch(set){case "cloth"->"cod4Rested";case "bronze"->"cod4BronzeGuard";case "phoenix"->"cod4PhoenixSpeed";default->"cod4Crit";};
        try{
            switch(set){
                case "cloth"->EquipmentBehaviors.wake(new net.minecraftforge.event.entity.player.PlayerWakeUpEvent(p,false,false));
                case "bronze"->EquipmentBehaviors.block(new ShieldBlockEvent(p,p.damageSources().mobAttack(target),10));
                case "phoenix"->p.hurt(p.damageSources().onFire(),2);
                default->{p.getRandom().setSeed(17);for(int i=0;i<100&&!p.getPersistentData().contains(key);i++)EquipmentBehaviors.hurt(new LivingHurtEvent(target,p.damageSources().playerAttack(p),10));}
            }
            h.assertTrue(p.getPersistentData().getLong(key)>EquipmentBehaviors.now(p),"Original trigger opens "+key);
            suit(p,set,2);equipmentTick(p);
            h.assertTrue(!p.getPersistentData().contains(key),"Dropping below three pieces must revoke "+key);
            suit(p,set,4);equipmentTick(p);h.assertTrue(!p.getPersistentData().contains(key),"Re-equipping cannot revive "+key);h.succeed();
        }finally{cleanup(p);}
    }
    private static void counter(GameTestHelper h,boolean armor){
        var p=player(h);var attacker=new Zombie(h.getLevel());attacker.setPos(p.position().add(1,0,0));p.setYRot(-90);
        try{
            if(armor)suit(p,"xuanwu",2);
            p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(armor?Items.SHIELD:ExpansionContent.DUCK.get()));
            if(!armor)p.setItemInHand(InteractionHand.OFF_HAND,new ItemStack(ExpansionContent.DUCK.get()));
            equipmentTick(p);p.startUsingItem(InteractionHand.MAIN_HAND);for(int i=0;i<5;i++)p.doTick();
            p.hurt(p.damageSources().mobAttack(attacker),10);p.stopUsingItem();
            h.assertTrue(p.getPersistentData().contains("cod4Counter"),"Actual native front block opens original counter");
            if(armor){suit(p,"xuanwu",0);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(ExpansionContent.DUCK.get()));p.setItemInHand(InteractionHand.OFF_HAND,new ItemStack(ExpansionContent.DUCK.get()));}
            else p.setItemInHand(InteractionHand.OFF_HAND,ItemStack.EMPTY);
            equipmentTick(p);h.assertTrue(!p.getPersistentData().contains("cod4Counter"),"Lost original grant cannot survive through other gear");
            var event=new LivingHurtEvent(attacker,p.damageSources().playerAttack(p),100);EquipmentBehaviors.hurt(event);
            h.assertTrue(Math.abs(event.getAmount()-100)<.001,"Revoked counter never adds damage");h.succeed();
        }finally{cleanup(p);}
    }
    private static void star(GameTestHelper h){
        var p=player(h);suit(p,"beidou",4);equipmentTick(p);p.setSprinting(true);
        try{
            for(int i=0;i<10;i++)EquipmentBehaviors.advanceStarStep(p,.25);
            h.assertTrue(p.getPersistentData().getLong("cod4StarIFrame")>EquipmentBehaviors.now(p),"Real stride grant active");
            var active=new LivingAttackEvent(p,p.damageSources().generic(),10);EquipmentBehaviors.attack(active);h.assertTrue(active.isCanceled(),"Four pieces protect");
            suit(p,"beidou",3); // Test the real interval before LivingEntity dispatches equipment change.
            var removed=new LivingAttackEvent(p,p.damageSources().generic(),10);EquipmentBehaviors.attack(removed);
            h.assertTrue(!removed.isCanceled(),"Live three-piece damage cannot borrow the old four-piece iframe");h.succeed();
        }finally{cleanup(p);}
    }
    private static void lastStand(GameTestHelper h){
        var p=player(h);var other=player(h);var reloaded=player(h);var boss=DynastyEntitiesForQa.boss(h);
        try{
            suit(p,"zhuque",4);equipmentTick(p);p.setHealth(5);p.invulnerableTime=0;
            p.hurt(p.damageSources().mobAttack(boss),100000);
            long until=EquipmentBehaviors.saved(p).getLong("lastStand");
            h.assertTrue(p.isAlive()&&until==EquipmentBehaviors.now(p)+6000,"Native boss-source lethal hit gives one 300-second lease");
            suit(p,"hongmeng",4);equipmentTick(p);h.assertTrue(!EquipmentBehaviors.ready(p,"lastStand",6000),"Armor swap cannot reset shared life-saving cooldown");
            CompoundTag disk=p.saveWithoutId(new CompoundTag());reloaded.load(disk);
            h.assertTrue(EquipmentBehaviors.saved(reloaded).getLong("lastStand")==until&&!EquipmentBehaviors.ready(reloaded,"lastStand",6000),"Native player NBT save/read retains exact expiry");
            h.assertTrue(EquipmentBehaviors.ready(other,"lastStand",6000),"Separate disconnected actor owns separate cooldown");
            var kill=new LivingDamageEvent(p,p.damageSources().genericKill(),99999);EquipmentBehaviors.damage(kill);h.assertTrue(kill.getAmount()==99999,"Administrative kill bypass remains");h.succeed();
        }finally{cleanup(p);cleanup(other);cleanup(reloaded);boss.discard();}
    }
    private static void ownedCounter(GameTestHelper h){
        for(int count:new int[]{2,3,4}){
            var p=player(h);var enemy=new Zombie(h.getLevel());enemy.setPos(p.position().add(1,0,0));
            try{
                suit(p,"xuanwu",count);equipmentTick(p);p.setYRot(-90);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.SHIELD));p.startUsingItem(InteractionHand.MAIN_HAND);
                for(int i=0;i<5;i++)p.doTick();p.hurt(p.damageSources().mobAttack(enemy),20);p.stopUsingItem();
                h.assertTrue(p.getPersistentData().getString("cod4CounterSource").equals("xuanwu"),"Native perfect block stamps its real source /"+count);
                var first=new LivingHurtEvent(enemy,p.damageSources().playerAttack(p),100);EquipmentBehaviors.hurt(first);
                h.assertTrue(Math.abs(first.getAmount()-(count>=3?120:110))<.001,"Original 10/20 percent counter remains /"+count);
                var second=new LivingHurtEvent(enemy,p.damageSources().playerAttack(p),100);EquipmentBehaviors.hurt(second);
                h.assertTrue(second.getAmount()==100&&!p.getPersistentData().contains("cod4CounterSource"),"Counter damage settles exactly once /"+count);
            }finally{cleanup(p);}
        }h.succeed();
    }
    private static void unwornBronze(GameTestHelper h){
        var p=player(h);var enemy=new Zombie(h.getLevel());
        try{
            EquipmentBehaviors.block(new ShieldBlockEvent(p,p.damageSources().mobAttack(enemy),10));
            suit(p,"bronze",3);equipmentTick(p);
            h.assertTrue(!p.getPersistentData().contains("cod4BronzeGuard"),"Blocking before equipping bronze cannot bank its armor window");h.succeed();
        }finally{cleanup(p);}
    }
    private static void unwornPhoenix(GameTestHelper h){
        var p=player(h);suit(p,"zhuque",2);equipmentTick(p);
        try{
            p.hurt(p.damageSources().onFire(),2);suit(p,"phoenix",3);equipmentTick(p);
            h.assertTrue(!p.getPersistentData().contains("cod4PhoenixSpeed"),"Zhuque fire immunity cannot bank a future Phoenix speed window");h.succeed();
        }finally{cleanup(p);}
    }
    private static final class DynastyEntitiesForQa {
        static LivingEntity boss(GameTestHelper h){return com.dynasty.entity.DynastyEntities.REBEL_GENERAL.get().create(h.getLevel());}
    }
}
