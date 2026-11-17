package com.dynasty.statusqa.mixin;
import com.dynasty.statusqa.Probe;
import com.dynasty.cod3.*;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
@Mixin(targets="com.dynasty.cod3.Cod3VisualPacket",remap=false)
public abstract class VisualWireProbe {
 @Inject(method="handle",at=@At("HEAD"),remap=false)
 private static void qa$wire(Cod3VisualPacket p,java.util.function.Supplier<net.minecraftforge.network.NetworkEvent.Context> s,CallbackInfo ci){Probe.wire(p);}
}
