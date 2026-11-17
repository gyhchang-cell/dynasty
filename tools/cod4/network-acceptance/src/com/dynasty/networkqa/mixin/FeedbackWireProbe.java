package com.dynasty.networkqa.mixin;
import com.dynasty.expansion.CombatFeedback;
import com.dynasty.networkqa.WeaponProbe;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(targets="com.dynasty.expansion.ExpansionClient",remap=false)
public abstract class FeedbackWireProbe {
 @Inject(method="feedback",at=@At("HEAD"),remap=false)
 private static void qa$feedback(CombatFeedback p,CallbackInfo ci){WeaponProbe.feedback(p);}
}
