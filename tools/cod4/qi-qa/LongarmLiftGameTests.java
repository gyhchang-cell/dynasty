package com.dynasty.cod3;

import com.dynasty.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.*;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.properties.*;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.gametest.*;
import java.util.*;
import java.util.function.Consumer;

@GameTestHolder("dynasty_qi_qa") @PrefixGameTestTemplate(false)
public final class LongarmLiftGameTests {
    private static final class StillCow extends net.minecraft.world.entity.animal.Cow {
        StillCow(net.minecraft.server.level.ServerLevel level){super(EntityType.COW,level);}
        @Override protected void registerGoals() {} // Keep real travel/gravity; suppress unrelated wandering.
    }
    private static FakePlayer player(GameTestHelper h,Item item) {
        var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"lift-qa")) {
            @Override public float getAttackStrengthScale(float partial){return 1;}
        };p.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(item));p.setOnGround(true);return p;
    }
    private static LivingEntity target(GameTestHelper h) {
        for(int x=1;x<=8;x++)for(int z=1;z<=8;z++){
            h.setBlock(new BlockPos(x,1,z),Blocks.STONE);for(int y=2;y<=6;y++)h.setBlock(new BlockPos(x,y,z),Blocks.AIR);
        }
        var t=new StillCow(h.getLevel());var at=h.absolutePos(new BlockPos(4,2,4));t.setPos(at.getX()+.5,at.getY(),at.getZ()+.5);
        h.getLevel().addFreshEntity(t);t.setNoAi(false);t.setNoGravity(false);t.setOnGround(true);
        t.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);t.setHealth(1000);t.setDeltaMovement(Vec3.ZERO);return t;
    }
    private static void attack(FakePlayer p,LivingEntity t){p.setPos(t.getX()-1,t.getY(),t.getZ());p.attack(t);}
    private static boolean stamped(FakePlayer p){return p.getPersistentData().contains(WeaponLift.STAMP);}
    @GameTest(template="bow_ritual_test",setupTicks=20,timeoutTicks=80)
    public static void juqueNativeImpulseRealAscentAndGravityLanding(GameTestHelper h) {
        var p=player(h,DynastyWeapons.JUQUE_SWORD.get());var t=target(h);double start=t.getY();
        var support=WeaponLift.groundSupport(t);h.assertTrue(support!=null&&Math.abs(support.point().y-start-.015)<1e-6,"No actual stone-top takeoff anchor");
        h.assertTrue(support.color()==h.getBlockState(new BlockPos(4,1,4)).getMapColor(h.getLevel(),h.absolutePos(new BlockPos(4,1,4))).col,"Ground chip color did not come from actual support");attack(p,t);
        h.assertTrue(t.getHealth()<1000&&t.getDeltaMovement().y>=.39,"Original native Juque hit/push absent");
        h.assertTrue(t.hasEffect(net.minecraft.world.effect.MobEffects.MOVEMENT_SLOWDOWN)&&t.getEffect(net.minecraft.world.effect.MobEffects.MOVEMENT_SLOWDOWN).getAmplifier()==1,"Original slow changed");
        h.assertTrue(!stamped(p),"Velocity alone emitted cue before displacement");
        h.runAfterDelay(3,()->{h.assertTrue(t.getY()>start+.02&&stamped(p),"Real rising Juque victim not confirmed: dy="+(t.getY()-start)+" stamp="+stamped(p));});
        h.runAfterDelay(25,()->{h.assertTrue(t.onGround()&&Math.abs(t.getY()-start)<.02,"Visuals fabricated continued float or changed landing: dy="+(t.getY()-start));t.discard();p.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void huanNativeKnockbackMustPhysicallyRise(GameTestHelper h) {
        var p=player(h,DynastyWeapons.HUAN_SHOU_DAO.get());var t=target(h);double start=t.getY();attack(p,t);
        h.assertTrue(t.getHealth()<1000&&!stamped(p),"Native hit absent or premature name-only cue");
        h.runAfterDelay(3,()->{h.assertTrue(t.getY()>start+.02&&stamped(p),"Actual vanilla Huan knockback ascent missed: dy="+(t.getY()-start)+" vy="+t.getDeltaMovement().y);t.discard();p.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void realTopSlabHeadroomRejectsJuqueLiftCue(GameTestHelper h) {
        var p=player(h,DynastyWeapons.JUQUE_SWORD.get());var t=target(h);
        for(int x=1;x<=8;x++)for(int z=1;z<=8;z++)h.setBlock(new BlockPos(x,3,z),Blocks.STONE_SLAB.defaultBlockState().setValue(BlockStateProperties.SLAB_TYPE,SlabType.TOP));
        attack(p,t);h.assertTrue(t.getHealth()<1000,"Roof fixture canceled actual damage");
        h.runAfterDelay(4,()->{h.assertTrue(!stamped(p)&&t.getPersistentData().getInt("cod4FeedbackType")!=com.dynasty.expansion.CombatFeedback.LAUNCH,"Blocked headroom advertised lift");t.discard();p.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void deniedVanillaKnockbackDoesNotGuessHuanLift(GameTestHelper h) {
        var p=player(h,DynastyWeapons.HUAN_SHOU_DAO.get());var t=target(h);double start=t.getY();
        Consumer<LivingKnockBackEvent> deny=e->{if(e.getEntity()==t)e.setCanceled(true);};MinecraftForge.EVENT_BUS.addListener(EventPriority.LOW,deny);
        try{attack(p,t);h.assertTrue(t.getHealth()<1000,"Knockback denial erased damage");}finally{MinecraftForge.EVENT_BUS.unregister(deny);}
        h.runAfterDelay(4,()->{h.assertTrue(!stamped(p)&&t.getY()<=start+.02,"Denied native knockback emitted lift");t.discard();p.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void canceledDamageCannotUseExistingJuquePush(GameTestHelper h) {
        var p=player(h,DynastyWeapons.JUQUE_SWORD.get());var t=target(h);
        Consumer<LivingHurtEvent> cancel=e->{if(e.getEntity()==t)e.setCanceled(true);};MinecraftForge.EVENT_BUS.addListener(EventPriority.LOW,cancel);
        try{attack(p,t);h.assertTrue(t.getHealth()==1000,"Native cancel changed damage");}finally{MinecraftForge.EVENT_BUS.unregister(cancel);}
        h.runAfterDelay(4,()->{h.assertTrue(!stamped(p),"Canceled native damage emitted visual from pre-existing push");t.discard();p.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void ordinarySwordAndPreexistingAirborneMotionRejectLift(GameTestHelper h) {
        var p=player(h,Items.IRON_SWORD);var t=target(h);attack(p,t);
        var airborne=target(h);airborne.setPos(airborne.position().add(0,2,0));airborne.setOnGround(false);airborne.setDeltaMovement(0,.6,0);
        var other=player(h,DynastyWeapons.HUAN_SHOU_DAO.get());attack(other,airborne);
        h.runAfterDelay(4,()->{h.assertTrue(!stamped(p)&&!stamped(other),"Wrong sword/existing rise substituted new impulse");t.discard();airborne.discard();p.discard();other.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void exactSourceAndActualMovementRequiredNotForgedFinalDamage(GameTestHelper h) {
        var p=player(h,DynastyWeapons.JUQUE_SWORD.get());var t=target(h);var attack=new AttackEntityEvent(p,t);
        DynastySchoolCombat.attack(attack);WeaponLift.attack(attack);var source=p.damageSources().playerAttack(p);WeaponLift.hurt(new LivingHurtEvent(t,source,20));
        WeaponLift.damage(new LivingDamageEvent(t,p.damageSources().playerAttack(p),20));t.setDeltaMovement(0,.4,0);
        h.runAfterDelay(4,()->{h.assertTrue(!stamped(p),"Different DamageSource stole cosmetic receipt");t.discard();p.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void innateResistanceAndUnsupportedAirCannotFabricateGroundLift(GameTestHelper h) {
        var p=player(h,DynastyWeapons.HUAN_SHOU_DAO.get());var t=target(h);t.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);double start=t.getY();attack(p,t);
        var air=target(h);air.setPos(air.position().add(0,2,0));air.setOnGround(false);
        h.assertTrue(WeaponLift.groundSupport(air)==null,"Unsupported air fabricated collider support");
        var other=player(h,DynastyWeapons.JUQUE_SWORD.get());double airStart=air.getY();attack(other,air);
        h.runAfterDelay(3,()->{h.assertTrue(!stamped(p)&&Math.abs(t.getY()-start)<.02,"Innate full knockback resistance emitted lift");
            h.assertTrue(air.getY()>airStart+.02&&stamped(other),"Real airborne Juque impulse suppressed");t.discard();air.discard();p.discard();other.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void deadAttackerCannotKeepDelayedVisualOwnership(GameTestHelper h) {
        var p=player(h,DynastyWeapons.JUQUE_SWORD.get());var t=target(h);attack(p,t);p.setHealth(0);
        h.runAfterDelay(3,()->{h.assertTrue(!stamped(p),"Dead attacker retained delayed cue ownership");t.discard();p.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",setupTicks=20,timeoutTicks=45,batch="longarm_lift")
    public static void sevenLongarmsOnlyAdvertiseTheirRealNativeAscent(GameTestHelper h) {
        var actors=new ArrayList<FakePlayer>();var targets=new ArrayList<LivingEntity>();
        for(String id:List.of("mu_mao","chang_qiang","dragon_spear","bawang_spear","thunder_spear","beichen_spear","baihu_glaive")) {
            var p=player(h,com.dynasty.expansion.ExpansionContent.item(id));var t=target(h);actors.add(p);targets.add(t);
            var wire=WeaponLift.packet(h.getLevel().dimension().location().toString(),t.getId(),id,1,h.getLevel().getGameTime(),1,t.position(),new Vec3(0,0,1),0x777777,true);
            h.assertTrue(wire.template()==3&&WeaponLift.accepts(wire),"Actual longarm uses the finite VFX#3 route: "+id);
            h.assertTrue(EquipmentFeedback.template(id,1,false)!=3&&EquipmentFeedback.template(id,3,true)!=3,"Name alone cannot select launch arc: "+id);
            attack(p,t);h.assertTrue(t.getHealth()<1000&&!stamped(p),"Successful native hit still waits for actual displacement: "+id);
        }
        h.runAfterDelay(3,()->{
            for(int i=0;i<actors.size();i++)h.assertTrue(stamped(actors.get(i)),"Real native longarm knockback confirms ascent: "+i);
        });
        h.runAfterDelay(25,()->{
            for(int i=0;i<actors.size();i++) {h.assertTrue(targets.get(i).onGround(),"Original gravity lands longarm target: "+i);targets.get(i).discard();actors.get(i).discard();}
            h.succeed();
        });
    }
    @GameTest(template="bow_ritual_test",setupTicks=20,batch="longarm_rejection")
    public static void longarmResistanceAndCanceledHitRejectNameOnlyOrUnrelatedMotion(GameTestHelper h) {
        var actors=new ArrayList<FakePlayer>();var targets=new ArrayList<LivingEntity>();
        for(String id:List.of("mu_mao","chang_qiang","dragon_spear","bawang_spear","thunder_spear","beichen_spear","baihu_glaive")) {
            var p=player(h,com.dynasty.expansion.ExpansionContent.item(id));var t=target(h);actors.add(p);targets.add(t);
            t.getAttribute(Attributes.KNOCKBACK_RESISTANCE).setBaseValue(1);attack(p,t);
            h.assertTrue(t.getHealth()<1000,"Resistance denies motion, not actual damage: "+id);
        }
        var canceled=player(h,com.dynasty.expansion.ExpansionContent.item("dragon_spear"));var victim=target(h);actors.add(canceled);targets.add(victim);
        Consumer<LivingHurtEvent> cancel=e->{if(e.getEntity()==victim)e.setCanceled(true);};MinecraftForge.EVENT_BUS.addListener(EventPriority.LOW,cancel);
        try{attack(canceled,victim);h.assertTrue(victim.getHealth()==1000,"Canceled hit cannot earn launch");}finally{MinecraftForge.EVENT_BUS.unregister(cancel);}
        victim.setDeltaMovement(0,.4,0); // unrelated subsequent motion must not rescue the cancelled receipt.
        h.runAfterDelay(4,()->{for(int i=0;i<actors.size();i++){boolean originalPolearmPush=i<actors.size()-1&&actors.get(i).getMainHandItem().getItem() instanceof DynastyWeapons.PolearmItem; h.assertTrue(stamped(actors.get(i))==originalPolearmPush,"Feedback follows actual original polearm push despite knockback resistance, and rejects resisted ordinary knockback/cancelled damage: "+i);targets.get(i).discard();actors.get(i).discard();}h.succeed();});
    }

    @GameTest(template="bow_ritual_test",setupTicks=20,batch="longarm_roof")
    public static void actualCeilingBlocksLongarmPushWithoutAdvertisingAnAscent(GameTestHelper h) {
        var p=player(h,DynastyWeapons.DRAGON_SPEAR.get());var t=target(h);
        for(int x=1;x<=8;x++)for(int z=1;z<=8;z++)h.setBlock(new BlockPos(x,3,z),Blocks.STONE_SLAB.defaultBlockState().setValue(BlockStateProperties.SLAB_TYPE,SlabType.TOP));
        attack(p,t);h.assertTrue(t.getHealth()<1000,"Roof leaves original successful polearm damage intact");
        h.runAfterDelay(4,()->{h.assertTrue(!stamped(p)&&t.getPersistentData().getInt("cod4FeedbackType")!=com.dynasty.expansion.CombatFeedback.LAUNCH,"Actual ceiling prevents the polearm lift arc");t.discard();p.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",setupTicks=20,batch="longarm_caster")
    public static void hunyuanKeepsOriginalSpellInsteadOfInventedMeleeLift(GameTestHelper h) {
        var p=player(h,DynastyWeapons.HUNYUAN_STAFF.get());var t=target(h);
        h.assertTrue(EdictSpells.weapon(p.getMainHandItem())&&!WeaponLift.isLongarm("hunyuan_staff"),"Original caster is not a melee-lift weapon");
        var event=new AttackEntityEvent(p,t);MinecraftForge.EVENT_BUS.post(event);
        h.assertTrue(event.isCanceled(),"Original left-click spell still owns input");
        attack(p,t);h.assertTrue(t.getHealth()==1000,"Casting must not introduce an instant melee hit");
        h.runAfterDelay(4,()->{h.assertTrue(!stamped(p),"Canceled melee cannot fabricate a lift arc");t.discard();p.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",batch="longarm_protocol")
    public static void longarmWireRetainsBoundedExistingArcAndRejectsWrongTemplate(GameTestHelper h) {
        for(String id:List.of("mu_mao","chang_qiang","dragon_spear","bawang_spear","thunder_spear","beichen_spear","baihu_glaive")) {
            var p=WeaponLift.packet("minecraft:overworld",42,id,7,100,1,Vec3.ZERO,new Vec3(0,0,1),0x777777,true);
            var wire=new net.minecraft.network.FriendlyByteBuf(io.netty.buffer.Unpooled.buffer());
            try {Cod3VisualPacket.encode(p,wire);h.assertTrue(Cod3VisualPacket.decode(wire).equals(p)&&wire.readableBytes()==0,"Exact existing wire round trip for VFX#3: "+id);}finally{wire.release();}
            var feet=new Vec3(0,.3,0);var geometry=WeaponLift.geometry(p,1,feet,true);var moved=WeaponLift.geometry(p,1,feet.add(0,.2,0),true);
            h.assertTrue(geometry.size()==68&&WeaponLift.geometry(p,8,feet,true).isEmpty(),"Existing finite arc/dust budget and eight-tick expiry: "+id);
            for(int i=0;i<geometry.size();i++)h.assertTrue(moved.get(i).a().subtract(geometry.get(i).a()).distanceTo(i<20?new Vec3(0,.2,0):Vec3.ZERO)<1e-8,"Arc follows target; dust remains on original actual ground");
            var wrong=new Cod3VisualPacket(p.dimension(),34,p.entityId(),p.seed(),p.start(),p.duration(),p.scale(),p.origin(),p.direction(),p.sequence(),p.tick(),p.tint());
            h.assertTrue(!WeaponLift.accepts(wrong),"Swords' dust-template route cannot masquerade as longarm VFX#3");
        }
        h.assertTrue(WeaponLift.color(null)==-1&&WeaponLift.packet("minecraft:overworld",1,"iron_sword",0,0,1,Vec3.ZERO,Vec3.ZERO,0,true)==null,"No invented generic-weapon eligibility");
        h.succeed();
    }

}
