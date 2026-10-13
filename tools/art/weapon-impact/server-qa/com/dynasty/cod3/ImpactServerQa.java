package com.dynasty.cod3;

import com.dynasty.expansion.ExpansionContent;
import com.mojang.authlib.GameProfile;
import net.minecraft.core.BlockPos;
import net.minecraft.gametest.framework.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.item.*;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.common.util.FakePlayer;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.gametest.*;
import java.util.*;

/** Disposable headless server; real Forge/vanilla callbacks, not real human players. */
@GameTestHolder("dynasty_impact_qa") @PrefixGameTestTemplate(false)
public final class ImpactServerQa {
    private static FakePlayer player(GameTestHelper h,String suffix) {
        return new FakePlayer(h.getLevel(),new GameProfile(UUID.randomUUID(),"impact-"+suffix)) {
            @Override public float getAttackStrengthScale(float partial){return 1;}
        };
    }
    private static Cow target(GameTestHelper h) {
        var t=h.spawn(EntityType.COW,new BlockPos(4,2,4));t.setNoAi(true);t.setNoGravity(true);
        t.getAttribute(Attributes.MAX_HEALTH).setBaseValue(1000);t.setHealth(1000);return t;
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void actualPlayerAttackInvokesListenerForSevenRegisteredMaterials(GameTestHelper h) {
        for(String id:new TreeSet<>(WeaponImpactVisual.weapons())) {
            var p=player(h,id);var t=target(h);p.setPos(t.getX()-1,t.getY(),t.getZ());p.setOnGround(true);
            p.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(ExpansionContent.item(id)));
            p.attack(t);
            h.assertTrue(t.getHealth()<1000,"Native primary attack caused no damage: "+id);
            h.assertTrue(p.getPersistentData().contains("cod3_material_impact_at")
                &&p.getPersistentData().getLong("cod3_material_impact_at")==h.getLevel().getGameTime(),"Actual Forge callback missed cue: "+id);
            h.assertTrue(WeaponImpactVisual.accepts(WeaponImpactVisual.packet(h.getLevel().dimension().location().toString(),id,0,h.getLevel().getGameTime(),t.position(),p.getLookAngle())),"Registered item cannot form valid original wire cue: "+id);
            t.discard();p.discard();
        }
        h.succeed();
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void canceledZeroArrowAndIndirectDamageCannotBorrowHeldMaterial(GameTestHelper h) {
        var p=player(h,"reject");var t=target(h);p.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(ExpansionContent.item("qinggang_sword")));
        var arrow=new Arrow(h.getLevel(),p);arrow.getPersistentData().put("cod3_firing_weapon",new ItemStack(Items.BOW).save(new net.minecraft.nbt.CompoundTag()));
        var canceled=new LivingDamageEvent(t,p.damageSources().playerAttack(p),10);canceled.setCanceled(true);
        for(var e:List.of(canceled,new LivingDamageEvent(t,p.damageSources().playerAttack(p),0),new LivingDamageEvent(t,p.damageSources().arrow(arrow,p),10),new LivingDamageEvent(t,p.damageSources().indirectMagic(p,p),10))) {
            // Direct dispatch exercises the explicit cancellation guard too; the
            // event bus additionally skips canceled events by default.
            WeaponImpactVisual.hit(e);
            h.assertTrue(!p.getPersistentData().contains("cod3_material_impact_at"),"Rejected source fabricated material cue");
        }
        p.setItemSlot(EquipmentSlot.MAINHAND,new ItemStack(Items.IRON_SWORD));
        MinecraftForge.EVENT_BUS.post(new LivingDamageEvent(t,p.damageSources().playerAttack(p),10));
        h.assertTrue(!p.getPersistentData().contains("cod3_material_impact_at"),"Foreign item fabricated Dynasty cue");
        h.assertTrue(t.getHealth()==1000,"Presentation reapplied damage");t.discard();p.discard();h.succeed();
    }
    @GameTest(template="bow_ritual_test",setupTicks=20)
    public static void cosmeticStampBoundsSameTickAndSurvivesRealPlayerNbtRoundTrip(GameTestHelper h) {
        var p=player(h,"stamp");var d=p.getPersistentData();
        h.assertTrue(WeaponImpactVisual.stamp(d,0)&&!WeaponImpactVisual.stamp(d,0),"First game tick or duplicate handling failed");
        var saved=new net.minecraft.nbt.CompoundTag();p.saveWithoutId(saved);var restored=player(h,"restored");restored.load(saved);
        h.assertTrue(!WeaponImpactVisual.stamp(restored.getPersistentData(),0)&&WeaponImpactVisual.stamp(restored.getPersistentData(),1),"NBT reload repeats same-tick cue or blocks later hit");
        h.assertTrue(p.getHealth()==p.getMaxHealth(),"Cosmetic stamp changed health");p.discard();restored.discard();h.succeed();
    }
}
