package com.sammy.malum.common.item.curiosities.weapons.scythe;

import com.sammy.malum.common.effect.gluttony.*;
import com.sammy.malum.core.helpers.*;
import com.sammy.malum.core.systems.spirit.SpiritLike;
import com.sammy.malum.registry.common.*;
import com.sammy.malum.registry.common.magic.*;
import com.sammy.malum.registry.common.sound.*;
import net.minecraft.server.level.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.item.*;
import net.neoforged.neoforge.client.event.*;
import net.neoforged.neoforge.event.entity.living.*;
import team.lodestar.lodestone.modules.toolkit.enchanting.LodestoneEnchantmentEffectCommonsHelper;
import team.lodestar.lodestone.modules.toolkit.item.*;
import team.lodestar.lodestone.modules.toolkit.sound.SoundPlayer;


public class RavenousScytheItem extends MagicScytheItem {

    public RavenousScytheItem(Tier tier, float attackDamage, float attackSpeed, float magicDamage, LodestoneItemProperties properties) {
        super(tier, attackDamage, attackSpeed, magicDamage, 0.5f, 3f, properties);
    }

    @Override
    public void modifyAttributeTooltipEvent(AddAttributeTooltipsEvent event) {
        event.addTooltipLines(TooltipComponentHelper.positiveItemEffect("ravenous_scythe_gluttony"));
    }

    @Override
    public SpiritLike getDefiningSpiritType(ItemStack stack) {
        return MalumSpiritTypes.EARTHEN_SPIRIT;
    }

    @Override
    public void outgoingDamageEvent(LivingDamageEvent.Pre event, LivingEntity attacker, LivingEntity target, ItemStack stack) {
        super.outgoingDamageEvent(event, attacker, target, stack);
        if (attacker.level() instanceof ServerLevel level) {
            var source = event.getSource();
            if (!source.is(MalumTags.DamageTypes.IS_SCYTHE) && !source.is(MalumDamageTypes.INVERTED_HEART_PROPAGATION)) {
                return;
            }
            if (source.is(MalumTags.DamageTypes.IS_SCYTHE_MELEE)) {
                if (!LodestoneEnchantmentEffectCommonsHelper.isChargedAttack(attacker)) {
                    return;
                }
                SoundPlayer.create(MalumGearSoundEvents.RAVENOUS_SCYTHE_EATS).pitch(1f, 1.5f).play(attacker);
            }
            if (source.is(MalumDamageTypes.SCYTHE_MAELSTROM)) {
                if (level.getRandom().nextFloat() >= 0.2f) {
                    return;
                }
            }
            GluttonyEffect.applyGluttony(attacker, b -> b
                    .setAmplifierGain(1)
                    .setAmplifierLimit(5));
        }
    }
}