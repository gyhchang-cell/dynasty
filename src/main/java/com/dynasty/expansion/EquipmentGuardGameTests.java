package com.dynasty.expansion;

import com.dynasty.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.ShieldBlockEvent;
import net.minecraftforge.gametest.*;
import java.util.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class EquipmentGuardGameTests {
    private static ServerPlayer player(GameTestHelper h){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"equipment-guard"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(6,2,6))));p.setNoGravity(true);return p;
    }
    private static void suit(ServerPlayer p,String id,int count){
        EquipmentSlot[] slots={EquipmentSlot.HEAD,EquipmentSlot.CHEST,EquipmentSlot.LEGS,EquipmentSlot.FEET};String[] names={"helmet","chestplate","leggings","boots"};
        for(int i=0;i<slots.length;i++)p.setItemSlot(slots[i],i<count?new ItemStack(ExpansionContent.item(id+"_"+names[i])):ItemStack.EMPTY);
    }
    @GameTest(template="bow_ritual_test",batch="cod4_perfect_guard")
    public static void perfectGuardUsesSixActualBlockingTicksAfterSchoolReduction(GameTestHelper h){
        var p=player(h);suit(p,"xuanwu",2);for(int i=0;i<60;i++)p.tick();
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyWeapons.ZHENYUE_BLADE.get()));p.setYRot(-90);p.startUsingItem(InteractionHand.MAIN_HAND);
        try{
            h.assertTrue(!EquipmentBehaviors.perfectGuard(p),"Unraised weapon cannot grant perfect guard");
            for(int i=0;i<5;i++)p.doTick();
            var source=p.damageSources().mobAttack(new Zombie(h.getLevel()));
            h.assertTrue(p.isBlocking()&&EquipmentBehaviors.perfectGuard(p),"Window starts at the first real block frame: ticks="+p.getTicksUsingItem()+", blocking="+p.isBlocking()+", using="+p.isUsingItem()+", item="+p.getUseItem());
            var event=new ShieldBlockEvent(p,source,20);net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(event);
            h.assertTrue(Math.abs(event.getBlockedDamage()-12)<.01,"School's 50% block becomes an actual 60% original-hit block after event ordering");
            // Isolate armor in this health-delta comparison while retaining the real equipped IDs.
            p.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.ARMOR).removeModifiers();
            p.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.ARMOR_TOUGHNESS).removeModifiers();
            var front=new Zombie(h.getLevel());front.setPos(p.position().add(1,0,0));var rear=new Zombie(h.getLevel());rear.setPos(p.position().add(-1,0,0));
            // Keep both samples above the global one-point damage floor and below the health cap.
            p.getAttribute(net.minecraft.world.entity.ai.attributes.Attributes.MAX_HEALTH).setBaseValue(500);p.setHealth(500);
            p.invulnerableTime=0;float health=p.getHealth();p.hurt(p.damageSources().mobAttack(front),40);float guarded=health-p.getHealth();
            p.invulnerableTime=0;health=p.getHealth();p.hurt(p.damageSources().mobAttack(rear),40);float unguarded=health-p.getHealth();
            h.assertTrue(guarded>0&&unguarded>0&&Math.abs(guarded/unguarded-.4F)<.01,"Actual front health loss is forty percent of the same rear hit: "+guarded+" / "+unguarded);
            for(int i=0;i<5;i++)p.doTick();
            h.assertTrue(EquipmentBehaviors.perfectGuard(p),"The sixth active blocking tick remains perfect");p.doTick();
            h.assertTrue(!EquipmentBehaviors.perfectGuard(p),"Seventh active blocking tick ends the window");
            var late=new ShieldBlockEvent(p,source,20);net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(late);
            h.assertTrue(Math.abs(late.getBlockedDamage()-10)<.01,"After the window, normal school block remains fifty percent");
            p.stopUsingItem();p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.SHIELD));p.startUsingItem(InteractionHand.MAIN_HAND);for(int i=0;i<5;i++)p.doTick();
            var shield=new ShieldBlockEvent(p,source,20);net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(shield);
            h.assertTrue(shield.getBlockedDamage()==20,"A fully blocking vanilla shield is never reduced to sixty percent");
            h.succeed();
        }finally{p.stopUsingItem();net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent(p));DynastyTrinkets.forget(p);p.discard();}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_sea_guards",timeoutTicks=100)
    public static void dragonArmorLeasesShrimpThenCrabAndNeverDuplicates(GameTestHelper h){
        for(int x=2;x<=11;x++)for(int z=2;z<=11;z++){h.setBlock(x,1,z,Blocks.STONE);h.setBlock(x,2,z,Blocks.WATER);h.setBlock(x,3,z,Blocks.WATER);}
        var p=player(h);h.getLevel().addNewPlayer(p);suit(p,"draco_king",3);p.baseTick();
        var owned=new ArrayList<SecondaryMob>();
        try{
            h.assertTrue(p.isInWater(),"Fixture is genuinely submerged");SummonedGuard.maintain(p,99);
            var first=h.getLevel().getEntitiesOfClass(SecondaryMob.class,p.getBoundingBox().inflate(8),m->m.getPersistentData().hasUUID("cod4Summoner")&&m.getPersistentData().getUUID("cod4Summoner").equals(p.getUUID()));owned.addAll(first);
            h.assertTrue(first.size()==1&&first.get(0).getType()==SecondaryMobs.SHRIMP.get(),"Three pieces enforce one shrimp even with an oversized request: count="+first.size()+", pieces="+EquipmentBehaviors.pieces(p,"draco_king")+", wet="+p.isInWater()+", lease="+EquipmentBehaviors.saved(p));
            SummonedGuard.maintain(p,2);h.assertTrue(h.getLevel().getEntitiesOfClass(SecondaryMob.class,p.getBoundingBox().inflate(8),m->m.getPersistentData().hasUUID("cod4Summoner")).size()==1,"Same saved lease cannot duplicate a guard");
            suit(p,"draco_king",4);EquipmentBehaviors.saved(p).putLong("guardsUntil",0);SummonedGuard.maintain(p,2);
            SummonedGuard.tick(first.get(0));h.assertTrue(first.get(0).isRemoved(),"A previous generation carrier loses authority");
            var next=h.getLevel().getEntitiesOfClass(SecondaryMob.class,p.getBoundingBox().inflate(8),m->m.getPersistentData().hasUUID("cod4Summoner")&&!m.isRemoved());owned.addAll(next);
            h.assertTrue(next.size()==2&&next.stream().anyMatch(m->m.getType()==SecondaryMobs.SHRIMP.get())&&next.stream().anyMatch(m->m.spec.id().equals("crab_soldier")),"Four pieces form a shrimp/crab pair");
            suit(p,"draco_king",3);for(var guard:next)SummonedGuard.tick(guard);
            h.assertTrue(next.stream().filter(m->!m.isRemoved()).count()==1&&next.stream().filter(m->!m.isRemoved()).allMatch(m->m.getType()==SecondaryMobs.SHRIMP.get()),"Unequipping the fourth piece immediately removes only the crab");
            suit(p,"draco_king",0);for(var guard:next)if(!guard.isRemoved())SummonedGuard.tick(guard);
            h.assertTrue(next.stream().allMatch(Entity::isRemoved),"Unequipping the set releases every temporary guard");h.succeed();
        }finally{owned.forEach(Entity::discard);h.getLevel().removePlayerImmediately(p,Entity.RemovalReason.DISCARDED);}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_hunyuan_qi")
    public static void hunyuanNeutralisationAndRageFeedExistingQiWithUnequipCleanup(GameTestHelper h){
        var p=player(h);suit(p,"hunyuan",4);
        try{
            ExpansionEffects.apply(p,ExpansionEffects.YANG,100);
            h.assertTrue(!EquipmentBehaviors.balanced(p),"Yang alone is not balance");
            ExpansionEffects.apply(p,ExpansionEffects.YIN,100);
            h.assertTrue(EquipmentBehaviors.balanced(p),"Opposing Qi really neutralises into a finite balance window");
            var target=new Zombie(h.getLevel());var event=new net.minecraftforge.event.entity.living.LivingHurtEvent(target,p.damageSources().playerAttack(p),100);
            EquipmentBehaviors.hurt(event);h.assertTrue(Math.abs(event.getAmount()-110)<.01,"Neutral balance adds the promised ten percent to the original hit");
            p.getPersistentData().putInt("cod4Rage",4);h.assertTrue(!EquipmentBehaviors.releaseHunyuanQi(p),"Four rage cannot release five-rage Qi");
            p.getPersistentData().putInt("cod4Rage",5);h.assertTrue(EquipmentBehaviors.releaseHunyuanQi(p)&&EquipmentBehaviors.qiActive(p)&&p.getPersistentData().getInt("cod4Rage")==0,"Five rage releases the original combo Qi and is spent once");
            p.getPersistentData().putInt("cod4Rage",5);h.assertTrue(!EquipmentBehaviors.releaseHunyuanQi(p),"Cooldown cannot be bypassed by refilling rage");
            suit(p,"hunyuan",0);EquipmentBehaviors.refresh(p);h.assertTrue(!EquipmentBehaviors.balanced(p)&&!EquipmentBehaviors.qiActive(p),"Unequipping drops both equipment grants");
            p.getPersistentData().putLong("cod4QiUntil",EquipmentBehaviors.now(p)+200);EquipmentBehaviors.refresh(p);
            h.assertTrue(EquipmentBehaviors.qiActive(p),"Independent pill Qi survives removing an equipment grant");h.succeed();
        }finally{DynastyTrinkets.forget(p);p.discard();}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_qinglong_qi",timeoutTicks=100)
    public static void fifthComboWaveReturnsExistingQiOnceAndResetsOnUnequip(GameTestHelper h){
        var p=player(h);suit(p,"qinglong",4);var target=new Zombie(h.getLevel());
        h.assertTrue(!EquipmentBehaviors.comboWave(p,target,4)&&!EquipmentBehaviors.qiActive(p),"Four stacks do not manufacture a full-combo grant");
        h.assertTrue(EquipmentBehaviors.comboWave(p,target,5)&&EquipmentBehaviors.qiActive(p),"Fifth stack grants three seconds of the shared combo Qi");
        h.assertTrue(!EquipmentBehaviors.comboWave(p,target,5),"Repeated full-stack events do not replay the wave or refresh the grant");
        h.assertTrue(DynastyTrinketOnHit.advanceCombo(p,target)==1,"Original shared combo starts at one");
        h.runAfterDelay(2,()->{try{
            h.assertTrue(DynastyTrinketOnHit.advanceCombo(p,target)==3,"Actual returned Qi advances the existing combo by two");
            suit(p,"qinglong",3);EquipmentBehaviors.refresh(p);h.assertTrue(!EquipmentBehaviors.qiActive(p),"Losing the fourth piece immediately stops equipment Qi");h.succeed();
        }finally{net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent(p));DynastyTrinkets.forget(p);p.discard();}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_blocked_sea_guard")
    public static void blockedWaterSpawnDoesNotConsumeLeaseAndCanRetry(GameTestHelper h){
        for(int x=2;x<=10;x++)for(int z=2;z<=10;z++)for(int y=1;y<=4;y++)h.setBlock(x,y,z,Blocks.STONE);
        h.setBlock(6,2,6,Blocks.WATER);h.setBlock(6,3,6,Blocks.WATER);var p=player(h);h.getLevel().addNewPlayer(p);suit(p,"draco_king",3);p.baseTick();
        try{
            SummonedGuard.maintain(p,1);h.assertTrue(EquipmentBehaviors.saved(p).getLong("guardsUntil")==0,"No safe water tile cannot consume thirty seconds of lease");
            h.setBlock(5,2,6,Blocks.WATER);h.setBlock(5,3,6,Blocks.WATER);SummonedGuard.maintain(p,1);
            var guards=h.getLevel().getEntitiesOfClass(SecondaryMob.class,p.getBoundingBox().inflate(8),m->m.getPersistentData().hasUUID("cod4Summoner")&&m.getPersistentData().getUUID("cod4Summoner").equals(p.getUUID()));
            h.assertTrue(guards.size()==1&&guards.get(0).getType()==SecondaryMobs.SHRIMP.get(),"Opening a nearby water tile immediately retries once without resetting the clock");
            guards.forEach(Entity::discard);h.succeed();
        }finally{h.getLevel().removePlayerImmediately(p,Entity.RemovalReason.DISCARDED);}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_weapon_provenance")
    public static void revengeBonusesUseActualDropsAndCanonicalGiftProgress(GameTestHelper h){
        var p=player(h);var zombie=new Zombie(h.getLevel());var phoenix=com.dynasty.entity.DynastyEntities.PHOENIX.get().create(h.getLevel());
        var rebel=com.dynasty.entity.DynastyEntities.REBEL_GENERAL.get().create(h.getLevel());var n=p.getPersistentData();
        try{
            n.putBoolean("dynasty_firstkill_dragon_king",true);h.assertTrue(EquipmentBehaviors.revengeBonus(p,zombie,"dragon_spear")==0,"A dragon-king kill is not the dragon spear's real source");
            n.putBoolean("dynasty_firstkill_undead_first_emperor",true);h.assertTrue(EquipmentBehaviors.revengeBonus(p,zombie,"dragon_spear")==.15F,"First-Emperor drop counters the actual undead faction");
            n.putBoolean("dynasty_firstkill_nine_heaven_general",true);h.assertTrue(EquipmentBehaviors.revengeBonus(p,phoenix,"sunbow")==0,"Unrelated sky boss does not unlock the phoenix gift");
            n.putBoolean("dynasty_gift_sunbow",true);h.assertTrue(EquipmentBehaviors.revengeBonus(p,phoenix,"sunbow")==.15F,"Daytime phoenix gift uses its canonical one-time flag");
            h.assertTrue(EquipmentBehaviors.revengeBonus(p,zombie,"seven_star_saber")==0,"One defeated boss is not the five-kind achievement");
            n.putInt("dynasty_boss_kinds",5);n.putString("dynasty_boss_kinds_list","dragon_emperor,rebel_general,eunuch_mastermind,undead_first_emperor,dragon_king");
            h.assertTrue(EquipmentBehaviors.revengeBonus(p,zombie,"seven_star_saber")==.15F,"Five-kind achievement recognises factions actually defeated");
            n.putBoolean("dynasty_firstkill_dragon_emperor",true);h.assertTrue(EquipmentBehaviors.revengeBonus(p,rebel,"supreme_sword")==0,"Dragon Emperor does not replace court rank");
            n.putBoolean("dynasty_gift_supreme_sword",true);h.assertTrue(EquipmentBehaviors.revengeBonus(p,rebel,"supreme_sword")==.15F,"Canonical court gift counters court enemies");h.succeed();
        }finally{DynastyTrinkets.forget(p);p.discard();}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_atomic_guard_pair")
    public static void partlyBlockedPairDoesNotLeaseOneGuardOrOverlapAndCanRetry(GameTestHelper h){
        for(int x=2;x<=10;x++)for(int z=2;z<=10;z++)for(int y=1;y<=4;y++)h.setBlock(x,y,z,Blocks.STONE);
        for(int x:new int[]{5,6})for(int y=2;y<=3;y++)h.setBlock(x,y,6,Blocks.WATER);
        var p=player(h);h.getLevel().addNewPlayer(p);suit(p,"draco_king",4);p.baseTick();
        try{
            SummonedGuard.maintain(p,2);
            var guards=h.getLevel().getEntitiesOfClass(SecondaryMob.class,p.getBoundingBox().inflate(8),m->m.getPersistentData().hasUUID("cod4Summoner")&&m.getPersistentData().getUUID("cod4Summoner").equals(p.getUUID()));
            h.assertTrue(guards.isEmpty()&&EquipmentBehaviors.saved(p).getLong("guardsUntil")==0,"A single safe tile cannot consume a pair lease or spawn overlapping carriers");
            for(int y=2;y<=3;y++)h.setBlock(7,y,6,Blocks.WATER);SummonedGuard.maintain(p,2);
            guards=h.getLevel().getEntitiesOfClass(SecondaryMob.class,p.getBoundingBox().inflate(8),m->m.getPersistentData().hasUUID("cod4Summoner")&&m.getPersistentData().getUUID("cod4Summoner").equals(p.getUUID()));
            h.assertTrue(guards.size()==2&&!guards.get(0).getBoundingBox().intersects(guards.get(1).getBoundingBox()),"Opening a second tile immediately creates the complete non-overlapping pair");
            guards.forEach(Entity::discard);h.succeed();
        }finally{h.getLevel().removePlayerImmediately(p,Entity.RemovalReason.DISCARDED);}
    }
    private EquipmentGuardGameTests(){}
}
