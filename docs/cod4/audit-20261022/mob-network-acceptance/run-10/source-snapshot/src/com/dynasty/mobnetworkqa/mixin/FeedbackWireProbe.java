package com.dynasty.mobnetworkqa.mixin;
import com.dynasty.mobnetworkqa.NativeStatusProbe;
import com.dynasty.expansion.CombatFeedback;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
@Mixin(value=CombatFeedback.class,remap=false) public abstract class FeedbackWireProbe {
 @Inject(method="handle",at=@At("HEAD"),remap=false) private static void qa$wire(CombatFeedback p,java.util.function.Supplier<net.minecraftforge.network.NetworkEvent.Context> supplier,CallbackInfo ci){NativeStatusProbe.event("actual-combat-feedback",java.util.Map.of("type",p.type(),"position",java.util.List.of(p.x(),p.y(),p.z())));}
}
