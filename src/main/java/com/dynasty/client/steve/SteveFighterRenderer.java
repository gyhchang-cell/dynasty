package com.dynasty.client.steve;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.math.Axis;
import net.minecraft.client.renderer.*;
import net.minecraft.client.renderer.entity.*;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.*;
import net.minecraft.world.item.*;
import com.dynasty.blueprint.TemplateMob;

/** Opaque pixel art and held equipment only; no aura, glyphs or decorative particle emitters. */
public final class SteveFighterRenderer<T extends Mob> extends MobRenderer<T,SteveFighterModel<T>> {
    private final String id;
    public SteveFighterRenderer(EntityRendererProvider.Context context,String id){
        super(context,new SteveFighterModel<>(id),.4f);this.id=id;
        addLayer(new RenderLayer<T,SteveFighterModel<T>>(this){
            @Override public void render(PoseStack pose,MultiBufferSource buffers,int light,T mob,float limb,float amount,float partial,float age,float yaw,float pitch){
                for(var hand:new HumanoidArm[]{HumanoidArm.RIGHT,HumanoidArm.LEFT}){
                    boolean left=hand==HumanoidArm.LEFT;ItemStack stack=hand==mob.getMainArm()?mob.getMainHandItem():mob.getOffhandItem();
                    if(stack.isEmpty()&&hand==HumanoidArm.RIGHT&&getParentModel().role.equals("crossbow")){stack=new ItemStack(Items.CROSSBOW);CrossbowItem.setCharged(stack,true);}
                    if(stack.isEmpty())continue;
                    pose.pushPose();getParentModel().translateToHand(hand,pose);pose.mulPose(Axis.XP.rotationDegrees(-90));pose.mulPose(Axis.YP.rotationDegrees(180));pose.translate((left?-1:1)/16.0,.125,-.625);
                    context.getItemInHandRenderer().renderItem(mob,stack,left?ItemDisplayContext.THIRD_PERSON_LEFT_HAND:ItemDisplayContext.THIRD_PERSON_RIGHT_HAND,left,pose,buffers,light);pose.popPose();
                }
            }
        });
    }
    @Override protected void scale(T mob,PoseStack pose,float partial){float s=model.visualScale;if(mob instanceof TemplateMob t&&t.isPossessed())s*=1.15f;pose.scale(s,s,s);}
    @Override protected float getFlipDegrees(T mob){return model.role.equals("shield")?0:super.getFlipDegrees(mob);}
    @Override public ResourceLocation getTextureLocation(T mob){return SteveFighterModel.texture(id);}
}
