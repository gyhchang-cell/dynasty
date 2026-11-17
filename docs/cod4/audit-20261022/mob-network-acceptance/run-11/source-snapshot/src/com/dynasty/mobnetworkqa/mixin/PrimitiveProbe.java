package com.dynasty.mobnetworkqa.mixin;
import com.dynasty.mobnetworkqa.NativeStatusProbe;
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
 @Unique int qa$id; @Unique String qa$kind="Vfx0";
 @Inject(method="draw",at=@At("HEAD"),remap=false)
 private void qa$kind(int id,DynastyVfxDefinition d,double expand,double life,double age,CallbackInfo ci){qa$id=id;qa$kind="Vfx"+id;}
 @Inject(method="status",at=@At("HEAD"),remap=false) private void qa$status(int code,int layers,double age,CallbackInfo ci){qa$kind="Status"+code;NativeStatusProbe.event("actual-status-render",java.util.Map.of("code",code,"layers",layers,"age",age));}
 @Inject(method="vertex",at=@At("HEAD"),remap=false)
 private void qa$vertex(Vec3 p,CallbackInfo ci){NativeStatusProbe.vertex(qa$kind,matrix,p,color,alpha);}
 @Inject(method="triangle",at=@At("HEAD"),remap=false)
 private void qa$triangle(Vec3 a,Vec3 b,Vec3 c,double shade,CallbackInfo ci){if(a.distanceToSqr(camera)>=.64&&b.distanceToSqr(camera)>=.64&&c.distanceToSqr(camera)>=.64)NativeStatusProbe.triangle(qa$kind,matrix,a,b,c,color,alpha);}
}
