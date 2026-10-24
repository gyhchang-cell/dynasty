package com.dynasty.packqa;
@mezz.jei.api.JeiPlugin
public class JeiProbe implements mezz.jei.api.IModPlugin {
 public static mezz.jei.api.runtime.IJeiRuntime runtime;
 public net.minecraft.resources.ResourceLocation getPluginUid(){return new net.minecraft.resources.ResourceLocation("dynastypackqa","probe");}
 public void onRuntimeAvailable(mezz.jei.api.runtime.IJeiRuntime value){runtime=value;}
}
