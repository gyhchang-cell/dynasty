package com.dynasty.client.questqa.mixin;

import com.dynasty.client.QuestJourneyUiQa;
import com.mojang.blaze3d.vertex.*;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Records actual native render dispatch; never changes dependency rendering. */
@Mixin(targets="dev.ftb.mods.ftbquests.client.gui.quests.QuestPanel",remap=false)
public abstract class QuestLineProbeMixin {
    @Inject(method="renderConnection",at=@At("HEAD"),remap=false)
    private void dynasty$record(@Coerce Object from,@Coerce Object to,PoseStack pose,
            BufferBuilder buffer,float width,int r,int g,int b,int a,int a1,
            float offset,Tesselator tesselator,CallbackInfo ci){
        QuestJourneyUiQa.recordConnection(from,to);
    }
}
