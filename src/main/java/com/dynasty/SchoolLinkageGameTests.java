package com.dynasty;

import com.dynasty.expansion.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.ShieldBlockEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.gametest.*;
import java.util.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class SchoolLinkageGameTests {
    private static ServerPlayer player(GameTestHelper h) {
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"school-link"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(6,2,6))));p.setNoGravity(true);h.getLevel().addNewPlayer(p);return p;
    }
    private static void equip(ServerPlayer p,String slot,ItemStack stack) {
        if(DynastyCuriosSetup.isLoaded())SchoolCombatGameTests.equip(p,slot,stack);
        else {
            int index=switch(slot){case "body"->9;case "bracelet"->10;case "charm"->11;case "back"->12;default->throw new IllegalArgumentException(slot);};
            p.getInventory().setItem(index,stack);DynastyTrinkets.forget(p);
        }
    }
    private static void close(GameTestHelper h,ServerPlayer p){
        DynastySchoolCombat.forget(p);DynastyTrinkets.forget(p);h.getLevel().removePlayerImmediately(p,Entity.RemovalReason.DISCARDED);
    }
    @GameTest(template="bow_ritual_test",batch="cod4_school_guard")
    public static void bothGuardWeaponsBlockRealFrontHitsAndSynergyOnlyChangesBlockedPart(GameTestHelper h){
        var p=player(h);var front=new Zombie(h.getLevel());front.setPos(p.position().add(1,0,0));
        var rear=new Zombie(h.getLevel());rear.setPos(p.position().add(-1,0,0));
        try{
            for(int i=0;i<60;i++)p.tick();p.getAttribute(Attributes.MAX_HEALTH).setBaseValue(500);p.setHealth(500);p.setYRot(-90);
            for(Item item:new Item[]{DynastyWeapons.ZHENYUE_BLADE.get(),DynastyWeapons.BEICHEN_SPEAR.get()}){
                equip(p,"body",ItemStack.EMPTY);equip(p,"bracelet",ItemStack.EMPTY);
                p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(item));p.startUsingItem(InteractionHand.MAIN_HAND);for(int i=0;i<12;i++)p.doTick();
                h.assertTrue(p.isBlocking(),"Registered item reaches a real raised weapon block: "+item);
                var event=new ShieldBlockEvent(p,p.damageSources().mobAttack(front),40);net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(event);
                h.assertTrue(Math.abs(event.getBlockedDamage()-20)<.001,"Baseline actual block is one half");
                equip(p,"body",new ItemStack(ExpansionContent.item("zhenguan_mirror")));
                equip(p,"bracelet",new ItemStack(ExpansionContent.item("huben_bracer")));
                h.assertTrue(DynastySchoolProgression.equippedSynergy(p,"guard"),"Two real guard ornaments activate the same canonical predicate");
                event=new ShieldBlockEvent(p,p.damageSources().mobAttack(front),40);net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(event);
                h.assertTrue(Math.abs(event.getBlockedDamage()-23.2F)<.001,"Extra eight percent is added to the actual blocked portion after the school hook");
                p.getAttribute(Attributes.ARMOR).removeModifiers();p.getAttribute(Attributes.ARMOR_TOUGHNESS).removeModifiers();
                p.setYRot(-90);front.setPos(p.position().add(1,0,0));rear.setPos(p.position().add(-1,0,0));
                h.assertTrue(p.isBlocking(),"Weapon remains actively raised before the actual health comparison: useTicks="+p.getTicksUsingItem()+", item="+p.getUseItem());
                p.invulnerableTime=0;float health=p.getHealth();p.hurt(p.damageSources().mobAttack(front),40);float guarded=health-p.getHealth();
                p.invulnerableTime=0;health=p.getHealth();p.hurt(p.damageSources().mobAttack(rear),40);float unguarded=health-p.getHealth();
                h.assertTrue(guarded>0&&unguarded>0&&Math.abs(guarded/unguarded-.42F)<.01,"Actual front health loss uses the enhanced block, while rear hits get no phantom block: "+guarded+" / "+unguarded+", yaw="+p.getYRot()+", blocking="+p.isBlocking()+", ticks="+p.getTicksUsingItem());
                equip(p,"bracelet",ItemStack.EMPTY);
                event=new ShieldBlockEvent(p,p.damageSources().mobAttack(front),40);net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(event);
                h.assertTrue(Math.abs(event.getBlockedDamage()-20)<.001,"Removing one ornament immediately restores normal blocking");p.stopUsingItem();
            }
            h.succeed();
        }finally{close(h,p);}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_talisman_window")
    public static void bothTalismanWeaponsReuseOneExtendedWindowAndDropItOnSwap(GameTestHelper h){
        var p=player(h);
        try{
            for(Item item:new Item[]{DynastyWeapons.CHILING_BRUSH.get(),DynastyWeapons.LEIFU_STAFF.get()}){
                p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(item));
                equip(p,"charm",ItemStack.EMPTY);equip(p,"back",ItemStack.EMPTY);
                DynastySchoolCombat.finishSpellCharge(p,true);
                h.assertTrue(DynastySchoolCombat.state(p).edictUntil==h.getLevel().getGameTime()+80,"Original window is shared by both existing weapons");
                equip(p,"charm",new ItemStack(ExpansionContent.item("sitian_seal")));
                equip(p,"back",new ItemStack(ExpansionContent.item("dingfeng_silk")));
                h.assertTrue(DynastySchoolProgression.equippedSynergy(p,"talisman"),"Real talisman ornaments activate synergy");
                EdictSpells.resolve(p,3,p.getEyePosition(),p.position());
                h.assertTrue(DynastySchoolCombat.state(p).edictUntil==h.getLevel().getGameTime()+96,"Completing the actual spell resolution opens the twenty-percent-longer original ready window");
                h.assertTrue(DynastySchoolCombat.consumeSpellWindow(p)==1.5F&&DynastySchoolCombat.consumeSpellWindow(p)==1,"One window cannot amplify two short spells");
                DynastySchoolCombat.finishSpellCharge(p,false);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.STICK));
                DynastySchoolCombat.tick(new TickEvent.PlayerTickEvent(TickEvent.Phase.END,p));p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(item));
                h.assertTrue(DynastySchoolCombat.consumeSpellWindow(p)==1,"Swap out and back cannot resurrect a previous window");
            }
            h.succeed();
        }finally{close(h,p);}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_symbol_mechanics")
    public static void matchingSymbolsAddActualBlockBurnBreakAndFiniteDragonWave(GameTestHelper h){
        var p=player(h);var z=new Zombie(h.getLevel());z.setPos(p.position().add(1,0,0));
        try{
            p.setItemSlot(EquipmentSlot.HEAD,new ItemStack(ExpansionContent.item("xuanwu_helmet")));
            p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyWeapons.XUANWU_BLADE.get()));p.startUsingItem(InteractionHand.MAIN_HAND);for(int i=0;i<12;i++)p.doTick();
            h.assertTrue(p.isBlocking(),"Xuanwu blade has a real native block input");
            var block=new ShieldBlockEvent(p,p.damageSources().mobAttack(z),40);net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(block);
            h.assertTrue(Math.abs(block.getBlockedDamage()-24)<.001,"Matching Xuanwu boosts actual block beyond the generic damage ratio");p.stopUsingItem();
            p.setItemSlot(EquipmentSlot.HEAD,new ItemStack(ExpansionContent.item("zhuque_helmet")));
            EquipmentBehaviors.symbolHit(p,z,new ItemStack(DynastyWeapons.ZHUQUE_BOW.get()));h.assertTrue(z.isOnFire(),"Real firing-weapon provenance can apply Zhuque fire");z.clearFire();
            EquipmentBehaviors.symbolHit(p,z,new ItemStack(DynastyWeapons.ZHUQUE_BOW.get()));h.assertTrue(!z.isOnFire(),"Fire cannot reproc on every pellet during its finite cooldown");
            p.setItemSlot(EquipmentSlot.HEAD,new ItemStack(ExpansionContent.item("baihu_helmet")));
            EquipmentBehaviors.symbolHit(p,z,new ItemStack(DynastyWeapons.BAIHU_GLAIVE.get()));h.assertTrue(z.hasEffect(ExpansionEffects.BREAK.get()),"White Tiger owns the existing real armor-break effect");
            p.setItemSlot(EquipmentSlot.HEAD,new ItemStack(ExpansionContent.item("qinglong_helmet")));p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyWeapons.THUNDER_SPEAR.get()));
            h.assertTrue(!EquipmentBehaviors.comboWave(p,z,4)&&EquipmentBehaviors.comboWave(p,z,5),"One matching piece enables the existing full-combo wave, without a full-set use gate");
            h.assertTrue(z.hasEffect(ExpansionEffects.THUNDER.get())&&z.getDeltaMovement().horizontalDistance()>0,"Strengthened dragon-wave contact owns bounded force and existing Thunder mark");
            p.setItemSlot(EquipmentSlot.HEAD,ItemStack.EMPTY);h.assertTrue(!EquipmentBehaviors.strengthenedWave(p),"Unequipping immediately revokes the special synergy");h.succeed();
        }finally{close(h,p);z.discard();}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_real_combo",timeoutTicks=160)
    public static void fiveRealPlayerAttacksReturnQiAfterVanillaResetsAttackCooldown(GameTestHelper h){
        var p=player(h);var target=EntityType.COW.create(h.getLevel());target.setNoAi(true);target.setNoGravity(true);
        target.getAttribute(Attributes.MAX_HEALTH).setBaseValue(100_000);target.setHealth(100_000);
        target.setPos(p.position().add(1,0,0));h.getLevel().addFreshEntity(target);
        String[] names={"helmet","chestplate","leggings","boots"};EquipmentSlot[] slots={EquipmentSlot.HEAD,EquipmentSlot.CHEST,EquipmentSlot.LEGS,EquipmentSlot.FEET};
        for(int i=0;i<4;i++)p.setItemSlot(slots[i],new ItemStack(ExpansionContent.item("qinglong_"+names[i])));
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(DynastyWeapons.THUNDER_SPEAR.get()));
        h.onEachTick(()->{if(!p.isRemoved())p.doTick();});var sequence=h.startSequence();
        for(int i=1;i<=5;i++){final int strike=i;sequence.thenIdle(22).thenExecute(()->{
            try {
                h.assertTrue(p.getAttackStrengthScale(.5F)>.9F,"Real cooldown fills before strike "+strike);
                target.invulnerableTime=0;float before=target.getHealth();p.setOnGround(true);p.setSprinting(false);p.attack(target);
                h.assertTrue(target.getHealth()<before&&p.getAttackStrengthScale(.5F)<.2F,"Actual Player.attack hurts and resets cooldown: strike="+strike+", hp="+before+" -> "+target.getHealth()+", cooldown="+p.getAttackStrengthScale(.5F)+", damage="+p.getAttributeValue(Attributes.ATTACK_DAMAGE)+", main="+p.getMainHandItem());
                h.assertTrue(EquipmentBehaviors.qiActive(p)==(strike==5),"Existing full combo returns Qi on exactly the fifth real hit: "+strike);
            } catch(RuntimeException|Error failure) {close(h,p);target.discard();throw failure;}
        });}
        sequence.thenExecute(()->{try{
            h.assertTrue(EquipmentBehaviors.saved(p).getLong("comboWave")>h.getLevel().getGameTime(),"The actual hit opens the finite wave cooldown");h.succeed();
        }finally{close(h,p);target.discard();}});
    }
    private SchoolLinkageGameTests(){}
}
