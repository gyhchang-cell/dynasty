package com.yellowbrossproductions.illageandspillage.util;

import net.minecraft.client.Minecraft;
import net.minecraft.world.level.Level;

import javax.annotation.Nullable;

public class ClientHelper {
    @Nullable
    public static Level getLevel() {
        return Minecraft.getInstance().level;
    }

}