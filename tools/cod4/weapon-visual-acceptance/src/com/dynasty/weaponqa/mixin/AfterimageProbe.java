package com.dynasty.weaponqa.mixin;
import com.dynasty.weaponqa.Probe;
import com.dynasty.cod3.*;
import net.minecraft.world.phys.Vec3;
import org.joml.Matrix4f;
import org.spongepowered.asm.mixin.*;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.*;
@Mixin(targets="com.dynasty.client.Cod3AfterImages",remap=false)
public abstract class AfterimageProbe {
 @Inject(method="weapon(Lnet/minecraft/world/item/ItemStack;Lcom/mojang/blaze3d/vertex/PoseStack;Lnet/minecraft/client/renderer/MultiBufferSource;IFLnet/minecraft/world/item/ItemDisplayContext;)V",at=@At("HEAD"),remap=false)
 private static void qa$weapon(net.minecraft.world.item.ItemStack s,com.mojang.blaze3d.vertex.PoseStack p,net.minecraft.client.renderer.MultiBufferSource b,int tint,float alpha,net.minecraft.world.item.ItemDisplayContext c,CallbackInfo ci){Probe.ghost(s,p.last().pose(),tint,alpha,c);}
}
