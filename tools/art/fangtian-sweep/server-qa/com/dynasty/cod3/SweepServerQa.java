package com.dynasty.cod3;

import com.dynasty.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.gametest.*;
import java.util.*;
import java.util.function.Consumer;

@GameTestHolder("dynasty_sweep_qa") @PrefixGameTestTemplate(false)
public final class SweepServerQa {
    private static FakePlayer player(GameTestHelper h,Item item) {
        var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"sweep-qa")) {
            @Override public float getAttackStrengthScale(float partial){return 1;}
        };p.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(item));p.setOnGround(true);return p;
    }
    private static LivingEntity target(GameTestHelper h,int x,int z) {
        var t=new net.minecraft.world.entity.animal.Cow(EntityType.COW,h.getLevel());
        for(int xx=1;xx<=10;xx++)for(int zz=1;zz<=10;zz++)for(int y=2;y<=5;y++)h.setBlock(new BlockPos(xx,y,zz),Blocks.AIR);
        var a=h.absolutePos(new BlockPos(x,2,z));t.setPos(a.getX()+.5,a.getY(),a.getZ()+.5);
        h.getLevel().addFreshEntity(t);t.setNoAi(true);t.setNoGravity(true);t.setOnGround(true);
        t.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);t.setHealth(1000);return t;
    }
    private static void attack(FakePlayer p,LivingEntity t){p.setPos(t.getX(),t.getY(),t.getZ()-1);p.setYRot(0);p.attack(t);}
    private static boolean stamped(FakePlayer p){return p.getPersistentData().contains(FangtianSweep.STAMP);}
    private static void done(GameTestHelper h,FakePlayer p,boolean expected,LivingEntity... targets) {
        h.runAfterDelay(2,()->{h.assertTrue(stamped(p)==expected,"Wrong native sweep receipt: expected="+expected+" stamp="+stamped(p));for(var t:targets)t.discard();p.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void nativeAllFourDirectionsExactlyOnceAndOriginalPush(GameTestHelper h) {
        var p=player(h,net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(net.minecraft.resources.ResourceLocation.parse("dynasty:halberd_fangtian")));var main=target(h,5,5);
        var front=target(h,5,7);var back=target(h,5,3);var left=target(h,3,5);var right=target(h,7,5);
        float[] mainAmount={0},sideAmount={0};int[] sideCalls={0};net.minecraft.world.phys.Vec3[] push={null};
        Consumer<LivingHurtEvent> observePush=e->{if(e.getEntity()==main)push[0]=main.getDeltaMovement();};MinecraftForge.EVENT_BUS.addListener(EventPriority.LOW,observePush);
        Consumer<LivingHurtEvent> amounts=e->{if(e.getSource().getEntity()==p){if(e.getEntity()==main)mainAmount[0]=e.getAmount();else if(e.getEntity()==right){sideAmount[0]=e.getAmount();sideCalls[0]++;}}};
        MinecraftForge.EVENT_BUS.addListener(EventPriority.HIGHEST,amounts);
        try{attack(p,main);}finally{MinecraftForge.EVENT_BUS.unregister(amounts);MinecraftForge.EVENT_BUS.unregister(observePush);}
        for(var t:List.of(main,front,back,left,right))h.assertTrue(t.getHealth()<1000,"360 native hit missing: "+t.position());
        h.assertTrue(sideCalls[0]==1&&Math.abs(sideAmount[0]-(mainAmount[0]+DynastyBalance.weaponBonus("halberd_fangtian"))*.6)<.001,"Original60%/single sweep changed: main="+mainAmount[0]+" side="+sideAmount[0]+" calls="+sideCalls[0]);
        h.assertTrue(push[0]!=null&&push[0].y>=.249&&push[0].z>=.79,"Original native yaw push changed");
        h.assertTrue(!stamped(p),"Sent before original hurt calls returned and native final confirmation");done(h,p,true,main,front,back,left,right);
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void alliesOcclusionAndBoundsStillFiltered(GameTestHelper h) {
        var p=player(h,net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(net.minecraft.resources.ResourceLocation.parse("dynasty:halberd_fangtian")));var main=target(h,5,5);
        var ally=target(h,3,5);var behind=target(h,7,5);var far=target(h,10,5);
        var score=h.getLevel().getScoreboard();var team=score.addPlayerTeam("sweep"+p.getUUID().toString().substring(0,8));score.addPlayerToTeam(p.getScoreboardName(),team);score.addPlayerToTeam(ally.getScoreboardName(),team);
        for(int z=3;z<=7;z++)for(int y=2;y<=4;y++)h.setBlock(new BlockPos(6,y,z),Blocks.STONE);
        attack(p,main);h.assertTrue(main.getHealth()<1000,"Wall erased valid main");
        h.assertTrue(ally.getHealth()==1000&&behind.getHealth()==1000&&far.getHealth()==1000,"Visual hook changed native ally/LOS/AABB predicate");
        h.runAfterDelay(2,()->{h.assertTrue(stamped(p),"Real main-only sweep lacked receipt");score.removePlayerTeam(team);for(var t:List.of(main,ally,behind,far))t.discard();p.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void allCanceledFinalDamageCannotEmitNameOnlySweep(GameTestHelper h) {
        var p=player(h,net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(net.minecraft.resources.ResourceLocation.parse("dynasty:halberd_fangtian")));var main=target(h,5,5);var side=target(h,7,5);
        Consumer<LivingDamageEvent> cancel=e->{if(e.getSource().getEntity()==p)e.setCanceled(true);};MinecraftForge.EVENT_BUS.addListener(EventPriority.HIGHEST,cancel);
        try{attack(p,main);}finally{MinecraftForge.EVENT_BUS.unregister(cancel);}
        h.assertTrue(main.getHealth()==1000&&side.getHealth()==1000,"Original final cancellation lost");done(h,p,false,main,side);
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void secondaryActualDamageSurvivesLaterPrimaryCancel(GameTestHelper h) {
        var p=player(h,net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(net.minecraft.resources.ResourceLocation.parse("dynasty:halberd_fangtian")));var main=target(h,5,5);var side=target(h,7,5);
        Consumer<LivingHurtEvent> cancel=e->{if(e.getEntity()==main)e.setCanceled(true);};MinecraftForge.EVENT_BUS.addListener(EventPriority.LOW,cancel);
        try{attack(p,main);}finally{MinecraftForge.EVENT_BUS.unregister(cancel);}
        h.assertTrue(main.getHealth()==1000&&side.getHealth()<1000,"Existing secondary execution before later main cancel changed");done(h,p,true,main,side);
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void invulnerableSecondaryAndCanceledMainHaveNoContact(GameTestHelper h) {
        var p=player(h,net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(net.minecraft.resources.ResourceLocation.parse("dynasty:halberd_fangtian")));var main=target(h,5,5);var side=target(h,7,5);side.setInvulnerable(true);
        Consumer<LivingHurtEvent> cancel=e->{if(e.getEntity()==main)e.setCanceled(true);};MinecraftForge.EVENT_BUS.addListener(EventPriority.LOW,cancel);
        try{attack(p,main);}finally{MinecraftForge.EVENT_BUS.unregister(cancel);}
        h.assertTrue(main.getHealth()==1000&&side.getHealth()==1000,"Fixture unexpectedly lost health");done(h,p,false,main,side);
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void directHurtWithoutNativeAttackAndOtherSwordReject(GameTestHelper h) {
        var p=player(h,net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(net.minecraft.resources.ResourceLocation.parse("dynasty:halberd_fangtian")));var main=target(h,5,5);var side=target(h,7,5);
        p.setPos(main.getX(),main.getY(),main.getZ()-1);main.hurt(p.damageSources().playerAttack(p),10);
        h.assertTrue(main.getHealth()<1000&&side.getHealth()<1000,"Existing direct-hurt gameplay changed");
        var other=player(h,Items.IRON_SWORD);var separate=target(h,1,1);attack(other,separate);
        h.runAfterDelay(2,()->{h.assertTrue(!stamped(p)&&!stamped(other),"Weapon name or non-native source stole receipt");for(var t:List.of(main,side,separate))t.discard();p.discard();other.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void nativeYawAnchorDoesNotFollowLaterTurnOrVictimMove(GameTestHelper h) {
        var p=player(h,net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(net.minecraft.resources.ResourceLocation.parse("dynasty:halberd_fangtian")));var main=target(h,5,5);p.setPos(main.getX()-1,main.getY(),main.getZ());p.setYRot(90);
        var before=main.position();net.minecraft.world.phys.Vec3[] push={null};
        Consumer<LivingHurtEvent> observe=e->{if(e.getEntity()==main)push[0]=main.getDeltaMovement();};MinecraftForge.EVENT_BUS.addListener(EventPriority.LOW,observe);
        try{p.attack(main);}finally{MinecraftForge.EVENT_BUS.unregister(observe);}h.assertTrue(push[0]!=null&&push[0].x<=-.79,"Native90degree pre-vanilla push not present");
        try {
            var field=FangtianSweep.class.getDeclaredField("PENDING");field.setAccessible(true);
            var receipt=((java.util.List<FangtianSweep.Receipt>)field.get(null)).stream().filter(v->v.player==p).findFirst().orElseThrow();
            h.assertTrue(receipt.direction.x<-.99&&receipt.origin.distanceTo(before.add(0,Math.min(1.1,main.getBbHeight()*.5),0))<1e-8,"Actual native receipt did not capture contact/yaw");
        }catch(ReflectiveOperationException ex){throw new RuntimeException(ex);}
        p.setYRot(270);main.setPos(main.position().add(0,0,1));
        done(h,p,true,main);
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void canceledNativeReceiptCannotBeBorrowedBySameTickOtherDamage(GameTestHelper h) {
        var p=player(h,net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(net.minecraft.resources.ResourceLocation.parse("dynasty:halberd_fangtian")));
        var main=target(h,5,5);var side=target(h,7,5);
        Consumer<LivingDamageEvent> cancel=e->{if(e.getSource().getEntity()==p)e.setCanceled(true);};MinecraftForge.EVENT_BUS.addListener(EventPriority.HIGHEST,cancel);
        try{attack(p,main);}finally{MinecraftForge.EVENT_BUS.unregister(cancel);}
        h.assertTrue(main.getHealth()==1000&&side.getHealth()==1000,"Native canceled fixture lost health");
        main.invulnerableTime=0;side.invulnerableTime=0;
        main.hurt(p.damageSources().playerAttack(p),10);
        h.assertTrue(main.getHealth()<1000&&side.getHealth()<1000,"Other source fixture lacked original actual sweep damage");
        done(h,p,false,main,side);
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void deadAttackerDiscardsConfirmedPendingSweep(GameTestHelper h) {
        var p=player(h,net.minecraftforge.registries.ForgeRegistries.ITEMS.getValue(net.minecraft.resources.ResourceLocation.parse("dynasty:halberd_fangtian")));
        var main=target(h,5,5);var side=target(h,7,5);attack(p,main);
        h.assertTrue(main.getHealth()<1000&&side.getHealth()<1000,"Original sweep absent");p.setHealth(0);done(h,p,false,main,side);
    }
}
