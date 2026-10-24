package com.dynasty.networkqa.mixin;
import com.dynasty.cod3.Cod3VisualPacket;
import com.dynasty.networkqa.WeaponProbe;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import java.util.function.Supplier;
@Mixin(targets="com.dynasty.cod3.Cod3VisualPacket",remap=false)
public abstract class VisualWireProbe {
 @Inject(method="handle",at=@At("HEAD"),remap=false)
 private static void qa$wire(Cod3VisualPacket p,Supplier<net.minecraftforge.network.NetworkEvent.Context> s,CallbackInfo ci){if(s.get().getDirection()==net.minecraftforge.network.NetworkDirection.PLAY_TO_CLIENT)WeaponProbe.vfx(p);}
}
