package com.sammy.malum.core.handlers;

import com.sammy.malum.common.item.*;
import com.sammy.malum.config.*;
import com.sammy.malum.core.systems.events.*;
import com.sammy.malum.registry.common.*;
import com.sammy.malum.registry.common.sound.*;
import net.minecraft.world.entity.*;
import net.neoforged.neoforge.common.*;
import net.neoforged.neoforge.event.entity.living.*;
import net.neoforged.neoforge.event.tick.*;
import team.lodestar.lodestone.helpers.*;
import team.lodestar.lodestone.modules.core.easing.Easing;
import team.lodestar.lodestone.modules.toolkit.sound.SoundPlayer;
import team.lodestar.lodestone.registry.common.tag.*;
import team.lodestar.wayward_attributes.WaywardTags;

import static team.lodestar.lodestone.handlers.ItemEventHandler.*;

public class SoulWardHandler {

    public static void entityTick(EntityTickEvent.Pre event) {
        if (event.getEntity() instanceof LivingEntity living) {
            var level = living.level();
            if (!level.isClientSide) {
                if (living.getAttributeValue(MalumAttributes.SOUL_WARD_CAPACITY) == 0 && !living.hasData(MalumAttachmentTypes.SOUL_WARD)) {
                    return;
                }
                var data = living.getData(MalumAttachmentTypes.SOUL_WARD);
                data.tickData(living);
            }
        }
    }

    public static void shieldPlayer(LivingDamageEvent.Pre event) {
        var living = event.getEntity();
        if (living.level().isClientSide()) {
            return;
        }
        if (event.getNewDamage() <= 0) {
            return;
        }
        var source = event.getSource();
        if (source.is(MalumTags.DamageTypes.BYPASSES_SOUL_WARD)) {
            return;
        }

        var data = living.getData(MalumAttachmentTypes.SOUL_WARD);
        data.addCooldown(living, 4f);
        if (!data.isDepleted()) {
            float amount = event.getNewDamage();
            double magicDamageAbsorption = 1 - CommonConfig.SOUL_WARD_MAGIC.getConfigValue();
            double physicalDamageAbsorption = 1 - CommonConfig.SOUL_WARD_PHYSICAL.getConfigValue();
            double integrity = living.getAttributeValue(MalumAttributes.SOUL_WARD_INTEGRITY)*2;
            var eventResponders = getEventResponders(living);
            var propertiesEvent = new ModifySoulWardPropertiesEvent(living, data, source, physicalDamageAbsorption, magicDamageAbsorption, integrity);
            eventResponders.forEach(lookup -> lookup.run(IMalumEventResponder.class, (eventResponderItem, stack) ->
                    eventResponderItem.modifySoulWardPropertiesEvent(propertiesEvent, living, stack)));
            NeoForge.EVENT_BUS.post(propertiesEvent);
            magicDamageAbsorption = propertiesEvent.getNewMagicDamageAbsorption();
            physicalDamageAbsorption = propertiesEvent.getNewPhysicalDamageAbsorption();
            integrity = propertiesEvent.getNewIntegrity();

            double absorptionMultiplier = source.is(WaywardTags.DamageTypeTags.IS_MAGIC) ? magicDamageAbsorption : physicalDamageAbsorption;
            double absorbedDamage = amount * (absorptionMultiplier);
            double soulWardDamage = absorbedDamage / Math.max(integrity, 0.01f);
            data.reduceSoulWard(soulWardDamage);

            var damageEvent = new SoulWardDamageEvent(living, data, source, absorbedDamage, soulWardDamage);
            eventResponders.forEach(lookup -> lookup.run(IMalumEventResponder.class, (eventResponderItem, stack) ->
                    eventResponderItem.soulWardDamageEvent(damageEvent, living, stack)));
            NeoForge.EVENT_BUS.post(damageEvent);

            var sound = data.getSoulWard() == 0 ? MalumSoundEvents.SOUL_WARD_DEPLETE : MalumSoundEvents.SOUL_WARD_HIT;
            var volume = source.is(MalumDamageTypes.KARMIC) ? 0.2f : 0.5f; //reduced volume for karmic damage, specifically with the pact of patience repaid in mind
            SoundPlayer.create(sound).volume(volume).pitch(1f, 1.5f).play(living);
            event.setNewDamage((float) (amount - absorbedDamage));
        }
    }
}