package com.yellowbrossproductions.illageandspillage.client.sound;

import com.yellowbrossproductions.illageandspillage.entities.CrocofangEntity;
import com.yellowbrossproductions.illageandspillage.entities.HinderEntity;
import com.yellowbrossproductions.illageandspillage.entities.MagispellerEntity;
import net.minecraft.client.resources.sounds.AbstractTickableSoundInstance;
import net.minecraft.client.resources.sounds.SoundInstance;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class MobFollowingSound extends AbstractTickableSoundInstance {
    private final Entity entity;
    private float volumeMultiplier;
    private final float pitchMultiplier;
    private int timePlayed;

    public MobFollowingSound(Entity entity, SoundEvent sound, float volume, float pitch, boolean loop) {
        super(sound, entity.getSoundSource(), SoundInstance.createUnseededRandom());
        this.entity = entity;
        this.x = entity.getX();
        this.y = entity.getY();
        this.z = entity.getZ();
        this.volumeMultiplier = volume;
        this.pitchMultiplier = pitch;
        this.looping = loop;
    }

    @Override
    public float getVolume() {
        return super.getVolume() * this.volumeMultiplier;
    }

    @Override
    public float getPitch() {
        return super.getPitch() * this.pitchMultiplier;
    }

    @Override
    public void tick() {
        if (this.entity.isAlive() && !this.entity.isRemoved() && !this.entity.isSilent() && this.additionalPlayConditions()) {
            if (this.additionalPositionConditions()) {
                this.x = this.entity.getX();
                this.y = this.entity.getY();
                this.z = this.entity.getZ();
            }

        } else this.stop();

        this.timePlayed++;
    }

    private boolean additionalPlayConditions() {
        if (this.entity instanceof CrocofangEntity) {
            return ((CrocofangEntity) this.entity).isCharging() || this.timePlayed < 1;
        }

        if (this.entity instanceof HinderEntity) {
            return ((HinderEntity) this.entity).isHealing() || this.timePlayed < 1;
        }

        return true;
    }

    private boolean additionalPositionConditions() {
        if (this.entity instanceof MagispellerEntity magispeller && magispeller.getAttackType() == 3) {
            return magispeller.getAttackTicks() < 49;
        }

        return true;
    }
}
