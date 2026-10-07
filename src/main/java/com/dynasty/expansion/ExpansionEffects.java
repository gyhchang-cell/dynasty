package com.dynasty.expansion;

import com.dynasty.DynastyEffects;
import com.dynasty.DynastyBalance;
import net.minecraft.world.effect.*;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraftforge.registries.RegistryObject;
import java.nio.charset.StandardCharsets;
import java.util.UUID;

/** Effects share the existing registry; all stacking and damage are server-authoritative. */
public final class ExpansionEffects {
    public static final RegistryObject<MobEffect> YIN = effect("yin_qi", false, 0x556A83, Attributes.MOVEMENT_SPEED, -.06);
    public static final RegistryObject<MobEffect> YANG = effect("yang_qi", true, 0xE7C866, Attributes.ATTACK_DAMAGE, .04);
    public static final RegistryObject<MobEffect> SHA = effect("sha_qi", false, 0x652D72, Attributes.ATTACK_DAMAGE, -.12);
    public static final RegistryObject<MobEffect> THUNDER = effect("thunder_mark", false, 0x8FE3F3, null, 0);
    public static final RegistryObject<MobEffect> SOUL = effect("soul_burn", false, 0x46BCDA, null, 0);
    public static final RegistryObject<MobEffect> FROST = effect("frost_vein", false, 0xBCE9F5, Attributes.MOVEMENT_SPEED, -.18);
    public static final RegistryObject<MobEffect> BREAK = effect("armor_break", false, 0xB78664, Attributes.ARMOR, -.20);
    public static final RegistryObject<MobEffect> STAGGER = effect("stagger", false, 0xAAA09B, Attributes.MOVEMENT_SPEED, -.65);
    public static void bootstrap() { }
    private static RegistryObject<MobEffect> effect(String id, boolean good, int color, Attribute attr, double amount) {
        return DynastyEffects.EFFECTS.register(id, () -> new MobEffect(good ? MobEffectCategory.BENEFICIAL : MobEffectCategory.HARMFUL, color) {
            { if (attr != null) addAttributeModifier(attr, UUID.nameUUIDFromBytes(("dynasty:"+id).getBytes(StandardCharsets.UTF_8)).toString(), amount, AttributeModifier.Operation.MULTIPLY_TOTAL); }
            @Override public boolean isDurationEffectTick(int duration, int amplifier) { return duration % 20 == 0; }
            @Override public void applyEffectTick(LivingEntity target, int amplifier) {
                if (target.level().isClientSide) return;
                if (id.equals("soul_burn")) target.hurt(target.damageSources().magic(), target.hasEffect(MobEffects.FIRE_RESISTANCE) ? 1 : 2);
                if (id.equals("yin_qi")) target.hurt(target.damageSources().magic(), amplifier + 1);
                if (id.equals("frost_vein") && target.isOnFire()) target.removeEffect(this);
            }
        });
    }
    public static boolean boss(LivingEntity target) {
        return target instanceof com.dynasty.ritual.ZhenyuanSovereign || target instanceof com.dynasty.DynastyBossCombat.BarHolder || !target.canChangeDimensions() || DynastyBalance.isBossOrBeast(target.getType());
    }
    public static void apply(LivingEntity target, RegistryObject<MobEffect> type, int duration) {
        if (target.level().isClientSide) return;
        if ((type == SHA || type == STAGGER) && boss(target)) { CombatFeedback.send(target, CombatFeedback.IMMUNE); return; }
        if (type == YIN && target.hasEffect(YANG.get())) { target.removeEffect(YANG.get()); return; }
        if (type == YANG && target.hasEffect(YIN.get())) { target.removeEffect(YIN.get()); return; }
        var old = target.getEffect(type.get());
        int amp = (type == YIN || type == YANG || type == THUNDER) && old != null ? Math.min(2, old.getAmplifier()+1) : 0;
        if (type == THUNDER && amp == 2) {
            target.removeEffect(type.get());
            target.hurt(target.damageSources().magic(), 12);
            CombatFeedback.send(target, CombatFeedback.THUNDER);
            return;
        }
        target.addEffect(new MobEffectInstance(type.get(), type == BREAK && boss(target) ? duration/2 : duration, amp));
    }
    private ExpansionEffects() { }
}
