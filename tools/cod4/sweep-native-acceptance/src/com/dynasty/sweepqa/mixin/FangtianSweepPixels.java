package com.dynasty.sweepqa.mixin;
import com.dynasty.sweepqa.Probe;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
import net.minecraftforge.client.event.RenderLevelStageEvent;
@Mixin(targets="com.dynasty.client.FangtianSweepRenderer",remap=false)
public abstract class FangtianSweepPixels {
 @Shadow @Final private static java.util.List<com.dynasty.cod3.Cod3VisualPacket> ACTIVE;
 @Inject(method="render",at=@At("HEAD"),remap=false) private static void qa$before(RenderLevelStageEvent e,CallbackInfo ci){if(e.getStage()==RenderLevelStageEvent.Stage.AFTER_PARTICLES)Probe.hook("FangtianSweep.before");Probe.pixelBefore("FangtianSweep",e,!ACTIVE.isEmpty());}
 @Inject(method="render",at=@At("RETURN"),remap=false) private static void qa$after(RenderLevelStageEvent e,CallbackInfo ci){if(e.getStage()==RenderLevelStageEvent.Stage.AFTER_PARTICLES)Probe.hook("FangtianSweep.after");Probe.pixelAfter("FangtianSweep");}
}
