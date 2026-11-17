package com.dynasty.weaponqa.mixin;
import com.dynasty.weaponqa.Probe;
import com.dynasty.cod3.DragonDecal;
import org.joml.Matrix4f;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
@Mixin(targets="com.dynasty.client.DragonDecalRenderer",remap=false)
public abstract class DragonDecalProbe {
 @Inject(method="triangle",at=@At("HEAD"),remap=false) private static void qa$triangle(Matrix4f m,DragonDecal.Triangle t,CallbackInfo ci){Probe.triangle("DragonDecal",m,t.a().position(),t.b().position(),t.c().position(),0xffffff,t.alpha());}
}
