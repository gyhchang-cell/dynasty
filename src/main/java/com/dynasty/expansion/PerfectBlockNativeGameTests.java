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
import net.minecraft.world.entity.monster.Zombie;
import net.minecraft.world.item.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.ShieldBlockEvent;
import net.minecraftforge.eventbus.api.*;
import net.minecraftforge.gametest.*;

@GameTestHolder("dynasty_cod4") @PrefixGameTestTemplate(false)
public final class PerfectBlockNativeGameTests {
    private static ServerPlayer player(GameTestHelper h,Item main,boolean xuanwu,boolean pair){
        var p=new ServerPlayer(h.getLevel().getServer(),h.getLevel(),new GameProfile(UUID.randomUUID(),"perfect-native"));
        p.connection=new net.minecraft.server.network.ServerGamePacketListenerImpl(h.getLevel().getServer(),new net.minecraft.network.Connection(net.minecraft.network.protocol.PacketFlow.SERVERBOUND),p);
        p.setPos(Vec3.atBottomCenterOf(h.absolutePos(new BlockPos(6,52,6))));p.setNoGravity(true);p.getFoodData().setFoodLevel(17);
        p.getAttribute(Attributes.MAX_HEALTH).setBaseValue(5000);p.setHealth(5000);p.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);
        if(xuanwu){p.setItemSlot(EquipmentSlot.HEAD,new ItemStack(ExpansionContent.item("xuanwu_helmet")));p.setItemSlot(EquipmentSlot.CHEST,new ItemStack(ExpansionContent.item("xuanwu_chestplate")));}
        p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(main));if(pair)p.setItemInHand(InteractionHand.OFF_HAND,new ItemStack(main));p.setYRot(-90);p.yRotO=-90;for(int i=0;i<61;i++)p.tick();return p;
    }
    private static Zombie attacker(GameTestHelper h,ServerPlayer p,int side){var z=new Zombie(h.getLevel());z.setPos(p.position().add(side,0,0));z.setNoAi(true);z.setNoGravity(true);h.getLevel().addFreshEntity(z);return z;}
    private static void raise(GameTestHelper h,ServerPlayer p,int ticks){
        p.stopUsingItem();p.invulnerableTime=0;p.gameMode.useItem(p,h.getLevel(),p.getMainHandItem(),InteractionHand.MAIN_HAND);
        for(int i=0;i<ticks;i++)p.doTick();
        boolean paired=p.isUsingItem()&&p.getUseItem().is(ExpansionContent.DUCK.get())&&p.getMainHandItem().is(ExpansionContent.DUCK.get())&&p.getOffhandItem().is(ExpansionContent.DUCK.get());
        h.assertTrue(p.isBlocking()||paired,"Actual native use input raises shield/guard blade or existing paired-axe guard: item="+p.getMainHandItem()+", using="+p.isUsingItem()+", ticks="+p.getTicksUsingItem());
    }
    private static void cleanup(ServerPlayer p,Entity... actors){p.stopUsingItem();for(var a:actors)a.discard();net.minecraftforge.common.MinecraftForge.EVENT_BUS.post(new net.minecraftforge.event.entity.player.PlayerEvent.PlayerLoggedOutEvent(p));DynastyTrinkets.forget(p);p.discard();}
    @GameTest(template="bow_ritual_test",batch="cod4_perfect_native_clear",setupTicks=20,timeoutTicks=100)
    public static void actualFrontBlockedDamageClearsStaggerOnShieldGuardBladeAndPairedAxesWithoutSuitGate(GameTestHelper h){
        var players=new ArrayList<ServerPlayer>();var attackers=new ArrayList<Zombie>();Item[] items={Items.SHIELD,DynastyWeapons.ZHENYUE_BLADE.get(),ExpansionContent.DUCK.get(),Items.SHIELD};
        for(int i=0;i<items.length;i++){var p=player(h,items[i],i==1||i==3,i==2);players.add(p);attackers.add(attacker(h,p,1));}
        h.startSequence().thenWaitUntil(()->{for(var z:attackers)h.assertTrue(z.tickCount>=2&&h.getLevel().getEntity(z.getUUID())==z,"Native actual damage-calibration attacker visible");})
        .thenExecute(()->{try{
            for(int i=0;i<players.size();i++){
                var p=players.get(i);double speed=p.getAttributeValue(Attributes.MOVEMENT_SPEED);ExpansionEffects.apply(p,ExpansionEffects.STAGGER,40);raise(h,p,5);
                h.assertTrue(p.hasEffect(ExpansionEffects.STAGGER.get())&&EquipmentBehaviors.perfectGuard(p),"Effect still live at actual first native perfect-block frame");
                float hp=p.getHealth();p.hurt(p.damageSources().mobAttack(attackers.get(i)),40);
                h.assertTrue(!p.hasEffect(ExpansionEffects.STAGGER.get())&&Math.abs(p.getAttributeValue(Attributes.MOVEMENT_SPEED)-speed)<.001,"Actual successful front block removes original stagger effect and modifier for case"+i);
                h.assertTrue(p.getHealth()<=hp,"Presentation/cleanse never repeats damage or heals blocked hit");
                if(i==2){
                    h.assertTrue(p.getPersistentData().contains("cod3_weapon_at_duck_guard"),"Real paired native guard owns its finite weapon pose cue");
                    float frontDamage=hp-p.getHealth();var rear=attacker(h,p,-1);p.invulnerableTime=0;hp=p.getHealth();p.hurt(p.damageSources().mobAttack(rear),40);float rearDamage=hp-p.getHealth();rear.discard();
                    h.assertTrue(frontDamage>0&&rearDamage>0&&Math.abs(frontDamage/rearDamage-.35F)<.02,"Original paired native front mitigation remains exactly65percent, not duplicated: "+frontDamage+"/"+rearDamage);
                    p.stopUsingItem();for(int tick=0;tick<22;tick++)p.doTick();p.attack(attackers.get(i));
                    h.assertTrue(attackers.get(i).isDeadOrDying()&&!p.getPersistentData().contains("cod4Counter")&&p.getPersistentData().contains("cod3_weapon_at_duck_counter"),"Actual primary attack consumes original counter once and owns finite paired-weapon afterimage cue");
                }
                if(i==0)h.assertTrue(!p.getPersistentData().contains("cod4Counter")&&!p.getPersistentData().contains("cod4Shell"),"Ordinary shield cleanse does not borrow Xuanwu counter/shell grants");
            }h.succeed();
        }finally{for(int i=0;i<players.size();i++)cleanup(players.get(i),attackers.get(i));}});
    }
    public static final class CancelBlock {
        private final UUID player;
        CancelBlock(ServerPlayer p){player=p.getUUID();}
        @SubscribeEvent(priority=EventPriority.HIGHEST) public void block(ShieldBlockEvent e){if(e.getEntity().getUUID().equals(player))e.setCanceled(true);}
    }
    @GameTest(template="bow_ritual_test",batch="cod4_perfect_native_controls",setupTicks=20,timeoutTicks=100)
    public static void actualRearLateAndCanceledBlocksLeaveLiveStaggerWhileFirstValidFrontBlockClearsIt(GameTestHelper h){
        var p=player(h,Items.SHIELD,false,false);var front=attacker(h,p,1);var rear=attacker(h,p,-1);
        h.startSequence().thenWaitUntil(()->h.assertTrue(front.tickCount>=2&&rear.tickCount>=2,"Native stationary source pair visible"))
        .thenExecute(()->{var bus=net.minecraftforge.common.MinecraftForge.EVENT_BUS;CancelBlock cancel=null;try{
            ExpansionEffects.apply(p,ExpansionEffects.STAGGER,40);raise(h,p,5);p.hurt(p.damageSources().mobAttack(rear),40);
            h.assertTrue(p.hasEffect(ExpansionEffects.STAGGER.get()),"Actual rear hurt never emits a valid blocked-hit event or cleanse");
            raise(h,p,11);h.assertTrue(!EquipmentBehaviors.perfectGuard(p),"Native seventh active block tick is beyond six-tick perfect window");p.hurt(p.damageSources().mobAttack(front),40);
            h.assertTrue(p.hasEffect(ExpansionEffects.STAGGER.get()),"Late actual front ordinary block does not cleanse live stagger");
            raise(h,p,5);cancel=new CancelBlock(p);bus.register(cancel);p.hurt(p.damageSources().mobAttack(front),40);bus.unregister(cancel);cancel=null;
            h.assertTrue(p.hasEffect(ExpansionEffects.STAGGER.get()),"Another Forge listener canceling the actual shield block prevents cleanse/counter/feedback");
            raise(h,p,5);p.hurt(p.damageSources().mobAttack(front),40);h.assertTrue(!p.hasEffect(ExpansionEffects.STAGGER.get()),"Next real uncanceled front perfect block clears once");h.succeed();
        }finally{if(cancel!=null)bus.unregister(cancel);cleanup(p,front,rear);}});
    }
}
