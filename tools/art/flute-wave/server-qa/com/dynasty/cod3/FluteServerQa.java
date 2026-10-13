package com.dynasty.cod3;

import com.dynasty.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.*;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.event.entity.living.MobEffectEvent;
import net.minecraftforge.eventbus.api.Event;
import net.minecraftforge.gametest.*;
import java.util.*;
import java.util.function.Consumer;

@GameTestHolder("dynasty_flute_qa") @PrefixGameTestTemplate(false)
public final class FluteServerQa {
    private static FakePlayer player(GameTestHelper h,InteractionHand hand) {
        var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"flute-qa"));
        var a=h.absolutePos(new BlockPos(5,2,5));p.setPos(a.getX()+.5,a.getY(),a.getZ()+.5);
        p.setItemInHand(hand,new ItemStack(DynastyWeapons.YU_DI.get()));p.setOnGround(true);return p;
    }
    private static LivingEntity target(GameTestHelper h,int x,int z) {
        var t=new net.minecraft.world.entity.animal.Cow(EntityType.COW,h.getLevel());
        var a=h.absolutePos(new BlockPos(x,2,z));t.setPos(a.getX()+.5,a.getY(),a.getZ()+.5);
        h.getLevel().addFreshEntity(t);t.setNoAi(true);t.setNoGravity(true);return t;
    }
    private static InteractionResult use(GameTestHelper h,FakePlayer p,InteractionHand hand) {
        return p.gameMode.useItem(p,h.getLevel(),p.getItemInHand(hand),hand);
    }
    private static boolean stamped(FakePlayer p){return p.getPersistentData().contains(FluteWave.STAMP);}
    private static void effects(GameTestHelper h,LivingEntity t) {
        for(var type:List.of(MobEffects.WEAKNESS,MobEffects.MOVEMENT_SLOWDOWN)) {
            var e=t.getEffect(type);h.assertTrue(e!=null&&e.getAmplifier()==1&&e.getDuration()==120,"Original active amplifier/duration changed");
        }
    }
    private static void close(GameTestHelper h,FakePlayer p,LivingEntity... ts){for(var t:ts)t.discard();p.discard();h.succeed();}
    @GameTest(template="bow_ritual_test",batch="flute_main",setupTicks=20)
    public static void nativeMainhandUseConfirmsActualEffectsAndOriginalCooldown(GameTestHelper h) {
        var p=player(h,InteractionHand.MAIN_HAND);var t=target(h,7,5);float hp=t.getHealth();
        h.assertTrue(use(h,p,InteractionHand.MAIN_HAND).consumesAction(),"Native gameMode item-use failed");effects(h,t);
        h.assertTrue(stamped(p)&&t.getHealth()==hp,"Missing confirmed debuff cue or additional damage");
        var strength=p.getEffect(MobEffects.DAMAGE_BOOST);h.assertTrue(strength!=null&&strength.getAmplifier()==0&&strength.getDuration()==160,"Original player strength changed");
        for(int i=0;i<119;i++)p.getCooldowns().tick();h.assertTrue(p.getCooldowns().isOnCooldown(DynastyWeapons.YU_DI.get()),"120tick cooldown shortened");
        p.getCooldowns().tick();h.assertTrue(!p.getCooldowns().isOnCooldown(DynastyWeapons.YU_DI.get()),"120tick cooldown lengthened");close(h,p,t);
    }
    @GameTest(template="bow_ritual_test",batch="flute_off",setupTicks=20)
    public static void nativeOffhandUseAndCooldownReentry(GameTestHelper h) {
        var p=player(h,InteractionHand.OFF_HAND);p.setItemInHand(InteractionHand.MAIN_HAND,new ItemStack(Items.IRON_SWORD));var t=target(h,7,5);
        h.assertTrue(use(h,p,InteractionHand.OFF_HAND).consumesAction(),"Native offhand use failed");effects(h,t);h.assertTrue(stamped(p),"Wrong mainhand displaced actual source");
        p.getPersistentData().remove(FluteWave.STAMP);
        h.assertTrue(use(h,p,InteractionHand.OFF_HAND)==InteractionResult.PASS&&!stamped(p),"Native cooldown allowed repeated cue/use");close(h,p,t);
    }
    @GameTest(template="bow_ritual_test",batch="flute_empty",setupTicks=20)
    public static void emptyRangeAndOutsideBoxKeepSelfBuffButHaveNoDebuffWave(GameTestHelper h) {
        var p=player(h,InteractionHand.MAIN_HAND);var far=target(h,15,5);use(h,p,InteractionHand.MAIN_HAND);
        h.assertTrue(!stamped(p)&&!far.hasEffect(MobEffects.WEAKNESS)&&!far.hasEffect(MobEffects.MOVEMENT_SLOWDOWN),"Empty/outside range fabricated hit wave");
        h.assertTrue(p.hasEffect(MobEffects.DAMAGE_BOOST)&&p.getCooldowns().isOnCooldown(DynastyWeapons.YU_DI.get()),"Empty cast changed original self buff/cooldown");close(h,p,far);
    }
    @GameTest(template="bow_ritual_test",batch="flute_denied",setupTicks=20)
    public static void forgeDeniedApplicationsCannotUseAttemptCountAsContact(GameTestHelper h) {
        var p=player(h,InteractionHand.MAIN_HAND);var t=target(h,7,5);
        Consumer<MobEffectEvent.Applicable> deny=e->{if(e.getEntity()==t)e.setResult(Event.Result.DENY);};MinecraftForge.EVENT_BUS.addListener(deny);
        try{use(h,p,InteractionHand.MAIN_HAND);}finally{MinecraftForge.EVENT_BUS.unregister(deny);}
        h.assertTrue(!t.hasEffect(MobEffects.WEAKNESS)&&!t.hasEffect(MobEffects.MOVEMENT_SLOWDOWN)&&!stamped(p),"Denied application fabricated wave");close(h,p,t);
    }
    @GameTest(template="bow_ritual_test",batch="flute_same",setupTicks=20)
    public static void equalAndInfiniteAndStrongerActiveDebuffsRejectCosmeticUpdates(GameTestHelper h) {
        var p=player(h,InteractionHand.MAIN_HAND);var equal=target(h,7,5);var infinite=target(h,3,5);var stronger=target(h,5,7);
        for(var type:List.of(MobEffects.WEAKNESS,MobEffects.MOVEMENT_SLOWDOWN)) {
            equal.addEffect(new MobEffectInstance(type,120,1,true,false));
            infinite.addEffect(new MobEffectInstance(type,-1,1,true,false));
            stronger.addEffect(new MobEffectInstance(type,20,2,true,false));
        }
        use(h,p,InteractionHand.MAIN_HAND);h.assertTrue(!stamped(p),"Flag-only/hidden/unchanged active update fabricated debuff wave");
        h.assertTrue(infinite.getEffect(MobEffects.WEAKNESS).getDuration()==-1&&stronger.getEffect(MobEffects.WEAKNESS).getAmplifier()==2,"Original stronger/infinite effect changed");close(h,p,equal,infinite,stronger);
    }
    @GameTest(template="bow_ritual_test",batch="flute_refresh",setupTicks=20)
    public static void trueShortDurationRefreshOrStrongerApplicationProducesWave(GameTestHelper h) {
        var p=player(h,InteractionHand.MAIN_HAND);var t=target(h,7,5);
        t.addEffect(new MobEffectInstance(MobEffects.WEAKNESS,40,1));t.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN,600,0));
        use(h,p,InteractionHand.MAIN_HAND);effects(h,t);h.assertTrue(stamped(p),"Real duration/active-strength refresh was discarded");close(h,p,t);
    }
    @GameTest(template="bow_ritual_test",batch="flute_original_filter",setupTicks=20)
    public static void actualOriginalBoxIncludesAllyAndOccludedTarget(GameTestHelper h) {
        var p=player(h,InteractionHand.MAIN_HAND);var ally=target(h,3,5);var occluded=target(h,7,5);
        var score=h.getLevel().getScoreboard();var team=score.addPlayerTeam("flute"+p.getUUID().toString().substring(0,8));score.addPlayerToTeam(p.getScoreboardName(),team);score.addPlayerToTeam(ally.getScoreboardName(),team);
        for(int y=2;y<=4;y++)for(int z=3;z<=7;z++)h.setBlock(new BlockPos(6,y,z),Blocks.STONE);
        use(h,p,InteractionHand.MAIN_HAND);effects(h,ally);effects(h,occluded);h.assertTrue(stamped(p),"Visuals introduced ally/LOS filter into existing gameplay");
        score.removePlayerTeam(team);close(h,p,ally,occluded);
    }
    @GameTest(template="bow_ritual_test",batch="flute_dead",setupTicks=20)
    public static void deadCasterCannotOwnWaveAfterOriginalTargetApplication(GameTestHelper h) {
        var p=player(h,InteractionHand.MAIN_HAND);var t=target(h,7,5);
        Consumer<MobEffectEvent.Added> kill=e->{if(e.getEntity()==t)p.setHealth(0);};MinecraftForge.EVENT_BUS.addListener(kill);
        try{use(h,p,InteractionHand.MAIN_HAND);}finally{MinecraftForge.EVENT_BUS.unregister(kill);}
        h.assertTrue(t.hasEffect(MobEffects.WEAKNESS)&&!stamped(p),"Dead caster emitted wave or original target application removed");close(h,p,t);
    }
    @GameTest(template="bow_ritual_test",batch="flute_partial",setupTicks=20)
    public static void actualPartialAcceptedDebuffAndSwappedHeldItemKeepOriginalCast(GameTestHelper h) {
        var p=player(h,InteractionHand.OFF_HAND);var t=target(h,7,5);
        Consumer<MobEffectEvent.Applicable> deny=e->{if(e.getEntity()==t&&e.getEffectInstance().getEffect()==MobEffects.WEAKNESS)e.setResult(Event.Result.DENY);};
        Consumer<MobEffectEvent.Added> swap=e->{if(e.getEntity()==t)p.setItemInHand(InteractionHand.OFF_HAND,new ItemStack(Items.IRON_SWORD));};
        MinecraftForge.EVENT_BUS.addListener(deny);MinecraftForge.EVENT_BUS.addListener(swap);
        try{use(h,p,InteractionHand.OFF_HAND);}finally{MinecraftForge.EVENT_BUS.unregister(deny);MinecraftForge.EVENT_BUS.unregister(swap);}
        h.assertTrue(!t.hasEffect(MobEffects.WEAKNESS)&&t.hasEffect(MobEffects.MOVEMENT_SLOWDOWN)&&stamped(p),"Original offhand cast lost accepted slow when active hand changed");close(h,p,t);
    }
    @GameTest(template="bow_ritual_test",batch="flute_anchor",setupTicks=20)
    public static void nativeCaptureRetainsAnchorLookAndHandRejectsTeleportedOwner(GameTestHelper h) {
        var p=player(h,InteractionHand.MAIN_HAND);var t=target(h,7,5);var original=p.position();p.setYRot(90);
        var capture=FluteWave.capture(h.getLevel(),p,p.getMainHandItem(),InteractionHand.MAIN_HAND);
        h.assertTrue(capture!=null&&capture.direction().x<-.99&&capture.anchor().distanceTo(original.add(0,p.getEyeHeight()*.7,0))<1e-8,"Native cast anchor/direction not captured");
        p.setPos(p.position().add(1,0,0));p.setYRot(270);
        h.assertTrue(capture.direction().x<-.99&&capture.hand()==InteractionHand.MAIN_HAND&&capture.anchor().x==original.x,"Capture changed with later actor pose");
        Consumer<MobEffectEvent.Added> teleport=e->{if(e.getEntity()==t)p.setPos(p.position().add(20,0,0));};MinecraftForge.EVENT_BUS.addListener(teleport);
        try{use(h,p,InteractionHand.MAIN_HAND);}finally{MinecraftForge.EVENT_BUS.unregister(teleport);}
        h.assertTrue(t.hasEffect(MobEffects.WEAKNESS)&&!stamped(p),"Teleported caster stole ownership of old-world contact");close(h,p,t);
    }
}
