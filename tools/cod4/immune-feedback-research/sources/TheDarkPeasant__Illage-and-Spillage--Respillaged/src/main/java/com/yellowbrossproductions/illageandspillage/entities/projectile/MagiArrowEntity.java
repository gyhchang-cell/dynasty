package com.yellowbrossproductions.illageandspillage.entities.projectile;

import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.level.Level;

public class MagiArrowEntity extends Arrow {
    public MagiArrowEntity(EntityType<? extends Arrow> p_36858_, Level p_36859_) {
        super(p_36858_, p_36859_);
    }

    public MagiArrowEntity(Level p_36866_, LivingEntity p_36867_) {
        super(p_36866_, p_36867_);
    }

    public void tick() {
        super.tick();
        if (this.tickCount > 80) {
            this.discard();
        }

    }
}
