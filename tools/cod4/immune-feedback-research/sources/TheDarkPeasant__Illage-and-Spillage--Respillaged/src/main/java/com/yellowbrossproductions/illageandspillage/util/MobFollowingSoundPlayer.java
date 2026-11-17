package com.yellowbrossproductions.illageandspillage.util;

import com.yellowbrossproductions.illageandspillage.client.sound.MobFollowingSound;
import net.minecraft.client.Minecraft;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public class MobFollowingSoundPlayer {
    public static void playSound(Level level, Entity entity, SoundEvent sound, float volume, float pitch, boolean loop) {
        if (level.isClientSide) {
            Minecraft.getInstance().getSoundManager().play(new MobFollowingSound(entity, sound, volume, pitch, loop));
        }
    }
}