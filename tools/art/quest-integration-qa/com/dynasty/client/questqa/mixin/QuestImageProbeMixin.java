package com.dynasty.client.questqa.mixin;

import com.dynasty.client.QuestJourneyUiQa;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(targets="dev.ftb.mods.ftbquests.client.gui.ImageComponentWidget",remap=false)
public abstract class QuestImageProbeMixin {
    @Inject(method="draw",at=@At("HEAD"),remap=false)
    private void dynasty$record(CallbackInfo ci){QuestJourneyUiQa.recordImage(this);}
}
