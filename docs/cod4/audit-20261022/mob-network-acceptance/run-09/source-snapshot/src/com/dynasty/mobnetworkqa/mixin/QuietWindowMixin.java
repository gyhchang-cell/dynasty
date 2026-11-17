package com.dynasty.mobnetworkqa.mixin;

import com.mojang.blaze3d.platform.Window;
import org.lwjgl.glfw.GLFW;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;
import java.util.function.*;
import net.minecraftforge.fml.loading.ImmediateWindowHandler;

/** Private acceptance presentation only; never shipped in the game mod. */
@Mixin(Window.class)
public abstract class QuietWindowMixin {
    @Redirect(method="<init>", at=@At(value="INVOKE", target="Lnet/minecraftforge/fml/loading/ImmediateWindowHandler;setupMinecraftWindow(Ljava/util/function/IntSupplier;Ljava/util/function/IntSupplier;Ljava/util/function/Supplier;Ljava/util/function/LongSupplier;)J", remap=false))
    private long cod4HiddenWindow(IntSupplier width, IntSupplier height, Supplier<String> title, LongSupplier monitor) {
        GLFW.glfwWindowHint(GLFW.GLFW_VISIBLE, GLFW.GLFW_FALSE);
        GLFW.glfwWindowHint(GLFW.GLFW_FOCUSED, GLFW.GLFW_FALSE);
        GLFW.glfwWindowHint(GLFW.GLFW_FOCUS_ON_SHOW, GLFW.GLFW_FALSE);
        System.out.println("GUARD_NETWORK_QA_HIDDEN_WINDOW_HINTS");
        long window=ImmediateWindowHandler.setupMinecraftWindow(width,height,title,monitor);
        int visible=GLFW.glfwGetWindowAttrib(window,GLFW.GLFW_VISIBLE);
        int focused=GLFW.glfwGetWindowAttrib(window,GLFW.GLFW_FOCUSED);
        System.out.println("GUARD_NETWORK_QA_WINDOW visible="+visible+" focused="+focused);
        if(visible!=GLFW.GLFW_FALSE||focused!=GLFW.GLFW_FALSE)throw new IllegalStateException("QA window must remain hidden and unfocused");
        return window;
    }
}
