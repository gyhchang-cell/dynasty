package com.dynasty.qa;
@mezz.jei.api.JeiPlugin
public class JeiProbe implements mezz.jei.api.IModPlugin {
    static mezz.jei.api.runtime.IJeiRuntime runtime;
    public net.minecraft.resources.ResourceLocation getPluginUid(){return new net.minecraft.resources.ResourceLocation("dynasty","bugfix_qa");}
    public void onRuntimeAvailable(mezz.jei.api.runtime.IJeiRuntime r){runtime=r;}
}
