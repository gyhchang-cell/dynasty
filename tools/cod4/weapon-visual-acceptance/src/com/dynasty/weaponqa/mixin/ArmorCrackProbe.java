package com.dynasty.weaponqa.mixin;
import com.dynasty.weaponqa.Probe;
import com.dynasty.cod3.*;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
@Mixin(targets="com.dynasty.client.ArmorCrackRenderer",remap=false)
public abstract class ArmorCrackProbe {
 @Inject(method="triangle",at=@At("HEAD"),remap=false)
 private static void qa$triangle(Matrix4f m,WeaponImpactVisual.Triangle t,CallbackInfo ci){Probe.triangle("ArmorCrack",m,t.a(),t.b(),t.c(),t.color(),t.alpha());}
}
