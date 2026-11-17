package com.sammy.malum.common.data.attachment;

import com.mojang.serialization.*;
import com.mojang.serialization.codecs.*;
import com.sammy.malum.config.*;
import com.sammy.malum.registry.common.*;
import com.sammy.malum.registry.common.sound.*;
import io.netty.buffer.*;
import net.minecraft.core.*;
import net.minecraft.network.codec.*;
import net.minecraft.util.*;
import net.minecraft.world.entity.*;
import net.minecraft.world.entity.ai.attributes.*;
import net.minecraft.world.entity.player.*;
import team.lodestar.lodestone.helpers.*;
import team.lodestar.lodestone.modules.toolkit.sound.SoundPlayer;

import java.util.*;

public class MalignantInfluenceData {

    public static Codec<MalignantInfluenceData> CODEC = RecordCodecBuilder.create(obj -> obj.group(
            Codec.INT.optionalFieldOf("malignantAegis", 0).forGetter(MalignantInfluenceData::getMalignantAegis),
            Codec.INT.optionalFieldOf("aegisCooldown", 0).forGetter(MalignantInfluenceData::getMalignantAegis)
    ).apply(obj, MalignantInfluenceData::new));

    public static StreamCodec<ByteBuf, MalignantInfluenceData> STREAM_CODEC = ByteBufCodecs.fromCodec(MalignantInfluenceData.CODEC);

    protected final HashMap<Holder<Attribute>, Double> cachedAttributeValues = new HashMap<>();
    protected int malignantAegis;
    protected int aegisCooldown;
    protected boolean isDirty;

    public MalignantInfluenceData() {
    }

    public MalignantInfluenceData(int malignantAegis, int aegisCooldown) {
        this.malignantAegis = malignantAegis;
        this.aegisCooldown = aegisCooldown;
    }

    public void tickData(LivingEntity entity) {
        int limit = getMalignantAegisCapacity(entity);
        if (getMalignantAegis() < limit) {
            if (aegisCooldown > 0) {
                aegisCooldown--;
            }
            if (aegisCooldown <= 0) {
                recoverAegis(entity, 1);
            }
        }
        if (getMalignantAegis() > limit) {
            setAegis(limit);
        }
        if (isDirty) {
            if (!entity.level().isClientSide) {
                entity.syncData(MalumAttachmentTypes.MALIGNANT_INFLUENCE);
            }
            isDirty = false;
        }
    }

    @SuppressWarnings("DataFlowIssue")
    public void recoverAegis(LivingEntity entity, double amount) {
        var capacity = entity.getAttribute(MalumAttributes.MALIGNANT_AEGIS_CAPACITY);
        if (getMalignantAegis() < capacity.getValue()) {
            var multiplier = Optional.ofNullable(entity.getAttribute(MalumAttributes.MALIGNANT_AEGIS_RECOVERY_GAIN)).map(AttributeInstance::getValue).orElse(1.0);
            var previousAegis = malignantAegis;
            addAegis(Mth.ceil(amount * multiplier));
            if (malignantAegis > previousAegis) {
                if (!(entity instanceof Player player) || !player.isCreative()) {
                    var sound = malignantAegis >= capacity.getValue() ? MalumSoundEvents.MALIGNANT_AEGIS_FULLY_CHARGED : MalumSoundEvents.MALIGNANT_AEGIS_GROW;
                    double pitchOffset = (malignantAegis / capacity.getValue()) * 0.5f;
                    SoundPlayer.create(sound).volume(0.75f).pitchVariance(1f + pitchOffset).play(entity);
                }
            }
        }
        addCooldown(entity, 1f);
    }

    public void addAegis(int added) {
        setAegis(malignantAegis + added);
    }

    public void reduceAegis(int removed) {
        setAegis(malignantAegis - removed);
    }

    public void setAegis(int malignantAegis) {
        this.malignantAegis = Math.max(malignantAegis, 0);
        isDirty = true;
    }

    public void addCooldown(LivingEntity entity, float multiplier) {
        double newCooldown = getMalignantAegisCooldown(entity) * multiplier;
        if (aegisCooldown < newCooldown) {
            aegisCooldown = Mth.floor(newCooldown);
            isDirty = true;
        }
    }

    public void cacheValue(AttributeInstance attribute) {
        cachedAttributeValues.put(attribute.getAttribute(), attribute.getValue());
    }

    public boolean hasCachedValue(Holder<Attribute> attribute) {
        return cachedAttributeValues.containsKey(attribute);
    }

    public double getCachedValue(Holder<Attribute> attribute) {
        return cachedAttributeValues.getOrDefault(attribute, 0.0);
    }

    public int getMalignantAegis() {
        return malignantAegis;
    }

    public static Optional<MalignantInfluenceData> getMalignantAegisData(LivingEntity entity) {
        if (getMalignantAegisCapacity(entity) <= 0) {
            return Optional.empty();
        }
        return Optional.of(entity.getData(MalumAttachmentTypes.MALIGNANT_INFLUENCE));
    }

    public static int getMalignantAegisCapacity(LivingEntity entity) {
        double aegis = entity.getAttributeValue(MalumAttributes.MALIGNANT_AEGIS_CAPACITY);
        return Mth.ceil(aegis);
    }

    public float getMalignantAegisCooldown(LivingEntity entity) {
        double recoveryRate = entity.getAttributeValue(MalumAttributes.MALIGNANT_AEGIS_RECOVERY_RATE);
        var cooldownDuration = CommonConfig.MALIGNANT_AEGIS_RATE.getConfigValue();
        return Mth.floor(cooldownDuration / recoveryRate);
    }
}