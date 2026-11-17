package com.dynasty.mobnetworkqa.mixin;

import com.mojang.blaze3d.platform.Window;
import org.lwjgl.glfw.GLFW;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Private QA only. Preserve Embeddium's original context-creation redirect. */
@Mixin(Window.class)
public abstract class QuietWindowMixin {
    @Redirect(method="<init>", at=@At(value="INVOKE", target="Lorg/lwjgl/glfw/GLFW;glfwDefaultWindowHints()V", remap=false))
    private void cod4HiddenHints() {
        GLFW.glfwDefaultWindowHints();
        GLFW.glfwWindowHint(GLFW.GLFW_VISIBLE, GLFW.GLFW_FALSE);
        GLFW.glfwWindowHint(GLFW.GLFW_FOCUSED, GLFW.GLFW_FALSE);
        GLFW.glfwWindowHint(GLFW.GLFW_FOCUS_ON_SHOW, GLFW.GLFW_FALSE);
        System.out.println("GUARD_NETWORK_QA_HIDDEN_WINDOW_HINTS");
    }
    @Inject(method="<init>", at=@At("RETURN"))
    private void cod4VerifyHidden(CallbackInfo ci) {
        long window=((Window)(Object)this).getWindow();
        int visible=GLFW.glfwGetWindowAttrib(window,GLFW.GLFW_VISIBLE);
        int focused=GLFW.glfwGetWindowAttrib(window,GLFW.GLFW_FOCUSED);
        System.out.println("GUARD_NETWORK_QA_WINDOW visible="+visible+" focused="+focused);
        if(visible!=GLFW.GLFW_FALSE||focused!=GLFW.GLFW_FALSE)throw new IllegalStateException("QA window must remain hidden and unfocused");
    }
}
