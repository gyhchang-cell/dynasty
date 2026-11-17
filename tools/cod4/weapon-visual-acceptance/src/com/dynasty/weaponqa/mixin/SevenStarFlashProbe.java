package com.dynasty.weaponqa.mixin;
import com.dynasty.weaponqa.Probe;
import com.dynasty.cod3.*;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
@Mixin(targets="com.dynasty.client.SevenStarFlashRenderer",remap=false)
public abstract class SevenStarFlashProbe {
 @Inject(method="triangle",at=@At("HEAD"),remap=false)
 private static void qa$triangle(Matrix4f m,Vec3 a,Vec3 b,Vec3 c,double alpha,int tint,CallbackInfo ci){Probe.triangle("SevenStarFlash",m,a,b,c,tint,alpha);}
}
