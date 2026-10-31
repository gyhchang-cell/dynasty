//
// Source code recreated from a .class file by IntelliJ IDEA
// (powered by FernFlower decompiler)
//

package floffy.toffys_hooks.mixins;

import floffy.toffys_hooks.entity.HookEntity;
import floffy.toffys_hooks.item.HookClawItem;
import floffy.toffys_hooks.item.IceSkateItem;
import floffy.toffys_hooks.register.ModItems;
import floffy.toffys_hooks.register.ModSoundEvents;
import floffy.toffys_hooks.util.PlayerWithHookData;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.minecraft.block.Blocks;
import net.minecraft.client.MinecraftClient;
import net.minecraft.entity.EquipmentSlot;
import net.minecraft.entity.attribute.EntityAttributes;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.ItemStack;
import net.minecraft.sound.SoundEvent;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Vec3d;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

@Mixin({PlayerEntity.class})
public abstract class PlayerMixin implements PlayerWithHookData {
    @Shadow
    public abstract void playSound(SoundEvent sound, float volume, float pitch);

    @Shadow public abstract void tickMovement();

    @Shadow public abstract void tick();
    private HookEntity hookEntity;
    @Unique
    private boolean onWall;
    @Unique
    private boolean airJump;

    public boolean isOnWall() {
        return this.onWall;
    }
    public void SetOnWall(boolean value) {
        this.onWall = value;
    }

    public PlayerMixin() {
    }
    public float getEntityJumpStrength(PlayerEntity entity){
        return 0.5f;
    }
    public HookEntity getHook() {
        return this.hookEntity;
    }

    public void setHook(HookEntity value) {
        this.hookEntity = value;
    }
    private float timeRunning;
    @Inject(
            method = {"tickMovement"},
            at = {@At("HEAD")}
    )
    @Environment(EnvType.CLIENT)
    public void tickMovement(CallbackInfo ci) {
        PlayerEntity player = (PlayerEntity)(Object)this;
        if (this.hookEntity != null && this.hookEntity.isInBlock()) {
            player.onLanding();
            if (player.isLogicalSideForUpdatingMovement()) {
                Vec3d vec3 = this.hookEntity.getPos().subtract(player.getEyePos());
                float g = this.hookEntity.getLength();
                double d = vec3.length();
                if (d > (double)g) {
                    double e = d / (double)g * 0.075;
                    player.addVelocity(vec3.multiply(1 / d).multiply(e, e * 1.1, e));
                }
            }
        }
        ItemStack feetSlot = player.getEquippedStack(EquipmentSlot.FEET);
        if (feetSlot.isOf(ModItems.CLIMBING_HOOK) && HookClawItem.isUsable(feetSlot)) {
            boolean condition = (player.horizontalCollision && (player.horizontalSpeed!=0)&&!player.isOnGround() && player.getVelocity().y<=0);
            if (player.getVelocity().y>= -0.126)player.onLanding();
            if (condition){
                if (player.isLogicalSideForUpdatingMovement()) {
                    if (!onWall) playSound(ModSoundEvents.HOOK_CLAW_CLIMB,.125f, 1F / (player.getWorld().getRandom().nextFloat() * 0.4F + 0.8F));
                    onWall = true;
                    player.setVelocity(player.getVelocity().x, player.isSneaking()?-0.25f:0.0f,player.getVelocity().z);
                    if (MinecraftClient.getInstance().player.input.jumping) player.setVelocity(player.getVelocity().x,getEntityJumpStrength((PlayerEntity)player),player.getVelocity().z);
                }
            }
            else{
                if (onWall) {player.onLanding();}
                onWall = false;}
        }

        if (feetSlot.isOf(ModItems.ICE_SKATES) && IceSkateItem.isUsable(feetSlot)) {
            player.getAttributeInstance(EntityAttributes.GENERIC_MOVEMENT_SPEED);
        }
    }
    @Inject(method ="getMovementSpeed",at= {@At("TAIL")},cancellable = true)
    public void getMovementSpeed(CallbackInfoReturnable<Float> cir){
        float MaxSpeed = 2;
        float Accumulation = 0.005f;
        PlayerEntity player = (PlayerEntity)(Object)this;
        ItemStack feetSlot = player.getEquippedStack(EquipmentSlot.FEET);
        if(player.isSprinting()) timeRunning+=Accumulation;
        else timeRunning=0f;
        if (timeRunning>MaxSpeed) timeRunning=MaxSpeed;
        if (timeRunning<0) timeRunning=0;
        if(feetSlot.isOf(ModItems.ICE_SKATES)) cir.setReturnValue((float) (player.getAttributeValue(EntityAttributes.GENERIC_MOVEMENT_SPEED)*(timeRunning+0.75f)));
    }
    @Inject(
            method = {"checkFallFlying"},
            at = {@At("HEAD")},
            cancellable = true)
    public void checkFallFlying(CallbackInfoReturnable<Boolean> cir){
        PlayerEntity player = (PlayerEntity)(Object)this;
        ItemStack feetSlot = player.getEquippedStack(EquipmentSlot.FEET);
        if (feetSlot.isOf(ModItems.CLIMBING_HOOK) && HookClawItem.isUsable(feetSlot)) {
            if (player.horizontalCollision && (player.horizontalSpeed!=0)&&!player.isOnGround() && player.getVelocity().y<=0 ) cir.setReturnValue(false);
        }
    }
}

