package com.dynasty.weaponqa.mixin;
import com.dynasty.weaponqa.Probe;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
import net.minecraftforge.client.event.RenderLevelStageEvent;
@Mixin(targets="com.dynasty.client.DragonDecalRenderer",remap=false)
public abstract class DragonDecalPixels {
 @Shadow @Final private static java.util.List<com.dynasty.cod3.Cod3VisualPacket> ACTIVE;
 @Inject(method="render",at=@At("HEAD"),remap=false) private static void qa$before(RenderLevelStageEvent e,CallbackInfo ci){Probe.pixelBefore("DragonDecal",e,!ACTIVE.isEmpty());}
 @Inject(method="render",at=@At("RETURN"),remap=false) private static void qa$after(RenderLevelStageEvent e,CallbackInfo ci){Probe.pixelAfter("DragonDecal");}
}
