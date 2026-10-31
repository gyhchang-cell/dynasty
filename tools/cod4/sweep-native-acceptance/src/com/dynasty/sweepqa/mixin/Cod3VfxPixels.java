package com.dynasty.sweepqa.mixin;
import com.dynasty.sweepqa.Probe;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
import net.minecraftforge.client.event.RenderLevelStageEvent;
@Mixin(targets="com.dynasty.client.Cod3VfxRenderer",remap=false)
public abstract class Cod3VfxPixels {
 @Shadow @Final private static java.util.List<com.dynasty.cod3.Cod3VisualPacket> ACTIVE;
 @Inject(method="render",at=@At("HEAD"),remap=false) private static void qa$before(RenderLevelStageEvent e,CallbackInfo ci){if(e.getStage()==RenderLevelStageEvent.Stage.AFTER_PARTICLES)Probe.hook("Cod3Vfx.before");Probe.pixelBefore("Cod3Vfx",e,!ACTIVE.isEmpty());}
 @Inject(method="render",at=@At("RETURN"),remap=false) private static void qa$after(RenderLevelStageEvent e,CallbackInfo ci){if(e.getStage()==RenderLevelStageEvent.Stage.AFTER_PARTICLES)Probe.hook("Cod3Vfx.after");Probe.pixelAfter("Cod3Vfx");}
}
