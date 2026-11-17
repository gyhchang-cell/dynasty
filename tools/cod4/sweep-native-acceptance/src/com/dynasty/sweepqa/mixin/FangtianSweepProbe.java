package com.dynasty.sweepqa.mixin;
import com.dynasty.sweepqa.Probe;
import com.dynasty.cod3.*;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
@Mixin(targets="com.dynasty.client.FangtianSweepRenderer",remap=false)
public abstract class FangtianSweepProbe {
 @Inject(method="triangle",at=@At("HEAD"),remap=false)
 private static void qa$triangle(Matrix4f m,WeaponImpactVisual.Triangle t,CallbackInfo ci){Probe.triangle("FangtianSweep",m,t.a(),t.b(),t.c(),t.color(),t.alpha());}
}
