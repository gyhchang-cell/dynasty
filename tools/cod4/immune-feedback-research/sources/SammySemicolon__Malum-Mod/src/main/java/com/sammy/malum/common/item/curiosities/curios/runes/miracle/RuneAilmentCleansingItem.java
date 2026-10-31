package com.sammy.malum.common.item.curiosities.curios.runes.miracle;

import com.sammy.malum.core.helpers.*;
import com.sammy.malum.registry.common.MalumContent;
import com.sammy.malum.registry.common.magic.MalumSpiritTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.world.effect.MobEffect;
import net.minecraft.world.effect.MobEffectCategory;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.LivingEntity;
import net.neoforged.neoforge.event.entity.living.MobEffectEvent;
import team.lodestar.lodestone.helpers.CurioHelper;
import team.lodestar.lodestone.helpers.EntityHelper;

import java.util.function.Consumer;

public class RuneAilmentCleansingItem extends MiracleRuneCurioItem {

    public RuneAilmentCleansingItem(Properties builder) {
        super(builder, MalumSpiritTypes.AQUEOUS_SPIRIT);
    }

    @Override
    public void addExtraTooltipLines(Consumer<Component> consumer) {
        consumer.accept(TooltipComponentHelper.positiveCurioEffect("shorten_negative_effect"));
    }

    public static void scaleDuration(MobEffectEvent.Added event) {
        LivingEntity entity = event.getEntity();
        if (event.getOldEffectInstance() == null && CurioHelper.hasCurioEquipped(entity, MalumContent.Gear.RUNE_OF_AILMENT_CLEANSING.get())) {
            MobEffectInstance effect = event.getEffectInstance();
            MobEffect type = effect.getEffect().value();
            if (type.getCategory().equals(MobEffectCategory.HARMFUL)) {
                EntityHelper.shortenEffect(effect, entity, effect.getDuration() / 3);
            }
        }
    }
}
