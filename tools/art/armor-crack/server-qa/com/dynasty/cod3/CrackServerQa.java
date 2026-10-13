package com.dynasty.cod3;

import com.dynasty.*;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.*;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.event.entity.living.*;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.gametest.*;
import net.minecraftforge.registries.ForgeRegistries;
import java.util.UUID;
import java.util.function.Consumer;

@GameTestHolder("dynasty_crack_qa") @PrefixGameTestTemplate(false)
public final class CrackServerQa {
    private static FakePlayer player(GameTestHelper h,Item item) {
        var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"crack-qa")) {
            @Override public float getAttackStrengthScale(float partial){return 1;}
        };p.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(item));p.setOnGround(true);return p;
    }
    private static LivingEntity target(GameTestHelper h,boolean dynasty) {
        LivingEntity t;
        if(dynasty){t=(LivingEntity)ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("dynasty:bandit_thug")).create(h.getLevel());var pos=h.absolutePos(new BlockPos(4,2,4));t.setPos(pos.getX()+.5,pos.getY(),pos.getZ()+.5);h.getLevel().addFreshEntity(t);}
        else t=h.spawn(EntityType.COW,new BlockPos(4,2,4));
        if(t instanceof Mob m)m.setNoAi(true);t.setNoGravity(true);t.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);t.setHealth(1000);return t;
    }
    private static boolean stamped(FakePlayer p){return p.getPersistentData().contains("cod3_armor_crack_at");}
    private static void attack(FakePlayer p,LivingEntity t){p.setPos(t.getX()-1,t.getY(),t.getZ());p.attack(t);}
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void twoRegisteredAxesTriggerOnlyAfterNativeMoraleHit(GameTestHelper h) {
        for(var item:new Item[]{DynastyWeapons.POJUN_AXE.get(),DynastyWeapons.XUANTIAN_AXE.get()}) {
            var p=player(h,item);var t=target(h,true);h.assertTrue(DynastyBalance.mobToughness(t.getType())>0,"No actual target morale");attack(p,t);
            h.assertTrue(t.getHealth()<1000&&stamped(p),"Native axe hit missed confirmed crack");
            h.assertTrue(p.getPersistentData().getLong("cod3_armor_crack_at")==h.getLevel().getGameTime(),"Wrong trigger tick");
            t.discard();p.discard();
        }h.succeed();
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void ordinaryArmorAndAnotherAxeCannotBorrowMoraleCrack(GameTestHelper h) {
        var p=player(h,DynastyWeapons.POJUN_AXE.get());var t=target(h,false);t.getAttribute(Attributes.ARMOR).setBaseValue(10);attack(p,t);
        h.assertTrue(t.getHealth()<1000&&!stamped(p),"Zero-morale vanilla armor fabricated crack");t.discard();p.discard();
        p=player(h,Items.IRON_AXE);t=target(h,true);attack(p,t);h.assertTrue(t.getHealth()<1000&&!stamped(p),"Axe item class fabricated reduction receipt");t.discard();p.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void originalMathAndExactSourceVictimReceiptRemainIntact(GameTestHelper h) {
        for(var item:new Item[]{DynastyWeapons.POJUN_AXE.get(),DynastyWeapons.XUANTIAN_AXE.get()}) {
            var p=player(h,item);var t=target(h,true);var source=p.damageSources().playerAttack(p);
            var hurt=new LivingHurtEvent(t,source,100);DynastyCombatEvents.onLivingHurt(hurt);
            double expected=(100+DynastyBalance.weaponBonus(DynastyTrinkets.idOf(p.getMainHandItem())))*(1-DynastyBalance.mobToughness(t.getType())*.5);
            h.assertTrue(Math.abs(hurt.getAmount()-expected)<.01,"Original morale/weapon damage changed");
            ArmorCrack.finalDamage(new LivingDamageEvent(t,p.damageSources().playerAttack(p),hurt.getAmount()));h.assertTrue(!stamped(p),"Unrelated DamageSource stole receipt");
            var wrong=target(h,true);ArmorCrack.finalDamage(new LivingDamageEvent(wrong,source,hurt.getAmount()));h.assertTrue(!stamped(p),"Unrelated victim stole receipt");wrong.discard();
            ArmorCrack.finalDamage(new LivingDamageEvent(t,source,hurt.getAmount()));h.assertTrue(stamped(p),"Exact final source/victim did not consume receipt");
            h.assertTrue(t.getHealth()==1000,"Visual receipt reapplied gameplay damage");
            var nbt=p.saveWithoutId(new net.minecraft.nbt.CompoundTag());var restored=player(h,item);restored.load(nbt);
            h.assertTrue(restored.getPersistentData().getLong("cod3_armor_crack_at")==h.getLevel().getGameTime(),"NBT lost per-tick cosmetic stamp");restored.discard();p.discard();t.discard();
        }h.succeed();
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void nativeLaterCancellationAndZeroFinalDamageDoNotEmit(GameTestHelper h) {
        var p=player(h,DynastyWeapons.POJUN_AXE.get());var t=target(h,true);
        Consumer<LivingHurtEvent> cancel=e->{if(e.getEntity()==t)e.setCanceled(true);};MinecraftForge.EVENT_BUS.addListener(EventPriority.LOW,cancel);
        try{attack(p,t);h.assertTrue(t.getHealth()==1000&&!stamped(p),"Canceled native hit emitted crack or damage");}finally{MinecraftForge.EVENT_BUS.unregister(cancel);}
        var source=p.damageSources().playerAttack(p);DynastyCombatEvents.onLivingHurt(new LivingHurtEvent(t,source,100));
        ArmorCrack.finalDamage(new LivingDamageEvent(t,source,0));h.assertTrue(!stamped(p),"Zero final damage emitted crack");
        ArmorCrack.finalDamage(new LivingDamageEvent(t,source,100));h.assertTrue(!stamped(p),"Consumed zero receipt could be replayed");
        t.discard();p.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void receiptExpiresAtServerTickAndRejectsInventedReduction(GameTestHelper h) {
        var p=player(h,DynastyWeapons.POJUN_AXE.get());var t=target(h,true);var source=p.damageSources().playerAttack(p);var hurt=new LivingHurtEvent(t,source,100);
        for(double[] values:new double[][]{{0,0},{.35,.35},{Double.NaN,0}})ArmorCrack.reduced(hurt,p,"pojun_axe",values[0],values[1]);
        ArmorCrack.reduced(hurt,p,"iron_axe",.35,.175);ArmorCrack.finalDamage(new LivingDamageEvent(t,source,100));h.assertTrue(!stamped(p),"Invented/non-reduced state emitted crack");
        DynastyCombatEvents.onLivingHurt(hurt);
        h.runAfterDelay(2,()->{ArmorCrack.finalDamage(new LivingDamageEvent(t,source,100));h.assertTrue(!stamped(p),"Previous-tick receipt survived and emitted crack");t.discard();p.discard();h.succeed();});
    }
}
