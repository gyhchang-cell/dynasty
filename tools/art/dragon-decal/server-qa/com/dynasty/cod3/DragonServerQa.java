package com.dynasty.cod3;

import com.dynasty.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.boss.enderdragon.EnderDragon;
import net.minecraft.world.entity.boss.enderdragon.phases.EnderDragonPhase;
import net.minecraft.world.item.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.event.entity.player.AttackEntityEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.gametest.*;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.*;
import java.util.function.Consumer;

@GameTestHolder("dynasty_dragon_qa") @PrefixGameTestTemplate(false)
public final class DragonServerQa {
    private static FakePlayer player(GameTestHelper h,Item item) {
        var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"dragon-qa")) {
            @Override public float getAttackStrengthScale(float partial){return 1;}
        };p.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(item));p.setOnGround(true);return p;
    }
    private static LivingEntity target(GameTestHelper h,String id) {
        var type=ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation(id));var t=(LivingEntity)type.create(h.getLevel());
        var pos=h.absolutePos(new BlockPos(4,2,4));t.setPos(pos.getX()+.5,pos.getY(),pos.getZ()+.5);
        if(t instanceof Mob m)m.setNoAi(true);t.setNoGravity(true);h.getLevel().addFreshEntity(t);t.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);t.setHealth(1000);return t;
    }
    private static void attack(FakePlayer p,Entity t){p.setPos(t.getX()-1,t.getY(),t.getZ());p.attack(t);}
    private static boolean stamped(FakePlayer p){return p.getPersistentData().contains(DragonDecal.STAMP);}
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void twoRegisteredDragonsEmitAtRealBodySurface(GameTestHelper h) {
        for(String id:List.of("dynasty:dragon_king","dynasty:dragon_emperor")) {
            var t=target(h,id);var p=player(h,DynastyWeapons.DRAGON_SLAYER.get());var cues=new ArrayList<Cod3VisualPacket>();
            Consumer<LivingDamageEvent> observe=e->{if(e.getEntity()==t){var cue=DragonDecal.cueFor(e);if(cue!=null)cues.add(cue);}};
            MinecraftForge.EVENT_BUS.addListener(EventPriority.LOW,observe);
            try{attack(p,t);h.assertTrue(t.getHealth()<1000&&stamped(p)&&cues.size()==1,"Native registered dragon did not emit exactly one cue: "+id+" HP="+t.getHealth()+" stamp="+stamped(p)+" cues="+cues.size()+" tag="+DragonDecal.target(t));
                var cue=cues.get(0);h.assertTrue(DragonDecal.accepts(cue),"Actual packet invalid");
                h.assertTrue(t.position().add(cue.origin()).distanceTo(DragonDecal.surface(t,cue.direction()))<1e-5,"Wrong body surface anchor");
                h.assertTrue(DynastyBalance.weaponBonus("dragon_slayer")==350,"Existing weapon bonus changed");
            }finally{MinecraftForge.EVENT_BUS.unregister(observe);t.discard();p.discard();}
        }h.succeed();
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void nativeEnderDragonHeadUsesPartRatherThanParentCenter(GameTestHelper h) {
        var t=(EnderDragon)target(h,"minecraft:ender_dragon");t.getPhaseManager().setPhase(EnderDragonPhase.HOLDING_PATTERN);
        t.head.setPos(t.position().add(6,2,0));var p=player(h,DynastyWeapons.DRAGON_SLAYER.get());var cues=new ArrayList<Cod3VisualPacket>();
        Consumer<LivingDamageEvent> observe=e->{if(e.getEntity()==t){var cue=DragonDecal.cueFor(e);if(cue!=null)cues.add(cue);}};
        MinecraftForge.EVENT_BUS.addListener(EventPriority.LOW,observe);
        try{attack(p,t.head);h.assertTrue(t.getHealth()<1000&&stamped(p)&&cues.size()==1,"Actual Player.attack(dragon.head) missed final callback: HP="+t.getHealth()+" stamp="+stamped(p)+" cues="+cues.size()+" tag="+DragonDecal.target(t));
            var cue=cues.get(0);var world=t.position().add(cue.origin());h.assertTrue(world.distanceTo(DragonDecal.surface(t.head,cue.direction()))<1e-5,"Cue did not retain actual hit-part anchor");
            h.assertTrue(world.distanceTo(DragonDecal.surface(t,cue.direction()))>2,"Cue accidentally used parent bounds");
            h.assertTrue(cue.tick()>0&&DragonDecal.anchor(cue,t,1).distanceTo(world)<1e-5,"Multipart slot or actual pose anchor lost");
            var headBefore=t.head.position();t.head.setPos(headBefore.add(0,1,2));
            h.assertTrue(DragonDecal.anchor(cue,t,1).subtract(world).distanceTo(new Vec3(0,1,2))<1e-5,"Turning/moving head detached decal");
            h.assertTrue(DragonDecal.anchor(cue,t,Double.NaN)==null,"Invalid interpolation accepted");t.head.setPos(headBefore);
            var moved=new Vec3(3,2,-4);var before=DragonDecal.geometry(cue,1,t.position());var after=DragonDecal.geometry(cue,1,t.position().add(moved));
            h.assertTrue(after.get(0).a().position().subtract(before.get(0).a().position()).distanceTo(moved)<1e-8,"Multipart cue detached from interpolated parent movement");
        }finally{MinecraftForge.EVENT_BUS.unregister(observe);t.discard();p.discard();}h.succeed();
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void ordinaryTargetWrongWeaponAndIndirectSourceRejected(GameTestHelper h) {
        var p=player(h,DynastyWeapons.DRAGON_SLAYER.get());var t=target(h,"minecraft:cow");attack(p,t);
        h.assertTrue(t.getHealth()<1000&&!stamped(p)&&!DragonDecal.target(t),"Ordinary target borrowed dragon cue");t.discard();p.discard();
        p=player(h,Items.IRON_SWORD);t=target(h,"dynasty:dragon_king");attack(p,t);h.assertTrue(t.getHealth()<1000&&!stamped(p),"Wrong sword emitted dragon glyph");p.discard();t.discard();
        p=player(h,DynastyWeapons.DRAGON_SLAYER.get());t=target(h,"dynasty:dragon_king");
        var arrow=new net.minecraft.world.entity.projectile.Arrow(h.getLevel(),p);DragonDecal.hit(new LivingDamageEvent(t,p.damageSources().arrow(arrow,p),20));
        h.assertTrue(!stamped(p),"Indirect damage substituted currently held blade");arrow.discard();p.discard();t.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void laterCanceledNativeHitAndZeroDamageRejectCue(GameTestHelper h) {
        var p=player(h,DynastyWeapons.DRAGON_SLAYER.get());var t=target(h,"dynasty:dragon_king");
        Consumer<LivingHurtEvent> cancel=e->{if(e.getEntity()==t)e.setCanceled(true);};MinecraftForge.EVENT_BUS.addListener(EventPriority.LOW,cancel);
        try{attack(p,t);h.assertTrue(t.getHealth()==1000&&!stamped(p),"Canceled native hit emitted glyph");}finally{MinecraftForge.EVENT_BUS.unregister(cancel);}
        var source=p.damageSources().playerAttack(p);for(float amount:new float[]{0,-1,Float.NaN}){
            DragonDecal.hit(new LivingDamageEvent(t,source,amount));h.assertTrue(!stamped(p),"Non-positive/NaN damage emitted glyph");}
        var canceled=new LivingDamageEvent(t,source,100);canceled.setCanceled(true);DragonDecal.hit(canceled);h.assertTrue(!stamped(p),"Canceled final damage emitted glyph");
        t.discard();p.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void multipartReceiptExpiresAndNpcNamesCannotGuessDragon(GameTestHelper h) {
        var p=player(h,DynastyWeapons.DRAGON_SLAYER.get());var t=(EnderDragon)target(h,"minecraft:ender_dragon");t.head.setPos(t.position().add(6,2,0));
        DragonDecal.partAttack(new AttackEntityEvent(p,t.head));var source=p.damageSources().playerAttack(p);
        h.assertTrue(DragonDecal.cueFor(new LivingDamageEvent(t,source,100))!=null,"Part receipt not recorded: target="+DragonDecal.target(t)+" item="+ForgeRegistries.ITEMS.getKey(p.getMainHandItem().getItem())+" partId="+t.head.getId()+" parentId="+t.getId());
        var cow=target(h,"minecraft:cow");cow.setCustomName(net.minecraft.network.chat.Component.literal("dragon_emperor"));
        h.assertTrue(!DragonDecal.target(cow),"Name string guessed dragon classification");cow.discard();
        h.runAfterDelay(2,()->{DragonDecal.hit(new LivingDamageEvent(t,source,100));h.assertTrue(!stamped(p),"Expired multipart receipt remained actionable");t.discard();p.discard();h.succeed();});
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void sameTickStampAndNbtDoNotReapplyDamage(GameTestHelper h) {
        var p=player(h,DynastyWeapons.DRAGON_SLAYER.get());var t=target(h,"dynasty:dragon_king");DynastySchoolCombat.attack(new AttackEntityEvent(p,t));var source=p.damageSources().playerAttack(p);
        DragonDecal.hit(new LivingDamageEvent(t,source,100));DragonDecal.hit(new LivingDamageEvent(t,source,100));
        h.assertTrue(t.getHealth()==1000&&stamped(p),"Presentation added damage or lost stamp");
        var restored=player(h,DynastyWeapons.DRAGON_SLAYER.get());restored.load(p.saveWithoutId(new net.minecraft.nbt.CompoundTag()));
        h.assertTrue(restored.getPersistentData().getLong(DragonDecal.STAMP)==h.getLevel().getGameTime(),"NBT stamp lost");
        t.discard();p.discard();restored.discard();h.succeed();
    }
}
