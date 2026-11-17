package galena.oreganized.mixin.client;

import com.mojang.blaze3d.vertex.PoseStack;
import galena.oreganized.content.item.ElectrumArmorItem;
import galena.oreganized.index.OItems;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.model.Model;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.layers.HumanoidArmorLayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.armortrim.ArmorTrim;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(HumanoidArmorLayer.class)
public abstract class HumanoidArmorLayerMixin {

    @Inject(method = "renderArmorPiece", at = @At("HEAD"), cancellable = true)
    public void renderElectrumArmorPiece(PoseStack poseStack, MultiBufferSource bufferSource, LivingEntity entity, EquipmentSlot slot, int packedLight, HumanoidModel<? extends LivingEntity> model, CallbackInfo ci) {
        var accessor = (HumanoidArmorLayerAccessor) this;
        var self = (HumanoidArmorLayer) (Object) this;

        ItemStack itemStack = entity.getItemBySlot(slot);
        Item item = itemStack.getItem();
        if (item instanceof ElectrumArmorItem armorItem) {
            if (armorItem.getEquipmentSlot() == slot) {
                var parent = (HumanoidModel<?>) self.getParentModel();
                parent.copyPropertiesTo((HumanoidModel) model);
                accessor.invokeSetPartVisibility(model, slot);
                Model electrumArmorModel = accessor.invokeGetArmorModelHook(entity, itemStack, slot, model);
                boolean usesInnerModel = accessor.invokeUsesInnerModel(slot);
                accessor.invokeRenderModel(poseStack, bufferSource, packedLight, armorItem, electrumArmorModel, usesInnerModel, 1.0F, 1.0F, 1.0F, accessor.invokeGetArmorResource(entity, itemStack, slot, null));

                Item baseArmorItem = (
                        item == OItems.ELECTRUM_HELMET.get() ? Items.IRON_HELMET :
                                item == OItems.ELECTRUM_CHESTPLATE.get() ? Items.IRON_CHESTPLATE :
                                        item == OItems.ELECTRUM_LEGGINGS.get() ? Items.IRON_LEGGINGS :
                                                Items.IRON_BOOTS
                );

                Model baseArmorModel = accessor.invokeGetArmorModelHook(entity, new ItemStack(baseArmorItem), slot, model);

                ArmorTrim.getTrim(entity.level().registryAccess(), itemStack).ifPresent((armorTrim) -> accessor.invokeRenderTrim(armorItem.getMaterial(), poseStack, bufferSource, packedLight, armorTrim, baseArmorModel, usesInnerModel));
                if (itemStack.hasFoil()) {
                    accessor.invokeRenderGlint(poseStack, bufferSource, packedLight, electrumArmorModel);
                }
                ci.cancel();
            }
        }
    }
}
