package com.dynasty.networkqa.mixin;
import com.dynasty.networkqa.WeaponProbe;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.*;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
@Mixin(targets="com.dynasty.cod3.EquipmentFeedback",remap=false)
public abstract class WeaponSourceProbe {
 @Inject(method="weapon",at=@At("HEAD"),remap=false)
 private static void qa$source(net.minecraft.world.entity.player.Player p,String cue,net.minecraft.world.phys.Vec3 end,CallbackInfo ci){WeaponProbe.weapon(p,cue);}
}
