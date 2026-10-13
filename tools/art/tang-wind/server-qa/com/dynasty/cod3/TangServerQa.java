package com.dynasty.cod3;

import com.dynasty.DynastyWeapons;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.effect.*;
import net.minecraft.world.item.*;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.event.entity.living.MobEffectEvent;
import net.minecraftforge.eventbus.api.Event;
import net.minecraftforge.gametest.*;
import java.util.UUID;
import java.util.function.Consumer;

/** Native vanilla attack/effect callbacks in a disposable server; not human acceptance. */
@GameTestHolder("dynasty_tang_qa") @PrefixGameTestTemplate(false)
public final class TangServerQa {
    private static FakePlayer player(GameTestHelper h) {
        var p=new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"tang-qa")) {
            @Override public float getAttackStrengthScale(float partial){return 1;}
        };
        p.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(DynastyWeapons.TANG_DAO.get()));p.setOnGround(true);return p;
    }
    private static void attack(GameTestHelper h,FakePlayer p) {
        var t=h.spawn(EntityType.COW,new BlockPos(4,2,4));t.setNoAi(true);t.setNoGravity(true);
        t.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);t.setHealth(1000);p.setPos(t.getX()-1,t.getY(),t.getZ());
        p.attack(t);h.assertTrue(t.getHealth()<1000,"Native attack did not run");t.discard();
    }
    private static boolean stamped(FakePlayer p){return p.getPersistentData().contains("cod3_tang_wind_at");}
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void nativeTangAttackAppliesOriginalSpeedAndWind(GameTestHelper h) {
        var p=player(h);attack(h,p);var effect=p.getEffect(MobEffects.MOVEMENT_SPEED);
        h.assertTrue(effect!=null&&effect.getDuration()==60&&effect.getAmplifier()==0&&effect.isAmbient()&&!effect.isVisible(),"Original speed parameters changed");
        h.assertTrue(stamped(p)&&p.getPersistentData().getLong("cod3_tang_wind_at")==h.getLevel().getGameTime(),"Accepted native effect missed cue");
        h.assertTrue(TangWind.accepts(TangWind.packet(h.getLevel().dimension().location().toString(),p.getId(),0,h.getLevel().getGameTime(),p.position(),p.getLookAngle())),"Invalid registered actor packet");
        p.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void strongerOrEqualSpeedCannotFabricateRefreshWind(GameTestHelper h) {
        for(int[] state:new int[][]{{0,60},{0,200},{1,200},{0,-1}}) {
            int amplifier=state[0],duration=state[1];
            var p=player(h);p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED,duration,amplifier));attack(h,p);
            h.assertTrue(!stamped(p),"Cosmetic flags or ineffective speed refresh fabricated wind: "+amplifier+"/"+duration);
            var effect=p.getEffect(MobEffects.MOVEMENT_SPEED);h.assertTrue(effect.getAmplifier()==amplifier&&effect.getDuration()==duration,"Existing speed changed");p.discard();
        }
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void shorterSpeedRefreshesAndSameTickCosmeticsStayBounded(GameTestHelper h) {
        var p=player(h);p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED,20,0));attack(h,p);
        h.assertTrue(stamped(p)&&p.getEffect(MobEffects.MOVEMENT_SPEED).getDuration()==60,"Actual refresh missed wind");
        long stamp=p.getPersistentData().getLong("cod3_tang_wind_at");TangWind.applied(p);h.assertTrue(p.getPersistentData().getLong("cod3_tang_wind_at")==stamp,"Duplicate changed stamp");
        var saved=p.saveWithoutId(new net.minecraft.nbt.CompoundTag());var restored=player(h);restored.load(saved);
        h.assertTrue(restored.getPersistentData().getLong("cod3_tang_wind_at")==stamp,"NBT lost cosmetic stamp");p.discard();restored.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void forgeDeniedEffectAndOtherWeaponCannotFabricateWind(GameTestHelper h) {
        var p=player(h);
        Consumer<MobEffectEvent.Applicable> deny=e->{if(e.getEntity()==p&&e.getEffectInstance().getEffect()==MobEffects.MOVEMENT_SPEED)e.setResult(Event.Result.DENY);};
        MinecraftForge.EVENT_BUS.addListener(deny);
        try{attack(h,p);h.assertTrue(!p.hasEffect(MobEffects.MOVEMENT_SPEED)&&!stamped(p),"Denied actual effect fabricated wind");}
        finally{MinecraftForge.EVENT_BUS.unregister(deny);}
        p.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(Items.IRON_SWORD));p.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SPEED,20,0));attack(h,p);
        h.assertTrue(!stamped(p),"Other weapon borrowed speed cue");p.discard();h.succeed();
    }
}
