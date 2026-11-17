package com.dynasty.sweepqa.mixin;
import com.dynasty.sweepqa.Probe;
import com.dynasty.cod3.*;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
@Mixin(targets="com.dynasty.client.Cod3VfxRenderer$Geometry",remap=false)
public abstract class PrimitiveProbe {
 @Shadow @Final Matrix4f matrix; @Shadow @Final Vec3 camera;
 @Shadow @Final int color; @Shadow @Final double alpha;
 @Unique int qa$id;
 @Inject(method="draw",at=@At("HEAD"),remap=false)
 private void qa$kind(int id,DynastyVfxDefinition d,double expand,double life,double age,CallbackInfo ci){qa$id=id;}
 @Inject(method="vertex",at=@At("HEAD"),remap=false)
 private void qa$vertex(Vec3 p,CallbackInfo ci){Probe.vertex("Vfx"+qa$id,matrix,p,color,alpha);}
 @Inject(method="triangle",at=@At("HEAD"),remap=false)
 private void qa$triangle(Vec3 a,Vec3 b,Vec3 c,double shade,CallbackInfo ci){if(a.distanceToSqr(camera)>=.64&&b.distanceToSqr(camera)>=.64&&c.distanceToSqr(camera)>=.64)Probe.triangle("Vfx"+qa$id,matrix,a,b,c,color,alpha);}
}
