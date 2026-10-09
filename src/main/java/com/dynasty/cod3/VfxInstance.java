package com.dynasty.cod3;

import net.minecraft.world.phys.Vec3;

public record VfxInstance(DynastyVfxDefinition definition,Vec3 origin,Vec3 direction,long seed,long start,int lifetime,double scale) {
    public enum Phase {SPAWN,EXPAND,SUSTAIN,COLLAPSE,END}
    public Phase phase(double age){return age>=lifetime?Phase.END:age<2?Phase.SPAWN:age<lifetime*.35?Phase.EXPAND:age<lifetime*.8?Phase.SUSTAIN:Phase.COLLAPSE;}
}
