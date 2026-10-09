package com.dynasty.expansion;

import com.dynasty.*;
import com.mojang.authlib.GameProfile;
import java.util.*;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.gametest.*;

/** Native primary attacks and effect lifetime verify the existing Yang hook without another damage handler. */
@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class YangNativeGameTests {
    private static ServerPlayer player(GameTestHelper h,boolean registered){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"yang-native"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(6,4,6))));p.setNoGravity(true);p.getFoodData().setFoodLevel(17);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.IRON_SWORD));
        if(registered){h.getLevel().addNewPlayer(p);h.onEachTick(()->{if(!p.isRemoved())p.doTick();});}return p;
    }
    private static <T extends Mob> T target(GameTestHelper h,EntityType<T> type,ServerPlayer p,int side){
        var t=type.create(h.getLevel());t.setPos(p.position().add(side,0,0));t.setNoAi(true);t.setNoGravity(true);
        t.getAttribute(Attributes.MAX_HEALTH).setBaseValue(5000);t.setHealth(5000);t.getAttribute(Attributes.ARMOR).setBaseValue(0);t.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);h.getLevel().addFreshEntity(t);return t;
    }
    private static float hit(GameTestHelper h,ServerPlayer p,Mob target){
        for(int i=0;i<22;i++)p.doTick();p.setSprinting(false);target.invulnerableTime=0;float hp=target.getHealth();
        h.assertTrue(p.getAttackStrengthScale(.5F)>.9F,"Native attack cooldown genuinely charged");p.attack(target);float damage=hp-target.getHealth();
        h.assertTrue(damage>0&&p.getAttackStrengthScale(.5F)<.2F,"Native primary input loses target health and resets cooldown");return damage;
    }
    private static void close(ServerPlayer p,Mob...targets){for(var t:targets)t.discard();net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent(p));DynastyTrinkets.forget(p);p.discard();}
    private static void ready(GameTestHelper h,Mob...targets){for(var t:targets)h.assertTrue(t.tickCount>=2&&h.getLevel().getEntity(t.getUUID())==t,"Actual stationary damage-calibration targets visible and ticking");}
    @GameTest(template="bow_ritual_test",batch="cod4_yang_primary",setupTicks=20,timeoutTicks=80)
    public static void actualPlayerPrimaryAttacksProveThreeCappedSpecificUndeadBonusesWithoutLosingGenericAttributeBenefit(GameTestHelper h){
        var p=player(h,false);var undead=target(h,EntityType.ZOMBIE,p,1);var ordinary=target(h,EntityType.COW,p,-1);
        h.startSequence().thenWaitUntil(()->ready(h,undead,ordinary)).thenExecute(()->{try{
            float baseUndead=hit(h,p,undead),baseOrdinary=hit(h,p,ordinary);double attack=p.getAttributeValue(Attributes.ATTACK_DAMAGE);
            for(int amp=0;amp<3;amp++){
                ExpansionEffects.apply(p,ExpansionEffects.YANG,100);h.assertTrue(p.getEffect(ExpansionEffects.YANG.get()).getAmplifier()==amp,"Original native effect stacks exactly one layer");
                float specific=hit(h,p,undead),normal=hit(h,p,ordinary);double expected=(baseUndead/baseOrdinary)*(1+.08*(amp+1));
                h.assertTrue(Math.abs(specific/normal-expected)<.004&&normal>baseOrdinary&&p.getAttributeValue(Attributes.ATTACK_DAMAGE)>attack,"Actual native undead damage has extra8/16/24percent above retained generic attribute: "+specific+"/"+normal+", expected ratio="+expected);
            }
            ExpansionEffects.apply(p,ExpansionEffects.YANG,100);h.assertTrue(p.getEffect(ExpansionEffects.YANG.get()).getAmplifier()==2,"Fourth application refreshes duration without a fourth layer");
            ExpansionEffects.apply(p,ExpansionEffects.YIN,100);h.assertTrue(!p.hasEffect(ExpansionEffects.YANG.get())&&!p.hasEffect(ExpansionEffects.YIN.get())&&Math.abs(p.getAttributeValue(Attributes.ATTACK_DAMAGE)-attack)<.001,"Opposite Qi uses original neutralisation and immediately removes Yang modifier");
            h.assertTrue(Math.abs(hit(h,p,undead)-baseUndead)<.02,"Next native attack no longer has any stale Yang damage benefit");h.succeed();
        }finally{close(p,undead,ordinary);}});
    }
    @GameTest(template="bow_ritual_test",batch="cod4_yang_expiry",setupTicks=20,timeoutTicks=180)
    public static void actualWorldAndNativePlayerTicksExpireYangAndNextPrimaryAttackReturnsToBaseline(GameTestHelper h){
        var p=player(h,true);var undead=target(h,EntityType.ZOMBIE,p,1);var ordinary=target(h,EntityType.COW,p,-1);
        h.startSequence().thenWaitUntil(()->ready(h,undead,ordinary)).thenExecute(()->{
            float baseline=hit(h,p,undead);double attack=p.getAttributeValue(Attributes.ATTACK_DAMAGE);ExpansionEffects.apply(p,ExpansionEffects.YANG,100);
            h.assertTrue(hit(h,p,undead)>baseline,"Original Yang really affects native primary damage before timeout");
            h.runAfterDelay(110,()->{try{
                h.assertTrue(!p.hasEffect(ExpansionEffects.YANG.get())&&Math.abs(p.getAttributeValue(Attributes.ATTACK_DAMAGE)-attack)<.001,"Real world/native player ticks expire original effect and fixed attribute UUID");
                h.assertTrue(Math.abs(hit(h,p,undead)-baseline)<.02,"Actual post-expiry primary health loss returns to baseline");h.succeed();
            }finally{close(p,undead,ordinary);}});
        });
    }
}
